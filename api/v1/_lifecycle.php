<?php
/**
 * Account Lifecycle History (BR-LAUNCH-09 Phase 3A Extension).
 *
 * Contract (L1 closed 2026-09-29, docs/br-launch-09-lifecycle-l1-draft.md):
 * - One minimal row per self-service deletion: previous userId, HMAC(normalized email, server key), created / deleted
 *   dates, lifetime, plan / role at deletion, account kind, signup origin, cleanup status, return counters.
 *   Never: raw email, password hash, profile, business data, consent contents, IP, UA, Stripe IDs.
 * - The HMAC key lives only in config.local.php (`lifecycleHmacKey` + `lifecycleHmacKeyId`; retired keys in
 *   `lifecycleHmacPreviousKeys` [id => key] stay usable for matching). Missing key / tables = not ready, and the
 *   account deletion refuses to run (fail closed).
 * - Rows are purged automatically 3 years after deleted_at.
 * - A new account whose email matches a history row is marked RETURNED; no past data is ever restored.
 */

require_once __DIR__ . '/_bootstrap.php';
require_once __DIR__ . '/_auth.php';
require_once __DIR__ . '/_registration.php';

const KPI_LIFECYCLE_RETENTION = '-3 years';
const KPI_LIFECYCLE_MIN_KEY_LENGTH = 32;

/** @return array{0:string,1:string}|null [keyId, key] */
function kpi_v1_lifecycle_active_key($cfg)
{
    $key = isset($cfg['lifecycleHmacKey']) && is_string($cfg['lifecycleHmacKey']) ? $cfg['lifecycleHmacKey'] : '';
    $id = isset($cfg['lifecycleHmacKeyId']) && is_string($cfg['lifecycleHmacKeyId']) ? trim($cfg['lifecycleHmacKeyId']) : '';
    if (strlen($key) < KPI_LIFECYCLE_MIN_KEY_LENGTH || !preg_match('/^[A-Za-z0-9_-]{1,16}$/', $id)) {
        return null;
    }
    return [$id, $key];
}

/** @return array<string,string> keyId => key, active key first */
function kpi_v1_lifecycle_all_keys($cfg)
{
    $out = [];
    $active = kpi_v1_lifecycle_active_key($cfg);
    if ($active !== null) {
        $out[$active[0]] = $active[1];
    }
    if (isset($cfg['lifecycleHmacPreviousKeys']) && is_array($cfg['lifecycleHmacPreviousKeys'])) {
        foreach ($cfg['lifecycleHmacPreviousKeys'] as $id => $key) {
            if (is_string($key) && strlen($key) >= KPI_LIFECYCLE_MIN_KEY_LENGTH && !isset($out[(string) $id])) {
                $out[(string) $id] = $key;
            }
        }
    }
    return $out;
}

function kpi_v1_lifecycle_normalize_email($email)
{
    return strtolower(trim((string) $email));
}

function kpi_v1_lifecycle_email_hmac($key, $email)
{
    return hash_hmac('sha256', 'kpn-lifecycle-email:' . kpi_v1_lifecycle_normalize_email($email), (string) $key);
}

/** @return string[] HMACs of this email under every configured key */
function kpi_v1_lifecycle_email_hmacs($cfg, $email)
{
    $out = [];
    foreach (kpi_v1_lifecycle_all_keys($cfg) as $key) {
        $out[] = kpi_v1_lifecycle_email_hmac($key, $email);
    }
    return array_values(array_unique($out));
}

function kpi_v1_lifecycle_dt($value)
{
    $ts = strtotime((string) $value . (preg_match('/Z|[+-]\d\d:?\d\d$/', (string) $value) ? '' : ' UTC'));
    return $ts === false ? null : gmdate('Y-m-d H:i:s', $ts);
}

function kpi_v1_lifecycle_cutoff()
{
    return gmdate('Y-m-d H:i:s', strtotime(KPI_LIFECYCLE_RETENTION));
}

/* ---------- File storage (local / file driver) ---------- */

function kpi_v1_lifecycle_dir()
{
    return __DIR__ . '/data/lifecycle';
}

function kpi_v1_lifecycle_file($name)
{
    return kpi_v1_lifecycle_dir() . '/' . $name . '.json';
}

function kpi_v1_lifecycle_file_read($name)
{
    $path = kpi_v1_lifecycle_file($name);
    if (!is_file($path)) {
        return [];
    }
    $data = json_decode((string) @file_get_contents($path), true);
    return is_array($data) ? $data : null;
}

/**
 * Runs $fn(deletions, origins) under the lifecycle file lock; $fn returns [deletions, origins, result] or null to abort.
 * @return mixed|null result, or null when the lock / read / write failed or $fn aborted
 */
function kpi_v1_lifecycle_file_tx(callable $fn)
{
    $dir = kpi_v1_lifecycle_dir();
    if (!is_dir($dir) && !@mkdir($dir, 0750, true)) {
        return null;
    }
    $lock = @fopen($dir . '/lifecycle.lock', 'c+');
    if ($lock === false || !flock($lock, LOCK_EX)) {
        if ($lock !== false) {
            fclose($lock);
        }
        return null;
    }
    try {
        $deletions = kpi_v1_lifecycle_file_read('deletions');
        $origins = kpi_v1_lifecycle_file_read('origins');
        if ($deletions === null || $origins === null) {
            return null;
        }
        $out = $fn($deletions, $origins);
        if (!is_array($out)) {
            return null;
        }
        if ($out[0] !== $deletions && !kpi_v1_registration_write_json_atomic(kpi_v1_lifecycle_file('deletions'), array_values($out[0]))) {
            return null;
        }
        if ($out[1] !== $origins && !kpi_v1_registration_write_json_atomic(kpi_v1_lifecycle_file('origins'), $out[1])) {
            return null;
        }
        return $out[2];
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

/* ---------- Readiness (fail closed) ---------- */

function kpi_v1_lifecycle_ready($cfg)
{
    if (kpi_v1_lifecycle_active_key($cfg) === null) {
        return false;
    }
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        try {
            $pdo = kpi_v1_db($cfg);
            $pdo->query('SELECT id FROM kpi_account_deletions LIMIT 0');
            $pdo->query('SELECT user_id FROM kpi_account_origins LIMIT 0');
            return true;
        } catch (Throwable $e) {
            return false;
        }
    }
    $dir = kpi_v1_lifecycle_dir();
    if (!is_dir($dir)) {
        @mkdir($dir, 0750, true);
    }
    return is_dir($dir) && is_writable($dir)
        && kpi_v1_lifecycle_file_read('deletions') !== null && kpi_v1_lifecycle_file_read('origins') !== null;
}

/* ---------- Deletion record ---------- */

/**
 * @param array $account userId, email, plan, role, createdAt, parentUserId
 * @param array|null $origin origin row of the account (origin, excludeFromMetrics) or null
 * @return array|null record, or null when no key is configured
 */
function kpi_v1_lifecycle_build_record($cfg, $account, $origin)
{
    $key = kpi_v1_lifecycle_active_key($cfg);
    if ($key === null) {
        return null;
    }
    $now = time();
    $created = kpi_v1_lifecycle_dt($account['createdAt'] ?? '') ?? gmdate('Y-m-d H:i:s', $now);
    $lifetime = (int) floor(max(0, $now - strtotime($created . ' UTC')) / 86400);
    $plan = strtolower((string) ($account['plan'] ?? 'basic'));
    $originName = is_array($origin) && in_array($origin['origin'] ?? '', ['new', 'returned', 'unknown'], true)
        ? (string) $origin['origin'] : 'legacy';
    return [
        'lifecycleId' => 'lc_' . bin2hex(random_bytes(12)),
        'previousUserId' => (string) $account['userId'],
        'emailHmac' => kpi_v1_lifecycle_email_hmac($key[1], (string) $account['email']),
        'hmacKeyId' => $key[0],
        'accountCreatedAt' => $created,
        'deletedAt' => gmdate('Y-m-d H:i:s', $now),
        'lifetimeDays' => $lifetime,
        'planAtDeletion' => $plan === 'pro' ? 'pro' : 'basic',
        'roleAtDeletion' => (string) ($account['role'] ?? 'user'),
        'accountKind' => !empty($account['parentUserId']) ? 'child' : 'standalone',
        'signupOrigin' => $originName,
        'deletionSource' => 'self_service',
        'cleanupStatus' => 'pending',
        'cleanupDetail' => null,
        'excludeFromMetrics' => is_array($origin) && !empty($origin['excludeFromMetrics']),
        'returnedAt' => null,
        'returnCount' => 0,
    ];
}

/** Inside the caller's MySQL transaction. Throws on failure so the account delete rolls back. */
function kpi_v1_lifecycle_db_insert(PDO $pdo, $r)
{
    $st = $pdo->prepare(
        'INSERT INTO kpi_account_deletions (lifecycle_id, previous_user_id, email_hmac, hmac_key_id, account_created_at,
           deleted_at, lifetime_days, plan_at_deletion, role_at_deletion, account_kind, signup_origin, deletion_source,
           cleanup_status, exclude_from_metrics, return_count)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)'
    );
    $st->execute([
        $r['lifecycleId'], $r['previousUserId'], $r['emailHmac'], $r['hmacKeyId'], $r['accountCreatedAt'],
        $r['deletedAt'], $r['lifetimeDays'], $r['planAtDeletion'], $r['roleAtDeletion'], $r['accountKind'],
        $r['signupOrigin'], $r['deletionSource'], $r['cleanupStatus'], $r['excludeFromMetrics'] ? 1 : 0,
    ]);
}

/** @return array|null origin row (origin, excludeFromMetrics) — throws on DB error */
function kpi_v1_lifecycle_db_origin(PDO $pdo, $userId)
{
    $st = $pdo->prepare('SELECT origin, exclude_from_metrics FROM kpi_account_origins WHERE user_id = ? LIMIT 1');
    $st->execute([(string) $userId]);
    $row = $st->fetch(PDO::FETCH_ASSOC);
    return $row ? ['origin' => (string) $row['origin'], 'excludeFromMetrics' => (int) $row['exclude_from_metrics'] === 1] : null;
}

/** File driver: append the pending record. @return bool */
function kpi_v1_lifecycle_file_insert($record)
{
    return kpi_v1_lifecycle_file_tx(function ($d, $o) use ($record) {
        foreach ($d as $row) {
            if ((string) ($row['previousUserId'] ?? '') === $record['previousUserId']) {
                return null;
            }
        }
        $d[] = $record;
        unset($o[$record['previousUserId']]);
        return [$d, $o, true];
    }) === true;
}

/** File driver: undo a pending record when the account could not be deleted. */
function kpi_v1_lifecycle_file_remove($lifecycleId)
{
    return kpi_v1_lifecycle_file_tx(function ($d, $o) use ($lifecycleId) {
        $d = array_values(array_filter($d, function ($row) use ($lifecycleId) {
            return (string) ($row['lifecycleId'] ?? '') !== (string) $lifecycleId;
        }));
        return [$d, $o, true];
    }) === true;
}

function kpi_v1_lifecycle_file_origin($userId)
{
    $o = kpi_v1_lifecycle_file_read('origins');
    return is_array($o) && isset($o[(string) $userId]) && is_array($o[(string) $userId]) ? $o[(string) $userId] : null;
}

/** After the post-delete cleanup. Best effort: a failure leaves the row at 'pending'. */
function kpi_v1_lifecycle_set_cleanup($cfg, $lifecycleId, $residual)
{
    $status = $residual === [] ? 'complete' : 'residual';
    $detail = $residual === [] ? null : substr(implode(',', $residual), 0, 255);
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            require_once __DIR__ . '/_db.php';
            $st = kpi_v1_db($cfg)->prepare('UPDATE kpi_account_deletions SET cleanup_status = ?, cleanup_detail = ? WHERE lifecycle_id = ?');
            $st->execute([$status, $detail, (string) $lifecycleId]);
            return $st->rowCount() === 1;
        }
        return kpi_v1_lifecycle_file_tx(function ($d, $o) use ($lifecycleId, $status, $detail) {
            foreach ($d as $i => $row) {
                if ((string) ($row['lifecycleId'] ?? '') === (string) $lifecycleId) {
                    $d[$i]['cleanupStatus'] = $status;
                    $d[$i]['cleanupDetail'] = $detail;
                }
            }
            return [$d, $o, true];
        }) === true;
    } catch (Throwable $e) {
        return false;
    }
}

/* ---------- Retention ---------- */

/** Deletes rows older than 3 years after deleted_at. @return int|null rows purged, null on failure */
function kpi_v1_lifecycle_purge($cfg)
{
    $cutoff = kpi_v1_lifecycle_cutoff();
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            require_once __DIR__ . '/_db.php';
            $pdo = kpi_v1_db($cfg);
            $st = $pdo->prepare('DELETE FROM kpi_account_deletions WHERE deleted_at < ?');
            $st->execute([$cutoff]);
            $n = $st->rowCount();
            if ($n > 0) {
                $pdo->exec('UPDATE kpi_account_origins o LEFT JOIN kpi_account_deletions d ON d.id = o.matched_deletion_id
                            SET o.matched_deletion_id = NULL WHERE o.matched_deletion_id IS NOT NULL AND d.id IS NULL');
            }
            return $n;
        }
        return kpi_v1_lifecycle_file_tx(function ($d, $o) use ($cutoff) {
            $kept = array_values(array_filter($d, function ($row) use ($cutoff) {
                return (string) ($row['deletedAt'] ?? '') >= $cutoff;
            }));
            $ids = array_column($kept, 'lifecycleId');
            foreach ($o as $uid => $row) {
                if (!empty($row['matchedLifecycleId']) && !in_array($row['matchedLifecycleId'], $ids, true)) {
                    $o[$uid]['matchedLifecycleId'] = null;
                }
            }
            return [$kept, $o, count($d) - count($kept)];
        });
    } catch (Throwable $e) {
        return null;
    }
}

/* ---------- Account creation (NEW / RETURNED) ---------- */

/**
 * Called after a new account exists. Never blocks or undoes the account creation:
 * any failure marks the origin 'unknown' (best effort) and is logged.
 * @return string new | returned | unknown
 */
function kpi_v1_lifecycle_on_account_created($cfg, $userId, $email)
{
    $userId = (string) $userId;
    $hmacs = kpi_v1_lifecycle_email_hmacs($cfg, $email);
    $now = gmdate('Y-m-d H:i:s');
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            require_once __DIR__ . '/_db.php';
            $pdo = kpi_v1_db($cfg);
            $pdo->beginTransaction();
            try {
                $matched = null;
                if ($hmacs !== []) {
                    $in = implode(',', array_fill(0, count($hmacs), '?'));
                    $st = $pdo->prepare("SELECT id FROM kpi_account_deletions WHERE email_hmac IN ($in)
                                         ORDER BY deleted_at DESC, id DESC LIMIT 1 FOR UPDATE");
                    $st->execute($hmacs);
                    $id = $st->fetchColumn();
                    if ($id !== false) {
                        $matched = (int) $id;
                        $up = $pdo->prepare("UPDATE kpi_account_deletions
                                             SET return_count = return_count + 1, returned_at = COALESCE(returned_at, ?)
                                             WHERE email_hmac IN ($in)");
                        $up->execute(array_merge([$now], $hmacs));
                    }
                }
                $origin = $hmacs === [] ? 'unknown' : ($matched !== null ? 'returned' : 'new');
                $ins = $pdo->prepare('INSERT INTO kpi_account_origins (user_id, origin, matched_deletion_id, exclude_from_metrics, created_at)
                                      VALUES (?, ?, ?, 0, ?)');
                $ins->execute([$userId, $origin, $matched, $now]);
                $pdo->commit();
            } catch (Throwable $e) {
                if ($pdo->inTransaction()) {
                    $pdo->rollBack();
                }
                throw $e;
            }
        } else {
            $origin = kpi_v1_lifecycle_file_tx(function ($d, $o) use ($userId, $hmacs, $now) {
                $matched = null;
                $latest = '';
                foreach ($d as $i => $row) {
                    if ($hmacs !== [] && in_array((string) ($row['emailHmac'] ?? ''), $hmacs, true)) {
                        $d[$i]['returnCount'] = (int) ($row['returnCount'] ?? 0) + 1;
                        if (empty($row['returnedAt'])) {
                            $d[$i]['returnedAt'] = $now;
                        }
                        if ((string) $row['deletedAt'] >= $latest) {
                            $latest = (string) $row['deletedAt'];
                            $matched = (string) $row['lifecycleId'];
                        }
                    }
                }
                $origin = $hmacs === [] ? 'unknown' : ($matched !== null ? 'returned' : 'new');
                $o[$userId] = ['origin' => $origin, 'matchedLifecycleId' => $matched, 'excludeFromMetrics' => false, 'createdAt' => $now];
                return [$d, $o, $origin];
            });
            if ($origin === null) {
                throw new RuntimeException('lifecycle file store unavailable');
            }
        }
        if ($hmacs === []) {
            error_log('kpn lifecycle: no HMAC key configured; origin unknown for ' . $userId);
        }
        return $origin;
    } catch (Throwable $e) {
        error_log('kpn lifecycle: origin lookup failed for ' . $userId . ': ' . get_class($e));
        kpi_v1_lifecycle_mark_unknown($cfg, $userId, $now);
        return 'unknown';
    }
}

function kpi_v1_lifecycle_mark_unknown($cfg, $userId, $now)
{
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            $st = kpi_v1_db($cfg)->prepare('INSERT IGNORE INTO kpi_account_origins (user_id, origin, matched_deletion_id, exclude_from_metrics, created_at)
                                            VALUES (?, \'unknown\', NULL, 0, ?)');
            $st->execute([(string) $userId, $now]);
            return;
        }
        kpi_v1_lifecycle_file_tx(function ($d, $o) use ($userId, $now) {
            if (!isset($o[$userId])) {
                $o[$userId] = ['origin' => 'unknown', 'matchedLifecycleId' => null, 'excludeFromMetrics' => false, 'createdAt' => $now];
            }
            return [$d, $o, true];
        });
    } catch (Throwable $e) {
        // Origin stays absent (shown as legacy); the account itself is unaffected.
    }
}

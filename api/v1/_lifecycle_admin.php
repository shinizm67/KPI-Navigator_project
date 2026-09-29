<?php
/**
 * Founder-side Account Lifecycle helpers (BR-LAUNCH-09 Phase 3A Extension L3).
 * Callers must already be Founder-gated. Rows are returned without the HMAC; raw email never exists here.
 *
 * Monthly churn contract (frozen 2026-09-29, Standalone Customer Account Churn):
 * - eligible = role user, no parent (child accounts counted separately), not exclude_from_metrics
 * - month boundaries in JST (Asia/Tokyo)
 * - denominator = eligible accounts existing at month start (disabled included)
 * - numerator = eligible accounts deleted during the month that existed at its start
 * - accounts created and deleted in the same month = Early Churn (not in the core rate)
 */

require_once __DIR__ . '/_lifecycle.php';
require_once __DIR__ . '/_admin_store.php';

function kpi_v1_lifecycle_row_from_db($r)
{
    return [
        'lifecycleId' => (string) $r['lifecycle_id'],
        'previousUserId' => (string) $r['previous_user_id'],
        'emailHmac' => (string) $r['email_hmac'],
        'accountCreatedAt' => (string) $r['account_created_at'],
        'deletedAt' => (string) $r['deleted_at'],
        'lifetimeDays' => (int) $r['lifetime_days'],
        'planAtDeletion' => (string) $r['plan_at_deletion'],
        'roleAtDeletion' => (string) $r['role_at_deletion'],
        'accountKind' => (string) $r['account_kind'],
        'signupOrigin' => (string) $r['signup_origin'],
        'deletionSource' => (string) $r['deletion_source'],
        'cleanupStatus' => (string) $r['cleanup_status'],
        'cleanupDetail' => $r['cleanup_detail'] !== null ? (string) $r['cleanup_detail'] : null,
        'excludeFromMetrics' => (int) $r['exclude_from_metrics'] === 1,
        'returnedAt' => $r['returned_at'] !== null ? (string) $r['returned_at'] : null,
        'returnCount' => (int) $r['return_count'],
    ];
}

/** @return array[]|null all history rows (newest deletion first), null on storage failure */
function kpi_v1_lifecycle_all_rows($cfg)
{
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            $st = kpi_v1_db($cfg)->query('SELECT * FROM kpi_account_deletions ORDER BY deleted_at DESC, id DESC');
            return array_map('kpi_v1_lifecycle_row_from_db', $st->fetchAll(PDO::FETCH_ASSOC));
        }
        $rows = kpi_v1_lifecycle_file_read('deletions');
        if ($rows === null) {
            return null;
        }
        usort($rows, function ($a, $b) {
            return strcmp((string) ($b['deletedAt'] ?? ''), (string) ($a['deletedAt'] ?? ''));
        });
        return $rows;
    } catch (Throwable $e) {
        return null;
    }
}

/** Founder view of a row: no HMAC / key id. */
function kpi_v1_lifecycle_public_row($r)
{
    return [
        'lifecycleId' => (string) $r['lifecycleId'],
        'previousUserId' => (string) $r['previousUserId'],
        'accountCreatedAt' => kpi_v1_admin_dt_to_iso($r['accountCreatedAt'] ?? null),
        'deletedAt' => kpi_v1_admin_dt_to_iso($r['deletedAt'] ?? null),
        'lifetimeDays' => (int) ($r['lifetimeDays'] ?? 0),
        'planAtDeletion' => (string) ($r['planAtDeletion'] ?? ''),
        'accountKind' => (string) ($r['accountKind'] ?? ''),
        'signupOrigin' => (string) ($r['signupOrigin'] ?? ''),
        'cleanupStatus' => (string) ($r['cleanupStatus'] ?? ''),
        'cleanupDetail' => isset($r['cleanupDetail']) ? $r['cleanupDetail'] : null,
        'excludeFromMetrics' => !empty($r['excludeFromMetrics']),
        'returned' => (int) ($r['returnCount'] ?? 0) > 0,
        'returnedAt' => kpi_v1_admin_dt_to_iso($r['returnedAt'] ?? null),
        'returnCount' => (int) ($r['returnCount'] ?? 0),
    ];
}

/** @return array[]|null rows matching this email under any configured key (input is neither stored nor logged) */
function kpi_v1_lifecycle_lookup($cfg, $email)
{
    $hmacs = kpi_v1_lifecycle_email_hmacs($cfg, $email);
    $rows = kpi_v1_lifecycle_all_rows($cfg);
    if ($rows === null) {
        return null;
    }
    return array_values(array_filter($rows, function ($r) use ($hmacs) {
        return in_array((string) ($r['emailHmac'] ?? ''), $hmacs, true);
    }));
}

/** @return string ok | not_found | failed */
function kpi_v1_lifecycle_erase($cfg, $lifecycleId)
{
    $lifecycleId = (string) $lifecycleId;
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            $pdo = kpi_v1_db($cfg);
            $pdo->beginTransaction();
            $st = $pdo->prepare('SELECT id FROM kpi_account_deletions WHERE lifecycle_id = ? FOR UPDATE');
            $st->execute([$lifecycleId]);
            $id = $st->fetchColumn();
            if ($id === false) {
                $pdo->rollBack();
                return 'not_found';
            }
            $pdo->prepare('UPDATE kpi_account_origins SET matched_deletion_id = NULL WHERE matched_deletion_id = ?')->execute([(int) $id]);
            $pdo->prepare('DELETE FROM kpi_account_deletions WHERE id = ?')->execute([(int) $id]);
            $pdo->commit();
            return 'ok';
        }
        $out = kpi_v1_lifecycle_file_tx(function ($d, $o) use ($lifecycleId) {
            $kept = array_values(array_filter($d, function ($r) use ($lifecycleId) {
                return (string) ($r['lifecycleId'] ?? '') !== $lifecycleId;
            }));
            if (count($kept) === count($d)) {
                return [$d, $o, 'not_found'];
            }
            foreach ($o as $uid => $row) {
                if ((string) ($row['matchedLifecycleId'] ?? '') === $lifecycleId) {
                    $o[$uid]['matchedLifecycleId'] = null;
                }
            }
            return [$kept, $o, 'ok'];
        });
        return $out === null ? 'failed' : $out;
    } catch (Throwable $e) {
        if (isset($pdo) && $pdo instanceof PDO && $pdo->inTransaction()) {
            $pdo->rollBack();
        }
        return 'failed';
    }
}

/** @return string ok | not_found | failed */
function kpi_v1_lifecycle_set_history_exclusion($cfg, $lifecycleId, $exclude)
{
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            $pdo = kpi_v1_db($cfg);
            $st = $pdo->prepare('SELECT 1 FROM kpi_account_deletions WHERE lifecycle_id = ?');
            $st->execute([(string) $lifecycleId]);
            if ($st->fetchColumn() === false) {
                return 'not_found';
            }
            $pdo->prepare('UPDATE kpi_account_deletions SET exclude_from_metrics = ? WHERE lifecycle_id = ?')
                ->execute([$exclude ? 1 : 0, (string) $lifecycleId]);
            return 'ok';
        }
        $out = kpi_v1_lifecycle_file_tx(function ($d, $o) use ($lifecycleId, $exclude) {
            $hit = false;
            foreach ($d as $i => $r) {
                if ((string) ($r['lifecycleId'] ?? '') === (string) $lifecycleId) {
                    $d[$i]['excludeFromMetrics'] = (bool) $exclude;
                    $hit = true;
                }
            }
            return [$d, $o, $hit ? 'ok' : 'not_found'];
        });
        return $out === null ? 'failed' : $out;
    } catch (Throwable $e) {
        return 'failed';
    }
}

/** Live account flag (kept in kpi_account_origins; accounts from before tracking get an origin row 'legacy'). */
function kpi_v1_lifecycle_set_account_exclusion($cfg, $userId, $exclude)
{
    $userId = (string) $userId;
    if (kpi_v1_auth_read_user($userId) === null) {
        return 'not_found';
    }
    $now = gmdate('Y-m-d H:i:s');
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            kpi_v1_db($cfg)->prepare(
                'INSERT INTO kpi_account_origins (user_id, origin, matched_deletion_id, exclude_from_metrics, created_at)
                 VALUES (?, \'legacy\', NULL, ?, ?)
                 ON DUPLICATE KEY UPDATE exclude_from_metrics = VALUES(exclude_from_metrics)'
            )->execute([$userId, $exclude ? 1 : 0, $now]);
            return 'ok';
        }
        $out = kpi_v1_lifecycle_file_tx(function ($d, $o) use ($userId, $exclude, $now) {
            if (!isset($o[$userId]) || !is_array($o[$userId])) {
                $o[$userId] = ['origin' => 'legacy', 'matchedLifecycleId' => null, 'excludeFromMetrics' => false, 'createdAt' => $now];
            }
            $o[$userId]['excludeFromMetrics'] = (bool) $exclude;
            return [$d, $o, 'ok'];
        });
        return $out === null ? 'failed' : $out;
    } catch (Throwable $e) {
        return 'failed';
    }
}

/** @return array<string,array{origin:string,excludeFromMetrics:bool}> userId => origin (missing = legacy) */
function kpi_v1_lifecycle_origins_map($cfg)
{
    $out = [];
    try {
        if (kpi_v1_storage_is_mysql($cfg)) {
            $st = kpi_v1_db($cfg)->query('SELECT user_id, origin, exclude_from_metrics FROM kpi_account_origins');
            foreach ($st->fetchAll(PDO::FETCH_ASSOC) as $r) {
                $out[(string) $r['user_id']] = ['origin' => (string) $r['origin'], 'excludeFromMetrics' => (int) $r['exclude_from_metrics'] === 1];
            }
            return $out;
        }
        foreach (kpi_v1_lifecycle_file_read('origins') ?: [] as $uid => $r) {
            if (is_array($r)) {
                $out[(string) $uid] = ['origin' => (string) ($r['origin'] ?? 'legacy'), 'excludeFromMetrics' => !empty($r['excludeFromMetrics'])];
            }
        }
    } catch (Throwable $e) {
        // Missing table (migration not applied): every account shows as legacy.
    }
    return $out;
}

/* ---------- Metrics ---------- */

function kpi_v1_lifecycle_jst()
{
    return new DateTimeZone('Asia/Tokyo');
}

/** @return string YYYY-MM of the current JST month */
function kpi_v1_lifecycle_current_month()
{
    return (new DateTimeImmutable('now', kpi_v1_lifecycle_jst()))->format('Y-m');
}

function kpi_v1_lifecycle_valid_month($month)
{
    return is_string($month) && preg_match('/^(\d{4})-(0[1-9]|1[0-2])$/', $month) === 1;
}

function kpi_v1_lifecycle_ts($value)
{
    if ($value === null || $value === '') {
        return null;
    }
    $dt = kpi_v1_lifecycle_dt($value);
    return $dt === null ? null : strtotime($dt . ' UTC');
}

/**
 * @param array[] $users kpi_v1_admin_list_users rows
 * @param array $origins kpi_v1_lifecycle_origins_map
 * @param array[] $rows kpi_v1_lifecycle_all_rows
 */
function kpi_v1_lifecycle_metrics_compute($users, $origins, $rows, $month, $now = null)
{
    $now = $now === null ? time() : (int) $now;
    $start = new DateTimeImmutable($month . '-01 00:00:00', kpi_v1_lifecycle_jst());
    $end = $start->modify('+1 month');
    $s = $start->getTimestamp();
    $e = $end->getTimestamp();

    $active = 0;
    $activeDisabled = 0;
    $excludedAccounts = 0;
    $denominator = 0;
    $new = ['new' => 0, 'returned' => 0, 'other' => 0];
    foreach ($users as $u) {
        if (($u['role'] ?? 'user') !== 'user' || !empty($u['parentUserId'])) {
            continue;
        }
        $o = $origins[(string) $u['userId']] ?? ['origin' => 'legacy', 'excludeFromMetrics' => false];
        if ($o['excludeFromMetrics']) {
            $excludedAccounts++;
            continue;
        }
        $active++;
        if (!empty($u['disabled'])) {
            $activeDisabled++;
        }
        $c = kpi_v1_lifecycle_ts($u['createdAt'] ?? null);
        if ($c === null) {
            continue;
        }
        if ($c < $s) {
            $denominator++;
        } elseif ($c < $e) {
            $key = $o['origin'] === 'returned' ? 'returned' : ($o['origin'] === 'new' || $o['origin'] === 'legacy' ? 'new' : 'other');
            $new[$key]++;
        }
    }

    $numerator = 0;
    $early = 0;
    $childDeletions = 0;
    $excludedRows = 0;
    foreach ($rows as $r) {
        if (!empty($r['excludeFromMetrics'])) {
            $excludedRows++;
            continue;
        }
        $c = kpi_v1_lifecycle_ts($r['accountCreatedAt'] ?? null);
        $d = kpi_v1_lifecycle_ts($r['deletedAt'] ?? null);
        if ($c === null || $d === null) {
            continue;
        }
        $inMonth = $d >= $s && $d < $e;
        if (($r['accountKind'] ?? 'standalone') === 'child') {
            if ($inMonth) {
                $childDeletions++;
            }
            continue;
        }
        if ($c < $s && $d >= $s) {
            $denominator++;
        }
        if ($c >= $s && $c < $e) {
            $origin = (string) ($r['signupOrigin'] ?? 'legacy');
            $key = $origin === 'returned' ? 'returned' : ($origin === 'new' || $origin === 'legacy' ? 'new' : 'other');
            $new[$key]++;
        }
        if ($inMonth) {
            if ($c < $s) {
                $numerator++;
            } else {
                $early++;
            }
        }
    }

    $windowStart = strtotime(KPI_LIFECYCLE_RETENTION, $now);
    return [
        'month' => $month,
        'timezone' => 'Asia/Tokyo',
        'monthStart' => $start->format('c'),
        'monthEnd' => $end->format('c'),
        'monthToDate' => $now >= $s && $now < $e,
        'active' => $active,
        'disabled' => $activeDisabled,
        'newAccounts' => $new['new'] + $new['returned'] + $new['other'],
        'newBreakdown' => $new,
        'returned' => $new['returned'],
        'deleted' => $numerator + $early,
        'churn' => [
            'numerator' => $numerator,
            'denominator' => $denominator,
            'ratePercent' => $denominator > 0 ? round($numerator / $denominator * 100, 2) : null,
        ],
        'earlyChurn' => $early,
        'childDeletions' => $childDeletions,
        'excluded' => ['accounts' => $excludedAccounts, 'historyRows' => $excludedRows],
        'beforeRetentionWindow' => $s < $windowStart,
    ];
}

/** @return array|null metrics, null when history storage is unavailable */
function kpi_v1_lifecycle_metrics($cfg, $month)
{
    $rows = kpi_v1_lifecycle_all_rows($cfg);
    if ($rows === null) {
        return null;
    }
    $users = kpi_v1_admin_list_users($cfg);
    foreach ($users as $i => $u) {
        // Founders listed in founderSuperAdminEmails may still carry role user in storage.
        if (kpi_v1_auth_is_founder_superadmin($u, $cfg)) {
            $users[$i]['role'] = 'founder_superadmin';
        }
    }
    return kpi_v1_lifecycle_metrics_compute($users, kpi_v1_lifecycle_origins_map($cfg), $rows, $month);
}

/** @return string[] selectable months (JST), newest first, within the 3-year retention window */
function kpi_v1_lifecycle_month_options()
{
    $out = [];
    $m = new DateTimeImmutable(kpi_v1_lifecycle_current_month() . '-01', kpi_v1_lifecycle_jst());
    for ($i = 0; $i < 36; $i++) {
        $out[] = $m->format('Y-m');
        $m = $m->modify('-1 month');
    }
    return $out;
}

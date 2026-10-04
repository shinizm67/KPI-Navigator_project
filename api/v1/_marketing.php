<?php
/**
 * Marketing opt-in subscribers + consent evidence (BR-LAUNCH-09 Extension M2).
 *
 * Contract (docs/br-launch-09-marketing-m1-draft.md, D1–D6 frozen 2026-09-29):
 * - A row exists only after an explicit opt-in (Registration checkbox / Settings). Existing users have none.
 * - One row per normalized email. Lifecycle History and this table are never linked (no HMAC / lifecycle id here).
 * - Stop (unsubscribe link / Settings / Delete "stop" / Founder / email change of the old address):
 *   never mailed → row + evidence deleted at once; mailed → evidence-only row (unsubscribed, never mailed again)
 *   until last_marketing_sent_at + 3 years, then purged (特定商取引法 / 特定電子メール法).
 *   Evidence-only keeps wording / source / timestamps / method / last send / retain_until and a marketing-only
 *   irreversible match key + match_key_id. Raw email is cleared. Not the lifecycle HMAC.
 * - Delete Account: a subscribed row needs "keep" or "stop"; "keep" only unlinks the account. Never turned on at delete.
 * - Email change: the subscription follows the account (D4).
 * - Unsubscribe token = HMAC(marketingTokenSecret, per-row nonce); only the nonce and sha256(token) are stored.
 * - Evidence match_key = HMAC(marketingEvidenceSecret, prefix + email). First key id is k1. Token secret is never
 *   used for matching. Lifecycle HMAC key is never used here.
 * - Missing tables (migration not applied) = no subscriber exists; only an opt-in needs the storage.
 * - Nothing here sends mail.
 */

require_once __DIR__ . '/_bootstrap.php';
require_once __DIR__ . '/_auth.php';
require_once __DIR__ . '/_registration.php';

/*
 * Version of the fixed opt-in wording (Registration / Settings). A new wording = a new version + text below.
 * The pages show exactly this sentence (Registration appends an "optional" marker) and send their version.
 */
const KPI_MARKETING_CONSENT_VERSION = 'mkt-2026-09-29';
const KPI_MARKETING_EVIDENCE_RETENTION = '+3 years';
const KPI_MARKETING_MIN_SECRET_LENGTH = 32;
const KPI_MARKETING_EVIDENCE_KEY_ID = 'k1';

function kpi_v1_marketing_consent_texts()
{
    return [
        'mkt-2026-09-29' => [
            'ja' => 'Forge Laboratoryから、KPNの新機能・新サービス・キャンペーン等のお知らせをメールで受け取る',
            'en' => 'Receive emails from Forge Laboratory about new KPN features, new services and campaigns',
            'zh-TW' => '接收 Forge Laboratory 以電子郵件寄送的 KPN 新功能、新服務及活動等通知',
        ],
    ];
}

function kpi_v1_marketing_locale($raw)
{
    $s = strtolower(trim((string) $raw));
    if (strpos($s, 'ja') === 0) {
        return 'ja';
    }
    if (strpos($s, 'zh') === 0) {
        return 'zh-TW';
    }
    return 'en';
}

function kpi_v1_marketing_now()
{
    return gmdate('Y-m-d H:i:s');
}

function kpi_v1_marketing_normalize_email($email)
{
    return strtolower(trim((string) $email));
}

/* ---------- Unsubscribe token ---------- */

function kpi_v1_marketing_dir()
{
    return kpi_v1_file_data_root() . '/marketing';
}

/** Unsubscribe-token secret only. Config `marketingTokenSecret` (>= 32 chars) or a generated file under data/marketing. Never used for evidence match_key. */
function kpi_v1_marketing_token_secret($cfg)
{
    if (isset($cfg['marketingTokenSecret']) && is_string($cfg['marketingTokenSecret'])
        && strlen($cfg['marketingTokenSecret']) >= KPI_MARKETING_MIN_SECRET_LENGTH) {
        return $cfg['marketingTokenSecret'];
    }
    $dir = kpi_v1_marketing_dir();
    if (!is_dir($dir) && !@mkdir($dir, 0750, true)) {
        return null;
    }
    $path = $dir . '/unsub_secret.key';
    if (is_file($path)) {
        $raw = trim((string) @file_get_contents($path));
        return strlen($raw) >= 64 ? $raw : null;
    }
    $secret = bin2hex(random_bytes(32));
    $tmp = $path . '.' . bin2hex(random_bytes(4)) . '.tmp';
    if (@file_put_contents($tmp, $secret, LOCK_EX) === false) {
        return null;
    }
    @chmod($tmp, 0600);
    if (is_file($path) || !@rename($tmp, $path)) {
        @unlink($tmp);
        $raw = trim((string) @file_get_contents($path));
        return strlen($raw) >= 64 ? $raw : null;
    }
    return $secret;
}

function kpi_v1_marketing_b64url($bin)
{
    return rtrim(strtr(base64_encode($bin), '+/', '-_'), '=');
}

function kpi_v1_marketing_token_for_nonce($secret, $nonce)
{
    return kpi_v1_marketing_b64url(hash_hmac('sha256', 'kpn-marketing-unsub|' . $nonce, (string) $secret, true));
}

/**
 * Evidence secret only (config `marketingEvidenceSecret`, >= 32 chars).
 * No file, no auto-generation, no fallback to the unsubscribe-token secret or the account-deletion matching key.
 */
function kpi_v1_marketing_evidence_secret($cfg)
{
    if (isset($cfg['marketingEvidenceSecret']) && is_string($cfg['marketingEvidenceSecret'])
        && strlen($cfg['marketingEvidenceSecret']) >= KPI_MARKETING_MIN_SECRET_LENGTH) {
        return $cfg['marketingEvidenceSecret'];
    }
    return null;
}

/** Active evidence key id (default k1). Invalid id → null (fail closed). */
function kpi_v1_marketing_evidence_key_id($cfg)
{
    $id = isset($cfg['marketingEvidenceKeyId']) && is_string($cfg['marketingEvidenceKeyId'])
        ? trim($cfg['marketingEvidenceKeyId']) : KPI_MARKETING_EVIDENCE_KEY_ID;
    if (!preg_match('/^[A-Za-z0-9_-]{1,16}$/', $id)) {
        return null;
    }
    return $id;
}

/** @return array<string,string> keyId => secret, active first; previous ids kept for the 3-year evidence window */
function kpi_v1_marketing_evidence_secrets($cfg)
{
    $out = [];
    $id = kpi_v1_marketing_evidence_key_id($cfg);
    $secret = kpi_v1_marketing_evidence_secret($cfg);
    if ($id !== null && $secret !== null) {
        $out[$id] = $secret;
    }
    if (isset($cfg['marketingEvidencePreviousSecrets']) && is_array($cfg['marketingEvidencePreviousSecrets'])) {
        foreach ($cfg['marketingEvidencePreviousSecrets'] as $kid => $key) {
            if (is_string($key) && strlen($key) >= KPI_MARKETING_MIN_SECRET_LENGTH
                && preg_match('/^[A-Za-z0-9_-]{1,16}$/', (string) $kid) && !isset($out[(string) $kid])) {
                $out[(string) $kid] = $key;
            }
        }
    }
    return $out;
}

function kpi_v1_marketing_match_key_with_secret($secret, $email)
{
    $norm = kpi_v1_marketing_normalize_email($email);
    if ($secret === null || $secret === '' || $norm === '' || strpos($norm, '@') === false) {
        return null;
    }
    return hash_hmac('sha256', 'kpn-marketing-evidence|' . $norm, (string) $secret);
}

/** Current-secret match_key (new writes). Token / lifecycle secrets are never used. */
function kpi_v1_marketing_match_key($cfg, $email)
{
    return kpi_v1_marketing_match_key_with_secret(kpi_v1_marketing_evidence_secret($cfg), $email);
}

/** @return array{0:string,1:string}|null [matchKey, matchKeyId] */
function kpi_v1_marketing_match_key_current($cfg, $email)
{
    $id = kpi_v1_marketing_evidence_key_id($cfg);
    $key = kpi_v1_marketing_match_key($cfg, $email);
    if ($id === null || $key === null) {
        return null;
    }
    return [$key, $id];
}

/** All match_key candidates for lookup after rotation (current + previous evidence secrets). */
function kpi_v1_marketing_match_keys_for_lookup($cfg, $email)
{
    $out = [];
    foreach (kpi_v1_marketing_evidence_secrets($cfg) as $secret) {
        $k = kpi_v1_marketing_match_key_with_secret($secret, $email);
        if ($k !== null) {
            $out[] = $k;
        }
    }
    return array_values(array_unique($out));
}

function kpi_v1_marketing_token_hash($token)
{
    return hash('sha256', 'kpn-marketing-unsub-token|' . (string) $token);
}

function kpi_v1_marketing_token_well_formed($token)
{
    return is_string($token) && preg_match('/^[A-Za-z0-9_-]{43}$/', $token) === 1;
}

/** @return array{0:string,1:string}|null [nonce, tokenHash] */
function kpi_v1_marketing_new_token($secret)
{
    if ($secret === null) {
        return null;
    }
    $nonce = bin2hex(random_bytes(16));
    return [$nonce, kpi_v1_marketing_token_hash(kpi_v1_marketing_token_for_nonce($secret, $nonce))];
}

/** Plain token for the (later) sender Phase. Never logged. */
function kpi_v1_marketing_token_of_row($cfg, $row)
{
    $secret = kpi_v1_marketing_token_secret($cfg);
    if ($secret === null || empty($row['tokenNonce']) || ($row['status'] ?? '') !== 'subscribed') {
        return null;
    }
    return kpi_v1_marketing_token_for_nonce($secret, (string) $row['tokenNonce']);
}

/* ---------- State changes (pure; storage-independent) ---------- */

function kpi_v1_marketing_event($event, $source, $meta = [])
{
    return [
        'event' => (string) $event,
        'source' => (string) $source,
        'consentTextVersion' => isset($meta['consentTextVersion']) ? (string) $meta['consentTextVersion'] : null,
        'privacyVersion' => isset($meta['privacyVersion']) ? (string) $meta['privacyVersion'] : null,
        'locale' => isset($meta['locale']) ? (string) $meta['locale'] : null,
        'occurredAt' => kpi_v1_marketing_now(),
    ];
}

/**
 * Opt-in (new row or re-subscribe). $consent: source, consentTextVersion, privacyVersion, locale, consentAt?, accountUserId?
 * @return array{0:array,1:array[]} [row, events]
 */
function kpi_v1_marketing_plan_subscribe($old, $email, $consent, $token, $matchKey, $matchKeyId)
{
    $now = kpi_v1_marketing_now();
    $row = is_array($old) ? $old : [
        'id' => null,
        'lastMarketingSentAt' => null,
        'createdAt' => $now,
        'accountUserId' => null,
    ];
    $row['email'] = (string) $email;
    $row['matchKey'] = $matchKey;
    $row['matchKeyId'] = $matchKeyId;
    $row['status'] = 'subscribed';
    $row['locale'] = kpi_v1_marketing_locale($consent['locale'] ?? 'en');
    $row['consentAt'] = isset($consent['consentAt']) && $consent['consentAt'] ? (string) $consent['consentAt'] : $now;
    $row['consentSource'] = (string) $consent['source'];
    $row['consentTextVersion'] = (string) $consent['consentTextVersion'];
    $row['privacyVersionAtConsent'] = (string) $consent['privacyVersion'];
    $row['unsubscribedAt'] = null;
    $row['unsubscribeSource'] = null;
    $row['retainUntil'] = null;
    $row['tokenNonce'] = $token[0];
    $row['tokenHash'] = $token[1];
    if (array_key_exists('accountUserId', $consent)) {
        $row['accountUserId'] = $consent['accountUserId'];
    }
    $row['updatedAt'] = $now;
    return [$row, [kpi_v1_marketing_event('subscribe', $consent['source'], [
        'consentTextVersion' => $row['consentTextVersion'],
        'privacyVersion' => $row['privacyVersionAtConsent'],
        'locale' => $row['locale'],
    ])]];
}

/**
 * Stop sending. Never mailed → null (row + evidence deleted); mailed → evidence-only row until last send + 3 years.
 * @return array{0:array|null,1:array[]}
 */
function kpi_v1_marketing_plan_stop($old, $source, $keepAccountLink)
{
    if (!is_array($old)) {
        return [null, []];
    }
    $now = kpi_v1_marketing_now();
    if (empty($old['lastMarketingSentAt'])) {
        return [null, []];
    }
    $row = $old;
    if ($row['status'] === 'subscribed') {
        $row['unsubscribedAt'] = $now;
        $row['unsubscribeSource'] = (string) $source;
    }
    $row['status'] = 'unsubscribed';
    $row['email'] = null;
    $row['tokenNonce'] = null;
    $row['tokenHash'] = null;
    $row['retainUntil'] = gmdate('Y-m-d H:i:s', strtotime((string) $old['lastMarketingSentAt'] . ' UTC ' . KPI_MARKETING_EVIDENCE_RETENTION));
    if (!$keepAccountLink) {
        $row['accountUserId'] = null;
    }
    $row['updatedAt'] = $now;
    return [$row, $old['status'] === 'subscribed' ? [kpi_v1_marketing_event('unsubscribe', $source)] : []];
}

/* ---------- Storage context ---------- */
/*
 * A context = ['find' => fn(email): row|null, 'findByToken' => fn(hash): row|null, 'findId' => fn(id): row|null,
 *              'all' => fn(): row[], 'apply' => fn(old|null, new|null, events): row|null].
 * apply(old, null) deletes the row and its evidence.
 */

function kpi_v1_marketing_row_from_db($r)
{
    return [
        'id' => (int) $r['id'],
        'email' => ($r['normalized_email'] !== null && $r['normalized_email'] !== '') ? (string) $r['normalized_email'] : null,
        'matchKey' => (!empty($r['match_key'])) ? (string) $r['match_key'] : null,
        'matchKeyId' => (!empty($r['match_key_id'])) ? (string) $r['match_key_id'] : null,
        'status' => (string) $r['status'],
        'locale' => (string) $r['locale'],
        'accountUserId' => $r['account_user_id'] !== null ? (string) $r['account_user_id'] : null,
        'consentAt' => $r['consent_at'],
        'consentSource' => $r['consent_source'],
        'consentTextVersion' => $r['consent_text_version'],
        'privacyVersionAtConsent' => $r['privacy_version_at_consent'],
        'unsubscribedAt' => $r['unsubscribed_at'],
        'unsubscribeSource' => $r['unsubscribe_source'],
        'lastMarketingSentAt' => $r['last_marketing_sent_at'],
        'tokenNonce' => $r['unsub_token_nonce'],
        'tokenHash' => $r['unsub_token_hash'],
        'retainUntil' => $r['retain_until'],
        'createdAt' => (string) $r['created_at'],
        'updatedAt' => (string) $r['updated_at'],
    ];
}

function kpi_v1_marketing_db_is_missing_table(PDOException $e)
{
    return (string) $e->getCode() === '42S02';
}

/** @return bool false when the marketing tables do not exist (throws on other DB errors) */
function kpi_v1_marketing_db_present(PDO $pdo)
{
    try {
        $pdo->query('SELECT id FROM kpi_marketing_subscribers LIMIT 0');
        $pdo->query('SELECT id FROM kpi_marketing_consent_events LIMIT 0');
        return true;
    } catch (PDOException $e) {
        if (kpi_v1_marketing_db_is_missing_table($e)) {
            return false;
        }
        throw $e;
    }
}

function kpi_v1_marketing_db_ctx($cfg, PDO $pdo)
{
    $one = function ($where, $arg) use ($pdo) {
        $st = $pdo->prepare('SELECT * FROM kpi_marketing_subscribers WHERE ' . $where . ' LIMIT 1 FOR UPDATE');
        $st->execute([$arg]);
        $r = $st->fetch(PDO::FETCH_ASSOC);
        return $r ? kpi_v1_marketing_row_from_db($r) : null;
    };
    return [
        'find' => function ($email) use ($one, $cfg) {
            $norm = kpi_v1_marketing_normalize_email($email);
            $hit = $one('normalized_email = ?', $norm);
            if ($hit) {
                return $hit;
            }
            foreach (kpi_v1_marketing_match_keys_for_lookup($cfg, $norm) as $key) {
                $hit = $one('match_key = ?', $key);
                if ($hit) {
                    return $hit;
                }
            }
            return null;
        },
        'findByToken' => function ($hash) use ($one) {
            return $one('unsub_token_hash = ?', (string) $hash);
        },
        'findId' => function ($id) use ($one) {
            return $one('id = ?', (int) $id);
        },
        'all' => function () use ($pdo) {
            $st = $pdo->query('SELECT * FROM kpi_marketing_subscribers ORDER BY id FOR UPDATE');
            return array_map('kpi_v1_marketing_row_from_db', $st->fetchAll(PDO::FETCH_ASSOC));
        },
        'apply' => function ($old, $new, $events) use ($pdo) {
            if ($new === null) {
                if (is_array($old) && $old['id'] !== null) {
                    $pdo->prepare('DELETE FROM kpi_marketing_consent_events WHERE subscriber_id = ?')->execute([(int) $old['id']]);
                    $pdo->prepare('DELETE FROM kpi_marketing_subscribers WHERE id = ?')->execute([(int) $old['id']]);
                }
                return null;
            }
            $vals = [
                $new['email'], $new['matchKey'] ?? null, $new['matchKeyId'] ?? KPI_MARKETING_EVIDENCE_KEY_ID,
                $new['status'], $new['locale'], $new['accountUserId'], $new['consentAt'],
                $new['consentSource'], $new['consentTextVersion'], $new['privacyVersionAtConsent'], $new['unsubscribedAt'],
                $new['unsubscribeSource'], $new['lastMarketingSentAt'], $new['tokenNonce'], $new['tokenHash'], $new['retainUntil'],
                $new['updatedAt'],
            ];
            if ($new['id'] === null) {
                $pdo->prepare(
                    'INSERT INTO kpi_marketing_subscribers (normalized_email, match_key, match_key_id, status, locale, account_user_id, consent_at, consent_source,
                       consent_text_version, privacy_version_at_consent, unsubscribed_at, unsubscribe_source, last_marketing_sent_at,
                       unsub_token_nonce, unsub_token_hash, retain_until, updated_at, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                )->execute(array_merge($vals, [$new['createdAt']]));
                $new['id'] = (int) $pdo->lastInsertId();
            } else {
                $pdo->prepare(
                    'UPDATE kpi_marketing_subscribers SET normalized_email = ?, match_key = ?, match_key_id = ?, status = ?, locale = ?, account_user_id = ?, consent_at = ?,
                       consent_source = ?, consent_text_version = ?, privacy_version_at_consent = ?, unsubscribed_at = ?,
                       unsubscribe_source = ?, last_marketing_sent_at = ?, unsub_token_nonce = ?, unsub_token_hash = ?,
                       retain_until = ?, updated_at = ? WHERE id = ?'
                )->execute(array_merge($vals, [(int) $new['id']]));
            }
            $ins = $pdo->prepare(
                'INSERT INTO kpi_marketing_consent_events (subscriber_id, event, source, consent_text_version, privacy_version, locale, occurred_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)'
            );
            foreach ($events as $ev) {
                $ins->execute([(int) $new['id'], $ev['event'], $ev['source'], $ev['consentTextVersion'], $ev['privacyVersion'],
                               $ev['locale'], $ev['occurredAt']]);
            }
            return $new;
        },
    ];
}

function kpi_v1_marketing_file_path($name)
{
    return kpi_v1_marketing_dir() . '/' . $name . '.json';
}

function kpi_v1_marketing_file_read($name)
{
    $path = kpi_v1_marketing_file_path($name);
    if (!is_file($path)) {
        return [];
    }
    $data = json_decode((string) @file_get_contents($path), true);
    return is_array($data) ? $data : null;
}

/** File-mode context over in-memory arrays (the caller persists them). */
function kpi_v1_marketing_file_ctx($cfg, &$subs, &$events)
{
    $find = function ($key, $val) use (&$subs) {
        foreach ($subs as $r) {
            if ((string) ($r[$key] ?? '') !== '' && (string) $r[$key] === (string) $val) {
                return $r;
            }
        }
        return null;
    };
    return [
        'find' => function ($email) use ($find, $cfg) {
            $norm = kpi_v1_marketing_normalize_email($email);
            $hit = $find('email', $norm);
            if ($hit) {
                return $hit;
            }
            foreach (kpi_v1_marketing_match_keys_for_lookup($cfg, $norm) as $key) {
                $hit = $find('matchKey', $key);
                if ($hit) {
                    return $hit;
                }
            }
            return null;
        },
        'findByToken' => function ($hash) use ($find) {
            return $find('tokenHash', $hash);
        },
        'findId' => function ($id) use ($find) {
            return $find('id', (int) $id);
        },
        'all' => function () use (&$subs) {
            return array_values($subs);
        },
        'apply' => function ($old, $new, $evs) use (&$subs, &$events) {
            if ($new === null) {
                if (is_array($old) && $old['id'] !== null) {
                    $id = (int) $old['id'];
                    $subs = array_values(array_filter($subs, function ($r) use ($id) {
                        return (int) $r['id'] !== $id;
                    }));
                    $events = array_values(array_filter($events, function ($e) use ($id) {
                        return (int) $e['subscriberId'] !== $id;
                    }));
                }
                return null;
            }
            if ($new['id'] === null) {
                $max = 0;
                foreach ($subs as $r) {
                    $max = max($max, (int) $r['id']);
                }
                $new['id'] = $max + 1;
                $subs[] = $new;
            } else {
                foreach ($subs as $i => $r) {
                    if ((int) $r['id'] === (int) $new['id']) {
                        $subs[$i] = $new;
                    }
                }
            }
            foreach ($evs as $ev) {
                $events[] = array_merge(['subscriberId' => (int) $new['id']], $ev);
            }
            return $new;
        },
    ];
}

/**
 * Runs $fn($ctx) against the marketing store.
 * MySQL with $pdo: inside the caller's transaction (exceptions propagate). Without $pdo: own transaction.
 * @return array{0:string,1?:mixed} ['ok', result] | ['absent'] (no tables: nothing subscribed) | ['failed']
 */
function kpi_v1_marketing_run($cfg, callable $fn, $pdo = null)
{
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        if ($pdo instanceof PDO) {
            if (!kpi_v1_marketing_db_present($pdo)) {
                return ['absent'];
            }
            return ['ok', $fn(kpi_v1_marketing_db_ctx($cfg, $pdo))];
        }
        try {
            $pdo = kpi_v1_db($cfg);
            if (!kpi_v1_marketing_db_present($pdo)) {
                return ['absent'];
            }
            $pdo->beginTransaction();
            $out = $fn(kpi_v1_marketing_db_ctx($cfg, $pdo));
            $pdo->commit();
            return ['ok', $out];
        } catch (Throwable $e) {
            if ($pdo instanceof PDO && $pdo->inTransaction()) {
                $pdo->rollBack();
            }
            error_log('kpn marketing: storage failure ' . get_class($e));
            return ['failed'];
        }
    }
    $dir = kpi_v1_marketing_dir();
    if (!is_dir($dir) && !@mkdir($dir, 0750, true)) {
        return ['failed'];
    }
    $lock = @fopen($dir . '/marketing.lock', 'c+');
    if ($lock === false || !flock($lock, LOCK_EX)) {
        if ($lock !== false) {
            fclose($lock);
        }
        return ['failed'];
    }
    try {
        $subs = kpi_v1_marketing_file_read('subscribers');
        $events = kpi_v1_marketing_file_read('events');
        if ($subs === null || $events === null) {
            return ['failed'];
        }
        $subs0 = $subs;
        $events0 = $events;
        $out = $fn(kpi_v1_marketing_file_ctx($cfg, $subs, $events));
        if ($subs !== $subs0 && !kpi_v1_registration_write_json_atomic(kpi_v1_marketing_file_path('subscribers'), array_values($subs))) {
            return ['failed'];
        }
        if ($events !== $events0 && !kpi_v1_registration_write_json_atomic(kpi_v1_marketing_file_path('events'), array_values($events))) {
            kpi_v1_registration_write_json_atomic(kpi_v1_marketing_file_path('subscribers'), array_values($subs0));
            return ['failed'];
        }
        return ['ok', $out];
    } catch (Throwable $e) {
        error_log('kpn marketing: storage failure ' . get_class($e));
        return ['failed'];
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

/** File mode: raw copies so a later failure of the surrounding operation can put the store back. */
function kpi_v1_marketing_file_snapshot()
{
    $out = [];
    foreach (['subscribers', 'events'] as $name) {
        $p = kpi_v1_marketing_file_path($name);
        $out[$name] = is_file($p) ? (string) @file_get_contents($p) : null;
    }
    return $out;
}

function kpi_v1_marketing_file_restore($snap)
{
    foreach ((array) $snap as $name => $raw) {
        $p = kpi_v1_marketing_file_path($name);
        if ($raw === null) {
            @unlink($p);
        } else {
            @file_put_contents($p, $raw, LOCK_EX);
        }
    }
}

/* ---------- Operations (take a context) ---------- */

/** @return array subscribed row (throws when the token secret is unavailable) */
function kpi_v1_marketing_op_subscribe($cfg, $ctx, $email, $consent)
{
    $token = kpi_v1_marketing_new_token(kpi_v1_marketing_token_secret($cfg));
    $mk = kpi_v1_marketing_match_key_current($cfg, $email);
    if ($token === null) {
        throw new RuntimeException('marketing token secret unavailable');
    }
    if ($mk === null) {
        throw new RuntimeException('marketing evidence secret unavailable');
    }
    $old = $ctx['find']($email);
    list($new, $events) = kpi_v1_marketing_plan_subscribe($old, $email, $consent, $token, $mk[0], $mk[1]);
    return $ctx['apply']($old, $new, $events);
}

/** @return string stopped | none */
function kpi_v1_marketing_op_stop_row($ctx, $old, $source, $keepAccountLink)
{
    if (!is_array($old)) {
        return 'none';
    }
    list($new, $events) = kpi_v1_marketing_plan_stop($old, $source, $keepAccountLink);
    $ctx['apply']($old, $new, $events);
    return 'stopped';
}

/**
 * Delete Account (inside the delete transaction). $choice: keep | stop | null.
 * @return string done | choice_required
 */
function kpi_v1_marketing_op_account_deleted($ctx, $email, $choice)
{
    $old = $ctx['find']($email);
    if (!is_array($old)) {
        return 'done';
    }
    if ($old['status'] === 'subscribed') {
        if ($choice === 'keep') {
            $new = $old;
            $new['accountUserId'] = null;
            $new['updatedAt'] = kpi_v1_marketing_now();
            $ctx['apply']($old, $new, [kpi_v1_marketing_event('keep_after_delete', 'delete_account')]);
            return 'done';
        }
        if ($choice !== 'stop') {
            return 'choice_required';
        }
        kpi_v1_marketing_op_stop_row($ctx, $old, 'delete_stop', false);
        return 'done';
    }
    /* Evidence-only row: stays under legal hold, loses the account link. */
    kpi_v1_marketing_op_stop_row($ctx, $old, 'delete_account', false);
    return 'done';
}

/**
 * Email change (D4, inside the change transaction): the subscription follows the account to the new address.
 * The old address keeps evidence only if it was ever mailed.
 */
function kpi_v1_marketing_op_email_changed($cfg, $ctx, $userId, $oldEmail, $newEmail)
{
    $a = $ctx['find']($oldEmail);
    $b = $ctx['find']($newEmail);
    if (!is_array($a) || $a['status'] !== 'subscribed') {
        if (is_array($a)) {
            kpi_v1_marketing_op_stop_row($ctx, $a, 'email_changed', false);
        }
        return;
    }
    if ($b === null && empty($a['lastMarketingSentAt'])) {
        $token = kpi_v1_marketing_new_token(kpi_v1_marketing_token_secret($cfg));
        if ($token === null) {
            throw new RuntimeException('marketing token secret unavailable');
        }
        $new = $a;
        $new['email'] = (string) $newEmail;
        $mk = kpi_v1_marketing_match_key_current($cfg, $newEmail);
        if ($mk === null) {
            throw new RuntimeException('marketing evidence secret unavailable');
        }
        $new['matchKey'] = $mk[0];
        $new['matchKeyId'] = $mk[1];
        $new['accountUserId'] = (string) $userId;
        $new['tokenNonce'] = $token[0];
        $new['tokenHash'] = $token[1];
        $new['updatedAt'] = kpi_v1_marketing_now();
        $ctx['apply']($a, $new, [kpi_v1_marketing_event('email_changed', 'email_change', ['locale' => $a['locale']])]);
        return;
    }
    kpi_v1_marketing_op_stop_row($ctx, $a, 'email_changed', false);
    kpi_v1_marketing_op_subscribe($cfg, $ctx, $newEmail, [
        'source' => 'email_change',
        'consentAt' => $a['consentAt'],
        'consentTextVersion' => $a['consentTextVersion'],
        'privacyVersion' => $a['privacyVersionAtConsent'],
        'locale' => $a['locale'],
        'accountUserId' => (string) $userId,
    ]);
}

/* ---------- Entry points ---------- */

/** Registration body → consent array, null (not requested) or ['error' => code]. */
function kpi_v1_marketing_consent_from_registration($body)
{
    if (!isset($body['marketingOptIn']) || $body['marketingOptIn'] !== true) {
        return null;
    }
    $version = isset($body['marketingConsentVersion']) && is_string($body['marketingConsentVersion'])
        ? trim($body['marketingConsentVersion']) : '';
    if ($version !== KPI_MARKETING_CONSENT_VERSION) {
        return ['error' => 'marketing_consent_outdated'];
    }
    return [
        'source' => 'registration',
        'consentTextVersion' => KPI_MARKETING_CONSENT_VERSION,
        'privacyVersion' => KPI_PRIVACY_VERSION,
        'locale' => kpi_v1_marketing_locale($body['marketingLocale'] ?? ''),
    ];
}

/**
 * Registration hook (called with the new account inside the account + consent write).
 * @return bool false = roll the registration back (fail closed)
 */
function kpi_v1_marketing_on_registration($cfg, $user, $consent, $pdo = null)
{
    $consent['accountUserId'] = (string) $user['userId'];
    $res = kpi_v1_marketing_run($cfg, function ($ctx) use ($cfg, $user, $consent) {
        return kpi_v1_marketing_op_subscribe($cfg, $ctx, (string) $user['email'], $consent);
    }, $pdo);
    return $res[0] === 'ok';
}

/** @return bool|null subscribed?  null = storage unavailable */
function kpi_v1_marketing_is_subscribed($cfg, $email)
{
    $res = kpi_v1_marketing_run($cfg, function ($ctx) use ($email) {
        $row = $ctx['find'](kpi_v1_marketing_normalize_email($email));
        return is_array($row) && $row['status'] === 'subscribed';
    });
    if ($res[0] === 'absent') {
        return false;
    }
    return $res[0] === 'ok' ? (bool) $res[1] : null;
}

/**
 * Public unsubscribe by token. Always the same answer for the caller; returns whether a row was found (internal).
 * @return string done | unavailable
 */
function kpi_v1_marketing_unsubscribe_by_token($cfg, $token, $source, &$matched = null)
{
    $matched = false;
    if (!kpi_v1_marketing_token_well_formed($token)) {
        return 'done';
    }
    $hash = kpi_v1_marketing_token_hash($token);
    $res = kpi_v1_marketing_run($cfg, function ($ctx) use ($hash, $source) {
        $row = $ctx['findByToken']($hash);
        if (!is_array($row) || $row['status'] !== 'subscribed' || !hash_equals((string) $row['tokenHash'], $hash)) {
            return false;
        }
        kpi_v1_marketing_op_stop_row($ctx, $row, $source, true);
        return true;
    });
    if ($res[0] === 'failed') {
        return 'unavailable';
    }
    $matched = $res[0] === 'ok' && $res[1] === true;
    return 'done';
}

const KPI_MARKETING_UNSUB_REASONS = ['too_many', 'not_relevant', 'not_requested', 'other'];

/** Public unsubscribe limits (counter files shared with registration, separate buckets). */
function kpi_v1_marketing_rate_limits($cfg)
{
    return [
        'marketing_unsub_global' => [kpi_v1_registration_int_cfg($cfg, 'marketingUnsubscribeGlobalMax', 300, 1, 100000), 600],
        'marketing_unsub_token' => [kpi_v1_registration_int_cfg($cfg, 'marketingUnsubscribeTokenMax', 20, 1, 1000), 600],
    ];
}

/** 503 when the counter storage is unavailable, 429 when the bucket is full. */
function kpi_v1_marketing_rate_gate($cfg, $bucket, $key)
{
    $allowed = kpi_v1_registration_rate_allow($cfg, $bucket, $key, null, kpi_v1_marketing_rate_limits($cfg));
    if ($allowed === null) {
        kpi_v1_json_out(503, ['ok' => false, 'error' => 'unavailable']);
    }
    if ($allowed === false) {
        kpi_v1_json_out(429, ['ok' => false, 'error' => 'rate_limited']);
    }
}

/** Optional unsubscribe reason, stored without email / token / IP (like anonymized feedback). */
function kpi_v1_marketing_record_reason($reason, $note)
{
    $reason = is_string($reason) && in_array($reason, KPI_MARKETING_UNSUB_REASONS, true) ? $reason : null;
    $note = is_string($note) ? trim(mb_substr($note, 0, 200)) : '';
    if ($reason === null && $note === '') {
        return true;
    }
    $dir = kpi_v1_marketing_dir();
    if (!is_dir($dir) && !@mkdir($dir, 0750, true)) {
        return false;
    }
    $line = json_encode(['at' => gmdate('Y-m-d\TH:i:s\Z'), 'reason' => $reason, 'note' => $note],
                        JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n";
    return @file_put_contents($dir . '/unsubscribe_reasons.jsonl', $line, FILE_APPEND | LOCK_EX) === strlen($line);
}

/** Purge evidence-only rows past retain_until. @return int|null rows purged, null on failure */
function kpi_v1_marketing_purge($cfg)
{
    $now = kpi_v1_marketing_now();
    $res = kpi_v1_marketing_run($cfg, function ($ctx) use ($cfg, $now) {
        return kpi_v1_marketing_purge_in($cfg, $ctx, $now);
    });
    if ($res[0] === 'absent') {
        return 0;
    }
    return $res[0] === 'ok' ? (int) $res[1] : null;
}

/** Deletes unsubscribed rows whose evidence period has ended (or that never needed one). */
function kpi_v1_marketing_purge_in($cfg, $ctx, $now)
{
    $n = 0;
    foreach ($ctx['all']() as $r) {
        if ($r['status'] === 'unsubscribed' && (empty($r['retainUntil']) || (string) $r['retainUntil'] < $now)) {
            $ctx['apply']($r, null, []);
            $n++;
        }
    }
    return $n;
}

/* ---------- Founder ---------- */

/** Founder view of a row: raw email only while subscribed (incl. keep-after-delete). Token / match key never. */
function kpi_v1_marketing_public_row($r)
{
    $iso = function ($v) {
        return $v ? gmdate('Y-m-d\TH:i:s\Z', strtotime((string) $v . ' UTC')) : null;
    };
    $raw = (!empty($r['email']) && ($r['status'] ?? '') === 'subscribed') ? (string) $r['email'] : null;
    return [
        'id' => (int) $r['id'],
        'email' => $raw,
        'status' => (string) $r['status'],
        'evidenceOnly' => $r['status'] === 'unsubscribed',
        'locale' => (string) $r['locale'],
        'hasAccount' => !empty($r['accountUserId']),
        'consentAt' => $iso($r['consentAt']),
        'consentSource' => $r['consentSource'],
        'consentTextVersion' => $r['consentTextVersion'],
        'privacyVersionAtConsent' => $r['privacyVersionAtConsent'],
        'unsubscribedAt' => $iso($r['unsubscribedAt']),
        'unsubscribeSource' => $r['unsubscribeSource'],
        'lastMarketingSentAt' => $iso($r['lastMarketingSentAt']),
        'retainUntil' => $iso($r['retainUntil']),
        'createdAt' => $iso($r['createdAt']),
        'updatedAt' => $iso($r['updatedAt']),
    ];
}

/** @return array|null ['ready' => bool, 'rows' => [...]] */
function kpi_v1_marketing_founder_list($cfg)
{
    kpi_v1_marketing_purge($cfg);
    $res = kpi_v1_marketing_run($cfg, function ($ctx) {
        return $ctx['all']();
    });
    if ($res[0] === 'absent') {
        return ['ready' => false, 'rows' => []];
    }
    if ($res[0] !== 'ok') {
        return null;
    }
    return ['ready' => true, 'rows' => array_map('kpi_v1_marketing_public_row', $res[1])];
}

/**
 * Founder manual action. unsubscribe = stop (source founder); erase = delete now if never mailed,
 * otherwise stop to evidence-only (legal hold; an evidence-only row cannot be erased before retain_until).
 * @return array{0:string,1?:string|null} [result, retainUntil]
 *   result: unsubscribed | erased | evidence_only | legal_hold | not_found | already | failed
 */
function kpi_v1_marketing_founder_action($cfg, $id, $action)
{
    $res = kpi_v1_marketing_run($cfg, function ($ctx) use ($id, $action) {
        $row = $ctx['findId']($id);
        if (!is_array($row)) {
            return ['not_found', null];
        }
        if ($action === 'unsubscribe') {
            if ($row['status'] !== 'subscribed') {
                return ['already', $row['retainUntil']];
            }
            list($new, $events) = kpi_v1_marketing_plan_stop($row, 'founder', true);
            $ctx['apply']($row, $new, $events);
            return [$new === null ? 'erased' : 'unsubscribed', $new === null ? null : $new['retainUntil']];
        }
        if (empty($row['lastMarketingSentAt'])) {
            $ctx['apply']($row, null, []);
            return ['erased', null];
        }
        if ($row['status'] === 'subscribed') {
            list($new, $events) = kpi_v1_marketing_plan_stop($row, 'founder', false);
            $ctx['apply']($row, $new, $events);
            return ['evidence_only', $new['retainUntil']];
        }
        return ['legal_hold', $row['retainUntil']];
    });
    if ($res[0] === 'absent') {
        return ['not_found', null];
    }
    return $res[0] === 'ok' ? $res[1] : ['failed', null];
}

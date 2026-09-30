<?php
/**
 * Public registration helpers: legal consent record, status, abuse protection.
 * Used by auth/register.php and auth/registration-status.php; auth/change-password.php reuses the password rule.
 * admin-create-user.php / login.php / reset-password.php keep their own contracts.
 */

require_once __DIR__ . '/_bootstrap.php';
require_once __DIR__ . '/_auth.php';

/* Canonical legal versions = "Last updated" date on legal/terms and legal/privacy (JP / EN / ZH-TW share one version). */
const KPI_TERMS_VERSION = '2026-02-16';
const KPI_PRIVACY_VERSION = '2026-09-30';

const KPI_CONSENT_SOURCE_PUBLIC_REGISTRATION = 'public_registration';

function kpi_v1_registration_enabled($cfg)
{
    return !empty($cfg['registrationEnabled']);
}

function kpi_v1_registration_int_cfg($cfg, $key, $default, $min, $max)
{
    $n = isset($cfg[$key]) ? (int) $cfg[$key] : (int) $default;
    if ($n < $min) {
        $n = $min;
    }
    if ($n > $max) {
        $n = $max;
    }
    return $n;
}

function kpi_v1_registration_dir()
{
    $dir = __DIR__ . '/data/registration';
    if (!is_dir($dir)) {
        @mkdir($dir, 0750, true);
    }
    return $dir;
}

/* ---------- Password (public registration + self password change; matches the Registration page rule) ---------- */

function kpi_v1_registration_password_ok($password)
{
    $pw = (string) $password;
    if (strlen($pw) < 8 || strlen($pw) > 1024) {
        return false;
    }
    return preg_match('/[a-zA-Z]/', $pw) === 1
        && preg_match('/[0-9]/', $pw) === 1
        && preg_match('/[^a-zA-Z0-9]/', $pw) === 1;
}

/* ---------- Form token (minimum submit time) ---------- */

function kpi_v1_registration_form_secret()
{
    $path = kpi_v1_registration_dir() . '/form_secret.key';
    if (is_file($path)) {
        $raw = trim((string) @file_get_contents($path));
        if (strlen($raw) >= 64) {
            return $raw;
        }
    }
    $secret = bin2hex(random_bytes(32));
    $tmp = $path . '.' . bin2hex(random_bytes(4)) . '.tmp';
    if (@file_put_contents($tmp, $secret, LOCK_EX) === false) {
        return null;
    }
    @chmod($tmp, 0600);
    if (is_file($path)) {
        @unlink($tmp);
        $raw = trim((string) @file_get_contents($path));
        return strlen($raw) >= 64 ? $raw : null;
    }
    if (!@rename($tmp, $path)) {
        @unlink($tmp);
        return null;
    }
    return $secret;
}

function kpi_v1_registration_issue_form_token($now = null)
{
    $secret = kpi_v1_registration_form_secret();
    if ($secret === null) {
        return null;
    }
    $ts = (string) ($now === null ? time() : (int) $now);
    return $ts . '.' . hash_hmac('sha256', 'kpn-reg-form|' . $ts, $secret);
}

/**
 * @return string|null null = ok; otherwise 'form_token_invalid' | 'too_fast' | 'form_token_expired'
 */
function kpi_v1_registration_check_form_token($cfg, $token, $now = null)
{
    $token = (string) $token;
    if (!preg_match('/^(\d{9,12})\.([0-9a-f]{64})$/', $token, $m)) {
        return 'form_token_invalid';
    }
    $secret = kpi_v1_registration_form_secret();
    if ($secret === null) {
        return 'form_token_invalid';
    }
    if (!hash_equals(hash_hmac('sha256', 'kpn-reg-form|' . $m[1], $secret), $m[2])) {
        return 'form_token_invalid';
    }
    $now = $now === null ? time() : (int) $now;
    $age = $now - (int) $m[1];
    $min = kpi_v1_registration_int_cfg($cfg, 'registrationMinSubmitSeconds', 2, 1, 30);
    $max = kpi_v1_registration_int_cfg($cfg, 'registrationFormMaxAgeSeconds', 86400, 600, 604800);
    if ($age < $min) {
        return 'too_fast';
    }
    if ($age > $max) {
        return 'form_token_expired';
    }
    return null;
}

/**
 * Honeypot + form token. Returns the internal reason, or null when the request looks human.
 * Callers answer every reason with the same generic registration_rejected.
 */
function kpi_v1_registration_bot_reason($cfg, $body)
{
    /* The Registration page always sends extraNote as ''. Missing, non-string or filled = not our form / a bot. */
    if (!array_key_exists('extraNote', $body) || $body['extraNote'] !== '') {
        return 'honeypot';
    }
    return kpi_v1_registration_check_form_token($cfg, isset($body['formToken']) ? $body['formToken'] : '');
}

/**
 * ConoHa WING gives no trusted client-IP contract, and its LiteSpeed rewrites REMOTE_ADDR from these
 * client-sent headers. The hosting front never sends them on normal requests, so their presence = spoofing attempt.
 */
function kpi_v1_registration_has_forwarded_ip_header()
{
    return isset($_SERVER['HTTP_CF_CONNECTING_IP']) || isset($_SERVER['HTTP_X_REAL_IP']);
}

/* ---------- Rate limit (file counters under data/registration; no new infra) ---------- */

/* REMOTE_ADDR is not trustworthy on this hosting: the 'ip' bucket is an auxiliary signal, the 'global_*' buckets are the volume bound. */
function kpi_v1_registration_client_ip()
{
    return isset($_SERVER['REMOTE_ADDR']) ? (string) $_SERVER['REMOTE_ADDR'] : 'unknown';
}

function kpi_v1_registration_rate_limits($cfg)
{
    return [
        'global_attempt' => [
            kpi_v1_registration_int_cfg($cfg, 'registrationGlobalAttemptMax', 30, 1, 10000),
            kpi_v1_registration_int_cfg($cfg, 'registrationGlobalAttemptWindowSeconds', 600, 60, 86400),
        ],
        'global_create_hour' => [
            kpi_v1_registration_int_cfg($cfg, 'registrationGlobalCreateHourMax', 10, 1, 10000),
            3600,
        ],
        'global_create_day' => [
            kpi_v1_registration_int_cfg($cfg, 'registrationGlobalCreateDayMax', 40, 1, 10000),
            86400,
        ],
        'ip' => [
            kpi_v1_registration_int_cfg($cfg, 'registrationRateLimitIpMax', 10, 1, 1000),
            kpi_v1_registration_int_cfg($cfg, 'registrationRateLimitIpWindowSeconds', 600, 60, 86400),
        ],
        'email' => [
            kpi_v1_registration_int_cfg($cfg, 'registrationRateLimitEmailMax', 5, 1, 1000),
            kpi_v1_registration_int_cfg($cfg, 'registrationRateLimitEmailWindowSeconds', 3600, 60, 86400),
        ],
    ];
}

/**
 * Sliding window. Every attempt counts (success or failure).
 * $limits: other callers' buckets (same counter files); default = the registration buckets.
 * @return bool|null true = allowed, false = limited, null = counter storage unavailable
 */
function kpi_v1_registration_rate_allow($cfg, $bucket, $key, $now = null, $limits = null)
{
    $limits = is_array($limits) ? $limits : kpi_v1_registration_rate_limits($cfg);
    if (!isset($limits[$bucket])) {
        return null;
    }
    list($max, $window) = $limits[$bucket];
    $now = $now === null ? time() : (int) $now;
    $path = kpi_v1_registration_dir() . '/rl_' . hash('sha256', $bucket . '|' . strtolower((string) $key)) . '.json';
    $fh = @fopen($path, 'c+');
    if ($fh === false) {
        return null;
    }
    if (!flock($fh, LOCK_EX)) {
        fclose($fh);
        return null;
    }
    try {
        $raw = stream_get_contents($fh);
        $data = json_decode((string) $raw, true);
        $hits = [];
        if (is_array($data) && isset($data['hits']) && is_array($data['hits'])) {
            foreach ($data['hits'] as $t) {
                $t = (int) $t;
                if ($t > $now - $window && $t <= $now) {
                    $hits[] = $t;
                }
            }
        }
        $allowed = count($hits) < $max;
        if ($allowed) {
            $hits[] = $now;
        }
        $json = json_encode(['hits' => $hits]);
        if (ftruncate($fh, 0) === false || rewind($fh) === false || fwrite($fh, $json) === false) {
            return null;
        }
        fflush($fh);
        return $allowed;
    } finally {
        flock($fh, LOCK_UN);
        fclose($fh);
    }
}

/** Exits with 503 when the counter storage is unavailable (fail closed) and 429 when the bucket is full. */
function kpi_v1_registration_rate_gate($cfg, $bucket, $key)
{
    $allowed = kpi_v1_registration_rate_allow($cfg, $bucket, $key);
    if ($allowed === null) {
        kpi_v1_json_out(503, ['ok' => false, 'error' => 'registration_unavailable']);
    }
    if ($allowed === false) {
        kpi_v1_json_out(429, ['ok' => false, 'error' => 'rate_limited']);
    }
}

/* ---------- Consent ---------- */

/**
 * @return array{error:string}|array{record:array}
 */
function kpi_v1_registration_consent_from_body($body)
{
    if (!isset($body['consentAccepted']) || $body['consentAccepted'] !== true) {
        return ['error' => 'consent_required'];
    }
    $terms = isset($body['termsVersion']) && is_string($body['termsVersion']) ? trim($body['termsVersion']) : '';
    $privacy = isset($body['privacyVersion']) && is_string($body['privacyVersion']) ? trim($body['privacyVersion']) : '';
    if ($terms === '' || $privacy === '') {
        return ['error' => 'consent_required'];
    }
    if ($terms !== KPI_TERMS_VERSION || $privacy !== KPI_PRIVACY_VERSION) {
        return ['error' => 'consent_outdated'];
    }
    return [
        'record' => [
            'termsVersion' => KPI_TERMS_VERSION,
            'privacyVersion' => KPI_PRIVACY_VERSION,
            'acceptedAt' => gmdate('c'),
            'source' => KPI_CONSENT_SOURCE_PUBLIC_REGISTRATION,
        ],
    ];
}

function kpi_v1_consent_dir()
{
    $dir = __DIR__ . '/data/consents';
    if (!is_dir($dir)) {
        @mkdir($dir, 0750, true);
    }
    return $dir;
}

function kpi_v1_consent_file_path($userId)
{
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
    if ($safe === '' || strpos($safe, '_') === 0) {
        return null;
    }
    return kpi_v1_consent_dir() . '/' . $safe . '.jsonl';
}

/** Append-only: one JSON line per acceptance. Existing lines are never rewritten. */
function kpi_v1_consent_file_append($userId, $record)
{
    $path = kpi_v1_consent_file_path($userId);
    if ($path === null) {
        return false;
    }
    $row = [
        'userId' => (string) $userId,
        'termsVersion' => (string) $record['termsVersion'],
        'privacyVersion' => (string) $record['privacyVersion'],
        'acceptedAt' => (string) $record['acceptedAt'],
        'source' => (string) $record['source'],
    ];
    $line = json_encode($row, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n";
    return @file_put_contents($path, $line, FILE_APPEND | LOCK_EX) === strlen($line);
}

/** Append-only insert. Existing rows are never updated or deleted. */
function kpi_v1_consent_db_insert(PDO $pdo, $userId, $record)
{
    $accepted = gmdate('Y-m-d H:i:s', strtotime((string) $record['acceptedAt']) ?: time());
    $st = $pdo->prepare(
        'INSERT INTO kpi_user_consents (user_id, terms_version, privacy_version, accepted_at, source)
         VALUES (?, ?, ?, ?, ?)'
    );
    $st->execute([
        (string) $userId,
        (string) $record['termsVersion'],
        (string) $record['privacyVersion'],
        $accepted,
        (string) $record['source'],
    ]);
}

/* ---------- Account + consent (all or nothing) ---------- */

function kpi_v1_registration_db_insert_user(PDO $pdo, $user)
{
    $now = gmdate('Y-m-d H:i:s');
    $created = gmdate('Y-m-d H:i:s', strtotime((string) $user['createdAt']) ?: time());
    $shapes = [
        [
            'INSERT INTO kpi_users (user_id, email, password_hash, plan, disabled, role, created_at, updated_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            [$user['userId'], $user['email'], $user['passwordHash'], $user['plan'], 0, 'user', $created, $now],
        ],
        [
            'INSERT INTO kpi_users (user_id, email, password_hash, plan, disabled, created_at, updated_at)
             VALUES (?, ?, ?, ?, ?, ?, ?)',
            [$user['userId'], $user['email'], $user['passwordHash'], $user['plan'], 0, $created, $now],
        ],
    ];
    $last = null;
    foreach ($shapes as $shape) {
        try {
            $pdo->prepare($shape[0])->execute($shape[1]);
            return;
        } catch (PDOException $e) {
            $info = $e->errorInfo;
            /* 1054 = unknown column (older kpi_users shape); anything else is final. */
            if (!isset($info[1]) || (int) $info[1] !== 1054) {
                throw $e;
            }
            $last = $e;
        }
    }
    throw $last;
}

function kpi_v1_registration_pdo_is_duplicate(PDOException $e)
{
    $info = $e->errorInfo;
    return isset($info[1]) && (int) $info[1] === 1062;
}

/**
 * Creates the user and its first consent row together. Never leaves a user without consent.
 * MySQL: one transaction. File: registration lock + compensating deletes.
 * $alsoWrite(PDO|null): optional extra write (marketing opt-in) inside the same unit; false = nothing is created.
 *
 * @return string 'ok' | 'email_taken' | 'failed'
 */
function kpi_v1_registration_create_user_with_consent($cfg, $user, $consent, $alsoWrite = null)
{
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        $pdo = kpi_v1_db($cfg);
        try {
            $pdo->beginTransaction();
            kpi_v1_registration_db_insert_user($pdo, $user);
            kpi_v1_consent_db_insert($pdo, $user['userId'], $consent);
            if ($alsoWrite !== null && $alsoWrite($pdo) !== true) {
                $pdo->rollBack();
                return 'failed';
            }
            $pdo->commit();
            return 'ok';
        } catch (PDOException $e) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            return kpi_v1_registration_pdo_is_duplicate($e) ? 'email_taken' : 'failed';
        } catch (Throwable $e) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            return 'failed';
        }
    }
    return kpi_v1_registration_file_create($user, $consent, $alsoWrite);
}

function kpi_v1_registration_write_json_atomic($path, $data)
{
    $tmp = $path . '.' . bin2hex(random_bytes(4)) . '.tmp';
    $json = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false || @file_put_contents($tmp, $json, LOCK_EX) === false) {
        @unlink($tmp);
        return false;
    }
    if (!@rename($tmp, $path)) {
        @unlink($tmp);
        return false;
    }
    return true;
}

function kpi_v1_registration_file_create($user, $consent, $alsoWrite = null)
{
    $lock = @fopen(kpi_v1_registration_dir() . '/register.lock', 'c+');
    if ($lock === false || !flock($lock, LOCK_EX)) {
        if ($lock !== false) {
            fclose($lock);
        }
        return 'failed';
    }
    try {
        $index = kpi_v1_auth_read_email_index();
        if (isset($index[$user['email']])) {
            return 'email_taken';
        }
        $userPath = kpi_v1_auth_user_path($user['userId']);
        $consentPath = kpi_v1_consent_file_path($user['userId']);
        if ($userPath === null || $consentPath === null || is_file($userPath) || is_file($consentPath)) {
            return 'failed';
        }
        if (!kpi_v1_registration_write_json_atomic($userPath, $user)) {
            return 'failed';
        }
        if (!kpi_v1_consent_file_append($user['userId'], $consent)) {
            @unlink($userPath);
            @unlink($consentPath);
            return 'failed';
        }
        $prevIndex = $index;
        $index[$user['email']] = $user['userId'];
        if (!kpi_v1_registration_write_json_atomic(kpi_v1_auth_email_index_path(), $index)) {
            @unlink($consentPath);
            @unlink($userPath);
            return 'failed';
        }
        if ($alsoWrite !== null && $alsoWrite(null) !== true) {
            kpi_v1_registration_write_json_atomic(kpi_v1_auth_email_index_path(), $prevIndex);
            @unlink($consentPath);
            @unlink($userPath);
            return 'failed';
        }
        return 'ok';
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

/* ---------- Public status ---------- */

function kpi_v1_registration_public_status($cfg)
{
    $enabled = kpi_v1_registration_enabled($cfg);
    $out = [
        'ok' => true,
        'registrationEnabled' => $enabled,
        'termsVersion' => KPI_TERMS_VERSION,
        'privacyVersion' => KPI_PRIVACY_VERSION,
    ];
    if ($enabled) {
        $token = kpi_v1_registration_issue_form_token();
        if ($token === null) {
            /* Cannot protect the form: report closed (fail closed). */
            $out['registrationEnabled'] = false;
        } else {
            $out['formToken'] = $token;
        }
    }
    return $out;
}

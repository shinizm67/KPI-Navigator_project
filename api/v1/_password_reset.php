<?php
/**
 * Password reset tokens — hash-only storage, one-time, expiry.
 * MySQL table kpi_password_reset_tokens or file fallback under data/password_reset/.
 */

require_once __DIR__ . '/_bootstrap.php';
require_once __DIR__ . '/_auth.php';
require_once __DIR__ . '/_mail.php';

function kpi_v1_password_reset_ttl_minutes($cfg)
{
    $n = isset($cfg['passwordResetTtlMinutes']) ? (int) $cfg['passwordResetTtlMinutes'] : 30;
    if ($n < 5) {
        $n = 5;
    }
    if ($n > 120) {
        $n = 120;
    }
    return $n;
}

function kpi_v1_password_reset_cooldown_seconds($cfg)
{
    $n = isset($cfg['passwordResetCooldownSeconds']) ? (int) $cfg['passwordResetCooldownSeconds'] : 120;
    if ($n < 30) {
        $n = 30;
    }
    if ($n > 3600) {
        $n = 3600;
    }
    return $n;
}

function kpi_v1_password_reset_public_base($cfg)
{
    if (!empty($cfg['passwordResetBaseUrl'])) {
        return rtrim((string) $cfg['passwordResetBaseUrl'], '/');
    }
    return 'https://forge-laboratory.com/kpi-navigator';
}

function kpi_v1_password_reset_normalize_locale($locale)
{
    $l = strtolower(trim((string) $locale));
    if ($l === 'ja' || $l === 'jp') {
        return 'ja';
    }
    if ($l === 'zh' || $l === 'zh-tw' || $l === 'zh_tw' || $l === 'tw') {
        return 'zh-tw';
    }
    return 'en';
}

function kpi_v1_password_reset_path_for_locale($locale)
{
    $loc = kpi_v1_password_reset_normalize_locale($locale);
    if ($loc === 'ja') {
        return '/reset-password/';
    }
    if ($loc === 'zh-tw') {
        return '/zh-tw/reset-password/';
    }
    return '/en/reset-password/';
}

function kpi_v1_password_reset_token_hash($plainToken)
{
    return hash('sha256', (string) $plainToken);
}

function kpi_v1_password_reset_new_plain_token()
{
    return bin2hex(random_bytes(32)); // 256-bit
}

function kpi_v1_password_reset_dir()
{
    $dir = __DIR__ . '/data/password_reset';
    if (!is_dir($dir)) {
        @mkdir($dir, 0750, true);
    }
    return $dir;
}

function kpi_v1_password_reset_throttle_path($emailKey)
{
    $safe = hash('sha256', strtolower(trim((string) $emailKey)));
    return kpi_v1_password_reset_dir() . '/throttle_' . $safe . '.json';
}

/**
 * Email-keyed cooldown (exists or not). Returns true if allowed.
 */
function kpi_v1_password_reset_throttle_allow($cfg, $emailKey)
{
    $cooldown = kpi_v1_password_reset_cooldown_seconds($cfg);
    $path = kpi_v1_password_reset_throttle_path($emailKey);
    $now = time();
    if (is_file($path)) {
        $raw = json_decode((string) file_get_contents($path), true);
        $last = is_array($raw) && isset($raw['at']) ? (int) $raw['at'] : 0;
        if ($last > 0 && ($now - $last) < $cooldown) {
            return false;
        }
    }
    @file_put_contents(
        $path,
        json_encode(['at' => $now], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
        LOCK_EX
    );
    return true;
}

function kpi_v1_password_reset_invalidate_user_tokens($cfg, $userId)
{
    $userId = (string) $userId;
    if ($userId === '') {
        return;
    }
    $now = gmdate('Y-m-d H:i:s');
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        $pdo = kpi_v1_db($cfg);
        $st = $pdo->prepare(
            'UPDATE kpi_password_reset_tokens SET used_at = ? WHERE user_id = ? AND used_at IS NULL'
        );
        $st->execute([$now, $userId]);
        return;
    }
    $dir = kpi_v1_password_reset_dir();
    foreach (glob($dir . '/tok_*.json') ?: [] as $path) {
        $row = json_decode((string) file_get_contents($path), true);
        if (!is_array($row)) {
            continue;
        }
        if ((string) ($row['userId'] ?? '') !== $userId) {
            continue;
        }
        if (!empty($row['usedAt'])) {
            continue;
        }
        $row['usedAt'] = gmdate('c');
        @file_put_contents($path, json_encode($row, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), LOCK_EX);
    }
}

/**
 * Create token row. Returns plaintext token (for email URL only) or null.
 */
function kpi_v1_password_reset_create_token($cfg, $userId)
{
    $userId = (string) $userId;
    $plain = kpi_v1_password_reset_new_plain_token();
    $hash = kpi_v1_password_reset_token_hash($plain);
    $ttl = kpi_v1_password_reset_ttl_minutes($cfg);
    $expiresTs = time() + ($ttl * 60);
    $expiresAt = gmdate('Y-m-d H:i:s', $expiresTs);
    $createdAt = gmdate('Y-m-d H:i:s');

    kpi_v1_password_reset_invalidate_user_tokens($cfg, $userId);

    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        $pdo = kpi_v1_db($cfg);
        $st = $pdo->prepare(
            'INSERT INTO kpi_password_reset_tokens (user_id, token_hash, expires_at, used_at, created_at)
             VALUES (?, ?, ?, NULL, ?)'
        );
        $st->execute([$userId, $hash, $expiresAt, $createdAt]);
        return $plain;
    }

    $row = [
        'userId' => $userId,
        'tokenHash' => $hash,
        'expiresAt' => gmdate('c', $expiresTs),
        'usedAt' => null,
        'createdAt' => gmdate('c'),
    ];
    $path = kpi_v1_password_reset_dir() . '/tok_' . $hash . '.json';
    if (@file_put_contents($path, json_encode($row, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), LOCK_EX) === false) {
        return null;
    }
    return $plain;
}

/**
 * Lookup unused, unexpired token by plaintext. Returns ['userId'=>..., 'tokenHash'=>...] or null.
 */
function kpi_v1_password_reset_find_valid($cfg, $plainToken)
{
    $plainToken = trim((string) $plainToken);
    if ($plainToken === '' || strlen($plainToken) < 32) {
        return null;
    }
    $hash = kpi_v1_password_reset_token_hash($plainToken);
    $now = time();

    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        $pdo = kpi_v1_db($cfg);
        $st = $pdo->prepare(
            'SELECT user_id, token_hash, expires_at, used_at FROM kpi_password_reset_tokens WHERE token_hash = ? LIMIT 1'
        );
        $st->execute([$hash]);
        $row = $st->fetch(PDO::FETCH_ASSOC);
        if (!$row) {
            return null;
        }
        if ($row['used_at'] !== null && $row['used_at'] !== '') {
            return null;
        }
        $exp = strtotime((string) $row['expires_at'] . ' UTC');
        if ($exp === false || $exp <= $now) {
            return null;
        }
        return [
            'userId' => (string) $row['user_id'],
            'tokenHash' => (string) $row['token_hash'],
        ];
    }

    $path = kpi_v1_password_reset_dir() . '/tok_' . $hash . '.json';
    if (!is_file($path)) {
        return null;
    }
    $row = json_decode((string) file_get_contents($path), true);
    if (!is_array($row)) {
        return null;
    }
    if (!empty($row['usedAt'])) {
        return null;
    }
    $exp = isset($row['expiresAt']) ? strtotime((string) $row['expiresAt']) : false;
    if ($exp === false || $exp <= $now) {
        return null;
    }
    return [
        'userId' => (string) ($row['userId'] ?? ''),
        'tokenHash' => (string) ($row['tokenHash'] ?? $hash),
        '_path' => $path,
    ];
}

function kpi_v1_password_reset_mark_used($cfg, $tokenMeta)
{
    $nowSql = gmdate('Y-m-d H:i:s');
    $hash = (string) ($tokenMeta['tokenHash'] ?? '');
    if ($hash === '') {
        return false;
    }
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        $pdo = kpi_v1_db($cfg);
        $st = $pdo->prepare(
            'UPDATE kpi_password_reset_tokens SET used_at = ? WHERE token_hash = ? AND used_at IS NULL'
        );
        $st->execute([$nowSql, $hash]);
        return $st->rowCount() > 0;
    }
    $path = isset($tokenMeta['_path'])
        ? (string) $tokenMeta['_path']
        : (kpi_v1_password_reset_dir() . '/tok_' . $hash . '.json');
    if (!is_file($path)) {
        return false;
    }
    $row = json_decode((string) file_get_contents($path), true);
    if (!is_array($row) || !empty($row['usedAt'])) {
        return false;
    }
    $row['usedAt'] = gmdate('c');
    return @file_put_contents($path, json_encode($row, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), LOCK_EX) !== false;
}

function kpi_v1_password_reset_mail_copy($locale, $resetUrl, $ttlMinutes)
{
    $loc = kpi_v1_password_reset_normalize_locale($locale);
    if ($loc === 'ja') {
        return [
            'subject' => 'KPN パスワード再設定',
            'body' =>
                "Key Performance Navigator のパスワード再設定リクエストを受け付けました。\n\n" .
                "以下のURLから {$ttlMinutes} 分以内に新しいパスワードを設定してください。\n\n" .
                $resetUrl . "\n\n" .
                "心当たりがない場合はこのメールを無視してください。パスワードは変更されません。\n",
        ];
    }
    if ($loc === 'zh-tw') {
        return [
            'subject' => 'KPN 密碼重設',
            'body' =>
                "我們收到 Key Performance Navigator 的密碼重設請求。\n\n" .
                "請於 {$ttlMinutes} 分鐘內透過以下連結設定新密碼：\n\n" .
                $resetUrl . "\n\n" .
                "若您未提出此請求，請忽略本郵件。密碼不會被變更。\n",
        ];
    }
    return [
        'subject' => 'KPN Password Reset',
        'body' =>
            "We received a password reset request for Key Performance Navigator.\n\n" .
            "Use the link below within {$ttlMinutes} minutes to set a new password:\n\n" .
            $resetUrl . "\n\n" .
            "If you did not request this, ignore this email. Your password will not change.\n",
    ];
}

/**
 * Founder Admin: send reset mail for a known user (honest result, no existence hiding).
 * Reuses token create + mail helpers. Skips anonymous throttle.
 * Never returns token plaintext or password hash.
 *
 * @param array $user auth user row
 * @return array{ok:true,mailed:bool}|array{ok:false,error:string}
 */
function kpi_v1_password_reset_admin_send($cfg, $user, $locale)
{
    if (!is_array($user) || empty($user['userId']) || empty($user['email'])) {
        return ['ok' => false, 'error' => 'user_not_found'];
    }
    if (kpi_v1_auth_user_is_disabled($user)) {
        return ['ok' => false, 'error' => 'user_disabled'];
    }
    $emailNorm = kpi_v1_auth_normalize_email($user['email']);
    if ($emailNorm === null) {
        return ['ok' => false, 'error' => 'invalid_email'];
    }
    $locale = kpi_v1_password_reset_normalize_locale($locale);
    $plain = kpi_v1_password_reset_create_token($cfg, $user['userId']);
    if ($plain === null || $plain === '') {
        return ['ok' => false, 'error' => 'token_failed'];
    }
    $ttl = kpi_v1_password_reset_ttl_minutes($cfg);
    $base = kpi_v1_password_reset_public_base($cfg);
    $path = kpi_v1_password_reset_path_for_locale($locale);
    $resetUrl = $base . $path . '?token=' . rawurlencode($plain);
    $copy = kpi_v1_password_reset_mail_copy($locale, $resetUrl, $ttl);
    $mailed = kpi_v1_mail_send($cfg, $emailNorm, $copy['subject'], $copy['body']);
    $plain = '';
    if (!$mailed) {
        return ['ok' => false, 'error' => 'mail_failed'];
    }
    return ['ok' => true, 'mailed' => true];
}

/**
 * Issue reset (if user exists) and always return generic success to caller.
 * Does not reveal existence. Never logs token/password.
 *
 * @return array{ok:bool, throttled?:bool, mailed?:bool}
 */
function kpi_v1_password_reset_request($cfg, $email, $locale)
{
    $emailNorm = kpi_v1_auth_normalize_email($email);
    $locale = kpi_v1_password_reset_normalize_locale($locale);

    // Invalid email format: still generic ok (no leak). Soft throttle key uses raw hash.
    $throttleKey = $emailNorm !== null ? $emailNorm : ('invalid:' . hash('sha256', (string) $email));
    if (!kpi_v1_password_reset_throttle_allow($cfg, $throttleKey)) {
        // Same external shape; do not reveal rate limit to anonymous clients.
        return ['ok' => true, 'throttled' => true];
    }

    if ($emailNorm === null) {
        return ['ok' => true, 'mailed' => false];
    }

    $user = kpi_v1_auth_find_user_by_email($emailNorm);
    if ($user === null || empty($user['userId']) || kpi_v1_auth_user_is_disabled($user)) {
        return ['ok' => true, 'mailed' => false];
    }

    $plain = kpi_v1_password_reset_create_token($cfg, $user['userId']);
    if ($plain === null || $plain === '') {
        // Internal failure — still generic to client.
        return ['ok' => true, 'mailed' => false];
    }

    $ttl = kpi_v1_password_reset_ttl_minutes($cfg);
    $base = kpi_v1_password_reset_public_base($cfg);
    $path = kpi_v1_password_reset_path_for_locale($locale);
    $resetUrl = $base . $path . '?token=' . rawurlencode($plain);
    $copy = kpi_v1_password_reset_mail_copy($locale, $resetUrl, $ttl);
    $mailed = kpi_v1_mail_send($cfg, $emailNorm, $copy['subject'], $copy['body']);
    // Clear plaintext from memory intent
    $plain = '';
    return ['ok' => true, 'mailed' => $mailed];
}

/**
 * Consume token and set new password. Returns error code or null on success.
 */
function kpi_v1_password_reset_consume($cfg, $plainToken, $newPassword)
{
    $newPassword = (string) $newPassword;
    if (strlen($newPassword) < 8) {
        return 'password_too_short';
    }

    $meta = kpi_v1_password_reset_find_valid($cfg, $plainToken);
    if ($meta === null || empty($meta['userId'])) {
        return 'invalid_or_expired_token';
    }

    $user = kpi_v1_auth_read_user($meta['userId']);
    if ($user === null || kpi_v1_auth_user_is_disabled($user)) {
        return 'invalid_or_expired_token';
    }

    $hash = password_hash($newPassword, PASSWORD_DEFAULT);
    if ($hash === false) {
        return 'hash_failed';
    }

    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        $pdo = kpi_v1_db($cfg);
        try {
            $pdo->beginTransaction();
            $st = $pdo->prepare(
                'UPDATE kpi_users SET password_hash = ?, updated_at = ? WHERE user_id = ? LIMIT 1'
            );
            $st->execute([$hash, gmdate('Y-m-d H:i:s'), $user['userId']]);
            $st2 = $pdo->prepare(
                'UPDATE kpi_password_reset_tokens SET used_at = ? WHERE token_hash = ? AND used_at IS NULL'
            );
            $st2->execute([gmdate('Y-m-d H:i:s'), $meta['tokenHash']]);
            if ($st2->rowCount() < 1) {
                $pdo->rollBack();
                return 'invalid_or_expired_token';
            }
            // Invalidate any other outstanding tokens for this user
            $st3 = $pdo->prepare(
                'UPDATE kpi_password_reset_tokens SET used_at = ? WHERE user_id = ? AND used_at IS NULL'
            );
            $st3->execute([gmdate('Y-m-d H:i:s'), $user['userId']]);
            $pdo->commit();
        } catch (Throwable $e) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            return 'reset_failed';
        }
    } else {
        $user['passwordHash'] = $hash;
        kpi_v1_auth_write_user($user);
        if (!kpi_v1_password_reset_mark_used($cfg, $meta)) {
            return 'invalid_or_expired_token';
        }
        kpi_v1_password_reset_invalidate_user_tokens($cfg, $user['userId']);
    }

    // Invalidate all sessions for this user (file-backed revoke epoch) + clear this browser.
    require_once __DIR__ . '/_session_revoke.php';
    kpi_v1_session_revoke_bump($user['userId']);
    if (kpi_v1_auth_current_user_id() !== null) {
        kpi_v1_auth_clear_session();
    }

    return null;
}

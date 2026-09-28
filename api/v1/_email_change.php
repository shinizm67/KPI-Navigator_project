<?php
/**
 * Signed-in email change (BR-LAUNCH-09 Phase 2).
 * Pending requests are file-backed under data/email_change/ (no DB schema):
 * the canonical email changes only after the 6-digit code sent to the new address is confirmed.
 * Codes are stored as password_hash only; never logged or returned.
 */

require_once __DIR__ . '/_registration.php';
require_once __DIR__ . '/_session_revoke.php';
require_once __DIR__ . '/_password_reset.php';

const KPI_EMAIL_CHANGE_MAX_ATTEMPTS = 5;
const KPI_EMAIL_CHANGE_MAX_SENDS_PER_HOUR = 5;

function kpi_v1_email_change_dir()
{
    $dir = __DIR__ . '/data/email_change';
    if (!is_dir($dir)) {
        @mkdir($dir, 0750, true);
    }
    return $dir;
}

function kpi_v1_email_change_path($kind, $userId)
{
    $safe = kpi_v1_session_revoke_safe_user_id($userId);
    if ($safe === null) {
        return null;
    }
    return kpi_v1_email_change_dir() . '/' . $kind . '_' . $safe . '.json';
}

function kpi_v1_email_change_read_json($path)
{
    if ($path === null || !is_file($path)) {
        return null;
    }
    $data = json_decode((string) file_get_contents($path), true);
    return is_array($data) ? $data : null;
}

function kpi_v1_email_change_read_pending($userId)
{
    return kpi_v1_email_change_read_json(kpi_v1_email_change_path('pending', $userId));
}

function kpi_v1_email_change_write_pending($userId, $pending)
{
    $path = kpi_v1_email_change_path('pending', $userId);
    return $path !== null && kpi_v1_registration_write_json_atomic($path, $pending);
}

function kpi_v1_email_change_delete_pending($userId)
{
    $path = kpi_v1_email_change_path('pending', $userId);
    if ($path !== null && is_file($path)) {
        @unlink($path);
    }
}

/* Binds a pending request to the password hash at request time, so a later password change / reset voids it. */
function kpi_v1_email_change_password_fingerprint($passwordHash)
{
    return hash('sha256', 'kpn-email-change|' . (string) $passwordHash);
}

/**
 * Serializes email changes with public registration (file mode shares the email index).
 * @return resource|null
 */
function kpi_v1_email_change_lock()
{
    $fh = @fopen(kpi_v1_registration_dir() . '/register.lock', 'c+');
    if ($fh === false) {
        return null;
    }
    if (!flock($fh, LOCK_EX)) {
        fclose($fh);
        return null;
    }
    return $fh;
}

function kpi_v1_email_change_unlock($fh)
{
    if ($fh) {
        flock($fh, LOCK_UN);
        fclose($fh);
    }
}

/**
 * Per-user send limit: cooldown between sends (Password Reset cooldown) + hourly cap.
 * @return int seconds to wait (0 = allowed)
 */
function kpi_v1_email_change_send_wait($cfg, $userId, $now)
{
    $log = kpi_v1_email_change_read_json(kpi_v1_email_change_path('sends', $userId));
    $sends = [];
    if (is_array($log) && isset($log['sends']) && is_array($log['sends'])) {
        foreach ($log['sends'] as $ts) {
            $ts = (int) $ts;
            if ($ts > $now - 3600) {
                $sends[] = $ts;
            }
        }
    }
    sort($sends);
    $wait = 0;
    if ($sends) {
        $last = $sends[count($sends) - 1];
        $cool = kpi_v1_password_reset_cooldown_seconds($cfg);
        if ($now - $last < $cool) {
            $wait = $cool - ($now - $last);
        }
    }
    if (count($sends) >= KPI_EMAIL_CHANGE_MAX_SENDS_PER_HOUR) {
        $wait = max($wait, $sends[0] + 3600 - $now);
    }
    return max(0, $wait);
}

function kpi_v1_email_change_record_send($userId, $now)
{
    $path = kpi_v1_email_change_path('sends', $userId);
    if ($path === null) {
        return false;
    }
    $log = kpi_v1_email_change_read_json($path);
    $sends = [];
    if (is_array($log) && isset($log['sends']) && is_array($log['sends'])) {
        foreach ($log['sends'] as $ts) {
            if ((int) $ts > $now - 3600) {
                $sends[] = (int) $ts;
            }
        }
    }
    $sends[] = $now;
    return kpi_v1_registration_write_json_atomic($path, ['sends' => $sends]);
}

function kpi_v1_email_change_mask($email)
{
    $email = (string) $email;
    $at = strrpos($email, '@');
    if ($at === false || $at < 1) {
        return '***';
    }
    return substr($email, 0, 1) . '***' . substr($email, $at);
}

function kpi_v1_email_change_code_mail($locale, $code, $ttlMinutes)
{
    $loc = kpi_v1_password_reset_normalize_locale($locale);
    if ($loc === 'ja') {
        return [
            'subject' => 'KPN メールアドレス変更の確認コード',
            'body' =>
                "Key Performance Navigator のメールアドレス変更を受け付けました。\n\n" .
                "確認コード: {$code}\n\n" .
                "{$ttlMinutes} 分以内に、メールアドレスの変更画面で入力してください。\n\n" .
                "心当たりがない場合はこのメールを無視してください。メールアドレスは変更されません。\n",
        ];
    }
    if ($loc === 'zh-tw') {
        return [
            'subject' => 'KPN 電子信箱變更確認碼',
            'body' =>
                "我們收到 Key Performance Navigator 的電子信箱變更請求。\n\n" .
                "確認碼：{$code}\n\n" .
                "請於 {$ttlMinutes} 分鐘內在電子信箱變更頁面輸入。\n\n" .
                "若您未提出此請求，請忽略本郵件。電子信箱不會被變更。\n",
        ];
    }
    return [
        'subject' => 'KPN Email Change Confirmation Code',
        'body' =>
            "We received an email change request for Key Performance Navigator.\n\n" .
            "Confirmation code: {$code}\n\n" .
            "Enter it on the Change Email page within {$ttlMinutes} minutes.\n\n" .
            "If you did not request this, ignore this email. Your email address will not change.\n",
    ];
}

function kpi_v1_email_change_notice_mail($cfg, $locale, $maskedNewEmail)
{
    $loc = kpi_v1_password_reset_normalize_locale($locale);
    $support = kpi_v1_mail_addresses($cfg)['to'];
    $when = gmdate('Y-m-d H:i') . ' UTC';
    if ($loc === 'ja') {
        return [
            'subject' => 'KPN メールアドレスが変更されました',
            'body' =>
                "Key Performance Navigator のログイン用メールアドレスが変更されました。\n\n" .
                "新しいメールアドレス: {$maskedNewEmail}\n" .
                "変更日時: {$when}\n\n" .
                "心当たりがない場合は {$support} までご連絡ください。\n",
        ];
    }
    if ($loc === 'zh-tw') {
        return [
            'subject' => 'KPN 電子信箱已變更',
            'body' =>
                "您的 Key Performance Navigator 登入電子信箱已變更。\n\n" .
                "新的電子信箱：{$maskedNewEmail}\n" .
                "變更時間：{$when}\n\n" .
                "若您未進行此操作，請聯絡 {$support}。\n",
        ];
    }
    return [
        'subject' => 'KPN Email Address Changed',
        'body' =>
            "The sign-in email address for your Key Performance Navigator account was changed.\n\n" .
            "New email address: {$maskedNewEmail}\n" .
            "Changed at: {$when}\n\n" .
            "If you did not make this change, contact {$support}.\n",
    ];
}

/**
 * Swap the canonical email. Only succeeds when email + password hash still match what the request saw.
 * @return string ok | stale | email_unavailable | failed
 */
function kpi_v1_email_change_apply($cfg, $userId, $oldEmail, $newEmail, $passwordHash)
{
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        try {
            $pdo = kpi_v1_db($cfg);
            $pdo->beginTransaction();
            $st = $pdo->prepare(
                'UPDATE kpi_users SET email = ?, updated_at = ? WHERE user_id = ? AND email = ? AND password_hash = ? LIMIT 1'
            );
            try {
                $st->execute([$newEmail, gmdate('Y-m-d H:i:s'), $userId, $oldEmail, $passwordHash]);
            } catch (PDOException $e) {
                $pdo->rollBack();
                $info = $e->errorInfo;
                return (isset($info[0]) && $info[0] === '23000') ? 'email_unavailable' : 'failed';
            }
            if ($st->rowCount() !== 1) {
                $pdo->rollBack();
                return 'stale';
            }
            if (kpi_v1_session_revoke_bump($userId) === null) {
                $pdo->rollBack();
                return 'failed';
            }
            $pdo->commit();
            return 'ok';
        } catch (Throwable $e) {
            if (isset($pdo) && $pdo instanceof PDO && $pdo->inTransaction()) {
                $pdo->rollBack();
            }
            return 'failed';
        }
    }

    $fresh = kpi_v1_auth_read_user($userId);
    if (
        $fresh === null
        || kpi_v1_auth_normalize_email($fresh['email'] ?? '') !== $oldEmail
        || !hash_equals((string) $passwordHash, (string) ($fresh['passwordHash'] ?? ''))
    ) {
        return 'stale';
    }
    $index = kpi_v1_auth_read_email_index();
    if (isset($index[$newEmail]) && (string) $index[$newEmail] !== (string) $userId) {
        return 'email_unavailable';
    }
    $userPath = kpi_v1_auth_user_path($userId);
    if ($userPath === null) {
        return 'failed';
    }
    $updated = $fresh;
    $updated['email'] = $newEmail;
    $updated['emailUpdatedAt'] = gmdate('c');
    if (!kpi_v1_registration_write_json_atomic($userPath, $updated)) {
        return 'failed';
    }
    $nextIndex = $index;
    unset($nextIndex[$oldEmail]);
    $nextIndex[$newEmail] = (string) $userId;
    if (!kpi_v1_registration_write_json_atomic(kpi_v1_auth_email_index_path(), $nextIndex)) {
        kpi_v1_registration_write_json_atomic($userPath, $fresh);
        return 'failed';
    }
    if (kpi_v1_session_revoke_bump($userId) === null) {
        kpi_v1_registration_write_json_atomic(kpi_v1_auth_email_index_path(), $index);
        kpi_v1_registration_write_json_atomic($userPath, $fresh);
        return 'failed';
    }
    return 'ok';
}

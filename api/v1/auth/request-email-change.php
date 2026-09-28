<?php
/**
 * POST /api/v1/auth/request-email-change.php
 * Body: { "currentPassword": "...", "newEmail": "...", "newEmailConfirm": "...", "locale"?: "ja"|"en"|"zh-tw", "expectedUserId": "..." }
 *
 * Signed-in user asks to change their sign-in email (BR-LAUNCH-09 Phase 2).
 * Verifies the current password, then mails a 6-digit code to the new address.
 * The canonical email does not change here; see confirm-email-change.php.
 * Never echoes passwords, codes or hashes.
 */

require __DIR__ . '/../_email_change.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$uid = kpi_v1_auth_current_user_id();
if ($uid === null) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}

$body = kpi_v1_auth_read_json_body();
kpi_v1_require_expected_user($uid, $body);

$user = kpi_v1_auth_read_user($uid);
if ($user === null || empty($user['passwordHash'])) {
    kpi_v1_auth_clear_session();
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}
kpi_v1_auth_reject_if_disabled($user);

$current = isset($body['currentPassword']) ? (string) $body['currentPassword'] : '';
$rawNew = isset($body['newEmail']) ? (string) $body['newEmail'] : '';
$rawConfirm = isset($body['newEmailConfirm']) ? (string) $body['newEmailConfirm'] : '';
$locale = kpi_v1_password_reset_normalize_locale(isset($body['locale']) ? (string) $body['locale'] : 'en');

$newEmail = strlen($rawNew) > 254 ? null : kpi_v1_auth_normalize_email($rawNew);
if ($newEmail === null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_email']);
}
if (kpi_v1_auth_normalize_email($rawConfirm) !== $newEmail) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'email_mismatch']);
}
$passwordHash = (string) $user['passwordHash'];
if ($current === '' || strlen($current) > 1024 || !password_verify($current, $passwordHash)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'current_password_incorrect']);
}
$oldEmail = kpi_v1_auth_normalize_email($user['email'] ?? '');
if ($oldEmail === null) {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'request_failed']);
}
if ($newEmail === $oldEmail) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'email_unchanged']);
}

/** @return array{0:int,1:array} */
function kpi_v1_email_change_request_locked($cfg, $uid, $oldEmail, $newEmail, $passwordHash, $locale)
{
    $owner = kpi_v1_auth_find_user_by_email($newEmail);
    if ($owner !== null && (string) ($owner['userId'] ?? '') !== (string) $uid) {
        return [409, ['ok' => false, 'error' => 'email_unavailable']];
    }

    $now = time();
    $wait = kpi_v1_email_change_send_wait($cfg, $uid, $now);
    if ($wait > 0) {
        return [429, ['ok' => false, 'error' => 'too_many_requests', 'retryAfterSeconds' => $wait]];
    }
    if (!kpi_v1_email_change_record_send($uid, $now)) {
        return [500, ['ok' => false, 'error' => 'request_failed']];
    }

    $code = sprintf('%06d', random_int(0, 999999));
    $codeHash = password_hash($code, PASSWORD_DEFAULT);
    $ttl = kpi_v1_password_reset_ttl_minutes($cfg);
    $pending = [
        'userId' => (string) $uid,
        'oldEmail' => $oldEmail,
        'newEmail' => $newEmail,
        'codeHash' => $codeHash,
        'passwordFingerprint' => kpi_v1_email_change_password_fingerprint($passwordHash),
        'revokeEpoch' => kpi_v1_session_revoke_get_epoch($uid),
        'locale' => $locale,
        'attempts' => 0,
        'createdAt' => $now,
        'expiresAt' => $now + ($ttl * 60),
    ];
    if ($codeHash === false || !kpi_v1_email_change_write_pending($uid, $pending)) {
        kpi_v1_email_change_delete_pending($uid);
        return [500, ['ok' => false, 'error' => 'request_failed']];
    }

    $mail = kpi_v1_email_change_code_mail($locale, $code, $ttl);
    $code = '';
    if (!kpi_v1_mail_send($cfg, $newEmail, $mail['subject'], $mail['body'])) {
        kpi_v1_email_change_delete_pending($uid);
        return [503, ['ok' => false, 'error' => 'mail_failed']];
    }
    return [200, ['ok' => true, 'newEmail' => $newEmail, 'expiresInMinutes' => $ttl]];
}

$lock = kpi_v1_email_change_lock();
if ($lock === null) {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'request_failed']);
}
try {
    $result = kpi_v1_email_change_request_locked($cfg, $uid, $oldEmail, $newEmail, $passwordHash, $locale);
} finally {
    kpi_v1_email_change_unlock($lock);
}
kpi_v1_json_out($result[0], $result[1]);

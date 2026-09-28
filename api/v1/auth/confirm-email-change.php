<?php
/**
 * POST /api/v1/auth/confirm-email-change.php
 * Body: { "code": "123456", "expectedUserId": "..." }
 *
 * Completes a signed-in email change (BR-LAUNCH-09 Phase 2).
 * The code must belong to this session's user, be unexpired, and the account must still have
 * the email + password + session revoke epoch it had at request time (a disabled account voids the request).
 * Then the canonical email changes, other sessions
 * are revoked, this session continues on a regenerated ID, and the old address gets a notice.
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
if (kpi_v1_auth_user_is_disabled($user)) {
    kpi_v1_email_change_delete_pending($uid);
    kpi_v1_json_out(403, ['ok' => false, 'error' => 'account_disabled']);
}

$code = isset($body['code']) ? trim((string) $body['code']) : '';

/** @return array{0:int,1:array,2?:array} */
function kpi_v1_email_change_confirm_locked($cfg, $uid, $user, $code)
{
    $pending = kpi_v1_email_change_read_pending($uid);
    if ($pending === null || (string) ($pending['userId'] ?? '') !== (string) $uid) {
        return [400, ['ok' => false, 'error' => 'code_expired']];
    }
    if ((int) ($pending['expiresAt'] ?? 0) <= time()) {
        kpi_v1_email_change_delete_pending($uid);
        return [400, ['ok' => false, 'error' => 'code_expired']];
    }
    $attempts = (int) ($pending['attempts'] ?? 0);
    if ($attempts >= KPI_EMAIL_CHANGE_MAX_ATTEMPTS) {
        kpi_v1_email_change_delete_pending($uid);
        return [400, ['ok' => false, 'error' => 'code_locked']];
    }
    if (!preg_match('/^[0-9]{6}$/', $code) || !password_verify($code, (string) ($pending['codeHash'] ?? ''))) {
        $pending['attempts'] = $attempts + 1;
        if ($pending['attempts'] >= KPI_EMAIL_CHANGE_MAX_ATTEMPTS) {
            kpi_v1_email_change_delete_pending($uid);
            return [400, ['ok' => false, 'error' => 'code_locked']];
        }
        if (!kpi_v1_email_change_write_pending($uid, $pending)) {
            kpi_v1_email_change_delete_pending($uid);
            return [400, ['ok' => false, 'error' => 'code_locked']];
        }
        return [400, ['ok' => false, 'error' => 'code_invalid']];
    }

    $oldEmail = (string) ($pending['oldEmail'] ?? '');
    $newEmail = kpi_v1_auth_normalize_email($pending['newEmail'] ?? '');
    $passwordHash = (string) $user['passwordHash'];
    if (
        $newEmail === null
        || kpi_v1_auth_normalize_email($user['email'] ?? '') !== $oldEmail
        || !hash_equals((string) ($pending['passwordFingerprint'] ?? ''), kpi_v1_email_change_password_fingerprint($passwordHash))
        || (int) ($pending['revokeEpoch'] ?? -1) !== kpi_v1_session_revoke_get_epoch($uid)
    ) {
        kpi_v1_email_change_delete_pending($uid);
        return [409, ['ok' => false, 'error' => 'email_change_stale']];
    }
    $owner = kpi_v1_auth_find_user_by_email($newEmail);
    if ($owner !== null && (string) ($owner['userId'] ?? '') !== (string) $uid) {
        kpi_v1_email_change_delete_pending($uid);
        return [409, ['ok' => false, 'error' => 'email_unavailable']];
    }

    $applied = kpi_v1_email_change_apply($cfg, $uid, $oldEmail, $newEmail, $passwordHash);
    if ($applied === 'failed') {
        return [500, ['ok' => false, 'error' => 'change_failed']];
    }
    kpi_v1_email_change_delete_pending($uid);
    if ($applied === 'stale') {
        return [409, ['ok' => false, 'error' => 'email_change_stale']];
    }
    if ($applied === 'email_unavailable') {
        return [409, ['ok' => false, 'error' => 'email_unavailable']];
    }
    return [200, ['ok' => true, 'email' => $newEmail], [
        'oldEmail' => $oldEmail,
        'newEmail' => $newEmail,
        'locale' => (string) ($pending['locale'] ?? 'en'),
    ]];
}

$lock = kpi_v1_email_change_lock();
if ($lock === null) {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'change_failed']);
}
try {
    $result = kpi_v1_email_change_confirm_locked($cfg, $uid, $user, $code);
} finally {
    kpi_v1_email_change_unlock($lock);
}

if ($result[0] === 200) {
    session_regenerate_id(true);
    kpi_v1_auth_set_session_user($uid);
    $done = $result[2];
    $notice = kpi_v1_email_change_notice_mail($cfg, $done['locale'], kpi_v1_email_change_mask($done['newEmail']));
    /* Best effort: the change is already committed, a failed notice must not undo it. */
    kpi_v1_mail_send($cfg, $done['oldEmail'], $notice['subject'], $notice['body']);
}
kpi_v1_json_out($result[0], $result[1]);

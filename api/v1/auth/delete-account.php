<?php
/**
 * POST /api/v1/auth/delete-account.php
 *
 * { "action": "verify", "currentPassword": "...", "expectedUserId": "..." }
 *   Checks the current password, role and child accounts; stores a short-lived delete intent
 *   in this server session. Deletes nothing.
 * { "action": "delete", "acknowledge": true, "expectedUserId": "..." }
 *   Requires a valid intent from this session, then deletes the account (BR-LAUNCH-09 Phase 3),
 *   revokes every session and destroys this one.
 *
 * Never echoes passwords or hashes.
 */

require __DIR__ . '/../_account_delete.php';

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

$action = isset($body['action']) ? (string) $body['action'] : '';

if ($action === 'verify') {
    unset($_SESSION['kpi_delete_intent']);
    $wait = kpi_v1_account_delete_failure_wait($uid);
    if ($wait > 0) {
        kpi_v1_json_out(429, ['ok' => false, 'error' => 'too_many_attempts', 'retryAfterSeconds' => $wait]);
    }
    $current = isset($body['currentPassword']) ? (string) $body['currentPassword'] : '';
    if ($current === '' || strlen($current) > 1024 || !password_verify($current, (string) $user['passwordHash'])) {
        kpi_v1_account_delete_record_failure($uid);
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'current_password_incorrect']);
    }
    $reject = kpi_v1_account_delete_reject_reason($cfg, $user);
    if ($reject !== null) {
        kpi_v1_json_out($reject === 'protected_account' ? 403 : 409, ['ok' => false, 'error' => $reject]);
    }
    kpi_v1_account_delete_issue_intent($user);
    kpi_v1_json_out(200, ['ok' => true, 'expiresInSeconds' => KPI_ACCOUNT_DELETE_INTENT_TTL]);
}

if ($action !== 'delete') {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_action']);
}
if (!isset($body['acknowledge']) || $body['acknowledge'] !== true) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'confirmation_required']);
}

$lock = kpi_v1_email_change_lock();
if ($lock === null) {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'delete_failed']);
}
list($status, $payload) = kpi_v1_account_delete_execute_locked($cfg, $uid);
kpi_v1_email_change_unlock($lock);

if ($status === 200 || $status === 401) {
    kpi_v1_auth_clear_session();
}
kpi_v1_json_out($status, $payload);

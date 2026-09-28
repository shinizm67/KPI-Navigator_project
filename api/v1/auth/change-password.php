<?php
/**
 * POST /api/v1/auth/change-password.php
 * Body: { "currentPassword": "...", "newPassword": "...", "newPasswordConfirm": "...", "expectedUserId": "..." }
 *
 * Signed-in user changes their own password (BR-LAUNCH-09 Phase 1).
 * - Current password must verify; new password follows the public registration rule.
 * - Other sessions are revoked through the same revoke epoch as password reset.
 * - This session stays signed in on a regenerated session ID.
 * Never echoes passwords or hashes.
 */

require __DIR__ . '/../_registration.php';
require_once __DIR__ . '/../_session_revoke.php';

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
$next = isset($body['newPassword']) ? (string) $body['newPassword'] : '';
$confirm = isset($body['newPasswordConfirm']) ? (string) $body['newPasswordConfirm'] : '';

if ($next !== $confirm) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'password_mismatch']);
}
if (!kpi_v1_registration_password_ok($next)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'password_weak']);
}
$oldHash = (string) $user['passwordHash'];
if ($current === '' || strlen($current) > 1024 || !password_verify($current, $oldHash)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'current_password_incorrect']);
}
if (password_verify($next, $oldHash)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'password_unchanged']);
}

$hash = password_hash($next, PASSWORD_DEFAULT);
if ($hash === false) {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'change_failed']);
}

if (kpi_v1_storage_is_mysql($cfg)) {
    require_once __DIR__ . '/../_db.php';
    try {
        $pdo = kpi_v1_db($cfg);
        $pdo->beginTransaction();
        /* Only replace the hash we verified, so a concurrent change / reset wins cleanly. */
        $st = $pdo->prepare(
            'UPDATE kpi_users SET password_hash = ?, updated_at = ? WHERE user_id = ? AND password_hash = ? LIMIT 1'
        );
        $st->execute([$hash, gmdate('Y-m-d H:i:s'), $uid, $oldHash]);
        if ($st->rowCount() !== 1) {
            $pdo->rollBack();
            kpi_v1_json_out(409, ['ok' => false, 'error' => 'password_conflict']);
        }
        if (kpi_v1_session_revoke_bump($uid) === null) {
            $pdo->rollBack();
            kpi_v1_json_out(500, ['ok' => false, 'error' => 'change_failed']);
        }
        $pdo->commit();
    } catch (Throwable $e) {
        if (isset($pdo) && $pdo instanceof PDO && $pdo->inTransaction()) {
            $pdo->rollBack();
        }
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'change_failed']);
    }
} else {
    $fresh = kpi_v1_auth_read_user($uid);
    if ($fresh === null || !hash_equals($oldHash, (string) ($fresh['passwordHash'] ?? ''))) {
        kpi_v1_json_out(409, ['ok' => false, 'error' => 'password_conflict']);
    }
    if (kpi_v1_session_revoke_bump($uid) === null) {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'change_failed']);
    }
    $fresh['passwordHash'] = $hash;
    $fresh['passwordUpdatedAt'] = gmdate('c');
    kpi_v1_auth_write_user($fresh);
}

session_regenerate_id(true);
kpi_v1_auth_set_session_user($uid);

kpi_v1_json_out(200, ['ok' => true]);

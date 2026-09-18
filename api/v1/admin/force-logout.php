<?php
/**
 * POST /api/v1/admin/force-logout.php
 * Founder Super Admin only.
 * Body: { "userId": "..." }
 * Does not trust body admin identity. Does not change password.
 */

require __DIR__ . '/../_admin_actions.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
$actor = kpi_v1_auth_require_founder_superadmin($cfg);

$body = kpi_v1_auth_read_json_body();
$userId = isset($body['userId']) ? (string) $body['userId'] : '';

$result = kpi_v1_admin_force_logout($cfg, $actor, $userId);
if (empty($result['ok'])) {
    $err = isset($result['error']) ? (string) $result['error'] : 'force_logout_failed';
    $code = 400;
    if ($err === 'user_not_found') {
        $code = 404;
    } elseif ($err === 'self_target_forbidden') {
        $code = 400;
    } elseif ($err === 'invalid_id') {
        $code = 400;
    }
    kpi_v1_json_out($code, ['ok' => false, 'error' => $err]);
}

kpi_v1_json_out(200, [
    'ok' => true,
    'userId' => $result['userId'],
    'sessionEpoch' => $result['sessionEpoch'],
]);

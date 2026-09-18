<?php
/**
 * POST /api/v1/admin/set-disabled.php
 * Founder Super Admin only.
 * Body: { "userId": "...", "disabled": true|false }
 * Uses existing kpi_users.disabled. No schema change.
 * Disable also bumps session revoke epoch.
 */

require __DIR__ . '/../_admin_actions.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
$actor = kpi_v1_auth_require_founder_superadmin($cfg);

$body = kpi_v1_auth_read_json_body();
$userId = isset($body['userId']) ? (string) $body['userId'] : '';
if (!array_key_exists('disabled', $body)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_disabled']);
}
$disabled = !empty($body['disabled']);

$result = kpi_v1_admin_set_disabled($cfg, $actor, $userId, $disabled);
if (empty($result['ok'])) {
    $err = isset($result['error']) ? (string) $result['error'] : 'set_disabled_failed';
    $code = 400;
    if ($err === 'user_not_found') {
        $code = 404;
    } elseif ($err === 'self_target_forbidden') {
        $code = 400;
    }
    kpi_v1_json_out($code, ['ok' => false, 'error' => $err]);
}

$out = [
    'ok' => true,
    'user' => $result['user'],
];
if (isset($result['sessionEpoch'])) {
    $out['sessionEpoch'] = $result['sessionEpoch'];
}
kpi_v1_json_out(200, $out);

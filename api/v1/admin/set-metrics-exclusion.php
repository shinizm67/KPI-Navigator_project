<?php
/**
 * POST /api/v1/admin/set-metrics-exclusion.php
 * Founder Super Admin only.
 * Body: { "userId": "..." , "exclude": true|false }        live account (Users page)
 *    or { "lifecycleId": "lc_...", "exclude": true|false } history row (Deleted Accounts page)
 */

require __DIR__ . '/../_lifecycle_admin.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
kpi_v1_auth_require_founder_superadmin($cfg);

$body = kpi_v1_auth_read_json_body();
if (!array_key_exists('exclude', $body) || !is_bool($body['exclude'])) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_exclude']);
}
$exclude = $body['exclude'];
$userId = isset($body['userId']) && is_string($body['userId']) ? $body['userId'] : '';
$lifecycleId = isset($body['lifecycleId']) && is_string($body['lifecycleId']) ? $body['lifecycleId'] : '';

if ($userId !== '' && $lifecycleId === '') {
    if (preg_match('/^[A-Za-z0-9_-]{1,64}$/', $userId) !== 1) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_user_id']);
    }
    $result = kpi_v1_lifecycle_set_account_exclusion($cfg, $userId, $exclude);
} elseif ($lifecycleId !== '' && $userId === '') {
    if (preg_match('/^lc_[a-f0-9]{24}$/', $lifecycleId) !== 1) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_lifecycle_id']);
    }
    $result = kpi_v1_lifecycle_set_history_exclusion($cfg, $lifecycleId, $exclude);
} else {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_target']);
}

if ($result === 'not_found') {
    kpi_v1_json_out(404, ['ok' => false, 'error' => 'not_found']);
}
if ($result !== 'ok') {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'update_failed']);
}
kpi_v1_json_out(200, ['ok' => true, 'exclude' => $exclude]);

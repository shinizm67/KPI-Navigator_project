<?php
/**
 * POST /api/v1/admin/lifecycle-erase.php
 * Founder Super Admin only. Body: { "lifecycleId": "lc_..." }
 * Permanently deletes one history row (erasure request). Returned accounts linked to it lose the link only.
 */

require __DIR__ . '/../_lifecycle_admin.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
kpi_v1_auth_require_founder_superadmin($cfg);

$body = kpi_v1_auth_read_json_body();
$lifecycleId = isset($body['lifecycleId']) && is_string($body['lifecycleId']) ? $body['lifecycleId'] : '';
if (preg_match('/^lc_[a-f0-9]{24}$/', $lifecycleId) !== 1) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_lifecycle_id']);
}
$result = kpi_v1_lifecycle_erase($cfg, $lifecycleId);
if ($result === 'not_found') {
    kpi_v1_json_out(404, ['ok' => false, 'error' => 'not_found']);
}
if ($result !== 'ok') {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'erase_failed']);
}
kpi_v1_json_out(200, ['ok' => true]);

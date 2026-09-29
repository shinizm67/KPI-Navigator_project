<?php
/**
 * GET /api/v1/admin/deleted-accounts.php
 * Founder Super Admin only. Account lifecycle history (no raw email, no HMAC in the response).
 * Applies the 3-year retention purge before listing.
 */

require __DIR__ . '/../_lifecycle_admin.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}
kpi_v1_auth_require_founder_superadmin($cfg);

if (kpi_v1_lifecycle_purge($cfg) === null) {
    error_log('kpn lifecycle: retention purge failed');
}
$rows = kpi_v1_lifecycle_all_rows($cfg);
if ($rows === null) {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'lifecycle_unavailable']);
}
kpi_v1_json_out(200, [
    'ok' => true,
    'ready' => kpi_v1_lifecycle_ready($cfg),
    'rows' => array_map('kpi_v1_lifecycle_public_row', $rows),
]);

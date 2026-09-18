<?php
/**
 * GET /api/v1/admin/dashboard.php
 * Founder Super Admin only.
 */

require __DIR__ . '/../_admin_store.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}
kpi_v1_auth_require_founder_superadmin($cfg);
$stats = kpi_v1_admin_dashboard_stats($cfg);
kpi_v1_json_out(200, array_merge(['ok' => true], $stats));

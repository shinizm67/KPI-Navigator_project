<?php
/**
 * GET /api/v1/admin/dashboard.php[?month=YYYY-MM]
 * Founder Super Admin only.
 * `lifecycle` = account lifecycle metrics for the JST month (default: current month, month-to-date); null if history storage is unavailable.
 */

require __DIR__ . '/../_lifecycle_admin.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}
kpi_v1_auth_require_founder_superadmin($cfg);
$stats = kpi_v1_admin_dashboard_stats($cfg);

$month = isset($_GET['month']) ? (string) $_GET['month'] : '';
$options = kpi_v1_lifecycle_month_options();
if (!in_array($month, $options, true)) {
    $month = $options[0];
}
if (kpi_v1_lifecycle_purge($cfg) === null) {
    error_log('kpn lifecycle: retention purge failed');
}
$stats['lifecycle'] = kpi_v1_lifecycle_metrics($cfg, $month);
$stats['lifecycleMonths'] = $options;
kpi_v1_json_out(200, array_merge(['ok' => true], $stats));

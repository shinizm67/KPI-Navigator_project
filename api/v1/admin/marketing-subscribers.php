<?php
/**
 * GET /api/v1/admin/marketing-subscribers.php
 * Founder Super Admin only. Marketing subscribers + evidence-only rows (raw email is shown here and nowhere else;
 * token material never). Applies the evidence purge before listing. No send function exists.
 */

require __DIR__ . '/../_marketing.php';
require_once __DIR__ . '/../_admin.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}
kpi_v1_auth_require_founder_superadmin($cfg);

$list = kpi_v1_marketing_founder_list($cfg);
if ($list === null) {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'marketing_unavailable']);
}
$counts = ['subscribed' => 0, 'evidenceOnly' => 0, 'total' => count($list['rows'])];
foreach ($list['rows'] as $r) {
    $counts[$r['status'] === 'subscribed' ? 'subscribed' : 'evidenceOnly']++;
}
kpi_v1_json_out(200, ['ok' => true, 'ready' => $list['ready'], 'counts' => $counts, 'rows' => $list['rows']]);

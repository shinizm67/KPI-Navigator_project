<?php
/**
 * GET /api/v1/export.php — download current store blob (B4-T1).
 * Session required (same gate as store.php session mode).
 * Basic: pl omitted (null). Pro: full pl.
 */

require __DIR__ . '/_entitlement.php';

$cfg = kpi_v1_load_config();
kpi_v1_store_boot($cfg);

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}

$userId = kpi_v1_store_resolve_user_id($cfg);
$plan = kpi_v1_entitlement_plan_for_store_user($cfg, $userId);
$path = kpi_v1_data_path($userId);
$blob = kpi_v1_read_blob($path);

$storeOut = $blob->store;
if ($plan === 'basic' && $storeOut !== null) {
    $storeOut = kpi_v1_entitlement_strip_pro_from_store($storeOut);
}
$plOut = $blob->pl;
if ($plan === 'basic') {
    $plOut = null;
}

$payload = [
    'ok' => true,
    'exportedAt' => gmdate('c'),
    'userId' => $userId,
    'plan' => $plan,
    'updatedAt' => $blob->updatedAt,
    'store' => $storeOut,
    'annualNav' => $blob->annualNav,
    'pl' => $plOut,
];

$safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
if ($safe === '') {
    $safe = 'export';
}
$filename = 'kpi-export-' . $safe . '-' . gmdate('Ymd\THis') . '.json';

http_response_code(200);
header('Content-Type: application/json; charset=utf-8');
header('Content-Disposition: attachment; filename="' . $filename . '"');
header('Cache-Control: no-store');
echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
exit;

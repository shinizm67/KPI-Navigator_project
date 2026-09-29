<?php
/**
 * POST /api/v1/admin/marketing-action.php
 * Founder Super Admin only. Body: { "id": <subscriber id>, "action": "unsubscribe" | "erase" }
 * erase: never mailed → deleted now; mailed → evidence-only until last send + 3 years (legal hold, 409 once already so).
 */

require __DIR__ . '/../_marketing.php';
require_once __DIR__ . '/../_admin.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
kpi_v1_auth_require_founder_superadmin($cfg);

$body = kpi_v1_auth_read_json_body();
$id = isset($body['id']) && is_int($body['id']) && $body['id'] > 0 ? $body['id'] : 0;
$action = isset($body['action']) ? (string) $body['action'] : '';
if ($id === 0 || !in_array($action, ['unsubscribe', 'erase'], true)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_request']);
}
list($result, $retainUntil) = kpi_v1_marketing_founder_action($cfg, $id, $action);
if ($result === 'not_found') {
    kpi_v1_json_out(404, ['ok' => false, 'error' => 'not_found']);
}
if ($result === 'failed') {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'action_failed']);
}
$retain = $retainUntil ? gmdate('Y-m-d\TH:i:s\Z', strtotime((string) $retainUntil . ' UTC')) : null;
if ($result === 'legal_hold') {
    kpi_v1_json_out(409, ['ok' => false, 'error' => 'legal_hold', 'retainUntil' => $retain]);
}
kpi_v1_json_out(200, ['ok' => true, 'result' => $result, 'retainUntil' => $retain]);

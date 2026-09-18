<?php
/**
 * GET /api/v1/admin/user-detail.php?id=<user_id>
 * Founder Super Admin only.
 */

require __DIR__ . '/../_admin_store.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}
kpi_v1_auth_require_founder_superadmin($cfg);

$id = isset($_GET['id']) ? preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $_GET['id']) : '';
if ($id === '') {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_id']);
}

$user = kpi_v1_auth_read_user($id);
if ($user === null) {
    kpi_v1_json_out(404, ['ok' => false, 'error' => 'user_not_found']);
}

$safe = kpi_v1_admin_safe_user_row($user);
$profile = kpi_v1_profile_read($cfg, $id);
$history = kpi_v1_plan_history_list($cfg, $id, 50);
$parentId = $safe['parentUserId'] ?? null;
$parent = null;
if ($parentId) {
    $pu = kpi_v1_auth_read_user($parentId);
    if ($pu) {
        $parent = [
            'userId' => (string) $pu['userId'],
            'email' => (string) $pu['email'],
        ];
    }
}
$childIds = kpi_v1_admin_list_child_ids($cfg, $id);
$children = [];
foreach ($childIds as $cid) {
    $cu = kpi_v1_auth_read_user($cid);
    if ($cu) {
        $children[] = [
            'userId' => (string) $cu['userId'],
            'email' => (string) $cu['email'],
        ];
    }
}

kpi_v1_json_out(200, [
    'ok' => true,
    'user' => $safe,
    'profile' => $profile,
    'planHistory' => $history,
    'parent' => $parent,
    'children' => $children,
]);

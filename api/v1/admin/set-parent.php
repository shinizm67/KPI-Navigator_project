<?php
/**
 * POST /api/v1/admin/set-parent.php
 * Founder Super Admin only.
 *
 * Body: { "userId": "<child>", "parentUserId": "<parent>"|null|"" }
 * - parentUserId null/empty clears parent
 * - Add Child / Remove Child reuse this (set/clear child.parent_user_id)
 *
 * Does not trust any body admin identity fields.
 */

require __DIR__ . '/../_admin_store.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
kpi_v1_auth_require_founder_superadmin($cfg);

$body = kpi_v1_auth_read_json_body();
$userId = isset($body['userId']) ? (string) $body['userId'] : '';
$parentRaw = array_key_exists('parentUserId', $body) ? $body['parentUserId'] : null;
if ($parentRaw === '' || $parentRaw === false) {
    $parentRaw = null;
} elseif ($parentRaw !== null) {
    $parentRaw = (string) $parentRaw;
}

$result = kpi_v1_admin_set_parent($cfg, $userId, $parentRaw);
if (empty($result['ok'])) {
    $err = isset($result['error']) ? (string) $result['error'] : 'set_parent_failed';
    $code = 400;
    if ($err === 'user_not_found') {
        $code = 404;
    } elseif ($err === 'parent_not_found' || $err === 'self_parent' || $err === 'cycle' || $err === 'invalid_parent') {
        $code = 400;
    } elseif ($err === 'invalid_id') {
        $code = 400;
    }
    kpi_v1_json_out($code, ['ok' => false, 'error' => $err]);
}

kpi_v1_json_out(200, [
    'ok' => true,
    'user' => $result['user'],
    'parent' => $result['parent'],
    'children' => $result['children'],
]);

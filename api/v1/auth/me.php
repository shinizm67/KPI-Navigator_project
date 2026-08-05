<?php
/**
 * GET /api/v1/auth/me.php
 */

require __DIR__ . '/../_auth.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}

$userId = kpi_v1_auth_current_user_id();
if ($userId === null) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}

$user = kpi_v1_auth_read_user($userId);
if ($user === null) {
    kpi_v1_auth_clear_session();
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}

kpi_v1_json_out(200, array_merge(['ok' => true], kpi_v1_auth_public_user($user)));

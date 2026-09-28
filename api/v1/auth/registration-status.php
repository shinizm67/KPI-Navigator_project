<?php
/**
 * GET /api/v1/auth/registration-status.php
 * Public, read-only. The Registration page shows the form only when this returns registrationEnabled === true.
 * register.php still enforces registrationEnabled itself.
 * No session is started.
 */

require_once __DIR__ . '/../_registration.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_cors($cfg);
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}

kpi_v1_json_out(200, kpi_v1_registration_public_status($cfg));

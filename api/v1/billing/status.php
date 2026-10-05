<?php
/**
 * GET /api/v1/billing/status.php
 * Authenticated read of server subscription state.
 * A Checkout success redirect is not proof. confirmed is true only after a webhook grant.
 */

require __DIR__ . '/../_stripe.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}

$uid = kpi_v1_auth_current_user_id();
if ($uid === null) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}
$user = kpi_v1_auth_read_user($uid);
if ($user === null) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}
if (kpi_v1_auth_user_is_disabled($user)) {
    kpi_v1_json_out(403, ['ok' => false, 'error' => 'account_disabled']);
}

kpi_v1_json_out(200, kpi_v1_billing_status_payload($cfg, $user));

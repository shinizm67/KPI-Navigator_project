<?php
/**
 * POST /api/v1/billing/checkout-session.php
 * Body: { "plan": "basic"|"pro", "locale"?: "ja"|"en"|"zh-tw" }
 * Session + X-KPI-Expected-User required.
 * Price ID, country, currency, and region are not accepted from the client.
 * The saved business country selects the Stripe Price.
 * Does not change the account plan. The webhook is authoritative.
 */

require __DIR__ . '/../_stripe.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
header('Cache-Control: no-store');

$body = kpi_v1_auth_read_json_body();
$uid = kpi_v1_auth_current_user_id();
if ($uid === null) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}
kpi_v1_require_expected_user($uid, $body);
$user = kpi_v1_auth_read_user($uid);
if ($user === null) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}

$result = kpi_v1_stripe_start_checkout($cfg, $user, $body, $_SERVER);
if (empty($result['ok'])) {
    $status = isset($result['status']) ? (int) $result['status'] : 500;
    $error = isset($result['error']) ? (string) $result['error'] : 'stripe_error';
    kpi_v1_json_out($status, ['ok' => false, 'error' => $error]);
}

kpi_v1_json_out(200, [
    'ok' => true,
    'url' => $result['url'],
    'id' => $result['id'],
]);

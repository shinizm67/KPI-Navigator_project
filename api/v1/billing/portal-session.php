<?php
/**
 * POST /api/v1/billing/portal-session.php
 * Body: { "locale"?: "ja"|"en"|"zh-tw" }
 * Session + X-KPI-Expected-User required.
 * Customer ID, subscription ID, return URL, and Stripe mode are not accepted from the client.
 * Opens the Stripe Customer Portal for the customer stored for this user.
 * Does not cancel the subscription and does not change the account plan.
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

$result = kpi_v1_stripe_start_portal($cfg, $user, $body, $_SERVER);
if (empty($result['ok'])) {
    $status = isset($result['status']) ? (int) $result['status'] : 500;
    $error = isset($result['error']) ? (string) $result['error'] : 'stripe_error';
    kpi_v1_json_out($status, ['ok' => false, 'error' => $error]);
}

kpi_v1_json_out(200, [
    'ok' => true,
    'url' => $result['url'],
]);

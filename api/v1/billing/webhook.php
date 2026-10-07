<?php
/**
 * POST /api/v1/billing/webhook.php
 * Stripe-Signature required. No session. No trust in the browser return URL.
 * test mode accepts only livemode false. live mode accepts only livemode true.
 */

require_once __DIR__ . '/../_stripe.php';

$cfg = kpi_v1_load_config();
header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}

$payload = file_get_contents('php://input');
$header = isset($_SERVER['HTTP_STRIPE_SIGNATURE']) ? (string) $_SERVER['HTTP_STRIPE_SIGNATURE'] : '';
$result = kpi_v1_stripe_handle_webhook($cfg, $payload === false ? '' : $payload, $header, $_SERVER);

$status = isset($result['status']) ? (int) $result['status'] : 500;
$body = ['ok' => !empty($result['ok'])];
if (empty($result['ok'])) {
    $body['error'] = isset($result['error']) ? (string) $result['error'] : 'webhook_failed';
} else {
    $body['duplicate'] = !empty($result['duplicate']);
    if (!empty($result['ignored'])) {
        $body['ignored'] = (string) $result['ignored'];
    }
}
kpi_v1_json_out($status, $body);

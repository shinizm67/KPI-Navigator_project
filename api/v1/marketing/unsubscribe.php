<?php
/**
 * POST /api/v1/marketing/unsubscribe.php?t=<token>
 * Public, no login, no session. Body (optional): JSON { "token", "reason", "note" } or the RFC 8058 One-Click form
 * "List-Unsubscribe=One-Click". GET does nothing here (mail scanners follow links; the confirm page posts).
 *
 * Same answer for valid / unknown / already unsubscribed tokens (no enumeration). After it, nothing is sent again;
 * re-subscribing needs the person's own action (Settings or Registration).
 */

require_once __DIR__ . '/../_marketing.php';

$cfg = kpi_v1_load_config();
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}

$raw = (string) file_get_contents('php://input', false, null, 0, 8192);
$json = json_decode($raw, true);
$body = is_array($json) ? $json : [];
$oneClick = !is_array($json) && isset($_POST['List-Unsubscribe']) && $_POST['List-Unsubscribe'] === 'One-Click';

$token = isset($body['token']) && is_string($body['token']) ? $body['token'] : (isset($_GET['t']) && is_string($_GET['t']) ? $_GET['t'] : '');

kpi_v1_marketing_rate_gate($cfg, 'marketing_unsub_global', 'all');
kpi_v1_marketing_rate_gate($cfg, 'marketing_unsub_token', hash('sha256', $token));

$matched = false;
if (kpi_v1_marketing_unsubscribe_by_token($cfg, $token, $oneClick ? 'one_click' : 'link', $matched) === 'unavailable') {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'unavailable']);
}
if ($matched && !kpi_v1_marketing_record_reason($body['reason'] ?? null, $body['note'] ?? null)) {
    error_log('kpn marketing: unsubscribe reason not recorded');
}
kpi_v1_json_out(200, ['ok' => true]);

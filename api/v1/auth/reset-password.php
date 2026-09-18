<?php
/**
 * POST /api/v1/auth/reset-password.php
 * Body: { "token": "...", "password": "..." }
 *
 * Updates password_hash via existing PASSWORD_DEFAULT contract.
 * Never echoes token or password.
 */

require __DIR__ . '/../_password_reset.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();
$token = isset($body['token']) ? (string) $body['token'] : '';
$password = isset($body['password']) ? (string) $body['password'] : '';

$err = kpi_v1_password_reset_consume($cfg, $token, $password);
if ($err === 'password_too_short') {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'password_too_short']);
}
if ($err === 'hash_failed' || $err === 'reset_failed') {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'reset_failed']);
}
if ($err !== null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_or_expired_token']);
}

kpi_v1_json_out(200, ['ok' => true]);

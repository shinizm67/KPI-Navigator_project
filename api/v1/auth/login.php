<?php
/**
 * POST /api/v1/auth/login.php
 * Body: { "email": "...", "password": "..." }
 */

require __DIR__ . '/../_auth.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();
$email = kpi_v1_auth_normalize_email(isset($body['email']) ? $body['email'] : '');
$password = isset($body['password']) ? (string) $body['password'] : '';

if ($email === null || $password === '') {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'invalid_credentials']);
}

$index = kpi_v1_auth_read_email_index();
if (!isset($index[$email])) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'invalid_credentials']);
}

$user = kpi_v1_auth_read_user($index[$email]);
if ($user === null || empty($user['passwordHash'])) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'invalid_credentials']);
}
if (!password_verify($password, (string) $user['passwordHash'])) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'invalid_credentials']);
}
if (kpi_v1_auth_user_is_disabled($user)) {
    kpi_v1_json_out(403, ['ok' => false, 'error' => 'account_disabled']);
}

kpi_v1_auth_set_session_user($user['userId']);
kpi_v1_json_out(200, array_merge(['ok' => true], kpi_v1_auth_public_user($user, $cfg)));

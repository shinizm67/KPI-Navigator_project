<?php
/**
 * POST /api/v1/auth/admin-set-password.php
 * Admin token required.
 * Body: { "email": "...", "password": "..." }
 */

require __DIR__ . '/../_auth.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();
kpi_v1_auth_require_admin($cfg, $body);

$email = kpi_v1_auth_normalize_email(isset($body['email']) ? $body['email'] : '');
$password = isset($body['password']) ? (string) $body['password'] : '';

if ($email === null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_email']);
}
if (strlen($password) < 8) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'password_too_short']);
}

$user = kpi_v1_auth_find_user_by_email($email);
if ($user === null) {
    kpi_v1_json_out(404, ['ok' => false, 'error' => 'user_not_found']);
}

$hash = password_hash($password, PASSWORD_DEFAULT);
if ($hash === false) {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'hash_failed']);
}

$user['passwordHash'] = $hash;
$user['passwordUpdatedAt'] = gmdate('c');
kpi_v1_auth_write_user($user);

kpi_v1_json_out(200, array_merge(['ok' => true], kpi_v1_auth_public_user($user, $cfg)));

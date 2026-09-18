<?php
/**
 * POST /api/v1/auth/register.php
 * Body: { "email": "...", "password": "..." }
 *
 * Public self-serve signup. Gated by config registrationEnabled (default false).
 * Admin account creation uses admin-create-user.php and is not affected by this gate.
 */

require __DIR__ . '/../_entitlement.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

if (empty($cfg['registrationEnabled'])) {
    kpi_v1_json_out(403, ['ok' => false, 'error' => 'registration_disabled']);
}

$body = kpi_v1_auth_read_json_body();
$email = kpi_v1_auth_normalize_email(isset($body['email']) ? $body['email'] : '');
$password = isset($body['password']) ? (string) $body['password'] : '';

if ($email === null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_email']);
}
if (strlen($password) < 8) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'password_too_short']);
}

$index = kpi_v1_auth_read_email_index();
if (isset($index[$email])) {
    kpi_v1_json_out(409, ['ok' => false, 'error' => 'email_taken']);
}

$userId = kpi_v1_auth_new_user_id();
$hash = password_hash($password, PASSWORD_DEFAULT);
if ($hash === false) {
    kpi_v1_json_out(500, ['ok' => false, 'error' => 'hash_failed']);
}

$user = [
    'userId' => $userId,
    'email' => $email,
    'passwordHash' => $hash,
    'plan' => kpi_v1_entitlement_default_plan($cfg),
    'role' => 'user',
    'disabled' => false,
    'createdAt' => gmdate('c'),
];
kpi_v1_auth_write_user($user);
$index[$email] = $userId;
kpi_v1_auth_write_email_index($index);

kpi_v1_auth_set_session_user($userId);
kpi_v1_json_out(201, array_merge(['ok' => true], kpi_v1_auth_public_user($user, $cfg)));

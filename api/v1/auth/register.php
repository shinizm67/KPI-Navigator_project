<?php
/**
 * POST /api/v1/auth/register.php
 * Body: { "email", "password", "consentAccepted": true, "termsVersion", "privacyVersion", "formToken", "extraNote": "" }
 *
 * Public self-serve signup. Gated by config registrationEnabled (default false).
 * Admin account creation uses admin-create-user.php and is not affected by this gate.
 * Public registration is Basic only until Billing: plan is fixed here, not taken from the client or defaultPlan.
 * The account and its first consent row are created together or not at all.
 */

require __DIR__ . '/../_entitlement.php';
require_once __DIR__ . '/../_registration.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

if (!kpi_v1_registration_enabled($cfg)) {
    kpi_v1_json_out(403, ['ok' => false, 'error' => 'registration_disabled']);
}

$ipAllowed = kpi_v1_registration_rate_allow($cfg, 'ip', kpi_v1_registration_client_ip());
if ($ipAllowed === null) {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'registration_unavailable']);
}
if ($ipAllowed === false) {
    kpi_v1_json_out(429, ['ok' => false, 'error' => 'rate_limited']);
}

$body = kpi_v1_auth_read_json_body();

if (kpi_v1_registration_bot_reason($cfg, $body) !== null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'registration_rejected']);
}

$email = kpi_v1_auth_normalize_email(isset($body['email']) ? $body['email'] : '');
if ($email === null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_email']);
}

$emailAllowed = kpi_v1_registration_rate_allow($cfg, 'email', $email);
if ($emailAllowed === null) {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'registration_unavailable']);
}
if ($emailAllowed === false) {
    kpi_v1_json_out(429, ['ok' => false, 'error' => 'rate_limited']);
}

$password = isset($body['password']) && is_string($body['password']) ? $body['password'] : '';
if (!kpi_v1_registration_password_ok($password)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'password_weak']);
}

$consent = kpi_v1_registration_consent_from_body($body);
if (isset($consent['error'])) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => $consent['error']]);
}

$index = kpi_v1_auth_read_email_index();
if (isset($index[$email])) {
    kpi_v1_json_out(409, ['ok' => false, 'error' => 'email_taken']);
}

$hash = password_hash($password, PASSWORD_DEFAULT);
if ($hash === false) {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'registration_unavailable']);
}

$user = [
    'userId' => kpi_v1_auth_new_user_id(),
    'email' => $email,
    'passwordHash' => $hash,
    'plan' => 'basic',
    'role' => 'user',
    'disabled' => false,
    'createdAt' => gmdate('c'),
];

$created = kpi_v1_registration_create_user_with_consent($cfg, $user, $consent['record']);
if ($created === 'email_taken') {
    kpi_v1_json_out(409, ['ok' => false, 'error' => 'email_taken']);
}
if ($created !== 'ok') {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'registration_unavailable']);
}

kpi_v1_auth_set_session_user($user['userId']);
kpi_v1_json_out(201, array_merge(['ok' => true], kpi_v1_auth_public_user($user, $cfg)));

<?php
/**
 * POST /api/v1/auth/register.php
 * Body: { "email", "password", "consentAccepted": true, "termsVersion", "privacyVersion", "formToken", "extraNote": "",
 *         optional "marketingOptIn": true, "marketingConsentVersion", "marketingLocale" }
 *
 * Public self-serve signup. Gated by config registrationEnabled (default false).
 * Admin account creation uses admin-create-user.php and is not affected by this gate.
 * Public registration is Basic only until Billing: plan is fixed here, not taken from the client or defaultPlan.
 * The account and its first consent row are created together or not at all.
 */

require __DIR__ . '/../_entitlement.php';
require_once __DIR__ . '/../_registration.php';
require_once __DIR__ . '/../_lifecycle.php';
require_once __DIR__ . '/../_marketing.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

if (!kpi_v1_registration_enabled($cfg)) {
    kpi_v1_json_out(403, ['ok' => false, 'error' => 'registration_disabled']);
}

/* Rejected before any counter so a spoofed header cannot consume or pick an IP bucket. */
if (kpi_v1_registration_has_forwarded_ip_header()) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'registration_rejected']);
}

kpi_v1_registration_rate_gate($cfg, 'global_attempt', 'all');
kpi_v1_registration_rate_gate($cfg, 'ip', kpi_v1_registration_client_ip());

$body = kpi_v1_auth_read_json_body();

if (kpi_v1_registration_bot_reason($cfg, $body) !== null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'registration_rejected']);
}

$email = kpi_v1_auth_normalize_email(isset($body['email']) ? $body['email'] : '');
if ($email === null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_email']);
}

kpi_v1_registration_rate_gate($cfg, 'email', $email);

$password = isset($body['password']) && is_string($body['password']) ? $body['password'] : '';
if (!kpi_v1_registration_password_ok($password)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'password_weak']);
}

$consent = kpi_v1_registration_consent_from_body($body);
if (isset($consent['error'])) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => $consent['error']]);
}

/* Optional and separate from the Terms consent; absent / false = no marketing row at all. */
$marketing = kpi_v1_marketing_consent_from_registration($body);
if (isset($marketing['error'])) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => $marketing['error']]);
}

$index = kpi_v1_auth_read_email_index();
if (isset($index[$email])) {
    kpi_v1_json_out(409, ['ok' => false, 'error' => 'email_taken']);
}

/* Counts every request that reaches account creation (a later create failure still uses the slot). */
kpi_v1_registration_rate_gate($cfg, 'global_create_day', 'all');
kpi_v1_registration_rate_gate($cfg, 'global_create_hour', 'all');

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

$alsoWrite = $marketing === null ? null : function ($pdo) use ($cfg, $user, $marketing) {
    return kpi_v1_marketing_on_registration($cfg, $user, $marketing, $pdo);
};
$created = kpi_v1_registration_create_user_with_consent($cfg, $user, $consent['record'], $alsoWrite);
if ($created === 'email_taken') {
    kpi_v1_json_out(409, ['ok' => false, 'error' => 'email_taken']);
}
if ($created !== 'ok') {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'registration_unavailable']);
}
kpi_v1_lifecycle_on_account_created($cfg, $user['userId'], $user['email']);

kpi_v1_auth_set_session_user($user['userId']);
kpi_v1_json_out(201, array_merge(['ok' => true], kpi_v1_auth_public_user($user, $cfg)));

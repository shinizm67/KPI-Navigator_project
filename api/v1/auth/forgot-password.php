<?php
/**
 * POST /api/v1/auth/forgot-password.php
 * Body: { "email": "...", "locale"?: "ja"|"en"|"zh-tw" }
 *
 * Always returns generic ok — never reveals whether the email exists.
 */

require __DIR__ . '/../_password_reset.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();
$email = isset($body['email']) ? (string) $body['email'] : '';
$locale = isset($body['locale']) ? (string) $body['locale'] : 'en';

kpi_v1_password_reset_request($cfg, $email, $locale);

kpi_v1_json_out(200, ['ok' => true]);

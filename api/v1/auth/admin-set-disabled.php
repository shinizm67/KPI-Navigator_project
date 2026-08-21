<?php
/**
 * POST /api/v1/auth/admin-set-disabled.php
 * Admin token required.
 * Body: { "email": "...", "disabled": true|false }
 */

require __DIR__ . '/../_auth.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();
kpi_v1_auth_require_admin($cfg, $body);

$email = kpi_v1_auth_normalize_email(isset($body['email']) ? $body['email'] : '');
if ($email === null) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_email']);
}
if (!array_key_exists('disabled', $body)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_disabled']);
}
$disabled = !empty($body['disabled']);

$user = kpi_v1_auth_find_user_by_email($email);
if ($user === null) {
    kpi_v1_json_out(404, ['ok' => false, 'error' => 'user_not_found']);
}

$user['disabled'] = $disabled;
$user['disabledUpdatedAt'] = gmdate('c');
kpi_v1_auth_write_user($user);

kpi_v1_json_out(200, array_merge(['ok' => true], kpi_v1_auth_public_user($user, $cfg)));

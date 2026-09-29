<?php
/**
 * POST /api/v1/admin/lifecycle-lookup.php
 * Founder Super Admin only. Body: { "email": "..." }
 * Finds history rows for an erasure request via HMAC under every configured key.
 * The email is neither stored nor logged; the response does not echo it.
 */

require __DIR__ . '/../_lifecycle_admin.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
kpi_v1_auth_require_founder_superadmin($cfg);

$body = kpi_v1_auth_read_json_body();
$email = isset($body['email']) && is_string($body['email']) ? $body['email'] : '';
if (kpi_v1_lifecycle_normalize_email($email) === '' || strpos($email, '@') === false) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_email']);
}
if (kpi_v1_lifecycle_all_keys($cfg) === []) {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'lifecycle_key_missing']);
}
$rows = kpi_v1_lifecycle_lookup($cfg, $email);
unset($email, $body);
if ($rows === null) {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'lifecycle_unavailable']);
}
kpi_v1_json_out(200, ['ok' => true, 'rows' => array_map('kpi_v1_lifecycle_public_row', $rows)]);

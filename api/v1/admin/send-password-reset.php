<?php
/**
 * POST /api/v1/admin/send-password-reset.php
 * Founder Super Admin only.
 * Body: { "userId": "...", "locale"?: "ja"|"en"|"zh-tw" }
 * Reuses Forgot Password token + mail. Never returns password / token / hash.
 */

require __DIR__ . '/../_admin_actions.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();
$actor = kpi_v1_auth_require_founder_superadmin($cfg);

$body = kpi_v1_auth_read_json_body();
$userId = isset($body['userId']) ? (string) $body['userId'] : '';
$locale = isset($body['locale']) ? (string) $body['locale'] : 'ja';

$result = kpi_v1_admin_send_password_reset($cfg, $actor, $userId, $locale);
if (empty($result['ok'])) {
    $err = isset($result['error']) ? (string) $result['error'] : 'reset_failed';
    $code = 400;
    if ($err === 'user_not_found') {
        $code = 404;
    } elseif ($err === 'mail_failed' || $err === 'token_failed') {
        $code = 500;
    }
    kpi_v1_json_out($code, ['ok' => false, 'error' => $err]);
}

kpi_v1_json_out(200, [
    'ok' => true,
    'mailed' => !empty($result['mailed']),
    'email' => (string) ($result['email'] ?? ''),
    'user' => $result['user'],
    'message' => 'Password reset email sent',
]);

<?php
/**
 * GET  /api/v1/marketing/preference.php → { ok, subscribed, consentTextVersion }
 * POST /api/v1/marketing/preference.php { "action": "subscribe" | "unsubscribe", "consentTextVersion", "locale",
 *                                          "expectedUserId" }
 * Signed-in user only, for the account's current email. Subscribing needs the current wording version
 * (the Settings page shows it); nobody else's status is ever readable here.
 */

require_once __DIR__ . '/../_marketing.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);

$uid = kpi_v1_auth_current_user_id();
if ($uid === null) {
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}
$user = kpi_v1_auth_read_user($uid);
if ($user === null) {
    kpi_v1_auth_clear_session();
    kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
}
kpi_v1_auth_reject_if_disabled($user);
$email = kpi_v1_marketing_normalize_email($user['email'] ?? '');

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $subscribed = kpi_v1_marketing_is_subscribed($cfg, $email);
    if ($subscribed === null) {
        kpi_v1_json_out(503, ['ok' => false, 'error' => 'unavailable']);
    }
    kpi_v1_json_out(200, ['ok' => true, 'subscribed' => $subscribed, 'consentTextVersion' => KPI_MARKETING_CONSENT_VERSION]);
}

kpi_v1_auth_require_post();
$body = kpi_v1_auth_read_json_body();
kpi_v1_require_expected_user($uid, $body);
$action = isset($body['action']) ? (string) $body['action'] : '';

if ($action === 'subscribe') {
    $version = isset($body['consentTextVersion']) && is_string($body['consentTextVersion']) ? trim($body['consentTextVersion']) : '';
    if ($version !== KPI_MARKETING_CONSENT_VERSION) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'marketing_consent_outdated']);
    }
    $res = kpi_v1_marketing_run($cfg, function ($ctx) use ($cfg, $uid, $email, $body) {
        return kpi_v1_marketing_op_subscribe($cfg, $ctx, $email, [
            'source' => 'settings',
            'consentTextVersion' => KPI_MARKETING_CONSENT_VERSION,
            'privacyVersion' => KPI_PRIVACY_VERSION,
            'locale' => kpi_v1_marketing_locale($body['locale'] ?? ''),
            'accountUserId' => (string) $uid,
        ]);
    });
} elseif ($action === 'unsubscribe') {
    $res = kpi_v1_marketing_run($cfg, function ($ctx) use ($email) {
        $row = $ctx['find']($email);
        if (is_array($row) && $row['status'] === 'subscribed') {
            kpi_v1_marketing_op_stop_row($ctx, $row, 'settings', true);
        }
        return true;
    });
    if ($res[0] === 'absent') {
        kpi_v1_json_out(200, ['ok' => true, 'subscribed' => false]);
    }
} else {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_action']);
}
if ($res[0] !== 'ok') {
    kpi_v1_json_out(503, ['ok' => false, 'error' => 'unavailable']);
}
kpi_v1_json_out(200, ['ok' => true, 'subscribed' => $action === 'subscribe']);

<?php
/**
 * GET/PUT /api/v1/profile.php
 * Session user may read/write own server-side profile.
 * Does not migrate localStorage history.
 */

require __DIR__ . '/_admin_store.php';

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

$method = $_SERVER['REQUEST_METHOD'];
if ($method === 'GET') {
    $profile = kpi_v1_profile_read($cfg, $uid);
    kpi_v1_json_out(200, ['ok' => true, 'profile' => $profile]);
}

if ($method === 'PUT' || $method === 'POST') {
    $body = kpi_v1_auth_read_json_body();
    $fields = [
        'businessName' => isset($body['businessName']) ? $body['businessName'] : (isset($body['business_name']) ? $body['business_name'] : null),
        'companyName' => isset($body['companyName']) ? $body['companyName'] : (isset($body['company']) ? $body['company'] : null),
        'businessType' => isset($body['businessType']) ? $body['businessType'] : (isset($body['industry']) ? $body['industry'] : null),
        'genre' => isset($body['genre']) ? $body['genre'] : null,
        'locale' => isset($body['locale']) ? $body['locale'] : null,
        'country' => isset($body['country']) ? $body['country'] : null,
        'stateRegion' => isset($body['stateRegion']) ? $body['stateRegion'] : (isset($body['state']) ? $body['state'] : null),
        'city' => isset($body['city']) ? $body['city'] : null,
        'currency' => isset($body['currency']) ? $body['currency'] : null,
    ];
    $saved = kpi_v1_profile_write($cfg, $uid, $fields);
    kpi_v1_json_out(200, ['ok' => true, 'profile' => $saved]);
}

kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);

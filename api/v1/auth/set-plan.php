<?php
/**
 * POST /api/v1/auth/set-plan.php
 * Body: { "plan": "basic"|"pro", "email"?: "..." }
 *
 * Auth:
 * - X-KPI-Plan-Admin-Token (or body.adminToken) matching config → set any user by email
 * - else if allowSelfPlanChange + session → set own plan
 */

require __DIR__ . '/../_entitlement.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();
$rawPlan = isset($body['plan']) ? strtolower(trim((string) $body['plan'])) : '';
if ($rawPlan !== 'basic' && $rawPlan !== 'pro') {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_plan']);
}
$plan = $rawPlan;

$adminTok = '';
if (isset($_SERVER['HTTP_X_KPI_PLAN_ADMIN_TOKEN'])) {
    $adminTok = (string) $_SERVER['HTTP_X_KPI_PLAN_ADMIN_TOKEN'];
} elseif (isset($body['adminToken'])) {
    $adminTok = (string) $body['adminToken'];
}
$expectedAdmin = isset($cfg['planAdminToken']) ? (string) $cfg['planAdminToken'] : '';
$isAdmin = ($expectedAdmin !== '' && hash_equals($expectedAdmin, $adminTok));

$user = null;
if ($isAdmin && !empty($body['email'])) {
    $email = kpi_v1_auth_normalize_email($body['email']);
    if ($email === null) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_email']);
    }
    $index = kpi_v1_auth_read_email_index();
    if (!isset($index[$email])) {
        kpi_v1_json_out(404, ['ok' => false, 'error' => 'user_not_found']);
    }
    $user = kpi_v1_auth_read_user($index[$email]);
} elseif ($isAdmin) {
    $uid = kpi_v1_auth_current_user_id();
    if ($uid === null) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'email_required']);
    }
    $user = kpi_v1_auth_read_user($uid);
} else {
    $allowSelf = !empty($cfg['allowSelfPlanChange']);
    if (!$allowSelf) {
        kpi_v1_json_out(403, ['ok' => false, 'error' => 'forbidden']);
    }
    $uid = kpi_v1_auth_current_user_id();
    if ($uid === null) {
        kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
    }
    $user = kpi_v1_auth_read_user($uid);
}

if ($user === null) {
    kpi_v1_json_out(404, ['ok' => false, 'error' => 'user_not_found']);
}

$user['plan'] = $plan;
$user['planUpdatedAt'] = gmdate('c');
kpi_v1_auth_write_user($user);

kpi_v1_json_out(200, array_merge(['ok' => true], kpi_v1_auth_public_user($user, $cfg)));

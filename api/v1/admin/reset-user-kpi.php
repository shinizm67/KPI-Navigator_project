<?php
/**
 * POST /api/v1/admin/reset-user-kpi.php
 *
 * Wipe one user's KPN operational data to empty/new-user equivalent.
 * Auth: Founder Super Admin session OR X-KPI-Plan-Admin-Token.
 * Body: { "email"?: "...", "userId"?: "...", "confirm": "RESET_KPN_DATA" }
 * Exactly one user must resolve; if both email and userId are set they must match.
 *
 * Preserves: kpi_users row (id/email/password/plan/role/disabled/parent), kpi_plan_history.
 * Resets: kpi_store JSON cols, kpi_user_profiles, kpi_daily_inputs, kpi_daily_facts, session epoch.
 * Never returns password_hash / tokens / secrets.
 */

require __DIR__ . '/../_admin_reset_kpi.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();
if (!is_array($body)) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_json']);
}

$actor = kpi_v1_admin_reset_require_actor($cfg, $body);

$confirm = isset($body['confirm']) ? (string) $body['confirm'] : '';
if ($confirm !== KPI_V1_ADMIN_RESET_CONFIRM) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'confirm_required']);
}

$resolved = kpi_v1_admin_reset_resolve_target($body);
if (empty($resolved['ok'])) {
    $err = isset($resolved['error']) ? (string) $resolved['error'] : 'user_not_found';
    $code = 400;
    if ($err === 'user_not_found') {
        $code = 404;
    } elseif ($err === 'invalid_id' || $err === 'invalid_email' || $err === 'missing_target' || $err === 'ambiguous_target') {
        $code = 400;
    }
    kpi_v1_json_out($code, ['ok' => false, 'error' => $err]);
}

$result = kpi_v1_admin_reset_user_kpi($cfg, $actor, $resolved['user']);
if (empty($result['ok'])) {
    $err = isset($result['error']) ? (string) $result['error'] : 'reset_failed';
    $code = 400;
    if ($err === 'user_not_found') {
        $code = 404;
    } elseif ($err === 'self_target_forbidden') {
        $code = 400;
    } elseif ($err === 'reset_failed' || $err === 'revoke_failed') {
        $code = 500;
    }
    kpi_v1_json_out($code, ['ok' => false, 'error' => $err]);
}

kpi_v1_json_out(200, [
    'ok' => true,
    'userId' => $result['userId'],
    'email' => $result['email'],
    'sessionEpoch' => $result['sessionEpoch'],
    'reset' => $result['reset'],
    'deletedDailyInputs' => $result['deletedDailyInputs'],
    'deletedDailyFacts' => $result['deletedDailyFacts'],
]);

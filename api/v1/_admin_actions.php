<?php
/**
 * Founder Admin Actions helpers (Force Logout / Password Reset / Disable).
 * Does not trust body admin identity. Never returns password_hash.
 */

require_once __DIR__ . '/_admin.php';
require_once __DIR__ . '/_session_revoke.php';
require_once __DIR__ . '/_password_reset.php';

/**
 * @return array{ok:true,user:array}|array{ok:false,error:string}
 */
function kpi_v1_admin_actions_load_target($userId)
{
    $userId = trim((string) $userId);
    if ($userId === '' || kpi_v1_session_revoke_safe_user_id($userId) === null) {
        return ['ok' => false, 'error' => 'invalid_id'];
    }
    $user = kpi_v1_auth_read_user($userId);
    if ($user === null || empty($user['userId'])) {
        return ['ok' => false, 'error' => 'user_not_found'];
    }
    return ['ok' => true, 'user' => $user];
}

/**
 * @param array $actor founder user
 * @return string|null error code
 */
function kpi_v1_admin_actions_self_target_error($actor, $targetUserId)
{
    $actorId = isset($actor['userId']) ? (string) $actor['userId'] : '';
    if ($actorId !== '' && $actorId === (string) $targetUserId) {
        return 'self_target_forbidden';
    }
    return null;
}

/**
 * @return array{ok:true,userId:string,sessionEpoch:int}|array{ok:false,error:string}
 */
function kpi_v1_admin_force_logout($cfg, $actor, $targetUserId)
{
    $selfErr = kpi_v1_admin_actions_self_target_error($actor, $targetUserId);
    if ($selfErr !== null) {
        return ['ok' => false, 'error' => $selfErr];
    }
    $loaded = kpi_v1_admin_actions_load_target($targetUserId);
    if (empty($loaded['ok'])) {
        return $loaded;
    }
    $epoch = kpi_v1_session_revoke_bump($loaded['user']['userId']);
    if ($epoch === null) {
        return ['ok' => false, 'error' => 'revoke_failed'];
    }
    return [
        'ok' => true,
        'userId' => (string) $loaded['user']['userId'],
        'sessionEpoch' => $epoch,
    ];
}

/**
 * @return array{ok:true,user:array,mailed:bool,email:string}|array{ok:false,error:string}
 */
function kpi_v1_admin_send_password_reset($cfg, $actor, $targetUserId, $locale)
{
    unset($actor); // actor already founder-gated by caller; unused (no self ban for reset)
    $loaded = kpi_v1_admin_actions_load_target($targetUserId);
    if (empty($loaded['ok'])) {
        return $loaded;
    }
    $user = $loaded['user'];
    if (kpi_v1_auth_user_is_disabled($user)) {
        return ['ok' => false, 'error' => 'user_disabled'];
    }
    $result = kpi_v1_password_reset_admin_send($cfg, $user, $locale);
    if (empty($result['ok'])) {
        return ['ok' => false, 'error' => isset($result['error']) ? (string) $result['error'] : 'reset_failed'];
    }
    return [
        'ok' => true,
        'user' => kpi_v1_admin_safe_user_row($user),
        'mailed' => !empty($result['mailed']),
        'email' => (string) ($user['email'] ?? ''),
    ];
}

/**
 * @return array{ok:true,user:array,sessionEpoch?:int}|array{ok:false,error:string}
 */
function kpi_v1_admin_set_disabled($cfg, $actor, $targetUserId, $disabled)
{
    $selfErr = kpi_v1_admin_actions_self_target_error($actor, $targetUserId);
    if ($selfErr !== null) {
        return ['ok' => false, 'error' => $selfErr];
    }
    $loaded = kpi_v1_admin_actions_load_target($targetUserId);
    if (empty($loaded['ok'])) {
        return $loaded;
    }
    $user = $loaded['user'];
    $user['disabled'] = !!$disabled;
    $user['disabledUpdatedAt'] = gmdate('c');
    kpi_v1_auth_write_user($user);

    $out = [
        'ok' => true,
        'user' => kpi_v1_admin_safe_user_row($user),
    ];
    if (!empty($user['disabled'])) {
        $epoch = kpi_v1_session_revoke_bump($user['userId']);
        if ($epoch !== null) {
            $out['sessionEpoch'] = $epoch;
        }
    }
    return $out;
}

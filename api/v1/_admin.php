<?php
/**
 * Founder Super Admin helpers + safe admin serializers.
 * Does not expose password_hash / tokens / config secrets.
 */

require_once __DIR__ . '/_auth.php';

function kpi_v1_auth_normalize_role($role)
{
    $r = strtolower(trim((string) $role));
    if ($r === 'founder_superadmin' || $r === 'admin_staff' || $r === 'support_readonly') {
        return $r;
    }
    return 'user';
}

function kpi_v1_auth_user_role($user)
{
    if (!is_array($user)) {
        return 'user';
    }
    if (!empty($user['role'])) {
        return kpi_v1_auth_normalize_role($user['role']);
    }
    return 'user';
}

/**
 * Founder gate: DB role OR config founderSuperAdminEmails (bootstrap only).
 * Never treats full_authorized / trial emails as admin automatically.
 */
function kpi_v1_auth_is_founder_superadmin($user, $cfg)
{
    if (!is_array($user)) {
        return false;
    }
    if (kpi_v1_auth_user_role($user) === 'founder_superadmin') {
        return true;
    }
    $email = isset($user['email']) ? strtolower(trim((string) $user['email'])) : '';
    if ($email === '') {
        return false;
    }
    $list = [];
    if (is_array($cfg) && !empty($cfg['founderSuperAdminEmails']) && is_array($cfg['founderSuperAdminEmails'])) {
        foreach ($cfg['founderSuperAdminEmails'] as $e) {
            $n = strtolower(trim((string) $e));
            if ($n !== '') {
                $list[] = $n;
            }
        }
    }
    return in_array($email, $list, true);
}

/**
 * Session required. 401 if unauthenticated, 403 if not founder.
 * @return array user
 */
function kpi_v1_auth_require_founder_superadmin($cfg)
{
    $uid = kpi_v1_auth_current_user_id();
    if ($uid === null) {
        kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
    }
    $user = kpi_v1_auth_read_user($uid);
    if ($user === null) {
        kpi_v1_auth_clear_session();
        kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
    }
    if (kpi_v1_auth_user_is_disabled($user)) {
        kpi_v1_auth_clear_session();
        kpi_v1_json_out(403, ['ok' => false, 'error' => 'account_disabled']);
    }
    if (!kpi_v1_auth_is_founder_superadmin($user, $cfg)) {
        kpi_v1_json_out(403, ['ok' => false, 'error' => 'forbidden']);
    }
    return $user;
}

/**
 * For PHP admin pages: return user or emit HTTP error page and exit.
 */
function kpi_v1_admin_require_founder_page($cfg)
{
    $uid = kpi_v1_auth_current_user_id();
    if ($uid === null) {
        http_response_code(401);
        header('Content-Type: text/plain; charset=utf-8');
        echo "401 unauthorized\n";
        exit;
    }
    $user = kpi_v1_auth_read_user($uid);
    if ($user === null) {
        kpi_v1_auth_clear_session();
        http_response_code(401);
        header('Content-Type: text/plain; charset=utf-8');
        echo "401 unauthorized\n";
        exit;
    }
    if (kpi_v1_auth_user_is_disabled($user) || !kpi_v1_auth_is_founder_superadmin($user, $cfg)) {
        http_response_code(403);
        header('Content-Type: text/plain; charset=utf-8');
        echo "403 forbidden\n";
        exit;
    }
    return $user;
}

function kpi_v1_admin_safe_user_row($user)
{
    if (!is_array($user)) {
        return null;
    }
    $out = [
        'userId' => (string) ($user['userId'] ?? ''),
        'email' => (string) ($user['email'] ?? ''),
        'plan' => isset($user['plan']) ? strtolower((string) $user['plan']) : 'basic',
        'disabled' => !empty($user['disabled']),
        'role' => kpi_v1_auth_user_role($user),
        'createdAt' => isset($user['createdAt']) ? (string) $user['createdAt'] : null,
        'planUpdatedAt' => isset($user['planUpdatedAt']) ? (string) $user['planUpdatedAt'] : null,
        'lastLoginAt' => isset($user['lastLoginAt']) ? (string) $user['lastLoginAt'] : null,
        'parentUserId' => isset($user['parentUserId']) && $user['parentUserId'] !== ''
            ? (string) $user['parentUserId']
            : null,
    ];
    if ($out['plan'] !== 'basic' && $out['plan'] !== 'pro') {
        $out['plan'] = 'pro';
    }
    return $out;
}

function kpi_v1_admin_dt_to_iso($dt)
{
    if ($dt === null || $dt === '') {
        return null;
    }
    $ts = strtotime((string) $dt . (preg_match('/Z|[+-]\\d\\d/', (string) $dt) ? '' : ' UTC'));
    if ($ts === false) {
        $ts = strtotime((string) $dt);
    }
    return $ts === false ? null : gmdate('c', $ts);
}

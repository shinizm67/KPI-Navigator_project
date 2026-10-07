<?php
/**
 * POST /api/v1/auth/login.php
 * Body: { "email": "...", "password": "..." }
 *
 * Failed attempts are counted per normalized email and REMOTE_ADDR.
 * After the threshold, further attempts from that pair are blocked until the window ends.
 * Unknown emails use the same generic failure as a wrong password.
 */

require_once __DIR__ . '/../_login_throttle.php';

/**
 * @return array{status:int, body:array}
 */
function kpi_v1_auth_attempt_login($cfg, $emailRaw, $password, $server, $now = null)
{
    $now = $now === null ? time() : (int) $now;
    $server = is_array($server) ? $server : [];
    $identity = kpi_v1_login_throttle_identity($emailRaw);
    $ip = kpi_v1_login_throttle_ip($server);
    $gate = kpi_v1_login_throttle_mutate($identity, $ip, 'check', $now);
    if ($gate === 'unavailable') {
        return ['status' => 503, 'body' => ['ok' => false, 'error' => 'login_unavailable']];
    }
    if ($gate === 'blocked') {
        return ['status' => 429, 'body' => ['ok' => false, 'error' => 'too_many_login_attempts']];
    }

    $email = kpi_v1_auth_normalize_email($emailRaw);
    $password = (string) $password;
    $user = null;
    if ($email !== null && $password !== '') {
        $index = kpi_v1_auth_read_email_index();
        if (isset($index[$email])) {
            $user = kpi_v1_auth_read_user($index[$email]);
        }
    }
    $valid = $user !== null
        && !empty($user['passwordHash'])
        && password_verify($password, (string) $user['passwordHash']);
    if (!$valid) {
        $recorded = kpi_v1_login_throttle_mutate($identity, $ip, 'fail', $now);
        if ($recorded === 'unavailable') {
            return ['status' => 503, 'body' => ['ok' => false, 'error' => 'login_unavailable']];
        }
        return ['status' => 401, 'body' => ['ok' => false, 'error' => 'invalid_credentials']];
    }
    if (kpi_v1_auth_user_is_disabled($user)) {
        return ['status' => 403, 'body' => ['ok' => false, 'error' => 'account_disabled']];
    }
    if (kpi_v1_login_throttle_mutate($identity, $ip, 'clear', $now) === 'unavailable') {
        return ['status' => 503, 'body' => ['ok' => false, 'error' => 'login_unavailable']];
    }

    require_once __DIR__ . '/../_admin_store.php';
    kpi_v1_admin_touch_last_login($cfg, $user['userId']);
    $fresh = kpi_v1_auth_read_user($user['userId']);
    if (is_array($fresh)) {
        $user = $fresh;
    }
    kpi_v1_auth_set_session_user($user['userId']);
    kpi_v1_auth_stamp_login_gen();
    return ['status' => 200, 'body' => array_merge(['ok' => true], kpi_v1_auth_public_user($user, $cfg))];
}

if (defined('KPI_V1_LOGIN_AS_LIBRARY')) {
    return;
}

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();
$email = isset($body['email']) ? $body['email'] : '';
$password = isset($body['password']) ? (string) $body['password'] : '';
$result = kpi_v1_auth_attempt_login($cfg, $email, $password, $_SERVER);
kpi_v1_json_out($result['status'], $result['body']);

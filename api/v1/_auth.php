<?php
/**
 * Phase B1-T1 — auth helpers (session cookie + file users).
 * Does not touch store.php / Phase A token gate.
 */

require_once __DIR__ . '/_bootstrap.php';

function kpi_v1_auth_cors($cfg)
{
    $origin = isset($cfg['corsOrigin']) ? (string) $cfg['corsOrigin'] : '*';
    header('Access-Control-Allow-Origin: ' . $origin);
    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, X-KPI-Plan-Admin-Token');
    header('Access-Control-Max-Age: 86400');
    if ($origin !== '*') {
        header('Access-Control-Allow-Credentials: true');
        header('Vary: Origin');
    }
}

function kpi_v1_auth_boot($cfg)
{
    kpi_v1_auth_cors($cfg);
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(204);
        exit;
    }
    if (session_status() !== PHP_SESSION_ACTIVE) {
        $secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
        session_name('KPISESSID');
        session_set_cookie_params([
            'lifetime' => 0,
            'path' => '/',
            'secure' => $secure,
            'httponly' => true,
            'samesite' => 'Lax',
        ]);
        session_start();
    }
}

function kpi_v1_auth_users_dir()
{
    $dir = __DIR__ . '/data/users';
    if (!is_dir($dir)) {
        mkdir($dir, 0750, true);
    }
    return $dir;
}

function kpi_v1_auth_email_index_path()
{
    return kpi_v1_auth_users_dir() . '/_email_index.json';
}

function kpi_v1_auth_user_path($userId)
{
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
    if ($safe === '' || strpos($safe, '_') === 0) {
        return null;
    }
    return kpi_v1_auth_users_dir() . '/' . $safe . '.json';
}

function kpi_v1_auth_read_email_index()
{
    $cfg = kpi_v1_load_config();
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        return kpi_v1_db_read_email_index($cfg);
    }
    $path = kpi_v1_auth_email_index_path();
    if (!is_file($path)) {
        return [];
    }
    $data = json_decode((string) file_get_contents($path), true);
    return is_array($data) ? $data : [];
}

function kpi_v1_auth_write_email_index($index)
{
    $cfg = kpi_v1_load_config();
    if (kpi_v1_storage_is_mysql($cfg)) {
        // Users table is source of truth; index writes are no-ops under MySQL.
        return;
    }
    $path = kpi_v1_auth_email_index_path();
    $tmp = $path . '.tmp';
    $json = json_encode($index, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false || file_put_contents($tmp, $json, LOCK_EX) === false) {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'index_write_failed']);
    }
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'index_rename_failed']);
    }
}

function kpi_v1_auth_read_user($userId)
{
    $cfg = kpi_v1_load_config();
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        return kpi_v1_db_read_user($cfg, $userId);
    }
    $path = kpi_v1_auth_user_path($userId);
    if ($path === null || !is_file($path)) {
        return null;
    }
    $data = json_decode((string) file_get_contents($path), true);
    return is_array($data) ? $data : null;
}

function kpi_v1_auth_write_user($user)
{
    if (!is_array($user) || empty($user['userId'])) {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'invalid_user']);
    }
    $cfg = kpi_v1_load_config();
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        try {
            kpi_v1_db_write_user($cfg, $user);
        } catch (PDOException $e) {
            $info = $e->errorInfo;
            if (isset($info[0]) && $info[0] === '23000') {
                kpi_v1_json_out(409, ['ok' => false, 'error' => 'email_taken']);
            }
            kpi_v1_json_out(500, ['ok' => false, 'error' => 'user_write_failed']);
        } catch (Throwable $e) {
            kpi_v1_json_out(500, ['ok' => false, 'error' => 'user_write_failed']);
        }
        return;
    }
    $path = kpi_v1_auth_user_path($user['userId']);
    if ($path === null) {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'invalid_user_id']);
    }
    $tmp = $path . '.tmp';
    $json = json_encode($user, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false || file_put_contents($tmp, $json, LOCK_EX) === false) {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'user_write_failed']);
    }
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'user_rename_failed']);
    }
}

function kpi_v1_auth_read_json_body()
{
    $raw = file_get_contents('php://input');
    $body = json_decode((string) $raw, true);
    if (!is_array($body)) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_json']);
    }
    return $body;
}

function kpi_v1_auth_normalize_email($email)
{
    $email = strtolower(trim((string) $email));
    if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        return null;
    }
    return $email;
}

function kpi_v1_auth_public_user($user, $cfg = null)
{
    $plan = 'pro';
    if (is_array($user) && isset($user['plan']) && (string) $user['plan'] !== '') {
        $p = strtolower(trim((string) $user['plan']));
        $plan = ($p === 'basic') ? 'basic' : 'pro';
    } elseif (is_array($cfg) && isset($cfg['legacyPlan'])) {
        $p = strtolower(trim((string) $cfg['legacyPlan']));
        $plan = ($p === 'basic') ? 'basic' : 'pro';
    }
    return [
        'userId' => (string) $user['userId'],
        'email' => (string) $user['email'],
        'plan' => $plan,
    ];
}

function kpi_v1_auth_set_session_user($userId)
{
    $_SESSION['kpi_user_id'] = (string) $userId;
}

function kpi_v1_auth_clear_session()
{
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000, $p['path'], $p['domain'] ?? '', !empty($p['secure']), !empty($p['httponly']));
    }
    session_destroy();
}

function kpi_v1_auth_current_user_id()
{
    if (empty($_SESSION['kpi_user_id'])) {
        return null;
    }
    return (string) $_SESSION['kpi_user_id'];
}

function kpi_v1_auth_require_post()
{
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
    }
}

function kpi_v1_auth_new_user_id()
{
    return 'u_' . bin2hex(random_bytes(8));
}

/**
 * Phase B2 — store.php boot (session + GET/PUT CORS).
 */
function kpi_v1_store_boot($cfg)
{
    $origin = isset($cfg['corsOrigin']) ? (string) $cfg['corsOrigin'] : '*';
    header('Access-Control-Allow-Origin: ' . $origin);
    header('Access-Control-Allow-Methods: GET, PUT, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, X-KPI-Store-Token, X-KPI-Plan-Admin-Token');
    header('Access-Control-Max-Age: 86400');
    if ($origin !== '*') {
        header('Access-Control-Allow-Credentials: true');
        header('Vary: Origin');
    }
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(204);
        exit;
    }
    if (session_status() !== PHP_SESSION_ACTIVE) {
        $secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
        session_name('KPISESSID');
        session_set_cookie_params([
            'lifetime' => 0,
            'path' => '/',
            'secure' => $secure,
            'httponly' => true,
            'samesite' => 'Lax',
        ]);
        session_start();
    }
}

/**
 * Resolve store userId: session (default) or legacy token gate.
 * storeAuthMode: session | token | dual
 */
function kpi_v1_store_resolve_user_id($cfg)
{
    $mode = isset($cfg['storeAuthMode']) ? (string) $cfg['storeAuthMode'] : 'session';

    if ($mode === 'session' || $mode === 'dual') {
        $uid = kpi_v1_auth_current_user_id();
        if ($uid !== null) {
            return $uid;
        }
        if ($mode === 'session') {
            kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
        }
    }

    kpi_v1_require_token($cfg);
    return (string) $cfg['userId'];
}

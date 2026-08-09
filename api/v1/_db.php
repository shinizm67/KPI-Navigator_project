<?php
/**
 * Phase B4-T2 — MySQL (PDO) helpers.
 * Default remains file storage until config storageDriver=mysql.
 */

require_once __DIR__ . '/_bootstrap.php';

/**
 * @return PDO|null
 */
function kpi_v1_db($cfg)
{
    static $pdo = null;
    static $tried = false;
    if ($tried) {
        return $pdo;
    }
    $tried = true;
    if (!kpi_v1_storage_is_mysql($cfg)) {
        return null;
    }
    $host = isset($cfg['dbHost']) ? (string) $cfg['dbHost'] : '127.0.0.1';
    $port = isset($cfg['dbPort']) ? (int) $cfg['dbPort'] : 3306;
    $name = isset($cfg['dbName']) ? (string) $cfg['dbName'] : '';
    $user = isset($cfg['dbUser']) ? (string) $cfg['dbUser'] : '';
    $pass = isset($cfg['dbPass']) ? (string) $cfg['dbPass'] : '';
    $charset = isset($cfg['dbCharset']) ? (string) $cfg['dbCharset'] : 'utf8mb4';
    if ($name === '' || $user === '') {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'db_config_missing']);
    }
    $dsn = 'mysql:host=' . $host . ';port=' . $port . ';dbname=' . $name . ';charset=' . $charset;
    try {
        $pdo = new PDO($dsn, $user, $pass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
    } catch (Throwable $e) {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'db_connect_failed']);
    }
    return $pdo;
}

function kpi_v1_db_json_encode($value)
{
    if ($value === null) {
        return null;
    }
    $json = json_encode($value, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    return ($json === false) ? null : $json;
}

function kpi_v1_db_json_decode_object($raw)
{
    if ($raw === null || $raw === '') {
        return null;
    }
    $data = json_decode((string) $raw, false);
    return is_object($data) ? $data : null;
}

function kpi_v1_db_read_blob($cfg, $userId)
{
    $pdo = kpi_v1_db($cfg);
    $stmt = $pdo->prepare('SELECT store_json, annual_nav_json, pl_json, updated_at FROM kpi_store WHERE user_id = ? LIMIT 1');
    $stmt->execute([(string) $userId]);
    $row = $stmt->fetch();
    $empty = (object) [
        'userId' => $userId,
        'updatedAt' => null,
        'store' => null,
        'annualNav' => null,
        'pl' => null,
    ];
    if (!$row) {
        return $empty;
    }
    $updated = null;
    if (!empty($row['updated_at'])) {
        $updated = gmdate('c', strtotime($row['updated_at'] . ' UTC'));
    }
    return (object) [
        'userId' => $userId,
        'updatedAt' => $updated,
        'store' => kpi_v1_db_json_decode_object($row['store_json']),
        'annualNav' => kpi_v1_db_json_decode_object($row['annual_nav_json']),
        'pl' => kpi_v1_db_json_decode_object($row['pl_json']),
    ];
}

function kpi_v1_db_write_blob($cfg, $userId, $blob)
{
    $pdo = kpi_v1_db($cfg);
    $updatedAt = isset($blob->updatedAt) ? (string) $blob->updatedAt : gmdate('c');
    $ts = gmdate('Y-m-d H:i:s', strtotime($updatedAt) ?: time());
    $stmt = $pdo->prepare(
        'INSERT INTO kpi_store (user_id, store_json, annual_nav_json, pl_json, updated_at)
         VALUES (?, ?, ?, ?, ?)
         ON DUPLICATE KEY UPDATE
           store_json = VALUES(store_json),
           annual_nav_json = VALUES(annual_nav_json),
           pl_json = VALUES(pl_json),
           updated_at = VALUES(updated_at)'
    );
    $stmt->execute([
        (string) $userId,
        kpi_v1_db_json_encode(isset($blob->store) ? $blob->store : null),
        kpi_v1_db_json_encode(isset($blob->annualNav) ? $blob->annualNav : null),
        kpi_v1_db_json_encode(isset($blob->pl) ? $blob->pl : null),
        $ts,
    ]);
}

function kpi_v1_db_read_user($cfg, $userId)
{
    $pdo = kpi_v1_db($cfg);
    $stmt = $pdo->prepare(
        'SELECT user_id, email, password_hash, plan, plan_updated_at, created_at
         FROM kpi_users WHERE user_id = ? LIMIT 1'
    );
    $stmt->execute([(string) $userId]);
    $row = $stmt->fetch();
    if (!$row) {
        return null;
    }
    $user = [
        'userId' => (string) $row['user_id'],
        'email' => (string) $row['email'],
        'passwordHash' => (string) $row['password_hash'],
        'plan' => (string) $row['plan'],
        'createdAt' => !empty($row['created_at'])
            ? gmdate('c', strtotime($row['created_at'] . ' UTC'))
            : gmdate('c'),
    ];
    if (!empty($row['plan_updated_at'])) {
        $user['planUpdatedAt'] = gmdate('c', strtotime($row['plan_updated_at'] . ' UTC'));
    }
    return $user;
}

function kpi_v1_db_write_user($cfg, $user)
{
    $pdo = kpi_v1_db($cfg);
    $userId = (string) $user['userId'];
    $email = (string) $user['email'];
    $hash = (string) $user['passwordHash'];
    $plan = isset($user['plan']) ? (string) $user['plan'] : 'basic';
    $created = isset($user['createdAt']) ? (string) $user['createdAt'] : gmdate('c');
    $createdTs = gmdate('Y-m-d H:i:s', strtotime($created) ?: time());
    $planUpdatedTs = null;
    if (!empty($user['planUpdatedAt'])) {
        $planUpdatedTs = gmdate('Y-m-d H:i:s', strtotime((string) $user['planUpdatedAt']) ?: time());
    }
    $now = gmdate('Y-m-d H:i:s');
    $stmt = $pdo->prepare(
        'INSERT INTO kpi_users (user_id, email, password_hash, plan, plan_updated_at, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?)
         ON DUPLICATE KEY UPDATE
           email = VALUES(email),
           password_hash = VALUES(password_hash),
           plan = VALUES(plan),
           plan_updated_at = VALUES(plan_updated_at),
           updated_at = VALUES(updated_at)'
    );
    $stmt->execute([$userId, $email, $hash, $plan, $planUpdatedTs, $createdTs, $now]);
}

function kpi_v1_db_find_user_id_by_email($cfg, $email)
{
    $pdo = kpi_v1_db($cfg);
    $stmt = $pdo->prepare('SELECT user_id FROM kpi_users WHERE email = ? LIMIT 1');
    $stmt->execute([(string) $email]);
    $row = $stmt->fetch();
    return $row ? (string) $row['user_id'] : null;
}

/**
 * Email index shim for MySQL (map email => userId).
 */
function kpi_v1_db_read_email_index($cfg)
{
    $pdo = kpi_v1_db($cfg);
    $stmt = $pdo->query('SELECT email, user_id FROM kpi_users');
    $index = [];
    while ($row = $stmt->fetch()) {
        $index[(string) $row['email']] = (string) $row['user_id'];
    }
    return $index;
}

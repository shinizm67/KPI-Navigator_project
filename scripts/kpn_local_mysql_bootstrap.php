<?php
/**
 * BR-LOCAL-VERIFY-01 Phase 3A.
 * Create or recreate kpn_local_test from api/v1/schema.sql.
 *
 * The process that runs init/recreate connects with the machine-local
 * bootstrap/admin identity. The KPN runtime identity is a different user,
 * stored only in an untracked machine-local file, with DML on kpn_local_test.
 *
 * Host and database name still come from the guarded config. The admin file
 * cannot retarget the connection.
 *
 *   php scripts/kpn_local_mysql_bootstrap.php init
 *   php scripts/kpn_local_mysql_bootstrap.php recreate
 */

if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "local_test_refused:cli\n");
    exit(1);
}

require_once __DIR__ . '/../api/v1/_db.php';
require_once __DIR__ . '/../api/v1/_local_test_guard.php';

if (isset($_SERVER['SCRIPT_FILENAME']) && realpath((string) $_SERVER['SCRIPT_FILENAME']) === realpath(__FILE__)) {
    kpn_local_mysql_bootstrap_main($argv);
}

function kpn_local_mysql_bootstrap_main($argv)
{
    $cmd = isset($argv[1]) ? (string) $argv[1] : '';
    if ($cmd !== 'init' && $cmd !== 'recreate') {
        fwrite(STDERR, "usage: php scripts/kpn_local_mysql_bootstrap.php init|recreate\n");
        exit(1);
    }

    $cfg = kpi_v1_load_config();
    if (empty($cfg['localTestMode']) || !kpi_v1_storage_is_mysql($cfg)) {
        fwrite(STDERR, "local_test_refused:fixture\n");
        exit(1);
    }
    $dbName = isset($cfg['dbName']) ? (string) $cfg['dbName'] : '';
    if (!kpi_v1_local_test_mysql_db_allowed($dbName)) {
        fwrite(STDERR, "local_test_refused:db_name\n");
        exit(1);
    }

    $schemaPath = __DIR__ . '/../api/v1/schema.sql';
    $schema = is_file($schemaPath) ? file_get_contents($schemaPath) : false;
    if (!is_string($schema) || trim($schema) === '') {
        fwrite(STDERR, "local_mysql_bootstrap_failed:schema\n");
        exit(1);
    }

    $literal = 'kpn_local_test';
    try {
        $pdo = kpi_v1_db_open(kpn_local_mysql_admin_cfg($cfg), false);
        if ($cmd === 'recreate') {
            $pdo->exec('DROP DATABASE IF EXISTS `' . $literal . '`');
        }
        $pdo->exec(
            'CREATE DATABASE IF NOT EXISTS `' . $literal . '` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
        );
        $pdo->exec('USE `' . $literal . '`');
        kpn_local_mysql_apply_schema($pdo, $schema);
        kpn_local_mysql_ensure_runtime($pdo);
    } catch (Throwable $e) {
        $code = $e instanceof PDOException ? preg_replace('/[^A-Za-z0-9]/', '', (string) $e->getCode()) : 'error';
        if ($code === '') {
            $code = 'error';
        }
        fwrite(STDERR, 'local_mysql_bootstrap_failed:' . $code . "\n");
        exit(1);
    }

    echo "bootstrapped {$literal}\n";
    exit(0);
}

function kpn_local_mysql_machine_dir()
{
    $override = getenv('KPN_LOCAL_MYSQL_HOME');
    if (is_string($override) && $override !== '') {
        return rtrim(str_replace('\\', '/', $override), '/');
    }
    $local = getenv('LOCALAPPDATA');
    if (is_string($local) && $local !== '') {
        return rtrim(str_replace('\\', '/', $local), '/') . '/kpn-tools';
    }
    $home = getenv('HOME');
    if (!is_string($home) || $home === '') {
        fwrite(STDERR, "local_mysql_bootstrap_failed:identity\n");
        exit(1);
    }
    return rtrim(str_replace('\\', '/', $home), '/') . '/.kpn-tools';
}

function kpn_local_mysql_identity_path($role)
{
    $envName = $role === 'admin' ? 'KPN_LOCAL_MYSQL_ADMIN_CONFIG' : 'KPN_LOCAL_MYSQL_RUNTIME_CONFIG';
    $override = getenv($envName);
    if (is_string($override) && $override !== '') {
        return str_replace('\\', '/', $override);
    }
    return kpn_local_mysql_machine_dir() . '/kpn-local-mysql-' . $role . '.php';
}

function kpn_local_mysql_read_identity($role)
{
    $path = kpn_local_mysql_identity_path($role);
    if (!is_file($path)) {
        return null;
    }
    $data = require $path;
    return is_array($data) ? $data : null;
}

/**
 * Admin user and password come from the machine-local file.
 * Host, port, database name, and localTestMode stay on the guarded config.
 *
 * @param array $guarded
 * @return array
 */
function kpn_local_mysql_admin_cfg($guarded)
{
    $id = kpn_local_mysql_read_identity('admin');
    $user = is_array($id) && isset($id['dbUser']) ? (string) $id['dbUser'] : '';
    if ($user === '' || !preg_match('/^[A-Za-z0-9_]+$/', $user)) {
        fwrite(STDERR, "local_mysql_bootstrap_failed:admin_identity\n");
        exit(1);
    }
    $cfg = $guarded;
    $cfg['dbUser'] = $user;
    $cfg['dbPass'] = is_array($id) && isset($id['dbPass']) ? (string) $id['dbPass'] : '';
    return $cfg;
}

function kpn_local_mysql_ensure_runtime(PDO $pdo)
{
    $path = kpn_local_mysql_identity_path('runtime');
    $dir = dirname($path);
    if (!is_dir($dir) && !@mkdir($dir, 0700, true) && !is_dir($dir)) {
        fwrite(STDERR, "local_mysql_bootstrap_failed:runtime_identity\n");
        exit(1);
    }
    $existing = kpn_local_mysql_read_identity('runtime');
    $user = 'kpn_local_runtime';
    if (
        is_array($existing)
        && isset($existing['dbUser'], $existing['dbPass'])
        && (string) $existing['dbUser'] === $user
        && preg_match('/^[A-Za-z0-9]+$/', (string) $existing['dbPass'])
    ) {
        $pass = (string) $existing['dbPass'];
    } else {
        $pass = bin2hex(random_bytes(24));
        $php = "<?php\nreturn [\n    'dbUser' => 'kpn_local_runtime',\n    'dbPass' => '" . $pass . "',\n];\n";
        if (file_put_contents($path, $php, LOCK_EX) === false) {
            fwrite(STDERR, "local_mysql_bootstrap_failed:runtime_identity\n");
            exit(1);
        }
    }
    foreach (array('127.0.0.1', 'localhost') as $host) {
        $account = "'" . $user . "'@'" . $host . "'";
        $pdo->exec('CREATE USER IF NOT EXISTS ' . $account . " IDENTIFIED BY '" . $pass . "'");
        $pdo->exec('ALTER USER ' . $account . " IDENTIFIED BY '" . $pass . "'");
        try {
            $pdo->exec('REVOKE ALL PRIVILEGES, GRANT OPTION FROM ' . $account);
        } catch (PDOException $e) {
            /* A brand-new account may have nothing beyond implicit USAGE. */
        }
        $pdo->exec(
            'GRANT SELECT, INSERT, UPDATE, DELETE ON `kpn_local_test`.* TO ' . $account
        );
    }
}

function kpn_local_mysql_apply_schema(PDO $pdo, $sql)
{
    $kept = [];
    foreach (preg_split("/\r\n|\n|\r/", (string) $sql) as $line) {
        if (strpos(ltrim($line), '--') === 0) {
            continue;
        }
        $kept[] = $line;
    }
    foreach (explode(';', implode("\n", $kept)) as $stmt) {
        $stmt = trim($stmt);
        if ($stmt === '') {
            continue;
        }
        $pdo->exec($stmt);
    }
}

<?php
/**
 * Shared bootstrap for api/v1 (no secrets in git — use config.local.php).
 */

function kpi_v1_send_cors($origin)
{
    header('Access-Control-Allow-Origin: ' . $origin);
    header('Access-Control-Allow-Methods: GET, PUT, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, X-KPI-Store-Token');
    header('Access-Control-Max-Age: 86400');
}

function kpi_v1_load_config()
{
    $local = __DIR__ . '/config.local.php';
    $example = __DIR__ . '/config.example.php';
    if (is_file($local)) {
        $cfg = require $local;
    } else {
        $cfg = require $example;
    }
    if (!is_array($cfg)) {
        $cfg = [];
    }
    return array_merge(
        [
            'token' => 'dev-change-me',
            'userId' => 'default',
            'corsOrigin' => '*',
            'storeAuthMode' => 'session',
            // B3: new registrations; users missing plan use legacyPlan
            'defaultPlan' => 'basic',
            'legacyPlan' => 'pro',
            // Local QA: allow logged-in user to POST /auth/set-plan.php
            'allowSelfPlanChange' => true,
            'planAdminToken' => 'dev-plan-admin-change-me',
            // Token-mode store (no user file): treat as this plan
            'tokenModePlan' => 'pro',
            // B4-T1: PUT 前に現行 blob を backups/ へ
            'backupEnabled' => true,
            'backupKeep' => 10,
        ],
        $cfg
    );
}

function kpi_v1_json_out($code, $payload)
{
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function kpi_v1_require_token($cfg)
{
    $hdr = '';
    if (isset($_SERVER['HTTP_X_KPI_STORE_TOKEN'])) {
        $hdr = (string) $_SERVER['HTTP_X_KPI_STORE_TOKEN'];
    } elseif (isset($_GET['token'])) {
        // Convenience for quick curl smoke only; prefer header in apps.
        $hdr = (string) $_GET['token'];
    }
    $expected = (string) $cfg['token'];
    if ($expected === '' || !hash_equals($expected, $hdr)) {
        kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized']);
    }
}

function kpi_v1_data_path($userId)
{
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
    if ($safe === '') {
        $safe = 'default';
    }
    $dir = __DIR__ . '/data';
    if (!is_dir($dir)) {
        mkdir($dir, 0750, true);
    }
    return $dir . '/' . $safe . '.json';
}

function kpi_v1_read_blob($path)
{
    $empty = (object) [
        'userId' => null,
        'updatedAt' => null,
        'store' => null,
        'annualNav' => null,
        'pl' => null,
    ];
    if (!is_file($path)) {
        return $empty;
    }
    $raw = file_get_contents($path);
    // assoc=false keeps {} as objects (not PHP empty arrays)
    $data = json_decode($raw, false);
    if (!is_object($data)) {
        return $empty;
    }
    return (object) [
        'userId' => isset($data->userId) ? $data->userId : null,
        'updatedAt' => isset($data->updatedAt) ? $data->updatedAt : null,
        'store' => property_exists($data, 'store') ? $data->store : null,
        'annualNav' => property_exists($data, 'annualNav') ? $data->annualNav : null,
        'pl' => property_exists($data, 'pl') ? $data->pl : null,
    ];
}

function kpi_v1_write_blob($path, $blob)
{
    $tmp = $path . '.tmp';
    $json = json_encode($blob, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false) {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'encode_failed']);
    }
    if (file_put_contents($tmp, $json, LOCK_EX) === false) {
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'write_failed']);
    }
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'rename_failed']);
    }
}

/**
 * B4-T1 — directory for per-user store backups (under data/, blocked by .htaccess).
 */
function kpi_v1_backup_dir($userId)
{
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
    if ($safe === '') {
        $safe = 'default';
    }
    $dir = __DIR__ . '/data/backups/' . $safe;
    if (!is_dir($dir)) {
        mkdir($dir, 0750, true);
    }
    return $dir;
}

/**
 * Copy current on-disk blob to backups/{userId}/{timestamp}.json, then prune to backupKeep.
 * No-op when backupEnabled is false or there is no existing file yet.
 */
function kpi_v1_backup_blob($cfg, $userId)
{
    if (empty($cfg['backupEnabled'])) {
        return;
    }
    $path = kpi_v1_data_path($userId);
    if (!is_file($path)) {
        return;
    }
    $keep = isset($cfg['backupKeep']) ? (int) $cfg['backupKeep'] : 10;
    if ($keep < 1) {
        $keep = 1;
    }
    $dir = kpi_v1_backup_dir($userId);
    $stamp = gmdate('Ymd\THis') . '_' . bin2hex(random_bytes(2));
    $dest = $dir . '/' . $stamp . '.json';
    if (!@copy($path, $dest)) {
        return;
    }
    $files = glob($dir . '/*.json');
    if (!is_array($files) || count($files) <= $keep) {
        return;
    }
    usort($files, function ($a, $b) {
        $ma = @filemtime($a);
        $mb = @filemtime($b);
        if ($ma === $mb) {
            return strcmp($a, $b);
        }
        return ($ma < $mb) ? -1 : 1;
    });
    $excess = count($files) - $keep;
    for ($i = 0; $i < $excess; $i++) {
        @unlink($files[$i]);
    }
}

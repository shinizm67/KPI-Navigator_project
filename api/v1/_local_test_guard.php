<?php
/**
 * BR-LOCAL-VERIFY-01 Phase 1.
 * Active only when config localTestMode === true.
 * Refuses production hosts, non-loopback DB/FTP, and mail().
 */

function kpi_v1_local_test_fail($reason)
{
    $reason = preg_replace('/[^a-z0-9_]/', '', (string) $reason);
    if ($reason === '') {
        $reason = 'refused';
    }
    if (PHP_SAPI === 'cli') {
        fwrite(STDERR, 'local_test_refused:' . $reason . "\n");
        exit(1);
    }
    http_response_code(500);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['ok' => false, 'error' => 'local_test_refused', 'reason' => $reason]);
    exit;
}

function kpi_v1_local_test_host_from_value($value)
{
    $value = trim((string) $value);
    if ($value === '') {
        return '';
    }
    if (preg_match('#^[a-z][a-z0-9+.-]*://#i', $value)) {
        $parts = parse_url($value);
        $value = isset($parts['host']) ? (string) $parts['host'] : '';
    }
    $value = strtolower($value);
    if (isset($value[0]) && $value[0] === '[') {
        $end = strpos($value, ']');
        $value = $end === false ? trim($value, '[]') : substr($value, 1, $end - 1);
    } else {
        $value = preg_replace('/:\d+$/', '', $value);
    }
    return $value;
}

function kpi_v1_local_test_is_loopback($host)
{
    return $host === '' || $host === 'localhost' || $host === '127.0.0.1' || $host === '::1';
}

function kpi_v1_local_test_is_production_host($host)
{
    if ($host === '') {
        return false;
    }
    $host = strtolower($host);
    $suffix = 'forge-laboratory.com';
    if ($host === $suffix || substr($host, -strlen('.' . $suffix)) === '.' . $suffix) {
        return true;
    }
    if (strpos($host, 'lolipop') !== false) {
        return true;
    }
    return false;
}

function kpi_v1_local_test_assert($cfg)
{
    if (!is_array($cfg) || empty($cfg['localTestMode'])) {
        return;
    }
    $driver = isset($cfg['storageDriver']) ? strtolower(trim((string) $cfg['storageDriver'])) : 'file';
    if ($driver !== 'file') {
        kpi_v1_local_test_fail('storage_driver');
    }
    $dbHost = kpi_v1_local_test_host_from_value(isset($cfg['dbHost']) ? $cfg['dbHost'] : '');
    if (!kpi_v1_local_test_is_loopback($dbHost) || kpi_v1_local_test_is_production_host($dbHost)) {
        kpi_v1_local_test_fail('db_host');
    }
    foreach (['ftpHost', 'ftpUrl'] as $ftpKey) {
        if (!isset($cfg[$ftpKey]) || trim((string) $cfg[$ftpKey]) === '') {
            continue;
        }
        $ftpHost = kpi_v1_local_test_host_from_value($cfg[$ftpKey]);
        if (!kpi_v1_local_test_is_loopback($ftpHost) || kpi_v1_local_test_is_production_host($ftpHost)) {
            kpi_v1_local_test_fail('ftp_host');
        }
    }
    foreach (['ftpUser', 'ftpPass', 'ftpPassword'] as $secretKey) {
        if (isset($cfg[$secretKey]) && trim((string) $cfg[$secretKey]) !== '') {
            kpi_v1_local_test_fail('ftp_credential');
        }
    }
    $resetUrl = isset($cfg['passwordResetBaseUrl']) ? trim((string) $cfg['passwordResetBaseUrl']) : '';
    $resetHost = kpi_v1_local_test_host_from_value($resetUrl);
    if ($resetUrl === '' || !kpi_v1_local_test_is_loopback($resetHost) || kpi_v1_local_test_is_production_host($resetHost)) {
        kpi_v1_local_test_fail('reset_url');
    }
    foreach (['supportEmail', 'supportFrom'] as $mailKey) {
        $mail = isset($cfg[$mailKey]) ? strtolower(trim((string) $cfg[$mailKey])) : '';
        if ($mail !== '' && substr($mail, -strlen('@forge-laboratory.com')) === '@forge-laboratory.com') {
            kpi_v1_local_test_fail('mail_address');
        }
    }
    foreach ($cfg as $key => $value) {
        if (!is_string($value) || strpos($value, '://') === false) {
            continue;
        }
        $host = kpi_v1_local_test_host_from_value($value);
        if (kpi_v1_local_test_is_production_host($host) || !kpi_v1_local_test_is_loopback($host)) {
            kpi_v1_local_test_fail('url_host');
        }
    }
    $root = isset($cfg['localDataRoot']) ? trim((string) $cfg['localDataRoot']) : '';
    $rootNorm = str_replace('\\', '/', $root);
    $absolute = (bool) preg_match('#^[A-Za-z]:/#', $rootNorm) || (isset($rootNorm[0]) && $rootNorm[0] === '/');
    if ($root === '' || !$absolute || !is_dir($root)) {
        kpi_v1_local_test_fail('data_root');
    }
    $rootReal = realpath($root);
    $live = realpath(__DIR__ . '/data');
    if ($rootReal === false) {
        kpi_v1_local_test_fail('data_root');
    }
    $rootRealNorm = str_replace('\\', '/', $rootReal);
    if (strpos($rootRealNorm, 'forge-laboratory') !== false || strpos(strtolower($rootRealNorm), 'lolipop') !== false) {
        kpi_v1_local_test_fail('data_root');
    }
    if ($live !== false) {
        $liveNorm = str_replace('\\', '/', $live);
        if ($rootRealNorm === $liveNorm || strpos($rootRealNorm, $liveNorm . '/') === 0) {
            kpi_v1_local_test_fail('data_root');
        }
    }
    $requestHost = '';
    if (isset($_SERVER['HTTP_HOST'])) {
        $requestHost = kpi_v1_local_test_host_from_value($_SERVER['HTTP_HOST']);
    }
    if ($requestHost !== '' && (!kpi_v1_local_test_is_loopback($requestHost) || kpi_v1_local_test_is_production_host($requestHost))) {
        kpi_v1_local_test_fail('request_host');
    }
}

function kpi_v1_local_test_note_mail_blocked($cfg)
{
    $root = isset($cfg['localDataRoot']) ? rtrim(str_replace('\\', '/', (string) $cfg['localDataRoot']), '/') : '';
    if ($root === '') {
        return;
    }
    @file_put_contents($root . '/mail-blocked.log', gmdate('c') . " blocked\n", FILE_APPEND | LOCK_EX);
}

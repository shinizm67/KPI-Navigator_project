<?php
/**
 * Per-user session revoke epoch (file-backed).
 * No DB schema. Force Logout / Disable bumps epoch; login stamps session epoch;
 * subsequent requests clear sessions with older epoch.
 */

function kpi_v1_session_revoke_dir()
{
    $dir = __DIR__ . '/data/session_revoke';
    if (!is_dir($dir)) {
        mkdir($dir, 0750, true);
    }
    return $dir;
}

function kpi_v1_session_revoke_safe_user_id($userId)
{
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
    if ($safe === '' || strpos($safe, '_') === 0) {
        return null;
    }
    return $safe;
}

function kpi_v1_session_revoke_path($userId)
{
    $safe = kpi_v1_session_revoke_safe_user_id($userId);
    if ($safe === null) {
        return null;
    }
    return kpi_v1_session_revoke_dir() . '/' . $safe . '.json';
}

/**
 * @return int epoch >= 0
 */
function kpi_v1_session_revoke_get_epoch($userId)
{
    $path = kpi_v1_session_revoke_path($userId);
    if ($path === null || !is_file($path)) {
        return 0;
    }
    $data = json_decode((string) file_get_contents($path), true);
    if (!is_array($data) || !isset($data['epoch'])) {
        return 0;
    }
    $n = (int) $data['epoch'];
    return $n < 0 ? 0 : $n;
}

/**
 * Bump revoke epoch for user. Returns new epoch or null on failure.
 * @return int|null
 */
function kpi_v1_session_revoke_bump($userId)
{
    $path = kpi_v1_session_revoke_path($userId);
    if ($path === null) {
        return null;
    }
    $next = kpi_v1_session_revoke_get_epoch($userId) + 1;
    $payload = [
        'userId' => (string) $userId,
        'epoch' => $next,
        'updatedAt' => gmdate('c'),
    ];
    $json = json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    $tmp = $path . '.tmp';
    if ($json === false || file_put_contents($tmp, $json, LOCK_EX) === false) {
        return null;
    }
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        return null;
    }
    return $next;
}

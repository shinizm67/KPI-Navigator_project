<?php
/**
 * Login failure throttle. Key is normalized email + REMOTE_ADDR.
 * A block expires. It is not a permanent lock, and another IP is a different key.
 * Forwarded client-IP headers are ignored.
 */

require_once __DIR__ . '/_auth.php';

function kpi_v1_login_throttle_policy()
{
    return [
        'threshold' => 5,
        'windowSeconds' => 900,
        'blockSeconds' => 900,
    ];
}

function kpi_v1_login_throttle_identity($emailRaw)
{
    $norm = kpi_v1_auth_normalize_email($emailRaw);
    if ($norm !== null) {
        return $norm;
    }
    return 'invalid:' . hash('sha256', (string) $emailRaw);
}

function kpi_v1_login_throttle_ip($server)
{
    $ip = '';
    if (is_array($server) && isset($server['REMOTE_ADDR'])) {
        $ip = trim((string) $server['REMOTE_ADDR']);
    }
    if ($ip === '' || strlen($ip) > 128 || preg_match('/[\r\n]/', $ip)) {
        return 'unknown';
    }
    return $ip;
}

function kpi_v1_login_throttle_path($identity, $ip)
{
    $dir = kpi_v1_file_data_root() . '/login_throttle';
    if (!is_dir($dir)) {
        @mkdir($dir, 0750, true);
    }
    $name = hash('sha256', $identity . "\n" . $ip);
    return $dir . '/' . $name . '.json';
}

/**
 * @param 'check'|'fail'|'clear' $op
 * @return 'ok'|'blocked'|'unavailable'
 */
function kpi_v1_login_throttle_mutate($identity, $ip, $op, $now)
{
    $policy = kpi_v1_login_throttle_policy();
    $now = (int) $now;
    $path = kpi_v1_login_throttle_path($identity, $ip);
    if ($op === 'clear') {
        if (is_file($path) && !@unlink($path)) {
            return 'unavailable';
        }
        return 'ok';
    }
    $fh = @fopen($path, 'c+');
    if ($fh === false) {
        return 'unavailable';
    }
    if (!flock($fh, LOCK_EX)) {
        fclose($fh);
        return 'unavailable';
    }
    try {
        $raw = stream_get_contents($fh);
        $data = json_decode((string) $raw, true);
        $failures = [];
        $blockedUntil = 0;
        if (is_array($data)) {
            $blockedUntil = isset($data['blockedUntil']) ? (int) $data['blockedUntil'] : 0;
            if (isset($data['failures']) && is_array($data['failures'])) {
                foreach ($data['failures'] as $t) {
                    $t = (int) $t;
                    if ($t > $now - $policy['windowSeconds'] && $t <= $now) {
                        $failures[] = $t;
                    }
                }
            }
        }
        if ($blockedUntil > 0 && $blockedUntil <= $now) {
            $blockedUntil = 0;
            $failures = [];
        }
        if ($blockedUntil > $now) {
            return 'blocked';
        }
        if ($op === 'fail') {
            $failures[] = $now;
            if (count($failures) >= $policy['threshold']) {
                $blockedUntil = $now + $policy['blockSeconds'];
            }
        }
        $json = json_encode([
            'failures' => $failures,
            'blockedUntil' => $blockedUntil,
        ]);
        if ($json === false || ftruncate($fh, 0) === false || rewind($fh) === false || fwrite($fh, $json) === false) {
            return 'unavailable';
        }
        fflush($fh);
        return 'ok';
    } finally {
        flock($fh, LOCK_UN);
        fclose($fh);
    }
}

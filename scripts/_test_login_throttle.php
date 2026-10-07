<?php
/**
 * Login throttle. File storage, injected clock. No network.
 */

$root = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'kpn-login-throttle-' . getmypid() . '-' . bin2hex(random_bytes(4));
if (!mkdir($root, 0700, true)) {
    fwrite(STDERR, "cannot create temp root\n");
    exit(1);
}
$configPath = $root . DIRECTORY_SEPARATOR . 'config.php';
file_put_contents($configPath, "<?php\nreturn " . var_export([
    'localTestMode' => true,
    'localDataRoot' => $root,
    'storageDriver' => 'file',
    'dbHost' => '127.0.0.1',
    'dbPort' => 3306,
    'dbName' => '',
    'dbUser' => '',
    'dbPass' => '',
    'corsOrigin' => 'http://127.0.0.1',
    'passwordResetBaseUrl' => 'http://127.0.0.1/kpi-navigator',
    'supportEmail' => 'sandbox@example.com',
    'supportFrom' => 'sandbox@example.com',
], true) . ";\n");
putenv('KPI_V1_CONFIG=' . $configPath);
$_ENV['KPI_V1_CONFIG'] = $configPath;

define('KPI_V1_LOGIN_AS_LIBRARY', true);
require dirname(__DIR__) . '/api/v1/auth/login.php';
require_once dirname(__DIR__) . '/api/v1/_registration.php';
require_once dirname(__DIR__) . '/api/v1/_password_reset.php';

$failed = 0;
function check($name, $ok, $detail = '')
{
    global $failed;
    if ($ok) {
        echo "PASS\t$name\n";
        return;
    }
    $failed++;
    echo "FAIL\t$name" . ($detail !== '' ? "\t$detail" : '') . "\n";
}

$cfg = kpi_v1_load_config();
$_SERVER['REQUEST_METHOD'] = 'POST';
$_SERVER['HTTPS'] = 'off';
kpi_v1_auth_boot($cfg);

function make_user($id, $email, $password)
{
    $hash = password_hash($password, PASSWORD_DEFAULT);
    kpi_v1_auth_write_user([
        'userId' => $id,
        'email' => $email,
        'passwordHash' => $hash,
        'plan' => 'basic',
        'role' => 'user',
        'disabled' => false,
        'createdAt' => gmdate('c'),
    ]);
    $index = kpi_v1_auth_read_email_index();
    $index[$email] = $id;
    kpi_v1_auth_write_email_index($index);
}

make_user('u_login_a', 'a@example.com', 'Abcd123!');
make_user('u_login_b', 'b@example.com', 'Abcd123!');

function attempt($email, $password, $ip, $now)
{
    return kpi_v1_auth_attempt_login(
        kpi_v1_load_config(),
        $email,
        $password,
        ['REMOTE_ADDR' => $ip],
        $now
    );
}

function err($result)
{
    return isset($result['body']['error']) ? $result['body']['error'] : '';
}

$t = 1_000_000;
$ok = attempt('a@example.com', 'Abcd123!', '10.0.0.1', $t);
check(
    '1 valid login still works',
    $ok['status'] === 200 && !empty($ok['body']['ok']) && $ok['body']['userId'] === 'u_login_a' && kpi_v1_auth_current_user_id() === 'u_login_a',
    (string) $ok['status']
);

$bad = attempt('a@example.com', 'wrong-pass-1!', '10.0.0.1', $t + 10);
check('2 one invalid password is generic auth failure', $bad['status'] === 401 && err($bad) === 'invalid_credentials');

$ip = '10.1.0.8';
$base = $t + 100;
$last = null;
for ($i = 1; $i <= 5; $i++) {
    $last = attempt('a@example.com', 'wrong-pass-1!', $ip, $base + $i);
}
check('3 five failures stay generic', $last['status'] === 401 && err($last) === 'invalid_credentials', err($last) . ' ' . $last['status']);
$blocked = attempt('a@example.com', 'wrong-pass-1!', $ip, $base + 6);
check('4 sixth attempt is 429', $blocked['status'] === 429 && err($blocked) === 'too_many_login_attempts', (string) $blocked['status'] . ' ' . err($blocked));
$still = attempt('a@example.com', 'Abcd123!', $ip, $base + 7);
check('5 correct password while blocked stays blocked', $still['status'] === 429 && err($still) === 'too_many_login_attempts');

$ip2 = '10.2.0.8';
$base2 = $t + 500;
attempt('a@example.com', 'wrong-pass-1!', $ip2, $base2);
attempt('a@example.com', 'wrong-pass-1!', $ip2, $base2 + 1);
$cleared = attempt('a@example.com', 'Abcd123!', $ip2, $base2 + 2);
$after = [];
for ($i = 0; $i < 4; $i++) {
    $after[] = attempt('a@example.com', 'wrong-pass-1!', $ip2, $base2 + 10 + $i);
}
$afterOk = true;
foreach ($after as $row) {
    if ($row['status'] !== 401 || err($row) !== 'invalid_credentials') {
        $afterOk = false;
    }
}
check('6 success before threshold clears failures', $cleared['status'] === 200 && $afterOk);

$ip3 = '10.3.0.8';
$base3 = $t + 800;
for ($i = 0; $i < 5; $i++) {
    attempt('a@example.com', 'wrong-pass-1!', $ip3, $base3 + $i);
}
$other = attempt('b@example.com', 'Abcd123!', $ip3, $base3 + 6);
check('7 another user on the same IP is not blocked', $other['status'] === 200 && $other['body']['userId'] === 'u_login_b');

$ip4 = '10.4.0.8';
$ip5 = '10.4.0.9';
$base4 = $t + 1200;
for ($i = 0; $i < 5; $i++) {
    attempt('a@example.com', 'wrong-pass-1!', $ip4, $base4 + $i);
}
$otherIp = attempt('a@example.com', 'Abcd123!', $ip5, $base4 + 6);
$sameIp = attempt('a@example.com', 'Abcd123!', $ip4, $base4 + 6);
check('8 another IP is not blocked and the failing IP still is', $otherIp['status'] === 200 && $sameIp['status'] === 429);

$ip6 = '10.6.0.8';
$start = $t + 2000;
for ($i = 0; $i < 5; $i++) {
    attempt('a@example.com', 'wrong-pass-1!', $ip6, $start);
}
$during = attempt('a@example.com', 'Abcd123!', $ip6, $start + 1);
$afterExpire = attempt('a@example.com', 'Abcd123!', $ip6, $start + 900);
check('9 block expires after 15 minutes', $during['status'] === 429 && $afterExpire['status'] === 200, (string) $during['status'] . '/' . $afterExpire['status']);

$ip7 = '10.7.0.8';
$base7 = $t + 4000;
$unknown = attempt('nobody@example.com', 'wrong-pass-1!', $ip7, $base7);
$known = attempt('a@example.com', 'wrong-pass-1!', '10.7.0.9', $base7);
for ($i = 0; $i < 4; $i++) {
    attempt('nobody@example.com', 'wrong-pass-1!', $ip7, $base7 + 1 + $i);
}
$unknownBlocked = attempt('nobody@example.com', 'Abcd123!', $ip7, $base7 + 10);
$knownStill = attempt('a@example.com', 'Abcd123!', $ip7, $base7 + 10);
$body = json_encode($unknownBlocked['body']);
check(
    '10 unknown email matches the generic failure and does not reveal existence',
    $unknown['status'] === 401
        && err($unknown) === 'invalid_credentials'
        && err($unknown) === err($known)
        && $unknownBlocked['status'] === 429
        && err($unknownBlocked) === 'too_many_login_attempts'
        && $knownStill['status'] === 200
        && strpos((string) $body, 'exist') === false
        && strpos((string) $body, 'nobody@example.com') === false
);

$reg = kpi_v1_registration_rate_allow($cfg, 'global_attempt', 'login-throttle-regression-' . bin2hex(random_bytes(4)), $t);
$reset1 = kpi_v1_password_reset_throttle_allow($cfg, 'reset-' . bin2hex(random_bytes(4)) . '@example.com');
$resetEmail = 'reset-second-' . bin2hex(random_bytes(4)) . '@example.com';
$resetFirst = kpi_v1_password_reset_throttle_allow($cfg, $resetEmail);
$resetSecond = kpi_v1_password_reset_throttle_allow($cfg, $resetEmail);
check('12 registration and password-reset throttles still behave', $reg === true && $reset1 === true && $resetFirst === true && $resetSecond === false);

$policy = kpi_v1_login_throttle_policy();
check('policy is 5 failures / 15 minutes / 15 minute block', $policy['threshold'] === 5 && $policy['windowSeconds'] === 900 && $policy['blockSeconds'] === 900);

if ($failed > 0) {
    echo "FAILED $failed\n";
    exit(1);
}
echo "OK\n";
exit(0);

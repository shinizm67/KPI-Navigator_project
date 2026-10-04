<?php
/**
 * BR-LOCAL-VERIFY-01 Phase 2.
 * Seed the canonical fixture manifest into a localTestMode file root.
 *
 * Destructive reset runs only when localTestMode is on, the root is not
 * api/v1/data, and the root already carries .kpn-local-fixture-root whose
 * recorded path matches this directory. An empty dedicated root may receive
 * that sentinel. A foreign directory is refused and nothing is deleted.
 */
if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "local_test_refused:cli\n");
    exit(1);
}

require_once __DIR__ . '/../api/v1/_auth.php';
require_once __DIR__ . '/../api/v1/_admin_store.php';

const KPN_FIXTURE_SENTINEL_NAME = '.kpn-local-fixture-root';
const KPN_FIXTURE_SENTINEL_MARK = 'kpn-local-fixture-root-v1';

function kpn_fixture_fail($reason)
{
    $reason = preg_replace('/[^a-z0-9_]/', '', (string) $reason);
    if ($reason === '') {
        $reason = 'refused';
    }
    fwrite(STDERR, 'local_test_refused:' . $reason . "\n");
    exit(1);
}

function kpn_fixture_norm($path)
{
    $path = str_replace('\\', '/', (string) $path);
    $path = rtrim($path, '/');
    if (PHP_OS_FAMILY === 'Windows') {
        $path = strtolower($path);
    }
    return $path;
}

function kpn_fixture_is_fs_root($rootNorm)
{
    if ($rootNorm === '' || $rootNorm === '/' || $rootNorm === '.') {
        return true;
    }
    return (bool) preg_match('#^[A-Za-z]:$#', $rootNorm);
}

function kpn_fixture_production_norms()
{
    $live = dirname(__DIR__) . '/api/v1/data';
    $norms = [kpn_fixture_norm($live)];
    $real = realpath($live);
    if ($real !== false) {
        $norms[] = kpn_fixture_norm($real);
    }
    return array_values(array_unique($norms));
}

function kpn_fixture_is_production_data($rootNorm)
{
    foreach (kpn_fixture_production_norms() as $liveNorm) {
        if ($liveNorm === '') {
            continue;
        }
        if ($rootNorm === $liveNorm || strpos($rootNorm, $liveNorm . '/') === 0) {
            return true;
        }
        if (strpos($liveNorm, $rootNorm . '/') === 0) {
            return true;
        }
    }
    return false;
}

function kpn_fixture_assert_root_identity($rootNorm)
{
    if (kpn_fixture_is_fs_root($rootNorm) || kpn_fixture_is_production_data($rootNorm)) {
        kpn_fixture_fail('production_data');
    }
    $repo = realpath(dirname(__DIR__));
    if ($repo !== false && $rootNorm === kpn_fixture_norm($repo)) {
        kpn_fixture_fail('root');
    }
    if (strpos($rootNorm, 'forge-laboratory') !== false || strpos(strtolower($rootNorm), 'lolipop') !== false) {
        kpn_fixture_fail('production_data');
    }
}

function kpn_fixture_sentinel_path($root)
{
    return rtrim(str_replace('\\', '/', $root), '/') . '/' . KPN_FIXTURE_SENTINEL_NAME;
}

function kpn_fixture_read_sentinel($path)
{
    if (!is_file($path)) {
        return null;
    }
    $raw = (string) file_get_contents($path);
    return preg_split("/\r\n|\n|\r/", $raw);
}

function kpn_fixture_write_sentinel($path, $rootNorm, $userIds)
{
    $lines = [KPN_FIXTURE_SENTINEL_MARK, $rootNorm];
    foreach ($userIds as $userId) {
        $lines[] = $userId;
    }
    $tmp = $path . '.tmp';
    $body = implode("\n", $lines) . "\n";
    if (file_put_contents($tmp, $body, LOCK_EX) === false) {
        kpn_fixture_fail('sentinel');
    }
    if (is_file($path)) {
        @unlink($path);
    }
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        kpn_fixture_fail('sentinel');
    }
}

function kpn_fixture_foreign_entries($root)
{
    $allowed = ['.', '..', 'mail-blocked.log'];
    $foreign = [];
    foreach (scandir($root) as $name) {
        if (in_array($name, $allowed, true)) {
            continue;
        }
        $foreign[] = $name;
    }
    return $foreign;
}

function kpn_fixture_dir_is_json_only($dir)
{
    if (!is_dir($dir)) {
        return true;
    }
    foreach (scandir($dir) as $name) {
        if ($name === '.' || $name === '..') {
            continue;
        }
        $full = $dir . DIRECTORY_SEPARATOR . $name;
        if (!is_file($full) || substr($name, -5) !== '.json') {
            return false;
        }
    }
    return true;
}

function kpn_fixture_unlink_inside($rootReal, $path)
{
    if (!is_file($path)) {
        return;
    }
    $real = realpath($path);
    if ($real === false) {
        kpn_fixture_fail('sentinel');
    }
    $rootNorm = kpn_fixture_norm($rootReal);
    $fileNorm = kpn_fixture_norm($real);
    if ($fileNorm !== $rootNorm && strpos($fileNorm, $rootNorm . '/') !== 0) {
        kpn_fixture_fail('sentinel');
    }
    if (!unlink($real)) {
        kpn_fixture_fail('sentinel');
    }
}

function kpn_fixture_unlink_json_dir($rootReal, $dir)
{
    if (!is_dir($dir)) {
        return;
    }
    if (!kpn_fixture_dir_is_json_only($dir)) {
        kpn_fixture_fail('sentinel');
    }
    foreach (scandir($dir) as $name) {
        if ($name === '.' || $name === '..') {
            continue;
        }
        kpn_fixture_unlink_inside($rootReal, $dir . DIRECTORY_SEPARATOR . $name);
    }
}

function kpn_fixture_prepare_root($root, $userIds)
{
    $real = realpath($root);
    if ($real === false || !is_dir($real)) {
        kpn_fixture_fail('root');
    }
    $rootNorm = kpn_fixture_norm($real);
    kpn_fixture_assert_root_identity($rootNorm);
    $sentinelPath = kpn_fixture_sentinel_path($real);
    $existing = kpn_fixture_read_sentinel($sentinelPath);
    if ($existing === null) {
        if (kpn_fixture_foreign_entries($real) !== []) {
            kpn_fixture_fail('sentinel');
        }
        if (!kpn_fixture_dir_is_json_only($real . DIRECTORY_SEPARATOR . 'users')
            || !kpn_fixture_dir_is_json_only($real . DIRECTORY_SEPARATOR . 'profiles')) {
            kpn_fixture_fail('sentinel');
        }
        kpn_fixture_write_sentinel($sentinelPath, $rootNorm, $userIds);
        return $real;
    }
    if (!isset($existing[0], $existing[1]) || $existing[0] !== KPN_FIXTURE_SENTINEL_MARK || $existing[1] !== $rootNorm) {
        kpn_fixture_fail('sentinel');
    }
    $priorIds = [];
    $count = count($existing);
    for ($i = 2; $i < $count; $i++) {
        $id = trim((string) $existing[$i]);
        if ($id !== '') {
            $priorIds[] = $id;
        }
    }
    foreach (array_unique(array_merge($priorIds, $userIds)) as $userId) {
        $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
        if ($safe === '' || isset($safe[0]) && $safe[0] === '_') {
            kpn_fixture_fail('fixture');
        }
        kpn_fixture_unlink_inside($real, $real . DIRECTORY_SEPARATOR . $safe . '.json');
    }
    kpn_fixture_unlink_json_dir($real, $real . DIRECTORY_SEPARATOR . 'users');
    kpn_fixture_unlink_json_dir($real, $real . DIRECTORY_SEPARATOR . 'profiles');
    kpn_fixture_write_sentinel($sentinelPath, $rootNorm, $userIds);
    return $real;
}

function kpn_fixture_pin_profile_updated_at($userId, $updatedAt)
{
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
    $path = kpi_v1_admin_profiles_dir() . '/' . $safe . '.json';
    $data = json_decode((string) file_get_contents($path), true);
    if (!is_array($data)) {
        kpn_fixture_fail('store');
    }
    $data['updatedAt'] = (string) $updatedAt;
    $json = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false || file_put_contents($path, $json, LOCK_EX) === false) {
        kpn_fixture_fail('store');
    }
}

function kpn_fixture_profile_array($profile)
{
    $out = [];
    foreach (['businessName', 'companyName', 'businessType', 'genre', 'locale', 'country', 'stateRegion', 'city', 'currency'] as $key) {
        if (is_object($profile) && property_exists($profile, $key) && $profile->{$key} !== null && $profile->{$key} !== '') {
            $out[$key] = $profile->{$key};
        }
    }
    return $out;
}

$cfg = kpi_v1_load_config();
if (empty($cfg['localTestMode'])) {
    kpn_fixture_fail('mode');
}

$manifestPath = dirname(__DIR__) . '/fixtures/local/canonical/manifest.json';
$fixture = json_decode((string) file_get_contents($manifestPath));
if (!is_object($fixture) || !isset($fixture->accounts) || !is_array($fixture->accounts)) {
    kpn_fixture_fail('fixture');
}
if (!isset($fixture->clock->fixtureClock, $fixture->clock->fixtureTimezone, $fixture->clock->canonicalDate)) {
    kpn_fixture_fail('fixture');
}
if ($fixture->clock->fixtureClock !== '2026-10-03T12:00:00+09:00'
    || $fixture->clock->fixtureTimezone !== 'Asia/Tokyo'
    || $fixture->clock->canonicalDate !== '2026-10-03') {
    kpn_fixture_fail('fixture');
}

$expectedIds = [
    'fx-basic-restaurant-ready',
    'fx-pro-restaurant-ready',
    'fx-pro-hotel-ready',
    'fx-basic-profile-required',
    'fx-basic-setup-required',
    'fx-legacy-pro',
];
$seenIds = [];
$seenUsers = [];
$seenEmails = [];
$userIds = [];
foreach ($fixture->accounts as $account) {
    if (!is_object($account) || !isset($account->id, $account->userId, $account->email, $account->planSource)) {
        kpn_fixture_fail('fixture');
    }
    $id = (string) $account->id;
    $userId = (string) $account->userId;
    $email = strtolower(trim((string) $account->email));
    if (isset($seenIds[$id]) || isset($seenUsers[$userId]) || isset($seenEmails[$email])) {
        kpn_fixture_fail('fixture');
    }
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', $userId);
    if ($safe !== $userId || $safe === '' || $safe[0] === '_') {
        kpn_fixture_fail('fixture');
    }
    if ($account->planSource === 'legacy') {
        if (property_exists($account, 'plan')) {
            kpn_fixture_fail('fixture');
        }
    } elseif ($account->planSource !== 'explicit' || !isset($account->plan) || ($account->plan !== 'basic' && $account->plan !== 'pro')) {
        kpn_fixture_fail('fixture');
    }
    $seenIds[$id] = true;
    $seenUsers[$userId] = true;
    $seenEmails[$email] = true;
    $userIds[] = $userId;
}
foreach ($expectedIds as $expectedId) {
    if (!isset($seenIds[$expectedId])) {
        kpn_fixture_fail('fixture');
    }
}
if (count($fixture->accounts) !== count($expectedIds)) {
    kpn_fixture_fail('fixture');
}

$root = kpi_v1_file_data_root();
kpn_fixture_prepare_root($root, $userIds);

$index = [];
foreach ($fixture->accounts as $account) {
    $email = strtolower(trim((string) $account->email));
    $userId = (string) $account->userId;
    $user = [
        'userId' => $userId,
        'email' => $email,
        'passwordHash' => password_hash((string) $account->password, PASSWORD_DEFAULT),
        'role' => 'user',
        'disabled' => false,
        'createdAt' => isset($account->createdAt) ? (string) $account->createdAt : '2026-10-03T03:00:00Z',
    ];
    if ($account->planSource !== 'legacy') {
        $user['plan'] = (string) $account->plan;
    }
    kpi_v1_auth_write_user($user);
    $index[$email] = $userId;
    $path = kpi_v1_data_path($userId);
    $json = json_encode($account->blob, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false || file_put_contents($path, $json, LOCK_EX) === false) {
        kpn_fixture_fail('store');
    }
    kpi_v1_profile_write($cfg, $userId, kpn_fixture_profile_array(isset($account->profile) ? $account->profile : null));
    kpn_fixture_pin_profile_updated_at($userId, (string) $fixture->clock->fixtureClock);
}
kpi_v1_auth_write_email_index($index);

echo 'seeded ' . kpi_v1_file_data_root() . "\n";

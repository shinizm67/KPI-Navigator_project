<?php
/**
 * BR-LOCAL-VERIFY-01 Phase 3B.
 * Seed five canonical accounts into kpn_local_test from the file manifest.
 * fx-legacy-pro is never written. Reseed deletes only those five user ids.
 *
 *   php scripts/kpn_local_mysql_seed.php
 *   php scripts/kpn_local_mysql_seed.php seed fx-basic-restaurant-ready
 *   php scripts/kpn_local_mysql_seed.php dump
 *
 * A fixture id reseeds only that canonical account. The default reseeds all five.
 */

if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "local_test_refused:cli\n");
    exit(1);
}

require_once __DIR__ . '/../api/v1/_db.php';

$cmd = isset($argv[1]) ? (string) $argv[1] : 'seed';
if ($cmd !== 'seed' && $cmd !== 'dump') {
    fwrite(STDERR, "usage: php scripts/kpn_local_mysql_seed.php [seed|dump]\n");
    exit(1);
}

$cfg = kpi_v1_load_config();
if (empty($cfg['localTestMode']) || !kpi_v1_storage_is_mysql($cfg)) {
    fwrite(STDERR, "local_test_refused:fixture\n");
    exit(1);
}
if (strtolower((string) $cfg['dbUser']) !== 'kpn_local_runtime') {
    fwrite(STDERR, "local_test_refused:runtime_user\n");
    exit(1);
}

$manifestPath = dirname(__DIR__) . '/fixtures/local/canonical/manifest.json';
$fixture = json_decode((string) file_get_contents($manifestPath));
if (!is_object($fixture) || !isset($fixture->accounts) || !is_array($fixture->accounts)) {
    fwrite(STDERR, "local_test_refused:fixture\n");
    exit(1);
}
if (!isset($fixture->clock->fixtureClock) || $fixture->clock->fixtureClock !== '2026-10-03T12:00:00+09:00') {
    fwrite(STDERR, "local_test_refused:fixture\n");
    exit(1);
}

$mysqlIds = array(
    'fx-basic-restaurant-ready',
    'fx-pro-restaurant-ready',
    'fx-pro-hotel-ready',
    'fx-basic-profile-required',
    'fx-basic-setup-required',
);
$byId = array();
foreach ($fixture->accounts as $account) {
    if (is_object($account) && isset($account->id)) {
        $byId[(string) $account->id] = $account;
    }
}
foreach ($mysqlIds as $id) {
    if (!isset($byId[$id]) || (isset($byId[$id]->planSource) && $byId[$id]->planSource === 'legacy')) {
        fwrite(STDERR, "local_test_refused:fixture\n");
        exit(1);
    }
}
if (isset($byId['fx-legacy-pro']) && property_exists($byId['fx-legacy-pro'], 'plan')) {
    fwrite(STDERR, "local_test_refused:fixture\n");
    exit(1);
}

$seedIds = $mysqlIds;
if ($cmd === 'seed' && isset($argv[2]) && (string) $argv[2] !== '') {
    $onlyId = (string) $argv[2];
    if (!in_array($onlyId, $mysqlIds, true)) {
        fwrite(STDERR, "local_test_refused:fixture\n");
        exit(1);
    }
    $seedIds = array($onlyId);
}

$userIds = array();
foreach ($mysqlIds as $id) {
    $userIds[] = (string) $byId[$id]->userId;
}
$seedUserIds = array();
foreach ($seedIds as $id) {
    $seedUserIds[] = (string) $byId[$id]->userId;
}

$stamp = gmdate('Y-m-d H:i:s', strtotime((string) $fixture->clock->fixtureClock));
$pdo = kpi_v1_db_open($cfg, true);

if ($cmd === 'dump') {
    kpn_mysql_seed_dump($pdo, $userIds);
    exit(0);
}

try {
    $pdo->beginTransaction();
    $marks = implode(',', array_fill(0, count($seedUserIds), '?'));
    $del = $pdo->prepare('DELETE FROM kpi_users WHERE user_id IN (' . $marks . ')');
    $del->execute($seedUserIds);
    foreach ($seedIds as $id) {
        kpn_mysql_seed_account($pdo, $byId[$id], $stamp);
    }
    $pdo->commit();
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    fwrite(STDERR, "local_mysql_seed_failed\n");
    exit(1);
}

echo 'seeded kpn_local_test ' . count($seedIds);
if (count($seedIds) === 1) {
    echo ' ' . $seedIds[0];
}
echo "\n";
exit(0);

function kpn_mysql_seed_account(PDO $pdo, $account, $stamp)
{
    $userId = (string) $account->userId;
    $email = strtolower(trim((string) $account->email));
    $created = gmdate('Y-m-d H:i:s', strtotime((string) $account->createdAt));
    $hash = password_hash((string) $account->password, PASSWORD_DEFAULT);
    $plan = (string) $account->plan;
    $pdo->prepare(
        'INSERT INTO kpi_users (user_id, email, password_hash, plan, disabled, role, created_at, updated_at)
         VALUES (?, ?, ?, ?, 0, ?, ?, ?)'
    )->execute(array($userId, $email, $hash, $plan, 'user', $created, $created));

    $blob = $account->blob;
    $pdo->prepare(
        'INSERT INTO kpi_store (user_id, store_json, annual_nav_json, pl_json, updated_at, revision)
         VALUES (?, ?, ?, ?, ?, ?)'
    )->execute(array(
        $userId,
        kpn_mysql_seed_json(isset($blob->store) ? $blob->store : null),
        kpn_mysql_seed_json(isset($blob->annualNav) ? $blob->annualNav : null),
        kpn_mysql_seed_json(isset($blob->pl) ? $blob->pl : null),
        $created,
        isset($blob->revision) ? (int) $blob->revision : 1,
    ));

    $profile = isset($account->profile) ? $account->profile : null;
    if (kpn_mysql_seed_profile_present($profile)) {
        $value = function ($key) use ($profile) {
            if (!is_object($profile) || !property_exists($profile, $key) || $profile->{$key} === null || $profile->{$key} === '') {
                return null;
            }
            return (string) $profile->{$key};
        };
        $pdo->prepare(
            'INSERT INTO kpi_user_profiles
              (user_id, business_name, company_name, business_type, genre, locale, country, state_region, city, currency, updated_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        )->execute(array(
            $userId,
            $value('businessName'),
            $value('companyName'),
            $value('businessType'),
            $value('genre'),
            $value('locale'),
            $value('country'),
            $value('stateRegion'),
            $value('city'),
            $value('currency'),
            $stamp,
        ));
    }

    $ins = $pdo->prepare(
        'INSERT INTO kpi_daily_inputs (user_id, iso, sales, business_day, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?)'
    );
    foreach (kpn_mysql_seed_input_rows(isset($blob->store) ? $blob->store : null) as $row) {
        $ins->execute(array($userId, $row[0], $row[1], $row[2], $stamp, $stamp));
    }
}

function kpn_mysql_seed_profile_present($profile)
{
    if (!is_object($profile)) {
        return false;
    }
    foreach (array('businessName', 'companyName', 'businessType', 'genre', 'locale', 'country', 'stateRegion', 'city', 'currency') as $key) {
        if (property_exists($profile, $key) && $profile->{$key} !== null && $profile->{$key} !== '') {
            return true;
        }
    }
    return false;
}

function kpn_mysql_seed_input_rows($store)
{
    if (!is_object($store) || !isset($store->timeline) || !is_object($store->timeline)) {
        return array();
    }
    $sales = isset($store->timeline->dailySales) ? get_object_vars($store->timeline->dailySales) : array();
    $days = isset($store->timeline->businessDays) ? get_object_vars($store->timeline->businessDays) : array();
    $isos = array_values(array_unique(array_merge(array_keys($sales), array_keys($days))));
    sort($isos);
    $rows = array();
    foreach ($isos as $iso) {
        $bd = array_key_exists($iso, $days) ? ($days[$iso] ? 1 : 0) : null;
        $amount = array_key_exists($iso, $sales) ? $sales[$iso] : 0;
        $rows[] = array($iso, $amount, $bd);
    }
    return $rows;
}

function kpn_mysql_seed_json($value)
{
    if ($value === null) {
        return null;
    }
    $json = json_encode($value, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        fwrite(STDERR, "local_mysql_seed_failed\n");
        exit(1);
    }
    return $json;
}

function kpn_mysql_seed_dump(PDO $pdo, array $userIds)
{
    $session = $pdo->query('SELECT CURRENT_USER() AS u, @@session.time_zone AS tz, @@character_set_connection AS cs, DATABASE() AS db')->fetch();
    $marks = implode(',', array_fill(0, count($userIds), '?'));
    $users = $pdo->prepare(
        'SELECT user_id, email, plan, disabled, role, created_at, updated_at FROM kpi_users WHERE user_id IN (' . $marks . ') ORDER BY user_id'
    );
    $users->execute($userIds);
    $profiles = $pdo->prepare('SELECT * FROM kpi_user_profiles WHERE user_id IN (' . $marks . ')');
    $profiles->execute($userIds);
    $stores = $pdo->prepare('SELECT user_id, store_json, annual_nav_json, pl_json, revision, updated_at FROM kpi_store WHERE user_id IN (' . $marks . ')');
    $stores->execute($userIds);
    $inputs = $pdo->prepare('SELECT user_id, iso, sales, business_day FROM kpi_daily_inputs WHERE user_id IN (' . $marks . ') ORDER BY user_id, iso');
    $inputs->execute($userIds);
    $legacy = $pdo->prepare('SELECT user_id FROM kpi_users WHERE user_id = ? OR email = ?');
    $legacy->execute(array('locallegacy01', 'local-legacy-pro@localhost.test'));
    $facts = $pdo->prepare('SELECT COUNT(*) AS n FROM kpi_daily_facts WHERE user_id IN (' . $marks . ')');
    $facts->execute($userIds);
    $out = array(
        'runtimeUser' => (string) $session['u'],
        'timeZone' => (string) $session['tz'],
        'charset' => (string) $session['cs'],
        'database' => (string) $session['db'],
        'users' => $users->fetchAll(),
        'profiles' => $profiles->fetchAll(),
        'stores' => $stores->fetchAll(),
        'inputs' => $inputs->fetchAll(),
        'legacyRows' => $legacy->fetchAll(),
        'factRows' => (int) $facts->fetch()['n'],
    );
    echo json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}

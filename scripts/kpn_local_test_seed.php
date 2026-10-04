<?php
/**
 * Seed LOCAL_BASIC / LOCAL_PRO into the localTestMode file root.
 * Refuses to run unless KPI_V1_CONFIG points at a localTestMode config.
 */
if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "local_test_refused:cli\n");
    exit(1);
}

require_once __DIR__ . '/../api/v1/_auth.php';
require_once __DIR__ . '/../api/v1/_admin_store.php';

$cfg = kpi_v1_load_config();
if (empty($cfg['localTestMode'])) {
    fwrite(STDERR, "local_test_refused:mode\n");
    exit(1);
}

$fixturePath = dirname(__DIR__) . '/fixtures/local/phase1-baseline.json';
$fixture = json_decode((string) file_get_contents($fixturePath), true);
if (!is_array($fixture) || empty($fixture['accounts'])) {
    fwrite(STDERR, "local_test_refused:fixture\n");
    exit(1);
}

$index = [];
foreach ($fixture['accounts'] as $account) {
    $email = strtolower(trim((string) $account['email']));
    $userId = (string) $account['userId'];
    kpi_v1_auth_write_user([
        'userId' => $userId,
        'email' => $email,
        'passwordHash' => password_hash((string) $account['password'], PASSWORD_DEFAULT),
        'plan' => (string) $account['plan'],
        'role' => 'user',
        'disabled' => false,
        'createdAt' => gmdate('c'),
    ]);
    $index[$email] = $userId;
    $blob = $account['blob'];
    $path = kpi_v1_data_path($userId);
    $json = json_encode($blob, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false || file_put_contents($path, $json, LOCK_EX) === false) {
        fwrite(STDERR, "local_test_refused:store\n");
        exit(1);
    }
    kpi_v1_profile_write($cfg, $userId, $account['profile']);
}
kpi_v1_auth_write_email_index($index);

echo 'seeded ' . kpi_v1_file_data_root() . "\n";

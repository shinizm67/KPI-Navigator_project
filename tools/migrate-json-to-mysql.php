#!/usr/bin/env php
<?php
/**
 * Migrate api/v1/data JSON users + store blobs into MySQL (B4-T2).
 *
 * Usage (repo root):
 *   php tools/migrate-json-to-mysql.php
 *
 * Requires config.local.php with storageDriver=mysql and db* credentials.
 * Creates tables from api/v1/schema.sql if missing, then imports:
 *   - data/users/*.json  → kpi_users
 *   - data/{userId}.json → kpi_store
 */

$root = dirname(__DIR__);
require $root . '/api/v1/_db.php';

$cfg = kpi_v1_load_config();
if (!kpi_v1_storage_is_mysql($cfg)) {
    fwrite(STDERR, "Set storageDriver => 'mysql' in api/v1/config.local.php first.\n");
    exit(1);
}

$pdo = kpi_v1_db($cfg);
$schema = file_get_contents($root . '/api/v1/schema.sql');
if ($schema === false) {
    fwrite(STDERR, "Cannot read api/v1/schema.sql\n");
    exit(1);
}
foreach (array_filter(array_map('trim', explode(';', $schema))) as $stmtSql) {
    if ($stmtSql === '' || strpos($stmtSql, '--') === 0) {
        continue;
    }
    // Skip pure comment blocks
    $lines = array_filter(array_map('trim', explode("\n", $stmtSql)), function ($l) {
        return $l !== '' && strpos($l, '--') !== 0;
    });
    if (!$lines) {
        continue;
    }
    $pdo->exec(implode("\n", $lines));
}

$usersDir = $root . '/api/v1/data/users';
$userFiles = glob($usersDir . '/*.json') ?: [];
$importedUsers = 0;
foreach ($userFiles as $file) {
    $base = basename($file);
    if ($base[0] === '_') {
        continue;
    }
    $data = json_decode((string) file_get_contents($file), true);
    if (!is_array($data) || empty($data['userId']) || empty($data['email']) || empty($data['passwordHash'])) {
        fwrite(STDERR, "skip user file: $base\n");
        continue;
    }
    kpi_v1_db_write_user($cfg, $data);
    $importedUsers++;
    echo "user {$data['userId']} ({$data['email']})\n";
}

$dataDir = $root . '/api/v1/data';
$storeFiles = glob($dataDir . '/*.json') ?: [];
$importedStores = 0;
foreach ($storeFiles as $file) {
    $base = basename($file, '.json');
    if ($base === '' || strpos($base, '_') === 0) {
        continue;
    }
    // Skip if this looks like a non-user file
    $raw = json_decode((string) file_get_contents($file), false);
    if (!is_object($raw)) {
        continue;
    }
    $userId = isset($raw->userId) && $raw->userId ? (string) $raw->userId : $base;
    // Ensure user row exists (orphan store → skip with note)
    $u = kpi_v1_db_read_user($cfg, $userId);
    if ($u === null) {
        fwrite(STDERR, "skip store (no user): $base\n");
        continue;
    }
    $blob = (object) [
        'userId' => $userId,
        'updatedAt' => isset($raw->updatedAt) ? $raw->updatedAt : gmdate('c'),
        'store' => property_exists($raw, 'store') ? $raw->store : null,
        'annualNav' => property_exists($raw, 'annualNav') ? $raw->annualNav : null,
        'pl' => property_exists($raw, 'pl') ? $raw->pl : null,
    ];
    kpi_v1_db_write_blob($cfg, $userId, $blob);
    $importedStores++;
    echo "store $userId\n";
}

echo "Done. users=$importedUsers stores=$importedStores\n";
echo "Keep storageDriver=mysql in config.local.php to serve from DB.\n";

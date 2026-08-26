#!/usr/bin/env php
<?php
/**
 * Step AP — migrate timeline.dailySales / businessDays from kpi_store blob
 * into kpi_daily_inputs (year chunks). Idempotent UPSERT.
 *
 * Usage (repo root):
 *   php tools/migrate-timeline-to-daily-inputs.php
 *   php tools/migrate-timeline-to-daily-inputs.php --user=USER_ID
 *
 * Requires storageDriver=mysql and kpi_daily_inputs table (Step AL).
 */

$root = dirname(__DIR__);
require $root . '/api/v1/_db.php';

$cfg = kpi_v1_load_config();
if (!kpi_v1_storage_is_mysql($cfg)) {
    fwrite(STDERR, "Set storageDriver => 'mysql' in api/v1/config.local.php first.\n");
    exit(1);
}

$onlyUser = null;
foreach (array_slice($argv, 1) as $arg) {
    if (strpos($arg, '--user=') === 0) {
        $onlyUser = substr($arg, 7);
    }
}

@set_time_limit(0);

$pdo = kpi_v1_db($cfg);
try {
    $pdo->query('SELECT 1 FROM kpi_daily_inputs LIMIT 1');
} catch (PDOException $e) {
    fwrite(STDERR, "kpi_daily_inputs missing. Run schema_kpi_daily_inputs.add.sql first (Step AL).\n");
    exit(1);
}

if ($onlyUser) {
    $userIds = [$onlyUser];
} else {
    $stmt = $pdo->query('SELECT user_id FROM kpi_store ORDER BY user_id');
    $userIds = [];
    while ($row = $stmt->fetch()) {
        if (!empty($row['user_id'])) {
            $userIds[] = (string) $row['user_id'];
        }
    }
}

$totalWritten = 0;
foreach ($userIds as $userId) {
    $blob = kpi_v1_db_read_blob($cfg, $userId);
    $store = isset($blob->store) ? $blob->store : null;
    if ($store === null) {
        echo "skip $userId (no store)\n";
        continue;
    }
    $timeline = null;
    if (is_object($store) && isset($store->timeline)) {
        $timeline = $store->timeline;
    } elseif (is_array($store) && isset($store['timeline'])) {
        $timeline = $store['timeline'];
    }
    if ($timeline === null) {
        echo "skip $userId (no timeline)\n";
        continue;
    }
    $salesMap = is_object($timeline)
        ? (isset($timeline->dailySales) ? $timeline->dailySales : null)
        : (isset($timeline['dailySales']) ? $timeline['dailySales'] : null);
    $bizMap = is_object($timeline)
        ? (isset($timeline->businessDays) ? $timeline->businessDays : null)
        : (isset($timeline['businessDays']) ? $timeline['businessDays'] : null);

    $byYear = [];
    $salesKeys = [];
    if (is_object($salesMap)) {
        $salesKeys = array_keys(get_object_vars($salesMap));
    } elseif (is_array($salesMap)) {
        $salesKeys = array_keys($salesMap);
    }
    foreach ($salesKeys as $iso) {
        if (!is_string($iso) || !preg_match('/^(\d{4})-\d{2}-\d{2}$/', $iso, $m)) {
            continue;
        }
        $y = (int) $m[1];
        $n = is_object($salesMap) ? $salesMap->{$iso} : $salesMap[$iso];
        if (!is_numeric($n)) {
            $n = 0;
        }
        $byYear[$y][$iso]['sales'] = round((float) $n, 2);
    }
    $bizKeys = [];
    if (is_object($bizMap)) {
        $bizKeys = array_keys(get_object_vars($bizMap));
    } elseif (is_array($bizMap)) {
        $bizKeys = array_keys($bizMap);
    }
    foreach ($bizKeys as $iso) {
        if (!is_string($iso) || !preg_match('/^(\d{4})-\d{2}-\d{2}$/', $iso, $m)) {
            continue;
        }
        $y = (int) $m[1];
        $b = is_object($bizMap) ? $bizMap->{$iso} : $bizMap[$iso];
        $byYear[$y][$iso]['business_day'] = $b ? 1 : 0;
        if (!isset($byYear[$y][$iso]['sales'])) {
            $byYear[$y][$iso]['sales'] = 0.0;
        }
    }

    ksort($byYear);
    $userWritten = 0;
    foreach ($byYear as $year => $days) {
        $rows = [];
        ksort($days);
        foreach ($days as $iso => $cell) {
            $sales = isset($cell['sales']) ? (float) $cell['sales'] : 0.0;
            /* Three-value: explicit timeline businessDays only — never infer from sales/weekday */
            if (array_key_exists('business_day', $cell)) {
                $rows[] = [
                    'iso' => $iso,
                    'sales' => $sales,
                    'touch_business_day' => true,
                    'business_day' => ((int) $cell['business_day']) ? 1 : 0,
                ];
            } else {
                $rows[] = [
                    'iso' => $iso,
                    'sales' => $sales,
                    'touch_business_day' => false,
                ];
            }
        }
        if (!$rows) {
            continue;
        }
        $n = kpi_v1_db_upsert_daily_inputs($cfg, $userId, $rows);
        $userWritten += $n;
        echo "user $userId year $year written $n\n";
    }
    $totalWritten += $userWritten;
    echo "user $userId total $userWritten\n";
}

echo "done total_written=$totalWritten users=" . count($userIds) . "\n";

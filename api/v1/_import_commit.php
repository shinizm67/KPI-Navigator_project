<?php
declare(strict_types=1);

/**
 * Mold import patch commit.
 * One transaction: lock kpi_store, revision CAS, merge only patch keys, then
 * the touched kpi_daily_inputs rows and the touched kpi_daily_facts rows.
 * A failure rolls all three back. Facts are not rebuilt after commit.
 * Normal store.php PUT is not used. kpi_daily_inputs has no sales_entered.
 */

function kpi_v1_import_allowed_maps()
{
    return [
        'salesByDate',
        'salesEnteredByDate',
        'businessDayByDate',
        'foodByDate',
        'drinkByDate',
        'dinnerSalesByDate',
        'lunchSalesByDate',
        'totalCustomersByDate',
        'lunchCustomersByDate',
        'dinnerCustomersByDate',
        'totalGroupsByDate',
        'lunchGroupsByDate',
        'dinnerGroupsByDate',
    ];
}

function kpi_v1_import_meal_fields()
{
    return [
        'dinnerSalesByDate' => 'dinner_sales',
        'lunchSalesByDate' => 'lunch_sales',
        'totalCustomersByDate' => 'total_customers',
        'lunchCustomersByDate' => 'lunch_customers',
        'dinnerCustomersByDate' => 'dinner_customers',
        'totalGroupsByDate' => 'total_groups',
        'lunchGroupsByDate' => 'lunch_groups',
        'dinnerGroupsByDate' => 'dinner_groups',
    ];
}

function kpi_v1_import_count_maps()
{
    return [
        'totalCustomersByDate',
        'lunchCustomersByDate',
        'dinnerCustomersByDate',
        'totalGroupsByDate',
        'lunchGroupsByDate',
        'dinnerGroupsByDate',
    ];
}

function kpi_v1_import_restaurant_maps()
{
    return [
        'foodByDate',
        'drinkByDate',
        'dinnerSalesByDate',
        'lunchSalesByDate',
        'totalCustomersByDate',
        'lunchCustomersByDate',
        'dinnerCustomersByDate',
        'totalGroupsByDate',
        'lunchGroupsByDate',
        'dinnerGroupsByDate',
    ];
}

function kpi_v1_import_canonical_business_type($raw)
{
    $s = strtolower(trim((string) $raw));
    $map = [
        '' => 'restaurant',
        'restaurant' => 'restaurant',
        'cafe' => 'restaurant',
        'bar' => 'restaurant',
        'retail' => 'retail',
        'wear_shop' => 'retail',
        'fitness' => 'fitness',
        'personal_trainer' => 'fitness',
        'hair_salon' => 'hair_salon',
        'hotel' => 'hotel',
        'other' => 'other',
    ];
    return isset($map[$s]) ? $map[$s] : 'other';
}

function kpi_v1_import_valid_iso($iso)
{
    if (!is_string($iso) || !preg_match('/^\d{4}-\d{2}-\d{2}$/', $iso)) {
        return false;
    }
    $y = (int) substr($iso, 0, 4);
    $m = (int) substr($iso, 5, 2);
    $d = (int) substr($iso, 8, 2);
    if ($y < 1990 || $y > 2100) {
        return false;
    }
    return checkdate($m, $d, $y);
}

function kpi_v1_import_fail($error, $status = 400)
{
    return ['ok' => false, 'error' => $error, 'status' => $status];
}

/**
 * Normalize a client patch. Absent keys stay absent. Explicit 0 stays 0.
 * Blank and non-numeric sales are rejected rather than stored as 0.
 * Null is accepted only for businessDayByDate and salesEnteredByDate.
 */
function kpi_v1_import_normalize_patch($patch, $scope)
{
    if (!is_array($patch)) {
        return kpi_v1_import_fail('invalid_patch');
    }
    if (!in_array($scope, ['sales-data', 'past-sales', 'workbook'], true)) {
        return kpi_v1_import_fail('invalid_scope');
    }
    $allowed = kpi_v1_import_allowed_maps();
    $counts = array_flip(kpi_v1_import_count_maps());
    $out = [];
    $dates = [];
    foreach ($patch as $mapName => $rows) {
        if (!in_array($mapName, $allowed, true)) {
            return kpi_v1_import_fail('invalid_field');
        }
        if (!is_array($rows)) {
            return kpi_v1_import_fail('invalid_field');
        }
        $clean = [];
        foreach ($rows as $iso => $value) {
            $iso = (string) $iso;
            if (!kpi_v1_import_valid_iso($iso)) {
                return kpi_v1_import_fail('invalid_date');
            }
            if ($value === '' || is_array($value)) {
                return kpi_v1_import_fail('invalid_value');
            }
            if ($mapName === 'businessDayByDate' || $mapName === 'salesEnteredByDate') {
                if ($value === null) {
                    $clean[$iso] = null;
                } elseif ($value === true || $value === 1 || $value === '1') {
                    $clean[$iso] = true;
                } elseif ($value === false || $value === 0 || $value === '0') {
                    $clean[$iso] = false;
                } else {
                    return kpi_v1_import_fail('invalid_value');
                }
            } else {
                if ($value === null) {
                    return kpi_v1_import_fail('invalid_value');
                }
                if (is_bool($value) || !is_numeric($value)) {
                    return kpi_v1_import_fail('invalid_value');
                }
                $num = (float) $value;
                if ($num < 0 || !is_finite($num)) {
                    return kpi_v1_import_fail('invalid_value');
                }
                if (isset($counts[$mapName])) {
                    if (abs($num - round($num)) > 0.000001) {
                        return kpi_v1_import_fail('invalid_value');
                    }
                    $clean[$iso] = (int) round($num);
                } else {
                    $clean[$iso] = round($num, 2);
                }
            }
            $dates[$iso] = true;
        }
        if ($clean) {
            $out[$mapName] = $clean;
        }
    }
    if (!$dates) {
        return kpi_v1_import_fail('empty_patch');
    }
    if (count($dates) > 3660) {
        return kpi_v1_import_fail('too_many_rows');
    }
    $out['_dates'] = array_keys($dates);
    return ['ok' => true, 'patch' => $out];
}

function kpi_v1_import_scope_date_ok($scope, $iso, $operatingYear)
{
    $year = (int) substr($iso, 0, 4);
    if ($scope === 'sales-data') {
        return $operatingYear !== null && $year === (int) $operatingYear;
    }
    if ($scope === 'past-sales') {
        return $operatingYear !== null && $year < (int) $operatingYear;
    }
    return true;
}

function kpi_v1_import_store_array($store)
{
    if (is_object($store)) {
        $store = json_decode(json_encode($store), true);
    }
    return is_array($store) ? $store : [];
}

function kpi_v1_import_ensure_year_map(array &$store, $year, $bucket)
{
    if (!isset($store['years']) || !is_array($store['years'])) {
        $store['years'] = [];
    }
    $key = (string) $year;
    if (!isset($store['years'][$key]) || !is_array($store['years'][$key])) {
        $store['years'][$key] = [];
    }
    if (!isset($store['years'][$key][$bucket]) || !is_array($store['years'][$key][$bucket])) {
        $store['years'][$key][$bucket] = [];
    }
    return $key;
}

function kpi_v1_import_set_stream(array &$store, $year, $bucket, $field, $iso, $value)
{
    $key = kpi_v1_import_ensure_year_map($store, $year, $bucket);
    if (!isset($store['years'][$key][$bucket][$field]) || !is_array($store['years'][$key][$bucket][$field])) {
        $store['years'][$key][$bucket][$field] = [];
    }
    $store['years'][$key][$bucket][$field][$iso] = $value;
}

/**
 * Merge only the normalized patch into the locked store document.
 * Dates and fields that are not in the patch are left as they are.
 */
function kpi_v1_import_merge_store(array $store, array $patch)
{
    if (!isset($store['timeline']) || !is_array($store['timeline'])) {
        $store['timeline'] = [];
    }
    if (!empty($patch['salesByDate'])) {
        if (!isset($store['timeline']['dailySales']) || !is_array($store['timeline']['dailySales'])) {
            $store['timeline']['dailySales'] = [];
        }
        $enteredMap = (isset($patch['salesEnteredByDate']) && is_array($patch['salesEnteredByDate']))
            ? $patch['salesEnteredByDate'] : [];
        foreach ($patch['salesByDate'] as $iso => $value) {
            $store['timeline']['dailySales'][$iso] = $value;
            if (!array_key_exists($iso, $enteredMap)) {
                if (!isset($store['timeline']['salesEntered']) || !is_array($store['timeline']['salesEntered'])) {
                    $store['timeline']['salesEntered'] = [];
                }
                $store['timeline']['salesEntered'][$iso] = true;
            }
        }
    }
    if (array_key_exists('businessDayByDate', $patch) && is_array($patch['businessDayByDate'])) {
        if (!isset($store['timeline']['businessDays']) || !is_array($store['timeline']['businessDays'])) {
            $store['timeline']['businessDays'] = [];
        }
        foreach ($patch['businessDayByDate'] as $iso => $value) {
            if ($value === null) {
                unset($store['timeline']['businessDays'][$iso]);
            } else {
                $store['timeline']['businessDays'][$iso] = $value ? true : false;
                if (isset($store['timeline']['businessDayUnresolved']) && is_array($store['timeline']['businessDayUnresolved'])) {
                    unset($store['timeline']['businessDayUnresolved'][$iso]);
                }
            }
        }
    }
    if (array_key_exists('salesEnteredByDate', $patch) && is_array($patch['salesEnteredByDate'])) {
        if (!isset($store['timeline']['salesEntered']) || !is_array($store['timeline']['salesEntered'])) {
            $store['timeline']['salesEntered'] = [];
        }
        foreach ($patch['salesEnteredByDate'] as $iso => $value) {
            $store['timeline']['salesEntered'][$iso] = $value;
        }
    }
    if (!empty($patch['foodByDate'])) {
        foreach ($patch['foodByDate'] as $iso => $value) {
            kpi_v1_import_set_stream($store, substr($iso, 0, 4), 'dailyIncome', 'food_sales', $iso, $value);
        }
    }
    if (!empty($patch['drinkByDate'])) {
        foreach ($patch['drinkByDate'] as $iso => $value) {
            kpi_v1_import_set_stream($store, substr($iso, 0, 4), 'dailyIncome', 'drink_sales', $iso, $value);
        }
    }
    foreach (kpi_v1_import_meal_fields() as $mapName => $field) {
        if (empty($patch[$mapName])) {
            continue;
        }
        foreach ($patch[$mapName] as $iso => $value) {
            kpi_v1_import_set_stream($store, substr($iso, 0, 4), 'dailyMeal', $field, $iso, $value);
        }
    }
    return $store;
}

function kpi_v1_import_flag_tinyint($value)
{
    if ($value === null) {
        return null;
    }
    return $value ? 1 : 0;
}

function kpi_v1_import_touch_rows(array $patch)
{
    $sales = isset($patch['salesByDate']) && is_array($patch['salesByDate']) ? $patch['salesByDate'] : [];
    $biz = isset($patch['businessDayByDate']) && is_array($patch['businessDayByDate']) ? $patch['businessDayByDate'] : [];
    $entered = isset($patch['salesEnteredByDate']) && is_array($patch['salesEnteredByDate']) ? $patch['salesEnteredByDate'] : [];
    $dates = [];
    foreach ([$sales, $biz, $entered] as $map) {
        foreach ($map as $iso => $_v) {
            $dates[(string) $iso] = true;
        }
    }
    $rows = [];
    foreach (array_keys($dates) as $iso) {
        $row = ['iso' => $iso];
        if (array_key_exists($iso, $sales)) {
            $row['sales'] = $sales[$iso];
        }
        if (array_key_exists($iso, $biz)) {
            $row['touchBiz'] = true;
            $row['businessDay'] = kpi_v1_import_flag_tinyint($biz[$iso]);
        }
        if (array_key_exists($iso, $entered)) {
            $row['touchEntered'] = true;
            $row['salesEntered'] = kpi_v1_import_flag_tinyint($entered[$iso]);
        } elseif (array_key_exists($iso, $sales)) {
            $row['touchEntered'] = true;
            $row['salesEntered'] = 1;
        }
        $rows[] = $row;
    }
    return $rows;
}

function kpi_v1_import_upsert_inputs(PDO $pdo, $userId, array $rows)
{
    if (!$rows) {
        return;
    }
    $now = gmdate('Y-m-d H:i:s');
    $find = $pdo->prepare('SELECT sales FROM kpi_daily_inputs WHERE user_id = ? AND iso = ?');
    $insert = $pdo->prepare(
        'INSERT INTO kpi_daily_inputs (user_id, iso, sales, business_day, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?)'
    );
    foreach ($rows as $row) {
        $hasSales = array_key_exists('sales', $row);
        $touchBiz = !empty($row['touchBiz']);
        if (!$hasSales && !$touchBiz) {
            continue;
        }
        $find->execute([(string) $userId, (string) $row['iso']]);
        $existing = $find->fetch();
        $salesText = $hasSales ? number_format((float) $row['sales'], 2, '.', '') : null;
        $biz = $touchBiz ? $row['businessDay'] : null;
        if ($existing === false) {
            if (!$hasSales) {
                continue;
            }
            $insert->execute([
                (string) $userId,
                (string) $row['iso'],
                $salesText,
                $touchBiz ? $biz : null,
                $now,
                $now,
            ]);
            continue;
        }
        $sets = ['updated_at = ?'];
        $params = [$now];
        if ($hasSales) {
            $sets[] = 'sales = ?';
            $params[] = $salesText;
        }
        if ($touchBiz) {
            $sets[] = 'business_day = ?';
            $params[] = $biz;
        }
        $params[] = (string) $userId;
        $params[] = (string) $row['iso'];
        $pdo->prepare('UPDATE kpi_daily_inputs SET ' . implode(', ', $sets) . ' WHERE user_id = ? AND iso = ?')
            ->execute($params);
    }
}

function kpi_v1_import_upsert_facts(PDO $pdo, $userId, array $rows)
{
    if (!$rows) {
        return;
    }
    $now = gmdate('Y-m-d H:i:s');
    $find = $pdo->prepare('SELECT sales FROM kpi_daily_facts WHERE user_id = ? AND iso = ?');
    $insert = $pdo->prepare(
        'INSERT INTO kpi_daily_facts (user_id, iso, sales, business_day, sales_entered, updated_at)
         VALUES (?, ?, ?, ?, ?, ?)'
    );
    foreach ($rows as $row) {
        $hasSales = array_key_exists('sales', $row);
        $touchBiz = !empty($row['touchBiz']);
        $touchEntered = !empty($row['touchEntered']);
        if (!$hasSales && !$touchBiz && !$touchEntered) {
            continue;
        }
        $salesText = $hasSales ? number_format((float) $row['sales'], 2, '.', '') : '0.00';
        $biz = $touchBiz ? $row['businessDay'] : null;
        $entered = $touchEntered ? $row['salesEntered'] : null;
        $find->execute([(string) $userId, (string) $row['iso']]);
        $existing = $find->fetch();
        if ($existing === false) {
            $insert->execute([
                (string) $userId,
                (string) $row['iso'],
                $salesText,
                $touchBiz ? $biz : null,
                $touchEntered ? $entered : null,
                $now,
            ]);
            continue;
        }
        $sets = ['updated_at = ?'];
        $params = [$now];
        if ($hasSales) {
            $sets[] = 'sales = ?';
            $params[] = $salesText;
        }
        if ($touchBiz) {
            $sets[] = 'business_day = ?';
            $params[] = $biz;
        }
        if ($touchEntered) {
            $sets[] = 'sales_entered = ?';
            $params[] = $entered;
        }
        $params[] = (string) $userId;
        $params[] = (string) $row['iso'];
        $pdo->prepare('UPDATE kpi_daily_facts SET ' . implode(', ', $sets) . ' WHERE user_id = ? AND iso = ?')
            ->execute($params);
    }
}

function kpi_v1_import_commit_mysql(PDO $pdo, $userId, $expectedRevision, $scope, $patch)
{
    $normalized = kpi_v1_import_normalize_patch($patch, $scope);
    if (empty($normalized['ok'])) {
        return $normalized;
    }
    $clean = $normalized['patch'];
    $dates = $clean['_dates'];
    unset($clean['_dates']);

    $pdo->beginTransaction();
    try {
        $lockSql = 'SELECT user_id, store_json, annual_nav_json, pl_json, updated_at, revision FROM kpi_store WHERE user_id = ?';
        if ($pdo->getAttribute(PDO::ATTR_DRIVER_NAME) === 'mysql') {
            $lockSql .= ' FOR UPDATE';
        }
        $stmt = $pdo->prepare($lockSql);
        $stmt->execute([(string) $userId]);
        $row = $stmt->fetch();
        $current = null;
        if (is_array($row)) {
            $current = (int) $row['revision'];
        }
        $expectedNull = $expectedRevision === null;
        if ($row === false) {
            if (!$expectedNull) {
                $pdo->rollBack();
                return kpi_v1_import_fail('conflict', 409);
            }
        } elseif ($expectedNull || (int) $expectedRevision !== $current) {
            $pdo->rollBack();
            return [
                'ok' => false,
                'error' => 'conflict',
                'status' => 409,
                'revision' => $current,
                'updatedAt' => gmdate('c'),
            ];
        }

        $blob = $row === false
            ? kpi_v1_empty_store_blob($userId)
            : kpi_v1_db_row_to_blob($userId, $row);
        $store = kpi_v1_import_store_array(isset($blob->store) ? $blob->store : []);
        $meta = isset($store['meta']) && is_array($store['meta']) ? $store['meta'] : [];
        $businessType = kpi_v1_import_canonical_business_type(isset($meta['businessType']) ? $meta['businessType'] : '');
        $operatingYear = isset($meta['operatingYear']) && is_numeric($meta['operatingYear'])
            ? (int) $meta['operatingYear']
            : null;
        if ($scope !== 'workbook' && $operatingYear === null) {
            $pdo->rollBack();
            return kpi_v1_import_fail('invalid_year');
        }
        if ($businessType !== 'restaurant') {
            foreach (kpi_v1_import_restaurant_maps() as $mapName) {
                if (!empty($clean[$mapName])) {
                    $pdo->rollBack();
                    return kpi_v1_import_fail('invalid_business_type');
                }
            }
        }
        foreach ($dates as $iso) {
            if (!kpi_v1_import_scope_date_ok($scope, $iso, $operatingYear)) {
                $pdo->rollBack();
                return kpi_v1_import_fail('invalid_year');
            }
        }

        $merged = kpi_v1_import_merge_store($store, $clean);
        $touchRows = kpi_v1_import_touch_rows($clean);
        $blob->store = json_decode(json_encode($merged));
        $updatedAt = gmdate('c');
        $blob->updatedAt = $updatedAt;
        $next = $row === false ? 1 : ($current + 1);
        $blob->revision = $next;
        kpi_v1_import_upsert_inputs($pdo, $userId, $touchRows);
        kpi_v1_import_upsert_facts($pdo, $userId, $touchRows);
        if ($row === false) {
            kpi_v1_db_insert_store_row($pdo, $userId, $blob);
        } else {
            $written = kpi_v1_db_update_store_row($pdo, $userId, $current, $blob);
            if ($written < 1) {
                $pdo->rollBack();
                return kpi_v1_import_fail('conflict', 409);
            }
        }
        $pdo->commit();
        return [
            'ok' => true,
            'revision' => $next,
            'updatedAt' => $updatedAt,
            'savedDates' => count($dates),
        ];
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        $fail = kpi_v1_import_fail('commit_failed', 500);
        if (getenv('KPN_IMPORT_COMMIT_DEBUG') === '1') {
            $fail['detail'] = $e->getMessage();
        }
        return $fail;
    }
}

<?php
/**
 * Phase 5 first slice — rebuild one year of kpi_daily_facts from the store blob.
 * Does not rewrite kpi_store.store_json. Does not replace store.php.
 * HTML is not wired yet (FileZilla Step AC). Screens keep the old JS path until Step AD.
 */

require __DIR__ . '/_entitlement.php';
require_once __DIR__ . '/_db.php';

$cfg = kpi_v1_load_config();
kpi_v1_store_boot($cfg);

$userId = kpi_v1_store_resolve_user_id($cfg);
$method = $_SERVER['REQUEST_METHOD'];

if (!kpi_v1_storage_is_mysql($cfg)) {
    kpi_v1_json_out(501, ['ok' => false, 'error' => 'storage_not_mysql']);
}

$KPI_REBUILD_DEFAULT_HL = [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115];
$KPI_REBUILD_PLACEHOLDER_SALES = 1234;
$KPI_REBUILD_WEEKDAY_FALLBACK = 1 / 7;

function kpi_v1_rebuild_prop($obj, $key, $default = null)
{
    if (is_object($obj) && isset($obj->{$key})) {
        return $obj->{$key};
    }
    if (is_array($obj) && array_key_exists($key, $obj)) {
        return $obj[$key];
    }
    return $default;
}

function kpi_v1_rebuild_map_has($map, $iso)
{
    if (is_object($map)) {
        return isset($map->{$iso});
    }
    if (is_array($map)) {
        return array_key_exists($iso, $map);
    }
    return false;
}

function kpi_v1_rebuild_map_get($map, $iso)
{
    if (is_object($map) && isset($map->{$iso})) {
        return $map->{$iso};
    }
    if (is_array($map) && array_key_exists($iso, $map)) {
        return $map[$iso];
    }
    return null;
}

function kpi_v1_rebuild_map_keys($map)
{
    if (is_object($map)) {
        return array_keys(get_object_vars($map));
    }
    if (is_array($map)) {
        return array_keys($map);
    }
    return [];
}

function kpi_v1_rebuild_js_truthy($value)
{
    if ($value === null || $value === false || $value === 0 || $value === 0.0 || $value === '0' || $value === '') {
        return false;
    }
    return true;
}

function kpi_v1_rebuild_pad2($n)
{
    return str_pad((string) (int) $n, 2, '0', STR_PAD_LEFT);
}

function kpi_v1_rebuild_iso($year, $m0, $day)
{
    return (int) $year . '-' . kpi_v1_rebuild_pad2($m0 + 1) . '-' . kpi_v1_rebuild_pad2($day);
}

function kpi_v1_rebuild_days_in_month($year, $m0)
{
    $dt = DateTime::createFromFormat('Y-n-j', ((int) $year) . '-' . ((int) $m0 + 1) . '-1');
    if (!$dt) {
        return 0;
    }
    return (int) $dt->format('t');
}

function kpi_v1_rebuild_dow($year, $m0, $day)
{
    $iso = kpi_v1_rebuild_iso($year, $m0, $day);
    $dt = DateTime::createFromFormat('Y-m-d', $iso);
    if (!$dt) {
        return null;
    }
    return (int) $dt->format('w');
}

function kpi_v1_rebuild_num($value)
{
    if ($value === null || $value === '' || !is_numeric($value)) {
        return null;
    }
    return (float) $value;
}

function kpi_v1_rebuild_is_finite_num($value)
{
    if (is_int($value)) {
        return true;
    }
    if (!is_float($value)) {
        return false;
    }
    return !is_nan($value) && !is_infinite($value);
}

function kpi_v1_rebuild_year_rec($store, $year)
{
    $years = kpi_v1_rebuild_prop($store, 'years');
    $rec = kpi_v1_rebuild_prop($years, (string) $year);
    if ($rec === null) {
        $rec = kpi_v1_rebuild_prop($years, (int) $year);
    }
    return $rec;
}

function kpi_v1_rebuild_is_calendar_biz($salesMap, $bizMap, $year, $m0, $day)
{
    $dow = kpi_v1_rebuild_dow($year, $m0, $day);
    if ($dow === null) {
        return false;
    }
    $iso = kpi_v1_rebuild_iso($year, $m0, $day);
    $isWk = ($dow === 0 || $dow === 6);
    if (kpi_v1_rebuild_map_has($bizMap, $iso)) {
        return kpi_v1_rebuild_js_truthy(kpi_v1_rebuild_map_get($bizMap, $iso));
    }
    if (kpi_v1_rebuild_map_has($salesMap, $iso)) {
        $n = kpi_v1_rebuild_num(kpi_v1_rebuild_map_get($salesMap, $iso));
        if ($n === null) {
            return !$isWk;
        }
        if ($n === 0.0) {
            return false;
        }
        return true;
    }
    return !$isWk;
}

function kpi_v1_rebuild_snapshot_biz($bizMap, $iso)
{
    if (!kpi_v1_facts_valid_iso($iso)) {
        return false;
    }
    if (kpi_v1_rebuild_map_has($bizMap, $iso)) {
        return kpi_v1_rebuild_js_truthy(kpi_v1_rebuild_map_get($bizMap, $iso));
    }
    $dt = DateTime::createFromFormat('Y-m-d', $iso);
    if (!$dt) {
        return false;
    }
    $dow = (int) $dt->format('w');
    return $dow !== 0 && $dow !== 6;
}

function kpi_v1_rebuild_snapshot_sales($salesMap, $iso, $placeholder)
{
    if (!kpi_v1_rebuild_map_has($salesMap, $iso)) {
        return 0.0;
    }
    $n = kpi_v1_rebuild_num(kpi_v1_rebuild_map_get($salesMap, $iso));
    if ($n === null || $n === (float) $placeholder) {
        return 0.0;
    }
    return $n;
}

function kpi_v1_rebuild_year_has_sales($salesMap, $year)
{
    $prefix = (string) ((int) $year) . '-';
    foreach (kpi_v1_rebuild_map_keys($salesMap) as $iso) {
        if (strpos((string) $iso, $prefix) !== 0) {
            continue;
        }
        $n = kpi_v1_rebuild_num(kpi_v1_rebuild_map_get($salesMap, $iso));
        if ($n !== null && $n > 0) {
            return true;
        }
    }
    return false;
}

function kpi_v1_rebuild_eligible_baseline_years($store, $salesMap, $operatingYear)
{
    $oy = (int) $operatingYear;
    $seen = [];
    $out = [];
    $years = kpi_v1_rebuild_prop($store, 'years');
    foreach (kpi_v1_rebuild_map_keys($years) as $yk) {
        $y = (int) $yk;
        if ($y >= $oy || isset($seen[$y])) {
            continue;
        }
        if (!kpi_v1_rebuild_year_has_sales($salesMap, $y)) {
            continue;
        }
        $seen[$y] = true;
        $out[] = $y;
    }
    foreach (kpi_v1_rebuild_map_keys($salesMap) as $iso) {
        if (!is_string($iso) || strlen($iso) < 4) {
            continue;
        }
        $y = (int) substr($iso, 0, 4);
        if ($y >= $oy || isset($seen[$y])) {
            continue;
        }
        if (!kpi_v1_rebuild_year_has_sales($salesMap, $y)) {
            continue;
        }
        $seen[$y] = true;
        $out[] = $y;
    }
    rsort($out, SORT_NUMERIC);
    $out = array_slice($out, 0, 5);
    sort($out, SORT_NUMERIC);
    return $out;
}

function kpi_v1_rebuild_default_baseline_years($store, $salesMap, $operatingYear)
{
    $eligible = kpi_v1_rebuild_eligible_baseline_years($store, $salesMap, $operatingYear);
    $picked = [];
    for ($i = count($eligible) - 1; $i >= 0 && count($picked) < 2; $i--) {
        array_unshift($picked, $eligible[$i]);
    }
    return $picked;
}

function kpi_v1_rebuild_normalize_baseline_years($years, $salesMap, $operatingYear)
{
    $oy = (int) $operatingYear;
    $seen = [];
    $out = [];
    if (!is_array($years)) {
        return [];
    }
    foreach ($years as $raw) {
        $y = (int) $raw;
        if ($y < 1 || $y >= $oy || isset($seen[$y])) {
            continue;
        }
        if (!kpi_v1_rebuild_year_has_sales($salesMap, $y)) {
            continue;
        }
        $seen[$y] = true;
        $out[] = $y;
    }
    sort($out, SORT_NUMERIC);
    return $out;
}

function kpi_v1_rebuild_read_baseline_years($store, $salesMap, $year)
{
    $rec = kpi_v1_rebuild_year_rec($store, $year);
    $plan = kpi_v1_rebuild_prop($rec, 'plan');
    $raw = kpi_v1_rebuild_prop($plan, 'weekdayBaselineYears');
    if (is_object($raw)) {
        $raw = array_values(get_object_vars($raw));
    }
    $normalized = kpi_v1_rebuild_normalize_baseline_years($raw, $salesMap, $year);
    if (count($normalized)) {
        return $normalized;
    }
    return kpi_v1_rebuild_default_baseline_years($store, $salesMap, $year);
}

function kpi_v1_rebuild_read_annual_target($store, $year)
{
    $rec = kpi_v1_rebuild_year_rec($store, $year);
    $plan = kpi_v1_rebuild_prop($rec, 'plan');
    $n = kpi_v1_rebuild_num(kpi_v1_rebuild_prop($plan, 'targetSales'));
    if ($n === null || $n <= 0) {
        return null;
    }
    return $n;
}

function kpi_v1_rebuild_read_hl_weights($store, $year, $defaultHl)
{
    $rec = kpi_v1_rebuild_year_rec($store, $year);
    $plan = kpi_v1_rebuild_prop($rec, 'plan');
    $weights = kpi_v1_rebuild_prop($plan, 'monthlyHlWeights');
    if (is_object($weights)) {
        $weights = array_values(get_object_vars($weights));
    }
    if (!is_array($weights) || count($weights) !== 12) {
        return $defaultHl;
    }
    $out = [];
    for ($i = 0; $i < 12; $i++) {
        $n = kpi_v1_rebuild_num($weights[$i]);
        $out[] = ($n === null) ? 100.0 : $n;
    }
    return $out;
}

function kpi_v1_rebuild_daily_target_mode($store, $year)
{
    $rec = kpi_v1_rebuild_year_rec($store, $year);
    $plan = kpi_v1_rebuild_prop($rec, 'plan');
    $mode = (string) kpi_v1_rebuild_prop($plan, 'dailyTargetMode', '');
    if ($mode === 'monthly-flat' || $mode === 'weekday-weighted') {
        return $mode;
    }
    return 'weekday-weighted';
}

function kpi_v1_rebuild_plan_monthly_targets($salesMap, $bizMap, $store, $year, $defaultHl)
{
    $annual = kpi_v1_rebuild_read_annual_target($store, $year);
    if ($annual === null) {
        return null;
    }
    $weights = kpi_v1_rebuild_read_hl_weights($store, $year, $defaultHl);
    $monthlyBD = array_fill(0, 12, 0);
    $totalBD = 0;
    for ($m0 = 0; $m0 < 12; $m0++) {
        $dc = kpi_v1_rebuild_days_in_month($year, $m0);
        for ($day = 1; $day <= $dc; $day++) {
            if (!kpi_v1_rebuild_is_calendar_biz($salesMap, $bizMap, $year, $m0, $day)) {
                continue;
            }
            $monthlyBD[$m0]++;
            $totalBD++;
        }
    }
    if ($totalBD <= 0) {
        return null;
    }
    $monthlyTargets = [];
    for ($mi = 0; $mi < 12; $mi++) {
        $hl = $weights[$mi];
        $bdCount = $monthlyBD[$mi];
        if ($bdCount <= 0) {
            $monthlyTargets[] = 0.0;
            continue;
        }
        $monthlyAvg = ($annual * $bdCount) / $totalBD;
        $monthlyTargets[] = ($monthlyAvg * $hl) / 100.0;
    }
    return [
        'monthlyBD' => $monthlyBD,
        'monthlyTargets' => $monthlyTargets,
    ];
}

function kpi_v1_rebuild_month_sales_total($salesMap, $bizMap, $year, $m0)
{
    $dc = kpi_v1_rebuild_days_in_month($year, $m0);
    $total = 0.0;
    for ($day = 1; $day <= $dc; $day++) {
        if (!kpi_v1_rebuild_is_calendar_biz($salesMap, $bizMap, $year, $m0, $day)) {
            continue;
        }
        $iso = kpi_v1_rebuild_iso($year, $m0, $day);
        $n = kpi_v1_rebuild_num(kpi_v1_rebuild_map_get($salesMap, $iso));
        if ($n !== null && $n > 0) {
            $total += $n;
        }
    }
    return $total;
}

function kpi_v1_rebuild_dow_sales_total($salesMap, $bizMap, $year, $m0, $dow)
{
    $dc = kpi_v1_rebuild_days_in_month($year, $m0);
    $total = 0.0;
    for ($day = 1; $day <= $dc; $day++) {
        if (!kpi_v1_rebuild_is_calendar_biz($salesMap, $bizMap, $year, $m0, $day)) {
            continue;
        }
        if (kpi_v1_rebuild_dow($year, $m0, $day) !== (int) $dow) {
            continue;
        }
        $iso = kpi_v1_rebuild_iso($year, $m0, $day);
        $n = kpi_v1_rebuild_num(kpi_v1_rebuild_map_get($salesMap, $iso));
        if ($n !== null && $n > 0) {
            $total += $n;
        }
    }
    return $total;
}

function kpi_v1_rebuild_share_for_year($salesMap, $bizMap, $year, $m0, $dow)
{
    $monthSales = kpi_v1_rebuild_month_sales_total($salesMap, $bizMap, $year, $m0);
    if (!($monthSales > 0)) {
        return null;
    }
    return kpi_v1_rebuild_dow_sales_total($salesMap, $bizMap, $year, $m0, $dow) / $monthSales;
}

function kpi_v1_rebuild_share_avg($salesMap, $bizMap, $baselineYears, $m0, $dow, $fallback)
{
    if (!count($baselineYears)) {
        return $fallback;
    }
    $sum = 0.0;
    $n = 0;
    foreach ($baselineYears as $y) {
        $share = kpi_v1_rebuild_share_for_year($salesMap, $bizMap, $y, $m0, $dow);
        if ($share === null || !kpi_v1_rebuild_is_finite_num($share)) {
            continue;
        }
        $sum += $share;
        $n++;
    }
    if (!$n) {
        return $fallback;
    }
    return $sum / $n;
}

function kpi_v1_rebuild_count_dow_in_month($salesMap, $bizMap, $year, $m0, $dow)
{
    $dc = kpi_v1_rebuild_days_in_month($year, $m0);
    $count = 0;
    for ($day = 1; $day <= $dc; $day++) {
        if (!kpi_v1_rebuild_is_calendar_biz($salesMap, $bizMap, $year, $m0, $day)) {
            continue;
        }
        if (kpi_v1_rebuild_dow($year, $m0, $day) === (int) $dow) {
            $count++;
        }
    }
    return $count;
}

function kpi_v1_rebuild_daily_kpi_by_dow($plan, $salesMap, $bizMap, $year, $m0, $dow, $baselineYears, $fallback)
{
    if ($plan === null) {
        return null;
    }
    $monthlyTarget = $plan['monthlyTargets'][$m0];
    if (!($monthlyTarget > 0)) {
        return 0.0;
    }
    $shareAvg = kpi_v1_rebuild_share_avg($salesMap, $bizMap, $baselineYears, $m0, $dow, $fallback);
    $count = kpi_v1_rebuild_count_dow_in_month($salesMap, $bizMap, $year, $m0, $dow);
    if ($count <= 0) {
        return 0.0;
    }
    return ($monthlyTarget * $shareAvg) / $count;
}

function kpi_v1_rebuild_flat_daily($plan, $salesMap, $bizMap, $year, $iso)
{
    if ($plan === null || !kpi_v1_facts_valid_iso($iso)) {
        return null;
    }
    $parts = explode('-', $iso);
    $m0 = ((int) $parts[1]) - 1;
    $day = (int) $parts[2];
    if (!kpi_v1_rebuild_is_calendar_biz($salesMap, $bizMap, $year, $m0, $day)) {
        return 0.0;
    }
    $bdCount = $plan['monthlyBD'][$m0];
    if (!($bdCount > 0)) {
        return 0.0;
    }
    $monthlyTarget = $plan['monthlyTargets'][$m0];
    if (!($monthlyTarget > 0)) {
        return 0.0;
    }
    return $monthlyTarget / $bdCount;
}

function kpi_v1_rebuild_raw_daily_target(
    $plan,
    $salesMap,
    $bizMap,
    $year,
    $iso,
    $mode,
    $baselineYears,
    $fallback
) {
    if (!kpi_v1_facts_valid_iso($iso)) {
        return null;
    }
    $parts = explode('-', $iso);
    $isoYear = (int) $parts[0];
    if ($isoYear !== (int) $year) {
        return null;
    }
    $m0 = ((int) $parts[1]) - 1;
    $day = (int) $parts[2];
    $value = null;
    if ($mode === 'weekday-weighted') {
        if (count($baselineYears)) {
            if (!kpi_v1_rebuild_is_calendar_biz($salesMap, $bizMap, $year, $m0, $day)) {
                $value = 0.0;
            } else {
                $dow = kpi_v1_rebuild_dow($year, $m0, $day);
                $value = kpi_v1_rebuild_daily_kpi_by_dow(
                    $plan,
                    $salesMap,
                    $bizMap,
                    $year,
                    $m0,
                    $dow,
                    $baselineYears,
                    $fallback
                );
            }
        }
        if ($value === null || !kpi_v1_rebuild_is_finite_num($value)) {
            $value = kpi_v1_rebuild_flat_daily($plan, $salesMap, $bizMap, $year, $iso);
        }
    } else {
        $value = kpi_v1_rebuild_flat_daily($plan, $salesMap, $bizMap, $year, $iso);
    }
    return $value;
}

function kpi_v1_rebuild_month_display_map(
    $plan,
    $salesMap,
    $bizMap,
    $year,
    $m0,
    $mode,
    $baselineYears,
    $fallback
) {
    $map = [];
    if ($plan === null) {
        return $map;
    }
    $monthlyTarget = $plan['monthlyTargets'][$m0];
    if (!($monthlyTarget > 0)) {
        return $map;
    }
    $rows = [];
    $dc = kpi_v1_rebuild_days_in_month($year, $m0);
    for ($day = 1; $day <= $dc; $day++) {
        if (!kpi_v1_rebuild_is_calendar_biz($salesMap, $bizMap, $year, $m0, $day)) {
            continue;
        }
        $iso = kpi_v1_rebuild_iso($year, $m0, $day);
        $raw = kpi_v1_rebuild_raw_daily_target(
            $plan,
            $salesMap,
            $bizMap,
            $year,
            $iso,
            $mode,
            $baselineYears,
            $fallback
        );
        if ($raw === null || !kpi_v1_rebuild_is_finite_num($raw)) {
            $raw = 0.0;
        }
        $rows[] = ['iso' => $iso, 'raw' => $raw];
    }
    $targetSum = (int) round($monthlyTarget);
    $sumRounded = 0;
    $last = count($rows) - 1;
    for ($i = 0; $i < count($rows); $i++) {
        if ($i === $last) {
            $display = $targetSum - $sumRounded;
        } else {
            $display = (int) round($rows[$i]['raw']);
            $sumRounded += $display;
        }
        $map[$rows[$i]['iso']] = $display;
    }
    return $map;
}

function kpi_v1_rebuild_year_rows($store, $year, $defaultHl, $placeholder, $fallback)
{
    $timeline = kpi_v1_rebuild_prop($store, 'timeline');
    $salesMap = kpi_v1_rebuild_prop($timeline, 'dailySales');
    $bizMap = kpi_v1_rebuild_prop($timeline, 'businessDays');
    $plan = kpi_v1_rebuild_plan_monthly_targets($salesMap, $bizMap, $store, $year, $defaultHl);
    $mode = kpi_v1_rebuild_daily_target_mode($store, $year);
    $baselineYears = kpi_v1_rebuild_read_baseline_years($store, $salesMap, $year);
    $monthMaps = [];
    for ($m0 = 0; $m0 < 12; $m0++) {
        $monthMaps[$m0] = kpi_v1_rebuild_month_display_map(
            $plan,
            $salesMap,
            $bizMap,
            $year,
            $m0,
            $mode,
            $baselineYears,
            $fallback
        );
    }

    $rows = [];
    $ytdA = 0.0;
    $ytdT = 0.0;
    $mtdA = 0.0;
    $mtdT = 0.0;
    $prevMonth = -1;
    for ($m0 = 0; $m0 < 12; $m0++) {
        $dc = kpi_v1_rebuild_days_in_month($year, $m0);
        for ($day = 1; $day <= $dc; $day++) {
            if ($m0 !== $prevMonth) {
                $mtdA = 0.0;
                $mtdT = 0.0;
                $prevMonth = $m0;
            }
            $iso = kpi_v1_rebuild_iso($year, $m0, $day);
            $isBiz = kpi_v1_rebuild_snapshot_biz($bizMap, $iso);
            $sales = kpi_v1_rebuild_snapshot_sales($salesMap, $iso, $placeholder);
            $dailyTarget = null;
            if ($isBiz) {
                if (isset($monthMaps[$m0][$iso])) {
                    $dailyTarget = (float) $monthMaps[$m0][$iso];
                } else {
                    $raw = kpi_v1_rebuild_raw_daily_target(
                        $plan,
                        $salesMap,
                        $bizMap,
                        $year,
                        $iso,
                        $mode,
                        $baselineYears,
                        $fallback
                    );
                    if ($raw !== null && kpi_v1_rebuild_is_finite_num($raw)) {
                        $dailyTarget = (float) round($raw);
                    }
                }
                $ytdA += $sales;
                $mtdA += $sales;
                if ($dailyTarget !== null) {
                    $ytdT += $dailyTarget;
                    $mtdT += $dailyTarget;
                }
            }
            $rows[] = [
                'iso' => $iso,
                'sales' => round($sales, 2),
                'business_day' => $isBiz ? 1 : 0,
                'daily_target' => $dailyTarget,
                'mtd_actual' => round($mtdA, 2),
                'mtd_target' => round($mtdT, 2),
                'ytd_actual' => round($ytdA, 2),
                'ytd_target' => round($ytdT, 2),
            ];
        }
    }
    return $rows;
}

if ($method === 'GET') {
    kpi_v1_json_out(200, [
        'ok' => true,
        'service' => 'rebuild-year-facts',
        'methods' => ['POST'],
        'note' => 'POST { "year": YYYY } writes that year of kpi_daily_facts from the store blob. Does not rewrite store_json.',
    ]);
}

if ($method === 'POST') {
    @set_time_limit(90);
    $raw = file_get_contents('php://input');
    $body = json_decode($raw, true);
    if (!is_array($body) || !isset($body['year'])) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'missing_year']);
    }
    $year = (int) $body['year'];
    if ($year < 2000 || $year > 2100) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_year']);
    }
    $blob = kpi_v1_db_read_blob($cfg, $userId);
    $store = isset($blob->store) ? $blob->store : null;
    if ($store === null) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'no_store']);
    }
    $rows = kpi_v1_rebuild_year_rows(
        $store,
        $year,
        $KPI_REBUILD_DEFAULT_HL,
        $KPI_REBUILD_PLACEHOLDER_SALES,
        $KPI_REBUILD_WEEKDAY_FALLBACK
    );
    $written = kpi_v1_db_upsert_daily_facts($cfg, $userId, $rows);
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'year' => $year,
        'written' => $written,
    ]);
}

kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);

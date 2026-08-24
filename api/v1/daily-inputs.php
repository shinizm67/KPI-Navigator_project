<?php
/**
 * snapshot-store 入力正本化 — window GET/PUT for kpi_daily_inputs.
 * Does not replace store.php. Does not rewrite kpi_store.store_json.
 * Does not touch kpi_daily_facts (解正本は別表).
 */

require __DIR__ . '/_entitlement.php';
require_once __DIR__ . '/_db.php';

$cfg = kpi_v1_load_config();
kpi_v1_store_boot($cfg);

$userId = kpi_v1_store_resolve_user_id($cfg);
$method = $_SERVER['REQUEST_METHOD'];

$MAX_WINDOW_DAYS = 550;
$MAX_PUT_ROWS = 366;

if (!kpi_v1_storage_is_mysql($cfg)) {
    kpi_v1_json_out(501, ['ok' => false, 'error' => 'storage_not_mysql']);
}

function kpi_v1_inputs_window_days($fromIso, $toIso)
{
    $from = DateTime::createFromFormat('Y-m-d', $fromIso);
    $to = DateTime::createFromFormat('Y-m-d', $toIso);
    if (!$from || !$to) {
        return null;
    }
    $from->setTime(0, 0, 0);
    $to->setTime(0, 0, 0);
    if ($to < $from) {
        return null;
    }
    return (int) $from->diff($to)->days + 1;
}

if ($method === 'GET') {
    $from = isset($_GET['from']) ? (string) $_GET['from'] : '';
    $to = isset($_GET['to']) ? (string) $_GET['to'] : '';
    if (!kpi_v1_facts_valid_iso($from) || !kpi_v1_facts_valid_iso($to)) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_from_or_to']);
    }
    $days = kpi_v1_inputs_window_days($from, $to);
    if ($days === null) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_range']);
    }
    if ($days > $MAX_WINDOW_DAYS) {
        kpi_v1_json_out(400, [
            'ok' => false,
            'error' => 'window_too_large',
            'maxDays' => $MAX_WINDOW_DAYS,
        ]);
    }
    $rows = kpi_v1_db_read_daily_inputs($cfg, $userId, $from, $to);
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'from' => $from,
        'to' => $to,
        'count' => count($rows),
        'rows' => $rows,
    ]);
}

if ($method === 'PUT') {
    $raw = file_get_contents('php://input');
    $body = json_decode($raw, true);
    if (!is_array($body) || !isset($body['rows']) || !is_array($body['rows'])) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'missing_rows']);
    }
    if (count($body['rows']) > $MAX_PUT_ROWS) {
        kpi_v1_json_out(400, [
            'ok' => false,
            'error' => 'too_many_rows',
            'maxRows' => $MAX_PUT_ROWS,
        ]);
    }
    $parsed = [];
    foreach ($body['rows'] as $item) {
        if (!is_array($item) || !isset($item['iso']) || !kpi_v1_facts_valid_iso((string) $item['iso'])) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_iso']);
        }
        $sales = kpi_v1_facts_num(isset($item['sales']) ? $item['sales'] : 0, false);
        if ($sales === false) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_number']);
        }
        $row = [
            'iso' => (string) $item['iso'],
            'sales' => $sales,
            'touch_business_day' => false,
            'business_day' => null,
        ];
        if (array_key_exists('businessDay', $item)) {
            $rawBiz = $item['businessDay'];
            if ($rawBiz === null) {
                $row['touch_business_day'] = true;
                $row['business_day'] = null;
            } elseif ($rawBiz === true || $rawBiz === 1 || $rawBiz === '1') {
                $row['touch_business_day'] = true;
                $row['business_day'] = 1;
            } elseif ($rawBiz === false || $rawBiz === 0 || $rawBiz === '0') {
                $row['touch_business_day'] = true;
                $row['business_day'] = 0;
            } else {
                kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_business_day']);
            }
        }
        $parsed[] = $row;
    }
    $written = kpi_v1_db_upsert_daily_inputs($cfg, $userId, $parsed);
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'written' => $written,
    ]);
}

kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);

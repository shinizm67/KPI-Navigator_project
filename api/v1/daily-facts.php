<?php
/**
 * Phase 2b — window GET/PUT for kpi_daily_facts rows.
 * Does not replace store.php. Does not rewrite kpi_store.store_json.
 * HTML is not wired yet (phase 2c).
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

function kpi_v1_facts_window_days($fromIso, $toIso)
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
    $days = kpi_v1_facts_window_days($from, $to);
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
    $rows = kpi_v1_db_read_daily_facts($cfg, $userId, $from, $to);
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
        $dailyTarget = kpi_v1_facts_num(
            array_key_exists('dailyTarget', $item) ? $item['dailyTarget'] : null,
            true
        );
        $mtdActual = kpi_v1_facts_num(isset($item['mtdActual']) ? $item['mtdActual'] : 0, false);
        $mtdTarget = kpi_v1_facts_num(
            array_key_exists('mtdTarget', $item) ? $item['mtdTarget'] : null,
            true
        );
        $ytdActual = kpi_v1_facts_num(isset($item['ytdActual']) ? $item['ytdActual'] : 0, false);
        $ytdTarget = kpi_v1_facts_num(
            array_key_exists('ytdTarget', $item) ? $item['ytdTarget'] : null,
            true
        );
        if ($sales === false || $dailyTarget === false || $mtdActual === false
            || $mtdTarget === false || $ytdActual === false || $ytdTarget === false) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_number']);
        }
        $biz = !empty($item['businessDay']);
        $parsed[] = [
            'iso' => (string) $item['iso'],
            'sales' => $sales,
            'business_day' => $biz ? 1 : 0,
            'daily_target' => $dailyTarget,
            'mtd_actual' => $mtdActual,
            'mtd_target' => $mtdTarget,
            'ytd_actual' => $ytdActual,
            'ytd_target' => $ytdTarget,
        ];
    }
    $written = kpi_v1_db_upsert_daily_facts($cfg, $userId, $parsed);
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'written' => $written,
    ]);
}

kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);

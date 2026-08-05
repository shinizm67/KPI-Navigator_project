<?php
/**
 * Phase A/B2 — kpiYearStore (+ optional annualNav) GET/PUT.
 * Phase B2: session auth (per-user JSON). Legacy token via storeAuthMode=token.
 * Docs: docs/backend-phase-a-store-api.md
 */

require __DIR__ . '/_auth.php';

$cfg = kpi_v1_load_config();
kpi_v1_store_boot($cfg);

$userId = kpi_v1_store_resolve_user_id($cfg);
$path = kpi_v1_data_path($userId);
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $blob = kpi_v1_read_blob($path);
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'updatedAt' => $blob->updatedAt,
        'store' => $blob->store,
        'annualNav' => $blob->annualNav,
    ]);
}

if ($method === 'PUT') {
    $raw = file_get_contents('php://input');
    $body = json_decode($raw, false);
    if (!is_object($body)) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_json']);
    }
    if (!property_exists($body, 'store') && !property_exists($body, 'annualNav')) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'missing_store_or_annualNav']);
    }

    $blob = kpi_v1_read_blob($path);
    if (property_exists($body, 'store')) {
        if ($body->store !== null && !is_object($body->store)) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'store_must_be_object_or_null']);
        }
        $blob->store = $body->store;
    }
    if (property_exists($body, 'annualNav')) {
        if ($body->annualNav !== null && !is_object($body->annualNav)) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'annualNav_must_be_object_or_null']);
        }
        $blob->annualNav = $body->annualNav;
    }
    $blob->userId = $userId;
    $blob->updatedAt = gmdate('c');
    kpi_v1_write_blob($path, $blob);
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'updatedAt' => $blob->updatedAt,
    ]);
}

kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);

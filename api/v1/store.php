<?php
/**
 * Phase A/B2/B3 — kpiYearStore (+ optional annualNav + pl) GET/PUT.
 * Phase B2: session auth (per-user JSON). Legacy token via storeAuthMode=token.
 * Phase B3-T1: Basic strips / rejects years.*.dailyExpenses.
 * Phase B3-T2: Basic omits / rejects pl bundle (PL localStorage mirror).
 * Docs: docs/backend-phase-a-store-api.md · docs/plan-entitlement-security-memo.md
 */

require __DIR__ . '/_entitlement.php';

$cfg = kpi_v1_load_config();
kpi_v1_store_boot($cfg);

$userId = kpi_v1_store_resolve_user_id($cfg);
$plan = kpi_v1_entitlement_plan_for_store_user($cfg, $userId);
$path = kpi_v1_data_path($userId);
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $blob = kpi_v1_read_blob($path);
    $storeOut = $blob->store;
    if ($plan === 'basic' && $storeOut !== null) {
        $storeOut = kpi_v1_entitlement_strip_pro_from_store($storeOut);
    }
    $plOut = $blob->pl;
    if ($plan === 'basic') {
        $plOut = null;
    }
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'plan' => $plan,
        'updatedAt' => $blob->updatedAt,
        'store' => $storeOut,
        'annualNav' => $blob->annualNav,
        'pl' => $plOut,
    ]);
}

if ($method === 'PUT') {
    $raw = file_get_contents('php://input');
    $body = json_decode($raw, false);
    if (!is_object($body)) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_json']);
    }
    if (!property_exists($body, 'store')
        && !property_exists($body, 'annualNav')
        && !property_exists($body, 'pl')) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'missing_store_or_annualNav_or_pl']);
    }

    $blob = kpi_v1_read_blob($path);
    if (property_exists($body, 'store')) {
        if ($body->store !== null && !is_object($body->store)) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'store_must_be_object_or_null']);
        }
        if ($plan === 'basic' && $body->store !== null) {
            if (kpi_v1_entitlement_store_has_pro_payload($body->store)) {
                kpi_v1_json_out(403, [
                    'ok' => false,
                    'error' => 'entitlement_required',
                    'plan' => 'basic',
                    'feature' => 'expenses',
                ]);
            }
            $blob->store = kpi_v1_entitlement_merge_store_preserving_pro($body->store, $blob->store);
        } else {
            $blob->store = $body->store;
        }
    }
    if (property_exists($body, 'annualNav')) {
        if ($body->annualNav !== null && !is_object($body->annualNav)) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'annualNav_must_be_object_or_null']);
        }
        $blob->annualNav = $body->annualNav;
    }
    if (property_exists($body, 'pl')) {
        if ($body->pl !== null && !is_object($body->pl)) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'pl_must_be_object_or_null']);
        }
        if ($plan === 'basic') {
            if (kpi_v1_entitlement_pl_has_payload($body->pl)) {
                kpi_v1_json_out(403, [
                    'ok' => false,
                    'error' => 'entitlement_required',
                    'plan' => 'basic',
                    'feature' => 'pl',
                ]);
            }
            // Empty/null pl from Basic must not wipe server Pro data.
            $blob->pl = kpi_v1_entitlement_merge_pl_preserving($body->pl, $blob->pl);
        } else {
            $blob->pl = $body->pl;
        }
    }
    $blob->userId = $userId;
    $blob->updatedAt = gmdate('c');
    kpi_v1_write_blob($path, $blob);
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'plan' => $plan,
        'updatedAt' => $blob->updatedAt,
    ]);
}

kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);

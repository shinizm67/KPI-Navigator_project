<?php
/**
 * Phase A/B2/B3 — kpiYearStore (+ optional annualNav + pl) GET/PUT.
 * Phase B2: session auth (per-user JSON). Legacy token via storeAuthMode=token.
 * Phase B3-T1: Basic strips / rejects years.*.dailyExpenses.
 * Phase B3-T2: Basic omits / rejects pl bundle (PL localStorage mirror).
 * Phase B4-T1: PUT snapshots previous blob under data/backups/{userId}/.
 * Revision OCC: monotonic kpi_store.revision; expectedRevision required on PUT.
 * Docs: docs/backend-phase-a-store-api.md · docs/plan-entitlement-security-memo.md
 */

require __DIR__ . '/_entitlement.php';

$cfg = kpi_v1_load_config();
kpi_v1_store_boot($cfg);

$userId = kpi_v1_store_resolve_user_id($cfg);
$plan = kpi_v1_entitlement_plan_for_store_user($cfg, $userId);
$path = kpi_v1_data_path($userId);
$method = $_SERVER['REQUEST_METHOD'];

function kpi_v1_store_conflict_out($blob)
{
    kpi_v1_json_out(409, [
        'ok' => false,
        'error' => 'conflict',
        'revision' => isset($blob->revision) ? $blob->revision : null,
        'updatedAt' => isset($blob->updatedAt) ? $blob->updatedAt : null,
    ]);
}

function kpi_v1_parse_expected_revision($body)
{
    if (!is_object($body) || !property_exists($body, 'expectedRevision')) {
        return ['error' => 'precondition_required'];
    }
    $v = $body->expectedRevision;
    if ($v === null) {
        return ['value' => null];
    }
    if (is_bool($v) || is_array($v) || is_object($v)) {
        return ['error' => 'invalid_expected_revision'];
    }
    if (is_string($v)) {
        if (!preg_match('/^\d+$/', $v)) {
            return ['error' => 'invalid_expected_revision'];
        }
        $v = (int) $v;
    }
    if (is_float($v)) {
        if ($v < 0 || $v != floor($v)) {
            return ['error' => 'invalid_expected_revision'];
        }
        $v = (int) $v;
    }
    if (!is_int($v) || $v < 0) {
        return ['error' => 'invalid_expected_revision'];
    }
    return ['value' => $v];
}

/**
 * Apply PUT body onto a cloned current blob. Shape/entitlement 403 must be done first.
 */
function kpi_v1_apply_store_put_body($blob, $body, $plan)
{
    if (property_exists($body, 'store')) {
        if ($plan === 'basic' && $body->store !== null) {
            $blob->store = kpi_v1_entitlement_merge_store_preserving_pro($body->store, $blob->store);
        } else {
            $blob->store = $body->store;
        }
    }
    if (property_exists($body, 'annualNav')) {
        $blob->annualNav = $body->annualNav;
    }
    if (property_exists($body, 'pl')) {
        if ($plan === 'basic') {
            $blob->pl = kpi_v1_entitlement_merge_pl_preserving($body->pl, $blob->pl);
        } elseif (!kpi_v1_entitlement_pl_has_payload($body->pl)) {
            /* C2-L5-A: empty Pro PUT must not replace existing pl_json. reset-user-kpi is separate. */
        } else {
            $blob->pl = $body->pl;
        }
    }
    return $blob;
}

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
    $revision = null;
    if (property_exists($blob, 'revision') && $blob->revision !== null && $blob->revision !== '') {
        $revision = (int) $blob->revision;
    }
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'plan' => $plan,
        'revision' => $revision,
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
    $expectedParsed = kpi_v1_parse_expected_revision($body);
    if (isset($expectedParsed['error'])) {
        if ($expectedParsed['error'] === 'precondition_required') {
            kpi_v1_json_out(428, [
                'ok' => false,
                'error' => 'precondition_required',
            ]);
        }
        kpi_v1_json_out(400, ['ok' => false, 'error' => $expectedParsed['error']]);
    }
    $expectedRevision = $expectedParsed['value'];
    if (!property_exists($body, 'store')
        && !property_exists($body, 'annualNav')
        && !property_exists($body, 'pl')) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'missing_store_or_annualNav_or_pl']);
    }
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
        }
    }
    if (property_exists($body, 'annualNav')) {
        if ($body->annualNav !== null && !is_object($body->annualNav)) {
            kpi_v1_json_out(400, ['ok' => false, 'error' => 'annualNav_must_be_object_or_null']);
        }
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
        }
    }

    $buildNext = function ($current) use ($body, $plan, $userId) {
        $blob = json_decode(json_encode($current));
        if (!is_object($blob)) {
            $blob = kpi_v1_empty_store_blob($userId);
        }
        return kpi_v1_apply_store_put_body($blob, $body, $plan);
    };

    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        $cas = kpi_v1_db_cas_put($cfg, $userId, $expectedRevision, $buildNext);
    } else {
        $cas = kpi_v1_file_cas_put($path, $userId, $expectedRevision, $buildNext);
    }

    if (empty($cas['ok'])) {
        kpi_v1_store_conflict_out(isset($cas['blob']) ? $cas['blob'] : kpi_v1_empty_store_blob($userId));
    }
    $out = $cas['blob'];
    kpi_v1_json_out(200, [
        'ok' => true,
        'userId' => $userId,
        'plan' => $plan,
        'revision' => isset($out->revision) ? (int) $out->revision : null,
        'updatedAt' => isset($out->updatedAt) ? $out->updatedAt : null,
    ]);
}

kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);

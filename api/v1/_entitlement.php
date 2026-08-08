<?php
/**
 * Phase B3 — Basic / Pro entitlement helpers.
 * Pro payload in kpiYearStore (for now): years.*.dailyExpenses
 * Docs: docs/plan-entitlement-security-memo.md
 */

require_once __DIR__ . '/_auth.php';

function kpi_v1_entitlement_normalize_plan($plan)
{
    $p = strtolower(trim((string) $plan));
    return $p === 'basic' ? 'basic' : 'pro';
}

function kpi_v1_entitlement_plan_from_user($user, $cfg)
{
    if (is_array($user) && isset($user['plan']) && (string) $user['plan'] !== '') {
        return kpi_v1_entitlement_normalize_plan($user['plan']);
    }
    $legacy = isset($cfg['legacyPlan']) ? $cfg['legacyPlan'] : 'pro';
    return kpi_v1_entitlement_normalize_plan($legacy);
}

function kpi_v1_entitlement_default_plan($cfg)
{
    $d = isset($cfg['defaultPlan']) ? $cfg['defaultPlan'] : 'basic';
    return kpi_v1_entitlement_normalize_plan($d);
}

/**
 * Resolve plan for the current store request (session user or token mode).
 */
function kpi_v1_entitlement_plan_for_store_user($cfg, $userId)
{
    $mode = isset($cfg['storeAuthMode']) ? (string) $cfg['storeAuthMode'] : 'session';
    $sessionUid = kpi_v1_auth_current_user_id();
    if ($sessionUid !== null && $sessionUid === (string) $userId) {
        $user = kpi_v1_auth_read_user($sessionUid);
        return kpi_v1_entitlement_plan_from_user($user, $cfg);
    }
    if ($mode === 'token' || ($mode === 'dual' && $sessionUid === null)) {
        $tokPlan = isset($cfg['tokenModePlan']) ? $cfg['tokenModePlan'] : 'pro';
        return kpi_v1_entitlement_normalize_plan($tokPlan);
    }
    $user = kpi_v1_auth_read_user($userId);
    return kpi_v1_entitlement_plan_from_user($user, $cfg);
}

function kpi_v1_entitlement_year_has_pro_payload($yearRec)
{
    if (!is_object($yearRec) && !is_array($yearRec)) {
        return false;
    }
    $de = is_object($yearRec)
        ? (isset($yearRec->dailyExpenses) ? $yearRec->dailyExpenses : null)
        : (isset($yearRec['dailyExpenses']) ? $yearRec['dailyExpenses'] : null);
    if ($de === null) {
        return false;
    }
    if (is_object($de)) {
        $arr = get_object_vars($de);
        return count($arr) > 0;
    }
    if (is_array($de)) {
        return count($de) > 0;
    }
    return false;
}

function kpi_v1_entitlement_store_has_pro_payload($store)
{
    if ($store === null) {
        return false;
    }
    if (!is_object($store) && !is_array($store)) {
        return false;
    }
    $years = is_object($store)
        ? (isset($store->years) ? $store->years : null)
        : (isset($store['years']) ? $store['years'] : null);
    if ($years === null) {
        return false;
    }
    if (is_object($years)) {
        foreach (get_object_vars($years) as $rec) {
            if (kpi_v1_entitlement_year_has_pro_payload($rec)) {
                return true;
            }
        }
        return false;
    }
    if (is_array($years)) {
        foreach ($years as $rec) {
            if (kpi_v1_entitlement_year_has_pro_payload($rec)) {
                return true;
            }
        }
    }
    return false;
}

/**
 * Deep-ish clone via JSON (store blobs are JSON-safe).
 */
function kpi_v1_entitlement_clone_json($value)
{
    if ($value === null) {
        return null;
    }
    return json_decode(json_encode($value));
}

/**
 * Strip Pro-only fields from a store object (for Basic GET responses).
 * Does not mutate the on-disk blob.
 */
function kpi_v1_entitlement_strip_pro_from_store($store)
{
    $out = kpi_v1_entitlement_clone_json($store);
    if ($out === null || !is_object($out) || !isset($out->years) || !is_object($out->years)) {
        return $out;
    }
    foreach (get_object_vars($out->years) as $yk => $rec) {
        if (is_object($rec) && property_exists($rec, 'dailyExpenses')) {
            unset($rec->dailyExpenses);
        }
    }
    return $out;
}

/**
 * Merge Basic PUT into existing blob without letting Basic wipe/overwrite Pro fields.
 * Caller must reject non-empty Pro payload on incoming first.
 */
function kpi_v1_entitlement_merge_store_preserving_pro($incoming, $existing)
{
    $merged = kpi_v1_entitlement_clone_json($incoming);
    if ($merged === null) {
        return $existing;
    }
    if (!is_object($merged)) {
        return $merged;
    }
    if (!isset($merged->years) || !is_object($merged->years)) {
        $merged->years = (object) [];
    }

    $exYears = null;
    if (is_object($existing) && isset($existing->years) && is_object($existing->years)) {
        $exYears = $existing->years;
    }

    foreach (get_object_vars($merged->years) as $yk => $rec) {
        if (!is_object($rec)) {
            continue;
        }
        if (property_exists($rec, 'dailyExpenses')) {
            unset($rec->dailyExpenses);
        }
        if ($exYears && isset($exYears->{$yk}) && is_object($exYears->{$yk})
            && isset($exYears->{$yk}->dailyExpenses)) {
            $rec->dailyExpenses = kpi_v1_entitlement_clone_json($exYears->{$yk}->dailyExpenses);
        }
    }

    // Years present only on server (Basic client omitted them): keep Pro data by
    // not deleting those years — last-write-wins on whole store means client years
    // replace. Preserve dailyExpenses on overlapping years only (above).
    // If a year exists only on server and client omitted it, it is dropped (same as
    // full store replace). Acceptable for B3-T1; Basic clients hydrate stripped store.

    return $merged;
}

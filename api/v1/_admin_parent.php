<?php
/**
 * Pure parent-link validation (no DB / config). Used by admin store + CLI tests.
 */

/**
 * Lookup-injectable parent validation. Returns null if OK, else error code.
 * $lookup: callable(string $userId): ?array user row with optional parentUserId, disabled
 */
function kpi_v1_admin_parent_reject_reason_lookup($childUserId, $parentUserId, $lookup)
{
    $childUserId = (string) $childUserId;
    $parentUserId = $parentUserId !== null && $parentUserId !== '' ? (string) $parentUserId : null;
    if ($parentUserId === null) {
        return null;
    }
    if ($parentUserId === $childUserId) {
        return 'self_parent';
    }
    if (!is_callable($lookup)) {
        return 'invalid_parent';
    }
    $parent = $lookup($parentUserId);
    if (!is_array($parent)) {
        return 'parent_not_found';
    }
    if (!empty($parent['disabled'])) {
        return 'invalid_parent';
    }
    // Walk ancestors of parent; reject if child appears (cycle).
    $seen = [];
    $cur = $parentUserId;
    $guard = 0;
    while ($cur !== null && $guard < 32) {
        if ($cur === $childUserId) {
            return 'cycle';
        }
        if (isset($seen[$cur])) {
            return 'cycle';
        }
        $seen[$cur] = true;
        $u = $lookup($cur);
        if (!is_array($u)) {
            break;
        }
        $cur = !empty($u['parentUserId']) ? (string) $u['parentUserId'] : null;
        $guard++;
    }
    return null;
}

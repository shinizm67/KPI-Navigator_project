<?php
/**
 * CLI — Related Accounts parent validation (in-memory; no production DB).
 * Usage: php scripts/_test_related_accounts_parent_logic.php
 */
declare(strict_types=1);

require dirname(__DIR__) . '/api/v1/_admin_parent.php';

$failed = 0;
$passed = 0;

function check(string $name, bool $cond, string $detail = ''): void
{
    global $failed, $passed;
    if ($cond) {
        $passed++;
        echo "PASS  {$name}\n";
    } else {
        $failed++;
        echo "FAIL  {$name}" . ($detail !== '' ? " — {$detail}" : '') . "\n";
    }
}

$users = [
    'A' => ['userId' => 'A', 'parentUserId' => null, 'disabled' => false],
    'B' => ['userId' => 'B', 'parentUserId' => 'A', 'disabled' => false],
    'C' => ['userId' => 'C', 'parentUserId' => 'B', 'disabled' => false],
    'D' => ['userId' => 'D', 'parentUserId' => null, 'disabled' => false],
    'X' => ['userId' => 'X', 'parentUserId' => null, 'disabled' => true],
];

$lookup = static function (string $uid) use (&$users) {
    return $users[$uid] ?? null;
};

// 1) valid parent set
check('valid parent set', kpi_v1_admin_parent_reject_reason_lookup('D', 'A', $lookup) === null);

// Simulate set: D.parent = A
$users['D']['parentUserId'] = 'A';
check('after set parent stored', ($users['D']['parentUserId'] ?? null) === 'A');

// 2) parent clear
check('parent clear allowed', kpi_v1_admin_parent_reject_reason_lookup('D', null, $lookup) === null);
$users['D']['parentUserId'] = null;
check('after clear parent null', empty($users['D']['parentUserId']));

// 3) self-parent reject
check('self-parent reject', kpi_v1_admin_parent_reject_reason_lookup('A', 'A', $lookup) === 'self_parent');

// 4) nonexistent parent reject
check('missing parent reject', kpi_v1_admin_parent_reject_reason_lookup('A', 'MISSING', $lookup) === 'parent_not_found');

// 5) cycle reject: A -> C would cycle because C->B->A
check('cycle reject', kpi_v1_admin_parent_reject_reason_lookup('A', 'C', $lookup) === 'cycle');

// disabled parent
check('disabled parent reject', kpi_v1_admin_parent_reject_reason_lookup('A', 'X', $lookup) === 'invalid_parent');

// children derivation from parent_user_id
$childrenOfA = [];
foreach ($users as $uid => $u) {
    if (!empty($u['parentUserId']) && $u['parentUserId'] === 'A') {
        $childrenOfA[] = $uid;
    }
}
sort($childrenOfA);
check('children derived from parent_user_id', $childrenOfA === ['B']);

echo "\n{$passed} passed, {$failed} failed\n";
exit($failed ? 1 : 0);

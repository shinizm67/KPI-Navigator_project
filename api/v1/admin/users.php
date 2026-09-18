<?php
/**
 * GET /api/v1/admin/users.php
 * Founder Super Admin only. Never returns password_hash / tokens.
 */

require __DIR__ . '/../_admin_store.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    kpi_v1_json_out(405, ['ok' => false, 'error' => 'method_not_allowed']);
}
kpi_v1_auth_require_founder_superadmin($cfg);

$users = kpi_v1_admin_list_users($cfg);
$rows = [];
foreach ($users as $u) {
    $uid = (string) $u['userId'];
    $profile = kpi_v1_profile_read($cfg, $uid);
    $children = kpi_v1_admin_list_child_ids($cfg, $uid);
    $rows[] = [
        'userId' => $uid,
        'email' => (string) ($u['email'] ?? ''),
        'plan' => (string) ($u['plan'] ?? 'basic'),
        'planUpdatedAt' => $u['planUpdatedAt'] ?? null,
        'createdAt' => $u['createdAt'] ?? null,
        'lastLoginAt' => $u['lastLoginAt'] ?? null,
        'parentUserId' => $u['parentUserId'] ?? null,
        'childCount' => count($children),
        'role' => $u['role'] ?? 'user',
        'disabled' => !empty($u['disabled']),
        'businessName' => $profile['synced'] ? ($profile['businessName'] ?? null) : null,
        'companyName' => $profile['synced'] ? ($profile['companyName'] ?? null) : null,
        'businessType' => $profile['synced'] ? ($profile['businessType'] ?? null) : null,
        'genre' => $profile['synced'] ? ($profile['genre'] ?? null) : null,
        'locale' => $profile['synced'] ? ($profile['locale'] ?? null) : null,
        'country' => $profile['synced'] ? ($profile['country'] ?? null) : null,
        'stateRegion' => $profile['synced'] ? ($profile['stateRegion'] ?? null) : null,
        'city' => $profile['synced'] ? ($profile['city'] ?? null) : null,
        'currency' => $profile['synced'] ? ($profile['currency'] ?? null) : null,
        'profileSynced' => !empty($profile['synced']),
        'accountStatus' => !empty($u['disabled']) ? 'disabled' : 'active',
    ];
}

kpi_v1_json_out(200, ['ok' => true, 'users' => $rows]);

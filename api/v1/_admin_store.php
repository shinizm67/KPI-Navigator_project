<?php
/**
 * Admin console data access: profiles, plan history, parent links, listings.
 * MySQL primary; file backend stores parallel JSON under api/v1/data/.
 */

require_once __DIR__ . '/_db.php';
require_once __DIR__ . '/_admin.php';

function kpi_v1_admin_profiles_dir()
{
    $dir = __DIR__ . '/data/profiles';
    if (!is_dir($dir)) {
        mkdir($dir, 0750, true);
    }
    return $dir;
}

function kpi_v1_admin_plan_history_path()
{
    return __DIR__ . '/data/plan_history.json';
}

function kpi_v1_profile_empty($userId)
{
    return [
        'userId' => (string) $userId,
        'businessName' => null,
        'companyName' => null,
        'businessType' => null,
        'genre' => null,
        'locale' => null,
        'country' => null,
        'stateRegion' => null,
        'city' => null,
        'currency' => null,
        'updatedAt' => null,
        'synced' => false,
    ];
}

function kpi_v1_profile_from_row($row)
{
    if (!$row) {
        return null;
    }
    return [
        'userId' => (string) $row['user_id'],
        'businessName' => $row['business_name'] !== null ? (string) $row['business_name'] : null,
        'companyName' => $row['company_name'] !== null ? (string) $row['company_name'] : null,
        'businessType' => $row['business_type'] !== null ? (string) $row['business_type'] : null,
        'genre' => $row['genre'] !== null ? (string) $row['genre'] : null,
        'locale' => $row['locale'] !== null ? (string) $row['locale'] : null,
        'country' => $row['country'] !== null ? (string) $row['country'] : null,
        'stateRegion' => $row['state_region'] !== null ? (string) $row['state_region'] : null,
        'city' => $row['city'] !== null ? (string) $row['city'] : null,
        'currency' => $row['currency'] !== null ? (string) $row['currency'] : null,
        'updatedAt' => !empty($row['updated_at']) ? kpi_v1_admin_dt_to_iso($row['updated_at']) : null,
        'synced' => true,
    ];
}

function kpi_v1_profile_read($cfg, $userId)
{
    $userId = (string) $userId;
    if (kpi_v1_storage_is_mysql($cfg)) {
        try {
            $pdo = kpi_v1_db($cfg);
            $st = $pdo->prepare('SELECT * FROM kpi_user_profiles WHERE user_id = ? LIMIT 1');
            $st->execute([$userId]);
            $row = $st->fetch(PDO::FETCH_ASSOC);
            $p = kpi_v1_profile_from_row($row);
            return $p !== null ? $p : kpi_v1_profile_empty($userId);
        } catch (Throwable $e) {
            return kpi_v1_profile_empty($userId);
        }
    }
    $path = kpi_v1_admin_profiles_dir() . '/' . preg_replace('/[^a-zA-Z0-9_-]/', '', $userId) . '.json';
    if (!is_file($path)) {
        return kpi_v1_profile_empty($userId);
    }
    $data = json_decode((string) file_get_contents($path), true);
    if (!is_array($data)) {
        return kpi_v1_profile_empty($userId);
    }
    $data['synced'] = true;
    $data['userId'] = $userId;
    return $data;
}

function kpi_v1_profile_write($cfg, $userId, $fields)
{
    $userId = (string) $userId;
    $now = gmdate('c');
    $payload = [
        'userId' => $userId,
        'businessName' => isset($fields['businessName']) ? (string) $fields['businessName'] : null,
        'companyName' => isset($fields['companyName']) ? (string) $fields['companyName'] : null,
        'businessType' => isset($fields['businessType']) ? (string) $fields['businessType'] : null,
        'genre' => isset($fields['genre']) ? (string) $fields['genre'] : null,
        'locale' => isset($fields['locale']) ? (string) $fields['locale'] : null,
        'country' => isset($fields['country']) ? (string) $fields['country'] : null,
        'stateRegion' => isset($fields['stateRegion']) ? (string) $fields['stateRegion'] : null,
        'city' => isset($fields['city']) ? (string) $fields['city'] : null,
        'currency' => isset($fields['currency']) ? (string) $fields['currency'] : null,
        'updatedAt' => $now,
        'synced' => true,
    ];
    foreach (['businessName','companyName','businessType','genre','locale','country','stateRegion','city','currency'] as $k) {
        if ($payload[$k] === '') {
            $payload[$k] = null;
        }
    }

    if (kpi_v1_storage_is_mysql($cfg)) {
        $pdo = kpi_v1_db($cfg);
        $st = $pdo->prepare(
            'INSERT INTO kpi_user_profiles
              (user_id, business_name, company_name, business_type, genre, locale, country, state_region, city, currency, updated_at)
             VALUES (?,?,?,?,?,?,?,?,?,?,?)
             ON DUPLICATE KEY UPDATE
               business_name=VALUES(business_name),
               company_name=VALUES(company_name),
               business_type=VALUES(business_type),
               genre=VALUES(genre),
               locale=VALUES(locale),
               country=VALUES(country),
               state_region=VALUES(state_region),
               city=VALUES(city),
               currency=VALUES(currency),
               updated_at=VALUES(updated_at)'
        );
        $ts = gmdate('Y-m-d H:i:s');
        $st->execute([
            $userId,
            $payload['businessName'],
            $payload['companyName'],
            $payload['businessType'],
            $payload['genre'],
            $payload['locale'],
            $payload['country'],
            $payload['stateRegion'],
            $payload['city'],
            $payload['currency'],
            $ts,
        ]);
        $payload['updatedAt'] = kpi_v1_admin_dt_to_iso($ts);
        return $payload;
    }

    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', $userId);
    $path = kpi_v1_admin_profiles_dir() . '/' . $safe . '.json';
    $tmp = $path . '.tmp';
    $json = json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json === false || file_put_contents($tmp, $json, LOCK_EX) === false || !rename($tmp, $path)) {
        @unlink($tmp);
        kpi_v1_json_out(500, ['ok' => false, 'error' => 'profile_write_failed']);
    }
    return $payload;
}

function kpi_v1_plan_history_append($cfg, $userId, $oldPlan, $newPlan, $changedBy, $source)
{
    $userId = (string) $userId;
    $newPlan = strtolower(trim((string) $newPlan));
    $oldPlan = $oldPlan !== null && $oldPlan !== '' ? strtolower(trim((string) $oldPlan)) : null;
    $source = preg_replace('/[^a-z0-9_\\-]/i', '', (string) $source) ?: 'system';
    $changedBy = $changedBy !== null && $changedBy !== '' ? (string) $changedBy : null;
    $now = gmdate('Y-m-d H:i:s');

    if (kpi_v1_storage_is_mysql($cfg)) {
        try {
            $pdo = kpi_v1_db($cfg);
            $st = $pdo->prepare(
                'INSERT INTO kpi_plan_history (user_id, old_plan, new_plan, changed_at, changed_by, source)
                 VALUES (?,?,?,?,?,?)'
            );
            $st->execute([$userId, $oldPlan, $newPlan, $now, $changedBy, $source]);
        } catch (Throwable $e) {
            // Table may not exist yet pre-migration; ignore to keep set-plan working.
        }
        return;
    }

    $path = kpi_v1_admin_plan_history_path();
    $rows = [];
    if (is_file($path)) {
        $decoded = json_decode((string) file_get_contents($path), true);
        if (is_array($decoded)) {
            $rows = $decoded;
        }
    }
    $rows[] = [
        'id' => count($rows) + 1,
        'userId' => $userId,
        'oldPlan' => $oldPlan,
        'newPlan' => $newPlan,
        'changedAt' => gmdate('c'),
        'changedBy' => $changedBy,
        'source' => $source,
    ];
    $tmp = $path . '.tmp';
    $json = json_encode($rows, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    if ($json !== false) {
        file_put_contents($tmp, $json, LOCK_EX);
        @rename($tmp, $path);
    }
}

function kpi_v1_plan_history_list($cfg, $userId, $limit = 50)
{
    $userId = (string) $userId;
    $limit = max(1, min(200, (int) $limit));
    if (kpi_v1_storage_is_mysql($cfg)) {
        try {
            $pdo = kpi_v1_db($cfg);
            $st = $pdo->prepare(
                'SELECT id, user_id, old_plan, new_plan, changed_at, changed_by, source
                 FROM kpi_plan_history WHERE user_id = ? ORDER BY changed_at DESC, id DESC LIMIT ' . (int) $limit
            );
            $st->execute([$userId]);
            $out = [];
            foreach ($st->fetchAll(PDO::FETCH_ASSOC) as $r) {
                $out[] = [
                    'id' => (int) $r['id'],
                    'userId' => (string) $r['user_id'],
                    'oldPlan' => $r['old_plan'] !== null ? (string) $r['old_plan'] : null,
                    'newPlan' => (string) $r['new_plan'],
                    'changedAt' => kpi_v1_admin_dt_to_iso($r['changed_at']),
                    'changedBy' => $r['changed_by'] !== null ? (string) $r['changed_by'] : null,
                    'source' => (string) $r['source'],
                ];
            }
            return $out;
        } catch (Throwable $e) {
            return [];
        }
    }
    $path = kpi_v1_admin_plan_history_path();
    if (!is_file($path)) {
        return [];
    }
    $decoded = json_decode((string) file_get_contents($path), true);
    if (!is_array($decoded)) {
        return [];
    }
    $rows = array_values(array_filter($decoded, function ($r) use ($userId) {
        return is_array($r) && isset($r['userId']) && (string) $r['userId'] === $userId;
    }));
    usort($rows, function ($a, $b) {
        return strcmp((string) ($b['changedAt'] ?? ''), (string) ($a['changedAt'] ?? ''));
    });
    return array_slice($rows, 0, $limit);
}

function kpi_v1_admin_touch_last_login($cfg, $userId)
{
    $userId = (string) $userId;
    $nowIso = gmdate('c');
    if (kpi_v1_storage_is_mysql($cfg)) {
        try {
            $pdo = kpi_v1_db($cfg);
            $st = $pdo->prepare('UPDATE kpi_users SET last_login_at = ?, updated_at = updated_at WHERE user_id = ?');
            $st->execute([gmdate('Y-m-d H:i:s'), $userId]);
        } catch (Throwable $e) {
            // Column may not exist pre-migration.
        }
        return $nowIso;
    }
    $user = kpi_v1_auth_read_user($userId);
    if ($user === null) {
        return null;
    }
    $user['lastLoginAt'] = $nowIso;
    // Preserve updatedAt semantics for file backend: do not bump updatedAt on login.
    $prevUpdated = isset($user['updatedAt']) ? $user['updatedAt'] : null;
    kpi_v1_auth_write_user($user);
    if ($prevUpdated !== null) {
        $user2 = kpi_v1_auth_read_user($userId);
        if (is_array($user2)) {
            $user2['updatedAt'] = $prevUpdated;
            $user2['lastLoginAt'] = $nowIso;
            // rewrite raw file without going through mysql path
            $path = kpi_v1_auth_user_path($userId);
            if ($path) {
                $json = json_encode($user2, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
                if ($json !== false) {
                    file_put_contents($path, $json, LOCK_EX);
                }
            }
        }
    }
    return $nowIso;
}

/**
 * Validate parent link: no self, parent exists, no cycle.
 */
function kpi_v1_admin_validate_parent($cfg, $childUserId, $parentUserId)
{
    $childUserId = (string) $childUserId;
    $parentUserId = $parentUserId !== null && $parentUserId !== '' ? (string) $parentUserId : null;
    if ($parentUserId === null) {
        return true;
    }
    if ($parentUserId === $childUserId) {
        return false;
    }
    $parent = kpi_v1_auth_read_user($parentUserId);
    if ($parent === null) {
        return false;
    }
    // Walk ancestors of parent; reject if child appears.
    $seen = [];
    $cur = $parentUserId;
    $guard = 0;
    while ($cur !== null && $guard < 32) {
        if ($cur === $childUserId) {
            return false;
        }
        if (isset($seen[$cur])) {
            return false;
        }
        $seen[$cur] = true;
        $u = kpi_v1_auth_read_user($cur);
        if ($u === null) {
            break;
        }
        $cur = !empty($u['parentUserId']) ? (string) $u['parentUserId'] : null;
        $guard++;
    }
    return true;
}

function kpi_v1_admin_list_child_ids($cfg, $parentUserId)
{
    $parentUserId = (string) $parentUserId;
    $out = [];
    if (kpi_v1_storage_is_mysql($cfg)) {
        try {
            $pdo = kpi_v1_db($cfg);
            $st = $pdo->prepare('SELECT user_id FROM kpi_users WHERE parent_user_id = ? ORDER BY created_at ASC');
            $st->execute([$parentUserId]);
            foreach ($st->fetchAll(PDO::FETCH_ASSOC) as $r) {
                $out[] = (string) $r['user_id'];
            }
        } catch (Throwable $e) {
            return [];
        }
        return $out;
    }
    $index = kpi_v1_auth_read_email_index();
    foreach ($index as $email => $uid) {
        $u = kpi_v1_auth_read_user($uid);
        if (is_array($u) && !empty($u['parentUserId']) && (string) $u['parentUserId'] === $parentUserId) {
            $out[] = (string) $u['userId'];
        }
    }
    sort($out);
    return $out;
}

function kpi_v1_admin_list_users($cfg)
{
    $users = [];
    if (kpi_v1_storage_is_mysql($cfg)) {
        $pdo = kpi_v1_db($cfg);
        $sql = 'SELECT user_id, email, plan, disabled, created_at, plan_updated_at';
        // optional columns
        try {
            $pdo->query('SELECT role, last_login_at, parent_user_id FROM kpi_users LIMIT 0');
            $sql = 'SELECT user_id, email, plan, disabled, role, created_at, plan_updated_at, last_login_at, parent_user_id';
        } catch (Throwable $e) {
            // pre-migration
        }
        $sql .= ' FROM kpi_users ORDER BY created_at ASC';
        $st = $pdo->query($sql);
        foreach ($st->fetchAll(PDO::FETCH_ASSOC) as $r) {
            $u = [
                'userId' => (string) $r['user_id'],
                'email' => (string) $r['email'],
                'plan' => (string) $r['plan'],
                'disabled' => !empty($r['disabled']),
                'role' => isset($r['role']) ? kpi_v1_auth_normalize_role($r['role']) : 'user',
                'createdAt' => kpi_v1_admin_dt_to_iso($r['created_at'] ?? null),
                'planUpdatedAt' => !empty($r['plan_updated_at']) ? kpi_v1_admin_dt_to_iso($r['plan_updated_at']) : null,
                'lastLoginAt' => !empty($r['last_login_at']) ? kpi_v1_admin_dt_to_iso($r['last_login_at']) : null,
                'parentUserId' => !empty($r['parent_user_id']) ? (string) $r['parent_user_id'] : null,
            ];
            $users[] = $u;
        }
        return $users;
    }
    $index = kpi_v1_auth_read_email_index();
    foreach ($index as $email => $uid) {
        $u = kpi_v1_auth_read_user($uid);
        if (is_array($u)) {
            $safe = kpi_v1_admin_safe_user_row($u);
            if ($safe) {
                $users[] = $safe;
            }
        }
    }
    usort($users, function ($a, $b) {
        return strcmp((string) ($a['createdAt'] ?? ''), (string) ($b['createdAt'] ?? ''));
    });
    return $users;
}

function kpi_v1_admin_dashboard_stats($cfg)
{
    $users = kpi_v1_admin_list_users($cfg);
    $total = count($users);
    $basic = 0;
    $pro = 0;
    $disabled = 0;
    $new7 = 0;
    $new30 = 0;
    $latest = null;
    $now = time();
    foreach ($users as $u) {
        $plan = strtolower((string) ($u['plan'] ?? 'basic'));
        if ($plan === 'basic') {
            $basic++;
        } else {
            $pro++;
        }
        if (!empty($u['disabled'])) {
            $disabled++;
        }
        $created = isset($u['createdAt']) ? strtotime((string) $u['createdAt']) : false;
        if ($created !== false) {
            if ($now - $created <= 7 * 86400) {
                $new7++;
            }
            if ($now - $created <= 30 * 86400) {
                $new30++;
            }
            if ($latest === null || $created > strtotime((string) $latest)) {
                $latest = $u['createdAt'];
            }
        }
    }
    return [
        'totalUsers' => $total,
        'basic' => $basic,
        'pro' => $pro,
        'disabled' => $disabled,
        'newUsers7d' => $new7,
        'newUsers30d' => $new30,
        'latestRegistration' => $latest,
    ];
}

<?php
/**
 * Admin — reset one user's KPN operational data to empty/new-user equivalent.
 * Does not delete kpi_users. Does not touch other users. Does not return secrets.
 */

require_once __DIR__ . '/_admin_actions.php';
require_once __DIR__ . '/_admin_store.php';
require_once __DIR__ . '/_bootstrap.php';

define('KPI_V1_ADMIN_RESET_CONFIRM', 'RESET_KPN_DATA');

/**
 * True when X-KPI-Plan-Admin-Token / body.adminToken matches config.
 */
function kpi_v1_auth_admin_token_matches($cfg, $body = null)
{
    $adminTok = '';
    if (isset($_SERVER['HTTP_X_KPI_PLAN_ADMIN_TOKEN'])) {
        $adminTok = (string) $_SERVER['HTTP_X_KPI_PLAN_ADMIN_TOKEN'];
    } elseif (is_array($body) && isset($body['adminToken'])) {
        $adminTok = (string) $body['adminToken'];
    }
    $expectedAdmin = isset($cfg['planAdminToken']) ? (string) $cfg['planAdminToken'] : '';
    if ($expectedAdmin === '' || $adminTok === '') {
        return false;
    }
    return hash_equals($expectedAdmin, $adminTok);
}

/**
 * Founder session OR planAdminToken. Returns actor user array (token uses synthetic id).
 *
 * @return array
 */
function kpi_v1_admin_reset_require_actor($cfg, $body)
{
    if (kpi_v1_auth_admin_token_matches($cfg, $body)) {
        return [
            'userId' => '__plan_admin_token__',
            'email' => '',
            'role' => 'plan_admin_token',
        ];
    }
    return kpi_v1_auth_require_founder_superadmin($cfg);
}

/**
 * Resolve exactly one target user from email and/or userId.
 * Both present must refer to the same user.
 *
 * @param array $body
 * @return array{ok:true,user:array}|array{ok:false,error:string}
 */
function kpi_v1_admin_reset_resolve_target($body)
{
    if (!is_array($body)) {
        return ['ok' => false, 'error' => 'invalid_json'];
    }
    $hasEmailKey = array_key_exists('email', $body) && $body['email'] !== null && trim((string) $body['email']) !== '';
    $userIdRaw = isset($body['userId']) ? trim((string) $body['userId']) : '';
    $hasId = $userIdRaw !== '';

    if (!$hasEmailKey && !$hasId) {
        return ['ok' => false, 'error' => 'missing_target'];
    }

    $userByEmail = null;
    $userById = null;

    if ($hasEmailKey) {
        $email = kpi_v1_auth_normalize_email($body['email']);
        if ($email === null) {
            return ['ok' => false, 'error' => 'invalid_email'];
        }
        $userByEmail = kpi_v1_auth_find_user_by_email($email);
        if ($userByEmail === null || empty($userByEmail['userId'])) {
            return ['ok' => false, 'error' => 'user_not_found'];
        }
    }

    if ($hasId) {
        $loaded = kpi_v1_admin_actions_load_target($userIdRaw);
        if (empty($loaded['ok'])) {
            return $loaded;
        }
        $userById = $loaded['user'];
    }

    if ($userByEmail !== null && $userById !== null) {
        if ((string) $userByEmail['userId'] !== (string) $userById['userId']) {
            return ['ok' => false, 'error' => 'ambiguous_target'];
        }
    }

    return ['ok' => true, 'user' => $userByEmail !== null ? $userByEmail : $userById];
}

/**
 * Wipe kpi_store JSON columns for one user; bump revision when row exists.
 *
 * @param PDO $pdo
 * @return bool true if store reset applied (row updated or inserted)
 */
function kpi_v1_admin_reset_wipe_store_pdo(PDO $pdo, $userId)
{
    $userId = (string) $userId;
    $ts = gmdate('Y-m-d H:i:s');
    $st = $pdo->prepare(
        'UPDATE kpi_store
         SET store_json = NULL, annual_nav_json = NULL, pl_json = NULL,
             updated_at = ?, revision = revision + 1
         WHERE user_id = ?'
    );
    $st->execute([$ts, $userId]);
    if ($st->rowCount() > 0) {
        return true;
    }
    $ins = $pdo->prepare(
        'INSERT INTO kpi_store (user_id, store_json, annual_nav_json, pl_json, updated_at, revision)
         VALUES (?, NULL, NULL, NULL, ?, 1)'
    );
    $ins->execute([$userId, $ts]);
    return true;
}

/**
 * Delete profile row for one user (returns to unsynced empty on next read).
 *
 * @param PDO $pdo
 */
function kpi_v1_admin_reset_wipe_profile_pdo(PDO $pdo, $userId)
{
    $st = $pdo->prepare('DELETE FROM kpi_user_profiles WHERE user_id = ?');
    $st->execute([(string) $userId]);
    return true;
}

/**
 * @param PDO $pdo
 * @return int deleted rows (0 if table missing)
 */
function kpi_v1_admin_reset_delete_daily_inputs_pdo(PDO $pdo, $userId)
{
    try {
        $st = $pdo->prepare('DELETE FROM kpi_daily_inputs WHERE user_id = ?');
        $st->execute([(string) $userId]);
        return (int) $st->rowCount();
    } catch (PDOException $e) {
        if (kpi_v1_db_inputs_table_missing($e)) {
            return 0;
        }
        throw $e;
    }
}

/**
 * @param PDO $pdo
 * @return int deleted rows (0 if table missing)
 */
function kpi_v1_admin_reset_delete_daily_facts_pdo(PDO $pdo, $userId)
{
    try {
        $st = $pdo->prepare('DELETE FROM kpi_daily_facts WHERE user_id = ?');
        $st->execute([(string) $userId]);
        return (int) $st->rowCount();
    } catch (PDOException $e) {
        if (kpi_v1_db_facts_table_missing($e)) {
            return 0;
        }
        throw $e;
    }
}

/**
 * File-backend store wipe for one userId.
 */
function kpi_v1_admin_reset_wipe_store_file($userId)
{
    $path = kpi_v1_data_path($userId);
    $blob = kpi_v1_empty_store_blob($userId);
    $blob->updatedAt = gmdate('c');
    $blob->revision = 1;
    if (is_file($path)) {
        $prev = kpi_v1_read_blob($path);
        if (isset($prev->revision) && $prev->revision !== null && $prev->revision !== '') {
            $blob->revision = ((int) $prev->revision) + 1;
        }
    }
    kpi_v1_write_blob($path, $blob);
    return true;
}

/**
 * File-backend profile wipe.
 */
function kpi_v1_admin_reset_wipe_profile_file($userId)
{
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $userId);
    if ($safe === '') {
        return false;
    }
    $path = kpi_v1_admin_profiles_dir() . '/' . $safe . '.json';
    if (is_file($path)) {
        @unlink($path);
    }
    return true;
}

/**
 * Reset one user's KPN data. Preserves kpi_users + kpi_plan_history.
 *
 * @param array $cfg
 * @param array $actor
 * @param array $targetUser
 * @return array{ok:true,userId:string,email:string,reset:array,sessionEpoch:int}|array{ok:false,error:string}
 */
function kpi_v1_admin_reset_user_kpi($cfg, $actor, $targetUser)
{
    if (!is_array($targetUser) || empty($targetUser['userId'])) {
        return ['ok' => false, 'error' => 'user_not_found'];
    }
    $userId = (string) $targetUser['userId'];
    $selfErr = kpi_v1_admin_actions_self_target_error($actor, $userId);
    if ($selfErr !== null) {
        return ['ok' => false, 'error' => $selfErr];
    }

    $reset = [
        'store' => false,
        'profile' => false,
        'dailyInputs' => false,
        'dailyFacts' => false,
        'sessionRevoked' => false,
    ];
    $deletedInputs = 0;
    $deletedFacts = 0;

    if (kpi_v1_storage_is_mysql($cfg)) {
        $pdo = kpi_v1_db($cfg);
        try {
            $pdo->beginTransaction();
            kpi_v1_admin_reset_wipe_store_pdo($pdo, $userId);
            $reset['store'] = true;
            kpi_v1_admin_reset_wipe_profile_pdo($pdo, $userId);
            $reset['profile'] = true;
            $deletedInputs = kpi_v1_admin_reset_delete_daily_inputs_pdo($pdo, $userId);
            $reset['dailyInputs'] = true;
            $deletedFacts = kpi_v1_admin_reset_delete_daily_facts_pdo($pdo, $userId);
            $reset['dailyFacts'] = true;
            $pdo->commit();
        } catch (Throwable $e) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            return ['ok' => false, 'error' => 'reset_failed'];
        }
    } else {
        try {
            kpi_v1_admin_reset_wipe_store_file($userId);
            $reset['store'] = true;
            kpi_v1_admin_reset_wipe_profile_file($userId);
            $reset['profile'] = true;
            /* daily_* tables are MySQL-only in this codebase */
            $reset['dailyInputs'] = true;
            $reset['dailyFacts'] = true;
        } catch (Throwable $e) {
            return ['ok' => false, 'error' => 'reset_failed'];
        }
    }

    $epoch = kpi_v1_session_revoke_bump($userId);
    if ($epoch === null) {
        return ['ok' => false, 'error' => 'revoke_failed'];
    }
    $reset['sessionRevoked'] = true;

    return [
        'ok' => true,
        'userId' => $userId,
        'email' => isset($targetUser['email']) ? (string) $targetUser['email'] : '',
        'reset' => $reset,
        'sessionEpoch' => $epoch,
        'deletedDailyInputs' => $deletedInputs,
        'deletedDailyFacts' => $deletedFacts,
    ];
}

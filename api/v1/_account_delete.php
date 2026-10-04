<?php
/**
 * Self-service account deletion (BR-LAUNCH-09 Phase 3).
 *
 * Contract (frozen 2026-09-28):
 * - Only role `user` may delete itself; privileged roles are rejected here, not only in the UI.
 * - Accounts with child accounts are rejected; children are never cascaded or re-parented.
 * - MySQL: deleting the kpi_users row removes store / daily facts / daily inputs / plan history /
 *   profile / reset tokens / consents through the existing ON DELETE CASCADE foreign keys.
 * - The session revoke file is bumped and kept: removing it would reset the epoch to 0 and
 *   let stale sessions of the (random, never reused) userId pass the epoch check again.
 * - Feedback left by the user is anonymized (message, sent time and category kept; identifiers, plan and page stripped).
 * - A minimal lifecycle history row (_lifecycle.php) is written together with the account delete: in MySQL inside the
 *   same transaction, so a history row exists exactly when the account row was deleted. No HMAC key / history
 *   tables = nothing is deleted (fail closed).
 * - A marketing subscription (_marketing.php) is settled in the same unit: subscribed = the user must choose
 *   keep (email kept for news only, account link removed) or stop; otherwise nothing is deleted. Never turned on here.
 */

require_once __DIR__ . '/_registration.php';
require_once __DIR__ . '/_session_revoke.php';
require_once __DIR__ . '/_email_change.php';
require_once __DIR__ . '/_admin_store.php';
require_once __DIR__ . '/_lifecycle.php';

const KPI_ACCOUNT_DELETE_INTENT_TTL = 600;
const KPI_ACCOUNT_DELETE_MAX_PASSWORD_FAILURES = 5;
const KPI_ACCOUNT_DELETE_FAILURE_LOCK_SECONDS = 900;

function kpi_v1_account_delete_password_fingerprint($passwordHash)
{
    return hash('sha256', 'kpn-account-delete|' . (string) $passwordHash);
}

/** @return string|null error code when this user may not delete itself */
function kpi_v1_account_delete_reject_reason($cfg, $user)
{
    $role = isset($user['role']) ? (string) $user['role'] : 'user';
    if ($role !== 'user') {
        return 'protected_account';
    }
    if (kpi_v1_account_delete_has_children($cfg, (string) $user['userId'])) {
        return 'has_child_accounts';
    }
    return null;
}

/** Fails closed: a lookup error counts as "has children". */
function kpi_v1_account_delete_has_children($cfg, $userId, $pdo = null)
{
    $userId = (string) $userId;
    if (kpi_v1_storage_is_mysql($cfg)) {
        try {
            $pdo = $pdo instanceof PDO ? $pdo : kpi_v1_db($cfg);
            $st = $pdo->prepare('SELECT 1 FROM kpi_users WHERE parent_user_id = ? LIMIT 1');
            $st->execute([$userId]);
            return $st->fetchColumn() !== false;
        } catch (Throwable $e) {
            return true;
        }
    }
    return kpi_v1_admin_list_child_ids($cfg, $userId) !== [];
}

/** @return int seconds until password attempts are allowed again (0 = allowed) */
function kpi_v1_account_delete_failure_wait($userId)
{
    $row = isset($_SESSION['kpi_delete_pw_fail']) && is_array($_SESSION['kpi_delete_pw_fail'])
        ? $_SESSION['kpi_delete_pw_fail'] : null;
    if ($row === null || (string) ($row['userId'] ?? '') !== (string) $userId) {
        return 0;
    }
    $until = (int) ($row['lockedUntil'] ?? 0);
    return $until > time() ? $until - time() : 0;
}

function kpi_v1_account_delete_record_failure($userId)
{
    $row = isset($_SESSION['kpi_delete_pw_fail']) && is_array($_SESSION['kpi_delete_pw_fail'])
        ? $_SESSION['kpi_delete_pw_fail'] : null;
    if ($row === null || (string) ($row['userId'] ?? '') !== (string) $userId) {
        $row = ['userId' => (string) $userId, 'count' => 0, 'lockedUntil' => 0];
    }
    $row['count'] = (int) $row['count'] + 1;
    if ($row['count'] >= KPI_ACCOUNT_DELETE_MAX_PASSWORD_FAILURES) {
        $row['count'] = 0;
        $row['lockedUntil'] = time() + KPI_ACCOUNT_DELETE_FAILURE_LOCK_SECONDS;
    }
    $_SESSION['kpi_delete_pw_fail'] = $row;
}

function kpi_v1_account_delete_issue_intent($user)
{
    unset($_SESSION['kpi_delete_pw_fail']);
    $_SESSION['kpi_delete_intent'] = [
        'userId' => (string) $user['userId'],
        'email' => (string) $user['email'],
        'passwordFingerprint' => kpi_v1_account_delete_password_fingerprint($user['passwordHash']),
        'revokeEpoch' => kpi_v1_session_revoke_get_epoch($user['userId']),
        'expiresAt' => time() + KPI_ACCOUNT_DELETE_INTENT_TTL,
    ];
}

/** Intent must belong to this user and still match email, password and revoke epoch. */
function kpi_v1_account_delete_intent_valid($user)
{
    $intent = isset($_SESSION['kpi_delete_intent']) && is_array($_SESSION['kpi_delete_intent'])
        ? $_SESSION['kpi_delete_intent'] : null;
    if ($intent === null || (int) ($intent['expiresAt'] ?? 0) < time()) {
        return false;
    }
    return hash_equals((string) $user['userId'], (string) ($intent['userId'] ?? ''))
        && hash_equals((string) $user['email'], (string) ($intent['email'] ?? ''))
        && hash_equals(
            kpi_v1_account_delete_password_fingerprint($user['passwordHash']),
            (string) ($intent['passwordFingerprint'] ?? '')
        )
        && (int) ($intent['revokeEpoch'] ?? -1) === kpi_v1_session_revoke_get_epoch($user['userId']);
}

/** Lifecycle history must be recordable and every directory the post-delete cleanup writes to must be writable. */
function kpi_v1_account_delete_preflight($cfg)
{
    if (!kpi_v1_lifecycle_ready($cfg)) {
        error_log('kpn account delete: lifecycle history not ready (HMAC key or history storage missing)');
        return false;
    }
    $dirs = [
        kpi_v1_session_revoke_dir(),
        kpi_v1_email_change_dir(),
        kpi_v1_password_reset_dir(),
        kpi_v1_registration_dir(),
    ];
    foreach (['/data/feedback', '/data/profiles', '/data/consents', '/data/backups'] as $rel) {
        if (is_dir(__DIR__ . $rel)) {
            $dirs[] = __DIR__ . $rel;
        }
    }
    foreach ($dirs as $dir) {
        if (!is_dir($dir) || !is_writable($dir)) {
            return false;
        }
    }
    return true;
}

/**
 * Remove the canonical user record and write its lifecycle history row; settle a marketing subscription
 * ($marketingChoice keep | stop, required only while subscribed) in the same unit.
 * Nothing is deleted (and no history row remains) when this returns anything but 'ok'.
 * @param string|null $lifecycleId set to the history row id on 'ok'
 * @return string ok | gone | stale | has_child_accounts | marketing_choice_required | failed
 */
function kpi_v1_account_delete_user_record($cfg, $user, &$lifecycleId = null, $marketingChoice = null)
{
    $userId = (string) $user['userId'];
    $lifecycleId = null;
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        try {
            $pdo = kpi_v1_db($cfg);
            $pdo->beginTransaction();
            $st = $pdo->prepare(
                'SELECT email, password_hash, role, plan, created_at, parent_user_id FROM kpi_users WHERE user_id = ? LIMIT 1 FOR UPDATE'
            );
            $st->execute([$userId]);
            $row = $st->fetch(PDO::FETCH_ASSOC);
            if (!$row) {
                $pdo->rollBack();
                return 'gone';
            }
            if (!hash_equals((string) $user['email'], (string) $row['email'])
                || !hash_equals((string) $user['passwordHash'], (string) $row['password_hash'])
                || (string) ($row['role'] ?? 'user') !== 'user') {
                $pdo->rollBack();
                return 'stale';
            }
            if (kpi_v1_account_delete_has_children($cfg, $userId, $pdo)) {
                $pdo->rollBack();
                return 'has_child_accounts';
            }
            $mkt = kpi_v1_marketing_run($cfg, function ($ctx) use ($row, $marketingChoice) {
                return kpi_v1_marketing_op_account_deleted($ctx, (string) $row['email'], $marketingChoice);
            }, $pdo);
            if ($mkt[0] === 'ok' && $mkt[1] === 'choice_required') {
                $pdo->rollBack();
                return 'marketing_choice_required';
            }
            $record = kpi_v1_lifecycle_build_record($cfg, [
                'userId' => $userId,
                'email' => (string) $row['email'],
                'plan' => (string) $row['plan'],
                'role' => (string) $row['role'],
                'createdAt' => (string) $row['created_at'],
                'parentUserId' => $row['parent_user_id'],
            ], kpi_v1_lifecycle_db_origin($pdo, $userId), kpi_v1_lifecycle_segment($cfg, $userId));
            if ($record === null) {
                $pdo->rollBack();
                return 'failed';
            }
            kpi_v1_lifecycle_db_insert($pdo, $record);
            $del = $pdo->prepare('DELETE FROM kpi_users WHERE user_id = ? LIMIT 1');
            $del->execute([$userId]);
            if ($del->rowCount() !== 1) {
                $pdo->rollBack();
                return 'failed';
            }
            $pdo->commit();
            $lifecycleId = $record['lifecycleId'];
            return 'ok';
        } catch (Throwable $e) {
            if (isset($pdo) && $pdo instanceof PDO && $pdo->inTransaction()) {
                $pdo->rollBack();
            }
            return 'failed';
        }
    }

    $userPath = kpi_v1_auth_user_path($userId);
    $fresh = kpi_v1_auth_read_user($userId);
    if ($userPath === null || $fresh === null) {
        return 'gone';
    }
    if (!hash_equals((string) $user['email'], (string) ($fresh['email'] ?? ''))
        || !hash_equals((string) $user['passwordHash'], (string) ($fresh['passwordHash'] ?? ''))) {
        return 'stale';
    }
    if (kpi_v1_account_delete_has_children($cfg, $userId)) {
        return 'has_child_accounts';
    }
    $record = kpi_v1_lifecycle_build_record($cfg, $fresh, kpi_v1_lifecycle_file_origin($userId), kpi_v1_lifecycle_segment($cfg, $userId));
    if ($record === null) {
        return 'failed';
    }
    $marketingSnap = kpi_v1_marketing_file_snapshot();
    $mkt = kpi_v1_marketing_run($cfg, function ($ctx) use ($fresh, $marketingChoice) {
        return kpi_v1_marketing_op_account_deleted($ctx, (string) $fresh['email'], $marketingChoice);
    });
    if ($mkt[0] !== 'ok') {
        return 'failed';
    }
    if ($mkt[1] === 'choice_required') {
        return 'marketing_choice_required';
    }
    if (!kpi_v1_lifecycle_file_insert($record)) {
        kpi_v1_marketing_file_restore($marketingSnap);
        return 'failed';
    }
    $index = kpi_v1_auth_read_email_index();
    $nextIndex = $index;
    foreach ($nextIndex as $email => $uid) {
        if ((string) $uid === $userId) {
            unset($nextIndex[$email]);
        }
    }
    if (!kpi_v1_registration_write_json_atomic(kpi_v1_auth_email_index_path(), $nextIndex)) {
        kpi_v1_lifecycle_file_remove($record['lifecycleId']);
        kpi_v1_marketing_file_restore($marketingSnap);
        return 'failed';
    }
    if (!@unlink($userPath)) {
        kpi_v1_registration_write_json_atomic(kpi_v1_auth_email_index_path(), $index);
        kpi_v1_lifecycle_file_remove($record['lifecycleId']);
        kpi_v1_marketing_file_restore($marketingSnap);
        return 'failed';
    }
    $lifecycleId = $record['lifecycleId'];
    return 'ok';
}

function kpi_v1_account_delete_remove_tree($dir)
{
    if (!is_dir($dir)) {
        return true;
    }
    $ok = true;
    foreach (scandir($dir) ?: [] as $name) {
        if ($name === '.' || $name === '..') {
            continue;
        }
        $path = $dir . '/' . $name;
        $ok = (is_dir($path) ? kpi_v1_account_delete_remove_tree($path) : @unlink($path)) && $ok;
    }
    return @rmdir($dir) && $ok;
}

function kpi_v1_account_delete_unlink($path)
{
    return $path === null || !file_exists($path) || @unlink($path);
}

/**
 * Best-effort cleanup after the user record is gone. Returns names of stores that could not be cleaned.
 * @return string[]
 */
function kpi_v1_account_delete_cleanup_files($cfg, $user)
{
    $userId = (string) $user['userId'];
    $email = strtolower((string) $user['email']);
    $safe = kpi_v1_session_revoke_safe_user_id($userId);
    $failed = [];
    if ($safe === null) {
        return ['invalid_user_id'];
    }
    $data = kpi_v1_file_data_root();

    foreach (['pending', 'sends'] as $kind) {
        if (!kpi_v1_account_delete_unlink(kpi_v1_email_change_path($kind, $userId))) {
            $failed[] = 'email_change';
        }
    }

    foreach (glob(kpi_v1_password_reset_dir() . '/tok_*.json') ?: [] as $path) {
        $row = json_decode((string) @file_get_contents($path), true);
        if (is_array($row) && (string) ($row['userId'] ?? '') === $userId && !@unlink($path)) {
            $failed[] = 'password_reset';
        }
    }

    $fileStores = [
        'store' => $data . '/' . $safe . '.json',
        'profile' => $data . '/profiles/' . $safe . '.json',
        'consent' => $data . '/consents/' . $safe . '.jsonl',
    ];
    foreach ($fileStores as $name => $path) {
        if (!kpi_v1_account_delete_unlink($path)) {
            $failed[] = $name;
        }
    }
    if (!kpi_v1_account_delete_remove_tree($data . '/backups/' . $safe)) {
        $failed[] = 'backups';
    }

    $historyPath = kpi_v1_admin_plan_history_path();
    if (is_file($historyPath)) {
        $rows = json_decode((string) @file_get_contents($historyPath), true);
        if (is_array($rows)) {
            $kept = array_values(array_filter($rows, function ($r) use ($userId) {
                return !is_array($r) || (string) ($r['userId'] ?? '') !== $userId;
            }));
            if (count($kept) !== count($rows) && !kpi_v1_registration_write_json_atomic($historyPath, $kept)) {
                $failed[] = 'plan_history';
            }
        }
    }

    foreach (glob($data . '/feedback/*.json') ?: [] as $path) {
        $row = json_decode((string) @file_get_contents($path), true);
        if (!is_array($row)) {
            continue;
        }
        $mine = (string) ($row['userId'] ?? '') === $userId
            || ($email !== '' && strtolower((string) ($row['sessionEmail'] ?? '')) === $email)
            || ($email !== '' && strtolower((string) ($row['contactEmail'] ?? '')) === $email);
        if (!$mine) {
            continue;
        }
        $row['userId'] = null;
        $row['sessionEmail'] = '';
        $row['contactEmail'] = '';
        $row['userAgent'] = '';
        $row['plan'] = '';
        $row['pageUrl'] = '';
        $row['anonymizedAt'] = gmdate('Y-m-d\TH:i:s\Z');
        if (!kpi_v1_registration_write_json_atomic($path, $row)) {
            $failed[] = 'feedback';
        }
    }

    return array_values(array_unique($failed));
}

/**
 * Runs under the registration lock. Returns [status, payload]; never exits.
 * @return array{0:int,1:array}
 */
function kpi_v1_account_delete_execute_locked($cfg, $userId, $marketingChoice = null)
{
    $user = kpi_v1_auth_read_user($userId);
    if ($user === null || empty($user['passwordHash'])) {
        return [401, ['ok' => false, 'error' => 'unauthorized']];
    }
    if (kpi_v1_auth_user_is_disabled($user)) {
        return [403, ['ok' => false, 'error' => 'account_disabled']];
    }
    $reject = kpi_v1_account_delete_reject_reason($cfg, $user);
    if ($reject !== null) {
        return [$reject === 'protected_account' ? 403 : 409, ['ok' => false, 'error' => $reject]];
    }
    if (!kpi_v1_account_delete_intent_valid($user)) {
        unset($_SESSION['kpi_delete_intent']);
        return [403, ['ok' => false, 'error' => 'delete_intent_required']];
    }
    if (!kpi_v1_account_delete_preflight($cfg)) {
        return [500, ['ok' => false, 'error' => 'delete_failed']];
    }

    $lifecycleId = null;
    $result = kpi_v1_account_delete_user_record($cfg, $user, $lifecycleId, $marketingChoice);
    if ($result === 'marketing_choice_required') {
        return [400, ['ok' => false, 'error' => 'marketing_choice_required']];
    }
    if ($result === 'gone') {
        return [401, ['ok' => false, 'error' => 'unauthorized']];
    }
    if ($result === 'stale') {
        unset($_SESSION['kpi_delete_intent']);
        return [403, ['ok' => false, 'error' => 'delete_intent_required']];
    }
    if ($result === 'has_child_accounts') {
        return [409, ['ok' => false, 'error' => 'has_child_accounts']];
    }
    if ($result !== 'ok') {
        return [500, ['ok' => false, 'error' => 'delete_failed']];
    }

    if (kpi_v1_session_revoke_bump($userId) === null) {
        error_log('kpn account delete: revoke bump failed for ' . $userId);
    }
    $residual = kpi_v1_account_delete_cleanup_files($cfg, $user);
    if ($residual !== []) {
        error_log('kpn account delete: residual files for ' . $userId . ': ' . implode(',', $residual));
    }
    if (!kpi_v1_lifecycle_set_cleanup($cfg, $lifecycleId, $residual)) {
        error_log('kpn account delete: lifecycle cleanup status not recorded for ' . $lifecycleId);
    }
    if (kpi_v1_lifecycle_purge($cfg) === null) {
        error_log('kpn lifecycle: retention purge failed');
    }
    if (kpi_v1_marketing_purge($cfg) === null) {
        error_log('kpn marketing: evidence purge failed');
    }
    return [200, ['ok' => true, 'deleted' => true]];
}

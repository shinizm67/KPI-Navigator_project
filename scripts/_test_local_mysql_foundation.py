# -*- coding: utf-8 -*-
"""BR-LOCAL-VERIFY-01 Phase 3A — local MySQL guard and, when a server is up, runtime.

Does not seed canonical accounts. Does not read config.local.php.
Real MySQL checks run only when 127.0.0.1:3306 accepts the temp config.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "results" / "local-mysql-foundation.json"
SCHEMA = ROOT / "api" / "v1" / "schema.sql"
BOOT = ROOT / "scripts" / "kpn_local_mysql_bootstrap.php"
GUARD = ROOT / "api" / "v1" / "_local_test_guard.php"
BOOTSTRAP_PHP = ROOT / "api" / "v1" / "_bootstrap.php"

EXPECTED_TABLES = [
    "kpi_users",
    "kpi_store",
    "kpi_daily_facts",
    "kpi_daily_inputs",
    "kpi_plan_history",
    "kpi_user_profiles",
    "kpi_password_reset_tokens",
    "kpi_account_deletions",
    "kpi_account_origins",
    "kpi_marketing_subscribers",
    "kpi_marketing_consent_events",
    "kpi_user_consents",
]


def php_bin() -> str:
    for name in ("php", "php.exe"):
        found = shutil.which(name)
        if found:
            return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "kpn-tools" / "php" / "php.exe"
    if local.is_file():
        return str(local)
    return ""


def php_prefix(php: str) -> list[str]:
    ext = Path(php).resolve().parent / "ext"
    dll = ext / "php_pdo_mysql.dll"
    if dll.is_file():
        return [php, f"-d", f"extension_dir={ext}", "-d", "extension=php_pdo_mysql.dll"]
    return [php]


def write_config(path: Path, root: Path, **overrides) -> None:
    data = {
        "localTestMode": True,
        "localDataRoot": root.as_posix(),
        "storageDriver": "file",
        "dbHost": "127.0.0.1",
        "dbPort": 3306,
        "dbName": "",
        "dbUser": "kpn_local_runtime",
        "dbPass": "",
        "dbCharset": "utf8mb4",
        "registrationEnabled": False,
        "allowSelfPlanChange": False,
        "passwordResetBaseUrl": "http://127.0.0.1:9",
        "supportEmail": "local-sink@localhost.test",
        "supportFrom": "local-sink@localhost.test",
        "token": "local-test-token",
        "planAdminToken": "local-test-plan-token",
    }
    data.update(overrides)
    lines = ["<?php", "return ["]
    for key, value in data.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, int):
            rendered = str(value)
        else:
            rendered = "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"
        lines.append(f"    '{key}' => {rendered},")
    lines.append("];")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def runtime_identity_path() -> Path:
    override = os.environ.get("KPN_LOCAL_MYSQL_RUNTIME_CONFIG", "")
    if override:
        return Path(override)
    return Path(os.environ.get("LOCALAPPDATA", "")) / "kpn-tools" / "kpn-local-mysql-runtime.php"


def read_runtime_identity() -> tuple[str, str]:
    text = runtime_identity_path().read_text(encoding="utf-8")
    user = re.search(r"'dbUser'\s*=>\s*'([A-Za-z0-9_]+)'", text)
    password = re.search(r"'dbPass'\s*=>\s*'([A-Za-z0-9]+)'", text)
    if not user or not password:
        raise SystemExit("runtime identity file is missing a user")
    if user.group(1) == "root":
        raise SystemExit("runtime identity must not be the admin account")
    return user.group(1), password.group(1)


def run_php(php: str, code: str, config: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["KPI_V1_CONFIG"] = str(config)
    return subprocess.run(
        php_prefix(php) + ["-r", code],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def expect_refuse(php: str, work: Path, reason: str, **overrides) -> None:
    root = work / reason
    root.mkdir(parents=True, exist_ok=True)
    config = work / f"{reason}.php"
    write_config(config, root, **overrides)
    code = (
        "require 'api/v1/_local_test_guard.php'; "
        "$cfg = require getenv('KPI_V1_CONFIG'); "
        "kpi_v1_local_test_assert($cfg); echo 'UNEXPECTED';"
    )
    result = run_php(php, code, config)
    combined = (result.stderr or "") + (result.stdout or "")
    if result.returncode == 0 or f"local_test_refused:{reason}" not in combined or "UNEXPECTED" in combined:
        raise SystemExit(f"guard {reason} failed: code={result.returncode} out={combined[:500]}")
    if "db_connect_failed" in combined or "PDO" in (result.stdout or ""):
        raise SystemExit(f"guard {reason} touched the database: {combined[:500]}")


def main() -> None:
    php = php_bin()
    if not php:
        raise SystemExit("php not found")
    checks: list[str] = []

    def check(name: str, ok: bool) -> None:
        checks.append(name)
        if not ok:
            raise SystemExit(f"FAIL {name}")

    guard_src = GUARD.read_text(encoding="utf-8")
    check("guard has no PDO", "new PDO" not in guard_src and "kpi_v1_db(" not in guard_src)
    boot_src = BOOTSTRAP_PHP.read_text(encoding="utf-8")
    assert_at = boot_src.find("kpi_v1_local_test_assert")
    return_at = boot_src.find("return $cfg;")
    check("guard runs before config return", assert_at != -1 and return_at != -1 and assert_at < return_at)
    check("bootstrap does not load db before return", "_db.php" not in boot_src[:return_at])
    schema = SCHEMA.read_text(encoding="utf-8")
    check("schema has created index", "idx_kpi_users_created" in schema)
    check("schema has last_login index", "idx_kpi_users_last_login" in schema)

    work = Path(tempfile.mkdtemp(prefix="kpn-p3a-"))
    data_root = work / "data"
    data_root.mkdir()
    try:
        file_cfg = work / "file.php"
        write_config(file_cfg, data_root)
        file_ok = run_php(
            php,
            "require 'api/v1/_local_test_guard.php'; $cfg = require getenv('KPI_V1_CONFIG'); "
            "kpi_v1_local_test_assert($cfg); echo 'GUARD_OK';",
            file_cfg,
        )
        check("file mode accepted", file_ok.returncode == 0 and "GUARD_OK" in (file_ok.stdout or ""))

        expect_refuse(php, work, "db_host", storageDriver="mysql", dbName="kpn_local_test", dbHost="203.0.113.10")
        expect_refuse(php, work, "db_host", storageDriver="mysql", dbName="kpn_local_test", dbHost="mysql.lolipop.jp")
        expect_refuse(php, work, "db_host", storageDriver="mysql", dbName="kpn_local_test", dbHost="")
        expect_refuse(php, work, "db_name", storageDriver="mysql", dbName="")
        expect_refuse(php, work, "db_name", storageDriver="mysql", dbName="kpn_production")
        expect_refuse(php, work, "db_name", storageDriver="mysql", dbName="kpn_local_test_extra")
        expect_refuse(php, work, "db_name", storageDriver="mysql", dbName="kpn_local_test;drop")
        expect_refuse(php, work, "storage_driver", storageDriver="sqlite", dbName="kpn_local_test")
        checks.extend(
            [
                "remote host rejected",
                "production host rejected",
                "empty mysql host rejected",
                "empty db name rejected",
                "wrong db name rejected",
                "db name substring rejected",
                "unsafe db name rejected",
                "unknown driver rejected",
            ]
        )

        good = work / "good.php"
        write_config(
            good,
            data_root,
            storageDriver="mysql",
            dbHost="127.0.0.1",
            dbName="kpn_local_test",
        )
        passed = run_php(
            php,
            "require 'api/v1/_local_test_guard.php'; $cfg = require getenv('KPI_V1_CONFIG'); "
            "kpi_v1_local_test_assert($cfg); echo 'GUARD_OK';",
            good,
        )
        check(
            "canonical mysql guard passes without connecting",
            passed.returncode == 0 and (passed.stdout or "").strip() == "GUARD_OK",
        )

        report = {
            "phase": "BR-LOCAL-VERIFY-01 Phase 3A",
            "codeVerified": True,
            "realMysqlVerified": False,
            "checks": checks,
            "php": php,
        }

        probe = run_php(
            php,
            "require 'scripts/kpn_local_mysql_bootstrap.php'; "
            "$cfg = kpi_v1_load_config(); "
            "$pdo = kpi_v1_db_open(kpn_local_mysql_admin_cfg($cfg), false); "
            "echo 'CONNECTED';",
            good,
        )
        connected = "CONNECTED" in (probe.stdout or "")
        report["serverProbe"] = "connected" if connected else "unavailable"
        if not connected:
            OUT.parent.mkdir(parents=True, exist_ok=True)
            OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"ok": True, "codeVerified": True, "realMysqlVerified": False}))
            return

        env = os.environ.copy()
        env["KPI_V1_CONFIG"] = str(good)
        boot = subprocess.run(
            php_prefix(php) + [str(BOOT), "recreate"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        check("schema recreate", boot.returncode == 0 and "bootstrapped kpn_local_test" in (boot.stdout or ""))
        runtime_user, runtime_pass = read_runtime_identity()
        check("runtime identity is dedicated", runtime_user == "kpn_local_runtime")
        write_config(
            good,
            data_root,
            storageDriver="mysql",
            dbHost="127.0.0.1",
            dbName="kpn_local_test",
            dbUser=runtime_user,
            dbPass=runtime_pass,
        )

        runtime_code = r"""
require 'api/v1/_db.php';
$cfg = kpi_v1_load_config();
if (!isset($cfg['dbUser']) || $cfg['dbUser'] !== 'kpn_local_runtime') { fwrite(STDERR, "runtime-user\n"); exit(1); }
$pdo = kpi_v1_db_open($cfg, true);
$who = $pdo->query('SELECT CURRENT_USER() AS u')->fetch();
if (stripos((string) ($who['u'] ?? ''), 'kpn_local_runtime@') !== 0) { fwrite(STDERR, "current-user\n"); exit(1); }
$tz = $pdo->query('SELECT @@session.time_zone AS tz, @@character_set_connection AS cs, DATABASE() AS db')->fetch();
if (($tz['db'] ?? '') !== 'kpn_local_test') { fwrite(STDERR, "db\n"); exit(1); }
if (($tz['tz'] ?? '') !== '+00:00') { fwrite(STDERR, "tz\n"); exit(1); }
if (stripos((string) ($tz['cs'] ?? ''), 'utf8mb4') === false) { fwrite(STDERR, "cs\n"); exit(1); }
$tables = $pdo->query('SHOW TABLES')->fetchAll(PDO::FETCH_NUM);
$names = array_map(function ($row) { return $row[0]; }, $tables);
$need = %s;
foreach ($need as $t) { if (!in_array($t, $names, true)) { fwrite(STDERR, "table:$t\n"); exit(1); } }
$idx = $pdo->query("SHOW INDEX FROM kpi_users WHERE Key_name IN ('idx_kpi_users_created','idx_kpi_users_last_login')")->fetchAll();
$keys = [];
foreach ($idx as $row) { $keys[$row['Key_name']] = true; }
if (empty($keys['idx_kpi_users_created']) || empty($keys['idx_kpi_users_last_login'])) { fwrite(STDERR, "index\n"); exit(1); }
$fk = $pdo->query("SELECT CONSTRAINT_NAME, DELETE_RULE FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = 'kpn_local_test' AND CONSTRAINT_NAME = 'fk_kpi_store_user'")->fetch();
if (!$fk || ($fk['DELETE_RULE'] ?? '') !== 'CASCADE') { fwrite(STDERR, "fk\n"); exit(1); }
$uid = 'p3a_disp_01';
$pdo->prepare('DELETE FROM kpi_users WHERE user_id = ?')->execute([$uid]);
$pdo->prepare('INSERT INTO kpi_users (user_id, email, password_hash, plan, created_at, updated_at) VALUES (?,?,?,?,?,?)')
    ->execute([$uid, 'p3a-disp@localhost.test', 'hash', 'basic', '2026-10-03 03:00:00', '2026-10-03 03:00:00']);
$row = $pdo->prepare('SELECT email FROM kpi_users WHERE user_id = ?');
$row->execute([$uid]);
if (($row->fetch()['email'] ?? '') !== 'p3a-disp@localhost.test') { fwrite(STDERR, "select\n"); exit(1); }
$pdo->prepare('UPDATE kpi_users SET email = ? WHERE user_id = ?')->execute(['p3a-upd@localhost.test', $uid]);
$row->execute([$uid]);
if (($row->fetch()['email'] ?? '') !== 'p3a-upd@localhost.test') { fwrite(STDERR, "update\n"); exit(1); }
$pdo->beginTransaction();
$pdo->prepare('UPDATE kpi_users SET email = ? WHERE user_id = ?')->execute(['p3a-roll@localhost.test', $uid]);
$pdo->rollBack();
$row->execute([$uid]);
if (($row->fetch()['email'] ?? '') !== 'p3a-upd@localhost.test') { fwrite(STDERR, "rollback\n"); exit(1); }
$pdo->beginTransaction();
$pdo->prepare('UPDATE kpi_users SET email = ? WHERE user_id = ?')->execute(['p3a-commit@localhost.test', $uid]);
$pdo->commit();
$row->execute([$uid]);
if (($row->fetch()['email'] ?? '') !== 'p3a-commit@localhost.test') { fwrite(STDERR, "commit\n"); exit(1); }
$fkFail = false;
try {
    $pdo->prepare('INSERT INTO kpi_store (user_id, updated_at, revision) VALUES (?, ?, 1)')->execute(['p3a_missing', '2026-10-03 03:00:00']);
} catch (PDOException $e) { $fkFail = true; }
if (!$fkFail) { fwrite(STDERR, "fk-insert\n"); exit(1); }
$pdo->prepare('INSERT INTO kpi_user_profiles (user_id, updated_at) VALUES (?, ?)')->execute([$uid, '2026-10-03 03:00:00']);
$pdo->prepare('DELETE FROM kpi_users WHERE user_id = ?')->execute([$uid]);
$left = $pdo->prepare('SELECT COUNT(*) AS n FROM kpi_user_profiles WHERE user_id = ?');
$left->execute([$uid]);
if ((int) ($left->fetch()['n'] ?? 1) !== 0) { fwrite(STDERR, "cascade\n"); exit(1); }
$gone = $pdo->prepare('SELECT user_id FROM kpi_users WHERE user_id = ?');
$gone->execute([$uid]);
if ($gone->fetch()) { fwrite(STDERR, "delete\n"); exit(1); }
$grants = $pdo->query('SHOW GRANTS FOR CURRENT_USER()')->fetchAll(PDO::FETCH_NUM);
$privs = array();
foreach ($grants as $g) {
    $line = preg_replace("/IDENTIFIED\\s+BY\\s+PASSWORD\\s+'[^']*'/i", '', (string) $g[0]);
    $line = preg_replace("/IDENTIFIED\\s+BY\\s+'[^']*'/i", '', $line);
    if (!preg_match('/GRANT\\s+(.+?)\\s+ON\\s+(\\S+)/i', $line, $m)) { continue; }
    $on = str_replace('`', '', $m[2]);
    $list = array_map(function ($p) { return strtoupper(trim($p)); }, explode(',', $m[1]));
    if ($on === '*.*') {
        if ($list !== array('USAGE')) { fwrite(STDERR, "global-grant\n"); exit(1); }
        continue;
    }
    if ($on !== 'kpn_local_test.*') { fwrite(STDERR, "other-grant\n"); exit(1); }
    foreach ($list as $p) { $privs[$p] = true; }
}
$expect = array('SELECT', 'INSERT', 'UPDATE', 'DELETE');
foreach ($expect as $p) { if (empty($privs[$p])) { fwrite(STDERR, "missing-priv\n"); exit(1); } }
if (count($privs) !== 4) { fwrite(STDERR, "extra-priv\n"); exit(1); }
$denied = function ($sql) use ($pdo) {
    try { $pdo->exec($sql); return false; } catch (PDOException $e) { return true; }
};
if (!$denied('DROP DATABASE `kpn_local_test`')) { fwrite(STDERR, "drop-db\n"); exit(1); }
$still = $pdo->query('SELECT DATABASE() AS db')->fetch();
if (($still['db'] ?? '') !== 'kpn_local_test') { fwrite(STDERR, "db-gone\n"); exit(1); }
if (!$denied('CREATE DATABASE `kpn_p3a_priv_probe`')) { fwrite(STDERR, "create-db\n"); exit(1); }
$mysqlDenied = false;
try { $pdo->query('SELECT COUNT(*) AS n FROM mysql.user'); }
catch (PDOException $e) { $mysqlDenied = true; }
if (!$mysqlDenied) { fwrite(STDERR, "mysql-db\n"); exit(1); }
echo 'RUNTIME_OK';
""" % json.dumps(EXPECTED_TABLES)
        runtime = run_php(php, runtime_code, good)
        if runtime.returncode != 0 or "RUNTIME_OK" not in (runtime.stdout or ""):
            raise SystemExit(f"runtime failed: {runtime.stderr or runtime.stdout}")
        report["realMysqlVerified"] = True
        report["runtime"] = [
            "connect",
            "timezone",
            "charset",
            "12 tables",
            "indexes",
            "fk cascade rule",
            "insert",
            "select",
            "update",
            "delete",
            "commit",
            "rollback",
            "fk reject",
            "cascade delete",
            "runtime user",
            "privileges select insert update delete",
            "drop database denied",
            "create database denied",
            "mysql database denied",
        ]
        report["runtimeUser"] = runtime_user
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "codeVerified": True, "realMysqlVerified": True, "checks": len(checks)}))
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

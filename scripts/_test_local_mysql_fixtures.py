# -*- coding: utf-8 -*-
"""BR-LOCAL-VERIFY-01 Phase 3B — canonical fixture MySQL parity and a small page smoke."""
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from kpn_local_php import php_bin, php_command

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "fixtures" / "local" / "canonical" / "manifest.json"
FILE_SEED = ROOT / "scripts" / "kpn_local_test_seed.php"
MYSQL_SEED = ROOT / "scripts" / "kpn_local_mysql_seed.php"
OUT = ROOT / "tests" / "results" / "local-mysql-fixtures.json"
MYSQL_IDS = [
    "fx-basic-restaurant-ready",
    "fx-pro-restaurant-ready",
    "fx-pro-hotel-ready",
    "fx-basic-profile-required",
    "fx-basic-setup-required",
]
PAGES = [
    "/app/home/index.html",
    "/app/annual/index.html",
    "/app/monthly/index.html",
    "/setting/profile.html",
]
PROFILE_KEYS = [
    "businessName",
    "companyName",
    "businessType",
    "genre",
    "locale",
    "country",
    "stateRegion",
    "city",
    "currency",
]


def runtime_identity_path() -> Path:
    override = os.environ.get("KPN_LOCAL_MYSQL_RUNTIME_CONFIG", "")
    if override:
        return Path(override)
    return Path(os.environ.get("LOCALAPPDATA", "")) / "kpn-tools" / "kpn-local-mysql-runtime.php"


def read_runtime_identity() -> tuple[str, str]:
    text = runtime_identity_path().read_text(encoding="utf-8")
    user = re.search(r"'dbUser'\s*=>\s*'([A-Za-z0-9_]+)'", text)
    password = re.search(r"'dbPass'\s*=>\s*'([A-Za-z0-9]+)'", text)
    if not user or not password or user.group(1) != "kpn_local_runtime":
        raise SystemExit("runtime identity is not kpn_local_runtime")
    return user.group(1), password.group(1)


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


def run_php(php: list[str], args: list[str], config: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["KPI_V1_CONFIG"] = str(config)
    return subprocess.run(
        php + args,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def instant(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", text):
        text = text.replace(" ", "T") + "+00:00"
    return datetime.fromisoformat(text).astimezone(timezone.utc)


def as_float_map(raw) -> dict:
    if not isinstance(raw, dict):
        return {}
    return {str(k): float(v) for k, v in raw.items()}


def as_bool_map(raw) -> dict:
    if not isinstance(raw, dict):
        return {}
    return {str(k): bool(v) for k, v in raw.items()}


def profile_map(raw) -> dict:
    src = raw or {}
    return {key: src.get(key) or None for key in PROFILE_KEYS}


def business_from_blob(blob: dict, profile: dict, plan: str) -> dict:
    store = blob.get("store") or {}
    meta = store.get("meta") or {}
    setup = meta.get("setup") or {}
    timeline = store.get("timeline") or {}
    years = store.get("years") or {}
    year = years.get("2026") or {}
    plan_row = year.get("plan") or {}
    meal = year.get("dailyMeal") or {}
    income = year.get("dailyIncome") or {}
    daily_exp = year.get("dailyExpenses") or {}
    pl = blob.get("pl") or {}
    month = ((pl.get("expensesByYear") or {}).get("2026") or {})
    return {
        "plan": plan,
        "businessType": meta.get("businessType"),
        "setupComplete": bool(setup.get("complete")),
        "targetSales": plan_row.get("targetSales"),
        "dailySales": as_float_map(timeline.get("dailySales")),
        "businessDays": as_bool_map(timeline.get("businessDays")),
        "lunch": (meal.get("lunch_sales") or {}).get("2026-10-03"),
        "dinner": (meal.get("dinner_sales") or {}).get("2026-10-03"),
        "customers": (meal.get("total_customers") or {}).get("2026-10-03"),
        "groups": (meal.get("total_groups") or {}).get("2026-10-03"),
        "food": (income.get("food_sales") or {}).get("2026-10-03"),
        "drink": (income.get("drink_sales") or {}).get("2026-10-03"),
        "hasMeal": "dailyMeal" in year,
        "hasIncome": "dailyIncome" in year,
        "dailyFoodCost": (daily_exp.get("exp_food_cost") or {}).get("2026-10-03"),
        "dailyLabor": (daily_exp.get("exp_variable_labor") or {}).get("2026-10-03"),
        "rent": month.get("exp_rent:9"),
        "linen": month.get("exp_linen_cleaning:9"),
        "ota": month.get("exp_ota_fees:9"),
        "profile": profile_map(profile),
    }


def file_business(root: Path, account: dict) -> dict:
    user_id = account["userId"]
    user = json.loads((root / "users" / f"{user_id}.json").read_text(encoding="utf-8"))
    profile_path = root / "profiles" / f"{user_id}.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8")) if profile_path.is_file() else {}
    blob = json.loads((root / f"{user_id}.json").read_text(encoding="utf-8"))
    return business_from_blob(blob, profile, user.get("plan"))


def mysql_business(dump: dict, account: dict) -> dict:
    user_id = account["userId"]
    user = next(row for row in dump["users"] if row["user_id"] == user_id)
    profile_row = next((row for row in dump["profiles"] if row["user_id"] == user_id), None)
    profile = {}
    if profile_row:
        profile = {
            "businessName": profile_row["business_name"],
            "companyName": profile_row["company_name"],
            "businessType": profile_row["business_type"],
            "genre": profile_row["genre"],
            "locale": profile_row["locale"],
            "country": profile_row["country"],
            "stateRegion": profile_row["state_region"],
            "city": profile_row["city"],
            "currency": profile_row["currency"],
        }
    store_row = next(row for row in dump["stores"] if row["user_id"] == user_id)
    blob = {
        "store": json.loads(store_row["store_json"]) if store_row["store_json"] else None,
        "annualNav": json.loads(store_row["annual_nav_json"]) if store_row["annual_nav_json"] else None,
        "pl": json.loads(store_row["pl_json"]) if store_row["pl_json"] else None,
    }
    return business_from_blob(blob, profile, user["plan"])


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return int(port)


def wait_http(port: int) -> None:
    url = f"http://127.0.0.1:{port}/api/v1/auth/registration-status.php"
    last = ""
    for _ in range(40):
        try:
            with urllib.request.urlopen(url, timeout=2) as res:
                if res.status == 200:
                    return
        except Exception as exc:
            last = str(exc)
        time.sleep(0.25)
    raise SystemExit(f"php server did not answer: {last}")


def smoke(php: list[str], config: Path, accounts: dict, port: int) -> dict:
    env = os.environ.copy()
    env["KPI_V1_CONFIG"] = str(config)
    server = subprocess.Popen(
        php + ["-S", f"127.0.0.1:{port}", "-t", str(ROOT)],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    production: list[str] = []
    pageerrors: list[str] = []
    ftp_hits: list[str] = []
    try:
        wait_http(port)
        from playwright.sync_api import sync_playwright

        base = f"http://127.0.0.1:{port}"
        pages = []

        def watch(page) -> None:
            def on_request(req) -> None:
                host = (urlparse(req.url).hostname or "").lower()
                if req.url.lower().startswith("ftp:") or "ftp." in host:
                    ftp_hits.append(req.url)
                if host in ("127.0.0.1", "localhost", ""):
                    return
                if "forge-laboratory.com" in host or "lolipop" in host:
                    production.append(req.url)

            def on_error(err) -> None:
                pageerrors.append(str(err))

            page.on("request", on_request)
            page.on("pageerror", on_error)

        def login(page, account) -> None:
            page.goto(base + "/login/index.html", wait_until="domcontentloaded", timeout=60000)
            page.fill("#user-id", account["email"])
            page.fill("#password", account["password"])
            page.click("#btn-login")
            page.wait_for_url("**/app/annual/**", timeout=60000)

        def read_state(page) -> dict:
            return page.evaluate(
                """() => new Promise((resolve) => {
                  const started = Date.now();
                  function snap() {
                    let store = null;
                    try { store = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore') || 'null'); }
                    catch (e) { store = null; }
                    const meta = store && store.meta ? store.meta : {};
                    const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                      || localStorage.getItem('kpiNavigator.subscriptionTier');
                    const sales = store && store.timeline ? store.timeline.dailySales : null;
                    const hydrated = !!(meta.businessType && meta.setup && meta.setup.complete && sales && Object.keys(sales).length);
                    if (hydrated || Date.now() - started > 20000) {
                      resolve({
                        businessType: meta.businessType || null,
                        tier: tier || null,
                        sales: sales && sales['2026-10-03'] != null ? Number(sales['2026-10-03']) : null,
                        setupComplete: !!(meta.setup && meta.setup.complete)
                      });
                      return;
                    }
                    setTimeout(snap, 250);
                  }
                  snap();
                })"""
            )

        def open_page(page, path: str, account) -> None:
            before = len(pageerrors)
            page.goto(base + path, wait_until="domcontentloaded", timeout=90000)
            row = {"path": path, "account": account["id"], "url": page.url}
            if path.endswith("/setting/profile.html"):
                api = page.evaluate(
                    """async () => {
                      const res = await fetch('/api/v1/profile.php', {credentials:'include'});
                      const body = await res.json();
                      return {status: res.status, profile: body.profile || {}};
                    }"""
                )
                row["pass"] = (
                    api["status"] == 200
                    and api["profile"].get("businessName") == account["profile"]["businessName"]
                    and api["profile"].get("businessType") == account["businessType"]
                    and len(pageerrors) == before
                )
            else:
                state = read_state(page)
                expected = account["blob"]["store"]["timeline"]["dailySales"]["2026-10-03"]
                row.update(state)
                row["pass"] = (
                    state["businessType"] == account["businessType"]
                    and state["tier"] == account["plan"]
                    and state["setupComplete"] is True
                    and state["sales"] == expected
                    and path.split("?")[0] in page.url
                    and len(pageerrors) == before
                )
            pages.append(row)
            if not row["pass"]:
                raise SystemExit(f"mysql page failed: {row}")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context()
            page = context.new_page()
            watch(page)
            login(page, accounts["fx-basic-restaurant-ready"])
            for path in PAGES:
                open_page(page, path, accounts["fx-basic-restaurant-ready"])
            context.clear_cookies()
            page.goto(base + "/login/index.html", wait_until="domcontentloaded")
            login(page, accounts["fx-pro-hotel-ready"])
            for path in PAGES:
                open_page(page, path, accounts["fx-pro-hotel-ready"])
            browser.close()
        return {
            "pages": pages,
            "pageerrors": pageerrors,
            "productionRequests": production,
            "ftp": ftp_hits,
        }
    finally:
        server.terminate()


def main() -> None:
    php_path = php_bin()
    if not php_path:
        raise SystemExit("php not found")
    php = php_command(php_path)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    accounts = {row["id"]: row for row in manifest["accounts"]}
    if "fx-legacy-pro" not in accounts or "plan" in accounts["fx-legacy-pro"]:
        raise SystemExit("legacy fixture changed")
    work = Path(tempfile.mkdtemp(prefix="kpn-p3b-"))
    file_root = work / "file"
    mysql_root = work / "mysql-root"
    file_root.mkdir()
    mysql_root.mkdir()
    try:
        file_cfg = work / "file.php"
        write_config(file_cfg, file_root)
        seeded = run_php(php, [str(FILE_SEED)], file_cfg)
        if seeded.returncode != 0 or "seeded" not in (seeded.stdout or ""):
            raise SystemExit(f"file seed failed: {seeded.stderr or seeded.stdout}")

        runtime_user, runtime_pass = read_runtime_identity()
        mysql_cfg = work / "mysql.php"
        write_config(
            mysql_cfg,
            mysql_root,
            storageDriver="mysql",
            dbName="kpn_local_test",
            dbUser=runtime_user,
            dbPass=runtime_pass,
            passwordResetBaseUrl="http://127.0.0.1:9",
        )
        root_cfg = work / "root.php"
        write_config(
            root_cfg,
            mysql_root,
            storageDriver="mysql",
            dbName="kpn_local_test",
            dbUser="root",
            dbPass="nope",
        )
        refused = run_php(php, [str(MYSQL_SEED)], root_cfg)
        if refused.returncode == 0 or "local_test_refused:runtime_user" not in (refused.stderr or ""):
            raise SystemExit(f"root seed was not refused: {refused.stderr or refused.stdout}")

        mysql = run_php(php, [str(MYSQL_SEED)], mysql_cfg)
        if mysql.returncode != 0 or "seeded kpn_local_test 5" not in (mysql.stdout or ""):
            raise SystemExit(f"mysql seed failed: {mysql.stderr or mysql.stdout}")
        first = json.loads(run_php(php, [str(MYSQL_SEED), "dump"], mysql_cfg).stdout)
        if not str(first["runtimeUser"]).startswith("kpn_local_runtime@"):
            raise SystemExit(f"runtime user mismatch: {first['runtimeUser']}")
        if first["timeZone"] != "+00:00" or "utf8mb4" not in first["charset"].lower():
            raise SystemExit("session contract failed")
        if first["database"] != "kpn_local_test" or first["legacyRows"] or first["factRows"] != 0:
            raise SystemExit("legacy or facts were seeded")
        if len(first["users"]) != 5:
            raise SystemExit("expected five mysql users")

        parity = {}
        for fixture_id in MYSQL_IDS:
            account = accounts[fixture_id]
            left = file_business(file_root, account)
            right = mysql_business(first, account)
            if left != right:
                raise SystemExit(f"parity {fixture_id}: file={left} mysql={right}")
            parity[fixture_id] = "match"
            inputs = [row for row in first["inputs"] if row["user_id"] == account["userId"]]
            by_iso = {row["iso"]: row for row in inputs}
            sales = left["dailySales"]
            days = left["businessDays"]
            for iso, amount in sales.items():
                if iso not in by_iso or float(by_iso[iso]["sales"]) != amount:
                    raise SystemExit(f"sales parity {fixture_id} {iso}")
            for iso, flag in days.items():
                raw = by_iso[iso]["business_day"]
                got = None if raw is None else bool(int(raw))
                if got is not flag:
                    raise SystemExit(f"business day parity {fixture_id} {iso}")
            if fixture_id == "fx-pro-hotel-ready" and (right["hasMeal"] or right["hasIncome"]):
                raise SystemExit("hotel has restaurant streams")
            if fixture_id == "fx-basic-profile-required" and any(right["profile"].values()):
                raise SystemExit("profile-required gained fields")

        mutated = run_php(
            php,
            [
                "-r",
                "require 'api/v1/_db.php'; $cfg = kpi_v1_load_config(); $pdo = kpi_v1_db_open($cfg, true); "
                "$pdo->prepare('UPDATE kpi_daily_inputs SET sales = 1 WHERE user_id = ? AND iso = ?')->execute(['localbasicrest','2026-10-03']); "
                "$row = $pdo->query(\"SELECT store_json FROM kpi_store WHERE user_id = 'localbasicrest'\")->fetch(); "
                "$store = json_decode($row['store_json'], true); $store['timeline']['dailySales']['2026-10-03'] = 1; "
                "$pdo->prepare('UPDATE kpi_store SET store_json = ? WHERE user_id = ?')->execute([json_encode($store), 'localbasicrest']); "
                "echo 'mutated';",
            ],
            mysql_cfg,
        )
        if "mutated" not in (mutated.stdout or ""):
            raise SystemExit(f"mutate failed: {mutated.stderr or mutated.stdout}")
        again = run_php(php, [str(MYSQL_SEED)], mysql_cfg)
        if again.returncode != 0:
            raise SystemExit(f"reseed failed: {again.stderr or again.stdout}")
        second = json.loads(run_php(php, [str(MYSQL_SEED), "dump"], mysql_cfg).stdout)
        restored = mysql_business(second, accounts["fx-basic-restaurant-ready"])
        if restored["dailySales"].get("2026-10-03") != 31000:
            raise SystemExit("reseed did not restore sales")

        port = free_port()
        write_config(
            mysql_cfg,
            mysql_root,
            storageDriver="mysql",
            dbName="kpn_local_test",
            dbUser=runtime_user,
            dbPass=runtime_pass,
            passwordResetBaseUrl=f"http://127.0.0.1:{port}",
        )
        viewed = smoke(php, mysql_cfg, accounts, port)
        if viewed["pageerrors"] or viewed["productionRequests"] or viewed["ftp"]:
            raise SystemExit(f"smoke leaked: {viewed}")
        report = {
            "phase": "BR-LOCAL-VERIFY-01 Phase 3B",
            "realMysqlVerified": True,
            "runtimeUser": first["runtimeUser"],
            "parity": parity,
            "reseed": "restored",
            "legacyExcluded": True,
            "pages": [row["path"] + " " + row["account"] for row in viewed["pages"]],
            "pageerrors": viewed["pageerrors"],
            "productionRequests": viewed["productionRequests"],
            "productionDbAccess": 0,
            "ftp": 0,
            "realMail": 0,
            "phpCommandUsesExtensionFlag": any(arg.startswith("-d") for arg in php),
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "ok": True,
            "parity": len(parity),
            "pages": len(viewed["pages"]),
            "pageerrors": 0,
            "productionRequests": 0,
        }))
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""BR-LOCAL-VERIFY-01 Phase 1 — safe local runtime foundation.

Boots php -S on 127.0.0.1 with localTestMode file storage.
Does not read config.local.php and does not call production.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "fixtures" / "local" / "canonical" / "manifest.json"
SEED = ROOT / "scripts" / "kpn_local_test_seed.php"
OUT = ROOT / "tests" / "results" / "local-runtime-foundation.json"
LIVE_DATA = ROOT / "api" / "v1" / "data"

JP_PAGES = [
    ("home", "/app/home/index.html"),
    ("annual", "/app/annual/index.html"),
    ("monthly", "/app/monthly/index.html"),
    ("profile", "/setting/profile.html"),
]
LOCALE_PAGES = {
    "en": [
        "/en/app/home/index.html",
        "/en/app/annual/index.html",
        "/en/app/monthly/index.html",
        "/en/setting/profile.html",
    ],
    "zh-tw": [
        "/zh-tw/app/home/index.html",
        "/zh-tw/app/annual/index.html",
        "/zh-tw/app/monthly/index.html",
        "/zh-tw/setting/profile.html",
    ],
}


def php_bin() -> str:
    for name in ("php", "php.exe"):
        found = shutil.which(name)
        if found:
            return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "kpn-tools" / "php" / "php.exe"
    if local.is_file():
        return str(local)
    return ""


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return int(port)


def write_config(path: Path, root: Path, port: int, **overrides) -> None:
    data = {
        "localTestMode": True,
        "localDataRoot": root.as_posix(),
        "storageDriver": "file",
        "dbHost": "127.0.0.1",
        "dbName": "",
        "dbUser": "",
        "dbPass": "",
        "registrationEnabled": False,
        "allowSelfPlanChange": False,
        "passwordResetBaseUrl": f"http://127.0.0.1:{port}",
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
        else:
            rendered = "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"
        lines.append(f"    '{key}' => {rendered},")
    lines.append("];")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_php(php: str, code: str, config: Path, cwd: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["KPI_V1_CONFIG"] = str(config)
    return subprocess.run(
        [php, "-r", code],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def expect_refuse(php: str, work: Path, port: int, reason: str, **overrides) -> None:
    root = work / reason
    root.mkdir(parents=True, exist_ok=True)
    config = work / f"{reason}.php"
    write_config(config, root, port, **overrides)
    code = "require 'api/v1/_bootstrap.php'; kpi_v1_load_config(); echo 'UNEXPECTED';"
    result = run_php(php, code, config, ROOT)
    combined = (result.stderr or "") + (result.stdout or "")
    if result.returncode == 0 or f"local_test_refused:{reason}" not in combined:
        raise SystemExit(f"guard {reason} failed: code={result.returncode} out={combined[:400]}")


def snapshot_live_users() -> set[str]:
    users = LIVE_DATA / "users"
    if not users.is_dir():
        return set()
    return {p.name for p in users.glob("*.json")}


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


def main() -> None:
    php = php_bin()
    if not php:
        raise SystemExit("php not found")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in manifest["accounts"]}
    aliases = manifest["phase1Aliases"]
    work = Path(tempfile.mkdtemp(prefix="kpn-lv1-"))
    data_root = work / "data"
    data_root.mkdir()
    port = free_port()
    config = work / "config.php"
    write_config(config, data_root, port)
    before_users = snapshot_live_users()
    report: dict = {
        "phase": "BR-LOCAL-VERIFY-01 Phase 1",
        "fullReleaseCheck": False,
        "humanSmoke": False,
        "php": php,
        "port": port,
        "dataRoot": str(data_root),
        "guards": {},
        "pages": [],
        "productionRequests": [],
        "externalHosts": [],
        "pageerrors": [],
    }
    try:
        example = run_php(
            php,
            "echo 'skip';",
            config,
            ROOT,
        )
        del example
        bare = subprocess.run(
            [php, "-r", "var_export(require 'api/v1/config.example.php');"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        if "'localTestMode' => false" not in bare.stdout:
            raise SystemExit("config.example.php localTestMode is not false")
        report["guards"]["example_off"] = True

        expect_refuse(php, work, port, "db_host", dbHost="mysql.lolipop.jp")
        expect_refuse(php, work, port, "ftp_host", ftpHost="ftp.lolipop.jp")
        expect_refuse(php, work, port, "ftp_credential", ftpUser="someone")
        expect_refuse(
            php,
            work,
            port,
            "reset_url",
            passwordResetBaseUrl="https://forge-laboratory.com/kpi-navigator",
        )
        expect_refuse(php, work, port, "mail_address", supportEmail="support@forge-laboratory.com")
        expect_refuse(php, work, port, "db_name", storageDriver="mysql")
        report["guards"]["refuse"] = [
            "db_host",
            "ftp_host",
            "ftp_credential",
            "reset_url",
            "mail_address",
            "db_name",
        ]

        mail = run_php(
            php,
            "require 'api/v1/_mail.php'; $cfg = kpi_v1_load_config(); "
            "$ok = kpi_v1_mail_send($cfg, 'local-sink@localhost.test', 'local', 'blocked'); "
            "echo $ok ? 'sent' : 'blocked';",
            config,
            ROOT,
        )
        if "blocked" not in (mail.stdout or "") or (data_root / "mail-blocked.log").is_file() is False:
            raise SystemExit(f"mail block failed: {mail.stdout} {mail.stderr}")
        report["guards"]["mail_blocked"] = True

        env = os.environ.copy()
        env["KPI_V1_CONFIG"] = str(config)
        seed = subprocess.run(
            [php, str(SEED)],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if seed.returncode != 0 or "seeded" not in (seed.stdout or ""):
            raise SystemExit(f"seed failed: {seed.stderr or seed.stdout}")
        report["seed"] = "ok"
        leaked = snapshot_live_users() - before_users
        if leaked:
            raise SystemExit(f"live data dir changed: {sorted(leaked)}")
        report["liveDataUntouched"] = True

        server = subprocess.Popen(
            [php, "-S", f"127.0.0.1:{port}", "-t", str(ROOT)],
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            wait_http(port)
            from playwright.sync_api import sync_playwright

            base = f"http://127.0.0.1:{port}"
            production_hits: list[str] = []
            external_hosts: set[str] = set()
            pageerrors: list[str] = []

            def watch(page) -> None:
                def on_request(req) -> None:
                    host = (urlparse(req.url).hostname or "").lower()
                    if host in ("127.0.0.1", "localhost", ""):
                        return
                    if "forge-laboratory.com" in host or "lolipop" in host:
                        production_hits.append(req.url)
                        return
                    external_hosts.add(host)

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
                        const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                          || localStorage.getItem('kpiNavigator.subscriptionTier');
                        const meta = store && store.meta ? store.meta : {};
                        const sales = store && store.timeline ? store.timeline.dailySales : null;
                        const hydrated = !!(meta.businessType && meta.setup && meta.setup.complete && sales && Object.keys(sales).length);
                        if (hydrated || Date.now() - started > 20000) {
                          resolve({
                            businessType: meta.businessType || null,
                            tier: tier || null,
                            sales: sales || null,
                            setupComplete: !!(meta.setup && meta.setup.complete)
                          });
                          return;
                        }
                        setTimeout(snap, 250);
                      }
                      snap();
                    })"""
                )

            def open_page(page, path: str, account, functional: bool) -> dict:
                errors_before = len(pageerrors)
                page.goto(base + path, wait_until="domcontentloaded", timeout=90000)
                page.wait_for_timeout(500)
                row = {
                    "path": path,
                    "account": account["id"],
                    "finalUrl": page.url,
                    "functional": functional,
                    "stayed": path.split("?")[0] in page.url.split("?")[0],
                }
                if functional and "profile" not in path:
                    state = read_state(page)
                    row.update(state)
                    row["pass"] = (
                        state["businessType"] == account["businessType"]
                        and state["tier"] == account["plan"]
                        and state["setupComplete"] is True
                        and len(pageerrors) == errors_before
                        and row["stayed"]
                    )
                    row["homeHydrated"] = row["stayed"] and path.endswith("/app/home/index.html")
                elif functional and path.endswith("/setting/profile.html"):
                    api = page.evaluate(
                        """async () => {
                          const res = await fetch('/api/v1/profile.php', {credentials:'include'});
                          const body = await res.json();
                          return {status: res.status, body: body};
                        }"""
                    )
                    profile = (api.get("body") or {}).get("profile") or {}
                    page.evaluate(
                        """(profile) => {
                          localStorage.setItem('kpi-profile-last', JSON.stringify({
                            businessName: profile.businessName || '',
                            company: profile.companyName || '',
                            businessType: profile.businessType || ''
                          }));
                        }""",
                        profile,
                    )
                    page.goto(base + path, wait_until="domcontentloaded", timeout=60000)
                    shown = ""
                    try:
                        page.wait_for_selector("#fixed-business-name", timeout=10000)
                        shown = page.locator("#fixed-business-name").inner_text().strip()
                    except Exception:
                        shown = ""
                    row["profileStatus"] = api.get("status")
                    row["profileBusinessType"] = profile.get("businessType")
                    row["profileName"] = profile.get("businessName")
                    row["shownName"] = shown
                    row["finalUrl"] = page.url
                    row["pass"] = (
                        api.get("status") == 200
                        and profile.get("businessType") == account["businessType"]
                        and profile.get("businessName") == account["profile"]["businessName"]
                        and shown == account["profile"]["businessName"]
                        and len(pageerrors) == errors_before
                    )
                else:
                    tier = page.evaluate(
                        """() => sessionStorage.getItem('kpiNavigator.subscriptionTier')
                          || localStorage.getItem('kpiNavigator.subscriptionTier')
                          || ''"""
                    )
                    row["tier"] = tier
                    row["pass"] = (
                        len(pageerrors) == errors_before
                        and page.url.startswith(base)
                        and row["stayed"]
                        and tier == account["plan"]
                    )
                if path.endswith("/setting/profile.html") and not functional:
                    row["pass"] = (
                        len(pageerrors) == errors_before
                        and "profile" in page.url
                        and row.get("tier") == account["plan"]
                    )
                report["pages"].append(row)
                if not row["pass"]:
                    raise SystemExit(f"page failed: {row}")
                return row

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
                context = browser.new_context()
                page = context.new_page()
                watch(page)
                basic = by_id[aliases["LOCAL_BASIC"]]
                pro = by_id[aliases["LOCAL_PRO"]]
                login(page, basic)
                for _name, path in JP_PAGES:
                    open_page(page, path, basic, True)
                for path in LOCALE_PAGES["en"] + LOCALE_PAGES["zh-tw"]:
                    open_page(page, path, basic, False)
                context.clear_cookies()
                page.goto(base + "/login/index.html", wait_until="domcontentloaded")
                login(page, pro)
                for _name, path in JP_PAGES:
                    open_page(page, path, pro, True)
                browser.close()

            report["productionRequests"] = production_hits
            report["externalHosts"] = sorted(external_hosts)
            report["pageerrors"] = pageerrors
            if production_hits or pageerrors:
                raise SystemExit("production request or pageerror")
            after_users = snapshot_live_users()
            if after_users - before_users:
                raise SystemExit("live users appeared during browse")
            report["ok"] = True
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except Exception:
                server.kill()
    finally:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({"ok": report.get("ok"), "pages": len(report["pages"]), "pageerrors": report["pageerrors"], "productionRequests": report["productionRequests"], "externalHosts": report["externalHosts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

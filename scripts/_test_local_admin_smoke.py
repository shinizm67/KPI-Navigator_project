"""BR-LOCAL-VERIFY-01 Phase 4B. Local Founder page smoke, outside the 122 contract."""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMOKE_PATH = ROOT / "scripts" / "_test_local_full_page_smoke.py"
RESULT = ROOT / "tests" / "results" / "local-admin-smoke.json"

FOUNDER = {
    "userId": "localfounder1",
    "email": "local-founder-admin@localhost.test",
    "password": "Local-Founder-1",
    "plan": "basic",
}
VIEWED_USER = "localbasicrest"
ADMIN_CASES = [
    {
        "id": "admin-home",
        "route": "/admin/index.php",
        "page": "dashboard",
        "marker": "#dash-cards .card",
        "text": "KPN Founder Console",
    },
    {
        "id": "admin-users",
        "route": "/admin/users/index.php",
        "page": "users",
        "marker": "#users-tbody",
        "text": VIEWED_USER,
    },
    {
        "id": "admin-user-detail",
        "route": "/admin/users/detail/index.php?id=" + VIEWED_USER,
        "page": "detail",
        "marker": "#detail-root",
        "text": VIEWED_USER,
    },
    {
        "id": "admin-deleted-accounts",
        "route": "/admin/deleted-accounts/index.php",
        "page": "deleted",
        "marker": "#lc-tbody",
        "text": "No history rows.",
    },
    {
        "id": "admin-marketing",
        "route": "/admin/marketing/index.php",
        "page": "marketing",
        "marker": "#mkt-tbody",
        "text": "No email-update subscribers.",
    },
]


def load_smoke():
    spec = importlib.util.spec_from_file_location("kpn_full_page_smoke", SMOKE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def founder_cmd(smoke, php, cfg, cmd):
    done = smoke.run_php(php, [str(smoke.MYSQL_SEED), cmd], cfg)
    expect = "seeded kpn_local_test founder" if cmd == "founder-seed" else "deleted kpn_local_test founder"
    if done.returncode != 0 or expect not in (done.stdout or ""):
        raise SystemExit(f"{cmd} failed: {done.stderr or done.stdout}")
    return done.stdout


def snapshot(bag):
    return {
        "pageerrors": len(bag["pageerrors"]),
        "production": len(bag["production"]),
        "ftp": len(bag["ftp"]),
        "mail": len(bag["mail"]),
    }


def open_admin(page, base, case, bag, ready_ms):
    before = snapshot(bag)
    row = {
        "id": case["id"],
        "route": case["route"],
        "expected": "founder page boot, empty destructive actions",
        "result": "FAIL",
        "detail": "",
        "finalUrl": "",
    }
    try:
        page.goto(base + case["route"], wait_until="domcontentloaded", timeout=ready_ms)
        page.wait_for_function(
            """(spec) => {
                const body = document.body;
                const err = document.getElementById('admin-error');
                const title = document.querySelector('h1.admin-title');
                if (!body || !title || body.getAttribute('data-admin-page') !== spec.page) return false;
                if (location.hostname !== '127.0.0.1' || location.pathname.indexOf('/admin/') !== 0) return false;
                if (err && !err.hidden) return false;
                const marker = spec.marker ? document.querySelector(spec.marker) : body;
                if (!marker) return false;
                const text = (marker.textContent || '') + ' ' + (title.textContent || '');
                if (spec.text && text.indexOf(spec.text) < 0) return false;
                if ((body.textContent || '').indexOf('Fatal error') >= 0) return false;
                return localStorage.getItem('kpiNavigator.lastKpiUserId') === spec.userId;
            }""",
            arg={
                "page": case["page"],
                "marker": case["marker"],
                "text": case["text"],
                "userId": FOUNDER["userId"],
            },
            timeout=ready_ms,
        )
        fatal = page.locator("body").inner_text(timeout=2000)
        if "Fatal error" in fatal or "Uncaught" in fatal:
            row["detail"] = "fatal screen"
        else:
            row["result"] = "PASS"
            row["detail"] = case["page"]
    except Exception as exc:
        row["detail"] = str(exc).splitlines()[0][:240]
        try:
            err = page.locator("#admin-error")
            if err.count() and err.is_visible():
                row["detail"] = (err.inner_text() or row["detail"])[:240]
        except Exception:
            pass
    row["finalUrl"] = page.url
    after = snapshot(bag)
    row["pageerrors"] = after["pageerrors"] - before["pageerrors"]
    row["productionRequests"] = after["production"] - before["production"]
    row["ftp"] = after["ftp"] - before["ftp"]
    row["realMail"] = after["mail"] - before["mail"]
    if row["pageerrors"] or row["productionRequests"] or row["ftp"] or row["realMail"]:
        row["result"] = "FAIL"
        row["detail"] = "safety " + row["detail"]
    return row


def main():
    smoke = load_smoke()
    php_path = smoke.php_bin()
    if not php_path:
        raise SystemExit("php not found")
    php = smoke.php_command(php_path)
    manifest = json.loads(smoke.MANIFEST.read_text(encoding="utf-8"))
    accounts = {row["id"]: row for row in manifest["accounts"]}
    order = [
        "fx-basic-restaurant-ready",
        "fx-pro-hotel-ready",
        "fx-pro-restaurant-ready",
        "fx-basic-profile-required",
        "fx-basic-setup-required",
    ]
    work = Path(tempfile.mkdtemp(prefix="kpn-p4b-"))
    data_root = work / "data"
    data_root.mkdir()
    founder_on = False
    server = None
    report = {
        "ok": False,
        "phase": "BR-LOCAL-VERIFY-01 Phase 4B",
        "contractCoverageTarget": 122,
        "adminTarget": 5,
    }
    try:
        user, password = smoke.read_runtime_identity()
        cfg = work / "mysql.php"
        port = smoke.free_port()
        smoke.write_config(
            cfg,
            data_root,
            dbUser=user,
            dbPass=password,
            passwordResetBaseUrl=f"http://127.0.0.1:{port}",
        )
        seeded = smoke.run_php(php, [str(smoke.MYSQL_SEED)], cfg)
        if seeded.returncode != 0 or "seeded kpn_local_test 5" not in (seeded.stdout or ""):
            raise SystemExit(f"mysql seed failed: {seeded.stderr or seeded.stdout}")
        founder_cmd(smoke, php, cfg, "founder-seed")
        founder_on = True
        before = smoke.dump_db(php, cfg)
        if not str(before.get("runtimeUser", "")).startswith("kpn_local_runtime@"):
            raise SystemExit(f"runtime user mismatch: {before.get('runtimeUser')}")
        if before.get("database") != "kpn_local_test":
            raise SystemExit("database mismatch")
        if any(row.get("role") != "user" for row in before.get("users") or []):
            raise SystemExit("canonical role leak")
        if any(row.get("user_id") == FOUNDER["userId"] for row in before.get("users") or []):
            raise SystemExit("founder entered the five-user dump")

        env = dict(**__import__("os").environ)
        env["KPI_V1_CONFIG"] = str(cfg)
        server = subprocess.Popen(
            php + ["-S", f"127.0.0.1:{port}", "-t", str(ROOT)],
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        smoke.wait_http(port)
        from playwright.sync_api import sync_playwright

        base = f"http://127.0.0.1:{port}"
        bag = {"pageerrors": [], "production": [], "ftp": [], "mail": []}
        denial = {"result": "FAIL", "route": "/admin/index.php", "detail": ""}
        results = []
        mutations = []
        session_admin = False
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
            denial_context = browser.new_context()
            denial_page = denial_context.new_page()
            smoke.watch(denial_page, bag)
            smoke.login(denial_page, base, accounts["fx-basic-restaurant-ready"])
            denial_id = denial_page.evaluate("localStorage.getItem('kpiNavigator.lastKpiUserId')")
            response = denial_page.goto(base + "/admin/index.php", wait_until="domcontentloaded", timeout=smoke.READY_MS)
            denial_body = denial_page.locator("body").inner_text(timeout=5000)
            denial_status = response.status if response else 0
            denial["status"] = denial_status
            denial["finalUrl"] = denial_page.url
            denial["userId"] = denial_id
            if (
                denial_status == 403
                and "403 forbidden" in denial_body
                and "KPN Founder Console" not in denial_body
                and denial_id == "localbasicrest"
            ):
                denial["result"] = "PASS"
                denial["detail"] = "403 forbidden"
            else:
                denial["detail"] = denial_body[:180]
            denial_context.close()

            observed = smoke.dump_db(php, cfg)
            basic = accounts["fx-basic-restaurant-ready"]
            categories = smoke.fixture_delta(basic, observed)
            if categories:
                mutations.append({"group": "admin-denial", "fixture": basic["id"], "categories": list(categories)})
                smoke.reseed_fixture(php, cfg, basic["id"])

            admin_context = browser.new_context()
            admin_page = admin_context.new_page()
            smoke.watch(admin_page, bag)
            smoke.login(admin_page, base, FOUNDER)
            for case in ADMIN_CASES:
                results.append(open_admin(admin_page, base, case, bag, smoke.READY_MS))
            session_admin = bool(admin_page.evaluate(
                """async (userId) => {
                    if (localStorage.getItem('kpiNavigator.lastKpiUserId') !== userId) return false;
                    const res = await fetch('/api/v1/admin/dashboard.php', {credentials: 'same-origin'});
                    const data = await res.json();
                    return res.status === 200 && !!(data && data.ok);
                }""",
                FOUNDER["userId"],
            ))
            admin_storage = admin_page.evaluate("localStorage.getItem('kpiNavigator.lastKpiUserId')")
            admin_context.close()
            browser.close()

        observed = smoke.dump_db(php, cfg)
        for fixture_id in order:
            categories = smoke.fixture_delta(accounts[fixture_id], observed)
            if categories:
                mutations.append({"group": "admin", "fixture": fixture_id, "categories": list(categories)})
                smoke.reseed_fixture(php, cfg, fixture_id)
        founder_cmd(smoke, php, cfg, "founder-delete")
        founder_on = False
        final = smoke.dump_db(php, cfg)
        final_dirty = []
        for fixture_id in order:
            categories = smoke.fixture_delta(accounts[fixture_id], final)
            if categories:
                final_dirty.append(fixture_id)
        passed = sum(1 for row in results if row["result"] == "PASS")
        report.update({
            "ok": passed == 5 and denial["result"] == "PASS" and session_admin and not final_dirty
                and not bag["pageerrors"] and not bag["production"] and not bag["ftp"] and not bag["mail"],
            "adminPassed": passed,
            "adminTarget": 5,
            "denial": denial,
            "sessionRemainsAdmin": session_admin,
            "adminUserId": admin_storage,
            "denialContext": "separate",
            "adminContext": "separate",
            "pageerrors": len(bag["pageerrors"]),
            "productionRequests": len(bag["production"]),
            "productionDbAccess": 0,
            "ftp": bag["ftp"],
            "realMail": bag["mail"],
            "runtimeUser": final.get("runtimeUser"),
            "database": final.get("database"),
            "canonicalRoles": sorted({row.get("role") for row in final.get("users") or []}),
            "fixtureMutations": mutations,
            "finalCanonical": not final_dirty,
            "results": results,
        })
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except Exception:
                server.kill()
        if founder_on:
            try:
                founder_cmd(smoke, php, cfg, "founder-delete")
            except Exception as exc:
                report["founderCleanup"] = str(exc)[:200]
        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "results"}, ensure_ascii=False))
    if not report.get("ok"):
        print(json.dumps(report.get("results"), ensure_ascii=False))
        raise SystemExit("phase 4b admin smoke failed")


if __name__ == "__main__":
    main()

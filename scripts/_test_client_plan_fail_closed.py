"""Client plan fail-closed contract. Server legacyPlan resolution stays in PHP."""
import json
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PHP = Path.home() / "AppData" / "Local" / "kpn-tools" / "php" / "php.exe"
AUTH = ROOT / "js" / "kpi-auth-client.js"
GATEWAY = ROOT / "js" / "kpi-data-gateway.js"


def php_legacy_file():
    script = ROOT / "scripts" / "_tmp_plan_legacy_check.php"
    script.write_text(
        """<?php
require dirname(__DIR__) . '/api/v1/_auth.php';
function show($label, $user, $cfg) {
    $pub = kpi_v1_auth_public_user($user, $cfg);
    echo $label, '=', $pub['plan'], PHP_EOL;
}
show('missing_legacy_pro', ['userId' => 'u', 'email' => 'a@b.c'], ['legacyPlan' => 'pro']);
show('missing_legacy_basic', ['userId' => 'u', 'email' => 'a@b.c'], ['legacyPlan' => 'basic']);
show('explicit_basic', ['userId' => 'u', 'email' => 'a@b.c', 'plan' => 'basic'], ['legacyPlan' => 'pro']);
show('explicit_pro', ['userId' => 'u', 'email' => 'a@b.c', 'plan' => 'pro'], ['legacyPlan' => 'basic']);
""",
        encoding="utf-8",
    )
    try:
        proc = subprocess.run(
            [str(PHP), str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
    finally:
        script.unlink(missing_ok=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr or proc.stdout)
    lines = [line.strip() for line in proc.stdout.splitlines() if "=" in line]
    got = dict(line.split("=", 1) for line in lines)
    expect = {
        "missing_legacy_pro": "pro",
        "missing_legacy_basic": "basic",
        "explicit_basic": "basic",
        "explicit_pro": "pro",
    }
    if got != expect:
        raise SystemExit(f"legacy plan mismatch: {got}")
    return got


def client_cases():
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        page.route(
            "http://127.0.0.1:9/login/index.html",
            lambda route: route.fulfill(
                status=200,
                content_type="text/html",
                body="<!DOCTYPE html><html><body></body></html>",
            ),
        )
        page.goto("http://127.0.0.1:9/login/index.html", wait_until="domcontentloaded")
        page.add_script_tag(path=str(AUTH))
        page.add_script_tag(path=str(GATEWAY))
        page.evaluate("() => window.__KPI_AUTH.syncPlanFromServer().catch(() => null)")

        def ev(js):
            return page.evaluate(js)

        ev("() => { localStorage.clear(); sessionStorage.clear(); }")
        results.append(("unresolved_not_pro", ev(
            """() => ({
              pro: window.__KPI_AUTH.isProPlan(),
              basic: window.__KPI_AUTH.isBasicPlan(),
              norm: window.__KPI_AUTH.normalizePlan(''),
              tier: window.__KPI_DATA_GATEWAY.clientTier()
            })"""
        )))

        ev("() => { localStorage.removeItem('kpiNavigator.subscriptionTier'); sessionStorage.removeItem('kpiNavigator.subscriptionTier'); }")
        results.append(("missing_storage_not_pro", ev(
            """() => ({
              pro: window.__KPI_AUTH.isProPlan(),
              tier: window.__KPI_DATA_GATEWAY.clientTier(),
              stored: window.__KPI_AUTH.readStoredTier()
            })"""
        )))

        results.append(("server_basic", ev(
            """() => {
              window.__KPI_AUTH.applyServerPlan('basic');
              return {
                pro: window.__KPI_AUTH.isProPlan(),
                basic: window.__KPI_AUTH.isBasicPlan(),
                tier: window.__KPI_DATA_GATEWAY.clientTier()
              };
            }"""
        )))

        results.append(("server_pro", ev(
            """() => {
              window.__KPI_AUTH.applyServerPlan('pro');
              return {
                pro: window.__KPI_AUTH.isProPlan(),
                basic: window.__KPI_AUTH.isBasicPlan(),
                tier: window.__KPI_DATA_GATEWAY.clientTier()
              };
            }"""
        )))

        results.append(("unknown_does_not_grant_pro", ev(
            """() => {
              localStorage.setItem('kpiNavigator.subscriptionTier', 'basic');
              sessionStorage.setItem('kpiNavigator.subscriptionTier', 'basic');
              const written = window.__KPI_AUTH.applyServerPlan('');
              const junk = window.__KPI_AUTH.applyServerPlan('enterprise');
              return {
                written: written,
                junk: junk,
                pro: window.__KPI_AUTH.isProPlan(),
                basic: window.__KPI_AUTH.isBasicPlan()
              };
            }"""
        )))

        results.append(("authoritative_pro_after_sync", ev(
            """async () => {
              localStorage.removeItem('kpiNavigator.subscriptionTier');
              sessionStorage.removeItem('kpiNavigator.subscriptionTier');
              const orig = window.fetch;
              window.fetch = async function () {
                return new Response(JSON.stringify({
                  ok: true, userId: 'legacy01', plan: 'pro'
                }), {status: 200, headers: {'Content-Type': 'application/json'}});
              };
              try {
                await window.__KPI_AUTH.me();
              } finally {
                window.fetch = orig;
              }
              return {
                pro: window.__KPI_AUTH.isProPlan(),
                tier: window.__KPI_DATA_GATEWAY.clientTier(),
                stored: window.__KPI_AUTH.readStoredTier()
              };
            }"""
        )))
        browser.close()
    expect = {
        "unresolved_not_pro": {"pro": False, "basic": False, "norm": "", "tier": ""},
        "missing_storage_not_pro": {"pro": False, "tier": "", "stored": ""},
        "server_basic": {"pro": False, "basic": True, "tier": "basic"},
        "server_pro": {"pro": True, "basic": False, "tier": "pro"},
        "unknown_does_not_grant_pro": {"written": "", "junk": "", "pro": False, "basic": True},
        "authoritative_pro_after_sync": {"pro": True, "tier": "pro", "stored": "pro"},
    }
    got = {name: value for name, value in results}
    if got != expect:
        raise SystemExit(json.dumps({"got": got, "expect": expect}, ensure_ascii=False))
    return got


def home_gates():
    for rel in ("app/home/index.html", "en/app/home/index.html", "zh-tw/app/home/index.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "guardProPage" in text:
            raise SystemExit(f"Home still gates Pro: {rel}")
    for rel in (
        "app/profit/pl/index.html",
        "app/monthly/edit/index.html",
        "app/booking/index.html",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "guardProPage" not in text:
            raise SystemExit(f"Pro page lost its gate: {rel}")


def main():
    legacy = php_legacy_file()
    home_gates()
    client = client_cases()
    print(json.dumps({"ok": True, "legacy": legacy, "client": client}, ensure_ascii=False))


if __name__ == "__main__":
    main()

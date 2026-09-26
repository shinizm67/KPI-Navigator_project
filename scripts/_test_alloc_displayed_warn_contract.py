# -*- coding: utf-8 -*-
"""Regression: Cockpit allocation warning must match the DISPLAYED 1-decimal total.

Fails if displayed total == 100% while warning class or ⚠ icon is present.
Covers generated Annual/Monthly HTML + shared kpi-planning-readiness.js,
not only the 2-decimal isAllocTotalOk helper.
"""
from __future__ import annotations

import http.cookiejar
import http.server
import json
import re
import socketserver
import sys
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "js" / "kpi-planning-readiness.js"
CACHE = "20260926-alloc3"
FMT_NEEDLE = "(Math.round(percent * 10) / 10).toLocaleString('en-US', { maximumFractionDigits: 1 }) + '%'"
HOSTS = [
    ROOT / "app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]
PAGES = {
    "annual": {
        "ja": "/app/annual/index.html",
        "en": "/en/app/annual/index.html",
        "zh-tw": "/zh-tw/app/annual/index.html",
    },
    "monthly": {
        "ja": "/app/monthly/index.html",
        "en": "/en/app/monthly/index.html",
        "zh-tw": "/zh-tw/app/monthly/index.html",
    },
}
BASE_PROD = "https://forge-laboratory.com/kpi-navigator"
API = BASE_PROD + "/api/v1"
DEMO_SECRET = Path.home() / "kpi-navigator-ops" / "demo-account-passwords-20260920.json"
PRO_EMAIL = "kpn_demo_restaurant_pro01@trial.forge-laboratory.com"
OUT = ROOT / "scripts" / "_tmp_alloc_displayed_warn_contract.json"
VIEWPORTS = [1200, 1280, 1366, 1440]
WARN_ORANGE = "rgb(217, 119, 6)"

PROBE = r"""() => {
  const pr = window.KpiPlanningReadiness;
  const formatPercentText = function (percent) {
    return (Math.round(percent * 10) / 10).toLocaleString('en-US', { maximumFractionDigits: 1 }) + '%';
  };
  function snap() {
    const cluster = document.querySelector('.annual-kpi-allocation-cluster');
    const pct = (cluster && cluster.querySelector('.annual-allocation-percent'))
      || document.getElementById('annual-allocation-percent');
    const mark = cluster && cluster.querySelector('.kpi-pr-anomaly-mark');
    const cs = mark ? getComputedStyle(mark) : null;
    const markVisible = !!(mark && !mark.hasAttribute('hidden') && cs
      && cs.display !== 'none' && cs.visibility !== 'hidden');
    const color = pct ? getComputedStyle(pct).color : null;
    const text = pct ? String(pct.textContent || '').trim() : null;
    const displayed100 = text === '100%' || text === '100.0%';
    const warnClass = !!(cluster && cluster.classList.contains('is-seasonality-anomaly'));
    return {
      text: text,
      displayed100: displayed100,
      warnClass: warnClass,
      markVisible: markVisible,
      color: color,
      orange: color === 'rgb(217, 119, 6)',
      broken100: displayed100 && (warnClass || markVisible),
      brokenNon100: !displayed100 && !!text && text !== '—' && (!warnClass || !markVisible),
    };
  }
  function paintAvg(avg) {
    const pct = document.getElementById('annual-allocation-percent');
    if (pct) pct.textContent = formatPercentText(avg);
    if (pr && typeof pr.refreshSeasonalityAnomalyUi === 'function') pr.refreshSeasonalityAnomalyUi();
    return snap();
  }
  const floatEqWeights = [100,100,100,100,100,100,100,100,100,100,100,99.52];
  const floatAvg = floatEqWeights.reduce(function (a, b) { return a + b; }, 0) / 12;
  const cases = {
    exact100: paintAvg(100),
    pct99_9: paintAvg(99.9),
    pct100_1: paintAvg(100.1),
    floatEq100: paintAvg(floatAvg),
  };
  const live = snap();
  return {
    live: live,
    cases: cases,
    floatAvg: floatAvg,
    helperDisplayed: pr && typeof pr.isDisplayedAllocTotalOk === 'function'
      ? pr.isDisplayedAllocTotalOk() : null,
    src: (document.querySelector('script[src*="kpi-planning-readiness.js"]') || {}).src || null,
  };
}"""


def check(cond: bool, msg: str, fails: list[str]) -> None:
    if not cond:
        fails.append(msg)


def static_contract() -> list[str]:
    fails: list[str] = []
    js = JS.read_text(encoding="utf-8")
    fn = js.split("function refreshSeasonalityAnomalyUi()")[1].split("function reasonLabels")[0]
    check("function isDisplayedAllocTotalOk()" in js, "js has isDisplayedAllocTotalOk", fails)
    check("var warn = !isDisplayedAllocTotalOk();" in js, "refresh uses displayed contract", fails)
    check("isAllocTotalOk" not in fn, "refresh does not call isAllocTotalOk", fails)
    check("assessSeasonalityAnomalies" not in fn, "refresh does not use year-pattern", fails)
    check("Math.round((sum / 12) * 10) / 10" in js, "displayed avg is 1-decimal like formatPercentText", fails)
    check("readHlWeights(operatingYear())" not in fn, "refresh does not mix operatingYear weights", fails)
    for path in HOSTS:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check(FMT_NEEDLE in html, f"{rel} formatPercentText 1-decimal en-US", fails)
        check(f"kpi-planning-readiness.js?v={CACHE}" in html, f"{rel} cache-bust {CACHE}", fails)
        check(
            not re.search(
                r"\.annual-kpi-allocation-cluster\.is-seasonality-anomaly",
                html.split("<script")[0],
            ),
            f"{rel} no page-local warning CSS",
            fails,
        )
    # Displayed 100% must not warn (1-decimal), including float-equivalent.
    def displayed_ok(avg: float) -> bool:
        return round(avg * 10) / 10 == 100.0

    check(displayed_ok(100.0) is True, "exact 100 display-ok", fails)
    check(displayed_ok(99.9) is False, "99.9 display-not-ok", fails)
    check(displayed_ok(100.1) is False, "100.1 display-not-ok", fails)
    check(displayed_ok(99.96) is True, "float-eq 99.96 displays 100", fails)
    check(displayed_ok(100.04) is True, "float-eq 100.04 displays 100", fails)
    return fails


def load_password(email: str) -> str:
    data = json.loads(DEMO_SECRET.read_text(encoding="utf-8"))
    rec = (data.get("accounts") or {}).get(email) or {}
    if not rec.get("password"):
        raise SystemExit("password missing")
    return str(rec["password"])


def login(email: str, password: str):
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    req = urllib.request.Request(
        API + "/auth/login.php",
        data=json.dumps({"email": email, "password": password}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with opener.open(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("ok"):
        raise SystemExit("login_failed")
    return [
        {
            "name": c.name,
            "value": c.value,
            "domain": "forge-laboratory.com",
            "path": c.path or "/",
            "secure": True,
            "sameSite": "Lax",
        }
        for c in jar
    ]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        return


def judge(rec: dict, live_expect_100: bool) -> list[str]:
    fails: list[str] = []
    cases = rec.get("cases") or {}
    exact = cases.get("exact100") or {}
    under = cases.get("pct99_9") or {}
    over = cases.get("pct100_1") or {}
    fe = cases.get("floatEq100") or {}
    if exact.get("broken100") or exact.get("warnClass") or exact.get("markVisible") or exact.get("orange"):
        fails.append("exact100_warn")
    if not under.get("warnClass") or not under.get("markVisible"):
        fails.append("pct99_9_no_warn")
    if not over.get("warnClass") or not over.get("markVisible"):
        fails.append("pct100_1_no_warn")
    if fe.get("broken100") or fe.get("warnClass") or fe.get("markVisible"):
        fails.append("floatEq100_warn")
    if CACHE not in (rec.get("src") or ""):
        fails.append("cachebust:" + str(rec.get("src") or "")[-48:])
    live = rec.get("live") or {}
    if live_expect_100 and live.get("text") in ("100%", "100.0%"):
        if live.get("warnClass") or live.get("markVisible") or live.get("broken100") or live.get("orange"):
            fails.append("live_100_still_warn")
    if live.get("broken100"):
        fails.append("live_broken100")
    return fails


def toggle_office(page, want_office: bool) -> None:
    is_office = page.evaluate("() => document.body.classList.contains('office-mode')")
    if bool(is_office) == want_office:
        return
    btn = page.locator("#btn-mode-toggle")
    if btn.count():
        btn.click()
        page.wait_for_timeout(200)
    else:
        page.evaluate(
            """(w) => { document.body.classList.toggle('office-mode', !!w); }""",
            want_office,
        )


def run_matrix(page, base: str, query: str, live_expect_100: bool, viewports: list[int]) -> list[dict]:
    rows = []
    for surface, langs in PAGES.items():
        for lang, path in langs.items():
            for width in viewports:
                page.set_viewport_size({"width": width, "height": 900})
                page.goto(base + path + query, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_selector("#annual-allocation-percent", state="attached", timeout=25000)
                page.wait_for_timeout(1200)
                for mode in ("scifi", "office"):
                    toggle_office(page, mode == "office")
                    rec = page.evaluate(PROBE)
                    rec.update({
                        "surface": surface,
                        "lang": lang,
                        "mode": mode,
                        "width": width,
                        "tag": f"{surface}-{lang}-{mode}-{width}",
                    })
                    rec["fails"] = judge(rec, live_expect_100)
                    rows.append(rec)
                    print(rec["tag"], rec.get("live", {}).get("text"), rec.get("fails"))
    return rows


def nav_reload_check(page, base: str, query: str) -> dict:
    annual = base + PAGES["annual"]["ja"] + query
    monthly = base + PAGES["monthly"]["ja"] + query
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(annual, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#annual-allocation-percent", timeout=25000)
    page.wait_for_timeout(1200)
    a1 = page.evaluate(PROBE)
    page.goto(monthly, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#annual-allocation-percent", timeout=25000)
    page.wait_for_timeout(1200)
    m1 = page.evaluate(PROBE)
    page.goto(annual, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#annual-allocation-percent", timeout=25000)
    page.wait_for_timeout(1200)
    a2 = page.evaluate(PROBE)
    page.reload(wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#annual-allocation-percent", timeout=25000)
    page.wait_for_timeout(1400)
    a3 = page.evaluate(PROBE)
    fails = []
    for name, rec in (("annual1", a1), ("monthly", m1), ("annual2", a2), ("reload", a3)):
        jf = judge(rec, live_expect_100=True)
        # nav check: synthetic cases must still pass; live 100% only if displayed 100
        live = rec.get("live") or {}
        if live.get("text") in ("100%", "100.0%") and (live.get("warnClass") or live.get("markVisible")):
            fails.append(f"{name}_live_100_warn")
        case_fails = [x for x in jf if not x.startswith("live_")]
        if case_fails:
            fails.extend(f"{name}:{x}" for x in case_fails)
        if live.get("broken100"):
            fails.append(f"{name}_broken100")
    return {"fails": fails, "annual1": a1.get("live"), "monthly": m1.get("live"), "reload": a3.get("live")}


def main() -> int:
    static_fails = static_contract()
    if static_fails:
        print("STATIC FAIL", static_fails)
        return 1
    print("static ok")

    from playwright.sync_api import sync_playwright

    want_prod = "prod" in sys.argv[1:] or "--prod" in sys.argv[1:]
    local_viewports = VIEWPORTS if want_prod else [1280]
    # Full width matrix is expensive; always cover 1280 all langs, and all widths on JA annual+monthly when prod.
    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    rows: list[dict] = []
    nav = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True, args=["--disk-cache-size=0"])
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            rows.extend(run_matrix(page, f"http://127.0.0.1:{port}", "?local=1", False, [1280]))
            # Local widths on JP annual only
            for width in VIEWPORTS:
                if width == 1280:
                    continue
                page.set_viewport_size({"width": width, "height": 900})
                page.goto(f"http://127.0.0.1:{port}/app/annual/index.html?local=1", wait_until="domcontentloaded")
                page.wait_for_selector("#annual-allocation-percent", timeout=25000)
                page.wait_for_timeout(800)
                rec = page.evaluate(PROBE)
                rec.update({"tag": f"annual-ja-scifi-{width}", "surface": "annual", "lang": "ja", "mode": "scifi", "width": width})
                rec["fails"] = judge(rec, False)
                rows.append(rec)
            local_nav = nav_reload_check(page, f"http://127.0.0.1:{port}", "?local=1")
            local_nav["fails"] = [f for f in (local_nav.get("fails") or []) if not f.endswith("_live_100_warn")]
            if local_nav["fails"]:
                rows.append({"tag": "local-nav", "fails": local_nav["fails"]})
            page.close()
            if want_prod:
                cookies = login(PRO_EMAIL, load_password(PRO_EMAIL))
                ctx = browser.new_context(viewport={"width": 1280, "height": 900})
                ctx.add_cookies(cookies)
                ctx.add_init_script("""try {
                  localStorage.setItem('kpiNavigator.storeSync', JSON.stringify({
                    enabled: true, authMode: 'session', baseUrl: '/kpi-navigator/api/v1/store.php'
                  }));
                } catch (e) {}""")
                prod = ctx.new_page()
                prod_rows = run_matrix(prod, BASE_PROD, "?allocWarn=1&kpiSync=1", True, local_viewports)
                for r in prod_rows:
                    r["env"] = "prod"
                rows.extend(prod_rows)
                nav = nav_reload_check(prod, BASE_PROD, "?allocWarn=1&kpiSync=1")
                ctx.close()
            browser.close()
    finally:
        httpd.shutdown()

    fails = [r["tag"] + ":" + ",".join(r.get("fails") or []) for r in rows if r.get("fails")]
    if nav.get("fails"):
        fails.append("nav:" + ",".join(nav["fails"]))
    n_ok = sum(1 for r in rows if not r.get("fails"))
    OUT.write_text(
        json.dumps(
            {"n": len(rows), "n_ok": n_ok, "fails": fails, "nav": nav, "rows": rows},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print("n_ok", n_ok, "/", len(rows))
    if fails:
        for f in fails:
            print(f)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

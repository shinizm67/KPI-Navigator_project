# -*- coding: utf-8 -*-
"""Production-path E2E: explicit businessDay false survives PUT/GET and Past Sales reload."""

from __future__ import annotations

import http.cookiejar
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://forge-laboratory.com/kpi-navigator"
API = BASE + "/api/v1"
DEMO_SECRET = Path.home() / "kpi-navigator-ops" / "demo-account-passwords-20260920.json"
PRO_EMAIL = "kpn_demo_restaurant_pro01@trial.forge-laboratory.com"
ROWS = [
    {"iso": "2025-11-01", "sales": 60930, "businessDay": True},
    {"iso": "2025-11-02", "sales": 0, "businessDay": False},
    {"iso": "2025-11-03", "sales": 0, "businessDay": False},
    {"iso": "2025-11-04", "sales": 144600, "businessDay": True},
    {"iso": "2025-11-09", "sales": 0, "businessDay": False},
]


def load_password(path: Path, email: str) -> tuple[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    accounts = data.get("accounts") if isinstance(data.get("accounts"), dict) else data
    rec = accounts.get(email) if isinstance(accounts, dict) else None
    if not isinstance(rec, dict) or not rec.get("password"):
        raise SystemExit(f"password missing for {email}")
    return str(rec["password"]), str(rec.get("userId") or "")


def api_call(opener, method, path, body=None, extra_headers=None):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with opener.open(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"ok": False, "raw": raw[:400]}
        return e.code, parsed


def login(email: str, password: str):
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    code, data = api_call(opener, "POST", "/auth/login.php", {"email": email, "password": password})
    if code != 200 or not data.get("ok"):
        raise SystemExit(f"login_failed:{email}:{code}:{data}")
    return jar, opener, data


def row_by_iso(rows, iso):
    for r in rows or []:
        if r and r.get("iso") == iso:
            return r
    return None


def main() -> int:
    if not DEMO_SECRET.is_file():
        print("SKIP: demo secret missing")
        return 0
    pw, uid = load_password(DEMO_SECRET, PRO_EMAIL)
    _jar, opener, login_data = login(PRO_EMAIL, pw)
    uid = str(login_data.get("userId") or uid)
    exp = {"X-KPI-Expected-User": uid}
    put_body = {"rows": ROWS, "expectedUserId": uid}
    put_code, put_data = api_call(opener, "PUT", "/daily-inputs.php", put_body, exp)
    if put_code != 200 or not put_data.get("ok"):
        print("FAIL PUT", put_code, put_data)
        return 1
    get_code, get_data = api_call(
        opener,
        "GET",
        "/daily-inputs.php?from=2025-11-01&to=2025-11-09",
        None,
        exp,
    )
    if get_code != 200 or not get_data.get("ok"):
        print("FAIL GET", get_code, get_data)
        return 1
    failed = 0
    for spec in ROWS:
        got = row_by_iso(get_data.get("rows"), spec["iso"])
        if not got:
            print("FAIL missing GET row", spec["iso"])
            failed += 1
            continue
        if got.get("businessDay") is not spec["businessDay"]:
            print("FAIL", spec["iso"], "businessDay", got.get("businessDay"), "want", spec["businessDay"])
            failed += 1
        if float(got.get("sales") or 0) != float(spec["sales"]):
            print("FAIL", spec["iso"], "sales", got.get("sales"), "want", spec["sales"])
            failed += 1
    if failed:
        return 1
    print("prod daily-inputs PUT/GET false preserved for Barca 11/1-11/9")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP playwright UI (not installed)")
        return 0

    want_checked = {
        "2025-11-01": True,
        "2025-11-02": False,
        "2025-11-03": False,
        "2025-11-04": True,
        "2025-11-09": False,
    }
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            for c in _jar:
                context.add_cookies(
                    [
                        {
                            "name": c.name,
                            "value": c.value,
                            "domain": "forge-laboratory.com",
                            "path": c.path or "/",
                            "httpOnly": True,
                            "secure": True,
                        }
                    ]
                )
            page = context.new_page()
            page.goto(BASE + "/app/annual/index.html", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4500)
            snap = page.evaluate(
                """() => {
                  const store = window.KpiYearStore && KpiYearStore.getStore && KpiYearStore.getStore();
                  const tl = (store && store.timeline) || {};
                  const ps = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.pastSales) || {};
                  const isos = ['2025-11-01','2025-11-02','2025-11-03','2025-11-04','2025-11-09'];
                  const out = { timeline: {}, pastSales: {}, layoutMarker: !!(window.KpiWorkbookLayout && window.KpiWorkbookLayout.overlayBusinessDaysPreserveExplicit) };
                  isos.forEach((iso) => {
                    out.timeline[iso] = Object.prototype.hasOwnProperty.call(tl.businessDays || {}, iso)
                      ? tl.businessDays[iso]
                      : 'ABSENT';
                    out.pastSales[iso] = Object.prototype.hasOwnProperty.call(ps.businessDayByDate || {}, iso)
                      ? ps.businessDayByDate[iso]
                      : 'ABSENT';
                  });
                  return out;
                }"""
            )
            page.locator("#annual-past-sales-btn").click()
            page.wait_for_timeout(800)
            boxes = page.evaluate(
                """() => {
                  const isos = ['2025-11-01','2025-11-02','2025-11-03','2025-11-04','2025-11-09'];
                  const out = {};
                  isos.forEach((iso) => {
                    const cb = document.querySelector('.past-sales-modal__cb[data-iso-date="' + iso + '"]');
                    out[iso] = cb ? !!cb.checked : 'MISSING';
                  });
                  return out;
                }"""
            )
            page.reload(wait_until="domcontentloaded")
            page.wait_for_timeout(4500)
            page.locator("#annual-past-sales-btn").click()
            page.wait_for_timeout(800)
            boxes2 = page.evaluate(
                """() => {
                  const isos = ['2025-11-01','2025-11-02','2025-11-03','2025-11-04','2025-11-09'];
                  const out = {};
                  isos.forEach((iso) => {
                    const cb = document.querySelector('.past-sales-modal__cb[data-iso-date="' + iso + '"]');
                    out[iso] = cb ? !!cb.checked : 'MISSING';
                  });
                  return out;
                }"""
            )
            browser.close()
    except Exception as exc:
        print("SKIP playwright UI:", exc)
        return 0

    print("store snap", json.dumps(snap, ensure_ascii=False))
    print("checkbox before reload", boxes)
    print("checkbox after reload", boxes2)
    ui_fail = 0
    for iso, checked in want_checked.items():
        if boxes2.get(iso) is not checked:
            print("FAIL UI reload", iso, boxes2.get(iso), "want", checked)
            ui_fail += 1
    if ui_fail:
        return 1
    print("prod Past Sales checkboxes match after reload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

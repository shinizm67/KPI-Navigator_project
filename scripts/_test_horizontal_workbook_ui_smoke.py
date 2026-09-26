# -*- coding: utf-8 -*-
"""BR-POST-HORIZONTAL-WORKBOOK-PARSER — Past Sales UI-path smoke.

Local: serve the working-tree Annual HTML on the production origin via route
fulfill (so auth/store stay production, importer is local). Confirm dialogs
are dismissed so Demo Pro is not mutated.

Usage:
  python scripts/_test_horizontal_workbook_ui_smoke.py
  python scripts/_test_horizontal_workbook_ui_smoke.py --production
"""
from __future__ import annotations

import argparse
import hashlib
import http.cookiejar
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\funki\kpi-navigator")
BASE = "https://forge-laboratory.com/kpi-navigator"
API = BASE + "/api/v1"
ANNUAL = BASE + "/app/annual/index.html"
DEMO_SECRET = Path.home() / "kpi-navigator-ops" / "demo-account-passwords-20260920.json"
PRO_EMAIL = "kpn_demo_restaurant_pro01@trial.forge-laboratory.com"
BASIC_EMAIL = "kpn_demo_restaurant_basic01@trial.forge-laboratory.com"
BARCA_CSV = ROOT / "fixtures" / "import" / "horizontal" / "barca_2025_11_data.csv"
BARCA_XLSX = ROOT / "fixtures" / "import" / "horizontal" / "barca_2025_11_data.xlsx"
VERTICAL_XLSX = ROOT / "fixtures" / "import" / "c2l6b" / "D_single_sales.xlsx"
VERTICAL_CSV = ROOT / "scripts" / "_tmp_hwb_vertical_sales.csv"
OUT = ROOT / "scripts" / "_tmp_hwb_ui_smoke.json"
FALLBACK_SNIP = "自動判定できませんでした"
WANT_NOV1 = {
    "sales": 60930,
    "customers": 13,
    "parties": 9,
    "lunch": 0,
    "food": 36880,
    "drink": 24050,
}


def load_password(path: Path, email: str) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    accounts = data.get("accounts") if isinstance(data.get("accounts"), dict) else data
    rec = accounts.get(email) if isinstance(accounts, dict) else None
    if not isinstance(rec, dict) or not rec.get("password"):
        raise SystemExit(f"password missing for {email}")
    return str(rec["password"])


def api_call(opener, method, path, body=None):
    req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(API + path, data=data, headers=req_headers, method=method)
    try:
        with opener.open(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"ok": False}
        return e.code, parsed


def login(email: str, password: str):
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    code, data = api_call(opener, "POST", "/auth/login.php", {"email": email, "password": password})
    if code != 200 or not data.get("ok"):
        raise SystemExit(f"login_failed:{email}:{code}")
    return jar, opener, data


def cookies_for_playwright(jar):
    out = []
    for c in jar:
        out.append(
            {
                "name": c.name,
                "value": c.value,
                "domain": "forge-laboratory.com",
                "path": c.path or "/",
                "httpOnly": bool(c.get_nonstandard_attr("HttpOnly")),
                "secure": True,
                "sameSite": "Lax",
            }
        )
    return out


def store_fp(blob: dict) -> str:
    store = blob.get("store") if isinstance(blob.get("store"), dict) else blob
    raw = json.dumps(store, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def daily_expenses_fp(blob: dict) -> str:
    store = blob.get("store") if isinstance(blob.get("store"), dict) else {}
    years = store.get("years") if isinstance(store.get("years"), dict) else {}
    de = {}
    for y, rec in years.items():
        if isinstance(rec, dict) and rec.get("dailyExpenses"):
            de[str(y)] = rec.get("dailyExpenses")
    raw = json.dumps(de, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def js_click(page, sel: str):
    page.evaluate("(s) => { const el = document.querySelector(s); if (el) el.click(); }", sel)


def wait_app(page):
    page.wait_for_function(
        """() => !!(window.__KPI_DAILY_IMPORT && window.KpiYearStore && window.KpiBusinessType)""",
        timeout=60000,
    )


def install_local_overrides(page):
    annual = (ROOT / "app" / "annual" / "index.html").read_bytes()
    layout = (ROOT / "js" / "kpi-workbook-layout.js").read_bytes()
    picker = (ROOT / "js" / "kpi-excel-sheet-picker.js").read_bytes()

    def on_route(route):
        url = route.request.url.split("?", 1)[0]
        if url.endswith("/js/kpi-workbook-layout.js"):
            route.fulfill(status=200, content_type="application/javascript; charset=utf-8", body=layout)
            return
        if url.endswith("/js/kpi-excel-sheet-picker.js"):
            route.fulfill(status=200, content_type="application/javascript; charset=utf-8", body=picker)
            return
        if url.endswith("/app/annual/index.html"):
            route.fulfill(status=200, content_type="text/html; charset=utf-8", body=annual)
            return
        route.continue_()

    page.route("**/*", on_route)


def hook_maps(page):
    page.evaluate(
        """() => {
          const api = window.__KPI_DAILY_IMPORT;
          if (!api || typeof api.parseFile !== 'function' || api.__hwbHooked) return false;
          const orig = api.parseFile.bind(api);
          api.parseFile = function (file) {
            return orig(file).then(function (maps) {
              const unknown = maps.unmatchedMetrics || [];
              window.__HWB_LAST_MAPS = {
                layout: maps.layout || '',
                imported: maps.imported || 0,
                years: maps.years || [],
                salesByDate: maps.salesByDate || {},
                totalCustomersByDate: maps.totalCustomersByDate || {},
                totalGroupsByDate: maps.totalGroupsByDate || {},
                lunchSalesByDate: maps.lunchSalesByDate || {},
                dinnerSalesByDate: maps.dinnerSalesByDate || {},
                foodByDate: maps.foodByDate || {},
                drinkByDate: maps.drinkByDate || {},
                unmatchedCount: unknown.length,
                expenseLabels: Array.from(new Set(unknown.filter(function (u) {
                  return u && u.kind === 'expense';
                }).map(function (u) { return u.label; }))),
                unknownSample: unknown.slice(0, 12),
                hasFoodCol: !!maps.hasFoodCol,
                hasDrinkCol: !!maps.hasDrinkCol
              };
              return maps;
            });
          };
          api.__hwbHooked = true;
          return true;
        }"""
    )


def enable_past_sales_edit(page):
    page.locator("#annual-past-sales-btn").wait_for(state="visible", timeout=20000)
    page.locator("#annual-past-sales-btn").click()
    page.locator("#past-sales-modal-csv").wait_for(state="visible", timeout=20000)
    sw = page.locator("#past-sales-modal [data-ps-edit-switch]").first
    sw.wait_for(state="visible", timeout=20000)
    if sw.get_attribute("aria-checked") != "true":
        sw.click()
        page.wait_for_timeout(600)
    page.wait_for_function(
        """() => {
          const b = document.getElementById('past-sales-modal-csv');
          const sw = document.querySelector('#past-sales-modal [data-ps-edit-switch]');
          return !!(b && !b.disabled && sw && sw.getAttribute('aria-checked') === 'true');
        }""",
        timeout=20000,
    )


def upload(page, btn_sel: str, path: Path):
    btn = page.locator(btn_sel)
    btn.wait_for(state="visible", timeout=20000)
    page.wait_for_function(
        """(sel) => {
          const el = document.querySelector(sel);
          return !!(el && !el.disabled);
        }""",
        arg=btn_sel,
        timeout=15000,
    )
    with page.expect_file_chooser(timeout=20000) as fc:
        try:
            btn.click(timeout=8000)
        except Exception:
            js_click(page, btn_sel)
    fc.value.set_files(str(path))


def select_sheet(page, needle: str):
    page.wait_for_selector("#kpi-excel-sheet-picker", timeout=20000)
    page.evaluate(
        """(needle) => {
          const all = Array.from(document.querySelectorAll('#kpi-excel-sheet-picker .kpi-sheet-picker__sheet'));
          const hit = all.find((b) => {
            const n = (b.getAttribute('data-kpi-sheet-name') || b.textContent || '');
            return n.indexOf(needle) >= 0;
          }) || all[all.length - 1];
          if (hit) hit.click();
        }""",
        needle,
    )


def wait_maps(page, timeout_ms=25000):
    page.wait_for_function("() => !!(window.__HWB_LAST_MAPS)", timeout=timeout_ms)
    return page.evaluate("() => window.__HWB_LAST_MAPS")


def clear_maps(page):
    page.evaluate("() => { window.__HWB_LAST_MAPS = null; }")


def check_nov1(maps: dict) -> list[str]:
    fails = []
    iso = "2025-11-01"
    sales = (maps.get("salesByDate") or {}).get(iso)
    cust = (maps.get("totalCustomersByDate") or {}).get(iso)
    parties = (maps.get("totalGroupsByDate") or {}).get(iso)
    lunch = (maps.get("lunchSalesByDate") or {}).get(iso)
    food = (maps.get("foodByDate") or {}).get(iso)
    drink = (maps.get("drinkByDate") or {}).get(iso)
    if sales != WANT_NOV1["sales"]:
        fails.append(f"nov1_sales:{sales}")
    if cust != WANT_NOV1["customers"]:
        fails.append(f"nov1_customers:{cust}")
    if parties != WANT_NOV1["parties"]:
        fails.append(f"nov1_parties:{parties}")
    if lunch != WANT_NOV1["lunch"]:
        fails.append(f"nov1_lunch:{lunch}")
    if food != WANT_NOV1["food"]:
        fails.append(f"nov1_food:{food}")
    if drink != WANT_NOV1["drink"]:
        fails.append(f"nov1_drink:{drink}")
    extra = {
        "2025-11-04": {"sales": 144600, "customers": 22, "parties": 5},
        "2025-11-05": {"sales": 195550, "customers": 30, "parties": 4},
        "2025-11-06": {"sales": 339960, "customers": 31, "parties": 3},
    }
    for day, want in extra.items():
        got_s = (maps.get("salesByDate") or {}).get(day)
        if got_s != want["sales"]:
            fails.append(f"{day}_sales:{got_s}")
        got_c = (maps.get("totalCustomersByDate") or {}).get(day)
        if got_c != want["customers"]:
            fails.append(f"{day}_customers:{got_c}")
        got_p = (maps.get("totalGroupsByDate") or {}).get(day)
        if got_p != want["parties"]:
            fails.append(f"{day}_parties:{got_p}")
    if maps.get("layout") != "horizontal":
        fails.append(f"layout:{maps.get('layout')}")
    if int(maps.get("imported") or 0) < 8:
        fails.append(f"imported:{maps.get('imported')}")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--production", action="store_true")
    args = ap.parse_args()
    if not BARCA_CSV.is_file():
        raise SystemExit("missing copied Barca CSV fixture")
    if not BARCA_XLSX.is_file():
        raise SystemExit("missing Barca XLSX fixture — run scripts/_build_horizontal_barca_xlsx.py")
    VERTICAL_CSV.write_text("日付,日次売上,トータル客数,トータル組数\n2025-03-02,12345,4,2\n", encoding="utf-8")

    fails = []
    rows = {"mode": "production" if args.production else "local-override", "ts": int(time.time())}
    pro_pw = load_password(DEMO_SECRET, PRO_EMAIL)
    basic_pw = load_password(DEMO_SECRET, BASIC_EMAIL)
    jar, opener, me = login(PRO_EMAIL, pro_pw)
    rows["plan"] = me.get("plan")
    _c, st_before = api_call(opener, "GET", "/store.php")
    fp_before = store_fp(st_before)
    de_before = daily_expenses_fp(st_before)
    rows["store_fp_before"] = fp_before
    rows["daily_expenses_fp_before"] = de_before

    dialogs = []

    def on_dialog(d):
        dialogs.append({"type": d.type, "message": d.message})
        msg = d.message or ""
        enter_edit = (
            "続けますか" in msg
            or "Continue?" in msg
            or "是否繼續" in msg
            or "編集します" in msg
            or "You will edit" in msg
            or "您將編輯" in msg
        )
        if d.type == "confirm" and enter_edit:
            d.accept()
        elif d.type == "confirm":
            d.dismiss()
        else:
            d.accept()

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_cookies(cookies_for_playwright(jar))
        page = ctx.new_page()
        page.on("dialog", on_dialog)
        if not args.production:
            install_local_overrides(page)
        page.goto(ANNUAL, wait_until="load", timeout=180000)
        wait_app(page)
        page.wait_for_function(
            """() => {
              const api = window.KpiBusinessType;
              return !!(api && api.isBusinessTypeSet && api.isBusinessTypeSet());
            }""",
            timeout=45000,
        )
        hooked = page.evaluate(
            """() => !!(window.KpiWorkbookLayout && window.__KPI_DAILY_IMPORT && window.__KPI_DAILY_IMPORT.parseFile)"""
        )
        rows["engine"] = {
            "hasLayout": hooked,
            "layoutScript": page.evaluate("() => !!(window.KpiWorkbookLayout && window.KpiWorkbookLayout.prepare)"),
        }
        if not rows["engine"]["layoutScript"]:
            fails.append("layout_missing")
        hook_maps(page)
        enable_past_sales_edit(page)
        rows["past_sales_open"] = True

        # --- A. CSV ---
        clear_maps(page)
        before_n = len(dialogs)
        upload(page, "#past-sales-modal-csv", BARCA_CSV)
        csv_maps = None
        try:
            csv_maps = wait_maps(page, 30000)
        except Exception as e:
            rows["csv_wait_error"] = str(e)
            fails.append("csv_no_maps")
        page.wait_for_timeout(1200)
        csv_dlgs = dialogs[before_n:]
        csv_alerts = " ".join(d["message"] for d in csv_dlgs if d["type"] == "alert")
        csv_confirms = [d["message"] for d in csv_dlgs if d["type"] == "confirm"]
        rows["csv"] = {
            "maps": csv_maps,
            "alerts": csv_alerts[:400],
            "confirm": (csv_confirms[-1][:500] if csv_confirms else ""),
            "fallback": FALLBACK_SNIP in csv_alerts,
        }
        if FALLBACK_SNIP in csv_alerts:
            fails.append("csv_fallback")
        if not csv_confirms:
            fails.append("csv_no_confirm")
        if csv_maps:
            fails.extend(["csv:" + f for f in check_nov1(csv_maps)])

        # --- B. XLSX + picker ---
        clear_maps(page)
        before_n = len(dialogs)
        upload(page, "#past-sales-modal-csv", BARCA_XLSX)
        picker_vis = False
        try:
            page.wait_for_selector("#kpi-excel-sheet-picker", timeout=20000)
            picker_vis = True
            select_sheet(page, "日次レポート")
        except Exception as e:
            rows["xlsx_picker_error"] = str(e)
            fails.append("xlsx_no_picker")
        xlsx_maps = None
        try:
            xlsx_maps = wait_maps(page, 30000)
        except Exception as e:
            rows["xlsx_wait_error"] = str(e)
            fails.append("xlsx_no_maps")
        page.wait_for_timeout(1200)
        xlsx_dlgs = dialogs[before_n:]
        xlsx_alerts = " ".join(d["message"] for d in xlsx_dlgs if d["type"] == "alert")
        xlsx_confirms = [d["message"] for d in xlsx_dlgs if d["type"] == "confirm"]
        rows["xlsx"] = {
            "picker": picker_vis,
            "maps": xlsx_maps,
            "alerts": xlsx_alerts[:400],
            "confirm": (xlsx_confirms[-1][:500] if xlsx_confirms else ""),
            "fallback": FALLBACK_SNIP in xlsx_alerts,
        }
        if FALLBACK_SNIP in xlsx_alerts:
            fails.append("xlsx_fallback")
        if not picker_vis:
            fails.append("xlsx_picker")
        if not xlsx_confirms:
            fails.append("xlsx_no_confirm")
        if xlsx_maps:
            fails.extend(["xlsx:" + f for f in check_nov1(xlsx_maps)])

        # --- vertical regression ---
        clear_maps(page)
        before_n = len(dialogs)
        upload(page, "#past-sales-modal-csv", VERTICAL_CSV)
        vert_maps = None
        try:
            vert_maps = wait_maps(page, 20000)
        except Exception as e:
            rows["vertical_csv_wait_error"] = str(e)
            fails.append("vertical_csv_no_maps")
        page.wait_for_timeout(800)
        v_dlgs = dialogs[before_n:]
        v_alerts = " ".join(d["message"] for d in v_dlgs if d["type"] == "alert")
        v_confirms = [d["message"] for d in v_dlgs if d["type"] == "confirm"]
        rows["vertical_csv"] = {
            "maps": vert_maps,
            "fallback": FALLBACK_SNIP in v_alerts,
            "confirm": bool(v_confirms),
        }
        if FALLBACK_SNIP in v_alerts:
            fails.append("vertical_csv_fallback")
        if not v_confirms:
            fails.append("vertical_csv_no_confirm")
        if vert_maps:
            if vert_maps.get("layout") == "horizontal":
                fails.append("vertical_csv_misdetected")
            if (vert_maps.get("salesByDate") or {}).get("2025-03-02") != 12345:
                fails.append("vertical_csv_sales")

        clear_maps(page)
        before_n = len(dialogs)
        upload(page, "#past-sales-modal-csv", VERTICAL_XLSX)
        vx_maps = None
        try:
            vx_maps = wait_maps(page, 20000)
        except Exception as e:
            rows["vertical_xlsx_wait_error"] = str(e)
            fails.append("vertical_xlsx_no_maps")
        page.wait_for_timeout(800)
        vx_dlgs = dialogs[before_n:]
        vx_alerts = " ".join(d["message"] for d in vx_dlgs if d["type"] == "alert")
        vx_confirms = [d["message"] for d in vx_dlgs if d["type"] == "confirm"]
        rows["vertical_xlsx"] = {
            "maps": vx_maps,
            "fallback": FALLBACK_SNIP in vx_alerts,
            "confirm": bool(vx_confirms),
        }
        if FALLBACK_SNIP in vx_alerts:
            fails.append("vertical_xlsx_fallback")
        if not vx_confirms:
            fails.append("vertical_xlsx_no_confirm")
        if vx_maps and vx_maps.get("layout") == "horizontal":
            fails.append("vertical_xlsx_misdetected")

        try:
            js_click(page, "#past-sales-modal-close")
        except Exception:
            pass
        page.close()
        ctx.close()

        # Basic: can Past Sales open, and would expenses be visible? Observe gate + confirm cancel.
        jar_b, opener_b, me_b = login(BASIC_EMAIL, basic_pw)
        rows["basic_plan"] = me_b.get("plan")
        ctx_b = browser.new_context(viewport={"width": 1440, "height": 900})
        ctx_b.add_cookies(cookies_for_playwright(jar_b))
        page_b = ctx_b.new_page()
        page_b.on("dialog", on_dialog)
        if not args.production:
            install_local_overrides(page_b)
        page_b.goto(ANNUAL, wait_until="load", timeout=180000)
        wait_app(page_b)
        page_b.wait_for_function(
            """() => {
              const api = window.KpiBusinessType;
              return !!(api && api.isBusinessTypeSet && api.isBusinessTypeSet());
            }""",
            timeout=45000,
        )
        hook_maps(page_b)
        try:
            enable_past_sales_edit(page_b)
            rows["basic_past_sales_open"] = True
            clear_maps(page_b)
            before_n = len(dialogs)
            upload(page_b, "#past-sales-modal-csv", BARCA_CSV)
            b_maps = wait_maps(page_b, 30000)
            page_b.wait_for_timeout(800)
            b_dlgs = dialogs[before_n:]
            b_alerts = " ".join(d["message"] for d in b_dlgs if d["type"] == "alert")
            rows["basic_csv"] = {
                "imported": (b_maps or {}).get("imported"),
                "layout": (b_maps or {}).get("layout"),
                "expenseLabels": (b_maps or {}).get("expenseLabels"),
                "unmatchedCount": (b_maps or {}).get("unmatchedCount"),
                "fallback": FALLBACK_SNIP in b_alerts,
                "confirm": any(d["type"] == "confirm" for d in b_dlgs),
            }
            if FALLBACK_SNIP in b_alerts:
                fails.append("basic_csv_fallback")
        except Exception as e:
            rows["basic_error"] = str(e)
            fails.append("basic_past_sales")
        try:
            js_click(page_b, "#past-sales-modal-close")
        except Exception:
            pass
        page_b.close()
        ctx_b.close()
        browser.close()

    _c, st_after = api_call(opener, "GET", "/store.php")
    fp_after = store_fp(st_after)
    de_after = daily_expenses_fp(st_after)
    rows["store_fp_after"] = fp_after
    rows["daily_expenses_fp_after"] = de_after
    rows["demo_pro_unchanged"] = fp_before == fp_after
    rows["daily_expenses_unchanged"] = de_before == de_after
    if fp_before != fp_after:
        fails.append("demo_pro_mutated")
    if de_before != de_after:
        fails.append("daily_expenses_mutated")

    expense = {
        "recognized_as_expense_kind": bool((csv_maps or {}).get("expenseLabels")),
        "labels": (csv_maps or {}).get("expenseLabels") or [],
        "unmatchedCount": (csv_maps or {}).get("unmatchedCount"),
        "in_confirm_preview": False,
        "persisted_on_past_sales_cancel": False,
        "daily_expenses_changed": de_before != de_after,
        "note": (
            "Past Sales applyMaps writes sales/biz/meal maps only. unmatchedMetrics are not "
            "shown in the confirm dialog and are not written to dailyExpenses. Confirm was dismissed."
        ),
    }
    confirm_txt = rows.get("csv", {}).get("confirm") or ""
    expense["in_confirm_preview"] = "仕入" in confirm_txt or "費目" in confirm_txt
    rows["expense_behavior"] = expense

    unique = []
    for f in fails:
        if f not in unique:
            unique.append(f)
    out = {"ok": not unique, "fails": unique, "rows": rows}
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps({"ok": out["ok"], "fails": unique, "mode": rows["mode"]}, ensure_ascii=False))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

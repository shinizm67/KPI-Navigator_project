# -*- coding: utf-8 -*-
"""Local UI smoke: unresolved business-day review in existing Setup alert."""

from __future__ import annotations

import http.server
import json
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PORT = 8878
OUT = ROOT / "scripts" / "_tmp_bdr_ui_smoke.json"

PAGES = [
    ("ja", "/app/annual/index.html", "過去営業日確認", "日未確定", "確認する", "すべて店休日", "個別に確認", "あとで", "営業日", "店休日"),
    ("en", "/en/app/annual/index.html", "Past business days", "days unconfirmed", "Review", "All closed days", "Review one by one", "Later", "Open", "Closed"),
    ("zh", "/zh-tw/app/annual/index.html", "過去營業日確認", "日未確定", "確認", "全部設為店休日", "逐日確認", "稍後", "營業日", "店休日"),
]


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *_a):
        pass


SEED = {
    "2025-11-03": {
        "sales": 0,
        "customers": 0,
        "parties": 0,
        "expense": 8400,
        "reason": "expense-only",
    },
    "2025-11-10": {
        "sales": 0,
        "customers": 0,
        "parties": 0,
        "expense": 1200,
        "reason": "expense-only",
    },
}


def seed_unresolved(page, recs: dict) -> int:
    return page.evaluate(
        """(recs) => {
          const api = window.KpiYearStore;
          const pr = window.KpiPlanningReadiness;
          if (!api || !pr) return -1;
          const store = api.getStore();
          if (!store.timeline) store.timeline = {};
          store.timeline.businessDayUnresolved = JSON.parse(JSON.stringify(recs || {}));
          try { sessionStorage.removeItem('kpi-pr-alert-dismissed'); } catch (e) {}
          pr.renderAlertFw({ force: true });
          return api.unresolvedBusinessDayCount();
        }""",
        recs,
    )


def alert_text(page) -> str:
    return page.evaluate(
        """() => {
          const el = document.getElementById('kpi-pr-alert-fw');
          return el ? (el.innerText || '') : '';
        }"""
    )


def run_page(page, path: str, copy: tuple, office: bool) -> dict:
    (
        _lang,
        _path,
        item,
        count_word,
        review,
        all_closed,
        one_by_one,
        later,
        open_lab,
        closed_lab,
    ) = copy
    errs: list[str] = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(f"http://127.0.0.1:{PORT}{path}", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("() => !!(window.KpiYearStore && window.KpiPlanningReadiness)", timeout=30000)
    page.wait_for_timeout(800)
    page.evaluate(
        """(office) => {
          document.body.classList.toggle('office-mode', !!office);
          const dlg = document.getElementById('kpi-demo-confirm') || document.querySelector('[data-demo-confirm]');
          if (dlg) dlg.remove();
        }""",
        office,
    )

    n0 = seed_unresolved(page, {})
    text0 = alert_text(page)
    page.wait_for_timeout(120)

    n1 = seed_unresolved(page, {"2025-11-03": SEED["2025-11-03"]})
    text1 = alert_text(page)

    n2 = seed_unresolved(page, SEED)
    text2 = alert_text(page)
    page.locator('#kpi-pr-alert-fw [data-pr-act="hist-review"]').click()
    page.wait_for_timeout(80)
    choose = alert_text(page)
    page.locator('#kpi-pr-alert-fw [data-pr-act="hist-all-closed"]').click()
    page.wait_for_timeout(160)
    after_bulk = page.evaluate("() => window.KpiYearStore.unresolvedBusinessDayCount()")
    text_after_bulk = alert_text(page)

    seed_unresolved(page, SEED)
    page.locator('#kpi-pr-alert-fw [data-pr-act="hist-review"]').click()
    page.wait_for_timeout(80)
    page.locator('#kpi-pr-alert-fw [data-pr-act="hist-one"]').click()
    page.wait_for_timeout(80)
    one_txt = alert_text(page)
    page.locator('#kpi-pr-alert-fw [data-pr-act="hist-closed"]').click()
    page.wait_for_timeout(80)
    mid = page.evaluate("() => window.KpiYearStore.unresolvedBusinessDayCount()")
    page.locator('#kpi-pr-alert-fw [data-pr-act="hist-later"]').click()
    page.wait_for_timeout(80)
    dismissed = page.evaluate(
        """() => ({
          gone: !document.getElementById('kpi-pr-alert-fw'),
          session: sessionStorage.getItem('kpi-pr-alert-dismissed'),
          left: window.KpiYearStore.unresolvedBusinessDayCount(),
        })"""
    )
    page.evaluate("() => window.KpiPlanningReadiness.showPageEntryAlert(false)")
    page.wait_for_timeout(80)
    still_gone = page.evaluate("() => !document.getElementById('kpi-pr-alert-fw')")
    page.evaluate(
        """() => {
          sessionStorage.removeItem('kpi-pr-alert-dismissed');
          window.KpiPlanningReadiness.showPageEntryAlert(true);
        }"""
    )
    page.wait_for_timeout(80)
    reopened = alert_text(page)

    seed_unresolved(page, SEED)
    page.locator('#kpi-pr-alert-fw [data-pr-act="hist-review"]').click()
    page.locator('#kpi-pr-alert-fw [data-pr-act="hist-all-open"]').click()
    page.wait_for_timeout(160)
    after_open = page.evaluate("() => window.KpiYearStore.unresolvedBusinessDayCount()")

    fails = []
    if n0 != 0:
        fails.append(f"zero_count={n0}")
    if item in text0:
        fails.append("zero_still_shows_item")
    if item not in text1:
        fails.append("one_missing_item")
    if "1" not in text1:
        fails.append("one_missing_1")
    if n2 != 2:
        fails.append(f"many_count={n2}")
    if "2" not in text2:
        fails.append("many_missing_2")
    if all_closed not in choose or one_by_one not in choose:
        fails.append("choose_missing_actions")
    if after_bulk != 0:
        fails.append(f"bulk_closed_left={after_bulk}")
    if item in text_after_bulk:
        fails.append("bulk_item_still_visible")
    if open_lab not in one_txt or closed_lab not in one_txt:
        fails.append("one_by_one_missing_buttons")
    if "2025/11/" not in one_txt and "2025-11-" not in one_txt:
        fails.append("one_by_one_missing_date")
    if mid != 1:
        fails.append(f"one_resolve_left={mid}")
    if not dismissed.get("gone") or dismissed.get("session") != "1":
        fails.append(f"later={dismissed}")
    if dismissed.get("left") != 1:
        fails.append(f"later_cleared_state={dismissed.get('left')}")
    if not still_gone:
        fails.append("session_redisplay")
    if item not in reopened:
        fails.append("reopen_missing_item")
    if after_open != 0:
        fails.append(f"bulk_open_left={after_open}")
    if office and "office-mode" not in page.evaluate("() => document.body.className"):
        fails.append("office_class_missing")
    return {
        "path": path,
        "office": office,
        "fails": fails,
        "page_errors": errs[:8],
        "review": review,
        "later": later,
    }


def main() -> int:
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), H)
    httpd.allow_reuse_address = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    results = []
    failed = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, channel="msedge")
            for copy in PAGES:
                for office in (False, True):
                    page = browser.new_page()
                    rec = run_page(page, copy[1], copy, office)
                    page.close()
                    results.append(rec)
                    if rec["fails"] or rec["page_errors"]:
                        failed += 1
                        print("FAIL", copy[0], "office" if office else "scifi", rec["fails"], rec["page_errors"])
                    else:
                        print("OK", copy[0], "office" if office else "scifi")
            browser.close()
    finally:
        httpd.shutdown()
        httpd.server_close()
    OUT.write_text(json.dumps({"failed": failed, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("failed", failed, "cases", len(results))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

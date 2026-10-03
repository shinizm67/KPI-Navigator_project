# -*- coding: utf-8 -*-
"""Browser smoke for the import recovery modal. No production account."""
from __future__ import annotations

import json
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _test_multi_business_upload_smoke as mb  # noqa: E402

OUT = ROOT / "tests" / "results" / "import-recovery-smoke.json"
FIXTURE = ROOT / "tests" / "results" / "_recovery_fixtures"
BAD_SALES = "date,amount_unknown,memo\n2026-04-01,100,note\n"
GOOD_SALES = "date,business_day,daily_sales\n日付,営業日,日次売上\n2026-06-15,1,120000\n"
BAD_EXPENSE = "hello,world\nfoo,bar\n"
MAP_EXPENSE = "date,item,amount\n2026-04-02,ZZZ Recovery Fee,1000\n"


def write_fixtures() -> dict[str, Path]:
    FIXTURE.mkdir(parents=True, exist_ok=True)
    files = {
        "bad_sales": FIXTURE / "bad_sales.csv",
        "good_sales": FIXTURE / "good_sales.csv",
        "bad_expense": FIXTURE / "bad_expense.csv",
        "map_expense": FIXTURE / "map_expense.csv",
    }
    files["bad_sales"].write_text(BAD_SALES, encoding="utf-8")
    files["good_sales"].write_text(GOOD_SALES, encoding="utf-8")
    files["bad_expense"].write_text(BAD_EXPENSE, encoding="utf-8")
    files["map_expense"].write_text(MAP_EXPENSE, encoding="utf-8")
    return files


def boot(browser, path: str):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True)
    page = ctx.new_page()
    errors = []
    page.add_init_script(
        """
        window.__MB_HYDRATED = false;
        document.addEventListener('kpi:storeHydrateSettled', function () { window.__MB_HYDRATED = true; });
        """
    )
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda dialog: dialog.accept())
    mb.STATE.reset()
    page.goto(f"http://127.0.0.1:{mb.PORT}{path}", wait_until="domcontentloaded", timeout=120000)
    return ctx, page, errors


def prepare(page, business_type: str, need_store: bool) -> None:
    mb.wait_user(page, need_store)
    mb.STATE.arm()
    mb.set_business_type(page, business_type)


def modal_snapshot(page) -> dict:
    return page.evaluate(
        """() => {
          const root = document.getElementById('kpi-import-recovery');
          if (!root) return null;
          const steps = root.querySelectorAll('#kpi-import-recovery-steps li');
          const buttons = Array.from(root.querySelectorAll('button')).map((b) => b.textContent);
          return {
            kind: root.getAttribute('data-recovery-kind'),
            category: root.getAttribute('data-recovery-category'),
            entry: root.getAttribute('data-recovery-entry'),
            restaurant: root.getAttribute('data-recovery-restaurant'),
            past: root.getAttribute('data-recovery-past'),
            reason: (document.getElementById('kpi-import-recovery-reason') || {}).textContent || '',
            protect: (document.getElementById('kpi-import-recovery-protect') || {}).textContent || '',
            restaurantText: (document.getElementById('kpi-import-recovery-restaurant') || {}).textContent || '',
            pastText: (document.getElementById('kpi-import-recovery-past') || {}).textContent || '',
            daily: (document.getElementById('kpi-import-recovery-daily') || {}).textContent || '',
            monthly: (document.getElementById('kpi-import-recovery-monthly') || {}).textContent || '',
            stepCount: steps.length,
            buttons: buttons
          };
        }"""
    )


def sales_count(page) -> int:
    return page.evaluate(
        """() => {
          const snap = (%s)();
          return Object.keys((snap && snap.sales) || {}).length;
        }"""
        % mb.READ_JS.strip()
    )


def wait_modal(page) -> dict:
    page.wait_for_selector("#kpi-import-recovery", timeout=20000)
    return modal_snapshot(page)


def record(rows, case_id, ok, detail) -> None:
    rows.append({"id": case_id, "status": "PASS" if ok else "FAIL", "detail": detail})


def open_bad_sales(page, button_id: str, bad: Path) -> dict:
    mb.choose_file(page, button_id, bad)
    return wait_modal(page)


def main() -> int:
    from playwright.sync_api import sync_playwright

    files = write_fixtures()
    rows = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), mb.Handler)
    mb.PORT = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            ctx, page, errors = boot(browser, "/app/annual/index.html")
            prepare(page, "restaurant", True)
            mb.open_current_sales(page)
            before = sales_count(page)
            snap = open_bad_sales(page, "sales-data-modal-csv", files["bad_sales"])
            after = sales_count(page)
            record(
                rows,
                "R1",
                snap
                and snap["kind"] == "sales"
                and snap["category"] in ("A", "D")
                and snap["entry"] == "current-year"
                and after == before,
                snap,
            )
            with page.expect_download(timeout=15000) as dl:
                page.locator("#kpi-import-recovery-download-sales").click()
            download = dl.value
            body = Path(download.path()).read_text(encoding="utf-8-sig")
            first = body.splitlines()[0] if body else ""
            record(
                rows,
                "R2",
                download.suggested_filename == "sales_template.csv"
                and first.startswith("date,business_day,daily_sales")
                and "雛形の1行目" not in body,
                {"file": download.suggested_filename, "header": first},
            )
            current_open = page.evaluate(
                "() => { const m = document.getElementById('sales-data-modal'); return !!(m && !m.hasAttribute('hidden')); }"
            )
            with page.expect_file_chooser(timeout=15000) as fc:
                page.locator("#kpi-import-recovery-retry").click()
            fc.value.set_files(str(files["good_sales"]))
            record(rows, "R3", current_open and snap["entry"] == "current-year", {"currentOpen": current_open})
            page.wait_for_function(
                """() => {
                  const s = (%s)();
                  return s && s.sales && s.sales['2026-06-15'] === 120000;
                }"""
                % mb.READ_JS.strip(),
                timeout=30000,
            )
            page.reload(wait_until="domcontentloaded", timeout=120000)
            mb.wait_user(page, True)
            kept = page.evaluate(
                """() => {
                  const s = (%s)();
                  return s && s.sales ? s.sales['2026-06-15'] : null;
                }"""
                % mb.READ_JS.strip()
            )
            record(rows, "R4", kept == 120000, {"reloaded": kept})
            record(
                rows,
                "R7",
                snap and snap["restaurant"] == "1" and "ディナー" in (snap.get("restaurantText") or ""),
                snap.get("restaurantText") if snap else None,
            )
            record(rows, "JP", len(errors) == 0 and snap and snap["stepCount"] == 4 and len(snap["buttons"]) == 3, {"pageerror": errors[:4], "buttons": snap["buttons"] if snap else None})
            ctx.close()

            ctx, page, errors = boot(browser, "/app/annual/index.html")
            prepare(page, "hotel", True)
            mb.open_current_sales(page)
            hotel = open_bad_sales(page, "sales-data-modal-csv", files["bad_sales"])
            record(
                rows,
                "R8",
                hotel and hotel["restaurant"] == "0" and not hotel.get("restaurantText"),
                hotel,
            )
            ctx.close()

            ctx, page, errors = boot(browser, "/app/annual/index.html")
            prepare(page, "restaurant", True)
            mb.open_past_sales(page)
            past = open_bad_sales(page, "past-sales-modal-csv", files["bad_sales"])
            past_open = page.evaluate(
                "() => { const m = document.getElementById('past-sales-modal'); return !!(m && !m.hasAttribute('hidden')); }"
            )
            with page.expect_file_chooser(timeout=15000) as fc:
                page.locator("#kpi-import-recovery-retry").click()
            fc.value.set_files(str(files["bad_sales"]))
            page.wait_for_selector("#kpi-import-recovery", timeout=20000)
            record(
                rows,
                "R5",
                past
                and past["entry"] == "past-sales"
                and past["past"] == "1"
                and "今年より前" in (past.get("pastText") or "")
                and past_open,
                past,
            )
            ctx.close()

            ctx, page, errors = boot(browser, "/app/monthly/edit/index.html")
            prepare(page, "restaurant", True)
            mb.open_mep(page)
            mep = open_bad_sales(page, "monthly-edit-float-csv-upload", files["bad_sales"])
            with page.expect_file_chooser(timeout=15000) as fc:
                page.locator("#kpi-import-recovery-retry").click()
            fc.value.set_files(str(files["bad_sales"]))
            record(
                rows,
                "R6",
                bool(mep) and mep["entry"] == "mep" and mep["past"] == "0",
                mep,
            )
            ctx.close()

            ctx, page, errors = boot(browser, "/app/profit/pl/index.html?year=2026")
            prepare(page, "restaurant", False)
            mb.choose_file(page, "pl-csv-upload", files["bad_expense"])
            expense = wait_modal(page)
            record(
                rows,
                "R9",
                expense
                and expense["kind"] == "expense"
                and expense["entry"] == "pl-expense"
                and expense["buttons"]
                and len(expense["buttons"]) == 4
                and "日付" in (expense.get("daily") or "")
                and "年月" in (expense.get("monthly") or ""),
                expense,
            )
            page.locator("#kpi-import-recovery-close").click()
            mb.choose_file(page, "pl-csv-upload", files["map_expense"])
            page.wait_for_selector(".pl-import-map__escape", timeout=20000)
            escape = page.evaluate(
                """() => {
                  const box = document.querySelector('.pl-import-map__escape');
                  const buttons = Array.from(document.querySelectorAll('[data-recovery-template]')).map((b) => b.getAttribute('data-recovery-template'));
                  return { text: box ? box.textContent : '', buttons: buttons };
                }"""
            )
            record(
                rows,
                "R10",
                escape
                and "費目の対応が難しい" in escape["text"]
                and escape["buttons"] == ["expense-daily", "expense-monthly"],
                escape,
            )
            ctx.close()

            ctx, page, errors = boot(browser, "/en/app/annual/index.html")
            prepare(page, "restaurant", True)
            mb.open_current_sales(page)
            en = open_bad_sales(page, "sales-data-modal-csv", files["bad_sales"])
            record(
                rows,
                "EN",
                en
                and en["stepCount"] == 4
                and en["buttons"] == ["Download template", "Upload again", "Close"]
                and en["reason"] == "The sales column could not be identified"
                and "Leave row 1 and row 2" in en["protect"]
                and "dinner" in (en.get("restaurantText") or "")
                and len(errors) == 0,
                en,
            )
            ctx.close()

            ctx, page, errors = boot(browser, "/zh-tw/app/annual/index.html")
            prepare(page, "restaurant", True)
            mb.open_current_sales(page)
            zh = open_bad_sales(page, "sales-data-modal-csv", files["bad_sales"])
            record(
                rows,
                "ZH-TW",
                zh
                and zh["stepCount"] == 4
                and zh["buttons"] == ["下載範本", "再上傳一次", "關閉"]
                and zh["reason"] == "無法判斷哪一欄是銷售"
                and "第1列和第2列" in zh["protect"]
                and "晚餐" in (zh.get("restaurantText") or "")
                and len(errors) == 0,
                zh,
            )
            ctx.close()
            browser.close()
    finally:
        server.shutdown()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "results": rows,
        "passed": sum(1 for row in rows if row["status"] == "PASS"),
        "failed": sum(1 for row in rows if row["status"] == "FAIL"),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

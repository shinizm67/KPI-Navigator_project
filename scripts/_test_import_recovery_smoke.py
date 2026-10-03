# -*- coding: utf-8 -*-
"""Browser smoke for the import recovery modal. No production account."""
from __future__ import annotations

import json
import re
import shutil
import sys
import threading
import zipfile
import xml.etree.ElementTree as ET
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
REQUIRED_KEYS = ("date", "business_day", "daily_sales")
RESTAURANT_ONLY = (
    "lunch_sales",
    "dinner_sales",
    "total_customers",
    "lunch_customers",
    "dinner_customers",
    "total_groups",
    "lunch_groups",
    "dinner_groups",
    "food_sales",
    "drink_sales",
)
ROW2 = {
    "ja": ("日付", "営業日", "日次売上"),
    "en": ("date", "business day", "daily sales"),
    "zh-tw": ("日期", "營業日", "日次銷售"),
}
FILENAMES = {
    "ja": "KPN_売上入力雛形.xlsx",
    "en": "KPN_Sales_Template.xlsx",
    "zh-tw": "KPN_銷售範本.xlsx",
}
SHEETS = {"ja": "売上", "en": "Sales", "zh-tw": "銷售"}
JA_STEPS = [
    "Excel雛形をダウンロード",
    "元のファイルから「日付」と「売上」をコピー",
    "雛形の3行目から貼り付け",
    "もう一度アップロード",
]
EN_STEPS = [
    "Download the Excel template",
    "Copy the date and sales from your file",
    "Paste from row 3 of the template",
    "Upload again",
]
ZH_STEPS = [
    "下載 Excel 範本",
    "從原本的檔案複製「日期」和「銷售」",
    "從範本第3列貼上",
    "再上傳一次",
]
JA_BUTTONS = ["Excel雛形をダウンロード", "CSV雛形", "もう一度アップロード", "閉じる"]
EN_BUTTONS = ["Download Excel template", "CSV template", "Upload again", "Close"]
ZH_BUTTONS = ["下載 Excel 範本", "CSV 範本", "再上傳一次", "關閉"]
ONE_ISO = "2026-08-20"
ONE_AMOUNT = 88000


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
    sheetjs = mb.ensure_sheetjs()
    ctx.route(
        "**/xlsx.full.min.js",
        lambda route: route.fulfill(path=str(sheetjs), content_type="text/javascript"),
    )
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
          const steps = Array.from(root.querySelectorAll('#kpi-import-recovery-steps li')).map((li) => li.textContent);
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
            steps: steps,
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


NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def sheetjs_wch(width) -> float | None:
    if width is None:
        return None
    # SheetJS 0.18.5 stores wch as OOXML width with MDW 6.
    return (float(width) * 6 - 5) / 6


def col_letter(index: int) -> str:
    letters = ""
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def col_index(letters: str) -> int:
    index = 0
    for ch in letters:
        index = index * 26 + (ord(ch) - 64)
    return index


def ref_cell(ref: str) -> tuple[str, int]:
    match = re.match(r"([A-Z]+)(\d+)", ref or "")
    if not match:
        return "", 0
    return match.group(1), int(match.group(2))


def inspect_xlsx(path: Path) -> dict:
    with zipfile.ZipFile(path) as book:
        workbook = ET.fromstring(book.read("xl/workbook.xml"))
        sheet = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
    names = [el.attrib.get("name", "") for el in workbook.findall("m:sheets/m:sheet", NS)]
    dimension = sheet.find("m:dimension", NS)
    end = (dimension.attrib.get("ref", "A1:A1").split(":")[-1] if dimension is not None else "A1")
    end_col, end_row = ref_cell(end)
    width_count = col_index(end_col) if end_col else 0
    widths = [None] * width_count
    for col in sheet.findall("m:cols/m:col", NS):
        start = int(col.attrib.get("min", "0"))
        stop = int(col.attrib.get("max", "0"))
        width = float(col.attrib["width"]) if "width" in col.attrib else None
        for index in range(start, stop + 1):
            if 1 <= index <= width_count:
                widths[index - 1] = width
    by_row: dict[int, dict[str, str]] = {}
    for row in sheet.findall("m:sheetData/m:row", NS):
        number = int(row.attrib.get("r", "0"))
        cells: dict[str, str] = {}
        for cell in row.findall("m:c", NS):
            letter, _row_number = ref_cell(cell.attrib.get("r", ""))
            value = cell.find("m:v", NS)
            cells[letter] = "" if value is None or value.text is None else value.text.strip()
        by_row[number] = cells
    rows = []
    for number in range(1, end_row + 1):
        cells = by_row.get(number, {})
        rows.append([cells.get(col_letter(index), "") for index in range(1, width_count + 1)])
    return {
        "sheets": names,
        "rows": rows,
        "widths": widths,
        "max_row": end_row,
        "wch": [sheetjs_wch(width) for width in widths],
    }


def save_download(download, name: str) -> tuple[str, Path]:
    dest = FIXTURE / name
    shutil.copy(download.path(), dest)
    return download.suggested_filename, dest


def download_click(page, selector: str, name: str) -> tuple[str, Path]:
    with page.expect_download(timeout=20000) as caught:
        page.locator(selector).click()
    return save_download(caught.value, name)


def write_one_data_row(src: Path, dest: Path) -> None:
    with zipfile.ZipFile(src) as book:
        files = {name: book.read(name) for name in book.namelist()}
    xml = files["xl/worksheets/sheet1.xml"].decode("utf-8")
    for ref, value in (("A3", ONE_ISO), ("B3", "1"), ("C3", str(ONE_AMOUNT))):
        updated, count = re.subn(
            rf'(<c r="{ref}"[^>]*>\s*<v>)(.*?)(</v>)',
            rf"\g<1>{value}\g<3>",
            xml,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"missing cell {ref}")
        xml = updated
    files["xl/worksheets/sheet1.xml"] = xml.encode("utf-8")
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as book:
        for name, payload in files.items():
            book.writestr(name, payload)


def store_dates(page) -> dict:
    return page.evaluate(
        """() => {
          const s = (%s)();
          return {
            sales: Object.keys((s && s.sales) || {}),
            days: Object.keys((s && s.businessDays) || {}),
            amount: s && s.sales ? s.sales[%r] : null
          };
        }"""
        % (mb.READ_JS.strip(), ONE_ISO)
    )


def template_view(info: dict, filename: str, locale: str) -> dict:
    header = info["rows"][0] if info["rows"] else []
    labels = info["rows"][1] if len(info["rows"]) > 1 else []
    data = info["rows"][2:] if len(info["rows"]) > 2 else []
    blank = sum(1 for row in data if not any(cell for cell in row))
    sample = [cell for row in data for cell in row if cell]
    wch = [n for n in info["wch"] if n is not None]
    required = wch[:3]
    return {
        "file": filename == FILENAMES[locale],
        "oneSheet": info["sheets"] == [SHEETS[locale]],
        "sheetName": bool(info["sheets"]) and info["sheets"][0] == SHEETS[locale],
        "keys": tuple(header[:3]) == REQUIRED_KEYS,
        "labels": tuple(labels[:3]) == ROW2[locale],
        "noSample": sample == [],
        "blank31": blank == 31 and len(data) == 31,
        "widths": len(info["widths"]) == len(header) and bool(header) and all(w is not None for w in info["widths"]),
        "requiredWidth": len(required) == 3 and all(n >= 15.9 for n in required),
        "cap": bool(wch) and all(n <= 22.05 for n in wch),
        "restaurant": all(key in header for key in RESTAURANT_ONLY),
        "commonOnly": header == list(REQUIRED_KEYS),
        "detail": {
            "file": filename,
            "sheets": info["sheets"],
            "header": header,
            "labels": labels[:3],
            "blank": blank,
            "sample": sample[:6],
            "wch": [None if n is None else round(n, 2) for n in info["wch"]],
        },
    }


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
            xlsx_name, xlsx_path = download_click(page, "#kpi-import-recovery-download-sales", "recovery_sales_ja.xlsx")
            view = template_view(inspect_xlsx(xlsx_path), xlsx_name, "ja")
            record(
                rows,
                "R2",
                view["file"] and view["oneSheet"] and view["keys"] and view["noSample"],
                view["detail"],
            )
            record(rows, "T1", view["file"], view["detail"])
            record(rows, "T2", view["oneSheet"], view["detail"])
            record(rows, "T3", view["sheetName"], view["detail"])
            record(rows, "T4", view["keys"], view["detail"])
            record(rows, "T5", view["labels"], view["detail"])
            record(rows, "T6", view["noSample"], view["detail"])
            record(rows, "T7", view["blank31"], view["detail"])
            record(rows, "T8", view["widths"], view["detail"])
            record(rows, "T9", view["requiredWidth"], view["detail"])
            record(rows, "T10", view["cap"], view["detail"])
            record(rows, "T11", view["restaurant"], view["detail"])
            csv_name, csv_path = download_click(page, "#kpi-import-recovery-download-csv", "recovery_sales.csv")
            csv_body = csv_path.read_text(encoding="utf-8-sig")
            csv_first = csv_body.splitlines()[0] if csv_body else ""
            record(
                rows,
                "T13",
                csv_name == "sales_template.csv"
                and csv_first.startswith("date,business_day,daily_sales")
                and "lunch_sales" in csv_first
                and "雛形の1行目" not in csv_body,
                {"file": csv_name, "header": csv_first},
            )
            still = modal_snapshot(page)
            record(
                rows,
                "T14",
                still
                and still["entry"] == "current-year"
                and still["buttons"] == JA_BUTTONS
                and "もう一度アップロード" in still["buttons"],
                still,
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
            server_kept = mb.wait_server_sales("2026-06-15", 120000, timeout_s=10)
            page.reload(wait_until="domcontentloaded", timeout=120000)
            mb.wait_user(page, True)
            kept = None
            for _poll in range(20):
                kept = page.evaluate(
                    """() => {
                      const s = (%s)();
                      return s && s.sales ? s.sales['2026-06-15'] : null;
                    }"""
                    % mb.READ_JS.strip()
                )
                if kept == 120000:
                    break
                page.wait_for_timeout(250)
            record(rows, "R4", server_kept and kept == 120000, {"reloaded": kept, "server": server_kept})
            before_dates = store_dates(page)
            mb.open_current_sales(page)
            open_bad_sales(page, "sales-data-modal-csv", files["bad_sales"])
            populated = FIXTURE / "recovery_one_row.xlsx"
            write_one_data_row(xlsx_path, populated)
            with page.expect_file_chooser(timeout=15000) as fc:
                page.locator("#kpi-import-recovery-retry").click()
            fc.value.set_files(str(populated))
            page.wait_for_function(
                """() => {
                  const s = (%s)();
                  return s && s.sales && s.sales[%r] === %d;
                }"""
                % (mb.READ_JS.strip(), ONE_ISO, ONE_AMOUNT),
                timeout=30000,
            )
            after_dates = store_dates(page)
            new_sales = set(after_dates["sales"]) - set(before_dates["sales"])
            new_days = set(after_dates["days"]) - set(before_dates["days"])
            record(
                rows,
                "T15",
                after_dates["amount"] == ONE_AMOUNT and new_sales == {ONE_ISO},
                {"amount": after_dates["amount"], "newSales": sorted(new_sales)},
            )
            record(
                rows,
                "T16",
                new_sales == {ONE_ISO}
                and new_days <= {ONE_ISO}
                and ONE_ISO != "2026-06-15"
                and "2026-06-15" in after_dates["sales"],
                {"newSales": sorted(new_sales), "newDays": sorted(new_days), "sales": after_dates["sales"]},
            )
            record(
                rows,
                "R7",
                snap and snap["restaurant"] == "1" and "ディナー" in (snap.get("restaurantText") or ""),
                snap.get("restaurantText") if snap else None,
            )
            record(
                rows,
                "JP",
                len(errors) == 0
                and snap
                and snap["stepCount"] == 4
                and snap.get("steps") == JA_STEPS
                and snap["buttons"] == JA_BUTTONS,
                {"pageerror": errors[:4], "buttons": snap["buttons"] if snap else None, "steps": snap.get("steps") if snap else None},
            )
            ctx.close()

            ctx, page, errors = boot(browser, "/app/annual/index.html")
            prepare(page, "hotel", True)
            mb.open_current_sales(page)
            hotel = open_bad_sales(page, "sales-data-modal-csv", files["bad_sales"])
            hotel_name, hotel_path = download_click(page, "#kpi-import-recovery-download-sales", "recovery_sales_hotel.xlsx")
            hotel_view = template_view(inspect_xlsx(hotel_path), hotel_name, "ja")
            record(rows, "T12", hotel_view["commonOnly"] and hotel_view["file"], hotel_view["detail"])
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
            en_name, en_path = download_click(page, "#kpi-import-recovery-download-sales", "recovery_sales_en.xlsx")
            en_view = template_view(inspect_xlsx(en_path), en_name, "en")
            record(
                rows,
                "EN",
                en
                and en["stepCount"] == 4
                and en.get("steps") == EN_STEPS
                and en["buttons"] == EN_BUTTONS
                and en["reason"] == "The sales column could not be identified"
                and "Leave row 1 and row 2" in en["protect"]
                and "dinner" in (en.get("restaurantText") or "")
                and en_view["file"]
                and en_view["sheetName"]
                and en_view["labels"]
                and en_view["restaurant"]
                and len(errors) == 0,
                {"modal": en, "file": en_view["detail"]},
            )
            ctx.close()

            ctx, page, errors = boot(browser, "/zh-tw/app/annual/index.html")
            prepare(page, "restaurant", True)
            mb.open_current_sales(page)
            zh = open_bad_sales(page, "sales-data-modal-csv", files["bad_sales"])
            zh_name, zh_path = download_click(page, "#kpi-import-recovery-download-sales", "recovery_sales_zh.xlsx")
            zh_view = template_view(inspect_xlsx(zh_path), zh_name, "zh-tw")
            record(
                rows,
                "ZH-TW",
                zh
                and zh["stepCount"] == 4
                and zh.get("steps") == ZH_STEPS
                and zh["buttons"] == ZH_BUTTONS
                and zh["reason"] == "無法判斷哪一欄是銷售"
                and "第1列和第2列" in zh["protect"]
                and "晚餐" in (zh.get("restaurantText") or "")
                and zh_view["file"]
                and zh_view["sheetName"]
                and zh_view["labels"]
                and zh_view["restaurant"]
                and len(errors) == 0,
                {"modal": zh, "file": zh_view["detail"]},
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

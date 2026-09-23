# -*- coding: utf-8 -*-
"""C2-L6-B: Excel Sheet Picker + template fallback. No new dependencies."""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "js" / "kpi-excel-sheet-picker.js"
FIXTURE_DIR = ROOT / "fixtures" / "import" / "c2l6b"
HTTP_ROOT = "https://forge-laboratory.com/kpi-navigator"

SALES_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]
MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]
PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]

FAILED = 0
PASSED = 0


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def cell_xml(ref: str, value, formula: str | None = None, cached=True) -> str:
    if formula is not None:
        if cached:
            return f'<c r="{ref}"><f>{escape(formula)}</f><v>{escape(str(value))}</v></c>'
        return f'<c r="{ref}"><f>{escape(formula)}</f></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{ref}"><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def sheet_xml(rows: list[list], formulas: dict | None = None) -> str:
    formulas = formulas or {}
    out = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>',
    ]
    for r, row in enumerate(rows, 1):
        cells = []
        for c, val in enumerate(row):
            ref = f"{chr(65 + c)}{r}"
            spec = formulas.get(ref)
            if spec:
                cells.append(cell_xml(ref, spec.get("v", ""), spec.get("f"), spec.get("cached", True)))
            else:
                cells.append(cell_xml(ref, val))
        out.append(f'<row r="{r}">{"".join(cells)}</row>')
    out.append("</sheetData></worksheet>")
    return "\n".join(out)


def write_xlsx(path: Path, sheets: list[tuple[str, list[list], dict | None]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    names = [s[0] for s in sheets]
    wb = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>',
    ]
    rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for i, name in enumerate(names, 1):
        wb.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
        rels.append(
            f'<Relationship Id="rId{i}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{i}.xml"/>'
        )
    wb.append("</sheets></workbook>")
    rels.append("</Relationships>")
    ctypes = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    for i in range(1, len(names) + 1):
        ctypes.append(
            f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    ctypes.append("</Types>")
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "\n".join(ctypes))
        z.writestr("xl/workbook.xml", "\n".join(wb))
        z.writestr("xl/_rels/workbook.xml.rels", "\n".join(rels))
        z.writestr("_rels/.rels", root_rels)
        for i, (_n, rows, formulas) in enumerate(sheets, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", sheet_xml(rows, formulas))
    path.write_bytes(buf.getvalue())


def build_fixtures() -> dict[str, Path]:
    sales = [["日付", "日次売上"], ["2026-03-05", 12345]]
    dummy = [["README"], ["do not import"]]
    daily = [["日付", "費目", "金額"], ["2026-03-05", "食材費", 500]]
    monthly = [["年月", "費目", "金額"], ["2026-03", "店舗家賃", 120000]]
    unsupported = [["メモ"], ["横持ちPL", "1月", "2月"]]
    files = {
        "A": FIXTURE_DIR / "A_multi_sales.xlsx",
        "B": FIXTURE_DIR / "B_multi_expense_daily.xlsx",
        "C": FIXTURE_DIR / "C_multi_expense_monthly.xlsx",
        "D": FIXTURE_DIR / "D_single_sales.xlsx",
        "E": FIXTURE_DIR / "E_unsupported.xlsx",
        "F_cached": FIXTURE_DIR / "F_formula_cached.xlsx",
        "F_absent": FIXTURE_DIR / "F_formula_absent.xlsx",
    }
    write_xlsx(files["A"], [("README", dummy, None), ("売上", sales, None)])
    write_xlsx(files["B"], [("README", dummy, None), ("日次支出", daily, None)])
    write_xlsx(files["C"], [("README", dummy, None), ("月次支出", monthly, None)])
    write_xlsx(files["D"], [("売上", sales, None)])
    write_xlsx(files["E"], [("README", dummy, None), ("不明", unsupported, None)])
    write_xlsx(
        files["F_cached"],
        [("売上", [["日付", "日次売上"], ["2026-03-05", 0]], {"B2": {"f": "10000+2345", "v": 12345, "cached": True}})],
    )
    write_xlsx(
        files["F_absent"],
        [("売上", [["日付", "日次売上"], ["2026-03-05", 0]], {"B2": {"f": "10000+2345", "v": "", "cached": False}})],
    )
    return files


def test_static_wiring() -> None:
    js = JS.read_text(encoding="utf-8")
    assert_true("KpiExcelSheetPicker" in js, "picker global")
    assert_true("raw: true" in js, "cached values only")
    assert_true("取り込むシートを選択してください" in js, "JP title")
    assert_true("Select the sheet to import" in js, "EN title")
    assert_true("選擇要匯入的工作表" in js, "ZH-TW title")
    assert_true("showTemplateFallback" in js, "template fallback helper")
    assert_true("z-index:20120" in js, "picker above host modal 20055")
    assert_true("z-index:13000" not in js, "old picker z-index removed")
    assert_true("おすすめシート" not in js, "no recommended-sheet scan")
    for path in SALES_PAGES + PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-excel-sheet-picker.js" in html, f"{rel} loads picker")
        assert_true("c2picker" in html, f"{rel} cache-bust picker z-index")
        assert_true("SheetNames[0]" not in html, f"{rel} no first-sheet auto import")
        assert_true("rowsFromWorkbook" in html, f"{rel} uses picker rowsFromWorkbook")
        assert_true("picker-required" in html, f"{rel} fail-closed without picker")
        assert_true("isCancelled" in html, f"{rel} cancel is silent")
    for path in SALES_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("showTemplateFallback('sales')" in html, f"{rel} sales template fallback")
        assert_true("/* KPI-DAILY-SALES-IMPORT */" in html, f"{rel} sales marker kept")
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("expenseRowsReadable" in html, f"{rel} expense readable gate")
        assert_true("showTemplateFallback('expense')" in html, f"{rel} MEP fallback")
        assert_true("KPI-CSV-IMPORT-SAFETY-6H" in html, f"{rel} 6H confirm kept")
    gen = (ROOT / "scripts" / "daily_sales_import_client.py").read_text(encoding="utf-8")
    assert_true("rowsFromWorkbook" in gen, "sales generator uses picker")
    assert_true("SheetNames[0]" not in gen, "sales generator no first-sheet auto")


def test_sales_iife_parity() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from daily_sales_import_client import daily_sales_import_js

    js = daily_sales_import_js()
    m = re.search(r"/\* KPI-DAILY-SALES-IMPORT \*/[\s\S]*?\}\)\(\);", js)
    assert_true(bool(m), "generator IIFE")
    gen = re.sub(r"\r\n", "\n", m.group(0)).strip() if m else ""
    blocks = []
    for path in SALES_PAGES:
        html = path.read_text(encoding="utf-8")
        hm = re.search(r"/\* KPI-DAILY-SALES-IMPORT \*/[\s\S]*?\}\)\(\);", html)
        block = re.sub(r"\r\n", "\n", hm.group(0)).strip() if hm else ""
        blocks.append(block)
        assert_true(block == gen, f"{path.relative_to(ROOT).as_posix()} matches generator")
    assert_true(len(set(blocks)) == 1, "JP/EN/ZH-TW sales IIFE identical")


def test_playwright_picker() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        assert_true(False, "playwright available")
        return
    files = build_fixtures()
    js_src = JS.read_text(encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        page.add_init_script("document.documentElement.lang = 'ja';")
        page.goto("about:blank")
        page.add_script_tag(url="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js")
        page.add_script_tag(content=js_src)
        page.evaluate("() => { document.documentElement.lang = 'ja'; }")

        def load_wb(path: Path):
            data = list(path.read_bytes())
            return page.evaluate(
                """(bytes) => {
                  const u8 = new Uint8Array(bytes);
                  return Object.keys(XLSX.read(u8, { type: 'array' }).Sheets || {});
                }""",
                data,
            )

        names_a = load_wb(files["A"])
        assert_true(names_a == ["README", "売上"], "fixture A sheet names")

        single = page.evaluate(
            """() => {
              const wb = XLSX.utils.book_new();
              XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet([['日付','日次売上']]), '売上');
              return KpiExcelSheetPicker.pickSheetName(wb.SheetNames);
            }"""
        )
        assert_true(single == "売上", "single sheet auto-selects")
        assert_true(page.locator("#kpi-excel-sheet-picker").count() == 0, "single sheet no picker")

        page.evaluate(
            """() => {
              window.__kpiPick = KpiExcelSheetPicker.pickSheetName(['README','売上','納品書']);
            }"""
        )
        page.wait_for_selector("#kpi-excel-sheet-picker")
        z = page.evaluate("() => getComputedStyle(document.getElementById('kpi-excel-sheet-picker')).zIndex")
        assert_true(str(z) == "20120", "computed picker z-index 20120")
        labels = page.locator(".kpi-sheet-picker__sheet").all_text_contents()
        assert_true(labels == ["README", "売上", "納品書"], "all sheet names shown")
        title_jp = page.locator("#kpi-excel-sheet-picker-title").inner_text().strip()
        assert_true(title_jp == "取り込むシートを選択してください", "JP title:" + repr(title_jp))
        page.locator("#kpi-excel-sheet-picker-cancel").click()
        cancelled = page.evaluate(
            """() => window.__kpiPick.then(() => 'ok', (e) => e && e.message)
            """
        )
        assert_true(cancelled == "cancelled", "cancel does not import")
        assert_true(page.locator("#kpi-excel-sheet-picker").count() == 0, "picker closed on cancel")

        page.evaluate("() => { window.__kpiPick = KpiExcelSheetPicker.pickSheetName(['README','売上']); }")
        page.wait_for_selector("#kpi-excel-sheet-picker")
        page.locator('[data-kpi-sheet-name="売上"]').click()
        picked = page.evaluate("() => window.__kpiPick")
        assert_true(picked == "売上", "selected sheet only")

        page.evaluate("document.documentElement.lang = 'en'")
        page.evaluate("() => { window.__kpiPick = KpiExcelSheetPicker.pickSheetName(['A','B']); }")
        page.wait_for_selector("#kpi-excel-sheet-picker-title")
        assert_true(page.locator("#kpi-excel-sheet-picker-title").inner_text() == "Select the sheet to import", "EN title")
        page.locator("#kpi-excel-sheet-picker-cancel").click()
        page.wait_for_timeout(50)

        page.evaluate("document.documentElement.lang = 'zh-TW'")
        page.evaluate("() => { window.__kpiPick = KpiExcelSheetPicker.pickSheetName(['A','B']); }")
        page.wait_for_selector("#kpi-excel-sheet-picker-title")
        assert_true(page.locator("#kpi-excel-sheet-picker-title").inner_text() == "選擇要匯入的工作表", "ZH-TW title")
        page.locator("#kpi-excel-sheet-picker-cancel").click()

        def rows_of(path: Path, want: str):
            data = list(path.read_bytes())
            return page.evaluate(
                """({ bytes, want }) => {
                  const u8 = new Uint8Array(bytes);
                  const wb = XLSX.read(u8, { type: 'array' });
                  return KpiExcelSheetPicker.sheetToRows(wb, want);
                }""",
                {"bytes": data, "want": want},
            )

        sales_rows = rows_of(files["A"], "売上")
        dummy_rows = rows_of(files["A"], "README")
        assert_true(sales_rows and sales_rows[0][0] in ("日付",) and sales_rows[1][1] == 12345, "selected sales rows")
        assert_true(dummy_rows and "README" in str(dummy_rows[0]), "dummy sheet not mixed")

        daily_rows = rows_of(files["B"], "日次支出")
        monthly_rows = rows_of(files["C"], "月次支出")
        assert_true(daily_rows[1][0] == "2026-03-05", "daily expense date kept")
        assert_true(str(monthly_rows[1][0]).startswith("2026-03"), "monthly expense month kept")

        cached = rows_of(files["F_cached"], "売上")
        absent = rows_of(files["F_absent"], "売上")
        assert_true(cached[1][1] == 12345, "formula cached value used")
        assert_true(absent[1][1] in ("", None, 0), "formula without cache is empty/unusable")

        fallback = page.evaluate("() => KpiExcelSheetPicker.text('fallback')")
        assert_true("KPNテンプレート" in fallback or "KPN template" in fallback or "KPN 範本" in fallback, "fallback copy")
        assert_true(page.evaluate("() => KpiExcelSheetPicker.isExcelName('a.xlsx')") is True, "xlsx is excel")
        assert_true(page.evaluate("() => KpiExcelSheetPicker.isExcelName('a.csv')") is False, "csv is not excel")
        browser.close()


def test_production_artifacts() -> None:
    urls = [
        f"{HTTP_ROOT}/js/kpi-excel-sheet-picker.js?v=20260923-c2picker",
        f"{HTTP_ROOT}/app/annual/index.html",
        f"{HTTP_ROOT}/en/app/annual/index.html",
        f"{HTTP_ROOT}/zh-tw/app/annual/index.html",
        f"{HTTP_ROOT}/app/monthly/edit/index.html",
        f"{HTTP_ROOT}/en/app/monthly/edit/index.html",
        f"{HTTP_ROOT}/zh-tw/app/monthly/edit/index.html",
        f"{HTTP_ROOT}/app/profit/pl/index.html",
        f"{HTTP_ROOT}/en/app/profit/pl/index.html",
        f"{HTTP_ROOT}/zh-tw/app/profit/pl/index.html",
    ]
    # Pre-deploy this only records reachability; live marker check runs after deploy.
    for url in urls:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=20) as res:
                body = res.read()
            assert_true(res.status == 200, f"GET {url}")
            if "sheet-picker.js" in url:
                assert_true(b"KpiExcelSheetPicker" in body, "prod js has picker")
        except Exception as e:
            assert_true(False, f"GET {url}: {e}")


def main() -> int:
    build_fixtures()
    test_static_wiring()
    test_sales_iife_parity()
    test_playwright_picker()
    print(f"PASSED={PASSED} FAILED={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

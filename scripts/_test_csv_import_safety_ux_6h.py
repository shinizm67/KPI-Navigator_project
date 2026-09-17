# -*- coding: utf-8 -*-
"""Unit 6H: CSV import overwrite confirmation UX. Parser/save contracts frozen."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from daily_sales_import_client import daily_sales_import_js  # noqa: E402

FAILED = 0
PASSED = 0

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

SALES_WARN_JA = "同じ日付のデータは取込値で上書きされます。"
SALES_BLANK_JA = "売上が空欄の場合は 0 として保存されます。"
SALES_WARN_EN = "Existing data for the same date will be overwritten with imported values."
SALES_BLANK_EN = "Blank sales are saved as 0."
SALES_WARN_ZH = "相同日期的既有資料會被匯入值覆寫。"
SALES_BLANK_ZH = "銷售額空白時會以 0 儲存。"

MEP_WARN_JA = "同じ日付・費目の既存値は、取込値で置き換えられます。"
MEP_WARN_EN = "Existing values for the same date and item will be replaced with imported values."
MEP_WARN_ZH = "相同日期與費目的既有值會被匯入值取代。"


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


u4 = load_module("u4_daily_sales_meal_csv_import", SCRIPTS / "_test_daily_sales_meal_csv_import.py")
u6c = load_module("u6c_expense_csv_import", SCRIPTS / "_test_expense_csv_import_6c.py")


def confirm_then_apply(ok: bool, apply_calls: list) -> str:
    """Twin of beginImport confirm gate / MEP confirm-before-apply."""
    if not ok:
        return "cancel"
    apply_calls.append("apply")
    return "applied"


def test_sales_warning_copy() -> None:
    js = daily_sales_import_js()
    assert_true("KPI-CSV-IMPORT-SAFETY-6H" in js, "Sales confirm has 6H marker")
    assert_true(SALES_WARN_JA in js, "JP overwrite warning")
    assert_true(SALES_BLANK_JA in js, "JP blank=0 warning")
    assert_true(SALES_WARN_EN in js, "EN overwrite warning")
    assert_true(SALES_BLANK_EN in js, "EN blank=0 warning")
    assert_true(SALES_WARN_ZH in js, "ZH-TW overwrite warning")
    assert_true(SALES_BLANK_ZH in js, "ZH-TW blank=0 warning")
    assert_true("この内容で表に反映しますか？" in js, "JP confirm question kept")
    assert_true("Apply to the table?" in js, "EN confirm question kept")
    assert_true("要套用到表格嗎？" in js, "ZH-TW confirm question")
    assert_true("window.confirm(msg)" in js, "reuses existing confirm UI")
    assert_true("function rowsToMaps" in js and "function parseSalesCell" in js, "parser functions still present")
    for path in SALES_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true(SALES_WARN_JA in html, f"{rel} has JP overwrite warning")
        assert_true(SALES_BLANK_JA in html, f"{rel} has JP blank=0 warning")
        assert_true(SALES_WARN_EN in html, f"{rel} has EN overwrite warning")
        assert_true(SALES_WARN_ZH in html, f"{rel} has ZH overwrite warning")


def test_sales_cancel_and_confirm_gate() -> None:
    js = daily_sales_import_js()
    begin = js.split("function beginImport(options)", 1)[1].split("function bindButton", 1)[0]
    confirm_at = begin.find("if (!confirmImport(")
    apply_at = begin.find("options.applyMaps")
    assert_true(confirm_at >= 0, "beginImport still confirms")
    assert_true(apply_at > confirm_at, "applyMaps runs only after confirm")
    assert_true("if (!confirmImport(maps, targetYear, { persistByCsvYear: persistByCsvYear })) return;" in begin, "cancel returns before apply")
    calls: list[str] = []
    assert_true(confirm_then_apply(False, calls) == "cancel" and calls == [], "3. Cancel apply 0")
    assert_true(confirm_then_apply(True, calls) == "applied" and calls == ["apply"], "Confirm reaches apply")
    before = u4.FAILED
    blank = u4.rows_to_maps(u4.csv_rows(["date", "daily_sales"], [["2026-03-01", ""], ["2026-03-02", "0"]]))
    assert_true(blank["salesByDate"]["2026-03-01"] == 0, "blank sales still 0")
    assert_true(blank["salesByDate"]["2026-03-02"] == 0, "explicit 0 still 0")
    same = u4.rows_to_maps(
        u4.csv_rows(["date", "daily_sales"], [["2026-03-01", "500"], ["2026-03-01", "99"]])
    )
    assert_true(same["salesByDate"]["2026-03-01"] == 99, "same-date last-row still wins")
    assert_true(u4.FAILED == before, "Unit 4 helper not dirtied")


def test_sales_put_max1_and_invalid_still_zero() -> None:
    before = u4.FAILED
    u4.test_mep_valid_import_single_full_put()
    u4.test_invalid_no_partial()
    assert_true(u4.FAILED == before, "valid PUT max1 + invalid mutation0 still green")
    src = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
    assert_true("salesByDate[rec.iso] = rec.sales" in src, "sales overwrite assignment unchanged")
    assert_true("if (!cell || cell.missing) return;" in src, "meal missing skip unchanged")
    assert_true("if (raw == null || raw === '') return 0;" in src, "blank sales parse unchanged")


def test_mep_expense_confirm() -> None:
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        handler = html.split("btnExpenseCsvUpload.addEventListener('click'", 1)[1].split("if (btnConfirm)", 1)[0]
        assert_true("KPI-CSV-IMPORT-SAFETY-6H" in handler, f"{rel} MEP has 6H marker")
        assert_true(MEP_WARN_JA in handler, f"{rel} MEP JP replace warning")
        assert_true(MEP_WARN_EN in handler, f"{rel} MEP EN replace warning")
        assert_true(MEP_WARN_ZH in handler, f"{rel} MEP ZH replace warning")
        assert_true("window.confirm(mepExpenseText(" in handler, f"{rel} MEP uses confirm")
        confirm_at = handler.find("window.confirm(mepExpenseText(")
        apply_at = handler.find("applyExpenseRows(rows)")
        assert_true(apply_at > confirm_at >= 0, f"{rel} apply runs after confirm")
        assert_true("))) return;" in handler, f"{rel} Cancel returns before apply")
        assert_true("labelMap.resolve" in html, f"{rel} lineId resolver kept")
        assert_true("cur[k] = Math.round(Number(inc[k]) || 0)" in html, f"{rel} replace semantics kept")
    calls: list[str] = []
    assert_true(confirm_then_apply(False, calls) == "cancel" and not calls, "MEP Cancel mutation 0")
    assert_true(confirm_then_apply(True, calls) == "applied", "MEP Confirm reaches replace")


def test_pl_policy_unchanged() -> None:
    src = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
    assert_true("KPI-CSV-IMPORT-SAFETY-6H" not in src, "PL client not rewritten by 6H")
    assert_true("polRadio('replace'" in src and "polRadio('add'" in src and "polRadio('skip'" in src, "PL policy radios kept")
    assert_true("重複時の扱い" in src, "PL conflict policy label kept")
    assert_true("analyzeConflicts" in src, "PL conflict detection kept")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("polRadio('replace'" in html, f"{rel} replace radio")
        assert_true("polRadio('add'" in html, f"{rel} add radio")
        assert_true("polRadio('skip'" in html, f"{rel} skip radio")
        assert_true("KPI-CSV-IMPORT-SAFETY-6H" not in html, f"{rel} PL not given MEP-style extra confirm")
    before = u6c.FAILED
    u6c.test_zero_blank_duplicate()
    u6c.test_inactive_orphan_unknown()
    assert_true(u6c.FAILED == before, "6C expense mapping still green")


def test_parsers_and_templates_untouched() -> None:
    sales = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
    expense = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
    csv_t = (SCRIPTS / "csv_template_generator.py").read_text(encoding="utf-8")
    xlsx_t = (SCRIPTS / "csv_excel_template_generator.py").read_text(encoding="utf-8")
    store = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
    assert_true("function rowsToMaps(rows)" in sales, "sales parser entry kept")
    assert_true("function buildPlan(rows, cols, resolver)" in expense, "expense parser entry kept")
    assert_true("KPI-CSV-IMPORT-SAFETY-6H" not in csv_t, "CSV templates untouched")
    assert_true("KPI-CSV-IMPORT-SAFETY-6H" not in xlsx_t, "Excel templates untouched")
    assert_true("KPI-CSV-IMPORT-SAFETY-6H" not in store, "store.php untouched")
    assert_true("getBusinessType" not in sales, "sales parser still has no BT gate")


def test_regression_1_to_6g() -> None:
    suites = [
        ("6A", "_test_csv_sales_schema_6a.py"),
        ("6B", "_test_sales_csv_business_type_6b.py"),
        ("6C", "_test_expense_csv_import_6c.py"),
        ("6D", "_test_csv_templates_6d.py"),
        ("6E", "_test_csv_smoke_fixtures_6e.py"),
        ("6F", "_test_csv_excel_templates_6f.py"),
        ("6G", "_test_csv_overwrite_policy_6g.py"),
    ]
    for label, fname in suites:
        mod = load_module(f"reg_{label}", SCRIPTS / fname)
        rc = mod.main()
        assert_true(rc == 0, f"Unit {label} still green")


def main() -> int:
    print("--- 6H sales warning ---")
    test_sales_warning_copy()
    test_sales_cancel_and_confirm_gate()
    test_sales_put_max1_and_invalid_still_zero()
    print("--- 6H MEP / PL ---")
    test_mep_expense_confirm()
    test_pl_policy_unchanged()
    print("--- 6H freeze ---")
    test_parsers_and_templates_untouched()
    print("--- 6H regression 1-6G ---")
    test_regression_1_to_6g()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""Unit 6G: freeze Reset / Sample / Import overwrite policy.

Does not add a product Reset feature. Documents and locks the current
import contracts so Reset CSVs are never shipped from the Download menu.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from csv_template_generator import (  # noqa: E402
    build_expense_template,
    build_sales_template,
    parse_csv_text,
)
from pl_line_catalog import reconcile_catalog_lines  # noqa: E402

FAILED = 0
PASSED = 0

CHROME_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
    ROOT / "setting/feedback.html",
    ROOT / "en/setting/feedback.html",
    ROOT / "zh-tw/setting/feedback.html",
]

MENU_FORBIDDEN = (
    "_reset",
    "reset.csv",
    "reset.xlsx",
    "generated-fixtures",
    "sample_2026",
    "/excel/",
    "excel/",
)


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


def menu_blob(html: str) -> str:
    if "template-dl-menu" not in html:
        return ""
    return html.split("template-dl-menu", 1)[1].split("</details>", 1)[0]


def merge_value(existing_has: bool, existing, incoming, policy: str):
    """PL expense overlap policy. Twin of pl_expense_import_client.mergeValue."""
    if policy == "add":
        return round((float(existing) if existing is not None else 0) + (float(incoming) or 0))
    if policy == "skip":
        return existing if existing_has else round(float(incoming) or 0)
    return round(float(incoming) or 0)


def test_product_dl_has_no_reset_or_fixture() -> None:
    chrome = (SCRIPTS / "site_chrome.py").read_text(encoding="utf-8")
    assert_true('data-kpi-csv-template="sales"' in chrome, "chrome has sales template DL")
    assert_true('data-kpi-csv-template="expense-daily"' in chrome, "chrome has daily expense DL")
    assert_true('data-kpi-csv-template="expense-monthly"' in chrome, "chrome has monthly expense DL")
    assert_true('data-kpi-excel-template="workbook"' in chrome, "chrome has Excel template DL")
    assert_true("{img}excel/" not in chrome, "chrome has no static excel/ href")
    assert_true("_reset" not in chrome, "chrome has no reset artifact")
    assert_true("generated-fixtures" not in chrome, "chrome does not ship smoke fixtures")
    assert_true("Reset CSV" not in chrome and "リセットCSV" not in chrome, "chrome has no Reset CSV label")
    js_csv = (ROOT / "js" / "kpi-csv-templates.js").read_text(encoding="utf-8")
    js_xlsx = (ROOT / "js" / "kpi-excel-templates.js").read_text(encoding="utf-8")
    assert_true("reset" not in js_csv.lower().split("filename")[0] or "sales_template.csv" in js_csv, "csv DL filenames are templates")
    assert_true("kpi_template_" in js_xlsx and "_reset" not in js_xlsx, "excel DL filename is kpi_template_{bt}.xlsx")
    for path in CHROME_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        menu = menu_blob(html)
        assert_true(menu != "", f"{rel} has download menu")
        low = menu.lower()
        for token in MENU_FORBIDDEN:
            assert_true(token.lower() not in low, f"{rel} menu has no {token}")
        assert_true("data-kpi-csv-template" in menu, f"{rel} uses dynamic CSV templates")
        assert_true("data-kpi-excel-template" in menu, f"{rel} uses dynamic Excel template")
        assert_true('href=' not in menu or "excel/" not in menu, f"{rel} menu has no excel/ href")


def test_html_scan_no_reset_distribution() -> None:
    hits = []
    for path in ROOT.rglob("*.html"):
        if "excel" in path.parts or "tests" in path.parts or "tools" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r"href=['\"][^'\"]*excel/[^'\"]*_reset", text, re.I):
            hits.append(path.relative_to(ROOT).as_posix())
        if "generated-fixtures" in text:
            hits.append(path.relative_to(ROOT).as_posix() + ":fixtures")
    assert_true(not hits, f"no product HTML ships reset/fixture hrefs: {hits}")
    leftover = []
    for path in ROOT.rglob("*.html"):
        if "excel" in path.parts or "tests" in path.parts or "tools" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        menu = menu_blob(text)
        if menu and re.search(r"href=['\"][^'\"]*excel/", menu):
            leftover.append(path.relative_to(ROOT).as_posix())
    assert_true(not leftover, f"no download menu still static-hrefs excel/: {leftover}")


def test_generated_fixtures_stay_under_tests() -> None:
    gen = (SCRIPTS / "csv_smoke_fixture_generator.py").read_text(encoding="utf-8")
    assert_true("tests/generated-fixtures" in gen, "6E fixtures dest is tests/generated-fixtures")
    assert_true("excel/ is forbidden" in gen, "6E never writes excel/")
    assert_true("reset files" in gen or "Never writes" in gen, "6E documents no reset files")
    fixture_root = ROOT / "tests" / "generated-fixtures"
    assert_true(fixture_root.is_dir(), "committed fixtures live under tests/")
    for path in fixture_root.rglob("*"):
        if path.is_file():
            assert_true("excel" not in path.parts, f"{path.name} not under excel/")
            assert_true("reset" not in path.name.lower(), f"{path.name} is not a reset artifact")
    excel_gen = (SCRIPTS / "csv_excel_template_generator.py").read_text(encoding="utf-8")
    assert_true("xlsx output must live under tests/" in excel_gen, "6F xlsx dest is tests/")
    csv_gen = (SCRIPTS / "csv_template_generator.py").read_text(encoding="utf-8")
    assert_true("write_text" not in csv_gen and "open(" not in csv_gen, "CSV templates are in-memory only")


def test_sales_overwrite_contract() -> None:
    first = u4.rows_to_maps(
        u4.csv_rows(
            ["date", "business_day", "daily_sales"],
            [["2026-03-01", "1", "500"], ["2026-03-02", "1", "800"]],
        )
    )
    second = u4.rows_to_maps(
        u4.csv_rows(
            ["date", "business_day", "daily_sales"],
            [["2026-03-01", "1", "120"], ["2026-03-01", "1", "99"]],
        )
    )
    assert_true(first["salesByDate"]["2026-03-01"] == 500, "initial sales parsed")
    assert_true(second["salesByDate"]["2026-03-01"] == 99, "same-date last row in file wins")
    assert_true("2026-03-02" not in second["salesByDate"], "import map only contains imported dates")
    blank = u4.rows_to_maps(
        u4.csv_rows(["date", "daily_sales"], [["2026-03-01", ""], ["2026-03-03", "0"]])
    )
    assert_true(blank["salesByDate"]["2026-03-01"] == 0, "blank daily_sales parses as 0")
    assert_true(blank["salesByDate"]["2026-03-03"] == 0, "explicit 0 daily_sales is 0")
    junk = u4.rows_to_maps(u4.csv_rows(["date", "daily_sales"], [["2026-03-04", "abc"]]))
    assert_true(junk["salesByDate"]["2026-03-04"] == 0, "non-numeric daily_sales parses as 0")
    src = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
    assert_true("salesByDate[rec.iso] = rec.sales" in src, "same-date map overwrite is last assignment")
    assert_true("rowStateByIso[iso] =" in src, "applyToRowState overwrites matching iso only")
    assert_true("Apply to the table?" in src, "sales confirm does not claim Reset")
    assert_true("リセット" not in src and "Reset CSV" not in src, "sales import UI is not a Reset action")


def test_meal_missing_preserve_and_explicit_zero() -> None:
    store = u4.FakeStore(
        {
            "dinner_sales": {"2026-03-01": 111, "2026-03-02": 222},
            "lunch_sales": {"2026-03-01": 50},
        }
    )
    maps = u4.rows_to_maps(
        u4.csv_rows(
            ["年月日", "日次売上", "ランチ売上", "ディナー売上", "ランチ客数", "ディナー客数", "トータル客数", "ランチ組数", "ディナー組数", "トータル組数"],
            [
                ["2026-03-01", "100", "", "40", "24", "13", "37", "11", "6", "17"],
                ["2026-03-03", "80", "", "", "0", "0", "0", "0", "0", "0"],
            ],
        )
    )
    assert_true("2026-03-01" not in maps["lunchSalesByDate"], "4. blank lunch is missing, not 0")
    assert_true(maps["dinnerSalesByDate"]["2026-03-01"] == 40, "explicit dinner overwrites")
    assert_true("2026-03-03" not in maps["dinnerSalesByDate"], "blank dinner sales missing")
    assert_true(maps["totalCustomersByDate"]["2026-03-03"] == 0, "5. explicit 0 customers is kept")
    wrote = u4.persist_daily_meal_from_maps(maps, store)
    assert_true(wrote > 0, "persist writes explicit meal cells")
    assert_true(store.dailyMeal["dinner_sales"]["2026-03-01"] == 40, "imported dinner overwrote that date")
    assert_true(store.dailyMeal["dinner_sales"]["2026-03-02"] == 222, "4. missing meal does not delete other dates")
    assert_true(store.dailyMeal["lunch_sales"]["2026-03-01"] == 50, "4. blank lunch column preserves existing")
    assert_true("2026-03-03" not in store.dailyMeal.get("dinner_sales", {}), "blank dinner does not write")
    assert_true(store.dailyMeal["total_customers"]["2026-03-03"] == 0, "5. explicit 0 is written")


def test_invalid_import_mutates_nothing() -> None:
    before = u4.FAILED
    store = u4.FakeStore({"dinner_sales": {"2026-03-01": 9}})
    caught = None
    try:
        u4.rows_to_maps(
            u4.csv_rows(
                ["年月日", "日次売上", "ランチ客数", "ディナー客数", "トータル客数"],
                [["2026-04-01", "100", "abc", "1", "2"]],
            )
        )
        u4.persist_daily_meal_from_maps({"dinnerSalesByDate": {"2026-04-01": 1}}, store)
    except u4.MealInvalid as err:
        caught = err
    assert_true(caught is not None, "6. invalid meal stops parse")
    u4.test_invalid_no_partial()
    u4.test_annual_persist_path()
    assert_true(u4.FAILED == before, "6. Unit 4 invalid mutation0/PUT0 still green")
    src = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
    assert_true("meal-invalid" in src, "invalid import alerts and stops")
    assert_true("if (mealErrors.length) throw mealErrors[0]" in src, "invalid throws before maps persist")


def test_expense_replace_add_skip() -> None:
    src = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
    assert_true("policy === 'add'" in src and "policy === 'skip'" in src, "7. PL has add/skip")
    assert_true("return Math.round(Number(incoming) || 0); // replace (default)" in src, "7. default replace")
    assert_true("置換（上書き）" in src, "7. replace is labelled overwrite, not Reset")
    assert_true(merge_value(True, 100, 30, "replace") == 30, "replace uses incoming")
    assert_true(merge_value(True, 100, 30, "add") == 130, "add sums")
    assert_true(merge_value(True, 100, 30, "skip") == 100, "skip keeps existing")
    assert_true(merge_value(False, None, 30, "skip") == 30, "skip fills when empty")
    u6c.test_zero_blank_duplicate()
    catalog = u6c.default_catalog_lines("retail")
    rows = [
        ["month", "item", "label", "amount"],
        ["年月", "lineId", "費目", "金額"],
        ["2026-06", "exp_inventory_cogs", "商品仕入", "0"],
        ["2026-06", "exp_inventory_cogs", "商品仕入", "10"],
        ["2026-06", "exp_inventory_cogs", "商品仕入", "15"],
    ]
    plan = u6c.build_plan(rows, catalog)
    assert_true(plan["monthlyByYear"][2026]["exp_inventory_cogs:5"] == 25, "same month/lineId summed in-file before apply")
    mep = (ROOT / "app/monthly/edit/index.html").read_text(encoding="utf-8")
    assert_true("cur[k] = Math.round(Number(inc[k]) || 0)" in mep, "MEP expense import is replace-only")


def test_unknown_and_inactive_custom() -> None:
    before = u6c.FAILED
    u6c.test_inactive_orphan_unknown()
    assert_true(u6c.FAILED == before, "8/9. unknown + inactive contracts still green")
    restaurant = u6c.default_catalog_lines("restaurant")
    retail = reconcile_catalog_lines(restaurant, "retail")
    retail = retail + [
        u6c.custom_line(line_id="exp_custom_variable_hidden", active=False),
        u6c.custom_line(line_id="exp_custom_variable_ok"),
    ]
    resolve = u6c.make_resolver(retail)
    assert_true(resolve("exp_custom_variable_ok") is not None, "9. active custom imports")
    assert_true(resolve("exp_custom_variable_hidden") is None, "9. inactive custom is not resurrected")
    assert_true(resolve("exp_unknown_zzzz") is None, "8. unknown lineId does not map")
    plan = u6c.build_plan(
        [
            ["month", "item", "label", "amount"],
            ["2026-03", "exp_unknown_zzzz", "謎", "100"],
            ["2026-03", "exp_custom_variable_hidden", "倉庫利用料", "80"],
            ["2026-03", "exp_custom_variable_ok", "倉庫利用料", "50"],
        ],
        retail,
    )
    assert_true("exp_unknown_zzzz" in plan["unmatched"], "8. unknown goes unmatched / skip")
    assert_true("exp_custom_variable_hidden:2" not in plan["monthlyByYear"].get(2026, {}), "9. inactive custom not written")
    assert_true(plan["monthlyByYear"][2026].get("exp_custom_variable_ok:2") == 50, "active custom amount imported")


def test_sample_strategy_is_dynamic() -> None:
    sales = build_sales_template("retail", "ja")
    daily = build_expense_template(None, style="daily", lang="ja", business_type="retail")
    rows = parse_csv_text(daily["text"])
    body_amounts = [row[3] for row in rows[2:] if len(row) > 3]
    assert_true(all(amt == "" for amt in body_amounts), "product expense template has empty amounts")
    assert_true(len(parse_csv_text(sales["text"])) == 2, "product sales template is header-only, not a filled sample")
    assert_true("sales_template.csv" in sales["filename"], "product file is a template not a reset")
    js = (ROOT / "js" / "kpi-csv-templates.js").read_text(encoding="utf-8")
    assert_true("buildSalesTemplate" in js and "buildExpenseTemplate" in js, "runtime can generate BT-aware samples later")
    chrome = (SCRIPTS / "site_chrome.py").read_text(encoding="utf-8")
    assert_true("kpi_template_restaurant.xlsx" not in chrome, "no static per-BT xlsx in chrome")
    assert_true("kpi_template_retail.xlsx" not in chrome, "no static Retail xlsx in chrome")


def test_import_ui_wording_is_not_reset() -> None:
    sales = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
    expense = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
    assert_true("この内容で表に反映しますか？" in sales, "sales confirm is apply, not reset")
    assert_true("支出データを取り込みます" in expense, "expense confirm is import")
    assert_true("リセット" not in sales, "sales import copy has no リセット")
    assert_true("Reset" not in expense.split("replace")[0], "expense client is not a Reset tool")
    assert_true("Conflicts are detected up front" in expense, "expense overwrite is never silent on PL")


def test_parsers_untouched() -> None:
    store = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
    presets = (SCRIPTS / "pl_line_catalog.py").read_text(encoding="utf-8")
    assert_true("overwrite_policy_6g" not in store, "store.php untouched")
    assert_true("csv_overwrite_policy" not in presets, "presets untouched")


def test_regression_1_to_6f() -> None:
    suites = [
        ("6A", "_test_csv_sales_schema_6a.py"),
        ("6B", "_test_sales_csv_business_type_6b.py"),
        ("6C", "_test_expense_csv_import_6c.py"),
        ("6D", "_test_csv_templates_6d.py"),
        ("6E", "_test_csv_smoke_fixtures_6e.py"),
        ("6F", "_test_csv_excel_templates_6f.py"),
    ]
    for label, fname in suites:
        mod = load_module(f"reg_{label}", SCRIPTS / fname)
        rc = mod.main()
        assert_true(rc == 0, f"Unit {label} still green")


def main() -> int:
    print("--- 6G product DL / fixtures ---")
    test_product_dl_has_no_reset_or_fixture()
    test_html_scan_no_reset_distribution()
    test_generated_fixtures_stay_under_tests()
    print("--- 6G sales / meal overwrite ---")
    test_sales_overwrite_contract()
    test_meal_missing_preserve_and_explicit_zero()
    test_invalid_import_mutates_nothing()
    print("--- 6G expense / custom ---")
    test_expense_replace_add_skip()
    test_unknown_and_inactive_custom()
    print("--- 6G sample / wording / freeze ---")
    test_sample_strategy_is_dynamic()
    test_import_ui_wording_is_not_reset()
    test_parsers_untouched()
    print("--- 6G regression 1-6F ---")
    test_regression_1_to_6f()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

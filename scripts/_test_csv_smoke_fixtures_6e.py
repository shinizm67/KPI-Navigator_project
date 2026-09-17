# -*- coding: utf-8 -*-
"""Unit 6E: Business Type smoke fixture generator."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from csv_sales_schema import (  # noqa: E402
    COMMON_KEYS,
    CSV_PERSISTED_MEAL_KEYS,
    LUNCH_VALIDATION_FIELDS,
    RESTAURANT_ONLY_KEYS,
)
from csv_smoke_fixture_generator import (  # noqa: E402
    CUSTOM_SMOKE_AMOUNT,
    CUSTOM_SMOKE_LINE,
    EXCEL_DIR,
    FIXTURE_ROOT,
    MINIMAL_YEAR,
    NON_RESTAURANT,
    RESTAURANT_YEARS,
    FixturePathError,
    assert_safe_dest,
    build_all,
    catalog_lines,
    pick_representative,
    write_fixtures,
)
from csv_template_generator import (  # noqa: E402
    EXPENSE_DAILY_MACHINE_HEADER,
    EXPENSE_MONTHLY_MACHINE_HEADER,
    parse_csv_text,
    sales_field_keys,
)
from pl_line_catalog import BUSINESS_TYPE_CANONICAL  # noqa: E402

FAILED = 0
PASSED = 0


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


def header_of(text: str) -> list[str]:
    return parse_csv_text(text)[0]


def test_restaurant_years() -> None:
    payload = build_all()
    years = [bundle["year"] for bundle in payload["restaurant"]]
    assert_true(tuple(years) == RESTAURANT_YEARS, "1. Restaurant 2024/2025/2026 generated")
    for bundle in payload["restaurant"]:
        sales_rows = parse_csv_text(bundle["sales"]["text"])
        year = bundle["year"]
        assert_true(sales_rows[0] == list(sales_field_keys("restaurant")), f"{year} sales machine header")
        assert_true(len(sales_rows) > 365, f"{year} has a full year of sales rows")
        dates = [row[0] for row in sales_rows[1:]]
        assert_true(dates[0].startswith(f"{year}-01-01"), f"{year} starts Jan 1")
        assert_true(dates[-1].startswith(f"{year}-12-31"), f"{year} ends Dec 31")
        assert_true(len(set(dates)) == len(dates), f"{year} sales dates unique")


def test_sales_columns_and_unit4() -> None:
    payload = build_all()
    rest = payload["restaurant"][2]
    keys = rest["sales"]["keys"]
    assert_true(tuple(keys[:3]) == COMMON_KEYS, "2. COMMON columns first")
    assert_true(tuple(keys[3:]) == RESTAURANT_ONLY_KEYS, "3. Restaurant-only columns follow")
    assert_true("lunch_sales" in keys, "4. lunch present in CSV")
    assert_true("dinner_sales" in keys, "4. dinner present in CSV")
    for lunch_key in LUNCH_VALIDATION_FIELDS:
        assert_true(lunch_key in keys, f"4. {lunch_key} in CSV")
        assert_true(lunch_key not in CSV_PERSISTED_MEAL_KEYS, f"4. {lunch_key} not persist canonical")
    rows = parse_csv_text(rest["sales"]["text"])
    maps = u4.rows_to_maps(rows)
    store = u4.FakeStore()
    u4.persist_daily_meal_from_maps(maps, store)
    open_iso = "2026-03-02"
    assert_true(maps["salesByDate"][open_iso] == maps["lunchSalesByDate"][open_iso] + maps["dinnerSalesByDate"][open_iso], "4. lunch+dinner=total")
    assert_true(store.dailyMeal["dinner_sales"][open_iso] == maps["dinnerSalesByDate"][open_iso], "4. dinner persisted")
    assert_true("lunch_sales" not in store.dailyMeal, "4. lunch not persisted")
    lunch_writes = [item for item in store.write_log if item[0] in LUNCH_VALIDATION_FIELDS]
    assert_true(lunch_writes == [], "4. lunch_* validation-only")


def test_non_restaurant_common_only() -> None:
    payload = build_all()
    by_type = {bundle["businessType"]: bundle for bundle in payload["minimal"]}
    for code in NON_RESTAURANT:
        bundle = by_type[code]
        keys = bundle["sales"]["keys"]
        assert_true(tuple(keys) == COMMON_KEYS, f"5/7-10. {code} sales COMMON only")
        for rest_key in RESTAURANT_ONLY_KEYS:
            assert_true(rest_key not in keys, f"{code} has no {rest_key}")
        rows = parse_csv_text(bundle["sales"]["text"])
        assert_true(rows[0] == list(COMMON_KEYS), f"{code} machine header")
        assert_true(len(rows) == 8, f"{code} 7 data days")
        amounts = [int(row[2]) for row in rows[1:] if row[1] == "1"]
        assert_true(len(set(amounts)) == len(amounts) and amounts, f"{code} open-day sales distinctive")


def test_expense_lineids_from_presets() -> None:
    payload = build_all()
    retail = next(bundle for bundle in payload["minimal"] if bundle["businessType"] == "retail")
    retail_catalog = catalog_lines("retail")
    daily_id = pick_representative(retail_catalog, "daily")["lineId"]
    monthly_id = pick_representative(retail_catalog, "monthly")["lineId"]
    assert_true(retail["expenses_daily"]["lineIds"] == (daily_id,), "6. Retail daily lineId from preset")
    assert_true(monthly_id in retail["expenses_monthly"]["lineIds"], "6. Retail monthly lineId from preset")
    daily_rows = parse_csv_text(retail["expenses_daily"]["text"])
    monthly_rows = parse_csv_text(retail["expenses_monthly"]["text"])
    assert_true(tuple(daily_rows[0]) == EXPENSE_DAILY_MACHINE_HEADER, "11. daily machine header")
    assert_true(tuple(monthly_rows[0]) == EXPENSE_MONTHLY_MACHINE_HEADER, "11. monthly machine header")
    catalog = u6c.default_catalog_lines("retail")
    plan_d = u6c.build_plan(daily_rows, catalog)
    plan_m = u6c.build_plan(monthly_rows, catalog)
    assert_true(daily_id in plan_d["dailyByYear"][MINIMAL_YEAR], "6. Retail daily maps by lineId")
    month_key = f"{monthly_id}:2"
    assert_true(month_key in plan_m["monthlyByYear"][MINIMAL_YEAR], "6. Retail monthly maps by lineId")
    assert_true(plan_d["monthlyByYear"] == {}, "11. daily file does not monthly-ize")
    assert_true(plan_m["dailyByYear"] == {}, "11. monthly file does not daily-ize")

    for bundle in payload["minimal"]:
        code = bundle["businessType"]
        cat = catalog_lines(code)
        daily = pick_representative(cat, "daily")["lineId"]
        monthly = pick_representative(cat, "monthly")["lineId"]
        assert_true(bundle["dailyLine"]["lineId"] == daily, f"{code} daily representative from preset")
        assert_true(bundle["monthlyLine"]["lineId"] == monthly, f"{code} monthly representative from preset")
        d_rows = parse_csv_text(bundle["expenses_daily"]["text"])
        m_rows = parse_csv_text(bundle["expenses_monthly"]["text"])
        assert_true(all(row[0].count("-") == 2 for row in d_rows[1:]), f"{code} daily uses YYYY-MM-DD")
        data_months = [row for row in m_rows[1:] if not str(row[1]).startswith("exp_custom_")]
        assert_true(all(row[0].count("-") == 1 for row in data_months), f"{code} monthly uses YYYY-MM")


def test_custom_fixture() -> None:
    payload = build_all()
    retail = next(bundle for bundle in payload["minimal"] if bundle["businessType"] == "retail")
    rows = parse_csv_text(retail["expenses_monthly"]["text"])
    custom_rows = [row for row in rows[1:] if row[1] == CUSTOM_SMOKE_LINE["lineId"]]
    assert_true(len(custom_rows) == 1, "12. retail custom expense row exists")
    assert_true(int(custom_rows[0][3]) == CUSTOM_SMOKE_AMOUNT, "12. custom amount distinctive")
    meta = payload["manifest"]["custom"]
    assert_true(meta["lineId"] == "exp_custom_variable_smoke", "12. custom lineId")
    assert_true(meta["mockCatalog"] is True and meta["productionCatalog"] is False, "12. mock catalog only")
    assert_true(meta["inputStyle"] == "monthly", "12. custom style monthly")
    src = (SCRIPTS / "csv_smoke_fixture_generator.py").read_text(encoding="utf-8")
    assert_true("kpiNavigator.plLineCatalog" not in src or "Never written" in src, "12. generator does not register production catalog")
    assert_true("setJson" not in src and "store.php" not in src, "12. no production catalog write")


def test_locale_reset_excel_deterministic() -> None:
    payload = build_all()
    again = build_all()
    assert_true(payload["files"] == again["files"], "16. deterministic generation")
    for name, text in payload["files"].items():
        if name == "manifest.json":
            continue
        header = header_of(text)
        assert_true("reset" not in name.lower() and "delete" not in name.lower(), "14. no reset filename")
        if name.endswith("_sales.csv"):
            if name.startswith("restaurant_"):
                assert_true(header == list(sales_field_keys("restaurant")), f"13. {name} restaurant machine keys")
            else:
                assert_true(header == list(COMMON_KEYS), f"13. {name} COMMON machine keys")
        elif "expenses_daily" in name:
            assert_true(header == list(EXPENSE_DAILY_MACHINE_HEADER), f"13. {name} daily expense keys")
        elif "expenses_monthly" in name:
            assert_true(header == list(EXPENSE_MONTHLY_MACHINE_HEADER), f"13. {name} monthly expense keys")
        assert_true("日付" not in header and "費目" not in header, f"13. {name} has no JA header")
    manifest = payload["manifest"]
    assert_true(manifest["reset"] is False and manifest["deletionSemantics"] is False, "14. no reset/deletion semantics")
    assert_true(manifest["locale"] == "machine-key", "13. locale independence declared")
    sales_en = parse_csv_text(payload["minimal"][0]["sales"]["text"])
    assert_true(sales_en[0] == ["date", "business_day", "daily_sales"], "13. non-restaurant machine keys")
    src = (SCRIPTS / "csv_smoke_fixture_generator.py").read_text(encoding="utf-8")
    assert_true("EXCEL_DIR" in src and "excel/ is forbidden" in src, "15. generator guards excel/")
    raised = False
    try:
        assert_safe_dest(EXCEL_DIR / "nope")
    except FixturePathError:
        raised = True
    assert_true(raised, "15. excel dest rejected")
    assert_true(str(FIXTURE_ROOT).replace("\\", "/").endswith("tests/generated-fixtures"), "15. dest tests/generated-fixtures")
    restaurant_labels = catalog_lines("retail")
    assert_true(all("labelJa" in line for line in restaurant_labels), "expense labels come from catalog")
    gen_src = src
    assert_true("商品仕入" not in gen_src, "no handwritten Retail labels in generator")
    assert_true("薬剤・施術材料費" not in gen_src, "no handwritten Hair Salon labels")
    assert_true("アメニティ費" not in gen_src, "no handwritten Hotel labels")


def test_write_and_committed_match() -> None:
    payload = build_all()
    written = write_fixtures(FIXTURE_ROOT)
    assert_true("manifest.json" in written, "manifest written")
    for name, text in payload["files"].items():
        on_disk = (FIXTURE_ROOT / name).read_text(encoding="utf-8")
        assert_true(on_disk == text, f"disk matches generator: {name}")
        assert_true(EXCEL_DIR not in (FIXTURE_ROOT / name).parents, f"{name} not under excel/")
    names = set(payload["manifest"]["files"])
    assert_true("restaurant_2024_sales.csv" in names, "restaurant 2024 sales named")
    assert_true("retail_minimal_expenses_monthly.csv" in names, "retail monthly named")
    assert_true("hair_salon_minimal_sales.csv" in names, "hair salon named")
    assert_true("hotel_minimal_sales.csv" in names, "hotel named")
    meta = json.loads((FIXTURE_ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert_true(meta["excel"] == "untouched", "manifest records excel untouched")
    assert_true(tuple(BUSINESS_TYPE_CANONICAL) == ("restaurant",) + NON_RESTAURANT, "canonical types unchanged")


def test_source_guards() -> None:
    gen = (SCRIPTS / "csv_smoke_fixture_generator.py").read_text(encoding="utf-8")
    assert_true("from csv_sales_schema import" in gen, "reuses sales schema")
    assert_true("from csv_template_generator import" in gen, "reuses template generator")
    assert_true("from pl_line_catalog import" in gen, "reuses line catalog")
    assert_true("default_catalog_lines" in gen, "expenses come from preset catalog")
    assert_true("EXPENSE_DETAIL_LINES_V1" not in gen, "does not duplicate restaurant tuples")
    sales_parser = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
    expense_parser = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
    assert_true("smoke_fixture" not in sales_parser, "sales parser unchanged")
    assert_true("smoke_fixture" not in expense_parser, "expense parser unchanged")
    presets = (SCRIPTS / "pl_line_catalog.py").read_text(encoding="utf-8")
    assert_true("exp_custom_variable_smoke" not in presets, "custom smoke line not added to presets")


def main() -> int:
    print("--- 6E restaurant / Unit 4 ---")
    test_restaurant_years()
    test_sales_columns_and_unit4()
    print("--- 6E non-restaurant / expenses ---")
    test_non_restaurant_common_only()
    test_expense_lineids_from_presets()
    print("--- 6E custom / locale / dest ---")
    test_custom_fixture()
    test_locale_reset_excel_deterministic()
    print("--- 6E write / guards ---")
    test_write_and_committed_match()
    test_source_guards()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

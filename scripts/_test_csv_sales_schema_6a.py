# -*- coding: utf-8 -*-
"""Unit 6A: freeze Sales CSV canonical keys / aliases / Unit 4 persist contract.

Does not change parser behavior. New CSV files are not created.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from csv_sales_schema import (  # noqa: E402
    ALIASES,
    CANONICAL_KEYS,
    CATEGORY_COMMON,
    CATEGORY_RESTAURANT_ONLY,
    COMMON_KEYS,
    CSV_PERSISTED_MEAL_KEYS,
    DAILY_SALES_CONTAINS_ALIASES,
    DAILY_SALES_EXACT_ALIASES,
    FIELD_BY_KEY,
    FIELDS,
    LUNCH_VALIDATION_FIELDS,
    MEAL_CSV_PERSIST_PAIRS,
    OPTIONAL_KEYS,
    PARSER_JS_ALIAS_ARRAYS,
    RESTAURANT_ONLY_KEYS,
    REQUIRED_KEYS,
    aliases_for,
    field,
)
from daily_sales_import_client import daily_sales_import_js  # noqa: E402

FAILED = 0
PASSED = 0

EXPECTED_CANONICAL = (
    "date",
    "business_day",
    "daily_sales",
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


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def load_u4():
    spec = importlib.util.spec_from_file_location(
        "u4_daily_sales_meal_csv_import",
        SCRIPTS / "_test_daily_sales_meal_csv_import.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extract_js_string_array(js: str, name: str) -> list[str]:
    m = re.search(rf"var {re.escape(name)} = \[([\s\S]*?)\];", js)
    if not m:
        return []
    return re.findall(r"'([^']*)'", m.group(1))


def extract_js_persist_pairs(js: str) -> list[tuple[str, str]]:
    m = re.search(r"var MEAL_PERSIST_PAIRS = \[([\s\S]*?)\];", js)
    if not m:
        return []
    return [
        (a, b)
        for a, b in re.findall(r"\['([^']+)', '([^']+)'\]", m.group(1))
    ]


def test_common_and_restaurant_classification() -> None:
    assert_true(COMMON_KEYS == ("date", "business_day", "daily_sales"), "1. COMMON fields")
    assert_true(
        RESTAURANT_ONLY_KEYS
        == (
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
        ),
        "2. RESTAURANT_ONLY fields",
    )
    for key in COMMON_KEYS:
        assert_true(field(key).category == CATEGORY_COMMON, f"{key} is COMMON")
    for key in RESTAURANT_ONLY_KEYS:
        assert_true(field(key).category == CATEGORY_RESTAURANT_ONLY, f"{key} is RESTAURANT_ONLY")
    expense_like = [k for k in CANONICAL_KEYS if k.startswith("exp_")]
    assert_true(expense_like == [], "Sales schema has no expense lineId fields")


def test_canonical_keys() -> None:
    assert_true(CANONICAL_KEYS == EXPECTED_CANONICAL, "3. canonical key list")
    assert_true(tuple(f.key for f in FIELDS) == EXPECTED_CANONICAL, "FIELDS order matches canonical")
    assert_true(set(FIELD_BY_KEY) == set(EXPECTED_CANONICAL), "FIELD_BY_KEY covers all keys")


def test_alias_compatibility_with_parser() -> None:
    js = daily_sales_import_js()
    for array_name, key in PARSER_JS_ALIAS_ARRAYS.items():
        extracted = tuple(extract_js_string_array(js, array_name))
        if array_name == "DAILY_SALES_EXACT_KEYS":
            expected = DAILY_SALES_EXACT_ALIASES
        elif array_name == "SALES_KEYS":
            expected = DAILY_SALES_CONTAINS_ALIASES
        else:
            expected = aliases_for(key)
        assert_true(
            extracted == expected,
            f"4. parser {array_name} aliases frozen ({extracted!r} vs {expected!r})",
        )
    daily_union = tuple(
        dict.fromkeys(DAILY_SALES_CONTAINS_ALIASES + DAILY_SALES_EXACT_ALIASES)
    )
    assert_true(daily_union == ALIASES["daily_sales"], "daily_sales alias union matches schema")
    assert_true("日付" in aliases_for("date"), "JA date alias kept")
    assert_true("date" in aliases_for("date"), "EN date alias kept")
    assert_true("ランチ売上" in aliases_for("lunch_sales"), "JA lunch sales alias kept")
    assert_true("dinnersales" in aliases_for("dinner_sales"), "EN dinner sales alias kept")


def test_required_optional() -> None:
    assert_true(REQUIRED_KEYS == ("date", "daily_sales"), "5+6. date and daily_sales required")
    assert_true(field("date").required == "required", "5. date required")
    assert_true(field("daily_sales").required == "required", "6. daily_sales required")
    assert_true(field("business_day").required == "optional", "7. business_day optional")
    assert_true("business_day" in OPTIONAL_KEYS, "7. business_day in optional set")
    js = daily_sales_import_js()
    assert_true("if (cols.dateIdx < 0 || cols.salesIdx < 0) throw new Error('columns');" in js, "parser requires date+sales cols")
    assert_true("var biz = cols.bizIdx >= 0 ? parseBizCell(row[cols.bizIdx]) : null;" in js, "parser treats biz as optional")


def test_meal_persist_vs_validation_only() -> None:
    assert_true(field("dinner_sales").persisted == "yes", "8. dinner_sales canonical persist")
    assert_true(field("dinner_sales").save_target == "dailyMeal", "8. dinner_sales -> dailyMeal")
    assert_true(field("lunch_sales").persisted == "validation-only", "9. lunch_sales validation-only")
    assert_true(field("total_customers").persisted == "yes", "10. total_customers canonical")
    assert_true(field("lunch_customers").persisted == "validation-only", "11. lunch_customers validation-only")
    assert_true(field("dinner_customers").persisted == "yes", "12. dinner_customers canonical")
    assert_true(field("total_groups").persisted == "yes", "13. total_groups canonical")
    assert_true(field("lunch_groups").persisted == "validation-only", "14. lunch_groups validation-only")
    assert_true(field("dinner_groups").persisted == "yes", "15. dinner_groups canonical")
    assert_true(CSV_PERSISTED_MEAL_KEYS == tuple(p[1] for p in MEAL_CSV_PERSIST_PAIRS), "persist pair keys")
    assert_true(LUNCH_VALIDATION_FIELDS == ("lunch_sales", "lunch_customers", "lunch_groups"), "lunch trio")
    js = daily_sales_import_js()
    pairs = extract_js_persist_pairs(js)
    assert_true(tuple(pairs) == MEAL_CSV_PERSIST_PAIRS, "parser MEAL_PERSIST_PAIRS frozen")
    assert_true("['lunchSalesByDate', 'lunch_sales']" not in js, "parser does not persist lunch_sales")
    assert_true("['lunchCustomersByDate', 'lunch_customers']" not in js, "parser does not persist lunch_customers")
    assert_true("['lunchGroupsByDate', 'lunch_groups']" not in js, "parser does not persist lunch_groups")


def test_food_drink_daily_income_contract() -> None:
    assert_true(field("food_sales").save_target == "dailyIncome", "16. food_sales -> dailyIncome")
    assert_true(field("drink_sales").save_target == "dailyIncome", "17. drink_sales -> dailyIncome")
    assert_true(field("food_sales").zero_behavior == "delete", "food/drink 0 keeps existing delete contract")
    assert_true(field("drink_sales").zero_behavior == "delete", "drink 0 delete contract unchanged")
    helper = (SCRIPTS / "apply_daily_sales_import.py").read_text(encoding="utf-8")
    assert_true("addIncome('food_sales'" in helper, "16. MEP CSV writes food_sales income")
    assert_true("addIncome('drink_sales'" in helper, "17. MEP CSV writes drink_sales income")
    store_js = (SCRIPTS / "kpi_year_store_client.py").read_text(encoding="utf-8")
    assert_true(
        "if (!Number.isFinite(n) || n === 0)" in store_js
        and "delete rec.dailyIncome[streamId][iso];" in store_js,
        "dailyIncome 0-delete contract not changed",
    )
    meal = daily_sales_import_js()
    assert_true("addIncome(" not in meal, "sales parser itself does not write dailyIncome")


def test_missing_zero_invalid_put_via_unit4(u4) -> None:
    before_f = u4.FAILED
    u4.test_missing_vs_zero_and_validation()
    u4.test_persist_five_fields_only()
    u4.test_invalid_no_partial()
    u4.test_mep_valid_import_single_full_put()
    assert_true(u4.FAILED == before_f, "18-21. Unit 4 missing/zero/invalid/PUT tests still green")
    assert_true(field("dinner_sales").missing_behavior == "keep_existing", "18. missing meal keeps existing")
    assert_true(field("dinner_sales").zero_behavior == "save_zero", "19. explicit 0 saves 0")
    assert_true(field("daily_sales").save_target == "dailySales", "22. dailySales is own target")
    maps = u4.rows_to_maps(
        u4.csv_rows(
            ["年月日", "日次売上", "ディナー売上"],
            [["2026-01-01", "132000", "100000"]],
        )
    )
    assert_true(maps["salesByDate"]["2026-01-01"] == 132000, "22. dailySales comes from the sales column")
    assert_true(maps["dinnerSalesByDate"]["2026-01-01"] == 100000, "dinner stored beside total")
    assert_true("2026-01-01" not in maps["lunchSalesByDate"], "missing lunch is not invented")
    assert_true(
        maps["salesByDate"]["2026-01-01"] != maps["dinnerSalesByDate"]["2026-01-01"],
        "22. dailySales is not replaced by dinner_sales",
    )
    store = u4.FakeStore({"dinner_sales": {"2026-01-01": 9}})
    persist_maps = u4.rows_to_maps(
        u4.csv_rows(
            ["年月日", "日次売上", "ディナー売上"],
            [["2026-01-02", "50", ""]],
        )
    )
    u4.persist_daily_meal_from_maps(persist_maps, store)
    assert_true(store.dailyMeal["dinner_sales"]["2026-01-01"] == 9, "18. blank dinner does not delete existing")
    assert_true("2026-01-02" not in store.dailyMeal.get("dinner_sales", {}), "18. missing dinner = no key")


def test_parser_source_unmodified_marker() -> None:
    js = daily_sales_import_js()
    assert_true("/* KPI-DAILY-SALES-IMPORT */" in js, "import marker kept")
    assert_true("function detectColumns(headerRow)" in js, "detectColumns kept")
    assert_true("KpiPlExpensePresets" not in js, "no Business Type / preset gate in sales parser")
    assert_true("getBusinessType" not in js, "no BT gate in sales parser")
    helper = (SCRIPTS / "apply_daily_sales_import.py").read_text(encoding="utf-8")
    assert_true("getBusinessType" not in helper, "apply helper has no BT gate")


def main() -> int:
    print("--- 6A classification / canonical ---")
    test_common_and_restaurant_classification()
    test_canonical_keys()
    print("--- 6A alias freeze vs parser ---")
    test_alias_compatibility_with_parser()
    print("--- 6A required / optional ---")
    test_required_optional()
    print("--- 6A meal persist vs validation-only ---")
    test_meal_persist_vs_validation_only()
    print("--- 6A food/drink dailyIncome ---")
    test_food_drink_daily_income_contract()
    print("--- 6A Unit 4 behavioral freeze ---")
    u4 = load_u4()
    test_missing_zero_invalid_put_via_unit4(u4)
    print("--- 6A no parser / BT gate ---")
    test_parser_source_unmodified_marker()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

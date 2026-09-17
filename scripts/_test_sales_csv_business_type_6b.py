# -*- coding: utf-8 -*-
"""Unit 6B: Sales CSV Business Type gate — COMMON persist, Restaurant-only ignore."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from csv_sales_schema import (  # noqa: E402
    COMMON_KEYS,
    RESTAURANT_ONLY_KEYS,
)
from csv_template_generator import build_sales_template, sales_field_keys  # noqa: E402

FAILED = 0
PASSED = 0

SALES_PARSER = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
APPLY_HELPER = (SCRIPTS / "apply_daily_sales_import.py").read_text(encoding="utf-8")
EXPENSE_PARSER = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")

ANNUAL_HTML = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]
MEP_HTML = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]
NON_RESTAURANT = ("retail", "hair_salon", "fitness", "hotel", "other")


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

CURRENT_BT = "restaurant"


def allows_restaurant_fields(bt=None) -> bool:
    """Missing/legacy BT falls back to restaurant (Unit 4)."""
    if bt is None:
        bt = CURRENT_BT
    if bt is None or bt == "":
        return True
    return bt == "restaurant"


def cell_at(row, idx):
    if idx < 0 or idx >= len(row):
        return None
    return row[idx]


def fill_food_drink(maps, rows, cols, allow_restaurant: bool) -> None:
    maps["foodByDate"] = {}
    maps["drinkByDate"] = {}
    maps["hasFoodCol"] = allow_restaurant and cols["foodIdx"] >= 0
    maps["hasDrinkCol"] = allow_restaurant and cols["drinkIdx"] >= 0
    if not allow_restaurant:
        return
    for row in rows[1:]:
        if not row:
            continue
        iso = u4.parse_date_cell(cell_at(row, cols["dateIdx"]))
        if not iso:
            continue
        has_food = u4.cell_has_value(row, cols["foodIdx"])
        has_drink = u4.cell_has_value(row, cols["drinkIdx"])
        if not has_food and not has_drink:
            continue
        sales = maps["salesByDate"].get(iso, 0)
        food = int(round(u4.parse_sales_cell(cell_at(row, cols["foodIdx"])))) if has_food else None
        drink = int(round(u4.parse_sales_cell(cell_at(row, cols["drinkIdx"])))) if has_drink else None
        if has_food and has_drink:
            pass
        elif has_food:
            drink = max(0, sales - food)
        else:
            food = max(0, sales - drink)
        maps["foodByDate"][iso] = food
        maps["drinkByDate"][iso] = drink


def rows_to_maps(rows, bt=None):
    allow = allows_restaurant_fields(bt)
    if allow:
        maps = u4.rows_to_maps(rows)
        cols = u4.detect_columns(rows[0])
        fill_food_drink(maps, rows, cols, True)
        return maps
    cols = u4.detect_columns(rows[0])
    if cols["dateIdx"] < 0 or cols["salesIdx"] < 0:
        raise ValueError("columns")
    maps = {
        "salesByDate": {},
        "businessDayByDate": {},
        "dinnerSalesByDate": {},
        "lunchSalesByDate": {},
        "totalCustomersByDate": {},
        "lunchCustomersByDate": {},
        "dinnerCustomersByDate": {},
        "totalGroupsByDate": {},
        "lunchGroupsByDate": {},
        "dinnerGroupsByDate": {},
        "foodByDate": {},
        "drinkByDate": {},
        "imported": 0,
        "hasFoodCol": False,
        "hasDrinkCol": False,
    }
    imported = 0
    for row in rows[1:]:
        if not row:
            continue
        iso = u4.parse_date_cell(cell_at(row, cols["dateIdx"]))
        if not iso:
            continue
        sales = int(round(u4.parse_sales_cell(cell_at(row, cols["salesIdx"]))))
        biz = (
            u4.parse_biz_cell(cell_at(row, cols["bizIdx"]))
            if cols["bizIdx"] >= 0
            else None
        )
        maps["salesByDate"][iso] = sales
        if biz is not None:
            maps["businessDayByDate"][iso] = bool(biz)
        imported += 1
    if not imported:
        raise ValueError("rows")
    maps["imported"] = imported
    return maps


class Store:
    def __init__(self):
        self.timeline = {}
        self.businessDays = {}
        self.dailyMeal = {}
        self.dailyIncome = {}
        self.write_log = []
        self.puts = 0
        self.persist_count = 0

    def write_daily_meal(self, field, iso, value):
        self.write_log.append((field, iso, value))
        self.dailyMeal.setdefault(field, {})
        if value is None:
            self.dailyMeal[field].pop(iso, None)
            return True
        self.dailyMeal[field][iso] = int(value)
        return True

    def persist_income(self, maps, allow_restaurant: bool) -> int:
        if not allow_restaurant:
            return 0
        n = 0
        for stream, key in (("food_sales", "foodByDate"), ("drink_sales", "drinkByDate")):
            src = maps.get(key) or {}
            for iso, val in src.items():
                amount = int(round(val))
                self.dailyIncome.setdefault(stream, {})
                if amount == 0:
                    self.dailyIncome[stream].pop(iso, None)
                else:
                    self.dailyIncome[stream][iso] = amount
                n += 1
        return n

    def persist_meal(self, maps, allow_restaurant: bool) -> int:
        if not allow_restaurant:
            return 0
        wrote = 0
        for map_key, field in u4.MEAL_PERSIST_PAIRS:
            src = maps.get(map_key) or {}
            for iso, val in src.items():
                self.write_daily_meal(field, iso, val)
                wrote += 1
        return wrote

    def persist_common(self, maps) -> None:
        for iso, val in (maps.get("salesByDate") or {}).items():
            self.timeline[iso] = int(val)
        for iso, val in (maps.get("businessDayByDate") or {}).items():
            self.businessDays[iso] = bool(val)

    def import_valid(self, maps, bt=None) -> None:
        allow = allows_restaurant_fields(bt)
        self.persist_meal(maps, allow)
        self.persist_income(maps, allow)
        self.persist_common(maps)
        self.puts += 1
        self.persist_count += 1


def csv_rows(header, data_rows):
    return u4.csv_rows(header, data_rows)


RESTAURANT_FULL_HEADER = [
    "年月日",
    "営業日",
    "日次売上",
    "ディナー売上",
    "トータル客数",
    "ディナー客数",
    "トータル組数",
    "ディナー組数",
    "フード売上",
    "ドリンク売上",
    "ランチ売上",
    "ランチ客数",
    "ランチ組数",
]


def restaurant_full_rows():
    return csv_rows(
        RESTAURANT_FULL_HEADER,
        [["2026-01-01", "1", "132000", "100000", "33", "12", "16", "6", "80000", "52000", "32000", "21", "10"]],
    )


def extract_import_block(html: str) -> str:
    m = re.search(r"/\* KPI-DAILY-SALES-IMPORT \*/[\s\S]*?\}\)\(\);", html)
    return m.group(0) if m else ""


def test_source_gate() -> None:
    js = SALES_PARSER
    assert_true("function salesCsvAllowsRestaurantFields" in js, "parser exports BT gate helper")
    assert_true("isRestaurantLike" in js, "gate reads KpiBusinessType.isRestaurantLike")
    assert_true("getBusinessType" not in js, "6A freeze: parser still avoids getBusinessType")
    assert_true("KpiPlExpensePresets" not in js, "sales parser has no expense presets")
    assert_true("KpiCsvTemplates" not in js, "sales parser not coupled to templates")
    assert_true("if (!salesCsvAllowsRestaurantFields()) return 0;" in js, "meal persist no-ops for non-restaurant")
    assert_true("var allowRestaurant = salesCsvAllowsRestaurantFields();" in js, "rowsToMaps consults BT")
    assert_true("if (!allowRestaurant) continue;" in js, "non-restaurant skips restaurant maps")
    assert_true("hasFoodCol: allowRestaurant && cols.foodIdx >= 0" in js, "food col gated in maps")
    assert_true("getBusinessType" not in APPLY_HELPER, "apply helper still avoids getBusinessType")
    assert_true("salesCsvAllowsRestaurantFields" in APPLY_HELPER, "MEP persist uses shared gate")
    assert_true("if (allowRestaurantFields)" in APPLY_HELPER, "MEP income persist is gated")
    assert_true("if (!allowRestaurantFields)" in APPLY_HELPER, "MEP grid ignores restaurant fields")
    assert_true("salesCsvAllowsRestaurantFields" not in EXPENSE_PARSER, "expense parser untouched")


def test_restaurant_unit4() -> None:
    global CURRENT_BT
    CURRENT_BT = "restaurant"
    maps = rows_to_maps(restaurant_full_rows())
    assert_true(maps["salesByDate"]["2026-01-01"] == 132000, "1. dailySales is 総売上")
    assert_true(maps["dinnerSalesByDate"]["2026-01-01"] == 100000, "2. dinner canonical")
    assert_true(maps["lunchSalesByDate"]["2026-01-01"] == 32000, "3. lunch stays in maps for validation")
    assert_true(maps["totalCustomersByDate"]["2026-01-01"] == 33, "4. total customers")
    assert_true(maps["dinnerCustomersByDate"]["2026-01-01"] == 12, "4. dinner customers")
    assert_true(maps["totalGroupsByDate"]["2026-01-01"] == 16, "4. total groups")
    assert_true(maps["dinnerGroupsByDate"]["2026-01-01"] == 6, "4. dinner groups")
    assert_true(maps["foodByDate"]["2026-01-01"] == 80000, "5. food dailyIncome map")
    assert_true(maps["drinkByDate"]["2026-01-01"] == 52000, "5. drink dailyIncome map")
    store = Store()
    store.import_valid(maps)
    assert_true(store.timeline["2026-01-01"] == 132000, "dailySales persisted")
    assert_true(store.dailyMeal["dinner_sales"]["2026-01-01"] == 100000, "dinner persisted")
    assert_true("lunch_sales" not in store.dailyMeal, "3. lunch not saved")
    assert_true("lunch_customers" not in store.dailyMeal, "3. lunch customers not saved")
    assert_true("lunch_groups" not in store.dailyMeal, "3. lunch groups not saved")
    assert_true(store.dailyIncome["food_sales"]["2026-01-01"] == 80000, "5. food persisted")
    assert_true(store.dailyIncome["drink_sales"]["2026-01-01"] == 52000, "5. drink persisted")
    assert_true(store.puts == 1, "9. valid PUT max 1")

    zero_maps = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "ディナー売上", "トータル客数"],
            [["2026-01-02", "0", "0", "0"]],
        )
    )
    store.import_valid(zero_maps)
    assert_true(store.dailyMeal["dinner_sales"]["2026-01-02"] == 0, "6. explicit 0 meal saved")
    assert_true(store.timeline["2026-01-02"] == 0, "6. explicit 0 sales saved")

    keep = Store()
    keep.dailyMeal = {"dinner_sales": {"2026-01-01": 9}}
    keep.dailyIncome = {"food_sales": {"2026-01-01": 40}}
    missing = rows_to_maps(csv_rows(["年月日", "日次売上"], [["2026-01-03", "50"]]))
    keep.import_valid(missing)
    assert_true(keep.dailyMeal["dinner_sales"]["2026-01-01"] == 9, "7. missing meal keeps existing")
    assert_true(keep.dailyIncome["food_sales"]["2026-01-01"] == 40, "7. missing income keeps existing")
    assert_true("2026-01-03" not in keep.dailyMeal.get("dinner_sales", {}), "7. missing = no key")

    bad = Store()
    caught = None
    try:
        rows_to_maps(
            csv_rows(
                ["年月日", "日次売上", "ディナー客数", "トータル客数"],
                [["2026-01-04", "100", "11", "10"]],
            )
        )
        bad.import_valid({})
    except u4.MealInvalid as err:
        caught = err
    assert_true(caught is not None and caught.reason == "dinner-gt-total", "8. invalid meal stops parse")
    assert_true(bad.puts == 0, "8. invalid PUT 0")
    assert_true(bad.timeline == {}, "8. invalid mutation 0")

    zero_food = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "フード売上", "ドリンク売上"],
            [["2026-01-05", "100", "0", "100"]],
        )
    )
    zstore = Store()
    zstore.dailyIncome = {"food_sales": {"2026-01-05": 9}}
    zstore.import_valid(zero_food)
    assert_true("2026-01-05" not in zstore.dailyIncome.get("food_sales", {}), "5. food explicit 0 deletes")
    assert_true(zstore.dailyIncome["drink_sales"]["2026-01-05"] == 100, "5. drink persisted")


def test_retail_common_only() -> None:
    maps = rows_to_maps(
        csv_rows(
            ["date", "business_day", "daily_sales", "dinner_sales", "total_customers", "food_sales", "drink_sales"],
            [["2026-03-01", "1", "4400", "9999", "88", "3000", "1400"]],
        ),
        bt="retail",
    )
    assert_true(maps["salesByDate"]["2026-03-01"] == 4400, "10. retail common sales")
    assert_true(maps["businessDayByDate"]["2026-03-01"] is True, "11. retail business day")
    assert_true(maps["dinnerSalesByDate"] == {}, "12. meal map empty")
    assert_true(maps["totalCustomersByDate"] == {}, "12. customer map empty")
    assert_true(maps["foodByDate"] == {}, "13. food map empty")
    assert_true(maps["drinkByDate"] == {}, "13. drink map empty")
    assert_true(maps["hasFoodCol"] is False, "13. food col not applied")
    store = Store()
    store.dailyMeal = {"dinner_sales": {"2026-03-01": 111}}
    store.dailyIncome = {"food_sales": {"2026-03-01": 222}, "drink_sales": {"2026-03-01": 333}}
    store.import_valid(maps, bt="retail")
    assert_true(store.timeline["2026-03-01"] == 4400, "10. retail sales saved")
    assert_true(store.businessDays["2026-03-01"] is True, "11. retail biz saved")
    assert_true(store.dailyMeal["dinner_sales"]["2026-03-01"] == 111, "14. existing meal not deleted")
    assert_true(store.dailyIncome["food_sales"]["2026-03-01"] == 222, "14. existing income not deleted")
    assert_true(store.dailyIncome["drink_sales"]["2026-03-01"] == 333, "14. existing drink not deleted")
    assert_true(store.write_log == [], "12. dailyMeal mutation none")
    assert_true(store.puts == 1, "15. retail valid PUT max 1")

    bad = Store()
    caught = None
    try:
        rows_to_maps(csv_rows(["not-a-date", "no-sales"], [["x", "y"]]), bt="retail")
        bad.import_valid({}, bt="retail")
    except ValueError as err:
        caught = err
    assert_true(caught is not None, "16. invalid columns rejected")
    assert_true(bad.puts == 0, "16. retail invalid PUT 0")
    assert_true(bad.timeline == {}, "16. retail invalid mutation 0")

    mismatch = rows_to_maps(
        csv_rows(
            ["date", "daily_sales", "dinner_sales", "lunch_sales"],
            [["2026-03-02", "100", "90", "20"]],
        ),
        bt="retail",
    )
    store2 = Store()
    store2.import_valid(mismatch, bt="retail")
    assert_true(store2.timeline["2026-03-02"] == 100, "restaurant-only mismatch does not invalidate COMMON")
    assert_true(store2.dailyMeal == {}, "mismatch dinner ignored")


def test_other_business_types() -> None:
    for bt in NON_RESTAURANT:
        maps = rows_to_maps(
            csv_rows(
                ["date", "daily_sales", "dinner_sales", "food_sales"],
                [["2026-04-01", "2100", "500", "700"]],
            ),
            bt=bt,
        )
        store = Store()
        store.dailyMeal = {"dinner_sales": {"2026-04-01": 8}}
        store.import_valid(maps, bt=bt)
        assert_true(store.timeline["2026-04-01"] == 2100, f"{bt} COMMON sales")
        assert_true(maps["dinnerSalesByDate"] == {}, f"{bt} meal ignored")
        assert_true(maps["foodByDate"] == {}, f"{bt} income ignored")
        assert_true(store.dailyMeal["dinner_sales"]["2026-04-01"] == 8, f"{bt} existing meal kept")
        assert_true(store.puts == 1, f"{bt} PUT max 1")


def test_missing_bt_fallback() -> None:
    maps = rows_to_maps(restaurant_full_rows(), bt=None)
    store = Store()
    store.import_valid(maps, bt=None)
    assert_true(store.dailyMeal["dinner_sales"]["2026-01-01"] == 100000, "21. missing BT restaurant fallback")
    maps_empty = rows_to_maps(restaurant_full_rows(), bt="")
    store2 = Store()
    store2.import_valid(maps_empty, bt="")
    assert_true(store2.dailyMeal["dinner_sales"]["2026-01-01"] == 100000, "21. blank BT restaurant fallback")


def test_switch_preserves_restaurant_data() -> None:
    rest_maps = rows_to_maps(restaurant_full_rows(), bt="restaurant")
    store = Store()
    store.import_valid(rest_maps, bt="restaurant")
    assert_true(store.dailyMeal["dinner_sales"]["2026-01-01"] == 100000, "switch start meal")
    assert_true(store.dailyIncome["food_sales"]["2026-01-01"] == 80000, "switch start income")
    retail_maps = rows_to_maps(
        csv_rows(
            ["date", "daily_sales", "dinner_sales", "food_sales", "drink_sales"],
            [["2026-01-01", "1500", "1", "2", "3"]],
        ),
        bt="retail",
    )
    store.import_valid(retail_maps, bt="retail")
    assert_true(store.timeline["2026-01-01"] == 1500, "22. retail sales overwrote COMMON")
    assert_true(store.dailyMeal["dinner_sales"]["2026-01-01"] == 100000, "22. meal preserved after retail import")
    assert_true(store.dailyIncome["food_sales"]["2026-01-01"] == 80000, "22. food preserved after retail import")
    assert_true(store.dailyIncome["drink_sales"]["2026-01-01"] == 52000, "22. drink preserved after retail import")
    restored = rows_to_maps(
        csv_rows(["date", "daily_sales"], [["2026-01-08", "10"]]),
        bt="restaurant",
    )
    store.import_valid(restored, bt="restaurant")
    assert_true(store.dailyMeal["dinner_sales"]["2026-01-01"] == 100000, "22. meal still there after restaurant restore")
    assert_true(store.dailyIncome["food_sales"]["2026-01-01"] == 80000, "22. income still there after restaurant restore")


def test_locale_machine_keys() -> None:
    ja = rows_to_maps(
        csv_rows(["日付", "営業日", "日次売上"], [["2026-05-01", "1", "700"]]),
        bt="retail",
    )
    en = rows_to_maps(
        csv_rows(["date", "business_day", "daily_sales"], [["2026-05-01", "1", "700"]]),
        bt="hotel",
    )
    zh = rows_to_maps(
        csv_rows(["date", "business_day", "daily_sales"], [["2026-05-01", "1", "700"]]),
        bt="other",
    )
    assert_true(ja["salesByDate"] == en["salesByDate"] == zh["salesByDate"], "cross-locale COMMON maps match")
    rest_en = rows_to_maps(
        csv_rows(["date", "daily_sales", "dinner_sales"], [["2026-05-02", "200", "120"]]),
        bt="restaurant",
    )
    rest_ja = rows_to_maps(
        csv_rows(["年月日", "日次売上", "ディナー売上"], [["2026-05-02", "200", "120"]]),
        bt="restaurant",
    )
    assert_true(
        rest_en["dinnerSalesByDate"] == rest_ja["dinnerSalesByDate"],
        "JA/EN restaurant dinner alias still maps",
    )


def test_schema_and_templates() -> None:
    assert_true(COMMON_KEYS == ("date", "business_day", "daily_sales"), "23. 6A COMMON")
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
        "23. 6A RESTAURANT_ONLY",
    )
    rest_keys = sales_field_keys("restaurant")
    retail_keys = sales_field_keys("retail")
    assert_true(rest_keys[:3] == COMMON_KEYS, "24. 6D restaurant starts COMMON")
    assert_true(rest_keys[3:] == RESTAURANT_ONLY_KEYS, "24. 6D restaurant extension")
    assert_true(retail_keys == COMMON_KEYS, "24. 6D retail COMMON only")
    rest_csv = build_sales_template("restaurant", lang="en")
    retail_csv = build_sales_template("retail", lang="en")
    assert_true("dinner_sales" in rest_csv["text"], "24. restaurant template has dinner_sales")
    assert_true("dinner_sales" not in retail_csv["text"], "24. retail template has no dinner_sales")
    assert_true("food_sales" not in retail_csv["text"], "24. retail template has no food_sales")


def test_runtime_html() -> None:
    from daily_sales_import_client import daily_sales_import_js

    js = daily_sales_import_js()
    blocks = []
    for path in ANNUAL_HTML + MEP_HTML:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        block = extract_import_block(html)
        blocks.append(block)
        assert_true("salesCsvAllowsRestaurantFields" in block, f"{rel} has BT gate")
        assert_true("isRestaurantLike" in block, f"{rel} uses isRestaurantLike")
        assert_true("persistDailyMealFromMaps" in block, f"{rel} still exports meal persist")
        assert_true("getBusinessType" not in block, f"{rel} avoids getBusinessType")
    assert_true(len(set(blocks)) == 1, "JP/EN/ZH-TW import IIFE identical")
    src_block = extract_import_block("      " + js)
    html_norm = re.sub(r"\r\n", "\n", blocks[0]).strip()
    gen_norm = re.sub(r"\r\n", "\n", src_block).strip()
    assert_true(html_norm == gen_norm, "HTML import IIFE matches generator")
    for path in MEP_HTML:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("allowRestaurantFields" in html, f"{rel} MEP persist gated")
        assert_true("writeMealGrid('incDinner'" in html, f"{rel} dinner grid kept")
        assert_true("writeMealGrid('incLunch'" not in html, f"{rel} no lunch grid")
        assert_true("persistFromAnnualDaily" in html, f"{rel} still one full persist path")


def test_regression_suites() -> None:
    before = u4.FAILED
    u4_maps = u4.rows_to_maps(
        u4.csv_rows(
            ["年月日", "日次売上", "ディナー売上", "ランチ売上"],
            [["2026-01-01", "132000", "100000", "32000"]],
        )
    )
    assert_true(u4_maps["salesByDate"]["2026-01-01"] == 132000, "Unit 4 twin still restaurant")
    assert_true(u4_maps["dinnerSalesByDate"]["2026-01-01"] == 100000, "Unit 4 twin dinner")
    assert_true(u4.FAILED == before, "Unit 4 helper not dirtied")
    assert_true("getBusinessType" not in SALES_PARSER, "6A freeze: no getBusinessType in parser")
    assert_true("KpiCsvTemplates" not in SALES_PARSER, "6D freeze: parser not coupled to templates")


def main() -> int:
    print("--- 6B source gate ---")
    test_source_gate()
    print("--- 6B Restaurant Unit 4 ---")
    test_restaurant_unit4()
    print("--- 6B Retail ---")
    test_retail_common_only()
    print("--- 6B other BT ---")
    test_other_business_types()
    print("--- 6B fallback / switch ---")
    test_missing_bt_fallback()
    test_switch_preserves_restaurant_data()
    print("--- 6B locale / schema / 6D ---")
    test_locale_machine_keys()
    test_schema_and_templates()
    print("--- 6B runtime HTML ---")
    test_runtime_html()
    print("--- 6B nested 6A/6D ---")
    test_regression_suites()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

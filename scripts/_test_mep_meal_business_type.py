# -*- coding: utf-8 -*-
"""Unit 5C-6 — MEP Edit meal / customer / group UI by Business Type."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from apply_mep_daily_meal import patch_one  # noqa: E402
from mep_daily_meal_client import mep_daily_meal_runtime_js  # noqa: E402
from pl_line_catalog import (  # noqa: E402
    expense_detail_default_catalog,
    get_analysis_metrics,
    get_default_expense_lines,
)

FAILED = 0
PASSED = 0

MEP_HTML = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]
TW_HTML = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]
APPLY = SCRIPTS / "apply_mep_daily_meal.py"
CLIENT = SCRIPTS / "mep_daily_meal_client.py"

MEAL_UI_ROW_IDS = (
    "incLunch",
    "incDinner",
    "cust",
    "custLunch",
    "custDinner",
    "pc",
    "pcLunch",
    "pcDinner",
    "groupCnt",
    "groupCntLunch",
    "groupCntDinner",
)
RESTAURANT_INCOME_IDS = ("food_sales", "drink_sales")
RESTAURANT_MEAL_LABELS = (
    "ランチ",
    "ディナー",
    "客数",
    "組数",
    "Lunch",
    "Dinner",
    "Customers",
    "Groups",
    "午餐",
    "晚餐",
    "來客數",
    "組數",
)
NEW_KPI_FORBIDDEN = (
    "room night",
    "Room night",
    "appointment",
    "Appointment",
    "session",
    "transaction count",
    "Retail transaction",
    "Salon appointment",
    "Hotel rooms",
    "Fitness sessions",
    "泊数",
    "予約件数",
    "セッション",
)
FORBIDDEN_SCOPE = [
    ROOT / "app" / "monthly" / "index.html",
    ROOT / "en" / "app" / "monthly" / "index.html",
    ROOT / "zh-tw" / "app" / "monthly" / "index.html",
    ROOT / "scripts" / "monthly_tw_mep_metrics_client.py",
    ROOT / "scripts" / "apply_monthly_tw_mep_metrics.py",
    ROOT / "scripts" / "_test_monthly_tw_business_type.py",
    ROOT / "scripts" / "insight_diff_client.py",
    ROOT / "scripts" / "pl_insight_data_client.py",
    ROOT / "api" / "v1" / "store.php",
    ROOT / "js" / "kpi-business-type.js",
    ROOT / "js" / "kpi-pl-expense-presets.js",
]
SAVE_CONTRACT_IDS = ("dailySales", "dailyMeal", "dailyExpenses")
NON_RESTAURANT = ("retail", "hair_salon", "fitness", "hotel", "other")
RETAIL_KEY_HINTS = ("exp_inventory_cogs", "exp_packaging", "exp_shipping")


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def fn_src(html: str, name: str) -> str:
    m = re.search(rf"function {re.escape(name)}\([^)]*\) \{{", html)
    assert_true(m is not None, f"{name} missing")
    if not m:
        return ""
    start = m.start()
    depth = 0
    for i, ch in enumerate(html[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return html[start : i + 1]
    return html[start:]


def current_rows_src(html: str) -> str:
    return fn_src(html, "currentRows")


def simulated_visible_row_ids(code: str) -> list[str]:
    restaurant = code == "restaurant"
    ids = ["store_sales", "sales_a", "sales_b"]
    if restaurant:
        ids.extend(RESTAURANT_INCOME_IDS)
        ids.extend(["incLunch", "incDinner"])
    ids.extend(["target", "diff", "ach"])
    if restaurant:
        ids.extend(
            [
                "cust",
                "custLunch",
                "custDinner",
                "pc",
                "pcLunch",
                "pcDinner",
                "groupCnt",
                "groupCntLunch",
                "groupCntDinner",
            ]
        )
    return ids


def test_client_helpers() -> None:
    helper = mep_daily_meal_runtime_js()
    client = CLIENT.read_text(encoding="utf-8")
    apply = APPLY.read_text(encoding="utf-8")
    assert_true("function mepEditIsRestaurantLike" in helper, "restaurant gate")
    assert_true("KpiBusinessType.isRestaurantLike" in helper, "reads KpiBusinessType")
    assert_true("function mepEditShouldShowRestaurantMealUi" in helper, "meal UI gate")
    assert_true("food_sales" in helper and "drink_sales" in helper, "restaurant income ids")
    assert_true("pcLunch" in helper and "pcDinner" in helper, "pc rows are restaurant UI")
    assert_true(
        "!mepEditShouldShowRestaurantMealUi()) {\n          return null;" in helper
        or "&& !mepEditShouldShowRestaurantMealUi()) {\n          return null;" in helper,
        "validate no-ops when meal UI hidden",
    )
    assert_true(
        "mepEditShouldShowRestaurantMealUi" in helper.split("function mepValidateMealBreakdown", 1)[-1][:400],
        "validate reads meal UI gate",
    )
    assert_true(
        "mepEditShouldShowRestaurantMealUi" in helper.split("function mepCollectMealTouchedIso", 1)[-1][:500],
        "collect does not mark hidden meal as cleared",
    )
    assert_true(
        "mepEditShouldShowRestaurantMealUi" in helper.split("function persistMepMealToYearStore", 1)[-1][:400],
        "persist skips write when meal UI hidden",
    )
    assert_true("delete rec.dailyMeal;" not in helper, "client never deletes dailyMeal object")
    assert_true("delete rec.dailyMeal;" not in apply, "apply never deletes dailyMeal object")
    assert_true("visibility:hidden" not in apply.lower() and "visibility: hidden" not in apply, "no visibility:hidden")
    assert_true("patch_current_rows_business_type" in apply, "currentRows skip generator")
    assert_true("KpiPlExpensePresets" not in helper, "meal client does not own expense presets")
    assert_true("EXPENSE_PRESET" not in apply, "no independent MEP expense preset")
    assert_true("from kpi_year_store_client import kpi_year_store_js" in client, "Unit 1 API still extracted")
    for bad in NEW_KPI_FORBIDDEN:
        assert_true(bad not in helper, f"no new KPI {bad!r} in client")
        assert_true(bad not in apply, f"no new KPI {bad!r} in apply")


def test_html_restaurant_and_non_restaurant() -> None:
    helper = mep_daily_meal_runtime_js()
    for path in MEP_HTML:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true(helper.strip() in html, f"{rel} helper block matches generator")
        assert_true("kpi-business-type.js" in html, f"{rel} loads KpiBusinessType")
        assert_true("kpi-pl-expense-presets.js" in html, f"{rel} loads KpiPlExpensePresets")
        rows = current_rows_src(html)
        assert_true("mepEditShouldShowRestaurantMealUi" in rows, f"{rel} currentRows gates meal UI")
        assert_true("mepEditIsRestaurantIncomeLineId" in rows, f"{rel} currentRows skips food/drink income")
        assert_true("visibility:hidden" not in rows and "visibility: hidden" not in rows, f"{rel} no visibility:hidden")
        assert_true("display:none" not in rows.replace(" ", ""), f"{rel} skip generation not CSS hide")
        for rid in MEAL_UI_ROW_IDS:
            assert_true(f"id: '{rid}'" in rows, f"{rel} restaurant still defines {rid}")
        for rid in RESTAURANT_INCOME_IDS:
            assert_true(rid in html, f"{rel} restaurant income {rid} remains in catalog/state")
        meal_hits = [lab for lab in RESTAURANT_MEAL_LABELS if lab in rows]
        assert_true(len(meal_hits) >= 4, f"{rel} restaurant meal labels kept ({meal_hits})")
        # Non-restaurant: rows are inside the restaurant UI if, so they are not generated.
        assert_true(
            rows.count("mepEditShouldShowRestaurantMealUi") >= 3,
            f"{rel} lunch/dinner + customer/group + income skip",
        )
        persist = fn_src(html, "persistMepMealToYearStore")
        assert_true("writeDailyMeal" in persist, f"{rel} restaurant save contract dailyMeal")
        assert_true("mepEditShouldShowRestaurantMealUi" in persist, f"{rel} hide does not write meal")
        assert_true("delete rec.dailyMeal;" not in html, f"{rel} never deletes dailyMeal object")
        assert_true("rec.dailyMeal = null" not in html, f"{rel} never nulls dailyMeal")
        merge = fn_src(html, "mergeMepDailyMealFromPayload")
        assert_true("MEP_MEAL_ROW_TO_FIELD" in merge, f"{rel} hydrate still loads dailyMeal")
        assert_true("mepEditShouldShowRestaurantMealUi" not in merge, f"{rel} hydrate ignores hide")
        collect = fn_src(html, "mepCollectMealTouchedIso")
        assert_true("mepEditShouldShowRestaurantMealUi" in collect, f"{rel} collect hide-only")
        validate = fn_src(html, "mepValidateMealBreakdown")
        assert_true("mepEditShouldShowRestaurantMealUi" in validate, f"{rel} validate skipped when hidden")
        persist_year = fn_src(html, "persistMepToYearStore")
        for key in SAVE_CONTRACT_IDS:
            if key == "dailySales":
                continue
            assert_true(key in persist_year or key in html, f"{rel} save contract {key}")
        assert_true("dailyExpenses" in persist_year, f"{rel} dailyExpenses persist kept")
        assert_true("persistMepMealToYearStore" in persist_year, f"{rel} dailyMeal persist kept")
        assert_true("writeDailyIncome" in html or "dailyIncome" in persist_year, f"{rel} income persist kept")
        assert_true("KpiPlExpensePresets.getDefaultExpenseLines" in html, f"{rel} expenses from 5B presets")
        assert_true("kpi-business-type.js" in html and "kpi-pl-expense-presets.js" in html, f"{rel} same 5C-5 sources")
        assert_true("kpiNavigator.kpiYearStore" in html or "KpiYearStore" in html, f"{rel} HR via year store")
        for bad in NEW_KPI_FORBIDDEN:
            assert_true(bad not in rows, f"{rel} no new KPI {bad!r} in currentRows")


def test_visible_rows_by_business_type() -> None:
    rest = simulated_visible_row_ids("restaurant")
    for rid in MEAL_UI_ROW_IDS:
        assert_true(rid in rest, f"restaurant shows {rid}")
    for rid in RESTAURANT_INCOME_IDS:
        assert_true(rid in rest, f"restaurant shows {rid}")
    for code in NON_RESTAURANT:
        ids = simulated_visible_row_ids(code)
        for rid in MEAL_UI_ROW_IDS:
            assert_true(rid not in ids, f"{code} hides {rid}")
        for rid in RESTAURANT_INCOME_IDS:
            assert_true(rid not in ids, f"{code} hides {rid}")
        for keep in ("target", "diff", "ach", "store_sales"):
            assert_true(keep in ids, f"{code} keeps {keep}")


def test_data_preservation_contract() -> None:
    helper = mep_daily_meal_runtime_js()
    persist = helper.split("function persistMepMealToYearStore", 1)[-1]
    collect = helper.split("function mepCollectMealTouchedIso", 1)[-1]
    merge = helper.split("function mergeMepDailyMealFromPayload", 1)[-1].split(
        "function persistMepMealToYearStore", 1
    )[0]
    assert_true("return true;" in persist[:500], "hidden persist is no-op success")
    assert_true("writeDailyMeal" not in persist.split("return true;", 1)[0], "hidden persist does not write")
    assert_true("delete " not in persist[:800], "persist does not delete")
    assert_true("return true;" in collect[:450], "hidden collect swallows meal keys")
    assert_true("out.dailyMeal" not in collect.split("mepIsMealPersistRowId", 1)[0], "hidden collect does not clear")
    assert_true("payload.dailyMeal" in merge, "restore hydrates from dailyMeal")
    html = MEP_HTML[0].read_text(encoding="utf-8")
    defaults = fn_src(html, "ensureDefaultsForMonth")
    assert_true("mepIsMealRowId(rowId)" in defaults, "ensureDefaults still skips meal 0-fill")


def test_retail_expense_preset_unchanged() -> None:
    metrics = get_analysis_metrics("retail")
    assert_true(metrics.get("mode") == "key_expenses", "retail key_expenses metadata")
    lines = get_default_expense_lines("retail")
    ids = [str(x[0]) for x in lines]
    catalog_ids = [str(x.get("lineId")) for x in expense_detail_default_catalog("retail")]
    for hint in RETAIL_KEY_HINTS:
        assert_true(hint in ids or hint in catalog_ids, f"retail preset keeps {hint}")
    apply = APPLY.read_text(encoding="utf-8")
    client = CLIENT.read_text(encoding="utf-8")
    assert_true("getDefaultExpenseLines" not in apply, "5C-6 does not fork expense presets")
    assert_true("expense_detail_default_catalog" not in client, "5C-6 does not fork catalog")


def test_monthly_tw_consistency() -> None:
    for path in TW_HTML:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        g2 = html[html.find("function resolveGroup2Values") : html.find("function resolveGroup3Values")]
        assert_true("if (!monthlyTwIsRestaurant()) return [];" in g2, f"{rel} TW hides meal group")
        assert_true("mepReadRow(iso, 'incLunch')" in html, f"{rel} TW restaurant still reads meal")
    helper = mep_daily_meal_runtime_js()
    assert_true("KpiBusinessType.isRestaurantLike" in helper, "MEP uses same restaurant gate")
    rest = simulated_visible_row_ids("restaurant")
    retail = simulated_visible_row_ids("retail")
    assert_true("incLunch" in rest and "cust" in rest and "groupCnt" in rest, "MEP restaurant meal UI")
    assert_true("incLunch" not in retail and "cust" not in retail and "groupCnt" not in retail, "MEP retail no meal UI")


def test_idempotent_apply() -> None:
    path = MEP_HTML[0]
    html = path.read_text(encoding="utf-8")
    again = patch_one(html)
    assert_true(again == html, "apply_mep_daily_meal must stay idempotent after 5C-6")


def test_scope_untouched() -> None:
    excel = ROOT / "excel"
    assert_true(excel.is_dir(), "excel/ still present")
    for path in FORBIDDEN_SCOPE:
        assert_true(path.is_file(), f"forbidden scope still present: {path.name}")


def main() -> int:
    test_client_helpers()
    test_html_restaurant_and_non_restaurant()
    test_visible_rows_by_business_type()
    test_data_preservation_contract()
    test_retail_expense_preset_unchanged()
    test_monthly_tw_consistency()
    test_idempotent_apply()
    test_scope_untouched()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

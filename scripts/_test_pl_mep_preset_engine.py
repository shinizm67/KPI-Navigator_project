# -*- coding: utf-8 -*-
"""Unit 5B-1 — Business Type PL/MEP expense preset engine."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pl_line_catalog import (  # noqa: E402
    BUSINESS_TYPE_CANONICAL,
    CATALOG_SCHEMA_VERSION,
    EXPENSE_DETAIL_LINES_V1,
    EXPENSE_PRESET_LINES,
    catalog_from_expense_tuples,
    expense_detail_default_catalog,
    get_default_expense_lines,
    has_defined_expense_preset,
    mep_catalog_entries,
    normalize_business_type_for_preset,
    reconcile_catalog_lines,
)

FAILED = 0
PASSED = 0

# Frozen restaurant contract from Unit 5B-1 start (do not invent new titles).
FROZEN_RESTAURANT = [
    ("exp_rent", "家賃", "Rent", "fixed", "monthly", True, "occupancy"),
    ("exp_fixed_asset_tax", "固定資産税", "Fixed asset tax", "fixed", "monthly", False, "labor_related"),
    ("exp_fixed_labor", "固定人件費", "Fixed Labor", "fixed", "monthly", True, "salaries_wages"),
    ("exp_lease", "リース料", "Lease", "fixed", "monthly", False, "lease"),
    ("exp_depreciable_asset_tax", "償却資産税", "Depreciable asset tax", "fixed", "monthly", False, "property_tax"),
    ("exp_depreciation", "減価償却費", "Depreciation expenses", "fixed", "monthly", False, "depreciation"),
    ("exp_non_life_insurance", "損害保険", "Non-life insurance", "fixed", "monthly", True, "insurance"),
    ("exp_social_insurance", "社会保険", "social insurance", "fixed", "monthly", False, "insurance"),
    ("exp_food_cost", "食材仕入れ費", "Food cost", "variable", "daily", True, "food_cost"),
    ("exp_drink_cost", "ドリンク仕入れ費", "Drink Cost", "variable", "daily", True, "drink_cost"),
    ("exp_supplies", "備品・消耗品仕入費", "Supplies & Consumables", "variable", "monthly", True, "supplies"),
    ("exp_misc", "雑費・小口精算費", "Miscellaneous Expense", "variable", "monthly", True, "miscellaneous"),
    ("exp_electric", "電気代", "Electricity Cost", "variable", "monthly", True, "utilities"),
    ("exp_gas", "ガス代", "Gas Cost", "variable", "monthly", True, "utilities"),
    ("exp_water", "水道代", "Water Cost", "variable", "monthly", True, "utilities"),
    ("exp_variable_labor", "アルバイト人件費", "Variable Labor", "variable", "daily", True, "variable_labor"),
    ("exp_telecom", "通信費", "Communication", "variable", "monthly", True, "communication"),
    ("exp_advertising", "広告宣伝費", "Advertising", "variable", "monthly", True, "advertising"),
    ("exp_uniforms", "被服費", "Uniforms & Workwear", "variable", "monthly", False, "uniforms"),
    ("exp_payment_fees", "クレジットカード手数料", "Payment Processing Fees", "variable", "monthly", True, "payment_fees"),
    ("exp_employment_insurance", "雇用保険", "employment insurance", "variable", "monthly", False, "labor_related"),
    ("exp_workers_comp", "労災保険", "Worker's compensation insurance", "variable", "monthly", False, "labor_related"),
    ("exp_consumption_tax", "消費税", "consumption tax", "variable", "monthly", False, "taxes"),
]

UNSET_TYPES = ("retail", "hair_salon", "personal_trainer", "hotel", "other")

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]
MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def test_restaurant_catalog_unchanged() -> None:
    assert_true(list(EXPENSE_DETAIL_LINES_V1) == FROZEN_RESTAURANT, "restaurant tuples unchanged")
    assert_true(
        list(get_default_expense_lines("restaurant")) == FROZEN_RESTAURANT,
        "get_default_expense_lines(restaurant) matches frozen set",
    )
    assert_true(
        get_default_expense_lines() == FROZEN_RESTAURANT,
        "default catalog arg is restaurant",
    )
    cat = expense_detail_default_catalog("restaurant")
    frozen_cat = catalog_from_expense_tuples(FROZEN_RESTAURANT)
    assert_true(cat == frozen_cat, "restaurant catalog dicts match frozen")
    by_id = {row["lineId"]: row for row in cat}
    assert_true(by_id["exp_food_cost"]["expenseAttribute"] == "food_cost", "food attr kept")
    assert_true(by_id["exp_drink_cost"]["expenseAttribute"] == "drink_cost", "drink attr kept")
    assert_true(by_id["exp_variable_labor"]["inputStyle"] == "daily", "variable labor daily")
    assert_true(by_id["exp_rent"]["bucket"] == "fixed", "rent still fixed")
    assert_true(by_id["exp_food_cost"]["lineId"] == "exp_food_cost", "food lineId unchanged")
    assert_true(CATALOG_SCHEMA_VERSION == 8, "schema version not bumped")


def test_selector_six_canonical() -> None:
    assert_true(
        BUSINESS_TYPE_CANONICAL
        == ("restaurant", "retail", "hair_salon", "personal_trainer", "hotel", "other"),
        "selector lists the 6 canonical types",
    )
    for code in BUSINESS_TYPE_CANONICAL:
        assert_true(code in EXPENSE_PRESET_LINES, f"preset map has {code}")
        assert_true(normalize_business_type_for_preset(code) == code, f"{code} stays itself")
    assert_true(has_defined_expense_preset("restaurant") is True, "restaurant preset defined")
    for code in UNSET_TYPES:
        assert_true(has_defined_expense_preset(code) is False, f"{code} preset unset")
        lines = get_default_expense_lines(code)
        assert_true(lines == [], f"{code} does not invent default titles")
        ids = {row[0] for row in lines}
        assert_true("exp_food_cost" not in ids, f"{code} does not spawn restaurant food")
        assert_true("exp_drink_cost" not in ids, f"{code} does not spawn restaurant drink")


def test_unknown_fallback_restaurant() -> None:
    assert_true(normalize_business_type_for_preset("not-a-type") == "restaurant", "unknown → restaurant")
    assert_true(normalize_business_type_for_preset("") == "restaurant", "empty → restaurant")
    assert_true(normalize_business_type_for_preset(None) == "restaurant", "None → restaurant")
    assert_true(has_defined_expense_preset("foobar") is True, "unknown uses defined restaurant preset")
    assert_true(
        get_default_expense_lines("foobar") == FROZEN_RESTAURANT,
        "unknown businessType falls back to restaurant catalog",
    )


def test_mep_mirrors_pl_parent() -> None:
    restaurant_mep = mep_catalog_entries("restaurant")
    default_mep = mep_catalog_entries()
    assert_true(restaurant_mep == default_mep, "MEP default is restaurant (PL parent)")
    income_ids = [r["lineId"] for r in restaurant_mep if r["section"] == "income"]
    expense_ids = [r["lineId"] for r in restaurant_mep if r["section"] == "expense"]
    assert_true(income_ids == ["store_sales", "sales_a", "sales_b", "food_sales", "drink_sales"], "MEP income contract")
    assert_true(expense_ids == [row[0] for row in FROZEN_RESTAURANT], "MEP expense ids follow PL restaurant")
    food = next(r for r in restaurant_mep if r["lineId"] == "exp_food_cost")
    assert_true(food["mepEditable"] is True, "food stays MEP daily editable")
    retail_mep = mep_catalog_entries("retail")
    retail_exp = [r for r in retail_mep if r["section"] == "expense"]
    retail_inc = [r for r in retail_mep if r["section"] == "income"]
    assert_true(retail_exp == [], "unset preset does not embed restaurant expenses on MEP")
    assert_true(len(retail_inc) == 5, "MEP income still present for unset types")
    src = (ROOT / "scripts" / "pl_line_catalog.py").read_text(encoding="utf-8")
    assert_true("MEP is the parent" not in src, "comment does not invert parent/child")
    assert_true("PL is the parent expense master" in src, "PL remains parent")


def test_custom_and_saved_amounts_kept() -> None:
    restaurant = expense_detail_default_catalog("restaurant")
    custom = {
        "lineId": "exp_custom_variable_abc123",
        "labelJa": "独自費目",
        "labelEn": "Shop custom",
        "bucket": "variable",
        "inputStyle": "monthly",
        "resolvedInputStyle": "monthly",
        "isDefault": False,
        "active": True,
        "sortOrder": 99,
    }
    old = json.loads(json.dumps(restaurant))
    for row in old:
        if row["lineId"] == "exp_uniforms":
            row["active"] = False
    old.append(custom)
    amounts = {
        "exp_food_cost:0": 1111,
        "exp_rent:6": 2222,
        "exp_custom_variable_abc123:0": 3333,
        "exp_uniforms:0": 4444,
    }
    snapshot_amounts = json.loads(json.dumps(amounts))

    still_restaurant = json.loads(json.dumps(old))
    for row in still_restaurant:
        if row["lineId"] == "exp_food_cost":
            row["active"] = False
    kept_hidden = reconcile_catalog_lines(still_restaurant, "restaurant")
    food_hidden = next(row for row in kept_hidden if row["lineId"] == "exp_food_cost")
    assert_true(food_hidden.get("active") is False, "user-hidden restaurant default stays hidden")
    assert_true(food_hidden.get("presetOrphan") is not True, "same-preset hide is not an orphan")

    switched = reconcile_catalog_lines(old, "retail")
    ids = [row["lineId"] for row in switched]
    food = next(row for row in switched if row["lineId"] == "exp_food_cost")
    custom_kept = next(row for row in switched if row["lineId"] == "exp_custom_variable_abc123")
    assert_true(food.get("presetOrphan") is True, "old restaurant default is orphaned, not deleted")
    assert_true(food.get("active") is False, "orphaned default is hidden")
    assert_true(custom_kept.get("active") is True, "custom stays active")
    assert_true(custom_kept.get("presetOrphan") is not True, "custom is not marked orphan")
    assert_true("exp_custom_variable_abc123" in ids, "custom lineId retained")
    assert_true("exp_food_cost" in ids, "saved default lineId retained")
    assert_true(amounts == snapshot_amounts, "amount map is not mutated by catalog reconcile")

    back = reconcile_catalog_lines(switched, "restaurant")
    food_back = next(row for row in back if row["lineId"] == "exp_food_cost")
    custom_back = next(row for row in back if row["lineId"] == "exp_custom_variable_abc123")
    uniforms_back = next(row for row in back if row["lineId"] == "exp_uniforms")
    assert_true(food_back.get("active") is True, "returning to restaurant restores default active")
    assert_true("presetOrphan" not in food_back, "restored default drops orphan flag")
    assert_true(custom_back["lineId"] == "exp_custom_variable_abc123", "custom survives round-trip")
    assert_true(uniforms_back.get("active") is False, "user-hidden default stays hidden after round-trip")
    assert_true(amounts == snapshot_amounts, "amounts still untouched after round-trip")


def test_runtime_files_and_pages() -> None:
    js = (ROOT / "js" / "kpi-pl-expense-presets.js").read_text(encoding="utf-8")
    assert_true("getDefaultExpenseLines" in js, "runtime exposes getDefaultExpenseLines")
    assert_true("hasDefinedPreset" in js, "runtime exposes hasDefinedPreset")
    assert_true("reconcileCatalogLines" in js, "runtime exposes reconcile")
    assert_true('"status": "unset"' in js, "non-restaurant presets are unset")
    assert_true("exp_food_cost" in js, "restaurant food remains in restaurant preset")
    bt = (ROOT / "js" / "kpi-business-type.js").read_text(encoding="utf-8")
    for code in BUSINESS_TYPE_CANONICAL:
        assert_true(f"'{code}'" in bt, f"5A helper still lists {code}")
        assert_true(f'"{code}"' in js, f"preset JS lists {code}")

    client = (ROOT / "scripts" / "pl_expense_detail_client.py").read_text(encoding="utf-8")
    assert_true("currentPresetLines" in client, "PL client selects preset at runtime")
    apply = (ROOT / "scripts" / "apply_mep_pl_catalog.py").read_text(encoding="utf-8")
    assert_true("hasDefinedPreset" in apply, "MEP generator uses PL preset selector")

    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-business-type.js" in html, f"{rel} loads BT helper")
        assert_true("kpi-pl-expense-presets.js" in html, f"{rel} loads preset engine")
        assert_true("currentPresetLines" in html, f"{rel} uses currentPresetLines")
        assert_true('"lineId": "exp_food_cost"' in html or '"lineId":"exp_food_cost"' in html, f"{rel} still embeds restaurant DEFAULT_LINES")
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-business-type.js" in html, f"{rel} loads BT helper")
        assert_true("kpi-pl-expense-presets.js" in html, f"{rel} loads preset engine")
        assert_true("hasDefinedPreset" in html, f"{rel} does not fall back to restaurant embed when unset")
        assert_true("PL-MEP-LINE-CATALOG" in html, f"{rel} still has PL→MEP catalog marker")


def test_did_not_touch_forbidden_surfaces() -> None:
    insight = (ROOT / "scripts" / "pl_analyze_client.py").read_text(encoding="utf-8")
    assert_true("KpiPlExpensePresets" not in insight, "PL Insight / analyze client untouched")
    year_store = (ROOT / "scripts" / "kpi_year_store_client.py").read_text(encoding="utf-8")
    assert_true("KpiPlExpensePresets" not in year_store, "year-store client not widened")
    meal = (ROOT / "scripts" / "mep_daily_meal_client.py").read_text(encoding="utf-8")
    assert_true("KpiPlExpensePresets" not in meal, "MEP meal client untouched")
    schema = (ROOT / "api" / "v1" / "schema.sql").read_text(encoding="utf-8")
    assert_true("business_type" not in schema.lower(), "no DB business_type column")
    store_php = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
    assert_true("KpiPlExpensePresets" not in store_php, "store.php API untouched")
    csv = (ROOT / "scripts" / "_test_daily_sales_meal_csv_import.py").read_text(encoding="utf-8")
    assert_true("get_default_expense_lines" not in csv, "Unit 4 CSV tests not rewritten")


def main() -> int:
    test_restaurant_catalog_unchanged()
    test_selector_six_canonical()
    test_unknown_fallback_restaurant()
    test_mep_mirrors_pl_parent()
    test_custom_and_saved_amounts_kept()
    test_runtime_files_and_pages()
    test_did_not_touch_forbidden_surfaces()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

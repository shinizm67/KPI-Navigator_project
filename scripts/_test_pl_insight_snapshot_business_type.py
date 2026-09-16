# -*- coding: utf-8 -*-
"""Unit 5C-0 / 5C-1 — PL Insight FL snapshot Business Type adaptation."""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pl_line_catalog import (  # noqa: E402
    KEY_EXPENSE_ANALYZE_MODE,
    LABOR_ANALYSIS_ATTRIBUTES,
    LABOR_ANALYSIS_LINE_IDS,
    RESTAURANT_ANALYZE_MODE,
    expense_detail_default_catalog,
    get_analysis_metrics,
)

FAILED = 0
PASSED = 0

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]

INSIGHT_CLIENT = _SCRIPTS / "pl_insight_data_client.py"
COMPARE_BUILDER = _SCRIPTS / "build_pl_table_page.py"

FOOD_IDS = {"exp_food_cost", "exp_drink_cost"}
FOOD_ATTRS = {"food_cost", "drink_cost"}
LABOR_IDS = set(LABOR_ANALYSIS_LINE_IDS)
LABOR_ATTRS = set(LABOR_ANALYSIS_ATTRIBUTES)

EXPECTED_KEY_LINE_IDS = {
    "retail": ("exp_inventory_cogs", "exp_packaging", "exp_shipping"),
    "hair_salon": ("exp_treatment_materials", "exp_retail_product_cogs"),
    "fitness": ("exp_facility_fee", "exp_training_equipment", "exp_equipment_maintenance"),
    "hotel": (
        "exp_linen_cleaning",
        "exp_cleaning_supplies",
        "exp_cleaning_outsource",
        "exp_ota_fees",
    ),
    "other": ("exp_materials", "exp_outsourcing"),
}

EXPECTED_LEFT_MAJOR = {
    "ja": "主要費目",
    "en": "Key costs",
    "zh": "主要費目",
}

GRAPH_METRICS = "var METRICS = ['income', 'expenses', 'fixed', 'expected', 'profit'];"
GRAPH_SERIES = "var SERIES = ['thisYear', 'lastYear', 'bestYear'];"
HOLD_FN = "function bindPlCompareDateHoldRepeat"
LIGHT_THIS = "pl-compare-series--thisYear"
LIGHT_LAST = "pl-compare-series--lastYear"
LIGHT_BEST = "pl-compare-series--bestYear"

FORBIDDEN_NON_RESTAURANT = ("Food", "FL", "フード", "ドリンク", "餐點")


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def _key_line_ids(code: str) -> set[str]:
    ids: set[str] = set()
    for group in get_analysis_metrics(code).get("groups") or []:
        for row in group.get("rows") or []:
            if row.get("source") == "labor":
                continue
            ids.update(row.get("lineIds") or [])
    return ids


def classify_line(line: dict, code: str) -> str:
    metrics = get_analysis_metrics(code)
    lid = line.get("lineId")
    attr = line.get("expenseAttribute")
    if metrics.get("mode") != KEY_EXPENSE_ANALYZE_MODE:
        if attr in FOOD_ATTRS or lid in FOOD_IDS:
            return "left"
        if attr in LABOR_ATTRS or lid in LABOR_IDS:
            return "labor"
        return "ignore"
    if attr in LABOR_ATTRS or lid in LABOR_IDS:
        return "labor"
    if lid in _key_line_ids(code):
        return "left"
    return "ignore"


def snapshot_from_amounts(code: str, amounts: dict[str, float], income: float) -> dict:
    left = 0.0
    labor = 0.0
    for line in expense_detail_default_catalog(code):
        amt = float(amounts.get(line["lineId"], 0) or 0)
        if not amt:
            continue
        side = classify_line(line, code)
        if side == "left":
            left += amt
        elif side == "labor":
            labor += amt
    if not income and not left and not labor:
        return {"empty": True}
    out = {
        "income": income,
        "left": left,
        "labor": labor,
        "total": left + labor,
        "empty": False,
    }
    if income > 0:
        out["f_rate"] = left / income
        out["l_rate"] = labor / income
        out["fl_rate"] = (left + labor) / income
    else:
        out["f_rate"] = None
        out["l_rate"] = None
        out["fl_rate"] = None
    return out


def test_restaurant_canonical_fl() -> None:
    metrics = get_analysis_metrics("restaurant")
    assert_true(metrics["mode"] == RESTAURANT_ANALYZE_MODE, "restaurant mode is restaurant_fl")
    snap = snapshot_from_amounts(
        "restaurant",
        {
            "exp_food_cost": 100,
            "exp_drink_cost": 50,
            "exp_variable_labor": 30,
            "exp_fixed_labor": 50,
            "exp_rent": 999,
        },
        1000,
    )
    assert_true(snap["left"] == 150, "F amount = food + drink")
    assert_true(snap["labor"] == 80, "L amount = labor")
    assert_true(snap["total"] == 230, "FL amount = food + drink + labor")
    assert_true(abs(snap["f_rate"] - 0.15) < 1e-9, "F rate = 15%")
    assert_true(abs(snap["l_rate"] - 0.08) < 1e-9, "L rate = 8%")
    assert_true(abs(snap["fl_rate"] - 0.23) < 1e-9, "FL rate = 23%")
    assert_true(snap["left"] != 100, "drink is included in restaurant F")


def test_zero_income_no_nan() -> None:
    snap = snapshot_from_amounts(
        "restaurant",
        {"exp_food_cost": 10, "exp_variable_labor": 5},
        0,
    )
    assert_true(snap["f_rate"] is None, "zero income F rate is dash not 0/NaN")
    assert_true(snap["l_rate"] is None, "zero income L rate is dash")
    assert_true(snap["fl_rate"] is None, "zero income FL rate is dash")
    for key in ("f_rate", "l_rate", "fl_rate"):
        val = snap[key]
        assert_true(val is None or (isinstance(val, float) and math.isfinite(val)), f"{key} not NaN/Inf")

    empty = snapshot_from_amounts("retail", {}, 0)
    assert_true(empty["empty"] is True, "all-zero snapshot is empty")


def test_non_restaurant_mappings() -> None:
    for code, line_ids in EXPECTED_KEY_LINE_IDS.items():
        metrics = get_analysis_metrics(code)
        assert_true(metrics["mode"] == KEY_EXPENSE_ANALYZE_MODE, f"{code} uses key_expenses")
        got = tuple(sorted(_key_line_ids(code)))
        want = tuple(sorted(line_ids))
        assert_true(got == want, f"{code} key lineIds {got} == {want}")

        amounts = {lid: 10.0 for lid in line_ids}
        amounts["exp_variable_labor"] = 40.0
        amounts["exp_food_cost"] = 777.0
        amounts["exp_drink_cost"] = 777.0
        snap = snapshot_from_amounts(code, amounts, 200.0)
        assert_true(snap["left"] == 10.0 * len(line_ids), f"{code} left sums key expenses only")
        assert_true(snap["labor"] == 40.0, f"{code} labor from labor lines")
        assert_true(snap["left"] != 777.0 * 2, f"{code} ignores restaurant food/drink")
        assert_true(abs(snap["l_rate"] - 0.2) < 1e-9, f"{code} L = labor/income")
        assert_true(
            abs(snap["fl_rate"] - ((10.0 * len(line_ids) + 40.0) / 200.0)) < 1e-9,
            f"{code} total rate = (key + labor)/income",
        )


def test_client_uses_existing_metadata() -> None:
    src = INSIGHT_CLIENT.read_text(encoding="utf-8")
    assert_true("getAnalysisMetrics" in src, "Insight snapshot reads getAnalysisMetrics")
    assert_true("KpiPlExpensePresets" in src, "Insight snapshot uses existing preset helper")
    assert_true("UNIT-5C-1-PL-INSIGHT-BT-BEGIN" in src, "5C-1 marker present")
    assert_true("plInsightClassifyLine" in src, "classify helper present")
    assert_true("plInsightSnapshotCopy" in src, "snapshotCopy labels helper present")
    assert_true(GRAPH_METRICS in src, "chart METRICS contract unchanged")
    assert_true(GRAPH_SERIES in src, "chart SERIES contract unchanged")
    assert_true("function buildArea1" in src, "buildArea1 kept")
    assert_true("function lineBreakdown" in src, "expense breakdown kept")
    assert_true("new canonical" not in src.lower(), "no second canonical table")

    builder = COMPARE_BUILDER.read_text(encoding="utf-8")
    assert_true("snapshotBarLabels" in builder, "compare overlay uses snapshot labels")
    assert_true("applySnapshotAreaTitles" in builder, "area titles follow Business Type")
    assert_true(HOLD_FN in builder, "long-press binder unchanged")
    assert_true("hasIncome" in builder, "zero income uses dash path")
    assert_true("function bindPlCompareDateHoldRepeat" in builder, "hold function still defined")


def test_runtime_pages_and_labels() -> None:
    client = INSIGHT_CLIENT.read_text(encoding="utf-8")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-pl-expense-presets.js" in html, f"{rel} loads presets")
        assert_true("UNIT-5C-1-PL-INSIGHT-BT-BEGIN" in html, f"{rel} has 5C-1 snapshot adapter")
        assert_true("snapshotCopy" in html, f"{rel} exposes snapshotCopy")
        assert_true(GRAPH_METRICS in html, f"{rel} METRICS unchanged")
        assert_true(GRAPH_SERIES in html, f"{rel} SERIES unchanged")
        assert_true(LIGHT_THIS in html and LIGHT_LAST in html and LIGHT_BEST in html, f"{rel} year series classes kept")
        assert_true("bindPlCompareDateHoldRepeat" in html, f"{rel} long-press kept")
        assert_true("compare_area1_title_key" in html, f"{rel} has non-restaurant area titles")
        assert_true("Food & Labor" in html or "餐點與人事" in html, f"{rel} restaurant labels still present")

    assert_true("主要費目" in client, "key group major is reused for non-restaurant left label")
    for word in ("Food & Labor", "Food / Labor"):
        assert_true(word in client, f"restaurant fallback still has {word}")

    # Non-restaurant copy must not mint F/FL names in the key-expense branch.
    start = client.find("plInsightIsRestaurantFl()")
    key_branch = client[client.find("restaurant: false"): client.find("UNIT-5C-1-PL-INSIGHT-BT-END")]
    for bad in FORBIDDEN_NON_RESTAURANT:
        assert_true(bad not in key_branch, f"non-restaurant snapshotCopy has no {bad!r}")
    assert_true("plInsightLaborShort" in client, "L label helper present")
    void_start = start  # keep start used
    assert_true(void_start >= 0, "isRestaurantFl helper exists")


def test_graph_and_hold_not_rewritten() -> None:
    builder = COMPARE_BUILDER.read_text(encoding="utf-8")
    assert_true("function bindPlCompareDateHoldRepeat" in builder, "hold function exists")
    assert_true("window.__PL_COMPARE_DATE_HOLDING" in builder, "hold flag exists")
    assert_true("light: true" in builder, "light chart path exists")
    assert_true("function renderArea1LineChart" in builder or "renderArea1Line" in builder or "pl-compare-series--thisYear" in builder, "line series render kept")
    insight = INSIGHT_CLIENT.read_text(encoding="utf-8")
    assert_true("function buildArea1(isoStr)" in insight, "Area1 chart builder untouched name")
    assert_true("function buildArea2(isoStr)" in insight, "Area2 chart builder untouched name")
    assert_true("function buildArea3(isoStr)" in insight, "Area3 chart builder untouched name")
    assert_true("function lineBreakdown(year, month0)" in insight, "breakdown builder untouched")


def main() -> int:
    test_restaurant_canonical_fl()
    test_zero_income_no_nan()
    test_non_restaurant_mappings()
    test_client_uses_existing_metadata()
    test_graph_and_hold_not_rewritten()
    test_runtime_pages_and_labels()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

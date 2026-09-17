# -*- coding: utf-8 -*-
"""Unit 5C-2 — Insight Summary Monthly/Annual Business Type adaptation."""
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

INSIGHT_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]

EXPENSE_CLIENT = _SCRIPTS / "insight_expense_read_client.py"
DIFF_CLIENT = _SCRIPTS / "insight_diff_client.py"

FOOD_IDS = {"exp_food_cost"}
DRINK_IDS = {"exp_drink_cost"}
FOOD_ATTRS = {"food_cost"}
DRINK_ATTRS = {"drink_cost"}
LABOR_IDS = set(LABOR_ANALYSIS_LINE_IDS)
LABOR_ATTRS = set(LABOR_ANALYSIS_ATTRIBUTES)

EXPECTED_KEY_ROWS = {
    "retail": ("exp_inventory_cogs", ("exp_packaging", "exp_shipping")),
    "hair_salon": ("exp_treatment_materials", "exp_retail_product_cogs"),
    "fitness": ("exp_facility_fee", ("exp_training_equipment", "exp_equipment_maintenance")),
    "hotel": (
        ("exp_linen_cleaning", "exp_cleaning_supplies", "exp_cleaning_outsource"),
        "exp_ota_fees",
    ),
    "other": ("exp_materials", "exp_outsourcing"),
}

FORBIDDEN_NON_RESTAURANT = ("Food", "Drink", "FL Rate", "FL率", "フード", "ドリンク", "餐點", "FL 率")


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def _as_ids(spec) -> tuple[str, ...]:
    if isinstance(spec, str):
        return (spec,)
    return tuple(spec)


def _key_rows(code: str) -> list[dict]:
    rows: list[dict] = []
    for group in get_analysis_metrics(code).get("groups") or []:
        for row in group.get("rows") or []:
            if row.get("source") == "labor":
                continue
            rows.append(row)
    return rows[:2]


def classify_line(line: dict, code: str) -> str:
    lid = line.get("lineId")
    attr = line.get("expenseAttribute")
    metrics = get_analysis_metrics(code)
    if attr in LABOR_ATTRS or lid in LABOR_IDS:
        return "labor"
    if metrics.get("mode") != KEY_EXPENSE_ANALYZE_MODE:
        if attr in FOOD_ATTRS or lid in FOOD_IDS:
            return "food"
        if attr in DRINK_ATTRS or lid in DRINK_IDS:
            return "drink"
        return "other"
    key_rows = _key_rows(code)
    if key_rows and lid in set(key_rows[0].get("lineIds") or []):
        return "key0"
    if len(key_rows) > 1 and lid in set(key_rows[1].get("lineIds") or []):
        return "key1"
    return "other"


def summary_from_amounts(code: str, amounts: dict[str, float], sales: float) -> dict:
    fixed = 0.0
    variable = 0.0
    food = 0.0
    drink = 0.0
    labor = 0.0
    key0 = 0.0
    key1 = 0.0
    for line in expense_detail_default_catalog(code):
        amt = float(amounts.get(line["lineId"], 0) or 0)
        if not amt:
            continue
        if line.get("bucket") == "fixed":
            fixed += amt
        else:
            variable += amt
        side = classify_line(line, code)
        if side == "food":
            food += amt
        elif side == "drink":
            drink += amt
        elif side == "labor":
            labor += amt
        elif side == "key0":
            key0 += amt
        elif side == "key1":
            key1 += amt
    misc = max(0.0, variable - food - drink)
    out = {
        "fixed": fixed,
        "variable": variable,
        "total": fixed + variable,
        "food": food,
        "drink": drink,
        "misc": misc,
        "labor": labor,
        "key0": key0,
        "key1": key1,
        "residual_variable": max(0.0, variable - key0 - key1),
    }
    if sales > 0:
        out["cost_rate"] = (fixed + variable) / sales
        out["fl_rate"] = (food + drink + labor) / sales
        out["l_rate"] = labor / sales
        out["food_rate"] = food / sales
        out["drink_rate"] = drink / sales
        out["misc_rate"] = misc / sales
        out["key0_rate"] = key0 / sales
        out["key1_rate"] = key1 / sales
    else:
        for key in (
            "cost_rate",
            "fl_rate",
            "l_rate",
            "food_rate",
            "drink_rate",
            "misc_rate",
            "key0_rate",
            "key1_rate",
        ):
            out[key] = None
    return out


def test_restaurant_fl_includes_drink() -> None:
    metrics = get_analysis_metrics("restaurant")
    assert_true(metrics["mode"] == RESTAURANT_ANALYZE_MODE, "restaurant mode restaurant_fl")
    snap = summary_from_amounts(
        "restaurant",
        {
            "exp_food_cost": 100,
            "exp_drink_cost": 50,
            "exp_variable_labor": 30,
            "exp_fixed_labor": 50,
            "exp_supplies": 20,
            "exp_rent": 10,
        },
        1000,
    )
    assert_true(snap["food"] == 100, "Food amount")
    assert_true(snap["drink"] == 50, "Drink amount")
    assert_true(snap["labor"] == 80, "Labor amount")
    assert_true(snap["misc"] == 50, "Misc = variable - food - drink (30 labor + 20 supplies)")
    assert_true(abs(snap["fl_rate"] - 0.23) < 1e-9, "FL = (food+drink+labor)/sales")
    assert_true(snap["fl_rate"] != (100 + 80) / 1000, "old Food+Labor FL is rejected")
    assert_true(abs(snap["food_rate"] - 0.1) < 1e-9, "Food rate")
    assert_true(abs(snap["drink_rate"] - 0.05) < 1e-9, "Drink rate")
    assert_true(abs(snap["cost_rate"] - 0.26) < 1e-9, "Cost Rate = total/sales")


def test_zero_sales_dash() -> None:
    snap = summary_from_amounts(
        "restaurant",
        {"exp_food_cost": 10, "exp_variable_labor": 5},
        0,
    )
    for key in ("fl_rate", "cost_rate", "l_rate", "food_rate"):
        assert_true(snap[key] is None, f"zero sales {key} is dash")
        val = snap[key]
        assert_true(val is None or (isinstance(val, float) and math.isfinite(val)), f"{key} not NaN")


def test_non_restaurant_mappings() -> None:
    for code, spec in EXPECTED_KEY_ROWS.items():
        metrics = get_analysis_metrics(code)
        assert_true(metrics["mode"] == KEY_EXPENSE_ANALYZE_MODE, f"{code} key_expenses")
        rows = _key_rows(code)
        assert_true(len(rows) == 2, f"{code} has two key rows")
        got0 = tuple(rows[0].get("lineIds") or [])
        got1 = tuple(rows[1].get("lineIds") or [])
        assert_true(got0 == _as_ids(spec[0]), f"{code} key0 {got0}")
        assert_true(got1 == _as_ids(spec[1]), f"{code} key1 {got1}")

        amounts = {"exp_variable_labor": 40.0, "exp_food_cost": 777.0, "exp_drink_cost": 777.0}
        for lid in _as_ids(spec[0]):
            amounts[lid] = 10.0
        for lid in _as_ids(spec[1]):
            amounts[lid] = 5.0
        snap = summary_from_amounts(code, amounts, 200.0)
        assert_true(snap["key0"] == 10.0 * len(_as_ids(spec[0])), f"{code} key0 sum")
        assert_true(snap["key1"] == 5.0 * len(_as_ids(spec[1])), f"{code} key1 sum")
        assert_true(snap["labor"] == 40.0, f"{code} labor")
        assert_true(snap["key0"] != 777.0, f"{code} ignores restaurant food")
        assert_true(abs(snap["l_rate"] - 0.2) < 1e-9, f"{code} L = labor/sales")
        # Residual is not a displayed row; key+labor must not double-count labor.
        assert_true(snap["key0"] + snap["key1"] != snap["labor"], f"{code} keys are not labor")


def test_clients_and_pages() -> None:
    exp = EXPENSE_CLIENT.read_text(encoding="utf-8")
    diff = DIFF_CLIENT.read_text(encoding="utf-8")
    assert_true("getAnalysisMetrics" in exp, "expense reader uses getAnalysisMetrics")
    assert_true("key0" in exp and "key1" in exp, "key expense totals on snapshot")
    assert_true("misc: Math.max(0, Math.round(variable - food - drink))" in exp, "restaurant Misc residual kept")
    assert_true("UNIT-5C-2-INSIGHT-SUMMARY-BT-BEGIN" in exp, "5C-2 expense marker")
    assert_true("UNIT-5C-2-INSIGHT-SUMMARY-BT-BEGIN" in diff, "5C-2 summary marker")
    assert_true("Number(scope.food) + Number(scope.drink) + Number(scope.labor)" in diff, "FL includes drink")
    assert_true("Number(scope.food) + Number(scope.labor)" not in diff.replace(
        "Number(scope.food) + Number(scope.drink) + Number(scope.labor)", ""
    ), "old Food+Labor FL gone")
    assert_true("patchSummaryCostBlock" in diff, "shared monthly/annual cost patch")
    assert_true("insightSummaryCostRowLabels" in diff, "label adapter present")
    assert_true("function patchSummaryDailyReferenceBlock" in diff, "Daily Summary patch kept")
    assert_true("insight-daily-expenses" in diff, "Daily expenses block kept")
    assert_true("function setGraphDailyAllocWidget" in diff, "Insight Graph daily kept")

    for path in INSIGHT_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-pl-expense-presets.js" in html, f"{rel} loads presets")
        assert_true("UNIT-5C-2-INSIGHT-SUMMARY-BT-BEGIN" in html, f"{rel} has 5C-2 summary adapter")
        assert_true("patchSummaryMonthlyBlocks" in html, f"{rel} monthly summary")
        assert_true("patchSummaryAnnualBlocks" in html, f"{rel} annual summary")
        assert_true("insight-monthly-cost__row" in html, f"{rel} monthly 9-row skeleton")
        assert_true("insight-annual-cost__row" in html, f"{rel} annual 9-row skeleton")
        assert_true(html.count("insight-monthly-cost__row") >= 9, f"{rel} monthly has 9 cost rows")
        assert_true(html.count("insight-annual-cost__row") >= 9, f"{rel} annual has 9 cost rows")
        assert_true("display:none" not in html[html.find("insight-monthly-cost"): html.find("insight-monthly-progress")], f"{rel} no display:none gap in monthly cost")
        assert_true("40px * 9" in html, f"{rel} 9-row vertical label geometry kept")
        assert_true("insight-daily-expenses" in html, f"{rel} Daily expenses markup kept")
        assert_true("function patchSummaryDaily" in html or "patchSummaryDailyReference" in html, f"{rel} Daily patch kept")

    key_branch = diff[diff.find("var k0 = Number(scope.key0)"): diff.find("UNIT-5C-2-INSIGHT-SUMMARY-BT-END")]
    for bad in FORBIDDEN_NON_RESTAURANT:
        assert_true(bad not in key_branch, f"non-restaurant cost branch has no {bad!r}")


def test_pl_insight_and_analyze_untouched() -> None:
    pl_client = (_SCRIPTS / "pl_insight_data_client.py").read_text(encoding="utf-8")
    assert_true("UNIT-5C-1-PL-INSIGHT-BT-BEGIN" in pl_client, "5C-1 PL Insight still present")
    assert_true("UNIT-5C-2" not in pl_client, "5C-2 did not edit PL Insight client")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("UNIT-5C-1-PL-INSIGHT-BT-BEGIN" in html, f"{rel} 5C-1 kept")
        assert_true("UNIT-5C-2-INSIGHT-SUMMARY-BT-BEGIN" not in html, f"{rel} no 5C-2 summary inject")

    analyze = (_SCRIPTS / "pl_analyze_business_type_client.py").read_text(encoding="utf-8")
    assert_true("plAnalyzeReadMetrics" in analyze, "PL Analyze metadata helper unchanged")
    diff = DIFF_CLIENT.read_text(encoding="utf-8")
    assert_true("renderInsightTwDiffs" in diff, "diff client still hosts overlay fill")
    assert_true("insight-pane-analyze" in diff, "Analyze pane path unchanged")
    assert_true("patchAnalyzeAnnualBlocks" in diff, "Analyze annual blocks kept")


def main() -> int:
    test_restaurant_fl_includes_drink()
    test_zero_sales_dash()
    test_non_restaurant_mappings()
    test_clients_and_pages()
    test_pl_insight_and_analyze_untouched()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

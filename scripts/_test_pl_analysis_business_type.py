# -*- coding: utf-8 -*-
"""Unit 5B-3 — PL Analyze Business Type adaptation."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pl_line_catalog import (  # noqa: E402
    ANALYSIS_METRICS_V1,
    CATALOG_SCHEMA_VERSION,
    EXPENSE_DETAIL_LINES_V1,
    KEY_EXPENSE_ANALYZE_MODE,
    LABOR_ANALYSIS_ATTRIBUTES,
    RESTAURANT_ANALYZE_MODE,
    catalog_from_expense_tuples,
    expense_detail_default_catalog,
    get_analysis_metrics,
    get_default_expense_lines,
)

FAILED = 0
PASSED = 0

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]

RESTAURANT_ANALYZE_IDS = (
    "analyze_food_sales",
    "analyze_food_cost",
    "analyze_drink_sales",
    "analyze_drink_cost",
    "analyze_labor_employee",
    "analyze_labor_pt",
    "analyze_labor_total",
    "analyze_monthly_food",
    "analyze_monthly_labor",
    "analyze_fl_total",
)

FORBIDDEN_NON_RESTAURANT_IDS = (
    "analyze_food_sales",
    "analyze_food_cost",
    "analyze_drink_sales",
    "analyze_drink_cost",
    "analyze_monthly_food",
    "analyze_fl_total",
    "food_sales",
    "drink_sales",
    "exp_food_cost",
    "exp_drink_cost",
)

EXPECTED_KEY_LINE_IDS = {
    "retail": (
        ("analyze_inventory_cogs", ("exp_inventory_cogs",)),
        ("analyze_packaging_shipping", ("exp_packaging", "exp_shipping")),
    ),
    "hair_salon": (
        ("analyze_treatment_materials", ("exp_treatment_materials",)),
        ("analyze_retail_product_cogs", ("exp_retail_product_cogs",)),
    ),
    "fitness": (
        ("analyze_facility_fee", ("exp_facility_fee",)),
        (
            "analyze_training_equipment",
            ("exp_training_equipment", "exp_equipment_maintenance"),
        ),
    ),
    "hotel": (
        (
            "analyze_linen_cleaning",
            ("exp_linen_cleaning", "exp_cleaning_supplies", "exp_cleaning_outsource"),
        ),
        ("analyze_ota_fees", ("exp_ota_fees",)),
    ),
    "other": (
        ("analyze_materials", ("exp_materials",)),
        ("analyze_outsourcing", ("exp_outsourcing",)),
    ),
}

EXPECTED_LABELS = {
    "retail": ("商品仕入額", "包装・梱包 / 配送系費用"),
    "hair_salon": ("薬剤・施術材料費", "店販商品仕入"),
    "fitness": ("ジム・施設利用料", "トレーニング機器 / メンテナンス関連"),
    "hotel": ("リネン / 清掃関連費", "OTA・予約手数料"),
    "other": ("材料・仕入費", "外注費"),
}


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
    else:
        FAILED += 1
        print("FAIL:", msg)


def _metric_rows(code: str) -> list[dict]:
    rows: list[dict] = []
    for group in get_analysis_metrics(code).get("groups") or []:
        rows.extend(group.get("rows") or [])
    return rows


def _key_rows(code: str) -> list[dict]:
    return [row for row in _metric_rows(code) if row.get("source") != "labor"]


def test_restaurant_analysis_unchanged() -> None:
    metrics = get_analysis_metrics("restaurant")
    assert_true(metrics["mode"] == RESTAURANT_ANALYZE_MODE, "Restaurant mode is restaurant_fl")
    assert_true(metrics.get("groups") == [], "Restaurant analysis has no replacement groups")
    cafe = get_analysis_metrics("cafe")
    assert_true(cafe["mode"] == RESTAURANT_ANALYZE_MODE, "cafe legacy still restaurant analysis")

    analyze_client = (_SCRIPTS / "pl_analyze_client.py").read_text(encoding="utf-8")
    assert_true("analyze_food_sales" in analyze_client, "Restaurant fill still maps Food sales")
    assert_true("analyze_fl_total" in analyze_client, "Restaurant fill still maps FL total")
    assert_true("KpiPlExpensePresets" not in analyze_client, "5B-1: presets stay out of analyze client")

    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for rid in RESTAURANT_ANALYZE_IDS:
            assert_true(f'data-row="{rid}"' in html, f"{rel} still has restaurant row {rid}")
        assert_true("plAnalyzeFillFlRatio" in html, f"{rel} still has restaurant FL fill")


def test_non_restaurant_hides_food_drink_fl() -> None:
    for code in EXPECTED_KEY_LINE_IDS:
        metrics = get_analysis_metrics(code)
        blob = str(metrics)
        assert_true(metrics["mode"] == KEY_EXPENSE_ANALYZE_MODE, f"{code} uses key_expenses mode")
        for forbidden in FORBIDDEN_NON_RESTAURANT_IDS:
            assert_true(forbidden not in blob, f"{code} analysis has no {forbidden}")
        labels = [row["labelJa"] for row in _metric_rows(code)]
        assert_true("フード売上" not in labels, f"{code} has no Food売上")
        assert_true("F率" not in labels, f"{code} has no F率")
        assert_true("FL率" not in labels, f"{code} has no FL率")


def test_key_line_ids_from_preset() -> None:
    for code, expected in EXPECTED_KEY_LINE_IDS.items():
        preset_ids = {row[0] for row in get_default_expense_lines(code)}
        key_rows = _key_rows(code)
        assert_true(len(key_rows) == len(expected), f"{code} has {len(expected)} key analysis rows")
        for row, (rid, line_ids) in zip(key_rows, expected):
            assert_true(row["id"] == rid, f"{code} row id {rid}")
            assert_true(tuple(row.get("lineIds") or ()) == line_ids, f"{code} {rid} lineIds")
            for lid in line_ids:
                assert_true(lid in preset_ids, f"{code} {lid} exists in 5B-2 preset")
        labels = tuple(row["labelJa"] for row in key_rows)
        assert_true(labels == EXPECTED_LABELS[code], f"{code} JP analysis labels")
        for row in key_rows:
            assert_true(row.get("labelEn"), f"{code} {row['id']} has EN label")
            assert_true(row.get("labelZh"), f"{code} {row['id']} has ZH label")


def test_labor_and_l_rate() -> None:
    assert_true(
        LABOR_ANALYSIS_ATTRIBUTES == ("salaries_wages", "variable_labor", "labor_related"),
        "labor attrs are preset labor attributes",
    )
    for code in EXPECTED_KEY_LINE_IDS:
        rows = _metric_rows(code)
        labor = [row for row in rows if row["id"] == "analyze_monthly_labor"]
        lrate = [row for row in rows if row["id"] == "analyze_l_rate"]
        assert_true(len(labor) == 1 and labor[0]["source"] == "labor", f"{code} monthly labor from labor attrs")
        assert_true(len(lrate) == 1 and lrate[0]["source"] == "labor", f"{code} L rate from labor attrs")
        assert_true(lrate[0].get("isTotal") is True, f"{code} L rate is the total row")
        assert_true(labor[0]["labelJa"] == "月次人件費", f"{code} 月次人件費 label")
        assert_true(lrate[0]["labelJa"] == "L率", f"{code} L率 label")
        labor_ids = {row[0] for row in get_default_expense_lines(code) if row[6] in LABOR_ANALYSIS_ATTRIBUTES}
        assert_true("exp_variable_labor" in labor_ids, f"{code} staff labor is a labor analysis source")


def test_preset_driven_client() -> None:
    client = (_SCRIPTS / "pl_analyze_business_type_client.py").read_text(encoding="utf-8")
    assert_true("getAnalysisMetrics" in client, "adapter reads analysis metadata")
    assert_true("innerHTML" in client, "adapter rebuilds analyze tbodies (no hidden gaps)")
    assert_true("display:none" not in client, "adapter does not hide leftover restaurant rows")
    assert_true("refreshPlRatios" in client, "ratios still divide by sales_total")
    assert_true("!(sales.value > 0)" not in client, "0-sales rule stays in existing ratio client")
    for needle in (
        "商品仕入",
        "フード売上",
        "hair_salon",
        "exp_inventory_cogs",
        "exp_treatment_materials",
        "exp_facility_fee",
        "exp_ota_fees",
        "exp_materials",
    ):
        assert_true(needle not in client, f"adapter does not hardcode {needle}")

    ratio_client = (_SCRIPTS / "pl_ratio_client.py").read_text(encoding="utf-8")
    assert_true("sales_total" in ratio_client, "ratio denominator is monthly total sales")
    assert_true("!(sales.value > 0)" in ratio_client, "0 sales yields em dash, not NaN")


def test_pages_and_runtime() -> None:
    js = (ROOT / "js" / "kpi-pl-expense-presets.js").read_text(encoding="utf-8")
    assert_true("getAnalysisMetrics" in js, "runtime exports getAnalysisMetrics")
    assert_true('"mode": "restaurant_fl"' in js, "runtime keeps restaurant_fl")
    assert_true('"mode": "key_expenses"' in js, "runtime has key_expenses")
    assert_true("analyze_inventory_cogs" in js, "runtime has retail analysis ids")
    assert_true("analyze_l_rate" in js, "runtime has L rate row")

    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("UNIT-5B-3-ANALYZE-BT-BEGIN" in html, f"{rel} has analyze BT adapter")
        assert_true("plAnalyzeRenderKeyLayout" in html, f"{rel} rebuilds non-restaurant analyze")
        assert_true("pl-v-major--r2" in html, f"{rel} has 2-row analyze height")
        assert_true("restaurantRefresh()" in html, f"{rel} restaurant path calls original fill")

    generator = (_SCRIPTS / "build_pl_table_page.py").read_text(encoding="utf-8")
    assert_true("pl_analyze_business_type_client_js" in generator, "PL generator includes adapter")
    assert_true("pl_analyze_business_type_css" in generator, "PL generator includes r2 CSS")


def test_presets_not_destroyed() -> None:
    assert_true(CATALOG_SCHEMA_VERSION == 8, "schema version unchanged")
    frozen = list(EXPENSE_DETAIL_LINES_V1)
    got = get_default_expense_lines("restaurant")
    assert_true(got == frozen, "restaurant expense tuples unchanged")
    assert_true(
        expense_detail_default_catalog() == catalog_from_expense_tuples(frozen),
        "restaurant catalog dicts unchanged",
    )
    retail = get_default_expense_lines("retail")
    assert_true(retail[5][0] == "exp_inventory_cogs", "retail preset still has merchandise purchases")
    assert_true("exp_food_cost" not in {row[0] for row in retail}, "retail preset still has no food cost")


def test_no_new_revenue_split() -> None:
    for code in EXPECTED_KEY_LINE_IDS:
        blob = str(get_analysis_metrics(code))
        assert_true("商品売上" not in blob, f"{code} does not invent 商品売上")
        assert_true("施術売上" not in blob, f"{code} does not invent 施術売上")
        assert_true("food_sales" not in blob, f"{code} does not invent food_sales split")


def test_client_js_is_valid() -> None:
    src = (_SCRIPTS / "pl_analyze_business_type_client.py").read_text(encoding="utf-8")
    ast.parse(src)
    from pl_analyze_business_type_client import pl_analyze_business_type_client_js

    js = pl_analyze_business_type_client_js()
    assert_true("function plAnalyzeRenderKeyLayout" in js, "adapter JS emits renderer")
    assert_true("{{" not in js, "f-string braces fully expanded")
    assert_true("getAnalysisMetrics" in js, "adapter JS reads metadata")


def main() -> int:
    test_restaurant_analysis_unchanged()
    test_non_restaurant_hides_food_drink_fl()
    test_key_line_ids_from_preset()
    test_labor_and_l_rate()
    test_preset_driven_client()
    test_pages_and_runtime()
    test_presets_not_destroyed()
    test_no_new_revenue_split()
    test_client_js_is_valid()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

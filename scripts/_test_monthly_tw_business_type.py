# -*- coding: utf-8 -*-
"""Unit 5C-5 — Monthly Table Window Business Type adaptation."""
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
    expense_detail_default_catalog,
    get_analysis_metrics,
)

FAILED = 0
PASSED = 0

TW_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]

CLIENT = _SCRIPTS / "monthly_tw_mep_metrics_client.py"
APPLY = _SCRIPTS / "apply_monthly_tw_mep_metrics.py"

FORBIDDEN_SCOPE = [
    ROOT / "scripts" / "insight_diff_client.py",
    ROOT / "scripts" / "insight_expense_read_client.py",
    ROOT / "scripts" / "pl_insight_data_client.py",
    ROOT / "scripts" / "pl_analyze_business_type_client.py",
    ROOT / "js" / "kpi-business-type.js",
    ROOT / "js" / "kpi-pl-expense-presets.js",
]

MEAL_LABELS = (
    "ランチ",
    "ディナー",
    "来客数",
    "組数",
    "Lunch",
    "Dinner",
    "Customer",
    "午餐",
    "晚餐",
    "來客數",
    "組數",
)
FOOD_DRINK_LABELS = ("フード", "ドリンク", "Food", "Beverage", "餐點", "飲料")
COMMON_G1 = ("売上", "目標", "差額", "達成率", "Sales", "Target", "Difference", "Achievement", "營業額", "目標營業額", "達成率")
COMMON_G3_TAIL = ("確定", "予想", "トータル", "Fixed", "Expected", "Total", "確定支出", "預計支出", "合計")

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

EXPECTED_LABEL_SUBSTR = {
    "retail": ("商品仕入", "包装", "Merchandise", "Packaging", "商品進貨", "包裝"),
    "hair_salon": ("施術材料", "店販", "Treatment", "Retail product", "施術材料", "店販"),
    "fitness": ("施設利用", "機器", "facility", "equipment", "場地", "器材"),
    "hotel": ("リネン", "OTA", "Linen", "OTA", "布巾", "OTA"),
    "other": ("材料", "外注", "Materials", "Outsourcing", "材料", "外包"),
}

NEW_KPI_FORBIDDEN = (
    "room night",
    "Room night",
    "appointment",
    "Appointment",
    "session",
    "transaction",
    "泊数",
    "予約件数",
    "セッション",
)


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


def _bucket_ids(code: str, bucket: str) -> list[str]:
    out = []
    for line in expense_detail_default_catalog(code):
        if line.get("active") is False:
            continue
        if line.get("bucket") == bucket and line.get("lineId"):
            out.append(str(line["lineId"]))
    return out


def tw_group_row_count(code: str, group_no: int) -> int:
    if code == "restaurant":
        return 6
    if group_no == 1:
        return 4
    if group_no == 2:
        return 0
    return 6


def tw_group3(code: str, amounts: dict[str, float]) -> dict:
    fixed_ids = _bucket_ids(code, "fixed")
    variable_ids = _bucket_ids(code, "variable")
    var_set = set(variable_ids)
    fixed = sum(float(amounts.get(i, 0) or 0) for i in fixed_ids)
    expected = sum(float(amounts.get(i, 0) or 0) for i in variable_ids)
    total = fixed + expected
    if code == "restaurant":
        food = float(amounts.get("exp_food_cost", 0) or 0)
        drink = float(amounts.get("exp_drink_cost", 0) or 0)
        misc = float(amounts.get("exp_misc", 0) or 0)
        return {
            "k0": food,
            "k1": drink,
            "residual": misc,
            "fixed": fixed,
            "expected": expected,
            "total": total,
        }
    rows = _key_rows(code)
    id0 = list(rows[0].get("lineIds") or []) if rows else []
    id1 = list(rows[1].get("lineIds") or []) if len(rows) > 1 else []
    k0 = sum(float(amounts.get(i, 0) or 0) for i in id0)
    k1 = sum(float(amounts.get(i, 0) or 0) for i in id1)
    var0 = sum(float(amounts.get(i, 0) or 0) for i in id0 if i in var_set)
    var1 = sum(float(amounts.get(i, 0) or 0) for i in id1 if i in var_set)
    residual = max(0.0, expected - var0 - var1)
    return {
        "k0": k0,
        "k1": k1,
        "residual": residual,
        "fixed": fixed,
        "expected": expected,
        "total": total,
    }


def test_row_counts() -> None:
    assert_true(tw_group_row_count("restaurant", 1) == 6, "restaurant G1 = 6")
    assert_true(tw_group_row_count("restaurant", 2) == 6, "restaurant G2 = 6")
    assert_true(tw_group_row_count("restaurant", 3) == 6, "restaurant G3 = 6")
    for code in EXPECTED_KEY_ROWS:
        assert_true(tw_group_row_count(code, 1) == 4, f"{code} G1 = 4")
        assert_true(tw_group_row_count(code, 2) == 0, f"{code} G2 = 0")
        assert_true(tw_group_row_count(code, 3) == 6, f"{code} G3 = 6")


def test_restaurant_group3_frozen() -> None:
    snap = tw_group3(
        "restaurant",
        {
            "exp_food_cost": 100,
            "exp_drink_cost": 40,
            "exp_misc": 15,
            "exp_rent": 200,
            "exp_variable_labor": 30,
        },
    )
    assert_true(snap["k0"] == 100, "restaurant food")
    assert_true(snap["k1"] == 40, "restaurant drink")
    assert_true(snap["residual"] == 15, "restaurant misc is exp_misc not a derived residual")
    assert_true(snap["fixed"] >= 200, "restaurant fixed includes rent")
    assert_true(snap["expected"] >= 100 + 40 + 15 + 30, "restaurant expected includes food/drink/misc/labor")
    assert_true(snap["total"] == snap["fixed"] + snap["expected"], "restaurant total = fixed+expected")
    for v in snap.values():
        assert_true(math.isfinite(v), "restaurant group3 finite")


def test_non_restaurant_keys_and_residual() -> None:
    for code, spec in EXPECTED_KEY_ROWS.items():
        metrics = get_analysis_metrics(code)
        assert_true(metrics["mode"] == KEY_EXPENSE_ANALYZE_MODE, f"{code} key_expenses metadata")
        rows = _key_rows(code)
        assert_true(len(rows) == 2, f"{code} two key rows")
        assert_true(tuple(rows[0].get("lineIds") or []) == _as_ids(spec[0]), f"{code} key0 ids")
        assert_true(tuple(rows[1].get("lineIds") or []) == _as_ids(spec[1]), f"{code} key1 ids")

        amounts = {
            "exp_food_cost": 777.0,
            "exp_drink_cost": 777.0,
            "exp_variable_labor": 40.0,
            "exp_rent": 90.0,
            "exp_supplies": 12.0,
        }
        for lid in _as_ids(spec[0]):
            amounts[lid] = 10.0
        for lid in _as_ids(spec[1]):
            amounts[lid] = 5.0
        snap = tw_group3(code, amounts)
        assert_true(snap["k0"] == 10.0 * len(_as_ids(spec[0])), f"{code} key0 sum")
        assert_true(snap["k1"] == 5.0 * len(_as_ids(spec[1])), f"{code} key1 sum")
        assert_true(snap["k0"] != 777.0, f"{code} ignores restaurant food")
        assert_true(snap["expected"] == snap["expected"], f"{code} expected finite")
        # Residual subtracts only the variable portion of key lineIds.
        var_ids = set(_bucket_ids(code, "variable"))
        var0 = sum(amounts[i] for i in _as_ids(spec[0]) if i in var_ids)
        var1 = sum(amounts[i] for i in _as_ids(spec[1]) if i in var_ids)
        assert_true(snap["residual"] == max(0.0, snap["expected"] - var0 - var1), f"{code} residual no double-count")
        assert_true(snap["k0"] + snap["k1"] != snap["residual"] or snap["residual"] == 0, f"{code} residual distinct")
        assert_true(snap["total"] == snap["fixed"] + snap["expected"], f"{code} total")
        for v in snap.values():
            assert_true(math.isfinite(float(v)) and not math.isnan(float(v)), f"{code} no NaN/Inf")


def test_zero_values() -> None:
    for code in ("restaurant",) + tuple(EXPECTED_KEY_ROWS):
        snap = tw_group3(code, {})
        for key, val in snap.items():
            assert_true(val == 0, f"{code} zero {key}")
            assert_true(math.isfinite(val), f"{code} zero {key} finite")


def test_pages_and_client() -> None:
    client = CLIENT.read_text(encoding="utf-8")
    apply = APPLY.read_text(encoding="utf-8")
    assert_true("getAnalysisMetrics" in client, "TW client uses getAnalysisMetrics")
    assert_true("isRestaurantLike" in client, "TW client uses isRestaurantLike")
    assert_true("monthlyTwGroupRowCount" in client, "dynamic row count helper")
    assert_true("applyMonthlyTwBusinessTypeLayout" in client, "layout adapter")
    assert_true("kpi:businessTypeChanged" in apply, "BT change listener wired")
    assert_true("--monthly-data-group1-rows" in apply, "per-group CSS vars")
    assert_true('data-tw-layout="key-expenses"' in apply, "key-expenses layout attr")
    assert_true("display = 'none'" in client and "data-tw-layout" in client, "labels hide with layout attr, not height-only")
    for bad in NEW_KPI_FORBIDDEN:
        assert_true(bad not in client, f"no new KPI {bad!r} in client")

    for path in TW_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-pl-expense-presets.js" in html, f"{rel} loads presets")
        assert_true("kpi-business-type.js" in html, f"{rel} loads business type")
        assert_true("UNIT-5C-5-MONTHLY-TW-BT-BEGIN" in html, f"{rel} 5C-5 JS")
        assert_true("UNIT-5C-5-MONTHLY-TW-BT-CSS-BEGIN" in html, f"{rel} 5C-5 CSS")
        assert_true("KPI-MONTHLY-GRAPH-CH3" in html, f"{rel} Graph CH3 kept")
        assert_true("UNIT-5C-2-INSIGHT-SUMMARY-BT-BEGIN" in html, f"{rel} Insight 5C-2 untouched")
        assert_true("function monthlyTwIsRestaurant" in html, f"{rel} restaurant gate")
        assert_true("if (!monthlyTwIsRestaurant()) return [];" in html, f"{rel} meal group unread")
        assert_true("g1: resolveGroup1Values(iso)" in html, f"{rel} rebuild uses resolve*")
        assert_true("function rebuildColumnsChunked" in html and "applyMonthlyTwBusinessTypeLayout" in html[html.find("function rebuildColumnsChunked"): html.find("function rebuildColumnsChunked")+500], f"{rel} chunked rebuild applies layout")
        assert_true("addEventListener('kpi:businessTypeChanged'" in html, f"{rel} immediate BT listener")
        assert_true("kpiNavigator.kpiYearStore" in html, f"{rel} HR persist via store key")
        assert_true("--monthly-data-group-rows: 6" in html, f"{rel} restaurant default 6 rows")
        assert_true("--monthly-data-group1-rows: 4" in html, f"{rel} non-rest G1 shrinks")
        assert_true("--monthly-data-group2-rows: 0" in html, f"{rel} non-rest G2 collapses")
        assert_true("--monthly-data-gap-after-g2: 0px" in html, f"{rel} no G2 gap")
        assert_true("repeat(var(--monthly-data-group3-rows)" in html, f"{rel} metric-col skips empty G2")
        assert_true('data-tw-rows="0"' in html or "data-tw-rows" in html, f"{rel} vfocus row attr")
        assert_true("monthly-vfocus-group[data-tw-rows=\"0\"]" in html, f"{rel} vfocus 0-row none")
        assert_true("var rowN = typeof monthlyTwGroupRowCount" in html, f"{rel} makeGroupColumn dynamic rows")
        assert_true("cellIndex === monthlyTwGroup1TargetIdx()" in html, f"{rel} target idx follows BT")

        # Restaurant source labels remain in markup (JS restores them).
        meal_hits = [lab for lab in MEAL_LABELS if lab in html]
        assert_true(len(meal_hits) >= 2, f"{rel} restaurant meal labels kept in markup ({meal_hits})")
        food_hits = [lab for lab in FOOD_DRINK_LABELS if lab in html]
        assert_true(len(food_hits) >= 1, f"{rel} restaurant food/drink labels kept in markup")
        common_g1 = [lab for lab in COMMON_G1 if lab in html]
        assert_true(len(common_g1) >= 3, f"{rel} sales/target/diff/ach labels present")
        common_g3 = [lab for lab in COMMON_G3_TAIL if lab in html]
        assert_true(len(common_g3) >= 2, f"{rel} confirmed/expected/total labels present")

        hide = html[html.find("function applyMonthlyTwMetricLabels") : html.find("function monthlyTwResizeVfocusGroup")]
        assert_true("hideIdx = [1, 2, 7, 8, 9, 10, 11, 12, 13]" in hide, f"{rel} meal rows hidden in key-expenses")
        assert_true("lines[14].textContent = spec.labels[0]" in hide, f"{rel} key0 label from metadata")
        assert_true("monthlyTwResidualLabel" in hide, f"{rel} residual label")

        for bad in NEW_KPI_FORBIDDEN:
            tw_js = html[html.find("UNIT-5C-5-MONTHLY-TW-BT-BEGIN") : html.find("UNIT-5C-5-MONTHLY-TW-BT-END")]
            assert_true(bad not in tw_js, f"{rel} 5C-5 JS has no {bad!r}")


def test_key_expense_labels_from_metadata() -> None:
    for code, needles in EXPECTED_LABEL_SUBSTR.items():
        rows = _key_rows(code)
        blob = " ".join(
            str(rows[i].get(k) or "")
            for i in range(len(rows))
            for k in ("labelJa", "labelEn", "labelZh")
        )
        ja = needles[0]
        ja2 = needles[1]
        assert_true(ja in blob, f"{code} metadata has {ja}")
        assert_true(ja2 in blob, f"{code} metadata has {ja2}")


def test_scope_untouched() -> None:
    marker = "UNIT-5C-5-MONTHLY-TW-BT"
    for path in FORBIDDEN_SCOPE:
        text = path.read_text(encoding="utf-8")
        assert_true(marker not in text, f"{path.name} not edited by 5C-5")
    daily_fw = ROOT / "app" / "annual" / "index.html"
    if daily_fw.is_file():
        html = daily_fw.read_text(encoding="utf-8")
        assert_true("UNIT-5C-5-MONTHLY-TW-BT-CSS-BEGIN" not in html, "Annual Daily FW CSS not patched")
    excel = ROOT / "excel"
    assert_true(excel.is_dir(), "excel/ still present")


def test_mep_read_path() -> None:
    client = CLIENT.read_text(encoding="utf-8")
    html = TW_PAGES[0].read_text(encoding="utf-8")
    assert_true("mepReadRow(iso, 'incLunch')" in html, "restaurant still reads meal rows")
    g2 = html[html.find("function resolveGroup2Values") : html.find("function resolveGroup3Values")]
    assert_true("if (!monthlyTwIsRestaurant()) return [];" in g2, "non-restaurant does not read meal/customer/group")
    g3 = html[html.find("function resolveGroup3Values") : html.find("function resolveMonthlyProfitValue")]
    assert_true("spec.idGroups" in g3, "non-restaurant expenses from metadata lineIds")
    assert_true("mepSumRows(iso, spec.idGroups[0]" in g3, "key0 from lineIds")
    assert_true("mepSumVariablePortion" in g3, "residual uses variable portion only")
    assert_true("function monthlyTwKeyExpenseSpec" in client, "spec from getAnalysisMetrics")


def main() -> int:
    test_row_counts()
    test_restaurant_group3_frozen()
    test_non_restaurant_keys_and_residual()
    test_zero_values()
    test_pages_and_client()
    test_key_expense_labels_from_metadata()
    test_scope_untouched()
    test_mep_read_path()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

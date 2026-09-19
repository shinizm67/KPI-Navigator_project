# -*- coding: utf-8 -*-
"""PL Insight functional wiring — real-data path (not top-nav Insight)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]
CLIENT = ROOT / "scripts/pl_insight_data_client.py"
BUILDER = ROOT / "scripts/build_pl_table_page.py"
ANALYZE_BT = ROOT / "scripts/pl_analyze_business_type_client.py"


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def main() -> int:
    client = CLIENT.read_text(encoding="utf-8")
    builder = BUILDER.read_text(encoding="utf-8")
    analyze = ANALYZE_BT.read_text(encoding="utf-8")

    # --- store sources (same as PL table) ---
    check("kpiNavigator.kpiYearStore" in client, "year store key")
    check("kpiNavigator.plLineCatalog" in client, "catalog key")
    check("kpi-pl-expenses-v1:" in client, "monthly expense prefix")
    check("kpi-pl-expense-adjustments-v1:" in client, "adjustment prefix")
    check("dailyExpenses" in client, "daily expense path")
    check("dailySales" in client, "daily sales path")
    check("PLACEHOLDER = 1234" in client and "v === PLACEHOLDER" in client, "placeholder sales excluded")
    check("__plPreviewMonthlyExpenseAllocation" in client, "shared monthly alloc engine")

    # --- public API ---
    for name in (
        "buildArea1",
        "buildArea2",
        "buildArea3",
        "flDay",
        "flYtd",
        "monthMetrics",
        "dayMetrics",
        "lineBreakdown",
        "resetCache",
        "snapshotCopy",
        "canShowBestYear",
    ):
        check(name in client, f"__plInsight exposes {name}")

    # --- overlay delegates to real provider (not stub FL) ---
    check("window.__plInsight.buildArea1" in builder, "Area1 chart → __plInsight")
    check("window.__plInsight.buildArea2" in builder, "Area2 chart → __plInsight")
    check("window.__plInsight.buildArea3" in builder, "Area3 chart → __plInsight")
    check("ins.flDay" in builder or "ins.flDay" in builder.replace(" ", ""), "FL render uses flDay")
    # generated pages use the same pattern
    jp = (ROOT / "app/profit/pl/index.html").read_text(encoding="utf-8")
    check("var flDay = (ins && typeof ins.flDay === 'function')" in jp, "runtime FL uses __plInsight.flDay")
    check("window.__plInsight.buildArea1" in jp, "runtime Area1 wired")
    check("plGraphMonthsFromInsight" in jp, "PL bottom graph months from __plInsight")

    # dead stubs must not be the live FL path
    check("function fetchCurrentFlSnapshot" in builder, "legacy stub still present")
    # ensure stub is never called (definition only)
    stub_calls = builder.count("fetchCurrentFlSnapshot(")
    check(stub_calls == 1, "fetchCurrentFlSnapshot defined once, never called")
    stub_calls2 = builder.count("fetchPreviousFlSnapshot(")
    check(stub_calls2 == 1, "fetchPreviousFlSnapshot defined once, never called")

    # --- date / month / year propagation ---
    check("selectedIso" in builder, "overlay selectedIso")
    check("fillDate" in builder or "function fillDate" in jp, "date fill")
    check("kpiNavigator.plInsightLast" in builder or "plInsightLast" in jp, "last state isolation key")
    check("flBtCacheKey" in client, "BT included in FL cache key")
    check("resetCache" in client and "flYtdCache = {}" in client, "cache clear on refresh")

    # --- Business Type ---
    check("getAnalysisMetrics" in client, "BT metrics for FL classify")
    check("plInsightClassifyLine" in client, "line classify by BT")
    check("getAnalysisMetrics" in analyze, "Analyze BT metrics")
    check("plAnalyzeIsRestaurant" in analyze, "Analyze restaurant gate")

    # --- custom / preset ---
    check("active !== false" in client, "custom active lines in catalog")
    check("function lineBreakdown" in client, "breakdown includes catalog lines with amount")
    check("KpiPlExpensePresets" in client, "preset helper")

    # --- Pro / Basic gate (existing lock UX, not hard-close of shell) ---
    check("isBasicTier" in builder or "isBasicTier" in jp, "Basic tier helper")
    check("applyPlComparePlanLocks" in jp, "plan locks applied")
    check("pl-compare-plan-lock" in jp, "Pro lock CTA markup")
    check("PL_COMPARE_LOCK_SELECTORS" in jp, "locked areas defined")
    check("kpi:planChanged" in jp, "locks refresh on plan change")
    # Basic can open shell; content locked — document existing contract
    check("function openOverlay" in jp, "openOverlay exists")
    check("isBasicTier()" not in jp.split("function openOverlay")[1][:400], "openOverlay not hard-blocked (locks instead)")

    # --- live refresh hooks ---
    check("kpi:mepDataChanged" in jp or "kpi:dailySalesChanged" in jp or "kpi:readSurfacesRefresh" in jp, "live refresh events")
    check("__plInsight.resetCache" in jp, "persist resets insight cache")

    # --- pages parity ---
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check("window.__plInsight" in html, f"{rel} has __plInsight")
        check("id=\"pl-graph-open\"" in html or "id='pl-graph-open'" in html, f"{rel} entry button")
        check("id=\"pl-graph-overlay\"" in html, f"{rel} overlay")
        check("UNIT-5C-1-PL-INSIGHT-BT-BEGIN" in html, f"{rel} 5C-1")
        check("kpi-pl-expense-presets.js" in html, f"{rel} presets")
        check("kpi-auth-client.js" in html, f"{rel} auth client")

    # DUMMY_MONTHS is PL-table graph no-data zero fill, not Insight overlay series
    check("var DUMMY_MONTHS" in jp, "DUMMY_MONTHS exists for table graph fallback")
    check("useDummy ? DUMMY_MONTHS" in jp, "dummy only when monthData null")
    check("plGraphMonthsFromInsight" in jp, "preferred path is insight metrics")

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

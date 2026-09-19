# -*- coding: utf-8 -*-
"""Top-level Insight (#insight-overlay) functional wiring contract.

PL Insight / PL分析 overlay is out of scope (separate tests).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

HOST_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]
AUTH = ROOT / "js/kpi-auth-client.js"
DIFF = ROOT / "scripts/insight_diff_client.py"
EXPENSE = ROOT / "scripts/insight_expense_read_client.py"
TREND_M = ROOT / "scripts/insight_trend_monthly_client.py"
TREND_A1 = ROOT / "scripts/insight_trend_annual_graph1_client.py"


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def main() -> int:
    auth = AUTH.read_text(encoding="utf-8")
    diff = DIFF.read_text(encoding="utf-8")
    expense = EXPENSE.read_text(encoding="utf-8")
    trend_m = TREND_M.read_text(encoding="utf-8")
    trend_a1 = TREND_A1.read_text(encoding="utf-8")

    # --- entry / Basic-Pro gate ---
    check("function bindInsightMenuGate" in auth, "auth Insight menu gate")
    check("function openInsightFloatingWindow" in auth, "auth opens Insight FW")
    check("isBasicPlan()" in auth and "resolveChangePlanHref" in auth, "Basic → Change Plan")
    check("openInsight()" in auth, "Pro calls openInsight")
    check("open=insight" in auth, "deep-link open=insight for non-overlay pages")

    # --- Summary fill sources ---
    check("window.renderInsightTwDiffs" in diff, "Summary/Analyze orchestrator")
    check("__computeTwMetricsForIso" in diff, "TW metrics source")
    check("__insightReadExpenseSnapshot" in diff, "expense snapshot wired")
    check("patchDailyKpiBlock" in diff, "daily KPI patch")
    check("patchSummaryMonthlyBlocks" in diff, "monthly summary patch")
    check("patchSummaryAnnualBlocks" in diff, "annual summary patch")
    check("patchSummaryCostBlock" in diff, "cost block patch")
    check("insightSummaryIsRestaurantFl" in diff, "Summary BT restaurant gate")
    check("UNIT-5C-2-INSIGHT-SUMMARY-BT" in diff, "Summary BT unit marker")
    check("patchSummaryComparisonBlocks" in diff, "prior-year comparison")
    check("patchSummaryMonthlyProgressBlock" in diff, "required sales / remaining BD")
    check("fmtInsightAchPct" in diff or "Math.round((actual / target) * 100)" in diff, "ach rounding")
    check("fmtInsightProfitMarginPct" in diff, "profit rate formatter")
    check("patchSummaryDailyReferenceBlock" in diff, "daily historical reference")

    # --- expense read ---
    check("window.__insightReadExpenseSnapshot" in expense, "expense snapshot export")
    check("fixed" in expense and "variable" in expense and "food" in expense, "expense scopes")
    check("key0" in expense and "key1" in expense, "non-restaurant key expenses")

    # --- Graph: store first, demo fallback only ---
    check("buildStorePayload" in trend_m, "monthly trend store payload")
    check("__buildMonthlyCumulativeTrendPayload" in trend_m, "monthly trend real builder")
    check("return buildDemoPayload(dim)" in trend_m, "demo is fallback only")
    check("buildStorePayload" in trend_a1, "annual graph1 store payload")
    check("__buildAnnualCumulativeTrendPayload" in trend_a1, "annual graph1 real builder")

    # --- numerical contracts (known Pro trial case) ---
    sales, target = 151960, 40059
    check(sales - target == 111901, "daily diff 111901")
    check(round(sales / target * 100) == 379, "daily ach 379%")
    mtd_s, prior_mtd = 963750, 770550
    check(mtd_s - prior_mtd == 193200, "monthly prior-year diff +193200")
    mtd_exp, mtd_fixed, mtd_var = 671788, 129996, 541792
    check(mtd_fixed + mtd_var == mtd_exp, "mtd fixed+var=total")
    ytd_s, ytd_exp, ytd_profit = 21817220, 15988148, 5829072
    check(ytd_s - ytd_exp == ytd_profit, "ytd profit source truth")
    check(round((mtd_s - mtd_exp) / mtd_s * 100) == 30, "mtd profit rate 30%")
    check(round(mtd_exp / mtd_s * 100) == 70, "mtd cost rate 70%")

    # --- hosts ---
    for path in HOST_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check('id="insight-overlay"' in html, f"{rel} insight-overlay root")
        check('id="global-nav-index-btn"' in html, f"{rel} Insight nav entry")
        check('data-href-basic=' in html and "change_plan.html" in html, f"{rel} Basic Change Plan href")
        check("window.renderInsightTwDiffs" in html, f"{rel} renderInsightTwDiffs")
        check("__insightReadExpenseSnapshot" in html, f"{rel} expense snapshot")
        check('id="insight-tab-summary"' in html, f"{rel} Summary tab")
        check('id="insight-tab-analyze"' in html, f"{rel} Analyze tab")
        check('id="insight-tab-graph"' in html, f"{rel} Graph tab")
        check('id="insight-pane-summary"' in html, f"{rel} Summary pane")
        check('id="insight-pane-analyze"' in html, f"{rel} Analyze pane")
        check('id="insight-pane-graph"' in html, f"{rel} Graph pane")
        check("__INSIGHT_SELECTED_ISO" in html, f"{rel} selected ISO")
        check("insight-overlay-prev-day" in html and "insight-overlay-next-day" in html, f"{rel} date nav")
        check('id="insight-overlay-today"' in html, f"{rel} today button")
        check("patchSummaryCostBlock" in html or "insightSummaryIsRestaurantFl" in html, f"{rel} Summary BT")
        check("buildStorePayload" in html, f"{rel} graph store payload")
        check("__buildMonthlyCumulativeTrendPayload" in html, f"{rel} monthly trend builder")
        check("__buildAnnualCumulativeTrendPayload" in html, f"{rel} annual trend builder")
        open_idx = html.find("window.__KPI_MONTHLY_OVERLAYS__.openInsight")
        check(open_idx >= 0, f"{rel} openInsight export")
        # language pages share same wiring markers
        check("renderInsightTwDiffs" in html and "__computeTwMetricsForIso" in html, f"{rel} same compute path")

        if "/monthly/" in rel:
            check("open === 'insight'" in html or "open=insight" in html, f"{rel} ?open=insight deep link")
        else:
            check("open === 'insight'" not in html, f"{rel} annual has no invent deep-link")

        # auth client on hosts
        check("kpi-auth-client.js" in html, f"{rel} auth client")

    # --- no Planning Readiness invent in Insight runtime ---
    check("Planning Readiness" not in diff and "KPI Setup Status" not in diff, "no Planning Readiness invent in diff client")

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

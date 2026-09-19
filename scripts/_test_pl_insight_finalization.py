# -*- coding: utf-8 -*-
"""Unit 5C finalization audit — blank gap / BT label / custom line contracts."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


PAGES = [
    "app/monthly/index.html",
    "en/app/monthly/index.html",
    "zh-tw/app/monthly/index.html",
    "app/annual/index.html",
    "en/app/annual/index.html",
    "zh-tw/app/annual/index.html",
]
PL_PAGES = [
    "app/profit/pl/index.html",
    "en/app/profit/pl/index.html",
    "zh-tw/app/profit/pl/index.html",
]


def main() -> int:
    diff = (ROOT / "scripts/insight_diff_client.py").read_text(encoding="utf-8")
    exp = (ROOT / "scripts/insight_expense_read_client.py").read_text(encoding="utf-8")
    plic = (ROOT / "scripts/pl_insight_data_client.py").read_text(encoding="utf-8")
    analyze = (ROOT / "scripts/pl_analyze_business_type_client.py").read_text(encoding="utf-8")

    check("patchSummaryCostBlock" in diff, "summary cost patch exists")
    check("insightSummaryCostRowLabels" in diff, "label remapper exists")
    check("insightSummaryIsRestaurantFl" in diff, "restaurant gate exists")
    # Non-restaurant remaps slots 4/5/6/8 — does not remove rows / display:none
    key = diff[diff.find("var k0 = Number(scope.key0)") : diff.find("UNIT-5C-2-INSIGHT-SUMMARY-BT-END")]
    check("setRowValue(4" in key and "setRowValue(8" in key, "non-restaurant fills all mapped slots")
    for bad in ("Food Cost", "Drink Cost", "FL Rate", "フード", "ドリンク"):
        check(bad not in key, f"non-restaurant branch has no {bad!r}")

    check("active !== false" in plic, "PL Insight catalog keeps custom active lines")
    check("function lineBreakdown" in plic, "custom lines eligible for breakdown")
    check("plInsightClassifyLine" in plic, "BT classify present")
    check("getAnalysisMetrics" in plic, "preset metrics drive FL")
    check("PLACEHOLDER" in plic and "v === PLACEHOLDER" in plic, "placeholder sales not treated as real income")
    check("return null" in plic and "flSnapFromParts" in plic, "all-zero FL → null No Data")

    check("getAnalysisMetrics" in analyze, "Analyze uses analysis metrics")
    check("line.active === false" in analyze, "Analyze skips inactive lines only")
    check("plAnalyzeIsRestaurant" in analyze, "Analyze restaurant gate")

    check("key0" in exp and "key1" in exp, "expense reader has key totals")
    check("isFoodLine" in exp and "isDrinkLine" in exp, "restaurant food/drink detectors kept")

    for rel in PAGES:
        t = (ROOT / rel).read_text(encoding="utf-8")
        m0, m1 = t.find("insight-monthly-cost"), t.find("insight-monthly-progress")
        a0, a1 = t.find("insight-annual-cost"), t.find("insight-annual-progress")
        m = t[m0:m1] if m0 >= 0 and m1 > m0 else ""
        a = t[a0:a1] if a0 >= 0 and a1 > a0 else ""
        check("display:none" not in m and "display: none" not in m, f"{rel} monthly cost no display:none gap")
        check("display:none" not in a and "display: none" not in a, f"{rel} annual cost no display:none gap")
        check(t.count("insight-monthly-cost__row") >= 9, f"{rel} monthly 9 cost rows")
        check(t.count("insight-annual-cost__row") >= 9, f"{rel} annual 9 cost rows")
        check("40px * 9" in t, f"{rel} 9-row geometry")
        check("UNIT-5C-2-INSIGHT-SUMMARY-BT-BEGIN" in t, f"{rel} 5C-2 present")

    for rel in PL_PAGES:
        t = (ROOT / rel).read_text(encoding="utf-8")
        check("UNIT-5C-1-PL-INSIGHT-BT-BEGIN" in t, f"{rel} 5C-1 present")
        check("kpi-pl-expense-presets.js" in t, f"{rel} presets")
        check("var METRICS = ['income', 'expenses', 'fixed', 'expected', 'profit']" in t, f"{rel} graph metrics")

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify Insight date-nav perf markers are present on all 4 pages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

CHECKS = [
    ("__INSIGHT_FILL_SCHED", "fill coalesce scheduler"),
    ("runInsightFillHeavy", "fill heavy runner"),
    ("__INSIGHT_FILL_BUSY", "fill in-flight guard"),
    ("wantAnalyze", "analyze pane skip"),
    ("wantGraph", "graph pane skip"),
    ("insight:tabChanged", "tab changed event"),
    ("which === 'analyze' || which === 'graph'", "tab re-render hook"),
    ("insightTrendDirty", "svg dirty flag"),
    ("insightTrendRender", "svg guarded render"),
    ("expenseSnapshotCache", "expense snapshot cache"),
    ("sumThroughMonthCache", "sumThroughMonth cache"),
    ("invalidateInsightExpenseCaches", "expense cache invalidate"),
    ("skipAnalyze: onAnalyze", "analyze skip during date nav"),
    ("__scheduleInsightAnalyzeSettle", "analyze settle scheduler"),
    ("patchAnalyzeMonthlyExpenseCharts(lightM, iso)", "light monthly expense charts"),
    ("patchAnalyzeAnnualYearExpenseCharts(lightM, iso)", "light annual expense charts"),
    ("patchAnnualHistAvgAlloc(lightM, iso)", "light annual hist avg"),
    ("__INSIGHT_DATE_HOLDING", "date hold flag"),
    ("__insightDateHoldStart", "date hold start"),
    ("__insightDateHoldEnd", "date hold end"),
    ("__invalidateTwSalesThroughCache", "sales through cache invalidate"),
    ("__INSIGHT_YEAR_EXPENSE_CACHE", "year expense cache"),
    ("twMetricsCache", "tw metrics cache"),
    ("tryIncrementalTwMetrics", "tw metrics incremental"),
    ("insightAnalyzeExpenseLightScope", "analyze expense light scope"),
]


def main() -> int:
    failed = 0
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for needle, label in CHECKS:
            if needle not in text:
                print(f"FAIL {rel}: missing {label} ({needle})", file=sys.stderr)
                failed += 1
        dirty_count = text.count("insightTrendDirty")
        if dirty_count < 3:
            print(
                f"FAIL {rel}: expected >=3 insightTrendDirty, got {dirty_count}",
                file=sys.stderr,
            )
            failed += 1
        # fill must not sync-call render before schedule
        if (
            "window.renderInsightTwDiffs(iso);" in text
            and "__INSIGHT_FILL_SCHED" in text
        ):
            # sync call may still exist inside runInsightFillHeavy as pending var — OK
            # but the old pattern "SELECTED_ISO = iso; try { renderInsightTwDiffs(iso)" must be gone
            if (
                "window.__INSIGHT_SELECTED_ISO = iso;\n"
                "        try {\n"
                "          if (typeof window.renderInsightTwDiffs === 'function') {\n"
                "            window.renderInsightTwDiffs(iso);"
            ) in text:
                print(f"FAIL {rel}: sync fill render still present", file=sys.stderr)
                failed += 1
        print(f"ok {rel}")
    if failed:
        print(f"{failed} check(s) failed", file=sys.stderr)
        return 1
    print("all date-nav perf checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

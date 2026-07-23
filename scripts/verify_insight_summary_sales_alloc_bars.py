#!/usr/bin/env python3
"""検証: Summary Today(Sales) 棒 + Annual 最下段 Historical Avg が Insight 日付に追従."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def build_seed() -> dict:
    import datetime

    daily_sales = {}
    business_days = {}

    def fill_month(year, month, base):
        d = datetime.date(year, month, 1)
        while d.month == month:
            iso = d.isoformat()
            wk = d.weekday() >= 5
            business_days[iso] = not wk
            if not wk:
                daily_sales[iso] = base + d.day * 100
            d += datetime.timedelta(days=1)

    for y, base in ((2023, 1000), (2024, 2000), (2025, 3000), (2026, 4000)):
        for mo in range(1, 8):
            fill_month(y, mo, base + mo * 100)

    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {"dailySales": daily_sales, "businessDays": business_days},
        "years": {
            str(y): {
                "year": y,
                "status": "open" if y == 2026 else "closed",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
            }
            for y in (2023, 2024, 2025, 2026)
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.add_init_script(
        "window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);"
        % json.dumps(json.dumps(build_seed()))
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "window.__insightSummarySalesWidgets && "
        "window.__insightSummarySalesWidgets.daily && "
        "window.__insightSummarySalesWidgets.monthly && "
        "window.__insightSummarySalesWidgets.annual && "
        "window.__insightSummaryComparisonWidgets && "
        "window.__insightSummaryComparisonWidgets.annualRevision && "
        "window.__insightSummaryComparisonWidgets.annualAnalyzeProgress",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          function openInsight() {
            const btn = document.getElementById('global-nav-index-btn');
            if (btn) btn.click();
          }
          function pct(list) {
            const w = list && list[0];
            return w && typeof w.getPercent === 'function' ? w.getPercent() : null;
          }
          openInsight();
          const isoA = '2026-07-10';
          const isoB = '2026-07-14';
          window.__INSIGHT_SELECTED_ISO = isoA;
          window.renderInsightTwDiffs(isoA);
          const a = {
            daily: pct(window.__insightSummarySalesWidgets.daily),
            monthly: pct(window.__insightSummarySalesWidgets.monthly),
            annual: pct(window.__insightSummarySalesWidgets.annual),
            revision: window.__insightSummaryComparisonWidgets.annualRevision.getPercent(),
            comparison: window.__insightSummaryComparisonWidgets.annual.getPercent(),
            analyzeProgress: pct(window.__insightSummaryComparisonWidgets.annualAnalyzeProgress),
          };
          window.__INSIGHT_SELECTED_ISO = isoB;
          window.renderInsightTwDiffs(isoB);
          const b = {
            daily: pct(window.__insightSummarySalesWidgets.daily),
            monthly: pct(window.__insightSummarySalesWidgets.monthly),
            annual: pct(window.__insightSummarySalesWidgets.annual),
            revision: window.__insightSummaryComparisonWidgets.annualRevision.getPercent(),
            comparison: window.__insightSummaryComparisonWidgets.annual.getPercent(),
            analyzeProgress: pct(window.__insightSummaryComparisonWidgets.annualAnalyzeProgress),
          };
          // light path (Analyze skip) should still move hist avg
          window.renderInsightTwDiffs(isoA, { skipAnalyze: true, mode: 'analyze' });
          const lightA = pct(window.__insightSummaryComparisonWidgets.annualAnalyzeProgress);
          window.renderInsightTwDiffs(isoB, { skipAnalyze: true, mode: 'analyze' });
          const lightB = pct(window.__insightSummaryComparisonWidgets.annualAnalyzeProgress);
          const mA = window.__computeTwMetricsForIso(isoA);
          const mB = window.__computeTwMetricsForIso(isoB);
          const expDailyA = (mA.dailySales / mA.dailyTarget) * 100;
          const expDailyB = (mB.dailySales / mB.dailyTarget) * 100;
          return {
            a, b, lightA, lightB,
            expDailyA, expDailyB, dailyA: mA.dailySales, dailyB: mB.dailySales
          };
        }"""
    )
    if result["a"]["daily"] is None or result["b"]["daily"] is None:
        problems.append(f"{url}: daily sales widget null")
    elif abs(result["a"]["daily"] - result["b"]["daily"]) < 0.01:
        problems.append(
            f"{url}: daily bar did not change {result['a']['daily']} -> {result['b']['daily']}"
        )
    if result["dailyA"] == result["dailyB"]:
        problems.append(f"{url}: test data daily sales equal (bad seed)")
    # revision should track annual comparison
    if abs(result["b"]["revision"] - result["b"]["comparison"]) > 0.5:
        problems.append(
            f"{url}: revision {result['b']['revision']} != comparison {result['b']['comparison']}"
        )
    if result["a"]["analyzeProgress"] is None or result["b"]["analyzeProgress"] is None:
        problems.append(f"{url}: analyzeProgress widget null")
    elif abs(result["b"]["analyzeProgress"] - result["b"]["comparison"]) > 0.5:
        problems.append(
            f"{url}: analyzeProgress {result['b']['analyzeProgress']} != "
            f"comparison {result['b']['comparison']}"
        )
    if result["lightA"] is None or result["lightB"] is None:
        problems.append(f"{url}: light-path analyzeProgress null")
    elif abs(result["lightA"] - result["lightB"]) < 0.01:
        problems.append(
            f"{url}: light-path hist avg did not change "
            f"{result['lightA']} -> {result['lightB']}"
        )
    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} a={result['a']} b={result['b']} sales={result['dailyA']}->{result['dailyB']}")
    return problems


def main() -> int:
    import os

    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
            problems.extend(verify_page(page, path.as_uri()))
            page.close()
        browser.close()
    if problems:
        print("FAIL:")
        for pr in problems:
            print(" ", pr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""検証: Insight → Summary Comparison 比較バーが過去平均%に追従."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
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
                daily_sales[iso] = base + d.day * 10
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
    seed = build_seed()
    page.add_init_script(
        "window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);"
        % json.dumps(json.dumps(seed))
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "window.__insightSummaryComparisonWidgets && "
        "window.__insightSummaryComparisonWidgets.monthly && "
        "window.__insightSummaryComparisonWidgets.annual",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const m = window.__computeTwMetricsForIso(iso);
          window.renderInsightTwDiffs(iso);
          const p1m = window.__sumMonthSalesThroughDay(2025, 7, 14);
          const p2m = window.__sumMonthSalesThroughDay(2024, 7, 14);
          const p3m = window.__sumMonthSalesThroughDay(2023, 7, 14);
          const avgM = (p1m.sum + p2m.sum + p3m.sum) / 3;
          const p1y = window.__sumYearSalesThroughDay(2025, 7, 14);
          const p2y = window.__sumYearSalesThroughDay(2024, 7, 14);
          const p3y = window.__sumYearSalesThroughDay(2023, 7, 14);
          const avgY = (p1y.sum + p2y.sum + p3y.sum) / 3;
          const gotM = window.__insightSummaryComparisonWidgets.monthly.getPercent();
          const gotA = window.__insightSummaryComparisonWidgets.annual.getPercent();
          const expM = (m.mtdA / avgM) * 100;
          const expA = (m.ytdA / avgY) * 100;
          const mWrap = document
            .querySelector('#insight-monthly-comparison-alloc-graph')
            .closest('.insight-kpi-graph-wrap');
          const aWrap = document
            .querySelector('#insight-annual-comparison-alloc-graph')
            .closest('.insight-kpi-graph-wrap');
          return {
            mtdA: m.mtdA,
            ytdA: m.ytdA,
            avgM,
            avgY,
            gotM,
            gotA,
            expM,
            expA,
            mKgi: mWrap && mWrap.style.getPropertyValue('--kgi-x'),
            aKgi: aWrap && aWrap.style.getPropertyValue('--kgi-x'),
            mFill: mWrap && mWrap.style.getPropertyValue('--fill-w'),
            closeEnough: Math.abs(gotM - expM) < 0.15 && Math.abs(gotA - expA) < 0.15,
            stillFallback: Math.abs(gotM - 85) < 0.01 || Math.abs(gotA - 85) < 0.01,
          };
        }"""
    )
    if result.get("stillFallback"):
        problems.append(f"{url}: still fallback 85% {result}")
    if not result.get("closeEnough"):
        problems.append(
            f"{url}: pct mismatch gotM={result.get('gotM')} expM={result.get('expM')} "
            f"gotA={result.get('gotA')} expA={result.get('expA')}"
        )
    if not result.get("mKgi") or result.get("mKgi") == "0px":
        problems.append(f"{url}: monthly --kgi-x empty/zero {result.get('mKgi')}")
    if not result.get("aKgi") or result.get("aKgi") == "0px":
        problems.append(f"{url}: annual --kgi-x empty/zero {result.get('aKgi')}")
    rel = url.split("/kpi-navigator/")[-1]
    print(
        f"  {rel} mtd={result.get('mtdA')} avgM={result.get('avgM'):.1f} "
        f"pctM={result.get('gotM'):.2f} (exp {result.get('expM'):.2f}) "
        f"kgi={result.get('mKgi')}"
    )
    print(
        f"    ytd={result.get('ytdA')} avgY={result.get('avgY'):.1f} "
        f"pctA={result.get('gotA'):.2f} (exp {result.get('expA'):.2f}) "
        f"kgi={result.get('aKgi')}"
    )
    return problems


def main() -> int:
    import os

    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
            url = path.as_uri()
            problems.extend(verify_page(page, url))
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

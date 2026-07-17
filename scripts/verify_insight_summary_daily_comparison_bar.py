#!/usr/bin/env python3
"""検証: Insight → Summary → Daily 比較バーが同曜日過去平均%に追従."""

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

    # 2026-07-14 Tue → -364 2025-07-15, -728 2024-07-16, -1092 2023-07-18
    pairs = [
        (2026, 7, 14, 4000),
        (2025, 7, 15, 2500),
        (2024, 7, 16, 1800),
        (2023, 7, 18, 1200),
    ]
    for y, m, d, amt in pairs:
        iso = datetime.date(y, m, d).isoformat()
        business_days[iso] = True
        daily_sales[iso] = amt

    for y in (2023, 2024, 2025, 2026):
        d = datetime.date(y, 7, 1)
        while d.month == 7:
            iso = d.isoformat()
            if iso not in business_days:
                business_days[iso] = d.weekday() < 5
            d += datetime.timedelta(days=1)

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
        "window.__insightSummaryComparisonWidgets.daily",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const m = window.__computeTwMetricsForIso(iso);
          window.renderInsightTwDiffs(iso);
          const avg = (2500 + 1800 + 1200) / 3;
          const got = window.__insightSummaryComparisonWidgets.daily.getPercent();
          const exp = (m.dailySales / avg) * 100;
          const wrap = document
            .querySelector('#insight-daily-historical-alloc-graph')
            .closest('.insight-kpi-graph-wrap');
          return {
            dailySales: m.dailySales,
            isBusinessToday: m.isBusinessToday,
            avg,
            got,
            exp,
            kgi: wrap && wrap.style.getPropertyValue('--kgi-x'),
            closeEnough: Math.abs(got - exp) < 0.15,
            stillFallback: Math.abs(got - 85) < 0.01,
          };
        }"""
    )
    if not result.get("isBusinessToday"):
        problems.append(f"{url}: expected business day")
    if result.get("stillFallback"):
        problems.append(f"{url}: still fallback 85% {result}")
    if not result.get("closeEnough"):
        problems.append(
            f"{url}: pct got={result.get('got')} exp={result.get('exp')}"
        )
    if not result.get("kgi") or result.get("kgi") == "0px":
        problems.append(f"{url}: --kgi-x empty/zero {result.get('kgi')}")
    rel = url.split("/kpi-navigator/")[-1]
    print(
        f"  {rel} sales={result.get('dailySales')} avg={result.get('avg'):.1f} "
        f"pct={result.get('got'):.2f} (exp {result.get('exp'):.2f}) kgi={result.get('kgi')}"
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

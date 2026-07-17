#!/usr/bin/env python3
"""検証: Same Month Historical Compare が Store の同月累計と一致."""

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

    fill_month(2023, 7, 1000)
    fill_month(2024, 7, 2000)
    fill_month(2025, 7, 3000)
    fill_month(2026, 7, 4000)

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
        "() => typeof window.__sumMonthSalesThroughDay === 'function' && "
        "typeof window.renderInsightTwDiffs === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const m = window.__computeTwMetricsForIso(iso);
          window.renderInsightTwDiffs(iso);
          const block = document.querySelector('.insight-monthly-historical-compare');
          const vals = [...block.querySelectorAll('.insight-monthly-historical-compare__value')].map(
            (el) => el.textContent.trim()
          );
          const p1 = window.__sumMonthSalesThroughDay(2025, 7, 14);
          const p2 = window.__sumMonthSalesThroughDay(2024, 7, 14);
          const p3 = window.__sumMonthSalesThroughDay(2023, 7, 14);
          const fmt = window.__twFmtMoney;
          const fmtDiff = window.__twFmtDiff;
          return {
            vals,
            mtdA: m && m.mtdA,
            expected: [
              fmt(p1.sum),
              fmtDiff(m.mtdA, p1.sum),
              fmt(p2.sum),
              fmtDiff(m.mtdA, p2.sum),
              fmt(p3.sum),
              fmtDiff(m.mtdA, p3.sum),
            ],
            prior: { p1: p1.sum, p2: p2.sum, p3: p3.sum, has: [p1.hasData, p2.hasData, p3.hasData] },
            stillPlaceholder: vals.some((v) => v === '$123,456' || v === '¥123,456'),
          };
        }"""
    )
    if result.get("stillPlaceholder"):
        problems.append(f"{url}: still placeholder {result['vals']}")
    exp = result.get("expected") or []
    got = result.get("vals") or []
    for i, (e, g) in enumerate(zip(exp, got)):
        if e != g:
            problems.append(f"{url}: row{i} got={g!r} expected={e!r}")
    if len(got) != 6:
        problems.append(f"{url}: row count {len(got)}")
    print(f"  {url.split('/kpi-navigator/')[-1]} mtdA={result.get('mtdA')} prior={result.get('prior')}")
    print(f"    vals={got}")
    return problems


def main() -> int:
    launch_kwargs = {"headless": True}
    if EXE.exists():
        launch_kwargs["executable_path"] = str(EXE)
    all_problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        for page_path in PAGES:
            context = browser.new_context()
            page = context.new_page()
            try:
                all_problems += verify_page(page, page_path.as_uri())
            except Exception as e:  # noqa: BLE001
                all_problems.append(f"{page_path}: EXCEPTION {e}")
            finally:
                context.close()
        browser.close()
    print("\n=== RESULT ===")
    if all_problems:
        for pr in all_problems:
            print("NG:", pr)
        return 1
    print("OK: Monthly Same Month Historical Compare = Store")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

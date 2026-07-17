#!/usr/bin/env python3
"""検証: Historical Annual Compare が Store の年累計（同期日まで）と一致."""

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

    def fill_through(year, end_month, end_day, base):
        d = datetime.date(year, 1, 1)
        end = datetime.date(year, end_month, end_day)
        while d <= end:
            iso = d.isoformat()
            wk = d.weekday() >= 5
            business_days[iso] = not wk
            if not wk:
                daily_sales[iso] = base + d.timetuple().tm_yday
            d += datetime.timedelta(days=1)

    fill_through(2023, 7, 14, 500)
    fill_through(2024, 7, 14, 800)
    fill_through(2025, 7, 14, 1200)
    fill_through(2026, 7, 14, 1600)

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
        "() => typeof window.__sumYearSalesThroughDay === 'function' && "
        "typeof window.renderInsightTwDiffs === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const m = window.__computeTwMetricsForIso(iso);
          window.renderInsightTwDiffs(iso);
          const block = document.querySelector('.insight-annual-historical-compare');
          const vals = [...block.querySelectorAll('.insight-annual-historical-compare__value')].map(
            (el) => el.textContent.trim()
          );
          const p1 = window.__sumYearSalesThroughDay(2025, 7, 14);
          const p2 = window.__sumYearSalesThroughDay(2024, 7, 14);
          const p3 = window.__sumYearSalesThroughDay(2023, 7, 14);
          const fmt = window.__twFmtMoney;
          const fmtDiff = window.__twFmtDiff;
          const fmtAch = window.__twFmtAchPct;
          const monthlyStill = [...document.querySelectorAll('.insight-monthly-historical-compare__value')]
            .map((el) => el.textContent.trim());
          return {
            vals,
            ytdA: m && m.ytdA,
            expected: [
              fmt(p1.sum),
              fmtDiff(m.ytdA, p1.sum),
              fmtAch(m.ytdA, p1.sum),
              fmt(p2.sum),
              fmtDiff(m.ytdA, p2.sum),
              fmt(p3.sum),
              fmtDiff(m.ytdA, p3.sum),
            ],
            prior: { p1: p1.sum, p2: p2.sum, p3: p3.sum },
            monthlyOk: monthlyStill.length === 6 && !monthlyStill.some((v) => v === '$123,456'),
            stillPlaceholder: vals.some((v) => v === '$123,456' || v === '$1,456' || v === '108.3%'),
          };
        }"""
    )
    if result.get("stillPlaceholder"):
        problems.append(f"{url}: still placeholder {result['vals']}")
    if not result.get("monthlyOk"):
        problems.append(f"{url}: monthly historical regress")
    exp = result.get("expected") or []
    got = result.get("vals") or []
    for i, (e, g) in enumerate(zip(exp, got)):
        if e != g:
            problems.append(f"{url}: row{i} got={g!r} expected={e!r}")
    if len(got) != 7:
        problems.append(f"{url}: row count {len(got)}")
    print(f"  {url.split('/kpi-navigator/')[-1]} ytdA={result.get('ytdA')} prior={result.get('prior')}")
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
    print("OK: Historical Annual Compare = Store（Monthly 回帰なし）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

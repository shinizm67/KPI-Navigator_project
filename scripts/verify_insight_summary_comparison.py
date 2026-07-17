#!/usr/bin/env python3
"""検証: Summary Comparison が前年同月/前年同日累計と一致."""

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

    # YTD 用に 1–7 月も埋める
    for y, base in ((2025, 2000), (2026, 4000)):
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
            for y in (2025, 2026)
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
        "typeof window.__sumYearSalesThroughDay === 'function' && "
        "typeof window.renderInsightTwDiffs === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const m = window.__computeTwMetricsForIso(iso);
          window.renderInsightTwDiffs(iso);
          const mVals = [...document.querySelectorAll(
            '.insight-monthly-comparison .insight-monthly-comparison__value'
          )].map((el) => el.textContent.trim());
          const aVals = [...document.querySelectorAll(
            '.insight-annual-comparison .insight-annual-comparison__value'
          )].map((el) => el.textContent.trim());
          const lastM = window.__sumMonthSalesThroughDay(2025, 7, 14);
          const lastY = window.__sumYearSalesThroughDay(2025, 7, 14);
          const fmt = window.__twFmtMoney;
          const fmtDiff = window.__twFmtDiff;
          return {
            mVals,
            aVals,
            mtdA: m && m.mtdA,
            ytdA: m && m.ytdA,
            expectedM: [
              fmt(m.mtdA),
              fmt(lastM.sum),
              fmtDiff(m.mtdA, lastM.sum),
              '—',
            ],
            expectedA: [
              fmt(m.ytdA),
              fmt(lastY.sum),
              fmtDiff(m.ytdA, lastY.sum),
              '—',
            ],
            prior: {
              lastM: lastM.sum,
              lastY: lastY.sum,
              hasM: lastM.hasData,
              hasY: lastY.hasData,
            },
            stillPlaceholder:
              mVals.concat(aVals).some(
                (v) => v === '$123,456' || v === '¥123,456' || v === '+1.8%'
              ),
          };
        }"""
    )
    if result.get("stillPlaceholder"):
        problems.append(
            f"{url}: still placeholder m={result['mVals']} a={result['aVals']}"
        )
    for label, exp_key, got_key in (
        ("monthly", "expectedM", "mVals"),
        ("annual", "expectedA", "aVals"),
    ):
        exp = result.get(exp_key) or []
        got = result.get(got_key) or []
        for i, (e, g) in enumerate(zip(exp, got)):
            if e != g:
                problems.append(f"{url}: {label} row{i} got={g!r} expected={e!r}")
        if len(got) != 4:
            problems.append(f"{url}: {label} row count {len(got)}")
    rel = url.split("/kpi-navigator/")[-1]
    print(
        f"  {rel} mtdA={result.get('mtdA')} ytdA={result.get('ytdA')} "
        f"prior={result.get('prior')}"
    )
    print(f"    monthly={result.get('mVals')}")
    print(f"    annual={result.get('aVals')}")
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

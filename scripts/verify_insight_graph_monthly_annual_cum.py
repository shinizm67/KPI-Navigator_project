#!/usr/bin/env python3
"""検証: Insight → Graph → Monthly/Annual 累計横棒が mtd/ytd に追従."""

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

    for mo in range(1, 8):
        fill_month(2026, mo, 4000 + mo * 100)

    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {"dailySales": daily_sales, "businessDays": business_days},
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
            }
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
        "window.__insightGraphCumWidgets && "
        "window.__insightGraphCumWidgets.monthly && "
        "window.__insightGraphCumWidgets.annual",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const m = window.__computeTwMetricsForIso(iso);
          window.renderInsightTwDiffs(iso);
          const fmt = window.__twFmtMoney;
          const mRow = document.querySelector(
            '#insight-jump-graph-monthly .insight-graph-monthly__row--cumulative'
          );
          const aRow = document.querySelector(
            '#insight-jump-graph-annual .insight-graph-annual__row--cumulative'
          );
          const capsM = [...mRow.querySelectorAll('.insight-graph-daily__marker-cap-value')].map(
            (el) => el.textContent.trim()
          );
          const capsA = [...aRow.querySelectorAll('.insight-graph-daily__marker-cap-value')].map(
            (el) => el.textContent.trim()
          );
          const pctM = document
            .getElementById('insight-graph-monthly-cumulative-target-actual-pct')
            .textContent.trim();
          const pctA = document
            .getElementById('insight-graph-annual-cumulative-target-actual-pct')
            .textContent.trim();
          const expPctM =
            m.mtdT > 0
              ? (Math.round((m.mtdA / m.mtdT) * 1000) / 10).toLocaleString('en-US', {
                  maximumFractionDigits: 1,
                }) + '%'
              : '—';
          const expPctA =
            m.ytdT > 0
              ? (Math.round((m.ytdA / m.ytdT) * 1000) / 10).toLocaleString('en-US', {
                  maximumFractionDigits: 1,
                }) + '%'
              : '—';
          return {
            mtdA: m.mtdA,
            mtdT: m.mtdT,
            ytdA: m.ytdA,
            ytdT: m.ytdT,
            hasPlan: m.hasPlan,
            capsM,
            capsA,
            pctM,
            pctA,
            expectedCapsM: [fmt(m.mtdA), fmt(m.mtdT)],
            expectedCapsA: [fmt(m.ytdA), fmt(m.ytdT)],
            expPctM,
            expPctA,
            stillPlaceholder:
              capsM.concat(capsA).some((v) => v.includes('123,456,789') || v.includes('100,456,789')) ||
              pctM === '123%' ||
              pctA === '123%',
          };
        }"""
    )
    if not result.get("hasPlan"):
        problems.append(f"{url}: expected hasPlan")
    if result.get("stillPlaceholder"):
        problems.append(f"{url}: still placeholder {result}")
    for label, exp_key, got_key in (
        ("monthly", "expectedCapsM", "capsM"),
        ("annual", "expectedCapsA", "capsA"),
    ):
        for i, (e, g) in enumerate(
            zip(result.get(exp_key) or [], result.get(got_key) or [])
        ):
            if e != g:
                problems.append(f"{url}: {label} cap{i} got={g!r} expected={e!r}")
    if result.get("pctM") != result.get("expPctM"):
        problems.append(
            f"{url}: pctM got={result.get('pctM')!r} expected={result.get('expPctM')!r}"
        )
    if result.get("pctA") != result.get("expPctA"):
        problems.append(
            f"{url}: pctA got={result.get('pctA')!r} expected={result.get('expPctA')!r}"
        )
    rel = url.split("/kpi-navigator/")[-1]
    print(
        f"  {rel} mtd={result.get('mtdA')}/{result.get('mtdT')} "
        f"ytd={result.get('ytdA')}/{result.get('ytdT')}"
    )
    print(f"    monthly caps={result.get('capsM')} pct={result.get('pctM')}")
    print(f"    annual  caps={result.get('capsA')} pct={result.get('pctA')}")
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

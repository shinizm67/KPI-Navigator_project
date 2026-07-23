#!/usr/bin/env python3
"""検証: Analyze Monthly Expense 当月棒が MEP÷mtdA になる."""

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
    d = datetime.date(2026, 7, 1)
    while d.month == 7:
        iso = d.isoformat()
        wk = d.weekday() >= 5
        business_days[iso] = not wk
        if not wk:
            daily_sales[iso] = 5000  # flat → MTD through 14 easy
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
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {
                    "exp_rent": {"2026-07-01": 10000},
                    "exp_food_cost": {"2026-07-14": 5000},
                },
            }
        },
    }


def catalog() -> dict:
    return {
        "lines": [
            {"lineId": "exp_rent", "bucket": "fixed", "inputStyle": "daily", "active": True},
            {
                "lineId": "exp_food_cost",
                "bucket": "variable",
                "inputStyle": "daily",
                "active": True,
            },
        ]
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.add_init_script(
        """
        window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);
        window.localStorage.setItem('kpiNavigator.plLineCatalog', %s);
        """
        % (json.dumps(json.dumps(build_seed())), json.dumps(json.dumps(catalog())))
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "typeof window.__insightReadMonthExpense === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const m = window.__computeTwMetricsForIso(iso);
          const paneSummary = document.getElementById('insight-pane-summary');
          const paneAnalyze = document.getElementById('insight-pane-analyze');
          const paneGraph = document.getElementById('insight-pane-graph');
          if (paneSummary) paneSummary.hidden = true;
          if (paneAnalyze) paneAnalyze.hidden = false;
          if (paneGraph) paneGraph.hidden = true;
          window.renderInsightTwDiffs(iso);
          const chart = document.getElementById('insight-analyze-expense-pl-current');
          const fixedEl = chart.querySelector('[data-role="fixed-pct"]');
          const varEl = chart.querySelector('[data-role="variable-pct"]');
          const exp = window.__insightReadMonthExpense(2026, 7, 14);
          const sales = m.mtdA;
          const expFixed = Math.round((exp.fixed / sales) * 100);
          const expVar = Math.round((exp.variable / sales) * 100);
          const other = document.getElementById('insight-analyze-expense-pl-last-year');
          const otherFixed = other && other.querySelector('[data-role="fixed-pct"]').textContent.trim();
          return {
            mtdA: sales,
            exp,
            gotFixed: fixedEl.textContent.trim(),
            gotVar: varEl.textContent.trim(),
            expFixed: expFixed + '%',
            expVar: expVar + '%',
            otherFixed,
            cssFixed: chart.style.getPropertyValue('--fixed-pct').trim(),
          };
        }"""
    )
    if result.get("gotFixed") != result.get("expFixed"):
        problems.append(
            f"{url}: fixed got={result.get('gotFixed')} exp={result.get('expFixed')}"
        )
    if result.get("gotVar") != result.get("expVar"):
        problems.append(
            f"{url}: var got={result.get('gotVar')} exp={result.get('expVar')}"
        )
    if result.get("gotFixed") == "40%":
        problems.append(f"{url}: still mock 40%")
    if not result.get("exp") or not result.get("exp", {}).get("hasData"):
        problems.append(f"{url}: expense hasData false {result.get('exp')}")
    # 前年データなし → 0%（全棒を実データ化する現行仕様）
    if result.get("otherFixed") not in ("0%", "0"):
        problems.append(f"{url}: last-year expected 0% got {result.get('otherFixed')}")
    rel = url.split("/kpi-navigator/")[-1]
    print(
        f"  {rel} mtdA={result.get('mtdA')} exp={result.get('exp')} "
        f"current={result.get('gotFixed')}/{result.get('gotVar')} "
        f"lastYear={result.get('otherFixed')}"
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

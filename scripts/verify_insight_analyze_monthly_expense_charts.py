#!/usr/bin/env python3
"""検証: Insight Analyze Monthly Expense 横棒4本が実データ % になる."""

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


def catalog() -> dict:
    return {
        "lines": [
            {"lineId": "exp_rent", "bucket": "fixed", "inputStyle": "monthly", "active": True},
            {
                "lineId": "exp_food_cost",
                "bucket": "variable",
                "inputStyle": "daily",
                "active": True,
            },
        ]
    }


def seed_store() -> dict:
    # July 2026 thru 14: sales 10000+20000=30000
    # fixed rent monthly 6000 → allocated across biz days (all days biz by default)
    # variable food 1000+2000 on 1 and 10
    # 2025 July: sales 50000 thru 14, rent 10000, food 5000 on day 1
    # 2024/2023: no expense → 0%
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {
            "dailySales": {
                "2026-07-01": 10000,
                "2026-07-10": 20000,
                "2026-07-20": 99999,
                "2025-07-01": 50000,
                "2025-07-20": 1,
                "2024-07-01": 8000,
            },
            "businessDays": {},
        },
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {
                    "exp_food_cost": {
                        "2026-07-01": 1000,
                        "2026-07-10": 2000,
                        "2026-07-20": 9999,
                    }
                },
            },
            "2025": {
                "year": 2025,
                "status": "closed",
                "plan": {"targetSales": 500000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {"exp_food_cost": {"2025-07-01": 5000}},
            },
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    store = seed_store()
    cat = catalog()
    # July dim=31; all days biz → rent 6000 / 31 per day * 14 ≈ through day amount
    # Better: use daily rent for precision in test
    page.add_init_script(
        """
        window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);
        window.localStorage.setItem('kpiNavigator.plLineCatalog', %s);
        window.localStorage.setItem('kpi-pl-expenses-v1:2026', %s);
        window.localStorage.setItem('kpi-pl-expenses-v1:2025', %s);
        """
        % (
            json.dumps(json.dumps(store)),
            json.dumps(json.dumps(cat)),
            # monthly rent July (month0=6): 6200 → easy /31
            json.dumps(json.dumps({"exp_rent:6": 6200})),
            json.dumps(json.dumps({"exp_rent:6": 9300})),
        )
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "typeof window.__insightReadMonthExpense === 'function' && "
        "typeof window.__sumMonthSalesThroughDay === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          window.renderInsightTwDiffs('2026-07-14');
          function read(id) {
            const el = document.getElementById(id);
            if (!el) return null;
            return {
              fixed: el.style.getPropertyValue('--fixed-pct').trim(),
              variable: el.style.getPropertyValue('--variable-pct').trim(),
              fixedLabel: (el.querySelector('[data-role="fixed-pct"]') || {}).textContent,
              variableLabel: (el.querySelector('[data-role="variable-pct"]') || {}).textContent,
            };
          }
          const curExp = window.__insightReadMonthExpense(2026, 7, 14);
          const lyExp = window.__insightReadMonthExpense(2025, 7, 14);
          const y2 = window.__insightReadMonthExpense(2024, 7, 14);
          const salesLy = window.__sumMonthSalesThroughDay(2025, 7, 14);
          return {
            charts: {
              current: read('insight-analyze-expense-pl-current'),
              lastYear: read('insight-analyze-expense-pl-last-year'),
              y2: read('insight-analyze-expense-pl-2y'),
              y3: read('insight-analyze-expense-pl-3y'),
            },
            curExp,
            lyExp,
            y2,
            salesLy,
            hasChartsFn: typeof window.patchAnalyzeMonthlyExpenseCharts === 'undefined'
              ? 'injected-inline'
              : 'exposed',
          };
        }"""
    )
    charts = result.get("charts") or {}
    cur = charts.get("current") or {}
    ly = charts.get("lastYear") or {}
    y2 = charts.get("y2") or {}
    y3 = charts.get("y3") or {}

    # 2026: sales thru 14 = 30000
    # rent 6200 / 31 * 14 = 2800 fixed (allocateAcrossBizDays: floor then rem on last)
    # Actually allocateAcrossBizDays: base=floor(6200/31)=200, rem=6200-6200=0? 31*200=6200, rem=0
    # days 1..14 each get 200 → fixed=2800
    # variable food 1000+2000=3000
    # fixed pct = 2800/30000*100 = 9.333 → 9
    # variable pct = 3000/30000*100 = 10
    if cur.get("fixed") != "9":
        problems.append(f"{url}: current fixed={cur.get('fixed')} expected 9")
    if cur.get("variable") != "10":
        problems.append(f"{url}: current variable={cur.get('variable')} expected 10")

    # 2025: sales 50000, rent 9300/31=300 exact, *14=4200 fixed; food 5000
    # fixed 4200/50000=8.4→8; var 5000/50000=10
    if ly.get("fixed") != "8":
        problems.append(f"{url}: lastYear fixed={ly.get('fixed')} expected 8")
    if ly.get("variable") != "10":
        problems.append(f"{url}: lastYear variable={ly.get('variable')} expected 10")

    # 2024: sales exist but no expense → 0
    if y2.get("fixed") != "0" or y2.get("variable") != "0":
        problems.append(f"{url}: 2y should be 0 got {y2}")
    if y3.get("fixed") != "0" or y3.get("variable") != "0":
        problems.append(f"{url}: 3y should be 0 got {y3}")

    # Must not remain mock 40/27
    if cur.get("fixedLabel") == "40%":
        problems.append(f"{url}: current still mock 40%")

    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} cur={cur} ly={ly} y2={y2} y3={y3}")
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

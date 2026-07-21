#!/usr/bin/env python3
"""検証: Analyze Annual Expense & Profit / Year Expense 横棒."""

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
    # 2026 YTD thru Jul 14: sales Jan-Jun none + Jul 10000+20000=30000
    # Actually need YTD sales - put sales in Jan and Jul
    sales = {
        "2026-01-15": 70000,
        "2026-07-01": 10000,
        "2026-07-10": 20000,
        "2025-01-15": 50000,
        "2025-07-01": 40000,
    }
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {"dailySales": sales, "businessDays": {}},
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {
                    "exp_food_cost": {
                        "2026-01-15": 5000,
                        "2026-07-01": 1000,
                        "2026-07-10": 2000,
                    }
                },
            },
            "2025": {
                "year": 2025,
                "status": "closed",
                "plan": {"targetSales": 500000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {
                    "exp_food_cost": {"2025-01-15": 4000, "2025-07-01": 3000}
                },
            },
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.add_init_script(
        """
        window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);
        window.localStorage.setItem('kpiNavigator.plLineCatalog', %s);
        window.localStorage.setItem('kpi-pl-expenses-v1:2026', %s);
        window.localStorage.setItem('kpi-pl-expenses-v1:2025', %s);
        """
        % (
            json.dumps(json.dumps(seed_store())),
            json.dumps(json.dumps(catalog())),
            # Jan month0=0 rent 3100; Jul month0=6 rent 6200
            json.dumps(json.dumps({"exp_rent:0": 3100, "exp_rent:6": 6200})),
            json.dumps(json.dumps({"exp_rent:0": 3100, "exp_rent:6": 6200})),
        )
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "typeof window.__insightReadMonthExpense === 'function' && "
        "typeof window.__sumYearSalesThroughDay === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          window.renderInsightTwDiffs('2026-07-14');
          function chart(id) {
            const el = document.getElementById(id);
            if (!el) return null;
            return {
              fixed: el.style.getPropertyValue('--fixed-pct').trim(),
              variable: el.style.getPropertyValue('--variable-pct').trim(),
              label: (el.querySelector('[data-role="fixed-pct"]') || {}).textContent,
            };
          }
          const block = document.querySelector(
            '#insight-jump-analyze-annual .insight-annual-expense-profit'
          );
          const vals = block
            ? Array.from(
                block.querySelectorAll('.insight-annual-expense-profit__value')
              ).map((el) => el.textContent.trim())
            : [];
          return {
            current: chart('insight-analyze-annual-year-expense-pl-current'),
            lastYear: chart('insight-analyze-annual-year-expense-pl-last-year'),
            y2: chart('insight-analyze-annual-year-expense-pl-2y'),
            profitRows: vals,
          };
        }"""
    )
    cur = result.get("current") or {}
    ly = result.get("lastYear") or {}
    y2 = result.get("y2") or {}
    rows = result.get("profitRows") or []

    if cur.get("fixed") == "40" or cur.get("label") == "40%":
        problems.append(f"{url}: current still mock 40%")
    if not cur.get("fixed") or cur.get("fixed") == "0" and cur.get("variable") == "0":
        # might be zero if sales path fails - check rows
        pass
    if not rows or rows[0] in ("$123,456", "¥123,456", "—"):
        problems.append(f"{url}: expense total still mock/empty {rows[:1]}")
    if len(rows) >= 5 and rows[4] in ("17.3%",):
        problems.append(f"{url}: margin still mock 17.3%")
    if y2.get("fixed") != "0" or y2.get("variable") != "0":
        problems.append(f"{url}: 2y should be 0 got {y2}")

    # last year should have some positive % if data present
    if ly.get("fixed") == "40":
        problems.append(f"{url}: lastYear still mock")

    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} cur={cur} ly={ly} y2={y2} rows={rows}")
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

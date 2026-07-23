#!/usr/bin/env python3
"""検証: Historical Insight Access Best/Worst Same Month が実データになる."""

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
            {
                "lineId": "exp_food_cost",
                "bucket": "variable",
                "inputStyle": "daily",
                "active": True,
            }
        ]
    }


def seed_store() -> dict:
    # Viewing 2026-04-21. Same-month April history:
    # 2025 Apr sales 40000 (full month), expense 10000 → margin 75%
    # 2024 Apr sales 90000, expense 30000 → margin ~67%  → BEST
    # 2023 Apr sales 10000, expense 8000 → margin 20%   → WORST
    sales = {}
    for d in range(1, 31):
        sales[f"2025-04-{d:02d}"] = 40000 // 30
        sales[f"2024-04-{d:02d}"] = 90000 // 30
        sales[f"2023-04-{d:02d}"] = 10000 // 30
    # remainder on day 1 for exact totals
    sales["2025-04-01"] = 40000 - (40000 // 30) * 29
    sales["2024-04-01"] = 90000 - (90000 // 30) * 29
    sales["2023-04-01"] = 10000 - (10000 // 30) * 29
    sales["2026-04-01"] = 1000
    sales["2026-04-21"] = 2000
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-04-21",
        },
        "timeline": {"dailySales": sales, "businessDays": {}},
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {},
            },
            "2025": {
                "year": 2025,
                "status": "closed",
                "plan": {"targetSales": 500000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {"exp_food_cost": {"2025-04-01": 10000}},
            },
            "2024": {
                "year": 2024,
                "status": "closed",
                "plan": {"targetSales": 500000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {"exp_food_cost": {"2024-04-01": 30000}},
            },
            "2023": {
                "year": 2023,
                "status": "closed",
                "plan": {"targetSales": 400000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {"exp_food_cost": {"2023-04-01": 8000}},
            },
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.add_init_script(
        """
        window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);
        window.localStorage.setItem('kpiNavigator.plLineCatalog', %s);
        """
        % (json.dumps(json.dumps(seed_store())), json.dumps(json.dumps(catalog())))
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "typeof window.__sumMonthSalesThroughDay === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const paneSummary = document.getElementById('insight-pane-summary');
          const paneAnalyze = document.getElementById('insight-pane-analyze');
          const paneGraph = document.getElementById('insight-pane-graph');
          if (paneSummary) paneSummary.hidden = true;
          if (paneAnalyze) paneAnalyze.hidden = false;
          if (paneGraph) paneGraph.hidden = true;
          window.renderInsightTwDiffs('2026-04-21');
          const block = document.querySelector(
            '#insight-jump-analyze-monthly .insight-historical-insight-access'
          );
          function group(key) {
            const g = block && block.querySelector('[data-insight-month-key="' + key + '"]');
            if (!g) return null;
            const rows = g.querySelectorAll('.insight-historical-insight-access__value');
            return {
              date: rows[0] && rows[0].textContent.trim(),
              sales: rows[1] && rows[1].textContent.trim(),
              margin: rows[2] && rows[2].textContent.trim(),
            };
          }
          return { best: group('best'), worst: group('worst') };
        }"""
    )
    best = result.get("best") or {}
    worst = result.get("worst") or {}
    if best.get("date") != "2024/04":
        problems.append(f"{url}: best.date={best.get('date')} expected 2024/04")
    if best.get("sales") in (None, "—", "$123,456", "¥123,456"):
        problems.append(f"{url}: best.sales still mock/empty {best.get('sales')}")
    # biz-day sales (~66k) − expense 30k → ~55%
    if best.get("margin") != "55%":
        problems.append(f"{url}: best.margin={best.get('margin')} expected 55%")
    if worst.get("date") != "2023/04":
        problems.append(f"{url}: worst.date={worst.get('date')} expected 2023/04")
    # biz-day sales (~6.6k) − expense 8k → about -20%
    if worst.get("margin") != "-20%":
        problems.append(f"{url}: worst.margin={worst.get('margin')} expected -20%")

    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} best={best} worst={worst}")
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

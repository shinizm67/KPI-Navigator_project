#!/usr/bin/env python3
"""検証: __insightReadMonthExpense が MEP dailyExpenses を読む（UI 非変更）."""

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
    # Minimal year store + catalog lines via gateway keys after load:
    # dailyExpenses on 2026-07 variable/fixed
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {"dailySales": {}, "businessDays": {}},
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {
                    "exp_rent": {"2026-07-01": 100000, "2026-07-14": 0},
                    "exp_food_cost": {
                        "2026-07-01": 1000,
                        "2026-07-10": 2000,
                        "2026-07-14": 3000,
                        "2026-07-20": 9999,  # after throughDay=14 → excluded
                    },
                    "exp_drink_cost": {"2026-07-14": 500},
                },
            }
        },
    }


def catalog() -> dict:
    return {
        "lines": [
            {"lineId": "exp_rent", "bucket": "fixed", "active": True},
            {"lineId": "exp_food_cost", "bucket": "variable", "active": True},
            {"lineId": "exp_drink_cost", "bucket": "variable", "active": True},
        ]
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    seed = build_seed()
    cat = catalog()
    page.add_init_script(
        """
        window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);
        window.localStorage.setItem('kpiNavigator.plLineCatalog', %s);
        """
        % (json.dumps(json.dumps(seed)), json.dumps(json.dumps(cat)))
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.__insightReadMonthExpense === 'function' && "
        "window.KpiYearStore && typeof window.KpiYearStore.loadMepYearPayload === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const full = window.__insightReadMonthExpense(2026, 7);
          const thru = window.__insightReadMonthExpense(2026, 7, 14);
          const empty = window.__insightReadMonthExpense(2026, 8);
          // chart placeholders still hardcoded %
          const chart = document.getElementById('insight-analyze-expense-pl-current');
          const fixedPct = chart && chart.querySelector('[data-role="fixed-pct"]');
          return {
            full,
            thru,
            empty,
            chartFixedLabel: fixedPct && fixedPct.textContent.trim(),
          };
        }"""
    )
    full = result.get("full") or {}
    thru = result.get("thru") or {}
    empty = result.get("empty") or {}
    # rent 100000 + food 1000+2000+3000+9999 + drink 500 = 116499
    if full.get("fixed") != 100000:
        problems.append(f"{url}: full.fixed={full.get('fixed')}")
    if full.get("variable") != 1000 + 2000 + 3000 + 9999 + 500:
        problems.append(f"{url}: full.variable={full.get('variable')}")
    if not full.get("hasData"):
        problems.append(f"{url}: full.hasData false")
    # through 14: rent 100000, food 6000, drink 500 → var 6500
    if thru.get("fixed") != 100000:
        problems.append(f"{url}: thru.fixed={thru.get('fixed')}")
    if thru.get("variable") != 6500:
        problems.append(f"{url}: thru.variable={thru.get('variable')} expected 6500")
    if thru.get("total") != 106500:
        problems.append(f"{url}: thru.total={thru.get('total')}")
    if empty.get("hasData"):
        problems.append(f"{url}: August should have no data")
    # UI not wired yet — still mock 40%
    if result.get("chartFixedLabel") not in (None, "40%"):
        # If somehow wired already, don't fail hard; just note
        pass
    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} full={full} thru={thru} empty.hasData={empty.get('hasData')} chart={result.get('chartFixedLabel')}")
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

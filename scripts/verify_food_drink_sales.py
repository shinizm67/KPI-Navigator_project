#!/usr/bin/env python3
"""検証: Food/Drink CSV 取込ルール + PL Analyze 売上配線."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ANNUAL = ROOT / "app/annual/index.html"
PL = ROOT / "app/profit/pl/index.html"
FOOD_CSV = ROOT / "excel/売上入力_日次_雛形_フード.csv"
DRINK_CSV = ROOT / "excel/売上入力_日次_雛形_ドリンク.csv"
BOTH_CSV = ROOT / "excel/売上入力_日次_雛形_フードドリンク.csv"
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def parse_csv_via_page(page, csv_text: str) -> dict:
    return page.evaluate(
        """(text) => {
          const rows = text.replace(/^\\uFEFF/, '').trim().split(/\\r?\\n/).map((line) => {
            // simple CSV (no quoted commas in fixtures)
            return line.split(',');
          });
          return window.__KPI_DAILY_IMPORT.rowsToMaps(rows);
        }""",
        csv_text,
    )


def verify_csv_import(page) -> list[str]:
    problems: list[str] = []
    page.goto(ANNUAL.as_uri(), wait_until="load")
    page.wait_for_function(
        "() => window.__KPI_DAILY_IMPORT && typeof window.__KPI_DAILY_IMPORT.rowsToMaps === 'function'",
        timeout=20000,
    )

    food = parse_csv_via_page(page, FOOD_CSV.read_text(encoding="utf-8"))
    # 2026-07-01: store 100000, food 70000 → drink 30000
    if food.get("foodByDate", {}).get("2026-07-01") != 70000:
        problems.append(f"food-only food={food.get('foodByDate', {}).get('2026-07-01')}")
    if food.get("drinkByDate", {}).get("2026-07-01") != 30000:
        problems.append(f"food-only drink={food.get('drinkByDate', {}).get('2026-07-01')}")
    if not food.get("hasFoodCol") or food.get("hasDrinkCol"):
        problems.append(f"food-only cols food={food.get('hasFoodCol')} drink={food.get('hasDrinkCol')}")

    drink = parse_csv_via_page(page, DRINK_CSV.read_text(encoding="utf-8"))
    # drink-only: Food = Store − Drink
    d0 = drink.get("drinkByDate", {}).get("2026-07-01")
    f0 = drink.get("foodByDate", {}).get("2026-07-01")
    s0 = drink.get("salesByDate", {}).get("2026-07-01")
    if not (isinstance(s0, (int, float)) and isinstance(d0, (int, float)) and isinstance(f0, (int, float))):
        problems.append(f"drink-only missing maps s={s0} f={f0} d={d0}")
    elif abs((f0 + d0) - s0) > 1:
        problems.append(f"drink-only f+d!=store ({f0}+{d0}!={s0})")
    if drink.get("hasFoodCol") or not drink.get("hasDrinkCol"):
        problems.append(f"drink-only cols food={drink.get('hasFoodCol')} drink={drink.get('hasDrinkCol')}")

    both = parse_csv_via_page(page, BOTH_CSV.read_text(encoding="utf-8"))
    if not (both.get("hasFoodCol") and both.get("hasDrinkCol")):
        problems.append("both-csv missing food/drink columns")
    print(
        f"  CSV food-only 07-01 food={food['foodByDate'].get('2026-07-01')} "
        f"drink={food['drinkByDate'].get('2026-07-01')}"
    )
    print(
        f"  CSV drink-only 07-01 food={f0} drink={d0} store={s0}"
    )
    print(
        f"  CSV both foodCount={both.get('foodCount')} drinkCount={both.get('drinkCount')} "
        f"mismatch={both.get('mismatchCount')}"
    )
    return problems


def cell_int(page, rid: str, month0: int):
    txt = page.evaluate(
        """({ rid, m }) => {
          const el = document.querySelector(
            '[data-field="amount"][data-row="' + rid + '"][data-month="' + m + '"] .pl-amt-cell__text'
          );
          if (!el) return null;
          const t = String(el.textContent || '').trim();
          if (!t || t === '—' || t === '-') return null;
          const n = Number(t.replace(/[^\\d.-]/g, ''));
          return Number.isFinite(n) ? n : null;
        }""",
        {"rid": rid, "m": month0},
    )
    return txt


def verify_pl_analyze(page) -> list[str]:
    problems: list[str] = []
    seed = {
        "meta": {"schemaVersion": 4, "operatingYear": 2026, "legacyMigrated": True},
        "timeline": {
            "dailySales": {
                "2026-07-01": 100000,
                "2026-07-02": 120000,
            },
            "businessDays": {},
        },
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000},
                "dailyExpenses": {
                    "exp_food_cost": {"2026-07-01": 10000, "2026-07-02": 12000},
                    "exp_drink_cost": {"2026-07-01": 3000},
                    "exp_variable_labor": {"2026-07-01": 5000, "2026-07-02": 5500},
                },
                "dailyIncome": {
                    "food_sales": {"2026-07-01": 70000, "2026-07-02": 85000},
                    "drink_sales": {"2026-07-01": 30000, "2026-07-02": 35000},
                },
                "dailyMeta": {"memos": {}, "flags": {}, "weather": {}},
            }
        },
    }
    page.add_init_script(
        """
        window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);
        window.localStorage.setItem('kpi-pl-expenses-v1:2026', %s);
        """
        % (
            json.dumps(json.dumps(seed)),
            json.dumps(json.dumps({"exp_fixed_labor:6": 200000})),
        )
    )
    page.goto(PL.as_uri(), wait_until="load")
    page.wait_for_function(
        "() => typeof window.__plRefreshAnalyzeBlock === 'function'",
        timeout=20000,
    )
    # July = month0 6
    page.evaluate(
        """() => {
          if (typeof window.__plRefreshAnalyzeBlock === 'function') window.__plRefreshAnalyzeBlock();
          if (typeof window.__plRefreshBottomGraph === 'function') window.__plRefreshBottomGraph();
        }"""
    )
    food = cell_int(page, "analyze_food_sales", 6)
    drink = cell_int(page, "analyze_drink_sales", 6)
    labor_emp = cell_int(page, "analyze_labor_employee", 6)
    labor_pt = cell_int(page, "analyze_labor_pt", 6)
    labor_total = cell_int(page, "analyze_labor_total", 6)
    fl_food = cell_int(page, "analyze_monthly_food", 6)
    fl_labor = cell_int(page, "analyze_monthly_labor", 6)
    fl_total = cell_int(page, "analyze_fl_total", 6)

    if food != 155000:
        problems.append(f"analyze_food_sales July={food} expected 155000")
    if drink != 65000:
        problems.append(f"analyze_drink_sales July={drink} expected 65000")
    if labor_emp != 200000:
        problems.append(f"analyze_labor_employee July={labor_emp} expected 200000")
    if labor_pt != 10500:
        problems.append(f"analyze_labor_pt July={labor_pt} expected 10500")
    if labor_total != 210500:
        problems.append(f"analyze_labor_total July={labor_total} expected 210500")
    if fl_food != 25000:
        problems.append(f"analyze_monthly_food July={fl_food} expected 25000")
    if fl_labor != 210500:
        problems.append(f"analyze_monthly_labor July={fl_labor} expected 210500")
    if fl_total != 235500:
        problems.append(f"analyze_fl_total July={fl_total} expected 235500")
    has_bottom = page.evaluate("() => typeof window.__plRefreshBottomGraph === 'function'")
    if not has_bottom:
        problems.append("__plRefreshBottomGraph missing")

    print(
        f"  PL Analyze Jul food={food} drink={drink} emp={labor_emp} "
        f"pt={labor_pt} laborTot={labor_total} flFood={fl_food} flLabor={fl_labor} flTot={fl_total}"
    )
    return problems


def main() -> int:
    import os

    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page()
        problems.extend(verify_csv_import(page))
        page.close()
        page = browser.new_page()
        problems.extend(verify_pl_analyze(page))
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

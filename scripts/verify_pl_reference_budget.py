#!/usr/bin/env python3
"""検証: PL L1 変動費の参考枠.

参考額 = 売上 × max(0, 目標総費率65% − 固定費率)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)

YEAR = 2026
STORE_KEY = "kpiNavigator.kpiYearStore"
EXP_KEY = f"kpi-pl-expenses-v1:{YEAR}"
# July sales 200000, fixed rent 40000 → fixed 20%, target 65% → var 45% → 90000
SALES = 200000
RENT = 40000
EXPECT_AMT = 90000
EXPECT_PCT = "45.00%"


def seed(page) -> None:
    page.evaluate(
        """({ storeKey, expKey, year, sales, rent }) => {
          localStorage.clear();
          localStorage.setItem(storeKey, JSON.stringify({
            meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
            timeline: {
              dailySales: {
                [year + '-07-01']: sales / 2,
                [year + '-07-02']: sales / 2,
              },
              businessDays: {},
            },
            years: {
              [String(year)]: {
                year,
                status: 'open',
                plan: {},
                dailyExpenses: {},
                dailyIncome: {},
                dailyMeta: { memos: {}, flags: {}, weather: {} },
              },
            },
          }));
          localStorage.setItem(expKey, JSON.stringify({ 'exp_rent:6': rent }));
        }""",
        {
            "storeKey": STORE_KEY,
            "expKey": EXP_KEY,
            "year": YEAR,
            "sales": SALES,
            "rent": RENT,
        },
    )


def cell_amount(page, month0: int):
    txt = page.evaluate(
        """({ m }) => {
          const el = document.querySelector(
            '[data-field="amount"][data-row="var_ref_budget"][data-month="' + m + '"] .pl-amt-cell__text'
          );
          return el ? el.textContent : null;
        }""",
        {"m": month0},
    )
    if txt is None:
        return "MISSING"
    s = txt.strip()
    if s in ("", "—", "-", "\u2014"):
        return None
    digits = re.sub(r"[^0-9]", "", s)
    return int(digits) if digits else None


def cell_ratio(page, month0: int) -> str:
    return page.evaluate(
        """({ m }) => {
          const el = document.querySelector(
            '[data-field="ratio"][data-row="var_ref_budget"][data-month="' + m + '"] .pl-ratio-cell__text'
          );
          return el ? String(el.textContent || '').trim() : '';
        }""",
        {"m": month0},
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.goto(f"{url}?year={YEAR}", wait_until="load")
    seed(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => typeof window.__plRefreshReferenceBudget === 'function'",
        timeout=15000,
    )
    page.evaluate(
        "() => { if (window.__plRefreshIncomeBlock) __plRefreshIncomeBlock(); "
        "if (window.__plRefreshReferenceBudget) __plRefreshReferenceBudget(); }"
    )
    page.wait_for_timeout(80)

    jul = cell_amount(page, 6)
    if jul != EXPECT_AMT:
        problems.append(f"july amount {jul!r} want {EXPECT_AMT}")
    pct = cell_ratio(page, 6)
    if pct != EXPECT_PCT:
        problems.append(f"july ratio {pct!r} want {EXPECT_PCT}")
    jan = cell_amount(page, 0)
    if jan is not None:
        problems.append(f"jan should be em-dash, got {jan!r}")

    return problems


def main() -> int:
    if not EXE.exists():
        print(f"Chrome missing: {EXE}", file=sys.stderr)
        return 2
    fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
            try:
                problems = verify_page(page, path.as_uri())
            except Exception as e:  # noqa: BLE001
                problems = [f"exception: {e}"]
            page.close()
            if problems:
                fail += 1
                print(f"FAIL {path}: {problems}")
            else:
                print(f"OK   {path}")
        browser.close()
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

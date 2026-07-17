#!/usr/bin/env python3
"""検証: PL Ratio(%) = 費目金額 ÷ 売上合計.

- 売上合計と支出金額がある月は ratio が xx.xx%
- 収入行(店舗/A/B/合計)も同じく Amount÷売上合計
- 売上なし / 金額なしは —
- 売上変更イベント後に再計算
"""

from __future__ import annotations

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
RENT = "exp_rent"


def seed(page) -> None:
    page.evaluate(
        """({ storeKey, expKey, year }) => {
          localStorage.clear();
          const store = {
            meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
            timeline: {
              dailySales: {
                [year + '-07-01']: 100000,
                [year + '-07-02']: 100000,
              },
              businessDays: {},
            },
            years: {
              [String(year)]: {
                year,
                status: 'open',
                plan: {},
                dailyExpenses: {},
                dailyIncome: {
                  sales_a: { [year + '-07-01']: 40000 },
                },
                dailyMeta: { memos: {}, flags: {}, weather: {} },
              },
            },
          };
          localStorage.setItem(storeKey, JSON.stringify(store));
          // July (month0=6): rent 20000 → ratio 20000/200000 = 10.00%
          localStorage.setItem(expKey, JSON.stringify({ [ 'exp_rent:6' ]: 20000 }));
        }""",
        {"storeKey": STORE_KEY, "expKey": EXP_KEY, "year": YEAR},
    )


def ratio_text(page, row_id: str, month0: int) -> str:
    return page.evaluate(
        """({ rowId, mi }) => {
          const cell = document.querySelector(
            '.pl-ratio-cell[data-row=\"' + rowId + '\"][data-month=\"' + mi + '\"] .pl-ratio-cell__text'
          );
          return cell ? String(cell.textContent || '').trim() : '';
        }""",
        {"rowId": row_id, "mi": month0},
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.goto(f"{url}?year={YEAR}", wait_until="load")
    seed(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => typeof window.__plRefreshRatios === 'function'",
        timeout=15000,
    )
    page.wait_for_timeout(200)
    page.evaluate(
        "() => { if (window.__plRefreshIncomeBlock) __plRefreshIncomeBlock(); "
        "if (window.__plRefreshExpenseAmounts) __plRefreshExpenseAmounts(); "
        "if (window.__plRefreshRatios) __plRefreshRatios(); }"
    )
    page.wait_for_timeout(100)

    july = ratio_text(page, RENT, 6)
    if july != "10.00%":
        problems.append(f"rent July ratio {july!r} want '10.00%'")

    jan = ratio_text(page, RENT, 0)
    if jan not in ("—", "\u2014", "-"):
        problems.append(f"rent Jan ratio should be em-dash, got {jan!r}")

    # Income ratios: total 200000, A 40000 → store 160000
    # store 80%, A 20%, B —, total 100%
    store_r = ratio_text(page, "store_sales", 6)
    if store_r != "80.00%":
        problems.append(f"store_sales July ratio {store_r!r} want '80.00%'")
    a_r = ratio_text(page, "sales_a", 6)
    if a_r != "20.00%":
        problems.append(f"sales_a July ratio {a_r!r} want '20.00%'")
    b_r = ratio_text(page, "sales_b", 6)
    if b_r not in ("—", "\u2014", "-"):
        problems.append(f"sales_b July ratio should be em-dash, got {b_r!r}")
    tot_r = ratio_text(page, "sales_total", 6)
    if tot_r != "100.00%":
        problems.append(f"sales_total July ratio {tot_r!r} want '100.00%'")

    # bump sales → ratio halves for rent; income ratios recompute
    page.evaluate(
        """({ key, year }) => {
          const store = JSON.parse(localStorage.getItem(key));
          store.timeline.dailySales[year + '-07-03'] = 200000;
          localStorage.setItem(key, JSON.stringify(store));
          document.dispatchEvent(new CustomEvent('kpi:dailySalesChanged', { detail: {} }));
          if (window.__plRefreshIncomeBlock) __plRefreshIncomeBlock();
          if (window.__plRefreshRatios) __plRefreshRatios();
        }""",
        {"key": STORE_KEY, "year": YEAR},
    )
    page.wait_for_timeout(100)
    july2 = ratio_text(page, RENT, 6)
    if july2 != "5.00%":
        problems.append(f"after sales bump rent July ratio {july2!r} want '5.00%'")
    # total now 400000, A still 40000 → store 360000 → 90% / 10% / 100%
    store_r2 = ratio_text(page, "store_sales", 6)
    if store_r2 != "90.00%":
        problems.append(f"after sales bump store ratio {store_r2!r} want '90.00%'")
    a_r2 = ratio_text(page, "sales_a", 6)
    if a_r2 != "10.00%":
        problems.append(f"after sales bump sales_a ratio {a_r2!r} want '10.00%'")
    tot_r2 = ratio_text(page, "sales_total", 6)
    if tot_r2 != "100.00%":
        problems.append(f"after sales bump sales_total ratio {tot_r2!r} want '100.00%'")

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

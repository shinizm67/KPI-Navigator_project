#!/usr/bin/env python3
"""検証: Daily Aggregate + Adjustment（日次合計 + 月次調整額）.

- PL daily 行の表示額 = MEP 月次合計 + 調整額
- 調整額は kpi-pl-expense-adjustments-v1:{year} に保存
- 日次入力 (dailyExpenses) は消えない
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
LINE = "exp_food_cost"
STORE_KEY = "kpiNavigator.kpiYearStore"
ADJ_KEY = f"kpi-pl-expense-adjustments-v1:{YEAR}"
JULY_DAILY = {f"{YEAR}-07-01": 1000, f"{YEAR}-07-10": 2000}  # sum 3000


def seed(page) -> None:
    page.evaluate(
        """({ storeKey, year, lineId, july }) => {
          localStorage.clear();
          localStorage.setItem(storeKey, JSON.stringify({
            meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
            timeline: { dailySales: { [year + '-07-01']: 100000 }, businessDays: {} },
            years: {
              [String(year)]: {
                year,
                status: 'open',
                plan: {},
                dailyExpenses: { [lineId]: july },
                dailyIncome: {},
                dailyMeta: { memos: {}, flags: {}, weather: {} },
              },
            },
          }));
        }""",
        {"storeKey": STORE_KEY, "year": YEAR, "lineId": LINE, "july": JULY_DAILY},
    )


def cell_int(page, month0: int):
    txt = page.evaluate(
        """({ lineId, m }) => {
          const cell = document.querySelector(
            '.pl-amt-cell--pl-daily-readonly[data-row="' + lineId +
            '"][data-month="' + m + '"] .pl-amt-cell__text'
          );
          return cell ? cell.textContent : null;
        }""",
        {"lineId": LINE, "m": month0},
    )
    if txt is None:
        return "MISSING"
    s = txt.strip()
    if s in ("", "—", "-", "\u2014"):
        return None
    # keep sign for negative adjustments
    cleaned = re.sub(r"[^\d-]", "", s)
    if cleaned in ("", "-"):
        return None
    return int(cleaned)


def daily_expense_sum(page) -> int:
    return page.evaluate(
        """({ key, year, lineId }) => {
          const store = JSON.parse(localStorage.getItem(key) || '{}');
          const rec = store.years && store.years[String(year)];
          const map = rec && rec.dailyExpenses && rec.dailyExpenses[lineId];
          if (!map) return 0;
          return Object.keys(map).reduce((s, iso) => s + (Number(map[iso]) || 0), 0);
        }""",
        {"key": STORE_KEY, "year": YEAR, "lineId": LINE},
    )


def adj_stored(page, month0: int):
    return page.evaluate(
        """({ key, lineId, m }) => {
          const map = JSON.parse(localStorage.getItem(key) || '{}');
          const v = map[lineId + ':' + m];
          return v == null ? null : Number(v);
        }""",
        {"key": ADJ_KEY, "lineId": LINE, "m": month0},
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.goto(f"{url}?year={YEAR}", wait_until="load")
    seed(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => typeof window.__plSetExpenseAdjustment === 'function' && "
        "typeof window.__plFillDailyExpenseRowsFromMep === 'function'",
        timeout=15000,
    )
    page.evaluate(
        "() => { if (window.__plFillDailyExpenseRowsFromMep) __plFillDailyExpenseRowsFromMep(); "
        "if (window.__plRefreshRatios) __plRefreshRatios(); }"
    )
    page.wait_for_timeout(80)

    if cell_int(page, 6) != 3000:
        problems.append(f"july before adj {cell_int(page, 6)!r} want 3000")

    page.evaluate(
        """({ lineId }) => {
          window.__plSetExpenseAdjustment(lineId, 6, -800);
          window.__plFillDailyExpenseRowsFromMep();
          if (window.__plRefreshRatios) __plRefreshRatios();
        }""",
        {"lineId": LINE},
    )
    page.wait_for_timeout(50)

    if cell_int(page, 6) != 2200:
        problems.append(f"july after adj {cell_int(page, 6)!r} want 2200")
    if adj_stored(page, 6) != -800:
        problems.append(f"stored adj {adj_stored(page, 6)!r} want -800")
    if daily_expense_sum(page) != 3000:
        problems.append(f"dailyExpenses changed to {daily_expense_sum(page)} (must stay 3000)")

    # clear adj → back to daily only
    page.evaluate(
        """({ lineId }) => {
          window.__plSetExpenseAdjustment(lineId, 6, 0);
          window.__plFillDailyExpenseRowsFromMep();
        }""",
        {"lineId": LINE},
    )
    page.wait_for_timeout(50)
    if cell_int(page, 6) != 3000:
        problems.append(f"july after clear adj {cell_int(page, 6)!r} want 3000")
    if adj_stored(page, 6) is not None:
        problems.append(f"adj key should be removed, got {adj_stored(page, 6)!r}")

    # modal path
    page.evaluate(
        """({ lineId }) => window.__plOpenExpenseAdjModal(lineId, 6)""",
        {"lineId": LINE},
    )
    page.wait_for_selector("#pl-expense-adj-modal:not([hidden])", timeout=5000)
    page.fill("#pl-expense-adj-input", "500")
    page.click('[data-pl-adj-action="confirm"]')
    page.wait_for_timeout(80)
    if cell_int(page, 6) != 3500:
        problems.append(f"july after modal adj {cell_int(page, 6)!r} want 3500")
    if adj_stored(page, 6) != 500:
        problems.append(f"modal stored adj {adj_stored(page, 6)!r} want 500")

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

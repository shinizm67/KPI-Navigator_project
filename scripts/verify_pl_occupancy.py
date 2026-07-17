#!/usr/bin/env python3
"""検証: PL 物件形態（賃貸=家賃 / 自持=償却資産税）の排他切替.

- 既定は賃貸 → exp_rent 表示、exp_depreciable_asset_tax 非表示
- 自持へ切替 → 償却資産税行のみ、localStorage plOccupancy=owned
- 賃貸へ戻す → 家賃行のみ。金額データは保持
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
OCC_KEY = "kpiNavigator.plOccupancy"
EXP_KEY = f"kpi-pl-expenses-v1:{YEAR}"
RENT = "exp_rent"
OWNED = "exp_depreciable_asset_tax"


def seed(page) -> None:
    page.evaluate(
        """({ storeKey, expKey, year }) => {
          localStorage.clear();
          localStorage.setItem(
            storeKey,
            JSON.stringify({
              meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
              timeline: { dailySales: {}, businessDays: {} },
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
            })
          );
          localStorage.setItem(
            expKey,
            JSON.stringify({ [ 'exp_rent:6' ]: 50000, [ 'exp_depreciable_asset_tax:6' ]: 12000 })
          );
        }""",
        {"storeKey": STORE_KEY, "expKey": EXP_KEY, "year": YEAR},
    )


def row_visible(page, line_id: str) -> bool:
    return page.evaluate(
        """(lineId) => {
          const row = document.querySelector(
            '#pl-expense-detail-data-body tr[data-line-id=\"' + lineId + '\"]'
          );
          return !!row;
        }""",
        line_id,
    )


def occupancy_value(page) -> str:
    return page.evaluate(
        """() => {
          const sel = document.querySelector('[data-pl-occupancy-select]');
          return sel ? String(sel.value || '') : '';
        }"""
    )


def stored_occupancy(page) -> str:
    return page.evaluate(
        """(key) => String(localStorage.getItem(key) || '')""",
        OCC_KEY,
    )


def amt_july(page, line_id: str) -> str:
    return page.evaluate(
        """(lineId) => {
          const el = document.querySelector(
            '[data-field="amount"][data-row=\"' +
              lineId +
              '\"][data-month="6"] .pl-amt-cell__text'
          );
          return el ? String(el.textContent || '').trim() : '';
        }""",
        line_id,
    )


def verify_page(page, url: str, lang: str) -> list[str]:
    errs: list[str] = []
    page.goto(url, wait_until="domcontentloaded")
    seed(page)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(700)
    page.evaluate(
        """() => {
          if (window.__plRefreshExpenseAmounts) __plRefreshExpenseAmounts();
        }"""
    )
    page.wait_for_timeout(200)

    if not page.locator("[data-pl-occupancy-select]").count():
        errs.append(f"{lang}: occupancy select missing")
        return errs

    if occupancy_value(page) != "rent":
        errs.append(f"{lang}: default select != rent ({occupancy_value(page)!r})")
    if stored_occupancy(page) not in ("", "rent"):
        # after first load sync may write 'rent'
        if stored_occupancy(page) != "rent":
            errs.append(f"{lang}: default storage {stored_occupancy(page)!r}")

    if not row_visible(page, RENT):
        errs.append(f"{lang}: rent row missing in default rent mode")
    if row_visible(page, OWNED):
        errs.append(f"{lang}: owned row should be hidden in rent mode")

    rent_amt = amt_july(page, RENT)
    if "50,000" not in rent_amt and "50000" not in rent_amt.replace(",", ""):
        errs.append(f"{lang}: rent July amount missing ({rent_amt!r})")

    page.select_option("[data-pl-occupancy-select]", "owned")
    page.wait_for_timeout(400)

    if occupancy_value(page) != "owned":
        errs.append(f"{lang}: select after switch != owned")
    if stored_occupancy(page) != "owned":
        errs.append(f"{lang}: storage after switch != owned ({stored_occupancy(page)!r})")
    if row_visible(page, RENT):
        errs.append(f"{lang}: rent row still visible in owned mode")
    if not row_visible(page, OWNED):
        errs.append(f"{lang}: owned row missing in owned mode")

    owned_amt = amt_july(page, OWNED)
    if "12,000" not in owned_amt and "12000" not in owned_amt.replace(",", ""):
        errs.append(f"{lang}: owned July amount missing ({owned_amt!r})")

    page.select_option("[data-pl-occupancy-select]", "rent")
    page.wait_for_timeout(400)

    if not row_visible(page, RENT):
        errs.append(f"{lang}: rent row missing after switch back")
    if row_visible(page, OWNED):
        errs.append(f"{lang}: owned row still visible after switch back")
    rent_amt2 = amt_july(page, RENT)
    if "50,000" not in rent_amt2 and "50000" not in rent_amt2.replace(",", ""):
        errs.append(f"{lang}: rent amount not preserved ({rent_amt2!r})")

    # API sanity
    api = page.evaluate(
        """() => ({
          get: typeof window.__plGetOccupancy === 'function' ? __plGetOccupancy() : null,
          set: typeof window.__plSetOccupancy === 'function',
        })"""
    )
    if api["get"] != "rent" or not api["set"]:
        errs.append(f"{lang}: occupancy API broken {api}")

    return errs


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: chromium not found at {EXE}", file=sys.stderr)
        return 2
    all_errs: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page()
        for path in PAGES:
            lang = "en" if "/en/" in str(path) else "ja"
            all_errs.extend(verify_page(page, path.resolve().as_uri(), lang))
        browser.close()
    if all_errs:
        print("FAIL")
        for e in all_errs:
            print(" -", e)
        return 1
    print("OK: PL occupancy select")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

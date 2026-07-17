#!/usr/bin/env python3
"""検証: PL L2 費目別参考予算（過去同月中央値 × 今月売上）.

- コーナーの +/- トグルを ON にしてから確認（既定は OFF）
- 過去年の同月 食材/売上 = 25% → 今月売上 200000 → 目安 50000
- 過去比率のない費目（家賃）には L2 を付けない
- 実績が目安を大きく超えると over クラス
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
FOOD = "exp_food_cost"
RENT = "exp_rent"
STORE_KEY = "kpiNavigator.kpiYearStore"


def seed(page) -> None:
    page.evaluate(
        """({ storeKey, year, food, rent }) => {
          localStorage.clear();
          const dailySales = {};
          // past July sales 100000 each year; food 25000 → 25%
          [year - 2, year - 1].forEach((y) => {
            dailySales[y + '-07-01'] = 50000;
            dailySales[y + '-07-02'] = 50000;
            localStorage.setItem(
              'kpi-pl-expenses-v1:' + y,
              JSON.stringify({ [food + ':6']: 25000 })
            );
          });
          // current July sales 200000
          dailySales[year + '-07-01'] = 100000;
          dailySales[year + '-07-02'] = 100000;
          localStorage.setItem(
            storeKey,
            JSON.stringify({
              meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
              timeline: { dailySales, businessDays: {} },
              years: {
                [String(year)]: {
                  year,
                  status: 'open',
                  plan: {},
                  dailyExpenses: {
                    [food]: {
                      [year + '-07-01']: 40000,
                      [year + '-07-02']: 40000,
                    },
                  },
                  dailyIncome: {},
                  dailyMeta: { memos: {}, flags: {}, weather: {} },
                },
              },
            })
          );
          // current July rent (fixed) — must not get L2
          localStorage.setItem(
            'kpi-pl-expenses-v1:' + year,
            JSON.stringify({ [rent + ':6']: 30000 })
          );
        }""",
        {"storeKey": STORE_KEY, "year": YEAR, "food": FOOD, "rent": RENT},
    )


def l2_meta(page, line_id: str, month0: int) -> dict:
    return page.evaluate(
        """({ lineId, mi }) => {
          const td = document.querySelector(
            '#pl-expense-detail-data-body .pl-amt-cell[data-row=\"' +
              lineId +
              '\"][data-month=\"' +
              mi +
              '\"]'
          );
          if (!td) return { missing: true };
          return {
            amount: td.getAttribute('data-pl-l2-amount'),
            rate: td.getAttribute('data-pl-l2-rate'),
            basis: td.getAttribute('data-pl-l2-basis'),
            has: td.classList.contains('pl-amt-cell--has-l2'),
            over: td.classList.contains('pl-amt-cell--over-l2'),
            hint: (td.querySelector('.pl-amt-cell__l2') || {}).textContent || '',
          };
        }""",
        {"lineId": line_id, "mi": month0},
    )


def verify_page(page, url: str, lang: str) -> list[str]:
    errs: list[str] = []
    page.goto(url, wait_until="domcontentloaded")
    seed(page)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(800)
    page.evaluate(
        """() => {
          if (window.__plRefreshExpenseAmounts) __plRefreshExpenseAmounts();
          if (window.__plRefreshIncomeBlock) __plRefreshIncomeBlock();
          if (typeof fillDailyExpenseRowsFromMep === 'function') fillDailyExpenseRowsFromMep();
          if (window.__plRefreshRatios) __plRefreshRatios();
          if (window.__plRefreshReferenceBudget) __plRefreshReferenceBudget();
        }"""
    )
    page.wait_for_timeout(300)
    # 目安は既定 OFF。コーナー +/- トグルを ON にする
    page.click("#pl-guide-toggle")
    page.wait_for_timeout(300)

    food = l2_meta(page, FOOD, 6)
    if food.get("missing"):
        errs.append(f"{lang}: food cell missing")
        return errs
    if not food.get("has") or food.get("amount") != "50000":
        errs.append(f"{lang}: food L2 amount {food} want 50000")
    if food.get("rate") not in ("25", "25.0", "25.00"):
        # attribute stores rounded rate * 100 / 100 → 25
        try:
            if abs(float(food.get("rate") or 0) - 25) > 0.05:
                errs.append(f"{lang}: food L2 rate {food.get('rate')!r} want ~25")
        except ValueError:
            errs.append(f"{lang}: food L2 rate {food.get('rate')!r}")
    if food.get("basis") != "same-month":
        errs.append(f"{lang}: food L2 basis {food.get('basis')!r}")
    # actual 80000 > 50000 * 1.05 → over
    if not food.get("over"):
        errs.append(f"{lang}: food should be over-l2 (actual 80k > guide 50k)")
    if "50000" not in food.get("hint", "").replace(",", "") and "50,000" not in food.get(
        "hint", ""
    ):
        # JA 目安 ¥50,000 / EN ~$50,000 depending on formatMoney
        hint_digits = "".join(ch for ch in food.get("hint", "") if ch.isdigit())
        if hint_digits != "50000":
            errs.append(f"{lang}: food hint {food.get('hint')!r}")

    rent = l2_meta(page, RENT, 6)
    if rent.get("missing"):
        errs.append(f"{lang}: rent cell missing")
    elif rent.get("has") or rent.get("amount"):
        errs.append(f"{lang}: rent has no past ratio → must not have L2 {rent}")

    jan = l2_meta(page, FOOD, 0)
    if jan.get("has"):
        errs.append(f"{lang}: Jan food should have no L2 without sales {jan}")

    return errs


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: chromium missing {EXE}", file=sys.stderr)
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
    print("OK: PL reference budget L2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

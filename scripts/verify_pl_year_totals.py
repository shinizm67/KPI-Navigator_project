#!/usr/bin/env python3
"""検証: PL 年計列 = 12ヶ月合計 / Ratio = 年計額÷年計売上合計.

- ヘッダ「年計」/「Annual」、Amount+Ratio 列が存在
- 収入・支出・営業日の年計が月合計と一致
- Ratio が年計売上を分母に算出
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
RENT = "exp_rent"


def parse_money(text: str) -> float | None:
    s = (text or "").strip()
    if not s or s in {"—", "-", "–"}:
        return None
    cleaned = re.sub(r"[^\d.-]", "", s)
    try:
        return float(cleaned)
    except ValueError:
        return None


def seed(page) -> None:
    page.evaluate(
        """({ storeKey, expKey, year }) => {
          localStorage.clear();
          const dailySales = {};
          // Jan: 100000, Jul: 200000 → year sales 300000
          dailySales[year + '-01-02'] = 100000;
          dailySales[year + '-07-01'] = 100000;
          dailySales[year + '-07-02'] = 100000;
          const store = {
            meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
            timeline: { dailySales, businessDays: {} },
            years: {
              [String(year)]: {
                year,
                status: 'open',
                plan: {},
                dailyExpenses: {},
                dailyIncome: {
                  sales_a: {
                    [year + '-01-02']: 30000,
                    [year + '-07-01']: 40000,
                  },
                },
                dailyMeta: { memos: {}, flags: {}, weather: {} },
              },
            },
          };
          localStorage.setItem(storeKey, JSON.stringify(store));
          // rent: Jan 10000 + Jul 20000 = 30000 year
          localStorage.setItem(
            expKey,
            JSON.stringify({ [ 'exp_rent:0' ]: 10000, [ 'exp_rent:6' ]: 20000 })
          );
        }""",
        {"storeKey": STORE_KEY, "expKey": EXP_KEY, "year": YEAR},
    )


def amt_text(page, row_id: str, month) -> str:
    return page.evaluate(
        """({ rowId, mi }) => {
          const sel =
            '[data-field="amount"][data-row="' +
            rowId +
            '"][data-month="' +
            mi +
            '"] .pl-amt-cell__text, ' +
            '.pl-month-cell[data-row="' +
            rowId +
            '"][data-month="' +
            mi +
            '"] .pl-month-cell__text';
          const el = document.querySelector(sel);
          return el ? String(el.textContent || '').trim() : '';
        }""",
        {"rowId": row_id, "mi": month},
    )


def ratio_text(page, row_id: str, month) -> str:
    return page.evaluate(
        """({ rowId, mi }) => {
          const el = document.querySelector(
            '.pl-ratio-cell[data-row="' +
              rowId +
              '"][data-month="' +
              mi +
              '"] .pl-ratio-cell__text'
          );
          return el ? String(el.textContent || '').trim() : '';
        }""",
        {"rowId": row_id, "mi": month},
    )


def sum_months(page, row_id: str) -> float:
    total = 0.0
    has = False
    for mi in range(12):
        v = parse_money(amt_text(page, row_id, mi))
        if v is None:
            continue
        total += v
        has = True
    return total if has else float("nan")


def verify_page(page, url: str, lang: str) -> list[str]:
    errs: list[str] = []
    page.goto(url, wait_until="domcontentloaded")
    seed(page)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(800)
    page.evaluate(
        """() => {
          if (window.__plRefreshIncomeBlock) __plRefreshIncomeBlock();
          if (window.__plRefreshExpenseAmounts) __plRefreshExpenseAmounts();
          if (window.__plRefreshRatios) __plRefreshRatios();
          if (window.__plRefreshYearTotals) __plRefreshYearTotals();
        }"""
    )
    page.wait_for_timeout(200)

    head = page.locator("#pl-month-head-year .pl-month-head__text")
    if head.count() != 1:
        errs.append(f"{lang}: year head missing")
    else:
        expected = "年計" if lang == "ja" else "Annual"
        got = head.inner_text().strip()
        if got != expected:
            errs.append(f"{lang}: year head {got!r} != {expected!r}")

    cols = page.evaluate(
        """() => {
          const tables = Array.from(
            document.querySelectorAll('table.pl-table--data')
          ).map((t) => ({
            id: t.id || '',
            amt: t.querySelectorAll('col.pl-col-amt').length,
            ratio: t.querySelectorAll('col.pl-col-ratio').length,
          }));
          return {
            tables,
            yearAmt: !!document.querySelector('[data-field="amount"][data-month="year"]'),
            yearRatio: !!document.querySelector('[data-field="ratio"][data-month="year"]'),
            yearFn: typeof window.__plRefreshYearTotals === 'function',
          };
        }"""
    )
    bad_tables = [t for t in cols["tables"] if t["amt"] != 13 or t["ratio"] != 13]
    if bad_tables:
        errs.append(f"{lang}: data tables colgroup not 13/13: {bad_tables}")
    if not cols["yearAmt"] or not cols["yearRatio"]:
        errs.append(f"{lang}: year amount/ratio cells missing")
    if not cols["yearFn"]:
        errs.append(f"{lang}: __plRefreshYearTotals missing")

    sales_year = parse_money(amt_text(page, "sales_total", "year"))
    sales_sum = sum_months(page, "sales_total")
    if sales_year is None or abs(sales_year - sales_sum) > 0.5:
        errs.append(f"{lang}: sales_total year {sales_year} != month sum {sales_sum}")
    if sales_year != 300000:
        errs.append(f"{lang}: sales_total year expected 300000 got {sales_year}")

    rent_year = parse_money(amt_text(page, RENT, "year"))
    rent_sum = sum_months(page, RENT)
    if rent_year is None or abs(rent_year - rent_sum) > 0.5:
        errs.append(f"{lang}: {RENT} year {rent_year} != month sum {rent_sum}")
    if rent_year != 30000:
        errs.append(f"{lang}: {RENT} year expected 30000 got {rent_year}")

    rent_ratio = ratio_text(page, RENT, "year")
    # 30000 / 300000 = 10.00%
    if rent_ratio != "10.00%":
        errs.append(f"{lang}: {RENT} year ratio {rent_ratio!r} != '10.00%'")

    sales_ratio = ratio_text(page, "sales_total", "year")
    if sales_ratio != "100.00%":
        errs.append(f"{lang}: sales_total year ratio {sales_ratio!r} != '100.00%'")

    biz = page.evaluate(
        """() => {
          const yearEl = document.querySelector('[data-pl-bizdays-month="year"] .pl-span-cell__text');
          let sum = 0;
          for (let i = 0; i < 12; i++) {
            const el = document.querySelector(
              '[data-pl-bizdays-month="' + i + '"] .pl-span-cell__text'
            );
            const n = Number(String(el && el.textContent || '').replace(/[^\\d.-]/g, ''));
            if (Number.isFinite(n)) sum += n;
          }
          return {
            year: yearEl ? String(yearEl.textContent || '').trim() : '',
            sum: String(sum),
          };
        }"""
    )
    if not biz["year"] or biz["year"] != biz["sum"]:
        errs.append(f"{lang}: bizdays year {biz['year']!r} != month sum {biz['sum']!r}")

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
            url = path.resolve().as_uri()
            all_errs.extend(verify_page(page, url, lang))
        browser.close()
    if all_errs:
        print("FAIL")
        for e in all_errs:
            print(" -", e)
        return 1
    print("OK: PL year totals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

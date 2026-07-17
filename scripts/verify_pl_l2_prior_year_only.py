#!/usr/bin/env python3
"""検証: L2 参考予算は「前年以前のデータがある時だけ」出す（一貫性・説明可能性優先）。

方針 B: 今年の他月は繁閑（季節性）を反映しないため目安の根拠にしない。
- ケース1: 今年のみ実績あり・過去年なし → 目安は出ない／行高も上げない
- ケース2: 前年に同費目の実績あり → 目安が出る（basis は過去実績系）
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
ELEC = "exp_electric"


def _sales(year: int):
    return [3000000, 2800000, 3200000, 3100000, 2900000, 3300000,
            3400000, 3500000, 3000000, 3100000, 3200000, 3600000]


def seed_current_only(page) -> None:
    page.evaluate(
        """({ year, elec }) => {
          localStorage.clear();
          const dailySales = {};
          const salesCur = [3000000,2800000,3200000,3100000,2900000,3300000,
                            3400000,3500000,3000000,3100000,3200000,3600000];
          salesCur.forEach((tot, mi) => {
            const mm = String(mi + 1).padStart(2, '0');
            dailySales[year + '-' + mm + '-10'] = Math.round(tot / 2);
            dailySales[year + '-' + mm + '-20'] = tot - Math.round(tot / 2);
          });
          const curMap = {};
          salesCur.forEach((s, mi) => { curMap[elec + ':' + mi] = Math.round(s * 0.03); });
          localStorage.setItem('kpi-pl-expenses-v1:' + year, JSON.stringify(curMap));
          localStorage.setItem('kpiNavigator.kpiYearStore', JSON.stringify({
            meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
            timeline: { dailySales, businessDays: {} },
            years: { [String(year)]: { year, status: 'open', plan: {},
              dailyExpenses: {}, dailyIncome: {}, dailyMeta: { memos: {}, flags: {}, weather: {} } } },
          }));
        }""",
        {"year": YEAR, "elec": ELEC},
    )


def seed_with_prior(page) -> None:
    page.evaluate(
        """({ year, elec }) => {
          localStorage.clear();
          const dailySales = {};
          const salesArr = [3000000,2800000,3200000,3100000,2900000,3300000,
                            3400000,3500000,3000000,3100000,3200000,3600000];
          [year, year - 1, year - 2].forEach((y) => {
            salesArr.forEach((tot, mi) => {
              const mm = String(mi + 1).padStart(2, '0');
              dailySales[y + '-' + mm + '-10'] = Math.round(tot / 2);
              dailySales[y + '-' + mm + '-20'] = tot - Math.round(tot / 2);
            });
          });
          // 前年・前々年に電気代 3% を投入（当年は入れない＝目安のみ確認）
          [year - 1, year - 2].forEach((y) => {
            const map = {};
            salesArr.forEach((s, mi) => { map[elec + ':' + mi] = Math.round(s * 0.03); });
            localStorage.setItem('kpi-pl-expenses-v1:' + y, JSON.stringify(map));
          });
          localStorage.setItem('kpiNavigator.kpiYearStore', JSON.stringify({
            meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
            timeline: { dailySales, businessDays: {} },
            years: { [String(year)]: { year, status: 'open', plan: {},
              dailyExpenses: {}, dailyIncome: {}, dailyMeta: { memos: {}, flags: {}, weather: {} } } },
          }));
        }""",
        {"year": YEAR, "elec": ELEC},
    )


def refresh(page) -> None:
    page.evaluate(
        """() => {
          if (window.__plRefreshExpenseAmounts) __plRefreshExpenseAmounts();
          if (typeof fillDailyExpenseRowsFromMep === 'function') fillDailyExpenseRowsFromMep();
          if (window.__plRefreshRatios) __plRefreshRatios();
          if (window.__plRefreshReferenceBudget) __plRefreshReferenceBudget();
        }"""
    )


def elec_meta(page, mi: int) -> dict:
    return page.evaluate(
        """({ lineId, mi }) => {
          const td = document.querySelector(
            '#pl-expense-detail-data-body .pl-amt-cell[data-row=\"' + lineId +
            '\"][data-month=\"' + mi + '\"]'
          );
          if (!td) return { missing: true };
          return { has: td.classList.contains('pl-amt-cell--has-l2'),
                   basis: td.getAttribute('data-pl-l2-basis') };
        }""",
        {"lineId": ELEC, "mi": mi},
    )


def verify_page(page, url: str, lang: str) -> list[str]:
    errs: list[str] = []

    # ケース1: 今年のみ → 目安は出ない
    page.goto(url, wait_until="domcontentloaded")
    seed_current_only(page)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(900)
    refresh(page)
    page.wait_for_timeout(200)
    page.click("#pl-guide-toggle")
    page.wait_for_timeout(400)
    s1 = page.evaluate(
        """() => ({
          has: document.querySelectorAll('#pl-expense-detail-data-body .pl-amt-cell--has-l2').length,
          hasData: document.body.classList.contains('pl-guide-has-data'),
        })"""
    )
    if s1["has"] != 0:
        errs.append(f"{lang}: 今年のみ実績で目安が出てしまう（前年のみ方針に反する）{s1}")
    if s1["hasData"]:
        errs.append(f"{lang}: 今年のみ実績で行高拡張フラグが付く {s1}")

    # ケース2: 前年あり → 目安が出る（過去実績基準）
    page.goto(url, wait_until="domcontentloaded")
    seed_with_prior(page)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(900)
    refresh(page)
    page.wait_for_timeout(200)
    page.click("#pl-guide-toggle")
    page.wait_for_timeout(400)
    jan = elec_meta(page, 0)
    if jan.get("missing"):
        errs.append(f"{lang}: electric Jan cell missing")
    elif not jan.get("has"):
        errs.append(f"{lang}: 前年データがあるのに目安が出ない {jan}")
    elif jan.get("basis") == "current-year":
        errs.append(f"{lang}: basis が current-year（撤去済みのはず）{jan}")

    return errs


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: chromium missing {EXE}", file=sys.stderr)
        return 2
    all_errs: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        for path in PAGES:
            lang = "en" if "/en/" in str(path) else "ja"
            all_errs.extend(verify_page(page, path.resolve().as_uri(), lang))
        browser.close()
    if all_errs:
        print("FAIL")
        for e in all_errs:
            print(" -", e)
        return 1
    print("OK: PL L2 prior-year-only（今年のみでは出さない／前年あれば出す）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

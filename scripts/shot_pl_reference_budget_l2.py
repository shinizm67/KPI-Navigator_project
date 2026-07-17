#!/usr/bin/env python3
"""L2 参考予算の見え方確認スクショ（テストデータ・本番データ非改変）。

過去年(2024/2025)の同月・費目比率を仕込み、当年売上に対する「目安」を描画。
出力: assets/shot_pl_l2_*.png
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app/profit/pl/index.html"
OUT_DIR = ROOT / "assets"
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)

YEAR = 2026


def seed(page) -> None:
    page.evaluate(
        """({ year }) => {
          localStorage.clear();
          const dailySales = {};
          function addMonthSales(y, monthTotals) {
            monthTotals.forEach((tot, mi) => {
              if (!tot) return;
              const mm = String(mi + 1).padStart(2, '0');
              // 2 日に分けて入れる（月合計 = tot）
              dailySales[y + '-' + mm + '-10'] = Math.round(tot / 2);
              dailySales[y + '-' + mm + '-20'] = tot - Math.round(tot / 2);
            });
          }
          // 各月の売上（万円規模、当年/過去年）
          const salesCur = [3000000, 2800000, 3200000, 3100000, 2900000, 3300000,
                            3400000, 3500000, 3000000, 3100000, 3200000, 3600000];
          const salesPast = [2800000, 2600000, 3000000, 2900000, 2700000, 3100000,
                             3200000, 3300000, 2800000, 2900000, 3000000, 3400000];
          addMonthSales(year, salesCur);
          addMonthSales(year - 1, salesPast);
          addMonthSales(year - 2, salesPast.map((v) => Math.round(v * 0.95)));

          // 過去年の費目別実績（比率が安定するように売上×比率で作る）
          const ratios = {
            exp_food_cost: 0.28,
            exp_drink_cost: 0.10,
            exp_variable_labor: 0.18,
            exp_electric: 0.03,
            exp_gas: 0.015,
            exp_water: 0.012,
          };
          [year - 1, year - 2].forEach((y) => {
            const base = y === year - 1 ? salesPast : salesPast.map((v) => Math.round(v * 0.95));
            const map = {};
            base.forEach((sales, mi) => {
              Object.keys(ratios).forEach((lineId) => {
                map[lineId + ':' + mi] = Math.round(sales * ratios[lineId]);
              });
            });
            localStorage.setItem('kpi-pl-expenses-v1:' + y, JSON.stringify(map));
          });

          // 当年の実績（monthly 行 electricity/gas/water を入力、food/drink は日次）
          const curMap = {};
          salesCur.forEach((sales, mi) => {
            curMap['exp_electric:' + mi] = Math.round(sales * 0.03);
            curMap['exp_gas:' + mi] = Math.round(sales * 0.02);   // 目安 1.5% 超 → over
            curMap['exp_water:' + mi] = Math.round(sales * 0.011);
          });
          localStorage.setItem('kpi-pl-expenses-v1:' + year, JSON.stringify(curMap));

          const dailyExpenses = {};
          const foodDaily = {};
          const drinkDaily = {};
          const laborDaily = {};
          salesCur.forEach((sales, mi) => {
            const mm = String(mi + 1).padStart(2, '0');
            // food 実績を目安(28%)より多めに → over 強調確認
            foodDaily[year + '-' + mm + '-10'] = Math.round(sales * 0.17);
            foodDaily[year + '-' + mm + '-20'] = Math.round(sales * 0.17);
            drinkDaily[year + '-' + mm + '-10'] = Math.round(sales * 0.05);
            drinkDaily[year + '-' + mm + '-20'] = Math.round(sales * 0.05);
            laborDaily[year + '-' + mm + '-10'] = Math.round(sales * 0.09);
            laborDaily[year + '-' + mm + '-20'] = Math.round(sales * 0.09);
          });
          dailyExpenses.exp_food_cost = foodDaily;
          dailyExpenses.exp_drink_cost = drinkDaily;
          dailyExpenses.exp_variable_labor = laborDaily;

          localStorage.setItem(
            'kpiNavigator.kpiYearStore',
            JSON.stringify({
              meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
              timeline: { dailySales, businessDays: {} },
              years: {
                [String(year)]: {
                  year,
                  status: 'open',
                  plan: {},
                  dailyExpenses,
                  dailyIncome: {},
                  dailyMeta: { memos: {}, flags: {}, weather: {} },
                },
              },
            })
          );
        }""",
        {"year": YEAR},
    )


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: chromium missing {EXE}", file=sys.stderr)
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(PAGE.resolve().as_uri(), wait_until="domcontentloaded")
        seed(page)
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        page.evaluate(
            """() => {
              if (window.__plRefreshExpenseAmounts) __plRefreshExpenseAmounts();
              if (window.__plRefreshIncomeBlock) __plRefreshIncomeBlock();
              if (typeof fillDailyExpenseRowsFromMep === 'function') fillDailyExpenseRowsFromMep();
              if (window.__plRefreshRatios) __plRefreshRatios();
              if (window.__plRefreshReferenceBudget) __plRefreshReferenceBudget();
            }"""
        )
        page.wait_for_timeout(600)

        full = OUT_DIR / "shot_pl_l2_full.png"
        page.screenshot(path=str(full))
        print("wrote", full)

        block = page.query_selector("#pl-expense-detail-block")
        if block:
            crop = OUT_DIR / "shot_pl_l2_expense_block.png"
            block.screenshot(path=str(crop))
            print("wrote", crop)

        # Count how many cells actually got a guideline
        stats = page.evaluate(
            """() => {
              const cells = document.querySelectorAll(
                '#pl-expense-detail-data-body .pl-amt-cell--has-l2'
              );
              const over = document.querySelectorAll(
                '#pl-expense-detail-data-body .pl-amt-cell--over-l2'
              );
              return { withL2: cells.length, over: over.length };
            }"""
        )
        print("L2 cells:", stats)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""費目別参考予算(L2) の +/- トグル検証（height 拡張・縮小型）。

確認項目:
  1. 既定は OFF（body に pl-guide-on なし・目安セルは非表示扱い）
  2. コーナー +/- を押すと ON（pl-guide-on 付与・目安セル出現・行高が増える）
  3. 変動費だけでなく固定費行にも目安が付く
  4. もう一度押すと OFF に戻り、行高が元へ縮む
  5. 状態が localStorage(kpiNavigator.plGuideOn) に保存される

副産物: assets/shot_pl_l2_off.png / shot_pl_l2_on.png（見え方確認用）
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
              dailySales[y + '-' + mm + '-10'] = Math.round(tot / 2);
              dailySales[y + '-' + mm + '-20'] = tot - Math.round(tot / 2);
            });
          }
          const salesCur = [3000000, 2800000, 3200000, 3100000, 2900000, 3300000,
                            3400000, 3500000, 3000000, 3100000, 3200000, 3600000];
          const salesPast = [2800000, 2600000, 3000000, 2900000, 2700000, 3100000,
                             3200000, 3300000, 2800000, 2900000, 3000000, 3400000];
          addMonthSales(year, salesCur);
          addMonthSales(year - 1, salesPast);
          addMonthSales(year - 2, salesPast.map((v) => Math.round(v * 0.95)));

          // 変動費 + 固定費(rent/labor 等) の過去比率
          const ratios = {
            exp_food_cost: 0.28,
            exp_drink_cost: 0.10,
            exp_variable_labor: 0.18,
            exp_electric: 0.03,
            exp_gas: 0.015,
            exp_water: 0.012,
            exp_rent: 0.08,
            exp_fixed_labor: 0.12,
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

          const curMap = {};
          salesCur.forEach((sales, mi) => {
            curMap['exp_electric:' + mi] = Math.round(sales * 0.03);
            curMap['exp_gas:' + mi] = Math.round(sales * 0.02);   // 目安 1.5% 超 → over
            curMap['exp_water:' + mi] = Math.round(sales * 0.011);
            curMap['exp_rent:' + mi] = Math.round(sales * 0.08);
            curMap['exp_fixed_labor:' + mi] = Math.round(sales * 0.14);  // 目安 12% 超 → over
          });
          localStorage.setItem('kpi-pl-expenses-v1:' + year, JSON.stringify(curMap));

          const dailyExpenses = {};
          const foodDaily = {};
          const drinkDaily = {};
          const laborDaily = {};
          salesCur.forEach((sales, mi) => {
            const mm = String(mi + 1).padStart(2, '0');
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


def refresh(page) -> None:
    page.evaluate(
        """() => {
          if (window.__plRefreshExpenseAmounts) __plRefreshExpenseAmounts();
          if (window.__plRefreshIncomeBlock) __plRefreshIncomeBlock();
          if (typeof fillDailyExpenseRowsFromMep === 'function') fillDailyExpenseRowsFromMep();
          if (window.__plRefreshRatios) __plRefreshRatios();
          if (window.__plRefreshReferenceBudget) __plRefreshReferenceBudget();
        }"""
    )


def sample_row_height(page) -> float:
    return page.evaluate(
        """() => {
          const tr = document.querySelector(
            '#pl-expense-detail-data-body tr[data-line-id]'
          );
          return tr ? tr.getBoundingClientRect().height : 0;
        }"""
    )


def guide_stats(page) -> dict:
    return page.evaluate(
        """() => {
          const on = document.body.classList.contains('pl-guide-on');
          const has = document.querySelectorAll(
            '#pl-expense-detail-data-body .pl-amt-cell--has-l2'
          ).length;
          const over = document.querySelectorAll(
            '#pl-expense-detail-data-body .pl-amt-cell--over-l2'
          ).length;
          // 目安セルのうち固定費バケットに属する数
          let fixedHas = 0;
          document
            .querySelectorAll('#pl-expense-detail-data-body .pl-amt-cell--has-l2')
            .forEach((td) => {
              const tr = td.closest('tr');
              if (tr && tr.getAttribute('data-bucket') === 'fixed') fixedHas += 1;
            });
          const hintVisible = (() => {
            const el = document.querySelector(
              '#pl-expense-detail-data-body .pl-amt-cell--has-l2 .pl-amt-cell__l2'
            );
            if (!el) return false;
            return getComputedStyle(el).display !== 'none';
          })();
          const pressed = (() => {
            const b = document.getElementById('pl-guide-toggle');
            return b ? b.getAttribute('aria-pressed') : null;
          })();
          const stored = localStorage.getItem('kpiNavigator.plGuideOn');
          return { on, has, over, fixedHas, hintVisible, pressed, stored };
        }"""
    )


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: chromium missing {EXE}", file=sys.stderr)
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(PAGE.resolve().as_uri(), wait_until="domcontentloaded")
        seed(page)
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(900)
        refresh(page)
        page.wait_for_timeout(400)

        # 1. 既定は OFF
        off = guide_stats(page)
        off_h = sample_row_height(page)
        if off["on"]:
            failures.append("既定で pl-guide-on が付いている")
        if off["hintVisible"]:
            failures.append("OFF で目安が表示されている")
        if off["pressed"] != "false":
            failures.append(f"OFF の aria-pressed が false でない: {off['pressed']}")
        block = page.query_selector("#pl-expense-detail-block")
        if block:
            block.screenshot(path=str(OUT_DIR / "shot_pl_l2_off.png"))

        # 2. トグル ON
        page.click("#pl-guide-toggle")
        page.wait_for_timeout(500)
        on = guide_stats(page)
        on_h = sample_row_height(page)
        if not on["on"]:
            failures.append("クリック後に pl-guide-on が付かない")
        if on["has"] <= 0:
            failures.append("ON でも目安セルが 0")
        if not on["hintVisible"]:
            failures.append("ON でも目安が非表示のまま")
        if on["pressed"] != "true":
            failures.append(f"ON の aria-pressed が true でない: {on['pressed']}")
        if on["stored"] != "1":
            failures.append(f"ON が localStorage に保存されない: {on['stored']}")
        # 3. 固定費行にも目安
        if on["fixedHas"] <= 0:
            failures.append("固定費行に目安が付いていない")
        # over 強調（gas/food/fixed_labor いずれか）
        if on["over"] <= 0:
            failures.append("over 強調が 1 つも無い")
        # 行高が拡張
        if not (on_h > off_h + 4):
            failures.append(f"ON で行高が十分拡張していない: off={off_h} on={on_h}")
        if block:
            block.screenshot(path=str(OUT_DIR / "shot_pl_l2_on.png"))

        # 4. もう一度で OFF
        page.click("#pl-guide-toggle")
        page.wait_for_timeout(500)
        off2 = guide_stats(page)
        off2_h = sample_row_height(page)
        if off2["on"]:
            failures.append("再クリックで OFF に戻らない")
        if off2["stored"] != "0":
            failures.append(f"OFF が localStorage に保存されない: {off2['stored']}")
        if not (abs(off2_h - off_h) <= 2):
            failures.append(f"OFF で行高が元に戻らない: {off_h} -> {off2_h}")

        print("OFF:", off, "h=", round(off_h, 1))
        print("ON :", on, "h=", round(on_h, 1))
        print("OFF2:", off2, "h=", round(off2_h, 1))
        browser.close()

    if failures:
        print("\nFAIL:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nPASS: L2 トグル（height 拡張・縮小型）は期待通り")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

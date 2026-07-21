"""PL Analyze block — Food/Drink Sales & Costs, Labor Share, FL Ratio.

Inserted inside the main PL IIFE (shares `plYear`, `formatMoney`, `parseMoney`).

- analyze_food_sales / analyze_drink_sales
    ← years.{Y}.dailyIncome.food_sales / drink_sales (MEP Confirm)
    Drink 欠落時は Store − Food（月次）で補完
- analyze_food_cost / analyze_drink_cost
    ← 支出明細セル exp_food_cost / exp_drink_cost の金額をコピー
- analyze_labor_employee / analyze_labor_pt / analyze_labor_total
    ← exp_fixed_labor（月次）/ exp_variable_labor（日次→月集計済み）
- analyze_monthly_food / analyze_monthly_labor / analyze_fl_total
    ← food+drink 原価 / labor 合計 / FL 合計
- Ratio(%) は既存 refreshPlRatios（÷ sales_total）に任せる
"""

from __future__ import annotations


def pl_analyze_client_js() -> str:
    return r"""
      var PL_ANALYZE_SALES_MAP = {
        analyze_food_sales: 'food_sales',
        analyze_drink_sales: 'drink_sales'
      };
      var PL_ANALYZE_COST_MAP = {
        analyze_food_cost: 'exp_food_cost',
        analyze_drink_cost: 'exp_drink_cost'
      };
      var PL_ANALYZE_LABOR_MAP = {
        analyze_labor_employee: 'exp_fixed_labor',
        analyze_labor_pt: 'exp_variable_labor'
      };

      function plAnalyzeEmptyMonthAgg() {
        return {
          totals: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          has: [
            false, false, false, false, false, false, false, false, false, false, false, false
          ]
        };
      }

      function plAnalyzeSumIsoMap(map, year) {
        var agg = plAnalyzeEmptyMonthAgg();
        if (!map || typeof map !== 'object') return agg;
        var yStr = String(year);
        Object.keys(map).forEach(function (iso) {
          if (!iso || iso.length < 7) return;
          if (iso.slice(0, 4) !== yStr) return;
          var mo = parseInt(iso.slice(5, 7), 10);
          if (!(mo >= 1 && mo <= 12)) return;
          var v = Number(map[iso]);
          if (!Number.isFinite(v)) return;
          agg.totals[mo - 1] += v;
          agg.has[mo - 1] = true;
        });
        return agg;
      }

      function plAnalyzeReadYearStore() {
        var gw = window.__KPI_DATA_GATEWAY;
        if (gw && typeof gw.getJson === 'function') {
          try {
            return gw.getJson('kpiNavigator.kpiYearStore');
          } catch (_e) {
            return null;
          }
        }
        try {
          var raw = localStorage.getItem('kpiNavigator.kpiYearStore');
          return raw ? JSON.parse(raw) : null;
        } catch (_e2) {
          return null;
        }
      }

      function plAnalyzeLoadStream(year, streamId) {
        var store = plAnalyzeReadYearStore();
        var rec = store && store.years && (store.years[year] || store.years[String(year)]);
        var di = rec && rec.dailyIncome && rec.dailyIncome[streamId];
        return plAnalyzeSumIsoMap(di, year);
      }

      function plAnalyzeSetAmount(rid, mi, sum, has) {
        var cell = document.querySelector(
          '[data-field="amount"][data-row="' + rid + '"][data-month="' + mi + '"] .pl-amt-cell__text'
        );
        if (!cell) return;
        cell.textContent = has ? formatMoney(sum) : '\u2014';
      }

      function plAnalyzeParseExpenseMonth(lineId, mi) {
        var cell = document.querySelector(
          '[data-field="amount"][data-row="' +
            lineId +
            '"][data-month="' +
            mi +
            '"] .pl-amt-cell__text'
        );
        if (!cell) return { value: 0, has: false };
        var raw = String(cell.textContent || '').replace(/\s+/g, ' ').trim();
        if (!raw || raw === '\u2014' || raw === '-') return { value: 0, has: false };
        var n =
          typeof parseMoney === 'function'
            ? parseMoney(raw)
            : Number(String(raw).replace(/[^\d.-]/g, ''));
        if (!Number.isFinite(n)) return { value: 0, has: false };
        return { value: n, has: true };
      }

      function plAnalyzeFillSales() {
        var food = plAnalyzeLoadStream(plYear, 'food_sales');
        var drink = plAnalyzeLoadStream(plYear, 'drink_sales');
        var storeTotals = null;
        var storeHas = null;
        if (typeof plIncomeStoreTotals !== 'undefined' && plIncomeStoreTotals) {
          storeTotals = plIncomeStoreTotals;
          storeHas = plIncomeStoreHas;
        }
        for (var mi = 0; mi < 12; mi++) {
          plAnalyzeSetAmount(
            'analyze_food_sales',
            mi,
            food.totals[mi],
            food.has[mi]
          );
          var dHas = !!drink.has[mi];
          var dVal = Number(drink.totals[mi]) || 0;
          if (!dHas && storeTotals && (food.has[mi] || (storeHas && storeHas[mi]))) {
            var storeVal = Number(storeTotals[mi]) || 0;
            var foodVal = Number(food.totals[mi]) || 0;
            dVal = Math.round(storeVal - foodVal);
            if (dVal < 0) dVal = 0;
            dHas = !!(storeHas && storeHas[mi]) || !!food.has[mi];
          }
          plAnalyzeSetAmount('analyze_drink_sales', mi, dVal, dHas);
        }
      }

      function plAnalyzeFillCosts() {
        Object.keys(PL_ANALYZE_COST_MAP).forEach(function (analyzeId) {
          var lineId = PL_ANALYZE_COST_MAP[analyzeId];
          for (var mi = 0; mi < 12; mi++) {
            var parsed = plAnalyzeParseExpenseMonth(lineId, mi);
            plAnalyzeSetAmount(analyzeId, mi, parsed.value, parsed.has);
          }
        });
      }

      /* Labor Share: 社員=月次固定人件費 / アルバイト=日次変動人件費（明細の月額） */
      function plAnalyzeFillLabor() {
        var laborByMonth = [];
        for (var mi = 0; mi < 12; mi++) {
          var emp = plAnalyzeParseExpenseMonth(PL_ANALYZE_LABOR_MAP.analyze_labor_employee, mi);
          var pt = plAnalyzeParseExpenseMonth(PL_ANALYZE_LABOR_MAP.analyze_labor_pt, mi);
          plAnalyzeSetAmount('analyze_labor_employee', mi, emp.value, emp.has);
          plAnalyzeSetAmount('analyze_labor_pt', mi, pt.value, pt.has);
          var total = (emp.has ? emp.value : 0) + (pt.has ? pt.value : 0);
          var has = emp.has || pt.has;
          plAnalyzeSetAmount('analyze_labor_total', mi, total, has);
          laborByMonth.push({ value: total, has: has });
        }
        return laborByMonth;
      }

      /* Food & Labor Ratio: 食材(フード+ドリンク仕入) + 人件費合計 */
      function plAnalyzeFillFlRatio(laborByMonth) {
        var labor =
          laborByMonth ||
          (function () {
            var out = [];
            for (var i = 0; i < 12; i++) {
              var emp = plAnalyzeParseExpenseMonth(PL_ANALYZE_LABOR_MAP.analyze_labor_employee, i);
              var pt = plAnalyzeParseExpenseMonth(PL_ANALYZE_LABOR_MAP.analyze_labor_pt, i);
              out.push({
                value: (emp.has ? emp.value : 0) + (pt.has ? pt.value : 0),
                has: emp.has || pt.has
              });
            }
            return out;
          })();
        for (var mi = 0; mi < 12; mi++) {
          var food = plAnalyzeParseExpenseMonth(PL_ANALYZE_COST_MAP.analyze_food_cost, mi);
          var drink = plAnalyzeParseExpenseMonth(PL_ANALYZE_COST_MAP.analyze_drink_cost, mi);
          var foodTotal = (food.has ? food.value : 0) + (drink.has ? drink.value : 0);
          var foodHas = food.has || drink.has;
          var lab = labor[mi] || { value: 0, has: false };
          plAnalyzeSetAmount('analyze_monthly_food', mi, foodTotal, foodHas);
          plAnalyzeSetAmount('analyze_monthly_labor', mi, lab.value, lab.has);
          plAnalyzeSetAmount(
            'analyze_fl_total',
            mi,
            foodTotal + lab.value,
            foodHas || lab.has
          );
        }
      }

      function refreshAnalyzeBlock() {
        plAnalyzeFillSales();
        plAnalyzeFillCosts();
        var laborByMonth = plAnalyzeFillLabor();
        plAnalyzeFillFlRatio(laborByMonth);
      }

      window.__plRefreshAnalyzeBlock = refreshAnalyzeBlock;
"""

"""PL bottom graph + expenses summary — live Fixed/Expected totals.

Inserted inside the main PL IIFE (shares `plYear`, `parseMoney`, `formatMoney`).
Does not write localStorage / MEP / expense maps (persist is elsewhere).

Priority for Fixed / Expected / Total:
  1) Sum expense-detail DOM by `data-bucket` (follows edits immediately)
  2) `__plInsight.monthMetrics` (after persist + resetCache)
  3) Existing summary cells
Sales for Profit / graph: sales_total cell, else Insight income.
"""

from __future__ import annotations


def pl_bottom_graph_data_client_js() -> str:
    return r"""
      /* PL-BOTTOM-GRAPH-DATA */
      function plGraphParseMoney(raw) {
        var s = String(raw == null ? '' : raw).replace(/\s+/g, ' ').trim();
        if (!s || s === '\u2014' || s === '-') return { value: 0, has: false };
        var n =
          typeof parseMoney === 'function'
            ? parseMoney(s)
            : Number(String(s).replace(/[^\d.-]/g, ''));
        if (!Number.isFinite(n)) return { value: 0, has: false };
        return { value: n, has: true };
      }

      function plGraphReadAmountCell(rowId, mi) {
        var cell = document.querySelector(
          '[data-field="amount"][data-row="' +
            rowId +
            '"][data-month="' +
            mi +
            '"] .pl-amt-cell__text'
        );
        if (!cell) return { value: 0, has: false };
        return plGraphParseMoney(cell.textContent);
      }

      function plGraphSetAmountCell(rowId, mi, value, has) {
        var cell = document.querySelector(
          '[data-field="amount"][data-row="' +
            rowId +
            '"][data-month="' +
            mi +
            '"] .pl-amt-cell__text'
        );
        if (!cell) return;
        if (!has) {
          cell.textContent =
            typeof formatMoney === 'function' ? formatMoney(0) : String(0);
          return;
        }
        cell.textContent =
          typeof formatMoney === 'function' ? formatMoney(value) : String(Math.round(value));
      }

      function plProfitSevLevels() {
        return [
          'pl-profit--ok',
          'pl-profit--sev-90',
          'pl-profit--sev-80',
          'pl-profit--sev-70',
          'pl-profit--sev-60',
          'pl-profit--sev-50',
          'pl-profit--sev-below'
        ];
      }

      /* Loss vs sales (break-even achievement): deeper red/orange as loss grows. */
      function plProfitSeverityClass(profit, sales) {
        if (!Number.isFinite(profit) || profit >= 0) return 'pl-profit--ok';
        var base = Number(sales);
        if (!Number.isFinite(base) || base <= 0) return 'pl-profit--sev-below';
        var ach = ((base + profit) / base) * 100;
        if (ach >= 90) return 'pl-profit--sev-90';
        if (ach >= 80) return 'pl-profit--sev-80';
        if (ach >= 70) return 'pl-profit--sev-70';
        if (ach >= 60) return 'pl-profit--sev-60';
        if (ach >= 50) return 'pl-profit--sev-50';
        return 'pl-profit--sev-below';
      }

      function plApplyProfitSeverityEl(el, profit, sales) {
        if (!el) return;
        var levels = plProfitSevLevels();
        for (var i = 0; i < levels.length; i++) el.classList.remove(levels[i]);
        if (profit == null || !Number.isFinite(Number(profit))) return;
        el.classList.add(plProfitSeverityClass(Number(profit), sales));
      }

      function plGraphSetProfitCell(mi, value, has, sales) {
        var cell = document.querySelector(
          '[data-row="profit"][data-month="' + mi + '"] .pl-month-cell__text'
        );
        if (!cell) return;
        if (!has) {
          cell.textContent = '\u2014';
          plApplyProfitSeverityEl(cell, null, 0);
          return;
        }
        cell.textContent =
          typeof formatMoney === 'function' ? formatMoney(value) : String(Math.round(value));
        plApplyProfitSeverityEl(cell, value, sales);
      }

      function plGraphMonthsFromInsight() {
        if (!window.__plInsight || typeof window.__plInsight.monthMetrics !== 'function') {
          return null;
        }
        var y =
          typeof plYear === 'number' && Number.isFinite(plYear)
            ? plYear
            : new Date().getFullYear();
        var out = [];
        for (var mi = 0; mi < 12; mi++) {
          var m = window.__plInsight.monthMetrics(y, mi) || {};
          var sales = Math.round(Number(m.income) || 0);
          var fixed = Math.round(Number(m.fixed) || 0);
          var expected = Math.round(Number(m.expected != null ? m.expected : m.variable) || 0);
          var expenses = Math.round(
            Number(m.expenses != null ? m.expenses : fixed + expected) || 0
          );
          out.push({
            sales: sales,
            expenses: expenses,
            fixed: fixed,
            expected: expected
          });
        }
        return out;
      }

      /* Fixed = sum(bucket=fixed), Expected = sum(bucket=variable) from detail pane. */
      function plGraphMonthsFromDetailDom() {
        var body = document.getElementById('pl-expense-detail-data-body');
        if (!body) return null;
        var rows = body.querySelectorAll('tr[data-line-id][data-bucket]');
        if (!rows.length) return null;
        var insight = plGraphMonthsFromInsight();
        var out = [];
        for (var mi = 0; mi < 12; mi++) {
          var fixed = 0;
          var expected = 0;
          for (var i = 0; i < rows.length; i++) {
            var tr = rows[i];
            var bucket = tr.getAttribute('data-bucket') || 'variable';
            var lineId = tr.getAttribute('data-line-id') || '';
            var textEl = tr.querySelector(
              '.pl-amt-cell[data-field="amount"][data-month="' +
                mi +
                '"] .pl-amt-cell__text'
            );
            if (!textEl && lineId) {
              textEl = body.querySelector(
                '.pl-amt-cell[data-field="amount"][data-row="' +
                  lineId +
                  '"][data-month="' +
                  mi +
                  '"] .pl-amt-cell__text'
              );
            }
            var parsed = plGraphParseMoney(textEl && textEl.textContent);
            if (!parsed.has) continue;
            if (bucket === 'fixed') fixed += parsed.value;
            else expected += parsed.value;
          }
          fixed = Math.round(fixed);
          expected = Math.round(expected);
          var salesCell = plGraphReadAmountCell('sales_total', mi);
          var sales = salesCell.has
            ? Math.round(salesCell.value)
            : insight && insight[mi]
              ? Math.round(Number(insight[mi].sales) || 0)
              : 0;
          out.push({
            sales: sales,
            expenses: fixed + expected,
            fixed: fixed,
            expected: expected
          });
        }
        return out;
      }

      function plGraphMonthsFromSummaryDom() {
        var out = [];
        for (var mi = 0; mi < 12; mi++) {
          var salesCell = plGraphReadAmountCell('sales_total', mi);
          var fixedCell = plGraphReadAmountCell('expense_fixed', mi);
          var expectedCell = plGraphReadAmountCell('expense_expected', mi);
          var totalCell = plGraphReadAmountCell('expenses_total', mi);
          var sales = salesCell.has ? Math.round(salesCell.value) : 0;
          var fixed = fixedCell.has ? Math.round(fixedCell.value) : 0;
          var expected = expectedCell.has ? Math.round(expectedCell.value) : 0;
          var expenses = totalCell.has
            ? Math.round(totalCell.value)
            : fixed + expected;
          out.push({
            sales: sales,
            expenses: expenses,
            fixed: fixed,
            expected: expected
          });
        }
        return out;
      }

      function plGraphCollectMonths() {
        var fromDetail = plGraphMonthsFromDetailDom();
        if (fromDetail) return fromDetail;
        var fromInsight = plGraphMonthsFromInsight();
        if (fromInsight) return fromInsight;
        return plGraphMonthsFromSummaryDom();
      }

      function plGraphApplyExpensesSummary(months) {
        if (!months) {
          for (var z = 0; z < 12; z++) {
            plGraphSetAmountCell('expense_fixed', z, 0, true);
            plGraphSetAmountCell('expense_expected', z, 0, true);
            plGraphSetAmountCell('expenses_total', z, 0, true);
            plGraphSetProfitCell(z, 0, false);
          }
          return;
        }
        for (var mi = 0; mi < 12; mi++) {
          var m = months[mi] || {};
          var fixed = Math.round(Number(m.fixed) || 0);
          var expected = Math.round(Number(m.expected) || 0);
          var expenses = Math.round(
            Number(m.expenses != null ? m.expenses : fixed + expected) || 0
          );
          var sales = Math.round(Number(m.sales) || 0);
          var has = !!(fixed || expected || expenses || sales);
          plGraphSetAmountCell('expense_fixed', mi, fixed, true);
          plGraphSetAmountCell('expense_expected', mi, expected, true);
          plGraphSetAmountCell('expenses_total', mi, expenses, true);
          plGraphSetProfitCell(mi, sales - expenses, has, sales);
        }
      }

      function refreshExpensesSummaryBlock() {
        plGraphApplyExpensesSummary(plGraphCollectMonths());
      }

      function refreshPlBottomGraph() {
        var months = plGraphCollectMonths();
        plGraphApplyExpensesSummary(months);
        if (typeof window.plGraphRender !== 'function') return;
        if (!months) return;
        window.plGraphRender(months);
      }

      window.__plRefreshBottomGraph = refreshPlBottomGraph;
      window.__plRefreshExpensesSummary = refreshExpensesSummaryBlock;
      window.__plApplyProfitSeverityEl = plApplyProfitSeverityEl;
      window.__plProfitSeverityClass = plProfitSeverityClass;
"""

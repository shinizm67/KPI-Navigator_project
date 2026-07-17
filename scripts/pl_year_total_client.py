"""PL year-total column — sum of 12 months (Amount + Ratio).

Inserted inside the main PL IIFE (shares `parseMoney`, `formatMoney`, `plYear`).
Year ratio denominator = annual sum of Total Sales amounts.
"""

from __future__ import annotations


def pl_year_total_client_js() -> str:
    return r"""
      function plYearParseAmountText(raw) {
        var s = String(raw || '').replace(/\s+/g, ' ').trim();
        if (!s || s === '\u2014' || s === '-') return { value: 0, has: false };
        var n = typeof parseMoney === 'function' ? parseMoney(s) : Number(String(s).replace(/[^\d.-]/g, ''));
        if (!Number.isFinite(n)) return { value: 0, has: false };
        return { value: n, has: true };
      }

      function plYearSumRowAmounts(rowId) {
        var sum = 0;
        var has = false;
        for (var mi = 0; mi < 12; mi++) {
          var cell =
            document.querySelector(
              '[data-field="amount"][data-row="' + rowId + '"][data-month="' + mi + '"]'
            ) ||
            document.querySelector(
              '.pl-month-cell[data-row="' + rowId + '"][data-month="' + mi + '"]'
            );
          if (!cell) continue;
          var span =
            cell.querySelector('.pl-amt-cell__text, .pl-month-cell__text, .pl-span-cell__text') ||
            cell;
          var parsed = plYearParseAmountText(span.textContent);
          if (!parsed.has) continue;
          sum += parsed.value;
          has = true;
        }
        return { sum: Math.round(sum), has: has };
      }

      function plYearSalesTotal() {
        return plYearSumRowAmounts('sales_total');
      }

      function formatPlYearRatioPct(n) {
        if (!Number.isFinite(n)) return '\u2014';
        var rounded = Math.round(n * 100) / 100;
        return rounded.toFixed(2) + '%';
      }

      function refreshPlYearTotals() {
        var sales = plYearSalesTotal();

        var bizYearCell = document.querySelector('[data-pl-bizdays-month="year"] .pl-span-cell__text');
        if (bizYearCell) {
          var bizSum = 0;
          var bizHas = false;
          for (var bmi = 0; bmi < 12; bmi++) {
            var bcell = document.querySelector(
              '[data-pl-bizdays-month="' + bmi + '"] .pl-span-cell__text'
            );
            if (!bcell) continue;
            var bn = Number(String(bcell.textContent || '').replace(/[^\d.-]/g, ''));
            if (!Number.isFinite(bn)) continue;
            bizSum += bn;
            bizHas = true;
          }
          bizYearCell.textContent = bizHas ? String(bizSum) : '';
        }

        document
          .querySelectorAll('[data-field="amount"][data-month="year"]')
          .forEach(function (amtTd) {
            var rowId = amtTd.getAttribute('data-row');
            if (!rowId) return;
            var span = amtTd.querySelector('.pl-amt-cell__text');
            if (!span) return;
            var agg = plYearSumRowAmounts(rowId);
            span.textContent = agg.has
              ? typeof formatMoney === 'function'
                ? formatMoney(agg.sum)
                : String(agg.sum)
              : '\u2014';
            var ratioTd = amtTd.nextElementSibling;
            if (
              !ratioTd ||
              ratioTd.getAttribute('data-field') !== 'ratio' ||
              ratioTd.getAttribute('data-month') !== 'year'
            ) {
              return;
            }
            var ratioSpan = ratioTd.querySelector('.pl-ratio-cell__text');
            if (!ratioSpan) return;
            if (!agg.has || !sales.has || !(sales.sum > 0)) {
              ratioSpan.textContent = '\u2014';
              return;
            }
            ratioSpan.textContent = formatPlYearRatioPct((agg.sum / sales.sum) * 100);
          });

        document.querySelectorAll('.pl-month-cell[data-month="year"]').forEach(function (td) {
          var rowId = td.getAttribute('data-row');
          if (!rowId) return;
          var span = td.querySelector('.pl-month-cell__text');
          if (!span) return;
          var agg = plYearSumRowAmounts(rowId);
          span.textContent = agg.has
            ? typeof formatMoney === 'function'
              ? formatMoney(agg.sum)
              : String(agg.sum)
            : '\u2014';
        });
      }

      window.__plRefreshYearTotals = refreshPlYearTotals;
"""

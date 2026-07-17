"""PL Ratio(%) — fill right-hand ratio cells as amount ÷ Total Sales.

Inserted inside the main PL IIFE (shares `parseMoney`, `plYear`).
Denominator = monthly Total Sales (`data-row="sales_total"` amount text).
Empty / missing sales or amount → "—".
"""

from __future__ import annotations


def pl_ratio_client_js() -> str:
    return r"""
      function formatPlRatioPct(n) {
        if (!Number.isFinite(n)) return '\u2014';
        var rounded = Math.round(n * 100) / 100;
        return rounded.toFixed(2) + '%';
      }

      function plRatioParseCellAmount(cell) {
        if (!cell) return { value: 0, has: false };
        var span =
          cell.querySelector('.pl-amt-cell__text, .pl-month-cell__text, .pl-span-cell__text') ||
          cell;
        var raw = String(span.textContent || '').replace(/\s+/g, ' ').trim();
        if (!raw || raw === '\u2014' || raw === '-') return { value: 0, has: false };
        var n = typeof parseMoney === 'function' ? parseMoney(raw) : Number(String(raw).replace(/[^\d.-]/g, ''));
        if (!Number.isFinite(n)) return { value: 0, has: false };
        return { value: n, has: true };
      }

      function plRatioSalesTotalsByMonth() {
        var out = [];
        for (var mi = 0; mi < 12; mi++) {
          var cell =
            document.querySelector(
              '[data-field="amount"][data-row="sales_total"][data-month="' + mi + '"]'
            ) ||
            document.querySelector(
              '.pl-month-cell[data-row="sales_total"][data-month="' + mi + '"]'
            );
          out[mi] = plRatioParseCellAmount(cell);
        }
        return out;
      }

      function refreshPlRatios() {
        var salesByMonth = plRatioSalesTotalsByMonth();
        document.querySelectorAll('.pl-ratio-cell[data-field="ratio"]').forEach(function (ratioCell) {
          var mi = Number(ratioCell.getAttribute('data-month'));
          if (!Number.isFinite(mi) || mi < 0 || mi > 11) return;
          var span = ratioCell.querySelector('.pl-ratio-cell__text');
          if (!span) return;
          var amtTd = ratioCell.previousElementSibling;
          if (!amtTd || amtTd.getAttribute('data-field') !== 'amount') {
            span.textContent = '\u2014';
            return;
          }
          var amt = plRatioParseCellAmount(amtTd);
          var sales = salesByMonth[mi];
          if (!amt.has || !sales.has || !(sales.value > 0)) {
            span.textContent = '\u2014';
            return;
          }
          span.textContent = formatPlRatioPct((amt.value / sales.value) * 100);
        });
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
      }

      window.__plRefreshRatios = refreshPlRatios;
"""

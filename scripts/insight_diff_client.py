"""Insight overlay — target-vs-actual Difference rows + Graph1 tooltip diff."""

from __future__ import annotations

INSIGHT_DIFF_JS_MARKER = "/* KPI-INSIGHT-TW-DIFF */"
INSIGHT_DIFF_JS_END = "/* END KPI-INSIGHT-TW-DIFF */"

INSIGHT_FILL_OLD = """      function fill(iso) {
        iso = iso || resolveIso();
        if (dateBtnEl) dateBtnEl.textContent = fmtDate(iso);
        if (todayBtnEl) todayBtnEl.hidden = iso === getTodayIso();
        if (dateInputEl) dateInputEl.value = iso;
      }"""

INSIGHT_FILL_NEW = """      function fill(iso) {
        iso = iso || resolveIso();
        if (dateBtnEl) dateBtnEl.textContent = fmtDate(iso);
        if (todayBtnEl) todayBtnEl.hidden = iso === getTodayIso();
        if (dateInputEl) dateInputEl.value = iso;
        try {
          if (typeof window.renderInsightTwDiffs === 'function') {
            window.renderInsightTwDiffs(iso);
          }
        } catch (_insightDiffErr) {}
      }"""

GRAPH1_DIFF_OLD = """          var diffEl = tooltipEl.querySelector('[data-field="diff"]');
          if (diffEl) diffEl.textContent = formatDetailMoney(diff);"""

GRAPH1_DIFF_NEW = """          var diffEl = tooltipEl.querySelector('[data-field="diff"]');
          if (diffEl) {
            if (typeof window.applyInsightTwDiffEl === 'function') {
              diffEl.textContent =
                typeof window.__twFmtDiff === 'function'
                  ? window.__twFmtDiff(sales, tgt)
                  : formatDetailMoney(diff);
              window.applyInsightTwDiffEl(diffEl, sales, tgt);
            } else {
              diffEl.textContent = formatDetailMoney(diff);
            }
          }"""

GRAPH1_DIFF_ANNUAL_OLD = """          var diffEl = tooltipEl.querySelector('[data-field="diff"]');
          if (diffEl) diffEl.textContent = formatDetailMoney(diff);
          var achEl = tooltipEl.querySelector('[data-field="achievement"]');
          if (achEl) achEl.textContent = pct.toFixed(1) + '%';

          var left = hit.x + CFG.tooltipOffset;
          var top = hit.y - CFG.tooltipH - CFG.tooltipOffset;
          if (left + CFG.tooltipW > 965) left = hit.x - CFG.tooltipW - CFG.tooltipOffset;
          if (left < 0) left = CFG.tooltipOffset;
          if (top < 0) top = hit.y + CFG.tooltipOffset;
          if (top + CFG.tooltipH > 618) top = Math.max(0, 618 - CFG.tooltipH - CFG.tooltipOffset);

          tooltipEl.style.left = left + 'px';
          tooltipEl.style.top = top + 'px';
          tooltipEl.classList.add('is-visible');
          tooltipEl.removeAttribute('hidden');
        }

        function onHoverMove(ev) {
          var state = frame.__trendChartState;
          if (!state) {
            hideHoverUi();
            return;
          }
          var pt = clientToSvg(ev);
          var hit = hitTest(pt.x, pt.y, state);
          if (!hit) {
            hideHoverUi();
            return;
          }
          showHoverUi(hit, state);
        }

        function placeEndpoint(el, pts, value) {"""

INSIGHT_OVERLAY_IIFE = "      var root = document.getElementById('insight-overlay');"


def insight_diff_js() -> str:
    return f"""    {INSIGHT_DIFF_JS_MARKER}
    (function () {{
      var DASH = '—';

      function fmtInsightMoney(n) {{
        if (typeof window.__twFmtMoney === 'function') return window.__twFmtMoney(n);
        if (n == null || !isFinite(Number(n))) return DASH;
        var isJa = document.documentElement.getAttribute('lang') === 'ja';
        var v = Math.round(Number(n));
        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');
      }}

      function twDiffLevels() {{
        if (window.__twDiffLevels && window.__twDiffLevels.length) return window.__twDiffLevels;
        return [
          'tw-diff--win',
          'tw-diff--neutral',
          'tw-diff--sev-90',
          'tw-diff--sev-80',
          'tw-diff--sev-70',
          'tw-diff--sev-60',
          'tw-diff--sev-50',
          'tw-diff--sev-below',
        ];
      }}

      window.applyInsightTwDiffEl = function (el, actual, target) {{
        if (!el) return;
        var levels = twDiffLevels();
        for (var i = 0; i < levels.length; i++) el.classList.remove(levels[i]);
        if (typeof window.__twDiffSeverityClass !== 'function') return;
        el.classList.add(window.__twDiffSeverityClass(actual, target));
      }};

      function setSalesSummaryRow(rows, rowIndex, valueEl, text, diffMeta) {{
        if (!rows[rowIndex] || !valueEl) return;
        valueEl.textContent = text;
        if (diffMeta) window.applyInsightTwDiffEl(valueEl, diffMeta.actual, diffMeta.target);
        else {{
          var levels = twDiffLevels();
          for (var i = 0; i < levels.length; i++) valueEl.classList.remove(levels[i]);
        }}
      }}

      function patchDailyKpiBlock(block, sales, target, hasPlan) {{
        var rows = block.querySelectorAll('.insight-daily-kpi__row');
        var salesEl = rows[0] && rows[0].querySelector('.insight-daily-kpi__value');
        var targetEl = rows[1] && rows[1].querySelector('.insight-daily-kpi__value');
        var diffEl = rows[2] && rows[2].querySelector('.insight-daily-kpi__value');
        setSalesSummaryRow(rows, 0, salesEl, hasPlan ? fmtInsightMoney(sales) : DASH, null);
        setSalesSummaryRow(rows, 1, targetEl, hasPlan ? fmtInsightMoney(target) : DASH, null);
        setSalesSummaryRow(
          rows,
          2,
          diffEl,
          hasPlan && typeof window.__twFmtDiff === 'function'
            ? window.__twFmtDiff(sales, target)
            : DASH,
          hasPlan ? {{ actual: Number(sales), target: Number(target) }} : null
        );
      }}

      function patchMonthlySummaryBlock(block, sales, target, hasPlan) {{
        var rows = block.querySelectorAll('.insight-monthly-sales-summary__row');
        var salesEl = rows[0] && rows[0].querySelector('.insight-monthly-sales-summary__value');
        var targetEl = rows[1] && rows[1].querySelector('.insight-monthly-sales-summary__value');
        var diffEl = rows[2] && rows[2].querySelector('.insight-monthly-sales-summary__value');
        setSalesSummaryRow(rows, 0, salesEl, fmtInsightMoney(sales), null);
        setSalesSummaryRow(rows, 1, targetEl, hasPlan ? fmtInsightMoney(target) : DASH, null);
        setSalesSummaryRow(
          rows,
          2,
          diffEl,
          hasPlan && typeof window.__twFmtDiff === 'function'
            ? window.__twFmtDiff(sales, target)
            : DASH,
          hasPlan ? {{ actual: Number(sales), target: Number(target) }} : null
        );
      }}

      function patchAnnualSummaryBlock(block, sales, target, hasPlan) {{
        var rows = block.querySelectorAll('.insight-annual-sales-summary__row');
        var salesEl = rows[0] && rows[0].querySelector('.insight-annual-sales-summary__value');
        var targetEl = rows[1] && rows[1].querySelector('.insight-annual-sales-summary__value');
        var diffEl = rows[2] && rows[2].querySelector('.insight-annual-sales-summary__value');
        setSalesSummaryRow(rows, 0, salesEl, fmtInsightMoney(sales), null);
        setSalesSummaryRow(rows, 1, targetEl, hasPlan ? fmtInsightMoney(target) : DASH, null);
        setSalesSummaryRow(
          rows,
          2,
          diffEl,
          hasPlan && typeof window.__twFmtDiff === 'function'
            ? window.__twFmtDiff(sales, target)
            : DASH,
          hasPlan ? {{ actual: Number(sales), target: Number(target) }} : null
        );
      }}

      window.renderInsightTwDiffs = function (iso) {{
        var root = document.getElementById('insight-overlay');
        if (!root) return;
        var compute =
          typeof window.__computeTwMetricsForIso === 'function'
            ? window.__computeTwMetricsForIso
            : null;
        var m = compute ? compute(iso) : null;

        root.querySelectorAll('.insight-daily-kpi').forEach(function (block) {{
          if (!m) {{
            patchDailyKpiBlock(block, NaN, NaN, false);
            return;
          }}
          var hasDailyPlan = m.isBusinessToday && m.dailyTarget != null;
          patchDailyKpiBlock(
            block,
            m.dailySales,
            m.dailyTarget,
            hasDailyPlan
          );
        }});

        root.querySelectorAll('.insight-monthly-sales-summary').forEach(function (block) {{
          if (!m) {{
            patchMonthlySummaryBlock(block, NaN, NaN, false);
            return;
          }}
          patchMonthlySummaryBlock(block, m.mtdA, m.mtdT, m.hasPlan);
        }});

        root.querySelectorAll('.insight-annual-sales-summary').forEach(function (block) {{
          if (!m) {{
            patchAnnualSummaryBlock(block, NaN, NaN, false);
            return;
          }}
          patchAnnualSummaryBlock(block, m.ytdA, m.ytdT, m.hasPlan);
        }});
      }};

      document.addEventListener('annual:dailyDateChanged', function () {{
        var root = document.getElementById('insight-overlay');
        if (!root || root.hidden) return;
        var iso =
          window.__ANNUAL_DATA &&
          window.__ANNUAL_DATA.daily &&
          window.__ANNUAL_DATA.daily.selectedDate;
        if (iso && typeof window.renderInsightTwDiffs === 'function') {{
          window.renderInsightTwDiffs(iso);
        }}
      }});
    }})();
    {INSIGHT_DIFF_JS_END}"""

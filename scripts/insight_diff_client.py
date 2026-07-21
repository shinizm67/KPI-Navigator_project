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
        window.__INSIGHT_SELECTED_ISO = iso;
        try {
          if (typeof window.renderInsightTwDiffs === 'function') {
            window.renderInsightTwDiffs(iso);
          }
        } catch (_insightDiffErr) {}
        try {
          document.dispatchEvent(new CustomEvent('insight:dateChanged', { detail: { iso: iso } }));
        } catch (_insightDateErr) {}
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

      function patchAnnualSalesSummaryProgressRows(block, m) {{
        var rows = block.querySelectorAll('.insight-annual-sales-summary__row');
        var bdEl = rows[4] && rows[4].querySelector('.insight-annual-sales-summary__value');
        var dailyEl = rows[5] && rows[5].querySelector('.insight-annual-sales-summary__value');
        if (!m) {{
          if (bdEl) bdEl.textContent = DASH;
          if (dailyEl) dailyEl.textContent = DASH;
          return;
        }}
        if (bdEl) bdEl.textContent = fmtInsightCount(m.yearRemainingBD);
        if (dailyEl) {{
          dailyEl.textContent =
            m.hasPlan && m.annualDailyNeed != null
              ? fmtInsightMoney(m.annualDailyNeed)
              : DASH;
        }}
      }}

      function fmtInsightGapPct(actual, target) {{
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return DASH;
        return Math.round(((actual - target) / target) * 100) + '%';
      }}

      function patchAnnualCurrentProgressBlock(block, m) {{
        var rows = block.querySelectorAll('.insight-annual-current-progress__row');
        var ytdTEl = rows[0] && rows[0].querySelector('.insight-annual-current-progress__value');
        var gapEl = rows[1] && rows[1].querySelector('.insight-annual-current-progress__value');
        var achEl = rows[2] && rows[2].querySelector('.insight-annual-current-progress__value');
        var gapPctEl = rows[3] && rows[3].querySelector('.insight-annual-current-progress__value');
        if (!m) {{
          if (ytdTEl) ytdTEl.textContent = DASH;
          if (gapEl) {{
            gapEl.textContent = DASH;
            window.applyInsightTwDiffEl(gapEl, NaN, NaN);
          }}
          if (achEl) achEl.textContent = DASH;
          if (gapPctEl) gapPctEl.textContent = DASH;
          return;
        }}
        if (ytdTEl) ytdTEl.textContent = m.hasPlan ? fmtInsightMoney(m.ytdT) : DASH;
        if (gapEl) {{
          gapEl.textContent =
            m.hasPlan && typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(m.ytdA, m.ytdT)
              : DASH;
          if (m.hasPlan) window.applyInsightTwDiffEl(gapEl, m.ytdA, m.ytdT);
          else window.applyInsightTwDiffEl(gapEl, NaN, NaN);
        }}
        if (achEl) achEl.textContent = m.hasPlan ? fmtInsightAchPct(m.ytdA, m.ytdT) : DASH;
        if (gapPctEl) {{
          gapPctEl.textContent = m.hasPlan ? fmtInsightGapPct(m.ytdA, m.ytdT) : DASH;
        }}
      }}

      function patchAnalyzeAnnualBlocks(root, m) {{
        var section = root.querySelector('#insight-jump-analyze-annual');
        if (!section) return;
        var salesSummary = section.querySelector('.insight-annual-sales-summary');
        var currentProgress = section.querySelector('.insight-annual-current-progress');
        if (salesSummary) patchAnnualSalesSummaryProgressRows(salesSummary, m);
        if (currentProgress) patchAnnualCurrentProgressBlock(currentProgress, m);
      }}

      function patchMonthlyHistoricalCompareBlock(block, m, iso) {{
        var rows = block.querySelectorAll('.insight-monthly-historical-compare__row');
        function setRow(i, text, actual, baseline) {{
          var el = rows[i] && rows[i].querySelector('.insight-monthly-historical-compare__value');
          if (!el) return;
          el.textContent = text;
          if (arguments.length >= 4 && typeof window.applyInsightTwDiffEl === 'function') {{
            window.applyInsightTwDiffEl(el, actual, baseline);
          }}
        }}
        function clearAll() {{
          for (var i = 0; i < 6; i++) setRow(i, DASH, NaN, NaN);
        }}
        if (!m || !iso) {{
          clearAll();
          return;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          clearAll();
          return;
        }}
        var sumFn =
          typeof window.__sumMonthSalesThroughDay === 'function'
            ? window.__sumMonthSalesThroughDay
            : null;
        if (!sumFn) {{
          clearAll();
          return;
        }}
        var current = Number(m.mtdA);
        function prior(yearsBack) {{
          return sumFn(y - yearsBack, month, day);
        }}
        var p1 = prior(1);
        var p2 = prior(2);
        var p3 = prior(3);
        setRow(0, p1 && p1.hasData ? fmtInsightMoney(p1.sum) : DASH);
        if (p1 && p1.hasData && Number.isFinite(current)) {{
          setRow(
            1,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, p1.sum)
              : DASH,
            current,
            p1.sum
          );
        }} else {{
          setRow(1, DASH, NaN, NaN);
        }}
        setRow(2, p2 && p2.hasData ? fmtInsightMoney(p2.sum) : DASH);
        if (p2 && p2.hasData && Number.isFinite(current)) {{
          setRow(
            3,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, p2.sum)
              : DASH,
            current,
            p2.sum
          );
        }} else {{
          setRow(3, DASH, NaN, NaN);
        }}
        setRow(4, p3 && p3.hasData ? fmtInsightMoney(p3.sum) : DASH);
        if (p3 && p3.hasData && Number.isFinite(current)) {{
          setRow(
            5,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, p3.sum)
              : DASH,
            current,
            p3.sum
          );
        }} else {{
          setRow(5, DASH, NaN, NaN);
        }}
      }}

      function patchAnalyzeMonthlyHistoricalCompare(root, m, iso) {{
        root.querySelectorAll('.insight-monthly-historical-compare').forEach(function (block) {{
          patchMonthlyHistoricalCompareBlock(block, m, iso);
        }});
      }}

      function patchAnnualHistoricalCompareBlock(block, m, iso) {{
        var rows = block.querySelectorAll('.insight-annual-historical-compare__row');
        function setRow(i, text, actual, baseline) {{
          var el = rows[i] && rows[i].querySelector('.insight-annual-historical-compare__value');
          if (!el) return;
          el.textContent = text;
          if (arguments.length >= 4 && typeof window.applyInsightTwDiffEl === 'function') {{
            window.applyInsightTwDiffEl(el, actual, baseline);
          }}
        }}
        function clearAll() {{
          for (var i = 0; i < 7; i++) setRow(i, DASH, NaN, NaN);
        }}
        if (!m || !iso) {{
          clearAll();
          return;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          clearAll();
          return;
        }}
        var sumFn =
          typeof window.__sumYearSalesThroughDay === 'function'
            ? window.__sumYearSalesThroughDay
            : null;
        if (!sumFn) {{
          clearAll();
          return;
        }}
        var current = Number(m.ytdA);
        function prior(yearsBack) {{
          return sumFn(y - yearsBack, month, day);
        }}
        var p1 = prior(1);
        var p2 = prior(2);
        var p3 = prior(3);
        setRow(0, p1 && p1.hasData ? fmtInsightMoney(p1.sum) : DASH);
        if (p1 && p1.hasData && Number.isFinite(current)) {{
          setRow(
            1,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, p1.sum)
              : DASH,
            current,
            p1.sum
          );
          setRow(2, fmtInsightAchPct(current, p1.sum));
        }} else {{
          setRow(1, DASH, NaN, NaN);
          setRow(2, DASH);
        }}
        setRow(3, p2 && p2.hasData ? fmtInsightMoney(p2.sum) : DASH);
        if (p2 && p2.hasData && Number.isFinite(current)) {{
          setRow(
            4,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, p2.sum)
              : DASH,
            current,
            p2.sum
          );
        }} else {{
          setRow(4, DASH, NaN, NaN);
        }}
        setRow(5, p3 && p3.hasData ? fmtInsightMoney(p3.sum) : DASH);
        if (p3 && p3.hasData && Number.isFinite(current)) {{
          setRow(
            6,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, p3.sum)
              : DASH,
            current,
            p3.sum
          );
        }} else {{
          setRow(6, DASH, NaN, NaN);
        }}
      }}

      function patchAnalyzeAnnualHistoricalCompare(root, m, iso) {{
        root.querySelectorAll('.insight-annual-historical-compare').forEach(function (block) {{
          patchAnnualHistoricalCompareBlock(block, m, iso);
        }});
      }}

      /* Summary Comparison (sales only; margin reserved until expense lands) */
      function avgPriorPeriodSales(sumFn, y, month, day) {{
        if (!sumFn) return null;
        var sum = 0;
        var n = 0;
        for (var back = 1; back <= 3; back++) {{
          var prior = sumFn(y - back, month, day);
          if (prior && prior.hasData && Number.isFinite(prior.sum)) {{
            sum += prior.sum;
            n += 1;
          }}
        }}
        if (n <= 0) return null;
        return sum / n;
      }}

      /** Same-weekday sales avg for prior 1–3 years (business days only). */
      function avgPriorSameWeekdaySales(iso) {{
        var sameFn =
          typeof window.__sameWeekdayIso === 'function' ? window.__sameWeekdayIso : null;
        var bizFn =
          typeof window.__isTwBusinessDay === 'function' ? window.__isTwBusinessDay : null;
        var salesFn =
          typeof window.__readTwDaySales === 'function' ? window.__readTwDaySales : null;
        if (!sameFn || !bizFn || !salesFn || !iso) return null;
        var sum = 0;
        var n = 0;
        for (var back = 1; back <= 3; back++) {{
          var priorIso = sameFn(iso, back);
          if (!priorIso || !bizFn(priorIso)) continue;
          var amt = Number(salesFn(priorIso));
          if (!Number.isFinite(amt)) amt = 0;
          sum += amt;
          n += 1;
        }}
        if (n <= 0) return null;
        return sum / n;
      }}

      function setSummaryComparisonAllocWidget(key, pct, disabled) {{
        var widgets = window.__insightSummaryComparisonWidgets;
        var w = widgets && widgets[key];
        if (!w) return;
        if (disabled) {{
          if (typeof w.setDisabled === 'function') w.setDisabled();
          return;
        }}
        if (typeof w.setPercent === 'function') {{
          w.setPercent(Math.max(0.1, Number(pct)));
        }}
      }}

      function patchMonthlyComparisonBlock(block, m, iso) {{
        var rows = block.querySelectorAll('.insight-monthly-comparison__row');
        function setRow(i, text, actual, baseline) {{
          var el = rows[i] && rows[i].querySelector('.insight-monthly-comparison__value');
          if (!el) return;
          el.textContent = text;
          if (arguments.length >= 4 && typeof window.applyInsightTwDiffEl === 'function') {{
            window.applyInsightTwDiffEl(el, actual, baseline);
          }}
        }}
        function clearAll() {{
          for (var i = 0; i < 4; i++) setRow(i, DASH, NaN, NaN);
          setSummaryComparisonAllocWidget('monthly', 0, true);
        }}
        if (!m || !iso) {{
          clearAll();
          return;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          clearAll();
          return;
        }}
        var sumFn =
          typeof window.__sumMonthSalesThroughDay === 'function'
            ? window.__sumMonthSalesThroughDay
            : null;
        if (!sumFn) {{
          clearAll();
          return;
        }}
        var current = Number(m.mtdA);
        var last = sumFn(y - 1, month, day);
        setRow(0, Number.isFinite(current) ? fmtInsightMoney(current) : DASH);
        setRow(1, last && last.hasData ? fmtInsightMoney(last.sum) : DASH);
        if (last && last.hasData && Number.isFinite(current)) {{
          setRow(
            2,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, last.sum)
              : DASH,
            current,
            last.sum
          );
        }} else {{
          setRow(2, DASH, NaN, NaN);
        }}
        var marginNow = null;
        var marginLast = null;
        if (
          typeof window.__insightReadExpenseSnapshot === 'function' &&
          last &&
          last.hasData &&
          Number.isFinite(current) &&
          current > 0
        ) {{
          var curSnap = window.__insightReadExpenseSnapshot(iso);
          var priorIso =
            String(y - 1) + '-' + pad2Insight(month) + '-' + pad2Insight(day);
          var priorSnap = window.__insightReadExpenseSnapshot(priorIso);
          if (curSnap && curSnap.hasData && priorSnap && priorSnap.hasData) {{
            marginNow = insightProfitMarginPct(current, curSnap.month.total);
            marginLast = insightProfitMarginPct(last.sum, priorSnap.month.total);
          }}
        }}
        if (marginNow != null && marginLast != null) {{
          setRow(3, fmtInsightMarginChangePct(marginNow, marginLast), marginNow, marginLast);
        }} else {{
          setRow(3, DASH, NaN, NaN);
        }}

        var histAvg = avgPriorPeriodSales(sumFn, y, month, day);
        if (Number.isFinite(current) && histAvg != null && histAvg > 0) {{
          setSummaryComparisonAllocWidget('monthly', (current / histAvg) * 100, false);
        }} else {{
          setSummaryComparisonAllocWidget('monthly', 0, true);
        }}
      }}

      function patchAnnualComparisonBlock(block, m, iso) {{
        var rows = block.querySelectorAll('.insight-annual-comparison__row');
        function setRow(i, text, actual, baseline) {{
          var el = rows[i] && rows[i].querySelector('.insight-annual-comparison__value');
          if (!el) return;
          el.textContent = text;
          if (arguments.length >= 4 && typeof window.applyInsightTwDiffEl === 'function') {{
            window.applyInsightTwDiffEl(el, actual, baseline);
          }}
        }}
        function clearAll() {{
          for (var i = 0; i < 4; i++) setRow(i, DASH, NaN, NaN);
          setSummaryComparisonAllocWidget('annual', 0, true);
        }}
        if (!m || !iso) {{
          clearAll();
          return;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          clearAll();
          return;
        }}
        var sumFn =
          typeof window.__sumYearSalesThroughDay === 'function'
            ? window.__sumYearSalesThroughDay
            : null;
        if (!sumFn) {{
          clearAll();
          return;
        }}
        var current = Number(m.ytdA);
        var last = sumFn(y - 1, month, day);
        setRow(0, Number.isFinite(current) ? fmtInsightMoney(current) : DASH);
        setRow(1, last && last.hasData ? fmtInsightMoney(last.sum) : DASH);
        if (last && last.hasData && Number.isFinite(current)) {{
          setRow(
            2,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, last.sum)
              : DASH,
            current,
            last.sum
          );
        }} else {{
          setRow(2, DASH, NaN, NaN);
        }}
        var marginNow = null;
        var marginLast = null;
        if (
          typeof window.__insightReadExpenseSnapshot === 'function' &&
          last &&
          last.hasData &&
          Number.isFinite(current) &&
          current > 0
        ) {{
          var curSnap = window.__insightReadExpenseSnapshot(iso);
          var priorIso =
            String(y - 1) + '-' + pad2Insight(month) + '-' + pad2Insight(day);
          var priorSnap = window.__insightReadExpenseSnapshot(priorIso);
          if (curSnap && curSnap.hasData && priorSnap && priorSnap.hasData) {{
            marginNow = insightProfitMarginPct(current, curSnap.year.total);
            marginLast = insightProfitMarginPct(last.sum, priorSnap.year.total);
          }}
        }}
        if (marginNow != null && marginLast != null) {{
          setRow(3, fmtInsightMarginChangePct(marginNow, marginLast), marginNow, marginLast);
        }} else {{
          setRow(3, DASH, NaN, NaN);
        }}

        var histAvg = avgPriorPeriodSales(sumFn, y, month, day);
        if (Number.isFinite(current) && histAvg != null && histAvg > 0) {{
          setSummaryComparisonAllocWidget('annual', (current / histAvg) * 100, false);
        }} else {{
          setSummaryComparisonAllocWidget('annual', 0, true);
        }}
      }}

      function patchSummaryComparisonBlocks(root, m, iso) {{
        root.querySelectorAll('.insight-monthly-comparison').forEach(function (block) {{
          patchMonthlyComparisonBlock(block, m, iso);
        }});
        root.querySelectorAll('.insight-annual-comparison').forEach(function (block) {{
          patchAnnualComparisonBlock(block, m, iso);
        }});
      }}

      function patchSummaryDailyComparisonBar(m, iso) {{
        if (!m || !iso || !m.isBusinessToday) {{
          setSummaryComparisonAllocWidget('daily', 0, true);
          return;
        }}
        var histAvg = avgPriorSameWeekdaySales(iso);
        var current = Number(m.dailySales);
        if (Number.isFinite(current) && histAvg != null && histAvg > 0) {{
          setSummaryComparisonAllocWidget('daily', (current / histAvg) * 100, false);
        }} else {{
          setSummaryComparisonAllocWidget('daily', 0, true);
        }}
      }}

      function fmtInsightCount(n) {{
        if (!Number.isFinite(Number(n))) return DASH;
        return String(Math.round(Number(n)));
      }}

      function fmtInsightPctFrom(base, part) {{
        var b = Number(base);
        var p = Number(part);
        if (!Number.isFinite(b) || b <= 0 || !Number.isFinite(p)) return DASH;
        return Math.round((p / b) * 100) + '%';
      }}

      function fmtInsightProfitMarginPct(sales, profit) {{
        var s = Number(sales);
        var p = Number(profit);
        if (!Number.isFinite(s) || s <= 0 || !Number.isFinite(p)) return DASH;
        return Math.round((p / s) * 100) + '%';
      }}

      function pad2Insight(n) {{
        return (n < 10 ? '0' : '') + n;
      }}

      function isoDaysAgo(iso, days) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        d.setDate(d.getDate() - Number(days));
        return (
          d.getFullYear() +
          '-' +
          pad2Insight(d.getMonth() + 1) +
          '-' +
          pad2Insight(d.getDate())
        );
      }}

      function insightProfitMarginPct(sales, expenseTotal) {{
        var s = Number(sales);
        var e = Number(expenseTotal);
        if (!Number.isFinite(s) || s <= 0) return null;
        if (!Number.isFinite(e)) e = 0;
        return ((s - e) / s) * 100;
      }}

      function fmtInsightMarginChangePct(currentPct, baselinePct) {{
        if (!Number.isFinite(currentPct) || !Number.isFinite(baselinePct)) return DASH;
        var delta = currentPct - baselinePct;
        var sign = delta >= 0 ? '+' : '';
        return sign + (Math.round(delta * 10) / 10) + '%';
      }}

      function patchSummarySalesKpiExpenseRows(rows, sales, scope) {{
        var expEl = rows[1] && rows[1].querySelector('.insight-monthly-kpi__value, .insight-annual-kpi__value');
        var profitEl = rows[2] && rows[2].querySelector('.insight-monthly-kpi__value, .insight-annual-kpi__value');
        var marginEl = rows[3] && rows[3].querySelector('.insight-monthly-kpi__value, .insight-annual-kpi__value');
        if (!scope || !Number.isFinite(Number(sales)) || Number(sales) <= 0) {{
          if (expEl) expEl.textContent = DASH;
          if (profitEl) profitEl.textContent = DASH;
          if (marginEl) marginEl.textContent = DASH;
          return;
        }}
        var s = Number(sales);
        var total = Number(scope.total);
        var profit = s - total;
        if (expEl) expEl.textContent = fmtInsightMoney(total);
        if (profitEl) profitEl.textContent = fmtInsightMoney(profit);
        if (marginEl) marginEl.textContent = fmtInsightProfitMarginPct(s, profit);
      }}

      function patchSummaryDailyReferenceBlock(block, m, iso) {{
        var rows = block.querySelectorAll('.insight-daily-reference__row');
        function setVal(i, text, actual, baseline) {{
          var el = rows[i] && rows[i].querySelector('.insight-daily-reference__value');
          if (!el) return;
          el.textContent = text;
          if (arguments.length >= 4 && typeof window.applyInsightTwDiffEl === 'function') {{
            window.applyInsightTwDiffEl(el, actual, baseline);
          }}
        }}
        function clearAll() {{
          for (var i = 0; i < 4; i++) setVal(i, DASH, NaN, NaN);
        }}
        if (!m || !iso || !m.isBusinessToday) {{
          clearAll();
          return;
        }}
        var sameFn =
          typeof window.__sameWeekdayIso === 'function' ? window.__sameWeekdayIso : null;
        var bizFn =
          typeof window.__isTwBusinessDay === 'function' ? window.__isTwBusinessDay : null;
        var salesFn =
          typeof window.__readTwDaySales === 'function' ? window.__readTwDaySales : null;
        if (!sameFn || !bizFn || !salesFn) {{
          clearAll();
          return;
        }}
        var current = Number(m.dailySales);
        if (!Number.isFinite(current)) {{
          clearAll();
          return;
        }}
        var histAvg = avgPriorSameWeekdaySales(iso);
        setVal(
          0,
          histAvg != null && histAvg > 0 ? fmtInsightMoney(histAvg) : DASH,
          histAvg != null ? current : NaN,
          histAvg != null ? histAvg : NaN
        );
        var lyIso = sameFn(iso, 1);
        var lyBiz = lyIso && bizFn(lyIso);
        var lySales = lyBiz ? Number(salesFn(lyIso)) : NaN;
        setVal(1, lyBiz && Number.isFinite(lySales) ? fmtInsightMoney(lySales) : DASH);
        if (histAvg != null && histAvg > 0) {{
          setVal(
            2,
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(current, histAvg)
              : DASH,
            current,
            histAvg
          );
        }} else {{
          setVal(2, DASH, NaN, NaN);
        }}
        var weekIso = isoDaysAgo(iso, 7);
        var weekBiz = weekIso && bizFn(weekIso);
        var weekSales = weekBiz ? Number(salesFn(weekIso)) : NaN;
        setVal(3, weekBiz && Number.isFinite(weekSales) ? fmtInsightMoney(weekSales) : DASH);
      }}

      function patchSummaryDailyReferenceBlocks(root, m, iso) {{
        root.querySelectorAll('.insight-daily-reference').forEach(function (block) {{
          patchSummaryDailyReferenceBlock(block, m, iso);
        }});
      }}

      function patchSummaryMonthlyKpiBlock(block, m, expenseSnap) {{
        var rows = block.querySelectorAll('.insight-monthly-kpi__row');
        var salesEl = rows[0] && rows[0].querySelector('.insight-monthly-kpi__value');
        if (!m) {{
          if (salesEl) salesEl.textContent = DASH;
          patchSummarySalesKpiExpenseRows(rows, NaN, null);
          return;
        }}
        if (salesEl) salesEl.textContent = fmtInsightMoney(m.mtdA);
        patchSummarySalesKpiExpenseRows(
          rows,
          m.mtdA,
          expenseSnap && expenseSnap.hasData ? expenseSnap.month : null
        );
      }}

      function patchSummaryMonthlyProgressBlock(block, m) {{
        var rows = block.querySelectorAll('.insight-monthly-progress__row');
        var bdEl = rows[0] && rows[0].querySelector('.insight-monthly-progress__value');
        var needEl = rows[1] && rows[1].querySelector('.insight-monthly-progress__value');
        var dailyEl = rows[2] && rows[2].querySelector('.insight-monthly-progress__value');
        if (!m) {{
          if (bdEl) bdEl.textContent = DASH;
          if (needEl) needEl.textContent = DASH;
          if (dailyEl) dailyEl.textContent = DASH;
          return;
        }}
        var monthlyNeed =
          m.hasPlan && Number.isFinite(m.monthlyFullTarget)
            ? m.monthlyFullTarget - m.mtdA
            : null;
        if (bdEl) bdEl.textContent = fmtInsightCount(m.monthRemainingBD);
        if (needEl) {{
          needEl.textContent =
            monthlyNeed != null && Number.isFinite(monthlyNeed)
              ? fmtInsightMoney(monthlyNeed)
              : DASH;
        }}
        if (dailyEl) {{
          dailyEl.textContent =
            m.hasPlan && m.monthlyDailyNeed != null
              ? fmtInsightMoney(m.monthlyDailyNeed)
              : DASH;
        }}
      }}

      function patchSummaryMonthlyBlocks(root, m) {{
        var section = root.querySelector('#insight-jump-summary-monthly');
        if (!section) return;
        var kpi = section.querySelector('.insight-monthly-kpi');
        var cost = section.querySelector('.insight-monthly-cost');
        var progress = section.querySelector('.insight-monthly-progress');
        var expenseSnap = null;
        if (window.__INSIGHT_SELECTED_ISO && typeof window.__insightReadExpenseSnapshot === 'function') {{
          expenseSnap = window.__insightReadExpenseSnapshot(window.__INSIGHT_SELECTED_ISO);
        }}

        function patchMonthlyCostBlock(block, sales, scope) {{
          var rows = block.querySelectorAll('.insight-monthly-cost__row');
          function setRowValue(rowIdx, valueText, splitPctText) {{
            var row = rows[rowIdx];
            if (!row) return;
            var vals = row.querySelectorAll('.insight-monthly-cost__value');
            if (!vals || !vals.length) return;
            vals[0].textContent = valueText;
            if (vals[1] && splitPctText != null) vals[1].textContent = splitPctText;
          }}
          if (!scope || !Number.isFinite(Number(sales)) || Number(sales) <= 0) {{
            for (var ri = 0; ri < rows.length; ri++) setRowValue(ri, DASH, DASH);
            return;
          }}
          var s = Number(sales);
          setRowValue(0, fmtInsightMoney(scope.total));
          setRowValue(1, fmtInsightMoney(scope.fixed));
          setRowValue(2, fmtInsightMoney(scope.variable));
          setRowValue(3, fmtInsightPctFrom(s, scope.total));
          setRowValue(4, fmtInsightMoney(scope.food), fmtInsightPctFrom(s, scope.food));
          setRowValue(5, fmtInsightMoney(scope.drink), fmtInsightPctFrom(s, scope.drink));
          setRowValue(6, fmtInsightMoney(scope.misc), fmtInsightPctFrom(s, scope.misc));
          setRowValue(7, fmtInsightPctFrom(s, scope.total));
          setRowValue(8, fmtInsightPctFrom(s, Number(scope.food) + Number(scope.labor)));
        }}

        if (!m) {{
          if (kpi) patchSummaryMonthlyKpiBlock(kpi, null, null);
          if (cost) patchMonthlyCostBlock(cost, NaN, null);
          if (progress) patchSummaryMonthlyProgressBlock(progress, null);
          return;
        }}
        if (kpi) patchSummaryMonthlyKpiBlock(kpi, m, expenseSnap);
        if (cost) patchMonthlyCostBlock(cost, m.mtdA, expenseSnap ? expenseSnap.month : null);
        if (progress) patchSummaryMonthlyProgressBlock(progress, m);
      }}

      function fmtInsightAchPct(actual, target) {{
        if (typeof window.__twFmtAchPct === 'function') return window.__twFmtAchPct(actual, target);
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return DASH;
        return Math.round((actual / target) * 100) + '%';
      }}

      function setInsightRevisionValue(el, text) {{
        if (el) el.textContent = text;
      }}

      function revisionValue(groups, groupIdx, rowIdx) {{
        var g = groups[groupIdx];
        if (!g) return null;
        var rows = g.querySelectorAll('.insight-annual-target-revision__row');
        var row = rows[rowIdx];
        return row && row.querySelector('.insight-annual-target-revision__value');
      }}

      function patchSummaryAnnualKpiBlock(block, m, expenseSnap) {{
        var rows = block.querySelectorAll('.insight-annual-kpi__row');
        var salesEl = rows[0] && rows[0].querySelector('.insight-annual-kpi__value');
        if (!m) {{
          if (salesEl) salesEl.textContent = DASH;
          patchSummarySalesKpiExpenseRows(rows, NaN, null);
          return;
        }}
        if (salesEl) salesEl.textContent = fmtInsightMoney(m.ytdA);
        patchSummarySalesKpiExpenseRows(
          rows,
          m.ytdA,
          expenseSnap && expenseSnap.hasData ? expenseSnap.year : null
        );
      }}

      function patchSummaryAnnualProgressBlock(block, m) {{
        var rows = block.querySelectorAll('.insight-annual-progress__row');
        var bdEl = rows[0] && rows[0].querySelector('.insight-annual-progress__value');
        var needEl = rows[1] && rows[1].querySelector('.insight-annual-progress__value');
        var dailyEl = rows[2] && rows[2].querySelector('.insight-annual-progress__value');
        if (!m) {{
          if (bdEl) bdEl.textContent = DASH;
          if (needEl) needEl.textContent = DASH;
          if (dailyEl) dailyEl.textContent = DASH;
          return;
        }}
        if (bdEl) bdEl.textContent = fmtInsightCount(m.yearRemainingBD);
        if (needEl) {{
          needEl.textContent =
            m.hasPlan && m.annualRemaining != null
              ? fmtInsightMoney(m.annualRemaining)
              : DASH;
        }}
        if (dailyEl) {{
          dailyEl.textContent =
            m.hasPlan && m.annualDailyNeed != null
              ? fmtInsightMoney(m.annualDailyNeed)
              : DASH;
        }}
      }}

      function patchSummaryAnnualTargetRevisionBlock(block, m) {{
        var groups = block.querySelectorAll('.insight-annual-target-revision__group');
        if (!m) {{
          for (var gi = 0; gi < groups.length; gi++) {{
            var gRows = groups[gi].querySelectorAll('.insight-annual-target-revision__row');
            for (var ri = 0; ri < gRows.length; ri++) {{
              var el = gRows[ri].querySelector('.insight-annual-target-revision__value');
              if (el) el.textContent = DASH;
            }}
          }}
          return;
        }}
        setInsightRevisionValue(
          revisionValue(groups, 0, 0),
          m.annualTarget != null ? fmtInsightMoney(m.annualTarget) : DASH
        );
        setInsightRevisionValue(revisionValue(groups, 0, 1), fmtInsightMoney(m.ytdA));
        setInsightRevisionValue(
          revisionValue(groups, 0, 2),
          m.hasPlan && m.annualRemaining != null ? fmtInsightMoney(m.annualRemaining) : DASH
        );
        setInsightRevisionValue(revisionValue(groups, 1, 0), fmtInsightCount(m.yearRemainingBD));
        setInsightRevisionValue(
          revisionValue(groups, 1, 1),
          m.hasPlan && m.annualDailyNeed != null ? fmtInsightMoney(m.annualDailyNeed) : DASH
        );
        setInsightRevisionValue(
          revisionValue(groups, 2, 0),
          m.hasPlan ? fmtInsightMoney(m.ytdT) : DASH
        );
        setInsightRevisionValue(
          revisionValue(groups, 2, 1),
          m.hasPlan && typeof window.__twFmtDiff === 'function'
            ? window.__twFmtDiff(m.ytdA, m.ytdT)
            : DASH
        );
        setInsightRevisionValue(
          revisionValue(groups, 2, 2),
          m.hasPlan ? fmtInsightAchPct(m.ytdA, m.ytdT) : DASH
        );
      }}

      function patchSummaryAnnualBlocks(root, m) {{
        var section = root.querySelector('#insight-jump-summary-annual');
        if (!section) return;
        var kpi = section.querySelector('.insight-annual-kpi');
        var cost = section.querySelector('.insight-annual-cost');
        var progress = section.querySelector('.insight-annual-progress');
        var revision = section.querySelector('.insight-annual-target-revision');
        var expenseSnap = null;
        if (window.__INSIGHT_SELECTED_ISO && typeof window.__insightReadExpenseSnapshot === 'function') {{
          expenseSnap = window.__insightReadExpenseSnapshot(window.__INSIGHT_SELECTED_ISO);
        }}

        function patchAnnualCostBlock(block, sales, scope) {{
          var rows = block.querySelectorAll('.insight-annual-cost__row');
          function setRowValue(rowIdx, valueText, splitPctText) {{
            var row = rows[rowIdx];
            if (!row) return;
            var vals = row.querySelectorAll('.insight-annual-cost__value');
            if (!vals || !vals.length) return;
            vals[0].textContent = valueText;
            if (vals[1] && splitPctText != null) vals[1].textContent = splitPctText;
          }}
          if (!scope || !Number.isFinite(Number(sales)) || Number(sales) <= 0) {{
            for (var ri = 0; ri < rows.length; ri++) setRowValue(ri, DASH, DASH);
            return;
          }}
          var s = Number(sales);
          setRowValue(0, fmtInsightMoney(scope.total));
          setRowValue(1, fmtInsightMoney(scope.fixed));
          setRowValue(2, fmtInsightMoney(scope.variable));
          setRowValue(3, fmtInsightPctFrom(s, scope.total));
          setRowValue(4, fmtInsightMoney(scope.food), fmtInsightPctFrom(s, scope.food));
          setRowValue(5, fmtInsightMoney(scope.drink), fmtInsightPctFrom(s, scope.drink));
          setRowValue(6, fmtInsightMoney(scope.misc), fmtInsightPctFrom(s, scope.misc));
          setRowValue(7, fmtInsightPctFrom(s, scope.total));
          setRowValue(8, fmtInsightPctFrom(s, Number(scope.food) + Number(scope.labor)));
        }}

        if (!m) {{
          if (kpi) patchSummaryAnnualKpiBlock(kpi, null, null);
          if (cost) patchAnnualCostBlock(cost, NaN, null);
          if (progress) patchSummaryAnnualProgressBlock(progress, null);
          if (revision) patchSummaryAnnualTargetRevisionBlock(revision, null);
          return;
        }}
        if (kpi) patchSummaryAnnualKpiBlock(kpi, m, expenseSnap);
        if (cost) patchAnnualCostBlock(cost, m.ytdA, expenseSnap ? expenseSnap.year : null);
        if (progress) patchSummaryAnnualProgressBlock(progress, m);
        if (revision) patchSummaryAnnualTargetRevisionBlock(revision, m);
      }}

      /* Insight → Graph → Daily */
      function setGraphDailyAllocWidget(key, pct, disabled) {{
        var widgets = window.__insightGraphDailyWidgets;
        var w = widgets && widgets[key];
        if (!w) return;
        if (disabled) {{
          if (typeof w.setDisabled === 'function') w.setDisabled();
          return;
        }}
        if (typeof w.setPercent === 'function') {{
          w.setPercent(Math.max(0.1, Number(pct)));
        }}
      }}

      function setGraphDailyRowCaps(row, kgiText, kpiText) {{
        if (!row) return;
        var caps = row.querySelectorAll('.insight-graph-daily__marker-cap-value');
        if (caps[0]) caps[0].textContent = kgiText;
        if (caps[1]) caps[1].textContent = kpiText;
      }}

      function layoutGraphDailyHistoricalBars(root) {{
        if (!root) return;
        var trackW = 588;
        var items = Array.prototype.slice.call(
          root.querySelectorAll('.insight-graph-daily-historical__item')
        );
        var max = 0;
        items.forEach(function (item) {{
          if (item.classList.contains('insight-graph-daily-historical__item--off')) return;
          var amt = Number(item.getAttribute('data-amount'));
          if (Number.isFinite(amt) && amt > max) max = amt;
        }});
        items.forEach(function (item) {{
          if (item.classList.contains('insight-graph-daily-historical__item--off')) return;
          var fill = item.querySelector('.insight-graph-daily-historical__bar-fill');
          var amt = Number(item.getAttribute('data-amount'));
          if (!fill) return;
          if (!Number.isFinite(amt) || max <= 0) {{
            fill.style.width = '0';
            return;
          }}
          fill.style.width = Math.round(trackW * (amt / max)) + 'px';
        }});
      }}

      function patchGraphDailyHistorical(block, iso) {{
        if (!block || !iso) return;
        var sameFn =
          typeof window.__sameWeekdayIso === 'function' ? window.__sameWeekdayIso : null;
        var bizFn =
          typeof window.__isTwBusinessDay === 'function' ? window.__isTwBusinessDay : null;
        var salesFn =
          typeof window.__readTwDaySales === 'function' ? window.__readTwDaySales : null;
        var items = block.querySelectorAll('.insight-graph-daily-historical__item');
        if (!sameFn || !bizFn || !salesFn || !items.length) return;
        for (var i = 0; i < items.length; i++) {{
          var item = items[i];
          var yearIso = sameFn(iso, i);
          if (!yearIso) continue;
          var y = Number(String(yearIso).split('-')[0]);
          item.setAttribute('data-year', String(y));
          var yearEl = item.querySelector('.insight-graph-daily-historical__year');
          if (yearEl && Number.isFinite(y)) yearEl.textContent = String(y);
          var valueEl = item.querySelector('.insight-graph-daily-historical__value');
          var track = item.querySelector('.insight-graph-daily-historical__bar-track');
          var isBiz = bizFn(yearIso);
          if (!isBiz) {{
            item.classList.add('insight-graph-daily-historical__item--off');
            item.removeAttribute('data-amount');
            if (track) track.innerHTML = '';
            if (valueEl) valueEl.textContent = 'OFF';
            continue;
          }}
          item.classList.remove('insight-graph-daily-historical__item--off');
          var amt = Number(salesFn(yearIso));
          if (!Number.isFinite(amt)) amt = 0;
          item.setAttribute('data-amount', String(amt));
          if (track && !track.querySelector('.insight-graph-daily-historical__bar-fill')) {{
            track.innerHTML = '<div class="insight-graph-daily-historical__bar-fill"></div>';
          }}
          if (valueEl) valueEl.textContent = fmtInsightMoney(amt);
        }}
        layoutGraphDailyHistoricalBars(block);
      }}

      function patchGraphDailyBlocks(root, m, iso) {{
        var section = root.querySelector('#insight-jump-graph-daily');
        if (!section) return;
        var row1 = section.querySelector('.insight-graph-daily__row--target-actual');
        var row2 = section.querySelector('.insight-graph-daily__row--last-year-weekday');
        var hist = section.querySelector('#insight-graph-daily-historical');

        function clearRow1() {{
          setGraphDailyRowCaps(row1, DASH, DASH);
          setGraphDailyAllocWidget('targetActual', 0, true);
        }}
        function clearRow2() {{
          setGraphDailyRowCaps(row2, DASH, DASH);
          setGraphDailyAllocWidget('lastYearWeekday', 0, true);
        }}

        if (!m || !iso) {{
          clearRow1();
          clearRow2();
          return;
        }}

        var hasDailyPlan = m.isBusinessToday && m.dailyTarget != null;
        if (hasDailyPlan) {{
          setGraphDailyRowCaps(
            row1,
            fmtInsightMoney(m.dailySales),
            fmtInsightMoney(m.dailyTarget)
          );
          var pct1 =
            Number(m.dailyTarget) > 0
              ? (Number(m.dailySales) / Number(m.dailyTarget)) * 100
              : NaN;
          if (Number.isFinite(pct1)) setGraphDailyAllocWidget('targetActual', pct1, false);
          else clearRow1();
        }} else {{
          clearRow1();
        }}

        var sameFn =
          typeof window.__sameWeekdayIso === 'function' ? window.__sameWeekdayIso : null;
        var bizFn =
          typeof window.__isTwBusinessDay === 'function' ? window.__isTwBusinessDay : null;
        var salesFn =
          typeof window.__readTwDaySales === 'function' ? window.__readTwDaySales : null;
        if (!m.isBusinessToday || !sameFn || !bizFn || !salesFn) {{
          clearRow2();
        }} else {{
          var lyIso = sameFn(iso, 1);
          var lyBiz = lyIso && bizFn(lyIso);
          var lySales = lyIso && lyBiz ? Number(salesFn(lyIso)) : NaN;
          if (lyBiz && Number.isFinite(lySales) && lySales > 0) {{
            setGraphDailyRowCaps(
              row2,
              fmtInsightMoney(m.dailySales),
              fmtInsightMoney(lySales)
            );
            var pct2 = (Number(m.dailySales) / lySales) * 100;
            setGraphDailyAllocWidget('lastYearWeekday', pct2, false);
          }} else if (lyBiz && Number.isFinite(lySales)) {{
            setGraphDailyRowCaps(
              row2,
              fmtInsightMoney(m.dailySales),
              fmtInsightMoney(lySales)
            );
            setGraphDailyAllocWidget('lastYearWeekday', 0, true);
          }} else {{
            setGraphDailyRowCaps(row2, fmtInsightMoney(m.dailySales), DASH);
            setGraphDailyAllocWidget('lastYearWeekday', 0, true);
          }}
        }}

        if (hist) patchGraphDailyHistorical(hist, iso);
      }}

      /* Insight → Graph → Monthly / Annual 累計横棒 */
      function setGraphCumAllocWidget(key, pct, disabled) {{
        var widgets = window.__insightGraphCumWidgets;
        var w = widgets && widgets[key];
        if (!w) return;
        if (disabled) {{
          if (typeof w.setDisabled === 'function') w.setDisabled();
          return;
        }}
        if (typeof w.setPercent === 'function') {{
          w.setPercent(Math.max(0.1, Number(pct)));
        }}
      }}

      function patchGraphCumRow(row, widgetKey, actual, target, hasPlan) {{
        if (!hasPlan || !Number.isFinite(Number(actual)) || !Number.isFinite(Number(target))) {{
          setGraphDailyRowCaps(row, DASH, DASH);
          setGraphCumAllocWidget(widgetKey, 0, true);
          return;
        }}
        var a = Number(actual);
        var t = Number(target);
        setGraphDailyRowCaps(row, fmtInsightMoney(a), fmtInsightMoney(t));
        if (t > 0) setGraphCumAllocWidget(widgetKey, (a / t) * 100, false);
        else setGraphCumAllocWidget(widgetKey, 0, true);
      }}

      function patchGraphMonthlyAnnualCumBars(root, m) {{
        var monthlyRow = root.querySelector(
          '#insight-jump-graph-monthly .insight-graph-monthly__row--cumulative'
        );
        var annualRow = root.querySelector(
          '#insight-jump-graph-annual .insight-graph-annual__row--cumulative'
        );
        if (!m) {{
          patchGraphCumRow(monthlyRow, 'monthly', NaN, NaN, false);
          patchGraphCumRow(annualRow, 'annual', NaN, NaN, false);
          return;
        }}
        patchGraphCumRow(monthlyRow, 'monthly', m.mtdA, m.mtdT, m.hasPlan);
        patchGraphCumRow(annualRow, 'annual', m.ytdA, m.ytdT, m.hasPlan);
      }}

      window.renderInsightTwDiffs = function (iso) {{
        var root = document.getElementById('insight-overlay');
        if (!root) return;
        var compute =
          typeof window.__computeTwMetricsForIso === 'function'
            ? window.__computeTwMetricsForIso
            : null;
        var m = compute ? compute(iso) : null;
        var expenseSnap = null;
        if (iso && typeof window.__insightReadExpenseSnapshot === 'function') {{
          expenseSnap = window.__insightReadExpenseSnapshot(iso);
        }}

        root.querySelectorAll('.insight-daily-kpi').forEach(function (block) {{
          if (!m) {{
            patchDailyKpiBlock(block, NaN, NaN, false);
            var pmRows = block.querySelectorAll('.insight-daily-kpi__row');
            var pmEl = pmRows[3] && pmRows[3].querySelector('.insight-daily-kpi__value');
            if (pmEl) pmEl.textContent = DASH;
            return;
          }}
          var hasDailyPlan = m.isBusinessToday && m.dailyTarget != null;
          patchDailyKpiBlock(
            block,
            m.dailySales,
            m.dailyTarget,
            hasDailyPlan
          );
          var rows = block.querySelectorAll('.insight-daily-kpi__row');
          var pmEl = rows[3] && rows[3].querySelector('.insight-daily-kpi__value');
          if (pmEl) {{
            if (!m.isBusinessToday) {{
              pmEl.textContent = DASH;
            }} else if (expenseSnap && expenseSnap.hasData) {{
              var sales = Number(m.dailySales);
              var profit = sales - Number(expenseSnap.day.total);
              pmEl.textContent = fmtInsightProfitMarginPct(sales, profit);
            }} else {{
              pmEl.textContent = DASH;
            }}
          }}
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

        patchSummaryDailyReferenceBlocks(root, m, iso);

        root.querySelectorAll('.insight-daily-expenses').forEach(function (block) {{
          var rows = block.querySelectorAll('.insight-daily-expenses__row');
          var vEl = rows[0] && rows[0].querySelector('.insight-daily-expenses__value');
          var fEl = rows[1] && rows[1].querySelector('.insight-daily-expenses__value');
          var tEl = rows[2] && rows[2].querySelector('.insight-daily-expenses__value');
          if (!expenseSnap || !expenseSnap.hasData) {{
            if (vEl) vEl.textContent = DASH;
            if (fEl) fEl.textContent = DASH;
            if (tEl) tEl.textContent = DASH;
            return;
          }}
          if (vEl) vEl.textContent = fmtInsightMoney(expenseSnap.day.variable);
          if (fEl) fEl.textContent = fmtInsightMoney(expenseSnap.day.fixed);
          if (tEl) tEl.textContent = fmtInsightMoney(expenseSnap.day.total);
        }});
        root.querySelectorAll('.insight-daily-profit').forEach(function (block) {{
          var rows = block.querySelectorAll('.insight-daily-profit__row');
          var pEl = rows[0] && rows[0].querySelector('.insight-daily-profit__value');
          var mEl = rows[1] && rows[1].querySelector('.insight-daily-profit__value');
          if (!m || !expenseSnap || !expenseSnap.hasData) {{
            if (pEl) pEl.textContent = DASH;
            if (mEl) mEl.textContent = DASH;
            return;
          }}
          var sales = Number(m.dailySales);
          var profit = Number(sales) - Number(expenseSnap.day.total);
          if (pEl) pEl.textContent = fmtInsightMoney(profit);
          if (mEl) mEl.textContent = fmtInsightProfitMarginPct(sales, profit);
        }});

        patchSummaryMonthlyBlocks(root, m);
        patchSummaryAnnualBlocks(root, m);
        patchSummaryComparisonBlocks(root, m, iso);
        patchSummaryDailyComparisonBar(m, iso);
        patchAnalyzeAnnualBlocks(root, m);
        patchAnalyzeMonthlyHistoricalCompare(root, m, iso);
        patchAnalyzeAnnualHistoricalCompare(root, m, iso);
        patchGraphDailyBlocks(root, m, iso);
        patchGraphMonthlyAnnualCumBars(root, m);
        patchAnalyzeMonthlyExpenseCharts(m, iso);
      }};

      function setExpensePlChartPct(chartEl, fixedPct, variablePct) {{
        if (!chartEl) return;
        var f = Math.round(Number(fixedPct));
        var v = Math.round(Number(variablePct));
        if (!Number.isFinite(f) || f < 0) f = 0;
        if (!Number.isFinite(v) || v < 0) v = 0;
        chartEl.style.setProperty('--fixed-pct', String(f));
        chartEl.style.setProperty('--variable-pct', String(v));
        var fixedEl = chartEl.querySelector('[data-role="fixed-pct"]');
        var variableEl = chartEl.querySelector('[data-role="variable-pct"]');
        if (fixedEl) fixedEl.textContent = f + '%';
        if (variableEl) variableEl.textContent = v + '%';
      }}

      function expensePlPctFrom(exp, sales) {{
        var s = Number(sales);
        if (!exp || !exp.hasData || !Number.isFinite(s) || s <= 0) {{
          return {{ fixed: 0, variable: 0 }};
        }}
        return {{
          fixed: (Number(exp.fixed) / s) * 100,
          variable: (Number(exp.variable) / s) * 100,
        }};
      }}

      /**
       * Analyze → Monthly Expense & Profit（4本）
       * 当月: expense thru day ÷ mtdA
       * 前年/2y/3y: 同月同日までの支出 ÷ 同月同日までの売上（Historical Compare と同スコープ）
       */
      function patchAnalyzeMonthlyExpenseCharts(m, iso) {{
        var ids = [
          'insight-analyze-expense-pl-current',
          'insight-analyze-expense-pl-last-year',
          'insight-analyze-expense-pl-2y',
          'insight-analyze-expense-pl-3y',
        ];
        function clearAll() {{
          ids.forEach(function (id) {{
            setExpensePlChartPct(document.getElementById(id), 0, 0);
          }});
        }}
        if (!iso || typeof window.__insightReadMonthExpense !== 'function') {{
          clearAll();
          return;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          clearAll();
          return;
        }}

        var sumFn =
          typeof window.__sumMonthSalesThroughDay === 'function'
            ? window.__sumMonthSalesThroughDay
            : null;

        function fillPrior(chartId, yearsBack) {{
          var chart = document.getElementById(chartId);
          if (!chart) return;
          var py = y - yearsBack;
          var exp = window.__insightReadMonthExpense(py, month, day);
          var salesScope = sumFn ? sumFn(py, month, day) : null;
          var sales =
            salesScope && salesScope.hasData ? Number(salesScope.sum) : NaN;
          var pct = expensePlPctFrom(exp, sales);
          setExpensePlChartPct(chart, pct.fixed, pct.variable);
        }}

        var currentChart = document.getElementById(ids[0]);
        if (currentChart) {{
          if (!m) {{
            setExpensePlChartPct(currentChart, 0, 0);
          }} else {{
            var curExp = window.__insightReadMonthExpense(y, month, day);
            var curPct = expensePlPctFrom(curExp, m.mtdA);
            setExpensePlChartPct(currentChart, curPct.fixed, curPct.variable);
          }}
        }}
        fillPrior(ids[1], 1);
        fillPrior(ids[2], 2);
        fillPrior(ids[3], 3);
      }}

      /* 互換: 旧名呼び出し */
      function patchAnalyzeMonthlyExpenseCurrent(m, iso) {{
        patchAnalyzeMonthlyExpenseCharts(m, iso);
      }}

      function refreshInsightTwDiffsFromStore() {{
        var root = document.getElementById('insight-overlay');
        if (!root || root.hidden) return;
        var iso =
          window.__INSIGHT_SELECTED_ISO ||
          (window.__ANNUAL_DATA &&
            window.__ANNUAL_DATA.daily &&
            window.__ANNUAL_DATA.daily.selectedDate);
        if (iso && typeof window.renderInsightTwDiffs === 'function') {{
          window.renderInsightTwDiffs(iso);
        }}
      }}

      document.addEventListener('annual:dailyDateChanged', refreshInsightTwDiffsFromStore);
      document.addEventListener('kpi:dailyTargetModeChanged', refreshInsightTwDiffsFromStore);
      document.addEventListener('kpi:weekdayBaselineChanged', refreshInsightTwDiffsFromStore);
      document.addEventListener('kpi:mepDataChanged', refreshInsightTwDiffsFromStore);
    }})();
    {INSIGHT_DIFF_JS_END}"""

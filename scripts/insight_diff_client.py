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
        window.__INSIGHT_PENDING_ISO = iso;
        if (window.__INSIGHT_FILL_SCHED) return;
        window.__INSIGHT_FILL_SCHED = true;
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            window.__INSIGHT_FILL_SCHED = false;
            function runInsightFillHeavy() {
              var pending = window.__INSIGHT_PENDING_ISO;
              if (!pending) return;
              if (window.__INSIGHT_FILL_BUSY) {
                window.__INSIGHT_FILL_RERUN = true;
                return;
              }
              window.__INSIGHT_FILL_BUSY = true;
              window.__INSIGHT_PENDING_ISO = null;
              var paneAnalyze = document.getElementById('insight-pane-analyze');
              var onAnalyze = !!(paneAnalyze && !paneAnalyze.hidden);
              var holding = !!window.__INSIGHT_DATE_HOLDING;
              try {
                if (typeof window.renderInsightTwDiffs === 'function') {
                  window.renderInsightTwDiffs(pending, {
                    analyzeAsync: true,
                    skipAnalyze: onAnalyze,
                  });
                }
              } catch (_insightDiffErr) {}
              try {
                // 長押し中は full settle を入れない（走って止まる主因）
                if (
                  onAnalyze &&
                  !holding &&
                  typeof window.__scheduleInsightAnalyzeSettle === 'function'
                ) {
                  window.__scheduleInsightAnalyzeSettle(pending);
                }
              } catch (_insightSettleErr) {}
              try {
                if (!holding) {
                  document.dispatchEvent(
                    new CustomEvent('insight:dateChanged', { detail: { iso: pending } })
                  );
                }
              } catch (_insightDateErr) {}
              window.__INSIGHT_FILL_BUSY = false;
              if (window.__INSIGHT_FILL_RERUN || window.__INSIGHT_PENDING_ISO) {
                window.__INSIGHT_FILL_RERUN = false;
                if (!window.__INSIGHT_PENDING_ISO) {
                  window.__INSIGHT_PENDING_ISO = window.__INSIGHT_SELECTED_ISO;
                }
                if (!window.__INSIGHT_FILL_SCHED) {
                  window.__INSIGHT_FILL_SCHED = true;
                  requestAnimationFrame(function () {
                    requestAnimationFrame(function () {
                      window.__INSIGHT_FILL_SCHED = false;
                      runInsightFillHeavy();
                    });
                  });
                }
              }
            }
            runInsightFillHeavy();
          });
        });
      }"""

INSIGHT_SET_TAB_OLD = """      function setInsightTab(which) {
        which = which || 'summary';
        if (paneSummary) paneSummary.hidden = which !== 'summary';
        if (paneAnalyze) paneAnalyze.hidden = which !== 'analyze';
        if (paneGraph) paneGraph.hidden = which !== 'graph';
        if (tabSummary) tabSummary.classList.toggle('is-active', which === 'summary');
        if (tabAnalyze) tabAnalyze.classList.toggle('is-active', which === 'analyze');
        if (tabGraph) tabGraph.classList.toggle('is-active', which === 'graph');
        if (titleEl) titleEl.textContent = insightTabTitles[which] || insightTabTitles.summary;
        if (insightScroll) insightScroll.scrollTop = 0;
        updateInsightJumpHrefs();
      }"""

INSIGHT_SET_TAB_NEW = """      function setInsightTab(which) {
        which = which || 'summary';
        if (paneSummary) paneSummary.hidden = which !== 'summary';
        if (paneAnalyze) paneAnalyze.hidden = which !== 'analyze';
        if (paneGraph) paneGraph.hidden = which !== 'graph';
        if (tabSummary) tabSummary.classList.toggle('is-active', which === 'summary');
        if (tabAnalyze) tabAnalyze.classList.toggle('is-active', which === 'analyze');
        if (tabGraph) tabGraph.classList.toggle('is-active', which === 'graph');
        if (titleEl) titleEl.textContent = insightTabTitles[which] || insightTabTitles.summary;
        if (insightScroll) insightScroll.scrollTop = 0;
        updateInsightJumpHrefs();
        try {
          document.dispatchEvent(new CustomEvent('insight:tabChanged', { detail: { tab: which } }));
        } catch (_insightTabEvErr) {}
        if (which === 'analyze' || which === 'graph') {
          var tabIso = window.__INSIGHT_SELECTED_ISO;
          var paneCache = window.__INSIGHT_PANE_CACHE || (window.__INSIGHT_PANE_CACHE = {});
          var cacheKey = which === 'analyze' ? 'analyzeIso' : 'graphIso';
          if (tabIso && paneCache[cacheKey] === tabIso) {
            return;
          }
          window.__INSIGHT_TAB_PENDING = which;
          if (window.__INSIGHT_TAB_SCHED) return;
          window.__INSIGHT_TAB_SCHED = true;
          requestAnimationFrame(function () {
            requestAnimationFrame(function () {
              window.__INSIGHT_TAB_SCHED = false;
              var pendingTab = window.__INSIGHT_TAB_PENDING;
              window.__INSIGHT_TAB_PENDING = null;
              if (!pendingTab) return;
              try {
                if (
                  window.__INSIGHT_SELECTED_ISO &&
                  typeof window.renderInsightTwDiffs === 'function'
                ) {
                  window.renderInsightTwDiffs(window.__INSIGHT_SELECTED_ISO, {
                    mode: pendingTab,
                  });
                }
              } catch (_insightTabErr) {}
            });
          });
        }
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

      /**
       * Analyze Annual Target Revision 4行 KPI（v1）
       * - Term: 選択日の四半期（Term 1–4）
       * - Suggested Adjustment: round((ytdA/ytdT - 1)*100)、±20% キャップ
       * - Status: |adj|<3 On Track / 3–10 Watch / >10 Revise
       * - Suggested Target: annualTarget * (1 + adj/100)
       */
      function computeAnnualTargetRevisionKpi(m, iso) {{
        var term = DASH;
        if (iso) {{
          var month = Number(String(iso).split('-')[1]);
          if (Number.isFinite(month) && month >= 1 && month <= 12) {{
            term = 'Term ' + (Math.floor((month - 1) / 3) + 1);
          }}
        }}
        if (
          !m ||
          !m.hasPlan ||
          !Number.isFinite(Number(m.ytdA)) ||
          !Number.isFinite(Number(m.ytdT)) ||
          Number(m.ytdT) <= 0
        ) {{
          return {{ term: term, status: DASH, adjText: DASH, targetText: DASH }};
        }}
        var adj = Math.round(((Number(m.ytdA) - Number(m.ytdT)) / Number(m.ytdT)) * 100);
        if (adj > 20) adj = 20;
        if (adj < -20) adj = -20;
        var abs = Math.abs(adj);
        var status = abs < 3 ? 'On Track' : abs <= 10 ? 'Watch' : 'Revise';
        var adjText = (adj > 0 ? '+' : '') + adj + '%';
        var targetText = DASH;
        if (m.annualTarget != null && Number.isFinite(Number(m.annualTarget))) {{
          targetText = fmtInsightMoney(Math.round(Number(m.annualTarget) * (1 + adj / 100)));
        }}
        return {{ term: term, status: status, adjText: adjText, targetText: targetText }};
      }}

      function patchAnalyzeAnnualTargetRevisionKpi(root, m, iso) {{
        if (!root) return;
        var blocks = root.querySelectorAll('.insight-annual-target-revision-kpi');
        if (!blocks.length) return;
        var kpi = computeAnnualTargetRevisionKpi(m, iso);
        blocks.forEach(function (block) {{
          var rows = block.querySelectorAll('.insight-annual-target-revision-kpi__row');
          function setRow(i, text) {{
            var el = rows[i] && rows[i].querySelector('.insight-annual-target-revision-kpi__value');
            if (el) el.textContent = text;
          }}
          setRow(0, kpi.term);
          setRow(1, kpi.status);
          setRow(2, kpi.adjText);
          setRow(3, kpi.targetText);
        }});
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
        if (!widgets) return;
        var list = [];
        if (widgets[key]) list.push(widgets[key]);
        // Annual 比較バーと同式の「年度目標改訂」最下段 Historical Avg
        if (key === 'annual' && widgets.annualRevision) list.push(widgets.annualRevision);
        // Analyze / Graph Current Progress 下段 Historical Avg
        if (key === 'annual' && widgets.annualAnalyzeProgress) {{
          var ap = widgets.annualAnalyzeProgress;
          if (Array.isArray(ap)) {{
            for (var ai = 0; ai < ap.length; ai++) list.push(ap[ai]);
          }} else {{
            list.push(ap);
          }}
        }}
        for (var i = 0; i < list.length; i++) {{
          var w = list[i];
          if (!w) continue;
          if (disabled) {{
            if (typeof w.setDisabled === 'function') w.setDisabled();
            continue;
          }}
          if (typeof w.setPercent === 'function') {{
            w.setPercent(Math.max(0.1, Number(pct)));
          }}
        }}
      }}

      /** Annual Historical Avg %（Summary 比較棒 / Analyze Current Progress 下段） */
      function patchAnnualHistAvgAlloc(m, iso) {{
        if (!m || !iso) {{
          setSummaryComparisonAllocWidget('annual', 0, true);
          return;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          setSummaryComparisonAllocWidget('annual', 0, true);
          return;
        }}
        var sumFn =
          typeof window.__sumYearSalesThroughDay === 'function'
            ? window.__sumYearSalesThroughDay
            : null;
        if (!sumFn) {{
          setSummaryComparisonAllocWidget('annual', 0, true);
          return;
        }}
        var current = Number(m.ytdA);
        var histAvg = avgPriorPeriodSales(sumFn, y, month, day);
        if (Number.isFinite(current) && histAvg != null && histAvg > 0) {{
          setSummaryComparisonAllocWidget('annual', (current / histAvg) * 100, false);
        }} else {{
          setSummaryComparisonAllocWidget('annual', 0, true);
        }}
      }}

      function setSummarySalesAllocWidget(key, actual, target, hasPlan) {{
        var widgets = window.__insightSummarySalesWidgets;
        var list = widgets && widgets[key];
        if (!list) return;
        if (!Array.isArray(list)) list = [list];
        var a = Number(actual);
        var t = Number(target);
        var disabled =
          !hasPlan || !Number.isFinite(a) || !Number.isFinite(t) || t <= 0;
        for (var i = 0; i < list.length; i++) {{
          var w = list[i];
          if (!w) continue;
          if (disabled) {{
            if (typeof w.setDisabled === 'function') w.setDisabled();
            continue;
          }}
          if (typeof w.setPercent === 'function') {{
            w.setPercent(Math.max(0.1, (a / t) * 100));
          }}
        }}
      }}

      function patchSummarySalesAllocBars(m) {{
        if (!m) {{
          setSummarySalesAllocWidget('daily', NaN, NaN, false);
          setSummarySalesAllocWidget('monthly', NaN, NaN, false);
          setSummarySalesAllocWidget('annual', NaN, NaN, false);
          return;
        }}
        setSummarySalesAllocWidget(
          'daily',
          m.dailySales,
          m.dailyTarget,
          m.isBusinessToday && m.dailyTarget != null
        );
        setSummarySalesAllocWidget('monthly', m.mtdA, m.mtdT, m.hasPlan);
        setSummarySalesAllocWidget('annual', m.ytdA, m.ytdT, m.hasPlan);
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

        patchAnnualHistAvgAlloc(m, iso);
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

      function runInsightAnalyzePatches(root, m, iso, asyncChunk) {{
        var jobs = [
          function () {{
            patchAnalyzeAnnualBlocks(root, m);
          }},
          function () {{
            patchAnalyzeMonthlyHistoricalCompare(root, m, iso);
          }},
          function () {{
            patchAnalyzeAnnualHistoricalCompare(root, m, iso);
          }},
          function () {{
            patchAnalyzeMonthlyExpenseCharts(m, iso);
          }},
          function () {{
            patchAnalyzeDualInsight(root, iso);
          }},
          function () {{
            patchAnalyzeAnnualExpenseProfit(root, m, iso);
          }},
          function () {{
            patchAnalyzeAnnualYearExpenseCharts(m, iso);
          }},
          function () {{
            patchAnalyzeAnnualTargetRevisionKpi(root, m, iso);
          }},
          function () {{
            patchHistoricalInsightAccess(root, iso);
          }},
        ];
        function markDone() {{
          var cache = window.__INSIGHT_PANE_CACHE || (window.__INSIGHT_PANE_CACHE = {{}});
          cache.analyzeIso = iso;
        }}
        if (!asyncChunk) {{
          window.__INSIGHT_ANALYZE_GEN = (window.__INSIGHT_ANALYZE_GEN || 0) + 1;
          for (var si = 0; si < jobs.length; si++) {{
            try {{
              jobs[si]();
            }} catch (_analyzeSyncErr) {{}}
          }}
          markDone();
          return;
        }}
        var gen = (window.__INSIGHT_ANALYZE_GEN = (window.__INSIGHT_ANALYZE_GEN || 0) + 1);
        function step(i) {{
          if (gen !== window.__INSIGHT_ANALYZE_GEN) return;
          if (i >= jobs.length) {{
            markDone();
            return;
          }}
          try {{
            jobs[i]();
          }} catch (_analyzeJobErr) {{}}
          if (i + 1 < jobs.length) {{
            requestAnimationFrame(function () {{
              step(i + 1);
            }});
          }} else {{
            step(i + 1);
          }}
        }}
        step(0);
      }}

      window.__scheduleInsightAnalyzeSettle = function (iso) {{
        if (window.__INSIGHT_DATE_HOLDING) {{
          window.__INSIGHT_ANALYZE_SETTLE_ISO = iso;
          return;
        }}
        window.__INSIGHT_ANALYZE_SETTLE_ISO = iso;
        if (window.__INSIGHT_ANALYZE_SETTLE_T) {{
          clearTimeout(window.__INSIGHT_ANALYZE_SETTLE_T);
        }}
        window.__INSIGHT_ANALYZE_SETTLE_T = setTimeout(function () {{
          window.__INSIGHT_ANALYZE_SETTLE_T = null;
          if (window.__INSIGHT_DATE_HOLDING) return;
          var pending =
            window.__INSIGHT_ANALYZE_SETTLE_ISO || window.__INSIGHT_SELECTED_ISO;
          var pane = document.getElementById('insight-pane-analyze');
          if (!pending || !pane || pane.hidden) return;
          if (typeof window.renderInsightTwDiffs !== 'function') return;
          try {{
            window.renderInsightTwDiffs(pending, {{ mode: 'analyze' }});
          }} catch (_settleErr) {{}}
        }}, 200);
      }};

      window.__insightDateHoldStart = function () {{
        window.__INSIGHT_DATE_HOLDING = true;
        if (window.__INSIGHT_ANALYZE_SETTLE_T) {{
          clearTimeout(window.__INSIGHT_ANALYZE_SETTLE_T);
          window.__INSIGHT_ANALYZE_SETTLE_T = null;
        }}
      }};

      window.__insightDateHoldEnd = function () {{
        if (!window.__INSIGHT_DATE_HOLDING) return;
        window.__INSIGHT_DATE_HOLDING = false;
        var iso = window.__INSIGHT_SELECTED_ISO || window.__INSIGHT_ANALYZE_SETTLE_ISO;
        try {{
          if (iso) {{
            document.dispatchEvent(new CustomEvent('insight:dateChanged', {{ detail: {{ iso: iso }} }}));
          }}
        }} catch (_holdDateErr) {{}}
        var pane = document.getElementById('insight-pane-analyze');
        if (pane && !pane.hidden && typeof window.__scheduleInsightAnalyzeSettle === 'function') {{
          window.__scheduleInsightAnalyzeSettle(iso);
        }}
      }};

      window.renderInsightTwDiffs = function (iso, opts) {{
        var root = document.getElementById('insight-overlay');
        if (!root) return;
        opts = opts || {{}};
        var mode = opts.mode || 'auto';
        var paneSummaryEl = document.getElementById('insight-pane-summary');
        var paneAnalyzeEl = document.getElementById('insight-pane-analyze');
        var paneGraphEl = document.getElementById('insight-pane-graph');
        var wantAnalyze =
          mode === 'analyze' ||
          (mode === 'auto' && (!paneAnalyzeEl || !paneAnalyzeEl.hidden));
        var wantGraph =
          mode === 'graph' || (mode === 'auto' && (!paneGraphEl || !paneGraphEl.hidden));
        var wantSummary =
          mode === 'summary' ||
          mode === 'full' ||
          (mode === 'auto' && (!paneSummaryEl || !paneSummaryEl.hidden));
        if (mode === 'analyze' || mode === 'graph') wantSummary = false;
        if (opts.skipAnalyze) {{
          wantAnalyze = false;
          // 進行中の Analyze chunk を中断（長押し中のメインスレッド確保）
          window.__INSIGHT_ANALYZE_GEN = (window.__INSIGHT_ANALYZE_GEN || 0) + 1;
          var skipCache = window.__INSIGHT_PANE_CACHE || (window.__INSIGHT_PANE_CACHE = {{}});
          skipCache.analyzeIso = null;
        }}
        // Analyze 長押し中: 重い DOM は後回し、可視グラフだけ即追従
        if (opts.skipAnalyze && !wantSummary && !wantGraph) {{
          var lightCompute =
            typeof window.__computeTwMetricsForIso === 'function'
              ? window.__computeTwMetricsForIso
              : null;
          var lightM = lightCompute ? lightCompute(iso) : null;
          patchSummarySalesAllocBars(lightM);
          var holdingLight = !!window.__INSIGHT_DATE_HOLDING;
          var lightScope = insightAnalyzeExpenseLightScope();
          if (!holdingLight || lightScope.monthly) {{
            patchAnalyzeMonthlyExpenseCharts(lightM, iso);
          }}
          if (!holdingLight || lightScope.annual) {{
            patchAnalyzeAnnualYearExpenseCharts(lightM, iso);
          }}
          // 数値 KPI は settle に任せ、長押し中は棒だけ追従
          if (!holdingLight) {{
            patchAnalyzeAnnualBlocks(root, lightM);
          }}
          patchAnnualHistAvgAlloc(lightM, iso);
          return;
        }}
        if (!wantSummary && !wantAnalyze && !wantGraph) return;

        var compute =
          typeof window.__computeTwMetricsForIso === 'function'
            ? window.__computeTwMetricsForIso
            : null;
        var m = compute ? compute(iso) : null;
        var expenseSnap = null;
        if (iso && typeof window.__insightReadExpenseSnapshot === 'function') {{
          expenseSnap = window.__insightReadExpenseSnapshot(iso);
        }}

        if (wantSummary) {{
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
        patchSummarySalesAllocBars(m);
        }} else if (wantAnalyze || wantGraph) {{
          patchSummarySalesAllocBars(m);
        }}

        if (wantAnalyze) {{
          // タブ切替 or 日付ナビ(analyzeAsync): 分割。verify は同期のまま。
          runInsightAnalyzePatches(
            root,
            m,
            iso,
            mode === 'analyze' || !!opts.analyzeAsync
          );
        }}
        if (wantGraph) {{
          patchGraphDailyBlocks(root, m, iso);
          patchGraphMonthlyAnnualCumBars(root, m);
          var gCache = window.__INSIGHT_PANE_CACHE || (window.__INSIGHT_PANE_CACHE = {{}});
          gCache.graphIso = iso;
        }}
      }};

      function insightIsJaLang() {{
        return (
          String(document.documentElement.getAttribute('lang') || '')
            .toLowerCase()
            .indexOf('ja') === 0
        );
      }}

      function dualInsightNoneLabel() {{
        return insightIsJaLang() ? 'なし' : 'None';
      }}

      function dualInsightWeatherLabel(code) {{
        var presets = [
          {{ code: '', ja: '—', en: '—' }},
          {{ code: 'sunny', ja: '晴れ', en: 'Sunny' }},
          {{ code: 'cloudy', ja: '曇り', en: 'Cloudy' }},
          {{ code: 'rain', ja: '雨', en: 'Rain' }},
          {{ code: 'snow', ja: '雪', en: 'Snow' }},
          {{ code: 'thunder', ja: '雷', en: 'Thunder' }},
          {{ code: 'storm', ja: '嵐', en: 'Storm' }},
          {{ code: 'gale', ja: '暴風', en: 'Gale' }},
        ];
        var s = String(code == null ? '' : code);
        var ja = insightIsJaLang();
        for (var i = 0; i < presets.length; i++) {{
          if (presets[i].code === s) return ja ? presets[i].ja : presets[i].en;
        }}
        return s ? s : DASH;
      }}

      function dualInsightLoadYearPayload(year) {{
        if (!window.KpiYearStore || typeof KpiYearStore.loadMepYearPayload !== 'function') {{
          return null;
        }}
        return KpiYearStore.loadMepYearPayload(year);
      }}

      function dualInsightMemoRowIds(year) {{
        var payload = dualInsightLoadYearPayload(year);
        if (!payload) return [];
        if (payload.mepMemoRows && payload.mepMemoRows.length) {{
          return payload.mepMemoRows.slice(0, 6).map(function (row) {{
            return row.id;
          }});
        }}
        var memos = (payload.dailyMeta && payload.dailyMeta.memos) || {{}};
        return Object.keys(memos);
      }}

      function dualInsightReadMemo(year, rowId, iso) {{
        var payload = dualInsightLoadYearPayload(year);
        if (!payload || !payload.dailyMeta || !payload.dailyMeta.memos || !rowId) return '';
        var byRow = payload.dailyMeta.memos[rowId];
        if (!byRow) return '';
        return String(byRow[iso] == null ? '' : byRow[iso]).trim();
      }}

      function dualInsightReadWeather(year, iso) {{
        var payload = dualInsightLoadYearPayload(year);
        if (!payload || !payload.dailyMeta || !payload.dailyMeta.weather) return '';
        return String(payload.dailyMeta.weather[iso] == null ? '' : payload.dailyMeta.weather[iso]);
      }}

      function dualInsightIsOff(iso) {{
        if (window.KpiYearStore && typeof KpiYearStore.readBusinessDay === 'function') {{
          return KpiYearStore.readBusinessDay(iso) === false;
        }}
        if (typeof window.__isTwBusinessDay === 'function') {{
          return !window.__isTwBusinessDay(iso);
        }}
        return false;
      }}

      function dualInsightDayFields(iso) {{
        var empty = {{
          weather: DASH,
          memos: [DASH, DASH, DASH, DASH, DASH, DASH],
        }};
        if (!iso || !/^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(String(iso))) return empty;
        if (dualInsightIsOff(iso)) return empty;
        var y = Number(String(iso).slice(0, 4));
        if (!Number.isFinite(y)) return empty;
        var rowIds = dualInsightMemoRowIds(y);
        var memos = [];
        for (var i = 0; i < 6; i++) {{
          var raw = dualInsightReadMemo(y, rowIds[i], iso);
          memos.push(raw ? raw : dualInsightNoneLabel());
        }}
        var wCode = dualInsightReadWeather(y, iso);
        return {{
          weather: dualInsightWeatherLabel(wCode),
          memos: memos,
        }};
      }}

      function fillDualInsightCol(col, fields) {{
        if (!col || !fields) return;
        var dds = col.querySelectorAll('.insight-analyze-dual-insight__row dd');
        if (dds[0]) dds[0].textContent = fields.weather;
        for (var i = 0; i < 6; i++) {{
          if (dds[i + 1]) dds[i + 1].textContent = fields.memos[i];
        }}
      }}

      function patchAnalyzeDualInsight(root, iso) {{
        if (!root) return;
        var blocks = root.querySelectorAll('.insight-analyze-dual-insight');
        if (!blocks.length) return;
        var todayFields = dualInsightDayFields(iso);
        var lyIso =
          iso && typeof window.__sameWeekdayIso === 'function'
            ? window.__sameWeekdayIso(iso, 1)
            : null;
        var lyFields = dualInsightDayFields(lyIso);
        blocks.forEach(function (block) {{
          fillDualInsightCol(
            block.querySelector('.insight-analyze-dual-insight__col--today'),
            todayFields
          );
          fillDualInsightCol(
            block.querySelector('.insight-analyze-dual-insight__col--last-year'),
            lyFields
          );
        }});
      }}

      function clearHistoricalInsightAccessGroup(group) {{
        if (!group) return;
        var rows = group.querySelectorAll('.insight-historical-insight-access__row');
        for (var i = 0; i < rows.length; i++) {{
          var el = rows[i].querySelector('.insight-historical-insight-access__value');
          if (el) el.textContent = DASH;
        }}
        var title = group.querySelector('.insight-historical-insight-access__popover-title');
        if (title) title.textContent = DASH;
        var list = group.querySelector('.insight-historical-insight-access__popover-list');
        if (list) {{
          list.innerHTML =
            '<li class="insight-historical-insight-access__popover-item">' + DASH + '</li>';
        }}
      }}

      function escapeInsightHtml(s) {{
        return String(s == null ? '' : s)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;');
      }}

      function historicalReasonEmptyLabel(kind) {{
        if (insightIsJaLang()) {{
          return kind === 'year' ? 'この期間のメモはありません' : 'この月のメモはありません';
        }}
        return kind === 'year' ? 'No memo for this period' : 'No memo for this month';
      }}

      function historicalReasonMemoLabels(year) {{
        var ja = insightIsJaLang();
        var defaults = ja
          ? ['店舗イベント', 'エリアイベント', 'SNS', 'マーケ', 'プロモ', '予約']
          : [
              'Store Event',
              'Area Event',
              'Social Media',
              'Marketing',
              'Promo Conversion',
              'Reservation',
            ];
        var payload = dualInsightLoadYearPayload(year);
        var labels = defaults.slice();
        if (payload && payload.mepMemoRows && payload.mepMemoRows.length) {{
          for (var i = 0; i < 6 && i < payload.mepMemoRows.length; i++) {{
            var row = payload.mepMemoRows[i];
            var lab = ja
              ? row.labelJa || row.labelEn || defaults[i]
              : row.labelEn || row.labelJa || defaults[i];
            if (lab) labels[i] = String(lab);
          }}
        }}
        return labels;
      }}

      function historicalReasonReadStrategyNote(year, month1) {{
        if (!window.KpiYearStore || typeof KpiYearStore.readStrategyUserNote !== 'function') {{
          return '';
        }}
        return String(KpiYearStore.readStrategyUserNote(year, month1 - 1) || '')
          .trim()
          .slice(0, 200);
      }}

      function historicalReasonUniqueJoin(values) {{
        var seen = {{}};
        var out = [];
        var truncated = false;
        for (var i = 0; i < values.length; i++) {{
          var v = String(values[i] == null ? '' : values[i]).trim();
          if (!v || v === DASH || v === dualInsightNoneLabel()) continue;
          if (seen[v]) continue;
          seen[v] = true;
          if (out.length >= 3) {{
            truncated = true;
            break;
          }}
          out.push(v);
        }}
        if (!out.length) return '';
        var text = out.join(', ');
        if (truncated) text += '…';
        return text.slice(0, 200);
      }}

      /**
       * View Reason: Best/Worst 月（または年ピア）の Weather＋6メモ＋User Note を集約。
       * kind=month → その年月全日
       * kind=year  → その年の 1/1〜12/31（売上ランキングは YTD でも、理由メモは通年）
       */
      function buildHistoricalReasonListHtml(rec, kind, day) {{
        if (!rec) {{
          return (
            '<li class="insight-historical-insight-access__popover-item">' + DASH + '</li>'
          );
        }}
        var y = Number(rec.year);
        var month = Number(rec.month);
        if (!Number.isFinite(y) || !Number.isFinite(month) || month < 1 || month > 12) {{
          return (
            '<li class="insight-historical-insight-access__popover-item">' +
            escapeInsightHtml(historicalReasonEmptyLabel(kind)) +
            '</li>'
          );
        }}
        var weatherVals = [];
        var memoVals = [[], [], [], [], [], []];
        var rowIds = dualInsightMemoRowIds(y);
        var mStart = kind === 'month' ? month : 1;
        var mEnd = kind === 'month' ? month : 12;
        for (var m = mStart; m <= mEnd; m++) {{
          var lastDay = new Date(y, m, 0).getDate();
          for (var d = 1; d <= lastDay; d++) {{
            var iso =
              y +
              '-' +
              pad2Insight(m) +
              '-' +
              pad2Insight(d);
            if (dualInsightIsOff(iso)) continue;
            var wCode = dualInsightReadWeather(y, iso);
            if (wCode) weatherVals.push(dualInsightWeatherLabel(wCode));
            for (var ri = 0; ri < 6; ri++) {{
              var raw = dualInsightReadMemo(y, rowIds[ri], iso);
              if (raw) memoVals[ri].push(raw);
            }}
          }}
        }}
        var lines = [];
        var weatherText = historicalReasonUniqueJoin(weatherVals);
        if (weatherText) {{
          lines.push({{
            label: insightIsJaLang() ? '天気' : 'Weather',
            value: weatherText,
          }});
        }}
        var memoLabels = historicalReasonMemoLabels(y);
        for (var mi = 0; mi < 6; mi++) {{
          var joined = historicalReasonUniqueJoin(memoVals[mi]);
          if (joined) lines.push({{ label: memoLabels[mi], value: joined }});
        }}
        if (kind === 'month') {{
          var note = historicalReasonReadStrategyNote(y, month);
          if (note) {{
            lines.unshift({{
              label: insightIsJaLang() ? '戦略メモ' : 'User Note',
              value: note,
            }});
          }}
        }} else {{
          var noteBits = [];
          for (var nm = 1; nm <= 12; nm++) {{
            var n = historicalReasonReadStrategyNote(y, nm);
            if (n) noteBits.push(pad2Insight(nm) + ': ' + n);
          }}
          var noteJoin = historicalReasonUniqueJoin(noteBits);
          if (noteJoin) {{
            lines.unshift({{
              label: insightIsJaLang() ? '戦略メモ' : 'User Note',
              value: noteJoin,
            }});
          }}
        }}
        if (!lines.length) {{
          return (
            '<li class="insight-historical-insight-access__popover-item">' +
            escapeInsightHtml(historicalReasonEmptyLabel(kind)) +
            '</li>'
          );
        }}
        var html = '';
        for (var li = 0; li < lines.length; li++) {{
          html +=
            '<li class="insight-historical-insight-access__popover-item"><strong>' +
            escapeInsightHtml(lines[li].label) +
            ':</strong> ' +
            escapeInsightHtml(lines[li].value) +
            '</li>';
        }}
        return html;
      }}

      function fillHistoricalInsightAccessGroup(group, rec, kind, day) {{
        if (!group) return;
        if (!rec) {{
          clearHistoricalInsightAccessGroup(group);
          return;
        }}
        var rows = group.querySelectorAll('.insight-historical-insight-access__row');
        var dateEl = rows[0] && rows[0].querySelector('.insight-historical-insight-access__value');
        var salesEl = rows[1] && rows[1].querySelector('.insight-historical-insight-access__value');
        var marginEl = rows[2] && rows[2].querySelector('.insight-historical-insight-access__value');
        if (kind === 'month') {{
          if (dateEl) dateEl.textContent = rec.year + '/' + pad2Insight(rec.month);
        }} else {{
          if (dateEl) dateEl.textContent = String(rec.year);
        }}
        if (salesEl) salesEl.textContent = fmtInsightMoney(rec.sales);
        if (marginEl) {{
          marginEl.textContent = rec.hasExpense
            ? fmtInsightProfitMarginPct(rec.sales, rec.profit)
            : DASH;
        }}
        var title = group.querySelector('.insight-historical-insight-access__popover-title');
        if (title) {{
          title.textContent =
            kind === 'month'
              ? rec.year + '/' + pad2Insight(rec.month)
              : String(rec.year);
        }}
        var list = group.querySelector('.insight-historical-insight-access__popover-list');
        if (list) list.innerHTML = buildHistoricalReasonListHtml(rec, kind, day);
      }}

      function collectSameMonthHistory(y, month) {{
        var sumFn =
          typeof window.__sumMonthSalesThroughDay === 'function'
            ? window.__sumMonthSalesThroughDay
            : null;
        if (!sumFn) return [];
        var dim = new Date(y, month, 0).getDate();
        var out = [];
        for (var back = 1; back <= 20; back++) {{
          var py = y - back;
          var scope = sumFn(py, month, dim);
          if (!scope || !scope.hasData) continue;
          var sales = Number(scope.sum);
          if (!Number.isFinite(sales)) continue;
          var exp =
            typeof window.__insightReadMonthExpense === 'function'
              ? window.__insightReadMonthExpense(py, month)
              : null;
          var hasExpense = !!(exp && exp.hasData);
          var profit = hasExpense ? sales - Number(exp.total) : NaN;
          out.push({{
            year: py,
            month: month,
            sales: sales,
            profit: profit,
            hasExpense: hasExpense,
          }});
        }}
        return out;
      }}

      function collectSameYtdHistory(y, month, day) {{
        var sumFn =
          typeof window.__sumYearSalesThroughDay === 'function'
            ? window.__sumYearSalesThroughDay
            : null;
        if (!sumFn) return [];
        var out = [];
        for (var back = 1; back <= 20; back++) {{
          var py = y - back;
          var scope = sumFn(py, month, day);
          if (!scope || !scope.hasData) continue;
          var sales = Number(scope.sum);
          if (!Number.isFinite(sales)) continue;
          var expTotal = 0;
          var hasExpense = false;
          if (typeof window.__insightReadMonthExpense === 'function') {{
            for (var m = 1; m <= month; m++) {{
              var td = m === month ? day : new Date(py, m, 0).getDate();
              var exp = window.__insightReadMonthExpense(py, m, td);
              if (exp && exp.hasData) {{
                hasExpense = true;
                expTotal += Number(exp.total) || 0;
              }}
            }}
          }}
          out.push({{
            year: py,
            month: month,
            sales: sales,
            profit: hasExpense ? sales - expTotal : NaN,
            hasExpense: hasExpense,
          }});
        }}
        return out;
      }}

      function pickBestWorstBySales(records) {{
        if (!records || !records.length) return {{ best: null, worst: null }};
        var best = records[0];
        var worst = records[0];
        for (var i = 1; i < records.length; i++) {{
          var r = records[i];
          if (r.sales > best.sales) best = r;
          if (r.sales < worst.sales) worst = r;
        }}
        return {{ best: best, worst: worst }};
      }}

      function patchHistoricalInsightAccess(root, iso) {{
        if (!root) return;
        var monthBlocks = root.querySelectorAll(
          '.insight-overlay__section--monthly .insight-historical-insight-access'
        );
        var annualBlocks = root.querySelectorAll(
          '.insight-overlay__section--annual .insight-historical-insight-access'
        );
        if (!iso) {{
          monthBlocks.forEach(function (block) {{
            clearHistoricalInsightAccessGroup(block.querySelector('[data-insight-month-key="best"]'));
            clearHistoricalInsightAccessGroup(block.querySelector('[data-insight-month-key="worst"]'));
          }});
          annualBlocks.forEach(function (block) {{
            clearHistoricalInsightAccessGroup(block.querySelector('[data-insight-year-key="best"]'));
            clearHistoricalInsightAccessGroup(
              block.querySelector('[data-insight-year-key="weakest"]')
            );
          }});
          return;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          patchHistoricalInsightAccess(root, null);
          return;
        }}

        var monthPick = pickBestWorstBySales(collectSameMonthHistory(y, month));
        monthBlocks.forEach(function (block) {{
          fillHistoricalInsightAccessGroup(
            block.querySelector('[data-insight-month-key="best"]'),
            monthPick.best,
            'month',
            day
          );
          fillHistoricalInsightAccessGroup(
            block.querySelector('[data-insight-month-key="worst"]'),
            monthPick.worst,
            'month',
            day
          );
        }});

        var yearPick = pickBestWorstBySales(collectSameYtdHistory(y, month, day));
        annualBlocks.forEach(function (block) {{
          fillHistoricalInsightAccessGroup(
            block.querySelector('[data-insight-year-key="best"]'),
            yearPick.best,
            'year',
            day
          );
          fillHistoricalInsightAccessGroup(
            block.querySelector('[data-insight-year-key="weakest"]'),
            yearPick.worst,
            'year',
            day
          );
        }});
      }}

      function setExpensePlChartPct(chartEl, fixedPct, variablePct) {{
        if (!chartEl) return;
        var f = Math.round(Number(fixedPct));
        var v = Math.round(Number(variablePct));
        if (!Number.isFinite(f) || f < 0) f = 0;
        if (!Number.isFinite(v) || v < 0) v = 0;
        if (
          chartEl.getAttribute('data-fixed-pct') === String(f) &&
          chartEl.getAttribute('data-variable-pct') === String(v)
        ) {{
          return;
        }}
        chartEl.setAttribute('data-fixed-pct', String(f));
        chartEl.setAttribute('data-variable-pct', String(v));
        chartEl.style.setProperty('--fixed-pct', String(f));
        chartEl.style.setProperty('--variable-pct', String(v));
        var fixedEl = chartEl.querySelector('[data-role="fixed-pct"]');
        var variableEl = chartEl.querySelector('[data-role="variable-pct"]');
        if (fixedEl) fixedEl.textContent = f + '%';
        if (variableEl) variableEl.textContent = v + '%';
        /* 0% セグメントは棒が消えるのにラベルが左端／Expenses と重なるので隠す */
        function setSegLabelVisible(kind, shown) {{
          var pctEl = chartEl.querySelector('[data-role="' + kind + '-pct"]');
          if (pctEl) {{
            if (shown) pctEl.removeAttribute('hidden');
            else pctEl.setAttribute('hidden', '');
            pctEl.setAttribute('aria-hidden', shown ? 'false' : 'true');
          }}
          var label = chartEl.querySelector(
            '.insight-monthly-expense-pl__seg-label--' +
              kind +
              ', .insight-annual-year-expense-pl__seg-label--' +
              kind
          );
          if (label) {{
            if (shown) label.removeAttribute('hidden');
            else label.setAttribute('hidden', '');
            label.setAttribute('aria-hidden', shown ? 'false' : 'true');
          }}
        }}
        setSegLabelVisible('fixed', f > 0);
        setSegLabelVisible('variable', v > 0);
      }}

      /** 長押し中は画面内の Monthly/Annual 支出棒だけ更新（両方見えていれば両方） */
      function insightAnalyzeExpenseLightScope() {{
        var monthly = document.getElementById('insight-jump-analyze-monthly');
        var annual = document.getElementById('insight-jump-analyze-annual');
        var scroll = document.querySelector('#insight-overlay .insight-overlay__scroll');
        if (!scroll) return {{ monthly: true, annual: true }};
        var sr = scroll.getBoundingClientRect();
        function visibleEnough(el) {{
          if (!el) return false;
          var r = el.getBoundingClientRect();
          return r.bottom > sr.top + 24 && r.top < sr.bottom - 24;
        }}
        var mVis = visibleEnough(monthly);
        var aVis = visibleEnough(annual);
        if (!mVis && !aVis) return {{ monthly: true, annual: true }};
        return {{ monthly: mVis, annual: aVis }};
      }}
      window.__setExpensePlChartPct = setExpensePlChartPct;

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

      function insightReadYearExpenseThrough(year, month, day) {{
        var empty = {{ fixed: 0, variable: 0, total: 0, hasData: false }};
        if (typeof window.__insightReadMonthExpense !== 'function') return empty;
        var y = Number(year);
        var mo = Number(month);
        var d = Number(day);
        if (!Number.isFinite(y) || !Number.isFinite(mo) || !Number.isFinite(d)) return empty;
        if (mo < 1 || mo > 12) return empty;
        var cache = window.__INSIGHT_YEAR_EXPENSE_CACHE || (window.__INSIGHT_YEAR_EXPENSE_CACHE = {{}});
        var cacheKey = y + '-' + mo + '-' + d;
        if (Object.prototype.hasOwnProperty.call(cache, cacheKey)) {{
          return cache[cacheKey];
        }}
        // 増分: 同月前日 or 前月末
        if (d > 1) {{
          var prevDayKey = y + '-' + mo + '-' + (d - 1);
          if (Object.prototype.hasOwnProperty.call(cache, prevDayKey)) {{
            var prevDay = cache[prevDayKey];
            var dayExp = window.__insightReadMonthExpense(y, mo, d);
            var prevThru = window.__insightReadMonthExpense(y, mo, d - 1);
            var addFixed = (Number(dayExp.fixed) || 0) - (Number(prevThru.fixed) || 0);
            var addVar = (Number(dayExp.variable) || 0) - (Number(prevThru.variable) || 0);
            var fwd = {{
              fixed: Math.round((Number(prevDay.fixed) || 0) + addFixed),
              variable: Math.round((Number(prevDay.variable) || 0) + addVar),
              total: 0,
              hasData: !!(prevDay.hasData || (dayExp && dayExp.hasData)),
            }};
            fwd.total = Math.round(fwd.fixed + fwd.variable);
            cache[cacheKey] = fwd;
            return fwd;
          }}
        }} else if (mo > 1) {{
          var prevDim = new Date(y, mo - 1, 0).getDate();
          var prevMonthKey = y + '-' + (mo - 1) + '-' + prevDim;
          if (Object.prototype.hasOwnProperty.call(cache, prevMonthKey)) {{
            var prevMo = cache[prevMonthKey];
            var day1 = window.__insightReadMonthExpense(y, mo, 1);
            var fromPrev = {{
              fixed: Math.round((Number(prevMo.fixed) || 0) + (Number(day1.fixed) || 0)),
              variable: Math.round((Number(prevMo.variable) || 0) + (Number(day1.variable) || 0)),
              total: 0,
              hasData: !!(prevMo.hasData || (day1 && day1.hasData)),
            }};
            fromPrev.total = Math.round(fromPrev.fixed + fromPrev.variable);
            cache[cacheKey] = fromPrev;
            return fromPrev;
          }}
        }}
        var fixed = 0;
        var variable = 0;
        var hasData = false;
        for (var mm = 1; mm <= mo; mm++) {{
          var td = mm === mo ? d : new Date(y, mm, 0).getDate();
          var exp = window.__insightReadMonthExpense(y, mm, td);
          if (!exp || !exp.hasData) continue;
          hasData = true;
          fixed += Number(exp.fixed) || 0;
          variable += Number(exp.variable) || 0;
        }}
        var result = {{
          fixed: Math.round(fixed),
          variable: Math.round(variable),
          total: Math.round(fixed + variable),
          hasData: hasData,
        }};
        cache[cacheKey] = result;
        return result;
      }}

      function patchAnalyzeAnnualExpenseProfit(root, m, iso) {{
        if (!root) return;
        var blocks = root.querySelectorAll('.insight-annual-expense-profit');
        if (!blocks.length) return;
        function clearBlock(block) {{
          var rows = block.querySelectorAll('.insight-annual-expense-profit__row');
          for (var i = 0; i < rows.length; i++) {{
            var el = rows[i].querySelector('.insight-annual-expense-profit__value');
            if (el) el.textContent = DASH;
          }}
        }}
        if (!m || !iso) {{
          blocks.forEach(clearBlock);
          return;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          blocks.forEach(clearBlock);
          return;
        }}
        var exp = insightReadYearExpenseThrough(y, month, day);
        var sales = Number(m.ytdA);
        blocks.forEach(function (block) {{
          var rows = block.querySelectorAll('.insight-annual-expense-profit__row');
          function setRow(i, text) {{
            var el = rows[i] && rows[i].querySelector('.insight-annual-expense-profit__value');
            if (el) el.textContent = text;
          }}
          if (!exp.hasData || !Number.isFinite(sales)) {{
            clearBlock(block);
            return;
          }}
          var profit = sales - Number(exp.total);
          setRow(0, fmtInsightMoney(exp.total));
          setRow(1, fmtInsightMoney(exp.fixed));
          setRow(2, fmtInsightMoney(exp.variable));
          setRow(3, fmtInsightMoney(profit));
          setRow(4, fmtInsightProfitMarginPct(sales, profit));
        }});
      }}

      /**
       * Analyze → Year Expense & Profit（4本）
       * 当年/前年/2y/3y とも 年初〜選択日の YTD 支出 ÷ YTD 売上
       */
      function patchAnalyzeAnnualYearExpenseCharts(m, iso) {{
        var ids = [
          'insight-analyze-annual-year-expense-pl-current',
          'insight-analyze-annual-year-expense-pl-last-year',
          'insight-analyze-annual-year-expense-pl-2y',
          'insight-analyze-annual-year-expense-pl-3y',
        ];
        function clearAll() {{
          ids.forEach(function (id) {{
            setExpensePlChartPct(document.getElementById(id), 0, 0);
          }});
        }}
        if (!iso) {{
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

        function fillYear(chartId, year, salesOverride) {{
          var chart = document.getElementById(chartId);
          if (!chart) return;
          var exp = insightReadYearExpenseThrough(year, month, day);
          var sales = salesOverride;
          if (!Number.isFinite(sales)) {{
            var scope = sumFn ? sumFn(year, month, day) : null;
            sales = scope && scope.hasData ? Number(scope.sum) : NaN;
          }}
          var pct = expensePlPctFrom(exp, sales);
          setExpensePlChartPct(chart, pct.fixed, pct.variable);
        }}

        fillYear(ids[0], y, m ? Number(m.ytdA) : NaN);
        fillYear(ids[1], y - 1, NaN);
        fillYear(ids[2], y - 2, NaN);
        fillYear(ids[3], y - 3, NaN);
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

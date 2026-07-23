"""Insight Graph Annual Graph2 — 年次累計比較の実データ化.

Graph1 / CSS / 棒グラフは触らない。
"""

from __future__ import annotations

# Graph2 のみ残っている未パッチ getFocus（Graph1 は既に resolveInsightTrendIso 付き）
TREND_GET_FOCUS_OLD = """        function getFocusYearContext() {
          var data = window.__ANNUAL_DATA || {};
          var iso = data.daily && data.daily.selectedDate;"""

TREND_GET_FOCUS_NEW = """        function resolveInsightTrendIso() {
          if (window.__INSIGHT_SELECTED_ISO) return window.__INSIGHT_SELECTED_ISO;
          var data = window.__ANNUAL_DATA || {};
          return data.daily && data.daily.selectedDate;
        }

        function getFocusYearContext() {
          var data = window.__ANNUAL_DATA || {};
          var iso = resolveInsightTrendIso();"""

TREND_BUILD_STORE_OLD = """          return {
            current: toCumulative(endDay, 1, 0),
            lastYear: toCumulative(dim, 0.9, 1.3),
            best: toCumulative(dim, 1.08, 2.4),
            todayDay: endDay
          };
        }

        function pathFromPoints(pts) {"""

TREND_BUILD_STORE_NEW = """          return {
            current: toCumulative(endDay, 1, 0),
            lastYear: toCumulative(dim, 0.9, 1.3),
            best: toCumulative(dim, 1.08, 2.4),
            todayDay: endDay
          };
        }

        function buildStoreComparePayload(ctx, dim) {
          var cutoffIso = resolveInsightTrendIso();
          if (typeof window.__buildAnnualCompareTrendPayload === 'function') {
            var built = window.__buildAnnualCompareTrendPayload(ctx.year, cutoffIso);
            if (
              built &&
              Array.isArray(built.current) &&
              Array.isArray(built.lastYear) &&
              Array.isArray(built.best) &&
              built.lastYear.length === dim &&
              built.best.length === dim
            ) {
              return built;
            }
          }
          return buildComparePayload(dim, ctx.dayOfYear);
        }

        function pathFromPoints(pts) {"""

TREND_RENDER_PAYLOAD_OLD = "          var payload = buildComparePayload(dim, ctx.dayOfYear);"
TREND_RENDER_PAYLOAD_NEW = "          var payload = buildStoreComparePayload(ctx, dim);"

TREND_LISTENERS_OLD = """        render();
        document.addEventListener('annual:calendarDateChanged', render);
      }
      function initGraphDailyHistoricalWeekday() {"""

TREND_LISTENERS_NEW = """        render();
        var insightTrendDirty = false;
        function insightTrendVisible() {
          var overlay = document.getElementById('insight-overlay');
          var pane = document.getElementById('insight-pane-graph');
          if (overlay && overlay.hidden) return false;
          if (pane && pane.hidden) return false;
          return true;
        }
        function insightTrendRender() {
          if (!insightTrendVisible()) {
            insightTrendDirty = true;
            return;
          }
          insightTrendDirty = false;
          render();
        }
        [
          'annual:calendarDateChanged',
          'annual:dailyDateChanged',
          'kpi:dailyTargetModeChanged',
          'kpi:weekdayBaselineChanged',
          'kpi:annualPlanChanged',
          'insight:dateChanged',
        ].forEach(function (evName) {
          document.addEventListener(evName, insightTrendRender);
        });
        document.addEventListener('insight:tabChanged', function (ev) {
          if (ev && ev.detail && ev.detail.tab === 'graph' && insightTrendDirty) {
            insightTrendRender();
          }
        });
      }
      function initGraphDailyHistoricalWeekday() {"""

MARKER_BUILD_STORE = "function buildStoreComparePayload(ctx, dim)"
MARKER_COMPARE_BUILDER = "__buildAnnualCompareTrendPayload"

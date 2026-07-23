"""Insight Graph Annual Graph1 — 累計折れ線の実データ化 + Insight 内日付追従.

Graph2 / CSS / 上部棒グラフは触らない。
"""

from __future__ import annotations

# Graph1 のみ（Graph2 より先に出る最初の getFocusYearContext）
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
            target: target,
            actual: actual,
            dailyTarget: dailyTarget,
            dailyActual: dailyActual,
            todayDay: endDay
          };
        }

        function pathFromPoints(pts) {"""

TREND_BUILD_STORE_NEW = """          return {
            target: target,
            actual: actual,
            dailyTarget: dailyTarget,
            dailyActual: dailyActual,
            todayDay: endDay
          };
        }

        function buildStorePayload(ctx, dim) {
          var cutoffIso = resolveInsightTrendIso();
          if (typeof window.__buildAnnualCumulativeTrendPayload === 'function') {
            var built = window.__buildAnnualCumulativeTrendPayload(ctx.year, cutoffIso);
            if (
              built &&
              built.target &&
              built.actual &&
              built.target.length === dim &&
              built.actual.length === dim
            ) {
              return built;
            }
          }
          return buildDemoPayload(dim, ctx.dayOfYear);
        }

        function pathFromPoints(pts) {"""

TREND_RENDER_PAYLOAD_OLD = "          var payload = buildDemoPayload(dim, ctx.dayOfYear);"
TREND_RENDER_PAYLOAD_NEW = "          var payload = buildStorePayload(ctx, dim);"

TREND_LISTENERS_OLD = """        render();
        document.addEventListener('annual:calendarDateChanged', render);
      }


      function initGraphAnnualCumulativeTrendGraph2() {"""

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


      function initGraphAnnualCumulativeTrendGraph2() {"""

MARKER_RESOLVE_ISO = "function resolveInsightTrendIso()"
MARKER_BUILD_STORE = "function buildStorePayload(ctx, dim)"
MARKER_ANNUAL_BUILDER = "__buildAnnualCumulativeTrendPayload"

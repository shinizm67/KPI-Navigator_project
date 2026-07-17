"""Insight Graph Monthly — 累計折れ線の実データ化 + Insight 内日付追従."""

from __future__ import annotations

TREND_GET_FOCUS_OLD = """        function getFocusYearMonth() {
          var data = window.__ANNUAL_DATA || {};
          var iso = data.daily && data.daily.selectedDate;"""

TREND_GET_FOCUS_NEW = """        function resolveInsightTrendIso() {
          if (window.__INSIGHT_SELECTED_ISO) return window.__INSIGHT_SELECTED_ISO;
          var data = window.__ANNUAL_DATA || {};
          return data.daily && data.daily.selectedDate;
        }

        function getFocusYearMonth() {
          var iso = resolveInsightTrendIso();"""

TREND_BUILD_STORE_OLD = """          var todayDay = Math.min(dim, 18);
          return {
            target: target,
            actual: actual,
            dailyTarget: dailyTarget,
            dailyActual: dailyActual,
            todayDay: todayDay
          };
        }

        function pathFromPoints(pts) {"""

TREND_BUILD_STORE_NEW = """          var todayDay = Math.min(dim, 18);
          return {
            target: target,
            actual: actual,
            dailyTarget: dailyTarget,
            dailyActual: dailyActual,
            todayDay: todayDay
          };
        }

        function buildStorePayload(ym, dim) {
          var cutoffIso = resolveInsightTrendIso();
          if (typeof window.__buildMonthlyCumulativeTrendPayload === 'function') {
            var built = window.__buildMonthlyCumulativeTrendPayload(ym.year, ym.month, cutoffIso);
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
          return buildDemoPayload(dim);
        }

        function pathFromPoints(pts) {"""

TREND_RENDER_PAYLOAD_OLD = "          var payload = buildDemoPayload(dim);"
TREND_RENDER_PAYLOAD_NEW = "          var payload = buildStorePayload(ym, dim);"

TREND_LISTENERS_OLD = """        render();
        document.addEventListener('annual:calendarDateChanged', render);
      }"""

TREND_LISTENERS_NEW = """        render();
        [
          'annual:calendarDateChanged',
          'annual:dailyDateChanged',
          'kpi:dailyTargetModeChanged',
          'kpi:weekdayBaselineChanged',
          'kpi:annualPlanChanged',
          'insight:dateChanged',
        ].forEach(function (evName) {
          document.addEventListener(evName, render);
        });
      }"""

MARKER_RESOLVE_ISO = "function resolveInsightTrendIso()"
MARKER_BUILD_STORE = "function buildStorePayload(ym, dim)"

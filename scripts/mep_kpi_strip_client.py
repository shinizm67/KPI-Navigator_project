"""MEP Analyze KPI strip — cumulative mtd/ytd via __computeTwMetricsForIso (Cockpit-aligned)."""

from __future__ import annotations

MEP_KPI_STRIP_MARKER = "/* KPI-MEP-STRIP */"
MEP_KPI_STRIP_END = "/* END KPI-MEP-STRIP */"

IS_TIMELINE_BIZ_DAY = """      function isTimelineBusinessDay(iso, bmap, isWeekend) {
        if (Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
        return !isWeekend;
      }"""


def mep_kpi_strip_js() -> str:
    return f"""      {MEP_KPI_STRIP_MARKER}
      function mepKpiAsOfIso() {{
        var end = monthCutoffDate();
        return dateToIso(end);
      }}
      function getKpiSummary() {{
        var empty = {{
          monthly: {{ actual: 0, target: 0, diff: 0, rate: 0, hasPlan: false }},
          annual: {{ actual: 0, target: 0, diff: 0, rate: 0, hasPlan: false }}
        }};
        var iso = mepKpiAsOfIso();
        if (!iso || typeof window.__computeTwMetricsForIso !== 'function') {{
          return empty;
        }}
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var m = window.__computeTwMetricsForIso(iso);
        if (!m) return empty;
        var hasPlan = !!m.hasPlan;
        var monthlyActual = Math.round(Number(m.mtdA) || 0);
        var annualActual = Math.round(Number(m.ytdA) || 0);
        var monthlyTarget = hasPlan ? Math.round(Number(m.mtdT) || 0) : 0;
        var annualTarget = hasPlan ? Math.round(Number(m.ytdT) || 0) : 0;
        return {{
          monthly: {{
            actual: monthlyActual,
            target: monthlyTarget,
            diff: monthlyActual - monthlyTarget,
            rate: monthlyTarget > 0 ? (monthlyActual / monthlyTarget) * 100 : 0,
            hasPlan: hasPlan
          }},
          annual: {{
            actual: annualActual,
            target: annualTarget,
            diff: annualActual - annualTarget,
            rate: annualTarget > 0 ? (annualActual / annualTarget) * 100 : 0,
            hasPlan: hasPlan
          }}
        }};
      }}
      function bindMepKpiStripRefresh() {{
        if (window.__MEP_KPI_STRIP_BOUND__) return;
        window.__MEP_KPI_STRIP_BOUND__ = true;
        [
          'kpi:dailySalesChanged',
          'kpi:dailyTargetModeChanged',
          'kpi:annualPlanChanged',
          'kpi:weekdayBaselineChanged',
          'annual:salesMapChanged',
          'annual:calendarYearChanged',
          'kpi:selectedDateChanged'
        ].forEach(function (name) {{
          document.addEventListener(name, function () {{
            if (typeof renderKpiStrip === 'function') renderKpiStrip();
          }});
        }});
      }}
      {MEP_KPI_STRIP_END}"""

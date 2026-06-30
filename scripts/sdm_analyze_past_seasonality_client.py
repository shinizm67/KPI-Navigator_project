"""Sales Data Analyze — Seasonality % and avg daily from past-year averages."""

from __future__ import annotations

ANALYZE_MODEL_MARKER = "/* KPI-SDM-ANALYZE-PAST-SEASONALITY */"
ANALYZE_MODEL_END = "/* END KPI-SDM-ANALYZE-PAST-SEASONALITY */"

ANALYZE_MODEL_OLD = """      function buildSalesDataAnalyzeModel(y) {
        var all = gatherYearDays(y);
        var annualSales = getAnnualTargetForAnalyze(y);
        var monthlySales = getMonthlyCumulativeSalesByMonth(y);
        var totalBD = 0;
        var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        for (var i = 0; i < all.length; i++) {
          var item = all[i];
          var defs = getRowDefaults(item.iso, item.isWk);
          if (!defs.off) {
            totalBD++;
            monthlyBD[item.m0]++;
          }
        }
        var avgDaily = annualSales != null && totalBD > 0 ? annualSales / totalBD : null;
        var months = [];
        for (var m0 = 0; m0 < 12; m0++) {
          var baseline = avgDaily != null && monthlyBD[m0] > 0 ? avgDaily * monthlyBD[m0] : null;
          var sales = monthlySales[m0];
          var seasonality = baseline != null && baseline > 0 ? (sales / baseline) * 100 : null;
          months.push({
            m0: m0,
            bd: monthlyBD[m0],
            sales: sales,
            baseline: baseline,
            seasonality: seasonality
          });
        }
        return {
          year: y,
          annualSales: annualSales,
          totalBD: totalBD,
          avgDaily: avgDaily,
          months: months
        };
      }"""


def analyze_model_js() -> str:
    return f"""      {ANALYZE_MODEL_MARKER}
      function buildSalesDataAnalyzeModel(y) {{
        var all = gatherYearDays(y);
        var operatingYear = getOperatingYear();
        var annualSales = getAnnualTargetForAnalyze(y);
        var totalBD = 0;
        var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        for (var i = 0; i < all.length; i++) {{
          var item = all[i];
          var defs = getRowDefaults(item.iso, item.isWk);
          if (!defs.off) {{
            totalBD++;
            monthlyBD[item.m0]++;
          }}
        }}
        var avgDaily = null;
        var seasonalityMonths = null;
        if (window.KpiYearStore && y === operatingYear) {{
          if (typeof KpiYearStore.computePastAverageDailySales === 'function') {{
            avgDaily = KpiYearStore.computePastAverageDailySales(operatingYear, 2);
          }}
          if (typeof KpiYearStore.computeAverageSeasonalityPct === 'function') {{
            var seasonPack = KpiYearStore.computeAverageSeasonalityPct(operatingYear, 2);
            seasonalityMonths = seasonPack ? seasonPack.months : null;
          }}
        }}
        if (avgDaily == null && annualSales != null && totalBD > 0) {{
          avgDaily = annualSales / totalBD;
        }}
        var months = [];
        for (var m0 = 0; m0 < 12; m0++) {{
          var baseline = avgDaily != null && monthlyBD[m0] > 0 ? avgDaily * monthlyBD[m0] : null;
          var seasonality =
            seasonalityMonths && seasonalityMonths[m0] != null ? seasonalityMonths[m0] : null;
          months.push({{
            m0: m0,
            bd: monthlyBD[m0],
            sales: null,
            baseline: baseline,
            seasonality: seasonality,
          }});
        }}
        return {{
          year: y,
          annualSales: annualSales,
          totalBD: totalBD,
          avgDaily: avgDaily,
          months: months,
        }};
      }}
      {ANALYZE_MODEL_END}"""

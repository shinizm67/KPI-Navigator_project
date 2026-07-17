"""Insight — MEP dailyExpenses の月次読取専用（書込・UI 非接触）."""

from __future__ import annotations

INSIGHT_EXPENSE_READ_MARKER = "/* KPI-INSIGHT-EXPENSE-READ */"
INSIGHT_EXPENSE_READ_END = "/* END KPI-INSIGHT-EXPENSE-READ */"


def insight_expense_read_js() -> str:
    return f"""    {INSIGHT_EXPENSE_READ_MARKER}
    (function () {{
      var MEP_CATALOG_KEY = 'kpiNavigator.plLineCatalog';
      var MEP_FALLBACK_FIXED = [
        'exp_rent',
        'exp_fixed_labor',
        'exp_non_life_insurance',
      ];
      var MEP_FALLBACK_VARIABLE = [
        'exp_food_cost',
        'exp_drink_cost',
        'exp_supplies',
        'exp_misc',
        'exp_electric',
        'exp_gas',
        'exp_water',
        'exp_communication',
        'exp_advertising',
        'exp_outsource',
        'exp_repair',
        'exp_travel',
        'exp_entertainment',
        'exp_fee',
        'exp_tax',
        'exp_other',
      ];

      function pad2(n) {{
        return (n < 10 ? '0' : '') + n;
      }}

      function plCatalogLines() {{
        try {{
          var raw =
            window.__KPI_DATA_GATEWAY && window.__KPI_DATA_GATEWAY.getJson(MEP_CATALOG_KEY);
          if (raw && Array.isArray(raw.lines)) return raw.lines;
        }} catch (_e) {{}}
        return null;
      }}

      function lineIdsForBucket(bucket) {{
        var lines = plCatalogLines();
        var out = [];
        if (lines && lines.length) {{
          lines.forEach(function (line) {{
            if (!line || line.active === false) return;
            if (line.bucket === bucket && line.lineId) out.push(String(line.lineId));
          }});
        }}
        if (!out.length) {{
          out = (bucket === 'fixed' ? MEP_FALLBACK_FIXED : MEP_FALLBACK_VARIABLE).slice();
        }}
        return out;
      }}

      function sumBucketThroughMonth(dailyExpenses, rowIds, year, month, throughDay) {{
        var y = Number(year);
        var m = Number(month);
        var dayMax = Number(throughDay);
        if (!Number.isFinite(y) || !Number.isFinite(m) || m < 1 || m > 12) {{
          return {{ sum: 0, hasData: false }};
        }}
        var dim = new Date(y, m, 0).getDate();
        if (!Number.isFinite(dayMax) || dayMax < 1) dayMax = dim;
        if (dayMax > dim) dayMax = dim;
        var map = dailyExpenses && typeof dailyExpenses === 'object' ? dailyExpenses : {{}};
        var sum = 0;
        var hasData = false;
        for (var d = 1; d <= dayMax; d++) {{
          var iso = y + '-' + pad2(m) + '-' + pad2(d);
          (rowIds || []).forEach(function (rowId) {{
            var byRow = map[rowId];
            if (!byRow || !Object.prototype.hasOwnProperty.call(byRow, iso)) return;
            hasData = true;
            var n = Number(byRow[iso]);
            if (Number.isFinite(n)) sum += n;
          }});
        }}
        return {{ sum: Math.round(sum), hasData: hasData }};
      }}

      /**
       * Read-only: MEP `years.{{Y}}.dailyExpenses` month totals (fixed / variable).
       * Does NOT merge PL monthly amounts. throughDay optional (1–31); omit = full month.
       * @returns {{ fixed, variable, total, hasData, source }}
       */
      window.__insightReadMonthExpense = function (year, month, throughDay) {{
        var empty = {{
          fixed: 0,
          variable: 0,
          total: 0,
          hasData: false,
          source: 'mep-daily',
        }};
        if (!window.KpiYearStore || typeof KpiYearStore.loadMepYearPayload !== 'function') {{
          return empty;
        }}
        var payload = KpiYearStore.loadMepYearPayload(year);
        var dailyExpenses = (payload && payload.dailyExpenses) || {{}};
        var fixedIds = lineIdsForBucket('fixed');
        var variableIds = lineIdsForBucket('variable');
        var fixed = sumBucketThroughMonth(dailyExpenses, fixedIds, year, month, throughDay);
        var variable = sumBucketThroughMonth(
          dailyExpenses,
          variableIds,
          year,
          month,
          throughDay
        );
        return {{
          fixed: fixed.sum,
          variable: variable.sum,
          total: fixed.sum + variable.sum,
          hasData: fixed.hasData || variable.hasData,
          source: 'mep-daily',
        }};
      }};
    }})();
    {INSIGHT_EXPENSE_READ_END}
"""

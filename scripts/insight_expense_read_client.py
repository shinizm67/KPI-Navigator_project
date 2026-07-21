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

      function categoryLineIds() {{
        var lines = plCatalogLines() || [];
        var out = {{
          food: ['exp_food_cost'],
          drink: ['exp_drink_cost'],
          labor: ['exp_fixed_labor', 'exp_variable_labor'],
        }};
        if (!lines.length) return out;
        function collect(testFn, fallback) {{
          var ids = [];
          lines.forEach(function (line) {{
            if (!line || line.active === false || !line.lineId) return;
            if (testFn(line)) ids.push(String(line.lineId));
          }});
          return ids.length ? ids : fallback.slice();
        }}
        out.food = collect(
          function (line) {{ return String(line.lineId) === 'exp_food_cost'; }},
          out.food
        );
        out.drink = collect(
          function (line) {{ return String(line.lineId) === 'exp_drink_cost'; }},
          out.drink
        );
        out.labor = collect(
          function (line) {{
            var id = String(line.lineId);
            return id === 'exp_fixed_labor' || id === 'exp_variable_labor';
          }},
          out.labor
        );
        return out;
      }}

      function sumBucketAtIso(dailyExpenses, rowIds, iso) {{
        var map = dailyExpenses && typeof dailyExpenses === 'object' ? dailyExpenses : {{}};
        var sum = 0;
        var hasData = false;
        (rowIds || []).forEach(function (rowId) {{
          var byRow = map[rowId];
          if (!byRow || !Object.prototype.hasOwnProperty.call(byRow, iso)) return;
          hasData = true;
          var n = Number(byRow[iso]);
          if (Number.isFinite(n)) sum += n;
        }});
        return {{ sum: Math.round(sum), hasData: hasData }};
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

      window.__insightReadExpenseSnapshot = function (iso) {{
        var empty = {{
          hasData: false,
          day: {{ fixed: 0, variable: 0, total: 0, food: 0, drink: 0, misc: 0, labor: 0 }},
          month: {{ fixed: 0, variable: 0, total: 0, food: 0, drink: 0, misc: 0, labor: 0 }},
          year: {{ fixed: 0, variable: 0, total: 0, food: 0, drink: 0, misc: 0, labor: 0 }},
          source: 'mep-daily',
        }};
        if (!iso || !/^\\d{4}-\\d{2}-\\d{2}$/.test(String(iso))) return empty;
        if (!window.KpiYearStore || typeof KpiYearStore.loadMepYearPayload !== 'function') {{
          return empty;
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) return empty;

        var payload = KpiYearStore.loadMepYearPayload(y);
        var dailyExpenses = (payload && payload.dailyExpenses) || {{}};
        var fixedIds = lineIdsForBucket('fixed');
        var variableIds = lineIdsForBucket('variable');
        var cat = categoryLineIds();

        var dayFixed = sumBucketAtIso(dailyExpenses, fixedIds, iso);
        var dayVariable = sumBucketAtIso(dailyExpenses, variableIds, iso);
        var dayFood = sumBucketAtIso(dailyExpenses, cat.food, iso);
        var dayDrink = sumBucketAtIso(dailyExpenses, cat.drink, iso);
        var dayLabor = sumBucketAtIso(dailyExpenses, cat.labor, iso);

        var monthFixed = sumBucketThroughMonth(dailyExpenses, fixedIds, y, month, day);
        var monthVariable = sumBucketThroughMonth(dailyExpenses, variableIds, y, month, day);
        var monthFood = sumBucketThroughMonth(dailyExpenses, cat.food, y, month, day);
        var monthDrink = sumBucketThroughMonth(dailyExpenses, cat.drink, y, month, day);
        var monthLabor = sumBucketThroughMonth(dailyExpenses, cat.labor, y, month, day);

        var yearFixed = 0;
        var yearVariable = 0;
        var yearFood = 0;
        var yearDrink = 0;
        var yearLabor = 0;
        var yearHasData = false;
        for (var m = 1; m <= month; m++) {{
          var td = m === month ? day : 31;
          var yf = sumBucketThroughMonth(dailyExpenses, fixedIds, y, m, td);
          var yv = sumBucketThroughMonth(dailyExpenses, variableIds, y, m, td);
          var yfood = sumBucketThroughMonth(dailyExpenses, cat.food, y, m, td);
          var ydrink = sumBucketThroughMonth(dailyExpenses, cat.drink, y, m, td);
          var ylabor = sumBucketThroughMonth(dailyExpenses, cat.labor, y, m, td);
          yearFixed += yf.sum;
          yearVariable += yv.sum;
          yearFood += yfood.sum;
          yearDrink += ydrink.sum;
          yearLabor += ylabor.sum;
          yearHasData = yearHasData || yf.hasData || yv.hasData || yfood.hasData || ydrink.hasData || ylabor.hasData;
        }}

        var dayTotal = dayFixed.sum + dayVariable.sum;
        var monthTotal = monthFixed.sum + monthVariable.sum;
        var yearTotal = Math.round(yearFixed + yearVariable);
        var out = {{
          hasData:
            dayFixed.hasData ||
            dayVariable.hasData ||
            monthFixed.hasData ||
            monthVariable.hasData ||
            yearHasData,
          day: {{
            fixed: dayFixed.sum,
            variable: dayVariable.sum,
            total: dayTotal,
            food: dayFood.sum,
            drink: dayDrink.sum,
            misc: Math.max(0, dayVariable.sum - dayFood.sum - dayDrink.sum),
            labor: dayLabor.sum,
          }},
          month: {{
            fixed: monthFixed.sum,
            variable: monthVariable.sum,
            total: monthTotal,
            food: monthFood.sum,
            drink: monthDrink.sum,
            misc: Math.max(0, monthVariable.sum - monthFood.sum - monthDrink.sum),
            labor: monthLabor.sum,
          }},
          year: {{
            fixed: Math.round(yearFixed),
            variable: Math.round(yearVariable),
            total: yearTotal,
            food: Math.round(yearFood),
            drink: Math.round(yearDrink),
            misc: Math.max(0, Math.round(yearVariable - yearFood - yearDrink)),
            labor: Math.round(yearLabor),
          }},
          source: 'mep-daily',
        }};
        return out;
      }};
    }})();
    {INSIGHT_EXPENSE_READ_END}
"""

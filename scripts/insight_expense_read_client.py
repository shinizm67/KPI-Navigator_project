"""Insight — PL 表 + MEP と同一ソースから支出を読取（Insight / PL Insight 整合）."""

from __future__ import annotations

INSIGHT_EXPENSE_READ_MARKER = "/* KPI-INSIGHT-EXPENSE-READ */"
INSIGHT_EXPENSE_READ_END = "/* END KPI-INSIGHT-EXPENSE-READ */"


def insight_expense_read_js() -> str:
    return f"""    {INSIGHT_EXPENSE_READ_MARKER}
    (function () {{
      var YEAR_STORE_KEY = 'kpiNavigator.kpiYearStore';
      var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
      var EXP_PREFIX = 'kpi-pl-expenses-v1:';
      var ADJ_PREFIX = 'kpi-pl-expense-adjustments-v1:';

      var allocCache = {{}};
      var catalogCache = null;
      var monthlyMapCache = {{}};
      var adjMapCache = {{}};
      var sumThroughMonthCache = {{}};
      var expenseSnapshotCache = {{}};

      function invalidateInsightExpenseCaches() {{
        allocCache = {{}};
        catalogCache = null;
        monthlyMapCache = {{}};
        adjMapCache = {{}};
        sumThroughMonthCache = {{}};
        expenseSnapshotCache = {{}};
        window.__INSIGHT_YEAR_EXPENSE_CACHE = {{}};
      }}

      function pad2(n) {{
        return (n < 10 ? '0' : '') + n;
      }}

      function isoOf(year, month, day) {{
        return year + '-' + pad2(month) + '-' + pad2(day);
      }}

      function getJson(key) {{
        try {{
          var g = window.__KPI_DATA_GATEWAY;
          if (g && typeof g.getJson === 'function') return g.getJson(key);
        }} catch (_e) {{}}
        try {{
          var raw = localStorage.getItem(key);
          return raw ? JSON.parse(raw) : null;
        }} catch (_e2) {{
          return null;
        }}
      }}

      function store() {{
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          try {{ KpiYearStore.syncToAnnualDaily(); }} catch (_e) {{}}
        }}
        var s = getJson(YEAR_STORE_KEY);
        return s && typeof s === 'object' ? s : null;
      }}

      function yearRec(s, year) {{
        if (!s || !s.years) return null;
        return s.years[year] || s.years[String(year)] || null;
      }}

      function catalog() {{
        if (catalogCache) return catalogCache;
        var lines = [];
        try {{
          var raw = getJson(CATALOG_KEY);
          if (raw && Array.isArray(raw.lines)) lines = raw.lines;
        }} catch (_e) {{}}
        catalogCache = (lines || []).filter(function (line) {{
          return line && line.lineId && line.active !== false;
        }});
        return catalogCache;
      }}

      function lineStyle(line) {{
        return (line.resolvedInputStyle || line.inputStyle || 'monthly') === 'daily'
          ? 'daily'
          : 'monthly';
      }}

      function monthlyMap(year) {{
        if (monthlyMapCache[year]) return monthlyMapCache[year];
        var m = getJson(EXP_PREFIX + year);
        monthlyMapCache[year] = m && typeof m === 'object' ? m : {{}};
        return monthlyMapCache[year];
      }}

      function adjMap(year) {{
        if (adjMapCache[year]) return adjMapCache[year];
        var m = getJson(ADJ_PREFIX + year);
        adjMapCache[year] = m && typeof m === 'object' ? m : {{}};
        return adjMapCache[year];
      }}

      function annualDailyMaps() {{
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        return {{
          businessDayByDate: daily.businessDayByDate || {{}},
          targetSalesByDate: daily.targetSalesByDate || {{}},
        }};
      }}

      function isBizDay(iso) {{
        if (typeof window.__isTwBusinessDay === 'function') return !!window.__isTwBusinessDay(iso);
        var maps = annualDailyMaps();
        var bmap = maps.businessDayByDate;
        var tmap = maps.targetSalesByDate;
        if (Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
        if (Object.prototype.hasOwnProperty.call(tmap, iso)) {{
          var n = Number(tmap[iso]);
          return Number.isFinite(n) ? n !== 0 : true;
        }}
        return true;
      }}

      function listBizDayIsos(year, month0) {{
        var dim = new Date(year, month0 + 1, 0).getDate();
        var out = [];
        for (var d = 1; d <= dim; d++) {{
          var iso = isoOf(year, month0 + 1, d);
          if (isBizDay(iso)) out.push(iso);
        }}
        return out;
      }}

      function allocateAcrossBizDays(amount, bizIsos) {{
        var amt = Math.round(Number(amount) || 0);
        var byDate = {{}};
        if (!bizIsos || !bizIsos.length || amt === 0) return byDate;
        var n = bizIsos.length;
        var base = Math.floor(amt / n);
        var rem = amt - base * n;
        for (var i = 0; i < n; i++) {{
          byDate[bizIsos[i]] = base + (i === n - 1 ? rem : 0);
        }}
        return byDate;
      }}

      function allocForMonth(year, month0) {{
        var key = year + '-' + month0;
        if (allocCache[key]) return allocCache[key];
        var out = {{}};
        var bizIsos = listBizDayIsos(year, month0);
        catalog().forEach(function (line) {{
          if (lineStyle(line) !== 'monthly') return;
          var mapKey = line.lineId + ':' + month0;
          var monthlyAmount = Object.prototype.hasOwnProperty.call(monthlyMap(year), mapKey)
            ? Math.round(Number(monthlyMap(year)[mapKey]) || 0)
            : 0;
          out[line.lineId] = allocateAcrossBizDays(monthlyAmount, bizIsos);
        }});
        allocCache[key] = out;
        return out;
      }}

      function lineDayAmount(s, year, month0, isoStr, line, alloc) {{
        if (lineStyle(line) === 'daily') {{
          var rec = yearRec(s, year);
          var de = rec && rec.dailyExpenses && rec.dailyExpenses[line.lineId];
          if (!de || !Object.prototype.hasOwnProperty.call(de, isoStr)) return 0;
          var v = Number(de[isoStr]);
          return Number.isFinite(v) ? v : 0;
        }}
        var byDate = alloc[line.lineId];
        if (!byDate) return 0;
        var mv = Number(byDate[isoStr]);
        return Number.isFinite(mv) ? mv : 0;
      }}

      function lineMonthAmount(s, year, month0, line) {{
        if (lineStyle(line) === 'monthly') {{
          var v = Number(monthlyMap(year)[line.lineId + ':' + month0]);
          return Number.isFinite(v) ? v : 0;
        }}
        var rec = yearRec(s, year);
        var de = rec && rec.dailyExpenses && rec.dailyExpenses[line.lineId];
        var sum = 0;
        var has = false;
        if (de) {{
          var dim = new Date(year, month0 + 1, 0).getDate();
          for (var d = 1; d <= dim; d++) {{
            var isoStr = isoOf(year, month0 + 1, d);
            if (!Object.prototype.hasOwnProperty.call(de, isoStr)) continue;
            has = true;
            var val = Number(de[isoStr]);
            if (Number.isFinite(val)) sum += val;
          }}
        }}
        var adj = Number(adjMap(year)[line.lineId + ':' + month0]);
        if (Number.isFinite(adj) && adj !== 0) {{
          has = true;
          sum += adj;
        }}
        return has ? Math.round(sum) : 0;
      }}

      function lineHasMonthData(s, year, month0, line) {{
        return lineMonthAmount(s, year, month0, line) !== 0;
      }}

      function lineHasAnyData(s, year, line) {{
        for (var m0 = 0; m0 < 12; m0++) {{
          if (lineHasMonthData(s, year, m0, line)) return true;
        }}
        return false;
      }}

      function isFoodLine(line) {{
        var a = line.expenseAttribute;
        if (a === 'food_cost') return true;
        return line.lineId === 'exp_food_cost';
      }}

      function isDrinkLine(line) {{
        var a = line.expenseAttribute;
        if (a === 'drink_cost') return true;
        return line.lineId === 'exp_drink_cost';
      }}

      function isLaborLine(line) {{
        var a = line.expenseAttribute;
        if (a === 'salaries_wages' || a === 'variable_labor' || a === 'labor_related') return true;
        return line.lineId === 'exp_fixed_labor' || line.lineId === 'exp_variable_labor';
      }}

      function sumDayMetrics(isoStr) {{
        var parts = String(isoStr).split('-');
        var year = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        var month0 = month - 1;
        var s = store();
        var emptyScope = {{
          fixed: 0,
          variable: 0,
          total: 0,
          food: 0,
          drink: 0,
          misc: 0,
          labor: 0,
          hasData: false,
        }};
        if (!s || !Number.isFinite(year) || !Number.isFinite(month) || !Number.isFinite(day)) {{
          return emptyScope;
        }}
        var alloc = allocForMonth(year, month0);
        var fixed = 0;
        var variable = 0;
        var food = 0;
        var drink = 0;
        var labor = 0;
        var hasData = false;
        catalog().forEach(function (line) {{
          if (lineHasMonthData(s, year, month0, line)) hasData = true;
          var amt = lineDayAmount(s, year, month0, isoStr, line, alloc);
          if (!amt) return;
          if (line.bucket === 'fixed') fixed += amt;
          else variable += amt;
          if (isFoodLine(line)) food += amt;
          if (isDrinkLine(line)) drink += amt;
          if (isLaborLine(line)) labor += amt;
        }});
        return {{
          fixed: Math.round(fixed),
          variable: Math.round(variable),
          total: Math.round(fixed + variable),
          food: Math.round(food),
          drink: Math.round(drink),
          misc: Math.max(0, Math.round(variable - food - drink)),
          labor: Math.round(labor),
          hasData: hasData,
        }};
      }}

      function packSumThrough(fixed, variable, food, drink, labor, hasData) {{
        return {{
          fixed: Math.round(fixed),
          variable: Math.round(variable),
          total: Math.round(fixed + variable),
          food: Math.round(food),
          drink: Math.round(drink),
          misc: Math.max(0, Math.round(variable - food - drink)),
          labor: Math.round(labor),
          hasData: !!hasData,
        }};
      }}

      function sumThroughMonth(year, month, throughDay) {{
        var y = Number(year);
        var m = Number(month);
        var dayMax = Number(throughDay);
        if (!Number.isFinite(y) || !Number.isFinite(m) || m < 1 || m > 12) {{
          return {{ fixed: 0, variable: 0, total: 0, food: 0, drink: 0, misc: 0, labor: 0, hasData: false }};
        }}
        var dim = new Date(y, m, 0).getDate();
        if (!Number.isFinite(dayMax) || dayMax < 1) dayMax = dim;
        if (dayMax > dim) dayMax = dim;
        var cacheKey = y + '-' + m + '-' + dayMax;
        if (Object.prototype.hasOwnProperty.call(sumThroughMonthCache, cacheKey)) {{
          return sumThroughMonthCache[cacheKey];
        }}

        // 日付スクラブ向け: 前後1日のキャッシュから増分（Annual YTD のボトルネック緩和）
        if (dayMax > 1) {{
          var prevKey = y + '-' + m + '-' + (dayMax - 1);
          if (Object.prototype.hasOwnProperty.call(sumThroughMonthCache, prevKey)) {{
            var prev = sumThroughMonthCache[prevKey];
            var addSnap = sumDayMetrics(isoOf(y, m, dayMax));
            var fwd = packSumThrough(
              prev.fixed + addSnap.fixed,
              prev.variable + addSnap.variable,
              prev.food + addSnap.food,
              prev.drink + addSnap.drink,
              prev.labor + addSnap.labor,
              prev.hasData
            );
            sumThroughMonthCache[cacheKey] = fwd;
            return fwd;
          }}
        }}
        if (dayMax < dim) {{
          var nextKey = y + '-' + m + '-' + (dayMax + 1);
          if (Object.prototype.hasOwnProperty.call(sumThroughMonthCache, nextKey)) {{
            var next = sumThroughMonthCache[nextKey];
            var subSnap = sumDayMetrics(isoOf(y, m, dayMax + 1));
            var back = packSumThrough(
              next.fixed - subSnap.fixed,
              next.variable - subSnap.variable,
              next.food - subSnap.food,
              next.drink - subSnap.drink,
              next.labor - subSnap.labor,
              next.hasData
            );
            sumThroughMonthCache[cacheKey] = back;
            return back;
          }}
        }}

        var fixed = 0;
        var variable = 0;
        var food = 0;
        var drink = 0;
        var labor = 0;
        var hasData = false;
        var s = store();
        catalog().forEach(function (line) {{
          if (lineHasMonthData(s, y, m - 1, line)) hasData = true;
        }});
        for (var d = 1; d <= dayMax; d++) {{
          var snap = sumDayMetrics(isoOf(y, m, d));
          fixed += snap.fixed;
          variable += snap.variable;
          food += snap.food;
          drink += snap.drink;
          labor += snap.labor;
        }}
        var result = packSumThrough(fixed, variable, food, drink, labor, hasData);
        sumThroughMonthCache[cacheKey] = result;
        return result;
      }}

      /**
       * Read-only: PL 表 + MEP と同一ロジックで月次支出（fixed / variable）を返す。
       * monthly-style 行は kpi-pl-expenses-v1 を営業日割り、daily-style 行は dailyExpenses。
       */
      window.__insightReadMonthExpense = function (year, month, throughDay) {{
        var scope = sumThroughMonth(year, month, throughDay);
        return {{
          fixed: scope.fixed,
          variable: scope.variable,
          total: scope.total,
          hasData: scope.hasData,
          source: 'pl-unified',
        }};
      }};

      window.__insightReadExpenseSnapshot = function (iso) {{
        var emptyDay = {{
          fixed: 0,
          variable: 0,
          total: 0,
          food: 0,
          drink: 0,
          misc: 0,
          labor: 0,
        }};
        var empty = {{
          hasData: false,
          day: emptyDay,
          month: emptyDay,
          year: emptyDay,
          source: 'pl-unified',
        }};
        if (!iso || !/^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(String(iso))) return empty;
        if (Object.prototype.hasOwnProperty.call(expenseSnapshotCache, iso)) {{
          return expenseSnapshotCache[iso];
        }}
        var parts = String(iso).split('-');
        var y = Number(parts[0]);
        var month = Number(parts[1]);
        var day = Number(parts[2]);
        if (!Number.isFinite(y) || !Number.isFinite(month) || !Number.isFinite(day)) return empty;

        var dayScope = sumDayMetrics(iso);
        var monthScope = sumThroughMonth(y, month, day);
        var yearFixed = 0;
        var yearVariable = 0;
        var yearFood = 0;
        var yearDrink = 0;
        var yearLabor = 0;
        var yearHasData = false;
        for (var m = 1; m <= month; m++) {{
          var td = m === month ? day : new Date(y, m, 0).getDate();
          var ms = sumThroughMonth(y, m, td);
          yearFixed += ms.fixed;
          yearVariable += ms.variable;
          yearFood += ms.food;
          yearDrink += ms.drink;
          yearLabor += ms.labor;
          if (ms.hasData) yearHasData = true;
        }}

        var result = {{
          hasData: dayScope.hasData || monthScope.hasData || yearHasData,
          day: {{
            fixed: dayScope.fixed,
            variable: dayScope.variable,
            total: dayScope.total,
            food: dayScope.food,
            drink: dayScope.drink,
            misc: dayScope.misc,
            labor: dayScope.labor,
          }},
          month: {{
            fixed: monthScope.fixed,
            variable: monthScope.variable,
            total: monthScope.total,
            food: monthScope.food,
            drink: monthScope.drink,
            misc: monthScope.misc,
            labor: monthScope.labor,
          }},
          year: {{
            fixed: Math.round(yearFixed),
            variable: Math.round(yearVariable),
            total: Math.round(yearFixed + yearVariable),
            food: Math.round(yearFood),
            drink: Math.round(yearDrink),
            misc: Math.max(0, Math.round(yearVariable - yearFood - yearDrink)),
            labor: Math.round(yearLabor),
          }},
          source: 'pl-unified',
        }};
        expenseSnapshotCache[iso] = result;
        return result;
      }};

      [
        'kpi:mepDataChanged',
        'kpi:annualPlanChanged',
        'kpi:dailyTargetModeChanged',
        'kpi:weekdayBaselineChanged',
      ].forEach(function (evName) {{
        document.addEventListener(evName, invalidateInsightExpenseCaches);
      }});
    }})();
    {INSIGHT_EXPENSE_READ_END}
"""

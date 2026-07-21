"""PL Insight real-data provider (window.__plInsight).

Self-contained IIFE injected into the PL table page. It reads the same stores the
PL table itself uses, so the PL Insight overlay's numbers match the PL table
(source of truth):

- Income  = kpiNavigator.kpiYearStore.timeline.dailySales (placeholder 1234 excluded)
- Expenses= fixed + variable expense lines
    - monthly-style line -> kpi-pl-expenses-v1:{year}[lineId:month0]
    - daily-style line   -> sum of kpiYearStore.years.{Y}.dailyExpenses[lineId][iso]
                            (+ kpi-pl-expense-adjustments-v1:{year}[lineId:month0] to match display)
- Fixed   = bucket==='fixed' lines ; Expected = variable (= expenses - fixed)
- Profit  = income - expenses
- FL snapshot: Food = expenseAttribute food_cost/drink_cost ; Labor = salaries_wages/
  variable_labor/labor_related (fallback to well-known default lineIds).

Per-day expense for monthly-style lines uses the shared allocation engine
(window.__plPreviewMonthlyExpenseAllocation) so daily cumulative lines end at the
month total. Best Year = past year (< selected) with the highest annual income,
requiring >= 3 data years overall (else hidden).

Exposes ``window.__plInsight`` with buildArea1/2/3(iso), flDay/flYtd, bestYear,
canShowBestYear, bestYearNumber, monthMetrics/dayMetrics, resetCache. The big
"compare" overlay IIFE delegates its mock builders to these.
"""

from __future__ import annotations


def pl_insight_data_client_js() -> str:
    """JS snippet (plain string; single braces are fine)."""
    return """
    /* ===== PL Insight 実データ源（window.__plInsight） ===== */
    (function () {
      var PLACEHOLDER = 1234;
      var YEAR_STORE_KEY = 'kpiNavigator.kpiYearStore';
      var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
      var EXP_PREFIX = 'kpi-pl-expenses-v1:';
      var ADJ_PREFIX = 'kpi-pl-expense-adjustments-v1:';
      var METRICS = ['income', 'expenses', 'fixed', 'expected', 'profit'];
      var SERIES = ['thisYear', 'lastYear', 'bestYear'];

      var allocCache = {};      // 'year-month0' -> { lineId: {iso:amount} }
      var catalogCache = null;
      var monthlyMapCache = {}; // year -> {lineId:month0 -> amt}
      var adjMapCache = {};     // year -> {lineId:month0 -> amt}

      function resetCache() {
        allocCache = {};
        catalogCache = null;
        monthlyMapCache = {};
        adjMapCache = {};
      }

      function getJson(key) {
        var g = window.__KPI_DATA_GATEWAY;
        if (g && typeof g.getJson === 'function') {
          try { return g.getJson(key); } catch (_e) {}
        }
        try { var raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : null; }
        catch (_e2) { return null; }
      }
      function store() {
        var s = getJson(YEAR_STORE_KEY);
        return (s && typeof s === 'object') ? s : null;
      }
      function yearRec(s, year) {
        if (!s || !s.years) return null;
        return s.years[year] || s.years[String(year)] || null;
      }
      function catalog() {
        if (catalogCache) return catalogCache;
        var lines = [];
        if (typeof window.__plGetCatalogLines === 'function') {
          try { var a = window.__plGetCatalogLines(); if (a && a.length) lines = a; } catch (_e) {}
        }
        if (!lines.length) {
          var raw = getJson(CATALOG_KEY);
          if (raw && raw.lines && raw.lines.length) lines = raw.lines;
        }
        catalogCache = (lines || []).filter(function (l) { return l && l.lineId && l.active !== false; });
        return catalogCache;
      }
      function monthlyMap(year) {
        if (monthlyMapCache[year]) return monthlyMapCache[year];
        var m = getJson(EXP_PREFIX + year);
        monthlyMapCache[year] = (m && typeof m === 'object') ? m : {};
        return monthlyMapCache[year];
      }
      function adjMap(year) {
        if (adjMapCache[year]) return adjMapCache[year];
        var m = getJson(ADJ_PREFIX + year);
        adjMapCache[year] = (m && typeof m === 'object') ? m : {};
        return adjMapCache[year];
      }

      function pad2(n) { return n < 10 ? '0' + n : String(n); }
      function iso(year, month0, day) { return year + '-' + pad2(month0 + 1) + '-' + pad2(day); }
      function daysInMonth(year, month0) { return new Date(year, month0 + 1, 0).getDate(); }
      function isoParts(s) {
        var d = new Date(String(s || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        return { year: d.getFullYear(), month: d.getMonth() + 1, day: d.getDate() };
      }
      function lineStyle(line) {
        return (line.resolvedInputStyle || line.inputStyle || 'monthly') === 'daily' ? 'daily' : 'monthly';
      }
      function isFood(line) {
        var a = line.expenseAttribute;
        if (a === 'food_cost' || a === 'drink_cost') return true;
        return line.lineId === 'exp_food_cost' || line.lineId === 'exp_drink_cost';
      }
      function isLabor(line) {
        var a = line.expenseAttribute;
        if (a === 'salaries_wages' || a === 'variable_labor' || a === 'labor_related') return true;
        return line.lineId === 'exp_fixed_labor' || line.lineId === 'exp_variable_labor';
      }

      function dailySales(s, isoStr) {
        var ds = s && s.timeline && s.timeline.dailySales;
        if (!ds) return 0;
        var v = Number(ds[isoStr]);
        if (!isFinite(v) || v === PLACEHOLDER) return 0;
        return v;
      }

      /* monthly-style lines allocated across biz days (shared engine), cached. */
      function allocForMonth(year, month0) {
        var key = year + '-' + month0;
        if (allocCache[key]) return allocCache[key];
        var out = {};
        if (typeof window.__plPreviewMonthlyExpenseAllocation === 'function') {
          try {
            var prev = window.__plPreviewMonthlyExpenseAllocation({ year: year, month0: month0 });
            var months = prev && prev.months;
            if (months && months.length) {
              var mlines = months[0].lines || {};
              Object.keys(mlines).forEach(function (lid) { out[lid] = mlines[lid].byDate || {}; });
            }
          } catch (_e) {}
        }
        allocCache[key] = out;
        return out;
      }

      function lineDayAmount(s, year, month0, isoStr, line, alloc) {
        if (lineStyle(line) === 'daily') {
          var rec = yearRec(s, year);
          var de = rec && rec.dailyExpenses && rec.dailyExpenses[line.lineId];
          var v = de ? Number(de[isoStr]) : 0;
          return isFinite(v) ? v : 0;
        }
        var byDate = alloc[line.lineId];
        var mv = byDate ? Number(byDate[isoStr]) : 0;
        return isFinite(mv) ? mv : 0;
      }

      /* per-line month amount, matching the PL table cell (adjustment included for daily). */
      function lineMonthAmount(s, year, month0, line) {
        if (lineStyle(line) === 'monthly') {
          var v = Number(monthlyMap(year)[line.lineId + ':' + month0]);
          return isFinite(v) ? v : 0;
        }
        var rec = yearRec(s, year);
        var de = rec && rec.dailyExpenses && rec.dailyExpenses[line.lineId];
        var sum = 0;
        if (de) {
          var dim = daysInMonth(year, month0);
          for (var d = 1; d <= dim; d++) {
            var val = Number(de[iso(year, month0, d)]);
            if (isFinite(val)) sum += val;
          }
        }
        var adj = Number(adjMap(year)[line.lineId + ':' + month0]);
        if (isFinite(adj)) sum += adj;
        return sum;
      }

      function monthMetrics(year, month0) {
        var s = store();
        var income = 0;
        var dim = daysInMonth(year, month0);
        for (var d = 1; d <= dim; d++) income += dailySales(s, iso(year, month0, d));
        var fixed = 0, variable = 0;
        catalog().forEach(function (line) {
          var amt = lineMonthAmount(s, year, month0, line);
          if (!amt) return;
          if (line.bucket === 'fixed') fixed += amt; else variable += amt;
        });
        var expenses = fixed + variable;
        return { income: income, fixed: fixed, variable: variable, expenses: expenses,
                 expected: variable, profit: income - expenses };
      }

      function dayMetrics(year, month0, day) {
        var s = store();
        var alloc = allocForMonth(year, month0);
        var isoStr = iso(year, month0, day);
        var income = dailySales(s, isoStr);
        var fixed = 0, variable = 0;
        catalog().forEach(function (line) {
          var amt = lineDayAmount(s, year, month0, isoStr, line, alloc);
          if (!amt) return;
          if (line.bucket === 'fixed') fixed += amt; else variable += amt;
        });
        var expenses = fixed + variable;
        return { income: income, fixed: fixed, variable: variable, expenses: expenses,
                 expected: variable, profit: income - expenses };
      }

      function emptyChart() {
        var mk = function () { return { thisYear: [], lastYear: [], bestYear: [] }; };
        var daily = {}, cumulative = {};
        METRICS.forEach(function (k) { daily[k] = mk(); cumulative[k] = mk(); });
        return { daily: daily, cumulative: cumulative };
      }
      function fillDaily(chart, seriesKey, year, month0, count) {
        var cum = { income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 };
        for (var d = 1; d <= count; d++) {
          var m = dayMetrics(year, month0, d);
          METRICS.forEach(function (k) {
            chart.daily[k][seriesKey].push(m[k]);
            cum[k] += m[k];
            chart.cumulative[k][seriesKey].push(cum[k]);
          });
        }
      }
      function fillMonthly(chart, seriesKey, year, upToMonth) {
        var cum = { income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 };
        for (var mo = 0; mo < upToMonth; mo++) {
          var m = monthMetrics(year, mo);
          METRICS.forEach(function (k) {
            chart.daily[k][seriesKey].push(m[k]);
            cum[k] += m[k];
            chart.cumulative[k][seriesKey].push(cum[k]);
          });
        }
      }

      /* ---- Best Year (real) ---- */
      function yearsWithData(s) {
        var years = {};
        if (s) {
          var ds = s.timeline && s.timeline.dailySales;
          if (ds) Object.keys(ds).forEach(function (k) {
            var v = Number(ds[k]);
            if (isFinite(v) && v !== 0 && v !== PLACEHOLDER) years[k.slice(0, 4)] = true;
          });
          if (s.years) Object.keys(s.years).forEach(function (y) { years[String(y)] = true; });
        }
        return Object.keys(years).map(Number).filter(function (n) { return isFinite(n); })
          .sort(function (a, b) { return a - b; });
      }
      function annualIncome(s, year) {
        var total = 0;
        for (var mo = 0; mo < 12; mo++) {
          var dim = daysInMonth(year, mo);
          for (var d = 1; d <= dim; d++) total += dailySales(s, iso(year, mo, d));
        }
        return total;
      }
      function bestYear(selYear) {
        var s = store();
        var yrs = yearsWithData(s);
        var past = yrs.filter(function (y) { return y < selYear; });
        if (yrs.length < 3 || !past.length) return null;
        var best = null, bestVal = -Infinity;
        past.forEach(function (y) {
          var v = annualIncome(s, y);
          if (v > bestVal) { bestVal = v; best = y; }
        });
        return best;
      }
      function bestYearNumber(selYear) {
        var b = bestYear(selYear);
        return b != null ? b : (selYear - 2);
      }
      function canShowBestYear(selYear) { return bestYear(selYear) != null; }

      /* ---- Area builders (shape matches the overlay renderers) ---- */
      function buildArea1(isoStr) {
        var p = isoParts(isoStr);
        if (!p) return null;
        var month0 = p.month - 1;
        var byNum = bestYearNumber(p.year);
        var chart = emptyChart();
        fillDaily(chart, 'thisYear', p.year, month0, p.day);
        fillDaily(chart, 'lastYear', p.year - 1, month0, p.day);
        fillDaily(chart, 'bestYear', byNum, month0, p.day);
        chart.dim = p.day;
        chart.periodCount = daysInMonth(p.year, month0);
        chart.axisMode = 'day';
        chart.refYears = { thisYear: p.year, lastYear: p.year - 1, bestYear: byNum };
        return chart;
      }
      function buildArea2(isoStr) {
        var p = isoParts(isoStr);
        if (!p) return null;
        var month0 = p.month - 1;
        var yTY = p.year - 1, yLY = p.year - 2, yBY = bestYearNumber(p.year);
        var periodCount = daysInMonth(yTY, month0);
        var chart = emptyChart();
        fillDaily(chart, 'thisYear', yTY, month0, periodCount);
        fillDaily(chart, 'lastYear', yLY, month0, periodCount);
        fillDaily(chart, 'bestYear', yBY, month0, periodCount);
        chart.dim = periodCount;
        chart.periodCount = periodCount;
        chart.axisMode = 'day';
        chart.refYears = { thisYear: yTY, lastYear: yLY, bestYear: yBY };
        return chart;
      }
      function buildArea3(isoStr) {
        var p = isoParts(isoStr);
        if (!p) return null;
        var byNum = bestYearNumber(p.year);
        var chart = emptyChart();
        fillMonthly(chart, 'thisYear', p.year, p.month);
        fillMonthly(chart, 'lastYear', p.year - 1, p.month);
        fillMonthly(chart, 'bestYear', byNum, p.month);
        chart.dim = p.month;
        chart.periodCount = 12;
        chart.axisMode = 'month';
        chart.refYears = { thisYear: p.year, lastYear: p.year - 1, bestYear: byNum };
        return chart;
      }

      /* ---- FL snapshots ---- */
      function flDay(year, month0, day) {
        var s = store();
        var alloc = allocForMonth(year, month0);
        var isoStr = iso(year, month0, day);
        var income = dailySales(s, isoStr);
        var food = 0, labor = 0;
        catalog().forEach(function (line) {
          var amt = lineDayAmount(s, year, month0, isoStr, line, alloc);
          if (!amt) return;
          if (isFood(line)) food += amt; else if (isLabor(line)) labor += amt;
        });
        if (!income && !food && !labor) return null;
        return { income: income, expenses: food + labor, variable: food, fixed: labor };
      }
      function flYtd(year, month0, day) {
        var s = store();
        var income = 0, food = 0, labor = 0;
        var lines = catalog();
        for (var mo = 0; mo <= month0; mo++) {
          var lastDay = (mo === month0) ? day : daysInMonth(year, mo);
          var alloc = allocForMonth(year, mo);
          for (var d = 1; d <= lastDay; d++) {
            var isoStr = iso(year, mo, d);
            income += dailySales(s, isoStr);
            for (var i = 0; i < lines.length; i++) {
              var line = lines[i];
              var amt = lineDayAmount(s, year, mo, isoStr, line, alloc);
              if (!amt) continue;
              if (isFood(line)) food += amt; else if (isLabor(line)) labor += amt;
            }
          }
        }
        if (!income && !food && !labor) return null;
        return { income: income, expenses: food + labor, variable: food, fixed: labor };
      }

      /* ---- 費目内訳（選択月の月次合計を費目単位で。金額降順・固定/変動グループ） ---- */
      function lineBreakdown(year, month0) {
        var s = store();
        var fixed = [], variable = [];
        var fixedTotal = 0, variableTotal = 0;
        catalog().forEach(function (line) {
          var amt = lineMonthAmount(s, year, month0, line);
          if (!amt) return;
          var row = {
            lineId: line.lineId,
            labelJa: line.labelJa || line.lineId,
            labelEn: line.labelEn || line.labelJa || line.lineId,
            bucket: line.bucket,
            inputStyle: lineStyle(line),
            amount: amt
          };
          if (line.bucket === 'fixed') { fixed.push(row); fixedTotal += amt; }
          else { variable.push(row); variableTotal += amt; }
        });
        var byDesc = function (a, b) { return b.amount - a.amount; };
        fixed.sort(byDesc); variable.sort(byDesc);
        return {
          fixed: fixed, variable: variable,
          fixedTotal: fixedTotal, variableTotal: variableTotal,
          total: fixedTotal + variableTotal
        };
      }

      window.__plInsight = {
        resetCache: resetCache,
        store: store,
        monthMetrics: monthMetrics,
        dayMetrics: dayMetrics,
        lineBreakdown: lineBreakdown,
        buildArea1: buildArea1,
        buildArea2: buildArea2,
        buildArea3: buildArea3,
        flDay: flDay,
        flYtd: flYtd,
        bestYear: bestYear,
        bestYearNumber: bestYearNumber,
        canShowBestYear: canShowBestYear,
        yearsWithData: function () { return yearsWithData(store()); }
      };
    })();
    """

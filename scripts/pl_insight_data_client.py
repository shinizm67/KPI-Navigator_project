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
- FL snapshot (Unit 5C-0/5C-1): restaurant canonical is
    F = (food_cost + drink_cost) / income
    L = labor / income
    FL = (food_cost + drink_cost + labor) / income
    using expenseAttribute food_cost/drink_cost and labor attrs
    (fallback to well-known default lineIds).
  Non-restaurant: no F/FL names. Left bar = ANALYSIS key-expense lineIds
  via KpiPlExpensePresets.getAnalysisMetrics(); right bar = labor.
  Chart METRICS/SERIES and long-press paths stay unchanged.

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
      /* Date-nav hot path: reuse full-month series / Area2-3 charts / best-year. */
      var monthSeriesCache = {}; // 'year-month0' -> { daily, cumulative, dim }
      var monthMetricsCache = {}; // 'year-month0' -> metrics
      var area2ChartCache = {}; // 'm0|yTY|yLY|yBY' -> chart (day-independent)
      var area3ChartCache = {}; // 'year|month|by' -> chart (day-independent within month)
      var bestYearCache = {}; // selYear -> year|null
      var annualIncomeCache = {}; // year -> number
      var flYtdCache = {}; // 'year|month0|day|bt' -> snapshot
      var flYtdPrefixCache = {}; // 'year|bt' -> { income, food, labor } cumulative through each month-day
      var keyExpenseIdCache = null;

      function resetCache() {
        allocCache = {};
        catalogCache = null;
        monthlyMapCache = {};
        adjMapCache = {};
        monthSeriesCache = {};
        monthMetricsCache = {};
        area2ChartCache = {};
        area3ChartCache = {};
        bestYearCache = {};
        annualIncomeCache = {};
        flYtdCache = {};
        flYtdPrefixCache = {};
        keyExpenseIdCache = null;
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
        var attrs;
        var extraIds;
        var api = window.KpiPlExpensePresets;
        if (api && api.LABOR_ANALYSIS_ATTRIBUTES && api.LABOR_ANALYSIS_ATTRIBUTES.length) {
          attrs = api.LABOR_ANALYSIS_ATTRIBUTES;
        } else {
          attrs = ['salaries_wages', 'variable_labor', 'labor_related'];
        }
        if (a && attrs.indexOf(a) >= 0) return true;
        extraIds = (api && api.LABOR_ANALYSIS_LINE_IDS && api.LABOR_ANALYSIS_LINE_IDS.length)
          ? api.LABOR_ANALYSIS_LINE_IDS
          : ['exp_fixed_labor', 'exp_variable_labor'];
        return extraIds.indexOf(line.lineId) >= 0;
      }

      /* === UNIT-5C-1-PL-INSIGHT-BT-BEGIN === */
      function plInsightPageLang() {
        var lang = '';
        try {
          lang = String(
            (document.documentElement && document.documentElement.getAttribute('lang')) || ''
          ).toLowerCase();
        } catch (_eLang) {}
        if (lang.indexOf('zh') === 0) return 'zh';
        if (lang.indexOf('en') === 0) return 'en';
        return 'ja';
      }
      function plInsightReadMetrics() {
        var api = window.KpiPlExpensePresets;
        if (api && typeof api.getAnalysisMetrics === 'function') {
          try { return api.getAnalysisMetrics(); } catch (_eM) {}
        }
        return { mode: 'restaurant_fl', groups: [] };
      }
      function plInsightIsRestaurantFl() {
        var rec = plInsightReadMetrics();
        return !rec || rec.mode !== 'key_expenses';
      }
      function plInsightKeyExpenseIdSet() {
        if (keyExpenseIdCache) return keyExpenseIdCache;
        var ids = {};
        var rec = plInsightReadMetrics();
        (rec.groups || []).forEach(function (group) {
          (group.rows || []).forEach(function (row) {
            if (!row || row.source === 'labor') return;
            (row.lineIds || []).forEach(function (id) {
              if (id) ids[id] = true;
            });
          });
        });
        keyExpenseIdCache = ids;
        return ids;
      }
      function plInsightClassifyLine(line) {
        if (!line || !line.lineId) return 'ignore';
        if (plInsightIsRestaurantFl()) {
          if (isFood(line)) return 'left';
          if (isLabor(line)) return 'labor';
          return 'ignore';
        }
        if (isLabor(line)) return 'labor';
        if (plInsightKeyExpenseIdSet()[line.lineId]) return 'left';
        return 'ignore';
      }
      function plInsightPickLabel(row, lang) {
        if (!row) return '';
        if (lang === 'zh') return row.labelZh || row.labelJa || row.labelEn || '';
        if (lang === 'en') return row.labelEn || row.labelJa || '';
        return row.labelJa || row.labelEn || '';
      }
      function plInsightJoinMajor(group, lang) {
        var lines =
          lang === 'zh'
            ? (group && (group.majorZh || group.majorJa))
            : lang === 'en'
              ? (group && (group.majorEn || group.majorJa))
              : (group && (group.majorJa || group.majorEn));
        if (!Array.isArray(lines) || !lines.length) return '';
        return lines.join('');
      }
      function plInsightLaborShort(lang) {
        if (lang === 'zh') return '人事費用';
        if (lang === 'en') return 'Labor';
        return '人件費';
      }
      function plInsightKeyAreaTitles(lang, pack) {
        pack = pack || {};
        if (lang === 'zh') {
          return {
            area1: pack.area1Key || '區域 1. 當日成本快照',
            area2: pack.area2Key || '區域 2. 去年同月成本快照',
            area3: pack.area3Key || '區域 3. 年初至今成本快照'
          };
        }
        if (lang === 'en') {
          return {
            area1: pack.area1Key || 'Area 1. Current Cost Snapshot',
            area2: pack.area2Key || 'Area 2. Last Year Same Month Cost Snapshot',
            area3: pack.area3Key || 'Area 3. Year-to-Date Cost Snapshot'
          };
        }
        return {
          area1: pack.area1Key || 'Area 1. 当日のコストスナップショット',
          area2: pack.area2Key || 'Area 2. 前年同月のコストスナップショット',
          area3: pack.area3Key || 'Area 3. 年初来（YTD）のコストスナップショット'
        };
      }
      function plInsightSnapshotCopy(pack) {
        pack = pack || {};
        var lang = plInsightPageLang();
        if (plInsightIsRestaurantFl()) {
          return {
            restaurant: true,
            combined: pack.foodLabor || 'Food & Labor',
            split: pack.foodSlashLabor || 'Food / Labor',
            area1: pack.area1 || '',
            area2: pack.area2 || '',
            area3: pack.area3 || ''
          };
        }
        var rec = plInsightReadMetrics();
        var keyGroup = null;
        (rec.groups || []).forEach(function (group) {
          var hasKey = (group.rows || []).some(function (row) {
            return row && row.source !== 'labor';
          });
          if (hasKey && !keyGroup) keyGroup = group;
        });
        var left = keyGroup ? plInsightJoinMajor(keyGroup, lang) : '';
        if (!left && keyGroup) {
          left = (keyGroup.rows || [])
            .filter(function (row) { return row && row.source !== 'labor'; })
            .map(function (row) { return plInsightPickLabel(row, lang); })
            .filter(Boolean)
            .join(' / ');
        }
        if (!left) left = lang === 'en' ? 'Key costs' : '主要費目';
        var right = plInsightLaborShort(lang);
        var titles = plInsightKeyAreaTitles(lang, pack);
        return {
          restaurant: false,
          combined: left + ' & ' + right,
          split: left + ' / ' + right,
          area1: titles.area1,
          area2: titles.area2,
          area3: titles.area3
        };
      }
      /* === UNIT-5C-1-PL-INSIGHT-BT-END === */

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
        var ck = year + '-' + month0;
        if (monthMetricsCache[ck]) return monthMetricsCache[ck];
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
        var out = { income: income, fixed: fixed, variable: variable, expenses: expenses,
                 expected: variable, profit: income - expenses };
        monthMetricsCache[ck] = out;
        return out;
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
      /* Full-month series for one calendar month (built once, sliced for Area1). */
      function monthSeries(year, month0) {
        var key = year + '-' + month0;
        if (monthSeriesCache[key]) return monthSeriesCache[key];
        var dim = daysInMonth(year, month0);
        var daily = {};
        var cumulative = {};
        METRICS.forEach(function (k) {
          daily[k] = [];
          cumulative[k] = [];
        });
        var cum = { income: 0, expenses: 0, fixed: 0, expected: 0, profit: 0 };
        for (var d = 1; d <= dim; d++) {
          var m = dayMetrics(year, month0, d);
          METRICS.forEach(function (k) {
            daily[k].push(m[k]);
            cum[k] += m[k];
            cumulative[k].push(cum[k]);
          });
        }
        monthSeriesCache[key] = { daily: daily, cumulative: cumulative, dim: dim };
        return monthSeriesCache[key];
      }
      function fillDaily(chart, seriesKey, year, month0, count) {
        var full = monthSeries(year, month0);
        var n = Math.max(0, Math.min(count, full.dim));
        METRICS.forEach(function (k) {
          chart.daily[k][seriesKey] = full.daily[k].slice(0, n);
          chart.cumulative[k][seriesKey] = full.cumulative[k].slice(0, n);
        });
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
        if (annualIncomeCache[year] != null) return annualIncomeCache[year];
        var total = 0;
        for (var mo = 0; mo < 12; mo++) {
          var dim = daysInMonth(year, mo);
          for (var d = 1; d <= dim; d++) total += dailySales(s, iso(year, mo, d));
        }
        annualIncomeCache[year] = total;
        return total;
      }
      function bestYear(selYear) {
        if (Object.prototype.hasOwnProperty.call(bestYearCache, selYear)) {
          return bestYearCache[selYear];
        }
        var s = store();
        var yrs = yearsWithData(s);
        var past = yrs.filter(function (y) { return y < selYear; });
        if (yrs.length < 3 || !past.length) {
          bestYearCache[selYear] = null;
          return null;
        }
        var best = null, bestVal = -Infinity;
        past.forEach(function (y) {
          var v = annualIncome(s, y);
          if (v > bestVal) { bestVal = v; best = y; }
        });
        bestYearCache[selYear] = best;
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
        var dayCap = Math.min(p.day, periodCount, daysInMonth(p.year, month0));
        if (dayCap < 1) dayCap = 1;
        /* Include day so ◀︎▶︎ pace charts track the selected date (not full month only). */
        var cacheKey = month0 + '|' + yTY + '|' + yLY + '|' + yBY + '|' + dayCap;
        if (area2ChartCache[cacheKey]) return area2ChartCache[cacheKey];
        var chart = emptyChart();
        fillDaily(chart, 'thisYear', yTY, month0, dayCap);
        fillDaily(chart, 'lastYear', yLY, month0, dayCap);
        fillDaily(chart, 'bestYear', yBY, month0, dayCap);
        chart.dim = dayCap;
        chart.periodCount = periodCount;
        chart.axisMode = 'day';
        chart.refYears = { thisYear: yTY, lastYear: yLY, bestYear: yBY };
        area2ChartCache[cacheKey] = chart;
        return chart;
      }
      function buildArea3(isoStr) {
        var p = isoParts(isoStr);
        if (!p) return null;
        var byNum = bestYearNumber(p.year);
        var cacheKey = p.year + '|' + p.month + '|' + byNum;
        if (area3ChartCache[cacheKey]) return area3ChartCache[cacheKey];
        var chart = emptyChart();
        fillMonthly(chart, 'thisYear', p.year, p.month);
        fillMonthly(chart, 'lastYear', p.year - 1, p.month);
        fillMonthly(chart, 'bestYear', byNum, p.month);
        chart.dim = p.month;
        chart.periodCount = 12;
        chart.axisMode = 'month';
        chart.refYears = { thisYear: p.year, lastYear: p.year - 1, bestYear: byNum };
        area3ChartCache[cacheKey] = chart;
        return chart;
      }

      /* ---- FL snapshots (5C-0 restaurant: left=food+drink, labor=labor, total=FL) ---- */
      function flBtCacheKey() {
        try {
          if (window.KpiPlExpensePresets && typeof window.KpiPlExpensePresets.resolveBusinessType === 'function') {
            return String(window.KpiPlExpensePresets.resolveBusinessType() || 'restaurant');
          }
        } catch (_eBt) {}
        return 'restaurant';
      }
      function flAccumulateLine(line, amt, acc) {
        var side = plInsightClassifyLine(line);
        if (side === 'left') acc.food += amt;
        else if (side === 'labor') acc.labor += amt;
      }
      function flSnapFromParts(income, left, labor) {
        if (!income && !left && !labor) return null;
        return { income: income, expenses: left + labor, variable: left, fixed: labor };
      }
      function flDay(year, month0, day) {
        var s = store();
        var alloc = allocForMonth(year, month0);
        var isoStr = iso(year, month0, day);
        var income = dailySales(s, isoStr);
        var acc = { food: 0, labor: 0 };
        catalog().forEach(function (line) {
          var amt = lineDayAmount(s, year, month0, isoStr, line, alloc);
          if (!amt) return;
          flAccumulateLine(line, amt, acc);
        });
        return flSnapFromParts(income, acc.food, acc.labor);
      }
      function flYtdPrefix(year) {
        var pk = year + '|' + flBtCacheKey();
        if (flYtdPrefixCache[pk]) return flYtdPrefixCache[pk];
        var s = store();
        var lines = catalog();
        var months = [];
        var run = { income: 0, food: 0, labor: 0 };
        for (var mo = 0; mo < 12; mo++) {
          var dim = daysInMonth(year, mo);
          var days = [null];
          var alloc = allocForMonth(year, mo);
          for (var d = 1; d <= dim; d++) {
            var isoStr = iso(year, mo, d);
            run.income += dailySales(s, isoStr);
            for (var i = 0; i < lines.length; i++) {
              var line = lines[i];
              var amt = lineDayAmount(s, year, mo, isoStr, line, alloc);
              if (!amt) continue;
              flAccumulateLine(line, amt, run);
            }
            days.push({ income: run.income, food: run.food, labor: run.labor });
          }
          months.push(days);
        }
        flYtdPrefixCache[pk] = months;
        return months;
      }
      function flYtd(year, month0, day) {
        var ck = year + '|' + month0 + '|' + day + '|' + flBtCacheKey();
        if (Object.prototype.hasOwnProperty.call(flYtdCache, ck)) return flYtdCache[ck];
        var months = flYtdPrefix(year);
        var days = months[month0];
        var snap = days && days[day] ? days[day] : null;
        if (!snap) {
          flYtdCache[ck] = null;
          return null;
        }
        var out = flSnapFromParts(snap.income, snap.food, snap.labor);
        flYtdCache[ck] = out;
        return out;
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
        snapshotCopy: plInsightSnapshotCopy,
        isRestaurantFl: plInsightIsRestaurantFl,
        classifyLine: plInsightClassifyLine,
        bestYear: bestYear,
        bestYearNumber: bestYearNumber,
        canShowBestYear: canShowBestYear,
        yearsWithData: function () { return yearsWithData(store()); }
      };
    })();
    """

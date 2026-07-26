/* KPI-PL-MEP-EXPORT */
(function () {
  'use strict';

  /* xlsx-js-style: SheetJS-compatible + borders / fills (community xlsx cannot write cell styles). */
  var XLSX_URL = 'https://cdn.jsdelivr.net/npm/xlsx-js-style@1.2.0/dist/xlsx.min.js';
  var STORE_KEY = 'kpiNavigator.kpiYearStore';
  var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
  var EXP_PREFIX = 'kpi-pl-expenses-v1:';
  var ADJ_PREFIX = 'kpi-pl-expense-adjustments-v1:';
  var TIER_KEY = 'kpiNavigator.subscriptionTier';
  var ANNUAL_NAV_KEY = 'kpiNavigator.annualNav';
  var MONTHLY_LAST_KEY = 'kpiNavigator.monthlyLast';
  var MARKER = 'KPI-PL-MEP-EXPORT';
  /* Same defaults as PL (bucket=fixed|variable; no section field). */
  var DEFAULT_EXPENSE_LINES = [{"lineId":"exp_rent","labelJa":"家賃","labelEn":"Rent","bucket":"fixed","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":0},{"lineId":"exp_fixed_asset_tax","labelJa":"固定資産税","labelEn":"Fixed asset tax","bucket":"fixed","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":1},{"lineId":"exp_fixed_labor","labelJa":"固定人件費","labelEn":"Fixed Labor","bucket":"fixed","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":2},{"lineId":"exp_lease","labelJa":"リース料","labelEn":"Lease","bucket":"fixed","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":3},{"lineId":"exp_depreciable_asset_tax","labelJa":"償却資産税","labelEn":"Depreciable asset tax","bucket":"fixed","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":4},{"lineId":"exp_depreciation","labelJa":"減価償却費","labelEn":"Depreciation expenses","bucket":"fixed","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":5},{"lineId":"exp_non_life_insurance","labelJa":"損害保険","labelEn":"Non-life insurance","bucket":"fixed","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":6},{"lineId":"exp_social_insurance","labelJa":"社会保険","labelEn":"social insurance","bucket":"fixed","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":7},{"lineId":"exp_food_cost","labelJa":"食材仕入れ費","labelEn":"Food cost","bucket":"variable","inputStyle":"daily","resolvedInputStyle":"daily","active":true,"sortOrder":0},{"lineId":"exp_drink_cost","labelJa":"ドリンク仕入れ費","labelEn":"Drink Cost","bucket":"variable","inputStyle":"daily","resolvedInputStyle":"daily","active":true,"sortOrder":1},{"lineId":"exp_supplies","labelJa":"備品・消耗品仕入費","labelEn":"Supplies & Consumables","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":2},{"lineId":"exp_misc","labelJa":"雑費・小口精算費","labelEn":"Miscellaneous Expense","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":3},{"lineId":"exp_electric","labelJa":"電気代","labelEn":"Electricity Cost","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":4},{"lineId":"exp_gas","labelJa":"ガス代","labelEn":"Gas Cost","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":5},{"lineId":"exp_water","labelJa":"水道代","labelEn":"Water Cost","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":6},{"lineId":"exp_variable_labor","labelJa":"アルバイト人件費","labelEn":"Variable Labor","bucket":"variable","inputStyle":"daily","resolvedInputStyle":"daily","active":true,"sortOrder":7},{"lineId":"exp_telecom","labelJa":"通信費","labelEn":"Communication","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":8},{"lineId":"exp_advertising","labelJa":"広告宣伝費","labelEn":"Advertising","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":9},{"lineId":"exp_uniforms","labelJa":"被服費","labelEn":"Uniforms & Workwear","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":10},{"lineId":"exp_payment_fees","labelJa":"クレジットカード手数料","labelEn":"Payment Processing Fees","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":true,"sortOrder":11},{"lineId":"exp_employment_insurance","labelJa":"雇用保険","labelEn":"employment insurance","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":12},{"lineId":"exp_workers_comp","labelJa":"労災保険","labelEn":"Worker's compensation insurance","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":13},{"lineId":"exp_consumption_tax","labelJa":"消費税","labelEn":"consumption tax","bucket":"variable","inputStyle":"monthly","resolvedInputStyle":"monthly","active":false,"sortOrder":14}];

  function useJa() {
    return String(document.documentElement.getAttribute('lang') || '')
      .toLowerCase()
      .indexOf('ja') === 0;
  }

  function t(ja, en) {
    return useJa() ? ja : en;
  }

  function isPro() {
    try {
      if (window.KpiYearStore && typeof KpiYearStore.isProSubscription === 'function') {
        return !!KpiYearStore.isProSubscription();
      }
    } catch (_e) {}
    try {
      var tier =
        sessionStorage.getItem(TIER_KEY) || localStorage.getItem(TIER_KEY) || 'pro';
      return String(tier).trim().toLowerCase() !== 'basic';
    } catch (_e2) {
      return true;
    }
  }

  function changePlanHref(btn) {
    var fromBtn = btn && btn.getAttribute('data-kpi-change-plan');
    if (fromBtn) return fromBtn;
    var path = location.pathname || '';
    if (path.indexOf('/en/') >= 0) {
      if (path.indexOf('/app/profit/pl') >= 0) return '../../../setting/change_plan.html';
      if (path.indexOf('/app/') >= 0) return '../../setting/change_plan.html';
      if (path.indexOf('/setting/') >= 0) return 'change_plan.html';
      return '../setting/change_plan.html';
    }
    if (path.indexOf('/app/profit/pl') >= 0) return '../../../setting/change_plan.html';
    if (path.indexOf('/app/') >= 0) return '../../setting/change_plan.html';
    if (path.indexOf('/setting/') >= 0) return 'change_plan.html';
    return 'setting/change_plan.html';
  }

  function loadXlsx() {
    return new Promise(function (resolve, reject) {
      if (window.XLSX) return resolve(window.XLSX);
      var s = document.createElement('script');
      s.src = XLSX_URL;
      s.async = true;
      s.onload = function () {
        window.XLSX ? resolve(window.XLSX) : reject(new Error('xlsx'));
      };
      s.onerror = function () {
        reject(new Error('xlsx'));
      };
      document.head.appendChild(s);
    });
  }

  function readJson(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      if (!raw) return fallback;
      return JSON.parse(raw);
    } catch (_e) {
      return fallback;
    }
  }

  function pad2(n) {
    return String(n).padStart(2, '0');
  }

  function isoFromYmd(y, m1, d) {
    return y + '-' + pad2(m1) + '-' + pad2(d);
  }

  function daysInMonth(y, m0) {
    return new Date(y, m0 + 1, 0).getDate();
  }

  function defaultYear() {
    try {
      var nav = readJson(ANNUAL_NAV_KEY, null);
      if (nav && Number.isFinite(Number(nav.calendarYear))) return Number(nav.calendarYear);
    } catch (_e) {}
    try {
      if (window.KpiYearStore && typeof KpiYearStore.getOperatingYear === 'function') {
        var oy = Number(KpiYearStore.getOperatingYear());
        if (Number.isFinite(oy)) return oy;
      }
    } catch (_e2) {}
    try {
      var qs = new URLSearchParams(location.search || '');
      var y = Number(qs.get('year'));
      if (Number.isFinite(y) && y >= 2000 && y <= 2100) return y;
    } catch (_e3) {}
    return new Date().getFullYear();
  }

  function defaultMonth0() {
    try {
      var qs = new URLSearchParams(location.search || '');
      var m = Number(qs.get('month'));
      if (Number.isFinite(m) && m >= 1 && m <= 12) return m - 1;
    } catch (_e) {}
    try {
      var last = sessionStorage.getItem(MONTHLY_LAST_KEY) || localStorage.getItem(MONTHLY_LAST_KEY);
      if (last && /^\d{4}-\d{2}/.test(last)) {
        var mm = Number(String(last).slice(5, 7));
        if (Number.isFinite(mm) && mm >= 1 && mm <= 12) return mm - 1;
      }
    } catch (_e2) {}
    return new Date().getMonth();
  }

  function loadStore() {
    try {
      if (window.KpiYearStore && typeof KpiYearStore._debugDump === 'function') {
        /* prefer public APIs below */
      }
    } catch (_e) {}
    return readJson(STORE_KEY, null);
  }

  function loadMepPayload(year) {
    try {
      if (window.KpiYearStore && typeof KpiYearStore.loadMepYearPayload === 'function') {
        return KpiYearStore.loadMepYearPayload(year);
      }
    } catch (_e) {}
    var store = loadStore();
    if (!store || !store.years) return { dailyExpenses: {}, dailyIncome: {} };
    var rec = store.years[String(year)] || {};
    return {
      dailyExpenses: rec.dailyExpenses || {},
      dailyIncome: rec.dailyIncome || {}
    };
  }

  function readDailySales(iso) {
    try {
      if (window.KpiYearStore && typeof KpiYearStore.readDailySales === 'function') {
        var v = Number(KpiYearStore.readDailySales(iso));
        return Number.isFinite(v) ? v : 0;
      }
    } catch (_e) {}
    var store = loadStore();
    var map = (store && store.timeline && store.timeline.dailySales) || {};
    var n = Number(map[iso]);
    return Number.isFinite(n) ? n : 0;
  }

  function loadCatalogLines() {
    try {
      if (typeof window.__plGetCatalogLines === 'function') {
        var fromPl = window.__plGetCatalogLines();
        if (fromPl && fromPl.length) return fromPl.slice();
      }
    } catch (_e) {}
    var cat = readJson(CATALOG_KEY, null);
    var lines = (cat && Array.isArray(cat.lines) && cat.lines.length && cat.lines) || DEFAULT_EXPENSE_LINES;
    return lines.filter(function (ln) {
      return ln && ln.lineId && ln.active !== false;
    });
  }

  function labelOf(line) {
    if (!line) return '';
    return useJa() ? line.labelJa || line.labelEn || line.lineId : line.labelEn || line.labelJa || line.lineId;
  }

  function lineStyle(line) {
    return (line.resolvedInputStyle || line.inputStyle || 'monthly') === 'daily' ? 'daily' : 'monthly';
  }

  function incomeOrder() {
    return [
      { id: 'sales_total', ja: '総売上', en: 'Total Sales', kind: 'sales_total' },
      { id: 'store_sales', ja: '店舗売上', en: 'Store Sales', kind: 'income' },
      { id: 'sales_a', ja: '売上A', en: 'Sales A', kind: 'income' },
      { id: 'sales_b', ja: '売上B', en: 'Sales B', kind: 'income' },
      { id: 'food_sales', ja: 'フード売上', en: 'Food Sales', kind: 'income' },
      { id: 'drink_sales', ja: 'ドリンク売上', en: 'Drink Sales', kind: 'income' }
    ];
  }

  function sortExpenseLines(lines) {
    return lines.slice().sort(function (a, b) {
      if (a.bucket !== b.bucket) return a.bucket === 'fixed' ? -1 : 1;
      return (Number(a.sortOrder) || 0) - (Number(b.sortOrder) || 0);
    });
  }

  /** Catalog uses bucket=fixed|variable (no section). Merge orphans from stored maps. */
  function expenseLines(extraIds) {
    var byId = {};
    loadCatalogLines().forEach(function (ln) {
      if (!ln || !ln.lineId) return;
      if (ln.section === 'income') return;
      if (ln.bucket === 'fixed' || ln.bucket === 'variable' || String(ln.lineId).indexOf('exp_') === 0) {
        byId[ln.lineId] = ln;
      }
    });
    (extraIds || []).forEach(function (id) {
      if (!id || byId[id]) return;
      byId[id] = {
        lineId: id,
        labelJa: id,
        labelEn: id,
        bucket: 'variable',
        inputStyle: 'daily',
        active: true,
        sortOrder: 999
      };
    });
    return sortExpenseLines(
      Object.keys(byId).map(function (k) {
        return byId[k];
      })
    );
  }

  function roundMoney(n) {
    var v = Math.round(Number(n) || 0);
    return v;
  }

  function pctOf(amount, sales) {
    var s = Number(sales) || 0;
    if (s <= 0) return '';
    var a = Number(amount) || 0;
    return Math.round((a / s) * 1000) / 10;
  }

  function monthSheetName(m0) {
    return useJa() ? m0 + 1 + '月' : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][m0];
  }

  function readBusinessDay(iso) {
    try {
      if (window.KpiYearStore && typeof KpiYearStore.readBusinessDay === 'function') {
        var v = KpiYearStore.readBusinessDay(iso);
        if (v === true || v === false) return v;
      }
    } catch (_e) {}
    var store = loadStore();
    var map = (store && store.timeline && store.timeline.businessDays) || {};
    if (Object.prototype.hasOwnProperty.call(map, iso)) return !!map[iso];
    return readDailySales(iso) > 0;
  }

  function monthlyAllocForLine(year, m0, lineId) {
    try {
      if (typeof window.__plPreviewMonthlyExpenseAllocation === 'function') {
        var prev = window.__plPreviewMonthlyExpenseAllocation({ year: year, month0: m0 });
        var months = prev && prev.months;
        if (months && months.length) {
          var mlines = months[0].lines || {};
          if (mlines[lineId] && mlines[lineId].byDate) return mlines[lineId].byDate;
        }
      }
    } catch (_e) {}
    return null;
  }

  function lineDayAmount(year, m0, iso, line, dailyExpenses, expMap) {
    if (lineStyle(line) === 'daily') {
      var map = (dailyExpenses && dailyExpenses[line.lineId]) || {};
      return Number(map[iso]) || 0;
    }
    var byDate = monthlyAllocForLine(year, m0, line.lineId);
    if (byDate && Object.prototype.hasOwnProperty.call(byDate, iso)) {
      return Number(byDate[iso]) || 0;
    }
    /* Fallback: put full monthly amount on day 1 so the line is visible on MEP. */
    var day = Number(String(iso).slice(8, 10));
    if (day === 1) return Number(expMap[line.lineId + ':' + m0]) || 0;
    return 0;
  }

  function lineMonthAmount(year, m0, line, dailyExpenses, expMap, adjMap) {
    if (lineStyle(line) === 'monthly') {
      return Number(expMap[line.lineId + ':' + m0]) || 0;
    }
    var map = (dailyExpenses && dailyExpenses[line.lineId]) || {};
    var sum = 0;
    var dim = daysInMonth(year, m0);
    for (var d = 1; d <= dim; d++) {
      sum += Number(map[isoFromYmd(year, m0 + 1, d)]) || 0;
    }
    sum += Number(adjMap[line.lineId + ':' + m0]) || 0;
    return sum;
  }

  function buildMepSheetAoA(year, m0) {
    var days = daysInMonth(year, m0);
    var payload = loadMepPayload(year) || { dailyExpenses: {}, dailyIncome: {} };
    var dailyIncome = payload.dailyIncome || {};
    var dailyExpenses = payload.dailyExpenses || {};
    var expMap = readJson(EXP_PREFIX + year, {}) || {};
    var orphanIds = Object.keys(dailyExpenses || {});
    var allExp = expenseLines(orphanIds);
    var groups = {
      fixed: allExp.filter(function (ln) {
        return ln.bucket === 'fixed';
      }),
      variable: allExp.filter(function (ln) {
        return ln.bucket !== 'fixed';
      })
    };

    var header = [t('収支', 'P&L')];
    var i;
    for (i = 1; i <= days; i++) {
      header.push(t(i + '日', 'Day ' + i));
      header.push('%');
    }
    var rows = [header];
    var isos = [];
    for (i = 1; i <= days; i++) isos.push(isoFromYmd(year, m0 + 1, i));

    function pushAmountRow(label, values, withPct) {
      var row = [label];
      for (var d = 0; d < days; d++) {
        var amt = roundMoney(values[d]);
        var sales = readDailySales(isos[d]);
        row.push(amt === 0 ? '' : amt);
        row.push(withPct ? pctOf(amt, sales) : '');
      }
      rows.push(row);
    }

    var bizRow = [t('営業日', 'Business Day')];
    for (i = 0; i < days; i++) {
      bizRow.push(readBusinessDay(isos[i]) ? 1 : 0);
      bizRow.push('');
    }
    rows.push(bizRow);

    var profitVals = isos.map(function (iso, di) {
      var expSum = 0;
      allExp.forEach(function (ln) {
        expSum += lineDayAmount(year, m0, iso, ln, dailyExpenses, expMap);
      });
      return readDailySales(iso) - expSum;
    });
    pushAmountRow(t('利益', 'Profit'), profitVals, false);

    incomeOrder().forEach(function (def) {
      var vals = isos.map(function (iso) {
        if (def.kind === 'sales_total') return readDailySales(iso);
        if (def.id === 'drink_sales') {
          var food = Number((dailyIncome.food_sales && dailyIncome.food_sales[iso]) || 0);
          var base =
            dailyIncome.store_sales && dailyIncome.store_sales[iso] != null
              ? Number(dailyIncome.store_sales[iso]) || 0
              : (function () {
                  var tot = readDailySales(iso);
                  var a = Number((dailyIncome.sales_a && dailyIncome.sales_a[iso]) || 0);
                  var b = Number((dailyIncome.sales_b && dailyIncome.sales_b[iso]) || 0);
                  return Math.max(0, Math.round(tot) - Math.round(a) - Math.round(b));
                })();
          return Math.max(0, Math.round(base) - Math.round(food));
        }
        if (def.id === 'store_sales') {
          if (dailyIncome.store_sales && dailyIncome.store_sales[iso] != null) {
            return Number(dailyIncome.store_sales[iso]) || 0;
          }
          var tot = readDailySales(iso);
          var sa = Number((dailyIncome.sales_a && dailyIncome.sales_a[iso]) || 0);
          var sb = Number((dailyIncome.sales_b && dailyIncome.sales_b[iso]) || 0);
          return Math.max(0, Math.round(tot) - Math.round(sa) - Math.round(sb));
        }
        var map = dailyIncome[def.id] || {};
        return Number(map[iso]) || 0;
      });
      pushAmountRow(useJa() ? def.ja : def.en, vals, false);
    });

    rows.push([t('— 支出 —', '— Expenses —')].concat(Array(days * 2).fill('')));
    rows.push([t('— 固定費 —', '— Fixed —')].concat(Array(days * 2).fill('')));
    groups.fixed.forEach(function (ln) {
      var vals = isos.map(function (iso) {
        return lineDayAmount(year, m0, iso, ln, dailyExpenses, expMap);
      });
      pushAmountRow(labelOf(ln), vals, true);
    });
    rows.push([t('— 変動費 —', '— Variable —')].concat(Array(days * 2).fill('')));
    groups.variable.forEach(function (ln) {
      var vals = isos.map(function (iso) {
        return lineDayAmount(year, m0, iso, ln, dailyExpenses, expMap);
      });
      pushAmountRow(labelOf(ln), vals, true);
    });

    return rows;
  }

  function monthSalesTotal(year, m0) {
    var days = daysInMonth(year, m0);
    var sum = 0;
    for (var d = 1; d <= days; d++) {
      sum += readDailySales(isoFromYmd(year, m0 + 1, d));
    }
    return sum;
  }

  function monthIncomeStream(year, m0, streamId) {
    var payload = loadMepPayload(year) || { dailyIncome: {} };
    var map = (payload.dailyIncome && payload.dailyIncome[streamId]) || {};
    var days = daysInMonth(year, m0);
    var sum = 0;
    for (var d = 1; d <= days; d++) {
      var iso = isoFromYmd(year, m0 + 1, d);
      sum += Number(map[iso]) || 0;
    }
    return sum;
  }

  function buildPlSheetAoA(year) {
    var expMap = readJson(EXP_PREFIX + year, {}) || {};
    var adjMap = readJson(ADJ_PREFIX + year, {}) || {};
    var payload = loadMepPayload(year) || { dailyExpenses: {}, dailyIncome: {} };
    var dailyExpenses = payload.dailyExpenses || {};
    var orphanIds = Object.keys(expMap)
      .map(function (k) {
        return String(k).split(':')[0];
      })
      .concat(Object.keys(dailyExpenses || {}));
    var allExp = expenseLines(orphanIds);
    var groups = {
      fixed: allExp.filter(function (ln) {
        return ln.bucket === 'fixed';
      }),
      variable: allExp.filter(function (ln) {
        return ln.bucket !== 'fixed';
      })
    };

    var header = [t('収支', 'P&L')];
    var m0;
    for (m0 = 0; m0 < 12; m0++) {
      header.push(monthSheetName(m0));
      header.push('%');
    }
    var rows = [header];
    var monthSales = [];
    for (m0 = 0; m0 < 12; m0++) monthSales.push(monthSalesTotal(year, m0));

    function pushRow(label, amounts, withPct) {
      var row = [label];
      for (var i = 0; i < 12; i++) {
        var amt = roundMoney(amounts[i]);
        row.push(amt === 0 ? '' : amt);
        row.push(withPct ? pctOf(amt, monthSales[i]) : '');
      }
      rows.push(row);
    }

    var salesTotal = monthSales.slice();
    var salesA = [];
    var salesB = [];
    var food = [];
    var store = [];
    var drink = [];
    var expenseTotals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    for (m0 = 0; m0 < 12; m0++) {
      salesA.push(monthIncomeStream(year, m0, 'sales_a'));
      salesB.push(monthIncomeStream(year, m0, 'sales_b'));
      food.push(monthIncomeStream(year, m0, 'food_sales'));
      var st = monthIncomeStream(year, m0, 'store_sales');
      if (!st) st = Math.max(0, salesTotal[m0] - salesA[m0] - salesB[m0]);
      store.push(st);
      drink.push(Math.max(0, Math.round(st) - Math.round(food[m0])));
      allExp.forEach(function (ln) {
        expenseTotals[m0] += lineMonthAmount(year, m0, ln, dailyExpenses, expMap, adjMap);
      });
    }

    var profit = [];
    for (m0 = 0; m0 < 12; m0++) profit.push(salesTotal[m0] - expenseTotals[m0]);

    pushRow(t('利益', 'Profit'), profit, false);
    pushRow(t('総売上', 'Total Sales'), salesTotal, false);
    pushRow(t('店舗売上', 'Store Sales'), store, false);
    pushRow(t('売上A', 'Sales A'), salesA, false);
    pushRow(t('売上B', 'Sales B'), salesB, false);
    pushRow(t('フード売上', 'Food Sales'), food, false);
    pushRow(t('ドリンク売上', 'Drink Sales'), drink, false);
    rows.push([t('— 支出 —', '— Expenses —')].concat(Array(24).fill('')));
    rows.push([t('— 固定費 —', '— Fixed —')].concat(Array(24).fill('')));
    groups.fixed.forEach(function (ln) {
      var amounts = [];
      for (m0 = 0; m0 < 12; m0++) {
        amounts.push(lineMonthAmount(year, m0, ln, dailyExpenses, expMap, adjMap));
      }
      pushRow(labelOf(ln), amounts, true);
    });
    rows.push([t('— 変動費 —', '— Variable —')].concat(Array(24).fill('')));
    groups.variable.forEach(function (ln) {
      var amounts = [];
      for (m0 = 0; m0 < 12; m0++) {
        amounts.push(lineMonthAmount(year, m0, ln, dailyExpenses, expMap, adjMap));
      }
      pushRow(labelOf(ln), amounts, true);
    });

    return rows;
  }

  function styleWorkbookSheet(XLSX, ws, aoa) {
    if (!ws || !aoa || !aoa.length) return;
    var cols = [{ wch: 22 }];
    var widthCount = (aoa[0] && aoa[0].length) || 1;
    for (var c = 1; c < widthCount; c++) {
      cols.push({ wch: c % 2 === 1 ? 11 : 6 });
    }
    ws['!cols'] = cols;

    var thin = { style: 'thin', color: { rgb: 'B8C0C8' } };
    var border = { top: thin, bottom: thin, left: thin, right: thin };
    var headerFill = { patternType: 'solid', fgColor: { rgb: 'D9E2EC' } };
    var sectionFill = { patternType: 'solid', fgColor: { rgb: 'F0F4F8' } };
    var ref = ws['!ref'];
    if (!ref) return;
    var range = XLSX.utils.decode_range(ref);
    for (var R = range.s.r; R <= range.e.r; R++) {
      var rowLabel = aoa[R] && aoa[R][0] != null ? String(aoa[R][0]) : '';
      var isSection = rowLabel.indexOf('—') === 0 || rowLabel.indexOf('- ') === 0;
      for (var C = range.s.c; C <= range.e.c; C++) {
        var addr = XLSX.utils.encode_cell({ r: R, c: C });
        if (!ws[addr]) ws[addr] = { t: 's', v: '' };
        var cell = ws[addr];
        cell.s = cell.s || {};
        cell.s.border = border;
        cell.s.alignment = { vertical: 'center', horizontal: C === 0 ? 'left' : 'right' };
        if (R === 0) {
          cell.s.font = { bold: true };
          cell.s.fill = headerFill;
        } else if (isSection) {
          cell.s.font = { bold: true };
          cell.s.fill = sectionFill;
        }
      }
    }
  }

  function ensureDialog() {
    var el = document.getElementById('kpi-pl-mep-export-dialog');
    if (el) return el;
    el = document.createElement('div');
    el.id = 'kpi-pl-mep-export-dialog';
    el.className = 'kpi-pl-mep-export-dialog';
    el.hidden = true;
    el.innerHTML =
      '<div class="kpi-pl-mep-export-dialog__backdrop" data-export-close="1"></div>' +
      '<div class="kpi-pl-mep-export-dialog__panel" role="dialog" aria-modal="true" aria-labelledby="kpi-pl-mep-export-title">' +
      '<h2 class="kpi-pl-mep-export-dialog__title" id="kpi-pl-mep-export-title"></h2>' +
      '<p class="kpi-pl-mep-export-dialog__hint" id="kpi-pl-mep-export-hint"></p>' +
      '<label class="kpi-pl-mep-export-dialog__label" for="kpi-pl-mep-export-year"></label>' +
      '<select id="kpi-pl-mep-export-year" class="kpi-pl-mep-export-dialog__select"></select>' +
      '<fieldset class="kpi-pl-mep-export-dialog__fieldset">' +
      '<legend id="kpi-pl-mep-export-month-legend"></legend>' +
      '<label class="kpi-pl-mep-export-dialog__radio"><input type="radio" name="kpi-export-month-mode" value="all" checked> <span id="kpi-pl-mep-export-month-all"></span></label>' +
      '<label class="kpi-pl-mep-export-dialog__radio"><input type="radio" name="kpi-export-month-mode" value="one"> <span id="kpi-pl-mep-export-month-one"></span></label>' +
      '<select id="kpi-pl-mep-export-month" class="kpi-pl-mep-export-dialog__select" disabled></select>' +
      '</fieldset>' +
      '<div class="kpi-pl-mep-export-dialog__actions">' +
      '<button type="button" class="kpi-pl-mep-export-dialog__btn" data-export-close="1" id="kpi-pl-mep-export-cancel"></button>' +
      '<button type="button" class="kpi-pl-mep-export-dialog__btn kpi-pl-mep-export-dialog__btn--primary" id="kpi-pl-mep-export-run"></button>' +
      '</div></div>';
    document.body.appendChild(el);

    if (!document.getElementById('kpi-pl-mep-export-style')) {
      var st = document.createElement('style');
      st.id = 'kpi-pl-mep-export-style';
      st.textContent =
        '.kpi-pl-mep-export-dialog{position:fixed;inset:0;z-index:14000;display:flex;align-items:center;justify-content:center;}' +
        '.kpi-pl-mep-export-dialog[hidden]{display:none!important;}' +
        '.kpi-pl-mep-export-dialog__backdrop{position:absolute;inset:0;background:rgba(0,0,0,.55);}' +
        '.kpi-pl-mep-export-dialog__panel{position:relative;z-index:1;width:min(420px,92vw);padding:20px 22px;border:1px solid rgba(88,225,243,.55);border-radius:6px;background:#101820;color:#58e1f3;box-shadow:0 12px 40px rgba(0,0,0,.45);}' +
        'body.office-mode .kpi-pl-mep-export-dialog__panel{background:#fff;color:#111;border-color:#999;}' +
        '.kpi-pl-mep-export-dialog__title{margin:0 0 8px;font-size:18px;}' +
        '.kpi-pl-mep-export-dialog__hint{margin:0 0 14px;font-size:12px;opacity:.85;line-height:1.5;}' +
        '.kpi-pl-mep-export-dialog__label,.kpi-pl-mep-export-dialog__fieldset{display:block;margin:0 0 8px;font-size:13px;}' +
        '.kpi-pl-mep-export-dialog__fieldset{border:1px solid rgba(88,225,243,.28);border-radius:4px;padding:10px 12px;margin:12px 0;}' +
        'body.office-mode .kpi-pl-mep-export-dialog__fieldset{border-color:#ccc;}' +
        '.kpi-pl-mep-export-dialog__radio{display:flex;align-items:center;gap:8px;margin:6px 0;font-size:13px;}' +
        '.kpi-pl-mep-export-dialog__select{width:100%;margin:0 0 10px;padding:8px 10px;border:1px solid rgba(88,225,243,.45);border-radius:4px;background:#0a1218;color:#58e1f3;}' +
        'body.office-mode .kpi-pl-mep-export-dialog__select{background:#fff;color:#111;border-color:#999;}' +
        '.kpi-pl-mep-export-dialog__actions{display:flex;justify-content:flex-end;gap:10px;margin-top:8px;}' +
        '.kpi-pl-mep-export-dialog__btn{padding:8px 14px;border:1px solid rgba(88,225,243,.55);border-radius:4px;background:transparent;color:#58e1f3;cursor:pointer;}' +
        '.kpi-pl-mep-export-dialog__btn--primary{background:rgba(88,225,243,.2);}' +
        'body.office-mode .kpi-pl-mep-export-dialog__btn{border-color:#111;color:#111;}' +
        'body.office-mode .kpi-pl-mep-export-dialog__btn--primary{background:#111;color:#fff;}';
      document.head.appendChild(st);
    }

    el.addEventListener('click', function (ev) {
      var t = ev.target;
      if (t && t.getAttribute && t.getAttribute('data-export-close') === '1') closeDialog();
    });
    return el;
  }

  function localizeDialog(el) {
    el.querySelector('#kpi-pl-mep-export-title').textContent = t('収支データの出力', 'Export P&L data');
    el.querySelector('#kpi-pl-mep-export-hint').textContent = t(
      '選択した年の MEP（日次）と PL（月次）を1つのExcelに出力します。PLは常に1〜12月です。',
      'Exports MEP (daily) and PL (monthly) into one Excel file. PL always includes Jan–Dec.'
    );
    el.querySelector('label[for="kpi-pl-mep-export-year"]').textContent = t('年', 'Year');
    el.querySelector('#kpi-pl-mep-export-month-legend').textContent = t('MEPの月', 'MEP months');
    el.querySelector('#kpi-pl-mep-export-month-all').textContent = t('全月（1〜12月タブ）', 'All months (12 tabs)');
    el.querySelector('#kpi-pl-mep-export-month-one').textContent = t('選択した月のみ', 'Selected month only');
    el.querySelector('#kpi-pl-mep-export-cancel').textContent = t('キャンセル', 'Cancel');
    el.querySelector('#kpi-pl-mep-export-run').textContent = t('ダウンロード', 'Download');
  }

  function fillSelects(el) {
    var yearSel = el.querySelector('#kpi-pl-mep-export-year');
    var monthSel = el.querySelector('#kpi-pl-mep-export-month');
    var yNow = new Date().getFullYear();
    var yDef = defaultYear();
    yearSel.innerHTML = '';
    for (var y = yNow - 8; y <= yNow + 2; y++) {
      var opt = document.createElement('option');
      opt.value = String(y);
      opt.textContent = useJa() ? y + '年' : String(y);
      if (y === yDef) opt.selected = true;
      yearSel.appendChild(opt);
    }
    monthSel.innerHTML = '';
    var mDef = defaultMonth0();
    for (var m0 = 0; m0 < 12; m0++) {
      var o = document.createElement('option');
      o.value = String(m0);
      o.textContent = monthSheetName(m0);
      if (m0 === mDef) o.selected = true;
      monthSel.appendChild(o);
    }
    function syncMonthEnabled() {
      var mode = (el.querySelector('input[name="kpi-export-month-mode"]:checked') || {}).value;
      monthSel.disabled = mode !== 'one';
    }
    el.querySelectorAll('input[name="kpi-export-month-mode"]').forEach(function (r) {
      r.addEventListener('change', syncMonthEnabled);
    });
    syncMonthEnabled();
  }

  function openDialog() {
    var el = ensureDialog();
    localizeDialog(el);
    fillSelects(el);
    el.hidden = false;
    var run = el.querySelector('#kpi-pl-mep-export-run');
    run.onclick = function () {
      runExport(el).catch(function (err) {
        console.error(MARKER, err);
        window.alert(
          t(
            'Excel出力に失敗しました。通信環境を確認して再試行してください。',
            'Excel export failed. Check your connection and try again.'
          )
        );
      });
    };
  }

  function closeDialog() {
    var el = document.getElementById('kpi-pl-mep-export-dialog');
    if (el) el.hidden = true;
    var details = document.getElementById('header-dl');
    if (details) details.removeAttribute('open');
  }

  function runExport(el) {
    var year = Number(el.querySelector('#kpi-pl-mep-export-year').value);
    var mode = (el.querySelector('input[name="kpi-export-month-mode"]:checked') || {}).value || 'all';
    var month0 = Number(el.querySelector('#kpi-pl-mep-export-month').value);
    var runBtn = el.querySelector('#kpi-pl-mep-export-run');
    runBtn.disabled = true;
    return loadXlsx()
      .then(function (XLSX) {
        var wb = XLSX.utils.book_new();
        var months = mode === 'one' ? [month0] : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
        months.forEach(function (m0) {
          var aoa = buildMepSheetAoA(year, m0);
          var ws = XLSX.utils.aoa_to_sheet(aoa);
          styleWorkbookSheet(XLSX, ws, aoa);
          XLSX.utils.book_append_sheet(wb, ws, monthSheetName(m0));
        });
        var plAoa = buildPlSheetAoA(year);
        var plWs = XLSX.utils.aoa_to_sheet(plAoa);
        styleWorkbookSheet(XLSX, plWs, plAoa);
        XLSX.utils.book_append_sheet(wb, plWs, 'PL');
        var fname =
          mode === 'one'
            ? t('収支_' + year + '_' + (month0 + 1) + '月.xlsx', 'PL_' + year + '_M' + (month0 + 1) + '.xlsx')
            : t('収支_' + year + '.xlsx', 'PL_' + year + '.xlsx');
        XLSX.writeFile(wb, fname);
        closeDialog();
      })
      .finally(function () {
        runBtn.disabled = false;
      });
  }

  function onExportClick(ev) {
    ev.preventDefault();
    var btn = ev.currentTarget;
    if (!isPro()) {
      location.href = changePlanHref(btn);
      return;
    }
    openDialog();
  }

  function bind() {
    var btn = document.getElementById('kpi-export-pl-mep');
    if (!btn || btn.getAttribute('data-' + MARKER) === '1') return;
    btn.setAttribute('data-' + MARKER, '1');
    btn.addEventListener('click', onExportClick);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
  window.__KPI_PL_MEP_EXPORT = { open: openDialog, bind: bind };
})();

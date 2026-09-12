/**
 * Shared PL monthly expense → MEP dailyExpenses allocation.
 * Open days: explicit timeline.businessDays[iso] === 1 / true / '1' only.
 * Unset and closed days are not allocation targets. No sales/weekday inference.
 * Touched line-months are fully replaced (clear month, then redistribute).
 */
(function (global) {
  'use strict';

  var PL_EXP_PREFIX = 'kpi-pl-expenses-v1:';
  var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
  var STORE_KEY = 'kpiNavigator.kpiYearStore';

  function pad2(n) {
    return n < 10 ? '0' + n : String(n);
  }

  function emptyKpiStore() {
    return {
      meta: {
        schemaVersion: 4,
        operatingYear: new Date().getFullYear(),
        legacyMigrated: false,
        selectedDate: null
      },
      timeline: { dailySales: {}, businessDays: {} },
      years: {}
    };
  }

  function gwGetJson(key) {
    var gw = global.__KPI_DATA_GATEWAY;
    if (gw && typeof gw.getJson === 'function') return gw.getJson(key);
    try {
      var raw = localStorage.getItem(key);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object' ? parsed : null;
    } catch (_e) {
      return null;
    }
  }

  function gwSetJson(key, value) {
    var gw = global.__KPI_DATA_GATEWAY;
    if (gw && typeof gw.setJson === 'function') return gw.setJson(key, value);
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (_e) {
      return false;
    }
  }

  function loadCanonicalBusinessDayMap() {
    var store = gwGetJson(STORE_KEY);
    var bmap = store && store.timeline && store.timeline.businessDays;
    return bmap && typeof bmap === 'object' ? bmap : {};
  }

  /**
   * Allocation open-day only: explicit business_day === 1.
   * 1 / true / '1' = open. 0 / false / '0' = closed. missing key = unset.
   * Unset is not an open day. Do not infer from sales or weekday.
   */
  function isExplicitOpenBusinessDay(iso, bmap) {
    if (!iso || !bmap || typeof bmap !== 'object') return false;
    if (!Object.prototype.hasOwnProperty.call(bmap, iso)) return false;
    var v = bmap[iso];
    return v === true || v === 1 || v === '1';
  }

  function isBizDayIso(iso, bmap) {
    return isExplicitOpenBusinessDay(iso, bmap);
  }

  function listBizDayIsosInMonth(year, month0, bmap) {
    var daysInMonth = new Date(year, month0 + 1, 0).getDate();
    var list = [];
    var map = bmap && typeof bmap === 'object' ? bmap : {};
    for (var day = 1; day <= daysInMonth; day++) {
      var iso = year + '-' + pad2(month0 + 1) + '-' + pad2(day);
      if (isExplicitOpenBusinessDay(iso, map)) list.push(iso);
    }
    return list;
  }

  function loadPlExpenseAmountMap(year) {
    try {
      var raw = localStorage.getItem(PL_EXP_PREFIX + year);
      if (!raw) return {};
      var map = JSON.parse(raw);
      return map && typeof map === 'object' ? map : {};
    } catch (_e) {
      return {};
    }
  }

  function loadMonthlyExpenseLineIdsFromCatalog(opts) {
    opts = opts || {};
    var ids = [];
    var seen = {};
    try {
      var raw = localStorage.getItem(CATALOG_KEY);
      if (raw) {
        var parsed = JSON.parse(raw);
        var lines = parsed && Array.isArray(parsed.lines) ? parsed.lines : [];
        lines.forEach(function (line) {
          if (!line || !line.lineId) return;
          if (line.active === false) return;
          var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
          if (style === 'daily') return;
          if (seen[line.lineId]) return;
          seen[line.lineId] = true;
          ids.push(String(line.lineId));
        });
      }
    } catch (_e) {}
    if (ids.length) return ids;
    if (typeof document !== 'undefined' && document.querySelectorAll) {
      document.querySelectorAll(
        '.pl-data-row--expense-detail.pl-expense-detail-row--input-monthly'
      ).forEach(function (tr) {
        var id = tr.getAttribute('data-line-id');
        if (!id || seen[id]) return;
        seen[id] = true;
        ids.push(id);
      });
    }
    if (ids.length) return ids;
    var fallback = opts.monthlyLineIds;
    if (Array.isArray(fallback)) {
      fallback.forEach(function (id) {
        if (!id || seen[id]) return;
        seen[id] = true;
        ids.push(String(id));
      });
    }
    return ids;
  }

  function loadDailyExpenseLineIdsFromCatalog() {
    var ids = [];
    try {
      var raw = localStorage.getItem(CATALOG_KEY);
      if (!raw) return ids;
      var parsed = JSON.parse(raw);
      var lines = parsed && Array.isArray(parsed.lines) ? parsed.lines : [];
      lines.forEach(function (line) {
        if (!line || !line.lineId) return;
        if (line.active === false) return;
        var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
        if (style === 'daily') ids.push(String(line.lineId));
      });
    } catch (_e) {}
    return ids;
  }

  /** Floor + remainder on last biz day so monthly sum stays exact. */
  function allocateAmountAcrossBizDays(monthlyAmount, bizIsos) {
    var amount = Math.round(Number(monthlyAmount) || 0);
    var byDate = {};
    if (!bizIsos || !bizIsos.length || amount === 0) {
      return {
        byDate: byDate,
        perDayBase: 0,
        remainder: 0,
        sum: 0,
        skipped: amount !== 0 && (!bizIsos || !bizIsos.length) ? 'no_biz_days' : null
      };
    }
    var n = bizIsos.length;
    var base = Math.floor(amount / n);
    var rem = amount - base * n;
    for (var i = 0; i < n; i++) {
      byDate[bizIsos[i]] = base + (i === n - 1 ? rem : 0);
    }
    return { byDate: byDate, perDayBase: base, remainder: rem, sum: amount, skipped: null };
  }

  function normalizeTouchedKeys(touchedKeys) {
    var out = [];
    if (!Array.isArray(touchedKeys)) return out;
    touchedKeys.forEach(function (item) {
      if (item == null || item === '') return;
      if (typeof item === 'string') {
        var idx = item.lastIndexOf(':');
        if (idx <= 0) return;
        var lineId = item.slice(0, idx);
        var month0 = Number(item.slice(idx + 1));
        if (!lineId || !Number.isFinite(month0)) return;
        out.push({ row: lineId, month: month0, key: item });
        return;
      }
      var row = item.row != null ? String(item.row) : '';
      var month = Number(item.month);
      if (!row || !Number.isFinite(month)) return;
      out.push({
        row: row,
        month: month,
        key: item.key || row + ':' + month
      });
    });
    return out;
  }

  /**
   * Phase B preview: monthly PL → per-biz-day. Does NOT write MEP.
   * opts: { year?, month0? (0-11, omit=all), lineId?, amountMap?, monthlyLineIds? }
   */
  function previewMonthlyExpenseAllocation(opts) {
    opts = opts || {};
    var year = opts.year != null ? Number(opts.year) : new Date().getFullYear();
    if (!Number.isFinite(year)) year = new Date().getFullYear();
    var amountMap = opts.amountMap || loadPlExpenseAmountMap(year);
    var bmap =
      opts.businessDayByDate && typeof opts.businessDayByDate === 'object'
        ? opts.businessDayByDate
        : loadCanonicalBusinessDayMap();
    var monthlyIds = loadMonthlyExpenseLineIdsFromCatalog(opts);
    if (opts.lineId) {
      monthlyIds = monthlyIds.filter(function (id) {
        return id === opts.lineId;
      });
    }
    var skippedDaily = loadDailyExpenseLineIdsFromCatalog();
    var monthIndexes = [];
    if (opts.month0 != null && Number.isFinite(Number(opts.month0))) {
      monthIndexes.push(Number(opts.month0));
    } else {
      for (var m = 0; m < 12; m++) monthIndexes.push(m);
    }

    var months = [];
    monthIndexes.forEach(function (month0) {
      if (month0 < 0 || month0 > 11) return;
      var bizDays = listBizDayIsosInMonth(year, month0, bmap);
      var lines = {};
      monthlyIds.forEach(function (lineId) {
        var key = lineId + ':' + month0;
        var monthlyAmount = Object.prototype.hasOwnProperty.call(amountMap, key)
          ? Math.round(Number(amountMap[key]) || 0)
          : 0;
        var alloc = allocateAmountAcrossBizDays(monthlyAmount, bizDays);
        lines[lineId] = {
          lineId: lineId,
          monthlyAmount: monthlyAmount,
          inputStyle: 'monthly',
          perDayBase: alloc.perDayBase,
          remainder: alloc.remainder,
          byDate: alloc.byDate,
          sum: alloc.sum,
          skipped: alloc.skipped
        };
      });
      months.push({
        year: year,
        month0: month0,
        month: month0 + 1,
        bizDayCount: bizDays.length,
        bizDays: bizDays,
        lines: lines
      });
    });

    return {
      year: year,
      months: months,
      monthlyLineIds: monthlyIds,
      skippedDailyLineIds: skippedDaily,
      wroteToMep: false
    };
  }

  /**
   * Phase C: write monthly PL amounts (÷ biz days) into MEP dailyExpenses.
   * Only monthly-style expense lines. Daily lines (MEP-entered) are never touched.
   * Re-allocation: for each touched line-month, always clear that month's existing
   * dailyExpenses first, then write the fresh allocation (or leave empty if amount 0 /
   * no explicit open days). Never skip a touched 0 amount.
   * opts: { year?, month0? (0-11, omit = all 12), touchedKeys?, monthlyLineIds?, amountMap?,
   *         allowLockedYearImport?, source? }
   * Regular PL Save must not pass allowLockedYearImport. CSV import may pass
   * allowLockedYearImport: true with source: 'csv-import' to write a locked past year.
   */
  function writeMonthlyExpenseAllocationToMep(opts) {
    opts = opts || {};
    var year = opts.year != null ? Number(opts.year) : new Date().getFullYear();
    if (!Number.isFinite(year)) year = new Date().getFullYear();

    var gw = global.__KPI_DATA_GATEWAY;
    if (!gw || typeof gw.getJson !== 'function' || typeof gw.setJson !== 'function') {
      return { ok: false, reason: 'no_gateway', wrote: false, year: year };
    }

    var store = gw.getJson(STORE_KEY);
    if (!store || typeof store !== 'object') {
      store = emptyKpiStore();
    }
    if (!store.meta || typeof store.meta !== 'object') {
      store.meta = emptyKpiStore().meta;
    }
    if (!store.years || typeof store.years !== 'object') store.years = {};

    var operatingYear = Number(store.meta.operatingYear);
    if (!Number.isFinite(operatingYear)) operatingYear = new Date().getFullYear();

    var rec = store.years[year];
    var allowLockedYearImport = opts.allowLockedYearImport === true;
    if (rec && rec.status === 'locked' && year < operatingYear && !allowLockedYearImport) {
      return { ok: false, reason: 'year_locked', wrote: false, year: year };
    }
    if (!rec || typeof rec !== 'object') {
      rec = { year: year, status: 'open', plan: {} };
      store.years[year] = rec;
    }
    if (!rec.dailyExpenses || typeof rec.dailyExpenses !== 'object') rec.dailyExpenses = {};
    if (!store.timeline || typeof store.timeline !== 'object') {
      store.timeline = { dailySales: {}, businessDays: {} };
    }
    if (!store.timeline.businessDays || typeof store.timeline.businessDays !== 'object') {
      store.timeline.businessDays = {};
    }

    var previewOpts = {
      year: year,
      amountMap: opts.amountMap,
      monthlyLineIds: opts.monthlyLineIds,
      businessDayByDate: store.timeline.businessDays
    };
    if (opts.month0 != null && Number.isFinite(Number(opts.month0))) {
      previewOpts.month0 = Number(opts.month0);
    }
    var preview = previewMonthlyExpenseAllocation(previewOpts);
    var monthlyIds = preview.monthlyLineIds || [];
    var monthFilter = null;
    if (opts.touchedKeys && Array.isArray(opts.touchedKeys)) {
      monthFilter = {};
      var monthlySet = {};
      monthlyIds.forEach(function (id) {
        monthlySet[id] = true;
      });
      normalizeTouchedKeys(opts.touchedKeys).forEach(function (item) {
        if (!monthlySet[item.row]) return;
        monthFilter[item.row + ':' + item.month] = true;
      });
      if (!Object.keys(monthFilter).length) {
        return {
          ok: true,
          wrote: false,
          skipped: true,
          reason: 'no_monthly_touched',
          year: year,
          monthlyLineIds: monthlyIds,
          skippedDailyLineIds: preview.skippedDailyLineIds || []
        };
      }
    }
    var changed = false;
    var replacedKeys = monthFilter ? Object.keys(monthFilter) : [];

    (preview.months || []).forEach(function (block) {
      var prefix = year + '-' + pad2(block.month0 + 1) + '-';
      monthlyIds.forEach(function (lineId) {
        if (monthFilter && !monthFilter[lineId + ':' + block.month0]) return;
        if (!monthFilter) replacedKeys.push(lineId + ':' + block.month0);
        /* Touched line-month: always replace. Amount 0 still clears the month. */
        changed = true;
        var byRow = rec.dailyExpenses[lineId];
        if (byRow && typeof byRow === 'object') {
          Object.keys(byRow).forEach(function (iso) {
            if (iso.indexOf(prefix) === 0) delete byRow[iso];
          });
        }
        var lineAlloc = (block.lines && block.lines[lineId]) || null;
        var byDate = lineAlloc && lineAlloc.byDate ? lineAlloc.byDate : null;
        if (!byDate) return;
        var isos = Object.keys(byDate);
        if (!isos.length) return;
        if (!rec.dailyExpenses[lineId] || typeof rec.dailyExpenses[lineId] !== 'object') {
          rec.dailyExpenses[lineId] = {};
        }
        isos.forEach(function (iso) {
          rec.dailyExpenses[lineId][iso] = Math.round(Number(byDate[iso]) || 0);
        });
      });
    });

    Object.keys(rec.dailyExpenses).forEach(function (lineId) {
      var byRow = rec.dailyExpenses[lineId];
      if (byRow && typeof byRow === 'object' && !Object.keys(byRow).length) {
        delete rec.dailyExpenses[lineId];
      }
    });

    rec.mepUpdatedAt = Date.now();
    var saved = gwSetJson(STORE_KEY, store);
    if (saved) {
      try {
        document.dispatchEvent(
          new CustomEvent('kpi:mepDataChanged', {
            detail: {
              year: year,
              source: 'pl-monthly-allocate',
              replacedKeys: replacedKeys
            }
          })
        );
      } catch (_e) {}
    }
    return {
      ok: saved,
      wrote: changed,
      year: year,
      monthlyLineIds: monthlyIds,
      replacedKeys: replacedKeys,
      skippedDailyLineIds: preview.skippedDailyLineIds || []
    };
  }

  var api = {
    pad2: pad2,
    isExplicitOpenBusinessDay: isExplicitOpenBusinessDay,
    isBizDayIso: isBizDayIso,
    listBizDayIsosInMonth: listBizDayIsosInMonth,
    allocateAmountAcrossBizDays: allocateAmountAcrossBizDays,
    loadPlExpenseAmountMap: loadPlExpenseAmountMap,
    previewMonthlyExpenseAllocation: previewMonthlyExpenseAllocation,
    writeMonthlyExpenseAllocationToMep: writeMonthlyExpenseAllocationToMep,
    normalizeTouchedKeys: normalizeTouchedKeys
  };

  global.KpiPlMonthlyAllocate = api;
  global.__plAllocateAmountAcrossBizDays = allocateAmountAcrossBizDays;
  global.__plPreviewMonthlyExpenseAllocation = previewMonthlyExpenseAllocation;
  global.__plWriteMonthlyExpenseAllocationToMep = writeMonthlyExpenseAllocationToMep;
})(typeof window !== 'undefined' ? window : this);

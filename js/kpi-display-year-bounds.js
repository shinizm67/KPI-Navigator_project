/**
 * KPI Navigator — displayYear bounds (canonical)
 *
 * Shared by Annual / Monthly / MEP / PL / Daily display-year navigation.
 * Do NOT mix operatingYear / planningYear into these bounds.
 *
 * Spec:
 * - Unstarted (no real Sales / Past Sales / expense > 0): 2000 .. 2100
 * - Started: oldest real-data year .. (calendar today year + 10)
 *
 * Ignored for "started" / oldest: 0 keys, business-day keys, H/L defaults,
 * plan auto values, memos, bookings/reservations.
 */
(function (global) {
  var DISPLAY_MIN_FLOOR = 2000;
  var DISPLAY_MAX_CEILING = 2100;
  var FUTURE_YEARS = 10;

  function getJsonSafe(key) {
    try {
      var g = global.__KPI_DATA_GATEWAY;
      if (g && typeof g.getJson === 'function') {
        var v = g.getJson(key);
        if (v != null) return v;
      }
    } catch (_e0) {}
    try {
      if (typeof localStorage === 'undefined') return null;
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (_e1) {
      return null;
    }
  }

  function getDisplayYearBounds() {
    var oldest = null;
    function considerYear(y) {
      y = Number(y);
      if (!Number.isFinite(y)) return;
      if (oldest == null || y < oldest) oldest = y;
    }
    function considerIsoAmountMap(map) {
      if (!map || typeof map !== 'object') return;
      Object.keys(map).forEach(function (k) {
        var m = /^(\d{4})-\d{2}-\d{2}$/.exec(String(k));
        if (!m) return;
        var n = Number(map[k]);
        if (!Number.isFinite(n) || n <= 0) return;
        considerYear(Number(m[1]));
      });
    }
    function considerYearKeyedAmounts(map, year) {
      if (!map || typeof map !== 'object') return;
      Object.keys(map).forEach(function (k) {
        var n = Number(map[k]);
        if (Number.isFinite(n) && n > 0) considerYear(year);
      });
    }
    function considerDailyExpenses(dailyExpenses) {
      if (!dailyExpenses || typeof dailyExpenses !== 'object') return;
      Object.keys(dailyExpenses).forEach(function (lineId) {
        considerIsoAmountMap(dailyExpenses[lineId]);
      });
    }

    var data = global.__ANNUAL_DATA || {};
    var daily = data.daily || {};
    considerIsoAmountMap(daily.targetSalesByDate);

    var past = data.pastSales || {};
    considerIsoAmountMap(past.salesByDate);
    var refY = past.referenceAnnualSalesByYear;
    if (refY && typeof refY === 'object') {
      Object.keys(refY).forEach(function (yk) {
        var n = Number(refY[yk]);
        if (Number.isFinite(n) && n > 0) considerYear(Number(yk));
      });
    }

    var pastGw = getJsonSafe('kpiNavigator.pastSalesShared');
    if (pastGw && typeof pastGw === 'object') {
      considerIsoAmountMap(pastGw.salesByDate);
      var refGw = pastGw.referenceAnnualSalesByYear;
      if (refGw && typeof refGw === 'object') {
        Object.keys(refGw).forEach(function (yk) {
          var n = Number(refGw[yk]);
          if (Number.isFinite(n) && n > 0) considerYear(Number(yk));
        });
      }
    }

    var store = null;
    try {
      if (global.KpiYearStore && typeof global.KpiYearStore.getStore === 'function') {
        store = global.KpiYearStore.getStore();
      }
    } catch (_e2) {}
    if (!store || typeof store !== 'object') {
      store = getJsonSafe('kpiNavigator.kpiYearStore');
    }
    if (store && store.timeline) {
      considerIsoAmountMap(store.timeline.dailySales);
    }
    var yearsObj = (store && store.years) || {};
    Object.keys(yearsObj).forEach(function (yk) {
      var y = Number(yk);
      var rec = yearsObj[yk];
      if (!rec || typeof rec !== 'object') return;
      considerDailyExpenses(rec.dailyExpenses);
      if (Number.isFinite(y)) {
        considerYearKeyedAmounts(getJsonSafe('kpi-pl-expenses-v1:' + y), y);
      }
    });

    if (oldest == null) {
      return { minYear: DISPLAY_MIN_FLOOR, maxYear: DISPLAY_MAX_CEILING };
    }
    var minYear = oldest;
    if (minYear < DISPLAY_MIN_FLOOR) minYear = DISPLAY_MIN_FLOOR;
    var maxYear = new Date().getFullYear() + FUTURE_YEARS;
    if (minYear > maxYear) minYear = maxYear;
    return { minYear: minYear, maxYear: maxYear };
  }

  global.__KPI_getDisplayYearBounds = getDisplayYearBounds;
  global.KpiDisplayYearBounds = {
    MIN_FLOOR: DISPLAY_MIN_FLOOR,
    MAX_CEILING: DISPLAY_MAX_CEILING,
    FUTURE_YEARS: FUTURE_YEARS,
    getBounds: getDisplayYearBounds,
  };
})(typeof window !== 'undefined' ? window : this);

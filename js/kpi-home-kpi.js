/* Home collapsed KPIs.
   Prefers store.years[y].dailyFacts, the snapshot KpiYearStore.invalidateDailyFacts
   writes and Daily FW reads through metricsFromDailyFacts / __computeTwMetricsForIso.
   Does not copy HL daily-target allocation. If that snapshot is missing, sales are
   summed from timeline.dailySales with the UI business-day rule and targets stay blank. */
(function () {
  'use strict';

  var DASH = '—';
  var STORE_KEY = 'kpiNavigator.kpiYearStore';
  var remoteFacts = {};
  var remoteLoaded = {};
  var remotePending = {};
  var lastIso = '';

  function readStore() {
    try {
      var gw = window.__KPI_DATA_GATEWAY;
      var store = gw && typeof gw.getJson === 'function' ? gw.getJson(STORE_KEY) : null;
      if (store && typeof store === 'object') return store;
    } catch (_e) {}
    try {
      var raw = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
      if (raw && typeof raw === 'object') return raw;
    } catch (_e2) {}
    return null;
  }

  function yearOf(iso) {
    return Number(String(iso || '').slice(0, 4));
  }

  function operatingYear(store) {
    var y = store && store.meta ? Number(store.meta.operatingYear) : NaN;
    return Number.isFinite(y) ? y : new Date().getFullYear();
  }

  function yearRec(store, year) {
    if (!store || !store.years) return null;
    return store.years[year] || store.years[String(year)] || null;
  }

  function hasSavedPlan(store, year) {
    var rec = yearRec(store, year);
    if (!rec || !rec.plan) return false;
    if (String(rec.plan.source || '') !== 'sales-data-save') return false;
    var n = Number(rec.plan.targetSales);
    return Number.isFinite(n) && n > 0;
  }

  function isUiBusinessDay(store, iso) {
    var bmap = store && store.timeline ? store.timeline.businessDays : null;
    if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
    return true;
  }

  function salesAmt(store, iso) {
    var smap = store && store.timeline ? store.timeline.dailySales : null;
    if (!smap || !Object.prototype.hasOwnProperty.call(smap, iso)) return 0;
    var n = Number(smap[iso]);
    if (!Number.isFinite(n)) return 0;
    if (n === 1234) {
      var y = yearOf(iso);
      if (Number.isFinite(y) && y < operatingYear(store)) return n;
      return 0;
    }
    return n;
  }

  function factsFor(store, iso) {
    var rec = yearRec(store, yearOf(iso));
    if (!rec || !rec.dailyFacts) return null;
    return rec.dailyFacts[iso] || null;
  }

  function factsUsable(store, iso, fact) {
    if (!fact) return false;
    var annualTarget = hasSavedPlan(store, yearOf(iso)) ? Number(yearRec(store, yearOf(iso)).plan.targetSales) : 0;
    if (
      annualTarget > 0 &&
      !(Number(fact.dailyTarget) > 0) &&
      !(Number(fact.mtdTarget) > 0) &&
      !(Number(fact.ytdTarget) > 0)
    ) {
      return false;
    }
    return true;
  }

  function numOrNull(v) {
    if (v == null || v === '') return null;
    var n = Number(v);
    return Number.isFinite(n) ? n : null;
  }

  function walkSales(store, iso) {
    var y = yearOf(iso);
    var m0 = Number(String(iso).slice(5, 7)) - 1;
    var mtdA = 0;
    var ytdA = 0;
    var dailySales = 0;
    var open = false;
    if (!Number.isFinite(y) || !Number.isFinite(m0)) return null;
    for (var m = 0; m < 12; m++) {
      var dc = new Date(y, m + 1, 0).getDate();
      for (var day = 1; day <= dc; day++) {
        var dayIso = y + '-' + (m + 1 < 10 ? '0' : '') + (m + 1) + '-' + (day < 10 ? '0' : '') + day;
        if (dayIso > iso) break;
        if (!isUiBusinessDay(store, dayIso)) {
          if (dayIso === iso) open = false;
          continue;
        }
        var amt = salesAmt(store, dayIso);
        ytdA += amt;
        if (m === m0) mtdA += amt;
        if (dayIso === iso) {
          open = true;
          dailySales = amt;
        }
      }
    }
    return {
      isBusinessToday: open,
      hasPlan: false,
      dailySales: dailySales,
      dailyTarget: null,
      mtdA: mtdA,
      mtdT: null,
      ytdA: ytdA,
      ytdT: null
    };
  }

  function rowToFact(row) {
    return {
      sales: row.sales,
      businessDay: !!row.businessDay,
      dailyTarget: row.dailyTarget,
      mtdActual: row.mtdActual,
      mtdTarget: row.mtdTarget,
      ytdActual: row.ytdActual,
      ytdTarget: row.ytdTarget
    };
  }

  function adoptRows(rows) {
    var n = 0;
    (rows || []).forEach(function (row) {
      if (!row || !row.iso) return;
      remoteFacts[row.iso] = rowToFact(row);
      n += 1;
    });
    return n;
  }

  function yearHasRemote(year) {
    var prefix = String(year) + '-';
    var keys = Object.keys(remoteFacts);
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].indexOf(prefix) === 0) return true;
    }
    return false;
  }

  /* Blob persist strips dailyFacts. Read the server snapshot, then the existing
     rebuild endpoint once if that year has a saved plan and no rows yet. */
  function loadRemoteYear(year) {
    if (remoteLoaded[year]) return Promise.resolve();
    if (remotePending[year]) return remotePending[year];
    var sync = window.__KPI_DAILY_FACTS_SYNC;
    if (!sync || typeof sync.hydrateWindow !== 'function') {
      remoteLoaded[year] = true;
      return Promise.resolve();
    }
    remotePending[year] = Promise.resolve()
      .then(function () {
        return sync.hydrateWindow({ force: true, backfill: false, year: year });
      })
      .then(function (data) {
        adoptRows(data && data.rows);
        if (yearHasRemote(year) || !hasSavedPlan(readStore(), year) || typeof sync.rebuildYear !== 'function') {
          return null;
        }
        return sync.rebuildYear(year).then(function (res) {
          if (!res || res.ok !== true) return null;
          return sync.hydrateWindow({ force: true, backfill: false, year: year });
        }).then(function (data2) {
          adoptRows(data2 && data2.rows);
        });
      })
      .catch(function () {})
      .then(function () {
        remoteLoaded[year] = true;
        delete remotePending[year];
      });
    return remotePending[year];
  }

  function metricsFor(iso) {
    var store = readStore();
    if (!store || !/^\d{4}-\d{2}-\d{2}$/.test(String(iso || ''))) return null;
    var fact = remoteFacts[iso] || factsFor(store, iso);
    if (factsUsable(store, iso, fact)) {
      var openFact = !!fact.businessDay;
      return {
        isBusinessToday: openFact,
        hasPlan: hasSavedPlan(store, yearOf(iso)),
        dailySales: Number(fact.sales) || 0,
        dailyTarget: openFact ? numOrNull(fact.dailyTarget) : null,
        mtdA: Number(fact.mtdActual) || 0,
        mtdT: numOrNull(fact.mtdTarget),
        ytdA: Number(fact.ytdActual) || 0,
        ytdT: numOrNull(fact.ytdTarget)
      };
    }
    return walkSales(store, iso);
  }

  function money(n) {
    if (n == null || !Number.isFinite(Number(n))) return DASH;
    var v = Math.round(Number(n));
    if (window.KpiCurrency && typeof KpiCurrency.format === 'function') {
      return KpiCurrency.format(v, { round: true });
    }
    return String(v);
  }

  function signed(n) {
    if (!Number.isFinite(n)) return DASH;
    if (n === 0) return money(0);
    if (window.KpiCurrency && typeof KpiCurrency.format === 'function') {
      return KpiCurrency.format(n, { round: true, signed: true });
    }
    return (n > 0 ? '+' : '−') + money(Math.abs(n));
  }

  function diff(actual, target) {
    if (!Number.isFinite(actual) || !Number.isFinite(target)) return DASH;
    return signed(actual - target);
  }

  function ach(actual, target) {
    if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return DASH;
    var pct = (actual / target) * 100;
    if (!Number.isFinite(pct)) return DASH;
    return Math.round(pct) + '%';
  }

  function cellsFor(kind, m) {
    if (!m) return [DASH, DASH, DASH, DASH];
    if (kind === 'daily') {
      if (!m.isBusinessToday) return [DASH, DASH, DASH, DASH];
      if (m.dailyTarget == null) return [money(m.dailySales), DASH, DASH, DASH];
      return [
        money(m.dailySales),
        money(m.dailyTarget),
        diff(m.dailySales, m.dailyTarget),
        ach(m.dailySales, m.dailyTarget)
      ];
    }
    var actual = kind === 'monthly' ? m.mtdA : m.ytdA;
    var target = kind === 'monthly' ? m.mtdT : m.ytdT;
    if (!m.hasPlan || target == null) return [money(actual), DASH, DASH, DASH];
    return [money(actual), money(target), diff(actual, target), ach(actual, target)];
  }

  function paint(iso) {
    lastIso = iso;
    var localFact = factsFor(readStore(), iso);
    var store = readStore();
    if (
      iso &&
      !remoteFacts[iso] &&
      !factsUsable(store, iso, localFact) &&
      !remoteLoaded[yearOf(iso)]
    ) {
      loadRemoteYear(yearOf(iso)).then(function () {
        if (lastIso === iso) paint(iso);
      });
    }
    var m = metricsFor(iso);
    document.querySelectorAll('[data-home-window]').forEach(function (win) {
      var kind = win.getAttribute('data-home-window');
      var texts = cellsFor(kind, m);
      var nodes = win.querySelectorAll('.home-window__kpi-value');
      for (var i = 0; i < nodes.length; i++) {
        nodes[i].textContent = texts[i] != null ? texts[i] : DASH;
      }
    });
  }

  window.__KPI_HOME_KPI = {
    paint: paint,
    metrics: metricsFor
  };
})();

/**
 * Phase 2c — daily facts window sync (parallel with store.php blob).
 * Work window: focus calendar year + 2 months past Jan 1 / past Dec 31.
 * Does not replace blob hydrate. Screens still use existing calc (phase 3).
 */
(function () {
  'use strict';

  if (window.__KPI_DAILY_FACTS_SYNC) return;

  var SYNC_KEY = 'kpiNavigator.storeSync';
  var PAD_MONTHS = 2;
  var putTimers = {};
  var lastGetYear = null;
  var bootStarted = false;

  function pad2(n) {
    return n < 10 ? '0' + n : String(n);
  }

  function resolveAppRoot() {
    try {
      if (window.__KPI_AUTH && typeof window.__KPI_AUTH.resolveAppRoot === 'function') {
        return window.__KPI_AUTH.resolveAppRoot();
      }
    } catch (_e) {}
    var path = window.location.pathname || '';
    var m = path.match(/^(.*?\/kpi-navigator)(?:\/|$)/);
    if (m) return m[1];
    return '';
  }

  function factsUrl() {
    return resolveAppRoot() + '/api/v1/daily-facts.php';
  }

  function readSyncEnabled() {
    try {
      if (window.__KPI_STORE_SYNC && window.__KPI_STORE_SYNC.enabled != null) {
        return !!window.__KPI_STORE_SYNC.enabled;
      }
    } catch (_e0) {}
    try {
      var raw = localStorage.getItem(SYNC_KEY);
      if (!raw) return false;
      var o = JSON.parse(raw);
      return !!(o && o.enabled);
    } catch (_e1) {
      return false;
    }
  }

  function buildHeaders() {
    var headers = { 'Content-Type': 'application/json' };
    try {
      var raw = localStorage.getItem(SYNC_KEY);
      var o = raw ? JSON.parse(raw) : null;
      if (o && o.token) headers['X-KPI-Store-Token'] = String(o.token);
    } catch (_e) {}
    return headers;
  }

  function shiftMonth(year, month0, delta) {
    var d = new Date(year, month0 + delta, 1);
    return { y: d.getFullYear(), m0: d.getMonth() };
  }

  function workWindow(year) {
    var y = Number(year);
    var start = shiftMonth(y, 0, -PAD_MONTHS);
    var end = shiftMonth(y, 11, PAD_MONTHS);
    var endLast = new Date(end.y, end.m0 + 1, 0).getDate();
    return {
      from: start.y + '-' + pad2(start.m0 + 1) + '-01',
      to: end.y + '-' + pad2(end.m0 + 1) + '-' + pad2(endLast),
    };
  }

  function focusYear() {
    if (window.KpiYearStore) {
      var iso =
        typeof KpiYearStore.getSelectedDate === 'function'
          ? KpiYearStore.getSelectedDate()
          : null;
      if (iso && /^\d{4}-\d{2}-\d{2}$/.test(iso)) return Number(iso.slice(0, 4));
      if (typeof KpiYearStore.getOperatingYear === 'function') {
        return KpiYearStore.getOperatingYear();
      }
    }
    var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
    if (Number.isFinite(cy)) return cy;
    return new Date().getFullYear();
  }

  function applyRows(rows) {
    if (!window.KpiYearStore || typeof KpiYearStore.getStore !== 'function') return;
    if (!rows || !rows.length) return;
    var store = KpiYearStore.getStore();
    if (!store.years) store.years = {};
    rows.forEach(function (row) {
      if (!row || !row.iso) return;
      var y = Number(String(row.iso).slice(0, 4));
      if (!Number.isFinite(y)) return;
      if (!store.years[y]) store.years[y] = { year: y, plan: {} };
      if (!store.years[y].dailyFacts || typeof store.years[y].dailyFacts !== 'object') {
        store.years[y].dailyFacts = {};
      }
      store.years[y].dailyFacts[row.iso] = {
        sales: row.sales,
        businessDay: !!row.businessDay,
        dailyTarget: row.dailyTarget,
        mtdActual: row.mtdActual,
        mtdTarget: row.mtdTarget,
        ytdActual: row.ytdActual,
        ytdTarget: row.ytdTarget,
      };
    });
    try {
      if (typeof window.__invalidateTwSalesThroughCache === 'function') {
        window.__invalidateTwSalesThroughCache();
      }
    } catch (_eInv) {}
    try {
      document.dispatchEvent(new CustomEvent('kpi:readSurfacesRefresh', { detail: { source: 'daily-facts' } }));
    } catch (_eRef) {}
  }

  function collectYearRows(year) {
    if (!window.KpiYearStore || typeof KpiYearStore.getStore !== 'function') return [];
    var rec = KpiYearStore.getStore().years[year];
    if (!rec || !rec.dailyFacts || typeof rec.dailyFacts !== 'object') return [];
    var out = [];
    Object.keys(rec.dailyFacts).forEach(function (iso) {
      if (Number(String(iso).slice(0, 4)) !== Number(year)) return;
      var f = rec.dailyFacts[iso];
      if (!f) return;
      out.push({
        iso: iso,
        sales: f.sales,
        businessDay: !!f.businessDay,
        dailyTarget: f.dailyTarget,
        mtdActual: f.mtdActual,
        mtdTarget: f.mtdTarget,
        ytdActual: f.ytdActual,
        ytdTarget: f.ytdTarget,
      });
    });
    return out;
  }

  function putYear(year) {
    if (!readSyncEnabled()) return;
    var y = Number(year);
    if (!Number.isFinite(y)) return;
    var rows = collectYearRows(y);
    if (!rows.length) return;
    fetch(factsUrl(), {
      method: 'PUT',
      headers: buildHeaders(),
      credentials: 'include',
      body: JSON.stringify({ rows: rows }),
    }).catch(function () {});
  }

  function schedulePutYear(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) return;
    if (putTimers[y]) window.clearTimeout(putTimers[y]);
    putTimers[y] = window.setTimeout(function () {
      delete putTimers[y];
      putYear(y);
    }, 400);
  }

  function hydrateWindow(opts) {
    opts = opts || {};
    if (!readSyncEnabled()) return;
    var year = opts.year != null ? Number(opts.year) : focusYear();
    if (!Number.isFinite(year)) return;
    if (!opts.force && lastGetYear === year) return;
    lastGetYear = year;
    var win = workWindow(year);
    var url = factsUrl() + '?from=' + encodeURIComponent(win.from) + '&to=' + encodeURIComponent(win.to);
    fetch(url, { method: 'GET', credentials: 'include' })
      .then(function (res) {
        if (!res.ok) return null;
        return res.json();
      })
      .then(function (data) {
        if (!data || !data.ok) return;
        applyRows(data.rows || []);
        var serverHasYear = (data.rows || []).some(function (row) {
          return row && String(row.iso).indexOf(String(year) + '-') === 0;
        });
        if (!serverHasYear && opts.backfill) {
          putYear(year);
        }
      })
      .catch(function () {});
  }

  function bootOnce() {
    if (bootStarted) return;
    bootStarted = true;
    hydrateWindow({ force: true, backfill: true });
  }

  document.addEventListener('kpi:storeHydratedFromServer', function () {
    bootOnce();
  });
  window.setTimeout(bootOnce, 2500);

  document.addEventListener('annual:calendarYearChanged', function (ev) {
    var y = ev && ev.detail && ev.detail.year != null ? Number(ev.detail.year) : NaN;
    hydrateWindow({
      force: true,
      backfill: true,
      year: Number.isFinite(y) ? y : focusYear(),
    });
  });

  window.__KPI_DAILY_FACTS_SYNC = {
    schedulePutYear: schedulePutYear,
    putYear: putYear,
    hydrateWindow: hydrateWindow,
    workWindow: workWindow,
  };
})();

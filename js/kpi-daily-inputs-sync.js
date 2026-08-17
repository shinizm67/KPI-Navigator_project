/**
 * snapshot-store 入力正本化 — Dual Write + window GET for kpi_daily_inputs.
 * AN: Save/merge → PUT inputs (+ timeline blob は既存どおり).
 * AO: 窓 GET → timeline にマージ。失敗時は blob/LS のまま (fallback).
 * Marker: KPI-DAILY-INPUTS-SYNC-AN
 */
(function () {
  'use strict';

  if (window.__KPI_DAILY_INPUTS_SYNC) return;

  var SYNC_KEY = 'kpiNavigator.storeSync';
  var PAD_MONTHS = 2;
  var putTimers = {};
  var bootStarted = false;
  var lastHydrateOk = false;

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

  function inputsUrl() {
    return resolveAppRoot() + '/api/v1/daily-inputs.php';
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

  function applyInputRows(rows) {
    if (!window.KpiYearStore || typeof KpiYearStore.getStore !== 'function') return false;
    if (!rows || !rows.length) return false;
    var store = KpiYearStore.getStore();
    if (!store.timeline) store.timeline = { dailySales: {}, businessDays: {} };
    if (!store.timeline.dailySales) store.timeline.dailySales = {};
    if (!store.timeline.businessDays) store.timeline.businessDays = {};
    var changed = false;
    rows.forEach(function (row) {
      if (!row || !row.iso) return;
      var sales = Number(row.sales);
      if (!Number.isFinite(sales)) sales = 0;
      var biz = !!row.businessDay;
      var prevS = store.timeline.dailySales[row.iso];
      var prevB = store.timeline.businessDays[row.iso];
      store.timeline.dailySales[row.iso] = sales;
      store.timeline.businessDays[row.iso] = biz;
      if (prevS !== sales || prevB !== biz) changed = true;
    });
    return changed;
  }

  function hydrateWindow(opts) {
    opts = opts || {};
    if (!readSyncEnabled()) {
      lastHydrateOk = false;
      return Promise.resolve({ ok: false, error: 'sync_off', fallback: true });
    }
    var year = opts.year != null ? Number(opts.year) : focusYear();
    if (!Number.isFinite(year)) {
      lastHydrateOk = false;
      return Promise.resolve({ ok: false, error: 'invalid_year', fallback: true });
    }
    var win = workWindow(year);
    var url = inputsUrl() + '?from=' + encodeURIComponent(win.from) + '&to=' + encodeURIComponent(win.to);
    return fetch(url, {
      method: 'GET',
      headers: buildHeaders(),
      credentials: 'include',
    })
      .then(function (res) {
        return res.json().then(
          function (data) {
            if (!res.ok || !data || !data.ok) {
              lastHydrateOk = false;
              return { ok: false, error: (data && data.error) || 'http_' + res.status, fallback: true };
            }
            applyInputRows(data.rows || []);
            lastHydrateOk = true;
            try {
              document.dispatchEvent(
                new CustomEvent('kpi:dailyInputsHydrated', {
                  detail: { year: year, from: win.from, to: win.to, count: (data.rows || []).length },
                })
              );
            } catch (_e) {}
            return { ok: true, year: year, count: (data.rows || []).length };
          },
          function () {
            lastHydrateOk = false;
            return { ok: false, error: 'http_' + res.status, fallback: true };
          }
        );
      })
      .catch(function () {
        lastHydrateOk = false;
        return { ok: false, error: 'network', fallback: true };
      });
  }

  function rowsFromIsoList(isos) {
    if (!window.KpiYearStore || typeof KpiYearStore.getStore !== 'function') return [];
    var store = KpiYearStore.getStore();
    var salesMap = (store.timeline && store.timeline.dailySales) || {};
    var bizMap = (store.timeline && store.timeline.businessDays) || {};
    var out = [];
    (isos || []).forEach(function (iso) {
      if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return;
      var sales = Number(salesMap[iso]);
      if (!Number.isFinite(sales)) sales = 0;
      var biz = Object.prototype.hasOwnProperty.call(bizMap, iso) ? !!bizMap[iso] : sales > 0;
      out.push({ iso: iso, sales: sales, businessDay: biz });
    });
    return out;
  }

  function rowsForYear(year) {
    var y = Number(year);
    if (!Number.isFinite(y) || !window.KpiYearStore || typeof KpiYearStore.getStore !== 'function') {
      return [];
    }
    var store = KpiYearStore.getStore();
    var salesMap = (store.timeline && store.timeline.dailySales) || {};
    var bizMap = (store.timeline && store.timeline.businessDays) || {};
    var prefix = String(y) + '-';
    var seen = {};
    var isos = [];
    Object.keys(salesMap).forEach(function (iso) {
      if (iso.indexOf(prefix) === 0) seen[iso] = true;
    });
    Object.keys(bizMap).forEach(function (iso) {
      if (iso.indexOf(prefix) === 0) seen[iso] = true;
    });
    Object.keys(seen)
      .sort()
      .forEach(function (iso) {
        isos.push(iso);
      });
    if (!isos.length) {
      for (var m0 = 0; m0 < 12; m0++) {
        var dc = new Date(y, m0 + 1, 0).getDate();
        for (var d = 1; d <= dc; d++) {
          isos.push(y + '-' + pad2(m0 + 1) + '-' + pad2(d));
        }
      }
    }
    return rowsFromIsoList(isos);
  }

  function putRows(rows) {
    if (!readSyncEnabled()) return Promise.resolve({ ok: false, error: 'sync_off' });
    if (!rows || !rows.length) return Promise.resolve({ ok: true, written: 0 });
    var chunks = [];
    for (var i = 0; i < rows.length; i += 366) {
      chunks.push(rows.slice(i, i + 366));
    }
    var p = Promise.resolve({ ok: true, written: 0 });
    chunks.forEach(function (chunk) {
      p = p.then(function (prev) {
        return fetch(inputsUrl(), {
          method: 'PUT',
          headers: buildHeaders(),
          credentials: 'include',
          body: JSON.stringify({ rows: chunk }),
        })
          .then(function (res) {
            return res.json().then(
              function (data) {
                if (!res.ok || !data || !data.ok) {
                  return {
                    ok: false,
                    error: (data && data.error) || 'http_' + res.status,
                    written: (prev && prev.written) || 0,
                  };
                }
                return {
                  ok: true,
                  written: ((prev && prev.written) || 0) + (Number(data.written) || chunk.length),
                };
              },
              function () {
                return { ok: false, error: 'http_' + res.status, written: (prev && prev.written) || 0 };
              }
            );
          })
          .catch(function () {
            return { ok: false, error: 'network', written: (prev && prev.written) || 0 };
          });
      });
    });
    return p;
  }

  function putYear(year) {
    return putRows(rowsForYear(year));
  }

  function schedulePutYear(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) return;
    if (putTimers[y]) window.clearTimeout(putTimers[y]);
    putTimers[y] = window.setTimeout(function () {
      delete putTimers[y];
      putYear(y).catch(function () {});
    }, 200);
  }

  function putYearsMap(yearsMap) {
    var years = Object.keys(yearsMap || {})
      .map(Number)
      .filter(Number.isFinite)
      .sort(function (a, b) {
        return a - b;
      });
    var p = Promise.resolve({ ok: true, written: 0 });
    years.forEach(function (y) {
      p = p.then(function (prev) {
        return putYear(y).then(function (r) {
          return {
            ok: !!(prev && prev.ok && r && r.ok),
            written: ((prev && prev.written) || 0) + ((r && r.written) || 0),
          };
        });
      });
    });
    return p;
  }

  function bootOnce() {
    if (bootStarted) return;
    bootStarted = true;
    hydrateWindow({ force: true });
  }

  document.addEventListener('kpi:storeHydratedFromServer', function () {
    bootOnce();
  });
  window.setTimeout(bootOnce, 2800);

  document.addEventListener('annual:calendarYearChanged', function (ev) {
    var y = ev && ev.detail && ev.detail.year != null ? Number(ev.detail.year) : NaN;
    hydrateWindow({
      force: true,
      year: Number.isFinite(y) ? y : focusYear(),
    });
  });

  window.__KPI_DAILY_INPUTS_SYNC = {
    hydrateWindow: hydrateWindow,
    putYear: putYear,
    putRows: putRows,
    schedulePutYear: schedulePutYear,
    putYearsMap: putYearsMap,
    workWindow: workWindow,
    lastHydrateOk: function () {
      return lastHydrateOk;
    },
  };
})();

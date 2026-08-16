/**
 * KPI Data Gateway — localStorage first, optional server mirror.
 * Docs: docs/backend-phase-a-store-api.md · docs/codex-cursor-backend-handoff.md
 *
 * Enable sync (any one):
 * - localStorage kpiNavigator.storeSync =
 *     {"enabled":true,"authMode":"session","baseUrl":"/api/v1/store.php"}
 *   or legacy token:
 *     {"enabled":true,"token":"dev-change-me","baseUrl":"/api/v1/store.php"}
 * - URL ?kpiSync=1 (session if no token; token via kpiSyncToken)
 * - window.__KPI_STORE_SYNC = { enabled:true, authMode:'session', baseUrl:'...' }
 *
 * Default: sync OFF (existing local-only behavior).
 *
 * B3-T2: also mirrors PL keys (catalog / expenses / adjustments / rate) as `pl`
 * on the same store.php blob. Raw localStorage writes to those keys trigger PUT.
 */
(function () {
  'use strict';

  if (window.__KPI_DATA_GATEWAY && window.__KPI_DATA_GATEWAY.__kpiStoreSyncReady) {
    return;
  }

  var STORE_KEY = 'kpiNavigator.kpiYearStore';
  var NAV_KEY = 'kpiNavigator.annualNav';
  var SYNC_KEY = 'kpiNavigator.storeSync';
  var TIER_KEY = 'kpiNavigator.subscriptionTier';
  var PL_CATALOG_KEY = 'kpiNavigator.plLineCatalog';
  var PL_EXP_PREFIX = 'kpi-pl-expenses-v1:';
  var PL_ADJ_PREFIX = 'kpi-pl-expense-adjustments-v1:';
  var PL_RATE_KEY = 'kpiNavigator.plTargetCostRate';

  var putTimer = null;
  var hydrated = false;
  var hookQuiet = false;
  var origSetItem = Storage.prototype.setItem;
  var origRemoveItem = Storage.prototype.removeItem;
  var origGetItem = Storage.prototype.getItem;

  function applyPlanFromPayload(data) {
    if (!data || !data.plan) return;
    var p = String(data.plan).toLowerCase() === 'basic' ? 'basic' : 'pro';
    try {
      if (window.__KPI_AUTH && typeof window.__KPI_AUTH.applyServerPlan === 'function') {
        window.__KPI_AUTH.applyServerPlan(p);
        return;
      }
    } catch (_e0) {}
    try {
      origSetItem.call(localStorage, TIER_KEY, p);
    } catch (_e1) {}
    try {
      sessionStorage.setItem(TIER_KEY, p);
    } catch (_e2) {}
    try {
      window.dispatchEvent(new CustomEvent('kpi:planChanged', { detail: { plan: p, source: 'server' } }));
    } catch (_e3) {}
  }

  function localTier() {
    try {
      var t = origGetItem.call(sessionStorage, TIER_KEY) || origGetItem.call(localStorage, TIER_KEY);
      return String(t || '').toLowerCase() === 'basic' ? 'basic' : 'pro';
    } catch (_e) {
      return 'pro';
    }
  }

  function isPlSyncKey(key) {
    if (!key) return false;
    if (key === PL_CATALOG_KEY || key === PL_RATE_KEY) return true;
    if (String(key).indexOf(PL_EXP_PREFIX) === 0) return true;
    if (String(key).indexOf(PL_ADJ_PREFIX) === 0) return true;
    return false;
  }

  function stripProFromStore(store) {
    if (!store || typeof store !== 'object') return store;
    var out;
    try {
      out = JSON.parse(JSON.stringify(store));
    } catch (_e) {
      return store;
    }
    var years = out.years;
    if (!years || typeof years !== 'object') return out;
    Object.keys(years).forEach(function (yk) {
      if (years[yk] && typeof years[yk] === 'object' && years[yk].dailyExpenses != null) {
        delete years[yk].dailyExpenses;
      }
    });
    return out;
  }

  /* 段階 2d: blob に解を戻さない。メモリと kpi_daily_facts が正本 */
  function yearRecordHasDailyFacts(rec) {
    return !!(
      rec &&
      typeof rec === 'object' &&
      (rec.dailyFacts || rec.dailyFactsUpdatedAt || rec.dailyFactsFromIso || rec.dailyFactsReason)
    );
  }

  function storeHasDailyFacts(store) {
    var years = store && store.years;
    if (!years || typeof years !== 'object') return false;
    var keys = Object.keys(years);
    for (var i = 0; i < keys.length; i++) {
      if (yearRecordHasDailyFacts(years[keys[i]])) return true;
    }
    return false;
  }

  function stripDailyFactsFromStore(store) {
    if (!store || typeof store !== 'object') return store;
    var years = store.years;
    if (!years || typeof years !== 'object') return store;
    var slimYears = {};
    Object.keys(years).forEach(function (yk) {
      var rec = years[yk];
      if (!rec || typeof rec !== 'object') {
        slimYears[yk] = rec;
        return;
      }
      var copy = {};
      Object.keys(rec).forEach(function (rk) {
        if (
          rk === 'dailyFacts' ||
          rk === 'dailyFactsUpdatedAt' ||
          rk === 'dailyFactsFromIso' ||
          rk === 'dailyFactsReason'
        ) {
          return;
        }
        copy[rk] = rec[rk];
      });
      slimYears[yk] = copy;
    });
    var out = {};
    Object.keys(store).forEach(function (k) {
      if (k === 'years') return;
      out[k] = store[k];
    });
    out.years = slimYears;
    return out;
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

  function defaultStoreUrl() {
    return resolveAppRoot() + '/api/v1/store.php';
  }

  function readSyncConfig() {
    var cfg = {
      enabled: false,
      authMode: 'session',
      token: '',
      baseUrl: defaultStoreUrl(),
    };
    try {
      if (window.__KPI_STORE_SYNC && typeof window.__KPI_STORE_SYNC === 'object') {
        if (window.__KPI_STORE_SYNC.enabled != null) cfg.enabled = !!window.__KPI_STORE_SYNC.enabled;
        if (window.__KPI_STORE_SYNC.authMode) cfg.authMode = String(window.__KPI_STORE_SYNC.authMode);
        if (window.__KPI_STORE_SYNC.token) cfg.token = String(window.__KPI_STORE_SYNC.token);
        if (window.__KPI_STORE_SYNC.baseUrl) cfg.baseUrl = String(window.__KPI_STORE_SYNC.baseUrl);
      }
    } catch (_e0) {}
    try {
      var raw = origGetItem.call(localStorage, SYNC_KEY);
      if (raw) {
        var o = JSON.parse(raw);
        if (o && typeof o === 'object') {
          if (o.enabled != null) cfg.enabled = !!o.enabled;
          if (o.authMode) cfg.authMode = String(o.authMode);
          if (o.token) cfg.token = String(o.token);
          if (o.baseUrl) cfg.baseUrl = String(o.baseUrl);
        }
      }
    } catch (_e1) {}
    try {
      var params = new URLSearchParams(window.location.search || '');
      if (params.get('kpiSync') === '1') cfg.enabled = true;
      if (params.get('kpiSyncToken')) cfg.token = String(params.get('kpiSyncToken'));
      if (params.get('kpiSyncUrl')) cfg.baseUrl = String(params.get('kpiSyncUrl'));
      if (params.get('kpiSyncAuth')) cfg.authMode = String(params.get('kpiSyncAuth'));
    } catch (_e2) {}
    try {
      var metaTok = document.querySelector('meta[name="kpi-store-token"]');
      if (metaTok && metaTok.content && !cfg.token) cfg.token = String(metaTok.content);
      var metaUrl = document.querySelector('meta[name="kpi-store-api"]');
      if (metaUrl && metaUrl.content) cfg.baseUrl = String(metaUrl.content);
    } catch (_e3) {}

    var authModeExplicit = false;
    try {
      if (window.__KPI_STORE_SYNC && window.__KPI_STORE_SYNC.authMode) authModeExplicit = true;
    } catch (_eA) {}
    try {
      var rawMode = origGetItem.call(localStorage, SYNC_KEY);
      var oMode = rawMode ? JSON.parse(rawMode) : null;
      if (oMode && oMode.authMode) authModeExplicit = true;
    } catch (_eB) {}
    try {
      var paramsMode = new URLSearchParams(window.location.search || '');
      if (paramsMode.get('kpiSyncAuth')) authModeExplicit = true;
    } catch (_eC) {}
    if (!authModeExplicit) {
      cfg.authMode = cfg.token ? 'token' : 'session';
    }

    if (!cfg.baseUrl || cfg.baseUrl === '/api/v1/store.php') {
      cfg.baseUrl = defaultStoreUrl();
    }
    return cfg;
  }

  function canSync(cfg) {
    if (!cfg || !cfg.enabled) return false;
    if (cfg.authMode === 'token') return !!cfg.token;
    if (cfg.authMode === 'dual') return true;
    return true;
  }

  function buildHeaders(cfg, withJson) {
    var headers = {};
    if (withJson) headers['Content-Type'] = 'application/json';
    if (cfg.token && (cfg.authMode === 'token' || cfg.authMode === 'dual')) {
      headers['X-KPI-Store-Token'] = cfg.token;
    }
    return headers;
  }

  function fetchCreds(cfg) {
    return cfg.authMode === 'token' ? 'omit' : 'include';
  }

  function localGet(key) {
    try {
      var raw = origGetItem.call(localStorage, key);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object' ? parsed : null;
    } catch (_e) {
      return null;
    }
  }

  function localSetRaw(key, stringValue) {
    hookQuiet = true;
    try {
      origSetItem.call(localStorage, key, stringValue);
      return true;
    } catch (_e) {
      return false;
    } finally {
      hookQuiet = false;
    }
  }

  function localRemoveRaw(key) {
    hookQuiet = true;
    try {
      origRemoveItem.call(localStorage, key);
      return true;
    } catch (_e) {
      return false;
    } finally {
      hookQuiet = false;
    }
  }

  function localSet(key, value) {
    try {
      return localSetRaw(key, JSON.stringify(value));
    } catch (_e) {
      return false;
    }
  }

  function collectPlFromLocal() {
    var pl = {
      catalog: localGet(PL_CATALOG_KEY) || {},
      expensesByYear: {},
      adjustmentsByYear: {},
      targetCostRate: null,
    };
    try {
      var rateRaw = origGetItem.call(localStorage, PL_RATE_KEY);
      if (rateRaw != null && rateRaw !== '') {
        var n = Number(rateRaw);
        if (isFinite(n)) pl.targetCostRate = n;
      }
    } catch (_eRate) {}
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (!k) continue;
        if (k.indexOf(PL_EXP_PREFIX) === 0) {
          var yExp = k.slice(PL_EXP_PREFIX.length);
          pl.expensesByYear[yExp] = localGet(k) || {};
        } else if (k.indexOf(PL_ADJ_PREFIX) === 0) {
          var yAdj = k.slice(PL_ADJ_PREFIX.length);
          pl.adjustmentsByYear[yAdj] = localGet(k) || {};
        }
      }
    } catch (_eScan) {}
    return pl;
  }

  function plHasLocalPayload(pl) {
    if (!pl || typeof pl !== 'object') return false;
    if (pl.catalog && typeof pl.catalog === 'object' && Object.keys(pl.catalog).length) return true;
    var ey = pl.expensesByYear || {};
    var ay = pl.adjustmentsByYear || {};
    var yk;
    for (yk in ey) {
      if (ey[yk] && typeof ey[yk] === 'object' && Object.keys(ey[yk]).length) return true;
    }
    for (yk in ay) {
      if (ay[yk] && typeof ay[yk] === 'object' && Object.keys(ay[yk]).length) return true;
    }
    if (pl.targetCostRate != null && isFinite(Number(pl.targetCostRate))) return true;
    return false;
  }

  function applyPlToLocal(pl) {
    if (!pl || typeof pl !== 'object') return false;
    var changed = false;
    if (pl.catalog && typeof pl.catalog === 'object') {
      localSet(PL_CATALOG_KEY, pl.catalog);
      changed = true;
    }
    if (pl.expensesByYear && typeof pl.expensesByYear === 'object') {
      Object.keys(pl.expensesByYear).forEach(function (y) {
        localSet(PL_EXP_PREFIX + y, pl.expensesByYear[y] || {});
        changed = true;
      });
    }
    if (pl.adjustmentsByYear && typeof pl.adjustmentsByYear === 'object') {
      Object.keys(pl.adjustmentsByYear).forEach(function (y) {
        localSet(PL_ADJ_PREFIX + y, pl.adjustmentsByYear[y] || {});
        changed = true;
      });
    }
    if (pl.targetCostRate != null && isFinite(Number(pl.targetCostRate))) {
      localSetRaw(PL_RATE_KEY, String(Number(pl.targetCostRate)));
      changed = true;
    }
    return changed;
  }

  function clearLocalPlKeys() {
    var toRemove = [];
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (isPlSyncKey(k)) toRemove.push(k);
      }
    } catch (_e) {}
    toRemove.forEach(function (k) {
      localRemoveRaw(k);
    });
  }

  function schedulePut(cfg) {
    if (!canSync(cfg)) return;
    if (putTimer != null) window.clearTimeout(putTimer);
    putTimer = window.setTimeout(function () {
      putTimer = null;
      var storePayload = stripDailyFactsFromStore(localGet(STORE_KEY));
      var body = {
        store: storePayload,
        annualNav: localGet(NAV_KEY),
      };
      if (localTier() === 'basic') {
        body.store = stripProFromStore(storePayload);
        // Do not send pl for Basic (avoids 403; server keeps disk pl).
      } else {
        body.pl = collectPlFromLocal();
      }
      fetch(cfg.baseUrl, {
        method: 'PUT',
        headers: buildHeaders(cfg, true),
        body: JSON.stringify(body),
        credentials: fetchCreds(cfg),
      }).catch(function () {});
    }, 400);
  }

  function hydrateFromServer(cfg) {
    if (!canSync(cfg) || hydrated) return;
    hydrated = true;
    fetch(cfg.baseUrl, {
      method: 'GET',
      headers: buildHeaders(cfg, false),
      credentials: fetchCreds(cfg),
    })
      .then(function (res) {
        if (!res.ok) return null;
        return res.json();
      })
      .then(function (data) {
        if (!data || !data.ok) return;
        applyPlanFromPayload(data);
        var changed = false;
        var storeHadFacts = false;
        if (data.store && typeof data.store === 'object') {
          storeHadFacts = storeHasDailyFacts(data.store);
          localSet(STORE_KEY, stripDailyFactsFromStore(data.store));
          changed = true;
        }
        if (data.annualNav && typeof data.annualNav === 'object') {
          localSet(NAV_KEY, data.annualNav);
          changed = true;
        }
        if (data.plan === 'basic') {
          // Server omits pl; drop any leftover local Pro PL keys so UI cannot leak.
          clearLocalPlKeys();
          changed = true;
        } else if (data.pl && typeof data.pl === 'object') {
          if (applyPlToLocal(data.pl)) changed = true;
        }
        if (storeHadFacts) schedulePut(cfg);
        if (changed) {
          try {
            document.dispatchEvent(
              new CustomEvent('kpi:storeHydratedFromServer', {
                detail: {
                  updatedAt: data.updatedAt || null,
                  plan: data.plan || null,
                  hasPl: !!(data.pl && plHasLocalPayload(data.pl)),
                },
              })
            );
          } catch (_e) {}
          try {
            if (window.KpiYearStore && typeof window.KpiYearStore.reload === 'function') {
              window.KpiYearStore.reload();
            }
          } catch (_eReload) {}
          try {
            document.dispatchEvent(new CustomEvent('kpi:readSurfacesRefresh'));
          } catch (_e3) {}
          try {
            console.info('[KPI Store Sync] hydrated from server', data.updatedAt || '', data.plan || '');
          } catch (_eLog) {}
        }
      })
      .catch(function () {});
  }

  function installLocalStorageHooks() {
    Storage.prototype.setItem = function (key, value) {
      origSetItem.apply(this, arguments);
      if (hookQuiet || this !== localStorage) return;
      if (!canSync(cfg)) return;
      if (key === STORE_KEY || key === NAV_KEY || isPlSyncKey(key)) {
        schedulePut(cfg);
      }
    };
    Storage.prototype.removeItem = function (key) {
      origRemoveItem.apply(this, arguments);
      if (hookQuiet || this !== localStorage) return;
      if (!canSync(cfg)) return;
      if (key === STORE_KEY || key === NAV_KEY || isPlSyncKey(key)) {
        schedulePut(cfg);
      }
    };
  }

  var cfg = readSyncConfig();
  installLocalStorageHooks();

  window.__KPI_DATA_GATEWAY = {
    __kpiStoreSyncReady: true,
    getJson: function (key) {
      return localGet(key);
    },
    setJson: function (key, value) {
      var ok = localSet(key, value);
      if (ok && (key === STORE_KEY || key === NAV_KEY || isPlSyncKey(key))) {
        schedulePut(cfg);
      }
      return ok;
    },
    syncConfig: function () {
      return {
        enabled: !!cfg.enabled,
        authMode: cfg.authMode || 'session',
        baseUrl: cfg.baseUrl,
        hasToken: !!cfg.token,
      };
    },
    enableSessionSync: function (baseUrl) {
      var next = {
        enabled: true,
        authMode: 'session',
        baseUrl: baseUrl || defaultStoreUrl(),
      };
      try {
        localSetRaw(SYNC_KEY, JSON.stringify(next));
      } catch (_e) {}
      cfg = readSyncConfig();
      hydrated = false;
      hydrateFromServer(cfg);
      return next;
    },
    pullFromServer: function () {
      hydrated = false;
      cfg = readSyncConfig();
      hydrateFromServer(cfg);
    },
    pushToServerNow: function () {
      cfg = readSyncConfig();
      if (putTimer != null) {
        window.clearTimeout(putTimer);
        putTimer = null;
      }
      schedulePut(cfg);
    },
    collectPlFromLocal: collectPlFromLocal,
  };

  if (canSync(cfg)) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        hydrateFromServer(cfg);
      });
    } else {
      hydrateFromServer(cfg);
    }
  }
})();

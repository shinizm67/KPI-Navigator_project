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
  var putTimer = null;
  var hydrated = false;

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
      localStorage.setItem(TIER_KEY, p);
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
      var t = sessionStorage.getItem(TIER_KEY) || localStorage.getItem(TIER_KEY);
      return String(t || '').toLowerCase() === 'basic' ? 'basic' : 'pro';
    } catch (_e) {
      return 'pro';
    }
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
      var raw = localStorage.getItem(SYNC_KEY);
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

    // Default authMode: explicit > token-only legacy > session
    var authModeExplicit = false;
    try {
      if (window.__KPI_STORE_SYNC && window.__KPI_STORE_SYNC.authMode) authModeExplicit = true;
    } catch (_eA) {}
    try {
      var rawMode = localStorage.getItem(SYNC_KEY);
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
    if (cfg.authMode === 'dual') return true; // session cookie and/or token
    // session (default)
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
    // Session / dual need cookies. Token-only can omit, but include is fine same-origin.
    return cfg.authMode === 'token' ? 'omit' : 'include';
  }

  function localGet(key) {
    try {
      var raw = localStorage.getItem(key);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object' ? parsed : null;
    } catch (_e) {
      return null;
    }
  }

  function localSet(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (_e) {
      return false;
    }
  }

  function schedulePut(cfg) {
    if (!canSync(cfg)) return;
    if (putTimer != null) window.clearTimeout(putTimer);
    putTimer = window.setTimeout(function () {
      putTimer = null;
      var storePayload = localGet(STORE_KEY);
      if (localTier() === 'basic') {
        storePayload = stripProFromStore(storePayload);
      }
      var body = {
        store: storePayload,
        annualNav: localGet(NAV_KEY),
      };
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
        if (data.store && typeof data.store === 'object') {
          localSet(STORE_KEY, data.store);
          changed = true;
        }
        if (data.annualNav && typeof data.annualNav === 'object') {
          localSet(NAV_KEY, data.annualNav);
          changed = true;
        }
        if (changed) {
          try {
            document.dispatchEvent(
              new CustomEvent('kpi:storeHydratedFromServer', {
                detail: { updatedAt: data.updatedAt || null, plan: data.plan || null },
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

  var cfg = readSyncConfig();

  window.__KPI_DATA_GATEWAY = {
    __kpiStoreSyncReady: true,
    getJson: function (key) {
      return localGet(key);
    },
    setJson: function (key, value) {
      var ok = localSet(key, value);
      if (ok && (key === STORE_KEY || key === NAV_KEY)) {
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
        localStorage.setItem(SYNC_KEY, JSON.stringify(next));
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

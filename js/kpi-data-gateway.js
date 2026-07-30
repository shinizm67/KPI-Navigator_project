/**
 * KPI Data Gateway — localStorage first, optional Phase A server mirror.
 * Docs: docs/backend-phase-a-store-api.md
 *
 * Enable sync (any one):
 * - localStorage key kpiNavigator.storeSync = {"enabled":true,"token":"dev-change-me","baseUrl":"/api/v1/store.php"}
 * - URL ?kpiSync=1 (uses token from storeSync or meta[name=kpi-store-token])
 * - window.__KPI_STORE_SYNC = { enabled:true, token:'...', baseUrl:'/api/v1/store.php' }
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
  var putTimer = null;
  var hydrated = false;

  function readSyncConfig() {
    var cfg = { enabled: false, token: '', baseUrl: '/api/v1/store.php' };
    try {
      if (window.__KPI_STORE_SYNC && typeof window.__KPI_STORE_SYNC === 'object') {
        cfg.enabled = !!window.__KPI_STORE_SYNC.enabled;
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
    } catch (_e2) {}
    try {
      var metaTok = document.querySelector('meta[name="kpi-store-token"]');
      if (metaTok && metaTok.content && !cfg.token) cfg.token = String(metaTok.content);
      var metaUrl = document.querySelector('meta[name="kpi-store-api"]');
      if (metaUrl && metaUrl.content) cfg.baseUrl = String(metaUrl.content);
    } catch (_e3) {}
    return cfg;
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
    if (!cfg.enabled || !cfg.token) return;
    if (putTimer != null) window.clearTimeout(putTimer);
    putTimer = window.setTimeout(function () {
      putTimer = null;
      var body = {
        store: localGet(STORE_KEY),
        annualNav: localGet(NAV_KEY),
      };
      fetch(cfg.baseUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-KPI-Store-Token': cfg.token,
        },
        body: JSON.stringify(body),
        credentials: 'omit',
      }).catch(function () {});
    }, 400);
  }

  function hydrateFromServer(cfg) {
    if (!cfg.enabled || !cfg.token || hydrated) return;
    hydrated = true;
    fetch(cfg.baseUrl, {
      method: 'GET',
      headers: { 'X-KPI-Store-Token': cfg.token },
      credentials: 'omit',
    })
      .then(function (res) {
        if (!res.ok) return null;
        return res.json();
      })
      .then(function (data) {
        if (!data || !data.ok) return;
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
                detail: { updatedAt: data.updatedAt || null },
              })
            );
          } catch (_e) {}
          // Year store は起動時に一度だけ読むため、取り込み後に再読込する
          try {
            if (window.KpiYearStore && typeof window.KpiYearStore.reload === 'function') {
              window.KpiYearStore.reload();
            }
          } catch (_eReload) {}
          try {
            document.dispatchEvent(new CustomEvent('kpi:readSurfacesRefresh'));
          } catch (_e3) {}
          try {
            console.info('[KPI Store Sync] hydrated from server', data.updatedAt || '');
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
        baseUrl: cfg.baseUrl,
        hasToken: !!cfg.token,
      };
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

  if (cfg.enabled) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        hydrateFromServer(cfg);
      });
    } else {
      hydrateFromServer(cfg);
    }
  }
})();

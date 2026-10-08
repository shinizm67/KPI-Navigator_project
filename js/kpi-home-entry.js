/* Home stays visible. Readiness is not a navigation gate.
   A fresh authenticated browser starts the same session store sync Annual uses.
   The shell repaints when that hydrate settles. Opening date stays in store.meta. */
(function () {
  'use strict';

  var windows = document.querySelector('.home-windows');
  if (windows) windows.hidden = false;

  function storeApiUrl() {
    var root = '';
    try {
      if (window.__KPI_AUTH && typeof window.__KPI_AUTH.resolveAppRoot === 'function') {
        root = String(window.__KPI_AUTH.resolveAppRoot() || '');
      }
    } catch (_e) {}
    if (!root) {
      try {
        var path = String(window.location && window.location.pathname || '');
        var matched = path.match(/^(.*?\/kpi-navigator)(?:\/|$)/);
        if (matched) root = matched[1];
      } catch (_e2) {}
    }
    return (root || '') + '/api/v1/store.php';
  }

  function markStoreScopeReady() {
    try {
      if (!window.KpiYearStore || typeof window.KpiYearStore !== 'object') {
        window.KpiYearStore = {};
      }
      window.KpiYearStore.__userScopeReady = true;
    } catch (_e) {}
    try {
      window.dispatchEvent(new CustomEvent('kpi:yearStoreUserScopeReady'));
    } catch (_e2) {}
  }

  function sessionOk(r) {
    return !!(r && r.status === 200 && r.data && r.data.ok === true);
  }

  function startStoreSync() {
    var gw = window.__KPI_DATA_GATEWAY;
    if (!gw || typeof gw.enableSessionSync !== 'function') return;
    var auth = window.__KPI_AUTH;
    if (!auth || typeof auth.syncPlanFromServer !== 'function') return;
    auth.syncPlanFromServer().then(function (r) {
      if (!sessionOk(r)) return;
      markStoreScopeReady();
      try {
        gw.enableSessionSync(storeApiUrl());
      } catch (_eEnable) {}
      markStoreScopeReady();
    }).catch(function () {});
  }

  startStoreSync();
})();

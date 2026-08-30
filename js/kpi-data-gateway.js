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
  /** Block PUT until KpiYearStore finishes post-bind init (KPI-LS-USER-SCOPE-7-B). */
  var userScopePutHold = false;
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

  function dailyExpensesHasData(de) {
    if (!de || typeof de !== 'object') return false;
    var lineIds = Object.keys(de);
    for (var i = 0; i < lineIds.length; i++) {
      var byIso = de[lineIds[i]];
      if (byIso && typeof byIso === 'object' && Object.keys(byIso).length) return true;
    }
    return false;
  }

  function dailyIncomeHasData(di) {
    if (!di || typeof di !== 'object') return false;
    var streamIds = Object.keys(di);
    for (var i = 0; i < streamIds.length; i++) {
      var byIso = di[streamIds[i]];
      if (byIso && typeof byIso === 'object' && Object.keys(byIso).length) return true;
    }
    return false;
  }

  function timelineMapHasYearData(map, year) {
    if (!map || typeof map !== 'object') return false;
    var yStr = String(year);
    return Object.keys(map).some(function (iso) {
      if (!iso || iso.slice(0, 4) !== yStr) return false;
      return Number.isFinite(Number(map[iso]));
    });
  }

  function mergeIsoTimelineMap(serverMap, localMap) {
    var out = {};
    if (serverMap && typeof serverMap === 'object') {
      Object.keys(serverMap).forEach(function (iso) {
        out[iso] = serverMap[iso];
      });
    }
    if (!localMap || typeof localMap !== 'object') return out;
    Object.keys(localMap).forEach(function (iso) {
      var lv = Number(localMap[iso]);
      if (!Number.isFinite(lv)) return;
      var hasServer = Object.prototype.hasOwnProperty.call(out, iso);
      var sv = hasServer ? Number(out[iso]) : NaN;
      if (!hasServer || (!Number.isFinite(sv) && lv !== 0) || (lv !== 0 && sv === 0)) {
        out[iso] = localMap[iso];
      }
    });
    return out;
  }

  /** Keep local MEP data when server hydrate would wipe unsynced MEP/PL imports. */
  function mergeStorePreservingLocalMepData(serverStore, localStore) {
    if (!serverStore || typeof serverStore !== 'object') return localStore || serverStore;
    if (!localStore || typeof localStore !== 'object') return serverStore;
    var out;
    try {
      out = JSON.parse(JSON.stringify(serverStore));
    } catch (_e) {
      return serverStore;
    }
    var localYears = localStore.years || {};
    if (!out.years || typeof out.years !== 'object') out.years = {};
    Object.keys(localYears).forEach(function (yk) {
      var localRec = localYears[yk];
      if (!localRec || typeof localRec !== 'object') return;
      var outRec = out.years[yk];
      if (!outRec || typeof outRec !== 'object') {
        out.years[yk] = JSON.parse(JSON.stringify(localRec));
        outRec = out.years[yk];
      }
      var localTs = Number(localRec.mepUpdatedAt) || 0;
      var serverTs = Number(outRec.mepUpdatedAt) || 0;
      var localDe = localRec.dailyExpenses;
      if (dailyExpensesHasData(localDe)) {
        var serverDe = outRec.dailyExpenses;
        if (!dailyExpensesHasData(serverDe) || localTs >= serverTs) {
          outRec.dailyExpenses = JSON.parse(JSON.stringify(localDe));
          if (localTs > serverTs && localRec.mepUpdatedAt != null) {
            outRec.mepUpdatedAt = localRec.mepUpdatedAt;
          }
        }
      }
      var localDi = localRec.dailyIncome;
      if (dailyIncomeHasData(localDi)) {
        var serverDi = outRec.dailyIncome;
        if (!dailyIncomeHasData(serverDi) || localTs >= serverTs) {
          outRec.dailyIncome = JSON.parse(JSON.stringify(localDi));
          if (localTs > serverTs && localRec.mepUpdatedAt != null) {
            outRec.mepUpdatedAt = localRec.mepUpdatedAt;
          }
        }
      }
    });
    if (localStore.timeline && typeof localStore.timeline === 'object') {
      if (!out.timeline || typeof out.timeline !== 'object') {
        out.timeline = { dailySales: {}, businessDays: {} };
      }
      out.timeline.dailySales = mergeIsoTimelineMap(
        out.timeline.dailySales,
        localStore.timeline.dailySales
      );
      out.timeline.businessDays = mergeIsoTimelineMap(
        out.timeline.businessDays,
        localStore.timeline.businessDays
      );
    }
    return out;
  }

  function mergeStorePreservingLocalExpenses(serverStore, localStore) {
    return mergeStorePreservingLocalMepData(serverStore, localStore);
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

  /* KPI-TIMELINE-SLIM-AR: LS には作業窓だけ残し、PUT はメモリのフル timeline を優先 */
  var TIMELINE_SLIM_PAD_MONTHS = 2;

  function collectTimelineKeepYears(store, sales, biz) {
    var years = {};
    Object.keys((store && store.years) || {}).forEach(function (yk) {
      var yn = Number(yk);
      if (Number.isFinite(yn)) years[yn] = true;
    });
    function markFromMap(map) {
      if (!map || typeof map !== 'object') return;
      Object.keys(map).forEach(function (iso) {
        if (!iso || iso.length < 4) return;
        var yn = Number(iso.slice(0, 4));
        if (Number.isFinite(yn)) years[yn] = true;
      });
    }
    markFromMap(sales);
    markFromMap(biz);
    return years;
  }

  function slimTimelineForLocalStorage(store) {
    if (!store || typeof store !== 'object') return store;
    var tl = store.timeline;
    if (!tl || typeof tl !== 'object') return store;
    var sales = tl.dailySales;
    var biz = tl.businessDays;
    if ((!sales || typeof sales !== 'object') && (!biz || typeof biz !== 'object')) {
      return store;
    }
    var keepYears = collectTimelineKeepYears(store, sales, biz);
    var focusY = null;
    try {
      if (window.KpiYearStore && typeof KpiYearStore.getOperatingYear === 'function') {
        focusY = Number(KpiYearStore.getOperatingYear());
      }
    } catch (_e0) {}
    if (!Number.isFinite(focusY)) {
      try {
        var nav = localGet(NAV_KEY);
        if (nav && nav.calendarYear != null) focusY = Number(nav.calendarYear);
      } catch (_e1) {}
    }
    if (!Number.isFinite(focusY)) focusY = new Date().getFullYear();
    var start = new Date(focusY, -TIMELINE_SLIM_PAD_MONTHS, 1);
    var end = new Date(focusY, 12 + TIMELINE_SLIM_PAD_MONTHS, 0);
    function inWindow(iso) {
      if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return false;
      var y = Number(iso.slice(0, 4));
      if (keepYears[y]) return true;
      var p = iso.split('-').map(Number);
      var d = new Date(p[0], p[1] - 1, p[2]);
      return d >= start && d <= end;
    }
    var slimSales = {};
    var slimBiz = {};
    if (sales && typeof sales === 'object') {
      Object.keys(sales).forEach(function (iso) {
        if (inWindow(iso)) slimSales[iso] = sales[iso];
      });
    }
    if (biz && typeof biz === 'object') {
      Object.keys(biz).forEach(function (iso) {
        if (inWindow(iso)) slimBiz[iso] = biz[iso];
      });
    }
    var out = {};
    Object.keys(store).forEach(function (k) {
      if (k === 'timeline') return;
      out[k] = store[k];
    });
    out.timeline = {
      dailySales: slimSales,
      businessDays: slimBiz,
    };
    return out;
  }

  function storePayloadForPut() {
    if (userScopePutHold || hookQuiet) return null;
    var fromMem = null;
    try {
      if (window.KpiYearStore && typeof KpiYearStore.getStore === 'function') {
        fromMem = window.KpiYearStore.getStore();
      }
    } catch (_e) {}
    if (fromMem && typeof fromMem === 'object') {
      return stripDailyFactsFromStore(fromMem);
    }
    return stripDailyFactsFromStore(localGet(STORE_KEY));
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

  var putInFlight = null;

  function buildPutBody(cfg) {
    var storePayload = storePayloadForPut();
    var body = {
      store: storePayload,
      annualNav: localGet(NAV_KEY),
    };
    if (localTier() === 'basic') {
      body.store = stripProFromStore(storePayload);
    } else {
      body.pl = collectPlFromLocal();
    }
    return body;
  }

  function doPut(cfg) {
    if (!canSync(cfg) || userScopePutHold || hookQuiet) return Promise.resolve();
    var body = buildPutBody(cfg);
    if (!body.store || typeof body.store !== 'object') return Promise.resolve();
    putInFlight = fetch(cfg.baseUrl, {
      method: 'PUT',
      headers: buildHeaders(cfg, true),
      body: JSON.stringify(body),
      credentials: fetchCreds(cfg),
    })
      .catch(function () {})
      .then(function () {
        putInFlight = null;
      });
    return putInFlight;
  }

  function schedulePut(cfg) {
    if (!canSync(cfg) || userScopePutHold || hookQuiet) return;
    if (putTimer != null) window.clearTimeout(putTimer);
    putTimer = window.setTimeout(function () {
      putTimer = null;
      doPut(cfg);
    }, 400);
  }

  function flushPut() {
    cfg = readSyncConfig();
    if (putTimer != null) {
      window.clearTimeout(putTimer);
      putTimer = null;
    }
    /* KPI-BUSY-CSV-CLOSE-DA: never let store PUT hang the Busy overlay forever */
    function withPutTimeout(p) {
      return Promise.race([
        Promise.resolve(p).catch(function () {}),
        new Promise(function (resolve) {
          window.setTimeout(function () { resolve(null); }, 15000);
        }),
      ]);
    }
    if (!canSync(cfg)) {
      return withPutTimeout(putInFlight || Promise.resolve());
    }
    if (putInFlight) {
      return withPutTimeout(
        putInFlight.then(function () {
          return doPut(cfg);
        })
      );
    }
    return withPutTimeout(doPut(cfg));
  }

  /**
   * Wait for KpiYearStore post-bind init on app pages; no-op elsewhere.
   */
  function waitForYearStoreUserScopeReady() {
    return new Promise(function (resolve) {
      try {
        if (window.KpiYearStore && window.KpiYearStore.__userScopeReady) {
          resolve();
          return;
        }
      } catch (_eReady) {}
      var done = false;
      function finish() {
        if (done) return;
        done = true;
        try {
          window.removeEventListener('kpi:yearStoreUserScopeReady', onReady);
        } catch (_eRm) {}
        resolve();
      }
      function onReady() {
        finish();
      }
      try {
        window.addEventListener('kpi:yearStoreUserScopeReady', onReady);
      } catch (_eAdd) {
        finish();
        return;
      }
      window.setTimeout(finish, 8000);
    });
  }

  function onLocalUserScopeChanged() {
    if (putTimer != null) {
      window.clearTimeout(putTimer);
      putTimer = null;
    }
    userScopePutHold = true;
    hydrated = false;
  }

  function onYearStoreUserScopeReady() {
    userScopePutHold = false;
  }

  try {
    window.addEventListener('kpi:localUserScopeChanged', onLocalUserScopeChanged);
    window.addEventListener('kpi:yearStoreUserScopeReady', onYearStoreUserScopeReady);
  } catch (_eEv) {}

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
        /* Bind / clear LS for this session user before merge or PUT (KPI-LS-USER-SCOPE-7). */
        var userScopeSwitched = false;
        try {
          if (
            data.userId &&
            window.__KPI_AUTH &&
            typeof window.__KPI_AUTH.bindLocalUserId === 'function'
          ) {
            var scopeBind = window.__KPI_AUTH.bindLocalUserId(data.userId);
            userScopeSwitched = !!(scopeBind && scopeBind.switched);
          }
        } catch (_eBind) {}
        if (userScopeSwitched) {
          try {
            if (window.KpiYearStore && typeof window.KpiYearStore.resetForUserScope === 'function') {
              window.KpiYearStore.resetForUserScope();
            }
          } catch (_eScopeReset) {}
        }
        applyPlanFromPayload(data);
        var changed = false;
        var storeHadFacts = false;
        if (data.store && typeof data.store === 'object') {
          storeHadFacts = storeHasDailyFacts(data.store);
          var localBeforeHydrate = userScopeSwitched ? null : localGet(STORE_KEY);
          var fullStore = stripDailyFactsFromStore(
            mergeStorePreservingLocalMepData(data.store, localBeforeHydrate)
          );
          /* Load full into LS briefly so KpiYearStore.reload sees full timeline, then slim LS. */
          localSet(STORE_KEY, fullStore);
          changed = true;
          try {
            if (window.KpiYearStore && typeof window.KpiYearStore.reload === 'function') {
              window.KpiYearStore.reload();
            }
          } catch (_eReloadEarly) {}
          hookQuiet = true;
          try {
            localSet(STORE_KEY, slimTimelineForLocalStorage(fullStore));
          } finally {
            hookQuiet = false;
          }
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
            /* reload already ran above when store present */
            if (!(data.store && typeof data.store === 'object')) {
              if (window.KpiYearStore && typeof window.KpiYearStore.reload === 'function') {
                window.KpiYearStore.reload();
              }
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

  /**
   * Wait for auth client when present so bindLocalUserId runs before first merge.
   * Login already binds; this covers Annual script order (gateway before auth).
   */
  function hydrateAfterAuthBind(cfg) {
    var tries = 0;
    function run() {
      var auth = window.__KPI_AUTH;
      if (auth && typeof auth.syncPlanFromServer === 'function') {
        Promise.resolve(auth.syncPlanFromServer())
          .catch(function () {
            return null;
          })
          .then(function () {
            return waitForYearStoreUserScopeReady();
          })
          .then(function () {
            hydrateFromServer(cfg);
          });
        return;
      }
      tries += 1;
      if (tries < 80) {
        window.setTimeout(run, 25);
        return;
      }
      hydrateFromServer(cfg);
    }
    run();
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
      /* Prefer in-memory full store — LS may hold a slimmed timeline window. */
      if (key === STORE_KEY) {
        try {
          if (window.KpiYearStore && typeof window.KpiYearStore.getStore === 'function') {
            var mem = window.KpiYearStore.getStore();
            if (mem && typeof mem === 'object') return mem;
          }
        } catch (_eMem) {}
      }
      return localGet(key);
    },
    setJson: function (key, value) {
      var toStore = value;
      if (key === STORE_KEY && value && typeof value === 'object') {
        toStore = slimTimelineForLocalStorage(stripDailyFactsFromStore(value));
      }
      var ok = localSet(key, toStore);
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
    /** Suppress LS→PUT while auth clears another account's keys (KPI-LS-USER-SCOPE-7). */
    beginLocalUserScopeReset: function () {
      if (putTimer != null) {
        window.clearTimeout(putTimer);
        putTimer = null;
      }
      userScopePutHold = true;
      hydrated = false;
      hookQuiet = true;
    },
    endLocalUserScopeReset: function () {
      if (putTimer != null) {
        window.clearTimeout(putTimer);
        putTimer = null;
      }
      hookQuiet = false;
      hydrated = false;
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
      hydrateAfterAuthBind(cfg);
      return next;
    },
    pullFromServer: function () {
      hydrated = false;
      cfg = readSyncConfig();
      hydrateAfterAuthBind(cfg);
    },
    pushToServerNow: function () {
      cfg = readSyncConfig();
      return flushPut();
    },
    flushPut: flushPut,
    collectPlFromLocal: collectPlFromLocal,
  };

  if (canSync(cfg)) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        hydrateAfterAuthBind(cfg);
      });
    } else {
      hydrateAfterAuthBind(cfg);
    }
  }
})();

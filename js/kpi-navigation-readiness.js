/**
 * BR-ONBOARDING-01 Phase 1 — Navigation Readiness.
 * Separate from KpiPlanningReadiness. Does not write store.meta.setup.
 * Phase 1 cockpit block: !grandfathered && !businessTypeComplete, after hydrate only.
 * A successful GET with store:null is an empty business state, not PENDING.
 * Phase 2: businessProfileComplete is the 7-field Hard Required AND.
 * It does not widen phase1Block.
 * Phase 4: currentYearSummary feeds STEP 03; completion is currentYearAcknowledged only.
 * Phase 5: annualTargetSummary feeds STEP 04; completion is targetAcknowledged only.
 * Phase 6: completionCheck / loadCompletion gate STEP 05; setup.complete is written only there.
 */
(function (global) {
  'use strict';

  if (global.KpiNavigationReadiness && global.KpiNavigationReadiness.__ready) {
    return;
  }

  var LEGACY_PLACEHOLDER_SALES = 1234;
  var ISO_RE = /^\d{4}-\d{2}-\d{2}$/;
  var COPY = {
    ja: 'KPNを利用するために、最初にビジネス情報を設定してください。',
    en: 'To use KPN, please set up your business information first.',
    zh: '使用 KPN 前，請先設定您的商家資訊。',
  };
  var START_COPY = {
    ja: '初期設定を始める',
    en: 'Start Initial Setup',
    zh: '開始初始設定',
  };
  var RESUME_COPY = {
    ja: '初期設定を続ける',
    en: 'Continue Setup',
    zh: '繼續初始設定',
  };
  var SETUP_PARAM = 'kpnSetup';
  var HARD_REQUIRED_FIELDS = [
    'businessName',
    'companyName',
    'businessType',
    'openingDate',
    'country',
    'stateRegion',
    'currency',
  ];

  function detectLang() {
    var raw = '';
    try {
      raw = String(
        (global.document &&
          global.document.documentElement &&
          global.document.documentElement.getAttribute('lang')) ||
          ''
      );
    } catch (_e) {}
    var l = raw.toLowerCase();
    if (l.indexOf('ja') === 0) return 'ja';
    if (l.indexOf('zh') === 0) return 'zh';
    return 'en';
  }

  function trimmed(value) {
    if (value == null) return '';
    return String(value).trim();
  }

  function finiteSales(value) {
    if (typeof value === 'number') return Number.isFinite(value) ? value : null;
    if (typeof value === 'string') {
      var s = value.trim();
      if (!s) return null;
      var n = Number(s);
      return Number.isFinite(n) ? n : null;
    }
    return null;
  }

  function operatingYearOf(store) {
    var oy = store && store.meta ? Number(store.meta.operatingYear) : NaN;
    if (Number.isFinite(oy)) return oy;
    return new Date().getFullYear();
  }

  function isCanonicalDailySales(iso, value, oy) {
    if (!iso || !ISO_RE.test(String(iso))) return false;
    var n = finiteSales(value);
    if (n == null) return false;
    var y = Number(String(iso).slice(0, 4));
    if (y >= oy && n === LEGACY_PLACEHOLDER_SALES) return false;
    return true;
  }

  function hasCanonicalDailySales(store, oy) {
    var map = store && store.timeline ? store.timeline.dailySales : null;
    if (!map || typeof map !== 'object') return false;
    var keys = Object.keys(map);
    for (var i = 0; i < keys.length; i++) {
      if (isCanonicalDailySales(keys[i], map[keys[i]], oy)) return true;
    }
    return false;
  }

  function yearRecord(store, oy) {
    if (!store || !store.years || typeof store.years !== 'object') return null;
    return store.years[oy] || store.years[String(oy)] || null;
  }

  function hasUserAnnualTarget(store, oy) {
    var rec = yearRecord(store, oy);
    var plan = rec && rec.plan;
    if (!plan) return false;
    var n = Number(plan.targetSales);
    if (!Number.isFinite(n) || !(n > 0)) return false;
    if (plan.source === 'rollover-snapshot') return false;
    return true;
  }

  function isValidOpeningDate(value) {
    var s = trimmed(value);
    if (!ISO_RE.test(s)) return false;
    var p = s.split('-');
    var y = Number(p[0]);
    var m = Number(p[1]);
    var d = Number(p[2]);
    if (m < 1 || m > 12 || d < 1 || d > 31) return false;
    var dt = new Date(Date.UTC(y, m - 1, d));
    return dt.getUTCFullYear() === y && dt.getUTCMonth() === m - 1 && dt.getUTCDate() === d;
  }

  function pad2(n) {
    return (n < 10 ? '0' : '') + n;
  }

  /** Year and month are required; a blank day is stored as 01. Invalid input returns ''. */
  function buildOpeningDate(year, month, day) {
    var y = Number(trimmed(year));
    var m = Number(trimmed(month));
    var dRaw = trimmed(day);
    var d = dRaw ? Number(dRaw) : 1;
    if (!Number.isInteger(y) || y < 1000 || y > 9999) return '';
    if (!Number.isInteger(m) || !Number.isInteger(d)) return '';
    var iso = String(y) + '-' + pad2(m) + '-' + pad2(d);
    return isValidOpeningDate(iso) ? iso : '';
  }

  /**
   * Pure 7-field Hard Required check.
   * businessTypeSet must be a saved or explicitly selected canonical type, never the fallback.
   */
  function evaluateBusinessProfile(values) {
    var v = values && typeof values === 'object' ? values : {};
    var flags = {
      businessName: !!trimmed(v.businessName),
      companyName: !!trimmed(v.companyName),
      businessType: v.businessTypeSet === true,
      openingDate: isValidOpeningDate(v.openingDate),
      country: !!trimmed(v.country),
      stateRegion: !!trimmed(v.stateRegion),
      currency: !!trimmed(v.currency),
    };
    var missing = HARD_REQUIRED_FIELDS.filter(function (k) {
      return !flags[k];
    });
    return { complete: missing.length === 0, missing: missing, flags: flags };
  }

  function setupBag(store) {
    var bag = store && store.meta && store.meta.setup;
    return bag && typeof bag === 'object' ? bag : null;
  }

  function hasHistoricalSales(store, oy, openingDate) {
    var map = store && store.timeline ? store.timeline.dailySales : null;
    if (!map || typeof map !== 'object') return false;
    var keys = Object.keys(map);
    for (var i = 0; i < keys.length; i++) {
      var iso = String(keys[i]);
      if (!isCanonicalDailySales(iso, map[iso], oy)) continue;
      var y = Number(iso.slice(0, 4));
      if (y < oy && iso >= openingDate) return true;
    }
    return false;
  }

  function initialDataState(store, oy, openingDate, openingOk) {
    if (!openingOk) return null;
    var openYear = Number(String(openingDate).slice(0, 4));
    if (openYear >= oy) return 'not_applicable';
    if (hasHistoricalSales(store, oy, openingDate)) return 'present';
    var bag = setupBag(store);
    if (bag && bag.historicalSkipped === true) return 'skipped';
    return 'absent';
  }

  function historicalYears(store, oy, openingDate) {
    var map = store && store.timeline ? store.timeline.dailySales : null;
    if (!map || typeof map !== 'object') return [];
    var seen = {};
    Object.keys(map).forEach(function (iso) {
      if (!isCanonicalDailySales(iso, map[iso], oy)) return;
      var y = Number(String(iso).slice(0, 4));
      if (y < oy && String(iso) >= openingDate) seen[y] = true;
    });
    return Object.keys(seen)
      .map(Number)
      .sort(function (a, b) {
        return a - b;
      });
  }

  /**
   * STEP 02 summary from the store alone. level follows the opening year only:
   * same year = not_applicable, previous year = recommended, two or more years back = strong.
   * Returns null while the opening date is not a valid YYYY-MM-DD.
   */
  function historicalSummary(store) {
    var s = store && typeof store === 'object' ? store : {};
    var oy = operatingYearOf(s);
    var openingDate = s.meta ? trimmed(s.meta.openingDate) : '';
    if (!isValidOpeningDate(openingDate)) return null;
    var openYear = Number(openingDate.slice(0, 4));
    var level = openYear >= oy ? 'not_applicable' : openYear === oy - 1 ? 'recommended' : 'strong';
    return {
      operatingYear: oy,
      openingDate: openingDate,
      openingYm: openingDate.slice(0, 7),
      rangeStart: level === 'not_applicable' ? null : openingDate.slice(0, 7),
      rangeEnd: level === 'not_applicable' ? null : String(oy - 1) + '-12',
      state: initialDataState(s, oy, openingDate, true),
      detectedYears: level === 'not_applicable' ? [] : historicalYears(s, oy, openingDate),
      level: level,
    };
  }

  /* Same rule as KpiYearStore.isUserSavedAnnualPlanSource (R2). The grandfather predicate keeps hasUserAnnualTarget. */
  var USER_TARGET_SOURCES = { 'sales-data-save': true };

  /**
   * STEP 04 summary. status: set (user-saved target > 0 for operatingYear) | not_set.
   * rollover-snapshot and memory-only heal values are not_set. Never decides completion;
   * only store.meta.setup.targetAcknowledged does.
   */
  function annualTargetSummary(store) {
    var s = store && typeof store === 'object' ? store : {};
    var oy = operatingYearOf(s);
    var rec = yearRecord(s, oy);
    var plan = rec && rec.plan;
    var n = plan ? Number(plan.targetSales) : NaN;
    var set = !!(plan && USER_TARGET_SOURCES[String(plan.source || '')] && Number.isFinite(n) && n > 0);
    var bag = setupBag(s);
    return {
      operatingYear: oy,
      targetSales: set ? n : null,
      status: set ? 'set' : 'not_set',
      acknowledged: !!(bag && bag.targetAcknowledged === true),
    };
  }

  /**
   * STEP 05 completion contract. step = first unresolved step (profile | history | current | target)
   * or null when setup.complete may be written. Hard 7 fields, historical present / skipped /
   * not_applicable, currentYearAcknowledged, targetAcknowledged. No stored step is read.
   */
  function completionCheck(ctx) {
    var c = ctx || {};
    var s = c.store && typeof c.store === 'object' ? c.store : {};
    var p = c.profile && typeof c.profile === 'object' ? c.profile : {};
    var hard = evaluateBusinessProfile({
      businessName: p.businessName,
      companyName: p.companyName,
      businessTypeSet: c.businessTypeSet === true,
      openingDate: s.meta ? s.meta.openingDate : '',
      country: p.country,
      stateRegion: p.stateRegion,
      currency: p.currency,
    });
    var history = historicalSummary(s);
    var current = currentYearSummary(s, c.today);
    var target = annualTargetSummary(s);
    var step = null;
    if (!hard.complete) step = 'profile';
    else if (!history || history.state === 'absent' || !history.state) step = 'history';
    else if (!current || current.status === 'invalid' || !current.acknowledged) step = 'current';
    else if (!target.acknowledged) step = 'target';
    var bag = setupBag(s);
    return {
      ready: step === null,
      step: step,
      missing: hard.missing,
      history: history,
      current: current,
      target: target,
      complete: !!(bag && bag.complete === true),
    };
  }

  function localTodayIso() {
    var d = new Date();
    return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
  }

  /**
   * STEP 03 summary. Range = max(openingDate, operatingYear-01-01) .. min(today, operatingYear-12-31).
   * status: present | none | new_business | invalid (invalidReason opening_future | no_period).
   * Counts never decide completion; only store.meta.setup.currentYearAcknowledged does.
   * today is an optional YYYY-MM-DD override. Returns null while the opening date is invalid.
   */
  function currentYearSummary(store, today) {
    var s = store && typeof store === 'object' ? store : {};
    var oy = operatingYearOf(s);
    var openingDate = s.meta ? trimmed(s.meta.openingDate) : '';
    if (!isValidOpeningDate(openingDate)) return null;
    var todayIso = isValidOpeningDate(today) ? String(today) : localTodayIso();
    var yearStart = String(oy) + '-01-01';
    var yearEnd = String(oy) + '-12-31';
    var rangeStart = openingDate > yearStart ? openingDate : yearStart;
    var rangeEnd = todayIso < yearEnd ? todayIso : yearEnd;
    var bag = setupBag(s);
    var out = {
      operatingYear: oy,
      openingDate: openingDate,
      openingYm: openingDate.slice(0, 7),
      today: todayIso,
      startedThisYear: Number(openingDate.slice(0, 4)) === oy,
      rangeStart: rangeStart,
      rangeEnd: rangeEnd,
      detectedDays: 0,
      positiveDays: 0,
      status: 'none',
      invalidReason: null,
      acknowledged: !!(bag && bag.currentYearAcknowledged === true),
    };
    if (openingDate > todayIso) {
      out.status = 'invalid';
      out.invalidReason = 'opening_future';
      return out;
    }
    if (rangeStart > rangeEnd) {
      out.status = 'invalid';
      out.invalidReason = 'no_period';
      return out;
    }
    var map = s.timeline ? s.timeline.dailySales : null;
    if (map && typeof map === 'object') {
      Object.keys(map).forEach(function (iso) {
        if (!isCanonicalDailySales(iso, map[iso], oy)) return;
        if (iso < rangeStart || iso > rangeEnd) return;
        out.detectedDays++;
        if (finiteSales(map[iso]) > 0) out.positiveDays++;
      });
    }
    if (out.detectedDays > 0) out.status = 'present';
    else if (out.startedThisYear) out.status = 'new_business';
    return out;
  }

  function blankFacts() {
    return {
      status: 'PENDING',
      phase1Block: false,
      grandfathered: false,
      explicitKnownSeedState: false,
      businessProfileComplete: false,
      businessProfileMissing: HARD_REQUIRED_FIELDS.slice(),
      businessTypeComplete: false,
      openingDateComplete: false,
      initialDataState: null,
      annualTargetComplete: false,
      setupComplete: false,
      activeSetup: false,
      currentYearAcknowledged: false,
      targetAcknowledged: false,
      historicalSkipped: false,
      expenseStep: 'soft',
    };
  }

  /**
   * Pure snapshot. businessTypeSet must come from KpiBusinessType.isBusinessTypeSet().
   * The restaurant fallback helper is not a readiness input.
   */
  function evaluateSnapshot(ctx) {
    ctx = ctx || {};
    if (!ctx.storeHydrated || !ctx.profileOk) return blankFacts();
    var store = ctx.store && typeof ctx.store === 'object' ? ctx.store : {};
    var profile = ctx.profile && typeof ctx.profile === 'object' ? ctx.profile : {};
    var oy = operatingYearOf(store);
    var bag = setupBag(store);
    var openingDate = store.meta ? trimmed(store.meta.openingDate) : '';
    var openingOk = isValidOpeningDate(openingDate);
    var setupComplete = !!(bag && bag.complete === true);
    var activeSetup = !!(bag && bag.complete !== true);
    var sales = hasCanonicalDailySales(store, oy);
    var target = hasUserAnnualTarget(store, oy);
    var grandfathered = setupComplete || (!activeSetup && (sales || target));
    var businessTypeComplete = ctx.businessTypeSet === true;
    var hard = evaluateBusinessProfile({
      businessName: profile.businessName,
      companyName: profile.companyName,
      businessTypeSet: businessTypeComplete,
      openingDate: openingDate,
      country: profile.country,
      stateRegion: profile.stateRegion,
      currency: profile.currency,
    });
    var businessProfileComplete = hard.complete;
    var annualTargetComplete = target;
    var status = 'NORMAL';
    if (!grandfathered) {
      if (!businessProfileComplete) {
        status = 'SETUP_PROFILE_REQUIRED';
      } else if (!setupComplete) {
        status = 'SETUP_INITIAL_REQUIRED';
      }
    }
    return {
      status: status,
      phase1Block: !grandfathered && !businessTypeComplete,
      grandfathered: grandfathered,
      explicitKnownSeedState: false,
      businessProfileComplete: businessProfileComplete,
      businessProfileMissing: hard.missing,
      businessTypeComplete: businessTypeComplete,
      openingDateComplete: openingOk,
      initialDataState: initialDataState(store, oy, openingDate, openingOk),
      annualTargetComplete: annualTargetComplete,
      setupComplete: setupComplete,
      activeSetup: activeSetup,
      currentYearAcknowledged: !!(bag && bag.currentYearAcknowledged === true),
      targetAcknowledged: !!(bag && bag.targetAcknowledged === true),
      historicalSkipped: !!(bag && bag.historicalSkipped === true),
      expenseStep: ctx.plan === 'basic' ? 'not_required' : 'soft',
    };
  }

  function resolveProfileApi() {
    if (global.__KPI_AUTH && typeof global.__KPI_AUTH.resolveAuthBase === 'function') {
      try {
        return global.__KPI_AUTH.resolveAuthBase().replace(/\/?$/, '') + '/profile.php';
      } catch (_e) {}
    }
    return '/kpi-navigator/api/v1/profile.php';
  }

  function readStore() {
    try {
      if (global.KpiYearStore && typeof global.KpiYearStore.getStore === 'function') {
        var mem = global.KpiYearStore.getStore();
        if (mem && typeof mem === 'object') return mem;
      }
    } catch (_e) {}
    return null;
  }

  function businessTypeIsSet() {
    try {
      return !!(
        global.KpiBusinessType &&
        typeof global.KpiBusinessType.isBusinessTypeSet === 'function' &&
        global.KpiBusinessType.isBusinessTypeSet()
      );
    } catch (_e) {
      return false;
    }
  }

  function fetchProfile() {
    if (typeof global.fetch !== 'function') {
      return Promise.resolve({ ok: false, profile: null });
    }
    return global
      .fetch(resolveProfileApi(), {
        method: 'GET',
        credentials: 'include',
        headers: { Accept: 'application/json' },
      })
      .then(function (res) {
        return res.json().catch(function () {
          return null;
        }).then(function (data) {
          if (!res.ok || !data || data.ok !== true) return { ok: false, profile: null };
          return { ok: true, profile: data.profile || {} };
        });
      })
      .catch(function () {
        return { ok: false, profile: null };
      });
  }

  function storeApiUrl() {
    try {
      var gw = global.__KPI_DATA_GATEWAY;
      var cfg = gw && typeof gw.syncConfig === 'function' ? gw.syncConfig() : null;
      if (cfg && cfg.baseUrl) return cfg.baseUrl;
    } catch (_e) {}
    return resolveProfileApi().replace(/profile\.php$/, 'store.php');
  }

  /** Read-only GET of the server store (no memory merge). */
  function fetchServerStore() {
    if (typeof global.fetch !== 'function') return Promise.resolve({ ok: false, store: null, revision: null });
    return global
      .fetch(storeApiUrl(), {
        method: 'GET',
        credentials: 'include',
        cache: 'no-store',
        headers: { Accept: 'application/json' },
      })
      .then(function (res) {
        return res.json().catch(function () {
          return null;
        }).then(function (data) {
          if (!res.ok || !data || data.ok !== true) return { ok: false, store: null, revision: null };
          return { ok: true, store: data.store || null, revision: data.revision == null ? null : data.revision };
        });
      })
      .catch(function () {
        return { ok: false, store: null, revision: null };
      });
  }

  /**
   * Latest server profile + business type, server store (read-only) and the in-memory store
   * that a save would send, evaluated with completionCheck. check uses the memory store;
   * server is returned for comparison.
   */
  function loadCompletion() {
    return Promise.all([hydrateBusinessTypeProfile(), fetchProfile(), fetchServerStore()]).then(function (all) {
      var prof = all[1] || { ok: false, profile: null };
      var srv = all[2] || { ok: false, store: null, revision: null };
      var mem = readStore();
      var ok = all[0] === true && prof.ok === true && srv.ok === true && !!mem;
      var profileCtx = prof.profile || {};
      var btSet = businessTypeIsSet();
      return {
        ok: ok,
        profile: profileCtx,
        check: completionCheck({ store: mem, profile: profileCtx, businessTypeSet: btSet }),
        server: {
          revision: srv.revision,
          check: srv.store ? completionCheck({ store: srv.store, profile: profileCtx, businessTypeSet: btSet }) : null,
        },
      };
    });
  }

  function currentPlan() {
    return lastPlan;
  }

  /** Any saved PL expense year in this browser's synced PL keys (Pro expense import / entry). */
  function hasExpenseData() {
    try {
      var gw = global.__KPI_DATA_GATEWAY;
      var pl = gw && typeof gw.collectPlFromLocal === 'function' ? gw.collectPlFromLocal() : null;
      var ey = (pl && pl.expensesByYear) || {};
      return Object.keys(ey).some(function (y) {
        return ey[y] && typeof ey[y] === 'object' && Object.keys(ey[y]).length > 0;
      });
    } catch (_e) {
      return false;
    }
  }

  function hydrateBusinessTypeProfile() {
    try {
      if (
        global.KpiBusinessType &&
        typeof global.KpiBusinessType.hydrateFromServerProfile === 'function'
      ) {
        return Promise.resolve(global.KpiBusinessType.hydrateFromServerProfile()).then(function (out) {
          return !!(out && out.ok);
        });
      }
    } catch (_e) {}
    return Promise.resolve(false);
  }

  var generation = 0;
  var lastPlan = null;
  var lastResult = null;
  var guardEl = null;
  var resumeEl = null;
  var setupParamHandled = false;

  function ensureStyle() {
    if (!global.document || global.document.getElementById('kpi-nr-guard-css')) return;
    var style = global.document.createElement('style');
    style.id = 'kpi-nr-guard-css';
    style.textContent = [
      '#kpi-nr-guard{position:fixed;inset:0;z-index:100000;display:flex;align-items:center;justify-content:center;padding:24px;',
      'background:rgba(2,8,18,.72);}',
      '#kpi-nr-guard[hidden]{display:none !important;}',
      '#kpi-nr-guard .kpi-nr-card{max-width:440px;width:100%;padding:28px 26px 24px;border:1px solid rgba(0,229,255,.7);',
      'background:rgba(4,14,28,.94);color:#e8fbff;box-shadow:0 0 24px rgba(0,229,255,.18);}',
      '#kpi-nr-guard .kpi-nr-headline{margin:0 0 12px;font-size:18px;letter-spacing:.08em;font-weight:700;}',
      '#kpi-nr-guard .kpi-nr-body{margin:0;font-size:14px;line-height:1.6;}',
      '#kpi-nr-guard .kpi-nr-start{margin-top:18px;padding:9px 16px;font:inherit;font-size:13px;font-weight:700;letter-spacing:.04em;cursor:pointer;',
      'border:1px solid rgba(0,229,255,.85);background:rgba(0,229,255,.14);color:#e8fbff;}',
      '#kpi-nr-guard .kpi-nr-start:hover{background:rgba(0,229,255,.26);}',
      '#kpi-nr-guard .kpi-nr-start[hidden]{display:none;}',
      'body.office-mode #kpi-nr-guard{background:rgba(20,20,20,.28);}',
      'body.office-mode #kpi-nr-guard .kpi-nr-card{border:1px solid #1c1c1c;background:#f4f1ea;color:#1a1a1c;box-shadow:none;}',
      'body.office-mode #kpi-nr-guard .kpi-nr-headline{letter-spacing:.04em;font-weight:600;}',
      'body.office-mode #kpi-nr-guard .kpi-nr-start{border-color:#1c1c1c;background:#1c1c1c;color:#fff;}',
      'body.office-mode #kpi-nr-guard .kpi-nr-start:hover{background:#3a3a3a;}',
      '#kpi-nr-resume{position:fixed;left:18px;bottom:70px;z-index:900;padding:7px 14px;font:inherit;font-size:12px;font-weight:700;letter-spacing:.06em;cursor:pointer;',
      'border:1px solid rgba(0,229,255,.6);background:rgba(4,14,28,.9);color:#e8fbff;}',
      '#kpi-nr-resume:hover{border-color:#00e5ff;background:rgba(0,229,255,.18);}',
      '#kpi-nr-resume[hidden]{display:none !important;}',
      'body.office-mode #kpi-nr-resume{border-color:#1c1c1c;background:#f4f1ea;color:#1c1c1c;}',
      'body.office-mode #kpi-nr-resume:hover{background:#e8e3d8;}',
    ].join('');
    (global.document.head || global.document.documentElement).appendChild(style);
  }

  function ensureGuard() {
    if (!global.document) return null;
    ensureStyle();
    if (guardEl && guardEl.parentNode) return guardEl;
    guardEl = global.document.getElementById('kpi-nr-guard');
    if (guardEl) return guardEl;
    guardEl = global.document.createElement('div');
    guardEl.id = 'kpi-nr-guard';
    guardEl.setAttribute('role', 'dialog');
    guardEl.setAttribute('aria-modal', 'true');
    guardEl.setAttribute('aria-labelledby', 'kpi-nr-headline');
    guardEl.hidden = true;
    guardEl.innerHTML =
      '<div class="kpi-nr-card"><h2 class="kpi-nr-headline" id="kpi-nr-headline">KPN SETUP REQUIRED</h2>' +
      '<p class="kpi-nr-body" id="kpi-nr-body"></p>' +
      '<button type="button" class="kpi-nr-start" id="kpi-nr-start" hidden></button></div>';
    global.document.body.appendChild(guardEl);
    var start = guardEl.querySelector('#kpi-nr-start');
    if (start) start.addEventListener('click', openStep0);
    return guardEl;
  }

  function step0Api() {
    var api = global.KpiSetupStep0;
    return api && typeof api.open === 'function' ? api : null;
  }

  function historyApi() {
    var api = global.KpiSetupStep0;
    return api && typeof api.openHistory === 'function' ? api : null;
  }

  function isSetupPending(result) {
    return !!(
      result &&
      !result.grandfathered &&
      (result.status === 'SETUP_PROFILE_REQUIRED' || result.status === 'SETUP_INITIAL_REQUIRED')
    );
  }

  /** Called from the guard: the user is not grandfathered, so Step 01 may start the setup object. */
  function openStep0() {
    var api = step0Api();
    if (!api) return;
    api.open({
      startSetup: true,
      continueSetup: !!historyApi(),
      onDone: function () {
        settle(lastPlan).then(function (result) {
          if (result && !result.grandfathered && result.status === 'SETUP_INITIAL_REQUIRED') {
            openHistory('flow');
          }
        });
      },
    });
  }

  function openHistory(entry) {
    var api = historyApi();
    if (!api) return;
    api.openHistory({
      entry: entry,
      onDone: function () {
        settle(lastPlan);
      },
    });
  }

  /** Resume is derived from Readiness only; no step is stored. */
  function resumeSetup() {
    var result = lastResult;
    if (!isSetupPending(result) || result.phase1Block) return;
    if (!result.businessProfileComplete) {
      openStep0();
      return;
    }
    openHistory('resume');
  }

  function setupDialogOpen() {
    var d = global.document && global.document.getElementById('kpi-s0');
    return !!(d && !d.hidden);
  }

  function hasHistoryImporter() {
    return !!(global.document && global.document.getElementById('annual-past-sales-btn'));
  }

  function hasCurrentYearImporter() {
    return !!(
      global.document &&
      global.document.getElementById('annual-current-sales-btn') &&
      global.document.getElementById('sales-data-modal')
    );
  }

  function applyResume(result) {
    if (!global.document || !global.document.body) return;
    var show = isSetupPending(result) && !result.phase1Block && hasHistoryImporter() && !!historyApi();
    if (!show && !resumeEl) return;
    if (!resumeEl) {
      ensureStyle();
      resumeEl = global.document.createElement('button');
      resumeEl.type = 'button';
      resumeEl.id = 'kpi-nr-resume';
      resumeEl.hidden = true;
      resumeEl.addEventListener('click', resumeSetup);
      global.document.body.appendChild(resumeEl);
    }
    var lang = detectLang();
    resumeEl.textContent = RESUME_COPY[lang] || RESUME_COPY.en;
    resumeEl.hidden = !show;
  }

  function takeSetupParam() {
    if (setupParamHandled) return false;
    setupParamHandled = true;
    var loc = global.location;
    if (!loc || !loc.search) return false;
    var re = new RegExp('([?&])' + SETUP_PARAM + '=1(&|$)');
    if (!re.test(loc.search)) return false;
    try {
      var search = loc.search.replace(re, function (_m, lead, tail) {
        return tail ? lead : '';
      }).replace(/[?&]$/, '');
      global.history.replaceState(global.history.state, '', loc.pathname + search + (loc.hash || ''));
    } catch (_e) {}
    return true;
  }

  function annualSetupUrl() {
    if (!global.document) return '';
    var a = global.document.querySelector('.global-nav-item a.nav-frame-btn[href*="annual/index.html"]');
    if (!a || !a.href) return '';
    return a.href.split('#')[0] + (a.href.indexOf('?') >= 0 ? '&' : '?') + SETUP_PARAM + '=1';
  }

  function applyGuard(result) {
    var el = ensureGuard();
    if (!el) return;
    var block = !!(result && result.phase1Block);
    el.hidden = !block;
    if (!block) return;
    var lang = detectLang();
    var body = el.querySelector('#kpi-nr-body');
    if (body) body.textContent = COPY[lang] || COPY.en;
    var start = el.querySelector('#kpi-nr-start');
    if (start) {
      start.textContent = START_COPY[lang] || START_COPY.en;
      start.hidden = !step0Api();
    }
  }

  function settle(plan) {
    var gen = ++generation;
    applyGuard(blankFacts());
    return Promise.all([hydrateBusinessTypeProfile(), fetchProfile()]).then(function (pair) {
      if (gen !== generation) return null;
      var btOk = pair[0] === true;
      var prof = pair[1] || { ok: false, profile: null };
      var store = readStore();
      var result = evaluateSnapshot({
        storeHydrated: true,
        profileOk: btOk && prof.ok === true,
        store: store,
        profile: prof.profile,
        businessTypeSet: businessTypeIsSet(),
        plan: plan,
      });
      if (!store && result.status !== 'PENDING') {
        result = blankFacts();
      }
      applyGuard(result);
      if (result.status === 'PENDING') return result;
      lastResult = result;
      applyResume(result);
      if (takeSetupParam() && !setupDialogOpen()) resumeSetup();
      return result;
    });
  }

  function onStoreHydrated(ev) {
    var plan = ev && ev.detail ? ev.detail.plan : null;
    if (plan != null) lastPlan = plan;
    settle(lastPlan);
  }

  function install() {
    if (!global.document || !global.document.addEventListener) return;
    global.document.addEventListener('kpi:storeHydrateSettled', onStoreHydrated);
  }

  global.KpiNavigationReadiness = {
    __ready: true,
    evaluateSnapshot: evaluateSnapshot,
    evaluateBusinessProfile: evaluateBusinessProfile,
    historicalSummary: historicalSummary,
    currentYearSummary: currentYearSummary,
    annualTargetSummary: annualTargetSummary,
    completionCheck: completionCheck,
    loadCompletion: loadCompletion,
    currentPlan: currentPlan,
    hasExpenseData: hasExpenseData,
    annualSetupUrl: annualSetupUrl,
    hasHistoryImporter: hasHistoryImporter,
    hasCurrentYearImporter: hasCurrentYearImporter,
    resumeSetup: resumeSetup,
    buildOpeningDate: buildOpeningDate,
    isValidOpeningDate: isValidOpeningDate,
    HARD_REQUIRED_FIELDS: HARD_REQUIRED_FIELDS.slice(),
    detectLang: detectLang,
    COPY: COPY,
    settle: settle,
  };

  install();
})(typeof window !== 'undefined' ? window : this);

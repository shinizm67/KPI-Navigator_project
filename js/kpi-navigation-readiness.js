/**
 * BR-ONBOARDING-01 Phase 1 — Navigation Readiness.
 * Separate from KpiPlanningReadiness. Does not write store.meta.setup.
 * Phase 1 cockpit block: !grandfathered && !businessTypeComplete, after hydrate only.
 * A successful GET with store:null is an empty business state, not PENDING.
 * Phase 2: businessProfileComplete is the 7-field Hard Required AND.
 * It does not widen phase1Block.
 */
(function (global) {
  'use strict';

  if (global.KpiNavigationReadiness && global.KpiNavigationReadiness.__ready) {
    return;
  }

  var LEGACY_PLACEHOLDER_SALES = 1234;
  var ISO_RE = /^\d{4}-\d{2}-\d{2}$/;
  var COPY = {
    ja: '業種が未設定のため、この画面はまだ通常利用できません。',
    en: 'Business Type is not set, so this screen is not ready for normal use yet.',
    zh: '尚未設定業種，此畫面目前還不能進入一般使用。',
  };
  var START_COPY = {
    ja: 'Business Profile を入力する',
    en: 'Enter Business Profile',
    zh: '填寫 Business Profile',
  };
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
  var guardEl = null;

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

  function openStep0() {
    var api = step0Api();
    if (!api) return;
    api.open({
      onDone: function () {
        settle(lastPlan);
      },
    });
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
    buildOpeningDate: buildOpeningDate,
    isValidOpeningDate: isValidOpeningDate,
    HARD_REQUIRED_FIELDS: HARD_REQUIRED_FIELDS.slice(),
    detectLang: detectLang,
    COPY: COPY,
    settle: settle,
  };

  install();
})(typeof window !== 'undefined' ? window : this);

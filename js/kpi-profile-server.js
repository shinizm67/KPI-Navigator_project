/**
 * Server profile sync for Profile Edit ↔ kpi_user_profiles.
 * The server profile is authoritative. localStorage is a cache written after a successful read or save.
 */
(function (global) {
  'use strict';

  var PROFILE_LAST_KEY = 'kpi-profile-last';
  var SYNC_RESULT_KEY = 'kpi-profile-server-sync';
  var saveInflight = null;
  var loadInflight = null;

  function resolveProfileApi() {
    if (global.__KPI_AUTH && typeof global.__KPI_AUTH.resolveAuthBase === 'function') {
      try {
        return global.__KPI_AUTH.resolveAuthBase().replace(/\/?$/, '') + '/profile.php';
      } catch (_e) {}
    }
    return '/kpi-navigator/api/v1/profile.php';
  }

  function normalizeLocale(raw) {
    var s = String(raw == null ? '' : raw).trim().toLowerCase();
    if (!s) {
      try {
        s = String(document.documentElement.getAttribute('lang') || '').trim().toLowerCase();
      } catch (_e) {
        s = '';
      }
    }
    if (s.indexOf('zh') === 0) return 'zh-TW';
    if (s.indexOf('ja') === 0 || s === 'jp') return 'ja';
    if (s.indexOf('en') === 0) return 'en';
    try {
      var path = String(global.location && global.location.pathname || '');
      if (path.indexOf('/zh-tw/') >= 0) return 'zh-TW';
      if (path.indexOf('/en/') >= 0) return 'en';
    } catch (_e2) {}
    return 'ja';
  }

  function readLocalProfile() {
    try {
      var raw = localStorage.getItem(PROFILE_LAST_KEY);
      var data = raw ? JSON.parse(raw) : {};
      return data && typeof data === 'object' ? data : {};
    } catch (_e) {
      return {};
    }
  }

  function strOrEmpty(v) {
    if (v == null) return '';
    return String(v);
  }

  function hasText(v) {
    return strOrEmpty(v).trim() !== '';
  }

  /** Map API profile → localStorage-shaped object. */
  function serverToLocalShape(profile) {
    var p = profile || {};
    var type = strOrEmpty(p.businessType);
    return {
      businessName: strOrEmpty(p.businessName),
      company: strOrEmpty(p.companyName),
      companyName: strOrEmpty(p.companyName),
      industry: type,
      businessType: type,
      genre: strOrEmpty(p.genre),
      country: strOrEmpty(p.country),
      state: strOrEmpty(p.stateRegion),
      stateRegion: strOrEmpty(p.stateRegion),
      city: strOrEmpty(p.city),
      currency: strOrEmpty(p.currency),
      locale: strOrEmpty(p.locale),
    };
  }

  /**
   * Prefer non-empty server fields; never wipe local with empty server/unsynced.
   */
  function mergePreferServer(local, serverProfile) {
    var base = local && typeof local === 'object' ? Object.assign({}, local) : {};
    if (!serverProfile || !serverProfile.synced) return base;
    var s = serverToLocalShape(serverProfile);
    ['businessName', 'company', 'companyName', 'industry', 'businessType', 'genre', 'country', 'state', 'stateRegion', 'city', 'currency', 'locale'].forEach(function (k) {
      if (hasText(s[k])) base[k] = s[k];
    });
    if (hasText(base.businessType)) base.industry = base.businessType;
    if (hasText(base.company) && !hasText(base.companyName)) base.companyName = base.company;
    if (hasText(base.companyName) && !hasText(base.company)) base.company = base.companyName;
    if (hasText(base.state) && !hasText(base.stateRegion)) base.stateRegion = base.state;
    if (hasText(base.stateRegion) && !hasText(base.state)) base.state = base.stateRegion;
    return base;
  }

  function stashSyncResult(result) {
    try {
      sessionStorage.setItem(
        SYNC_RESULT_KEY,
        JSON.stringify({
          at: Date.now(),
          ok: !!(result && result.ok),
          skipped: !!(result && result.skipped),
          status: result && result.status != null ? result.status : null,
          error: result && result.error ? String(result.error) : null,
        })
      );
    } catch (_e) {}
  }

  function isAuthenticatedSession() {
    if (!global.__KPI_AUTH) return Promise.resolve(false);
    var probe =
      typeof global.__KPI_AUTH.me === 'function'
        ? global.__KPI_AUTH.me()
        : typeof global.__KPI_AUTH.syncPlanFromServer === 'function'
          ? global.__KPI_AUTH.syncPlanFromServer()
          : null;
    if (!probe || typeof probe.then !== 'function') return Promise.resolve(false);
    return probe
      .then(function (r) {
        return !!(r && r.status === 200 && r.data && r.data.ok && r.data.userId);
      })
      .catch(function () {
        return false;
      });
  }

  function loadServerProfile() {
    if (loadInflight) return loadInflight;
    loadInflight = fetch(resolveProfileApi(), {
      method: 'GET',
      credentials: 'include',
      headers: { Accept: 'application/json' },
    })
      .then(function (r) {
        return r.json().catch(function () {
          return { ok: false };
        }).then(function (data) {
          return {
            ok: !!(data && data.ok),
            status: r.status,
            profile: data && data.profile ? data.profile : null,
            error: data && data.error ? data.error : null,
          };
        });
      })
      .catch(function () {
        return { ok: false, status: 0, profile: null, error: 'network' };
      })
      .then(function (res) {
        loadInflight = null;
        return res;
      });
    return loadInflight;
  }

  function buildPayload(data) {
    var company =
      data && data.company != null
        ? data.company
        : data && data.companyName != null
          ? data.companyName
          : '';
    var type =
      data && data.businessType != null
        ? data.businessType
        : data && data.industry != null
          ? data.industry
          : '';
    var state =
      data && data.state != null
        ? data.state
        : data && data.stateRegion != null
          ? data.stateRegion
          : '';
    return {
      businessName: data && data.businessName != null ? String(data.businessName) : '',
      companyName: String(company),
      businessType: String(type),
      genre: data && data.genre != null ? String(data.genre) : '',
      locale: normalizeLocale(data && data.locale),
      country: data && data.country != null ? String(data.country) : '',
      stateRegion: String(state),
      city: data && data.city != null ? String(data.city) : '',
      currency: data && data.currency != null ? String(data.currency) : '',
    };
  }

  /**
   * Authenticated users only. Does not write the local profile cache.
   * Duplicate concurrent saves share one in-flight request.
   */
  function saveServerProfile(data) {
    if (saveInflight) return saveInflight;

    saveInflight = isAuthenticatedSession().then(function (authed) {
      if (!authed) {
        var skipped = { ok: false, skipped: true, status: 401, error: 'unauthorized' };
        stashSyncResult(skipped);
        return skipped;
      }
      var payload = buildPayload(data);
      if (
        global.__KPI_AUTH &&
        typeof global.__KPI_AUTH.assertCanMutateUserData === 'function' &&
        !global.__KPI_AUTH.assertCanMutateUserData({ notify: true })
      ) {
        var blocked = { ok: false, skipped: true, status: 403, error: 'stale_account' };
        stashSyncResult(blocked);
        return blocked;
      }
      var headers = { 'Content-Type': 'application/json', Accept: 'application/json' };
      try {
        if (global.__KPI_AUTH && typeof global.__KPI_AUTH.attachExpectedUser === 'function') {
          var attached = global.__KPI_AUTH.attachExpectedUser(headers, payload);
          headers = attached.headers;
          payload = attached.body || payload;
        }
      } catch (_eExp) {}
      return fetch(resolveProfileApi(), {
        method: 'POST',
        credentials: 'include',
        headers: headers,
        body: JSON.stringify(payload),
      })
        .then(function (r) {
          return r.json().catch(function () {
            return { ok: false };
          }).then(function (body) {
            var result = {
              ok: !!(body && body.ok) && r.status >= 200 && r.status < 300,
              skipped: false,
              status: r.status,
              profile: body && body.profile ? body.profile : null,
              error: body && body.error ? body.error : r.status >= 400 ? 'save_failed' : null,
            };
            stashSyncResult(result);
            return result;
          });
        })
        .catch(function () {
          var failed = { ok: false, skipped: false, status: 0, error: 'network', profile: null };
          stashSyncResult(failed);
          return failed;
        });
    });

    return saveInflight.then(function (res) {
      saveInflight = null;
      return res;
    });
  }

  function setInputValue(id, value) {
    var el = document.getElementById(id);
    if (!el) return;
    el.value = value != null ? String(value) : '';
  }

  /**
   * Apply local-shaped profile onto Profile Edit form fields.
   * Uses Location/Currency display helpers when present.
   */
  function applyLocalShapeToForm(data) {
    var d = data || {};
    setInputValue('profile-business-name', d.businessName || '');
    setInputValue('profile-company', d.company || d.companyName || '');

    var industry = document.getElementById('profile-industry');
    var type = d.businessType || d.industry || '';
    if (industry) {
      if (type) {
        if (global.KpiBusinessType && typeof global.KpiBusinessType.normalizeBusinessType === 'function') {
          type = global.KpiBusinessType.normalizeBusinessType(type) || type;
        }
        industry.value = type;
      } else {
        /* Empty profile must clear select (do not leave stale prior-user value). */
        industry.value = '';
      }
      /* Never auto-write store.meta.businessType during hydrate (BR-LAUNCH-01-A Option B). */
    }

    var genre = document.getElementById('profile-genre');
    if (genre) genre.value = d.genre || '';

    var Loc = global.KpiProfileLocation;
    var locale = Loc && typeof Loc.localeFromDocument === 'function' ? Loc.localeFromDocument() : 'en';
    var countryInput = document.getElementById('profile-country');
    var stateInput = document.getElementById('profile-state');
    var cityInput = document.getElementById('profile-city');
    if (countryInput) {
      countryInput.value = Loc && Loc.displayCountry ? Loc.displayCountry(d.country, locale) : strOrEmpty(d.country);
      if (Loc && Loc.isPrompt && Loc.isPrompt(countryInput.value)) countryInput.value = '';
    }
    if (stateInput) {
      stateInput.value = Loc && Loc.displayState ? Loc.displayState(d.state || d.stateRegion, locale) : strOrEmpty(d.state || d.stateRegion);
      if (Loc && Loc.isPrompt && Loc.isPrompt(stateInput.value)) stateInput.value = '';
    }
    if (cityInput) {
      cityInput.value = Loc && Loc.displayCity ? Loc.displayCity(d.city, locale) : strOrEmpty(d.city);
      if (Loc && Loc.isPrompt && Loc.isPrompt(cityInput.value)) cityInput.value = '';
    }

    var currencyInput = document.getElementById('profile-currency');
    if (currencyInput && d.currency) {
      var code = d.currency;
      if (global.KpiCurrency && typeof global.KpiCurrency.normalizeCode === 'function') {
        code = global.KpiCurrency.normalizeCode(code) || code;
      }
      currencyInput.value = code;
    }
    setInputValue('profile-timezone', d.timezone || '');
    setInputValue('profile-kpi-focus', d.kpiFocus || '');
  }

  function canonicalMetaType() {
    try {
      if (global.KpiBusinessType && typeof global.KpiBusinessType.readMetaBusinessType === 'function') {
        return global.KpiBusinessType.readMetaBusinessType() || '';
      }
    } catch (_e) {}
    return '';
  }

  function withCanonicalType(shape) {
    var next = Object.assign({}, shape || {});
    var meta = canonicalMetaType();
    if (meta) {
      next.businessType = meta;
      next.industry = meta;
    }
    return next;
  }

  function attachLocalOnly(shape, local) {
    var next = Object.assign({}, shape || {});
    var src = local || {};
    next.timezone = strOrEmpty(src.timezone);
    next.kpiFocus = strOrEmpty(src.kpiFocus);
    return next;
  }

  function writeProfileCache(shape) {
    try {
      localStorage.setItem(PROFILE_LAST_KEY, JSON.stringify(shape || {}));
      if (shape && shape.currency) localStorage.setItem('kpi-currency', String(shape.currency));
      localStorage.setItem('kpi-profile-edited', '1');
      sessionStorage.setItem('kpi-profile-tmp', JSON.stringify(shape || {}));
    } catch (_e) {}
  }

  var MIGRATE_PREFIX = 'kpi-profile-migrate-v1:';

  function migrationDone(userId) {
    try {
      return localStorage.getItem(MIGRATE_PREFIX + String(userId || '')) === '1';
    } catch (_e) {
      return false;
    }
  }

  function markMigrationDone(userId) {
    try {
      localStorage.setItem(MIGRATE_PREFIX + String(userId || ''), '1');
    } catch (_e) {}
  }

  function serverRowEmpty(profile) {
    if (!profile || !profile.synced) return true;
    var shape = serverToLocalShape(profile);
    return !['businessName', 'companyName', 'businessType', 'genre', 'country', 'stateRegion', 'city', 'currency'].some(function (k) {
      return hasText(shape[k]);
    });
  }

  /**
   * One-time copy from this browser only when the server profile row is empty.
   * A populated server row is never patched from local cache.
   */
  function emptyServerMigration(serverProfile, local) {
    var userId = serverProfile && serverProfile.userId ? serverProfile.userId : '';
    var shape = serverToLocalShape(serverProfile && serverProfile.synced ? serverProfile : {});
    if (!serverRowEmpty(serverProfile) || migrationDone(userId)) return { shape: shape, payload: null };
    var payload = serverToLocalShape(serverProfile && serverProfile.synced ? serverProfile : {});
    var changed = false;
    function fill(key, localKey) {
      if (hasText(payload[key])) return;
      var fromLocal = local && (local[localKey || key] != null ? local[localKey || key] : local[key]);
      if (!hasText(fromLocal)) return;
      payload[key] = String(fromLocal).trim();
      shape[key] = payload[key];
      changed = true;
    }
    fill('businessName');
    fill('company', 'company');
    fill('companyName', 'companyName');
    if (!hasText(payload.companyName) && hasText(payload.company)) payload.companyName = payload.company;
    if (!hasText(payload.company) && hasText(payload.companyName)) payload.company = payload.companyName;
    fill('genre');
    fill('country');
    fill('state', 'state');
    fill('stateRegion', 'stateRegion');
    if (!hasText(payload.stateRegion) && hasText(payload.state)) payload.stateRegion = payload.state;
    if (!hasText(payload.state) && hasText(payload.stateRegion)) payload.state = payload.stateRegion;
    fill('city');
    fill('currency');
    var meta = canonicalMetaType();
    if (meta) {
      shape.businessType = meta;
      shape.industry = meta;
      if (!hasText(payload.businessType)) {
        payload.businessType = meta;
        payload.industry = meta;
        changed = true;
      }
    } else {
      fill('businessType', 'businessType');
      if (!hasText(payload.businessType)) fill('industry', 'industry');
      if (hasText(payload.businessType)) payload.industry = payload.businessType;
    }
    if (!changed) return { shape: withCanonicalType(shape), payload: null };
    return { shape: withCanonicalType(shape), payload: payload };
  }

  function requiredGaps(data) {
    var d = data || {};
    var gaps = [];
    if (!hasText(d.businessName)) gaps.push('businessName');
    if (!hasText(d.company) && !hasText(d.companyName)) gaps.push('companyName');
    if (!hasText(d.country)) gaps.push('country');
    if (!hasText(d.state) && !hasText(d.stateRegion)) gaps.push('stateRegion');
    if (!hasText(d.currency)) gaps.push('currency');
    if (!hasText(d.businessType) && !hasText(d.industry)) gaps.push('businessType');
    return gaps;
  }

  function chosenType(data) {
    var raw = data && hasText(data.businessType) ? data.businessType : data && data.industry;
    if (global.KpiBusinessType && typeof global.KpiBusinessType.normalizeBusinessType === 'function') {
      return global.KpiBusinessType.normalizeBusinessType(raw) || '';
    }
    return hasText(raw) ? String(raw).trim() : '';
  }

  /**
   * Canonical store type first when it changes, then the profile copy.
   * Local cache is written only after the required writes succeed.
   * A failed profile copy rolls the canonical type back. Cache is not updated.
   */
  function commitProfileEdit(data) {
    var gaps = requiredGaps(data);
    if (gaps.length) return Promise.resolve({ ok: false, error: 'required', missing: gaps });
    var nextType = chosenType(data);
    if (!nextType) return Promise.resolve({ ok: false, error: 'required', missing: ['businessType'] });
    var prevType = canonicalMetaType();
    var payload = Object.assign({}, data, { businessType: nextType, industry: nextType });

    function remember() {
      var shaped = attachLocalOnly(serverToLocalShape(buildPayload(payload)), payload);
      shaped.businessType = nextType;
      shaped.industry = nextType;
      shaped.company = shaped.company || shaped.companyName || strOrEmpty(payload.company);
      shaped.state = shaped.state || shaped.stateRegion || strOrEmpty(payload.state);
      writeProfileCache(shaped);
    }

    function pushType(type) {
      if (!global.KpiBusinessType || typeof global.KpiBusinessType.syncBusinessType !== 'function') {
        return Promise.resolve({ ok: false, error: 'business_type_unavailable' });
      }
      return global.KpiBusinessType.syncBusinessType(type || '');
    }

    function saveCopy() {
      return saveServerProfile(payload).then(function (saved) {
        if (!saved || saved.ok !== true) {
          return { ok: false, error: (saved && saved.error) || 'save_failed', status: saved && saved.status };
        }
        remember();
        return { ok: true };
      });
    }

    if (prevType === nextType && prevType) return saveCopy();

    return pushType(nextType).then(function (pushed) {
      if (!pushed || pushed.ok !== true) {
        return pushType(prevType).then(function () {
          return { ok: false, error: (pushed && pushed.error) || 'store_push_failed' };
        });
      }
      return saveCopy().then(function (saved) {
        if (saved && saved.ok === true) return saved;
        return pushType(prevType).then(function () {
          return { ok: false, error: (saved && saved.error) || 'save_failed', status: saved && saved.status };
        });
      });
    });
  }

  function profileHasContent(profile) {
    if (!profile || !profile.synced) return false;
    var shape = serverToLocalShape(profile);
    return ['businessName', 'companyName', 'businessType', 'genre', 'country', 'stateRegion', 'city', 'currency'].some(function (k) {
      return hasText(shape[k]);
    }) || !!canonicalMetaType();
  }

  function hydrateDisplay(opts) {
    opts = opts || {};
    return isAuthenticatedSession().then(function (authed) {
      if (!authed) {
        if (typeof opts.onUnavailable === 'function') opts.onUnavailable({ reason: 'unauthorized' });
        return { source: 'unavailable' };
      }
      return loadServerProfile().then(function (res) {
        if (!res.ok || !res.profile) {
          if (typeof opts.onUnavailable === 'function') opts.onUnavailable(res);
          return { source: 'unavailable' };
        }
        var local = readLocalProfile();
        var plan = emptyServerMigration(res.profile, local);
        function paint(shape) {
          var view = attachLocalOnly(withCanonicalType(shape), local);
          try {
            localStorage.setItem(PROFILE_LAST_KEY, JSON.stringify(view));
            if (view.currency) localStorage.setItem('kpi-currency', String(view.currency));
          } catch (_eCache) {}
          if (typeof opts.onReady === 'function') opts.onReady(view, res.profile);
          return { source: 'server', profile: view };
        }
        if (!profileHasContent(res.profile) && !plan.payload) {
          if (typeof opts.onEmpty === 'function') opts.onEmpty(res.profile);
          return { source: 'empty', profile: res.profile };
        }
        if (!plan.payload) return paint(plan.shape);
        return saveServerProfile(plan.payload).then(function (saved) {
          if (!saved || saved.ok !== true) {
            if (profileHasContent(res.profile)) return paint(serverToLocalShape(res.profile));
            if (typeof opts.onUnavailable === 'function') opts.onUnavailable(saved);
            return { source: 'unavailable' };
          }
          markMigrationDone(res.profile.userId);
          return paint(plan.shape);
        });
      });
    });
  }

  /**
   * Hydrate Profile Edit from the server. Stale local fields do not override
   * populated server values. An API failure leaves the form unconfirmed.
   */
  function hydrateEditForm(opts) {
    opts = opts || {};
    return isAuthenticatedSession().then(function (authed) {
      if (!authed) {
        if (typeof opts.onDone === 'function') opts.onDone({ source: 'unavailable', profile: null });
        return { source: 'unavailable', profile: null };
      }
      return loadServerProfile().then(function (res) {
        if (!res.ok || !res.profile) {
          if (typeof opts.onDone === 'function') opts.onDone({ source: 'unavailable', profile: null });
          return { source: 'unavailable', profile: null };
        }
        var local = readLocalProfile();
        var plan = emptyServerMigration(res.profile, local);
        function apply(shape) {
          var view = attachLocalOnly(withCanonicalType(shape), local);
          applyLocalShapeToForm(view);
          try {
            localStorage.setItem(PROFILE_LAST_KEY, JSON.stringify(view));
            if (view.currency) localStorage.setItem('kpi-currency', String(view.currency));
          } catch (_eStore) {}
          if (typeof opts.onServer === 'function') {
            try {
              opts.onServer(view, res.profile);
            } catch (_e1) {}
          }
          if (typeof opts.onDone === 'function') opts.onDone({ source: 'server', profile: view });
          return { source: 'server', profile: view };
        }
        if (!plan.payload) return apply(plan.shape);
        return saveServerProfile(plan.payload).then(function (saved) {
          if (saved && saved.ok === true) markMigrationDone(res.profile.userId);
          var shape = saved && saved.ok === true ? plan.shape : serverToLocalShape(res.profile.synced ? res.profile : {});
          return apply(shape);
        });
      });
    });
  }

  global.__KPI_PROFILE_SERVER = {
    saveServerProfile: saveServerProfile,
    loadServerProfile: loadServerProfile,
    hydrateEditForm: hydrateEditForm,
    hydrateDisplay: hydrateDisplay,
    commitProfileEdit: commitProfileEdit,
    requiredGaps: requiredGaps,
    mergePreferServer: mergePreferServer,
    readLocalProfile: readLocalProfile,
    applyLocalShapeToForm: applyLocalShapeToForm,
    normalizeLocale: normalizeLocale,
    SYNC_RESULT_KEY: SYNC_RESULT_KEY,
  };
})(typeof window !== 'undefined' ? window : this);

/**
 * Server profile sync for Profile Edit ↔ kpi_user_profiles.
 * localStorage remains the interactive store; server is best-effort for Admin.
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
   * Authenticated users only. Never rolls back localStorage (caller owns local save).
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
  }

  /**
   * Hydrate Profile Edit: local first, then overlay non-empty server fields when synced.
   */
  function hydrateEditForm(opts) {
    opts = opts || {};
    var local = readLocalProfile();
    applyLocalShapeToForm(local);
    if (typeof opts.onLocal === 'function') {
      try {
        opts.onLocal(local);
      } catch (_e0) {}
    }

    return isAuthenticatedSession().then(function (authed) {
      if (!authed) {
        if (typeof opts.onDone === 'function') opts.onDone({ source: 'local', profile: local });
        return { source: 'local', profile: local };
      }
      return loadServerProfile().then(function (res) {
        if (!res.ok || !res.profile || !res.profile.synced) {
          if (typeof opts.onDone === 'function') opts.onDone({ source: 'local', profile: local });
          return { source: 'local', profile: local };
        }
        var merged = mergePreferServer(local, res.profile);
        applyLocalShapeToForm(merged);
        try {
          var store = Object.assign({}, local, {
            businessName: merged.businessName || local.businessName || '',
            company: merged.company || merged.companyName || local.company || '',
            industry: merged.businessType || merged.industry || local.industry || '',
            businessType: merged.businessType || merged.industry || local.businessType || '',
            genre: merged.genre || local.genre || '',
            country: merged.country || local.country || '',
            state: merged.state || merged.stateRegion || local.state || '',
            city: merged.city || local.city || '',
            currency: merged.currency || local.currency || '',
          });
          localStorage.setItem(PROFILE_LAST_KEY, JSON.stringify(store));
          if (store.currency) localStorage.setItem('kpi-currency', store.currency);
        } catch (_eStore) {}
        if (typeof opts.onServer === 'function') {
          try {
            opts.onServer(merged, res.profile);
          } catch (_e1) {}
        }
        if (typeof opts.onDone === 'function') opts.onDone({ source: 'server', profile: merged });
        return { source: 'server', profile: merged };
      });
    });
  }

  global.__KPI_PROFILE_SERVER = {
    saveServerProfile: saveServerProfile,
    loadServerProfile: loadServerProfile,
    hydrateEditForm: hydrateEditForm,
    mergePreferServer: mergePreferServer,
    readLocalProfile: readLocalProfile,
    applyLocalShapeToForm: applyLocalShapeToForm,
    normalizeLocale: normalizeLocale,
    SYNC_RESULT_KEY: SYNC_RESULT_KEY,
  };
})(typeof window !== 'undefined' ? window : this);

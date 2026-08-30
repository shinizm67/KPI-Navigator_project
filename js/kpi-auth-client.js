/**
 * KPI Auth Client — Phase B1-T2 / B3
 * Session cookie (KPISESSID) against /api/v1/auth/*.php
 *
 * Override base:
 * - window.__KPI_AUTH_BASE = '/kpi-navigator/api/v1'
 * - meta[name="kpi-auth-api"] content="/kpi-navigator/api/v1"
 * - localStorage kpiNavigator.authBase
 */
(function (global) {
  'use strict';

  if (global.__KPI_AUTH && global.__KPI_AUTH.__ready) {
    return;
  }

  var REG_FLAG = 'kpiNavigator.registrationComplete';
  var AUTH_BASE_KEY = 'kpiNavigator.authBase';
  var TIER_KEY = 'kpiNavigator.subscriptionTier';
  /** Last KPI account bound to this browser's user-scoped localStorage. Marker: KPI-LS-USER-SCOPE-7 */
  var LAST_USER_KEY = 'kpiNavigator.lastKpiUserId';

  /** Keep across user switch (browser prefs / auth plumbing — not KPI body data). */
  var USER_SCOPE_KEEP = {
    'kpiNavigator.lastKpiUserId': true,
    'kpiNavigator.registrationComplete': true,
    'kpiNavigator.authBase': true,
    'kpiNavigator.storeSync': true,
    'kpiNavigator.subscriptionTier': true,
    'kpi-office-mode': true,
    'kpi-tutorial-advanced': true,
    'kpi-annual-focus-bar-expanded': true,
  };

  /** Exact keys that hold per-account KPI / profile payload. */
  var USER_SCOPE_CLEAR_EXACT = [
    'kpiNavigator.kpiYearStore',
    'kpiNavigator.annualDailyShared',
    'kpiNavigator.pastSalesShared',
    'kpiNavigator.annualNav',
    'kpiNavigator.plLineCatalog',
    'kpiNavigator.plTargetCostRate',
    'kpiNavigator.monthlyLast',
    'kpi-profile-last',
    'kpi-profile-edited',
    'kpi-currency',
    'kpi-auth-password',
  ];

  var USER_SCOPE_CLEAR_PREFIXES = [
    'kpi-pl-expenses-v1:',
    'kpi-pl-expense-adjustments-v1:',
  ];

  /** KpiYearStore not ready at bind — consumed on Annual/Monthly init (KPI-LS-USER-SCOPE-7-B). */
  var pendingUserScopeStoreReset = false;
  /** Skip migrateLegacy / reconcile on next KpiYearStore init after user switch. */
  var pendingUserScopeLegacySkip = false;

  function resolveAppRoot() {
    var path = global.location.pathname || '';
    var m = path.match(/^(.*?\/kpi-navigator)(?:\/|$)/);
    if (m) return m[1];
    return '';
  }

  function resolveAuthBase() {
    try {
      if (global.__KPI_AUTH_BASE) return String(global.__KPI_AUTH_BASE).replace(/\/$/, '');
    } catch (_e0) {}
    try {
      var meta = document.querySelector('meta[name="kpi-auth-api"]');
      if (meta && meta.content) return String(meta.content).replace(/\/$/, '');
    } catch (_e1) {}
    try {
      var stored = localStorage.getItem(AUTH_BASE_KEY);
      if (stored) return String(stored).replace(/\/$/, '');
    } catch (_e2) {}
    return resolveAppRoot() + '/api/v1';
  }

  function setRegistrationComplete() {
    try {
      localStorage.setItem(REG_FLAG, '1');
    } catch (_e) {}
  }

  function readLastKpiUserId() {
    try {
      var v = localStorage.getItem(LAST_USER_KEY);
      return v ? String(v) : '';
    } catch (_e) {
      return '';
    }
  }

  function writeLastKpiUserId(userId) {
    try {
      localStorage.setItem(LAST_USER_KEY, String(userId));
    } catch (_e) {}
  }

  function shouldClearKeyForUserScope(key) {
    if (!key || USER_SCOPE_KEEP[key]) return false;
    if (USER_SCOPE_CLEAR_EXACT.indexOf(key) >= 0) return true;
    for (var i = 0; i < USER_SCOPE_CLEAR_PREFIXES.length; i++) {
      if (String(key).indexOf(USER_SCOPE_CLEAR_PREFIXES[i]) === 0) return true;
    }
    /* Other kpiNavigator.* body keys (not in keep list) */
    if (String(key).indexOf('kpiNavigator.') === 0) return true;
    return false;
  }

  /** Clear in-memory KpiYearStore when present (KPI-LS-USER-SCOPE-7-B). */
  function resetKpiYearStoreMemory() {
    try {
      if (global.KpiYearStore && typeof global.KpiYearStore.resetForUserScope === 'function') {
        global.KpiYearStore.resetForUserScope();
      } else {
        pendingUserScopeStoreReset = true;
      }
    } catch (_eReset) {}
  }

  /**
   * @returns {boolean} true when bind ran before KpiYearStore existed (caller should resetForUserScope).
   */
  function consumePendingUserScopeReset() {
    var pending = pendingUserScopeStoreReset;
    pendingUserScopeStoreReset = false;
    return pending;
  }

  /**
   * @returns {boolean} true when userId switched — caller should skip legacy timeline merge on init.
   */
  function consumeUserScopeLegacySkip() {
    var skip = pendingUserScopeLegacySkip;
    pendingUserScopeLegacySkip = false;
    return skip;
  }

  /**
   * Drop per-account KPI localStorage without localStorage.clear().
   * Suppresses gateway PUT hooks when available so stale data is not uploaded.
   */
  function clearUserScopedLocalData() {
    var gw = global.__KPI_DATA_GATEWAY;
    var began = false;
    try {
      if (gw && typeof gw.beginLocalUserScopeReset === 'function') {
        gw.beginLocalUserScopeReset();
        began = true;
      }
    } catch (_eBegin) {}
    try {
      var i;
      for (i = 0; i < USER_SCOPE_CLEAR_EXACT.length; i++) {
        try {
          localStorage.removeItem(USER_SCOPE_CLEAR_EXACT[i]);
        } catch (_eRm) {}
      }
      var toRemove = [];
      try {
        for (i = 0; i < localStorage.length; i++) {
          var k = localStorage.key(i);
          if (shouldClearKeyForUserScope(k)) toRemove.push(k);
        }
      } catch (_eScan) {}
      for (i = 0; i < toRemove.length; i++) {
        try {
          localStorage.removeItem(toRemove[i]);
        } catch (_eRm2) {}
      }
      resetKpiYearStoreMemory();
    } finally {
      if (began) {
        try {
          if (gw && typeof gw.endLocalUserScopeReset === 'function') {
            gw.endLocalUserScopeReset();
          }
        } catch (_eEnd) {}
      }
    }
  }

  /**
   * Bind this browser's KPI localStorage to userId.
   * Different / unknown previous user → clear user-scoped keys before hydrate/PUT.
   * Same userId → keep LS.
   * @returns {{ switched: boolean, cleared: boolean, previousUserId: string, userId: string }}
   */
  function bindLocalUserId(userId) {
    var uid = userId != null ? String(userId) : '';
    if (!uid) {
      return { switched: false, cleared: false, previousUserId: readLastKpiUserId(), userId: '' };
    }
    var prev = readLastKpiUserId();
    var switched = !prev || prev !== uid;
    if (switched) {
      pendingUserScopeLegacySkip = true;
      clearUserScopedLocalData();
      writeLastKpiUserId(uid);
      try {
        global.dispatchEvent(
          new CustomEvent('kpi:localUserScopeChanged', {
            detail: { previousUserId: prev || null, userId: uid, cleared: true },
          })
        );
      } catch (_eEv) {}
      return { switched: true, cleared: true, previousUserId: prev, userId: uid };
    }
    return { switched: false, cleared: false, previousUserId: prev, userId: uid };
  }

  function normalizePlan(plan) {
    return String(plan || '').toLowerCase() === 'basic' ? 'basic' : 'pro';
  }

  /** Server plan → localStorage/sessionStorage (display gate). Dispatches kpi:planChanged. */
  function applyServerPlan(plan) {
    var p = normalizePlan(plan);
    try {
      localStorage.setItem(TIER_KEY, p);
    } catch (_e0) {}
    try {
      sessionStorage.setItem(TIER_KEY, p);
    } catch (_e1) {}
    try {
      global.dispatchEvent(new CustomEvent('kpi:planChanged', { detail: { plan: p, source: 'server' } }));
    } catch (_e2) {}
    return p;
  }

  function request(method, path, body, extraHeaders) {
    var url = resolveAuthBase() + path;
    var opts = {
      method: method,
      credentials: 'include',
      headers: {},
    };
    if (extraHeaders && typeof extraHeaders === 'object') {
      Object.keys(extraHeaders).forEach(function (k) {
        opts.headers[k] = extraHeaders[k];
      });
    }
    if (body != null) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    return fetch(url, opts).then(function (res) {
      return res.json().catch(function () {
        return { ok: false, error: 'invalid_response' };
      }).then(function (data) {
        return { status: res.status, data: data || { ok: false } };
      });
    });
  }

  function register(email, password) {
    return request('POST', '/auth/register.php', {
      email: email,
      password: password,
    }).then(function (r) {
      if (r.status === 201 && r.data && r.data.ok) {
        if (r.data.userId) bindLocalUserId(r.data.userId);
        setRegistrationComplete();
        if (r.data.plan) applyServerPlan(r.data.plan);
      }
      return r;
    });
  }

  function login(email, password) {
    return request('POST', '/auth/login.php', {
      email: email,
      password: password,
    }).then(function (r) {
      if (r.status === 200 && r.data && r.data.ok) {
        /* Clear other account's LS before storeSync/hydrate can PUT it. */
        if (r.data.userId) bindLocalUserId(r.data.userId);
        setRegistrationComplete();
        if (r.data.plan) applyServerPlan(r.data.plan);
      }
      return r;
    });
  }

  function logout() {
    return request('POST', '/auth/logout.php', null);
  }

  function me() {
    return request('GET', '/auth/me.php', null).then(function (r) {
      if (r.status === 200 && r.data && r.data.ok) {
        if (r.data.userId) bindLocalUserId(r.data.userId);
        if (r.data.plan) applyServerPlan(r.data.plan);
      }
      return r;
    });
  }

  function setPlan(plan, opts) {
    opts = opts || {};
    var body = { plan: normalizePlan(plan) };
    if (opts.email) body.email = opts.email;
    if (opts.adminToken) body.adminToken = opts.adminToken;
    var headers = {};
    if (opts.adminToken) headers['X-KPI-Plan-Admin-Token'] = opts.adminToken;
    return request('POST', '/auth/set-plan.php', body, headers).then(function (r) {
      if (r.status === 200 && r.data && r.data.ok && r.data.plan) {
        applyServerPlan(r.data.plan);
      }
      return r;
    });
  }

  /** Shared in-flight me() so Insight gate can wait for server plan. */
  var planSyncPromise = null;

  function syncPlanFromServer() {
    if (!planSyncPromise) {
      planSyncPromise = me().then(
        function (r) {
          return r;
        },
        function (err) {
          planSyncPromise = null;
          throw err;
        }
      );
    }
    return planSyncPromise;
  }

  /**
   * Resolve after /auth/me.php and bindLocalUserId for the current session user.
   * Annual KpiYearStore.init must run only after this (KPI-LS-USER-SCOPE-7-B).
   */
  function ensureUserScopeBound() {
    return syncPlanFromServer();
  }

  function readStoredTier() {
    try {
      return sessionStorage.getItem(TIER_KEY) || localStorage.getItem(TIER_KEY) || '';
    } catch (_e) {
      return '';
    }
  }

  function isBasicPlan() {
    return String(readStoredTier() || '').toLowerCase() === 'basic';
  }

  /** Locale-aware Change Plan URL (absolute under /kpi-navigator when possible). */
  function resolveChangePlanHref() {
    var root = resolveAppRoot();
    var path = String(global.location.pathname || '');
    if (root) {
      if (path.indexOf('/zh-tw/') >= 0) return root + '/zh-tw/setting/change_plan.html';
      if (path.indexOf('/en/') >= 0) return root + '/en/setting/change_plan.html';
      return root + '/setting/change_plan.html';
    }
    if (
      path.indexOf('/app/booking') >= 0 ||
      path.indexOf('/app/profit') >= 0 ||
      path.indexOf('/app/monthly') >= 0 ||
      path.indexOf('/app/annual') >= 0
    ) {
      if (path.indexOf('/en/') >= 0 || path.indexOf('/zh-tw/') >= 0) return '../../../setting/change_plan.html';
      return '../../setting/change_plan.html';
    }
    return '../setting/change_plan.html';
  }

  /** Locale-aware login page URL after logout. */
  function resolveLoginHref() {
    var root = resolveAppRoot();
    var path = String(global.location.pathname || '');
    if (root) {
      if (path.indexOf('/zh-tw/') >= 0) return root + '/zh-tw/login/index.html';
      if (path.indexOf('/en/') >= 0) return root + '/en/login/index.html';
      return root + '/login/index.html';
    }
    if (
      path.indexOf('/app/booking') >= 0 ||
      path.indexOf('/app/profit') >= 0 ||
      path.indexOf('/app/monthly') >= 0 ||
      path.indexOf('/app/annual') >= 0 ||
      path.indexOf('/en/') >= 0 ||
      path.indexOf('/zh-tw/') >= 0
    ) {
      return '../../login/index.html';
    }
    return '../login/index.html';
  }

  /** Settings panel logout — session only; does not clear KPI localStorage. */
  function bindAccountSettingsLogout(root) {
    var scope = root && root.querySelector ? root : document;
    var el = scope.getElementById ? scope.getElementById('account-settings-logout') : null;
    if (!el || el.getAttribute('data-kpi-logout-bound') === '1') return;
    el.setAttribute('data-kpi-logout-bound', '1');
    el.addEventListener('click', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      function goLogin() {
        try {
          global.location.href = resolveLoginHref();
        } catch (_eGo) {}
      }
      Promise.resolve(logout()).then(goLogin).catch(goLogin);
    });
  }

  /**
   * Capture-phase Pro gate for links with data-href-basic / data-href-pro.
   * Waits for /auth/me.php so stale localStorage "basic" cannot send Pro users to Change Plan.
   */
  function bindProHrefGate(el) {
    if (!el || el.getAttribute('data-kpi-plan-gate') === '1') return;
    var hrefBasic = el.getAttribute('data-href-basic') || '';
    if (!hrefBasic) return;
    el.setAttribute('data-kpi-plan-gate', '1');
    el.addEventListener(
      'click',
      function (ev) {
        var hrefPro = el.getAttribute('data-href-pro') || el.getAttribute('href') || '';
        ev.preventDefault();
        ev.stopImmediatePropagation();
        function go() {
          var target = isBasicPlan() ? hrefBasic : hrefPro;
          if (target) window.location.href = target;
        }
        syncPlanFromServer().then(go).catch(go);
      },
      true
    );
  }

  /**
   * Insight (#global-nav-index-btn) + Booking (#header-booking-btn) + [data-kpi-pro-gate].
   */
  function bindInsightNavGate(root) {
    var doc = root && root.querySelector ? root : document;
    bindProHrefGate(doc.getElementById ? doc.getElementById('global-nav-index-btn') : null);
    bindProHrefGate(doc.getElementById ? doc.getElementById('header-booking-btn') : null);
    var nodes = doc.querySelectorAll ? doc.querySelectorAll('[data-kpi-pro-gate]') : [];
    for (var i = 0; i < nodes.length; i++) {
      bindProHrefGate(nodes[i]);
    }
  }

  /**
   * Page entry guard (Booking / similar Pro-only surfaces).
   * Syncs plan from server then redirects Basic → Change Plan.
   */
  function guardProPage(changePlanHref) {
    var href = changePlanHref || resolveChangePlanHref();
    function bounceIfBasic() {
      if (!isBasicPlan()) return false;
      try {
        global.location.replace(href);
      } catch (_e) {
        global.location.href = href;
      }
      return true;
    }
    if (bounceIfBasic()) {
      return Promise.resolve({ redirected: true });
    }
    return syncPlanFromServer()
      .then(function () {
        return { redirected: bounceIfBasic() };
      })
      .catch(function () {
        return { redirected: bounceIfBasic() };
      });
  }

  function errorMessage(lang, status, data) {
    var code = (data && data.error) || '';
    var isJa = lang === 'ja';
    var isZh = lang === 'zh' || lang === 'zh-tw';
    if (code === 'email_taken') {
      if (isJa) return 'このメールアドレスは既に登録されています。';
      if (isZh) return '此電子郵件已被註冊。';
      return 'This email is already registered.';
    }
    if (code === 'invalid_credentials' || status === 401) {
      if (isJa) return 'メールアドレスまたはパスワードが正しくありません。';
      if (isZh) return '電子郵件或密碼不正確。';
      return 'Email or password is incorrect.';
    }
    if (code === 'invalid_email') {
      if (isJa) return 'メールアドレスの形式が正しくありません。';
      if (isZh) return '電子郵件格式不正確。';
      return 'Invalid email address.';
    }
    if (code === 'password_too_short') {
      if (isJa) return 'パスワードは8文字以上にしてください。';
      if (isZh) return '密碼至少需 8 個字元。';
      return 'Password must be at least 8 characters.';
    }
    if (code === 'entitlement_required' || status === 403) {
      if (isJa) return 'この機能には Pro プランが必要です。';
      if (isZh) return '此功能需要 Pro 方案。';
      return 'This feature requires the Pro plan.';
    }
    if (isJa) return '通信エラーが発生しました。しばらくしてから再試行してください。';
    if (isZh) return '發生通訊錯誤，請稍後再試。';
    return 'A network error occurred. Please try again.';
  }

  global.__KPI_AUTH = {
    __ready: true,
    resolveAuthBase: resolveAuthBase,
    resolveAppRoot: resolveAppRoot,
    register: register,
    login: login,
    logout: logout,
    me: me,
    setPlan: setPlan,
    applyServerPlan: applyServerPlan,
    syncPlanFromServer: syncPlanFromServer,
    isBasicPlan: isBasicPlan,
    resolveChangePlanHref: resolveChangePlanHref,
    resolveLoginHref: resolveLoginHref,
    bindAccountSettingsLogout: bindAccountSettingsLogout,
    bindProHrefGate: bindProHrefGate,
    bindInsightNavGate: bindInsightNavGate,
    guardProPage: guardProPage,
    setRegistrationComplete: setRegistrationComplete,
    bindLocalUserId: bindLocalUserId,
    clearUserScopedLocalData: clearUserScopedLocalData,
    ensureUserScopeBound: ensureUserScopeBound,
    consumePendingUserScopeReset: consumePendingUserScopeReset,
    consumeUserScopeLegacySkip: consumeUserScopeLegacySkip,
    readLastKpiUserId: readLastKpiUserId,
    errorMessage: errorMessage,
  };

  // App pages: refresh display gate from server session as soon as the client loads.
  try {
    syncPlanFromServer().catch(function () {});
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        bindInsightNavGate(document);
      });
    } else {
      bindInsightNavGate(document);
    }
  } catch (_boot) {}
})(typeof window !== 'undefined' ? window : this);

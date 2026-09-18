/**
 * Profile / change-email pages: reflect session userId / email from __KPI_AUTH
 * (GET /auth/me.php). Display only — does not read or write localStorage.
 *
 * Unauthorized / me non-200: clear identity DOM and redirect to login.
 * Never fall back to Founder or other hardcoded identity.
 */
(function () {
  'use strict';

  var global = typeof window !== 'undefined' ? window : this;
  var PLACEHOLDER = '—';

  var VIEW_IDS = { userId: 'fixed-user-id', email: 'fixed-email' };
  var EDIT_IDS = { userId: 'profile-user-id', email: 'profile-email-display' };
  var CHANGE_EMAIL_IDS = { userId: null, email: 'current-email' };

  function resolveIds() {
    var script = document.currentScript;
    if (!script) {
      var scripts = document.getElementsByTagName('script');
      for (var i = scripts.length - 1; i >= 0; i--) {
        if (scripts[i].src && scripts[i].src.indexOf('kpi-profile-session-account.js') >= 0) {
          script = scripts[i];
          break;
        }
      }
    }
    var mode = script && script.getAttribute('data-kpi-profile-account-mode');
    if (mode === 'edit') return EDIT_IDS;
    if (mode === 'change-email') return CHANGE_EMAIL_IDS;
    return VIEW_IDS;
  }

  function setText(id, value) {
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    var v = value != null ? String(value).trim() : '';
    el.textContent = v || PLACEHOLDER;
  }

  function clearIdentity(ids) {
    if (!ids) return;
    setText(ids.userId, '');
    setText(ids.email, '');
  }

  function redirectLogin() {
    var auth = global.__KPI_AUTH;
    var href =
      auth && typeof auth.resolveLoginHref === 'function'
        ? auth.resolveLoginHref()
        : '../login/index.html';
    try {
      global.location.replace(href);
    } catch (_e) {
      try {
        global.location.href = href;
      } catch (_e2) {}
    }
  }

  function isAuthorized(r) {
    return !!(r && r.status === 200 && r.data && r.data.ok);
  }

  function applySessionAccount(r, ids) {
    if (!isAuthorized(r)) {
      clearIdentity(ids);
      redirectLogin();
      return;
    }
    setText(ids.userId, r.data.userId);
    setText(ids.email, r.data.email);
  }

  function boot() {
    var ids = resolveIds();
    // Clear before me resolves so HTML / LS placeholders never linger as identity.
    clearIdentity(ids);

    var auth = global.__KPI_AUTH;
    if (!auth) {
      redirectLogin();
      return;
    }
    var sync =
      typeof auth.syncPlanFromServer === 'function'
        ? auth.syncPlanFromServer()
        : typeof auth.me === 'function'
          ? auth.me()
          : null;
    if (!sync || typeof sync.then !== 'function') {
      clearIdentity(ids);
      redirectLogin();
      return;
    }
    sync
      .then(function (r) {
        applySessionAccount(r, ids);
      })
      .catch(function () {
        clearIdentity(ids);
        redirectLogin();
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

/**
 * Profile pages: reflect session userId / email from __KPI_AUTH (GET /auth/me.php).
 * Display only — does not read or write localStorage.
 */
(function () {
  'use strict';

  var global = typeof window !== 'undefined' ? window : this;

  var VIEW_IDS = { userId: 'fixed-user-id', email: 'fixed-email' };
  var EDIT_IDS = { userId: 'profile-user-id', email: 'profile-email-display' };

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
    return mode === 'edit' ? EDIT_IDS : VIEW_IDS;
  }

  function setText(id, value) {
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    var v = value != null ? String(value).trim() : '';
    if (v) el.textContent = v;
  }

  function applySessionAccount(r, ids) {
    if (!r || r.status !== 200 || !r.data || !r.data.ok) return;
    setText(ids.userId, r.data.userId);
    setText(ids.email, r.data.email);
  }

  function boot() {
    var auth = global.__KPI_AUTH;
    if (!auth) return;
    var ids = resolveIds();
    var sync =
      typeof auth.syncPlanFromServer === 'function'
        ? auth.syncPlanFromServer()
        : typeof auth.me === 'function'
          ? auth.me()
          : null;
    if (!sync || typeof sync.then !== 'function') return;
    sync
      .then(function (r) {
        applySessionAccount(r, ids);
      })
      .catch(function () {});
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

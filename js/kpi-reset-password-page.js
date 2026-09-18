/**
 * Reset Password page (JA / EN / zh-tw). Token from ?token=.
 */
(function () {
  'use strict';

  var form = document.getElementById('reset-form');
  var pwEl = document.getElementById('new-password');
  var confirmEl = document.getElementById('confirm-password');
  var btn = document.getElementById('btn-reset');
  var errEl = document.getElementById('reset-error');
  var okEl = document.getElementById('reset-success');
  var okMsgEl = document.getElementById('reset-success-msg');
  var loginLink = document.getElementById('reset-login-link');
  if (!form || !pwEl || !confirmEl || !btn) return;
  if (!window.__KPI_AUTH) {
    console.warn('[KPI Auth] kpi-auth-client.js not loaded');
    return;
  }

  var langAttr = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var lang = langAttr.indexOf('zh') === 0 ? 'zh' : langAttr.split('-')[0];
  var REDIRECT_MS = 2500;

  function tokenFromQuery() {
    try {
      var q = new URLSearchParams(window.location.search || '');
      return (q.get('token') || '').trim();
    } catch (_e) {
      return '';
    }
  }

  var token = tokenFromQuery();

  function showErr(text) {
    if (errEl) {
      errEl.hidden = !text;
      errEl.textContent = text || '';
    }
    if (okEl) okEl.hidden = true;
  }

  /**
   * Prefer app-root absolute login URL (stable vs trailing-slash / relative resolution).
   * JP:  /kpi-navigator/login/index.html
   * EN:  /kpi-navigator/en/login/index.html
   * ZH:  /kpi-navigator/zh-tw/login/index.html
   */
  function loginHref() {
    try {
      if (typeof window.__KPI_AUTH.resolveLoginHref === 'function') {
        var resolved = window.__KPI_AUTH.resolveLoginHref();
        if (resolved) return resolved;
      }
    } catch (_eRes) {}
    try {
      if (loginLink && loginLink.href) return loginLink.href;
    } catch (_eAbs) {}
    var path = String(window.location.pathname || '');
    var rootMatch = path.match(/^(.*?\/kpi-navigator)(?:\/|$)/);
    var root = rootMatch ? rootMatch[1] : '';
    if (root) {
      if (path.indexOf('/zh-tw/') >= 0) return root + '/zh-tw/login/index.html';
      if (path.indexOf('/en/') >= 0) return root + '/en/login/index.html';
      return root + '/login/index.html';
    }
    return '../login/index.html';
  }

  function goLogin(href) {
    var target = href || loginHref();
    try {
      window.location.assign(target);
      return;
    } catch (_eAssign) {}
    try {
      window.location.href = target;
    } catch (_eHref) {}
  }

  function showSuccess() {
    var href = loginHref();
    // Never assign text onto the success container — that would wipe the static Login <a href> fallback.
    if (okMsgEl) {
      okMsgEl.textContent = window.__KPI_AUTH.resetPasswordSuccessMessage(lang);
    }
    if (loginLink) {
      try {
        loginLink.setAttribute('href', href);
      } catch (_eLink) {}
    }
    form.hidden = true;
    if (okEl) okEl.hidden = false;
    window.setTimeout(function () {
      goLogin(href);
    }, REDIRECT_MS);
  }

  function checkActive() {
    if (btn.getAttribute('data-busy') === '1') return;
    var ok = token.length >= 32 && pwEl.value.length >= 8 && confirmEl.value.length >= 8;
    btn.disabled = !ok;
  }

  if (!token) {
    showErr(window.__KPI_AUTH.errorMessage(lang, 400, { error: 'invalid_or_expired_token' }));
    btn.disabled = true;
  }

  pwEl.addEventListener('input', checkActive);
  confirmEl.addEventListener('input', checkActive);
  checkActive();

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!token) {
      showErr(window.__KPI_AUTH.errorMessage(lang, 400, { error: 'invalid_or_expired_token' }));
      return;
    }
    if (pwEl.value.length < 8) {
      showErr(window.__KPI_AUTH.errorMessage(lang, 400, { error: 'password_too_short' }));
      return;
    }
    if (pwEl.value !== confirmEl.value) {
      showErr(window.__KPI_AUTH.errorMessage(lang, 400, { error: 'password_mismatch' }));
      return;
    }
    btn.disabled = true;
    btn.setAttribute('data-busy', '1');
    showErr('');
    window.__KPI_AUTH
      .resetPassword(token, pwEl.value)
      .then(function (r) {
        btn.removeAttribute('data-busy');
        if (r.status === 200 && r.data && r.data.ok) {
          showSuccess();
          return;
        }
        showErr(window.__KPI_AUTH.errorMessage(lang, r.status, r.data));
        checkActive();
      })
      .catch(function () {
        btn.removeAttribute('data-busy');
        showErr(window.__KPI_AUTH.errorMessage(lang, 0, { error: 'network' }));
        checkActive();
      });
  });
})();

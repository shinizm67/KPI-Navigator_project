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
  if (!form || !pwEl || !confirmEl || !btn) return;
  if (!window.__KPI_AUTH) {
    console.warn('[KPI Auth] kpi-auth-client.js not loaded');
    return;
  }

  var langAttr = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var lang = langAttr.indexOf('zh') === 0 ? 'zh' : langAttr.split('-')[0];

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
          if (okEl) {
            okEl.hidden = false;
            okEl.textContent = window.__KPI_AUTH.resetPasswordSuccessMessage(lang);
          }
          form.hidden = true;
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

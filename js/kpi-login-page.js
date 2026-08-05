/**
 * Login page submit wiring (JA / EN / zh-tw).
 * Requires kpi-auth-client.js loaded first.
 */
(function () {
  'use strict';

  var form = document.getElementById('login-form');
  var userId = document.getElementById('user-id');
  var password = document.getElementById('password');
  var btnLogin = document.getElementById('btn-login');
  if (!form || !userId || !password || !btnLogin) return;
  if (!window.__KPI_AUTH) {
    console.warn('[KPI Auth] kpi-auth-client.js not loaded');
    return;
  }

  var langAttr = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var lang = langAttr.indexOf('zh') === 0 ? 'zh' : langAttr.split('-')[0];

  function annualHref() {
    // login/ → ../app/annual/ ; en/login|zh-tw/login → ../app/annual/
    return '../app/annual/index.html';
  }

  function busy(on) {
    btnLogin.disabled = !!on;
    if (on) {
      btnLogin.setAttribute('data-busy', '1');
    } else {
      btnLogin.removeAttribute('data-busy');
      checkActive();
    }
  }

  function checkActive() {
    if (btnLogin.getAttribute('data-busy') === '1') return;
    var idOk = userId.value.trim().length > 0;
    var pwOk = password.value.length >= 8;
    btnLogin.disabled = !(idOk && pwOk);
  }

  userId.addEventListener('input', checkActive);
  userId.addEventListener('change', checkActive);
  password.addEventListener('input', checkActive);
  password.addEventListener('change', checkActive);
  checkActive();

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = userId.value.trim();
    var pw = password.value;
    if (!email || pw.length < 8) return;

    busy(true);
    window.__KPI_AUTH
      .login(email, pw)
      .then(function (r) {
        if (r.status === 200 && r.data && r.data.ok) {
          window.location.href = annualHref();
          return;
        }
        alert(window.__KPI_AUTH.errorMessage(lang, r.status, r.data));
        busy(false);
      })
      .catch(function () {
        alert(window.__KPI_AUTH.errorMessage(lang, 0, { error: 'network' }));
        busy(false);
      });
  });
})();

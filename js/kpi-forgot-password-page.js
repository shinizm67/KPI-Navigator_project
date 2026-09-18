/**
 * Forgot Password page (JA / EN / zh-tw).
 * Always shows generic success — never reveals email existence.
 */
(function () {
  'use strict';

  var form = document.getElementById('forgot-form');
  var emailEl = document.getElementById('forgot-email');
  var btn = document.getElementById('btn-forgot');
  var msg = document.getElementById('forgot-message');
  if (!form || !emailEl || !btn) return;
  if (!window.__KPI_AUTH) {
    console.warn('[KPI Auth] kpi-auth-client.js not loaded');
    return;
  }

  var langAttr = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var lang = langAttr.indexOf('zh') === 0 ? 'zh-tw' : langAttr.split('-')[0];
  if (lang !== 'ja' && lang !== 'zh-tw') lang = 'en';

  function checkActive() {
    if (btn.getAttribute('data-busy') === '1') return;
    btn.disabled = emailEl.value.trim().length < 3;
  }

  emailEl.addEventListener('input', checkActive);
  emailEl.addEventListener('change', checkActive);
  checkActive();

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = emailEl.value.trim();
    if (!email) return;
    btn.disabled = true;
    btn.setAttribute('data-busy', '1');
    if (msg) {
      msg.hidden = true;
      msg.textContent = '';
    }
    window.__KPI_AUTH
      .forgotPassword(email, lang)
      .then(function (r) {
        if (msg) {
          msg.hidden = false;
          msg.textContent = window.__KPI_AUTH.forgotPasswordGenericMessage(lang);
        }
        btn.removeAttribute('data-busy');
        checkActive();
        return r;
      })
      .catch(function () {
        if (msg) {
          msg.hidden = false;
          msg.textContent = window.__KPI_AUTH.forgotPasswordGenericMessage(lang);
        }
        btn.removeAttribute('data-busy');
        checkActive();
      });
  });
})();

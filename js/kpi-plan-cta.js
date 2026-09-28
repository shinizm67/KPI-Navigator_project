/**
 * Plan page Basic CTA: points to Registration only while the server reports registrationEnabled === true.
 * Default markup (Early Access mailto) stays on any failure, so a closed or unreachable API never
 * sends visitors to a stopped Registration page. Pro CTA is not touched.
 */
(function () {
  'use strict';
  var script = document.currentScript;
  var a = document.getElementById('plan-basic-cta');
  if (!script || !a || typeof window.fetch !== 'function') return;
  var href = a.getAttribute('data-register-href');
  var label = a.getAttribute('data-register-label');
  if (!href || !label) return;
  var root = String(script.src).replace(/js\/kpi-plan-cta\.js(?:\?.*)?$/, '');
  window
    .fetch(root + 'api/v1/auth/registration-status.php', { credentials: 'omit', cache: 'no-store' })
    .then(function (r) {
      return r.ok ? r.json() : null;
    })
    .then(function (d) {
      /* Same open condition as the Registration page, so the CTA never leads to a closed form. */
      if (!d || d.registrationEnabled !== true || typeof d.termsVersion !== 'string' ||
          typeof d.privacyVersion !== 'string' || typeof d.formToken !== 'string' || !d.formToken) return;
      a.setAttribute('href', href);
      a.textContent = label;
    })
    .catch(function () {});
})();

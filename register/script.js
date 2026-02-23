/**
 * KPI Navigator - Global script
 * Si-Fi Registration page: language selector & form handling
 */

(function () {
  'use strict';

  var STORAGE_KEY_OFFICE = 'kpi-office-mode';
  var STORAGE_KEY_PLAN = 'kpi-registration-plan';
  var isJa = (document.documentElement.getAttribute('lang') || '').toLowerCase().split('-')[0] === 'ja';

  /* プラン表示: URL の ?plan=basic / ?plan=pro。言語切替で同じプランを維持するため sessionStorage に保存 */
  var planTitle = document.getElementById('plan-title');
  var planPrice = document.getElementById('plan-price');
  var planCancel = document.getElementById('plan-cancel');
  if (planTitle && planPrice) {
    var params = new URLSearchParams(window.location.search);
    var planFromUrl = params.get('plan');
    var plan = (planFromUrl || sessionStorage.getItem(STORAGE_KEY_PLAN) || 'basic').toLowerCase();
    if (planFromUrl) {
      sessionStorage.setItem(STORAGE_KEY_PLAN, plan);
    }
    if (plan === 'pro') {
      planTitle.textContent = 'KPI Navigator Pro';
      planPrice.textContent = isJa ? '¥3,000/月' : '$29 / Month';
    } else {
      planTitle.textContent = 'KPI Navigator Basic';
      planPrice.textContent = isJa ? '¥500/月' : '$5 / Month';
    }
    if (planCancel) {
      planCancel.textContent = isJa ? 'いつでも解約可能' : 'Cancel anytime';
    }
  }

  /* Forge Lab 風カスタム言語選択（画面右下） */
  const langWrap = document.getElementById('lang-select-wrap');
  const langBtn = document.getElementById('lang-select-btn');
  const langDropdown = document.getElementById('lang-select-dropdown');
  const langOptions = document.querySelectorAll('.lang-option');

  if (langBtn && langDropdown) {
    langBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      const isOpen = langDropdown.hidden === false;
      langDropdown.hidden = isOpen;
      langBtn.setAttribute('aria-expanded', !isOpen);
    });

    document.addEventListener('click', function () {
      langDropdown.hidden = true;
      langBtn.setAttribute('aria-expanded', 'false');
    });

    var wrap = document.getElementById('lang-select-wrap');
    var urlEn = wrap && wrap.getAttribute('data-url-en');
    var urlJa = wrap && wrap.getAttribute('data-url-ja');
    var bodyElLang = document.getElementById('body-el');

    langOptions.forEach(function (opt) {
      opt.addEventListener('click', function (e) {
        e.stopPropagation();
        if (bodyElLang && bodyElLang.classList.contains('office-mode')) {
          sessionStorage.setItem(STORAGE_KEY_OFFICE, '1');
        }
        var params = new URLSearchParams(window.location.search);
        var plan = (params.get('plan') || sessionStorage.getItem(STORAGE_KEY_PLAN) || 'basic').toLowerCase();
        var lang = this.getAttribute('data-lang');
        var baseUrl = (lang === 'ja' && urlJa) ? urlJa : (lang === 'en' && urlEn) ? urlEn : null;
        if (baseUrl) {
          var sep = baseUrl.indexOf('?') >= 0 ? '&' : '?';
          window.location.href = baseUrl + sep + 'plan=' + plan;
        }
      });
    });
  }

  /* ページ言語: en ならアラート等を英語、ja なら日本語で表示 */
  var pageLang = (document.documentElement.getAttribute('lang') || 'en').toLowerCase().split('-')[0];

  var messages = {
    en: {
      required: 'Please enter this field.',
      passwordLength: 'Password must be at least 8 characters, including letters, numbers, and symbols.'
    },
    ja: {
      required: 'このフィールドを入力してください。',
      passwordLength: 'パスワードは8文字以上で、英数字と記号を含めてください。'
    }
  };
  var msg = messages[pageLang] || messages.en;

  /* Sci-Fi Mode ←→ Office Mode 切り替え（body クラス・JP/EN 共通） */
  var bodyEl = document.getElementById('body-el');
  var btnModeToggle = document.getElementById('btn-mode-toggle');
  var btnModeText = document.getElementById('btn-mode-text');

  function updateModeButton() {
    if (!btnModeText || !btnModeToggle) return;
    var isOffice = bodyEl && bodyEl.classList.contains('office-mode');
    if (isJa) {
      btnModeText.textContent = isOffice ? 'SCI-FI MODE' : 'オフィスモード';
      btnModeToggle.setAttribute('aria-label', isOffice ? 'Sci-Fiモードに切り替え' : 'オフィスモードに切り替え');
    } else {
      btnModeText.textContent = isOffice ? 'SCI-FI MODE' : 'OFFICE MODE';
      btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');
    }
  }

  if (bodyEl && btnModeToggle) {
    if (sessionStorage.getItem(STORAGE_KEY_OFFICE) === '1') {
      bodyEl.classList.add('office-mode');
    }
    btnModeToggle.addEventListener('click', function (e) {
      e.preventDefault();
      bodyEl.classList.toggle('office-mode');
      if (bodyEl.classList.contains('office-mode')) {
        sessionStorage.setItem(STORAGE_KEY_OFFICE, '1');
      } else {
        sessionStorage.removeItem(STORAGE_KEY_OFFICE);
      }
      updateModeButton();
    });
    updateModeButton();
  }

  /* パスワード条件: 8文字以上・英字・数字・記号をそれぞれ1文字以上 */
  function isPasswordValid(pw) {
    if (!pw || pw.length < 8) return false;
    var hasLetter = /[a-zA-Z]/.test(pw);
    var hasNumber = /[0-9]/.test(pw);
    var hasSymbol = /[^a-zA-Z0-9]/.test(pw);
    return hasLetter && hasNumber && hasSymbol;
  }

  /* Register ボタン: 全入力＋パスワード条件＋Confirm 一致＋同意チェックで有効化 */
  var agreeTerms = document.getElementById('agree-terms') || document.getElementById('agree-terms-jp');
  var btnRegister = document.getElementById('btn-register');
  var nameInput = document.getElementById('name');
  var companyInput = document.getElementById('company');
  var emailInput = document.getElementById('email');
  var passwordInput = document.getElementById('password');
  var passwordConfirmInput = document.getElementById('password-confirm');

  function setRegisterButtonState() {
    if (!btnRegister) return;
    var nameOk = nameInput && nameInput.value.trim().length > 0;
    var companyOk = companyInput && companyInput.value.trim().length > 0;
    var emailOk = emailInput && emailInput.value.trim().length > 0;
    var pw = passwordInput ? passwordInput.value : '';
    var pwConfirm = passwordConfirmInput ? passwordConfirmInput.value : '';
    var passwordOk = isPasswordValid(pw);
    var confirmOk = pw.length > 0 && pwConfirm.length > 0 && pw === pwConfirm;
    var agreed = agreeTerms && agreeTerms.checked;
    btnRegister.disabled = !(nameOk && companyOk && emailOk && passwordOk && confirmOk && agreed);
  }

  if (btnRegister) {
    setRegisterButtonState();
    if (agreeTerms) agreeTerms.addEventListener('change', setRegisterButtonState);
    [nameInput, companyInput, emailInput, passwordInput, passwordConfirmInput].forEach(function (el) {
      if (el) {
        el.addEventListener('input', setRegisterButtonState);
        el.addEventListener('change', setRegisterButtonState);
      }
    });
  }

  /* パスワード表示切替（目のアイコン） */
  document.querySelectorAll('.btn-password-toggle').forEach(function (btn) {
    var targetId = btn.getAttribute('data-target');
    var input = targetId ? document.getElementById(targetId) : null;
    var openEl = btn.querySelector('.icon-eye-open');
    var closedEl = btn.querySelector('.icon-eye-closed');
    if (!input || !openEl || !closedEl) return;
    btn.addEventListener('click', function () {
      var isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      openEl.hidden = isPassword;
      closedEl.hidden = !isPassword;
      if (isJa) {
        btn.setAttribute('aria-label', isPassword ? 'パスワードを隠す' : 'パスワードを表示');
        btn.setAttribute('title', isPassword ? 'パスワードを隠す' : 'パスワードを表示');
      } else {
        btn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
        btn.setAttribute('title', isPassword ? 'Hide password' : 'Show password');
      }
    });
  });

  const regForm = document.getElementById('registration-form');
  if (regForm) {
    regForm.addEventListener('invalid', function (e) {
      if (e.target.validity.valueMissing && (e.target.required || e.target.getAttribute('required') !== null)) {
        e.target.setCustomValidity(msg.required);
      } else {
        e.target.setCustomValidity('');
      }
    }, true);

    regForm.addEventListener('input', function (e) {
      e.target.setCustomValidity('');
    });

    regForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var password = document.getElementById('password');
      var passwordConfirm = document.getElementById('password-confirm');
      if (password && !isPasswordValid(password.value)) {
        alert(msg.passwordLength);
        return;
      }
      if (password && passwordConfirm && password.value !== passwordConfirm.value) {
        alert(isJa ? 'パスワードが一致しません。' : 'Passwords do not match.');
        return;
      }
      console.log('Registration form submitted (placeholder).');
    });
  }
})();

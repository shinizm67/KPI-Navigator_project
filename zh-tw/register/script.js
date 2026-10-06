/**
 * Key Performance Navigator - Global script
 * Si-Fi Registration page: language selector & form handling
 */

(function () {
  'use strict';

  var STORAGE_KEY_OFFICE = 'kpi-office-mode';

  /* 受付可否は server の registrationEnabled が正本。status GET が true を返すまで停止表示のまま（fail closed） */
  var regDisabledNotice = document.getElementById('registration-disabled-notice');
  var regFormGate = document.getElementById('registration-form');
  var registrationOpen = false;
  var registrationStatus = null;
  if (regFormGate) {
    regFormGate.setAttribute('hidden', 'hidden');
    regFormGate.setAttribute('aria-hidden', 'true');
    regFormGate.addEventListener('submit', function (e) {
      if (registrationOpen) return;
      e.preventDefault();
      e.stopImmediatePropagation();
    }, true);
  }
  var btnGate = document.getElementById('btn-register');
  if (btnGate) btnGate.disabled = true;

  function isOpenStatus(r) {
    var d = r && r.status === 200 ? r.data : null;
    return !!(
      d &&
      d.registrationEnabled === true &&
      typeof d.termsVersion === 'string' && d.termsVersion &&
      typeof d.privacyVersion === 'string' && d.privacyVersion &&
      typeof d.formToken === 'string' && d.formToken
    );
  }

  /* Newsletter (optional, default OFF): shown only when the server wording version equals this page's; otherwise nothing is sent */
  var marketingWrap = document.getElementById('marketing-optin-wrap');
  var marketingBox = document.getElementById('marketing-optin');

  function marketingOffered() {
    return !!(marketingWrap && marketingBox && !marketingWrap.hidden);
  }

  function openRegistrationForm(d) {
    registrationStatus = d;
    registrationOpen = true;
    if (marketingWrap && marketingBox) {
      var pageVersion = marketingWrap.getAttribute('data-marketing-version') || '';
      marketingBox.checked = false;
      marketingWrap.hidden = !(pageVersion && d.marketingConsentVersion === pageVersion);
    }
    if (regDisabledNotice) regDisabledNotice.hidden = true;
    if (regFormGate) {
      regFormGate.removeAttribute('hidden');
      regFormGate.removeAttribute('aria-hidden');
    }
    setRegisterButtonState();
  }

  if (regFormGate && window.__KPI_AUTH && typeof window.__KPI_AUTH.registrationStatus === 'function') {
    window.__KPI_AUTH
      .registrationStatus()
      .then(function (r) {
        if (isOpenStatus(r)) openRegistrationForm(r.data);
      })
      .catch(function () {});
  }

  var bodyEl = document.getElementById('body-el');
  var btnModeToggle = document.getElementById('btn-mode-toggle');
  var btnModeText = document.getElementById('btn-mode-text');

  function updateModeButton() {
    if (!btnModeText || !btnModeToggle) return;
    var isOffice = bodyEl && bodyEl.classList.contains('office-mode');
    btnModeText.textContent = isOffice ? 'SCI-FI MODE' : 'OFFICE MODE';
    btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');
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

  /* 公開 Registration は Billing 実装まで Basic 固定。?plan= は表示にも権限にも使わない */
  var planTitle = document.getElementById('plan-title');
  var planPrice = document.getElementById('plan-price');
  if (planTitle && planPrice) {
    planTitle.textContent = 'Key Performance Navigator Basic';
    planPrice.textContent = '$10 / 月';
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
    var urlZhTw = wrap && wrap.getAttribute('data-url-zh-tw');

    langOptions.forEach(function (opt) {
      opt.addEventListener('click', function (e) {
        e.stopPropagation();
        if (bodyEl && bodyEl.classList.contains('office-mode')) {
          sessionStorage.setItem(STORAGE_KEY_OFFICE, '1');
        }
        var lang = this.getAttribute('data-lang');
        var baseUrl =
          lang === 'ja' && urlJa
            ? urlJa
            : lang === 'en' && urlEn
              ? urlEn
              : lang === 'zh-tw' && urlZhTw
                ? urlZhTw
                : null;
        if (baseUrl) {
          window.location.href = baseUrl;
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
    },
    zh: {
      required: '請填寫此欄位。',
      passwordLength: '密碼至少需 8 個字元，並包含字母、數字與符號。'
    }
  };
  var msg = messages[pageLang] || messages.en;

  /* Register ボタン: Email＋パスワード条件＋Confirm 一致＋同意チェックで有効化。Business Profile は Initial Setup STEP 01 */
  var agreeTerms = document.getElementById('agree-terms');
  var btnRegister = document.getElementById('btn-register');
  var emailInput = document.getElementById('email');
  var passwordInput = document.getElementById('password');
  var passwordConfirmInput = document.getElementById('password-confirm');

  function isPasswordValid(pw) {
    if (!pw || pw.length < 8) return false;
    var hasLetter = /[a-zA-Z]/.test(pw);
    var hasNumber = /[0-9]/.test(pw);
    var hasSymbol = /[^a-zA-Z0-9]/.test(pw);
    return hasLetter && hasNumber && hasSymbol;
  }

  function setRegisterButtonState() {
    if (!btnRegister) return;
    var emailOk = emailInput && emailInput.value.trim().length > 0;
    var pw = passwordInput ? passwordInput.value : '';
    var pwConfirm = passwordConfirmInput ? passwordConfirmInput.value : '';
    var passwordOk = isPasswordValid(pw);
    var confirmOk = pw.length > 0 && pwConfirm.length > 0 && pw === pwConfirm;
    var agreed = agreeTerms && agreeTerms.checked;
    btnRegister.disabled = !(registrationOpen && emailOk && passwordOk && confirmOk && agreed);
  }

  if (btnRegister) {
    setRegisterButtonState();
    if (agreeTerms) agreeTerms.addEventListener('change', setRegisterButtonState);
    [emailInput, passwordInput, passwordConfirmInput].forEach(function (el) {
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
      btn.setAttribute('aria-label', isPassword ? '隱藏密碼' : '顯示密碼');
      btn.setAttribute('title', isPassword ? '隱藏密碼' : '顯示密碼');
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
      if (!registrationOpen || !registrationStatus) return;
      var password = document.getElementById('password');
      var passwordConfirm = document.getElementById('password-confirm');
      var emailEl = document.getElementById('email');
      if (password && !isPasswordValid(password.value)) {
        alert(msg.passwordLength);
        return;
      }
      if (password && passwordConfirm && password.value !== passwordConfirm.value) {
        alert(pageLang === 'ja' ? 'パスワードが一致しません。' : pageLang === 'zh' ? '密碼不一致。' : 'Passwords do not match.');
        return;
      }
      if (!window.__KPI_AUTH) {
        alert('Auth module failed to load.');
        return;
      }
      var email = emailEl ? emailEl.value.trim() : '';
      var pw = password ? password.value : '';
      var extraNote = document.getElementById('reg-extra-note');
      var marketingOptIn = marketingOffered() && marketingBox.checked;
      var extra = {
        consentAccepted: !!(agreeTerms && agreeTerms.checked),
        termsVersion: registrationStatus.termsVersion,
        privacyVersion: registrationStatus.privacyVersion,
        formToken: registrationStatus.formToken,
        extraNote: extraNote ? extraNote.value : ''
      };
      if (marketingOptIn) {
        extra.marketingOptIn = true;
        extra.marketingConsentVersion = marketingWrap.getAttribute('data-marketing-version');
        extra.marketingLocale = 'zh-TW';
      }
      if (btnRegister) btnRegister.disabled = true;
      window.__KPI_AUTH
        .register(email, pw, extra)
        .then(function (r) {
          if (r.status === 201 && r.data && r.data.ok) {
            alert('註冊完成，將前往登入頁面。');
            window.location.href = '../login/index.html';
            return;
          }
          if (r.data && r.data.error === 'marketing_consent_outdated') {
            alert('通知郵件的文字已更新。請重新載入頁面，確認內容後再試一次。');
            setRegisterButtonState();
            return;
          }
          alert(window.__KPI_AUTH.errorMessage('zh', r.status, r.data));
          setRegisterButtonState();
        })
        .catch(function () {
          alert(window.__KPI_AUTH.errorMessage('zh', 0, { error: 'network' }));
          setRegisterButtonState();
        });
    });
  }
})();

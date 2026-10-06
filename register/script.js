/**
 * Key Performance Navigator - Global script
 * Si-Fi Registration page: language selector & form handling
 */

(function () {
  'use strict';

  var STORAGE_KEY_OFFICE = 'kpi-office-mode';
  var isJa = (document.documentElement.getAttribute('lang') || '').toLowerCase().split('-')[0] === 'ja';
  var pageLangRaw = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var authLang = pageLangRaw.indexOf('zh') === 0 ? 'zh' : (pageLangRaw.indexOf('ja') === 0 ? 'ja' : 'en');

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

  /* お知らせメール（任意・既定 OFF）: server の文言版とページの文言版が一致したときだけ表示。不一致なら送らない */
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


  /* 公開 Registration は Billing 実装まで Basic 固定。?plan= は表示にも権限にも使わない */
  var planTitle = document.getElementById('plan-title');
  var planPrice = document.getElementById('plan-price');
  var planCancel = document.getElementById('plan-cancel');
  if (planTitle && planPrice) {
    planTitle.textContent = 'Key Performance Navigator Basic';
    planPrice.textContent = isJa ? '¥1,000/月' : '$10 / Month';
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
    var urlZhTw = wrap && wrap.getAttribute('data-url-zh-tw');
    var bodyElLang = document.getElementById('body-el');

    langOptions.forEach(function (opt) {
      opt.addEventListener('click', function (e) {
        e.stopPropagation();
        if (bodyElLang && bodyElLang.classList.contains('office-mode')) {
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

  /* Register ボタン: Email＋パスワード条件＋Confirm 一致＋同意チェックで有効化。Business Profile は Initial Setup STEP 01 */
  var agreeTerms = document.getElementById('agree-terms') || document.getElementById('agree-terms-jp');
  var btnRegister = document.getElementById('btn-register');
  var emailInput = document.getElementById('email');
  var passwordInput = document.getElementById('password');
  var passwordConfirmInput = document.getElementById('password-confirm');

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
      if (!registrationOpen || !registrationStatus) return;
      var password = document.getElementById('password');
      var passwordConfirm = document.getElementById('password-confirm');
      var emailEl = document.getElementById('email');
      if (password && !isPasswordValid(password.value)) {
        alert(msg.passwordLength);
        return;
      }
      if (password && passwordConfirm && password.value !== passwordConfirm.value) {
        alert(isJa ? 'パスワードが一致しません。' : 'Passwords do not match.');
        return;
      }
      if (!window.__KPI_AUTH) {
        alert(isJa ? '認証モジュールを読み込めませんでした。' : 'Auth module failed to load.');
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
        extra.marketingLocale = 'ja';
      }
      if (btnRegister) btnRegister.disabled = true;
      window.__KPI_AUTH
        .register(email, pw, extra)
        .then(function (r) {
          if (r.status === 201 && r.data && r.data.ok) {
            alert(isJa ? '登録が完了しました。ログイン画面へ進みます。' : 'Registration complete. Proceeding to login.');
            window.location.href = '../../login/index.html';
            return;
          }
          if (r.data && r.data.error === 'marketing_consent_outdated') {
            alert('お知らせメールの文言が更新されました。ページを再読み込みし、内容を確認してから、もう一度お試しください。');
            setRegisterButtonState();
            return;
          }
          alert(window.__KPI_AUTH.errorMessage(authLang, r.status, r.data));
          setRegisterButtonState();
        })
        .catch(function () {
          alert(window.__KPI_AUTH.errorMessage(authLang, 0, { error: 'network' }));
          setRegisterButtonState();
        });
    });
  }
})();

/**
 * KPI Navigator - Global script
 * Si-Fi Registration page: language selector & form handling
 */

(function () {
  'use strict';

  /* プラン表示: URL の ?plan=basic / ?plan=pro でタイトル・価格を切り替え（EN/JP 両対応） */
  var planTitle = document.getElementById('plan-title');
  var planPrice = document.getElementById('plan-price');
  var planCancel = document.getElementById('plan-cancel');
  var isJa = (document.documentElement.getAttribute('lang') || '').toLowerCase().split('-')[0] === 'ja';
  if (planTitle && planPrice) {
    var params = new URLSearchParams(window.location.search);
    var plan = (params.get('plan') || 'basic').toLowerCase();
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

    langOptions.forEach(function (opt) {
      opt.addEventListener('click', function (e) {
        e.stopPropagation();
        const lang = this.getAttribute('data-lang');
        langOptions.forEach(function (o) {
          o.classList.toggle('lang-option-active', o.getAttribute('data-lang') === lang);
        });
        var codeEl = langBtn.querySelector('.lang-code');
        var nameEl = langBtn.querySelector('.lang-name');
        if (codeEl) codeEl.textContent = lang === 'ja' ? 'JP' : 'EN';
        if (nameEl) nameEl.textContent = lang === 'ja' ? 'Japanese' : 'English';
        langDropdown.hidden = true;
        langBtn.setAttribute('aria-expanded', 'false');
        if (lang === 'ja' && urlJa) {
          window.location.href = urlJa;
        } else if (lang === 'en' && urlEn) {
          window.location.href = urlEn;
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

  /* Register ボタン: 同意チェックで有効化（EN: agree-terms / JP: agree-terms-jp） */
  var agreeTerms = document.getElementById('agree-terms') || document.getElementById('agree-terms-jp');
  var btnRegister = document.getElementById('btn-register');
  if (agreeTerms && btnRegister) {
    function setRegisterButtonState() {
      btnRegister.disabled = !agreeTerms.checked;
    }
    setRegisterButtonState();
    agreeTerms.addEventListener('change', setRegisterButtonState);
  }

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
      if (password && password.value.length < 8) {
        alert(msg.passwordLength);
        return;
      }
      console.log('Registration form submitted (placeholder).');
    });
  }
})();

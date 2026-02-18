/**
 * KPI Navigator - Global script
 * Si-Fi Registration page: language selector & form handling
 */

(function () {
  'use strict';

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

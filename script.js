/**
 * KPI Navigator - Global script
 * Si-Fi Registration page: language selector & form handling
 */

(function () {
  'use strict';

  const langSelect = document.getElementById('lang-select');
  if (langSelect) {
    langSelect.addEventListener('change', function () {
      const value = this.value;
      if (value === 'ja') {
        // 日本語版が用意されたら registration_si-fi_ja.html などへ
        window.location.href = 'registration_si-fi_ja.html';
      } else {
        window.location.href = 'registration_si-fi_en.html';
      }
    });
  }

  const regForm = document.getElementById('registration-form');
  if (regForm) {
    regForm.addEventListener('submit', function (e) {
      e.preventDefault();
      // TODO: バリデーション・送信処理（PHP or API 連携時に実装）
      var password = document.getElementById('password');
      if (password && password.value.length < 8) {
        alert('Password must be at least 8 characters, including letters, numbers, and symbols.');
        return;
      }
      console.log('Registration form submitted (placeholder).');
      // alert('Registration submitted. (Backend not connected yet.)');
    });
  }
})();

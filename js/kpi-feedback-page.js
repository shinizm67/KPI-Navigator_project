/**
 * setting/feedback.html — POST /api/v1/feedback.php
 */
(function (global) {
  'use strict';

  function resolveApiBase() {
    try {
      if (global.__KPI_AUTH && typeof global.__KPI_AUTH.resolveAuthBase === 'function') {
        return global.__KPI_AUTH.resolveAuthBase();
      }
    } catch (_e0) {}
    try {
      if (global.__KPI_AUTH_BASE) return String(global.__KPI_AUTH_BASE).replace(/\/$/, '');
    } catch (_e1) {}
    var path = global.location.pathname || '';
    var m = path.match(/^(.*?\/kpi-navigator)(?:\/|$)/);
    return (m ? m[1] : '') + '/api/v1';
  }

  function setStatus(el, kind, text) {
    if (!el) return;
    el.hidden = !text;
    el.textContent = text || '';
    el.setAttribute('data-kind', kind || '');
  }

  function init() {
    var form = document.getElementById('kpi-feedback-form');
    if (!form) return;
    var status = document.getElementById('kpi-feedback-status');
    var submitBtn = document.getElementById('kpi-feedback-submit');
    var msgs = {
      ja: {
        ok: '送信しました。ありがとうございます。',
        empty: 'メッセージを入力してください。',
        rate: '送信間隔が短すぎます。少し待ってから再度お試しください。',
        mail: '送信に失敗しました。しばらくしてから再度お試しください。',
        net: '通信エラーです。接続を確認してください。',
      },
      en: {
        ok: 'Sent. Thank you.',
        empty: 'Please enter a message.',
        rate: 'Please wait a moment before sending again.',
        mail: 'Could not send. Please try again later.',
        net: 'Network error. Check your connection.',
      },
      'zh-tw': {
        ok: '已送出，謝謝。',
        empty: '請輸入訊息。',
        rate: '傳送間隔過短，請稍后再試。',
        mail: '傳送失敗，請稍后再試。',
        net: '連線錯誤，請確認網路。',
      },
    };
    var lang = (document.documentElement.lang || 'ja').toLowerCase();
    var pack = msgs.ja;
    if (lang.indexOf('en') === 0) pack = msgs.en;
    else if (lang.indexOf('zh') === 0) pack = msgs['zh-tw'];

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var categoryEl = form.querySelector('input[name="feedback-category"]:checked');
      var messageEl = document.getElementById('feedback-message');
      var contactEl = document.getElementById('feedback-contact');
      var message = messageEl ? String(messageEl.value || '').trim() : '';
      if (!message) {
        setStatus(status, 'error', pack.empty);
        if (messageEl) messageEl.focus();
        return;
      }
      var payload = {
        category: categoryEl ? categoryEl.value : 'other',
        message: message,
        contactEmail: contactEl ? String(contactEl.value || '').trim() : '',
        pageUrl: global.location.href,
        userAgent: global.navigator && global.navigator.userAgent ? global.navigator.userAgent : '',
      };
      if (submitBtn) submitBtn.disabled = true;
      setStatus(status, 'pending', '');
      fetch(resolveApiBase() + '/feedback.php', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function (res) {
          return res.json().catch(function () {
            return {};
          }).then(function (data) {
            return { res: res, data: data };
          });
        })
        .then(function (r) {
          if (r.res.ok && r.data && r.data.ok) {
            setStatus(status, 'ok', pack.ok);
            form.reset();
            var other = form.querySelector('input[name="feedback-category"][value="other"]');
            if (other) other.checked = true;
            return;
          }
          var err = r.data && r.data.error ? String(r.data.error) : '';
          if (err === 'rate_limited') setStatus(status, 'error', pack.rate);
          else setStatus(status, 'error', pack.mail);
        })
        .catch(function () {
          setStatus(status, 'error', pack.net);
        })
        .then(function () {
          if (submitBtn) submitBtn.disabled = false;
        });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(typeof window !== 'undefined' ? window : this);

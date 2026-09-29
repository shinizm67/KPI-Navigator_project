/**
 * Newsletter unsubscribe confirmation page (JA / EN / zh-tw). BR-LAUNCH-09 Extension M3.
 * Opening the page changes nothing (mail scanners follow links); only the button posts.
 * No login. The token from ?t= goes in the POST body. The answer is the same for every token.
 */
(function () {
  'use strict';

  var form = document.getElementById('unsubscribe-form');
  var btn = document.getElementById('btn-unsubscribe');
  var errEl = document.getElementById('unsubscribe-error');
  var doneEl = document.getElementById('unsubscribe-done');
  var reasonEl = document.getElementById('unsubscribe-reason');
  var noteEl = document.getElementById('unsubscribe-note');
  if (!form || !btn || !doneEl) return;

  var langAttr = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var lang = langAttr.indexOf('zh') === 0 ? 'zh' : langAttr.indexOf('ja') === 0 ? 'ja' : 'en';
  var TEXT = {
    ja: {
      invalid: 'このリンクは正しくありません。メール内のリンクをもう一度開くか、support@forge-laboratory.com までご連絡ください。',
      limited: '短時間にリクエストが続いたため、一時的に受け付けを制限しています。しばらく時間をおいてから、もう一度お試しください。',
      failed: '現在、配信停止を処理できません。しばらくしてから、もう一度お試しいただくか、support@forge-laboratory.com までご連絡ください。'
    },
    en: {
      invalid: 'This link is not valid. Please open the link in the email again, or contact support@forge-laboratory.com.',
      limited: 'Too many requests in a short time. Please wait a while and try again.',
      failed: 'We cannot process your request right now. Please try again later, or contact support@forge-laboratory.com.'
    },
    zh: {
      invalid: '此連結無效。請再次開啟郵件中的連結，或聯絡 support@forge-laboratory.com。',
      limited: '短時間內請求過多，暫時無法受理。請稍候再試。',
      failed: '目前無法處理取消訂閱。請稍後再試，或聯絡 support@forge-laboratory.com。'
    }
  }[lang];

  function tokenFromQuery() {
    try {
      return (new URLSearchParams(window.location.search || '').get('t') || '').trim();
    } catch (_e) {
      return '';
    }
  }

  function apiUrl() {
    var path = String(window.location.pathname || '');
    var m = path.match(/^(.*?\/kpi-navigator)(?:\/|$)/);
    return (m ? m[1] : '') + '/api/v1/marketing/unsubscribe.php';
  }

  function showErr(text) {
    if (!errEl) return;
    errEl.hidden = !text;
    errEl.textContent = text || '';
  }

  var token = tokenFromQuery();
  var wellFormed = /^[A-Za-z0-9_-]{43}$/.test(token);
  if (!wellFormed) {
    showErr(TEXT.invalid);
    btn.disabled = true;
    return;
  }
  btn.disabled = false;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (btn.disabled) return;
    btn.disabled = true;
    showErr('');
    var body = { token: token };
    if (reasonEl && reasonEl.value) body.reason = reasonEl.value;
    if (noteEl && noteEl.value.trim()) body.note = noteEl.value.trim().slice(0, 200);
    fetch(apiUrl(), {
      method: 'POST',
      credentials: 'omit',
      cache: 'no-store',
      referrerPolicy: 'no-referrer',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
      .then(function (res) {
        if (res.status === 200) {
          form.hidden = true;
          doneEl.hidden = false;
          return;
        }
        showErr(res.status === 429 ? TEXT.limited : TEXT.failed);
        btn.disabled = false;
      })
      .catch(function () {
        showErr(TEXT.failed);
        btn.disabled = false;
      });
  });
})();

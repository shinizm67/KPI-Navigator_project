/**
 * Preferences: newsletter (marketing email) row (JA / EN / zh-tw). BR-LAUNCH-09 Extension M3.
 * The row stays hidden until the server answers the current state (no hidden / default opt-in).
 * Checking = a new explicit consent for the wording version shown on this page; unchecking = unsubscribe.
 * Applies immediately (not through "Save").
 */
(function () {
  'use strict';

  var row = document.getElementById('pref-marketing-row');
  var box = document.getElementById('pref-marketing');
  var stateEl = document.getElementById('pref-marketing-state');
  if (!row || !box || !stateEl) return;

  var langAttr = (document.documentElement.getAttribute('lang') || 'en').toLowerCase();
  var lang = langAttr.indexOf('zh') === 0 ? 'zh' : langAttr.indexOf('ja') === 0 ? 'ja' : 'en';
  var locale = lang === 'zh' ? 'zh-TW' : lang;
  var pageVersion = row.getAttribute('data-marketing-version') || '';

  var TEXT = {
    ja: {
      on: '現在の状態：受け取る',
      off: '現在の状態：受け取らない',
      subscribed: 'お知らせメールの受け取りを開始しました。',
      unsubscribed: 'お知らせメールの配信を停止しました。',
      outdated: 'お知らせメールの文言が更新されました。ページを再読み込みして、内容をご確認ください。',
      failed: '現在、変更を処理できません。しばらくしてから、もう一度お試しください。'
    },
    en: {
      on: 'Current status: receiving',
      off: 'Current status: not receiving',
      subscribed: 'You will now receive email updates from Forge Laboratory.',
      unsubscribed: 'You have unsubscribed from email updates.',
      outdated: 'The email updates wording has been updated. Please reload the page and review it.',
      failed: 'This change cannot be processed right now. Please try again later.'
    },
    zh: {
      on: '目前狀態：接收',
      off: '目前狀態：不接收',
      subscribed: '已開始接收通知郵件。',
      unsubscribed: '已取消訂閱通知郵件。',
      outdated: '通知郵件的文字已更新。請重新載入頁面並確認內容。',
      failed: '目前無法處理此變更，請稍後再試。'
    }
  }[lang];

  var auth = window.__KPI_AUTH;
  if (!auth || typeof auth.resolveAuthBase !== 'function' || typeof window.fetch !== 'function') return;
  var url = auth.resolveAuthBase() + '/marketing/preference.php';
  var subscribed = false;
  var versionOk = false;

  function readJson(res) {
    return res
      .json()
      .catch(function () {
        return { ok: false };
      })
      .then(function (data) {
        return { status: res.status, data: data || { ok: false } };
      });
  }

  function render(note) {
    box.checked = subscribed;
    /* A stale page may still unsubscribe, but never subscribe with wording it did not show. */
    box.disabled = !subscribed && !versionOk;
    stateEl.textContent = (subscribed ? TEXT.on : TEXT.off) + (note ? ' — ' + note : '');
  }

  function post(action) {
    var headers = { 'Content-Type': 'application/json' };
    var body = { action: action, consentTextVersion: pageVersion, locale: locale };
    if (typeof auth.attachExpectedUser === 'function') {
      var attached = auth.attachExpectedUser(headers, body);
      headers = attached.headers;
      body = attached.body;
    }
    return fetch(url, { method: 'POST', credentials: 'include', headers: headers, body: JSON.stringify(body) }).then(readJson);
  }

  box.addEventListener('change', function () {
    var want = box.checked;
    if (typeof auth.assertCanMutateUserData === 'function' && !auth.assertCanMutateUserData()) {
      render('');
      return;
    }
    box.disabled = true;
    var ready =
      typeof auth.ensureUserScopeBound === 'function'
        ? Promise.resolve(auth.ensureUserScopeBound()).catch(function () {
            return null;
          })
        : Promise.resolve(null);
    ready
      .then(function () {
        return post(want ? 'subscribe' : 'unsubscribe');
      })
      .then(function (r) {
        if (r.status === 200 && r.data && r.data.ok) {
          subscribed = r.data.subscribed === true;
          render(subscribed ? TEXT.subscribed : TEXT.unsubscribed);
          return;
        }
        if (r.data && r.data.error === 'marketing_consent_outdated') {
          versionOk = false;
          render(TEXT.outdated);
          return;
        }
        if (r.data && r.data.error === 'stale_account' && typeof auth.showStaleAccountWarning === 'function') {
          auth.showStaleAccountWarning();
        }
        render(TEXT.failed);
      })
      .catch(function () {
        render(TEXT.failed);
      });
  });

  fetch(url, { method: 'GET', credentials: 'include', headers: { Accept: 'application/json' } })
    .then(readJson)
    .then(function (r) {
      if (r.status !== 200 || !r.data || r.data.ok !== true || typeof r.data.subscribed !== 'boolean') return;
      subscribed = r.data.subscribed;
      versionOk = !!pageVersion && r.data.consentTextVersion === pageVersion;
      render(versionOk ? '' : TEXT.outdated);
      row.hidden = false;
    })
    .catch(function () {});
})();

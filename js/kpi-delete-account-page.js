/**
 * Delete Account flow (BR-LAUNCH-09 Phase 3).
 * Step 3 (#delete-security-form): current password -> /auth/delete-account.php action=verify
 *   (server keeps a short-lived delete intent in the session; nothing is deleted).
 * Step 4 (#delete-final-form): acknowledgement -> action=delete. Only a 200 { ok, deleted } response
 *   clears this browser's account data and opens the completion page.
 * Completion page (#delete-accomplished-panel): shown only when this tab saw the server success.
 * Uses only __KPI_AUTH members that predate this page, so a cached kpi-auth-client.js still works.
 */
(function () {
  'use strict';

  var DONE_FLAG = 'kpi-account-deleted';
  /* Theme + UI preferences survive deletion; everything tied to the account does not. */
  var LOCAL_ACCOUNT_KEYS = [
    'kpiNavigator.lastKpiUserId',
    'kpiNavigator.subscriptionTier',
    'kpiNavigator.storeSync',
    'kpiNavigator.registrationComplete',
  ];
  var SESSION_KEEP = { 'kpi-office-mode': true };

  function lang() {
    var l = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
    if (l.indexOf('zh') === 0) return 'zh';
    if (l.indexOf('ja') === 0) return 'ja';
    return 'en';
  }

  function t(ja, en, zh) {
    var l = lang();
    return l === 'ja' ? ja : l === 'zh' ? zh : en;
  }

  var MSG = {
    pwEmpty: function () {
      return t('現在のパスワードを入力してください。', 'Please enter your current password.', '請輸入目前的密碼。');
    },
    pwIncorrect: function () {
      return t('現在のパスワードが正しくありません。', 'Current password is incorrect.', '目前的密碼不正確。');
    },
    wait: function (sec) {
      var m = Math.max(1, Math.ceil((sec || 0) / 60));
      return t(
        'パスワードの入力に続けて失敗したため、一時的に受け付けを停止しています。' + m + '分後に、もう一度お試しください。',
        'Too many incorrect passwords. Please try again in ' + m + ' minutes.',
        '密碼錯誤次數過多，暫時停止受理。請於 ' + m + ' 分鐘後再試。'
      );
    },
    protectedAccount: function () {
      return t(
        'このアカウントはこの画面から削除できません。',
        'This account cannot be deleted from this page.',
        '此帳戶無法從此頁面刪除。'
      );
    },
    children: function () {
      return t(
        '関連アカウントを先に整理してください。',
        'Please resolve the linked accounts first.',
        '請先整理關聯帳戶。'
      );
    },
    ackRequired: function () {
      return t(
        '内容を確認し、チェックを入れてください。',
        'Please confirm by checking the box.',
        '請確認內容並勾選方塊。'
      );
    },
    intentRequired: function () {
      return t(
        '本人確認の有効期限が切れたか、アカウント情報が変更されました。STEP 3 に戻って、もう一度パスワードを入力してください。',
        'Your verification expired or your account changed. Go back to Step 3 and enter your password again.',
        '身分驗證已過期或帳戶資訊已變更。請返回步驟 3 重新輸入密碼。'
      );
    },
    failed: function () {
      return t(
        'アカウントを削除できませんでした。データは削除されていません。しばらくしてから、もう一度お試しください。',
        'Your account could not be deleted. No data was deleted. Please try again later.',
        '無法刪除帳戶，資料未被刪除。請稍後再試。'
      );
    },
    unknown: function () {
      return t(
        '通信が途切れたため、削除が完了したか確認できませんでした。もう一度「アカウントを削除」を押してください。削除済みの場合はログイン画面に移動します。',
        'The connection was lost, so we could not confirm whether the deletion finished. Press "Delete Account" again. If it was deleted, you will be taken to the sign-in page.',
        '連線中斷，無法確認刪除是否完成。請再按一次「刪除帳戶」。若已刪除，將前往登入頁面。'
      );
    },
    verifyFailed: function () {
      return t(
        '本人確認を完了できませんでした。しばらくしてから、もう一度お試しください。',
        'Verification could not be completed. Please try again later.',
        '無法完成身分驗證，請稍後再試。'
      );
    },
  };

  function setErr(el, msg) {
    if (!el) return;
    el.textContent = msg || '';
    el.hidden = !msg;
  }

  function post(auth, body) {
    var headers = { 'Content-Type': 'application/json' };
    if (typeof auth.attachExpectedUser === 'function') {
      var attached = auth.attachExpectedUser(headers, body);
      headers = attached.headers;
      body = attached.body;
    }
    return fetch(auth.resolveAuthBase() + '/auth/delete-account.php', {
      method: 'POST',
      credentials: 'include',
      headers: headers,
      body: JSON.stringify(body),
    }).then(function (res) {
      return res
        .json()
        .catch(function () {
          return { ok: false, error: 'invalid_response' };
        })
        .then(function (data) {
          return { status: res.status, data: data || { ok: false } };
        });
    });
  }

  function send(body) {
    var auth = window.__KPI_AUTH;
    if (!auth || typeof auth.resolveAuthBase !== 'function' || typeof window.fetch !== 'function') {
      return Promise.resolve(null);
    }
    var ready =
      typeof auth.ensureUserScopeBound === 'function'
        ? Promise.resolve(auth.ensureUserScopeBound()).catch(function () {
            return null;
          })
        : Promise.resolve(null);
    return ready.then(function () {
      return post(auth, body);
    });
  }

  /* Returns true when the session is gone and the page is leaving. */
  function handleSessionLoss(r) {
    var code = (r && r.data && r.data.error) || '';
    if ((r && r.status === 401) || code === 'account_disabled') {
      var auth = window.__KPI_AUTH;
      if (auth && typeof auth.handleUnauthorizedSession === 'function') auth.handleUnauthorizedSession(r);
      return true;
    }
    return false;
  }

  function staleAccountText(fallback) {
    var auth = window.__KPI_AUTH;
    return auth && typeof auth.staleAccountMessage === 'function' ? auth.staleAccountMessage() : fallback;
  }

  function commonError(code) {
    if (code === 'protected_account') return MSG.protectedAccount();
    if (code === 'has_child_accounts') return MSG.children();
    if (code === 'stale_account') return staleAccountText('');
    return '';
  }

  function clearAccountClientData() {
    var auth = window.__KPI_AUTH;
    try {
      if (auth && typeof auth.clearUserScopedLocalData === 'function') auth.clearUserScopedLocalData();
    } catch (_eScope) {}
    LOCAL_ACCOUNT_KEYS.forEach(function (k) {
      try {
        localStorage.removeItem(k);
      } catch (_eLs) {}
    });
    try {
      var keys = [];
      for (var i = 0; i < sessionStorage.length; i++) keys.push(sessionStorage.key(i));
      keys.forEach(function (k) {
        if (k && !SESSION_KEEP[k]) sessionStorage.removeItem(k);
      });
    } catch (_eSs) {}
  }

  /* ---------- Step 3: current password ---------- */
  var securityForm = document.getElementById('delete-security-form');
  if (securityForm) {
    var pwEl = document.getElementById('verify-password');
    var pwErr = document.getElementById('delete-security-error');
    var pwBtn = securityForm.querySelector('button[type="submit"]');
    var verifying = false;

    securityForm.addEventListener('submit', function (e) {
      e.preventDefault();
      if (verifying) return;
      setErr(pwErr, '');
      var pw = pwEl ? String(pwEl.value || '') : '';
      if (!pw) {
        setErr(pwErr, MSG.pwEmpty());
        return;
      }
      verifying = true;
      if (pwBtn) pwBtn.disabled = true;
      send({ action: 'verify', currentPassword: pw })
        .then(function (r) {
          if (pwEl) pwEl.value = '';
          if (r && r.status === 200 && r.data && r.data.ok === true) {
            window.location.href = 'delete_account5.html';
            return;
          }
          verifying = false;
          if (pwBtn) pwBtn.disabled = false;
          if (!r) return setErr(pwErr, MSG.verifyFailed());
          if (handleSessionLoss(r)) return;
          var code = (r.data && r.data.error) || '';
          if (code === 'current_password_incorrect') {
            setErr(pwErr, MSG.pwIncorrect());
            if (pwEl) pwEl.focus();
            return;
          }
          if (code === 'too_many_attempts') return setErr(pwErr, MSG.wait(r.data.retryAfterSeconds));
          setErr(pwErr, commonError(code) || MSG.verifyFailed());
        })
        .catch(function () {
          verifying = false;
          if (pwBtn) pwBtn.disabled = false;
          if (pwEl) pwEl.value = '';
          setErr(pwErr, MSG.verifyFailed());
        });
    });
  }

  /* ---------- Step 4: final confirmation -> server delete ---------- */
  var finalForm = document.getElementById('delete-final-form');
  if (finalForm) {
    var ackEl = document.getElementById('delete-final-ack');
    var finalErr = document.getElementById('delete-final-error');
    var finalBtn = document.getElementById('btn-final-delete');
    var backToVerify = document.getElementById('delete-final-reverify');
    var deleting = false;

    finalForm.addEventListener('submit', function (e) {
      e.preventDefault();
      if (deleting) return;
      setErr(finalErr, '');
      if (backToVerify) backToVerify.hidden = true;
      if (!ackEl || !ackEl.checked) {
        setErr(finalErr, MSG.ackRequired());
        return;
      }
      deleting = true;
      if (finalBtn) finalBtn.disabled = true;
      send({ action: 'delete', acknowledge: true })
        .then(function (r) {
          if (r && r.status === 200 && r.data && r.data.ok === true && r.data.deleted === true) {
            clearAccountClientData();
            try {
              sessionStorage.setItem(DONE_FLAG, '1');
            } catch (_eFlag) {}
            window.location.replace('delete_account_accomplished.html');
            return;
          }
          deleting = false;
          if (finalBtn) finalBtn.disabled = false;
          if (!r) return setErr(finalErr, MSG.failed());
          /* A retry after a lost response lands here once the account is gone. */
          if (r.status === 401) clearAccountClientData();
          if (handleSessionLoss(r)) return;
          var code = (r.data && r.data.error) || '';
          if (code === 'delete_intent_required') {
            setErr(finalErr, MSG.intentRequired());
            if (backToVerify) backToVerify.hidden = false;
            return;
          }
          setErr(finalErr, commonError(code) || MSG.failed());
        })
        .catch(function () {
          deleting = false;
          if (finalBtn) finalBtn.disabled = false;
          setErr(finalErr, MSG.unknown());
        });
    });
  }

  /* ---------- Completion page ---------- */
  var donePanel = document.getElementById('delete-accomplished-panel');
  if (donePanel) {
    var done = false;
    try {
      done = sessionStorage.getItem(DONE_FLAG) === '1';
    } catch (_eRead) {}
    if (!done) {
      window.location.replace(donePanel.getAttribute('data-kpi-home') || '../index.html');
      return;
    }
    donePanel.hidden = false;
  }
})();

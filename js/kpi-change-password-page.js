/**
 * Change Password page (BR-LAUNCH-09 Phase 1).
 * Server is the only judge: success screen only after /auth/change-password.php returns ok.
 * Password values are never written to localStorage / sessionStorage.
 * Uses only __KPI_AUTH members that predate this page, so a cached kpi-auth-client.js still works.
 */
(function () {
  'use strict';

  try {
    localStorage.removeItem('kpi-auth-password');
  } catch (_ePw) {}

  /* Success screen: the message is shown only right after a server-confirmed change. */
  var success = document.getElementById('password-success');
  if (success) {
    var flag = null;
    try {
      flag = sessionStorage.getItem('kpi-password-change-success');
      sessionStorage.removeItem('kpi-password-change-success');
    } catch (_eFlag) {}
    success.hidden = flag !== '1';
  }

  var form = document.getElementById('change-password-form');
  if (!form) return;

  var currentEl = document.getElementById('current-password');
  var newPwEl = document.getElementById('new-password');
  var confirmEl = document.getElementById('confirm-password');
  var errCurrent = document.getElementById('err-current-password');
  var errNew = document.getElementById('err-new-password');
  var errConfirm = document.getElementById('err-confirm-password');
  var errForm = document.getElementById('err-change-password');
  var submitBtn = form.querySelector('button[type="submit"]');
  var inFlight = false;

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
    currentEmpty: function () {
      return t('現在のパスワードを入力してください。', 'Please enter your current password.', '請輸入目前的密碼。');
    },
    currentIncorrect: function () {
      return t('現在のパスワードが正しくありません。', 'Current password is incorrect.', '目前的密碼不正確。');
    },
    newEmpty: function () {
      return t('新しいパスワードを入力してください。', 'Please enter a new password.', '請輸入新密碼。');
    },
    weak: function () {
      return t(
        'パスワードは8文字以上で、英字・数字・記号を含めてください。',
        'Password must be at least 8 characters and include letters, numbers, and symbols.',
        '密碼須至少 8 個字元，並包含英文字母、數字與符號。'
      );
    },
    unchanged: function () {
      return t(
        '現在と異なるパスワードを入力してください。',
        'Enter a password different from your current one.',
        '請輸入與目前不同的密碼。'
      );
    },
    confirmEmpty: function () {
      return t('確認用パスワードを入力してください。', 'Please confirm your new password.', '請確認新密碼。');
    },
    mismatch: function () {
      return t('パスワードが一致しません。', 'Passwords do not match.', '密碼不一致。');
    },
    conflict: function () {
      return t(
        'パスワードが別の操作で変更されました。ページを再読み込みして、もう一度お試しください。',
        'Your password was changed elsewhere. Reload the page and try again.',
        '密碼已在其他地方變更。請重新載入頁面後再試。'
      );
    },
    failed: function () {
      return t(
        'パスワードを変更できませんでした。しばらくしてから、もう一度お試しください。',
        'Your password could not be changed. Please try again later.',
        '無法變更密碼，請稍後再試。'
      );
    },
  };

  function setErr(el, msg) {
    if (!el) return;
    el.textContent = msg || '';
    el.hidden = !msg;
  }

  function clearErrors() {
    setErr(errCurrent, '');
    setErr(errNew, '');
    setErr(errConfirm, '');
    setErr(errForm, '');
  }

  function isPasswordValid(pw) {
    if (!pw || pw.length < 8) return false;
    return /[A-Za-z]/.test(pw) && /[0-9]/.test(pw) && /[^A-Za-z0-9]/.test(pw);
  }

  function clearInputs(all) {
    if (currentEl) currentEl.value = '';
    if (all) {
      if (newPwEl) newPwEl.value = '';
      if (confirmEl) confirmEl.value = '';
    }
  }

  function setBusy(on) {
    inFlight = on;
    if (submitBtn) submitBtn.disabled = on;
  }

  function post(auth, body) {
    var headers = { 'Content-Type': 'application/json' };
    if (typeof auth.attachExpectedUser === 'function') {
      var attached = auth.attachExpectedUser(headers, body);
      headers = attached.headers;
      body = attached.body;
    }
    return fetch(auth.resolveAuthBase() + '/auth/change-password.php', {
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

  function showServerError(auth, r) {
    var code = (r && r.data && r.data.error) || '';
    if ((r && r.status === 401) || code === 'account_disabled') {
      clearInputs(true);
      if (typeof auth.handleUnauthorizedSession === 'function') auth.handleUnauthorizedSession(r);
      return;
    }
    if (code === 'current_password_incorrect') {
      clearInputs(false);
      setErr(errCurrent, MSG.currentIncorrect());
      if (currentEl) currentEl.focus();
      return;
    }
    clearInputs(true);
    if (code === 'password_weak') return setErr(errNew, MSG.weak());
    if (code === 'password_unchanged') return setErr(errNew, MSG.unchanged());
    if (code === 'password_mismatch') return setErr(errConfirm, MSG.mismatch());
    if (code === 'password_conflict') return setErr(errForm, MSG.conflict());
    if (code === 'stale_account' && typeof auth.staleAccountMessage === 'function') {
      return setErr(errForm, auth.staleAccountMessage());
    }
    setErr(errForm, MSG.failed());
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (inFlight) return;
    clearErrors();

    var currentPw = currentEl ? String(currentEl.value || '') : '';
    var newPw = newPwEl ? String(newPwEl.value || '') : '';
    var confirmPw = confirmEl ? String(confirmEl.value || '') : '';
    var hasError = false;

    if (!currentPw) {
      setErr(errCurrent, MSG.currentEmpty());
      hasError = true;
    }
    if (!newPw) {
      setErr(errNew, MSG.newEmpty());
      hasError = true;
    } else if (!isPasswordValid(newPw)) {
      setErr(errNew, MSG.weak());
      hasError = true;
    } else if (currentPw && newPw === currentPw) {
      setErr(errNew, MSG.unchanged());
      hasError = true;
    }
    if (!confirmPw) {
      setErr(errConfirm, MSG.confirmEmpty());
      hasError = true;
    } else if (newPw && newPw !== confirmPw) {
      setErr(errConfirm, MSG.mismatch());
      hasError = true;
    }
    if (hasError) return;

    var auth = window.__KPI_AUTH;
    if (!auth || typeof auth.resolveAuthBase !== 'function' || typeof window.fetch !== 'function') {
      setErr(errForm, MSG.failed());
      return;
    }

    setBusy(true);
    var ready =
      typeof auth.ensureUserScopeBound === 'function'
        ? Promise.resolve(auth.ensureUserScopeBound()).catch(function () {
            return null;
          })
        : Promise.resolve(null);
    ready
      .then(function () {
        return post(auth, {
          currentPassword: currentPw,
          newPassword: newPw,
          newPasswordConfirm: confirmPw,
        });
      })
      .then(function (r) {
        if (r.status === 200 && r.data && r.data.ok === true) {
          clearInputs(true);
          try {
            sessionStorage.setItem('kpi-password-change-success', '1');
          } catch (_eFlag) {}
          window.location.href = 'change_password_success.html';
          return;
        }
        setBusy(false);
        showServerError(auth, r);
      })
      .catch(function () {
        setBusy(false);
        clearInputs(true);
        setErr(errForm, MSG.failed());
      });
  });
})();

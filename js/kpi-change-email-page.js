/**
 * Change Email (Edit) page (BR-LAUNCH-09 Phase 2).
 * Step A: current password + new email -> /auth/request-email-change.php mails a 6-digit code.
 * Step B: code -> /auth/confirm-email-change.php changes the sign-in email on the server.
 * The success banner is flagged only after the server confirms; nothing is written to the local profile.
 * Uses only __KPI_AUTH members that predate this page, so a cached kpi-auth-client.js still works.
 */
(function () {
  'use strict';

  var requestForm = document.getElementById('change-email-form');
  var confirmForm = document.getElementById('confirm-email-form');
  if (!requestForm || !confirmForm) return;

  var newEmailEl = document.getElementById('new-email');
  var confirmEl = document.getElementById('confirm-email');
  var passwordEl = document.getElementById('current-password');
  var codeEl = document.getElementById('email-code');
  var sentEl = document.getElementById('email-code-sent');
  var backEl = document.getElementById('email-change-back');
  var errNew = document.getElementById('err-new-email');
  var errConfirm = document.getElementById('err-confirm-email');
  var errPw = document.getElementById('err-current-password');
  var errRequest = document.getElementById('err-change-email');
  var errCode = document.getElementById('err-email-code');
  var errConfirmForm = document.getElementById('err-confirm-email-form');
  var requestBtn = requestForm.querySelector('button[type="submit"]');
  var confirmBtn = confirmForm.querySelector('button[type="submit"]');
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

  function locale() {
    var l = lang();
    return l === 'zh' ? 'zh-tw' : l;
  }

  var MSG = {
    newEmpty: function () {
      return t('新しいメールアドレスを入力してください。', 'Please enter a new email address.', '請輸入新的電子信箱。');
    },
    invalid: function () {
      return t('メールアドレスの形式が正しくありません。', 'Please enter a valid email address.', '請輸入有效的電子信箱。');
    },
    confirmEmpty: function () {
      return t('確認用メールアドレスを入力してください。', 'Please confirm your new email address.', '請確認新的電子信箱。');
    },
    mismatch: function () {
      return t('メールアドレスが一致しません。', 'Email addresses do not match.', '電子信箱不一致。');
    },
    unchanged: function () {
      return t(
        '現在と異なるメールアドレスを入力してください。',
        'Enter an email address different from your current one.',
        '請輸入與目前不同的電子信箱。'
      );
    },
    unavailable: function () {
      return t('このメールアドレスは使用できません。', 'This email address cannot be used.', '此電子信箱無法使用。');
    },
    pwEmpty: function () {
      return t('現在のパスワードを入力してください。', 'Please enter your current password.', '請輸入目前的密碼。');
    },
    pwIncorrect: function () {
      return t('現在のパスワードが正しくありません。', 'Current password is incorrect.', '目前的密碼不正確。');
    },
    wait: function (sec) {
      var s = Math.max(1, Math.ceil(sec || 0));
      return t(
        '確認コードの送信回数が多すぎます。' + s + '秒後に、もう一度お試しください。',
        'Too many confirmation codes were sent. Please try again in ' + s + ' seconds.',
        '確認碼傳送次數過多。請於 ' + s + ' 秒後再試。'
      );
    },
    mailFailed: function () {
      return t(
        '確認コードを送信できませんでした。しばらくしてから、もう一度お試しください。',
        'The confirmation code could not be sent. Please try again later.',
        '無法傳送確認碼，請稍後再試。'
      );
    },
    sent: function (email, minutes) {
      return t(
        email + ' に確認コードを送信しました。' + minutes + '分以内に入力してください。',
        'A confirmation code was sent to ' + email + '. Enter it within ' + minutes + ' minutes.',
        '確認碼已傳送至 ' + email + '。請於 ' + minutes + ' 分鐘內輸入。'
      );
    },
    codeEmpty: function () {
      return t('確認コードを入力してください。', 'Please enter the confirmation code.', '請輸入確認碼。');
    },
    codeFormat: function () {
      return t('確認コードは6桁の数字です。', 'The confirmation code is 6 digits.', '確認碼為 6 位數字。');
    },
    codeInvalid: function () {
      return t('確認コードが正しくありません。', 'The confirmation code is incorrect.', '確認碼不正確。');
    },
    codeExpired: function () {
      return t(
        '確認コードの有効期限が切れたか、無効になりました。入力画面に戻って、もう一度送信してください。',
        'The confirmation code has expired or is no longer valid. Go back and send a new code.',
        '確認碼已過期或失效。請返回輸入頁面重新傳送。'
      );
    },
    stale: function () {
      return t(
        'アカウント情報が別の操作で変更されました。入力画面に戻って、もう一度お試しください。',
        'Your account was changed elsewhere. Go back and try again.',
        '帳戶資訊已在其他地方變更。請返回輸入頁面再試一次。'
      );
    },
    failed: function () {
      return t(
        'メールアドレスを変更できませんでした。しばらくしてから、もう一度お試しください。',
        'Your email address could not be changed. Please try again later.',
        '無法變更電子信箱，請稍後再試。'
      );
    },
  };

  function setErr(el, msg) {
    if (!el) return;
    el.textContent = msg || '';
    el.hidden = !msg;
  }

  function clearErrors() {
    [errNew, errConfirm, errPw, errRequest, errCode, errConfirmForm].forEach(function (el) {
      setErr(el, '');
    });
  }

  function norm(v) {
    return String(v || '').trim().toLowerCase();
  }

  function isEmailLike(v) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
  }

  function setBusy(on) {
    inFlight = on;
    if (requestBtn) requestBtn.disabled = on;
    if (confirmBtn) confirmBtn.disabled = on;
  }

  function showStep(step) {
    requestForm.hidden = step !== 'request';
    confirmForm.hidden = step !== 'confirm';
  }

  function post(auth, path, body) {
    var headers = { 'Content-Type': 'application/json' };
    if (typeof auth.attachExpectedUser === 'function') {
      var attached = auth.attachExpectedUser(headers, body);
      headers = attached.headers;
      body = attached.body;
    }
    return fetch(auth.resolveAuthBase() + path, {
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

  function send(path, body) {
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
      return post(auth, path, body);
    });
  }

  /* Returns true when the session is gone and the page is leaving. */
  function handleSessionLoss(r) {
    var code = (r && r.data && r.data.error) || '';
    if ((r && r.status === 401) || code === 'account_disabled') {
      if (passwordEl) passwordEl.value = '';
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

  requestForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if (inFlight) return;
    clearErrors();

    var newEmail = norm(newEmailEl && newEmailEl.value);
    var confirmEmail = norm(confirmEl && confirmEl.value);
    var pw = passwordEl ? String(passwordEl.value || '') : '';
    var hasError = false;

    if (!newEmail) {
      setErr(errNew, MSG.newEmpty());
      hasError = true;
    } else if (!isEmailLike(newEmail)) {
      setErr(errNew, MSG.invalid());
      hasError = true;
    }
    if (!confirmEmail) {
      setErr(errConfirm, MSG.confirmEmpty());
      hasError = true;
    } else if (newEmail && confirmEmail !== newEmail) {
      setErr(errConfirm, MSG.mismatch());
      hasError = true;
    }
    if (!pw) {
      setErr(errPw, MSG.pwEmpty());
      hasError = true;
    }
    if (hasError) return;

    setBusy(true);
    send('/auth/request-email-change.php', {
      currentPassword: pw,
      newEmail: newEmail,
      newEmailConfirm: confirmEmail,
      locale: locale(),
    })
      .then(function (r) {
        setBusy(false);
        if (passwordEl) passwordEl.value = '';
        if (!r) return setErr(errRequest, MSG.failed());
        if (r.status === 200 && r.data && r.data.ok === true) {
          if (sentEl) sentEl.textContent = MSG.sent(String(r.data.newEmail || newEmail), r.data.expiresInMinutes || 30);
          if (codeEl) codeEl.value = '';
          showStep('confirm');
          if (codeEl) codeEl.focus();
          return;
        }
        if (handleSessionLoss(r)) return;
        var code = (r.data && r.data.error) || '';
        if (code === 'current_password_incorrect') {
          setErr(errPw, MSG.pwIncorrect());
          if (passwordEl) passwordEl.focus();
          return;
        }
        if (code === 'invalid_email') return setErr(errNew, MSG.invalid());
        if (code === 'email_mismatch') return setErr(errConfirm, MSG.mismatch());
        if (code === 'email_unchanged') return setErr(errNew, MSG.unchanged());
        if (code === 'email_unavailable') return setErr(errNew, MSG.unavailable());
        if (code === 'too_many_requests') return setErr(errRequest, MSG.wait(r.data.retryAfterSeconds));
        if (code === 'mail_failed') return setErr(errRequest, MSG.mailFailed());
        if (code === 'stale_account') return setErr(errRequest, staleAccountText(MSG.failed()));
        setErr(errRequest, MSG.failed());
      })
      .catch(function () {
        setBusy(false);
        if (passwordEl) passwordEl.value = '';
        setErr(errRequest, MSG.failed());
      });
  });

  confirmForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if (inFlight) return;
    clearErrors();

    var code = String((codeEl && codeEl.value) || '').replace(/\s+/g, '');
    if (!code) return setErr(errCode, MSG.codeEmpty());
    if (!/^[0-9]{6}$/.test(code)) return setErr(errCode, MSG.codeFormat());

    setBusy(true);
    send('/auth/confirm-email-change.php', { code: code })
      .then(function (r) {
        if (r && r.status === 200 && r.data && r.data.ok === true) {
          try {
            sessionStorage.setItem('kpi-email-change-success', '1');
          } catch (_eFlag) {}
          window.location.href = 'change_email.html';
          return;
        }
        setBusy(false);
        if (codeEl) codeEl.value = '';
        if (!r) return setErr(errConfirmForm, MSG.failed());
        if (handleSessionLoss(r)) return;
        var err = (r.data && r.data.error) || '';
        if (err === 'code_invalid') {
          setErr(errCode, MSG.codeInvalid());
          if (codeEl) codeEl.focus();
          return;
        }
        if (err === 'code_expired' || err === 'code_locked') return setErr(errConfirmForm, MSG.codeExpired());
        if (err === 'email_unavailable') return setErr(errConfirmForm, MSG.unavailable());
        if (err === 'email_change_stale') return setErr(errConfirmForm, MSG.stale());
        if (err === 'stale_account') return setErr(errConfirmForm, staleAccountText(MSG.failed()));
        setErr(errConfirmForm, MSG.failed());
      })
      .catch(function () {
        setBusy(false);
        if (codeEl) codeEl.value = '';
        setErr(errConfirmForm, MSG.failed());
      });
  });

  if (backEl) {
    backEl.addEventListener('click', function (e) {
      e.preventDefault();
      if (inFlight) return;
      clearErrors();
      if (codeEl) codeEl.value = '';
      showStep('request');
      if (passwordEl) passwordEl.focus();
    });
  }
})();

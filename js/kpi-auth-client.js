/**
 * KPI Auth Client — Phase B1-T2
 * Session cookie (KPISESSID) against /api/v1/auth/*.php
 *
 * Override base:
 * - window.__KPI_AUTH_BASE = '/kpi-navigator/api/v1'
 * - meta[name="kpi-auth-api"] content="/kpi-navigator/api/v1"
 * - localStorage kpiNavigator.authBase
 */
(function (global) {
  'use strict';

  if (global.__KPI_AUTH && global.__KPI_AUTH.__ready) {
    return;
  }

  var REG_FLAG = 'kpiNavigator.registrationComplete';
  var AUTH_BASE_KEY = 'kpiNavigator.authBase';

  function resolveAppRoot() {
    var path = global.location.pathname || '';
    var m = path.match(/^(.*?\/kpi-navigator)(?:\/|$)/);
    if (m) return m[1];
    return '';
  }

  function resolveAuthBase() {
    try {
      if (global.__KPI_AUTH_BASE) return String(global.__KPI_AUTH_BASE).replace(/\/$/, '');
    } catch (_e0) {}
    try {
      var meta = document.querySelector('meta[name="kpi-auth-api"]');
      if (meta && meta.content) return String(meta.content).replace(/\/$/, '');
    } catch (_e1) {}
    try {
      var stored = localStorage.getItem(AUTH_BASE_KEY);
      if (stored) return String(stored).replace(/\/$/, '');
    } catch (_e2) {}
    return resolveAppRoot() + '/api/v1';
  }

  function setRegistrationComplete() {
    try {
      localStorage.setItem(REG_FLAG, '1');
    } catch (_e) {}
  }

  function request(method, path, body) {
    var url = resolveAuthBase() + path;
    var opts = {
      method: method,
      credentials: 'include',
      headers: {},
    };
    if (body != null) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    return fetch(url, opts).then(function (res) {
      return res.json().catch(function () {
        return { ok: false, error: 'invalid_response' };
      }).then(function (data) {
        return { status: res.status, data: data || { ok: false } };
      });
    });
  }

  function register(email, password) {
    return request('POST', '/auth/register.php', {
      email: email,
      password: password,
    }).then(function (r) {
      if (r.status === 201 && r.data && r.data.ok) {
        setRegistrationComplete();
      }
      return r;
    });
  }

  function login(email, password) {
    return request('POST', '/auth/login.php', {
      email: email,
      password: password,
    }).then(function (r) {
      if (r.status === 200 && r.data && r.data.ok) {
        setRegistrationComplete();
      }
      return r;
    });
  }

  function logout() {
    return request('POST', '/auth/logout.php', null);
  }

  function me() {
    return request('GET', '/auth/me.php', null);
  }

  function errorMessage(lang, status, data) {
    var code = (data && data.error) || '';
    var isJa = lang === 'ja';
    var isZh = lang === 'zh' || lang === 'zh-tw';
    if (code === 'email_taken') {
      if (isJa) return 'このメールアドレスは既に登録されています。';
      if (isZh) return '此電子郵件已被註冊。';
      return 'This email is already registered.';
    }
    if (code === 'invalid_credentials' || status === 401) {
      if (isJa) return 'メールアドレスまたはパスワードが正しくありません。';
      if (isZh) return '電子郵件或密碼不正確。';
      return 'Email or password is incorrect.';
    }
    if (code === 'invalid_email') {
      if (isJa) return 'メールアドレスの形式が正しくありません。';
      if (isZh) return '電子郵件格式不正確。';
      return 'Invalid email address.';
    }
    if (code === 'password_too_short') {
      if (isJa) return 'パスワードは8文字以上にしてください。';
      if (isZh) return '密碼至少需 8 個字元。';
      return 'Password must be at least 8 characters.';
    }
    if (isJa) return '通信エラーが発生しました。しばらくしてから再試行してください。';
    if (isZh) return '發生通訊錯誤，請稍後再試。';
    return 'A network error occurred. Please try again.';
  }

  global.__KPI_AUTH = {
    __ready: true,
    resolveAuthBase: resolveAuthBase,
    resolveAppRoot: resolveAppRoot,
    register: register,
    login: login,
    logout: logout,
    me: me,
    setRegistrationComplete: setRegistrationComplete,
    errorMessage: errorMessage,
  };
})(typeof window !== 'undefined' ? window : this);

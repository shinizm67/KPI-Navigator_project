/**
 * Checkout return pages. The success URL is not proof of subscription.
 * confirmed comes only from GET /billing/status.php.
 */
(function () {
  'use strict';

  var statusEl = document.getElementById('checkout-return-status');
  var loginEl = document.getElementById('checkout-return-login');
  var continueEl = document.getElementById('checkout-return-continue');
  var mode = document.body.getAttribute('data-checkout') || '';

  function lang() {
    var raw = '';
    try {
      raw = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
    } catch (_e) {}
    if (raw.indexOf('zh') === 0) return 'zh-tw';
    if (raw.indexOf('en') === 0) return 'en';
    return 'ja';
  }

  function t(ja, en, zh) {
    var code = lang();
    if (code === 'zh-tw') return zh;
    if (code === 'en') return en;
    return ja;
  }

  function paint(text) {
    if (statusEl) statusEl.textContent = text;
  }

  function show(el, on) {
    if (!el) return;
    el.hidden = !on;
  }

  if (mode !== 'success') return;

  try {
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, '', window.location.pathname);
    }
  } catch (_eHist) {}

  var auth = window.__KPI_AUTH;
  if (!auth || typeof auth.resolveAuthBase !== 'function') {
    show(loginEl, true);
    show(continueEl, false);
    paint(t(
      'お申し込みを受け付けました。契約状況はStripeから安全に確認されます。KPNへログインして続行してください。',
      'Your subscription request was received. Your billing status is verified securely through Stripe. Sign in to continue.',
      '已收到您的訂閱申請。合約狀態會透過 Stripe 安全確認。請登入 KPN 以繼續。'
    ));
    return;
  }

  var tries = 0;

  function tick() {
    window
      .fetch(auth.resolveAuthBase() + '/billing/status.php', {
        method: 'GET',
        credentials: 'include',
        cache: 'no-store',
      })
      .then(function (res) {
        return res.json().catch(function () {
          return { ok: false };
        }).then(function (data) {
          return { status: res.status, data: data || { ok: false } };
        });
      })
      .then(function (r) {
        if (r.status === 401 || r.status === 403) {
          show(loginEl, true);
          show(continueEl, false);
          paint(t(
            'お申し込みを受け付けました。契約状況はStripeから安全に確認されます。KPNへログインして続行してください。',
            'Your subscription request was received. Your billing status is verified securely through Stripe. Sign in to continue.',
            '已收到您的訂閱申請。合約狀態會透過 Stripe 安全確認。請登入 KPN 以繼續。'
          ));
          return;
        }
        show(loginEl, false);
        var billing = r.data && r.data.billing ? r.data.billing : null;
        if (billing && billing.confirmed === true && (billing.plan === 'basic' || billing.plan === 'pro')) {
          if (typeof auth.applyServerPlan === 'function' && r.data.plan) {
            auth.applyServerPlan(r.data.plan);
          }
          show(continueEl, true);
          var label = billing.plan === 'pro' ? t('プロ', 'Pro', '專業') : t('ベーシック', 'Basic', '基本');
          paint(t(
            'サブスクリプションを確認しました（' + label + '）。',
            'Subscription confirmed (' + label + ').',
            '已確認訂閱（' + label + '）。'
          ));
          return;
        }
        show(continueEl, false);
        tries += 1;
        if (tries < 8) {
          paint(t(
            '決済結果を確認しています。画面の移動だけでは契約は確定しません。',
            'Checking the payment result. Returning from Checkout does not confirm a subscription.',
            '正在確認付款結果。從結帳頁返回並不代表訂閱已成立。'
          ));
          window.setTimeout(tick, 2000);
          return;
        }
        paint(t(
          'まだ確定していません。反映まで少し時間がかかることがあります。プランはサーバーの通知で更新されます。',
          'Not confirmed yet. It can take a moment. The plan updates from the server notification.',
          '尚未確認。可能需要一點時間。方案會依伺服器通知更新。'
        ));
      })
      .catch(function () {
        paint(t(
          '確認できませんでした。プランはまだ変更されていません。',
          'Could not check the subscription. Your plan has not changed.',
          '無法確認訂閱。方案尚未變更。'
        ));
      });
  }

  paint(t(
    '決済結果を確認しています。画面の移動だけでは契約は確定しません。',
    'Checking the payment result. Returning from Checkout does not confirm a subscription.',
    '正在確認付款結果。從結帳頁返回並不代表訂閱已成立。'
  ));
  tick();
})();

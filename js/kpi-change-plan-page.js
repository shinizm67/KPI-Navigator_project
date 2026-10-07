/**
 * Change Plan page: live Current Plan from server / subscriptionTier.
 * Requires kpi-auth-client.js?v=20260923-c2c (loaded via site chrome header on this page).
 */
(function () {
  'use strict';

  var TIER_KEY = 'kpiNavigator.subscriptionTier';

  function pageLang() {
    try {
      var lang = String(document.documentElement.getAttribute('lang') || '')
        .trim()
        .toLowerCase();
      if (lang.indexOf('zh') === 0) return 'zh-tw';
      if (lang.indexOf('en') === 0) return 'en';
    } catch (_e) {}
    return 'ja';
  }

  function t(ja, en, zh) {
    var lang = pageLang();
    if (lang === 'zh-tw') return zh;
    if (lang === 'en') return en;
    return ja;
  }

  function readTier() {
    try {
      if (window.__KPI_AUTH && typeof window.__KPI_AUTH.readStoredTier === 'function') {
        var stored = String(window.__KPI_AUTH.readStoredTier() || '').trim().toLowerCase();
        if (stored === 'basic' || stored === 'pro') return stored;
        return '';
      }
    } catch (_e0) {}
    try {
      var raw = String(sessionStorage.getItem(TIER_KEY) || localStorage.getItem(TIER_KEY) || '')
        .trim()
        .toLowerCase();
      if (raw === 'basic' || raw === 'pro') return raw;
      return '';
    } catch (_e1) {
      return '';
    }
  }

  function setCellContent(el, html, asStatus) {
    if (!el) return;
    var parent = el.parentNode;
    if (!parent) return;
    var next;
    if (asStatus) {
      next = document.createElement('span');
      next.className = 'btn-register btn-plan-current';
      next.setAttribute('role', 'status');
      next.setAttribute('aria-label', html);
      next.textContent = html;
    } else {
      next = document.createElement('a');
      next.href = '#';
      next.className = 'btn-register btn-plan-downgrade';
      next.textContent = html;
    }
    next.id = el.id;
    parent.replaceChild(next, el);
  }

  function applyUi(tier) {
    var isPro = tier === 'pro';
    var tierEl = document.getElementById('change-plan-current-tier');
    var note = document.getElementById('change-plan-already-pro-note');
    var basicAction = document.getElementById('change-plan-basic-action');
    var proAction = document.getElementById('change-plan-pro-action');

    if (tierEl) {
      tierEl.textContent = isPro
        ? t('プロ', 'Pro', '專業')
        : t('ベーシック', 'Basic', '基本');
    }
    if (note) {
      note.hidden = !isPro;
    }

    if (isPro) {
      setCellContent(basicAction, '\u2014', true);
      setCellContent(
        proAction,
        t('現在のプラン', 'Current Plan', '目前方案'),
        true
      );
    } else {
      setCellContent(
        basicAction,
        t('現在のプラン', 'Current Plan', '目前方案'),
        true
      );
      setCellContent(
        proAction,
        t('プロを契約', 'Subscribe to Pro', '訂閱專業方案'),
        false
      );
    }
  }

  function statusEl() {
    var el = document.getElementById('stripe-checkout-status');
    if (el) return el;
    el = document.createElement('p');
    el.id = 'stripe-checkout-status';
    el.setAttribute('role', 'status');
    var anchor = document.getElementById('change-plan-current-tier');
    if (anchor && anchor.parentNode) anchor.parentNode.appendChild(el);
    else document.body.appendChild(el);
    return el;
  }

  function checkoutError(code) {
    if (code === 'unauthorized' || code === 'precondition_required') {
      return t('ログインが必要です。', 'Please sign in.', '請先登入。');
    }
    if (code === 'invalid_plan' || code === 'client_price_forbidden') {
      return t('プランを選択できません。', 'That plan cannot be selected.', '無法選擇此方案。');
    }
    if (code === 'already_subscribed') {
      return t(
        '契約中は、この画面から別のプランの決済を開始できません。',
        'A new checkout cannot be started from this page while a subscription is active.',
        '訂閱有效期間，無法在此頁面開始新的結帳。'
      );
    }
    if (code === 'not_configured') {
      return t('Stripe サンドボックスが未設定です。', 'Stripe sandbox is not configured.', '尚未設定 Stripe 沙箱。');
    }
    if (code === 'production_forbidden' || code === 'live_key_forbidden') {
      return t('本番環境では決済を開始できません。', 'Checkout cannot start on production.', '無法在正式環境開始結帳。');
    }
    return t('決済を開始できませんでした。', 'Checkout could not be started.', '無法開始結帳。');
  }

  function portalError(code) {
    if (code === 'unauthorized' || code === 'precondition_required') {
      return t('ログインが必要です。', 'Please sign in.', '請先登入。');
    }
    if (code === 'no_stripe_customer') {
      return t('まだお支払い情報はありません。', 'There is no billing profile yet.', '尚無付款資料。');
    }
    if (code === 'client_billing_forbidden') {
      return t('請求画面を開けません。', 'The billing page cannot be opened.', '無法開啟付款頁面。');
    }
    return t('支払い・契約の管理画面を開けませんでした。', 'The billing page could not be opened.', '無法開啟付款與訂閱管理頁面。');
  }

  function paintPortal(data) {
    var wrap = document.getElementById('change-plan-portal');
    var btn = document.getElementById('change-plan-portal-btn');
    if (!wrap || !btn) return;
    var billing = data && data.billing ? data.billing : {};
    btn.textContent = t('支払い・契約を管理', 'Manage billing & subscription', '管理付款與訂閱');
    wrap.hidden = billing.portalAvailable !== true;
  }

  var portalBusy = false;

  function beginPortal() {
    var auth = window.__KPI_AUTH;
    if (!auth || typeof auth.resolveAuthBase !== 'function' || typeof auth.attachExpectedUser !== 'function') {
      statusEl().textContent = portalError('unauthorized');
      return;
    }
    if (portalBusy) return;
    portalBusy = true;
    statusEl().textContent = t(
      '支払い・契約の管理画面へ移動しています。',
      'Opening the billing page.',
      '正在前往付款與訂閱管理頁面。'
    );
    var attached = auth.attachExpectedUser({}, { locale: pageLang() });
    window
      .fetch(auth.resolveAuthBase() + '/billing/portal-session.php', {
        method: 'POST',
        credentials: 'include',
        headers: Object.assign({ 'Content-Type': 'application/json' }, attached.headers),
        body: JSON.stringify(attached.body),
      })
      .then(function (res) {
        return res.json().catch(function () {
          return { ok: false, error: 'invalid_response' };
        }).then(function (data) {
          return { status: res.status, data: data || { ok: false } };
        });
      })
      .then(function (r) {
        portalBusy = false;
        var data = r.data || {};
        var url = typeof data.url === 'string' ? data.url : '';
        if (r.status === 200 && data.ok && url.indexOf('https://billing.stripe.com/') === 0) {
          window.location.assign(url);
          return;
        }
        statusEl().textContent = portalError(data.error || '');
      })
      .catch(function () {
        portalBusy = false;
        statusEl().textContent = portalError('');
      });
  }

  var checkoutBusy = false;

  function beginStripeCheckout(plan) {
    var auth = window.__KPI_AUTH;
    if (!auth || typeof auth.resolveAuthBase !== 'function' || typeof auth.attachExpectedUser !== 'function') {
      statusEl().textContent = checkoutError('unauthorized');
      return;
    }
    if (checkoutBusy) return;
    checkoutBusy = true;
    statusEl().textContent = t(
      'Stripe の決済画面へ移動しています。',
      'Redirecting to Stripe Checkout.',
      '正在前往 Stripe 結帳頁面。'
    );
    var attached = auth.attachExpectedUser({}, { plan: plan, locale: pageLang() });
    window
      .fetch(auth.resolveAuthBase() + '/billing/checkout-session.php', {
        method: 'POST',
        credentials: 'include',
        headers: Object.assign({ 'Content-Type': 'application/json' }, attached.headers),
        body: JSON.stringify(attached.body),
      })
      .then(function (res) {
        return res.json().catch(function () {
          return { ok: false, error: 'invalid_response' };
        }).then(function (data) {
          return { status: res.status, data: data || { ok: false } };
        });
      })
      .then(function (r) {
        checkoutBusy = false;
        var data = r.data || {};
        var url = typeof data.url === 'string' ? data.url : '';
        if (r.status === 200 && data.ok && url.indexOf('https://checkout.stripe.com/') === 0) {
          window.location.assign(url);
          return;
        }
        statusEl().textContent = checkoutError(data.error || '');
      })
      .catch(function () {
        checkoutBusy = false;
        statusEl().textContent = checkoutError('');
      });
  }

  function intervalLabel() {
    return t('月', 'month', '每月');
  }

  function offerHeading(planName, row) {
    if (!row || typeof row.formattedAmount !== 'string' || row.formattedAmount === '') return planName;
    return planName + ' ' + row.formattedAmount + ' / ' + intervalLabel();
  }

  function paintOffer(offer) {
    if (!offer || typeof offer !== 'object') return;
    var basic = document.getElementById('change-plan-basic-price');
    var pro = document.getElementById('change-plan-pro-price');
    if (basic) {
      basic.textContent = offerHeading(t('ベーシック', 'Basic', '基本'), offer.basic);
    }
    if (pro) {
      pro.textContent = offerHeading(t('プロ', 'Pro', '專業'), offer.pro);
    }
  }

  function paintSubscription(data) {
    var el = document.getElementById('change-plan-current-price');
    if (!el) return;
    var billing = data && data.billing ? data.billing : {};
    var price = billing.subscriptionPrice;
    if (billing.confirmed === true && price && price.known === true && price.formattedAmount) {
      el.textContent = price.formattedAmount + ' / ' + intervalLabel();
      return;
    }
    if (price && price.known === false) {
      el.textContent = t(
        '請求額を確認できません',
        'The billed amount cannot be confirmed.',
        '無法確認收費金額。'
      );
      return;
    }
    el.textContent = '—';
  }

  function loadServerPricing() {
    var auth = window.__KPI_AUTH;
    if (!auth || typeof auth.resolveAuthBase !== 'function') return;
    window
      .fetch(auth.resolveAuthBase() + '/billing/status.php', {
        method: 'GET',
        credentials: 'include',
        cache: 'no-store',
      })
      .then(function (res) {
        return res.json().catch(function () {
          return null;
        });
      })
      .then(function (data) {
        if (!data || data.ok !== true) return;
        paintOffer(data.offer);
        paintSubscription(data);
        paintPortal(data);
      })
      .catch(function () {});
  }

  function boot() {
    applyUi(readTier());
    function refresh() {
      applyUi(readTier());
    }
    window.addEventListener('kpi:planChanged', refresh);
    if (window.__KPI_AUTH && typeof window.__KPI_AUTH.syncPlanFromServer === 'function') {
      window.__KPI_AUTH.syncPlanFromServer().then(refresh).catch(refresh);
    }
    loadServerPricing();
    document.addEventListener('click', function (ev) {
      var node = ev.target && ev.target.closest ? ev.target.closest('#change-plan-basic-action, #change-plan-pro-action') : null;
      if (!node || String(node.tagName).toUpperCase() !== 'A') return;
      ev.preventDefault();
      beginStripeCheckout(node.id === 'change-plan-basic-action' ? 'basic' : 'pro');
    });
    document.addEventListener('click', function (ev) {
      var portalBtn = ev.target && ev.target.closest ? ev.target.closest('#change-plan-portal-btn') : null;
      if (!portalBtn) return;
      ev.preventDefault();
      beginPortal();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

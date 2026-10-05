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
      setCellContent(
        basicAction,
        t('ダウングレード', 'Down Grade Plan', '降級方案'),
        false
      );
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
        t('アップグレード', 'Upgrade Plan', '升級方案'),
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
        '有効なサブスクリプションがある間、このサンドボックスではプラン変更を開始できません。',
        'Plan changes cannot be started in this sandbox while a subscription is active.',
        '訂閱有效期間，此沙箱無法開始變更方案。'
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

  function boot() {
    applyUi(readTier());
    function refresh() {
      applyUi(readTier());
    }
    window.addEventListener('kpi:planChanged', refresh);
    if (window.__KPI_AUTH && typeof window.__KPI_AUTH.syncPlanFromServer === 'function') {
      window.__KPI_AUTH.syncPlanFromServer().then(refresh).catch(refresh);
    }
    document.addEventListener('click', function (ev) {
      var node = ev.target && ev.target.closest ? ev.target.closest('#change-plan-basic-action, #change-plan-pro-action') : null;
      if (!node || String(node.tagName).toUpperCase() !== 'A') return;
      ev.preventDefault();
      beginStripeCheckout(node.id === 'change-plan-basic-action' ? 'basic' : 'pro');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

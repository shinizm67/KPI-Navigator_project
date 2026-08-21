/**
 * Change Plan page: live Current Plan from server / subscriptionTier.
 * Requires kpi-auth-client.js (loaded via site chrome header on this page).
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
      if (window.__KPI_AUTH && typeof window.__KPI_AUTH.isBasicPlan === 'function') {
        return window.__KPI_AUTH.isBasicPlan() ? 'basic' : 'pro';
      }
    } catch (_e0) {}
    try {
      var raw = sessionStorage.getItem(TIER_KEY) || localStorage.getItem(TIER_KEY) || 'pro';
      return String(raw).toLowerCase() === 'basic' ? 'basic' : 'pro';
    } catch (_e1) {
      return 'pro';
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
    var isPro = tier !== 'basic';
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

  function boot() {
    applyUi(readTier());
    function refresh() {
      applyUi(readTier());
    }
    window.addEventListener('kpi:planChanged', refresh);
    if (window.__KPI_AUTH && typeof window.__KPI_AUTH.syncPlanFromServer === 'function') {
      window.__KPI_AUTH.syncPlanFromServer().then(refresh).catch(refresh);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

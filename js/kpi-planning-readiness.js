/**
 * Planning Readiness / KPI Setup Status
 * Spec: docs/planning-readiness.md
 *
 * Seasonality contract (runtime-confirmed):
 * - Stored: years[YYYY].plan.monthlyHlWeights (length 12)
 * - Default seed: [85,85,100,110,120,85,100,100,100,110,110,115] (NOT all-100)
 * - Structural validity: each value integer 60–200, multiple of 5
 * - Alloc UI OK: average of 12 months ≈ 100% (|avg-100| < 0.01)
 * - No auto-adjust of weights
 */
(function (global) {
  'use strict';

  if (global.KpiPlanningReadiness && global.KpiPlanningReadiness.__ready) {
    return;
  }

  var STATE = { NOT_READY: 'NOT_READY', PROVISIONAL: 'PROVISIONAL', READY: 'READY' };
  var DEFAULT_HL_WEIGHTS = [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115];
  var ALL_100 = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100];
  var BODY_PROVISIONAL = 'kpi-pr-provisional';
  var BODY_NOT_READY = 'kpi-pr-not-ready';
  var SESSION_ALERT_KEY = 'kpi.pr.pageAlert.';
  var CSS_ID = 'kpi-planning-readiness-css';

  function pageLang() {
    try {
      var lang = String(
        (document.documentElement && document.documentElement.getAttribute('lang')) || ''
      ).toLowerCase();
      if (lang.indexOf('zh') === 0) return 'zh';
      if (lang.indexOf('en') === 0) return 'en';
      return 'ja';
    } catch (_e) {
      return 'ja';
    }
  }

  function t(key) {
    var lang = pageLang();
    var table = {
      ja: {
        confirmBd: '営業日設定を確定',
        confirmSeason: '月次配分を確定',
        bdAllOpenTitle: '営業日設定の確認',
        bdAllOpenBody:
          '年間の全日が営業日として設定されています。\nこの設定でよろしいですか？',
        bdConfirm: 'このまま確定',
        bdEdit: '営業日を編集',
        seasonDefaultTitle: '月次配分の確認',
        seasonDefaultBody:
          '月次配分は現在デフォルト設定です。\nこの設定を使用しますか？',
        seasonConfirm: 'このまま確定',
        seasonAdjust: '調整する',
        seasonInvalid:
          '月次配分が正式条件（各月の平均が100%）を満たしていないため確定できません。',
        alertTitle: 'KPI設定に未確定項目があります。',
        alertBody: '現在表示している目標値は暫定値です。',
        reasonAnnual: '年次目標売上',
        reasonBd: '営業日設定',
        reasonSeason: '月次配分',
        tipTitle: '暫定目標値',
        tipBody:
          'KPI設定が完了していないため、\nこの目標値は暫定計算です。',
        tipUnset: '未確定:',
        dismiss: '閉じる',
        goSettings: '設定を確認する',
      },
      en: {
        confirmBd: 'Confirm business days',
        confirmSeason: 'Confirm monthly allocation',
        bdAllOpenTitle: 'Confirm business days',
        bdAllOpenBody:
          'Every day of the year is marked as a business day.\nIs this correct?',
        bdConfirm: 'Confirm as-is',
        bdEdit: 'Edit business days',
        seasonDefaultTitle: 'Confirm monthly allocation',
        seasonDefaultBody:
          'Monthly allocation is currently the default.\nUse this setting?',
        seasonConfirm: 'Confirm as-is',
        seasonAdjust: 'Adjust',
        seasonInvalid:
          'Monthly allocation does not meet the formal rule (monthly average ≈ 100%).',
        alertTitle: 'KPI setup has unconfirmed items.',
        alertBody: 'Displayed target values are provisional.',
        reasonAnnual: 'Annual target sales',
        reasonBd: 'Business days',
        reasonSeason: 'Monthly allocation',
        tipTitle: 'Provisional target',
        tipBody:
          'KPI setup is incomplete.\nThis target is a provisional calculation.',
        tipUnset: 'Unconfirmed:',
        dismiss: 'Close',
        goSettings: 'Review settings',
      },
      zh: {
        confirmBd: '確認營業日設定',
        confirmSeason: '確認月次配分',
        bdAllOpenTitle: '確認營業日設定',
        bdAllOpenBody: '全年每日皆設為營業日。\n確定使用此設定嗎？',
        bdConfirm: '維持並確認',
        bdEdit: '編輯營業日',
        seasonDefaultTitle: '確認月次配分',
        seasonDefaultBody: '月次配分目前為預設設定。\n要使用此設定嗎？',
        seasonConfirm: '維持並確認',
        seasonAdjust: '調整',
        seasonInvalid: '月次配分未符合正式條件（各月平均約 100%），無法確認。',
        alertTitle: 'KPI 設定尚有未確認項目。',
        alertBody: '目前顯示的目標值為暫定值。',
        reasonAnnual: '年度目標營業額',
        reasonBd: '營業日設定',
        reasonSeason: '月次配分',
        tipTitle: '暫定目標值',
        tipBody: 'KPI 設定尚未完成。\n此目標值為暫定計算。',
        tipUnset: '未確認：',
        dismiss: '關閉',
        goSettings: '前往設定',
      },
    };
    return (table[lang] || table.ja)[key] || (table.ja[key] || key);
  }

  function storeApi() {
    return global.KpiYearStore || null;
  }

  function operatingYear() {
    var api = storeApi();
    if (api && typeof api.getOperatingYear === 'function') {
      var y = Number(api.getOperatingYear());
      if (Number.isFinite(y)) return y;
    }
    return new Date().getFullYear();
  }

  function ensurePrRecord(year) {
    var api = storeApi();
    if (!api || typeof api.getStore !== 'function') return null;
    var store = api.getStore();
    if (!store || !store.years) return null;
    var y = Number(year);
    if (!Number.isFinite(y)) return null;
    if (!store.years[y]) store.years[y] = { year: y, status: 'open', plan: {} };
    if (!store.years[y].planningReadiness || typeof store.years[y].planningReadiness !== 'object') {
      store.years[y].planningReadiness = {};
    }
    return store.years[y].planningReadiness;
  }

  function persistStoreQuiet() {
    var api = storeApi();
    if (!api || typeof api.getStore !== 'function') return;
    try {
      var raw = JSON.stringify(api.getStore());
      localStorage.setItem('kpiNavigator.kpiYearStore', raw);
    } catch (_e) {}
    try {
      if (typeof api.syncLegacyKeys === 'function') api.syncLegacyKeys();
    } catch (_e2) {}
  }

  function fnv1a(str) {
    var h = 2166136261;
    for (var i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(16);
  }

  function pad2(n) {
    return n < 10 ? '0' + n : String(n);
  }

  function isUiBusinessDay(iso) {
    var api = storeApi();
    if (api && typeof api.isUiBusinessDay === 'function') return !!api.isUiBusinessDay(iso);
    if (api && typeof api.readBusinessDay === 'function') {
      var flag = api.readBusinessDay(iso);
      if (flag === false) return false;
      return true;
    }
    return true;
  }

  function businessDaysSignature(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) return '';
    var parts = [];
    for (var m0 = 0; m0 < 12; m0++) {
      var dc = new Date(y, m0 + 1, 0).getDate();
      for (var d = 1; d <= dc; d++) {
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(d);
        parts.push(isUiBusinessDay(iso) ? '1' : '0');
      }
    }
    return 'bd:' + y + ':' + fnv1a(parts.join(''));
  }

  function countOpenDays(year) {
    var y = Number(year);
    var open = 0;
    var total = 0;
    for (var m0 = 0; m0 < 12; m0++) {
      var dc = new Date(y, m0 + 1, 0).getDate();
      for (var d = 1; d <= dc; d++) {
        total++;
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(d);
        if (isUiBusinessDay(iso)) open++;
      }
    }
    return { open: open, total: total };
  }

  function normalizeHlWeights(weights) {
    var api = storeApi();
    if (api && typeof api.normalizeHlWeights === 'function') {
      return api.normalizeHlWeights(weights);
    }
    if (!weights || weights.length !== 12) return null;
    var out = [];
    for (var i = 0; i < 12; i++) {
      var n = Number(weights[i]);
      if (!Number.isFinite(n) || !Number.isInteger(n) || n % 5 !== 0 || n < 60 || n > 200) {
        return null;
      }
      out.push(n);
    }
    return out;
  }

  function readHlWeights(year) {
    var api = storeApi();
    if (api && typeof api.readMonthlyHlWeights === 'function') {
      var w = api.readMonthlyHlWeights(year);
      var norm = normalizeHlWeights(w);
      if (norm) return norm;
    }
    return DEFAULT_HL_WEIGHTS.slice();
  }

  function seasonalitySignature(year) {
    var w = readHlWeights(year);
    return 'hl:' + Number(year) + ':' + w.join(',');
  }

  function allocTotal(weights) {
    if (!weights || weights.length !== 12) return null;
    var sum = 0;
    for (var i = 0; i < 12; i++) {
      var n = Number(weights[i]);
      sum += Number.isFinite(n) ? n : 100;
    }
    return Math.round((sum / 12) * 100) / 100;
  }

  function isAllocTotalOk(weights) {
    var total = allocTotal(weights);
    return total != null && Math.abs(total - 100) < 0.01;
  }

  function weightsEqual(a, b) {
    if (!a || !b || a.length !== 12 || b.length !== 12) return false;
    for (var i = 0; i < 12; i++) {
      if (Number(a[i]) !== Number(b[i])) return false;
    }
    return true;
  }

  function isDefaultSeasonality(weights) {
    return weightsEqual(weights, DEFAULT_HL_WEIGHTS) || weightsEqual(weights, ALL_100);
  }

  function hasAnnualTarget(year) {
    var api = storeApi();
    if (api && typeof api.hasSavedAnnualPlanTarget === 'function') {
      if (api.hasSavedAnnualPlanTarget(year)) return true;
    }
    if (api && typeof api.readAnnualTarget === 'function') {
      var n = Number(api.readAnnualTarget(year));
      return Number.isFinite(n) && n > 0;
    }
    return false;
  }

  function evaluate(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var pr = ensurePrRecord(y) || {};
    var annualOk = hasAnnualTarget(y);
    var bdCur = businessDaysSignature(y);
    var hlCur = seasonalitySignature(y);
    var bdSaved = pr.businessDaysConfirmedSignature || null;
    var hlSaved = pr.seasonalityConfirmedSignature || null;

    var bdStatus = 'unconfirmed';
    if (bdSaved) {
      bdStatus = bdSaved === bdCur ? 'confirmed' : 'changed';
    }
    var seasonStatus = 'unconfirmed';
    var weights = readHlWeights(y);
    var structural = normalizeHlWeights(weights);
    if (!structural) {
      seasonStatus = 'invalid';
    } else if (hlSaved) {
      seasonStatus = hlSaved === hlCur ? 'confirmed' : 'changed';
    }

    var missingReasons = [];
    var provisionalReasons = [];
    var state = STATE.READY;

    if (!annualOk) {
      state = STATE.NOT_READY;
      missingReasons.push('annualTarget');
    } else {
      if (bdStatus !== 'confirmed') {
        provisionalReasons.push(bdStatus === 'changed' ? 'businessDaysChanged' : 'businessDays');
      }
      if (seasonStatus !== 'confirmed') {
        if (seasonStatus === 'invalid') provisionalReasons.push('seasonalityInvalid');
        else if (seasonStatus === 'changed') provisionalReasons.push('seasonalityChanged');
        else provisionalReasons.push('seasonality');
      }
      if (provisionalReasons.length) state = STATE.PROVISIONAL;
    }

    return {
      state: state,
      year: y,
      annualTarget: annualOk ? 'ready' : 'missing',
      businessDays: bdStatus,
      seasonality: seasonStatus,
      missingReasons: missingReasons,
      provisionalReasons: provisionalReasons,
      businessDaysCurrentSignature: bdCur,
      seasonalityCurrentSignature: hlCur,
      isDefaultSeasonality: isDefaultSeasonality(weights),
      allocTotalOk: isAllocTotalOk(weights),
      openDayCount: countOpenDays(y),
    };
  }

  function confirmBusinessDays(year, opts) {
    opts = opts || {};
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var counts = countOpenDays(y);
    if (counts.open === counts.total && !opts.skipAllOpenPrompt) {
      return { needAllOpenConfirm: true, counts: counts };
    }
    var pr = ensurePrRecord(y);
    if (!pr) return { ok: false };
    pr.businessDaysConfirmedSignature = businessDaysSignature(y);
    pr.businessDaysConfirmedAt = Date.now();
    pr.businessDaysVisited = true;
    persistStoreQuiet();
    emitChanged(y);
    return { ok: true };
  }

  function canConfirmSeasonality(year) {
    var weights = readHlWeights(year);
    if (!normalizeHlWeights(weights)) return false;
    if (isDefaultSeasonality(weights)) return true;
    return isAllocTotalOk(weights);
  }

  function confirmSeasonality(year, opts) {
    opts = opts || {};
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var weights = readHlWeights(y);
    if (!normalizeHlWeights(weights)) return { ok: false, reason: 'invalid' };
    var isDefault = isDefaultSeasonality(weights);
    if (!isDefault && !isAllocTotalOk(weights)) {
      return { ok: false, reason: 'alloc' };
    }
    if (isDefault && !opts.skipDefaultPrompt) {
      return { needDefaultConfirm: true };
    }
    var pr = ensurePrRecord(y);
    if (!pr) return { ok: false };
    pr.seasonalityConfirmedSignature = seasonalitySignature(y);
    pr.seasonalityConfirmedAt = Date.now();
    pr.seasonalityVisited = true;
    persistStoreQuiet();
    emitChanged(y);
    return { ok: true };
  }

  function markVisited(year, which) {
    var pr = ensurePrRecord(year);
    if (!pr) return;
    if (which === 'businessDays') pr.businessDaysVisited = true;
    if (which === 'seasonality') pr.seasonalityVisited = true;
    persistStoreQuiet();
  }

  function emitChanged(year) {
    try {
      document.dispatchEvent(
        new CustomEvent('kpi:planningReadinessChanged', {
          detail: { year: Number(year), snapshot: evaluate(year) },
        })
      );
    } catch (_e) {}
    applyBodyState();
    refreshTooltips();
  }

  function applyBodyState() {
    var snap = evaluate(operatingYear());
    document.body.classList.remove(BODY_PROVISIONAL, BODY_NOT_READY);
    if (snap.state === STATE.PROVISIONAL) document.body.classList.add(BODY_PROVISIONAL);
    if (snap.state === STATE.NOT_READY) document.body.classList.add(BODY_NOT_READY);
  }

  function ensureCss() {
    if (document.getElementById(CSS_ID)) return;
    var style = document.createElement('style');
    style.id = CSS_ID;
    style.textContent =
      'body.kpi-pr-provisional .annual-daily-row__cell--plan-target,' +
      'body.kpi-pr-provisional .monthly-data-column__cell--plan-target,' +
      'body.kpi-pr-provisional .monthly-vfocus-cell--plan-target,' +
      'body.kpi-pr-provisional .kpi-pr-target-warn {' +
      '  box-shadow: inset 0 0 0 1.5px rgba(198, 90, 50, 0.55);' +
      '  background-color: rgba(198, 90, 50, 0.10);' +
      '  color: #a14a2e;' +
      '}' +
      'body.office-mode.kpi-pr-provisional .annual-daily-row__cell--plan-target,' +
      'body.office-mode.kpi-pr-provisional .monthly-data-column__cell--plan-target,' +
      'body.office-mode.kpi-pr-provisional .monthly-vfocus-cell--plan-target,' +
      'body.office-mode.kpi-pr-provisional .kpi-pr-target-warn {' +
      '  box-shadow: inset 0 0 0 1.5px rgba(183, 84, 48, 0.5);' +
      '  background-color: rgba(183, 84, 48, 0.08);' +
      '  color: #8d3f28;' +
      '}' +
      '.kpi-pr-alert {' +
      '  position: fixed; z-index: 12000; left: 50%; top: 72px; transform: translateX(-50%);' +
      '  width: min(440px, calc(100vw - 32px)); padding: 16px 18px; border-radius: 10px;' +
      '  background: #fff8f4; border: 1px solid rgba(198, 90, 50, 0.45);' +
      '  box-shadow: 0 10px 28px rgba(0,0,0,0.18); color: #4a2c22; font-size: 14px; line-height: 1.45;' +
      '}' +
      '.kpi-pr-alert__title { font-weight: 700; margin: 0 0 6px; }' +
      '.kpi-pr-alert__list { margin: 8px 0 12px; padding-left: 1.2em; }' +
      '.kpi-pr-alert__actions { display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap; }' +
      '.kpi-pr-alert button { cursor: pointer; border-radius: 6px; border: 1px solid #c65a32; background: #fff; color: #a14a2e; padding: 6px 12px; }' +
      '.kpi-pr-alert button.kpi-pr-alert__primary { background: #c65a32; color: #fff; }' +
      '.kpi-pr-sdm-bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0; }' +
      '.kpi-pr-sdm-bar button { cursor: pointer; border-radius: 6px; border: 1px solid #c65a32; background: #fff8f4; color: #a14a2e; padding: 6px 10px; font-size: 12px; }' +
      '.kpi-pr-dialog-back { position: fixed; inset: 0; z-index: 13000; background: rgba(0,0,0,0.35); }' +
      '.kpi-pr-dialog { position: fixed; z-index: 13001; left: 50%; top: 50%; transform: translate(-50%,-50%);' +
      '  width: min(420px, calc(100vw - 32px)); background: #fff; border-radius: 12px; padding: 18px 20px;' +
      '  box-shadow: 0 16px 40px rgba(0,0,0,0.25); }' +
      '.kpi-pr-dialog h3 { margin: 0 0 8px; font-size: 16px; }' +
      '.kpi-pr-dialog p { margin: 0 0 14px; white-space: pre-line; font-size: 14px; line-height: 1.45; }' +
      '.kpi-pr-dialog__actions { display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap; }' +
      '.kpi-pr-dialog button { cursor: pointer; border-radius: 6px; border: 1px solid #888; background: #fff; padding: 6px 12px; }' +
      '.kpi-pr-dialog button.primary { border-color: #c65a32; background: #c65a32; color: #fff; }';
    document.head.appendChild(style);
  }

  function reasonLabels(snap) {
    var labels = [];
    if (snap.annualTarget === 'missing') labels.push(t('reasonAnnual'));
    if (snap.businessDays !== 'confirmed') labels.push(t('reasonBd'));
    if (snap.seasonality !== 'confirmed') labels.push(t('reasonSeason'));
    return labels;
  }

  function tooltipText(snap) {
    var lines = [t('tipTitle'), t('tipBody'), '', t('tipUnset')];
    reasonLabels(snap).forEach(function (lab) {
      lines.push('・' + lab);
    });
    return lines.join('\n');
  }

  function refreshTooltips() {
    var snap = evaluate(operatingYear());
    var tip = snap.state === STATE.READY ? '' : tooltipText(snap);
    var nodes = document.querySelectorAll(
      '.annual-daily-focus-bar-lower__cell.kpi-pr-tip-host,' +
        '.annual-daily-focus-bar-upper__cell.kpi-pr-tip-host,' +
        '.monthly-vfocus-cell--plan-target,' +
        '.daily-overlay__daily-kpi .daily-overlay__kpi-row:nth-child(2) .daily-overlay__daily-value-box,' +
        '.insight-daily-kpi .insight-daily-kpi__row:nth-child(2) .insight-daily-kpi__value'
    );
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (tip) {
        el.setAttribute('title', tip);
        el.classList.add('kpi-pr-target-warn');
      } else {
        el.removeAttribute('title');
        el.classList.remove('kpi-pr-target-warn');
      }
    }
    // Focus Bar: mark 目標売上 cell hosts once
    markFocusBarTipHosts();
  }

  function markFocusBarTipHosts() {
    var bars = document.querySelectorAll(
      '.annual-daily-focus-bar-lower, .annual-daily-focus-bar-upper, .monthly-vfocus'
    );
    for (var b = 0; b < bars.length; b++) {
      var cells = bars[b].querySelectorAll(
        '.annual-daily-focus-bar-lower__cell, .annual-daily-focus-bar-upper__cell, .monthly-vfocus-cell'
      );
      for (var i = 0; i < cells.length; i++) {
        var label = (cells[i].textContent || '').replace(/\s+/g, '');
        if (
          label.indexOf('目標売上') >= 0 ||
          label.indexOf('Target') >= 0 ||
          label.indexOf('目標營業額') >= 0 ||
          cells[i].classList.contains('monthly-vfocus-cell--plan-target')
        ) {
          cells[i].classList.add('kpi-pr-tip-host');
        }
      }
    }
  }

  function showDialog(title, body, primaryLabel, secondaryLabel, onPrimary, onSecondary) {
    var back = document.createElement('div');
    back.className = 'kpi-pr-dialog-back';
    var dlg = document.createElement('div');
    dlg.className = 'kpi-pr-dialog';
    dlg.setAttribute('role', 'dialog');
    dlg.innerHTML =
      '<h3></h3><p></p><div class="kpi-pr-dialog__actions">' +
      '<button type="button" class="secondary"></button>' +
      '<button type="button" class="primary"></button></div>';
    dlg.querySelector('h3').textContent = title;
    dlg.querySelector('p').textContent = body;
    var btnSec = dlg.querySelector('.secondary');
    var btnPri = dlg.querySelector('.primary');
    btnSec.textContent = secondaryLabel;
    btnPri.textContent = primaryLabel;
    function close() {
      back.remove();
      dlg.remove();
    }
    btnSec.addEventListener('click', function () {
      close();
      if (onSecondary) onSecondary();
    });
    btnPri.addEventListener('click', function () {
      close();
      if (onPrimary) onPrimary();
    });
    back.addEventListener('click', close);
    document.body.appendChild(back);
    document.body.appendChild(dlg);
  }

  function openSalesDataModal() {
    var btn =
      document.getElementById('annual-sales-data-open') ||
      document.getElementById('sales-data-open') ||
      document.querySelector('[data-open-sales-data]');
    if (btn) {
      try {
        btn.click();
      } catch (_e) {}
    }
  }

  function runConfirmBusinessDays() {
    var y = operatingYear();
    markVisited(y, 'businessDays');
    var res = confirmBusinessDays(y);
    if (res && res.needAllOpenConfirm) {
      showDialog(
        t('bdAllOpenTitle'),
        t('bdAllOpenBody'),
        t('bdConfirm'),
        t('bdEdit'),
        function () {
          confirmBusinessDays(y, { skipAllOpenPrompt: true });
        },
        function () {
          openSalesDataModal();
        }
      );
      return;
    }
  }

  function runConfirmSeasonality() {
    var y = operatingYear();
    markVisited(y, 'seasonality');
    var res = confirmSeasonality(y);
    if (res && res.needDefaultConfirm) {
      showDialog(
        t('seasonDefaultTitle'),
        t('seasonDefaultBody'),
        t('seasonConfirm'),
        t('seasonAdjust'),
        function () {
          confirmSeasonality(y, { skipDefaultPrompt: true });
        },
        function () {
          openSalesDataModal();
          try {
            var tab = document.querySelector('.sales-data-modal__tab[data-sdm-tab="analyze"]');
            if (tab) tab.click();
          } catch (_e) {}
        }
      );
      return;
    }
    if (res && res.ok === false) {
      try {
        window.alert(t('seasonInvalid'));
      } catch (_a) {}
    }
  }

  function mountSdmConfirmBar() {
    var modal = document.getElementById('sales-data-modal');
    if (!modal || modal.querySelector('.kpi-pr-sdm-bar')) return;
    var saveBtn = document.getElementById('sales-data-modal-save');
    if (!saveBtn || !saveBtn.parentNode) return;
    var bar = document.createElement('div');
    bar.className = 'kpi-pr-sdm-bar';
    bar.setAttribute('data-kpi-guard-ignore', '');
    var bdBtn = document.createElement('button');
    bdBtn.type = 'button';
    bdBtn.textContent = t('confirmBd');
    bdBtn.addEventListener('click', runConfirmBusinessDays);
    var seBtn = document.createElement('button');
    seBtn.type = 'button';
    seBtn.textContent = t('confirmSeason');
    seBtn.addEventListener('click', runConfirmSeasonality);
    bar.appendChild(bdBtn);
    bar.appendChild(seBtn);
    saveBtn.parentNode.insertBefore(bar, saveBtn);
  }

  function showPageEntryAlert(force) {
    var snap = evaluate(operatingYear());
    if (snap.state === STATE.READY) return;
    var key = SESSION_ALERT_KEY + snap.year + '.' + snap.state + '.' + (location.pathname || '');
    if (!force) {
      try {
        if (sessionStorage.getItem(key) === '1') return;
      } catch (_e) {}
    }
    if (document.querySelector('.kpi-pr-alert')) return;
    var alert = document.createElement('div');
    alert.className = 'kpi-pr-alert';
    alert.setAttribute('role', 'status');
    var list = reasonLabels(snap)
      .map(function (x) {
        return '<li>' + x + '</li>';
      })
      .join('');
    alert.innerHTML =
      '<p class="kpi-pr-alert__title"></p><p class="kpi-pr-alert__body"></p>' +
      '<ul class="kpi-pr-alert__list"></ul>' +
      '<div class="kpi-pr-alert__actions">' +
      '<button type="button" class="kpi-pr-alert__dismiss"></button>' +
      '<button type="button" class="kpi-pr-alert__primary"></button></div>';
    alert.querySelector('.kpi-pr-alert__title').textContent = t('alertTitle');
    alert.querySelector('.kpi-pr-alert__body').textContent = t('alertBody');
    alert.querySelector('.kpi-pr-alert__list').innerHTML = list;
    alert.querySelector('.kpi-pr-alert__dismiss').textContent = t('dismiss');
    alert.querySelector('.kpi-pr-alert__primary').textContent = t('goSettings');
    alert.querySelector('.kpi-pr-alert__dismiss').addEventListener('click', function () {
      alert.remove();
      try {
        sessionStorage.setItem(key, '1');
      } catch (_e2) {}
    });
    alert.querySelector('.kpi-pr-alert__primary').addEventListener('click', function () {
      alert.remove();
      try {
        sessionStorage.setItem(key, '1');
      } catch (_e3) {}
      openSalesDataModal();
    });
    document.body.appendChild(alert);
  }

  function bindListeners() {
    [
      'kpi:businessDayChanged',
      'kpi:annualPlanChanged',
      'kpi:weekdayBaselineChanged',
      'kpi:dailyTargetModeChanged',
      'annual:salesDataSaved',
      'annual:pastSalesSaved',
      'kpi:planningReadinessChanged',
    ].forEach(function (ev) {
      document.addEventListener(ev, function () {
        applyBodyState();
        refreshTooltips();
      });
    });
    document.addEventListener('insight:dateChanged', refreshTooltips);
    document.addEventListener('annual:dailyDateChanged', refreshTooltips);
  }

  function boot() {
    ensureCss();
    applyBodyState();
    mountSdmConfirmBar();
    refreshTooltips();
    bindListeners();
    // page-entry alert once per session path+state
    setTimeout(function () {
      showPageEntryAlert(false);
    }, 700);
    // remount SDM bar when modal opens
    var obs = new MutationObserver(function () {
      if (document.body.classList.contains('sales-data-modal-open')) {
        mountSdmConfirmBar();
        markVisited(operatingYear(), 'businessDays');
      }
    });
    try {
      obs.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    } catch (_o) {}
  }

  var api = {
    __ready: true,
    STATE: STATE,
    DEFAULT_HL_WEIGHTS: DEFAULT_HL_WEIGHTS.slice(),
    evaluate: evaluate,
    confirmBusinessDays: confirmBusinessDays,
    confirmSeasonality: confirmSeasonality,
    canConfirmSeasonality: canConfirmSeasonality,
    businessDaysSignature: businessDaysSignature,
    seasonalitySignature: seasonalitySignature,
    isDefaultSeasonality: isDefaultSeasonality,
    isAllocTotalOk: isAllocTotalOk,
    normalizeHlWeights: normalizeHlWeights,
    showPageEntryAlert: showPageEntryAlert,
    applyBodyState: applyBodyState,
    refreshTooltips: refreshTooltips,
    runConfirmBusinessDays: runConfirmBusinessDays,
    runConfirmSeasonality: runConfirmSeasonality,
  };

  global.KpiPlanningReadiness = api;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})(typeof window !== 'undefined' ? window : this);

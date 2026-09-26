/**
 * Planning Readiness / KPI Setup Status
 * Spec: docs/planning-readiness.md
 *
 * Seasonality modes:
 * - AUTO: KPN Recommended (Reference → 5% snap → sum 1200). Ready when valid.
 * - MANUAL: user HL edits. Ready only if valid AND (matches recommendation OR
 *   deviation explicitly confirmed). Never overwrite MANUAL with AUTO silently.
 *
 * Reference Seasonality formula is NOT redefined here — uses
 * KpiYearStore.computeAverageSeasonalityPct (selected baseline years' monthlyPct mean).
 * Projection algorithm: KpiSeasonalityAllocator.projectAndBalance.
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
  var CSS_ID = 'kpi-planning-readiness-css';
  var ALERT_ID = 'kpi-pr-alert-fw';
  var pageAlertDismissed = false;
  var completeTimer = null;

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
        editBd: '編集する',
        adjustSeason: '調整する',
        bdAllOpenTitle: '営業日設定の確認',
        bdAllOpenBody:
          '年間365日すべて営業日として設定されています。\nこの設定でよろしいですか？',
        bdConfirm: 'このまま確定',
        bdEdit: '営業日を編集',
        seasonDefaultTitle: '月次配分の確認',
        seasonDefaultBody:
          '月次配分は現在デフォルト設定です。\nこの設定を使用しますか？',
        seasonConfirm: 'このまま確定',
        seasonAdjust: '調整する',
        seasonInvalid:
          '月次配分の設定が確定条件を満たしていません。\n調整後に再度確定してください。',
        alertTitle: 'KPI設定に未確定項目があります。',
        alertBody: '現在表示している目標値は暫定値です。',
        alertDone: 'KPI設定が完了しました。',
        reasonAnnual: '年次目標売上',
        reasonBd: '営業日設定',
        reasonSeason: '月次配分',
        tipTitle: '暫定目標値',
        tipBody: 'KPI設定が完了していないため、\nこの目標値は暫定計算です。',
        tipUnset: '未確定:',
        seasonDeviationBody: 'KPN推奨の月次配分と異なる設定があります。',
        seasonConfirmOverride: 'この配分で確定',
        seasonRestoreRecommended: '推奨配分に戻す',
        seasonModeAuto: 'AUTO',
        seasonModeManual: 'MANUAL',
        dismiss: '閉じる',
        anomalyAllocTip:
          '選択中のベースライン年に、過去の繁閑パターンから大きく乖離した年度があります。\nベースライン年設定を確認してください。',
        anomalyAllocAria: '繁閑パターン乖離の警告',
      },
      en: {
        confirmBd: 'Confirm business days',
        confirmSeason: 'Confirm monthly allocation',
        editBd: 'Edit',
        adjustSeason: 'Adjust',
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
          'Monthly allocation does not meet confirmation requirements.\nAdjust and confirm again.',
        alertTitle: 'KPI setup has unconfirmed items.',
        alertBody: 'Displayed target values are provisional.',
        alertDone: 'KPI setup is complete.',
        reasonAnnual: 'Annual target sales',
        reasonBd: 'Business days',
        reasonSeason: 'Monthly allocation',
        tipTitle: 'Provisional target',
        tipBody: 'KPI setup is incomplete.\nThis target is a provisional calculation.',
        tipUnset: 'Unconfirmed:',
        seasonDeviationBody: 'Monthly allocation differs from the KPN recommendation.',
        seasonConfirmOverride: 'Confirm this allocation',
        seasonRestoreRecommended: 'Restore recommended',
        seasonModeAuto: 'AUTO',
        seasonModeManual: 'MANUAL',
        dismiss: 'Close',
        anomalyAllocTip:
          'A selected baseline year diverges sharply from past seasonality patterns.\nReview baseline year settings.',
        anomalyAllocAria: 'Seasonality pattern divergence warning',
      },
      zh: {
        confirmBd: '確認營業日設定',
        confirmSeason: '確認月次配分',
        editBd: '編輯',
        adjustSeason: '調整',
        bdAllOpenTitle: '確認營業日設定',
        bdAllOpenBody: '全年每日皆設為營業日。\n確定使用此設定嗎？',
        bdConfirm: '維持並確認',
        bdEdit: '編輯營業日',
        seasonDefaultTitle: '確認月次配分',
        seasonDefaultBody: '月次配分目前為預設設定。\n要使用此設定嗎？',
        seasonConfirm: '維持並確認',
        seasonAdjust: '調整',
        seasonInvalid: '月次配分未符合確認條件。\n請調整後再次確認。',
        alertTitle: 'KPI 設定尚有未確認項目。',
        alertBody: '目前顯示的目標值為暫定值。',
        alertDone: 'KPI 設定已完成。',
        reasonAnnual: '年度目標營業額',
        reasonBd: '營業日設定',
        reasonSeason: '月次配分',
        tipTitle: '暫定目標值',
        tipBody: 'KPI 設定尚未完成。\n此目標值為暫定計算。',
        tipUnset: '未確認：',
        seasonDeviationBody: '月次配分與 KPN 建議值不同。',
        seasonConfirmOverride: '以此配分確認',
        seasonRestoreRecommended: '還原建議配分',
        seasonModeAuto: 'AUTO',
        seasonModeManual: 'MANUAL',
        dismiss: '關閉',
        anomalyAllocTip:
          '選定的基準年中，有年度的淡旺季型態與過去差異很大。\n請確認基準年設定。',
        anomalyAllocAria: '淡旺季型態差異警告',
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
      localStorage.setItem('kpiNavigator.kpiYearStore', JSON.stringify(api.getStore()));
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
        if (isUiBusinessDay(y + '-' + pad2(m0 + 1) + '-' + pad2(d))) open++;
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
    return 'hl:' + Number(year) + ':' + readHlWeights(year).join(',');
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

  function allocator() {
    return global.KpiSeasonalityAllocator || null;
  }

  function getHlSource(year) {
    var api = storeApi();
    if (!api || typeof api.getStore !== 'function') return null;
    var store = api.getStore();
    var y = Number(year);
    var rec = store && store.years && store.years[y];
    return rec && rec.plan ? rec.plan.hlSource || null : null;
  }

  function readReferencePack(year) {
    var api = storeApi();
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    if (!api || typeof api.computeAverageSeasonalityPct !== 'function') return null;
    var pack = api.computeAverageSeasonalityPct(y);
    if (!pack || !pack.months || pack.months.length !== 12) return null;
    return pack;
  }

  function getRecommendedSeasonality(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var alloc = allocator();
    if (!alloc || typeof alloc.projectAndBalance !== 'function') {
      return { ok: false, reason: 'no-allocator' };
    }
    var pack = readReferencePack(y);
    if (!pack) return { ok: false, reason: 'no-reference' };
    var projected = alloc.projectAndBalance(pack.months);
    if (!projected || !projected.ok) {
      return { ok: false, reason: (projected && projected.reason) || 'project-failed', pack: pack };
    }
    var sourceSignature =
      typeof alloc.referenceSourceSignature === 'function'
        ? alloc.referenceSourceSignature(y, pack.months, pack.yearsUsed || [])
        : 'ref:' + y;
    return {
      ok: true,
      weights: projected.weights.slice(),
      sum: projected.sum,
      steps: projected.steps,
      yearsUsed: (pack.yearsUsed || []).slice(),
      referenceMonths: pack.months.slice(),
      sourceSignature: sourceSignature,
      recommendedSignature: 'hl:' + y + ':' + projected.weights.join(','),
    };
  }

  function weightsEqual(a, b) {
    var alloc = allocator();
    if (alloc && typeof alloc.weightsEqual === 'function') return alloc.weightsEqual(a, b);
    if (!a || !b || a.length !== 12 || b.length !== 12) return false;
    for (var i = 0; i < 12; i++) {
      if (Number(a[i]) !== Number(b[i])) return false;
    }
    return true;
  }

  function isStrictAllocValid(weights) {
    var norm = normalizeHlWeights(weights);
    return !!(norm && isAllocTotalOk(norm));
  }

  function isFormalSeasonalityValid(weights) {
    var norm = normalizeHlWeights(weights);
    if (!norm) return false;
    if (isDefaultSeasonality(norm)) return true;
    return isAllocTotalOk(norm);
  }

  function evaluateSeasonalityStatus(year, pr, weights) {
    var y = Number(year);
    var mode = pr.seasonalityMode || null;
    var hlCur = seasonalitySignature(y);
    var hlSaved = pr.seasonalityConfirmedSignature || null;
    var recommended = getRecommendedSeasonality(y);
    var matchRec =
      recommended.ok && weights && weightsEqual(weights, recommended.weights);

    if (!normalizeHlWeights(weights)) {
      return {
        seasonStatus: 'invalid',
        mode: mode || 'manual',
        needsSeasonAction: true,
        seasonDeviation: false,
        recommended: recommended,
        matchRecommended: false,
      };
    }

    // AUTO with valid recommendation → ready (auto-confirmed)
    if (mode === 'auto' && recommended.ok) {
      var autoReady =
        matchRec &&
        hlSaved &&
        hlSaved === hlCur &&
        pr.seasonalityAutoSourceSignature === recommended.sourceSignature;
      if (autoReady) {
        return {
          seasonStatus: 'confirmed',
          mode: 'auto',
          needsSeasonAction: false,
          seasonDeviation: false,
          recommended: recommended,
          matchRecommended: true,
        };
      }
      // AUTO but stale — sync should fix; until then treat as provisional only if not matched
      return {
        seasonStatus: matchRec && hlSaved === hlCur ? 'confirmed' : 'changed',
        mode: 'auto',
        needsSeasonAction: !(matchRec && hlSaved === hlCur),
        seasonDeviation: false,
        recommended: recommended,
        matchRecommended: matchRec,
      };
    }

    // MANUAL
    if (mode === 'manual') {
      if (!isStrictAllocValid(weights)) {
        return {
          seasonStatus: 'invalid',
          mode: 'manual',
          needsSeasonAction: true,
          seasonDeviation: !!(recommended.ok && !matchRec),
          recommended: recommended,
          matchRecommended: false,
        };
      }
      if (recommended.ok && matchRec) {
        var okMatch = hlSaved && hlSaved === hlCur;
        return {
          seasonStatus: okMatch ? 'confirmed' : 'unconfirmed',
          mode: 'manual',
          needsSeasonAction: !okMatch,
          seasonDeviation: false,
          recommended: recommended,
          matchRecommended: true,
        };
      }
      // valid + deviation
      if (recommended.ok && !matchRec) {
        var approved =
          hlSaved &&
          hlSaved === hlCur &&
          pr.seasonalityDeviationApprovedSignature === hlCur;
        return {
          seasonStatus: approved ? 'confirmed' : 'unconfirmed',
          mode: 'manual',
          needsSeasonAction: !approved,
          seasonDeviation: !approved,
          recommended: recommended,
          matchRecommended: false,
        };
      }
      // no recommendation available — require explicit confirm of valid manual
      var okManual = hlSaved && hlSaved === hlCur;
      return {
        seasonStatus: okManual ? 'confirmed' : 'unconfirmed',
        mode: 'manual',
        needsSeasonAction: !okManual,
        seasonDeviation: false,
        recommended: recommended,
        matchRecommended: false,
      };
    }

    // Legacy / unset mode
    if (hlSaved) {
      var st = hlSaved === hlCur ? 'confirmed' : 'changed';
      return {
        seasonStatus: st,
        mode: mode,
        needsSeasonAction: st !== 'confirmed',
        seasonDeviation: false,
        recommended: recommended,
        matchRecommended: matchRec,
      };
    }
    // Untouched default without AUTO → still needs explicit confirm
    return {
      seasonStatus: 'unconfirmed',
      mode: mode,
      needsSeasonAction: true,
      seasonDeviation: false,
      recommended: recommended,
      matchRecommended: matchRec,
    };
  }

  function evaluate(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var pr = ensurePrRecord(y) || {};
    var annualOk = hasAnnualTarget(y);
    var bdCur = businessDaysSignature(y);
    var hlCur = seasonalitySignature(y);
    var bdSaved = pr.businessDaysConfirmedSignature || null;

    var bdStatus = 'unconfirmed';
    if (bdSaved) bdStatus = bdSaved === bdCur ? 'confirmed' : 'changed';

    var weights = readHlWeights(y);
    var seasonEval = evaluateSeasonalityStatus(y, pr, weights);
    var seasonStatus = seasonEval.seasonStatus;

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
        else if (seasonEval.seasonDeviation) provisionalReasons.push('seasonalityDeviation');
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
      seasonalityMode: seasonEval.mode,
      seasonDeviation: !!seasonEval.seasonDeviation,
      matchRecommended: !!seasonEval.matchRecommended,
      recommendedWeights: seasonEval.recommended && seasonEval.recommended.ok
        ? seasonEval.recommended.weights
        : null,
      missingReasons: missingReasons,
      provisionalReasons: provisionalReasons,
      businessDaysCurrentSignature: bdCur,
      seasonalityCurrentSignature: hlCur,
      isDefaultSeasonality: isDefaultSeasonality(weights),
      allocTotalOk: isAllocTotalOk(weights),
      openDayCount: countOpenDays(y),
      needsBdAction: annualOk && bdStatus !== 'confirmed',
      needsSeasonAction: annualOk && !!seasonEval.needsSeasonAction,
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

  function isUserSeasonalityEditSource(meta) {
    var src = (meta && meta.source) || '';
    return (
      src === 'sales-data-analyze' ||
      src === 'cockpit-plan-edit' ||
      src === 'sales-data-hl' ||
      src === 'user-edit'
    );
  }

  function writeSeasonalityConfirmed(year, opts) {
    opts = opts || {};
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var pr = ensurePrRecord(y);
    if (!pr) return { ok: false };
    var sig = seasonalitySignature(y);
    pr.seasonalityConfirmedSignature = sig;
    pr.seasonalityConfirmedAt = Date.now();
    pr.seasonalityVisited = true;
    if (opts.edited) pr.seasonalityEdited = true;
    if (opts.auto) pr.seasonalityAutoConfirmed = true;
    if (opts.deviationApproved) pr.seasonalityDeviationApprovedSignature = sig;
    if (opts.clearDeviation) delete pr.seasonalityDeviationApprovedSignature;
    if (opts.mode) pr.seasonalityMode = opts.mode;
    persistStoreQuiet();
    emitChanged(y);
    return { ok: true, auto: !!opts.auto };
  }

  function confirmSeasonality(year, opts) {
    opts = opts || {};
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var weights = readHlWeights(y);
    if (!normalizeHlWeights(weights)) return { ok: false, reason: 'invalid' };
    var isDefault = isDefaultSeasonality(weights);
    if (!isDefault && !isAllocTotalOk(weights)) return { ok: false, reason: 'alloc' };
    if (isDefault && !opts.skipDefaultPrompt && !opts.autoFromEdit) {
      return { needDefaultConfirm: true };
    }
    return writeSeasonalityConfirmed(y, {
      edited: !!opts.edited,
      mode: opts.mode || 'manual',
      clearDeviation: true,
    });
  }

  function confirmSeasonalityDeviation(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var weights = readHlWeights(y);
    if (!isStrictAllocValid(weights)) return { ok: false, reason: 'invalid' };
    var pr = ensurePrRecord(y);
    if (!pr) return { ok: false };
    pr.seasonalityMode = 'manual';
    return writeSeasonalityConfirmed(y, {
      edited: true,
      mode: 'manual',
      deviationApproved: true,
    });
  }

  function restoreRecommendedSeasonality(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var recommended = getRecommendedSeasonality(y);
    if (!recommended.ok) return { ok: false, reason: recommended.reason || 'no-recommendation' };
    var api = storeApi();
    if (!api || typeof api.writeMonthlyHlWeights !== 'function') return { ok: false };
    var ok = api.writeMonthlyHlWeights(y, recommended.weights, { source: 'seasonality-auto' });
    if (!ok) return { ok: false, reason: 'write-failed' };
    var pr = ensurePrRecord(y);
    if (!pr) return { ok: false };
    pr.seasonalityMode = 'auto';
    pr.seasonalityEdited = false;
    pr.seasonalityAutoSourceSignature = recommended.sourceSignature;
    pr.seasonalityRecommendedSignature = recommended.recommendedSignature;
    delete pr.seasonalityDeviationApprovedSignature;
    return writeSeasonalityConfirmed(y, { mode: 'auto', auto: true, clearDeviation: true });
  }

  function applyAutoSeasonality(year, force) {
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var pr = ensurePrRecord(y);
    if (!pr) return { ok: false };
    if (pr.seasonalityMode === 'manual' && !force) return { ok: false, reason: 'manual' };
    var recommended = getRecommendedSeasonality(y);
    if (!recommended.ok) return { ok: false, reason: recommended.reason || 'no-recommendation' };
    var api = storeApi();
    if (!api || typeof api.writeMonthlyHlWeights !== 'function') return { ok: false };
    var current = readHlWeights(y);
    var hlCur = 'hl:' + y + ':' + recommended.weights.join(',');
    var sameWeights = weightsEqual(current, recommended.weights);
    var sameSrc = pr.seasonalityAutoSourceSignature === recommended.sourceSignature;
    var alreadyConfirmed =
      pr.seasonalityMode === 'auto' &&
      sameWeights &&
      sameSrc &&
      pr.seasonalityConfirmedSignature === hlCur;
    if (alreadyConfirmed) return { ok: true, skipped: true };

    if (!sameWeights) {
      var written = api.writeMonthlyHlWeights(y, recommended.weights, {
        source: 'seasonality-auto',
      });
      if (!written) return { ok: false, reason: 'write-failed' };
    }
    pr.seasonalityMode = 'auto';
    pr.seasonalityAutoSourceSignature = recommended.sourceSignature;
    pr.seasonalityRecommendedSignature = recommended.recommendedSignature;
    pr.seasonalityEdited = false;
    delete pr.seasonalityDeviationApprovedSignature;
    return writeSeasonalityConfirmed(y, { mode: 'auto', auto: true, clearDeviation: true });
  }

  /**
   * Existing-user migration — never overwrite differing weights.
   * matching recommendation → AUTO; different → MANUAL preserve.
   */
  function migrateSeasonalityMode(year) {
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var pr = ensurePrRecord(y);
    if (!pr) return { ok: false };
    if (pr.seasonalityMode === 'auto' || pr.seasonalityMode === 'manual') {
      if (pr.seasonalityMode === 'auto') applyAutoSeasonality(y, false);
      return { ok: true, mode: pr.seasonalityMode, migrated: false };
    }
    var recommended = getRecommendedSeasonality(y);
    var weights = readHlWeights(y);
    var src = getHlSource(y);
    if (recommended.ok && weightsEqual(weights, recommended.weights)) {
      pr.seasonalityMode = 'auto';
      pr.seasonalityAutoSourceSignature = recommended.sourceSignature;
      pr.seasonalityRecommendedSignature = recommended.recommendedSignature;
      writeSeasonalityConfirmed(y, { mode: 'auto', auto: true, clearDeviation: true });
      return { ok: true, mode: 'auto', migrated: true };
    }
    if (recommended.ok) {
      // Preserve existing configured weights (user or legacy seed) as MANUAL.
      pr.seasonalityMode = 'manual';
      persistStoreQuiet();
      return { ok: true, mode: 'manual', migrated: true, preserved: true };
    }
    // No reference: keep legacy unset; default seed still needs explicit confirm.
    if (src === 'sales-data-analyze' || pr.seasonalityEdited) {
      pr.seasonalityMode = 'manual';
      persistStoreQuiet();
      return { ok: true, mode: 'manual', migrated: true };
    }
    return { ok: true, mode: null, migrated: false };
  }

  function onSeasonalityUserSaved(year, weights, meta) {
    if (!isUserSeasonalityEditSource(meta)) return { ok: false, reason: 'not-user-edit' };
    var y = Number(year);
    if (!Number.isFinite(y)) y = operatingYear();
    var norm = normalizeHlWeights(weights != null ? weights : readHlWeights(y));
    var pr = ensurePrRecord(y);
    if (!pr) return { ok: false };
    pr.seasonalityMode = 'manual';
    pr.seasonalityEdited = true;
    pr.seasonalityVisited = true;
    delete pr.seasonalityAutoConfirmed;

    if (!norm || !isStrictAllocValid(norm)) {
      persistStoreQuiet();
      emitChanged(y);
      if (document.getElementById(ALERT_ID)) {
        pageAlertDismissed = false;
        renderAlertFw({ force: true, afterAction: true });
      }
      return { ok: true, confirmed: false, reason: 'invalid', mode: 'manual' };
    }

    var recommended = getRecommendedSeasonality(y);
    if (recommended.ok && weightsEqual(norm, recommended.weights)) {
      var res = writeSeasonalityConfirmed(y, {
        edited: true,
        mode: 'manual',
        clearDeviation: true,
      });
      if (document.getElementById(ALERT_ID)) {
        pageAlertDismissed = false;
        renderAlertFw({ force: true, afterAction: true });
      }
      return { ok: !!res.ok, confirmed: true, mode: 'manual', matchRecommended: true };
    }

    // Valid deviation — do not auto-confirm
    delete pr.seasonalityDeviationApprovedSignature;
    // Invalidate prior confirm if signature no longer matches after edit
    persistStoreQuiet();
    emitChanged(y);
    if (document.getElementById(ALERT_ID)) {
      pageAlertDismissed = false;
      renderAlertFw({ force: true, afterAction: true });
    }
    return {
      ok: true,
      confirmed: false,
      mode: 'manual',
      reason: 'deviation',
      matchRecommended: false,
    };
  }

  function markVisited(year, which) {
    var pr = ensurePrRecord(year);
    if (!pr) return;
    if (which === 'businessDays') pr.businessDaysVisited = true;
    if (which === 'seasonality') pr.seasonalityVisited = true;
    persistStoreQuiet();
  }

  function hookWriteMonthlyHlWeights() {
    var api = storeApi();
    if (!api || typeof api.writeMonthlyHlWeights !== 'function') return;
    if (api.writeMonthlyHlWeights.__kpiPrHooked) return;
    var orig = api.writeMonthlyHlWeights;
    api.writeMonthlyHlWeights = function (year, weights, meta) {
      var ok = orig.call(api, year, weights, meta);
      if (ok) {
        try {
          onSeasonalityUserSaved(year, weights, meta || {});
        } catch (_e) {}
      }
      return ok;
    };
    api.writeMonthlyHlWeights.__kpiPrHooked = true;
  }

  function refreshSeasonalityModeBadge() {
    var title =
      document.querySelector('.sales-data-modal__seasonality-title') ||
      document.querySelector('[data-sdm-tab="analyze"] .sales-data-modal__seasonality h3');
    if (!title) return;
    var snap = evaluate(operatingYear());
    var mode = snap.seasonalityMode;
    var badge = title.querySelector('.kpi-pr-season-mode');
    if (!mode) {
      if (badge) badge.remove();
      return;
    }
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'kpi-pr-season-mode';
      title.appendChild(document.createTextNode(' '));
      title.appendChild(badge);
    }
    badge.textContent = mode === 'auto' ? t('seasonModeAuto') : t('seasonModeManual');
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
    refreshSeasonalityAnomalyUi();
  }

  function ensureCss() {
    var style = document.getElementById(CSS_ID);
    if (!style) {
      style = document.createElement('style');
      style.id = CSS_ID;
      document.head.appendChild(style);
    }
    style.textContent =
      /* Sci-Fi PROVISIONAL: dark amber/gold (not bright orange / not error) */ '' +
      'body.kpi-pr-provisional:not(.office-mode) {' +
      '  --kpn-pr-warn-bg: rgba(180, 125, 25, 0.16);' +
      '  --kpn-pr-warn-bg-soft: rgba(180, 125, 25, 0.10);' +
      '  --kpn-pr-warn-border: rgba(230, 180, 55, 0.75);' +
      '  --kpn-pr-warn-border-soft: rgba(230, 180, 55, 0.55);' +
      '  --kpn-pr-warn-text: #D9AD45;' +
      '}' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-row__cell--plan-target,' +
      'body.kpi-pr-provisional:not(.office-mode) .monthly-data-column__cell--plan-target,' +
      'body.kpi-pr-provisional:not(.office-mode) .monthly-vfocus-cell--plan-target,' +
      'body.kpi-pr-provisional:not(.office-mode) .kpi-pr-target-warn,' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-bar-lower__group--base > .annual-daily-focus-bar-lower__cell:nth-child(3),' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-bar-upper__group--base > .annual-daily-focus-bar-upper__cell:nth-child(3),' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-bar-lower__group--monthly > .annual-daily-focus-bar-lower__cell:nth-child(1),' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-bar-upper__group--monthly > .annual-daily-focus-bar-upper__cell:nth-child(1),' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-bar-lower__group--annual > .annual-daily-focus-bar-lower__cell:nth-child(1),' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-bar-upper__group--annual > .annual-daily-focus-bar-upper__cell:nth-child(1) {' +
      '  box-shadow: inset 0 0 0 1px var(--kpn-pr-warn-border);' +
      '  background-color: var(--kpn-pr-warn-bg) !important;' +
      '  color: var(--kpn-pr-warn-text) !important;' +
      '}' +
      /* Headers: border + text first; soft amber wash only */ '' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-menu-group--base > .annual-daily-hdr__cell:nth-child(3),' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-menu-group--monthly > .annual-daily-hdr__cell:nth-child(1),' +
      'body.kpi-pr-provisional:not(.office-mode) .annual-daily-focus-menu-group--annual > .annual-daily-hdr__cell:nth-child(1) {' +
      '  box-shadow: inset 0 0 0 1px var(--kpn-pr-warn-border-soft);' +
      '  background-color: var(--kpn-pr-warn-bg-soft) !important;' +
      '  color: var(--kpn-pr-warn-text) !important;' +
      '}' +
      /* Office: keep existing warm/neutral warning (do not import Sci-Fi amber) */ '' +
      'body.office-mode.kpi-pr-provisional .annual-daily-row__cell--plan-target,' +
      'body.office-mode.kpi-pr-provisional .monthly-data-column__cell--plan-target,' +
      'body.office-mode.kpi-pr-provisional .monthly-vfocus-cell--plan-target,' +
      'body.office-mode.kpi-pr-provisional .kpi-pr-target-warn,' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-bar-lower__group--base > .annual-daily-focus-bar-lower__cell:nth-child(3),' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-bar-upper__group--base > .annual-daily-focus-bar-upper__cell:nth-child(3),' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-bar-lower__group--monthly > .annual-daily-focus-bar-lower__cell:nth-child(1),' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-bar-upper__group--monthly > .annual-daily-focus-bar-upper__cell:nth-child(1),' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-bar-lower__group--annual > .annual-daily-focus-bar-lower__cell:nth-child(1),' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-bar-upper__group--annual > .annual-daily-focus-bar-upper__cell:nth-child(1) {' +
      '  box-shadow: inset 0 0 0 1.5px rgba(180, 100, 30, 0.55);' +
      '  background-color: rgba(255, 236, 179, 0.75) !important;' +
      '  color: #9a3412 !important;' +
      '}' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-menu-group--base > .annual-daily-hdr__cell:nth-child(3),' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-menu-group--monthly > .annual-daily-hdr__cell:nth-child(1),' +
      'body.office-mode.kpi-pr-provisional .annual-daily-focus-menu-group--annual > .annual-daily-hdr__cell:nth-child(1) {' +
      '  box-shadow: inset 0 0 0 1px rgba(180, 100, 30, 0.45);' +
      '  background-color: rgba(255, 236, 179, 0.35) !important;' +
      '  color: #9a3412 !important;' +
      '}' +
      /* Focus Bar default pointer-events:none — enable target cells for tooltip */ '' +
      'body.kpi-pr-provisional .annual-daily-focus-bar-lower,' +
      'body.kpi-pr-provisional .annual-daily-focus-bar-upper,' +
      'body.kpi-pr-provisional .annual-daily-focus-bar-lower-scroll,' +
      'body.kpi-pr-provisional .annual-daily-focus-bar-upper-scroll {' +
      '  pointer-events: none;' +
      '}' +
      'body.kpi-pr-provisional .annual-daily-focus-bar-lower__group--base > .annual-daily-focus-bar-lower__cell:nth-child(3),' +
      'body.kpi-pr-provisional .annual-daily-focus-bar-upper__group--base > .annual-daily-focus-bar-upper__cell:nth-child(3),' +
      'body.kpi-pr-provisional .monthly-vfocus-cell--plan-target {' +
      '  pointer-events: auto;' +
      '  cursor: help;' +
      '  position: relative;' +
      '  z-index: 5;' +
      '}' +
      /* Office Alert */ '' +
      '.kpi-pr-alert {' +
      '  position: fixed; z-index: 12000; left: 50%; top: 72px; transform: translateX(-50%);' +
      '  width: min(460px, calc(100vw - 32px)); padding: 16px 18px; border-radius: 10px;' +
      '  background: #fff8f4; border: 1px solid rgba(198, 90, 50, 0.45);' +
      '  box-shadow: 0 10px 28px rgba(0,0,0,0.18); color: #4a2c22; font-size: 14px; line-height: 1.45;' +
      '}' +
      'body:not(.office-mode) .kpi-pr-alert {' +
      '  background: #0a0f12; border: 1px solid #3dff3d; color: #58e1f3;' +
      '  box-shadow: 0 12px 32px rgba(0,0,0,0.55);' +
      '}' +
      '.kpi-pr-alert__title { font-weight: 700; margin: 0 0 6px; }' +
      '.kpi-pr-alert__body { margin: 0 0 10px; }' +
      '.kpi-pr-alert__section { margin: 12px 0; padding: 10px 0 0; border-top: 1px solid rgba(198,90,50,0.25); }' +
      'body:not(.office-mode) .kpi-pr-alert__section { border-top-color: rgba(61,255,61,0.35); }' +
      '.kpi-pr-alert__section-title { font-weight: 600; margin: 0 0 8px; }' +
      '.kpi-pr-alert__row { display: flex; gap: 8px; flex-wrap: wrap; }' +
      '.kpi-pr-alert__actions { display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap; margin-top: 12px; }' +
      '.kpi-pr-alert button { cursor: pointer; border-radius: 6px; border: 1px solid #c65a32; background: #fff; color: #a14a2e; padding: 6px 12px; }' +
      '.kpi-pr-alert button.kpi-pr-alert__primary { background: #c65a32; color: #fff; }' +
      'body:not(.office-mode) .kpi-pr-alert button {' +
      '  border: 1px solid #3dff3d; background: #1a1f24; color: #58e1f3;' +
      '}' +
      'body:not(.office-mode) .kpi-pr-alert button.kpi-pr-alert__primary {' +
      '  background: #16301a; border-color: #3dff3d; color: #9eff9e;' +
      '}' +
      '.kpi-pr-dialog-back { position: fixed; inset: 0; z-index: 13000; background: rgba(0,0,0,0.35); }' +
      '.kpi-pr-dialog { position: fixed; z-index: 13001; left: 50%; top: 50%; transform: translate(-50%,-50%);' +
      '  width: min(420px, calc(100vw - 32px)); background: #fff; border-radius: 12px; padding: 18px 20px;' +
      '  box-shadow: 0 16px 40px rgba(0,0,0,0.25); color: #222; }' +
      'body:not(.office-mode) .kpi-pr-dialog {' +
      '  background: #0a0f12; border: 1px solid #3dff3d; color: #58e1f3;' +
      '}' +
      '.kpi-pr-dialog h3 { margin: 0 0 8px; font-size: 16px; }' +
      '.kpi-pr-dialog p { margin: 0 0 14px; white-space: pre-line; font-size: 14px; line-height: 1.45; }' +
      '.kpi-pr-dialog__actions { display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap; }' +
      '.kpi-pr-dialog button { cursor: pointer; border-radius: 6px; border: 1px solid #888; background: #fff; padding: 6px 12px; }' +
      '.kpi-pr-dialog button.primary { border-color: #c65a32; background: #c65a32; color: #fff; }' +
      'body:not(.office-mode) .kpi-pr-dialog button { border-color: #3dff3d; background: #1a1f24; color: #58e1f3; }' +
      'body:not(.office-mode) .kpi-pr-dialog button.primary { background: #16301a; color: #9eff9e; }' +
      '.kpi-pr-season-mode { display: inline-block; margin-left: 8px; font-size: 11px; font-weight: 600; opacity: 0.85; letter-spacing: 0.04em; }' +
      '.kpi-pr-alert__note { margin: 0 0 8px; font-size: 13px; opacity: 0.95; }' +
      /* Seasonality anomaly stays in the actionable baseline-year UI, not the Cockpit summary. */ '' +
      'body.tutorial-advanced-off .sdm-weekday-baseline__anomaly[data-kpi-tutorial-tip]:hover::after,' +
      'body.tutorial-advanced-off .sdm-weekday-baseline__anomaly[data-kpi-tutorial-tip]:focus-visible::after {' +
      '  content: none !important;' +
      '}' +
      '.sdm-weekday-baseline__anomaly {' +
      '  display: inline-block; margin-left: 4px; color: #d97706; font-size: 12px;' +
      '  cursor: help; position: relative; flex-shrink: 0;' +
      '}' +
      '.sdm-weekday-baseline__row.is-anomaly .sdm-weekday-baseline__year { color: #d97706; }' +
      '.sdm-weekday-baseline__anomaly[data-tooltip]:hover::after,' +
      '.sdm-weekday-baseline__anomaly[data-tooltip]:focus-visible::after {' +
      '  content: attr(data-tooltip); position: absolute; left: 50%; bottom: calc(100% + 6px);' +
      '  transform: translateX(-50%); width: max-content; max-width: 220px; padding: 5px 7px;' +
      '  border: 1px solid rgba(217,119,6,0.55); background: rgba(12,14,16,0.95); color: #fbbf24;' +
      '  font-size: 11px; font-weight: 600; line-height: 1.3; white-space: normal; z-index: 50;' +
      '  pointer-events: none;' +
      '}' +
      /* Remove any leftover SDM confirm bar from prior build */ '' +
      '.kpi-pr-sdm-bar { display: none !important; }';
  }

  function refreshSeasonalityAnomalyUi() {
    /*
     * Cockpit "Monthly Allocation Total" is an integrity summary.
     * Baseline-year anomaly warnings are actionable in the baseline selector itself,
     * so do not color or annotate the Cockpit total. Also clean markers/classes
     * left by older cached builds.
     */
    var clusters = document.querySelectorAll('.annual-kpi-allocation-cluster');
    for (var i = 0; i < clusters.length; i++) {
      var cluster = clusters[i];
      cluster.classList.remove('is-seasonality-anomaly');
      cluster.setAttribute('aria-hidden', 'true');
      var marks = cluster.querySelectorAll('.kpi-pr-anomaly-mark');
      for (var j = 0; j < marks.length; j++) marks[j].remove();
    }
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

  function focusBarTargetCells() {
    return document.querySelectorAll(
      '.annual-daily-focus-bar-lower__group--base > .annual-daily-focus-bar-lower__cell:nth-child(3),' +
        '.annual-daily-focus-bar-upper__group--base > .annual-daily-focus-bar-upper__cell:nth-child(3),' +
        '.monthly-vfocus-cell--plan-target'
    );
  }

  function refreshTooltips() {
    var snap = evaluate(operatingYear());
    var tip = snap.state === STATE.READY || snap.state === STATE.NOT_READY ? '' : tooltipText(snap);
    var warn = tip !== '';

    var focusNodes = focusBarTargetCells();
    for (var i = 0; i < focusNodes.length; i++) {
      var el = focusNodes[i];
      el.classList.add('kpi-pr-tip-host');
      if (warn) {
        el.setAttribute('title', tip);
        el.setAttribute('data-kpi-pr-tip', tip);
        el.classList.add('kpi-pr-target-warn');
      } else {
        el.removeAttribute('title');
        el.removeAttribute('data-kpi-pr-tip');
        el.classList.remove('kpi-pr-target-warn');
      }
    }

    var extra = document.querySelectorAll(
      '.daily-overlay__daily-kpi .daily-overlay__kpi-row:nth-child(2) .daily-overlay__daily-value-box,' +
        '.insight-daily-kpi .insight-daily-kpi__row:nth-child(2) .insight-daily-kpi__value'
    );
    for (var j = 0; j < extra.length; j++) {
      if (warn) {
        extra[j].setAttribute('title', tip);
        extra[j].classList.add('kpi-pr-target-warn');
      } else {
        extra[j].removeAttribute('title');
        extra[j].classList.remove('kpi-pr-target-warn');
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

  function openSalesDataModal(analyze) {
    var btn =
      document.getElementById('annual-current-sales-btn') ||
      document.getElementById('monthly-current-sales-btn') ||
      document.querySelector('[data-open-sales-data]');
    if (btn) {
      try {
        btn.click();
      } catch (_e) {}
    }
    if (analyze) {
      setTimeout(function () {
        try {
          var tab = document.querySelector('.sales-data-modal__tab[data-sdm-tab="analyze"]');
          if (tab) tab.click();
        } catch (_e2) {}
      }, 120);
    }
  }

  function removeLegacySdmBar() {
    var bars = document.querySelectorAll('.kpi-pr-sdm-bar');
    for (var i = 0; i < bars.length; i++) bars[i].remove();
  }

  function closeAlertFw() {
    var el = document.getElementById(ALERT_ID);
    if (el) el.remove();
    if (completeTimer) {
      clearTimeout(completeTimer);
      completeTimer = null;
    }
  }

  function showCompleteThenClose() {
    var el = document.getElementById(ALERT_ID) || document.createElement('div');
    el.id = ALERT_ID;
    el.className = 'kpi-pr-alert';
    el.setAttribute('role', 'status');
    el.innerHTML = '<p class="kpi-pr-alert__title"></p>';
    el.querySelector('.kpi-pr-alert__title').textContent = t('alertDone');
    if (!el.parentNode) document.body.appendChild(el);
    if (completeTimer) clearTimeout(completeTimer);
    completeTimer = setTimeout(function () {
      closeAlertFw();
      completeTimer = null;
    }, 1200);
  }

  function afterConfirmRefresh() {
    pageAlertDismissed = false;
    renderAlertFw({ force: true, afterAction: true });
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
          afterConfirmRefresh();
        },
        function () {
          openSalesDataModal(false);
        }
      );
      return;
    }
    if (res && res.ok) afterConfirmRefresh();
  }

  function runConfirmSeasonality() {
    var y = operatingYear();
    markVisited(y, 'seasonality');
    var snap = evaluate(y);
    if (snap.seasonDeviation) {
      confirmSeasonalityDeviation(y);
      afterConfirmRefresh();
      return;
    }
    var res = confirmSeasonality(y);
    if (res && res.needDefaultConfirm) {
      showDialog(
        t('seasonDefaultTitle'),
        t('seasonDefaultBody'),
        t('seasonConfirm'),
        t('seasonAdjust'),
        function () {
          confirmSeasonality(y, { skipDefaultPrompt: true, mode: 'manual' });
          afterConfirmRefresh();
        },
        function () {
          openSalesDataModal(true);
        }
      );
      return;
    }
    if (res && res.ok === false) {
      try {
        window.alert(t('seasonInvalid'));
      } catch (_a) {}
      return;
    }
    if (res && res.ok) afterConfirmRefresh();
  }

  function runRestoreRecommended() {
    var y = operatingYear();
    var res = restoreRecommendedSeasonality(y);
    if (res && res.ok) afterConfirmRefresh();
  }

  function renderAlertFw(opts) {
    opts = opts || {};
    var snap = evaluate(operatingYear());

    if (snap.state === STATE.READY) {
      if (opts.afterAction) showCompleteThenClose();
      else closeAlertFw();
      return;
    }

    if (snap.state === STATE.NOT_READY && !snap.needsBdAction && !snap.needsSeasonAction) {
      // annual missing only — still show message without confirm actions
    }

    if (!opts.force && !opts.afterAction && pageAlertDismissed) return;

    var el = document.getElementById(ALERT_ID);
    if (!el) {
      el = document.createElement('div');
      el.id = ALERT_ID;
      el.className = 'kpi-pr-alert';
      el.setAttribute('role', 'dialog');
      el.setAttribute('aria-modal', 'false');
      document.body.appendChild(el);
    }

    var html = '';
    html += '<p class="kpi-pr-alert__title"></p>';
    html += '<p class="kpi-pr-alert__body"></p>';
    if (snap.needsBdAction) {
      html +=
        '<div class="kpi-pr-alert__section" data-pr-section="bd">' +
        '<p class="kpi-pr-alert__section-title"></p>' +
        '<div class="kpi-pr-alert__row">' +
        '<button type="button" class="kpi-pr-alert__primary" data-pr-act="confirm-bd"></button>' +
        '<button type="button" data-pr-act="edit-bd"></button>' +
        '</div></div>';
    }
    if (snap.needsSeasonAction) {
      html +=
        '<div class="kpi-pr-alert__section" data-pr-section="season">' +
        '<p class="kpi-pr-alert__section-title"></p>';
      if (snap.seasonDeviation) {
        html += '<p class="kpi-pr-alert__note" data-pr-note="deviation"></p>';
        html +=
          '<div class="kpi-pr-alert__row">' +
          '<button type="button" class="kpi-pr-alert__primary" data-pr-act="confirm-season-override"></button>' +
          '<button type="button" data-pr-act="restore-season"></button>' +
          '<button type="button" data-pr-act="adjust-season"></button>' +
          '</div></div>';
      } else {
        html +=
          '<div class="kpi-pr-alert__row">' +
          '<button type="button" class="kpi-pr-alert__primary" data-pr-act="confirm-season"></button>' +
          '<button type="button" data-pr-act="adjust-season"></button>' +
          '</div></div>';
      }
    }
    if (snap.annualTarget === 'missing') {
      html +=
        '<div class="kpi-pr-alert__section" data-pr-section="annual">' +
        '<p class="kpi-pr-alert__section-title"></p>' +
        '<div class="kpi-pr-alert__row">' +
        '<button type="button" data-pr-act="edit-annual"></button>' +
        '</div></div>';
    }
    html +=
      '<div class="kpi-pr-alert__actions">' +
      '<button type="button" data-pr-act="dismiss"></button></div>';

    el.innerHTML = html;
    el.querySelector('.kpi-pr-alert__title').textContent = t('alertTitle');
    el.querySelector('.kpi-pr-alert__body').textContent = t('alertBody');

    var bdSec = el.querySelector('[data-pr-section="bd"]');
    if (bdSec) {
      bdSec.querySelector('.kpi-pr-alert__section-title').textContent = t('reasonBd');
      bdSec.querySelector('[data-pr-act="confirm-bd"]').textContent = t('confirmBd');
      bdSec.querySelector('[data-pr-act="edit-bd"]').textContent = t('editBd');
    }
    var seSec = el.querySelector('[data-pr-section="season"]');
    if (seSec) {
      seSec.querySelector('.kpi-pr-alert__section-title').textContent = t('reasonSeason');
      var note = seSec.querySelector('[data-pr-note="deviation"]');
      if (note) note.textContent = t('seasonDeviationBody');
      var btnConfirm = seSec.querySelector('[data-pr-act="confirm-season"]');
      if (btnConfirm) btnConfirm.textContent = t('confirmSeason');
      var btnOverride = seSec.querySelector('[data-pr-act="confirm-season-override"]');
      if (btnOverride) btnOverride.textContent = t('seasonConfirmOverride');
      var btnRestore = seSec.querySelector('[data-pr-act="restore-season"]');
      if (btnRestore) btnRestore.textContent = t('seasonRestoreRecommended');
      var btnAdj = seSec.querySelector('[data-pr-act="adjust-season"]');
      if (btnAdj) btnAdj.textContent = t('adjustSeason');
    }
    var anSec = el.querySelector('[data-pr-section="annual"]');
    if (anSec) {
      anSec.querySelector('.kpi-pr-alert__section-title').textContent = t('reasonAnnual');
      anSec.querySelector('[data-pr-act="edit-annual"]').textContent = t('editBd');
    }
    el.querySelector('[data-pr-act="dismiss"]').textContent = t('dismiss');

    el.onclick = function (ev) {
      var btn = ev.target && ev.target.closest ? ev.target.closest('[data-pr-act]') : null;
      if (!btn) return;
      var act = btn.getAttribute('data-pr-act');
      if (act === 'dismiss') {
        pageAlertDismissed = true;
        closeAlertFw();
        return;
      }
      if (act === 'confirm-bd') runConfirmBusinessDays();
      if (act === 'edit-bd' || act === 'edit-annual') openSalesDataModal(false);
      if (act === 'confirm-season' || act === 'confirm-season-override') runConfirmSeasonality();
      if (act === 'restore-season') runRestoreRecommended();
      if (act === 'adjust-season') openSalesDataModal(true);
    };
  }

  function showPageEntryAlert(force) {
    if (!force && pageAlertDismissed) return;
    renderAlertFw({ force: !!force });
  }

  function bindListeners() {
    function onDataChanged(ev) {
      // Avoid re-entry loops from our own emitChanged
      if (ev && ev.type === 'kpi:planningReadinessChanged') {
        applyBodyState();
        refreshTooltips();
        refreshSeasonalityModeBadge();
        return;
      }
      try {
        migrateSeasonalityMode(operatingYear());
      } catch (_m) {}
      applyBodyState();
      refreshTooltips();
      refreshSeasonalityModeBadge();
      if (document.getElementById(ALERT_ID)) {
        pageAlertDismissed = false;
        renderAlertFw({ force: true });
      }
    }
    [
      'kpi:businessDayChanged',
      'kpi:annualPlanChanged',
      'kpi:weekdayBaselineChanged',
      'kpi:dailyTargetModeChanged',
      'kpi:observedChanged',
      'annual:salesDataSaved',
      'annual:pastSalesSaved',
      'kpi:planningReadinessChanged',
    ].forEach(function (ev) {
      document.addEventListener(ev, onDataChanged);
    });
    document.addEventListener('insight:dateChanged', refreshTooltips);
    document.addEventListener('annual:dailyDateChanged', refreshTooltips);
    document.addEventListener('annual:timelineRowsRendered', refreshTooltips);
  }

  function boot() {
    ensureCss();
    removeLegacySdmBar();
    hookWriteMonthlyHlWeights();
    setTimeout(hookWriteMonthlyHlWeights, 0);
    setTimeout(hookWriteMonthlyHlWeights, 500);
    try {
      migrateSeasonalityMode(operatingYear());
    } catch (_mig) {}
    applyBodyState();
    refreshTooltips();
    refreshSeasonalityModeBadge();
    bindListeners();
    setTimeout(function () {
      try {
        migrateSeasonalityMode(operatingYear());
      } catch (_m2) {}
      showPageEntryAlert(false);
      refreshTooltips();
      refreshSeasonalityModeBadge();
    }, 700);
    setInterval(function () {
      if (document.body.classList.contains(BODY_PROVISIONAL)) refreshTooltips();
      refreshSeasonalityModeBadge();
    }, 2500);
  }

  var api = {
    __ready: true,
    STATE: STATE,
    DEFAULT_HL_WEIGHTS: DEFAULT_HL_WEIGHTS.slice(),
    evaluate: evaluate,
    confirmBusinessDays: confirmBusinessDays,
    confirmSeasonality: confirmSeasonality,
    confirmSeasonalityDeviation: confirmSeasonalityDeviation,
    restoreRecommendedSeasonality: restoreRecommendedSeasonality,
    applyAutoSeasonality: applyAutoSeasonality,
    migrateSeasonalityMode: migrateSeasonalityMode,
    getRecommendedSeasonality: getRecommendedSeasonality,
    canConfirmSeasonality: canConfirmSeasonality,
    isFormalSeasonalityValid: isFormalSeasonalityValid,
    onSeasonalityUserSaved: onSeasonalityUserSaved,
    isUserSeasonalityEditSource: isUserSeasonalityEditSource,
    businessDaysSignature: businessDaysSignature,
    seasonalitySignature: seasonalitySignature,
    isDefaultSeasonality: isDefaultSeasonality,
    isAllocTotalOk: isAllocTotalOk,
    normalizeHlWeights: normalizeHlWeights,
    showPageEntryAlert: showPageEntryAlert,
    renderAlertFw: renderAlertFw,
    applyBodyState: applyBodyState,
    refreshTooltips: refreshTooltips,
    refreshSeasonalityAnomalyUi: refreshSeasonalityAnomalyUi,
    runConfirmBusinessDays: runConfirmBusinessDays,
    runConfirmSeasonality: runConfirmSeasonality,
    runRestoreRecommended: runRestoreRecommended,
    removeLegacySdmBar: removeLegacySdmBar,
    hookWriteMonthlyHlWeights: hookWriteMonthlyHlWeights,
  };

  global.KpiPlanningReadiness = api;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})(typeof window !== 'undefined' ? window : this);

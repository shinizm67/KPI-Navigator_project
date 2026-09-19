/**
 * Deterministic Recommended Seasonality allocator.
 * Spec: docs/planning-readiness.md (Automatic Seasonality)
 *
 * Reference Seasonality (unchanged — computed elsewhere):
 *   KpiYearStore.computeAverageSeasonalityPct(oy)  // selected baseline years
 *   = equal-weight mean of past years' computeObserved().monthlyPct
 *
 * This module only: 5% projection + sum-1200 balance.
 * snap rule = existing snapHlWeightFromObserved / clampSdmHlWeight:
 *   Math.round(n/5)*5, clamp 60..200, null → 100
 */
(function (global) {
  'use strict';

  if (global.KpiSeasonalityAllocator && global.KpiSeasonalityAllocator.__ready) {
    return;
  }

  var HL_MIN = 60;
  var HL_MAX = 200;
  var HL_STEP = 5;
  var TARGET_SUM = 1200;

  function snapToFive(n) {
    var v = Number(n);
    if (!Number.isFinite(v)) return 100;
    var snapped = Math.round(v / HL_STEP) * HL_STEP;
    if (snapped < HL_MIN) snapped = HL_MIN;
    if (snapped > HL_MAX) snapped = HL_MAX;
    return snapped;
  }

  function refForPenalty(raw) {
    var v = Number(raw);
    return Number.isFinite(v) ? v : 100;
  }

  function projectAndBalance(referenceMonths) {
    if (!referenceMonths || referenceMonths.length !== 12) {
      return { ok: false, reason: 'bad-length', weights: null };
    }
    var refs = [];
    var weights = [];
    var i;
    for (i = 0; i < 12; i++) {
      refs.push(refForPenalty(referenceMonths[i]));
      weights.push(snapToFive(referenceMonths[i]));
    }
    var steps = 0;
    var maxSteps = 500;
    while (sumOf(weights) !== TARGET_SUM && steps < maxSteps) {
      steps++;
      var total = sumOf(weights);
      var direction = total < TARGET_SUM ? 1 : -1;
      var step = HL_STEP * direction;
      var bestPenalty = null;
      var bestI = null;
      for (i = 0; i < 12; i++) {
        var candidate = weights[i] + step;
        if (candidate < HL_MIN || candidate > HL_MAX) continue;
        var penalty = Math.abs(candidate - refs[i]) - Math.abs(weights[i] - refs[i]);
        if (
          bestPenalty == null ||
          penalty < bestPenalty ||
          (penalty === bestPenalty && bestI != null && i < bestI)
        ) {
          bestPenalty = penalty;
          bestI = i;
        }
      }
      if (bestI == null) {
        return {
          ok: false,
          reason: 'stuck',
          weights: weights.slice(),
          sum: sumOf(weights),
          steps: steps,
        };
      }
      weights[bestI] += step;
    }
    var s = sumOf(weights);
    return {
      ok: s === TARGET_SUM,
      reason: s === TARGET_SUM ? null : 'unbalanced',
      weights: weights.slice(),
      sum: s,
      avg: Math.round((s / 12) * 100) / 100,
      steps: steps,
      roundedOnly: steps === 0,
    };
  }

  function sumOf(arr) {
    var s = 0;
    for (var i = 0; i < arr.length; i++) s += Number(arr[i]) || 0;
    return s;
  }

  function weightsEqual(a, b) {
    if (!a || !b || a.length !== 12 || b.length !== 12) return false;
    for (var i = 0; i < 12; i++) {
      if (Number(a[i]) !== Number(b[i])) return false;
    }
    return true;
  }

  function referenceSourceSignature(year, months, yearsUsed) {
    var parts = [];
    for (var i = 0; i < 12; i++) {
      var m = months && months[i];
      var v = Number(m);
      parts.push(Number.isFinite(v) ? v.toFixed(2) : 'null');
    }
    var yuList = (yearsUsed || [])
      .map(function (y) {
        return Number(y);
      })
      .filter(function (y) {
        return Number.isFinite(y);
      })
      .sort(function (a, b) {
        return a - b;
      });
    var yu = yuList.join(',');
    var cnt = yuList.length;
    return 'ref:' + Number(year) + ':n=' + cnt + ':' + yu + ':' + parts.join('|');
  }

  var api = {
    __ready: true,
    HL_MIN: HL_MIN,
    HL_MAX: HL_MAX,
    HL_STEP: HL_STEP,
    TARGET_SUM: TARGET_SUM,
    snapToFive: snapToFive,
    projectAndBalance: projectAndBalance,
    weightsEqual: weightsEqual,
    referenceSourceSignature: referenceSourceSignature,
  };

  global.KpiSeasonalityAllocator = api;
})(typeof window !== 'undefined' ? window : this);

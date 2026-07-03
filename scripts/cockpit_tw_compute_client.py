"""Cockpit-only TW metrics compute (pages without full Focus TW timeline)."""

from __future__ import annotations

COCKPIT_TW_MARKER = "/* KPI-COCKPIT-TW-COMPUTE */"
COCKPIT_TW_END = "/* END KPI-COCKPIT-TW-COMPUTE */"


def cockpit_tw_compute_js() -> str:
    return f"""    {COCKPIT_TW_MARKER}
    (function () {{
      if (typeof window.__computeTwMetricsForIso === 'function') return;
      var isJa = document.documentElement.getAttribute('lang') === 'ja';
      function pad2(n) {{
        return n < 10 ? '0' + n : String(n);
      }}
      function fmtMoney(n) {{
        if (n == null || !isFinite(Number(n))) return '—';
        var v = Math.round(Number(n));
        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');
      }}
      function isTimelineBusinessDay(iso, bmap, isWeekend) {{
        if (Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
        return !isWeekend;
      }}
      function readTwSalesAmt(iso, smap) {{
        if (!smap || !Object.prototype.hasOwnProperty.call(smap, iso)) return 0;
        var n = Number(smap[iso]);
        if (!Number.isFinite(n) || n === 1234) return 0;
        return n;
      }}
      function twDefaultHlWeights() {{
        return [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115];
      }}
      function resolveTwPlanForYear(year) {{
        var y = Number(year);
        if (!Number.isFinite(y)) return null;
        var oy = window.KpiYearStore ? KpiYearStore.getOperatingYear() : new Date().getFullYear();
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = oy;
        var target = null;
        var weights = null;
        if (window.KpiYearStore) {{
          target = KpiYearStore.readAnnualTarget(y);
          weights = KpiYearStore.readMonthlyHlWeights(y);
          if (KpiYearStore.isYearLocked(y)) {{
            if (target == null || !Number.isFinite(Number(target)) || Number(target) <= 0) return null;
          }} else if (y === oy || y === cy) {{
            if (
              (target == null || !Number.isFinite(Number(target)) || Number(target) <= 0) &&
              window.__ANNUAL_DATA &&
              window.__ANNUAL_DATA.targetSales != null
            ) {{
              target = Number(window.__ANNUAL_DATA.targetSales);
            }}
          }} else if (y < oy) {{
          }} else {{
            return null;
          }}
        }} else if (window.__ANNUAL_DATA && y === cy && window.__ANNUAL_DATA.targetSales != null) {{
          target = Number(window.__ANNUAL_DATA.targetSales);
        }}
        if (target == null || !Number.isFinite(Number(target)) || Number(target) <= 0) {{
          var past = window.__ANNUAL_DATA && window.__ANNUAL_DATA.pastSales;
          if (
            past &&
            past.referenceAnnualSalesByYear &&
            past.referenceAnnualSalesByYear[y] != null
          ) {{
            target = Number(past.referenceAnnualSalesByYear[y]);
          }}
        }}
        if (target == null || !Number.isFinite(Number(target)) || Number(target) <= 0) return null;
        if (!weights || weights.length !== 12) weights = twDefaultHlWeights();
        return {{ target: Number(target), weights: weights.slice() }};
      }}
      function buildDailyTargetMapForYear(year, bmap) {{
        var y = Number(year);
        var plan = resolveTwPlanForYear(y);
        var out = {{}};
        if (!plan) return out;
        var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        var days = [];
        for (var m0 = 0; m0 < 12; m0++) {{
          var dc = new Date(y, m0 + 1, 0).getDate();
          for (var day = 1; day <= dc; day++) {{
            var dt = new Date(y, m0, day);
            var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
            var isWk = dt.getDay() === 0 || dt.getDay() === 6;
            if (!isTimelineBusinessDay(iso, bmap, isWk)) continue;
            monthlyBD[m0]++;
            days.push({{ iso: iso, m0: m0 }});
          }}
        }}
        var totalBD = days.length;
        if (totalBD <= 0) return out;
        var annualTarget = plan.target;
        var monthlyDailyTarget = [];
        for (var mi = 0; mi < 12; mi++) {{
          var hl = Number(plan.weights[mi]);
          if (!Number.isFinite(hl)) hl = 100;
          var bdCount = monthlyBD[mi];
          if (bdCount <= 0) {{
            monthlyDailyTarget[mi] = NaN;
            continue;
          }}
          var monthlyAvg = (annualTarget * bdCount) / totalBD;
          var monthlyTarget = (monthlyAvg * hl) / 100;
          monthlyDailyTarget[mi] = monthlyTarget / bdCount;
        }}
        for (var i = 0; i < days.length; i++) {{
          var item = days[i];
          var dt = monthlyDailyTarget[item.m0];
          if (Number.isFinite(dt) && dt > 0) out[item.iso] = dt;
        }}
        return out;
      }}
      var TW_DIFF_LEVELS = [
        'tw-diff--win',
        'tw-diff--neutral',
        'tw-diff--sev-90',
        'tw-diff--sev-80',
        'tw-diff--sev-70',
        'tw-diff--sev-60',
        'tw-diff--sev-50',
        'tw-diff--sev-below',
      ];
      function twDiffAchPct(actual, target) {{
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return NaN;
        return (actual / target) * 100;
      }}
      function twDiffSeverityClass(actual, target) {{
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return 'tw-diff--neutral';
        var diff = actual - target;
        if (diff > 0) return 'tw-diff--win';
        if (diff === 0) return 'tw-diff--neutral';
        var ach = twDiffAchPct(actual, target);
        if (ach >= 90) return 'tw-diff--sev-90';
        if (ach >= 80) return 'tw-diff--sev-80';
        if (ach >= 70) return 'tw-diff--sev-70';
        if (ach >= 60) return 'tw-diff--sev-60';
        if (ach >= 50) return 'tw-diff--sev-50';
        return 'tw-diff--sev-below';
      }}
      function fmtTwSignedMoney(n) {{
        if (!Number.isFinite(n)) return '—';
        if (n === 0) return fmtMoney(0);
        var r = Math.round(Math.abs(n));
        var body = isJa ? '¥' + r.toLocaleString('ja-JP') : '$' + r.toLocaleString('en-US');
        return (n > 0 ? '+' : '−') + body;
      }}
      function fmtTwDiff(actual, target) {{
        if (!Number.isFinite(actual) || !Number.isFinite(target)) return '—';
        return fmtTwSignedMoney(actual - target);
      }}
      function computeTwMetricsForIso(iso) {{
        if (!iso) return null;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        var d = new Date(String(iso).trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        var y = d.getFullYear();
        var m0 = d.getMonth();
        var tgtMap = buildDailyTargetMapForYear(y, bmap);
        var plan = resolveTwPlanForYear(y);
        var annualTarget = plan && Number.isFinite(Number(plan.target)) ? Number(plan.target) : null;
        var hasPlan = false;
        var isBusinessToday = false;
        var dailySales = 0;
        var dailyTarget = null;
        var mtdA = 0;
        var mtdT = 0;
        var ytdA = 0;
        var ytdT = 0;
        var monthlyFullTarget = 0;
        var monthRemainingBD = 0;
        var yearRemainingBD = 0;
        for (var m = 0; m < 12; m++) {{
          var dc = new Date(y, m + 1, 0).getDate();
          for (var day = 1; day <= dc; day++) {{
            var dt = new Date(y, m, day);
            var dayIso = y + '-' + pad2(m + 1) + '-' + pad2(day);
            var isWk = dt.getDay() === 0 || dt.getDay() === 6;
            if (!isTimelineBusinessDay(dayIso, bmap, isWk)) continue;
            var dayTarget = null;
            if (Object.prototype.hasOwnProperty.call(tgtMap, dayIso)) {{
              dayTarget = Number(tgtMap[dayIso]);
              if (!Number.isFinite(dayTarget)) dayTarget = null;
            }}
            if (m === m0 && dayTarget != null) monthlyFullTarget += dayTarget;
            if (dayIso <= iso) {{
              var salesAmt = readTwSalesAmt(dayIso, smap);
              ytdA += salesAmt;
              if (m === m0) mtdA += salesAmt;
              if (dayTarget != null) {{
                ytdT += dayTarget;
                hasPlan = true;
                if (m === m0) mtdT += dayTarget;
              }}
            }}
            if (dayIso >= iso) {{
              if (m === m0) monthRemainingBD++;
              yearRemainingBD++;
            }}
            if (dayIso === iso) {{
              isBusinessToday = true;
              dailySales = readTwSalesAmt(dayIso, smap);
              dailyTarget = dayTarget;
            }}
          }}
        }}
        var monthlyNeed =
          hasPlan && Number.isFinite(monthlyFullTarget) ? monthlyFullTarget - mtdA : null;
        var monthlyDailyNeed =
          monthRemainingBD > 0 && monthlyNeed != null && Number.isFinite(monthlyNeed)
            ? monthlyNeed / monthRemainingBD
            : null;
        var annualRemaining =
          annualTarget != null && Number.isFinite(annualTarget) ? annualTarget - ytdA : null;
        var annualDailyNeed =
          yearRemainingBD > 0 &&
          annualRemaining != null &&
          Number.isFinite(annualRemaining)
            ? annualRemaining / yearRemainingBD
            : null;
        return {{
          iso: iso,
          isBusinessToday: isBusinessToday,
          hasPlan: hasPlan,
          dailySales: dailySales,
          dailyTarget: dailyTarget,
          mtdA: mtdA,
          mtdT: mtdT,
          ytdA: ytdA,
          ytdT: ytdT,
          monthlyFullTarget: monthlyFullTarget,
          monthRemainingBD: monthRemainingBD,
          monthlyDailyNeed: monthlyDailyNeed,
          annualTarget: annualTarget,
          annualRemaining: annualRemaining,
          yearRemainingBD: yearRemainingBD,
          annualDailyNeed: annualDailyNeed,
        }};
      }}
      window.__computeTwMetricsForIso = computeTwMetricsForIso;
      window.__twFmtMoney = fmtMoney;
      window.__twFmtDiff = fmtTwDiff;
      window.__twDiffSeverityClass = twDiffSeverityClass;
      window.__twDiffLevels = TW_DIFF_LEVELS;
    }})();
    {COCKPIT_TW_END}"""

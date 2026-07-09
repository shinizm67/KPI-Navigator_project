"""Focus Bar / Table Window — Target vs Actual metrics from KpiYearStore plan + timeline."""

from __future__ import annotations

from focus_bar_timeline_scroll_client import FILL_STATE_HELPERS

FOCUS_TW_MARKER = "/* KPI-FOCUS-TW-METRICS */"
FOCUS_TW_END = "/* END KPI-FOCUS-TW-METRICS */"

RENDER_TIMELINE_OLD = """      function renderAnnualDailyTimeline(anchorYear, opts) {
        opts = opts || {};
        anchorYear = Number(anchorYear);
        if (!Number.isFinite(anchorYear)) anchorYear = new Date().getFullYear();
        var scrollEl = document.getElementById('annual-daily-focus-scroll');
        var prevScroll = opts.preserveScroll && scrollEl ? scrollEl.scrollTop : null;
        var bounds = computeFocusTimelineBounds(anchorYear);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.calendarYear = anchorYear;
        var daily = window.__ANNUAL_DATA.daily || {};
        var tmap = daily.targetSalesByDate || {};
        var bmap = daily.businessDayByDate || {};
        rowsRoot.innerHTML = '';"""


def focus_tw_metrics_js() -> str:
    return f"""      {FOCUS_TW_MARKER}
{FILL_STATE_HELPERS}
      function fmtTwAchPct(actual, target) {{
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return '—';
        return Math.round((actual / target) * 100) + '%';
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
      function applyTwDiffCellClass(cell, actual, target) {{
        if (!cell) return;
        for (var i = 0; i < TW_DIFF_LEVELS.length; i++) {{
          cell.classList.remove(TW_DIFF_LEVELS[i]);
        }}
        cell.classList.remove('annual-daily-row__cell--neg');
        cell.classList.add(twDiffSeverityClass(actual, target));
      }}
      function readTwSalesAmt(iso, smap) {{
        if (!smap || !Object.prototype.hasOwnProperty.call(smap, iso)) return 0;
        var n = Number(smap[iso]);
        if (!Number.isFinite(n)) return 0;
        if (n === 1234) {{
          var oy = window.KpiYearStore
            ? KpiYearStore.getOperatingYear()
            : new Date().getFullYear();
          var y = Number(String(iso || '').split('-')[0]);
          if (Number.isFinite(y) && y < oy) return n;
          return 0;
        }}
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
            /* past year: fall through to referenceAnnualSalesByYear fallback */
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
      function buildLegacyFlatDailyTargetMapForYear(plan, days) {{
        var out = {{}};
        var totalBD = days.length;
        if (totalBD <= 0) return out;
        var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        for (var di = 0; di < days.length; di++) {{
          monthlyBD[days[di].m0]++;
        }}
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
      function twShouldUseDailyTargetResolver(year) {{
        if (!window.KpiYearStore) return false;
        if (typeof KpiYearStore.resolveDailyTargetByIso !== 'function') return false;
        if (typeof KpiYearStore.getOperatingYear !== 'function') return false;
        var y = Number(year);
        var oy = KpiYearStore.getOperatingYear();
        if (!Number.isFinite(y) || y !== oy) return false;
        return true;
      }}
      function buildDailyTargetMapForYear(year, bmap) {{
        var y = Number(year);
        var plan = resolveTwPlanForYear(y);
        var out = {{}};
        if (!plan) return out;
        var days = [];
        for (var m0 = 0; m0 < 12; m0++) {{
          var dc = new Date(y, m0 + 1, 0).getDate();
          for (var day = 1; day <= dc; day++) {{
            var dt = new Date(y, m0, day);
            var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
            var isWk = dt.getDay() === 0 || dt.getDay() === 6;
            if (!isTimelineBusinessDay(iso, bmap, isWk)) continue;
            days.push({{ iso: iso, m0: m0 }});
          }}
        }}
        if (twShouldUseDailyTargetResolver(y)) {{
          for (var ri = 0; ri < days.length; ri++) {{
            var row = days[ri];
            var resolved = KpiYearStore.resolveDailyTargetByIso(y, row.iso);
            var val = resolved && resolved.value;
            if (Number.isFinite(val) && val > 0) out[row.iso] = val;
          }}
          return out;
        }}
        return buildLegacyFlatDailyTargetMapForYear(plan, days);
      }}
      function createTwCumState() {{
        return {{ month: -1, mtdA: 0, mtdT: 0, ytdA: 0, ytdT: 0, hasPlan: false }};
      }}
      function renderAnnualDailyTimeline(anchorYear, opts) {{
        opts = opts || {{}};
        anchorYear = Number(anchorYear);
        if (!Number.isFinite(anchorYear)) anchorYear = new Date().getFullYear();
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var scrollEl = document.getElementById('annual-daily-focus-scroll');
        var prevScroll = opts.preserveScroll && scrollEl ? scrollEl.scrollTop : null;
        var bounds = computeFocusTimelineBounds(anchorYear);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {{}};
        window.__ANNUAL_DATA.calendarYear = anchorYear;
        var daily = window.__ANNUAL_DATA.daily || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        var targetMapsByYear = {{}};
        var cumByYear = {{}};
        var memoFlagMapsByYear = {{}};
        function memoFlagMapForYear(y) {{
          if (!memoFlagMapsByYear[y]) {{
            memoFlagMapsByYear[y] =
              window.KpiYearStore &&
              typeof KpiYearStore.readDailyMemoFlagMapForYear === 'function'
                ? KpiYearStore.readDailyMemoFlagMapForYear(y)
                : {{}};
          }}
          return memoFlagMapsByYear[y];
        }}
        function targetMapForYear(y) {{
          if (!targetMapsByYear[y]) targetMapsByYear[y] = buildDailyTargetMapForYear(y, bmap);
          return targetMapsByYear[y];
        }}
        function cumForYear(y) {{
          if (!cumByYear[y]) cumByYear[y] = createTwCumState();
          return cumByYear[y];
        }}
        rowsRoot.innerHTML = '';
        rowsRoot.setAttribute('data-year', String(anchorYear));
        rowsRoot.setAttribute('data-timeline-min-year', String(bounds.minYear));
        rowsRoot.setAttribute('data-timeline-max-year', String(bounds.maxYear));
        rowsRoot.setAttribute(
          'aria-label',
          isJa
            ? bounds.minYear + '〜' + bounds.maxYear + '年の日次一覧'
            : 'Daily rows ' + bounds.minYear + '–' + bounds.maxYear
        );

        var prevYearMarker = null;
        for (var d = new Date(bounds.rangeStart); d <= bounds.rangeEnd; d.setDate(d.getDate() + 1)) {{
          var iso =
            d.getFullYear() +
            '-' +
            pad2(d.getMonth() + 1) +
            '-' +
            pad2(d.getDate());
          var dow = d.getDay();
          var isWeekend = dow === 0 || dow === 6;
          var isBusiness = isTimelineBusinessDay(iso, bmap, isWeekend);
          var rowYear = d.getFullYear();
          var isOutsideYear = rowYear !== anchorYear;
          var row = document.createElement('div');
          row.className =
            'annual-daily-row' +
            (!isBusiness ? ' annual-daily-row--off' : '') +
            (isOutsideYear ? ' annual-daily-row--outside-year' : '');
          if (d.getMonth() === 0 && d.getDate() === 1 && prevYearMarker !== rowYear) {{
            row.classList.add('annual-daily-row--year-boundary');
            prevYearMarker = rowYear;
          }}
          row.setAttribute('role', 'listitem');
          row.setAttribute('data-iso-date', iso);
          row.setAttribute('data-row-year', String(rowYear));
          row.setAttribute('data-active-year', isOutsideYear ? '0' : '1');

          var dateLabel;
          if (isJa) {{
            dateLabel = d.getMonth() + 1 + '/' + d.getDate() + ' ' + WEEKDAYS_JA[dow];
            if (!isBusiness) dateLabel += ' OFF';
          }} else {{
            dateLabel = d.getMonth() + 1 + '/' + d.getDate() + ' ' + WEEKDAYS_EN[dow];
            if (!isBusiness) dateLabel += ' OFF';
          }}

          var dash = '—';
          function createCell(fieldKey, value, extraClass) {{
            var cell = document.createElement('div');
            var cls = 'annual-daily-row__cell';
            if (extraClass) cls += ' ' + extraClass;
            if (fieldKey === 'target' || fieldKey === 'monthlyTarget' || fieldKey === 'annualTarget') {{
              cls += ' annual-daily-row__cell--plan-target';
            }}
            cell.className = cls;
            if (fieldKey) {{
              cell.setAttribute('data-field', 'annual.dailyTable.' + iso + '.' + fieldKey);
              applyDailyCellFillState(cell, fieldKey, value, !isBusiness, isOutsideYear, dash);
            }}
            cell.textContent = value;
            return cell;
          }}
          function createDiffCell(fieldKey, actual, target, enabled) {{
            var cell = document.createElement('div');
            cell.className = 'annual-daily-row__cell';
            var display = enabled ? fmtTwDiff(actual, target) : dash;
            if (fieldKey) {{
              cell.setAttribute('data-field', 'annual.dailyTable.' + iso + '.' + fieldKey);
              applyDailyCellFillState(cell, fieldKey, display, !isBusiness, isOutsideYear, dash);
            }}
            cell.textContent = display;
            if (enabled) applyTwDiffCellClass(cell, actual, target);
            return cell;
          }}

          var salesNum = 0;
          var dailyTgt = null;
          var mtdA = 0;
          var mtdT = 0;
          var ytdA = 0;
          var ytdT = 0;
          var rowHasPlan = false;
          if (isBusiness) {{
            salesNum = readTwSalesAmt(iso, smap);
            var tgtMap = targetMapForYear(rowYear);
            if (Object.prototype.hasOwnProperty.call(tgtMap, iso)) {{
              dailyTgt = Number(tgtMap[iso]);
              if (!Number.isFinite(dailyTgt)) dailyTgt = null;
            }}
            var c = cumForYear(rowYear);
            var m0 = d.getMonth();
            if (c.month !== m0) {{
              c.month = m0;
              c.mtdA = 0;
              c.mtdT = 0;
            }}
            c.mtdA += salesNum;
            c.ytdA += salesNum;
            if (dailyTgt != null) {{
              c.mtdT += dailyTgt;
              c.ytdT += dailyTgt;
              c.hasPlan = true;
            }}
            mtdA = c.mtdA;
            mtdT = c.mtdT;
            ytdA = c.ytdA;
            ytdT = c.ytdT;
            rowHasPlan = c.hasPlan;
          }}

          var groupBase = document.createElement('div');
          groupBase.className = 'annual-daily-row__group annual-daily-row__group--base';
          var dateCell = createCell(null, dateLabel, 'annual-daily-row__cell--date');
          if (memoFlagMapForYear(rowYear)[iso]) {{
            dateCell.classList.add('annual-daily-row__cell--has-memo');
            dateCell.setAttribute('data-has-memo', '1');
            dateCell.setAttribute(
              'title',
              isJa ? 'メモがあります' : 'Memo saved'
            );
            dateCell.setAttribute(
              'aria-label',
              isJa ? dateLabel + '（メモあり）' : dateLabel + ' (memo saved)'
            );
          }}
          groupBase.appendChild(dateCell);
          if (!isBusiness) {{
            groupBase.appendChild(createCell('sales', dash));
            groupBase.appendChild(createCell('target', dash));
            groupBase.appendChild(createCell('diff', dash));
            groupBase.appendChild(createCell('ach', dash));
          }} else {{
            groupBase.appendChild(createCell('sales', fmtMoney(salesNum)));
            groupBase.appendChild(
              createCell('target', dailyTgt != null ? fmtMoney(dailyTgt) : dash)
            );
            groupBase.appendChild(
              createDiffCell('diff', salesNum, dailyTgt, dailyTgt != null)
            );
            groupBase.appendChild(
              createCell(
                'ach',
                dailyTgt != null ? fmtTwAchPct(salesNum, dailyTgt) : dash
              )
            );
          }}

          var groupMonthly = document.createElement('div');
          groupMonthly.className = 'annual-daily-row__group annual-daily-row__group--monthly';
          if (!isBusiness) {{
            groupMonthly.appendChild(createCell('monthlyTarget', dash));
            groupMonthly.appendChild(createCell('monthlySales', dash));
            groupMonthly.appendChild(createCell('monthlyDiff', dash));
            groupMonthly.appendChild(createCell('monthlyAch', dash));
          }} else {{
            groupMonthly.appendChild(
              createCell('monthlyTarget', rowHasPlan ? fmtMoney(mtdT) : dash)
            );
            groupMonthly.appendChild(createCell('monthlySales', fmtMoney(mtdA)));
            groupMonthly.appendChild(
              createDiffCell('monthlyDiff', mtdA, mtdT, rowHasPlan)
            );
            groupMonthly.appendChild(
              createCell('monthlyAch', rowHasPlan ? fmtTwAchPct(mtdA, mtdT) : dash)
            );
          }}

          var groupAnnual = document.createElement('div');
          groupAnnual.className = 'annual-daily-row__group annual-daily-row__group--annual';
          if (!isBusiness) {{
            groupAnnual.appendChild(createCell('annualTarget', dash));
            groupAnnual.appendChild(createCell('annualSales', dash));
            groupAnnual.appendChild(createCell('annualDiff', dash));
            groupAnnual.appendChild(createCell('annualAch', dash));
          }} else {{
            groupAnnual.appendChild(
              createCell('annualTarget', rowHasPlan ? fmtMoney(ytdT) : dash)
            );
            groupAnnual.appendChild(createCell('annualSales', fmtMoney(ytdA)));
            groupAnnual.appendChild(
              createDiffCell('annualDiff', ytdA, ytdT, rowHasPlan)
            );
            groupAnnual.appendChild(
              createCell('annualAch', rowHasPlan ? fmtTwAchPct(ytdA, ytdT) : dash)
            );
          }}

          row.appendChild(groupBase);
          row.appendChild(groupMonthly);
          row.appendChild(groupAnnual);
          rowsRoot.appendChild(row);
        }}

        if (prevScroll != null && scrollEl) {{
          scrollEl.scrollTop = prevScroll;
        }}
        document.dispatchEvent(new CustomEvent('annual:timelineRowsRendered'));
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
      window.__twFmtAchPct = fmtTwAchPct;
      window.__twDiffSeverityClass = twDiffSeverityClass;
      window.__twDiffLevels = TW_DIFF_LEVELS;
      var __twTimelineRefreshTimer = null;
      function scheduleRenderAnnualDailyTimeline(anchorYear, opts) {{
        opts = opts || {{ preserveScroll: true }};
        var cy = Number(anchorYear);
        if (!Number.isFinite(cy)) {{
          cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        }}
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        if (__twTimelineRefreshTimer != null) window.clearTimeout(__twTimelineRefreshTimer);
        __twTimelineRefreshTimer = window.setTimeout(function () {{
          __twTimelineRefreshTimer = null;
          renderAnnualDailyTimeline(cy, opts);
        }}, 32);
      }}
      window.__scheduleRenderAnnualDailyTimeline = scheduleRenderAnnualDailyTimeline;
      {FOCUS_TW_END}"""


FOCUS_TW_LISTENERS_OLD = """      document.addEventListener('annual:salesMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);"""

FOCUS_BAR_REFRESH_OLD = """      document.addEventListener('annual:calendarYearChanged', function () {
        setTimeout(refreshLower, 0);
      });
      setTimeout(refreshLower, 0);"""

FOCUS_BAR_REFRESH_NEW = """      document.addEventListener('annual:calendarYearChanged', function () {
        setTimeout(refreshLower, 0);
      });
      document.addEventListener('annual:timelineRowsRendered', function () {
        setTimeout(refreshLower, 0);
      });
      /* KPI-FOCUS-BAR-READ-SURFACES-11-5 */
      document.addEventListener('kpi:dailyTargetModeChanged', function () {
        setTimeout(refreshLower, 0);
      });
      document.addEventListener('kpi:weekdayBaselineChanged', function () {
        setTimeout(refreshLower, 0);
      });
      setTimeout(refreshLower, 0);"""

FOCUS_TW_LISTENERS_NEW = """      document.addEventListener('annual:salesMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:dailySalesChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:businessDayChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:annualPlanChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:dailyTargetModeChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:weekdayBaselineChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:mepDataChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:salesDataSaved', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastSalesSaved', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastSalesMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastBusinessDayMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);"""

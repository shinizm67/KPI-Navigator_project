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
        if (twShouldUseDailyTargetResolver(y)) {{
          if (
            window.KpiYearStore &&
            typeof KpiYearStore.buildDailyTargetDisplayMapForYear === 'function'
          ) {{
            return KpiYearStore.buildDailyTargetDisplayMapForYear(y);
          }}
        }}
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
      var __twTargetMapCacheByYear = {{}};
      function buildDailyTargetMapForYearCached(year, bmap) {{
        var y = Number(year);
        if (!Number.isFinite(y)) return {{}};
        if (__twTargetMapCacheByYear[y]) return __twTargetMapCacheByYear[y];
        var map = buildDailyTargetMapForYear(y, bmap);
        __twTargetMapCacheByYear[y] = map;
        return map;
      }}
      window.clearTwTargetMapsByYear = function () {{
        __twTargetMapCacheByYear = {{}};
      }};
      document.addEventListener('kpi:dailyTargetModeChanged', function () {{
        __twTargetMapCacheByYear = {{}};
      }});
      document.addEventListener('kpi:weekdayBaselineChanged', function () {{
        __twTargetMapCacheByYear = {{}};
      }});
      document.addEventListener('kpi:annualPlanChanged', function () {{
        __twTargetMapCacheByYear = {{}};
      }});
      window.__buildDailyTargetMapForYear = buildDailyTargetMapForYear;
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
        var bounds =
          opts.boundsHint === 'anchor-year-only' &&
          typeof computeAnchorYearTimelineBounds === 'function'
            ? computeAnchorYearTimelineBounds(anchorYear)
            : computeFocusTimelineBounds(anchorYear);
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
        if (document.body.classList.contains('monthly-page')) {{
          if (opts.boundsHint === 'anchor-year-only') {{
            window.__monthlyVerticalTwPartialRendered = true;
          }} else {{
            window.__monthlyVerticalTwPartialRendered = true;
            window.__monthlyVerticalTwFullRendered = true;
          }}
        }}
        document.dispatchEvent(new CustomEvent('annual:timelineRowsRendered'));
      }}
      function buildMonthlyCumulativeTrendPayload(year, month, cutoffIso) {{
        var y = Number(year);
        var m = Number(month);
        if (!Number.isFinite(y) || !Number.isFinite(m) || m < 1 || m > 12) return null;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        var dim = new Date(y, m, 0).getDate();
        var cutoffDay = dim;
        if (cutoffIso) {{
          var parts = String(cutoffIso).split('-');
          var cy = Number(parts[0]);
          var cm = Number(parts[1]);
          var cd = Number(parts[2]);
          if (cy === y && cm === m && Number.isFinite(cd)) {{
            cutoffDay = Math.max(1, Math.min(dim, cd));
          }}
        }}
        var tgtMap = buildDailyTargetMapForYearCached(y, bmap);
        var target = [];
        var actual = [];
        var dailyTarget = [];
        var dailyActual = [];
        var tSum = 0;
        var aSum = 0;
        for (var day = 1; day <= dim; day++) {{
          var dayIso = y + '-' + pad2(m) + '-' + pad2(day);
          var dt = new Date(y, m - 1, day);
          var isWk = dt.getDay() === 0 || dt.getDay() === 6;
          var isBiz = isTimelineBusinessDay(dayIso, bmap, isWk);
          var dtVal = 0;
          var daVal = 0;
          if (isBiz) {{
            if (Object.prototype.hasOwnProperty.call(tgtMap, dayIso)) {{
              var t = Number(tgtMap[dayIso]);
              if (Number.isFinite(t)) dtVal = t;
            }}
            if (day <= cutoffDay) daVal = readTwSalesAmt(dayIso, smap);
          }}
          tSum += dtVal;
          if (day <= cutoffDay) aSum += daVal;
          dailyTarget.push(dtVal);
          dailyActual.push(daVal);
          target.push(tSum);
          actual.push(aSum);
        }}
        return {{
          target: target,
          actual: actual,
          dailyTarget: dailyTarget,
          dailyActual: dailyActual,
          todayDay: cutoffDay,
        }};
      }}
      window.__buildMonthlyCumulativeTrendPayload = buildMonthlyCumulativeTrendPayload;
      function buildAnnualCumulativeTrendPayload(year, cutoffIso) {{
        var y = Number(year);
        if (!Number.isFinite(y)) return null;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        var dim = (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0 ? 366 : 365;
        var cutoffDay = dim;
        if (cutoffIso) {{
          var cp = String(cutoffIso).split('-');
          var cy = Number(cp[0]);
          if (cy === y) {{
            var cm = Number(cp[1]);
            var cd = Number(cp[2]);
            if (Number.isFinite(cm) && Number.isFinite(cd)) {{
              var dtCut = new Date(y, cm - 1, cd);
              cutoffDay = Math.floor((dtCut - new Date(y, 0, 1)) / 86400000) + 1;
              cutoffDay = Math.max(0, Math.min(dim, cutoffDay));
            }}
          }} else if (String(cutoffIso) < y + '-01-01') {{
            cutoffDay = 0;
          }}
        }}
        var tgtMap = buildDailyTargetMapForYearCached(y, bmap);
        var target = [];
        var actual = [];
        var dailyTarget = [];
        var dailyActual = [];
        var tSum = 0;
        var aSum = 0;
        for (var doy = 1; doy <= dim; doy++) {{
          var dtObj = new Date(y, 0, doy);
          var month = dtObj.getMonth() + 1;
          var day = dtObj.getDate();
          var dayIso = y + '-' + pad2(month) + '-' + pad2(day);
          var isWk = dtObj.getDay() === 0 || dtObj.getDay() === 6;
          var dtVal = 0;
          var daVal = 0;
          if (isTimelineBusinessDay(dayIso, bmap, isWk)) {{
            if (Object.prototype.hasOwnProperty.call(tgtMap, dayIso)) {{
              var t = Number(tgtMap[dayIso]);
              if (Number.isFinite(t)) dtVal = t;
            }}
            if (cutoffDay > 0 && doy <= cutoffDay) {{
              daVal = readTwSalesAmt(dayIso, smap);
            }}
          }}
          dailyTarget.push(dtVal);
          dailyActual.push(daVal);
          tSum += dtVal;
          if (cutoffDay > 0 && doy <= cutoffDay) aSum += daVal;
          target.push(tSum);
          actual.push(aSum);
        }}
        return {{
          target: target,
          actual: actual,
          dailyTarget: dailyTarget,
          dailyActual: dailyActual,
          todayDay: cutoffDay,
        }};
      }}
      window.__buildAnnualCumulativeTrendPayload = buildAnnualCumulativeTrendPayload;
      function buildAnnualCompareTrendPayload(year, cutoffIso) {{
        var y = Number(year);
        if (!Number.isFinite(y)) return null;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        function dimOf(yy) {{
          return (yy % 4 === 0 && yy % 100 !== 0) || yy % 400 === 0 ? 366 : 365;
        }}
        var dim = dimOf(y);
        var cutoffDay = dim;
        if (cutoffIso) {{
          var cp = String(cutoffIso).split('-');
          var cy = Number(cp[0]);
          if (cy === y) {{
            var cm = Number(cp[1]);
            var cd = Number(cp[2]);
            if (Number.isFinite(cm) && Number.isFinite(cd)) {{
              var dtCut = new Date(y, cm - 1, cd);
              cutoffDay = Math.floor((dtCut - new Date(y, 0, 1)) / 86400000) + 1;
              cutoffDay = Math.max(0, Math.min(dim, cutoffDay));
            }}
          }} else if (String(cutoffIso) < y + '-01-01') {{
            cutoffDay = 0;
          }}
        }}
        function seriesForYear(yy, untilDoy) {{
          var dimY = dimOf(yy);
          var maxD = untilDoy == null ? dimY : Math.max(0, Math.min(dimY, untilDoy));
          var arr = [];
          var sum = 0;
          for (var doy = 1; doy <= maxD; doy++) {{
            var dtObj = new Date(yy, 0, doy);
            var dayIso = yy + '-' + pad2(dtObj.getMonth() + 1) + '-' + pad2(dtObj.getDate());
            var isWk = dtObj.getDay() === 0 || dtObj.getDay() === 6;
            var daVal = 0;
            if (isTimelineBusinessDay(dayIso, bmap, isWk)) {{
              daVal = readTwSalesAmt(dayIso, smap);
            }}
            sum += daVal;
            arr.push(sum);
          }}
          return arr;
        }}
        function alignToDim(src, alignDim) {{
          var out = [];
          var last = 0;
          for (var i = 0; i < alignDim; i++) {{
            if (i < src.length) {{
              last = src[i];
              out.push(src[i]);
            }} else {{
              out.push(last);
            }}
          }}
          return out;
        }}
        var current = cutoffDay > 0 ? seriesForYear(y, cutoffDay) : [];
        var lastYear = alignToDim(seriesForYear(y - 1, null), dim);
        var bestYearNum = null;
        var bestTotal = -1;
        var scanYears = [];
        if (window.KpiYearStore && typeof KpiYearStore.getStore === 'function') {{
          try {{
            var st = KpiYearStore.getStore();
            if (st && st.years) {{
              Object.keys(st.years).forEach(function (k) {{
                var yn = Number(k);
                if (Number.isFinite(yn) && yn < y) scanYears.push(yn);
              }});
            }}
          }} catch (_e) {{}}
        }}
        if (!scanYears.length) {{
          for (var back = 1; back <= 15; back++) scanYears.push(y - back);
        }}
        scanYears.sort(function (a, b) {{ return b - a; }});
        for (var si = 0; si < scanYears.length; si++) {{
          var yy = scanYears[si];
          var full = seriesForYear(yy, null);
          var total = full.length ? full[full.length - 1] : 0;
          if (!(total > 0)) continue;
          if (total > bestTotal) {{
            bestTotal = total;
            bestYearNum = yy;
          }}
        }}
        var best = bestYearNum != null
          ? alignToDim(seriesForYear(bestYearNum, null), dim)
          : alignToDim([], dim);
        return {{
          current: current,
          lastYear: lastYear,
          best: best,
          todayDay: cutoffDay,
          bestYear: bestYearNum,
        }};
      }}
      window.__buildAnnualCompareTrendPayload = buildAnnualCompareTrendPayload;
      var twMetricsCache = {{}};
      function shiftTwIsoByDays(iso, delta) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        d.setDate(d.getDate() + (Number(delta) || 0));
        return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
      }}
      function finalizeTwMetricsNeeds(m) {{
        var monthlyNeed =
          m.hasPlan && Number.isFinite(m.monthlyFullTarget) ? m.monthlyFullTarget - m.mtdA : null;
        m.monthlyDailyNeed =
          m.monthRemainingBD > 0 && monthlyNeed != null && Number.isFinite(monthlyNeed)
            ? monthlyNeed / m.monthRemainingBD
            : null;
        m.annualRemaining =
          m.annualTarget != null && Number.isFinite(m.annualTarget) ? m.annualTarget - m.ytdA : null;
        m.annualDailyNeed =
          m.yearRemainingBD > 0 &&
          m.annualRemaining != null &&
          Number.isFinite(m.annualRemaining)
            ? m.annualRemaining / m.yearRemainingBD
            : null;
        return m;
      }}
      function cloneTwMetrics(src) {{
        return {{
          iso: src.iso,
          isBusinessToday: src.isBusinessToday,
          hasPlan: src.hasPlan,
          dailySales: src.dailySales,
          dailyTarget: src.dailyTarget,
          mtdA: src.mtdA,
          mtdT: src.mtdT,
          ytdA: src.ytdA,
          ytdT: src.ytdT,
          monthlyFullTarget: src.monthlyFullTarget,
          monthRemainingBD: src.monthRemainingBD,
          monthlyDailyNeed: src.monthlyDailyNeed,
          annualTarget: src.annualTarget,
          annualRemaining: src.annualRemaining,
          yearRemainingBD: src.yearRemainingBD,
          annualDailyNeed: src.annualDailyNeed,
        }};
      }}
      function tryIncrementalTwMetrics(fromIso, toIso, fromMetrics, direction) {{
        // direction: +1 = from -> to (to = from+1), -1 = from -> to (to = from-1)
        if (!fromMetrics || !fromIso || !toIso) return null;
        var fromD = new Date(String(fromIso).trim() + 'T00:00:00');
        var toD = new Date(String(toIso).trim() + 'T00:00:00');
        if (!isFinite(fromD.getTime()) || !isFinite(toD.getTime())) return null;
        if (fromD.getFullYear() !== toD.getFullYear()) return null;
        if (fromD.getMonth() !== toD.getMonth()) return null;
        ensureTwAnnualDailySynced();
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        var y = toD.getFullYear();
        var tgtMap = buildDailyTargetMapForYearCached(y, bmap);
        var m = cloneTwMetrics(fromMetrics);
        m.iso = toIso;

        function dayMeta(dayIso) {{
          var dd = new Date(String(dayIso).trim() + 'T00:00:00');
          var isWk = dd.getDay() === 0 || dd.getDay() === 6;
          var biz = isTimelineBusinessDay(dayIso, bmap, isWk);
          var dayTarget = null;
          if (Object.prototype.hasOwnProperty.call(tgtMap, dayIso)) {{
            dayTarget = Number(tgtMap[dayIso]);
            if (!Number.isFinite(dayTarget)) dayTarget = null;
          }}
          return {{
            biz: biz,
            sales: biz ? readTwSalesAmt(dayIso, smap) : 0,
            target: biz ? dayTarget : null,
          }};
        }}

        if (direction > 0) {{
          // leave fromIso, enter toIso
          var left = dayMeta(fromIso);
          if (left.biz) {{
            m.yearRemainingBD = Math.max(0, Number(m.yearRemainingBD) - 1);
            m.monthRemainingBD = Math.max(0, Number(m.monthRemainingBD) - 1);
          }}
          var entered = dayMeta(toIso);
          if (entered.biz) {{
            m.ytdA = Number(m.ytdA) + entered.sales;
            m.mtdA = Number(m.mtdA) + entered.sales;
            if (entered.target != null) {{
              m.ytdT = Number(m.ytdT) + entered.target;
              m.mtdT = Number(m.mtdT) + entered.target;
              m.hasPlan = true;
            }}
            m.isBusinessToday = true;
            m.dailySales = entered.sales;
            m.dailyTarget = entered.target;
          }} else {{
            m.isBusinessToday = false;
            m.dailySales = 0;
            m.dailyTarget = null;
          }}
        }} else {{
          // leave fromIso (newer), enter toIso (older)
          var dropped = dayMeta(fromIso);
          if (dropped.biz) {{
            m.ytdA = Number(m.ytdA) - dropped.sales;
            m.mtdA = Number(m.mtdA) - dropped.sales;
            if (dropped.target != null) {{
              m.ytdT = Number(m.ytdT) - dropped.target;
              m.mtdT = Number(m.mtdT) - dropped.target;
            }}
            m.yearRemainingBD = Number(m.yearRemainingBD) + 1;
            m.monthRemainingBD = Number(m.monthRemainingBD) + 1;
          }}
          var back = dayMeta(toIso);
          if (back.biz) {{
            m.isBusinessToday = true;
            m.dailySales = back.sales;
            m.dailyTarget = back.target;
          }} else {{
            m.isBusinessToday = false;
            m.dailySales = 0;
            m.dailyTarget = null;
          }}
        }}
        return finalizeTwMetricsNeeds(m);
      }}
      function computeTwMetricsForIso(iso) {{
        if (!iso) return null;
        if (Object.prototype.hasOwnProperty.call(twMetricsCache, iso)) {{
          return twMetricsCache[iso];
        }}
        var prevIso = shiftTwIsoByDays(iso, -1);
        if (prevIso && Object.prototype.hasOwnProperty.call(twMetricsCache, prevIso)) {{
          var fwd = tryIncrementalTwMetrics(prevIso, iso, twMetricsCache[prevIso], 1);
          if (fwd) {{
            twMetricsCache[iso] = fwd;
            return fwd;
          }}
        }}
        var nextIso = shiftTwIsoByDays(iso, 1);
        if (nextIso && Object.prototype.hasOwnProperty.call(twMetricsCache, nextIso)) {{
          var back = tryIncrementalTwMetrics(nextIso, iso, twMetricsCache[nextIso], -1);
          if (back) {{
            twMetricsCache[iso] = back;
            return back;
          }}
        }}

        ensureTwAnnualDailySynced();
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        var d = new Date(String(iso).trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        var y = d.getFullYear();
        var m0 = d.getMonth();
        var tgtMap = buildDailyTargetMapForYearCached(y, bmap);
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
        var result = finalizeTwMetricsNeeds({{
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
          monthlyDailyNeed: null,
          annualTarget: annualTarget,
          annualRemaining: null,
          yearRemainingBD: yearRemainingBD,
          annualDailyNeed: null,
        }});
        twMetricsCache[iso] = result;
        return result;
      }}
      var salesThroughCache = {{}};
      function invalidateTwSalesThroughCache() {{
        salesThroughCache = {{}};
        twMetricsCache = {{}};
        window.__TW_ANNUAL_DAILY_SYNCED = false;
      }}
      window.__invalidateTwSalesThroughCache = invalidateTwSalesThroughCache;
      function ensureTwAnnualDailySynced() {{
        if (window.__TW_ANNUAL_DAILY_SYNCED) return;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        window.__TW_ANNUAL_DAILY_SYNCED = true;
      }}
      function addOneSalesDay(acc, y, mm, d, smap, bmap) {{
        var dayIso = y + '-' + pad2(mm) + '-' + pad2(d);
        var dt = new Date(y, mm - 1, d);
        var isWk = dt.getDay() === 0 || dt.getDay() === 6;
        if (!isTimelineBusinessDay(dayIso, bmap, isWk)) return acc;
        if (Object.prototype.hasOwnProperty.call(smap, dayIso)) acc.hasData = true;
        acc.sum += readTwSalesAmt(dayIso, smap);
        return acc;
      }}
      function sumMonthSalesThroughDay(year, month, day) {{
        var y = Number(year);
        var m = Number(month);
        var dayN = Number(day);
        if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(dayN)) return null;
        if (m < 1 || m > 12) return null;
        var dim = new Date(y, m, 0).getDate();
        var until = Math.max(0, Math.min(dim, Math.floor(dayN)));
        var cacheKey = 'm:' + y + '-' + m + '-' + until;
        if (Object.prototype.hasOwnProperty.call(salesThroughCache, cacheKey)) {{
          return salesThroughCache[cacheKey];
        }}
        ensureTwAnnualDailySynced();
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        if (until > 0) {{
          var prevMKey = 'm:' + y + '-' + m + '-' + (until - 1);
          if (Object.prototype.hasOwnProperty.call(salesThroughCache, prevMKey)) {{
            var prevM = salesThroughCache[prevMKey];
            var fwdM = {{ sum: prevM.sum, hasData: prevM.hasData }};
            addOneSalesDay(fwdM, y, m, until, smap, bmap);
            salesThroughCache[cacheKey] = fwdM;
            return fwdM;
          }}
        }}
        if (until < dim) {{
          var nextMKey = 'm:' + y + '-' + m + '-' + (until + 1);
          if (Object.prototype.hasOwnProperty.call(salesThroughCache, nextMKey)) {{
            var nextM = salesThroughCache[nextMKey];
            var backM = {{ sum: nextM.sum, hasData: nextM.hasData }};
            var remIso = y + '-' + pad2(m) + '-' + pad2(until + 1);
            var remDt = new Date(y, m - 1, until + 1);
            var remWk = remDt.getDay() === 0 || remDt.getDay() === 6;
            if (isTimelineBusinessDay(remIso, bmap, remWk)) {{
              backM.sum -= readTwSalesAmt(remIso, smap);
            }}
            salesThroughCache[cacheKey] = backM;
            return backM;
          }}
        }}
        var sum = 0;
        var hasData = false;
        for (var d = 1; d <= until; d++) {{
          var dayIso = y + '-' + pad2(m) + '-' + pad2(d);
          var dt = new Date(y, m - 1, d);
          var isWk = dt.getDay() === 0 || dt.getDay() === 6;
          if (!isTimelineBusinessDay(dayIso, bmap, isWk)) continue;
          if (Object.prototype.hasOwnProperty.call(smap, dayIso)) hasData = true;
          sum += readTwSalesAmt(dayIso, smap);
        }}
        var monthResult = {{ sum: sum, hasData: hasData }};
        salesThroughCache[cacheKey] = monthResult;
        return monthResult;
      }}
      window.__sumMonthSalesThroughDay = sumMonthSalesThroughDay;
      function sumYearSalesThroughDay(year, month, day) {{
        var y = Number(year);
        var m = Number(month);
        var dayN = Number(day);
        if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(dayN)) return null;
        if (m < 1 || m > 12) return null;
        var dimMonth = new Date(y, m, 0).getDate();
        var untilDay = Math.max(1, Math.min(dimMonth, Math.floor(dayN)));
        var cacheKey = 'y:' + y + '-' + m + '-' + untilDay;
        if (Object.prototype.hasOwnProperty.call(salesThroughCache, cacheKey)) {{
          return salesThroughCache[cacheKey];
        }}
        ensureTwAnnualDailySynced();
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var smap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        if (untilDay > 1) {{
          var prevYKey = 'y:' + y + '-' + m + '-' + (untilDay - 1);
          if (Object.prototype.hasOwnProperty.call(salesThroughCache, prevYKey)) {{
            var prevY = salesThroughCache[prevYKey];
            var fwdY = {{ sum: prevY.sum, hasData: prevY.hasData }};
            addOneSalesDay(fwdY, y, m, untilDay, smap, bmap);
            salesThroughCache[cacheKey] = fwdY;
            return fwdY;
          }}
        }} else if (m > 1) {{
          var prevDim = new Date(y, m - 1, 0).getDate();
          var prevMonthEndKey = 'y:' + y + '-' + (m - 1) + '-' + prevDim;
          if (Object.prototype.hasOwnProperty.call(salesThroughCache, prevMonthEndKey)) {{
            var prevEnd = salesThroughCache[prevMonthEndKey];
            var fromPrev = {{ sum: prevEnd.sum, hasData: prevEnd.hasData }};
            addOneSalesDay(fromPrev, y, m, 1, smap, bmap);
            salesThroughCache[cacheKey] = fromPrev;
            return fromPrev;
          }}
        }}
        if (untilDay < dimMonth) {{
          var nextYKey = 'y:' + y + '-' + m + '-' + (untilDay + 1);
          if (Object.prototype.hasOwnProperty.call(salesThroughCache, nextYKey)) {{
            var nextY = salesThroughCache[nextYKey];
            var backY = {{ sum: nextY.sum, hasData: nextY.hasData }};
            var remYIso = y + '-' + pad2(m) + '-' + pad2(untilDay + 1);
            var remYDt = new Date(y, m - 1, untilDay + 1);
            var remYWk = remYDt.getDay() === 0 || remYDt.getDay() === 6;
            if (isTimelineBusinessDay(remYIso, bmap, remYWk)) {{
              backY.sum -= readTwSalesAmt(remYIso, smap);
            }}
            salesThroughCache[cacheKey] = backY;
            return backY;
          }}
        }}
        var sum = 0;
        var hasData = false;
        for (var mm = 1; mm <= m; mm++) {{
          var dim = new Date(y, mm, 0).getDate();
          var last = mm === m ? untilDay : dim;
          for (var d = 1; d <= last; d++) {{
            var dayIso = y + '-' + pad2(mm) + '-' + pad2(d);
            var dt = new Date(y, mm - 1, d);
            var isWk = dt.getDay() === 0 || dt.getDay() === 6;
            if (!isTimelineBusinessDay(dayIso, bmap, isWk)) continue;
            if (Object.prototype.hasOwnProperty.call(smap, dayIso)) hasData = true;
            sum += readTwSalesAmt(dayIso, smap);
          }}
        }}
        var yearResult = {{ sum: sum, hasData: hasData }};
        salesThroughCache[cacheKey] = yearResult;
        return yearResult;
      }}
      window.__sumYearSalesThroughDay = sumYearSalesThroughDay;
      window.__computeTwMetricsForIso = computeTwMetricsForIso;
      window.__twFmtMoney = fmtMoney;
      window.__twFmtDiff = fmtTwDiff;
      window.__twFmtAchPct = fmtTwAchPct;
      window.__twDiffSeverityClass = twDiffSeverityClass;
      window.__twDiffLevels = TW_DIFF_LEVELS;
      /** Same weekday N years back (364 * yearsBack days). yearsBack=0 → iso itself. */
      window.__sameWeekdayIso = function (iso, yearsBack) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        var n = Number(yearsBack);
        if (!Number.isFinite(n) || n < 0) n = 1;
        if (n > 0) d.setDate(d.getDate() - 364 * n);
        return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
      }};
      window.__readTwDaySales = function (iso) {{
        if (!iso) return 0;
        ensureTwAnnualDailySynced();
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        return readTwSalesAmt(iso, daily.targetSalesByDate || {{}});
      }};
      window.__isTwBusinessDay = function (iso) {{
        if (!iso) return false;
        ensureTwAnnualDailySynced();
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {{}};
        var bmap = daily.businessDayByDate || {{}};
        var d = new Date(String(iso).trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return false;
        var isWk = d.getDay() === 0 || d.getDay() === 6;
        return isTimelineBusinessDay(iso, bmap, isWk);
      }};
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
      [
        'annual:salesMapChanged',
        'kpi:dailySalesChanged',
        'kpi:businessDayChanged',
        'kpi:annualPlanChanged',
        'kpi:dailyTargetModeChanged',
        'kpi:weekdayBaselineChanged',
        'annual:pastSalesSaved',
      ].forEach(function (evName) {{
        document.addEventListener(evName, function () {{
          invalidateTwSalesThroughCache();
        }});
      }});
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

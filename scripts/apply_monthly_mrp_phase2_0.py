#!/usr/bin/env python3
"""MRP Phase 2.0 — Monthly perf: precompute column metrics, frame budget, staged DOM commit,
defer vertical TW until focus bar expanded, cache computeTwMetricsForIso."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-0 */"

BOOTSTRAP_OLD = """      (function bootstrapMonthlyVerticalTw() {
        var kick = function () {
          if (window.__monthlyVerticalTwPartialRendered) return;
          window.__ensureMonthlyVerticalTwRendered();
        };
        if (document.body.classList.contains('annual-focus-bar-expanded')) {
          window.requestAnimationFrame(function () {
            window.requestAnimationFrame(kick);
          });
          return;
        }
        window.__monthlyVerticalTwBootstrapPending = true;
        document.addEventListener('monthly:pageReady', function () {
          window.requestAnimationFrame(kick);
        }, { once: true });
        if (typeof window.requestIdleCallback === 'function') {
          window.requestIdleCallback(kick, { timeout: 900 });
        } else {
          window.setTimeout(kick, 400);
        }
      })();"""

BOOTSTRAP_NEW = f"""      {MARKER}
      /* Monthly: フォーカスバー未展開時は縦TWを描画しない（約400行DOMを省略） */
      (function bootstrapMonthlyVerticalTw() {{
        var kick = function () {{
          if (window.__monthlyVerticalTwPartialRendered) return;
          if (!document.body.classList.contains('annual-focus-bar-expanded')) {{
            window.__monthlyVerticalTwBootstrapPending = true;
            return;
          }}
          window.__monthlyVerticalTwBootstrapPending = false;
          window.__ensureMonthlyVerticalTwRendered();
        }};
        if (document.body.classList.contains('annual-focus-bar-expanded')) {{
          window.requestAnimationFrame(function () {{
            window.requestAnimationFrame(kick);
          }});
          return;
        }}
        window.__monthlyVerticalTwBootstrapPending = true;
      }})();"""

COMPUTE_TW_OLD = """      function computeTwMetricsForIso(iso) {
        if (!iso) return null;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }"""

COMPUTE_TW_NEW = f"""      {MARKER}
      var __twMetricsCache = Object.create(null);
      function clearTwMetricsCache() {{
        __twMetricsCache = Object.create(null);
      }}
      function computeTwMetricsForIso(iso) {{
        if (!iso) return null;
        if (__twMetricsCache[iso]) return __twMetricsCache[iso];
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}"""

COMPUTE_TW_RETURN_OLD = """        return {
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
        };
      }
      window.__computeTwMetricsForIso = computeTwMetricsForIso;"""

COMPUTE_TW_RETURN_NEW = """        var __twResult = {
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
        };
        __twMetricsCache[iso] = __twResult;
        return __twResult;
      }
      window.__computeTwMetricsForIso = computeTwMetricsForIso;
      window.clearTwMetricsCache = clearTwMetricsCache;"""

INVALIDATE_OLD = """      function invalidateMonthlyTwTargetCache() {
        clearMonthlyTwTargetMapsByYear();
        window.__monthlyTwTargetCacheYear = null;
        window.__monthlyTwTargetCache = null;
      }"""

INVALIDATE_NEW = f"""      function invalidateMonthlyTwTargetCache() {{
        clearMonthlyTwTargetMapsByYear();
        if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();
        window.__monthlyTwTargetCacheYear = null;
        window.__monthlyTwTargetCache = null;
      }}"""

PRECOMPUTE_INSERT_OLD = """      function makeGroupColumn(buffer, off, iso, aria, groupNo) {
        var div = document.createElement('div');
        div.className =
          'monthly-data-column monthly-data-column--group' +
          (buffer ? ' monthly-data-column--buffer' : '') +
          (off ? ' monthly-data-column--off' : '');
        div.setAttribute('role', 'presentation');
        div.setAttribute('data-iso', iso);
        div.setAttribute('aria-label', aria);
        var values = getMonthlyGroupCellValues(groupNo, off, iso);"""

PRECOMPUTE_INSERT_NEW = f"""      {MARKER}
      function precomputeMonthlyRebuildMetrics(dayObjs) {{
        var map = Object.create(null);
        var cache = window.__MONTHLY_MEP_METRICS__ || {{}};
        var fixedIds = cache.fixedIds || [];
        var variableIds = cache.variableIds || [];
        for (var di = 0; di < dayObjs.length; di++) {{
          var dayObj = dayObjs[di];
          var iso = toISODateLocal(dayObj);
          var off = !isBusinessDayByIso(iso, dayObj);
          if (off) {{
            map[iso] = {{ off: true }};
            continue;
          }}
          var sales = dailySalesAmount(iso);
          var snap = readGroup1TwSnapshot(iso);
          var lunch = mepReadRow(iso, 'incLunch');
          var dinner = Math.max(0, Math.round(sales) - Math.round(lunch));
          var g1 = [
            fmtTwMoney(snap.sales),
            fmtTwMoney(lunch),
            fmtTwMoney(dinner),
            snap.targetText,
            snap.diffText,
            snap.achText,
          ];
          var g2;
          if (useJa) {{
            var cust = mepReadRow(iso, 'cust');
            var custLunch = mepReadRow(iso, 'custLunch');
            var custDinner = mepParentMinusLunch(iso, 'cust', 'custLunch');
            var grp = mepReadRow(iso, 'groupCnt');
            var grpLunch = mepReadRow(iso, 'groupCntLunch');
            var grpDinner = mepParentMinusLunch(iso, 'groupCnt', 'groupCntLunch');
            g2 = [
              fmtTwCount(cust),
              fmtTwCount(custLunch),
              fmtTwCount(custDinner),
              fmtTwCount(grp),
              fmtTwCount(grpLunch),
              fmtTwCount(grpDinner),
            ];
          }} else {{
            var custEn = mepReadRow(iso, 'cust');
            var custLunchEn = mepReadRow(iso, 'custLunch');
            var custDinnerEn = mepParentMinusLunch(iso, 'cust', 'custLunch');
            var pc = mepReadRow(iso, 'pc');
            var pcLunch = mepReadRow(iso, 'pcLunch');
            var pcDinner = mepParentMinusLunch(iso, 'pc', 'pcLunch');
            g2 = [
              fmtTwCount(custEn),
              fmtTwCount(custLunchEn),
              fmtTwCount(custDinnerEn),
              fmtTwMoney(pc),
              fmtTwMoney(pcLunch),
              fmtTwMoney(pcDinner),
            ];
          }}
          var food = mepReadRow(iso, 'exp_food_cost');
          var bev = mepReadRow(iso, 'exp_drink_cost');
          var misc = mepReadRow(iso, 'exp_misc');
          var fixedSum = mepSumRows(iso, fixedIds);
          var varSum = mepSumRows(iso, variableIds);
          var total = fixedSum + varSum;
          map[iso] = {{
            off: false,
            g1: g1,
            g2: g2,
            g3: [
              fmtTwMoney(food),
              fmtTwMoney(bev),
              fmtTwMoney(misc),
              fmtTwMoney(fixedSum),
              fmtTwMoney(varSum),
              fmtTwMoney(total),
            ],
            profit: fmtTwMoney(sales - total),
            snap: snap,
          }};
        }}
        return map;
      }}
      function makeGroupColumn(buffer, off, iso, aria, groupNo, metrics) {{
        var div = document.createElement('div');
        div.className =
          'monthly-data-column monthly-data-column--group' +
          (buffer ? ' monthly-data-column--buffer' : '') +
          (off ? ' monthly-data-column--off' : '');
        div.setAttribute('role', 'presentation');
        div.setAttribute('data-iso', iso);
        div.setAttribute('aria-label', aria);
        var values;
        if (!off && metrics) {{
          if (groupNo === 1) values = metrics.g1;
          else if (groupNo === 2) values = metrics.g2;
          else values = metrics.g3;
        }} else {{
          values = getMonthlyGroupCellValues(groupNo, off, iso);
        }}"""

MAKE_PROFIT_OLD = """      function makeProfitColumn(buffer, off, iso, aria) {
        var div = document.createElement('div');
        div.className =
          'monthly-data-column monthly-data-column--profit' +
          (buffer ? ' monthly-data-column--buffer' : '') +
          (off ? ' monthly-data-column--off' : '');
        div.setAttribute('role', 'presentation');
        div.setAttribute('data-iso', iso);
        div.setAttribute('aria-label', aria);
        var cell = document.createElement('span');
        cell.className = 'monthly-data-column__cell';
        cell.setAttribute('aria-hidden', 'true');
        cell.textContent = getMonthlyProfitCellValue(off, iso);
        div.appendChild(cell);
        return div;
      }"""

MAKE_PROFIT_NEW = """      function makeProfitColumn(buffer, off, iso, aria, metrics) {
        var div = document.createElement('div');
        div.className =
          'monthly-data-column monthly-data-column--profit' +
          (buffer ? ' monthly-data-column--buffer' : '') +
          (off ? ' monthly-data-column--off' : '');
        div.setAttribute('role', 'presentation');
        div.setAttribute('data-iso', iso);
        div.setAttribute('aria-label', aria);
        var cell = document.createElement('span');
        cell.className = 'monthly-data-column__cell';
        cell.setAttribute('aria-hidden', 'true');
        if (!off && metrics) {
          cell.textContent = metrics.profit;
        } else {
          cell.textContent = getMonthlyProfitCellValue(off, iso);
        }
        div.appendChild(cell);
        return div;
      }"""

REBUILD_CHUNKED_OLD = """      function rebuildColumnsChunked(runToken, onDone) {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);
        invalidateGroup1TwCache();
        isoToIndex = {};
        var fragDate = document.createDocumentFragment();
        var fragGroup1 = document.createDocumentFragment();
        var fragGroup2 = document.createDocumentFragment();
        var fragGroup3 = document.createDocumentFragment();
        var fragProfit = document.createDocumentFragment();
        var y = state.year;
        var m0 = state.month0;
        var prevMonthLast = new Date(y, m0, 0);
        var prevMonthDays = prevMonthLast.getDate();
        var anchorX = getFocusAnchorXInViewport();
        var neededLeading = Math.max(1, Math.ceil((anchorX - COL_W / 2) / COL_STEP));
        var baselineStart = Math.min(PREV_MONTH_START_DAY, prevMonthDays);
        var baselineLeading = prevMonthDays - baselineStart + 1;
        var startDay = baselineStart;
        if (baselineLeading < neededLeading) {
          startDay = Math.max(1, prevMonthDays - neededLeading + 1);
        }
        var start = new Date(y, m0 - 1, startDay);
        var end = new Date(y, m0 + 1, NEXT_MONTH_END_DAY);
        var days = [];
        for (var d = new Date(start.getFullYear(), start.getMonth(), start.getDate()); d <= end; d = addDays(d, 1)) {
          days.push(new Date(d.getFullYear(), d.getMonth(), d.getDate()));
        }
        var g1Label = useJa ? 'グループ1' : 'Group 1';
        var g2Label = useJa ? 'グループ2' : 'Group 2';
        var g3Label = useJa ? 'グループ3' : 'Group 3';
        var cursor = 0;
        var CHUNK_SIZE = 8;
        function buildChunk() {
          if (runToken !== __monthlyRebuildRunToken) return;
          var upper = Math.min(days.length, cursor + CHUNK_SIZE);
          for (; cursor < upper; cursor++) {
            var dayObj = days[cursor];
            var iso = toISODateLocal(dayObj);
            var inMonth = dayObj.getMonth() === m0 && dayObj.getFullYear() === y;
            var buffer = !inMonth;
            var off = !isBusinessDayByIso(iso, dayObj);
            isoToIndex[iso] = cursor;
            var p = document.createElement('p');
            p.className = 'monthly-date-header-cell';
            if (off) p.classList.add('monthly-date-header-cell--off');
            if (buffer) p.classList.add('monthly-date-header-cell--buffer');
            p.setAttribute('data-iso', iso);
            p.textContent = dateLabelText(dayObj);
            p.setAttribute('aria-label', ariaDateLabel(dayObj, inMonth));
            fragDate.appendChild(p);
            var colNum = cursor + 1;
            fragGroup1.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g1Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
                1
              )
            );
            fragGroup2.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g2Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
                2
              )
            );
            fragGroup3.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g3Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
                3
              )
            );
            fragProfit.appendChild(
              makeProfitColumn(
                buffer,
                off,
                iso,
                (useJa ? 'Profit 列' : 'Profit column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : '')
              )
            );
          }
          if (cursor < days.length) {
            window.requestAnimationFrame(buildChunk);
            return;
          }
          if (runToken !== __monthlyRebuildRunToken) return;
          trackDate.replaceChildren(fragDate);
          trackGroup1.replaceChildren(fragGroup1);
          trackGroup2.replaceChildren(fragGroup2);
          trackGroup3.replaceChildren(fragGroup3);
          trackProfit.replaceChildren(fragProfit);
          scheduleVFocusUpdate();
          if (typeof onDone === 'function') onDone();
        }
        window.requestAnimationFrame(buildChunk);
      }"""

REBUILD_CHUNKED_NEW = """      function rebuildColumnsChunked(runToken, onDone) {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);
        invalidateGroup1TwCache();
        isoToIndex = {};
        var fragDate = document.createDocumentFragment();
        var fragGroup1 = document.createDocumentFragment();
        var fragGroup2 = document.createDocumentFragment();
        var fragGroup3 = document.createDocumentFragment();
        var fragProfit = document.createDocumentFragment();
        var y = state.year;
        var m0 = state.month0;
        var prevMonthLast = new Date(y, m0, 0);
        var prevMonthDays = prevMonthLast.getDate();
        var anchorX = getFocusAnchorXInViewport();
        var neededLeading = Math.max(1, Math.ceil((anchorX - COL_W / 2) / COL_STEP));
        var baselineStart = Math.min(PREV_MONTH_START_DAY, prevMonthDays);
        var baselineLeading = prevMonthDays - baselineStart + 1;
        var startDay = baselineStart;
        if (baselineLeading < neededLeading) {
          startDay = Math.max(1, prevMonthDays - neededLeading + 1);
        }
        var start = new Date(y, m0 - 1, startDay);
        var end = new Date(y, m0 + 1, NEXT_MONTH_END_DAY);
        var days = [];
        for (var d = new Date(start.getFullYear(), start.getMonth(), start.getDate()); d <= end; d = addDays(d, 1)) {
          days.push(new Date(d.getFullYear(), d.getMonth(), d.getDate()));
        }
        var metricsByIso = precomputeMonthlyRebuildMetrics(days);
        var g1Label = useJa ? 'グループ1' : 'Group 1';
        var g2Label = useJa ? 'グループ2' : 'Group 2';
        var g3Label = useJa ? 'グループ3' : 'Group 3';
        var cursor = 0;
        var FRAME_BUDGET_MS = 10;
        function buildChunk() {
          if (runToken !== __monthlyRebuildRunToken) return;
          var t0 =
            typeof performance !== 'undefined' && performance.now
              ? performance.now()
              : 0;
          while (cursor < days.length) {
            var dayObj = days[cursor];
            var iso = toISODateLocal(dayObj);
            var inMonth = dayObj.getMonth() === m0 && dayObj.getFullYear() === y;
            var buffer = !inMonth;
            var off = !isBusinessDayByIso(iso, dayObj);
            var metrics = metricsByIso[iso] || null;
            isoToIndex[iso] = cursor;
            var p = document.createElement('p');
            p.className = 'monthly-date-header-cell';
            if (off) p.classList.add('monthly-date-header-cell--off');
            if (buffer) p.classList.add('monthly-date-header-cell--buffer');
            p.setAttribute('data-iso', iso);
            p.textContent = dateLabelText(dayObj);
            p.setAttribute('aria-label', ariaDateLabel(dayObj, inMonth));
            fragDate.appendChild(p);
            var colNum = cursor + 1;
            var inactiveSuffix = (buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : '';
            fragGroup1.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g1Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
                1,
                metrics
              )
            );
            fragGroup2.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g2Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
                2,
                metrics
              )
            );
            fragGroup3.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g3Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
                3,
                metrics
              )
            );
            fragProfit.appendChild(
              makeProfitColumn(
                buffer,
                off,
                iso,
                (useJa ? 'Profit 列' : 'Profit column ') + colNum + inactiveSuffix,
                metrics
              )
            );
            cursor += 1;
            if (FRAME_BUDGET_MS > 0 && t0 > 0 && performance.now() - t0 >= FRAME_BUDGET_MS) {
              break;
            }
          }
          if (cursor < days.length) {
            window.requestAnimationFrame(buildChunk);
            return;
          }
          if (runToken !== __monthlyRebuildRunToken) return;
          function commitTracksStep(step) {
            if (runToken !== __monthlyRebuildRunToken) return;
            if (step === 0) trackDate.replaceChildren(fragDate);
            else if (step === 1) trackGroup1.replaceChildren(fragGroup1);
            else if (step === 2) trackGroup2.replaceChildren(fragGroup2);
            else if (step === 3) trackGroup3.replaceChildren(fragGroup3);
            else if (step === 4) trackProfit.replaceChildren(fragProfit);
            else {
              scheduleVFocusUpdate();
              if (typeof onDone === 'function') onDone();
              return;
            }
            window.requestAnimationFrame(function () {
              commitTracksStep(step + 1);
            });
          }
          window.requestAnimationFrame(function () {
            commitTracksStep(0);
          });
        }
        window.requestAnimationFrame(buildChunk);
      }"""

MONTHLY_TW_REBUILD_OLD = """      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();"""

MONTHLY_TW_REBUILD_NEW = """      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();
        if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();"""


def apply_replacements(text: str) -> str:
    pairs = [
        (BOOTSTRAP_OLD, BOOTSTRAP_NEW),
        (COMPUTE_TW_OLD, COMPUTE_TW_NEW),
        (COMPUTE_TW_RETURN_OLD, COMPUTE_TW_RETURN_NEW),
        (INVALIDATE_OLD, INVALIDATE_NEW),
        (PRECOMPUTE_INSERT_OLD, PRECOMPUTE_INSERT_NEW),
        (MAKE_PROFIT_OLD, MAKE_PROFIT_NEW),
        (REBUILD_CHUNKED_OLD, REBUILD_CHUNKED_NEW),
        (MONTHLY_TW_REBUILD_OLD, MONTHLY_TW_REBUILD_NEW),
    ]
    for old, new in pairs:
        if old not in text:
            raise ValueError(f"anchor not found ({old[:60]}...)")
        text = text.replace(old, new, 1)
    return text


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"MISSING: {path}", file=sys.stderr)
            return 1
        original = path.read_text(encoding="utf-8")
        if MARKER in original:
            print(f"SKIP (already applied): {path}")
            continue
        updated = apply_replacements(original)
        path.write_text(updated, encoding="utf-8")
        print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

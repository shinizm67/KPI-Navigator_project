#!/usr/bin/env python3
"""MRP Phase 2.2 — computeTwMetricsForIso: year-level cumulative index (O(1) per iso after index build)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-2 */"

OLD_BLOCK = """      /* KPI-MRP-PHASE2-0 */
      var __twMetricsCache = Object.create(null);
      function clearTwMetricsCache() {
        __twMetricsCache = Object.create(null);
      }
      function computeTwMetricsForIso(iso) {
        if (!iso) return null;
        if (__twMetricsCache[iso]) return __twMetricsCache[iso];
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        var daily = (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) || {};
        var smap = daily.targetSalesByDate || {};
        var bmap = daily.businessDayByDate || {};
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
        for (var m = 0; m < 12; m++) {
          var dc = new Date(y, m + 1, 0).getDate();
          for (var day = 1; day <= dc; day++) {
            var dt = new Date(y, m, day);
            var dayIso = y + '-' + pad2(m + 1) + '-' + pad2(day);
            var isWk = dt.getDay() === 0 || dt.getDay() === 6;
            if (!isTimelineBusinessDay(dayIso, bmap, isWk)) continue;
            var dayTarget = null;
            if (Object.prototype.hasOwnProperty.call(tgtMap, dayIso)) {
              dayTarget = Number(tgtMap[dayIso]);
              if (!Number.isFinite(dayTarget)) dayTarget = null;
            }
            if (m === m0 && dayTarget != null) monthlyFullTarget += dayTarget;
            if (dayIso <= iso) {
              var salesAmt = readTwSalesAmt(dayIso, smap);
              ytdA += salesAmt;
              if (m === m0) mtdA += salesAmt;
              if (dayTarget != null) {
                ytdT += dayTarget;
                hasPlan = true;
                if (m === m0) mtdT += dayTarget;
              }
            }
            if (dayIso >= iso) {
              if (m === m0) monthRemainingBD++;
              yearRemainingBD++;
            }
            if (dayIso === iso) {
              isBusinessToday = true;
              dailySales = readTwSalesAmt(dayIso, smap);
              dailyTarget = dayTarget;
            }
          }
        }
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
        var __twResult = {
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

NEW_BLOCK = f"""      /* KPI-MRP-PHASE2-0 */
      {MARKER}
      var __twMetricsCache = Object.create(null);
      var __twMetricsYearIndex = Object.create(null);
      function clearTwMetricsCache() {{
        __twMetricsCache = Object.create(null);
        __twMetricsYearIndex = Object.create(null);
      }}
      function twLastRowAtMost(rows, lo, hi, iso) {{
        if (lo < 0 || hi < lo || !rows || !rows.length) return -1;
        var last = -1;
        var l = lo;
        var r = hi;
        while (l <= r) {{
          var mid = (l + r) >> 1;
          if (rows[mid].iso <= iso) {{
            last = mid;
            l = mid + 1;
          }} else {{
            r = mid - 1;
          }}
        }}
        return last;
      }}
      function twCountFromIso(rows, lo, hi, iso) {{
        if (lo < 0 || hi < lo || !rows || !rows.length) return 0;
        var l = lo;
        var r = hi + 1;
        while (l < r) {{
          var mid = (l + r) >> 1;
          if (rows[mid].iso < iso) l = mid + 1;
          else r = mid;
        }}
        return l <= hi ? hi - l + 1 : 0;
      }}
      function buildTwMetricsYearIndex(y, smap, bmap, tgtMap) {{
        var rows = [];
        var monthlyFullTarget = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        var monthFirst = [];
        var monthLast = [];
        for (var mi = 0; mi < 12; mi++) {{
          monthFirst[mi] = -1;
          monthLast[mi] = -1;
        }}
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
            if (dayTarget != null) monthlyFullTarget[m] += dayTarget;
            var salesAmt = readTwSalesAmt(dayIso, smap);
            var prev = rows.length ? rows[rows.length - 1] : null;
            var mtdA = prev && prev.m0 === m ? prev.mtdA + salesAmt : salesAmt;
            var mtdT =
              prev && prev.m0 === m
                ? prev.mtdT + (dayTarget != null ? dayTarget : 0)
                : dayTarget != null
                  ? dayTarget
                  : 0;
            var ytdA = prev ? prev.ytdA + salesAmt : salesAmt;
            var ytdT =
              prev ? prev.ytdT + (dayTarget != null ? dayTarget : 0) : dayTarget != null ? dayTarget : 0;
            var hasPlan = (prev && prev.hasPlan) || dayTarget != null;
            var ri = rows.length;
            rows.push({{
              iso: dayIso,
              m0: m,
              sales: salesAmt,
              target: dayTarget,
              ytdA: ytdA,
              ytdT: ytdT,
              mtdA: mtdA,
              mtdT: mtdT,
              hasPlan: hasPlan,
            }});
            if (monthFirst[m] < 0) monthFirst[m] = ri;
            monthLast[m] = ri;
          }}
        }}
        var isoToRow = Object.create(null);
        for (var i = 0; i < rows.length; i++) isoToRow[rows[i].iso] = i;
        return {{
          year: y,
          rows: rows,
          isoToRow: isoToRow,
          monthFirst: monthFirst,
          monthLast: monthLast,
          monthlyFullTarget: monthlyFullTarget,
        }};
      }}
      function ensureTwMetricsYearIndex(y, smap, bmap) {{
        y = Number(y);
        if (__twMetricsYearIndex[y]) return __twMetricsYearIndex[y];
        var tgtMap = buildDailyTargetMapForYear(y, bmap);
        var index = buildTwMetricsYearIndex(y, smap, bmap, tgtMap);
        __twMetricsYearIndex[y] = index;
        return index;
      }}
      function lookupTwMetricsFromIndex(index, iso, m0, annualTarget) {{
        var rows = index.rows;
        var isBusinessToday = false;
        var dailySales = 0;
        var dailyTarget = null;
        var mtdA = 0;
        var mtdT = 0;
        var ytdA = 0;
        var ytdT = 0;
        var hasPlan = false;
        var mStart = index.monthFirst[m0];
        var mEnd = index.monthLast[m0];
        var rowIdx = index.isoToRow[iso];
        if (rowIdx != null) {{
          var row = rows[rowIdx];
          isBusinessToday = true;
          dailySales = row.sales;
          dailyTarget = row.target;
          mtdA = row.mtdA;
          mtdT = row.mtdT;
          ytdA = row.ytdA;
          ytdT = row.ytdT;
          hasPlan = row.hasPlan;
        }} else {{
          var ytdIdx = twLastRowAtMost(rows, 0, rows.length - 1, iso);
          if (ytdIdx >= 0) {{
            var ytdRow = rows[ytdIdx];
            ytdA = ytdRow.ytdA;
            ytdT = ytdRow.ytdT;
            hasPlan = ytdRow.hasPlan;
          }}
          if (mStart >= 0) {{
            var mtdIdx = twLastRowAtMost(rows, mStart, mEnd, iso);
            if (mtdIdx >= 0) {{
              mtdA = rows[mtdIdx].mtdA;
              mtdT = rows[mtdIdx].mtdT;
            }}
          }}
        }}
        var monthRemainingBD = twCountFromIso(rows, mStart, mEnd, iso);
        var yearRemainingBD = twCountFromIso(rows, 0, rows.length - 1, iso);
        var monthlyFullTarget = index.monthlyFullTarget[m0] || 0;
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
      function computeTwMetricsForIso(iso) {{
        if (!iso) return null;
        if (__twMetricsCache[iso]) return __twMetricsCache[iso];
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
        var plan = resolveTwPlanForYear(y);
        var annualTarget = plan && Number.isFinite(Number(plan.target)) ? Number(plan.target) : null;
        var index = ensureTwMetricsYearIndex(y, smap, bmap);
        var __twResult = lookupTwMetricsFromIndex(index, iso, m0, annualTarget);
        __twMetricsCache[iso] = __twResult;
        return __twResult;
      }}
      window.__computeTwMetricsForIso = computeTwMetricsForIso;
      window.clearTwMetricsCache = clearTwMetricsCache;"""


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"MISSING: {path}", file=sys.stderr)
            return 1
        original = path.read_text(encoding="utf-8")
        if MARKER in original:
            print(f"SKIP (already applied): {path}")
            continue
        if OLD_BLOCK not in original:
            print(f"ANCHOR NOT FOUND: {path}", file=sys.stderr)
            return 1
        updated = original.replace(OLD_BLOCK, NEW_BLOCK, 1)
        path.write_text(updated, encoding="utf-8")
        print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

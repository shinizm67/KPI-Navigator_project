#!/usr/bin/env python3
"""MRP Phase 2.1 — Monthly reload perf: block vertical TW when collapsed, cache target maps,
lazy column metrics, async rebuild on data events, skip duplicate initial-sync rebuild."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-1 */"

BUILD_TARGET_MAP_OLD = """      function buildDailyTargetMapForYear(year, bmap) {
        var y = Number(year);
        var plan = resolveTwPlanForYear(y);
        var out = {};
        if (!plan) return out;"""

BUILD_TARGET_MAP_NEW = f"""      {MARKER}
      var __twTargetMapsByYear = Object.create(null);
      function clearTwTargetMapsByYear() {{
        __twTargetMapsByYear = Object.create(null);
      }}
      window.clearTwTargetMapsByYear = clearTwTargetMapsByYear;
      function buildDailyTargetMapForYear(year, bmap) {{
        var y = Number(year);
        if (__twTargetMapsByYear[y]) return __twTargetMapsByYear[y];
        var plan = resolveTwPlanForYear(y);
        var out = {{}};
        if (!plan) {{
          __twTargetMapsByYear[y] = out;
          return out;
        }}"""

BUILD_TARGET_MAP_END_OLD = """        return buildLegacyFlatDailyTargetMapForYear(plan, days);
      }
      function createTwCumState() {"""

BUILD_TARGET_MAP_END_NEW = """        out = buildLegacyFlatDailyTargetMapForYear(plan, days);
        __twTargetMapsByYear[y] = out;
        return out;
      }
      function createTwCumState() {"""

BUILD_TARGET_MAP_RESOLVER_OLD = """          return out;
        }
        return buildLegacyFlatDailyTargetMapForYear(plan, days);"""

BUILD_TARGET_MAP_RESOLVER_NEW = """          __twTargetMapsByYear[y] = out;
          return out;
        }
        out = buildLegacyFlatDailyTargetMapForYear(plan, days);
        __twTargetMapsByYear[y] = out;
        return out;"""

RENDER_TIMELINE_OLD = """      function renderAnnualDailyTimeline(anchorYear, opts) {
        opts = opts || {};
        /* KPI-MRP-PHASE1 */
        if (document.body.classList.contains('monthly-page') && !opts.boundsHint) {
          opts.boundsHint = 'anchor-year-only';
        }"""

RENDER_TIMELINE_NEW = f"""      function renderAnnualDailyTimeline(anchorYear, opts) {{
        opts = opts || {{}};
        {MARKER}
        if (
          document.body.classList.contains('monthly-page') &&
          !opts.forceVerticalTw &&
          !document.body.classList.contains('annual-focus-bar-expanded') &&
          !window.__monthlyVerticalTwPartialRendered
        ) {{
          window.__monthlyVerticalTwBootstrapPending = true;
          return;
        }}
        /* KPI-MRP-PHASE1 */
        if (document.body.classList.contains('monthly-page') && !opts.boundsHint) {{
          opts.boundsHint = 'anchor-year-only';
        }}"""

SCHEDULE_TW_OLD = """      function scheduleRenderAnnualDailyTimeline(anchorYear, opts) {
        opts = opts || { preserveScroll: true };
        var cy = Number(anchorYear);"""

SCHEDULE_TW_NEW = f"""      function scheduleRenderAnnualDailyTimeline(anchorYear, opts) {{
        opts = opts || {{ preserveScroll: true }};
        {MARKER}
        if (
          document.body.classList.contains('monthly-page') &&
          !opts.forceVerticalTw &&
          !document.body.classList.contains('annual-focus-bar-expanded') &&
          !window.__monthlyVerticalTwPartialRendered
        ) {{
          window.__monthlyVerticalTwBootstrapPending = true;
          return;
        }}
        var cy = Number(anchorYear);"""

ENSURE_VTW_OLD = """      window.__ensureMonthlyVerticalTwRendered = function () {
        if (window.__monthlyVerticalTwPartialRendered) return;
        window.__monthlyVerticalTwPartialRendered = true;
        window.__monthlyVerticalTwBootstrapPending = false;
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { boundsHint: 'anchor-year-only', preserveScroll: true });
      };"""

ENSURE_VTW_NEW = """      window.__ensureMonthlyVerticalTwRendered = function () {
        if (window.__monthlyVerticalTwPartialRendered) return;
        window.__monthlyVerticalTwPartialRendered = true;
        window.__monthlyVerticalTwBootstrapPending = false;
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, {
          boundsHint: 'anchor-year-only',
          preserveScroll: true,
          forceVerticalTw: true,
        });
      };"""

CAL_YEAR_LISTENER_OLD = """      document.addEventListener('annual:calendarYearChanged', function (ev) {
        if (ev.detail && ev.detail.skipTableRender) return;
        var y = ev.detail && ev.detail.year;
        if (y != null) renderAnnualDailyTable(Number(y));
      });"""

CAL_YEAR_LISTENER_NEW = f"""      document.addEventListener('annual:calendarYearChanged', function (ev) {{
        if (ev.detail && ev.detail.skipTableRender) return;
        {MARKER}
        if (
          document.body.classList.contains('monthly-page') &&
          !document.body.classList.contains('annual-focus-bar-expanded') &&
          !window.__monthlyVerticalTwPartialRendered
        ) {{
          window.__monthlyVerticalTwBootstrapPending = true;
          return;
        }}
        var y = ev.detail && ev.detail.year;
        if (y != null) renderAnnualDailyTable(Number(y));
      }});"""

PRIME_CACHE_OLD = """      function primeMonthlyTwTargetCache(y) {
        y = Number(y);
        getMonthlyTwTargetMapForYear(y);
        getMonthlyTwTargetMapForYear(y - 1);
        getMonthlyTwTargetMapForYear(y + 1);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = window.__monthlyTwTargetMapsByYear[y] || null;
      }"""

PRIME_CACHE_NEW = f"""      function primeMonthlyTwTargetCache(y) {{
        y = Number(y);
        getMonthlyTwTargetMapForYear(y);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = window.__monthlyTwTargetMapsByYear[y] || null;
        {MARKER}
        var deferNeighborYears = function () {{
          getMonthlyTwTargetMapForYear(y - 1);
          getMonthlyTwTargetMapForYear(y + 1);
        }};
        if (typeof window.requestIdleCallback === 'function') {{
          window.requestIdleCallback(deferNeighborYears, {{ timeout: 1200 }});
        }} else {{
          window.setTimeout(deferNeighborYears, 120);
        }}
      }}"""

INVALIDATE_TARGET_OLD = """      function invalidateMonthlyTwTargetCache() {
        clearMonthlyTwTargetMapsByYear();
        if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();
        window.__monthlyTwTargetCacheYear = null;
        window.__monthlyTwTargetCache = null;
      }"""

INVALIDATE_TARGET_NEW = """      function invalidateMonthlyTwTargetCache() {
        clearMonthlyTwTargetMapsByYear();
        if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();
        if (typeof window.clearTwTargetMapsByYear === 'function') window.clearTwTargetMapsByYear();
        window.__monthlyTwTargetCacheYear = null;
        window.__monthlyTwTargetCache = null;
      }"""

PRECOMPUTE_FN_OLD = """      /* KPI-MRP-PHASE2-0 */
      function precomputeMonthlyRebuildMetrics(dayObjs) {
        var map = Object.create(null);
        var cache = window.__MONTHLY_MEP_METRICS__ || {};
        var fixedIds = cache.fixedIds || [];
        var variableIds = cache.variableIds || [];
        for (var di = 0; di < dayObjs.length; di++) {
          var dayObj = dayObjs[di];
          var iso = toISODateLocal(dayObj);
          var off = !isBusinessDayByIso(iso, dayObj);
          if (off) {
            map[iso] = { off: true };
            continue;
          }
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
          if (useJa) {
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
          } else {
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
          }
          var food = mepReadRow(iso, 'exp_food_cost');
          var bev = mepReadRow(iso, 'exp_drink_cost');
          var misc = mepReadRow(iso, 'exp_misc');
          var fixedSum = mepSumRows(iso, fixedIds);
          var varSum = mepSumRows(iso, variableIds);
          var total = fixedSum + varSum;
          map[iso] = {
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
          };
        }
        return map;
      }"""

PRECOMPUTE_FN_NEW = f"""      /* KPI-MRP-PHASE2-0 */
      {MARKER}
      function computeMonthlyRebuildMetricsForDay(dayObj) {{
        var iso = toISODateLocal(dayObj);
        var off = !isBusinessDayByIso(iso, dayObj);
        if (off) return {{ off: true }};
        var cache = window.__MONTHLY_MEP_METRICS__ || {{}};
        var fixedIds = cache.fixedIds || [];
        var variableIds = cache.variableIds || [];
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
        return {{
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
      function getMonthlyRebuildMetrics(metricsByIso, dayObj) {{
        var iso = toISODateLocal(dayObj);
        if (metricsByIso[iso]) return metricsByIso[iso];
        var metrics = computeMonthlyRebuildMetricsForDay(dayObj);
        metricsByIso[iso] = metrics;
        return metrics;
      }}"""

REBUILD_METRICS_LINE_OLD = """        var metricsByIso = precomputeMonthlyRebuildMetrics(days);
        var g1Label = useJa ? 'グループ1' : 'Group 1';"""

REBUILD_METRICS_LINE_NEW = """        var metricsByIso = Object.create(null);
        var g1Label = useJa ? 'グループ1' : 'Group 1';"""

REBUILD_METRICS_USE_OLD = """            var metrics = metricsByIso[iso] || null;"""

REBUILD_METRICS_USE_NEW = """            var metrics = getMonthlyRebuildMetrics(metricsByIso, dayObj);"""

DAILY_DATE_CHANGED_OLD = """      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var iso = ev && ev.detail && ev.detail.isoDate;
        var source = ev && ev.detail && ev.detail.source;
        if (!iso) return;
        if (source === 'focus-sync') return;"""

DAILY_DATE_CHANGED_NEW = f"""      document.addEventListener('annual:dailyDateChanged', function (ev) {{
        var iso = ev && ev.detail && ev.detail.isoDate;
        var source = ev && ev.detail && ev.detail.source;
        if (!iso) return;
        if (source === 'focus-sync') return;
        {MARKER}
        if (source === 'initial-sync') return;"""

MONTHLY_TW_REBUILD_OLD = """      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();
        if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();
        var keepIso =
          currentFocusIso ||
          readDailySelectedIso() ||
          toISODateLocal(new Date(state.year, state.month0, 1));
        rebuildColumns();
        scheduleScroll(keepIso);
      }"""

MONTHLY_TW_REBUILD_NEW = """      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();
        if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();
        var keepIso =
          currentFocusIso ||
          readDailySelectedIso() ||
          toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleRebuildColumns(keepIso);
      }"""

SALES_MAP_REBUILD_OLD = """      document.addEventListener('annual:salesMapChanged', function () {
        var keepIso = currentFocusIso || readDailySelectedIso() || toISODateLocal(new Date(state.year, state.month0, 1));
        rebuildColumns();
        scheduleScroll(keepIso);
      });"""

SALES_MAP_REBUILD_NEW = f"""      document.addEventListener('annual:salesMapChanged', function () {{
        var keepIso = currentFocusIso || readDailySelectedIso() || toISODateLocal(new Date(state.year, state.month0, 1));
        {MARKER}
        scheduleRebuildColumns(keepIso);
      }});"""

BIZ_MAP_REBUILD_OLD = """      document.addEventListener('annual:businessDayMapChanged', function () {
        invalidateMonthlyTwTargetCache();
        var keepIso = currentFocusIso || readDailySelectedIso() || toISODateLocal(new Date(state.year, state.month0, 1));
        rebuildColumns();
        scheduleScroll(keepIso);
      });"""

BIZ_MAP_REBUILD_NEW = f"""      document.addEventListener('annual:businessDayMapChanged', function () {{
        invalidateMonthlyTwTargetCache();
        var keepIso = currentFocusIso || readDailySelectedIso() || toISODateLocal(new Date(state.year, state.month0, 1));
        {MARKER}
        scheduleRebuildColumns(keepIso);
      }});"""


def apply_replacements(text: str) -> str:
    pairs = [
        (BUILD_TARGET_MAP_OLD, BUILD_TARGET_MAP_NEW),
        (BUILD_TARGET_MAP_RESOLVER_OLD, BUILD_TARGET_MAP_RESOLVER_NEW),
        (RENDER_TIMELINE_OLD, RENDER_TIMELINE_NEW),
        (SCHEDULE_TW_OLD, SCHEDULE_TW_NEW),
        (ENSURE_VTW_OLD, ENSURE_VTW_NEW),
        (CAL_YEAR_LISTENER_OLD, CAL_YEAR_LISTENER_NEW),
        (PRIME_CACHE_OLD, PRIME_CACHE_NEW),
        (INVALIDATE_TARGET_OLD, INVALIDATE_TARGET_NEW),
        (PRECOMPUTE_FN_OLD, PRECOMPUTE_FN_NEW),
        (REBUILD_METRICS_LINE_OLD, REBUILD_METRICS_LINE_NEW),
        (REBUILD_METRICS_USE_OLD, REBUILD_METRICS_USE_NEW),
        (DAILY_DATE_CHANGED_OLD, DAILY_DATE_CHANGED_NEW),
        (MONTHLY_TW_REBUILD_OLD, MONTHLY_TW_REBUILD_NEW),
        (SALES_MAP_REBUILD_OLD, SALES_MAP_REBUILD_NEW),
        (BIZ_MAP_REBUILD_OLD, BIZ_MAP_REBUILD_NEW),
    ]
    for old, new in pairs:
        if old not in text:
            raise ValueError(f"anchor not found ({old[:72]}...)")
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

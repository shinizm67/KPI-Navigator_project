#!/usr/bin/env python3
"""MRP Phase 2.5 — INP stability: idle pageReady sync, dedupe cockpit refresh, sales cache."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-5 */"

GATHER_SALES_OLD = """        function gatherMonthlySales(year) {
          var sales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var any = false;
          for (var m0 = 0; m0 < 12; m0++) {
            var dc = new Date(year, m0 + 1, 0).getDate();
            for (var day = 1; day <= dc; day++) {
              if (!isCalendarBusinessDay(year, m0, day)) continue;
              var iso = year + '-' + pad2(m0 + 1) + '-' + pad2(day);
              var amt = readDailySalesAmount(iso);
              if (Number.isFinite(amt) && amt > 0) {
                sales[m0] += amt;
                any = true;
              }
            }
          }
          return { sales: sales, any: any };
        }"""

GATHER_SALES_NEW = f"""        {MARKER}
        var __gatheredMonthlySalesByYear = Object.create(null);
        function clearGatheredMonthlySalesCache() {{
          __gatheredMonthlySalesByYear = Object.create(null);
        }}
        function gatherMonthlySales(year) {{
          year = Number(year);
          if (__gatheredMonthlySalesByYear[year]) return __gatheredMonthlySalesByYear[year];
          var sales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var any = false;
          for (var m0 = 0; m0 < 12; m0++) {{
            var dc = new Date(year, m0 + 1, 0).getDate();
            for (var day = 1; day <= dc; day++) {{
              if (!isCalendarBusinessDay(year, m0, day)) continue;
              var iso = year + '-' + pad2(m0 + 1) + '-' + pad2(day);
              var amt = readDailySalesAmount(iso);
              if (Number.isFinite(amt) && amt > 0) {{
                sales[m0] += amt;
                any = true;
              }}
            }}
          }}
          var out = {{ sales: sales, any: any }};
          __gatheredMonthlySalesByYear[year] = out;
          return out;
        }}
        document.addEventListener('annual:salesMapChanged', clearGatheredMonthlySalesCache);
        document.addEventListener('kpi:dailySalesChanged', clearGatheredMonthlySalesCache);
        document.addEventListener('annual:pastSalesSaved', clearGatheredMonthlySalesCache);"""

PAGE_READY_SYNC_OLD = """            document.addEventListener(
              'monthly:pageReady',
              function () {
                /* KPI-MRP-PHASE2-4 */
                /* syncCockpitForCalendarYearCore 内で refreshArea1Cockpit 済み。二重呼び出しを廃止 */
                window.requestAnimationFrame(function () {
                  syncCockpitForCalendarYear();
                });
              },
              { once: true }
            );"""

PAGE_READY_SYNC_NEW = f"""            document.addEventListener(
              'monthly:pageReady',
              function () {{
                {MARKER}
                /* 初回 Cockpit 同期は idle に退避し、矢印操作とのメインスレッド競合を避ける */
                var runSync = function () {{
                  syncCockpitForCalendarYear();
                }};
                if (typeof window.requestIdleCallback === 'function') {{
                  window.requestIdleCallback(runSync, {{ timeout: 800 }});
                }} else {{
                  window.setTimeout(runSync, 400);
                }}
              }},
              {{ once: true }}
            );"""

ARROW_COCKPIT_OLD = """        if (src === 'focus-sync') {
          onArea1CockpitRefreshLowPriority();
          return;
        }
        onArea1CockpitRefresh();
      });"""

ARROW_COCKPIT_NEW = f"""        if (src === 'focus-sync') {{
          onArea1CockpitRefreshLowPriority();
          return;
        }}
        {MARKER}
        if (
          document.body.classList.contains('monthly-page') &&
          (src === 'arrow' || src === 'monthly-vfocus-nav' || src === 'today')
        ) {{
          if (window.__monthlyTwColumnsBusy) {{
            if (__area1CockpitLowPriorityTimer != null) {{
              window.clearTimeout(__area1CockpitLowPriorityTimer);
            }}
            __area1CockpitLowPriorityTimer = window.setTimeout(function () {{
              __area1CockpitLowPriorityTimer = null;
              onArea1CockpitRefresh();
            }}, 320);
          }} else {{
            onArea1CockpitRefreshLowPriority();
          }}
          return;
        }}
        onArea1CockpitRefresh();
      }});"""

COCKPIT_LISTENERS_OLD = """      document.addEventListener('kpi:annualPlanChanged', onArea1CockpitRefresh);
      document.addEventListener('kpi:mepDataChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:timelineRowsRendered', onArea1CockpitRefresh);
      document.addEventListener('annual:salesMapChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:businessDayMapChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:calendarYearChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:salesDataSaved', onArea1CockpitRefresh);
      document.addEventListener('annual:targetSalesChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:pastSalesSaved', onArea1CockpitRefresh);"""

COCKPIT_LISTENERS_NEW = f"""      {MARKER}
      function onArea1CockpitRefreshUnlessMonthlySync() {{
        if (document.body.classList.contains('monthly-page')) return;
        onArea1CockpitRefresh();
      }}
      document.addEventListener('kpi:annualPlanChanged', onArea1CockpitRefreshUnlessMonthlySync);
      document.addEventListener('kpi:mepDataChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:timelineRowsRendered', onArea1CockpitRefresh);
      document.addEventListener('annual:salesMapChanged', onArea1CockpitRefreshUnlessMonthlySync);
      document.addEventListener('annual:businessDayMapChanged', onArea1CockpitRefreshUnlessMonthlySync);
      document.addEventListener('annual:calendarYearChanged', onArea1CockpitRefreshUnlessMonthlySync);
      document.addEventListener('annual:salesDataSaved', onArea1CockpitRefresh);
      document.addEventListener('annual:targetSalesChanged', onArea1CockpitRefreshUnlessMonthlySync);
      document.addEventListener('annual:pastSalesSaved', onArea1CockpitRefreshUnlessMonthlySync);"""

SCHEDULE_SCROLL_OLD = """      function scheduleScroll(iso, scrollOpts) {
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            scrollToIso(iso, scrollOpts);
          });
        });
      }"""

SCHEDULE_SCROLL_NEW = f"""      function scheduleScroll(iso, scrollOpts) {{
        {MARKER}
        requestAnimationFrame(function () {{
          scrollToIso(iso, scrollOpts);
        }});
      }}"""

COMPUTE_TW_OLD = """      function computeTwMetricsForIso(iso) {
        if (!iso) return null;
        if (__twMetricsCache[iso]) return __twMetricsCache[iso];
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }"""

COMPUTE_TW_NEW = f"""      {MARKER}
      var __twLastSyncMs = 0;
      function computeTwMetricsForIso(iso) {{
        if (!iso) return null;
        if (__twMetricsCache[iso]) return __twMetricsCache[iso];
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          var nowMs = typeof performance !== 'undefined' ? performance.now() : 0;
          if (!nowMs || nowMs - __twLastSyncMs > 120) {{
            __twLastSyncMs = nowMs;
            KpiYearStore.syncToAnnualDaily();
          }}
        }}"""

REBUILD_CHUNKED_START_OLD = """      function rebuildColumnsChunked(runToken, onDone) {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }"""

REBUILD_SCHEDULE_OLD = """      function scheduleRebuildColumns(scrollIso, scrollOpts, onComplete) {
        if (scrollIso) __monthlyRebuildScrollIso = scrollIso;
        if (scrollOpts) __monthlyRebuildScrollOpts = scrollOpts;
        if (typeof onComplete === 'function') __monthlyRebuildOnComplete = onComplete;
        __monthlyRebuildRunToken += 1;"""

REBUILD_SCHEDULE_NEW = f"""      function scheduleRebuildColumns(scrollIso, scrollOpts, onComplete) {{
        if (scrollIso) __monthlyRebuildScrollIso = scrollIso;
        if (scrollOpts) __monthlyRebuildScrollOpts = scrollOpts;
        if (typeof onComplete === 'function') __monthlyRebuildOnComplete = onComplete;
        {MARKER}
        window.__monthlyTwColumnsBusy = true;
        __monthlyRebuildRunToken += 1;"""

REBUILD_CHUNKED_START_NEW = f"""      function rebuildColumnsChunked(runToken, onDone) {{
        {MARKER}
        window.__monthlyTwColumnsBusy = true;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}"""

REBUILD_DONE_OLD = """            if (typeof __monthlyRebuildOnComplete === 'function') {
              var done = __monthlyRebuildOnComplete;
              __monthlyRebuildOnComplete = null;
              done();
            }
          });
        }, 32);
      }"""

REBUILD_DONE_NEW = f"""            if (typeof __monthlyRebuildOnComplete === 'function') {{
              var done = __monthlyRebuildOnComplete;
              __monthlyRebuildOnComplete = null;
              done();
            }}
            {MARKER}
            window.__monthlyTwColumnsBusy = false;
          }});
        }}, 32);
      }}"""


def apply_replacements(text: str) -> str:
    pairs = [
        (GATHER_SALES_OLD, GATHER_SALES_NEW),
        (PAGE_READY_SYNC_OLD, PAGE_READY_SYNC_NEW),
        (ARROW_COCKPIT_OLD, ARROW_COCKPIT_NEW),
        (COCKPIT_LISTENERS_OLD, COCKPIT_LISTENERS_NEW),
        (SCHEDULE_SCROLL_OLD, SCHEDULE_SCROLL_NEW),
        (COMPUTE_TW_OLD, COMPUTE_TW_NEW),
        (REBUILD_SCHEDULE_OLD, REBUILD_SCHEDULE_NEW),
        (REBUILD_CHUNKED_START_OLD, REBUILD_CHUNKED_START_NEW),
        (REBUILD_DONE_OLD, REBUILD_DONE_NEW),
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

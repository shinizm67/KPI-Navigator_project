#!/usr/bin/env python3
"""MRP Phase 2.7 — Focus-first hydrate, pause on input, instant first skeleton."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-7 */"

SETTLE_SKIP_OLD = """      var settleSkip = 0;

      var useJa ="""

SETTLE_SKIP_NEW = f"""      var settleSkip = 0;
      {MARKER}
      var __monthlyTwFirstSchedule = true;
      var __monthlyTwHydratePaused = false;
      var __monthlyTwHydrateResumeTimer = null;

      var useJa ="""

CSS_SKELETON_OLD = """    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--group .monthly-data-column__cell,
    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--profit .monthly-data-column__cell {
      opacity: 0.5;
    }"""

CSS_SKELETON_NEW = f"""    {MARKER}
    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--group .monthly-data-column__cell,
    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--profit .monthly-data-column__cell {{
      opacity: 1;
      color: rgba(88, 225, 243, 0.38);
    }}"""

SCHEDULE_REBUILD_OLD = """        if (__monthlyRebuildTimer != null) window.clearTimeout(__monthlyRebuildTimer);
        __monthlyRebuildTimer = window.setTimeout(function () {
          if (runToken !== __monthlyRebuildRunToken) return;
          __monthlyRebuildTimer = null;
          rebuildColumnsChunked(runToken, function () {
            if (runToken !== __monthlyRebuildRunToken) return;
            if (__monthlyRebuildScrollIso) {
              scheduleScroll(__monthlyRebuildScrollIso, __monthlyRebuildScrollOpts || undefined);
              __monthlyRebuildScrollIso = null;
              __monthlyRebuildScrollOpts = null;
            }
            if (typeof __monthlyRebuildOnComplete === 'function') {
              var done = __monthlyRebuildOnComplete;
              __monthlyRebuildOnComplete = null;
              done();
            }
            /* KPI-MRP-PHASE2-5 */
            window.__monthlyTwColumnsBusy = false;
          });
        }, 32);
      }"""

SCHEDULE_REBUILD_NEW = f"""        function runScheduledRebuild() {{
          if (runToken !== __monthlyRebuildRunToken) return;
          __monthlyRebuildTimer = null;
          rebuildColumnsChunked(runToken, function () {{
            if (runToken !== __monthlyRebuildRunToken) return;
            if (__monthlyRebuildScrollIso) {{
              scheduleScroll(__monthlyRebuildScrollIso, __monthlyRebuildScrollOpts || undefined);
              __monthlyRebuildScrollIso = null;
              __monthlyRebuildScrollOpts = null;
            }}
            if (typeof __monthlyRebuildOnComplete === 'function') {{
              var done = __monthlyRebuildOnComplete;
              __monthlyRebuildOnComplete = null;
              done();
            }}
            /* KPI-MRP-PHASE2-5 */
            window.__monthlyTwColumnsBusy = false;
          }});
        }}
        {MARKER}
        if (__monthlyTwFirstSchedule) {{
          __monthlyTwFirstSchedule = false;
          runScheduledRebuild();
          return;
        }}
        if (__monthlyRebuildTimer != null) window.clearTimeout(__monthlyRebuildTimer);
        __monthlyRebuildTimer = window.setTimeout(runScheduledRebuild, 32);
      }}"""

HYDRATE_FN_OLD = """      function scheduleMonthlyTwHydrate(runToken, days, y, m0) {
        var metricsByIso = Object.create(null);
        var hydrateCursor = 0;
        var HYDRATE_BUDGET_MS = 10;
        function hydrateChunk() {
          if (runToken !== __monthlyRebuildRunToken) return;
          var t0 =
            typeof performance !== 'undefined' && performance.now
              ? performance.now()
              : 0;
          while (hydrateCursor < days.length) {
            var dayObj = days[hydrateCursor];
            var iso = toISODateLocal(dayObj);
            var inMonth = dayObj.getMonth() === m0 && dayObj.getFullYear() === y;
            var buffer = !inMonth;
            var off = !isBusinessDayByIso(iso, dayObj);
            var metrics = getMonthlyRebuildMetrics(metricsByIso, dayObj);
            var colIdx = hydrateCursor;
            hydrateMonthlyColumnCells(
              trackGroup1.children[colIdx],
              1,
              metrics,
              iso,
              buffer,
              off
            );
            hydrateMonthlyColumnCells(
              trackGroup2.children[colIdx],
              2,
              metrics,
              iso,
              buffer,
              off
            );
            hydrateMonthlyColumnCells(
              trackGroup3.children[colIdx],
              3,
              metrics,
              iso,
              buffer,
              off
            );
            hydrateMonthlyProfitCell(trackProfit.children[colIdx], metrics, off, iso);
            hydrateCursor += 1;
            if (HYDRATE_BUDGET_MS > 0 && t0 > 0 && performance.now() - t0 >= HYDRATE_BUDGET_MS) {
              break;
            }
          }
          if (hydrateCursor < days.length) {
            window.requestAnimationFrame(hydrateChunk);
            return;
          }
          if (runToken !== __monthlyRebuildRunToken) return;
          document.documentElement.setAttribute('data-monthly-tw-hydrated', '1');
          scheduleVFocusUpdate();
        }
        window.requestAnimationFrame(hydrateChunk);
      }"""

HYDRATE_FN_NEW = f"""      {MARKER}
      function buildMonthlyTwHydrateOrder(len, focusIdx) {{
        var order = [];
        if (len <= 0) return order;
        focusIdx = Math.max(0, Math.min(len - 1, focusIdx));
        order.push(focusIdx);
        for (var spread = 1; order.length < len; spread++) {{
          var li = focusIdx - spread;
          var ri = focusIdx + spread;
          if (li >= 0) order.push(li);
          if (order.length >= len) break;
          if (ri < len) order.push(ri);
        }}
        return order;
      }}
      function scheduleMonthlyTwHydrateTick(fn) {{
        if (typeof window.requestIdleCallback === 'function') {{
          window.requestIdleCallback(fn, {{ timeout: 48 }});
        }} else {{
          window.requestAnimationFrame(fn);
        }}
      }}
      function scheduleMonthlyTwHydrate(runToken, days, y, m0, focusIso) {{
        var focusIdx = 0;
        for (var fi = 0; fi < days.length; fi++) {{
          if (toISODateLocal(days[fi]) === focusIso) {{
            focusIdx = fi;
            break;
          }}
        }}
        var hydrateOrder = buildMonthlyTwHydrateOrder(days.length, focusIdx);
        var metricsByIso = Object.create(null);
        var hydrateCursor = 0;
        var HYDRATE_BUDGET_MS = 6;
        function hydrateColumnAt(colIdx) {{
          var dayObj = days[colIdx];
          var iso = toISODateLocal(dayObj);
          var inMonth = dayObj.getMonth() === m0 && dayObj.getFullYear() === y;
          var buffer = !inMonth;
          var off = !isBusinessDayByIso(iso, dayObj);
          var metrics = getMonthlyRebuildMetrics(metricsByIso, dayObj);
          hydrateMonthlyColumnCells(
            trackGroup1.children[colIdx],
            1,
            metrics,
            iso,
            buffer,
            off
          );
          hydrateMonthlyColumnCells(
            trackGroup2.children[colIdx],
            2,
            metrics,
            iso,
            buffer,
            off
          );
          hydrateMonthlyColumnCells(
            trackGroup3.children[colIdx],
            3,
            metrics,
            iso,
            buffer,
            off
          );
          hydrateMonthlyProfitCell(trackProfit.children[colIdx], metrics, off, iso);
        }}
        function hydrateChunk() {{
          if (runToken !== __monthlyRebuildRunToken) return;
          if (__monthlyTwHydratePaused) {{
            scheduleMonthlyTwHydrateTick(hydrateChunk);
            return;
          }}
          var t0 =
            typeof performance !== 'undefined' && performance.now
              ? performance.now()
              : 0;
          while (hydrateCursor < hydrateOrder.length) {{
            hydrateColumnAt(hydrateOrder[hydrateCursor]);
            hydrateCursor += 1;
            if (HYDRATE_BUDGET_MS > 0 && t0 > 0 && performance.now() - t0 >= HYDRATE_BUDGET_MS) {{
              break;
            }}
          }}
          if (hydrateCursor < hydrateOrder.length) {{
            scheduleMonthlyTwHydrateTick(hydrateChunk);
            return;
          }}
          if (runToken !== __monthlyRebuildRunToken) return;
          document.documentElement.setAttribute('data-monthly-tw-hydrated', '1');
          scheduleVFocusUpdate();
        }}
        scheduleMonthlyTwHydrateTick(hydrateChunk);
      }}"""

REBUILD_SKELETON_START_OLD = """      function rebuildColumnsChunked(runToken, onDone) {
        /* KPI-MRP-PHASE2-5 */
        window.__monthlyTwColumnsBusy = true;
        document.documentElement.setAttribute('data-monthly-tw-hydrated', '0');
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        isoToIndex = {};"""

REBUILD_SKELETON_START_NEW = f"""      function rebuildColumnsChunked(runToken, onDone) {{
        /* KPI-MRP-PHASE2-5 */
        window.__monthlyTwColumnsBusy = true;
        document.documentElement.setAttribute('data-monthly-tw-hydrated', '0');
        {MARKER}
        isoToIndex = {{}};"""

REBUILD_HYDRATE_CALL_OLD = """        if (typeof onDone === 'function') onDone();
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);
        invalidateGroup1TwCache();
        scheduleMonthlyTwHydrate(runToken, days, y, m0);
      }"""

REBUILD_HYDRATE_CALL_NEW = f"""        if (typeof onDone === 'function') onDone();
        loadMonthlyMepMetricsForYear(state.year);
        invalidateGroup1TwCache();
        var hydrateFocusIso =
          __monthlyRebuildScrollIso ||
          currentFocusIso ||
          readDailySelectedIso() ||
          toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleMonthlyTwHydrate(runToken, days, y, m0, hydrateFocusIso);
      }}"""

INIT_OLD = """      var init = pickInitialYearMonth();
      setStateYearMonth(init.year, init.month0);
      persistMonthlyLast();
      renderPickerMenu();
      var initIso = focusIsoForNav(init.nav, init.dailyIso) || toISODateLocal(new Date(state.year, state.month0, 1));
      scheduleRebuildColumns(initIso, undefined, function () {"""

INIT_NEW = f"""      {MARKER}
      document.addEventListener(
        'keydown',
        function (ev) {{
          if (!document.body.classList.contains('monthly-page')) return;
          var key = ev.key;
          if (
            key !== 'ArrowLeft' &&
            key !== 'ArrowRight' &&
            key !== 'ArrowUp' &&
            key !== 'ArrowDown'
          ) {{
            return;
          }}
          __monthlyTwHydratePaused = true;
          if (__monthlyTwHydrateResumeTimer != null) {{
            window.clearTimeout(__monthlyTwHydrateResumeTimer);
          }}
          __monthlyTwHydrateResumeTimer = window.setTimeout(function () {{
            __monthlyTwHydrateResumeTimer = null;
            __monthlyTwHydratePaused = false;
          }}, 360);
        }},
        true
      );

      var init = pickInitialYearMonth();
      setStateYearMonth(init.year, init.month0);
      persistMonthlyLast();
      renderPickerMenu();
      var initIso = focusIsoForNav(init.nav, init.dailyIso) || toISODateLocal(new Date(state.year, state.month0, 1));
      scheduleRebuildColumns(initIso, undefined, function () {{"""


def apply_replacements(text: str) -> str:
    pairs = [
        (SETTLE_SKIP_OLD, SETTLE_SKIP_NEW),
        (CSS_SKELETON_OLD, CSS_SKELETON_NEW),
        (SCHEDULE_REBUILD_OLD, SCHEDULE_REBUILD_NEW),
        (HYDRATE_FN_OLD, HYDRATE_FN_NEW),
        (REBUILD_SKELETON_START_OLD, REBUILD_SKELETON_START_NEW),
        (REBUILD_HYDRATE_CALL_OLD, REBUILD_HYDRATE_CALL_NEW),
        (INIT_OLD, INIT_NEW),
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

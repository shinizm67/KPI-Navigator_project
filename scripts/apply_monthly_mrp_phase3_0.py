#!/usr/bin/env python3
"""MRP Phase 3.0 — Viewport-first TW hydrate + scroll lazy hydrate (Monthly)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE3-0 */"

VARS_OLD = """      /* KPI-MRP-PHASE2-7 */
      var __monthlyTwFirstSchedule = true;
      var __monthlyTwHydratePaused = false;
      var __monthlyTwHydrateResumeTimer = null;

      var useJa ="""

VARS_NEW = f"""      /* KPI-MRP-PHASE2-7 */
      var __monthlyTwFirstSchedule = true;
      var __monthlyTwHydratePaused = false;
      var __monthlyTwHydrateResumeTimer = null;
      {MARKER}
      var MONTHLY_TW_VISIBLE_HYDRATE_PAD = 6;
      var __monthlyTwHydratedColSet = Object.create(null);
      var __monthlyTwDaysCtx = null;
      var __monthlyTwLazyHydrateTimer = null;

      var useJa ="""

HYDRATE_BLOCK_OLD = """      /* KPI-MRP-PHASE2-7 */
      function buildMonthlyTwHydrateOrder(len, focusIdx) {
        var order = [];
        if (len <= 0) return order;
        focusIdx = Math.max(0, Math.min(len - 1, focusIdx));
        order.push(focusIdx);
        for (var spread = 1; order.length < len; spread++) {
          var li = focusIdx - spread;
          var ri = focusIdx + spread;
          if (li >= 0) order.push(li);
          if (order.length >= len) break;
          if (ri < len) order.push(ri);
        }
        return order;
      }
      function scheduleMonthlyTwHydrateTick(fn) {
        if (typeof window.requestIdleCallback === 'function') {
          window.requestIdleCallback(fn, { timeout: 48 });
        } else {
          window.requestAnimationFrame(fn);
        }
      }
      function scheduleMonthlyTwHydrate(runToken, days, y, m0, focusIso) {
        var focusIdx = 0;
        for (var fi = 0; fi < days.length; fi++) {
          if (toISODateLocal(days[fi]) === focusIso) {
            focusIdx = fi;
            break;
          }
        }
        var hydrateOrder = buildMonthlyTwHydrateOrder(days.length, focusIdx);
        var metricsByIso = Object.create(null);
        var hydrateCursor = 0;
        var HYDRATE_BUDGET_MS = 6;
        function hydrateColumnAt(colIdx) {
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
        }
        function hydrateChunk() {
          if (runToken !== __monthlyRebuildRunToken) return;
          if (__monthlyTwHydratePaused) {
            scheduleMonthlyTwHydrateTick(hydrateChunk);
            return;
          }
          var t0 =
            typeof performance !== 'undefined' && performance.now
              ? performance.now()
              : 0;
          while (hydrateCursor < hydrateOrder.length) {
            hydrateColumnAt(hydrateOrder[hydrateCursor]);
            hydrateCursor += 1;
            if (HYDRATE_BUDGET_MS > 0 && t0 > 0 && performance.now() - t0 >= HYDRATE_BUDGET_MS) {
              break;
            }
          }
          if (hydrateCursor < hydrateOrder.length) {
            scheduleMonthlyTwHydrateTick(hydrateChunk);
            return;
          }
          if (runToken !== __monthlyRebuildRunToken) return;
          document.documentElement.setAttribute('data-monthly-tw-hydrated', '1');
          scheduleVFocusUpdate();
        }
        scheduleMonthlyTwHydrateTick(hydrateChunk);
      }"""

HYDRATE_BLOCK_NEW = f"""      /* KPI-MRP-PHASE2-7 */
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
      {MARKER}
      function clearMonthlyTwHydratedCols() {{
        __monthlyTwHydratedColSet = Object.create(null);
      }}
      function isMonthlyTwColHydrated(colIdx) {{
        return !!__monthlyTwHydratedColSet[colIdx];
      }}
      function markMonthlyTwColHydrated(colIdx) {{
        __monthlyTwHydratedColSet[colIdx] = true;
      }}
      function getMonthlyTwVisibleColRange() {{
        var n = trackDate.children.length;
        if (!n || !scrollEl) return {{ lo: 0, hi: 0 }};
        var anchorX = getFocusAnchorXInViewport();
        var centerX = scrollEl.scrollLeft + anchorX;
        var centerIdx = Math.round((centerX - COL_W / 2) / COL_STEP);
        if (!Number.isFinite(centerIdx)) centerIdx = 0;
        if (centerIdx < 0) centerIdx = 0;
        if (centerIdx >= n) centerIdx = n - 1;
        return {{
          lo: Math.max(0, centerIdx - MONTHLY_TW_VISIBLE_HYDRATE_PAD),
          hi: Math.min(n - 1, centerIdx + MONTHLY_TW_VISIBLE_HYDRATE_PAD),
        }};
      }}
      function hydrateMonthlyTwColumnAt(colIdx, days, y, m0, metricsByIso) {{
        if (isMonthlyTwColHydrated(colIdx)) return;
        var dayObj = days[colIdx];
        if (!dayObj) return;
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
        markMonthlyTwColHydrated(colIdx);
      }}
      function scheduleMonthlyTwLazyVisibleHydrate() {{
        if (!__monthlyTwDaysCtx) return;
        if (__monthlyTwLazyHydrateTimer != null) window.clearTimeout(__monthlyTwLazyHydrateTimer);
        __monthlyTwLazyHydrateTimer = window.setTimeout(function () {{
          __monthlyTwLazyHydrateTimer = null;
          var ctx = __monthlyTwDaysCtx;
          if (!ctx || ctx.runToken !== __monthlyRebuildRunToken) return;
          if (__monthlyTwHydratePaused) return;
          var range = getMonthlyTwVisibleColRange();
          var metricsByIso = Object.create(null);
          var touched = false;
          for (var ci = range.lo; ci <= range.hi; ci++) {{
            if (isMonthlyTwColHydrated(ci)) continue;
            hydrateMonthlyTwColumnAt(ci, ctx.days, ctx.y, ctx.m0, metricsByIso);
            touched = true;
          }}
          if (touched) scheduleVFocusUpdate();
        }}, 80);
      }}
      function scheduleMonthlyTwHydrate(runToken, days, y, m0, focusIso) {{
        __monthlyTwDaysCtx = {{ days: days, y: y, m0: m0, runToken: runToken }};
        var focusIdx = 0;
        for (var fi = 0; fi < days.length; fi++) {{
          if (toISODateLocal(days[fi]) === focusIso) {{
            focusIdx = fi;
            break;
          }}
        }}
        var phase1Lo = Math.max(0, focusIdx - MONTHLY_TW_VISIBLE_HYDRATE_PAD);
        var phase1Hi = Math.min(days.length - 1, focusIdx + MONTHLY_TW_VISIBLE_HYDRATE_PAD);
        var bgOrder = buildMonthlyTwHydrateOrder(days.length, focusIdx);
        var bgCursor = 0;
        var HYDRATE_BUDGET_MS = 6;
        function runPhase1() {{
          if (runToken !== __monthlyRebuildRunToken) return;
          if (__monthlyTwHydratePaused) {{
            scheduleMonthlyTwHydrateTick(runPhase1);
            return;
          }}
          var metricsByIso = Object.create(null);
          for (var p1 = phase1Lo; p1 <= phase1Hi; p1++) {{
            hydrateMonthlyTwColumnAt(p1, days, y, m0, metricsByIso);
          }}
          document.documentElement.setAttribute('data-monthly-tw-hydrated', '1');
          document.documentElement.setAttribute('data-monthly-tw-interactive', '1');
          scheduleVFocusUpdate();
          scheduleMonthlyTwHydrateTick(runPhase2);
        }}
        function runPhase2() {{
          if (runToken !== __monthlyRebuildRunToken) return;
          if (__monthlyTwHydratePaused) {{
            scheduleMonthlyTwHydrateTick(runPhase2);
            return;
          }}
          var metricsByIso = Object.create(null);
          var t0 =
            typeof performance !== 'undefined' && performance.now
              ? performance.now()
              : 0;
          while (bgCursor < bgOrder.length) {{
            var colIdx = bgOrder[bgCursor];
            bgCursor += 1;
            if (colIdx >= phase1Lo && colIdx <= phase1Hi) continue;
            if (isMonthlyTwColHydrated(colIdx)) continue;
            hydrateMonthlyTwColumnAt(colIdx, days, y, m0, metricsByIso);
            if (HYDRATE_BUDGET_MS > 0 && t0 > 0 && performance.now() - t0 >= HYDRATE_BUDGET_MS) {{
              break;
            }}
          }}
          if (bgCursor < bgOrder.length) {{
            scheduleMonthlyTwHydrateTick(runPhase2);
            return;
          }}
          if (runToken !== __monthlyRebuildRunToken) return;
          document.documentElement.setAttribute('data-monthly-tw-fully-hydrated', '1');
          scheduleVFocusUpdate();
        }}
        scheduleMonthlyTwHydrateTick(runPhase1);
      }}"""

REBUILD_START_OLD = """        document.documentElement.setAttribute('data-monthly-tw-hydrated', '0');
        /* KPI-MRP-PHASE2-7 */
        isoToIndex = {};"""

REBUILD_START_NEW = f"""        document.documentElement.setAttribute('data-monthly-tw-hydrated', '0');
        document.documentElement.removeAttribute('data-monthly-tw-interactive');
        document.documentElement.removeAttribute('data-monthly-tw-fully-hydrated');
        {MARKER}
        clearMonthlyTwHydratedCols();
        __monthlyTwDaysCtx = null;
        /* KPI-MRP-PHASE2-7 */
        isoToIndex = {{}};"""

SETTLE_OLD = """        scrollToIso(iso);
        syncArea2ByIso(iso);
      }
      function scheduleMonthlySettle() {"""

SETTLE_NEW = f"""        scrollToIso(iso);
        syncArea2ByIso(iso);
        {MARKER}
        scheduleMonthlyTwLazyVisibleHydrate();
      }}
      function scheduleMonthlySettle() {{"""

PAGE_READY_WAIT_OLD = """                var waitTwThenSync = function () {
                  if (document.documentElement.getAttribute('data-monthly-tw-hydrated') === '1') {
                    scheduleCockpitChunkTick(runChunkedSync);
                    return;
                  }"""

PAGE_READY_WAIT_NEW = f"""                var waitTwThenSync = function () {{
                  {MARKER}
                  if (
                    document.documentElement.getAttribute('data-monthly-tw-interactive') === '1' ||
                    document.documentElement.getAttribute('data-monthly-tw-hydrated') === '1'
                  ) {{
                    scheduleCockpitChunkTick(runChunkedSync);
                    return;
                  }}"""


def apply_replacements(text: str) -> str:
    pairs = [
        (VARS_OLD, VARS_NEW),
        (HYDRATE_BLOCK_OLD, HYDRATE_BLOCK_NEW),
        (REBUILD_START_OLD, REBUILD_START_NEW),
        (SETTLE_OLD, SETTLE_NEW),
        (PAGE_READY_WAIT_OLD, PAGE_READY_WAIT_NEW),
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

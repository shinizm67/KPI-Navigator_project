#!/usr/bin/env python3
"""MRP Phase 2.4 — Verified INP fixes: remove duplicate cockpit refresh, defer init/neighbor work."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-4 */"

PAGE_READY_COCKPIT_OLD = """            document.addEventListener(
              'monthly:pageReady',
              function () {
                window.requestAnimationFrame(function () {
                  syncCockpitForCalendarYear();
                  if (typeof window.refreshArea1Cockpit === 'function') {
                    window.refreshArea1Cockpit();
                  }
                });
              },
              { once: true }
            );"""

PAGE_READY_COCKPIT_NEW = f"""            document.addEventListener(
              'monthly:pageReady',
              function () {{
                {MARKER}
                /* syncCockpitForCalendarYearCore 内で refreshArea1Cockpit 済み。二重呼び出しを廃止 */
                window.requestAnimationFrame(function () {{
                  syncCockpitForCalendarYear();
                }});
              }},
              {{ once: true }}
            );"""

PRIME_CACHE_OLD = """      function primeMonthlyTwTargetCache(y) {
        y = Number(y);
        getMonthlyTwTargetMapForYear(y);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = window.__monthlyTwTargetMapsByYear[y] || null;
        /* KPI-MRP-PHASE2-1 */
        var deferNeighborYears = function () {
          getMonthlyTwTargetMapForYear(y - 1);
          getMonthlyTwTargetMapForYear(y + 1);
        };
        if (typeof window.requestIdleCallback === 'function') {
          window.requestIdleCallback(deferNeighborYears, { timeout: 1200 });
        } else {
          window.setTimeout(deferNeighborYears, 120);
        }
      }"""

PRIME_CACHE_NEW = f"""      {MARKER}
      function primeMonthlyTwNeighborTargetMaps(y) {{
        y = Number(y);
        getMonthlyTwTargetMapForYear(y - 1);
        getMonthlyTwTargetMapForYear(y + 1);
      }}
      function primeMonthlyTwTargetCache(y) {{
        y = Number(y);
        getMonthlyTwTargetMapForYear(y);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = window.__monthlyTwTargetMapsByYear[y] || null;
      }}"""

INVALIDATE_TARGET_OLD = """      function invalidateMonthlyTwTargetCache() {
        clearMonthlyTwTargetMapsByYear();
        if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();
        if (typeof window.clearTwTargetMapsByYear === 'function') window.clearTwTargetMapsByYear();
        window.__monthlyTwTargetCacheYear = null;
        window.__monthlyTwTargetCache = null;
      }"""

INIT_COMPLETE_OLD = """      scheduleRebuildColumns(initIso, undefined, function () {
        scheduleVFocusUpdate();
        scheduleMonthlySettle();
        syncYearUi(state.year);
        document.documentElement.setAttribute('data-monthly-page-ready', '1');
        document.dispatchEvent(new CustomEvent('monthly:pageReady'));
      });"""

INIT_COMPLETE_NEW = f"""      scheduleRebuildColumns(initIso, undefined, function () {{
        scheduleVFocusUpdate();
        scheduleMonthlySettle();
        syncYearUi(state.year);
        document.documentElement.setAttribute('data-monthly-page-ready', '1');
        document.dispatchEvent(new CustomEvent('monthly:pageReady'));
        {MARKER}
        var deferNeighbors = function () {{
          primeMonthlyTwNeighborTargetMaps(state.year);
        }};
        if (typeof window.requestIdleCallback === 'function') {{
          window.requestIdleCallback(deferNeighbors, {{ timeout: 3000 }});
        }} else {{
          window.setTimeout(deferNeighbors, 800);
        }}
      }});"""

CROSS_MONTH_OLD = """        state.year = next.year;
        state.month0 = next.month0;
        persistMonthlyLast();
        renderPickerMenu();
        var iso = dir < 0
          ? toISODateLocal(new Date(state.year, state.month0, daysInMonth(state.year, state.month0)))
          : toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleRebuildColumns(iso, undefined, function () {"""

CROSS_MONTH_NEW = f"""        state.year = next.year;
        state.month0 = next.month0;
        {MARKER}
        primeMonthlyTwNeighborTargetMaps(state.year);
        persistMonthlyLast();
        renderPickerMenu();
        var iso = dir < 0
          ? toISODateLocal(new Date(state.year, state.month0, daysInMonth(state.year, state.month0)))
          : toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleRebuildColumns(iso, undefined, function () {{"""

READ_SURFACES_OLD = """      document.addEventListener('kpi:readSurfacesRefresh', onArea1CockpitRefresh);"""

READ_SURFACES_NEW = f"""      {MARKER}
      document.addEventListener('kpi:readSurfacesRefresh', function (ev) {{
        if (
          document.body.classList.contains('monthly-page') &&
          ev &&
          ev.detail &&
          ev.detail.source === 'init'
        ) {{
          return;
        }}
        onArea1CockpitRefresh();
      }});"""

ARROW_COCKPIT_OLD = """      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var src = ev && ev.detail && ev.detail.source;
        /* KPI-MRP-PHASE2-3 */
        if (document.body.classList.contains('monthly-page') && src === 'initial') return;
        if (src === 'focus-sync') {
          onArea1CockpitRefreshLowPriority();
          return;
        }
        onArea1CockpitRefresh();
      });"""

ARROW_COCKPIT_NEW = f"""      document.addEventListener('annual:dailyDateChanged', function (ev) {{
        var src = ev && ev.detail && ev.detail.source;
        /* KPI-MRP-PHASE2-3 */
        if (document.body.classList.contains('monthly-page') && src === 'initial') return;
        {MARKER}
        if (
          document.body.classList.contains('monthly-page') &&
          (src === 'arrow' || src === 'monthly-vfocus-nav') &&
          document.documentElement.getAttribute('data-monthly-page-ready') !== '1'
        ) {{
          return;
        }}
        if (src === 'focus-sync') {{
          onArea1CockpitRefreshLowPriority();
          return;
        }}
        onArea1CockpitRefresh();
      }});"""


def apply_replacements(text: str) -> str:
    pairs = [
        (PAGE_READY_COCKPIT_OLD, PAGE_READY_COCKPIT_NEW),
        (PRIME_CACHE_OLD, PRIME_CACHE_NEW),
        (INIT_COMPLETE_OLD, INIT_COMPLETE_NEW),
        (CROSS_MONTH_OLD, CROSS_MONTH_NEW),
        (READ_SURFACES_OLD, READ_SURFACES_NEW),
        (ARROW_COCKPIT_OLD, ARROW_COCKPIT_NEW),
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

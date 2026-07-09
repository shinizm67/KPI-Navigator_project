#!/usr/bin/env python3
"""MRP Phase 2.3b — Revert harmful 2.3 batching; keep single pageReady cockpit refresh + skip initial dup."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-3B */"

MONTHLY_TW_IIFE_OLD = """    (function () {
      /* KPI-MRP-PHASE2-3 */
      window.__monthlyTwRebuildBusy = true;
      var __monthlyTwReadyQueue = [];
      window.__runWhenMonthlyTwReady = function (fn) {
        if (typeof fn !== 'function') return;
        if (
          !window.__monthlyTwRebuildBusy &&
          document.documentElement.getAttribute('data-monthly-page-ready') === '1'
        ) {
          fn();
          return;
        }
        for (var qi = 0; qi < __monthlyTwReadyQueue.length; qi++) {
          if (__monthlyTwReadyQueue[qi] === fn) return;
        }
        __monthlyTwReadyQueue.push(fn);
      };
      window.__flushMonthlyTwReadyQueue = function () {
        var q = __monthlyTwReadyQueue.slice();
        __monthlyTwReadyQueue = [];
        for (var qj = 0; qj < q.length; qj++) q[qj]();
      };
      var STORAGE_ANNUAL = 'kpiNavigator.annualNav';"""

MONTHLY_TW_IIFE_NEW = f"""    (function () {{
      {MARKER}
      var STORAGE_ANNUAL = 'kpiNavigator.annualNav';"""

SCHEDULE_REBUILD_OLD = """      function scheduleRebuildColumns(scrollIso, scrollOpts, onComplete) {
        /* KPI-MRP-PHASE2-3 */
        window.__monthlyTwRebuildBusy = true;
        if (scrollIso) __monthlyRebuildScrollIso = scrollIso;
        if (scrollOpts) __monthlyRebuildScrollOpts = scrollOpts;
        if (typeof onComplete === 'function') __monthlyRebuildOnComplete = onComplete;
        __monthlyRebuildRunToken += 1;
        var runToken = __monthlyRebuildRunToken;
        if (__monthlyRebuildTimer != null) window.clearTimeout(__monthlyRebuildTimer);
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
            window.__monthlyTwRebuildBusy = false;
            if (typeof window.__flushMonthlyTwReadyQueue === 'function') {
              window.__flushMonthlyTwReadyQueue();
            }
          });
        }, 32);
      }"""

SCHEDULE_REBUILD_NEW = """      function scheduleRebuildColumns(scrollIso, scrollOpts, onComplete) {
        if (scrollIso) __monthlyRebuildScrollIso = scrollIso;
        if (scrollOpts) __monthlyRebuildScrollOpts = scrollOpts;
        if (typeof onComplete === 'function') __monthlyRebuildOnComplete = onComplete;
        __monthlyRebuildRunToken += 1;
        var runToken = __monthlyRebuildRunToken;
        if (__monthlyRebuildTimer != null) window.clearTimeout(__monthlyRebuildTimer);
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
          });
        }, 32);
      }"""

SYNC_REBUILD_START_OLD = """      function rebuildColumns() {
        /* KPI-MRP-PHASE2-3 */
        window.__monthlyTwRebuildBusy = true;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {"""

SYNC_REBUILD_START_NEW = """      function rebuildColumns() {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {"""

SYNC_REBUILD_END_OLD = """        trackProfit.replaceChildren(fragProfit);
        scheduleVFocusUpdate();
        window.__monthlyTwRebuildBusy = false;
        if (typeof window.__flushMonthlyTwReadyQueue === 'function') {
          window.__flushMonthlyTwReadyQueue();
        }
      }
      function scrollToIso(iso, opts) {"""

SYNC_REBUILD_END_NEW = """        trackProfit.replaceChildren(fragProfit);
        scheduleVFocusUpdate();
      }
      function scrollToIso(iso, opts) {"""

INIT_COMPLETE_OLD = """      scheduleRebuildColumns(initIso, undefined, function () {
        scheduleVFocusUpdate();
        scheduleMonthlySettle();
        syncYearUi(state.year);
        document.documentElement.setAttribute('data-monthly-page-ready', '1');
        document.dispatchEvent(new CustomEvent('monthly:pageReady'));
        /* KPI-MRP-PHASE2-3 */
        if (typeof window.refreshArea1Cockpit === 'function') {
          window.requestAnimationFrame(function () {
            window.refreshArea1Cockpit();
          });
        }
      });"""

INIT_COMPLETE_NEW = f"""      scheduleRebuildColumns(initIso, undefined, function () {{
        scheduleVFocusUpdate();
        scheduleMonthlySettle();
        syncYearUi(state.year);
        document.documentElement.setAttribute('data-monthly-page-ready', '1');
        document.dispatchEvent(new CustomEvent('monthly:pageReady'));
      }});"""

SHIFT_DATE_OLD = """      function shiftDateByDays(deltaDays) {
        /* KPI-MRP-PHASE2-3 */
        if (
          document.body.classList.contains('monthly-page') &&
          window.__monthlyTwRebuildBusy &&
          typeof window.__runWhenMonthlyTwReady === 'function'
        ) {
          window.__runWhenMonthlyTwReady(function () {
            shiftDateByDays(deltaDays);
          });
          return;
        }
        var curIso = window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate;"""

SHIFT_DATE_NEW = """      function shiftDateByDays(deltaDays) {
        var curIso = window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate;"""

STEP_FOCUS_OLD = """      function stepFocusDay(delta) {
        /* KPI-MRP-PHASE2-3 */
        if (window.__monthlyTwRebuildBusy && typeof window.__runWhenMonthlyTwReady === 'function') {
          window.__runWhenMonthlyTwReady(function () {
            stepFocusDay(delta);
          });
          return;
        }
        var baseIso = currentFocusIso || readDailySelectedIso();"""

STEP_FOCUS_NEW = """      function stepFocusDay(delta) {
        var baseIso = currentFocusIso || readDailySelectedIso();"""

COCKPIT_REFRESH_OLD = """      function onArea1CockpitRefreshCore() {
        if (__area1CockpitRefreshTimer != null) window.clearTimeout(__area1CockpitRefreshTimer);
        __area1CockpitRefreshTimer = window.setTimeout(function () {
          __area1CockpitRefreshTimer = null;
          refreshArea1Cockpit(resolveArea1Iso());
        }, 0);
      }
      /* KPI-MRP-PHASE2-3 */
      function onArea1CockpitRefresh() {
        if (document.body.classList.contains('monthly-page')) {
          if (
            window.__monthlyTwRebuildBusy ||
            document.documentElement.getAttribute('data-monthly-page-ready') !== '1'
          ) {
            if (typeof window.__runWhenMonthlyTwReady === 'function') {
              window.__runWhenMonthlyTwReady(onArea1CockpitRefreshCore);
              return;
            }
          }
        }
        onArea1CockpitRefreshCore();
      }"""

COCKPIT_REFRESH_NEW = f"""      {MARKER}
      function onArea1CockpitRefresh() {{
        if (__area1CockpitRefreshTimer != null) window.clearTimeout(__area1CockpitRefreshTimer);
        __area1CockpitRefreshTimer = window.setTimeout(function () {{
          __area1CockpitRefreshTimer = null;
          refreshArea1Cockpit(resolveArea1Iso());
        }}, 0);
      }}"""

INITIAL_COCKPIT_SYNC_OLD = """        function scheduleInitialCockpitSync() {
          /* KPI-MRP-PHASE2-3 */
          if (document.body.classList.contains('monthly-page')) {
            document.addEventListener(
              'monthly:pageReady',
              function () {
                syncCockpitForCalendarYear();
              },
              { once: true }
            );
            return;
          }
          setTimeout(function () {
            syncCockpitForCalendarYear();
          }, 0);
        }"""

INITIAL_COCKPIT_SYNC_NEW = f"""        function scheduleInitialCockpitSync() {{
          {MARKER}
          if (document.body.classList.contains('monthly-page')) {{
            document.addEventListener(
              'monthly:pageReady',
              function () {{
                window.requestAnimationFrame(function () {{
                  syncCockpitForCalendarYear();
                  if (typeof window.refreshArea1Cockpit === 'function') {{
                    window.refreshArea1Cockpit();
                  }}
                }});
              }},
              {{ once: true }}
            );
            return;
          }}
          setTimeout(function () {{
            syncCockpitForCalendarYear();
          }}, 0);
        }}"""


def apply_replacements(text: str) -> str:
    pairs = [
        (MONTHLY_TW_IIFE_OLD, MONTHLY_TW_IIFE_NEW),
        (SCHEDULE_REBUILD_OLD, SCHEDULE_REBUILD_NEW),
        (SYNC_REBUILD_START_OLD, SYNC_REBUILD_START_NEW),
        (SYNC_REBUILD_END_OLD, SYNC_REBUILD_END_NEW),
        (INIT_COMPLETE_OLD, INIT_COMPLETE_NEW),
        (SHIFT_DATE_OLD, SHIFT_DATE_NEW),
        (STEP_FOCUS_OLD, STEP_FOCUS_NEW),
        (COCKPIT_REFRESH_OLD, COCKPIT_REFRESH_NEW),
        (INITIAL_COCKPIT_SYNC_OLD, INITIAL_COCKPIT_SYNC_NEW),
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

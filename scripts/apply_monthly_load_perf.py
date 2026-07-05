#!/usr/bin/env python3
"""Monthly page load — defer vertical TW, batch cockpit sync, defer initial rebuild."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MONTHLY-LOAD-PERF */"

TW_RENDER_OLD = """      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);
    })();"""

TW_RENDER_NEW = f"""      {MARKER}
      window.__ensureMonthlyVerticalTwRendered = function () {{
        if (window.__monthlyVerticalTwRendered) return;
        window.__monthlyVerticalTwRendered = true;
        window.__monthlyVerticalTwBootstrapPending = false;
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy);
      }};
      document.addEventListener('annual:focusBarStateChanged', function (ev) {{
        if (ev && ev.detail && ev.detail.expanded) {{
          window.__ensureMonthlyVerticalTwRendered();
        }}
      }});
      (function bootstrapMonthlyVerticalTw() {{
        if (document.body.classList.contains('annual-focus-bar-expanded')) {{
          window.requestAnimationFrame(function () {{
            window.requestAnimationFrame(function () {{
              window.__ensureMonthlyVerticalTwRendered();
            }});
          }});
          return;
        }}
        window.__monthlyVerticalTwBootstrapPending = true;
        var runDeferred = function () {{
          if (!window.__monthlyVerticalTwBootstrapPending || window.__monthlyVerticalTwRendered) return;
          window.__ensureMonthlyVerticalTwRendered();
        }};
        if (typeof window.requestIdleCallback === 'function') {{
          window.requestIdleCallback(runDeferred, {{ timeout: 4000 }});
        }} else {{
          window.setTimeout(runDeferred, 2000);
        }}
      }})();
    }})();"""

SYNC_COCKPIT_FN_OLD = """        function syncCockpitForCalendarYear(explicitYear) {
          var year = resolveCalendarYear(explicitYear);"""

SYNC_COCKPIT_FN_NEW = """        function syncCockpitForCalendarYearCore(explicitYear) {
          var year = resolveCalendarYear(explicitYear);"""

SYNC_COCKPIT_WRAP_OLD = """          if (typeof window.refreshArea1Cockpit === 'function') {
            window.refreshArea1Cockpit();
          }
        }

        window.__ANNUAL_UI = window.__ANNUAL_UI || {};
        window.__ANNUAL_UI.syncCockpitForCalendarYear = syncCockpitForCalendarYear;"""

SYNC_COCKPIT_WRAP_NEW = """          if (typeof window.refreshArea1Cockpit === 'function') {
            window.refreshArea1Cockpit();
          }
        }

        var __syncCockpitTimer = null;
        var __syncCockpitPendingYear;
        function syncCockpitForCalendarYear(explicitYear) {
          if (arguments.length > 0) __syncCockpitPendingYear = explicitYear;
          if (__syncCockpitTimer != null) window.clearTimeout(__syncCockpitTimer);
          __syncCockpitTimer = window.setTimeout(function () {
            __syncCockpitTimer = null;
            var pending = __syncCockpitPendingYear;
            __syncCockpitPendingYear = undefined;
            syncCockpitForCalendarYearCore(pending);
          }, 0);
        }

        window.__ANNUAL_UI = window.__ANNUAL_UI || {};
        window.__ANNUAL_UI.syncCockpitForCalendarYear = syncCockpitForCalendarYear;"""

REBUILD_SCHEDULE_OLD = """      var __monthlyRebuildScrollOpts = null;
      function primeMonthlyTwTargetCache(y) {"""

REBUILD_SCHEDULE_NEW = """      var __monthlyRebuildScrollOpts = null;
      var __monthlyRebuildOnComplete = null;
      function primeMonthlyTwTargetCache(y) {"""

REBUILD_FN_OLD = """      function scheduleRebuildColumns(scrollIso, scrollOpts) {
        if (scrollIso) __monthlyRebuildScrollIso = scrollIso;
        if (scrollOpts) __monthlyRebuildScrollOpts = scrollOpts;
        if (__monthlyRebuildTimer != null) window.clearTimeout(__monthlyRebuildTimer);
        __monthlyRebuildTimer = window.setTimeout(function () {
          __monthlyRebuildTimer = null;
          rebuildColumns();
          if (__monthlyRebuildScrollIso) {
            scheduleScroll(__monthlyRebuildScrollIso, __monthlyRebuildScrollOpts || undefined);
            __monthlyRebuildScrollIso = null;
            __monthlyRebuildScrollOpts = null;
          }
        }, 32);
      }"""

REBUILD_FN_NEW = """      function scheduleRebuildColumns(scrollIso, scrollOpts, onComplete) {
        if (scrollIso) __monthlyRebuildScrollIso = scrollIso;
        if (scrollOpts) __monthlyRebuildScrollOpts = scrollOpts;
        if (typeof onComplete === 'function') __monthlyRebuildOnComplete = onComplete;
        if (__monthlyRebuildTimer != null) window.clearTimeout(__monthlyRebuildTimer);
        __monthlyRebuildTimer = window.setTimeout(function () {
          __monthlyRebuildTimer = null;
          rebuildColumns();
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
        }, 32);
      }"""

INIT_LOAD_OLD = """      renderPickerMenu();
      rebuildColumns();
      var initIso = focusIsoForNav(init.nav, init.dailyIso) || toISODateLocal(new Date(state.year, state.month0, 1));
      scheduleScroll(initIso);
      scheduleVFocusUpdate();
      scheduleMonthlySettle();
      syncYearUi(state.year);
      document.documentElement.setAttribute('data-monthly-page-ready', '1');
      document.dispatchEvent(new CustomEvent('monthly:pageReady'));"""

INIT_LOAD_NEW = """      renderPickerMenu();
      var initIso = focusIsoForNav(init.nav, init.dailyIso) || toISODateLocal(new Date(state.year, state.month0, 1));
      scheduleRebuildColumns(initIso, undefined, function () {
        scheduleVFocusUpdate();
        scheduleMonthlySettle();
        syncYearUi(state.year);
        document.documentElement.setAttribute('data-monthly-page-ready', '1');
        document.dispatchEvent(new CustomEvent('monthly:pageReady'));
      });"""

COCKPIT_INIT_OLD = """      onArea1CockpitRefresh();
      document.addEventListener('annual:dailyDateChanged', onArea1CockpitRefresh);"""

COCKPIT_INIT_NEW = """      /* Initial refresh: scheduleInitialCockpitSync after refreshArea1Cockpit exists. */
      document.addEventListener('annual:dailyDateChanged', onArea1CockpitRefresh);"""

TRY_SCROLL_OLD = """        function tryScrollToISO() {
          tries += 1;
          var row = document.querySelector('#annual-daily-rows .annual-daily-row[data-iso-date="' + iso + '"]');"""

TRY_SCROLL_NEW = """        function tryScrollToISO() {
          tries += 1;
          if (typeof window.__ensureMonthlyVerticalTwRendered === 'function') {
            window.__ensureMonthlyVerticalTwRendered();
          }
          var row = document.querySelector('#annual-daily-rows .annual-daily-row[data-iso-date="' + iso + '"]');"""

MARKER2 = "/* KPI-MONTHLY-LOAD-PERF-2 */"

TW_BOOTSTRAP_V1 = """      /* KPI-MONTHLY-LOAD-PERF */
      window.__ensureMonthlyVerticalTwRendered = function () {
        if (window.__monthlyVerticalTwRendered) return;
        window.__monthlyVerticalTwRendered = true;
        window.__monthlyVerticalTwBootstrapPending = false;
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy);
      };
      document.addEventListener('annual:focusBarStateChanged', function (ev) {
        if (ev && ev.detail && ev.detail.expanded) {
          window.__ensureMonthlyVerticalTwRendered();
        }
      });
      (function bootstrapMonthlyVerticalTw() {
        if (document.body.classList.contains('annual-focus-bar-expanded')) {
          window.requestAnimationFrame(function () {
            window.requestAnimationFrame(function () {
              window.__ensureMonthlyVerticalTwRendered();
            });
          });
          return;
        }
        window.__monthlyVerticalTwBootstrapPending = true;
        var runDeferred = function () {
          if (!window.__monthlyVerticalTwBootstrapPending || window.__monthlyVerticalTwRendered) return;
          window.__ensureMonthlyVerticalTwRendered();
        };
        if (typeof window.requestIdleCallback === 'function') {
          window.requestIdleCallback(runDeferred, { timeout: 4000 });
        } else {
          window.setTimeout(runDeferred, 2000);
        }
      })();"""

TW_BOOTSTRAP_V2 = f"""      /* KPI-MONTHLY-LOAD-PERF */
      {MARKER2}
      function scheduleMonthlyFullTwRender(cy) {{
        if (window.__monthlyVerticalTwFullRendered) return;
        var runFull = function () {{
          if (window.__monthlyVerticalTwFullRendered) return;
          window.__monthlyVerticalTwFullRendered = true;
          window.__monthlyVerticalTwBootstrapPending = false;
          renderAnnualDailyTimeline(cy, {{ preserveScroll: true }});
        }};
        if (typeof window.requestIdleCallback === 'function') {{
          window.requestIdleCallback(runFull, {{ timeout: 2500 }});
        }} else {{
          window.setTimeout(runFull, 600);
        }}
      }}
      window.__ensureMonthlyVerticalTwRendered = function (forceFull) {{
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        if (forceFull || window.__monthlyVerticalTwFullRendered) {{
          if (window.__monthlyVerticalTwFullRendered) return;
          window.__monthlyVerticalTwFullRendered = true;
          window.__monthlyVerticalTwBootstrapPending = false;
          renderAnnualDailyTimeline(cy, {{ preserveScroll: true }});
          return;
        }}
        if (window.__monthlyVerticalTwPartialRendered) {{
          scheduleMonthlyFullTwRender(cy);
          return;
        }}
        window.__monthlyVerticalTwPartialRendered = true;
        window.__monthlyVerticalTwBootstrapPending = false;
        renderAnnualDailyTimeline(cy, {{ boundsHint: 'anchor-year-only', preserveScroll: true }});
        scheduleMonthlyFullTwRender(cy);
      }};
      document.addEventListener('annual:focusBarStateChanged', function (ev) {{
        if (ev && ev.detail && ev.detail.expanded) {{
          window.__ensureMonthlyVerticalTwRendered(true);
        }}
      }});
      (function bootstrapMonthlyVerticalTw() {{
        var kick = function () {{
          if (window.__monthlyVerticalTwPartialRendered || window.__monthlyVerticalTwFullRendered) return;
          window.__ensureMonthlyVerticalTwRendered(false);
        }};
        if (document.body.classList.contains('annual-focus-bar-expanded')) {{
          window.requestAnimationFrame(function () {{
            window.requestAnimationFrame(function () {{
              window.__ensureMonthlyVerticalTwRendered(true);
            }});
          }});
          return;
        }}
        window.__monthlyVerticalTwBootstrapPending = true;
        document.addEventListener('monthly:pageReady', function () {{
          window.requestAnimationFrame(kick);
        }}, {{ once: true }});
        if (typeof window.requestIdleCallback === 'function') {{
          window.requestIdleCallback(kick, {{ timeout: 900 }});
        }} else {{
          window.setTimeout(kick, 400);
        }}
      }})();"""

BOUNDS_HELPER_OLD = """        return { rangeStart: rangeStart, rangeEnd: rangeEnd, minYear: minY, maxYear: maxY };
      }

      function isTimelineBusinessDay(iso, bmap, isWeekend) {"""

BOUNDS_HELPER_NEW = """        return { rangeStart: rangeStart, rangeEnd: rangeEnd, minYear: minY, maxYear: maxY };
      }

      function computeAnchorYearTimelineBounds(anchorYear) {
        anchorYear = Number(anchorYear);
        if (!Number.isFinite(anchorYear)) anchorYear = new Date().getFullYear();
        var rangeStart = new Date(anchorYear, 0, 1);
        rangeStart.setDate(rangeStart.getDate() - 14);
        var rangeEnd = new Date(anchorYear, 11, 31);
        rangeEnd.setDate(rangeEnd.getDate() + 14);
        return {
          rangeStart: rangeStart,
          rangeEnd: rangeEnd,
          minYear: anchorYear,
          maxYear: anchorYear,
        };
      }

      function isTimelineBusinessDay(iso, bmap, isWeekend) {"""

BOUNDS_USE_OLD = """        var bounds = computeFocusTimelineBounds(anchorYear);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};"""

BOUNDS_USE_NEW = """        var bounds =
          opts.boundsHint === 'anchor-year-only'
            ? computeAnchorYearTimelineBounds(anchorYear)
            : computeFocusTimelineBounds(anchorYear);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};"""

RENDER_FLAGS_OLD = """        if (prevScroll != null && scrollEl) {
          scrollEl.scrollTop = prevScroll;
        }
        document.dispatchEvent(new CustomEvent('annual:timelineRowsRendered'));
      }
      function computeTwMetricsForIso(iso) {"""

RENDER_FLAGS_NEW = """        if (prevScroll != null && scrollEl) {
          scrollEl.scrollTop = prevScroll;
        }
        if (opts.boundsHint === 'anchor-year-only') {
          window.__monthlyVerticalTwPartialRendered = true;
        } else {
          window.__monthlyVerticalTwPartialRendered = true;
          window.__monthlyVerticalTwFullRendered = true;
        }
        document.dispatchEvent(new CustomEvent('annual:timelineRowsRendered'));
      }
      function computeTwMetricsForIso(iso) {"""


def _apply(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if MARKER in text and label == "tw bootstrap":
        return text
    if "syncCockpitForCalendarYearCore" in text and label in (
        "sync cockpit fn",
        "sync cockpit wrap",
    ):
        return text
    if "__monthlyRebuildOnComplete" in text and label in (
        "rebuild onComplete var",
        "rebuild fn",
    ):
        return text
    if "scheduleRebuildColumns(initIso" in text and label == "init load":
        return text
    if "scheduleInitialCockpitSync after refreshArea1Cockpit" in text and label == "cockpit init":
        return text
    if "__ensureMonthlyVerticalTwRendered" in text and "tryScrollToISO" in old and label == "try scroll":
        return text
    if MARKER2 in text and label in (
        "tw bootstrap v2",
        "bounds helper",
        "bounds use",
        "render flags",
    ):
        return text
    if "computeAnchorYearTimelineBounds" in text and label in ("bounds helper", "bounds use"):
        return text
    if "boundsHint === 'anchor-year-only'" in text and label == "bounds use":
        return text
    if "__monthlyVerticalTwPartialRendered" in text and label == "render flags":
        return text
    raise SystemExit(f"{label} patch miss in page")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = _apply(text, TW_RENDER_OLD, TW_RENDER_NEW, "tw bootstrap")
    text = _apply(text, SYNC_COCKPIT_FN_OLD, SYNC_COCKPIT_FN_NEW, "sync cockpit fn")
    text = _apply(text, SYNC_COCKPIT_WRAP_OLD, SYNC_COCKPIT_WRAP_NEW, "sync cockpit wrap")
    text = _apply(text, REBUILD_SCHEDULE_OLD, REBUILD_SCHEDULE_NEW, "rebuild onComplete var")
    text = _apply(text, REBUILD_FN_OLD, REBUILD_FN_NEW, "rebuild fn")
    text = _apply(text, INIT_LOAD_OLD, INIT_LOAD_NEW, "init load")
    text = _apply(text, COCKPIT_INIT_OLD, COCKPIT_INIT_NEW, "cockpit init")
    text = _apply(text, TRY_SCROLL_OLD, TRY_SCROLL_NEW, "try scroll")
    text = _apply(text, TW_BOOTSTRAP_V1, TW_BOOTSTRAP_V2, "tw bootstrap v2")
    text = _apply(text, BOUNDS_HELPER_OLD, BOUNDS_HELPER_NEW, "bounds helper")
    text = _apply(text, BOUNDS_USE_OLD, BOUNDS_USE_NEW, "bounds use")
    text = _apply(text, RENDER_FLAGS_OLD, RENDER_FLAGS_NEW, "render flags")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

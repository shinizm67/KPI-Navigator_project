#!/usr/bin/env python3
"""Monthly year navigation — batch target map, defer cockpit, drop duplicate work."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

EXPORT_TARGET_MAP_OLD = """        return buildLegacyFlatDailyTargetMapForYear(plan, days);
      }
      function createTwCumState() {"""

EXPORT_TARGET_MAP_NEW = """        return buildLegacyFlatDailyTargetMapForYear(plan, days);
      }
      window.__buildDailyTargetMapForYear = buildDailyTargetMapForYear;
      function createTwCumState() {"""

COCKPIT_YEAR_LISTENER_OLD = """        document.addEventListener('annual:calendarYearChanged', function () {
          syncCockpitForCalendarYear();
        });"""

COCKPIT_YEAR_LISTENER_NEW = """        document.addEventListener('annual:calendarYearChanged', function () {
          window.requestAnimationFrame(function () {
            syncCockpitForCalendarYear();
          });
        });"""

DUP_BD_LISTENER = """      document.addEventListener('annual:calendarYearChanged', function () {
        syncBusinessDayDisplayFromDailyMap();
      });
      document.addEventListener('annual:editModalSaved', function () {"""

DUP_BD_REMOVED = """      document.addEventListener('annual:editModalSaved', function () {"""

COCKPIT_SELECTED_OLD = """      document.addEventListener('kpi:selectedDateChanged', onArea1CockpitRefresh);"""

COCKPIT_SELECTED_NEW = """      document.addEventListener('kpi:selectedDateChanged', function (ev) {
        var src = ev && ev.detail && ev.detail.source;
        if (
          src === 'arrow' ||
          src === 'today' ||
          src === 'annual-ui' ||
          src === 'picker' ||
          src === 'selection'
        ) {
          return;
        }
        onArea1CockpitRefresh();
      });"""

SET_SELECTED_DATE_OLD = """        function setSelectedDate(iso, source) {
          if (!validIso(iso)) return;
          store.meta.selectedDate = iso;
          persistStore();
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) {
            window.__ANNUAL_DATA.daily.selectedDate = iso;
          }
          try {
            gw().setJson(SELECTED_DATE_KEY, {
              calendarYear: isoYear(iso),
              selectedIso: iso,
            });
          } catch (_e) {}
          document.dispatchEvent(
            new CustomEvent('kpi:selectedDateChanged', {
              detail: { isoDate: iso, source: source || 'kpi-year-store' },
            })
          );
        }"""

SET_SELECTED_DATE_NEW = """        function setSelectedDate(iso, source) {
          if (!validIso(iso)) return;
          store.meta.selectedDate = iso;
          var navSrc = source || 'kpi-year-store';
          var deferPersist =
            navSrc === 'arrow' ||
            navSrc === 'today' ||
            navSrc === 'annual-ui' ||
            navSrc === 'picker' ||
            navSrc === 'selection';
          if (!deferPersist) {
            persistStore();
          } else {
            if (window.__kpiSelectedDatePersistTimer != null) {
              window.clearTimeout(window.__kpiSelectedDatePersistTimer);
            }
            window.__kpiSelectedDatePersistTimer = window.setTimeout(function () {
              window.__kpiSelectedDatePersistTimer = null;
              persistStore();
            }, 500);
          }
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) {
            window.__ANNUAL_DATA.daily.selectedDate = iso;
          }
          try {
            gw().setJson(SELECTED_DATE_KEY, {
              calendarYear: isoYear(iso),
              selectedIso: iso,
            });
          } catch (_e) {}
          document.dispatchEvent(
            new CustomEvent('kpi:selectedDateChanged', {
              detail: { isoDate: iso, source: navSrc },
            })
          );
        }"""

REBUILD_HELPERS_OLD = """      function rebuildColumns() {
        loadMonthlyMepMetricsForYear(state.year);
        invalidateGroup1TwCache();"""

REBUILD_HELPERS_NEW = """      var __monthlyRebuildTimer = null;
      var __monthlyRebuildScrollIso = null;
      var __monthlyRebuildScrollOpts = null;
      function primeMonthlyTwTargetCache(y) {
        y = Number(y);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = null;
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var bmap = (daily && daily.businessDayByDate) || {};
        if (typeof window.__buildDailyTargetMapForYear === 'function') {
          window.__monthlyTwTargetCache = window.__buildDailyTargetMapForYear(y, bmap);
        }
      }
      function scheduleRebuildColumns(scrollIso, scrollOpts) {
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
      }
      function rebuildColumns() {
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);
        invalidateGroup1TwCache();"""

DAILY_DATE_REBUILD_OLD = """        if (prevYear !== state.year || prevMonth0 !== state.month0) {
          rebuildColumns();
        }
        var scrollOpts = source === 'today' ? { behavior: 'smooth' } : undefined;
        scheduleScroll(iso, scrollOpts);"""

DAILY_DATE_REBUILD_NEW = """        var scrollOpts = source === 'today' ? { behavior: 'smooth' } : undefined;
        if (prevYear !== state.year || prevMonth0 !== state.month0) {
          scheduleRebuildColumns(iso, scrollOpts);
        } else {
          scheduleScroll(iso, scrollOpts);
        }"""

SNAPSHOT_RESOLVE_OLD = """        var dailyTarget = null;
        if (window.KpiYearStore && typeof KpiYearStore.resolveDailyTargetByIso === 'function') {
          var rowYear = Number(String(iso).slice(0, 4));
          if (Number.isFinite(rowYear)) {
            var resolved = KpiYearStore.resolveDailyTargetByIso(rowYear, iso);
            if (resolved && Number.isFinite(Number(resolved.value))) {
              dailyTarget = Number(resolved.value);
            }
          }
        } else if (typeof window.__computeTwMetricsForIso === 'function') {"""

SNAPSHOT_RESOLVE_NEW = """        var dailyTarget = null;
        var rowYear = Number(String(iso).slice(0, 4));
        var cacheMap = window.__monthlyTwTargetCache;
        var cacheY = window.__monthlyTwTargetCacheYear;
        if (
          cacheMap &&
          Number.isFinite(rowYear) &&
          cacheY === rowYear &&
          Object.prototype.hasOwnProperty.call(cacheMap, iso)
        ) {
          var cachedTarget = Number(cacheMap[iso]);
          if (Number.isFinite(cachedTarget)) dailyTarget = cachedTarget;
        } else if (window.KpiYearStore && typeof KpiYearStore.resolveDailyTargetByIso === 'function') {
          if (Number.isFinite(rowYear)) {
            var resolved = KpiYearStore.resolveDailyTargetByIso(rowYear, iso);
            if (resolved && Number.isFinite(Number(resolved.value))) {
              dailyTarget = Number(resolved.value);
            }
          }
        } else if (typeof window.__computeTwMetricsForIso === 'function') {"""


def _apply(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n", 1)[0].strip() in text:
        return text
    raise SystemExit(f"{label} patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = _apply(text, EXPORT_TARGET_MAP_OLD, EXPORT_TARGET_MAP_NEW, "export target map")
    text = _apply(text, COCKPIT_YEAR_LISTENER_OLD, COCKPIT_YEAR_LISTENER_NEW, "defer cockpit")
    if DUP_BD_LISTENER in text:
        text = text.replace(DUP_BD_LISTENER, DUP_BD_REMOVED, 1)
    text = _apply(text, COCKPIT_SELECTED_OLD, COCKPIT_SELECTED_NEW, "skip dup cockpit")
    text = _apply(text, SET_SELECTED_DATE_OLD, SET_SELECTED_DATE_NEW, "defer persist")
    text = _apply(text, REBUILD_HELPERS_OLD, REBUILD_HELPERS_NEW, "rebuild helpers")
    text = _apply(text, DAILY_DATE_REBUILD_OLD, DAILY_DATE_REBUILD_NEW, "schedule rebuild")
    text = _apply(text, SNAPSHOT_RESOLVE_OLD, SNAPSHOT_RESOLVE_NEW, "target cache lookup")
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

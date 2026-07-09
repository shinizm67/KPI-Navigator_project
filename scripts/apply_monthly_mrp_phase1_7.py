#!/usr/bin/env python3
"""MRP Phase 1.7 — Monthly only: defer month-cross rebuild; keep target-map cache across rebuilds."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE1-7 */"

CROSS_MONTH_OLD = """      function crossMonthByEdge(dir) {
        var next = clampYearMonth(state.year, state.month0 + dir);
        if (next.year === state.year && next.month0 === state.month0) return false;
        state.year = next.year;
        state.month0 = next.month0;
        persistMonthlyLast();
        renderPickerMenu();
        rebuildColumns();
        var iso = dir < 0
          ? toISODateLocal(new Date(state.year, state.month0, daysInMonth(state.year, state.month0)))
          : toISODateLocal(new Date(state.year, state.month0, 1));
        scrollToIso(iso);
        syncArea2ByIso(iso);
        syncYearUi(state.year);
        pendingCross = null;
        return true;
      }"""

CROSS_MONTH_NEW = f"""      {MARKER}
      function crossMonthByEdge(dir) {{
        var next = clampYearMonth(state.year, state.month0 + dir);
        if (next.year === state.year && next.month0 === state.month0) return false;
        state.year = next.year;
        state.month0 = next.month0;
        persistMonthlyLast();
        renderPickerMenu();
        var iso = dir < 0
          ? toISODateLocal(new Date(state.year, state.month0, daysInMonth(state.year, state.month0)))
          : toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleRebuildColumns(iso, undefined, function () {{
          syncArea2ByIso(iso);
          syncYearUi(state.year);
          pendingCross = null;
        }});
        return true;
      }}"""

BUMP_MONTH_OLD = """      function bumpMonth(delta) {
        var clamped = clampYearMonth(state.year, state.month0 + delta);
        if (clamped.year === state.year && clamped.month0 === state.month0) {
          scheduleScroll(toISODateLocal(new Date(state.year, state.month0, 1)));
          return;
        }
        state.year = clamped.year;
        state.month0 = clamped.month0;
        persistMonthlyLast();
        renderPickerMenu();
        rebuildColumns();
        var iso = toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleScroll(iso);
        syncArea2ByIso(iso);
        syncYearUi(state.year);
      }"""

BUMP_MONTH_NEW = """      function bumpMonth(delta) {
        var clamped = clampYearMonth(state.year, state.month0 + delta);
        if (clamped.year === state.year && clamped.month0 === state.month0) {
          scheduleScroll(toISODateLocal(new Date(state.year, state.month0, 1)));
          return;
        }
        state.year = clamped.year;
        state.month0 = clamped.month0;
        persistMonthlyLast();
        renderPickerMenu();
        var iso = toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleRebuildColumns(iso, undefined, function () {
          syncArea2ByIso(iso);
          syncYearUi(state.year);
        });
      }"""

APPLY_NAV_OLD = """        setStateYearMonth(y, m);
        persistMonthlyLast();
        renderPickerMenu();
        rebuildColumns();
        var iso = focusIsoForNav(nav, dailyIso) || toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleScroll(iso);
        syncYearUi(state.year);
      }
      function bumpMonth(delta) {"""

APPLY_NAV_NEW = """        setStateYearMonth(y, m);
        persistMonthlyLast();
        renderPickerMenu();
        var iso = focusIsoForNav(nav, dailyIso) || toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleRebuildColumns(iso, undefined, function () {
          syncYearUi(state.year);
        });
      }
      function bumpMonth(delta) {"""

MENU_CLICK_OLD = """          setStateYearMonth(state.year, idx);
          persistMonthlyLast();
          renderPickerMenu();
          rebuildColumns();
          var isoPick = toISODateLocal(new Date(state.year, state.month0, 1));
          scheduleScroll(isoPick);
          syncArea2ByIso(isoPick);
          syncYearUi(state.year);"""

MENU_CLICK_NEW = """          setStateYearMonth(state.year, idx);
          persistMonthlyLast();
          renderPickerMenu();
          var isoPick = toISODateLocal(new Date(state.year, state.month0, 1));
          scheduleRebuildColumns(isoPick, undefined, function () {
            syncArea2ByIso(isoPick);
            syncYearUi(state.year);
          });"""

SET_MONTH0_OLD = """      window.__MONTHLY_UI.setMonth0 = function (m0) {
        m0 = Number(m0);
        if (m0 < 0 || m0 > 11) return;
        setStateYearMonth(state.year, m0);
        persistMonthlyLast();
        renderPickerMenu();
        rebuildColumns();
        var iso = toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleScroll(iso);
        syncArea2ByIso(iso);
        syncYearUi(state.year);
      };"""

SET_MONTH0_NEW = """      window.__MONTHLY_UI.setMonth0 = function (m0) {
        m0 = Number(m0);
        if (m0 < 0 || m0 > 11) return;
        setStateYearMonth(state.year, m0);
        persistMonthlyLast();
        renderPickerMenu();
        var iso = toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleRebuildColumns(iso, undefined, function () {
          syncArea2ByIso(iso);
          syncYearUi(state.year);
        });
      };"""

PRIME_OLD = """      function primeMonthlyTwTargetCache(y) {
        y = Number(y);
        clearMonthlyTwTargetMapsByYear();
        getMonthlyTwTargetMapForYear(y);
        getMonthlyTwTargetMapForYear(y - 1);
        getMonthlyTwTargetMapForYear(y + 1);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = window.__monthlyTwTargetMapsByYear[y] || null;
      }"""

PRIME_NEW = f"""      {MARKER}
      function invalidateMonthlyTwTargetCache() {{
        clearMonthlyTwTargetMapsByYear();
        window.__monthlyTwTargetCacheYear = null;
        window.__monthlyTwTargetCache = null;
      }}
      function primeMonthlyTwTargetCache(y) {{
        y = Number(y);
        getMonthlyTwTargetMapForYear(y);
        getMonthlyTwTargetMapForYear(y - 1);
        getMonthlyTwTargetMapForYear(y + 1);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = window.__monthlyTwTargetMapsByYear[y] || null;
      }}"""

INVALIDATE_LISTENERS_OLD = """      /* KPI-MONTHLY-TW-LISTENERS */
      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();"""

INVALIDATE_LISTENERS_NEW = """      /* KPI-MONTHLY-TW-LISTENERS */
      document.addEventListener('kpi:annualPlanChanged', invalidateMonthlyTwTargetCache);
      document.addEventListener('kpi:businessDayChanged', invalidateMonthlyTwTargetCache);
      document.addEventListener('kpi:dailyTargetModeChanged', invalidateMonthlyTwTargetCache);
      document.addEventListener('kpi:weekdayBaselineChanged', invalidateMonthlyTwTargetCache);
      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();"""

BD_MAP_OLD = """      document.addEventListener('annual:businessDayMapChanged', function () {
        var keepIso = currentFocusIso || readDailySelectedIso() || toISODateLocal(new Date(state.year, state.month0, 1));
        rebuildColumns();
        scheduleScroll(keepIso);
      });"""

BD_MAP_NEW = """      document.addEventListener('annual:businessDayMapChanged', function () {
        invalidateMonthlyTwTargetCache();
        var keepIso = currentFocusIso || readDailySelectedIso() || toISODateLocal(new Date(state.year, state.month0, 1));
        rebuildColumns();
        scheduleScroll(keepIso);
      });"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already applied) {path.relative_to(ROOT)}")
        return
    replacements = (
        (CROSS_MONTH_OLD, CROSS_MONTH_NEW, "crossMonth"),
        (BUMP_MONTH_OLD, BUMP_MONTH_NEW, "bumpMonth"),
        (APPLY_NAV_OLD, APPLY_NAV_NEW, "applyNav"),
        (MENU_CLICK_OLD, MENU_CLICK_NEW, "menuClick"),
        (SET_MONTH0_OLD, SET_MONTH0_NEW, "setMonth0"),
        (PRIME_OLD, PRIME_NEW, "prime"),
        (INVALIDATE_LISTENERS_OLD, INVALIDATE_LISTENERS_NEW, "listeners"),
        (BD_MAP_OLD, BD_MAP_NEW, "bdMap"),
    )
    for old, new, label in replacements:
        if old not in text:
            raise SystemExit(f"phase1.7 {label} anchor miss: {path}")
        text = text.replace(old, new, 1)
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

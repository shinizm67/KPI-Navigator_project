#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP-5b: Annual スクロール hot path の副作用削減（性能第2弾）

計測で判明したボトルネック:
  - focus-sync 毎に onArea1CockpitRefresh → computeTwMetricsForIso（年365日ループ）
  - focus-sync 毎に persistStore / syncAnnualNavToStorage（同期ストレージ書き込み）
  - refreshLower が毎フレームセル textContent を全書き換え

対策（Monthly MRP 2.5 同型を Annual に移植）:
  1) focus-sync 時は Cockpit 更新を 320ms debounce（着地後1回）
  2) focus-sync 時は persistStore を 500ms debounce
  3) refreshLower は行 index 変化時のみセル内容を更新（transform は毎フレーム）

冪等: 'KPI-ARP-PHASE5B' が既に含まれていればスキップ。
"""

from pathlib import Path

FILES = [
    "app/annual/index.html",
    "en/app/annual/index.html",
]

MARKER = "KPI-ARP-PHASE5B"

SET_SELECTED_DATE_OLD = """        function setSelectedDate(iso, source) {
          if (!validIso(iso)) return;
          store.meta.selectedDate = iso;
          persistStore();"""

SET_SELECTED_DATE_NEW = """        function setSelectedDate(iso, source) {
          if (!validIso(iso)) return;
          store.meta.selectedDate = iso;
          /* KPI-ARP-PHASE5B: focus-sync は永続化を debounce（スクロール中の同期 I/O 回避） */
          var navSrc = source || 'kpi-year-store';
          var deferPersist =
            navSrc === 'focus-sync' ||
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
          }"""

COCKPIT_LISTENERS_OLD = """      document.addEventListener('annual:dailyDateChanged', onArea1CockpitRefresh);
      document.addEventListener('kpi:selectedDateChanged', onArea1CockpitRefresh);"""

COCKPIT_LISTENERS_NEW = """      /* KPI-ARP-PHASE5B: focus-sync 中の Cockpit 再計算を debounce（着地後1回） */
      var __area1CockpitLowPriorityTimer = null;
      function onArea1CockpitRefreshLowPriority() {
        if (__area1CockpitLowPriorityTimer != null) window.clearTimeout(__area1CockpitLowPriorityTimer);
        __area1CockpitLowPriorityTimer = window.setTimeout(function () {
          __area1CockpitLowPriorityTimer = null;
          refreshArea1Cockpit(resolveArea1Iso());
        }, 320);
      }
      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var src = ev && ev.detail && ev.detail.source;
        if (src === 'focus-sync') {
          onArea1CockpitRefreshLowPriority();
          return;
        }
        onArea1CockpitRefresh();
      });
      document.addEventListener('kpi:selectedDateChanged', function (ev) {
        var src = ev && ev.detail && ev.detail.source;
        if (src === 'focus-sync') {
          onArea1CockpitRefreshLowPriority();
          return;
        }
        onArea1CockpitRefresh();
      });"""

APPLY_DAILY_NAV_OLD = """        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncAnnualNavToStorage === 'function') {
          window.__ANNUAL_UI.syncAnnualNavToStorage();
        }
        return true;"""

APPLY_DAILY_NAV_NEW = """        /* KPI-ARP-PHASE5B: focus-sync の nav 永続化も debounce */
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncAnnualNavToStorage === 'function') {
          var navSrc2 = source || 'selection';
          if (navSrc2 === 'focus-sync') {
            if (window.__annualNavPersistTimer != null) {
              window.clearTimeout(window.__annualNavPersistTimer);
            }
            window.__annualNavPersistTimer = window.setTimeout(function () {
              window.__annualNavPersistTimer = null;
              window.__ANNUAL_UI.syncAnnualNavToStorage();
            }, 500);
          } else {
            window.__ANNUAL_UI.syncAnnualNavToStorage();
          }
        }
        return true;"""

REFRESH_LOWER_OLD = """      var raf = 0;
      var LOWER_ROW_STEP_PX = 49;

      function refreshLower() {
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(function () {
          var state = getFocusedRowState();
          writeLowerFromRow(state.row);
          var expanded = document.body.classList.contains('annual-focus-bar-expanded');
          var rows = rowsRoot.children;
          var prevRow = state.idx > 0 ? rows[state.idx - 1] : state.row;
          var nextRow = state.idx < rows.length - 1 ? rows[state.idx + 1] : state.row;
          writeLowerFromRowTo(lowerPrev, prevRow);
          writeLowerFromRowTo(lowerNext, nextRow);
          lowerPrev.style.display = 'flex';
          lowerNext.style.display = 'flex';
          var oy = state.offset;"""

REFRESH_LOWER_NEW = """      var raf = 0;
      var LOWER_ROW_STEP_PX = 49;
      /* KPI-ARP-PHASE5B: 行 index が変わったときだけセル内容を更新 */
      var __lowerLastIdx = -1;

      function refreshLower() {
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(function () {
          var state = getFocusedRowState();
          var idx = state.idx;
          if (idx !== __lowerLastIdx) {
            __lowerLastIdx = idx;
            writeLowerFromRow(state.row);
            var rows = rowsRoot.children;
            var prevRow = idx > 0 ? rows[idx - 1] : state.row;
            var nextRow = idx < rows.length - 1 ? rows[idx + 1] : state.row;
            writeLowerFromRowTo(lowerPrev, prevRow);
            writeLowerFromRowTo(lowerNext, nextRow);
            lowerPrev.style.display = 'flex';
            lowerNext.style.display = 'flex';
          }
          var expanded = document.body.classList.contains('annual-focus-bar-expanded');
          var oy = state.offset;"""

TIMELINE_INVALIDATE_OLD = """      document.addEventListener('annual:timelineRowsRendered', function () {
        setTimeout(refreshLower, 0);
      });"""

TIMELINE_INVALIDATE_NEW = """      document.addEventListener('annual:timelineRowsRendered', function () {
        __lowerLastIdx = -1;
        setTimeout(refreshLower, 0);
      });"""

EDITS = [
    ("setSelectedDate defer persist", SET_SELECTED_DATE_OLD, SET_SELECTED_DATE_NEW),
    ("cockpit focus-sync debounce", COCKPIT_LISTENERS_OLD, COCKPIT_LISTENERS_NEW),
    ("applyDailySelection nav defer", APPLY_DAILY_NAV_OLD, APPLY_DAILY_NAV_NEW),
    ("refreshLower index cache", REFRESH_LOWER_OLD, REFRESH_LOWER_NEW),
    ("timeline invalidate lower idx", TIMELINE_INVALIDATE_OLD, TIMELINE_INVALIDATE_NEW),
]


def apply_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"  SKIP (already applied): {path}")
        return False
    for name, old, new in EDITS:
        cnt = text.count(old)
        if cnt != 1:
            raise SystemExit(f"  ERROR in {path}: [{name}] expected 1, found {cnt}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  OK: {path}")
    return True


def main():
    root = Path(__file__).resolve().parent.parent
    changed = 0
    for rel in FILES:
        p = root / rel
        if apply_file(p):
            changed += 1
    print(f"Done. {changed} file(s) changed.")


if __name__ == "__main__":
    main()

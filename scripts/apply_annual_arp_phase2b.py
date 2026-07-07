#!/usr/bin/env python3
"""ARP Phase 2b — Cockpit year-nav display follow (display only) + landing polish.

- setCalendarYearDisplayOnly(): Cockpit の 年ナビ表示・メニュー・calendarYear を
  annual:calendarYearChanged を飛ばさずに軽量同期（二重描画 / selectedDate 上書き無し）。
- crossYearByEdge: 年跨ぎ時に Cockpit 年ナビ表示 + 営業日数表示を追従。
- 着地: 慣性スクロールを rAF で打ち消し、snapping 保持を 60ms→160ms に延長。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ARP-PHASE2B */"

SET_CAL_YEAR_OLD = """      window.__ANNUAL_UI.setCalendarYear = function (y) {
        y = Number(y);
        if (!Number.isFinite(y)) return;
        y = Math.max(minYear, Math.min(maxYear, Math.round(y)));
        if (currentYear === y) return;
        currentYear = y;
        renderYear();
      };"""

SET_CAL_YEAR_NEW = """      window.__ANNUAL_UI.setCalendarYear = function (y) {
        y = Number(y);
        if (!Number.isFinite(y)) return;
        y = Math.max(minYear, Math.min(maxYear, Math.round(y)));
        if (currentYear === y) return;
        currentYear = y;
        renderYear();
      };
      /* KPI-ARP-PHASE2B: 年ナビ表示のみを軽量同期（イベント非発火・副作用なし） */
      window.__ANNUAL_UI.setCalendarYearDisplayOnly = function (y) {
        y = Number(y);
        if (!Number.isFinite(y)) return;
        y = Math.max(minYear, Math.min(maxYear, Math.round(y)));
        currentYear = y;
        yearBtn.textContent = String(currentYear);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.calendarYear = currentYear;
        buildYearMenu();
      };"""

CROSS_TAIL_OLD = """        var yearBadge = document.getElementById('annual-daily-focus-tw-year');
        if (yearBadge) yearBadge.textContent = String(nextYear);
        var iso = dir > 0 ? nextYear + '-01-01' : nextYear + '-12-31';
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        var idx = -1;
        for (var i = 0; i < rows.length; i++) {
          if (rows[i].getAttribute('data-iso-date') === iso) {
            idx = i;
            break;
          }
        }
        if (idx >= 0) {
          var target = getScrollTopForRowIndex(idx);
          tableScroll.scrollTop = target;
          setTimeout(function () {
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
          }, 60);
        } else {
          snapping = false;
        }
        return true;"""

CROSS_TAIL_NEW = """        var yearBadge = document.getElementById('annual-daily-focus-tw-year');
        if (yearBadge) yearBadge.textContent = String(nextYear);
        /* KPI-ARP-PHASE2B: Cockpit 年ナビ表示・営業日数を追従（表示のみ・副作用なし） */
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setCalendarYearDisplayOnly === 'function') {
          window.__ANNUAL_UI.setCalendarYearDisplayOnly(nextYear);
        }
        if (
          window.__ANNUAL_UI &&
          typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
        ) {
          window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
        }
        var iso = dir > 0 ? nextYear + '-01-01' : nextYear + '-12-31';
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        var idx = -1;
        for (var i = 0; i < rows.length; i++) {
          if (rows[i].getAttribute('data-iso-date') === iso) {
            idx = i;
            break;
          }
        }
        if (idx >= 0) {
          var target = getScrollTopForRowIndex(idx);
          /* KPI-ARP-PHASE2B: 慣性スクロールを打ち消して境界日に確実に着地 */
          tableScroll.scrollTop = target;
          requestAnimationFrame(function () {
            tableScroll.scrollTop = target;
            requestAnimationFrame(function () {
              tableScroll.scrollTop = target;
            });
          });
          setTimeout(function () {
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
          }, 160);
        } else {
          snapping = false;
        }
        return true;"""


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"skip (already applied): {path.relative_to(ROOT)}")
            continue
        if SET_CAL_YEAR_OLD not in text:
            raise ValueError(f"setCalendarYear anchor not found: {path.relative_to(ROOT)}")
        if CROSS_TAIL_OLD not in text:
            raise ValueError(f"crossYearByEdge tail anchor not found: {path.relative_to(ROOT)}")
        text = text.replace(SET_CAL_YEAR_OLD, SET_CAL_YEAR_NEW, 1)
        text = text.replace(CROSS_TAIL_OLD, CROSS_TAIL_NEW, 1)
        path.write_text(text, encoding="utf-8")
        print(f"applied: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

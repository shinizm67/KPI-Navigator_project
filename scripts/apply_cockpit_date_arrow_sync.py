#!/usr/bin/env python3
"""Cockpit ◀/▶ must move one day and snap TW instantly (no smooth-scroll fight)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNUAL = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]
MONTHLY = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]

SHIFT_YEAR_OLD = """      function shiftDailyDateToCalendarYear(newYear) {
        newYear = Number(newYear);
        if (!Number.isFinite(newYear)) return;
        var cur = parseISODateLocal(window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate);
        if (!cur) return;
        var mo = cur.getMonth();"""

SHIFT_YEAR_NEW = """      function shiftDailyDateToCalendarYear(newYear) {
        newYear = Number(newYear);
        if (!Number.isFinite(newYear)) return;
        var cur = parseISODateLocal(window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate);
        if (!cur) return;
        if (cur.getFullYear() === newYear) return;
        var mo = cur.getMonth();"""

SHIFT_OLD = """      function shiftDateByDays(deltaDays) {
        var curIso = window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate;
        var cur = parseISODateLocal(curIso);
        if (!cur) return;
        var d = new Date(cur.getFullYear(), cur.getMonth(), cur.getDate() + Number(deltaDays || 0));
        var ok = applyDailySelection(d, 'arrow');
        if (!ok) return;
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setCalendarYear === 'function') {
          window.__ANNUAL_UI.setCalendarYear(d.getFullYear());
        }
      }"""

SHIFT_NEW = """      function shiftDateByDays(deltaDays) {
        var curIso = window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate;
        var cur = parseISODateLocal(curIso);
        if (!cur) return;
        var d = new Date(cur.getFullYear(), cur.getMonth(), cur.getDate() + Number(deltaDays || 0));
        var prevY = cur.getFullYear();
        var ok = applyDailySelection(d, 'arrow');
        if (!ok) return;
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.lockFocusDateSync === 'function') {
          window.__ANNUAL_UI.lockFocusDateSync(toISODateLocal(d), d.getFullYear() !== prevY ? 800 : 220);
        }
        if (
          d.getFullYear() !== prevY &&
          window.__ANNUAL_UI &&
          typeof window.__ANNUAL_UI.setCalendarYear === 'function'
        ) {
          window.__ANNUAL_UI.setCalendarYear(d.getFullYear());
        }
      }"""

HOLD_OLD = """        function stepOnce() {
          shiftDateByDays(delta);
        }
        function onPointerDown(ev) {
          if (ev.pointerType === 'mouse' && ev.button !== 0) return;
          ev.preventDefault();
          try { btn.setPointerCapture(ev.pointerId); } catch (_capErr) {}
          clearHold();
          stepOnce();
          delayId = setTimeout(function () {
            repeatId = setInterval(stepOnce, 75);
          }, 400);
        }"""

HOLD_NEW = """        function stepOnce() {
          var curIso = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate;
          var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
          var iy = curIso ? Number(String(curIso).slice(0, 4)) : NaN;
          if (Number.isFinite(cy) && Number.isFinite(iy) && cy !== iy) return;
          shiftDateByDays(delta);
        }
        function onPointerDown(ev) {
          if (ev.pointerType === 'mouse' && ev.button !== 0) return;
          ev.preventDefault();
          try { btn.setPointerCapture(ev.pointerId); } catch (_capErr) {}
          clearHold();
          stepOnce();
          delayId = setTimeout(function () {
            repeatId = setInterval(stepOnce, 75);
          }, 400);
        }"""

ANNUAL_ARROW_YEAR_OLD = """        if (source === 'focus-sync') return;
        if (
          source === 'timeline-bootstrap' ||
          source === 'initial-sync' ||
          source === 'initial'
        ) {
          lockFocusDateSync(iso, 1800);
        }"""

ANNUAL_ARROW_YEAR_NEW = """        if (source === 'focus-sync') return;
        if (source === 'arrow') {
          var __arrowCy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
          var __arrowIy = Number(String(iso).slice(0, 4));
          if (Number.isFinite(__arrowCy) && Number.isFinite(__arrowIy) && __arrowCy !== __arrowIy) {
            lockFocusDateSync(iso, 800);
            return;
          }
        }
        if (
          source === 'timeline-bootstrap' ||
          source === 'initial-sync' ||
          source === 'initial'
        ) {
          lockFocusDateSync(iso, 1800);
        }"""

ANNUAL_SCROLL_OLD = """          if (
            hardBootstrap &&
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.scrollTableToIso === 'function' &&
            window.__ANNUAL_UI.scrollTableToIso(iso, { lockMs: 1800 })
          ) {
            return;
          }
          var row = document.querySelector('#annual-daily-rows .annual-daily-row[data-iso-date="' + iso + '"]');
          if (!row) {
            if (tries < maxTries) {
              setTimeout(tryScrollToISO, 50);
            }
            return;
          }
          var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
          var idx = -1;
          for (var i = 0; i < rows.length; i += 1) {
            if (rows[i] === row) {
              idx = i;
              break;
            }
          }
          if (idx < 0) return;

          if (snapTimer) clearTimeout(snapTimer);
          snapping = true;
          var target = getScrollTopForRowIndex(idx);
          tableScroll.scrollTo({ top: target, behavior: 'smooth' });
          setTimeout(function () {
            snapping = false;
          }, 220);"""

ANNUAL_SCROLL_NEW = """          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.scrollTableToIso === 'function' &&
            window.__ANNUAL_UI.scrollTableToIso(iso, { lockMs: hardBootstrap ? 1800 : 400 })
          ) {
            return;
          }
          var row = document.querySelector('#annual-daily-rows .annual-daily-row[data-iso-date="' + iso + '"]');
          if (!row) {
            if (tries < maxTries) {
              setTimeout(tryScrollToISO, 50);
            }
            return;
          }
          var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
          var idx = -1;
          for (var i = 0; i < rows.length; i += 1) {
            if (rows[i] === row) {
              idx = i;
              break;
            }
          }
          if (idx < 0) return;

          if (snapTimer) clearTimeout(snapTimer);
          snapping = true;
          __geomCache = null;
          var target = getScrollTopForRowIndex(idx);
          tableScroll.scrollTop = target;
          snapping = false;
          if (typeof window.__refreshAnnualFocusBarLower === 'function') {
            window.__refreshAnnualFocusBarLower();
          }"""

MONTHLY_ARROW_YEAR_OLD = """        currentFocusIso = iso;
        if (source === 'focus-sync') return;
        /* KPI-MRP-PHASE2-9 */"""

MONTHLY_ARROW_YEAR_NEW = """        currentFocusIso = iso;
        if (source === 'focus-sync') return;
        if (source === 'arrow') {
          var __arrowCy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
          var __arrowIy = Number(String(iso).slice(0, 4));
          if (Number.isFinite(__arrowCy) && Number.isFinite(__arrowIy) && __arrowCy !== __arrowIy) {
            return;
          }
        }
        /* KPI-MRP-PHASE2-9 */"""

MONTHLY_SCROLL_OLD = """          if (snapTimer) clearTimeout(snapTimer);
          snapping = true;
          var target = getScrollTopForRowIndex(idx);
          tableScroll.scrollTo({ top: target, behavior: 'smooth' });
          setTimeout(function () {
            snapping = false;
          }, 220);
        }
        tryScrollToISO();
      });"""

MONTHLY_SCROLL_NEW = """          if (snapTimer) clearTimeout(snapTimer);
          snapping = true;
          var target = getScrollTopForRowIndex(idx);
          tableScroll.scrollTop = target;
          snapping = false;
          if (typeof window.__refreshAnnualFocusBarLower === 'function') {
            window.__refreshAnnualFocusBarLower();
          }
        }
        tryScrollToISO();
      });"""


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    cnt = text.count(old)
    if cnt == 0:
        if new in text:
            print(f"  skip {label} (already) {path.relative_to(ROOT)}")
            return text
        raise SystemExit(f"  ERROR {label} not found: {path.relative_to(ROOT)}")
    if cnt != 1:
        raise SystemExit(f"  ERROR {label} found {cnt}: {path.relative_to(ROOT)}")
    print(f"  patch {label} {path.relative_to(ROOT)}")
    return text.replace(old, new, 1)


def main() -> int:
    for path in ANNUAL:
        text = path.read_text(encoding="utf-8")
        text = replace_once(text, SHIFT_OLD, SHIFT_NEW, "shift", path)
        text = replace_once(text, SHIFT_YEAR_OLD, SHIFT_YEAR_NEW, "shift-year", path)
        text = replace_once(text, HOLD_OLD, HOLD_NEW, "hold", path)
        text = replace_once(text, ANNUAL_ARROW_YEAR_OLD, ANNUAL_ARROW_YEAR_NEW, "arrow-year", path)
        text = replace_once(text, ANNUAL_SCROLL_OLD, ANNUAL_SCROLL_NEW, "scroll", path)
        path.write_text(text, encoding="utf-8")
    for path in MONTHLY:
        text = path.read_text(encoding="utf-8")
        # Monthly MRP may have prepended a busy-guard to shiftDateByDays.
        if SHIFT_OLD in text:
            text = replace_once(text, SHIFT_OLD, SHIFT_NEW, "shift", path)
        elif "lockFocusDateSync(toISODateLocal(d), d.getFullYear() !== prevY ? 800 : 220)" in text:
            print(f"  skip shift (already) {path.relative_to(ROOT)}")
        else:
            print(f"  warn shift skipped {path.relative_to(ROOT)}")
        text = replace_once(text, SHIFT_YEAR_OLD, SHIFT_YEAR_NEW, "shift-year", path)
        text = replace_once(text, HOLD_OLD, HOLD_NEW, "hold", path)
        text = replace_once(text, MONTHLY_ARROW_YEAR_OLD, MONTHLY_ARROW_YEAR_NEW, "arrow-year", path)
        text = replace_once(text, MONTHLY_SCROLL_OLD, MONTHLY_SCROLL_NEW, "scroll", path)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

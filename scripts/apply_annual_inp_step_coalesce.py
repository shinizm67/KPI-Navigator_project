#!/usr/bin/env python3
"""Annual Focus Bar 行送りの INP 改善: smooth 廃止 + rAF 集約."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "KPI-ARP-INP-STEP"

OLD = """      function stepTableByRows(step) {
        step = Number(step);
        if (!Number.isFinite(step) || step === 0) return;
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return;
        var range = anchorYearRowRange();
        var idx = getNearestActiveFocusRowIndex() + (step > 0 ? 1 : -1);
        if (range.first >= 0 && range.last >= 0) {
          if (idx < range.first) idx = range.first;
          if (idx > range.last) idx = range.last;
        } else {
          if (idx < 0) idx = 0;
          if (idx >= rows.length) idx = rows.length - 1;
        }
        var target = getScrollTopForRowIndex(idx);
        if (snapTimer) clearTimeout(snapTimer);
        if (Math.abs(target - tableScroll.scrollTop) < 1) {
          syncDailyDateFromFocusedRowForIndex(idx);
          return;
        }
        snapping = true;
        tableScroll.scrollTo({ top: target, behavior: 'smooth' });
        waitForVerticalScrollSettle(target, function () {
          snapping = false;
          syncDailyDateFromFocusedRowForIndex(idx);
        });
      }"""

NEW = """      /* KPI-ARP-INP-STEP: 行送りは即時 scroll + rAF 集約（smooth の INP 悪化を回避） */
      var __stepPendingDelta = 0;
      var __stepRaf = 0;
      function stepTableByRows(step) {
        step = Number(step);
        if (!Number.isFinite(step) || step === 0) return;
        __stepPendingDelta += step > 0 ? 1 : -1;
        if (__stepRaf) return;
        __stepRaf = requestAnimationFrame(function () {
          __stepRaf = 0;
          var pending = __stepPendingDelta;
          __stepPendingDelta = 0;
          if (!pending) return;
          stepTableByRowsNow(pending);
        });
      }
      function stepTableByRowsNow(step) {
        step = Number(step);
        if (!Number.isFinite(step) || step === 0) return;
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return;
        var range = anchorYearRowRange();
        var idx = getNearestActiveFocusRowIndex() + step;
        if (range.first >= 0 && range.last >= 0) {
          if (idx < range.first) idx = range.first;
          if (idx > range.last) idx = range.last;
        } else {
          if (idx < 0) idx = 0;
          if (idx >= rows.length) idx = rows.length - 1;
        }
        var target = getScrollTopForRowIndex(idx);
        if (snapTimer) clearTimeout(snapTimer);
        if (Math.abs(target - tableScroll.scrollTop) < 1) {
          syncDailyDateFromFocusedRowForIndex(idx);
          return;
        }
        snapping = true;
        tableScroll.scrollTop = target;
        snapping = false;
        syncDailyDateFromFocusedRowForIndex(idx);
        if (typeof window.__refreshAnnualFocusBarLower === 'function') {
          window.__refreshAnnualFocusBarLower();
        }
      }"""


def main() -> int:
    for path in PAGES:
        text = path.read_text()
        if MARKER in text:
            print(f"skip {path.relative_to(ROOT)} (already applied)")
            continue
        if OLD not in text:
            print(f"MISS {path.relative_to(ROOT)}")
            return 1
        path.write_text(text.replace(OLD, NEW, 1))
        print(f"patched {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

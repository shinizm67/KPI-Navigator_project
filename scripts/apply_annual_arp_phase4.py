#!/usr/bin/env python3
"""ARP Phase 4 — Open mode vertical scroll year-cross (same crossYearByEdge)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ARP-PHASE4 */"

CROSS_EXPANDED_GUARD_OLD = """        /* ARP-2: Close モードのみ。Open は ARP-4 で対応 */
        if (body.classList.contains('annual-focus-bar-expanded')) return false;"""

CROSS_EXPANDED_GUARD_NEW = """        /* KPI-ARP-PHASE4: Close / Open 両方で年跨ぎ */"""

SCHEDULE_SNAP_EXPANDED_OLD = """          if (body.classList.contains('annual-focus-bar-expanded')) {
            snapTableToNearestRow();
          } else {
            /* KPI-ARP-PHASE2: Close時、縦スクロール端で年跨ぎ */
            var maxTop = Math.max(0, tableScroll.scrollHeight - tableScroll.clientHeight);
            if (maxTop > 0) {
              if (tableScroll.scrollTop <= ARP_EDGE_EPS && crossYearByEdge(-1)) return;
              if (tableScroll.scrollTop >= maxTop - ARP_EDGE_EPS && crossYearByEdge(1)) return;
            }
            syncDailyDateFromFocusedRow();
          }"""

SCHEDULE_SNAP_EXPANDED_NEW = """          /* KPI-ARP-PHASE4: Close / Open 共通 — 縦スクロール端で年跨ぎ */
          var maxTop = Math.max(0, tableScroll.scrollHeight - tableScroll.clientHeight);
          if (maxTop > 0) {
            if (tableScroll.scrollTop <= ARP_EDGE_EPS && crossYearByEdge(-1)) return;
            if (tableScroll.scrollTop >= maxTop - ARP_EDGE_EPS && crossYearByEdge(1)) return;
          }
          if (body.classList.contains('annual-focus-bar-expanded')) {
            snapTableToNearestRow();
          } else {
            syncDailyDateFromFocusedRow();
          }"""

CROSS_HSCROLL_OLD = """        var yearBadge = document.getElementById('annual-daily-focus-tw-year');
        if (yearBadge) yearBadge.textContent = String(nextYear);"""

CROSS_HSCROLL_NEW = """        var yearBadge = document.getElementById('annual-daily-focus-tw-year');
        if (yearBadge) yearBadge.textContent = String(nextYear);
        /* KPI-ARP-PHASE4: Open 時の横スクロール位置をリセットして3グループを先頭に */
        if (body.classList.contains('annual-focus-bar-expanded')) {
          tableScroll.scrollLeft = 0;
          syncScrollLeft(tableScroll);
        }"""


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"skip (already applied): {path.relative_to(ROOT)}")
            continue
        if CROSS_EXPANDED_GUARD_OLD not in text:
            raise ValueError(f"expanded guard anchor not found: {path.relative_to(ROOT)}")
        if SCHEDULE_SNAP_EXPANDED_OLD not in text:
            raise ValueError(f"scheduleSnap anchor not found: {path.relative_to(ROOT)}")
        if CROSS_HSCROLL_OLD not in text:
            raise ValueError(f"hscroll anchor not found: {path.relative_to(ROOT)}")
        text = text.replace(CROSS_EXPANDED_GUARD_OLD, CROSS_EXPANDED_GUARD_NEW, 1)
        text = text.replace(SCHEDULE_SNAP_EXPANDED_OLD, SCHEDULE_SNAP_EXPANDED_NEW, 1)
        text = text.replace(CROSS_HSCROLL_OLD, CROSS_HSCROLL_NEW, 1)
        path.write_text(text, encoding="utf-8")
        print(f"applied: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

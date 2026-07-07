#!/usr/bin/env python3
"""ARP Phase 1 — Annual TW: anchor-year-only bounds (default), drop multi-year DOM."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ARP-PHASE1 */"

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

RENDER_HEAD_OLD = """      function renderAnnualDailyTimeline(anchorYear, opts) {
        opts = opts || {};
        anchorYear = Number(anchorYear);
        if (!Number.isFinite(anchorYear)) anchorYear = new Date().getFullYear();
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        var scrollEl = document.getElementById('annual-daily-focus-scroll');
        var prevScroll = opts.preserveScroll && scrollEl ? scrollEl.scrollTop : null;
        var bounds = computeFocusTimelineBounds(anchorYear);"""

RENDER_HEAD_NEW = f"""      function renderAnnualDailyTimeline(anchorYear, opts) {{
        opts = opts || {{}};
        {MARKER}
        if (!document.body.classList.contains('monthly-page') && !opts.boundsHint) {{
          opts.boundsHint = 'anchor-year-only';
        }}
        anchorYear = Number(anchorYear);
        if (!Number.isFinite(anchorYear)) anchorYear = new Date().getFullYear();
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var scrollEl = document.getElementById('annual-daily-focus-scroll');
        var prevScroll = opts.preserveScroll && scrollEl ? scrollEl.scrollTop : null;
        var bounds =
          opts.boundsHint === 'anchor-year-only'
            ? computeAnchorYearTimelineBounds(anchorYear)
            : computeFocusTimelineBounds(anchorYear);"""


def _apply(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if MARKER in text:
        return text
    raise ValueError(f"{label}: anchor not found")


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"skip (already applied): {path.relative_to(ROOT)}")
            continue
        text = _apply(text, BOUNDS_HELPER_OLD, BOUNDS_HELPER_NEW, "bounds helper")
        text = _apply(text, RENDER_HEAD_OLD, RENDER_HEAD_NEW, "render head")
        path.write_text(text, encoding="utf-8")
        print(f"applied: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

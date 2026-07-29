#!/usr/bin/env python3
"""Phase 1: Annual ARP silent year-cross → sync Open table / Cockpit without calendarYearChanged."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

MARKER = "KPI-ARP-YEAR-COCKPIT-SYNC"

OLD = """        function __arpDeferredYearSync() {
          if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setCalendarYearDisplayOnly === 'function') {
            window.__ANNUAL_UI.setCalendarYearDisplayOnly(nextYear);
          }
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
          }
        }"""

NEW = """        function __arpDeferredYearSync() {
          if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setCalendarYearDisplayOnly === 'function') {
            window.__ANNUAL_UI.setCalendarYearDisplayOnly(nextYear);
          }
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
          }
          /* KPI-ARP-YEAR-COCKPIT-SYNC: DisplayOnly 後に Open 表・年次目標を同年へ（イベント非発火） */
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function'
          ) {
            window.__ANNUAL_UI.syncCockpitForCalendarYear(nextYear);
          }
        }"""


def patch_page(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already) {rel}")
        return
    if OLD not in text:
        raise SystemExit(f"__arpDeferredYearSync miss: {rel}")
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"wrote {rel}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

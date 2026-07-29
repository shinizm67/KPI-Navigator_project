#!/usr/bin/env python3
"""Phase 3b: Monthly DisplayOnly path → persist annualNav.calendarYear lightly."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]

MARKER = "KPI-ARP-YEAR-NAV-PERSIST"

OLD = """        /* KPI-ARP-YEAR-COCKPIT-SYNC: DisplayOnly 後に Cockpit/Open 表を同年へ（イベント非発火） */
        if (
          window.__ANNUAL_UI &&
          typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function'
        ) {
          window.__ANNUAL_UI.syncCockpitForCalendarYear(Number(y));
        }
        syncMonthlyVfocusYearBadge(Number(y));
      }"""

NEW = """        /* KPI-ARP-YEAR-COCKPIT-SYNC: DisplayOnly 後に Cockpit/Open 表を同年へ（イベント非発火） */
        if (
          window.__ANNUAL_UI &&
          typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function'
        ) {
          window.__ANNUAL_UI.syncCockpitForCalendarYear(Number(y));
        }
        /* KPI-ARP-YEAR-NAV-PERSIST: calendarYear のみ軽量永続（selectedIso は維持） */
        try {
          var gwNav = window.__KPI_DATA_GATEWAY;
          if (gwNav && typeof gwNav.getJson === 'function' && typeof gwNav.setJson === 'function') {
            var prevNav = gwNav.getJson('kpiNavigator.annualNav') || {};
            var keepIso =
              (window.__ANNUAL_DATA &&
                window.__ANNUAL_DATA.daily &&
                window.__ANNUAL_DATA.daily.selectedDate) ||
              prevNav.selectedIso ||
              null;
            gwNav.setJson('kpiNavigator.annualNav', {
              calendarYear: Number(y),
              selectedIso: keepIso,
            });
          }
        } catch (_eNavPersist) {}
        syncMonthlyVfocusYearBadge(Number(y));
      }"""


def patch_page(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already) {rel}")
        return
    if OLD not in text:
        raise SystemExit(f"cockpit-sync block miss: {rel}")
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

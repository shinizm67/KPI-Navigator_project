#!/usr/bin/env python3
"""ARP Phase 3 — Focus Bar sync hardening after scroll year-cross."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ARP-PHASE3 */"

CROSS_SETTLE_OLD = """          setTimeout(function () {
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
          }, 160);"""

CROSS_SETTLE_NEW = """          setTimeout(function () {
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
            /* KPI-ARP-PHASE3: 年跨ぎ後に Focus Bar 行を確実に同期 */
            if (typeof window.__refreshAnnualFocusBarLower === 'function') {
              window.__refreshAnnualFocusBarLower();
            }
          }, 160);"""

FOCUS_BAR_EXPORT_OLD = """      setTimeout(refreshLower, 0);

      window.__getAnnualDailyFocusedRowState = getFocusedRowState;
    })();"""

FOCUS_BAR_EXPORT_NEW = """      setTimeout(refreshLower, 0);

      window.__getAnnualDailyFocusedRowState = getFocusedRowState;
      /* KPI-ARP-PHASE3 */
      window.__refreshAnnualFocusBarLower = refreshLower;
      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var src = ev && ev.detail && ev.detail.source;
        if (src === 'focus-sync' || src === 'initial-sync') return;
        setTimeout(refreshLower, 0);
      });
    })();"""


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"skip (already applied): {path.relative_to(ROOT)}")
            continue
        if CROSS_SETTLE_OLD not in text:
            raise ValueError(f"crossYear settle anchor not found: {path.relative_to(ROOT)}")
        if FOCUS_BAR_EXPORT_OLD not in text:
            raise ValueError(f"focus bar export anchor not found: {path.relative_to(ROOT)}")
        text = text.replace(CROSS_SETTLE_OLD, CROSS_SETTLE_NEW, 1)
        text = text.replace(FOCUS_BAR_EXPORT_OLD, FOCUS_BAR_EXPORT_NEW, 1)
        path.write_text(text, encoding="utf-8")
        print(f"applied: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

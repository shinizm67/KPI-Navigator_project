#!/usr/bin/env python3
"""Focus Bar must refresh when the ISO at the same row index changes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

IDX_OLD = """      var __lowerLastIdx = -1;

      function refreshLower() {"""

IDX_NEW = """      var __lowerLastIdx = -1;
      var __lowerLastIso = '';
      window.__invalidateAnnualFocusBarLowerCache = function () {
        __lowerLastIdx = -1;
        __lowerLastIso = '';
      };

      function refreshLower() {"""

SKIP_OLD = """          var idx = state.idx;
          if (idx !== __lowerLastIdx) {
            __lowerLastIdx = idx;
            writeLowerFromRow(state.row);"""

SKIP_NEW = """          var idx = state.idx;
          var rowIso = (state.row && state.row.getAttribute('data-iso-date')) || '';
          if (idx !== __lowerLastIdx || rowIso !== __lowerLastIso) {
            __lowerLastIdx = idx;
            __lowerLastIso = rowIso;
            writeLowerFromRow(state.row);"""

RESET_OLD = """      document.addEventListener('annual:calendarYearChanged', function () {
        setTimeout(refreshLower, 0);
      });
      document.addEventListener('annual:timelineRowsRendered', function () {
        __lowerLastIdx = -1;
        setTimeout(refreshLower, 0);
      });"""

RESET_NEW = """      document.addEventListener('annual:calendarYearChanged', function () {
        __lowerLastIdx = -1;
        __lowerLastIso = '';
        setTimeout(refreshLower, 0);
      });
      document.addEventListener('annual:timelineRowsRendered', function () {
        __lowerLastIdx = -1;
        __lowerLastIso = '';
        setTimeout(refreshLower, 0);
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
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        text = replace_once(text, IDX_OLD, IDX_NEW, "cache", path)
        text = replace_once(text, SKIP_OLD, SKIP_NEW, "skip-iso", path)
        text = replace_once(text, RESET_OLD, RESET_NEW, "reset", path)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Follow-up: gap/margin for spacer pitch + Monthly focus index hook."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    cnt = text.count(old)
    if cnt == 0:
        if new in text:
            print(f"  skip {label} {path.relative_to(ROOT)}")
            return text
        raise SystemExit(f"  ERROR {label} not found {path.relative_to(ROOT)}")
    if cnt != 1:
        raise SystemExit(f"  ERROR {label} found {cnt} {path.relative_to(ROOT)}")
    print(f"  patch {label} {path.relative_to(ROOT)}")
    return text.replace(old, new, 1)


CSS_OLD = """    .annual-daily-rows {
      display: flex;
      flex-direction: column;
      gap: 2px;
      width: 600px;
      max-width: none;
      margin: 0;
      padding: 0;
    }
    /* KPI-TW-SPACER: 年+14日の高さは残し、実DOM行は Focus 前後だけ */
    .annual-daily-rows-spacer {
      flex: 0 0 auto;
      width: 100%;
      pointer-events: none;
      visibility: hidden;
    }"""

CSS_NEW = """    .annual-daily-rows {
      display: flex;
      flex-direction: column;
      gap: 0;
      width: 600px;
      max-width: none;
      margin: 0;
      padding: 0;
    }
    /* KPI-TW-SPACER: 年+14日の高さは残し、実DOM行は Focus 前後だけ */
    .annual-daily-rows-spacer {
      flex: 0 0 auto;
      width: 100%;
      pointer-events: none;
      visibility: hidden;
    }
    .annual-daily-rows > .annual-daily-row {
      margin-bottom: 2px;
    }"""

MONTHLY_HOOK_OLD = """      function syncDailyDateFromFocusedRow() {
        syncDailyDateFromFocusedRowForIndex(getNearestFocusRowIndex());
      }

      tableScroll.addEventListener('scroll', function () {
        if (window.__twMaybeShiftVisibleWindow) window.__twMaybeShiftVisibleWindow();"""

MONTHLY_HOOK_NEW = """      function syncDailyDateFromFocusedRow() {
        syncDailyDateFromFocusedRowForIndex(getNearestFocusRowIndex());
      }
      window.__annualTwFocusRowIndex = getNearestFocusRowIndex;

      tableScroll.addEventListener('scroll', function () {
        if (window.__twMaybeShiftVisibleWindow) window.__twMaybeShiftVisibleWindow();"""

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        text = replace_once(text, CSS_OLD, CSS_NEW, "gap", path)
        if "/monthly/" in str(path.relative_to(ROOT)):
            text = replace_once(text, MONTHLY_HOOK_OLD, MONTHLY_HOOK_NEW, "focus-hook", path)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

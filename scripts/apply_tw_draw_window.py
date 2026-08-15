#!/usr/bin/env python3
"""Phase 4: TW draw window (Focus ±4 weeks) + slide at non-year edges."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_block_only import PAGES, patch as patch_tw_block  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

ANNUAL_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]
MONTHLY_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]

ENFORCE_FIRST_OLD = """        if (focusIdx === range.first && lastScrollDir < 0) {
          if (isYearCrossGuardActive() || __crossYearInFlight) {"""

ENFORCE_FIRST_NEW = """        if (focusIdx === range.first && lastScrollDir < 0) {
          /* KPI-TW-DRAW-WINDOW: 年始以外の描画端は窓をずらす */
          var __twFirstIso = '';
          var __twFirstRows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
          if (__twFirstRows && range.first >= 0 && range.first < __twFirstRows.length) {
            __twFirstIso = String(__twFirstRows[range.first].getAttribute('data-iso-date') || '');
          }
          var __twCyTop = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
          if (__twFirstIso && Number.isFinite(__twCyTop) && __twFirstIso !== __twCyTop + '-01-01') {
            edgeArmedDir = 0;
            if (window.__ensureTwDrawWindow && window.__ensureTwDrawWindow(__twFirstIso)) return true;
          }
          if (isYearCrossGuardActive() || __crossYearInFlight) {"""

ENFORCE_LAST_OLD = """        if (focusIdx === range.last && lastScrollDir > 0) {
          if (isYearCrossGuardActive() || __crossYearInFlight) {"""

ENFORCE_LAST_NEW = """        if (focusIdx === range.last && lastScrollDir > 0) {
          /* KPI-TW-DRAW-WINDOW: 年末以外の描画端は窓をずらす */
          var __twLastIso = '';
          var __twLastRows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
          if (__twLastRows && range.last >= 0 && range.last < __twLastRows.length) {
            __twLastIso = String(__twLastRows[range.last].getAttribute('data-iso-date') || '');
          }
          var __twCyBot = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
          if (__twLastIso && Number.isFinite(__twCyBot) && __twLastIso !== __twCyBot + '-12-31') {
            edgeArmedDir = 0;
            if (window.__ensureTwDrawWindow && window.__ensureTwDrawWindow(__twLastIso)) return true;
          }
          if (isYearCrossGuardActive() || __crossYearInFlight) {"""

STEP_ANNUAL_OLD = """        var idx = getNearestActiveFocusRowIndex() + step;
        if (range.first >= 0 && range.last >= 0) {
          if (idx < range.first) idx = range.first;
          if (idx > range.last) idx = range.last;
        } else {
          if (idx < 0) idx = 0;
          if (idx >= rows.length) idx = rows.length - 1;
        }"""

STEP_ANNUAL_NEW = """        var idx = getNearestActiveFocusRowIndex() + step;
        if (range.first >= 0 && range.last >= 0) {
          if (idx < range.first) {
            var __stepFirstIso = rows[range.first]
              ? String(rows[range.first].getAttribute('data-iso-date') || '')
              : '';
            var __stepCy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
            if (
              __stepFirstIso &&
              Number.isFinite(__stepCy) &&
              __stepFirstIso !== __stepCy + '-01-01' &&
              window.__twShiftIso &&
              window.__ensureTwDrawWindow &&
              window.__ensureTwDrawWindow(window.__twShiftIso(__stepFirstIso, -1))
            ) {
              return;
            }
            idx = range.first;
          }
          if (idx > range.last) {
            var __stepLastIso = rows[range.last]
              ? String(rows[range.last].getAttribute('data-iso-date') || '')
              : '';
            var __stepCy2 = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
            if (
              __stepLastIso &&
              Number.isFinite(__stepCy2) &&
              __stepLastIso !== __stepCy2 + '-12-31' &&
              window.__twShiftIso &&
              window.__ensureTwDrawWindow &&
              window.__ensureTwDrawWindow(window.__twShiftIso(__stepLastIso, 1))
            ) {
              return;
            }
            idx = range.last;
          }
        } else {
          if (idx < 0) idx = 0;
          if (idx >= rows.length) idx = rows.length - 1;
        }"""

STEP_MONTHLY_OLD = """        var idx = getNearestFocusRowIndex() + (step > 0 ? 1 : -1);
        if (idx < 0) idx = 0;
        if (idx >= rows.length) idx = rows.length - 1;"""

STEP_MONTHLY_NEW = """        var idx = getNearestFocusRowIndex() + (step > 0 ? 1 : -1);
        if (idx < 0) {
          var __mFirstIso = rows[0] ? String(rows[0].getAttribute('data-iso-date') || '') : '';
          if (
            __mFirstIso &&
            window.__twShiftIso &&
            window.__ensureTwDrawWindow &&
            window.__ensureTwDrawWindow(window.__twShiftIso(__mFirstIso, -1))
          ) {
            return;
          }
          idx = 0;
        }
        if (idx >= rows.length) {
          var __mLastIso = rows[rows.length - 1]
            ? String(rows[rows.length - 1].getAttribute('data-iso-date') || '')
            : '';
          if (
            __mLastIso &&
            window.__twShiftIso &&
            window.__ensureTwDrawWindow &&
            window.__ensureTwDrawWindow(window.__twShiftIso(__mLastIso, 1))
          ) {
            return;
          }
          idx = rows.length - 1;
        }"""


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    cnt = text.count(old)
    if cnt == 0:
        if new.strip()[:40] in text:
            print(f"  skip {label} (already) {path.relative_to(ROOT)}")
            return text
        raise SystemExit(f"  ERROR {label} not found: {path.relative_to(ROOT)}")
    if cnt != 1:
        raise SystemExit(f"  ERROR {label} found {cnt} times: {path.relative_to(ROOT)}")
    print(f"  patch {label} {path.relative_to(ROOT)}")
    return text.replace(old, new, 1)


CROSS_FOCUS_OLD = """        window.__renderAnnualDailyTimeline(nextYear, {
          boundsHint: 'anchor-year-only',
          preserveScroll: false,
          skipBootstrapScroll: true,
        });"""

CROSS_FOCUS_NEW = """        window.__renderAnnualDailyTimeline(nextYear, {
          boundsHint: 'anchor-year-only',
          preserveScroll: false,
          skipBootstrapScroll: true,
          focusIso: iso,
        });"""


def patch_annual_scroll(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, ENFORCE_FIRST_OLD, ENFORCE_FIRST_NEW, "enforce-first", path)
    text = replace_once(text, ENFORCE_LAST_OLD, ENFORCE_LAST_NEW, "enforce-last", path)
    text = replace_once(text, STEP_ANNUAL_OLD, STEP_ANNUAL_NEW, "step-annual", path)
    text = replace_once(text, CROSS_FOCUS_OLD, CROSS_FOCUS_NEW, "cross-focusIso", path)
    path.write_text(text, encoding="utf-8")


def patch_monthly_step(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, STEP_MONTHLY_OLD, STEP_MONTHLY_NEW, "step-monthly", path)
    path.write_text(text, encoding="utf-8")


CSS_SCROLL_OLD = """    .annual-daily-focus-scroll {
      height: 100%;
      overflow: auto;
      box-sizing: border-box;
      padding: 12px 10px;
      -webkit-overflow-scrolling: touch;
    }"""

CSS_SCROLL_NEW = """    .annual-daily-focus-scroll {
      height: 100%;
      overflow: auto;
      box-sizing: border-box;
      padding: 12px 10px;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior: contain;
    }"""


def patch_overscroll(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CSS_SCROLL_NEW in text:
        print(f"  skip overscroll (already) {path.relative_to(ROOT)}")
        return
    if CSS_SCROLL_OLD not in text:
        print(f"  skip overscroll (no css) {path.relative_to(ROOT)}")
        return
    path.write_text(text.replace(CSS_SCROLL_OLD, CSS_SCROLL_NEW, 1), encoding="utf-8")
    print(f"  patch overscroll {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        path.write_text(patch_tw_block(text), encoding="utf-8")
        print(f"wrote TW block {path.relative_to(ROOT)}")

    for path in ANNUAL_PAGES:
        patch_annual_scroll(path)
    for path in MONTHLY_PAGES:
        patch_monthly_step(path)
    for path in PAGES:
        patch_overscroll(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

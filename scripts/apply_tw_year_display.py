#!/usr/bin/env python3
"""TW / Focus Bar year display + Annual Global Menu border-radius fix."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ANNUAL_CSS_MARKER = "/* Annual: sales entry via cockpit Sales Data — not TW Global Menu Edit */"
ANNUAL_HTML_MARKER = '<nav class="annual-daily-focus-global-menu"'
ANNUAL_JS_MARKER = "var btnEdit = document.getElementById('annual-daily-focus-edit-btn');"

MONTHLY_VAR_ANCHOR = "      --monthly-vfocus-profit-raise: 1px;"
MONTHLY_MARGIN_ANCHOR = "      margin: 80px calc((100% - 1100px) / 2) 0;"
MONTHLY_DATE_TOP_ANCHOR = "      --monthly-vfocus-date-top-in-tw: 12px;"
MONTHLY_TOP_CTRL_ANCHOR = "      height: 39px;"
MONTHLY_FILL_TOP_ANCHOR = "      top: 39px;"
MONTHLY_STACK_MARGIN_ANCHOR = (
    "      margin-top: calc(var(--monthly-vfocus-date-top-in-tw) - var(--monthly-vfocus-bar-top) - 39px);"
)

MONTHLY_TOP_CTRL_CSS_END = "    .monthly-vfocus-today-btn:focus-visible {\n      outline: none;\n    }"

MONTHLY_HTML_OLD = """            <div class="monthly-vfocus-top-controls" aria-label="フォーカスバー操作">
              <button
                type="button"
                class="monthly-vfocus-today-btn"
                id="monthly-vfocus-today-btn"
                aria-label="本日の列へ移動"
              >
                <span class="monthly-vfocus-graph-btn__inner">今日</span>
              </button>
              <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-prev-day" aria-label="前の日">◀</button>
              <button type="button" class="monthly-vfocus-top-edit" id="monthly-vfocus-edit" aria-label="編集">編集</button>
              <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-next-day" aria-label="次の日">▶</button>
              <button"""

MONTHLY_HTML_NEW = """            <div class="monthly-vfocus-top-controls" aria-label="フォーカスバー操作">
              <button
                type="button"
                class="monthly-vfocus-today-btn"
                id="monthly-vfocus-today-btn"
                aria-label="本日の列へ移動"
              >
                <span class="monthly-vfocus-graph-btn__inner">今日</span>
              </button>
              <div class="monthly-vfocus-top-edit-row">
                <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-prev-day" aria-label="前の日">◀</button>
                <button type="button" class="monthly-vfocus-top-edit" id="monthly-vfocus-edit" aria-label="編集">編集</button>
                <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-next-day" aria-label="次の日">▶</button>
              </div>
              <span class="monthly-vfocus-year-cell" id="monthly-vfocus-year" aria-label="表示年">2026</span>
              <button"""

MONTHLY_HTML_OLD_EN = """            <div class="monthly-vfocus-top-controls" aria-label="Focus Bar controls">
              <button
                type="button"
                class="monthly-vfocus-today-btn"
                id="monthly-vfocus-today-btn"
                aria-label="Go to today’s column"
              >
                <span class="monthly-vfocus-graph-btn__inner">Today</span>
              </button>
              <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-prev-day" aria-label="Previous day">◀</button>
              <button type="button" class="monthly-vfocus-top-edit" id="monthly-vfocus-edit" aria-label="Edit">Edit</button>
              <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-next-day" aria-label="Next day">▶</button>
              <button"""

MONTHLY_HTML_NEW_EN = """            <div class="monthly-vfocus-top-controls" aria-label="Focus Bar controls">
              <button
                type="button"
                class="monthly-vfocus-today-btn"
                id="monthly-vfocus-today-btn"
                aria-label="Go to today’s column"
              >
                <span class="monthly-vfocus-graph-btn__inner">Today</span>
              </button>
              <div class="monthly-vfocus-top-edit-row">
                <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-prev-day" aria-label="Previous day">◀</button>
                <button type="button" class="monthly-vfocus-top-edit" id="monthly-vfocus-edit" aria-label="Edit">Edit</button>
                <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-next-day" aria-label="Next day">▶</button>
              </div>
              <span class="monthly-vfocus-year-cell" id="monthly-vfocus-year" aria-label="Display year">2026</span>
              <button"""

MONTHLY_TOP_EXTRA_CSS = """
    .monthly-vfocus-top-edit-row {
      position: absolute;
      left: 50%;
      top: 14px;
      transform: translateX(-50%);
      height: var(--monthly-vfocus-tab-h);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      z-index: 4;
      pointer-events: auto;
    }
    .monthly-vfocus-year-cell {
      position: absolute;
      left: 50%;
      top: calc(14px + var(--monthly-vfocus-tab-h));
      transform: translateX(-50%);
      width: var(--monthly-vfocus-col-w);
      height: var(--monthly-vfocus-year-row-h);
      box-sizing: border-box;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0;
      padding: 0;
      border: 1px solid #58e1f3;
      border-top: 0;
      border-radius: 0;
      background: transparent;
      color: #58e1f3;
      font-family: 'Orbitron', sans-serif;
      font-size: 14px;
      font-weight: 700;
      line-height: 1;
      letter-spacing: 0.02em;
      pointer-events: none;
      user-select: none;
      z-index: 3;
    }
    html[lang='ja'] .monthly-vfocus-year-cell {
      font-family: 'BIZ UDPGothic', sans-serif;
      font-size: 13px;
    }
    .office-mode .monthly-vfocus-year-cell {
      border-color: #000;
      color: #111;
      font-family: 'BIZ UDPGothic', sans-serif;
    }
"""

ANNUAL_TW_YEAR_CSS = """
    .annual-daily-focus-tw-year {
      position: absolute;
      left: 14px;
      top: 50%;
      min-width: 54px;
      height: 22px;
      transform: translateY(-50%);
      z-index: 12;
      display: flex;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
      color: #58e1f3;
      font-family: 'Orbitron', sans-serif;
      font-size: 11px;
      font-weight: 400;
      line-height: 1;
      letter-spacing: 0.02em;
      pointer-events: none;
      user-select: none;
      background: #2a2a2a;
    }
    html[lang="ja"] .annual-daily-focus-tw-year {
      font-family: 'BIZ UDPGothic', sans-serif;
    }
    body.annual-focus-bar-expanded .annual-daily-focus-tw-year {
      top: 0;
      height: 100%;
      transform: none;
      align-items: center;
    }
    body.annual-focus-bar-expanded:not(.office-mode) .annual-daily-focus-tw-year::after {
      content: "";
      position: absolute;
      left: 100%;
      top: 0;
      bottom: 0;
      width: var(--annual-global-menu-date-overhang);
      background: #2a2a2a;
      pointer-events: none;
    }
    .office-mode .annual-daily-focus-tw-year {
      background: #e8e8e8;
      color: #000;
      font-family: 'BIZ UDPGothic', sans-serif;
    }
    body.annual-focus-bar-expanded.office-mode .annual-daily-focus-tw-year::after {
      content: "";
      position: absolute;
      left: calc(100% + 1px);
      top: 0;
      bottom: 0;
      width: max(0px, calc(var(--annual-daily-focus-table-pad-left) - 14px - 100% - 1px));
      background: #e8e8e8;
      pointer-events: none;
    }
"""

ANNUAL_BEFORE_MASK = """    body.annual-focus-bar-expanded .annual-daily-focus-global-menu::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: var(--annual-date-left-mask-w);
      background: #2a2a2a;
      z-index: 10;
      pointer-events: none;
    }"""

ANNUAL_AFTER_MASK = """    body.annual-focus-bar-expanded .annual-daily-focus-global-menu::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: var(--annual-date-left-mask-w);
      background: #2a2a2a;
      border-top-left-radius: 13px;
      z-index: 10;
      pointer-events: none;
    }"""

ANNUAL_OFFICE_MASK_BEFORE = """    .office-mode.annual-focus-bar-expanded .annual-daily-focus-global-menu::before {
      background: #e8e8e8;
      width: calc(var(--annual-date-left-mask-w) + 1px);
    }"""

ANNUAL_OFFICE_MASK_AFTER = """    .office-mode.annual-focus-bar-expanded .annual-daily-focus-global-menu::before {
      background: #e8e8e8;
      width: calc(var(--annual-date-left-mask-w) + 1px);
      border-top-left-radius: 13px;
    }"""

ANNUAL_HTML_INSERT_BEFORE = """            <button type="button" class="annual-daily-focus-edit-btn" id="annual-daily-focus-edit-btn\""""

ANNUAL_HTML_INSERT = """            <span class="annual-daily-focus-tw-year" id="annual-daily-focus-tw-year" aria-label="表示年">2026</span>
            <button type="button" class="annual-daily-focus-edit-btn" id="annual-daily-focus-edit-btn\""""

ANNUAL_HTML_INSERT_EN = """            <span class="annual-daily-focus-tw-year" id="annual-daily-focus-tw-year" aria-label="Display year">2026</span>
            <button type="button" class="annual-daily-focus-edit-btn" id="annual-daily-focus-edit-btn\""""

ANNUAL_JS_SNIPPET = """
      (function () {
        var twYearEl = document.getElementById('annual-daily-focus-tw-year');
        if (!twYearEl) return;
        function syncTwYearBadge(y) {
          if (y == null || !isFinite(Number(y))) {
            y = window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear;
          }
          if (y == null || !isFinite(Number(y))) return;
          twYearEl.textContent = String(Number(y));
        }
        syncTwYearBadge();
        document.addEventListener('annual:calendarYearChanged', function (ev) {
          syncTwYearBadge(ev && ev.detail ? ev.detail.year : null);
        });
      })();
"""

MONTHLY_JS_SNIPPET = """
      function syncMonthlyVfocusYearBadge(iso) {
        var el = document.getElementById('monthly-vfocus-year');
        if (!el) return;
        var m = /^(\d{4})-/.exec(String(iso || ''));
        if (m) {
          el.textContent = m[1];
          return;
        }
        if (typeof state !== 'undefined' && state && Number.isFinite(state.year)) {
          el.textContent = String(state.year);
        }
      }
"""

MONTHLY_JS_SYNC_CALL = """          var isoNow = hdr.getAttribute('data-iso');
          if (isoNow) syncArea2ByIso(isoNow);"""

MONTHLY_JS_SYNC_CALL_NEW = """          var isoNow = hdr.getAttribute('data-iso');
          if (isoNow) {
            syncArea2ByIso(isoNow);
            syncMonthlyVfocusYearBadge(isoNow);
          }"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise ValueError(f"{label}: anchor not found")
    return text.replace(old, new, 1)


def apply_annual(path: Path, lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    if "annual-daily-focus-tw-year" in text:
        print(f"skip annual (already applied): {path}")
        return

    text = replace_once(text, ANNUAL_CSS_MARKER, ANNUAL_TW_YEAR_CSS + ANNUAL_CSS_MARKER, str(path))
    text = replace_once(text, ANNUAL_BEFORE_MASK, ANNUAL_AFTER_MASK, str(path))
    if ANNUAL_OFFICE_MASK_BEFORE in text:
        text = replace_once(text, ANNUAL_OFFICE_MASK_BEFORE, ANNUAL_OFFICE_MASK_AFTER, str(path))

    insert = ANNUAL_HTML_INSERT_EN if lang == "en" else ANNUAL_HTML_INSERT
    text = replace_once(text, ANNUAL_HTML_INSERT_BEFORE, insert, str(path))
    text = replace_once(text, ANNUAL_JS_MARKER, ANNUAL_JS_SNIPPET + ANNUAL_JS_MARKER, str(path))

    path.write_text(text, encoding="utf-8")
    print(f"applied annual: {path}")


def apply_monthly(path: Path, lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    if "monthly-vfocus-year-cell" in text:
        print(f"skip monthly (already applied): {path}")
        return

    text = replace_once(
        text,
        MONTHLY_VAR_ANCHOR,
        MONTHLY_VAR_ANCHOR
        + "\n      --monthly-vfocus-tab-h: 28px;\n"
        + "      --monthly-vfocus-year-row-h: 28px;\n"
        + "      --monthly-vfocus-top-header-h: calc(14px + var(--monthly-vfocus-tab-h) + var(--monthly-vfocus-year-row-h));\n"
        + "      --monthly-cockpit-tw-gap-boost: var(--monthly-vfocus-tab-h);",
        str(path),
    )
    text = replace_once(
        text,
        MONTHLY_MARGIN_ANCHOR,
        "      margin: calc(80px + var(--monthly-cockpit-tw-gap-boost)) calc((100% - 1100px) / 2) 0;",
        str(path),
    )
    text = replace_once(text, MONTHLY_DATE_TOP_ANCHOR, "      --monthly-vfocus-date-top-in-tw: 40px;", str(path))
    text = text.replace(MONTHLY_TOP_CTRL_ANCHOR, "      height: var(--monthly-vfocus-top-header-h);", 1)
    text = text.replace(MONTHLY_FILL_TOP_ANCHOR, "      top: var(--monthly-vfocus-top-header-h);", 1)
    text = replace_once(
        text,
        MONTHLY_STACK_MARGIN_ANCHOR,
        "      margin-top: calc(var(--monthly-vfocus-date-top-in-tw) - var(--monthly-vfocus-bar-top) - var(--monthly-vfocus-top-header-h));",
        str(path),
    )
    text = replace_once(text, MONTHLY_TOP_CTRL_CSS_END, MONTHLY_TOP_CTRL_CSS_END + MONTHLY_TOP_EXTRA_CSS, str(path))

    html_old = MONTHLY_HTML_OLD_EN if lang == "en" else MONTHLY_HTML_OLD
    html_new = MONTHLY_HTML_NEW_EN if lang == "en" else MONTHLY_HTML_NEW
    text = replace_once(text, html_old, html_new, str(path))

    # monthly JS: helper near vfocus block
    anchor = "      function setFocusBarDateFromHeader(dateEl, hdrLane) {"
    if MONTHLY_JS_SNIPPET.strip() not in text:
        text = replace_once(text, anchor, MONTHLY_JS_SNIPPET + anchor, str(path))
    text = replace_once(text, MONTHLY_JS_SYNC_CALL, MONTHLY_JS_SYNC_CALL_NEW, str(path))

    path.write_text(text, encoding="utf-8")
    print(f"applied monthly: {path}")


def main() -> int:
    apply_annual(ROOT / "app/annual/index.html", "ja")
    apply_annual(ROOT / "en/app/annual/index.html", "en")
    apply_monthly(ROOT / "app/monthly/index.html", "ja")
    apply_monthly(ROOT / "en/app/monthly/index.html", "en")
    return 0


if __name__ == "__main__":
    sys.exit(main())

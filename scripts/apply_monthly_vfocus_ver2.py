#!/usr/bin/env python3
"""Monthly Focus Bar: switch to vertical_focus_bar_*_ver2.svg (+28px year row)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "/* KPI-VFOCUS-VER2 */"

VAR_BLOCK_OLD = """      --monthly-vfocus-bar-top: -42px;
      --monthly-vfocus-date-top-in-tw: 12px;"""

VAR_BLOCK_NEW = f"""      {MARKER}
      --monthly-vfocus-ver2-offset: 28px;
      --monthly-vfocus-edit-header-h: 39px;
      --monthly-vfocus-year-row-h: 28px;
      --monthly-vfocus-header-h: calc(
        var(--monthly-vfocus-edit-header-h) + var(--monthly-vfocus-year-row-h)
      );
      --monthly-vfocus-fill-top: var(--monthly-vfocus-header-h);
      --monthly-vfocus-frame-h: 1103px;
      --monthly-vfocus-bar-top: calc(-42px - var(--monthly-vfocus-ver2-offset));
      --monthly-vfocus-date-top-in-tw: 12px;"""

TW_MARGIN_OLD = "      margin: 80px calc((100% - 1100px) / 2) 0;"
TW_MARGIN_NEW = """      margin: calc(80px + var(--monthly-vfocus-ver2-offset)) calc((100% - 1100px) / 2) 0;"""

TW_MIN_H_OLD = "      min-height: 1070px;"
TW_MIN_H_NEW = "      min-height: calc(1070px + var(--monthly-vfocus-ver2-offset));"

VF_BAR_H_OLD = "      height: 1075px;"
VF_BAR_H_NEW = "      height: var(--monthly-vfocus-frame-h);"

VF_COMMENT_OLD = "    /* SVG vertical_focus_bar.svg の内側ダーク領域（rect y=39 h=860）に合わせる */"
VF_COMMENT_NEW = "    /* SVG vertical_focus_bar_ver2.svg: Edit y=0-39, Year y=39-67, dark rect y=66 */"

TOP_CTRL_H_OLD = """      top: 0;
      height: 39px;"""
TOP_CTRL_H_NEW = """      top: 0;
      height: var(--monthly-vfocus-header-h);"""

GRAPH_TOP_OLD = "      top: 14px;"
GRAPH_TOP_NEW = "      top: var(--monthly-vfocus-edit-header-h);"

FILL_TOP_OLD = "      top: 39px;"
FILL_TOP_NEW = "      top: var(--monthly-vfocus-fill-top);"

STACK_MARGIN_OLD = (
    "      margin-top: calc(var(--monthly-vfocus-date-top-in-tw) - var(--monthly-vfocus-bar-top) - 39px);"
)
STACK_MARGIN_NEW = (
    "      margin-top: calc(var(--monthly-vfocus-date-top-in-tw) - var(--monthly-vfocus-bar-top) - var(--monthly-vfocus-fill-top));"
)

SVG_SCI_FI_OLD = '              src="../../images/vertical_focus_bar.svg"'
SVG_SCI_FI_NEW = '              src="../../images/vertical_focus_bar_ver2.svg"'
SVG_OFFICE_OLD = '              src="../../images/vertical_focus_bar_office.svg"'
SVG_OFFICE_NEW = '              src="../../images/vertical_focus_bar_office_ver2.svg"'

SVG_SCI_FI_OLD_EN = '              src="../../../images/vertical_focus_bar.svg"'
SVG_SCI_FI_NEW_EN = '              src="../../../images/vertical_focus_bar_ver2.svg"'
SVG_OFFICE_OLD_EN = '              src="../../../images/vertical_focus_bar_office.svg"'
SVG_OFFICE_NEW_EN = '              src="../../../images/vertical_focus_bar_office_ver2.svg"'

EXTRA_CSS = f"""
    {MARKER}
    .monthly-vfocus-edit-row {{
      position: absolute;
      left: 0;
      right: 0;
      top: 0;
      height: var(--monthly-vfocus-edit-header-h);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      z-index: 4;
      pointer-events: auto;
    }}
    .monthly-vfocus-year-cell {{
      position: absolute;
      left: 50%;
      top: var(--monthly-vfocus-edit-header-h);
      transform: translateX(-50%);
      width: var(--monthly-vfocus-col-w);
      height: var(--monthly-vfocus-year-row-h);
      box-sizing: border-box;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0;
      padding: 0;
      border: 0;
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
    }}
    html[lang='ja'] .monthly-vfocus-year-cell {{
      font-family: 'BIZ UDPGothic', sans-serif;
      font-size: 13px;
    }}
    .office-mode .monthly-vfocus-year-cell {{
      color: #111;
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
"""

CSS_ANCHOR = "    .monthly-vfocus-today-btn:focus-visible {\n      outline: none;\n    }"

HTML_JA_OLD = """              <button
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

HTML_JA_NEW = """              <div class="monthly-vfocus-edit-row">
                <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-prev-day" aria-label="前の日">◀</button>
                <button type="button" class="monthly-vfocus-top-edit" id="monthly-vfocus-edit" aria-label="編集">編集</button>
                <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-next-day" aria-label="次の日">▶</button>
              </div>
              <button
                type="button"
                class="monthly-vfocus-today-btn"
                id="monthly-vfocus-today-btn"
                aria-label="本日の列へ移動"
              >
                <span class="monthly-vfocus-graph-btn__inner">今日</span>
              </button>
              <span class="monthly-vfocus-year-cell" id="monthly-vfocus-year" aria-label="表示年">2026</span>
              <button"""

HTML_EN_OLD = """              <button
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

HTML_EN_NEW = """              <div class="monthly-vfocus-edit-row">
                <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-prev-day" aria-label="Previous day">◀</button>
                <button type="button" class="monthly-vfocus-top-edit" id="monthly-vfocus-edit" aria-label="Edit">Edit</button>
                <button type="button" class="monthly-vfocus-top-btn" id="monthly-vfocus-next-day" aria-label="Next day">▶</button>
              </div>
              <button
                type="button"
                class="monthly-vfocus-today-btn"
                id="monthly-vfocus-today-btn"
                aria-label="Go to today’s column"
              >
                <span class="monthly-vfocus-graph-btn__inner">Today</span>
              </button>
              <span class="monthly-vfocus-year-cell" id="monthly-vfocus-year" aria-label="Display year">2026</span>
              <button"""

JS_HELPER = """
      /* KPI-VFOCUS-VER2 */
      function syncMonthlyVfocusYearBadge(isoOrYear) {
        var el = document.getElementById('monthly-vfocus-year');
        if (!el) return;
        if (isoOrYear === '' || (typeof isoOrYear === 'number' && !Number.isFinite(isoOrYear))) {
          el.textContent = '';
          return;
        }
        if (typeof isoOrYear === 'number' && Number.isFinite(isoOrYear)) {
          el.textContent = String(isoOrYear);
          return;
        }
        var m = /^(\\d{4})/.exec(String(isoOrYear || ''));
        if (m) {
          el.textContent = m[1];
          return;
        }
        if (typeof state !== 'undefined' && state && Number.isFinite(state.year)) {
          el.textContent = String(state.year);
        }
      }
"""

JS_ANCHOR = "      function setFocusBarDateFromHeader(dateEl, hdrLane) {"

JS_SYNC_OLD = """          var isoNow = hdr.getAttribute('data-iso');
          if (isoNow) syncArea2ByIso(isoNow);"""

JS_SYNC_NEW = """          var isoNow = hdr.getAttribute('data-iso');
          if (isoNow) {
            syncArea2ByIso(isoNow);
            syncMonthlyVfocusYearBadge(isoNow);
          }"""

JS_SYNC_YEAR_OLD = """      function syncYearUi(y) {
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setCalendarYear === 'function') {
          window.__ANNUAL_UI.setCalendarYear(y);
        }
      }"""

JS_SYNC_YEAR_NEW = """      function syncYearUi(y) {
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setCalendarYear === 'function') {
          window.__ANNUAL_UI.setCalendarYear(y);
        }
        syncMonthlyVfocusYearBadge(Number(y));
      }"""

JS_CLEAR_YEAR = """        if (n === 0) {
          syncMonthlyVfocusYearBadge(NaN);
          for (var le = 0; le < 3; le++) {"""

JS_CLEAR_YEAR_OLD = """        if (n === 0) {
          for (var le = 0; le < 3; le++) {"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise ValueError(f"{label}: anchor not found")
    return text.replace(old, new, 1)


def apply(path: Path, lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already applied): {path}")
        return

    text = replace_once(text, VAR_BLOCK_OLD, VAR_BLOCK_NEW, str(path))
    text = replace_once(text, TW_MARGIN_OLD, TW_MARGIN_NEW, str(path))
    text = replace_once(text, TW_MIN_H_OLD, TW_MIN_H_NEW, str(path))
    text = replace_once(text, VF_BAR_H_OLD, VF_BAR_H_NEW, str(path))
    if VF_COMMENT_OLD in text:
        text = replace_once(text, VF_COMMENT_OLD, VF_COMMENT_NEW, str(path))
    text = replace_once(text, TOP_CTRL_H_OLD, TOP_CTRL_H_NEW, str(path))
    # Today and Graph both use top: 14px — replace only within vfocus button blocks
    text = text.replace(
        """    .monthly-vfocus-graph-btn {
      position: absolute;
      left: 100%;
      transform: translateX(0.3px);
      top: 14px;""",
        """    .monthly-vfocus-graph-btn {
      position: absolute;
      left: 100%;
      transform: translateX(0.3px);
      top: var(--monthly-vfocus-edit-header-h);""",
        1,
    )
    text = text.replace(
        """    .monthly-vfocus-today-btn {
      position: absolute;
      right: 100%;
      left: auto;
      transform: translateX(-0.3px);
      top: 14px;""",
        """    .monthly-vfocus-today-btn {
      position: absolute;
      right: 100%;
      left: auto;
      transform: translateX(-0.3px);
      top: var(--monthly-vfocus-edit-header-h);""",
        1,
    )
    text = replace_once(text, FILL_TOP_OLD, FILL_TOP_NEW, str(path))
    text = replace_once(text, STACK_MARGIN_OLD, STACK_MARGIN_NEW, str(path))
    text = replace_once(text, CSS_ANCHOR, CSS_ANCHOR + EXTRA_CSS, str(path))

    if lang == "en":
        text = replace_once(text, SVG_SCI_FI_OLD_EN, SVG_SCI_FI_NEW_EN, str(path))
        text = replace_once(text, SVG_OFFICE_OLD_EN, SVG_OFFICE_NEW_EN, str(path))
        text = replace_once(text, HTML_EN_OLD, HTML_EN_NEW, str(path))
    else:
        text = replace_once(text, SVG_SCI_FI_OLD, SVG_SCI_FI_NEW, str(path))
        text = replace_once(text, SVG_OFFICE_OLD, SVG_OFFICE_NEW, str(path))
        text = replace_once(text, HTML_JA_OLD, HTML_JA_NEW, str(path))

    text = replace_once(text, JS_ANCHOR, JS_HELPER + JS_ANCHOR, str(path))
    text = replace_once(text, JS_SYNC_OLD, JS_SYNC_NEW, str(path))
    text = replace_once(text, JS_SYNC_YEAR_OLD, JS_SYNC_YEAR_NEW, str(path))
    text = replace_once(text, JS_CLEAR_YEAR_OLD, JS_CLEAR_YEAR, str(path))

    path.write_text(text, encoding="utf-8")
    print(f"applied: {path}")


def main() -> int:
    apply(ROOT / "app/monthly/index.html", "ja")
    apply(ROOT / "en/app/monthly/index.html", "en")
    return 0


if __name__ == "__main__":
    sys.exit(main())

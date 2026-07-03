#!/usr/bin/env python3
"""Split Year/Month into separate ym grid cells (center each cell independently)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

PS_YM_GRID_OLD = """    .past-sales-modal__ym {
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 649fr);"""

PS_YM_GRID_NEW = """    .past-sales-modal__ym {
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 324.5fr) minmax(0, 324.5fr);"""

SDM_YM_GRID_OLD = """    .sales-data-modal__ym {
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 649fr);"""

SDM_YM_GRID_NEW = """    .sales-data-modal__ym {
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 324.5fr) minmax(0, 324.5fr);"""

PS_NAV_SPLIT_CSS_OLD = """    .past-sales-modal__ym-cell--nav-split {
      display: grid;
      grid-template-columns: 1fr 1fr;
      padding: 0;
      gap: 0;
    }
    .past-sales-modal__ym-nav-group {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      max-width: 100%;
      white-space: nowrap;
    }
    .past-sales-modal__ym-nav-label {
      flex-shrink: 0;
    }
    .past-sales-modal__ym-nav {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;
      min-width: 0;
      height: 100%;
      box-sizing: border-box;
      border-right: 1px solid var(--psm-line);
    }
    .past-sales-modal__ym-nav--month {
      border-right: 0;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-nav--month {
      display: none;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-cell--nav-split {
      grid-template-columns: 1fr;
    }"""

PS_NAV_SPLIT_CSS_NEW = """    .past-sales-modal__ym-nav-group {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      max-width: 100%;
      white-space: nowrap;
    }
    .past-sales-modal__ym-nav-label {
      flex-shrink: 0;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-cell--month-nav {
      display: none;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym {
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 649fr);
    }"""

SDM_NAV_SPLIT_CSS_OLD = """    .sales-data-modal__ym-cell--nav-split {
      display: grid;
      grid-template-columns: 1fr 1fr;
      padding: 0;
      gap: 0;
    }
    .sales-data-modal__ym-nav-group {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      max-width: 100%;
      white-space: nowrap;
    }
    .sales-data-modal__ym-nav-label {
      flex-shrink: 0;
    }
    .sales-data-modal__ym-nav-value {
      text-decoration: underline;
      font-variant-numeric: tabular-nums;
    }
    .sales-data-modal__ym-arrow-decor {
      opacity: 0.9;
      user-select: none;
      pointer-events: none;
    }
    .sales-data-modal__ym-nav {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;
      min-width: 0;
      height: 100%;
      box-sizing: border-box;
      border-right: 1px solid var(--sdm-line);
    }
    .sales-data-modal__ym-nav--month {
      border-right: 0;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-nav--month {
      display: none;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-cell--nav-split {
      grid-template-columns: 1fr;
    }"""

SDM_NAV_SPLIT_CSS_NEW = """    .sales-data-modal__ym-nav-group {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      max-width: 100%;
      white-space: nowrap;
    }
    .sales-data-modal__ym-nav-label {
      flex-shrink: 0;
    }
    .sales-data-modal__ym-nav-value {
      text-decoration: underline;
      font-variant-numeric: tabular-nums;
    }
    .sales-data-modal__ym-arrow-decor {
      opacity: 0.9;
      user-select: none;
      pointer-events: none;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-cell--month-nav {
      display: none;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym {
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 649fr);
    }"""

PS_NAV_HTML_JA_OLD = """          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--nav-split">
            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--annual">
              <div class="past-sales-modal__ym-nav-group">
                <span class="past-sales-modal__ym-nav-label">年</span>
                <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="前年">
                  ◀︎
                </button>
                <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="年"></select>
                <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="翌年">
                  ▶︎
                </button>
              </div>
            </div>
            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--month">
              <div class="past-sales-modal__ym-nav-group">
                <span class="past-sales-modal__ym-nav-label">月</span>
                <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="前月">
                  ◀︎
                </button>
                <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="月"></select>
                <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="翌月">
                  ▶︎
                </button>
              </div>
            </div>
          </div>"""

PS_NAV_HTML_JA_NEW = """          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--year-nav">
            <div class="past-sales-modal__ym-nav-group">
              <span class="past-sales-modal__ym-nav-label">年</span>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="前年">
                ◀︎
              </button>
              <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="年"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="翌年">
                ▶︎
              </button>
            </div>
          </div>
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--month-nav">
            <div class="past-sales-modal__ym-nav-group">
              <span class="past-sales-modal__ym-nav-label">月</span>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="前月">
                ◀︎
              </button>
              <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="月"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="翌月">
                ▶︎
              </button>
            </div>
          </div>"""

PS_NAV_HTML_EN_OLD = """          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--nav-split">
            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--annual">
              <div class="past-sales-modal__ym-nav-group">
                <span class="past-sales-modal__ym-nav-label">Year</span>
                <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="Previous year">
                  ◀︎
                </button>
                <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="Year"></select>
                <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="Next year">
                  ▶︎
                </button>
              </div>
            </div>
            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--month">
              <div class="past-sales-modal__ym-nav-group">
                <span class="past-sales-modal__ym-nav-label">Month</span>
                <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="Previous month">
                  ◀︎
                </button>
                <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="Month"></select>
                <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="Next month">
                  ▶︎
                </button>
              </div>
            </div>
          </div>"""

PS_NAV_HTML_EN_NEW = """          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--year-nav">
            <div class="past-sales-modal__ym-nav-group">
              <span class="past-sales-modal__ym-nav-label">Year</span>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="Previous year">
                ◀︎
              </button>
              <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="Year"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="Next year">
                ▶︎
              </button>
            </div>
          </div>
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--month-nav">
            <div class="past-sales-modal__ym-nav-group">
              <span class="past-sales-modal__ym-nav-label">Month</span>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="Previous month">
                ◀︎
              </button>
              <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="Month"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="Next month">
                ▶︎
              </button>
            </div>
          </div>"""

SDM_NAV_HTML_JA_OLD = """          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--nav-split">
            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--annual" aria-live="polite">
              <div class="sales-data-modal__ym-nav-group">
                <span class="sales-data-modal__ym-nav-label">年</span>
                <span class="sales-data-modal__ym-arrow-decor" aria-hidden="true">◀︎</span>
                <span id="sales-data-year-label" class="sales-data-modal__ym-nav-value">—</span>
                <span class="sales-data-modal__ym-arrow-decor" aria-hidden="true">▶︎</span>
              </div>
            </div>
            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--month">
              <div class="sales-data-modal__ym-nav-group">
                <span class="sales-data-modal__ym-nav-label">月</span>
                <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="前月">
                  ◀︎
                </button>
                <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="月"></select>
                <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="翌月">
                  ▶︎
                </button>
              </div>
            </div>
          </div>"""

SDM_NAV_HTML_JA_NEW = """          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-nav" aria-live="polite">
            <span id="sales-data-year-label" class="sales-data-modal__ym-year-label">—</span>
          </div>
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--month-nav">
            <div class="sales-data-modal__ym-nav-group">
              <span class="sales-data-modal__ym-nav-label">月</span>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="前月">
                ◀︎
              </button>
              <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="月"></select>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="翌月">
                ▶︎
              </button>
            </div>
          </div>"""

SDM_NAV_HTML_EN_OLD = """          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--nav-split">
            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--annual" aria-live="polite">
              <div class="sales-data-modal__ym-nav-group">
                <span class="sales-data-modal__ym-nav-label">Year</span>
                <span class="sales-data-modal__ym-arrow-decor" aria-hidden="true">◀︎</span>
                <span id="sales-data-year-label" class="sales-data-modal__ym-nav-value">—</span>
                <span class="sales-data-modal__ym-arrow-decor" aria-hidden="true">▶︎</span>
              </div>
            </div>
            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--month">
              <div class="sales-data-modal__ym-nav-group">
                <span class="sales-data-modal__ym-nav-label">Month</span>
                <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="Previous month">
                  ◀︎
                </button>
                <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="Month"></select>
                <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="Next month">
                  ▶︎
                </button>
              </div>
            </div>
          </div>"""
SDM_NAV_HTML_EN_NEW = """          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-nav" aria-live="polite">
            <span id="sales-data-year-label" class="sales-data-modal__ym-year-label">—</span>
          </div>
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--month-nav">
            <div class="sales-data-modal__ym-nav-group">
              <span class="sales-data-modal__ym-nav-label">Month</span>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="Previous month">
                ◀︎
              </button>
              <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="Month"></select>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="Next month">
                ▶︎
              </button>
            </div>
          </div>"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "en/app/annual" not in str(path).replace("\\", "/")

    for old, new in (
        (PS_YM_GRID_OLD, PS_YM_GRID_NEW),
        (SDM_YM_GRID_OLD, SDM_YM_GRID_NEW),
        (PS_NAV_SPLIT_CSS_OLD, PS_NAV_SPLIT_CSS_NEW),
        (SDM_NAV_SPLIT_CSS_OLD, SDM_NAV_SPLIT_CSS_NEW),
    ):
        if old in text:
            text = text.replace(old, new, 1)

    ps_html_old = PS_NAV_HTML_JA_OLD if is_ja else PS_NAV_HTML_EN_OLD
    ps_html_new = PS_NAV_HTML_JA_NEW if is_ja else PS_NAV_HTML_EN_NEW
    if ps_html_old in text:
        text = text.replace(ps_html_old, ps_html_new, 1)
    elif "ym-cell--year-nav" not in text:
        raise SystemExit(f"past-sales nav html not found in {path}")

    sdm_html_old = SDM_NAV_HTML_JA_OLD if is_ja else SDM_NAV_HTML_EN_OLD
    sdm_html_new = SDM_NAV_HTML_JA_NEW if is_ja else SDM_NAV_HTML_EN_NEW
    if sdm_html_old in text:
        text = text.replace(sdm_html_old, sdm_html_new, 1)
    elif "sales-data-modal__ym-cell--year-nav" not in text:
        raise SystemExit(f"sales-data nav html not found in {path}")

    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

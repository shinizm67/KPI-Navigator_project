#!/usr/bin/env python3
"""Year/Month nav labels + centered groups in Sales Data / Past Sales ym row."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

NAV_GROUP_CSS_PSM = """
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
    }"""

NAV_GROUP_CSS_SDM = """
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
    }"""

PS_ANNUAL_JA_OLD = """            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--annual">
              <label class="past-sales-modal__sr-only" for="past-sales-year-select">年</label>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="前年">
                ◀︎
              </button>
              <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="年"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="翌年">
                ▶︎
              </button>
            </div>"""

PS_ANNUAL_JA_NEW = """            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--annual">
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
            </div>"""

PS_MONTH_JA_OLD = """            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--month">
              <label class="past-sales-modal__sr-only" for="past-sales-month-select">月</label>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="前月">
                ◀︎
              </button>
              <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="月"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="翌月">
                ▶︎
              </button>
            </div>"""

PS_MONTH_JA_NEW = """            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--month">
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

PS_ANNUAL_EN_OLD = """            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--annual">
              <label class="past-sales-modal__sr-only" for="past-sales-year-select">Year</label>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="Previous year">
                ◀︎
              </button>
              <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="Year"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="Next year">
                ▶︎
              </button>
            </div>"""

PS_ANNUAL_EN_NEW = """            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--annual">
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
            </div>"""

PS_MONTH_EN_OLD = """            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--month">
              <label class="past-sales-modal__sr-only" for="past-sales-month-select">Month</label>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="Previous month">
                ◀︎
              </button>
              <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="Month"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="Next month">
                ▶︎
              </button>
            </div>"""

PS_MONTH_EN_NEW = """            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--month">
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

SDM_ANNUAL_JA_OLD = """            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--annual" aria-live="polite">
              <span id="sales-data-year-label" class="sales-data-modal__ym-year-label"></span>
            </div>"""

SDM_ANNUAL_JA_NEW = """            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--annual" aria-live="polite">
              <div class="sales-data-modal__ym-nav-group">
                <span class="sales-data-modal__ym-nav-label">年</span>
                <span class="sales-data-modal__ym-arrow-decor" aria-hidden="true">◀︎</span>
                <span id="sales-data-year-label" class="sales-data-modal__ym-nav-value">—</span>
                <span class="sales-data-modal__ym-arrow-decor" aria-hidden="true">▶︎</span>
              </div>
            </div>"""

SDM_MONTH_JA_OLD = """            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--month">
              <label class="sales-data-modal__sr-only" for="sales-data-month-select">月</label>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="前月">
                ◀︎
              </button>
              <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="月"></select>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="翌月">
                ▶︎
              </button>
            </div>"""

SDM_MONTH_JA_NEW = """            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--month">
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

SDM_ANNUAL_EN_OLD = SDM_ANNUAL_JA_OLD
SDM_ANNUAL_EN_NEW = """            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--annual" aria-live="polite">
              <div class="sales-data-modal__ym-nav-group">
                <span class="sales-data-modal__ym-nav-label">Year</span>
                <span class="sales-data-modal__ym-arrow-decor" aria-hidden="true">◀︎</span>
                <span id="sales-data-year-label" class="sales-data-modal__ym-nav-value">—</span>
                <span class="sales-data-modal__ym-arrow-decor" aria-hidden="true">▶︎</span>
              </div>
            </div>"""

SDM_MONTH_EN_OLD = """            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--month">
              <label class="sales-data-modal__sr-only" for="sales-data-month-select">Month</label>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="Previous month">
                ◀︎
              </button>
              <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="Month"></select>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="Next month">
                ▶︎
              </button>
            </div>"""

SDM_MONTH_EN_NEW = """            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--month">
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

SYNC_YEAR_LABEL_OLD = """        el.textContent = isJa ? String(y) + '年' : String(y);"""
SYNC_YEAR_LABEL_NEW = """        el.textContent = String(y);"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "en/app/annual" not in str(path).replace("\\", "/")

    if is_ja:
        pairs = (
            (PS_ANNUAL_JA_OLD, PS_ANNUAL_JA_NEW),
            (PS_MONTH_JA_OLD, PS_MONTH_JA_NEW),
            (SDM_ANNUAL_JA_OLD, SDM_ANNUAL_JA_NEW),
            (SDM_MONTH_JA_OLD, SDM_MONTH_JA_NEW),
        )
    else:
        pairs = (
            (PS_ANNUAL_EN_OLD, PS_ANNUAL_EN_NEW),
            (PS_MONTH_EN_OLD, PS_MONTH_EN_NEW),
            (SDM_ANNUAL_EN_OLD, SDM_ANNUAL_EN_NEW),
            (SDM_MONTH_EN_OLD, SDM_MONTH_EN_NEW),
        )

    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
        elif "ym-nav-group" not in text:
            raise SystemExit(f"nav block not found in {path}")

    if SYNC_YEAR_LABEL_OLD in text:
        text = text.replace(SYNC_YEAR_LABEL_OLD, SYNC_YEAR_LABEL_NEW, 1)

    if ".past-sales-modal__ym-nav-group {" not in text:
        anchor = ".past-sales-modal__ym-nav {"
        if anchor not in text:
            raise SystemExit(f"psm nav css anchor missing in {path}")
        text = text.replace(anchor, NAV_GROUP_CSS_PSM.strip() + "\n    " + anchor, 1)

    if ".sales-data-modal__ym-nav-group {" not in text:
        anchor = ".sales-data-modal__ym-nav {"
        if anchor not in text:
            raise SystemExit(f"sdm nav css anchor missing in {path}")
        text = text.replace(anchor, NAV_GROUP_CSS_SDM.strip() + "\n    " + anchor, 1)

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

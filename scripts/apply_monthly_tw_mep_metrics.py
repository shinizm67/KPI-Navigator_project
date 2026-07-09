#!/usr/bin/env python3
"""Wire Monthly Table Window to KpiYearStore MEP payload (0 when unset)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from monthly_tw_mep_metrics_client import (  # noqa: E402
    MAKE_GROUP_COLUMN_NEW,
    MAKE_GROUP_COLUMN_OLD,
    MONTHLY_TW_DIFF_CSS_ANCHOR,
    MONTHLY_TW_DIFF_CSS_BLOCK,
    MONTHLY_TW_DIFF_CSS_MARKER,
    MONTHLY_VFOCUS_TW_DIFF_LANE_MARKER,
    MONTHLY_TW_LISTENERS_MARKER,
    MONTHLY_TW_MEP_END,
    MONTHLY_TW_MEP_LISTENERS,
    MONTHLY_TW_MEP_MARKER,
    MONTHLY_TW_MEP_OLD_EN,
    MONTHLY_TW_MEP_OLD_JA,
    VFOCUS_CELL_COPY_NEW,
    VFOCUS_CELL_COPY_OLD,
    monthly_tw_mep_metrics_js,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

PROFIT_OLD = """      function getMonthlyProfitCellValue(off, iso) {
        if (!off) return demoMoney;"""

PROFIT_NEW = """      function getMonthlyProfitCellValue(off, iso) {
        if (!off) return resolveMonthlyProfitValue(iso);"""

TEXT_OR_DEMO_OLD = """      function textOrDemo(t) {
        var s = String(t || '')
          .replace(/\\s+/g, ' ')
          .trim();
        return s || demoMoney;
      }"""

TEXT_OR_DEMO_NEW = """      function textOrDemo(t) {
        var s = String(t || '')
          .replace(/\\s+/g, ' ')
          .trim();
        if (!s) return useJa ? '\\u00a50' : '$0';
        return s;
      }"""

REBUILD_HOOK_OLD = """      function rebuildColumns() {
        isoToIndex = {};"""

REBUILD_HOOK_OLD_LOADED = """      function rebuildColumns() {
        loadMonthlyMepMetricsForYear(state.year);
        isoToIndex = {};"""

REBUILD_HOOK_NEW = """      function rebuildColumns() {
        loadMonthlyMepMetricsForYear(state.year);
        invalidateGroup1TwCache();
        isoToIndex = {};"""


def inject_metrics_block(text: str) -> str:
    block = monthly_tw_mep_metrics_js().rstrip() + "\n"
    if MONTHLY_TW_MEP_MARKER in text:
        pattern = (
            re.escape(MONTHLY_TW_MEP_MARKER)
            + r"[\s\S]*?"
            + re.escape(MONTHLY_TW_MEP_END)
            + r"\n?"
        )
        return re.sub(pattern, lambda _m: block, text, count=1)
    if MONTHLY_TW_MEP_OLD_JA in text:
        return text.replace(MONTHLY_TW_MEP_OLD_JA, block.rstrip(), 1)
    if MONTHLY_TW_MEP_OLD_EN in text:
        return text.replace(MONTHLY_TW_MEP_OLD_EN, block.rstrip(), 1)
    raise SystemExit("getActiveDummyGroupValues block not found")


MONTHLY_TW_OFFICE_DIFF_WIN_MARKER = "/* KPI-MONTHLY-TW-OFFICE-DIFF-WIN */"

MONTHLY_TW_SCI_FI_DIFF_OLD = """    .monthly-data-column__cell.tw-diff--win,
    .monthly-vfocus-cell.tw-diff--win {
      color: #58e1f3;
    }
    .monthly-data-column__cell.tw-diff--neutral,
    .monthly-vfocus-cell.tw-diff--neutral {
      color: #58e1f3;
    }"""

MONTHLY_TW_SCI_FI_DIFF_NEW = """    body:not(.office-mode) .monthly-data-column__cell.tw-diff--win,
    body:not(.office-mode) .monthly-vfocus-cell.tw-diff--win {
      color: #58e1f3;
    }
    body:not(.office-mode) .monthly-data-column__cell.tw-diff--neutral,
    body:not(.office-mode) .monthly-vfocus-cell.tw-diff--neutral {
      color: #58e1f3;
    }"""

MONTHLY_TW_OFFICE_WIN_OLD = """    .office-mode .monthly-data-column__cell.tw-diff--win,
    .office-mode .monthly-vfocus-cell.tw-diff--win {
      color: #0d7a8c;
    }
    .office-mode .monthly-data-column__cell.tw-diff--neutral,
    .office-mode .monthly-vfocus-cell.tw-diff--neutral {
      color: #111;
    }"""

MONTHLY_TW_OFFICE_WIN_NEW = """    .office-mode .monthly-data-column__cell.tw-diff--win,
    .office-mode .monthly-vfocus-cell.tw-diff--win {
      color: #111;
    }
    .office-mode .monthly-data-column__cell.tw-diff--neutral,
    .office-mode .monthly-vfocus-cell.tw-diff--neutral {
      color: #111;
    }
    /* KPI-MONTHLY-TW-OFFICE-DIFF-WIN */
    body.office-mode .monthly-data-column .monthly-data-column__cell.tw-diff--win,
    body.office-mode .monthly-data-column .monthly-data-column__cell.tw-diff--neutral,
    body.office-mode .monthly-vfocus-lane .monthly-vfocus-cell.tw-diff--win,
    body.office-mode .monthly-vfocus-lane .monthly-vfocus-cell.tw-diff--neutral {
      color: #111;
    }"""

MONTHLY_VFOCUS_OFFICE_WIN_ANCHOR = """    .office-mode .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer) .monthly-vfocus-cell.tw-diff--sev-below,
    .office-mode .monthly-vfocus-lane--center.monthly-vfocus-lane--tw-off .monthly-vfocus-cell.tw-diff--sev-below {
      color: #7a0f0f;
    }
    /* buffer/off はベースの border より後で指定（border 略式で上書きされないようにする） */"""

MONTHLY_VFOCUS_OFFICE_WIN_BLOCK = """    .office-mode .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer) .monthly-vfocus-cell.tw-diff--sev-below,
    .office-mode .monthly-vfocus-lane--center.monthly-vfocus-lane--tw-off .monthly-vfocus-cell.tw-diff--sev-below {
      color: #7a0f0f;
    }
    /* Office: 中央レーンのベース色より TW diff win/neutral を優先 */
    .office-mode .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer) .monthly-vfocus-cell.tw-diff--win,
    .office-mode .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer) .monthly-vfocus-cell.tw-diff--neutral,
    .office-mode .monthly-vfocus-lane--center.monthly-vfocus-lane--tw-off .monthly-vfocus-cell.tw-diff--win,
    .office-mode .monthly-vfocus-lane--center.monthly-vfocus-lane--tw-off .monthly-vfocus-cell.tw-diff--neutral {
      color: #111;
    }
    /* buffer/off はベースの border より後で指定（border 略式で上書きされないようにする） */"""

MONTHLY_TW_OFFICE_WIN_INSERT_ANCHOR = """    .office-mode .monthly-data-column__cell.tw-diff--neutral,
    .office-mode .monthly-vfocus-cell.tw-diff--neutral {
      color: #111;
    }
    .office-mode .monthly-data-column__cell.tw-diff--sev-90,"""

MONTHLY_TW_OFFICE_WIN_INSERT_BLOCK = """    .office-mode .monthly-data-column__cell.tw-diff--neutral,
    .office-mode .monthly-vfocus-cell.tw-diff--neutral {
      color: #111;
    }
    /* KPI-MONTHLY-TW-OFFICE-DIFF-WIN */
    body.office-mode .monthly-data-column .monthly-data-column__cell.tw-diff--win,
    body.office-mode .monthly-data-column .monthly-data-column__cell.tw-diff--neutral,
    body.office-mode .monthly-vfocus-lane .monthly-vfocus-cell.tw-diff--win,
    body.office-mode .monthly-vfocus-lane .monthly-vfocus-cell.tw-diff--neutral {
      color: #111;
    }
    .office-mode .monthly-data-column__cell.tw-diff--sev-90,"""


def patch_monthly_tw_office_diff(text: str) -> str:
    if "body:not(.office-mode) .monthly-data-column__cell.tw-diff--win" not in text:
        if MONTHLY_TW_SCI_FI_DIFF_OLD in text:
            text = text.replace(MONTHLY_TW_SCI_FI_DIFF_OLD, MONTHLY_TW_SCI_FI_DIFF_NEW, 1)
    if MONTHLY_TW_OFFICE_DIFF_WIN_MARKER not in text:
        if MONTHLY_TW_OFFICE_WIN_OLD in text:
            text = text.replace(MONTHLY_TW_OFFICE_WIN_OLD, MONTHLY_TW_OFFICE_WIN_NEW, 1)
        elif MONTHLY_TW_OFFICE_WIN_INSERT_ANCHOR in text:
            text = text.replace(MONTHLY_TW_OFFICE_WIN_INSERT_ANCHOR, MONTHLY_TW_OFFICE_WIN_INSERT_BLOCK, 1)
    if "Office: 中央レーンのベース色より TW diff win/neutral を優先" not in text:
        if MONTHLY_VFOCUS_OFFICE_WIN_ANCHOR in text:
            text = text.replace(MONTHLY_VFOCUS_OFFICE_WIN_ANCHOR, MONTHLY_VFOCUS_OFFICE_WIN_BLOCK, 1)
    return text


def inject_diff_css(text: str) -> str:
    if MONTHLY_TW_DIFF_CSS_MARKER in text and MONTHLY_VFOCUS_TW_DIFF_LANE_MARKER in text:
        return patch_monthly_tw_office_diff(text)
    if MONTHLY_TW_DIFF_CSS_MARKER in text and MONTHLY_VFOCUS_TW_DIFF_LANE_MARKER not in text:
        raise SystemExit("monthly TW diff CSS present but vfocus lane override missing — re-run from anchor")
    if MONTHLY_TW_DIFF_CSS_ANCHOR not in text:
        raise SystemExit("monthly TW diff CSS anchor miss")
    return text.replace(MONTHLY_TW_DIFF_CSS_ANCHOR, MONTHLY_TW_DIFF_CSS_BLOCK, 1)


def inject_tw_listeners(text: str) -> str:
    if MONTHLY_TW_LISTENERS_MARKER in text:
        return text
    anchor = "      document.addEventListener('annual:salesMapChanged', function () {\n        var keepIso = currentFocusIso || readDailySelectedIso() || toISODateLocal(new Date(state.year, state.month0, 1));\n        rebuildColumns();\n        scheduleScroll(keepIso);\n      });"
    if anchor not in text:
        raise SystemExit("monthly TW listeners anchor miss")
    return text.replace(anchor, anchor + "\n" + MONTHLY_TW_MEP_LISTENERS, 1)


def patch_make_group_column(text: str) -> str:
    if "decorateMonthlyGroup1Cell(cell, i, iso)" in text:
        return text
    if MAKE_GROUP_COLUMN_OLD not in text:
        raise SystemExit("makeGroupColumn patch miss")
    return text.replace(MAKE_GROUP_COLUMN_OLD, MAKE_GROUP_COLUMN_NEW, 1)


def patch_vfocus_copy(text: str) -> str:
    if "if (gi2 === 0 && ci2 === 4)" in text:
        return text
    if VFOCUS_CELL_COPY_OLD not in text:
        raise SystemExit("vfocus cell copy patch miss")
    return text.replace(VFOCUS_CELL_COPY_OLD, VFOCUS_CELL_COPY_NEW, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_metrics_block(text)
    text = inject_diff_css(text)
    if PROFIT_OLD in text:
        text = text.replace(PROFIT_OLD, PROFIT_NEW, 1)
    elif "resolveMonthlyProfitValue(iso)" in text:
        pass
    else:
        raise SystemExit(f"profit patch miss: {path}")
    if TEXT_OR_DEMO_OLD in text:
        text = text.replace(TEXT_OR_DEMO_OLD, TEXT_OR_DEMO_NEW, 1)
    if REBUILD_HOOK_OLD in text:
        text = text.replace(REBUILD_HOOK_OLD, REBUILD_HOOK_NEW, 1)
    elif REBUILD_HOOK_OLD_LOADED in text:
        text = text.replace(REBUILD_HOOK_OLD_LOADED, REBUILD_HOOK_NEW, 1)
    elif "invalidateGroup1TwCache()" in text:
        pass
    else:
        raise SystemExit(f"rebuild hook miss: {path}")
    text = patch_make_group_column(text)
    text = patch_vfocus_copy(text)
    text = inject_tw_listeners(text)
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

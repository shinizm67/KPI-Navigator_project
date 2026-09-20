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
    monthly_tw_5c5_helpers_js,
    monthly_tw_mep_metrics_js,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
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
        if (typeof applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout();
        loadMonthlyMepMetricsForYear(state.year);
        invalidateGroup1TwCache();
        isoToIndex = {};"""

REBUILD_HOOK_LOADED_NO_LAYOUT = """      function rebuildColumns() {
        loadMonthlyMepMetricsForYear(state.year);
        invalidateGroup1TwCache();
        isoToIndex = {};"""


def inject_metrics_block(text: str) -> str:
    # Pages already host an evolved MEP block (Graph CH3 / target maps).
    # Never wholesale-replace it — 5C-5 helpers are inserted surgically.
    if MONTHLY_TW_MEP_MARKER in text:
        return text
    block = monthly_tw_mep_metrics_js().rstrip() + "\n"
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
    if "decorateMonthlyGroup1Cell(cell, i, iso" in text:
        return text
    if MAKE_GROUP_COLUMN_OLD not in text:
        raise SystemExit("makeGroupColumn patch miss")
    return text.replace(MAKE_GROUP_COLUMN_OLD, MAKE_GROUP_COLUMN_NEW, 1)


def patch_vfocus_copy(text: str) -> str:
    if "if (gi2 === 0 && ci2 === 4)" in text:
        return text
    if "laneCounts.push(nLane)" in text or "ci2 === diffIdx" in text:
        return text
    if VFOCUS_CELL_COPY_OLD not in text:
        raise SystemExit("vfocus cell copy patch miss")
    return text.replace(VFOCUS_CELL_COPY_OLD, VFOCUS_CELL_COPY_NEW, 1)


CSS_5C5_BEGIN = "/* === UNIT-5C-5-MONTHLY-TW-BT-CSS-BEGIN === */"
CSS_5C5_END = "/* === UNIT-5C-5-MONTHLY-TW-BT-CSS-END === */"

CSS_5C5_VARS_OLD = """      --monthly-data-group-rows: 6;
      --monthly-data-group-grid-rows: repeat(var(--monthly-data-group-rows), var(--monthly-data-row-h));
      --monthly-data-group-outer-top: 60px;
      --monthly-data-group-outer-h: calc(
        var(--monthly-data-group-rows) * var(--monthly-data-row-h) +
          2 * var(--monthly-data-cell-border)
      );
      --monthly-data-gap-between-groups: 39px;
      --monthly-data-group2-outer-top: calc(
        var(--monthly-data-group-outer-top) + var(--monthly-data-group-outer-h) +
          var(--monthly-data-gap-between-groups)
      );
      --monthly-data-group3-outer-top: calc(
        var(--monthly-data-group2-outer-top) + var(--monthly-data-group-outer-h) +
          var(--monthly-data-gap-between-groups)
      );"""

CSS_5C5_VARS_NEW = """      --monthly-data-group-rows: 6;
      --monthly-data-group1-rows: 6;
      --monthly-data-group2-rows: 6;
      --monthly-data-group3-rows: 6;
      --monthly-data-group-grid-rows: repeat(var(--monthly-data-group-rows), var(--monthly-data-row-h));
      --monthly-data-group-outer-top: 60px;
      --monthly-data-group-outer-h: calc(
        var(--monthly-data-group-rows) * var(--monthly-data-row-h) +
          2 * var(--monthly-data-cell-border)
      );
      --monthly-data-group1-outer-h: calc(
        var(--monthly-data-group1-rows) * var(--monthly-data-row-h) +
          2 * var(--monthly-data-cell-border)
      );
      --monthly-data-group2-border-pad: calc(2 * var(--monthly-data-cell-border));
      --monthly-data-group2-outer-h: calc(
        var(--monthly-data-group2-rows) * var(--monthly-data-row-h) +
          var(--monthly-data-group2-border-pad)
      );
      --monthly-data-group3-outer-h: calc(
        var(--monthly-data-group3-rows) * var(--monthly-data-row-h) +
          2 * var(--monthly-data-cell-border)
      );
      --monthly-data-gap-between-groups: 39px;
      --monthly-data-gap-after-g1: var(--monthly-data-gap-between-groups);
      --monthly-data-gap-after-g2: var(--monthly-data-gap-between-groups);
      --monthly-data-group2-outer-top: calc(
        var(--monthly-data-group-outer-top) + var(--monthly-data-group1-outer-h) +
          var(--monthly-data-gap-after-g1)
      );
      --monthly-data-group3-outer-top: calc(
        var(--monthly-data-group2-outer-top) + var(--monthly-data-group2-outer-h) +
          var(--monthly-data-gap-after-g2)
      );"""

CSS_5C5_STACK_OLD = """      --monthly-scroll-stack-h-three-groups: calc(
        var(--monthly-date-row-h) + var(--monthly-data-group-outer-h) +
          var(--monthly-data-gap-between-groups) + var(--monthly-data-group-outer-h) +
          var(--monthly-data-gap-between-groups) + var(--monthly-data-group-outer-h)
      );"""

CSS_5C5_STACK_NEW = """      --monthly-scroll-stack-h-three-groups: calc(
        var(--monthly-date-row-h) + var(--monthly-data-group1-outer-h) +
          var(--monthly-data-gap-after-g1) + var(--monthly-data-group2-outer-h) +
          var(--monthly-data-gap-after-g2) + var(--monthly-data-group3-outer-h)
      );"""

CSS_5C5_PROFIT_OLD = """      --monthly-profit-row-top: calc(
        var(--monthly-data-group3-outer-top) + var(--monthly-data-group-outer-h) +
          var(--monthly-profit-gap-after-group3)
      );"""

CSS_5C5_PROFIT_NEW = """      --monthly-profit-row-top: calc(
        var(--monthly-data-group3-outer-top) + var(--monthly-data-group3-outer-h) +
          var(--monthly-profit-gap-after-group3)
      );"""

CSS_5C5_BLOCK = f"""    {CSS_5C5_BEGIN}
    .monthly-table-window[data-tw-layout="key-expenses"] {{
      --monthly-data-group1-rows: 4;
      --monthly-data-group2-rows: 0;
      --monthly-data-group2-border-pad: 0px;
      --monthly-data-gap-after-g2: 0px;
    }}
    .monthly-table-window[data-tw-layout="key-expenses"] .monthly-table-window__vlabel--customer {{
      display: none;
    }}
    .monthly-table-window[data-tw-layout="key-expenses"] .monthly-table-window__metric-col {{
      height: calc(
        var(--monthly-data-group1-rows) * var(--monthly-data-row-h) +
          var(--monthly-data-gap-after-g1) +
          var(--monthly-data-group3-rows) * var(--monthly-data-row-h)
      );
      grid-template-rows:
        repeat(var(--monthly-data-group1-rows), var(--monthly-data-row-h))
        var(--monthly-data-gap-after-g1)
        repeat(var(--monthly-data-group3-rows), var(--monthly-data-row-h));
    }}
    .monthly-table-window[data-tw-layout="key-expenses"] #monthly-scroll-track-group2 {{
      overflow: hidden;
      min-height: 0;
    }}
    .monthly-table-window[data-tw-layout="key-expenses"] #monthly-scroll-track-group2 .monthly-data-column--group {{
      border-width: 0;
      min-height: 0;
      overflow: hidden;
    }}
    #monthly-scroll-track-group1.monthly-scroll-data__track--group {{
      height: var(--monthly-data-group1-outer-h);
      flex-basis: var(--monthly-data-group1-outer-h);
    }}
    #monthly-scroll-track-group2.monthly-scroll-data__track--group {{
      height: var(--monthly-data-group2-outer-h);
      flex-basis: var(--monthly-data-group2-outer-h);
    }}
    #monthly-scroll-track-group3.monthly-scroll-data__track--group {{
      height: var(--monthly-data-group3-outer-h);
      flex-basis: var(--monthly-data-group3-outer-h);
    }}
    #monthly-scroll-track-group1 .monthly-data-column--group {{
      height: var(--monthly-data-group1-outer-h);
      grid-template-rows: repeat(var(--monthly-data-group1-rows), var(--monthly-data-row-h));
    }}
    #monthly-scroll-track-group2 .monthly-data-column--group {{
      height: var(--monthly-data-group2-outer-h);
      grid-template-rows: repeat(var(--monthly-data-group2-rows), var(--monthly-data-row-h));
    }}
    #monthly-scroll-track-group3 .monthly-data-column--group {{
      height: var(--monthly-data-group3-outer-h);
      grid-template-rows: repeat(var(--monthly-data-group3-rows), var(--monthly-data-row-h));
    }}
    #monthly-scroll-track-group1 .monthly-scroll-data__track-spacer {{
      min-height: var(--monthly-data-group1-outer-h);
    }}
    #monthly-scroll-track-group2 .monthly-scroll-data__track-spacer {{
      min-height: var(--monthly-data-group2-outer-h);
    }}
    #monthly-scroll-track-group3 .monthly-scroll-data__track-spacer {{
      min-height: var(--monthly-data-group3-outer-h);
    }}
    #monthly-scroll-track-group2 + .monthly-scroll-data__between {{
      flex-basis: var(--monthly-data-gap-after-g2);
      height: var(--monthly-data-gap-after-g2);
      min-height: var(--monthly-data-gap-after-g2);
    }}
    .monthly-table-window__metric-col {{
      height: calc(
        var(--monthly-data-group1-rows) * var(--monthly-data-row-h) +
          var(--monthly-data-gap-after-g1) +
          var(--monthly-data-group2-rows) * var(--monthly-data-row-h) +
          var(--monthly-data-gap-after-g2) +
          var(--monthly-data-group3-rows) * var(--monthly-data-row-h)
      );
      grid-template-rows:
        repeat(var(--monthly-data-group1-rows), var(--monthly-data-row-h))
        var(--monthly-data-gap-after-g1)
        repeat(var(--monthly-data-group2-rows), var(--monthly-data-row-h))
        var(--monthly-data-gap-after-g2)
        repeat(var(--monthly-data-group3-rows), var(--monthly-data-row-h));
    }}
    .monthly-vfocus-group[data-tw-rows="4"] {{
      grid-template-rows: repeat(3, var(--monthly-vfocus-cell-row-h)) var(--monthly-vfocus-cell-inner-h);
    }}
    .monthly-vfocus-group[data-tw-rows="0"] {{
      display: none;
      margin-top: 0 !important;
      height: 0;
      border-width: 0;
    }}
    .monthly-table-window__h-line-775,
    .monthly-table-window__h-line-775-right {{
      top: var(--monthly-profit-row-top);
    }}
    {CSS_5C5_END}
"""

CSS_5C5_VLABEL_OLD = """    .monthly-table-window__vlabel--income {
      top: var(--monthly-data-group-outer-top);
      height: var(--monthly-data-group-outer-h);
    }
    .monthly-table-window__vlabel--customer {
      top: var(--monthly-data-group2-outer-top);
      height: var(--monthly-data-group-outer-h);
    }
    .monthly-table-window__vlabel--expenses {
      top: var(--monthly-data-group3-outer-top);
      height: var(--monthly-data-group-outer-h);
    }"""

CSS_5C5_VLABEL_NEW = """    .monthly-table-window__vlabel--income {
      top: var(--monthly-data-group-outer-top);
      height: var(--monthly-data-group1-outer-h);
    }
    .monthly-table-window__vlabel--customer {
      top: var(--monthly-data-group2-outer-top);
      height: var(--monthly-data-group2-outer-h);
    }
    .monthly-table-window__vlabel--expenses {
      top: var(--monthly-data-group3-outer-top);
      height: var(--monthly-data-group3-outer-h);
    }"""

CSS_5C5_INSERT_ANCHOR = """    .monthly-table-window__metric-col .monthly-table-window__metric-line:nth-child(7),
    .monthly-table-window__metric-col .monthly-table-window__metric-line:nth-child(14) {
      visibility: hidden;
    }"""

COMPUTE_METRICS_OLD = """      function computeMonthlyRebuildMetricsForDay(dayObj) {
        var iso = toISODateLocal(dayObj);
        var off = !isBusinessDayByIso(iso, dayObj);
        if (off) return { off: true };
        var cache = window.__MONTHLY_MEP_METRICS__ || {};
        var fixedIds = cache.fixedIds || [];
        var variableIds = cache.variableIds || [];
        var sales = dailySalesAmount(iso);
        var snap = readGroup1TwSnapshot(iso);
        var lunch = mepReadRow(iso, 'incLunch');
        var dinner = Math.max(0, Math.round(sales) - Math.round(lunch));
        var g1 = [
          fmtTwMoney(snap.sales),
          fmtTwMoney(lunch),
          fmtTwMoney(dinner),
          snap.targetText,
          snap.diffText,
          snap.achText,
        ];
        var g2;
        if (useJa) {
          var cust = mepReadRow(iso, 'cust');
          var custLunch = mepReadRow(iso, 'custLunch');
          var custDinner = mepParentMinusLunch(iso, 'cust', 'custLunch');
          var grp = mepReadRow(iso, 'groupCnt');
          var grpLunch = mepReadRow(iso, 'groupCntLunch');
          var grpDinner = mepParentMinusLunch(iso, 'groupCnt', 'groupCntLunch');
          g2 = [
            fmtTwCount(cust),
            fmtTwCount(custLunch),
            fmtTwCount(custDinner),
            fmtTwCount(grp),
            fmtTwCount(grpLunch),
            fmtTwCount(grpDinner),
          ];
        } else {
          var custEn = mepReadRow(iso, 'cust');
          var custLunchEn = mepReadRow(iso, 'custLunch');
          var custDinnerEn = mepParentMinusLunch(iso, 'cust', 'custLunch');
          var pc = mepReadRow(iso, 'pc');
          var pcLunch = mepReadRow(iso, 'pcLunch');
          var pcDinner = mepParentMinusLunch(iso, 'pc', 'pcLunch');
          g2 = [
            fmtTwCount(custEn),
            fmtTwCount(custLunchEn),
            fmtTwCount(custDinnerEn),
            fmtTwMoney(pc),
            fmtTwMoney(pcLunch),
            fmtTwMoney(pcDinner),
          ];
        }
        var food = mepReadRow(iso, 'exp_food_cost');
        var bev = mepReadRow(iso, 'exp_drink_cost');
        var misc = mepReadRow(iso, 'exp_misc');
        var fixedSum = mepSumRows(iso, fixedIds);
        var varSum = mepSumRows(iso, variableIds);
        var total = fixedSum + varSum;
        return {
          off: false,
          g1: g1,
          g2: g2,
          g3: [
            fmtTwMoney(food),
            fmtTwMoney(bev),
            fmtTwMoney(misc),
            fmtTwMoney(fixedSum),
            fmtTwMoney(varSum),
            fmtTwMoney(total),
          ],
          profit: fmtTwMoney(sales - total),
          snap: snap,
        };
      }"""

COMPUTE_METRICS_NEW = """      function computeMonthlyRebuildMetricsForDay(dayObj) {
        var iso = toISODateLocal(dayObj);
        var off = !isBusinessDayByIso(iso, dayObj);
        if (off) return { off: true };
        var snap = readGroup1TwSnapshot(iso);
        return {
          off: false,
          g1: resolveGroup1Values(iso),
          g2: resolveGroup2Values(iso),
          g3: resolveGroup3Values(iso),
          profit: resolveMonthlyProfitValue(iso),
          snap: snap,
        };
      }"""


def inject_5c5_css(text: str) -> str:
    if CSS_5C5_BEGIN in text:
        pattern = re.escape(CSS_5C5_BEGIN) + r"[\s\S]*?" + re.escape(CSS_5C5_END)
        text = re.sub(pattern, CSS_5C5_BLOCK.strip(), text, count=1)
    else:
        if CSS_5C5_VARS_OLD not in text:
            raise SystemExit("5C-5 CSS vars anchor miss")
        text = text.replace(CSS_5C5_VARS_OLD, CSS_5C5_VARS_NEW, 1)
        if CSS_5C5_STACK_OLD in text:
            text = text.replace(CSS_5C5_STACK_OLD, CSS_5C5_STACK_NEW, 1)
        if CSS_5C5_PROFIT_OLD in text:
            text = text.replace(CSS_5C5_PROFIT_OLD, CSS_5C5_PROFIT_NEW, 1)
        if CSS_5C5_INSERT_ANCHOR not in text:
            raise SystemExit("5C-5 CSS insert anchor miss")
        text = text.replace(CSS_5C5_INSERT_ANCHOR, CSS_5C5_INSERT_ANCHOR + "\n" + CSS_5C5_BLOCK, 1)
    if CSS_5C5_VLABEL_OLD in text:
        text = text.replace(CSS_5C5_VLABEL_OLD, CSS_5C5_VLABEL_NEW, 1)
    text = text.replace(
        "--monthly-income-cell-outer-h: var(--monthly-data-group-outer-h);",
        "--monthly-income-cell-outer-h: var(--monthly-data-group1-outer-h);",
        1,
    )
    text = text.replace(
        "--monthly-expenses-cell-outer-h: var(--monthly-data-group-outer-h);",
        "--monthly-expenses-cell-outer-h: var(--monthly-data-group3-outer-h);",
        1,
    )
    return text


JS_5C5_BEGIN = "/* === UNIT-5C-5-MONTHLY-TW-BT-BEGIN === */"
JS_5C5_END = "/* === UNIT-5C-5-MONTHLY-TW-BT-END === */"

DECORATE_OLD = """      function decorateMonthlyGroup1Cell(cell, cellIndex, iso, skipDiffDecor) {
        if (!cell || skipDiffDecor) return;
        if (cellIndex === 3) {
          cell.classList.add('monthly-data-column__cell--plan-target');
        }
        if (cellIndex !== 4) return;
        var snap = readGroup1TwSnapshot(iso);
        applyMonthlyTwDiffClass(cell, snap.diffActual, snap.diffTarget);
      }"""

DECORATE_NEW = """      function decorateMonthlyGroup1Cell(cell, cellIndex, iso, skipDiffDecor) {
        if (!cell) return;
        cell.classList.remove('monthly-data-column__cell--plan-target');
        if (skipDiffDecor) {
          clearMonthlyTwDiffClasses(cell);
          return;
        }
        if (cellIndex === monthlyTwGroup1TargetIdx()) {
          cell.classList.add('monthly-data-column__cell--plan-target');
        }
        if (cellIndex !== monthlyTwGroup1DiffIdx()) return;
        var snap = readGroup1TwSnapshot(iso);
        applyMonthlyTwDiffClass(cell, snap.diffActual, snap.diffTarget);
      }"""

SYNC_VFOCUS_OLD = """        var srcDiff = srcCells && srcCells[4] ? srcCells[4] : null;"""

SYNC_VFOCUS_NEW = """        var diffIdx = typeof monthlyTwGroup1DiffIdx === 'function' ? monthlyTwGroup1DiffIdx() : 4;
        var srcDiff = srcCells && srcCells[diffIdx] ? srcCells[diffIdx] : null;"""

RESOLVE_G1_OLD = """      function resolveGroup1Values(iso) {
        var snap = readGroup1TwSnapshot(iso);
        var lunch = mepReadRow(iso, 'incLunch');
        var dinner = mepSalesRowMinusLunch(iso, 'incLunch');
        return [
          fmtTwMoney(snap.sales),
          fmtTwMoney(lunch),
          fmtTwMoney(dinner),
          snap.targetText,
          snap.diffText,
          snap.achText,
        ];
      }"""

RESOLVE_G1_NEW = """      function resolveGroup1Values(iso) {
        var snap = readGroup1TwSnapshot(iso);
        if (!monthlyTwIsRestaurant()) {
          return [
            fmtTwMoney(snap.sales),
            snap.targetText,
            snap.diffText,
            snap.achText,
          ];
        }
        var lunch = mepReadRow(iso, 'incLunch');
        var dinner = mepSalesRowMinusLunch(iso, 'incLunch');
        return [
          fmtTwMoney(snap.sales),
          fmtTwMoney(lunch),
          fmtTwMoney(dinner),
          snap.targetText,
          snap.diffText,
          snap.achText,
        ];
      }"""

RESOLVE_G2_OLD = """      function resolveGroup2Values(iso) {
        var cust = mepReadRow(iso, 'cust');"""

RESOLVE_G2_NEW = """      function resolveGroup2Values(iso) {
        if (!monthlyTwIsRestaurant()) return [];
        var cust = mepReadRow(iso, 'cust');"""

RESOLVE_G3_OLD = """      function resolveGroup3Values(iso) {
        var cache = window.__MONTHLY_MEP_METRICS__ || {};
        var food = mepReadRow(iso, 'exp_food_cost');
        var bev = mepReadRow(iso, 'exp_drink_cost');
        var misc = mepReadRow(iso, 'exp_misc');
        var fixed = mepSumRows(iso, cache.fixedIds);
        var expected = mepSumRows(iso, cache.variableIds);
        var total = fixed + expected;
        return [
          fmtTwMoney(food),
          fmtTwMoney(bev),
          fmtTwMoney(misc),
          fmtTwMoney(fixed),
          fmtTwMoney(expected),
          fmtTwMoney(total),
        ];
      }"""

RESOLVE_G3_NEW = """      function resolveGroup3Values(iso) {
        var cache = window.__MONTHLY_MEP_METRICS__ || {};
        var fixed = mepSumRows(iso, cache.fixedIds);
        var expected = mepSumRows(iso, cache.variableIds);
        var total = fixed + expected;
        if (monthlyTwIsRestaurant()) {
          var food = mepReadRow(iso, 'exp_food_cost');
          var bev = mepReadRow(iso, 'exp_drink_cost');
          var misc = mepReadRow(iso, 'exp_misc');
          return [
            fmtTwMoney(food),
            fmtTwMoney(bev),
            fmtTwMoney(misc),
            fmtTwMoney(fixed),
            fmtTwMoney(expected),
            fmtTwMoney(total),
          ];
        }
        var spec = monthlyTwKeyExpenseSpec();
        var k0 = mepSumRows(iso, spec.idGroups[0] || []);
        var k1 = mepSumRows(iso, spec.idGroups[1] || []);
        var residual = Math.max(
          0,
          expected -
            mepSumVariablePortion(iso, spec.idGroups[0] || [], cache.variableIds) -
            mepSumVariablePortion(iso, spec.idGroups[1] || [], cache.variableIds)
        );
        return [
          fmtTwMoney(k0),
          fmtTwMoney(k1),
          fmtTwMoney(residual),
          fmtTwMoney(fixed),
          fmtTwMoney(expected),
          fmtTwMoney(total),
        ];
      }"""

INVALIDATE_OLD = """      function invalidateMonthlyMepMetricsCache() {
        window.__MONTHLY_MEP_METRICS__ = null;
      }"""

INVALIDATE_NEW = """      function invalidateMonthlyMepMetricsCache() {
        window.__MONTHLY_MEP_METRICS__ = null;
        __monthlyTwKeyCache = null;
      }"""

DOM_READER_OLD = """        if (!cells || cells.length < 4) return null;
        var salesText = cells[0] ? cells[0].textContent : '';
        var targetText = cells[3] ? cells[3].textContent : '';"""

DOM_READER_NEW = """        var tIdx = typeof monthlyTwGroup1TargetIdx === 'function' ? monthlyTwGroup1TargetIdx() : 3;
        if (!cells || cells.length <= tIdx) return null;
        var salesText = cells[0] ? cells[0].textContent : '';
        var targetText = cells[tIdx] ? cells[tIdx].textContent : '';"""

REBUILD_SYNC_OLD = """      function rebuildColumns() {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        loadMonthlyMepMetricsForYear(state.year);"""

REBUILD_SYNC_NEW = """      function rebuildColumns() {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        if (typeof applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout();
        loadMonthlyMepMetricsForYear(state.year);"""

KEEP_FOCUS_INNER_OLD = """          invalidateMonthlyMepMetricsCache();
          invalidateGroup1TwCache();"""

KEEP_FOCUS_INNER_NEW = """          if (typeof applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout();
          invalidateMonthlyMepMetricsCache();
          invalidateGroup1TwCache();"""

BT_LISTENERS_OLD = "      /* END KPI-MONTHLY-TW-LISTENERS */"
BT_LISTENERS_NEW = """      document.addEventListener('kpi:businessTypeChanged', monthlyTwRebuildKeepFocus);
      window.addEventListener('storage', function (ev) {
        if (!ev || String(ev.key || '') !== 'kpiNavigator.kpiYearStore') return;
        monthlyTwRebuildKeepFocus();
      });
      /* END KPI-MONTHLY-TW-LISTENERS */"""


def inject_5c5_js(text: str) -> str:
    block = monthly_tw_5c5_helpers_js().rstrip() + "\n"
    if JS_5C5_BEGIN in text:
        pattern = re.escape(JS_5C5_BEGIN) + r"[\s\S]*?" + re.escape(JS_5C5_END)
        return re.sub(pattern, lambda _m: block.rstrip(), text, count=1)
    marker = "      function decorateMonthlyGroup1Cell"
    if marker not in text:
        raise SystemExit("5C-5 JS insert miss (decorateMonthlyGroup1Cell)")
    return text.replace(marker, block + "\n" + marker, 1)


def patch_5c5_runtime(text: str) -> str:
    if "cellIndex === monthlyTwGroup1TargetIdx()" not in text:
        if DECORATE_OLD not in text:
            raise SystemExit("decorateMonthlyGroup1Cell 5C-5 patch miss")
        text = text.replace(DECORATE_OLD, DECORATE_NEW, 1)
    if "var diffIdx = typeof monthlyTwGroup1DiffIdx" not in text:
        if SYNC_VFOCUS_OLD not in text:
            raise SystemExit("syncMonthlyVfocusDiffClass 5C-5 patch miss")
        text = text.replace(SYNC_VFOCUS_OLD, SYNC_VFOCUS_NEW, 1)
    if "if (!monthlyTwIsRestaurant()) {" not in text:
        if RESOLVE_G1_OLD not in text:
            raise SystemExit("resolveGroup1Values 5C-5 patch miss")
        text = text.replace(RESOLVE_G1_OLD, RESOLVE_G1_NEW, 1)
    if "if (!monthlyTwIsRestaurant()) return [];" not in text:
        if RESOLVE_G2_OLD not in text:
            raise SystemExit("resolveGroup2Values 5C-5 patch miss")
        text = text.replace(RESOLVE_G2_OLD, RESOLVE_G2_NEW, 1)
    if "fmtTwMoney(k0)" not in text:
        if RESOLVE_G3_OLD not in text:
            raise SystemExit("resolveGroup3Values 5C-5 patch miss")
        text = text.replace(RESOLVE_G3_OLD, RESOLVE_G3_NEW, 1)
    if "__monthlyTwKeyCache = null;" not in text.split("function invalidateMonthlyMepMetricsCache", 1)[-1][:200]:
        if INVALIDATE_OLD not in text:
            raise SystemExit("invalidateMonthlyMepMetricsCache 5C-5 patch miss")
        text = text.replace(INVALIDATE_OLD, INVALIDATE_NEW, 1)
    if "monthlyTwGroup1TargetIdx === 'function'" not in text:
        if DOM_READER_OLD not in text:
            raise SystemExit("readMonthlyTwGroup1MetricsFromDom 5C-5 patch miss")
        text = text.replace(DOM_READER_OLD, DOM_READER_NEW, 1)
    return text


CHUNKED_OLD = """      function rebuildColumnsChunked(runToken, onDone) {
        /* KPI-MRP-PHASE2-5 */
        window.__monthlyTwColumnsBusy = true;"""

CHUNKED_NEW = """      function rebuildColumnsChunked(runToken, onDone) {
        if (typeof applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout();
        /* KPI-MRP-PHASE2-5 */
        window.__monthlyTwColumnsBusy = true;"""


def patch_5c5_rebuild_and_listeners(text: str) -> str:
    if CHUNKED_OLD in text:
        text = text.replace(CHUNKED_OLD, CHUNKED_NEW, 1)
    elif "function rebuildColumnsChunked(runToken, onDone)" in text and "applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout();\n        /* KPI-MRP-PHASE2-5 */" not in text:
        if "function rebuildColumnsChunked(runToken, onDone) {\n        if (typeof applyMonthlyTwBusinessTypeLayout" not in text:
            raise SystemExit("rebuildColumnsChunked 5C-5 layout hook miss")
    if "applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout();\n        loadMonthlyMepMetricsForYear" not in text:
        if REBUILD_SYNC_OLD not in text:
            raise SystemExit("rebuildColumns 5C-5 layout hook miss")
        text = text.replace(REBUILD_SYNC_OLD, REBUILD_SYNC_NEW, 1)
    if KEEP_FOCUS_INNER_OLD in text and "applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout();\n          invalidateMonthlyMepMetricsCache" not in text:
        text = text.replace(KEEP_FOCUS_INNER_OLD, KEEP_FOCUS_INNER_NEW, 1)
    if "addEventListener('kpi:businessTypeChanged'" not in text:
        if BT_LISTENERS_OLD not in text:
            raise SystemExit("TW listeners end marker miss")
        text = text.replace(BT_LISTENERS_OLD, BT_LISTENERS_NEW, 1)
    return text


def patch_compute_metrics(text: str) -> str:
    if "g1: resolveGroup1Values(iso)" in text:
        return text
    if COMPUTE_METRICS_OLD not in text:
        raise SystemExit("computeMonthlyRebuildMetricsForDay patch miss")
    return text.replace(COMPUTE_METRICS_OLD, COMPUTE_METRICS_NEW, 1)


def patch_make_group_row_count(text: str) -> str:
    old = """        for (var i = 0; i < 6; i++) {
          var cell = document.createElement('span');
          cell.className = 'monthly-data-column__cell';
          cell.setAttribute('aria-hidden', 'true');
          cell.textContent = values[i] || '';
          if (groupNo === 1) decorateMonthlyGroup1Cell(cell, i, iso, buffer);
          div.appendChild(cell);
        }"""
    new = """        var rowN = typeof monthlyTwGroupRowCount === 'function' ? monthlyTwGroupRowCount(groupNo) : 6;
        for (var i = 0; i < rowN; i++) {
          var cell = document.createElement('span');
          cell.className = 'monthly-data-column__cell';
          cell.setAttribute('aria-hidden', 'true');
          cell.textContent = values[i] || '';
          if (groupNo === 1) decorateMonthlyGroup1Cell(cell, i, iso, buffer);
          div.appendChild(cell);
        }"""
    if "var rowN = typeof monthlyTwGroupRowCount" in text:
        return text
    if old not in text:
        raise SystemExit("makeGroupColumn row-count patch miss")
    return text.replace(old, new, 1)


def patch_hydrate_row_count(text: str) -> str:
    old = """        for (var hi = 0; hi < 6; hi++) {
          if (!cells[hi]) continue;
          cells[hi].textContent = values[hi] || '';
          if (groupNo === 1) decorateMonthlyGroup1Cell(cells[hi], hi, iso, buffer);
        }"""
    new = """        var hydN = typeof monthlyTwGroupRowCount === 'function' ? monthlyTwGroupRowCount(groupNo) : 6;
        for (var hi = 0; hi < hydN; hi++) {
          if (!cells[hi]) continue;
          cells[hi].textContent = values[hi] || '';
          if (groupNo === 1) decorateMonthlyGroup1Cell(cells[hi], hi, iso, buffer);
        }"""
    if "var hydN = typeof monthlyTwGroupRowCount" in text:
        return text
    if old not in text:
        raise SystemExit("hydrateMonthlyColumnCells row-count patch miss")
    return text.replace(old, new, 1)


def patch_ensure_group_shell(text: str) -> str:
    old = """      function ensureGroupShell(g) {
        if (!g) return;
        if (g.childElementCount === 0) {
          for (var i = 0; i < 6; i++) {
            var sp = document.createElement('span');
            sp.className = 'monthly-vfocus-cell';
            sp.setAttribute('aria-hidden', 'true');
            g.appendChild(sp);
          }
        }
      }"""
    new = """      function ensureGroupShell(g, groupNo) {
        if (!g) return;
        var rows = typeof monthlyTwGroupRowCount === 'function' ? monthlyTwGroupRowCount(groupNo || 1) : 6;
        g.setAttribute('data-tw-rows', String(rows));
        while (g.childElementCount > rows) g.removeChild(g.lastChild);
        while (g.childElementCount < rows) {
          var sp = document.createElement('span');
          sp.className = 'monthly-vfocus-cell';
          sp.setAttribute('aria-hidden', 'true');
          g.appendChild(sp);
        }
      }"""
    if "function ensureGroupShell(g, groupNo)" in text:
        return text
    if old not in text:
        raise SystemExit("ensureGroupShell patch miss")
    text = text.replace(old, new, 1)
    old_call = """        ].forEach(ensureGroupShell);"""
    new_call = """        ].forEach(function (g, idx) {
          var gNo = (idx % 3) + 1;
          ensureGroupShell(g, gNo);
        });"""
    if old_call not in text:
        raise SystemExit("ensureGroupShell forEach patch miss")
    return text.replace(old_call, new_call, 1)


def patch_vfocus_fill_lane(text: str) -> str:
    old_empty = """            for (var gi = 0; gi < 3; gi++) {
              var gEmpty = groups[gi];
              if (!gEmpty) continue;
              for (var ci0 = 0; ci0 < 6; ci0++) {
                if (gEmpty.children[ci0]) gEmpty.children[ci0].textContent = '';
              }
            }"""
    new_empty = """            for (var gi = 0; gi < 3; gi++) {
              var gEmpty = groups[gi];
              if (!gEmpty) continue;
              var emptyN = typeof monthlyTwGroupRowCount === 'function' ? monthlyTwGroupRowCount(gi + 1) : 6;
              for (var ci0 = 0; ci0 < emptyN; ci0++) {
                if (gEmpty.children[ci0]) gEmpty.children[ci0].textContent = '';
              }
            }"""
    if old_empty in text:
        text = text.replace(old_empty, new_empty, 1)
    old_copy = """          var valuesLane = [];
          [trackGroup1, trackGroup2, trackGroup3].forEach(function (t) {
            var col = t && t.children ? t.children[colIdx] : null;
            if (!col) return;
            var cells = col.querySelectorAll('.monthly-data-column__cell');
            for (var k = 0; k < 6; k++) {
              valuesLane.push(textOrDemo(cells[k] ? cells[k].textContent : ''));
            }
          });
          while (valuesLane.length < 18) valuesLane.push(emptyMoney);
          for (var gi2 = 0; gi2 < 3; gi2++) {
            var g2 = groups[gi2];
            if (!g2) continue;
            for (var ci2 = 0; ci2 < 6; ci2++) {
              var cell = g2.children[ci2];
              if (cell) {
                cell.textContent = valuesLane[gi2 * 6 + ci2] || emptyMoney;
                if (gi2 === 0 && ci2 === 4) {
                  syncMonthlyVfocusDiffClass(cell, colIdx);
                } else if (gi2 === 0) {
                  clearMonthlyTwDiffClasses(cell);
                }
              }
            }
          }"""
    new_copy = """          var valuesLane = [];
          var laneCounts = [];
          [trackGroup1, trackGroup2, trackGroup3].forEach(function (t, giLane) {
            var nLane = typeof monthlyTwGroupRowCount === 'function' ? monthlyTwGroupRowCount(giLane + 1) : 6;
            laneCounts.push(nLane);
            var col = t && t.children ? t.children[colIdx] : null;
            var cells = col ? col.querySelectorAll('.monthly-data-column__cell') : [];
            for (var k = 0; k < nLane; k++) {
              valuesLane.push(textOrDemo(cells[k] ? cells[k].textContent : ''));
            }
          });
          var laneOffset = 0;
          for (var gi2 = 0; gi2 < 3; gi2++) {
            var g2 = groups[gi2];
            var nCopy = laneCounts[gi2] || 0;
            var diffIdx = typeof monthlyTwGroup1DiffIdx === 'function' ? monthlyTwGroup1DiffIdx() : 4;
            if (g2) {
              for (var ci2 = 0; ci2 < nCopy; ci2++) {
                var cell = g2.children[ci2];
                if (cell) {
                  cell.textContent = valuesLane[laneOffset + ci2] || emptyMoney;
                  if (gi2 === 0 && ci2 === diffIdx) {
                    syncMonthlyVfocusDiffClass(cell, colIdx);
                  } else if (gi2 === 0) {
                    clearMonthlyTwDiffClasses(cell);
                  }
                }
              }
            }
            laneOffset += nCopy;
          }"""
    if "laneCounts.push(nLane)" in text:
        return text
    old_copy_plan = """          var valuesLane = [];
          [trackGroup1, trackGroup2, trackGroup3].forEach(function (t) {
            var col = t && t.children ? t.children[colIdx] : null;
            if (!col) return;
            var cells = col.querySelectorAll('.monthly-data-column__cell');
            for (var k = 0; k < 6; k++) {
              valuesLane.push(textOrDemo(cells[k] ? cells[k].textContent : ''));
            }
          });
          while (valuesLane.length < 18) valuesLane.push(emptyMoney);
          for (var gi2 = 0; gi2 < 3; gi2++) {
            var g2 = groups[gi2];
            if (!g2) continue;
            for (var ci2 = 0; ci2 < 6; ci2++) {
              var cell = g2.children[ci2];
              if (cell) {
                cell.textContent = valuesLane[gi2 * 6 + ci2] || emptyMoney;
                if (gi2 === 0 && ci2 === 4) {
                  cell.classList.remove('monthly-vfocus-cell--plan-target');
                  syncMonthlyVfocusDiffClass(cell, colIdx);
                } else if (gi2 === 0 && ci2 === 3) {
                  clearMonthlyTwDiffClasses(cell);
                  cell.classList.add('monthly-vfocus-cell--plan-target');
                } else if (gi2 === 0) {
                  clearMonthlyTwDiffClasses(cell);
                  cell.classList.remove('monthly-vfocus-cell--plan-target');
                } else {
                  cell.classList.remove('monthly-vfocus-cell--plan-target');
                }
              }
            }
          }"""
    new_copy_plan = """          var valuesLane = [];
          var laneCounts = [];
          [trackGroup1, trackGroup2, trackGroup3].forEach(function (t, giLane) {
            var nLane = typeof monthlyTwGroupRowCount === 'function' ? monthlyTwGroupRowCount(giLane + 1) : 6;
            laneCounts.push(nLane);
            var col = t && t.children ? t.children[colIdx] : null;
            var cells = col ? col.querySelectorAll('.monthly-data-column__cell') : [];
            for (var k = 0; k < nLane; k++) {
              valuesLane.push(textOrDemo(cells[k] ? cells[k].textContent : ''));
            }
          });
          var laneOffset = 0;
          for (var gi2 = 0; gi2 < 3; gi2++) {
            var g2 = groups[gi2];
            var nCopy = laneCounts[gi2] || 0;
            var diffIdx = typeof monthlyTwGroup1DiffIdx === 'function' ? monthlyTwGroup1DiffIdx() : 4;
            var targetIdx = typeof monthlyTwGroup1TargetIdx === 'function' ? monthlyTwGroup1TargetIdx() : 3;
            if (g2) {
              for (var ci2 = 0; ci2 < nCopy; ci2++) {
                var cell = g2.children[ci2];
                if (cell) {
                  cell.textContent = valuesLane[laneOffset + ci2] || emptyMoney;
                  if (gi2 === 0 && ci2 === diffIdx) {
                    cell.classList.remove('monthly-vfocus-cell--plan-target');
                    syncMonthlyVfocusDiffClass(cell, colIdx);
                  } else if (gi2 === 0 && ci2 === targetIdx) {
                    clearMonthlyTwDiffClasses(cell);
                    cell.classList.add('monthly-vfocus-cell--plan-target');
                  } else if (gi2 === 0) {
                    clearMonthlyTwDiffClasses(cell);
                    cell.classList.remove('monthly-vfocus-cell--plan-target');
                  } else {
                    cell.classList.remove('monthly-vfocus-cell--plan-target');
                  }
                }
              }
            }
            laneOffset += nCopy;
          }"""
    if old_copy in text:
        return text.replace(old_copy, new_copy, 1)
    if old_copy_plan in text:
        return text.replace(old_copy_plan, new_copy_plan, 1)
    raise SystemExit("vfocus fillLane copy patch miss")


def patch_off_zero_and_dash(text: str) -> str:
    old_off = """      function offZeroRow6(groupNo) {
        var z = twZeroMoney();
        if (groupNo === 1) return [z, z, z, z, z, '0%'];
        if (groupNo === 2) {
          if (useJa) return ['0', '0', '0', '0', '0', '0'];
          return ['0', '0', '0', z, z, z];
        }
        return [z, z, z, z, z, z];
      }"""
    new_off = """      function offZeroRow6(groupNo) {
        var z = twZeroMoney();
        var n = typeof monthlyTwGroupRowCount === 'function' ? monthlyTwGroupRowCount(groupNo) : 6;
        if (groupNo === 1) {
          if (n === 4) return [z, z, z, '0%'];
          return [z, z, z, z, z, '0%'];
        }
        if (groupNo === 2) {
          if (!n) return [];
          if (useJa) return ['0', '0', '0', '0', '0', '0'].slice(0, n);
          return ['0', '0', '0', z, z, z].slice(0, n);
        }
        return [z, z, z, z, z, z].slice(0, n);
      }"""
    if "if (n === 4) return [z, z, z, '0%']" in text:
        pass
    elif old_off not in text:
        raise SystemExit("offZeroRow6 patch miss")
    else:
        text = text.replace(old_off, new_off, 1)
    old_dash_fn = """      function dashRow6() {
        return [
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_PCT,
        ];
      }"""
    new_dash_fn = """      function dashRow6(groupNo) {
        var n = typeof monthlyTwGroupRowCount === 'function' ? monthlyTwGroupRowCount(groupNo || 1) : 6;
        var row = [
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_PCT,
        ];
        if (groupNo === 1 && n === 4) return [TW_SKELETON_MONEY, TW_SKELETON_MONEY, TW_SKELETON_MONEY, TW_SKELETON_PCT];
        return row.slice(0, n);
      }"""
    if "function dashRow6(groupNo)" not in text:
        if old_dash_fn not in text:
            raise SystemExit("dashRow6 fn patch miss")
        text = text.replace(old_dash_fn, new_dash_fn, 1)
    old_dash_call = "          values = dashRow6();"
    new_dash_call = "          values = dashRow6(groupNo);"
    if old_dash_call in text:
        text = text.replace(old_dash_call, new_dash_call, 1)
    return text


def patch_rebuild_keep_focus(text: str) -> str:
    old = """      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();"""
    new = """      function monthlyTwRebuildKeepFocus() {
        if (typeof applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout();
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();"""
    if "applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout()" in text and "function monthlyTwRebuildKeepFocus" in text:
        if old in text:
            text = text.replace(old, new, 1)
        return text
    if old in text:
        text = text.replace(old, new, 1)
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_metrics_block(text)
    text = inject_diff_css(text)
    text = inject_5c5_css(text)
    text = inject_5c5_js(text)
    text = patch_5c5_runtime(text)
    if PROFIT_OLD in text:
        text = text.replace(PROFIT_OLD, PROFIT_NEW, 1)
    elif "resolveMonthlyProfitValue(iso)" in text:
        pass
    else:
        raise SystemExit(f"profit patch miss: {path}")
    if TEXT_OR_DEMO_OLD in text:
        text = text.replace(TEXT_OR_DEMO_OLD, TEXT_OR_DEMO_NEW, 1)
    text = patch_5c5_rebuild_and_listeners(text)
    if REBUILD_HOOK_OLD in text:
        text = text.replace(REBUILD_HOOK_OLD, REBUILD_HOOK_NEW, 1)
    elif REBUILD_HOOK_OLD_LOADED in text:
        text = text.replace(REBUILD_HOOK_OLD_LOADED, REBUILD_HOOK_NEW, 1)
    elif REBUILD_HOOK_LOADED_NO_LAYOUT in text:
        text = text.replace(REBUILD_HOOK_LOADED_NO_LAYOUT, REBUILD_HOOK_NEW, 1)
    elif "applyMonthlyTwBusinessTypeLayout === 'function') applyMonthlyTwBusinessTypeLayout()" in text:
        pass
    elif "invalidateGroup1TwCache()" in text:
        pass
    else:
        raise SystemExit(f"rebuild hook miss: {path}")
    text = patch_make_group_column(text)
    text = patch_vfocus_copy(text)
    text = inject_tw_listeners(text)
    text = patch_rebuild_keep_focus(text)
    text = patch_compute_metrics(text)
    text = patch_make_group_row_count(text)
    text = patch_hydrate_row_count(text)
    text = patch_ensure_group_shell(text)
    text = patch_vfocus_fill_lane(text)
    text = patch_off_zero_and_dash(text)
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

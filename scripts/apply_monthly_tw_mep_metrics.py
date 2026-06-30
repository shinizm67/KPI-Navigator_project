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


def inject_diff_css(text: str) -> str:
    if MONTHLY_TW_DIFF_CSS_MARKER in text:
        return text
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

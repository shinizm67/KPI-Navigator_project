#!/usr/bin/env python3
"""Unit 5B: isolate PL Analyze refresh from bottom-graph refresh."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_pl_analyze_business_type import patch_html as patch_analyze_bt
from pl_bottom_graph_data_client import pl_bottom_graph_data_client_js

ROOT = Path(__file__).resolve().parents[1]

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]

GRAPH_BEGIN = "      /* === UNIT-5B-GRAPH-REFRESH-GUARD-BEGIN === */"
GRAPH_END = "      /* === UNIT-5B-GRAPH-REFRESH-GUARD-END === */"

OLD_GRAPH_FN = """      function refreshPlBottomGraph() {
        var months = plGraphCollectMonths();
        plGraphApplyExpensesSummary(months);
        if (typeof window.plGraphRender !== 'function') return;
        if (!months) return;
        window.plGraphRender(months);
      }

      window.__plRefreshBottomGraph = refreshPlBottomGraph;"""

CHAIN_5 = """        if (typeof refreshAnalyzeBlock === 'function') refreshAnalyzeBlock();
        if (typeof refreshPlRatios === 'function') refreshPlRatios();
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
        if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
        if (typeof refreshPlBottomGraph === 'function') refreshPlBottomGraph();"""

CHAIN_5_INDENTED = """            if (typeof refreshAnalyzeBlock === 'function') refreshAnalyzeBlock();
            if (typeof refreshPlRatios === 'function') refreshPlRatios();
            if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
            if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
            if (typeof refreshPlBottomGraph === 'function') refreshPlBottomGraph();"""

LIVE_TIMER = """          if (typeof refreshPlRatios === 'function') refreshPlRatios();
          if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
          if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
          if (typeof refreshPlBottomGraph === 'function') refreshPlBottomGraph();"""

BOOT_OLD = """      if (typeof refreshIncomeBlock === 'function') {
        refreshIncomeBlock();
      }
      if (typeof refreshAnalyzeBlock === 'function') {
        refreshAnalyzeBlock();
      }
      if (typeof refreshPlRatios === 'function') {
        refreshPlRatios();
      }
      if (typeof refreshPlYearTotals === 'function') {
        refreshPlYearTotals();
      }
      if (typeof refreshPlReferenceBudget === 'function') {
        refreshPlReferenceBudget();
      }
      if (typeof refreshPlBottomGraph === 'function') {
        refreshPlBottomGraph();
      }"""

INCOME_SURFACES_OLD = """      function plRefreshAllIncomeSurfaces() {
        if (typeof refreshIncomeBlock === 'function') refreshIncomeBlock();
        if (typeof refreshAnalyzeBlock === 'function') refreshAnalyzeBlock();
        if (typeof fillDailyExpenseRowsFromMep === 'function') fillDailyExpenseRowsFromMep();
        if (typeof refreshPlRatios === 'function') refreshPlRatios();
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
        if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
        if (typeof refreshPlBottomGraph === 'function') refreshPlBottomGraph();
      }"""

LIVE_SURFACES_OLD = """      function refreshPlExpenseLiveSurfaces() {
        if (typeof refreshAnalyzeBlock === 'function') refreshAnalyzeBlock();
        if (typeof refreshPlRatios === 'function') refreshPlRatios();
        if (typeof refreshPlYearTotals === 'function') refreshPlYearTotals();
        if (typeof refreshPlReferenceBudget === 'function') refreshPlReferenceBudget();
        if (typeof refreshPlBottomGraph === 'function') refreshPlBottomGraph();
      }"""


def _guard_block() -> str:
    js = pl_bottom_graph_data_client_js()
    start = js.index(GRAPH_BEGIN)
    stop = js.index(GRAPH_END) + len(GRAPH_END)
    return js[start:stop]


def _replace_marked(text: str, begin: str, end: str, block: str) -> str:
    start = text.index(begin)
    stop = text.index(end) + len(end)
    return text[:start] + block.rstrip("\n") + text[stop:]


def patch_graph_guard(text: str) -> str:
    block = _guard_block()
    if GRAPH_BEGIN in text and GRAPH_END in text:
        text = _replace_marked(text, GRAPH_BEGIN, GRAPH_END, block)
    elif OLD_GRAPH_FN in text:
        text = text.replace(OLD_GRAPH_FN, block, 1)
    else:
        raise SystemExit("graph refresh function anchor missing")

    text = text.replace(CHAIN_5_INDENTED, "            plRefreshAnalyzeAndGraph();")
    text = text.replace(CHAIN_5, "        plRefreshAnalyzeAndGraph();")
    text = text.replace(
        LIVE_TIMER,
        """          plSafeRefresh(refreshPlRatios);
          plSafeRefresh(refreshPlYearTotals);
          plSafeRefresh(refreshPlReferenceBudget);
          plSafeRefresh(refreshPlBottomGraph);""",
    )
    text = text.replace(LIVE_SURFACES_OLD, """      function refreshPlExpenseLiveSurfaces() {
        plRefreshAnalyzeAndGraph();
      }""")
    text = text.replace(
        INCOME_SURFACES_OLD,
        """      function plRefreshAllIncomeSurfaces() {
        plSafeRefresh(refreshIncomeBlock);
        plSafeRefresh(refreshAnalyzeBlock);
        plSafeRefresh(fillDailyExpenseRowsFromMep);
        plSafeRefresh(refreshPlRatios);
        plSafeRefresh(refreshPlYearTotals);
        plSafeRefresh(refreshPlReferenceBudget);
        plSafeRefresh(refreshPlBottomGraph);
      }""",
    )
    text = text.replace(
        BOOT_OLD,
        """      plSafeRefresh(refreshIncomeBlock);
      plRefreshAnalyzeAndGraph();""",
    )
    text = text.replace(
        "if (typeof refreshAnalyzeBlock === 'function') refreshAnalyzeBlock();",
        "plSafeRefresh(refreshAnalyzeBlock);",
    )
    text = text.replace(
        "if (typeof refreshPlBottomGraph === 'function') refreshPlBottomGraph();",
        "plSafeRefresh(refreshPlBottomGraph);",
    )
    return text


def main() -> None:
    for path in PL_PAGES:
        original = path.read_text(encoding="utf-8")
        updated = patch_analyze_bt(original)
        updated = patch_graph_guard(updated)
        if updated == original:
            print(f"unchanged {path.relative_to(ROOT).as_posix()}")
            continue
        path.write_text(updated, encoding="utf-8", newline="\n")
        print(f"patched {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()

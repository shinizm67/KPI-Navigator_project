#!/usr/bin/env python3
"""Insight — Summary Comparison 比較バー（過去平均）を実データ化."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402
from insight_diff_client import (  # noqa: E402
    INSIGHT_DIFF_JS_END,
    INSIGHT_DIFF_JS_MARKER,
    INSIGHT_OVERLAY_IIFE,
    insight_diff_js,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "setSummaryComparisonAllocWidget"

ANNUAL_WIDGET_OLD = """      initAllocationWidget({
        graphId: 'insight-annual-comparison-alloc-graph',
        dataKey: 'insightAnnualComparisonPercent',
        graphWidth: 654,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 85
      });"""

ANNUAL_WIDGET_NEW = """      window.__insightSummaryComparisonWidgets = window.__insightSummaryComparisonWidgets || {};
      window.__insightSummaryComparisonWidgets.annual = initAllocationWidget({
        graphId: 'insight-annual-comparison-alloc-graph',
        dataKey: 'insightAnnualComparisonPercent',
        graphWidth: 654,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 85
      });"""

# Monthly comparison bar had no widget init — insert before annual comparison widget.
MONTHLY_WIDGET_INSERT = """      window.__insightSummaryComparisonWidgets = window.__insightSummaryComparisonWidgets || {};
      window.__insightSummaryComparisonWidgets.monthly = initAllocationWidget({
        graphId: 'insight-monthly-comparison-alloc-graph',
        dataKey: 'insightMonthlyComparisonPercent',
        graphWidth: 654,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 85
      });
"""


def inject_insight_diff_js(text: str) -> str:
    block = insight_diff_js().rstrip() + "\n"
    if INSIGHT_DIFF_JS_MARKER not in text:
        pos = text.find(INSIGHT_OVERLAY_IIFE)
        if pos < 0:
            raise SystemExit("insight-overlay IIFE anchor miss")
        return text[:pos] + block + text[pos:]
    pattern = (
        re.escape(INSIGHT_DIFF_JS_MARKER)
        + r"[\s\S]*?"
        + re.escape(INSIGHT_DIFF_JS_END)
        + r"\n?"
    )
    return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)


def patch_widgets(text: str) -> str:
    if "window.__insightSummaryComparisonWidgets.annual" not in text:
        if ANNUAL_WIDGET_OLD not in text:
            raise SystemExit("annual comparison alloc widget miss")
        text = text.replace(ANNUAL_WIDGET_OLD, ANNUAL_WIDGET_NEW, 1)
    if "window.__insightSummaryComparisonWidgets.monthly" not in text:
        anchor = "window.__insightSummaryComparisonWidgets.annual = initAllocationWidget({"
        if anchor not in text:
            raise SystemExit("annual comparison widget anchor miss for monthly insert")
        text = text.replace(anchor, MONTHLY_WIDGET_INSERT + "\n      " + anchor, 1)
    return text


def patch_page(path: Path) -> None:
    patch_focus_tw(path)
    text = path.read_text(encoding="utf-8")
    text = inject_insight_diff_js(text)
    text = patch_widgets(text)
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing: {path}")
    if "insight-monthly-comparison-alloc-graph" not in text:
        raise SystemExit(f"monthly comparison graph id missing: {path}")
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

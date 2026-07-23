#!/usr/bin/env python3
"""Insight Summary — Today(Sales)/Target 棒 + Annual 最下段 Historical Avg を日付追従させる."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

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

# graphId -> registry assignment (array push or single)
SALES_GRAPH_IDS = {
    "insight-daily-alloc-graph": "daily",
    "insight-analyze-daily-alloc-graph": "daily",
    "insight-monthly-alloc-graph": "monthly",
    "insight-analyze-monthly-sales-alloc-graph": "monthly",
    "insight-graph-monthly-sales-alloc-graph": "monthly",
    "insight-annual-alloc-graph": "annual",
    "insight-analyze-annual-sales-alloc-graph": "annual",
    "insight-graph-annual-sales-alloc-graph": "annual",
}

REVISION_GRAPH_ID = "insight-annual-target-revision-alloc-graph"

# Analyze / Graph Current Progress 下段 Historical Avg（annual と同式）
ANALYZE_PROGRESS_GRAPH_IDS = [
    "insight-analyze-annual-current-progress-alloc-graph",
    "insight-graph-annual-current-progress-alloc-graph",
]

INIT_WIDGET_RE_TMPL = (
    r"initAllocationWidget\(\{\n"
    r"        graphId: 'GID',\n"
    r"(?:.*\n)*?"
    r"      \}\);"
)


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


def wrap_sales_widget(text: str, graph_id: str, key: str) -> str:
    """Wrap one initAllocationWidget into __insightSummarySalesWidgets[key] array push."""
    marker = f"__insightSummarySalesWidgets.{key}"
    push_pat = re.compile(
        rf"{re.escape(marker)}\.push\(initAllocationWidget\(\{{\n"
        rf"        graphId: '{re.escape(graph_id)}',"
    )
    if push_pat.search(text):
        return text

    pat = re.compile(INIT_WIDGET_RE_TMPL.replace("GID", re.escape(graph_id)))
    m = pat.search(text)
    if not m:
        # optional graph-pane copies may be absent on some pages
        if graph_id.startswith("insight-graph-"):
            return text
        raise SystemExit(f"sales widget miss: {graph_id}")

    ensure = (
        "window.__insightSummarySalesWidgets = window.__insightSummarySalesWidgets || {};\n"
        f"      window.__insightSummarySalesWidgets.{key} = "
        f"window.__insightSummarySalesWidgets.{key} || [];\n"
        f"      window.__insightSummarySalesWidgets.{key}.push("
    )
    old = m.group(0)
    # initAllocationWidget({...}); -> ensure + push(initAllocationWidget({...}));
    new = ensure + old[:-1] + ");"
    return text[: m.start()] + new + text[m.end() :]


def wrap_revision_widget(text: str) -> str:
    if "__insightSummaryComparisonWidgets.annualRevision" in text:
        return text
    pat = re.compile(INIT_WIDGET_RE_TMPL.replace("GID", re.escape(REVISION_GRAPH_ID)))
    m = pat.search(text)
    if not m:
        raise SystemExit("revision widget miss")
    old = m.group(0)
    new = (
        "window.__insightSummaryComparisonWidgets = window.__insightSummaryComparisonWidgets || {};\n"
        "      window.__insightSummaryComparisonWidgets.annualRevision = "
        + old
    )
    return text[: m.start()] + new + text[m.end() :]


def wrap_analyze_progress_widget(text: str, graph_id: str) -> str:
    """Register Analyze/Graph Current Progress hist bar onto annualAnalyzeProgress[]."""
    marker = "__insightSummaryComparisonWidgets.annualAnalyzeProgress"
    push_pat = re.compile(
        rf"{re.escape(marker)}\.push\(initAllocationWidget\(\{{\n"
        rf"        graphId: '{re.escape(graph_id)}',"
    )
    if push_pat.search(text):
        return text

    pat = re.compile(INIT_WIDGET_RE_TMPL.replace("GID", re.escape(graph_id)))
    m = pat.search(text)
    if not m:
        if graph_id.startswith("insight-graph-"):
            return text
        raise SystemExit(f"analyze progress widget miss: {graph_id}")

    ensure = (
        "window.__insightSummaryComparisonWidgets = window.__insightSummaryComparisonWidgets || {};\n"
        f"      {marker} = {marker} || [];\n"
        f"      {marker}.push("
    )
    old = m.group(0)
    new = ensure + old[:-1] + ");"
    return text[: m.start()] + new + text[m.end() :]


def patch_widgets(text: str) -> str:
    for gid, key in SALES_GRAPH_IDS.items():
        text = wrap_sales_widget(text, gid, key)
    text = wrap_revision_widget(text)
    for gid in ANALYZE_PROGRESS_GRAPH_IDS:
        text = wrap_analyze_progress_widget(text, gid)
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_insight_diff_js(text)
    text = patch_widgets(text)
    checks = [
        "patchSummarySalesAllocBars",
        "setSummarySalesAllocWidget",
        "patchAnnualHistAvgAlloc",
        "annualAnalyzeProgress",
        "__insightSummarySalesWidgets.daily",
        "__insightSummarySalesWidgets.monthly",
        "__insightSummarySalesWidgets.annual",
        "annualRevision",
        "widgets.annualRevision",
        "widgets.annualAnalyzeProgress",
    ]
    for needle in checks:
        if needle not in text:
            raise SystemExit(f"missing {needle}: {path}")
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

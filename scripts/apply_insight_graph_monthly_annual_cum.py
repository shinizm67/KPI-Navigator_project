#!/usr/bin/env python3
"""Insight — Graph → Monthly / Annual 累計横棒（caps/%）を実データ化."""

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

MARKER = "patchGraphMonthlyAnnualCumBars"

MONTHLY_OLD = """      initAllocationWidget({
        graphId: 'insight-graph-monthly-cumulative-target-actual',
        percentId: 'insight-graph-monthly-cumulative-target-actual-pct',
        dataKey: 'achievementPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 123
      });"""

MONTHLY_NEW = """      window.__insightGraphCumWidgets = window.__insightGraphCumWidgets || {};
      window.__insightGraphCumWidgets.monthly = initAllocationWidget({
        graphId: 'insight-graph-monthly-cumulative-target-actual',
        percentId: 'insight-graph-monthly-cumulative-target-actual-pct',
        dataKey: 'achievementPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 123
      });"""

ANNUAL_OLD = """      initAllocationWidget({
        graphId: 'insight-graph-annual-cumulative-target-actual',
        percentId: 'insight-graph-annual-cumulative-target-actual-pct',
        dataKey: 'achievementPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 123
      });"""

ANNUAL_NEW = """      window.__insightGraphCumWidgets = window.__insightGraphCumWidgets || {};
      window.__insightGraphCumWidgets.annual = initAllocationWidget({
        graphId: 'insight-graph-annual-cumulative-target-actual',
        percentId: 'insight-graph-annual-cumulative-target-actual-pct',
        dataKey: 'achievementPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 123
      });"""


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
    if "window.__insightGraphCumWidgets.monthly" not in text:
        if MONTHLY_OLD not in text:
            raise SystemExit("monthly cum widget miss")
        text = text.replace(MONTHLY_OLD, MONTHLY_NEW, 1)
    if "window.__insightGraphCumWidgets.annual" not in text:
        if ANNUAL_OLD not in text:
            raise SystemExit("annual cum widget miss")
        text = text.replace(ANNUAL_OLD, ANNUAL_NEW, 1)
    return text


def patch_page(path: Path) -> None:
    patch_focus_tw(path)
    text = path.read_text(encoding="utf-8")
    text = inject_insight_diff_js(text)
    text = patch_widgets(text)
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing: {path}")
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

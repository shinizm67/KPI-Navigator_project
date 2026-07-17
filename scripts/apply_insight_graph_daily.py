#!/usr/bin/env python3
"""Insight — Graph → Daily（目標対実績 / 去年同曜日 / 過去同曜日）を実データ化."""

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

MARKER = "patchGraphDailyBlocks"

WIDGET_TARGET_OLD = """      initAllocationWidget({
        graphId: 'insight-graph-daily-target-actual',
        percentId: 'insight-graph-daily-target-actual-pct',
        dataKey: 'achievementPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 89
      });"""

WIDGET_TARGET_NEW = """      window.__insightGraphDailyWidgets = window.__insightGraphDailyWidgets || {};
      window.__insightGraphDailyWidgets.targetActual = initAllocationWidget({
        graphId: 'insight-graph-daily-target-actual',
        percentId: 'insight-graph-daily-target-actual-pct',
        dataKey: 'achievementPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 89
      });"""

WIDGET_LAST_YEAR_OLD = """      initAllocationWidget({
        graphId: 'insight-graph-daily-last-year-weekday',
        percentId: 'insight-graph-daily-last-year-weekday-pct',
        dataKey: 'insightDailySalesVsHistoricalPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 118
      });"""

WIDGET_LAST_YEAR_NEW = """      window.__insightGraphDailyWidgets = window.__insightGraphDailyWidgets || {};
      window.__insightGraphDailyWidgets.lastYearWeekday = initAllocationWidget({
        graphId: 'insight-graph-daily-last-year-weekday',
        percentId: 'insight-graph-daily-last-year-weekday-pct',
        dataKey: 'insightDailySalesVsHistoricalPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 118
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
    if "window.__insightGraphDailyWidgets.targetActual" not in text:
        if WIDGET_TARGET_OLD not in text:
            raise SystemExit("graph-daily target-actual widget miss")
        text = text.replace(WIDGET_TARGET_OLD, WIDGET_TARGET_NEW, 1)
    if "window.__insightGraphDailyWidgets.lastYearWeekday" not in text:
        if WIDGET_LAST_YEAR_OLD not in text:
            raise SystemExit("graph-daily last-year-weekday widget miss")
        text = text.replace(WIDGET_LAST_YEAR_OLD, WIDGET_LAST_YEAR_NEW, 1)
    return text


def patch_page(path: Path) -> None:
    patch_focus_tw(path)
    text = path.read_text(encoding="utf-8")
    text = inject_insight_diff_js(text)
    text = patch_widgets(text)
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing: {path}")
    if "__sameWeekdayIso" not in text:
        raise SystemExit(f"__sameWeekdayIso missing: {path}")
    if "__readTwDaySales" not in text:
        raise SystemExit(f"__readTwDaySales missing: {path}")
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

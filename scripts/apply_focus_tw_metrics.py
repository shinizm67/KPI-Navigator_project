#!/usr/bin/env python3
"""Wire Focus Bar / Table Window metrics (plan target vs timeline actual)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from focus_tw_metrics_client import (  # noqa: E402
    FOCUS_BAR_REFRESH_NEW,
    FOCUS_BAR_REFRESH_OLD,
    FOCUS_TW_END,
    FOCUS_TW_LISTENERS_NEW,
    FOCUS_TW_LISTENERS_OLD,
    FOCUS_TW_MARKER,
    RENDER_TIMELINE_OLD,
    focus_tw_metrics_js,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

RENDER_TIMELINE_END = "        document.dispatchEvent(new CustomEvent('annual:timelineRowsRendered'));\n      }"


def replace_timeline_render(text: str) -> str:
    block = focus_tw_metrics_js().rstrip() + "\n"
    if FOCUS_TW_MARKER in text:
        pattern = (
            re.escape(FOCUS_TW_MARKER) + r"[\s\S]*?" + re.escape(FOCUS_TW_END) + r"\n?"
        )
        return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
    start = text.find(RENDER_TIMELINE_OLD)
    if start < 0:
        if "buildDailyTargetMapForYear" in text:
            return text
        raise SystemExit("renderAnnualDailyTimeline block start not found")
    end = text.find(RENDER_TIMELINE_END, start)
    if end < 0:
        raise SystemExit("renderAnnualDailyTimeline block end not found")
    end += len(RENDER_TIMELINE_END)
    return text[:start] + block + text[end:]


def replace_listeners(text: str) -> str:
    if FOCUS_TW_LISTENERS_OLD in text:
        return text.replace(FOCUS_TW_LISTENERS_OLD, FOCUS_TW_LISTENERS_NEW, 1)
    if "document.addEventListener('annual:pastSalesSaved'" in text and "kpi:annualPlanChanged" in text:
        return text
    anchor = """      document.addEventListener('annual:salesDataSaved', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);"""
    past_block = """      document.addEventListener('annual:pastSalesSaved', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastSalesMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastBusinessDayMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);"""
    if anchor in text:
        return text.replace(anchor, past_block, 1)
    if "kpi:annualPlanChanged" in text and "annual:salesDataSaved" in text:
        return text
    raise SystemExit("focus TW listener patch miss")


def replace_focus_bar_refresh(text: str) -> str:
    if FOCUS_BAR_REFRESH_OLD in text:
        return text.replace(FOCUS_BAR_REFRESH_OLD, FOCUS_BAR_REFRESH_NEW, 1)
    if "annual:timelineRowsRendered" in text and "refreshLower" in text:
        return text
    raise SystemExit("focus bar refresh patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_timeline_render(text)
    text = replace_listeners(text)
    text = replace_focus_bar_refresh(text)
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

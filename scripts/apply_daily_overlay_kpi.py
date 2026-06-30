#!/usr/bin/env python3
"""Wire Daily Floating Window KPIs to KpiYearStore / TW metrics."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402
from daily_overlay_kpi_client import (  # noqa: E402
    DAILY_OVERLAY_KPI_END,
    DAILY_OVERLAY_KPI_MARKER,
    FILL_NEW,
    FILL_OLD,
    FILL_WITH_RENDER_OLD,
    OPEN_MONTHLY_NEW,
    OPEN_MONTHLY_OLD,
    OPEN_NEW,
    OPEN_OLD,
    OVERLAY_LISTENERS_ANCHOR,
    OVERLAY_LISTENERS_NEW,
    daily_overlay_kpi_js,
)
from focus_tw_metrics_client import FOCUS_TW_END, FOCUS_TW_MARKER  # noqa: E402

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

DAILY_OVERLAY_IIFE = "    (function () {\n      var root = document.getElementById('daily-overlay');"


def ensure_compute_fn(text: str) -> str:
    if "__computeTwMetricsForIso" in text:
        return text
    if FOCUS_TW_MARKER not in text:
        raise SystemExit("KPI-FOCUS-TW-METRICS block missing — run apply_focus_tw_metrics first")
    block_end = text.find(FOCUS_TW_END)
    if block_end < 0:
        raise SystemExit("KPI-FOCUS-TW-METRICS end marker missing")
    raise SystemExit("__computeTwMetricsForIso missing — re-run apply_focus_tw_metrics.py")


def inject_overlay_kpi_block(text: str) -> str:
    block = daily_overlay_kpi_js().rstrip() + "\n"
    if DAILY_OVERLAY_KPI_MARKER in text:
        pattern = (
            re.escape(DAILY_OVERLAY_KPI_MARKER)
            + r"[\s\S]*?"
            + re.escape(DAILY_OVERLAY_KPI_END)
            + r"\n?"
        )
        return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
    pos = text.find(DAILY_OVERLAY_IIFE)
    if pos < 0:
        raise SystemExit("daily-overlay IIFE anchor not found")
    return text[:pos] + block + text[pos:]


def patch_open(text: str) -> str:
    if OPEN_NEW in text or OPEN_MONTHLY_NEW in text:
        return text
    if OPEN_OLD in text:
        return text.replace(OPEN_OLD, OPEN_NEW, 1)
    if OPEN_MONTHLY_OLD in text:
        return text.replace(OPEN_MONTHLY_OLD, OPEN_MONTHLY_NEW, 1)
    raise SystemExit("daily-overlay open() patch miss")


def patch_fill(text: str) -> str:
    if FILL_NEW in text:
        text = text
    elif FILL_WITH_RENDER_OLD in text:
        text = text.replace(FILL_WITH_RENDER_OLD, FILL_NEW, 1)
    elif FILL_OLD in text:
        text = text.replace(FILL_OLD, FILL_NEW, 1)
    else:
        raise SystemExit("daily-overlay fill() patch miss")
    return patch_open(text)


def patch_overlay_listeners(text: str) -> str:
    if "refreshDailyOverlayFromStore" in text:
        return text
    if OVERLAY_LISTENERS_ANCHOR in text:
        return text.replace(OVERLAY_LISTENERS_ANCHOR, OVERLAY_LISTENERS_NEW, 1)
    raise SystemExit("daily-overlay listeners patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = ensure_compute_fn(text)
    text = inject_overlay_kpi_block(text)
    text = patch_fill(text)
    text = patch_overlay_listeners(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_focus_tw(path)
    for path in PAGES:
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

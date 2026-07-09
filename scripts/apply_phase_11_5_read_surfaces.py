#!/usr/bin/env python3
"""Phase 11-5 — wire Focus Bar / Daily FW read surfaces to weekday target resolver refresh."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_cockpit_refresh import patch_page as patch_cockpit  # noqa: E402
from apply_daily_overlay_kpi import patch_page as patch_daily_overlay  # noqa: E402
from apply_diff_step3 import patch_page as patch_insight_diff  # noqa: E402
from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402
from focus_bar_read_surfaces_client import (  # noqa: E402
    FOCUS_BAR_READ_SURFACES_MARKER,
    FOCUS_BAR_REFRESH_AFTER_115,
    FOCUS_BAR_REFRESH_BEFORE_115,
    GRAPH_LISTENERS_AFTER_115,
    GRAPH_LISTENERS_BEFORE_115,
    GRAPH_POPOVER_INJECT_NEW,
    GRAPH_POPOVER_INJECT_OLD,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def patch_focus_bar_refresh(text: str) -> str:
    if FOCUS_BAR_READ_SURFACES_MARKER in text:
        return text
    if FOCUS_BAR_REFRESH_BEFORE_115 in text:
        return text.replace(FOCUS_BAR_REFRESH_BEFORE_115, FOCUS_BAR_REFRESH_AFTER_115, 1)
    if "kpi:dailyTargetModeChanged', function () {\n        setTimeout(refreshLower" in text:
        return text
    raise SystemExit("Focus Bar refreshLower Phase 11-5 patch miss")


def patch_graph_listeners(text: str) -> str:
    if "kpi:dailyTargetModeChanged', refreshGraphPopoverFromStore" in text:
        return text
    if GRAPH_LISTENERS_BEFORE_115 in text:
        return text.replace(GRAPH_LISTENERS_BEFORE_115, GRAPH_LISTENERS_AFTER_115, 1)
    if GRAPH_POPOVER_INJECT_OLD in text:
        return text.replace(GRAPH_POPOVER_INJECT_OLD, GRAPH_POPOVER_INJECT_NEW, 1)
    if "refreshGraphPopoverFromStore" in text:
        raise SystemExit("graph popover listeners present but Phase 11-5 upgrade miss")
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_focus_bar_refresh(text)
    text = patch_graph_listeners(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote 11-5 {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_focus_tw(path)
        patch_daily_overlay(path)
        patch_insight_diff(path)
        patch_cockpit(path)
    for path in PAGES:
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

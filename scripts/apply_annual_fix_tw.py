#!/usr/bin/env python3
"""Annual-only fixes: TW row render (fill-state helpers) + hide obsolete TW Edit button."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from focus_bar_timeline_scroll_client import FILL_STATE_HELPERS  # noqa: E402
from focus_tw_metrics_client import FOCUS_TW_MARKER  # noqa: E402

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

HIDE_EDIT_CSS = """
    /* Annual: sales entry via cockpit Sales Data — not TW Global Menu Edit */
    body.profile-page:not(.monthly-page) .annual-daily-focus-edit-btn {
      display: none !important;
      pointer-events: none;
    }
    body.profile-page:not(.monthly-page).annual-focus-bar-expanded .annual-daily-focus-edit-btn::after {
      content: none !important;
      display: none !important;
    }
"""


def inject_fill_helpers(text: str) -> str:
    if "function applyDailyCellFillState" in text:
        return text
    if FOCUS_TW_MARKER not in text:
        raise SystemExit("KPI-FOCUS-TW-METRICS marker missing")
    return text.replace(FOCUS_TW_MARKER, FOCUS_TW_MARKER + FILL_STATE_HELPERS, 1)


def inject_hide_edit_css(text: str) -> str:
    if "Annual: sales entry via cockpit Sales Data" in text:
        return text
    anchor = "    .annual-daily-focus-edit-btn {"
    if anchor not in text:
        raise SystemExit("edit btn CSS anchor missing")
    return text.replace(anchor, HIDE_EDIT_CSS + anchor, 1)


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        text = inject_fill_helpers(text)
        text = inject_hide_edit_css(text)
        if "function applyDailyCellFillState" not in text:
            raise SystemExit(f"fill helpers not applied: {path}")
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

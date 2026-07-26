#!/usr/bin/env python3
"""Apply Daily FW Office Mode shell CSS (Insight-matched) to Annual/Monthly JA/EN."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from daily_overlay_office_client import (  # noqa: E402
    MARKER,
    MARKER_END,
    PANEL_OFFICE_NEW,
    PANEL_OFFICE_OLD,
    STICKY_HEAD_NEW,
    STICKY_HEAD_OLD,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def apply(text: str) -> str:
    if STICKY_HEAD_OLD in text:
        text = text.replace(STICKY_HEAD_OLD, STICKY_HEAD_NEW, 1)

    if MARKER in text and MARKER_END in text:
        text = re.sub(
            re.escape(MARKER) + r"[\s\S]*?" + re.escape(MARKER_END),
            PANEL_OFFICE_NEW.strip(),
            text,
            count=1,
        )
        return text

    if PANEL_OFFICE_OLD in text:
        return text.replace(PANEL_OFFICE_OLD, PANEL_OFFICE_NEW, 1)

    # Already partially patched with old cyan office panel — replace that rule
    cyan_panel = re.search(
        r"    \.office-mode \.daily-overlay__panel \{\n"
        r"      border-color: rgba\(88, 225, 243, 0\.75\);\n"
        r"      box-shadow: 0 0 20px rgba\(88, 225, 243, 0\.18\);\n"
        r"    \}",
        text,
    )
    if cyan_panel:
        return text[: cyan_panel.start()] + PANEL_OFFICE_NEW + text[cyan_panel.end() :]

    raise ValueError("panel office block not found")


def main() -> int:
    for path in PAGES:
        raw = path.read_text(encoding="utf-8")
        try:
            updated = apply(raw)
        except ValueError as exc:
            print(f"FAIL {path.relative_to(ROOT)}: {exc}")
            return 1
        if updated != raw:
            path.write_text(updated, encoding="utf-8")
            print(f"updated: {path.relative_to(ROOT)}")
        else:
            print(f"unchanged: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Apply Daily FW Office Mode monotone CSS to Annual/Monthly JA/EN index.html."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from daily_overlay_office_client import (  # noqa: E402
    MARKER,
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
    if MARKER in text:
        return text
    if STICKY_HEAD_OLD in text:
        text = text.replace(STICKY_HEAD_OLD, STICKY_HEAD_NEW, 1)
    if PANEL_OFFICE_OLD not in text:
        raise ValueError("panel office block not found")
    return text.replace(PANEL_OFFICE_OLD, PANEL_OFFICE_NEW, 1)


def main() -> int:
    for path in PAGES:
        raw = path.read_text(encoding="utf-8")
        updated = apply(raw)
        if updated != raw:
            path.write_text(updated, encoding="utf-8")
            print(f"updated: {path.relative_to(ROOT)}")
        else:
            print(f"unchanged: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

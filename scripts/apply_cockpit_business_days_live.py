#!/usr/bin/env python3
"""Cockpit Business Days live preview from Sales Data modal checkboxes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cockpit_business_days_live_client import (  # noqa: E402
    CB_CHANGE_AFTER,
    CB_CHANGE_BEFORE,
    CLOSE_MODAL_NEW,
    CLOSE_MODAL_OLD,
    RESOLVE_BMAP_NEW,
    RESOLVE_BMAP_OLD,
    UI_EXPOSE_NEW,
    UI_EXPOSE_OLD,
    YEAR_SYNC_RESOLVE_NEW,
    YEAR_SYNC_RESOLVE_OLD,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_annual = "/annual/" in str(path)

    if RESOLVE_BMAP_OLD in text:
        text = text.replace(RESOLVE_BMAP_OLD, RESOLVE_BMAP_NEW, 1)
    elif "modalLive" not in text.split("resolveBusinessDayMapForCockpit")[1][:400]:
        raise SystemExit(f"resolveBusinessDayMapForCockpit patch missing: {path}")

    if YEAR_SYNC_RESOLVE_OLD in text:
        text = text.replace(YEAR_SYNC_RESOLVE_OLD, YEAR_SYNC_RESOLVE_NEW, 1)

    if UI_EXPOSE_OLD in text and UI_EXPOSE_NEW.split("\n")[-1] not in text:
        text = text.replace(UI_EXPOSE_OLD, UI_EXPOSE_NEW, 1)

    if is_annual:
        if CB_CHANGE_BEFORE in text:
            text = text.replace(CB_CHANGE_BEFORE, CB_CHANGE_AFTER, 1)
        elif "syncBusinessDayDisplayFromDailyMap();" not in text.split("salesDataRowApplyOffState")[1][:500]:
            raise SystemExit(f"checkbox cockpit sync missing: {path}")

        if CLOSE_MODAL_OLD in text:
            text = text.replace(CLOSE_MODAL_OLD, CLOSE_MODAL_NEW, 1)

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

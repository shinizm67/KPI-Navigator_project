#!/usr/bin/env python3
"""Phase 11 perf — re-apply Store + TW bulk target map after weekday-weighted regression."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402
from apply_monthly_load_perf import (  # noqa: E402
    BOUNDS_USE_NEW,
    BOUNDS_USE_OLD,
    RENDER_FLAGS_NEW,
    RENDER_FLAGS_OLD,
)
from apply_weekday_target_section import patch_page as patch_weekday_store  # noqa: E402

STORE_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

TW_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MONTHLY_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def patch_monthly_bounds(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if BOUNDS_USE_OLD in text:
        text = text.replace(BOUNDS_USE_OLD, BOUNDS_USE_NEW, 1)
    elif "boundsHint === 'anchor-year-only'" not in text:
        raise SystemExit(f"bounds use patch miss: {path}")
    if RENDER_FLAGS_OLD in text:
        text = text.replace(RENDER_FLAGS_OLD, RENDER_FLAGS_NEW, 1)
    elif "__monthlyVerticalTwPartialRendered = true" not in text:
        raise SystemExit(f"render flags patch miss: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote bounds {path.relative_to(ROOT)}")


def main() -> int:
    for path in STORE_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        text = patch_weekday_store(text)
        path.write_text(text, encoding="utf-8")
        print(f"wrote store {path.relative_to(ROOT)}")
    for path in TW_PAGES:
        patch_focus_tw(path)
    for path in MONTHLY_PAGES:
        patch_monthly_bounds(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

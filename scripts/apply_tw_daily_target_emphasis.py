#!/usr/bin/env python3
"""Inject TW daily Target Sales column emphasis CSS (Annual + Monthly, JA + EN)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402
from tw_daily_target_emphasis_client import (  # noqa: E402
    TW_DAILY_TARGET_EMPHASIS_ANCHOR,
    TW_DAILY_TARGET_EMPHASIS_END,
    TW_DAILY_TARGET_EMPHASIS_MARKER,
    tw_daily_target_emphasis_css,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def inject_css(text: str) -> str:
    block = tw_daily_target_emphasis_css().rstrip() + "\n"
    if TW_DAILY_TARGET_EMPHASIS_MARKER in text:
        pattern = (
            re.escape(TW_DAILY_TARGET_EMPHASIS_MARKER)
            + r"[\s\S]*?"
            + re.escape(TW_DAILY_TARGET_EMPHASIS_END)
            + r"\n?"
        )
        return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
    if TW_DAILY_TARGET_EMPHASIS_ANCHOR not in text:
        raise SystemExit("KPI-TW-DIFF-SEVERITY anchor missing")
    return text.replace(
        TW_DAILY_TARGET_EMPHASIS_ANCHOR,
        TW_DAILY_TARGET_EMPHASIS_ANCHOR + "\n" + block.rstrip(),
        1,
    )


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_css(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote CSS {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_focus_tw(path)
        print(f"wrote TW JS {path.relative_to(ROOT)}")
    for path in PAGES:
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

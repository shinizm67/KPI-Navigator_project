#!/usr/bin/env python3
"""Re-inject KPI-FOCUS-TW-METRICS block only (phase 3 facts read)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from focus_tw_metrics_client import FOCUS_TW_END, FOCUS_TW_MARKER, focus_tw_metrics_js  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]


def patch(text: str) -> str:
    if FOCUS_TW_MARKER not in text:
        raise SystemExit("KPI-FOCUS-TW-METRICS marker missing")
    pattern = (
        re.escape(FOCUS_TW_MARKER) + r"[\s\S]*?" + re.escape(FOCUS_TW_END) + r"\n?"
    )
    block = focus_tw_metrics_js().rstrip() + "\n"
    if not re.search(pattern, text):
        raise SystemExit("KPI-FOCUS-TW-METRICS block boundary not matched")
    return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        path.write_text(patch(text), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

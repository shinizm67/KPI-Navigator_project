#!/usr/bin/env python3
"""Wire Annual page Cockpit (Area1) KPI strip to live TW metrics + achievement bars."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_cockpit_refresh import (  # noqa: E402
    COCKPIT_REFRESH_BLOCK_RE,
    patch_cockpit_widgets,
    patch_widget_return,
)
from cockpit_refresh_client import cockpit_refresh_js  # noqa: E402
from diff_step4_client import (  # noqa: E402
    AREA1_CSS_ANCHOR,
    AREA1_CSS_BLOCK,
    DIFF_STEP4_CSS_END,
    DIFF_STEP4_MARKER,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

AREA1_JS_ANCHOR = "      /* END KPI-FOCUS-TW-METRICS */"


def patch_area1_css(text: str) -> str:
    css_start = f"    {DIFF_STEP4_MARKER}"
    css_end = f"    {DIFF_STEP4_CSS_END}"
    if css_start in text and css_end in text:
        return text
    if AREA1_CSS_ANCHOR not in text:
        raise SystemExit("area1 diff CSS anchor miss")
    return text.replace(AREA1_CSS_ANCHOR, AREA1_CSS_BLOCK + "\n", 1)


def inject_cockpit_refresh_annual(text: str) -> str:
    block = cockpit_refresh_js().rstrip() + "\n"
    if COCKPIT_REFRESH_BLOCK_RE.search(text):
        return COCKPIT_REFRESH_BLOCK_RE.sub(block, text, count=1)
    if AREA1_JS_ANCHOR not in text:
        raise SystemExit("focus tw end anchor miss")
    if "/* KPI-COCKPIT-REFRESH */" in text:
        return text
    return text.replace(AREA1_JS_ANCHOR, AREA1_JS_ANCHOR + "\n" + block, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "/* KPI-FOCUS-TW-METRICS */" not in text:
        raise SystemExit(f"focus tw metrics missing in {path}")
    text = patch_area1_css(text)
    text = patch_widget_return(text)
    text = patch_cockpit_widgets(text)
    text = inject_cockpit_refresh_annual(text)
    if "refreshArea1Cockpit" not in text or "window.__area1CockpitWidgets" not in text:
        raise SystemExit(f"annual cockpit refresh not applied: {path}")
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

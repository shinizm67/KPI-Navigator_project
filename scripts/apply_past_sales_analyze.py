#!/usr/bin/env python3
"""Apply Past Sales Analyze tab (KPI table + seasonality chart) to annual index JA/EN."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from past_sales_analyze_client import (  # noqa: E402
    CSS_BLOCK_NEW,
    CSS_BLOCK_OLD,
    CSS_SCROLL_DUP_NEW,
    CSS_SCROLL_DUP_OLD,
    CSS_VARS_NEW,
    CSS_VARS_OLD,
    HTML_EN,
    HTML_JA,
    HTML_OLD_EN,
    HTML_OLD_JA,
    PATCH_MARKER,
    RENDER_NEW,
    RENDER_OLD,
    SET_TAB_NEW,
    SET_TAB_OLD,
    STATE_NEW,
    STATE_OLD,
    SUMMARY_NEW,
    SUMMARY_OLD,
    VARS_NEW,
    VARS_OLD,
    YM_HTML_NEW,
    YM_HTML_OLD,
)

TARGETS = {
    ROOT / "app/annual/index.html": (HTML_OLD_JA, HTML_JA),
    ROOT / "en/app/annual/index.html": (HTML_OLD_EN, HTML_EN),
}

PATCHES_COMMON = [
    (CSS_VARS_OLD, CSS_VARS_NEW, "css-vars"),
    (CSS_SCROLL_DUP_OLD, CSS_SCROLL_DUP_NEW, "css-scroll-dup"),
    (CSS_BLOCK_OLD, CSS_BLOCK_NEW, "css-analyze"),
    (None, None, "html"),  # filled per target
    (YM_HTML_OLD, YM_HTML_NEW, "ym-html"),
    (STATE_OLD, STATE_NEW, "state"),
    (VARS_OLD, VARS_NEW, "vars"),
    (SUMMARY_OLD, SUMMARY_NEW, "summary-hook"),
    (RENDER_OLD, RENDER_NEW, "render"),
    (SET_TAB_OLD, SET_TAB_NEW, "set-tab"),
]


def patch_file(path: Path, html_old: str, html_new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if PATCH_MARKER in text or "past-sales-analyze-input-sales" in text:
        print(f"skip (already patched): {path.relative_to(ROOT)}", file=sys.stderr)
        return
    for old, new, label in PATCHES_COMMON:
        if label == "html":
            old = html_old
            new = html_new
        if old not in text:
            raise SystemExit(f"patch anchor missing in {path}: {label}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path, (html_old, html_new) in TARGETS.items():
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_file(path, html_old, html_new)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

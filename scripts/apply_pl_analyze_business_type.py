#!/usr/bin/env python3
"""Unit 5B-3: surgically patch PL Analyze for Business Type layouts."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pl_analyze_business_type_client import (
    CSS_BEGIN,
    CSS_END,
    JS_BEGIN,
    JS_END,
    pl_analyze_business_type_client_js,
    pl_analyze_business_type_css,
)

ROOT = Path(__file__).resolve().parents[1]

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]

JS_ANCHOR = "      window.__plRefreshAnalyzeBlock = refreshAnalyzeBlock;\n"
CSS_ANCHOR = """    .pl-v-major--analyze.pl-v-major--r4 {
      height: calc(var(--pl-row-label-h) * 4);
      min-height: calc(var(--pl-row-label-h) * 4);
      max-height: calc(var(--pl-row-label-h) * 4);
    }
"""


def _replace_marked(text: str, begin: str, end: str, block: str) -> str:
    if begin in text and end in text:
        start = text.index(begin)
        stop = text.index(end) + len(end)
        return text[:start] + block.rstrip("\n") + text[stop:]
    return text


def patch_html(text: str) -> str:
    js_block = pl_analyze_business_type_client_js().strip("\n")
    css_block = pl_analyze_business_type_css().rstrip("\n")

    if JS_BEGIN in text:
        text = _replace_marked(text, JS_BEGIN, JS_END, js_block)
    else:
        if JS_ANCHOR not in text:
            raise SystemExit("analyze refresh anchor missing")
        text = text.replace(JS_ANCHOR, JS_ANCHOR + "\n" + js_block + "\n", 1)

    if CSS_BEGIN in text:
        text = _replace_marked(text, CSS_BEGIN, CSS_END, css_block)
    else:
        if CSS_ANCHOR not in text:
            raise SystemExit("analyze r4 CSS anchor missing")
        text = text.replace(CSS_ANCHOR, CSS_ANCHOR + css_block + "\n", 1)
    return text


def main() -> None:
    for path in PL_PAGES:
        original = path.read_text(encoding="utf-8")
        updated = patch_html(original)
        if updated == original:
            print(f"unchanged {path.relative_to(ROOT).as_posix()}")
            continue
        path.write_text(updated, encoding="utf-8", newline="\n")
        print(f"patched {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()

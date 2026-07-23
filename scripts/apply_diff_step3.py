#!/usr/bin/env python3
"""Difference Step 3 — Insight target-vs-actual diff severity."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from diff_step3_client import (  # noqa: E402
    DIFF_STEP3_MARKER,
    INSIGHT_DIFF_CSS_ANCHOR,
    INSIGHT_DIFF_CSS_BLOCK,
)
from insight_diff_client import (  # noqa: E402
    GRAPH1_DIFF_ANNUAL_OLD,
    GRAPH1_DIFF_NEW,
    GRAPH1_DIFF_OLD,
    INSIGHT_DIFF_JS_END,
    INSIGHT_DIFF_JS_MARKER,
    INSIGHT_FILL_NEW,
    INSIGHT_FILL_OLD,
    INSIGHT_OVERLAY_IIFE,
    insight_diff_js,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def patch_insight_css(text: str) -> str:
    if DIFF_STEP3_MARKER in text:
        return text
    if INSIGHT_DIFF_CSS_ANCHOR not in text:
        raise SystemExit("insight diff CSS anchor miss")
    return text.replace(INSIGHT_DIFF_CSS_ANCHOR, INSIGHT_DIFF_CSS_BLOCK + "\n    " + INSIGHT_DIFF_CSS_ANCHOR, 1)


def inject_insight_diff_js(text: str) -> str:
    block = insight_diff_js().rstrip() + "\n"
    if INSIGHT_DIFF_JS_MARKER in text:
        pattern = (
            re.escape(INSIGHT_DIFF_JS_MARKER)
            + r"[\s\S]*?"
            + re.escape(INSIGHT_DIFF_JS_END)
            + r"\n?"
        )
        return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
    pos = text.find(INSIGHT_OVERLAY_IIFE)
    if pos < 0:
        raise SystemExit("insight-overlay IIFE anchor miss")
    return text[:pos] + block + text[pos:]


def patch_insight_fill(text: str) -> str:
    if "__INSIGHT_FILL_SCHED" in text:
        return text
    if "renderInsightTwDiffs" in text and INSIGHT_FILL_NEW.split("renderInsightTwDiffs")[0] in text:
        return text
    if INSIGHT_FILL_OLD not in text:
        raise SystemExit("insight overlay fill() patch miss")
    return text.replace(INSIGHT_FILL_OLD, INSIGHT_FILL_NEW, 1)


def patch_graph_tooltips(text: str) -> str:
    if "applyInsightTwDiffEl(diffEl, sales, tgt)" in text:
        return text
    count = text.count(GRAPH1_DIFF_OLD)
    if count < 1:
        return text
    if count < 2:
        text = text.replace(GRAPH1_DIFF_OLD, GRAPH1_DIFF_NEW, count)
        return text
    text = text.replace(GRAPH1_DIFF_OLD, GRAPH1_DIFF_NEW, 2)
    if GRAPH1_DIFF_ANNUAL_OLD in text:
        # Annual graph1 uses the same diffEl block; second occurrence may differ — already patched if shared
        pass
    remaining = text.count(GRAPH1_DIFF_OLD)
    if remaining:
        text = text.replace(GRAPH1_DIFF_OLD, GRAPH1_DIFF_NEW, remaining)
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_insight_css(text)
    text = inject_insight_diff_js(text)
    text = patch_insight_fill(text)
    text = patch_graph_tooltips(text)
    if DIFF_STEP3_MARKER not in text or INSIGHT_DIFF_JS_MARKER not in text:
        raise SystemExit(f"step3 not applied: {path}")
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

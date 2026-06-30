#!/usr/bin/env python3
"""Difference Step 4 — Area1 KPI strip + MEP diff severity."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from diff_step4_client import (  # noqa: E402
    AREA1_CSS_ANCHOR,
    AREA1_CSS_BLOCK,
    DIFF_STEP4_CSS_END,
    DIFF_STEP4_END,
    DIFF_STEP4_MARKER,
    MEP_KPI_CSS_ANCHOR,
    MEP_KPI_CSS_BLOCK,
    MEP_RENDER_KPI_STRIP_DIFF_NEW,
    MEP_RENDER_KPI_STRIP_DIFF_OLD,
    MEP_TW_HELPERS_ANCHOR,
    MEP_TW_HELPERS_INJECT,
    diff_step4_area1_js,
)

AREA1_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MEP_EDIT_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

AREA1_JS_ANCHOR = "      /* END KPI-FOCUS-TW-METRICS */"

LEGACY_AREA1_RE = re.compile(
    r"    \(function \(\) \{\n"
    r"      function formatCurrency\(value\) \{[\s\S]*?"
    r"        diffEl\.textContent = formatCurrency\(fallbackDifference\);\n"
    r"      \}\n"
    r"    \}\)\(\);\n",
    re.MULTILINE,
)

AREA1_JS_BLOCK_RE = re.compile(
    r"    "
    + re.escape(DIFF_STEP4_MARKER)
    + r"\n"
    + r"    \(function \(\) \{[\s\S]*?"
    + re.escape(DIFF_STEP4_END)
    + r"\n?",
    re.MULTILINE,
)


def patch_area1_css(text: str) -> str:
    css_start = f"    {DIFF_STEP4_MARKER}"
    css_end = f"    {DIFF_STEP4_CSS_END}"
    if css_start in text and css_end in text:
        return text
    if AREA1_CSS_ANCHOR not in text:
        raise SystemExit("area1 diff CSS anchor miss")
    return text.replace(AREA1_CSS_ANCHOR, AREA1_CSS_BLOCK + "\n", 1)


def remove_legacy_area1_iife(text: str) -> str:
    if "refreshArea1KpiStripDiffs" in text:
        return text
    m = LEGACY_AREA1_RE.search(text)
    if not m:
        raise SystemExit("legacy area1 KPI IIFE miss")
    return text[: m.start()] + text[m.end() :]


def inject_area1_js(text: str) -> str:
    block = diff_step4_area1_js().rstrip() + "\n"
    if AREA1_JS_BLOCK_RE.search(text):
        return AREA1_JS_BLOCK_RE.sub(block, text, count=1)
    if AREA1_JS_ANCHOR not in text:
        raise SystemExit("focus tw end anchor miss")
    return text.replace(AREA1_JS_ANCHOR, AREA1_JS_ANCHOR + "\n" + block, 1)


def patch_area1_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "/* END KPI-FOCUS-TW-METRICS */" not in text:
        print(f"skip area1 (no focus tw): {path.relative_to(ROOT)}", file=sys.stderr)
        return
    text = patch_area1_css(text)
    text = remove_legacy_area1_iife(text)
    text = inject_area1_js(text)
    if "refreshArea1KpiStripDiffs" not in text or DIFF_STEP4_MARKER not in text:
        raise SystemExit(f"area1 step4 not applied: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote area1 {path.relative_to(ROOT)}")


def patch_mep_edit_css(text: str) -> str:
    css_start = f"    {DIFF_STEP4_MARKER}"
    css_end = f"    {DIFF_STEP4_CSS_END}"
    if css_start in text and css_end in text:
        return text
    if MEP_KPI_CSS_ANCHOR not in text:
        raise SystemExit("mep kpi diff CSS anchor miss")
    return text.replace(MEP_KPI_CSS_ANCHOR, MEP_KPI_CSS_BLOCK + "\n", 1)


def patch_mep_kpi_strip(text: str) -> str:
    if "mep-kpi-annual-diff" in text:
        return text
    if MEP_TW_HELPERS_ANCHOR not in text:
        raise SystemExit("renderKpiStrip anchor miss")
    text = text.replace(MEP_TW_HELPERS_ANCHOR, MEP_TW_HELPERS_INJECT, 1)
    if MEP_RENDER_KPI_STRIP_DIFF_OLD not in text:
        raise SystemExit("renderKpiStrip diff cells miss")
    return text.replace(MEP_RENDER_KPI_STRIP_DIFF_OLD, MEP_RENDER_KPI_STRIP_DIFF_NEW, 1)


def patch_mep_edit_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_mep_edit_css(text)
    text = patch_mep_kpi_strip(text)
    if "mep-kpi-annual-diff" not in text or "ensureTwDiffExports" not in text:
        raise SystemExit(f"mep edit step4 not applied: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote mep edit {path.relative_to(ROOT)}")


def main() -> int:
    for path in AREA1_PAGES + MEP_EDIT_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
    for path in AREA1_PAGES:
        patch_area1_page(path)
    for path in MEP_EDIT_PAGES:
        patch_mep_edit_page(path)

    from apply_mep_memo_float import sync_js_block  # noqa: E402

    for path in MEP_EDIT_PAGES:
        sync_js_block(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

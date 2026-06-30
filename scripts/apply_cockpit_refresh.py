#!/usr/bin/env python3
"""Wire Cockpit (Area1) KPI strip to live TW metrics + achievement bars."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cockpit_refresh_client import (  # noqa: E402
    COCKPIT_ANNUAL_WIDGET_NEW,
    COCKPIT_ANNUAL_WIDGET_OLD,
    COCKPIT_ANNUAL_WIDGET_OLD_EN,
    COCKPIT_COMPUTE_ANCHOR,
    COCKPIT_DAILY_WIDGET_NEW,
    COCKPIT_DAILY_WIDGET_OLD,
    COCKPIT_DAILY_WIDGET_OLD_EN,
    COCKPIT_MONTHLY_WIDGET_NEW,
    COCKPIT_MONTHLY_WIDGET_OLD,
    COCKPIT_MONTHLY_WIDGET_OLD_EN,
    COCKPIT_REFRESH_END,
    COCKPIT_REFRESH_MARKER,
    WIDGET_RETURN_NEW,
    WIDGET_RETURN_OLD,
    cockpit_refresh_js,
)
from cockpit_tw_compute_client import (  # noqa: E402
    COCKPIT_TW_END,
    COCKPIT_TW_MARKER,
    cockpit_tw_compute_js,
)
from diff_step4_client import DIFF_STEP4_END, DIFF_STEP4_MARKER  # noqa: E402

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

LEGACY_AREA1_RE = re.compile(
    r"    \(function \(\) \{\n"
    r"      function formatCurrency\(value\) \{[\s\S]*?"
    r"        diffEl\.textContent = formatCurrency\(fallbackDifference\);\n"
    r"      \}\n"
    r"    \}\)\(\);\n",
    re.MULTILINE,
)

DIFF_STEP4_BLOCK_RE = re.compile(
    r"    "
    + re.escape(DIFF_STEP4_MARKER)
    + r"\n"
    + r"    \(function \(\) \{[\s\S]*?"
    + re.escape(DIFF_STEP4_END)
    + r"\n?",
    re.MULTILINE,
)

COCKPIT_REFRESH_BLOCK_RE = re.compile(
    r"    "
    + re.escape(COCKPIT_REFRESH_MARKER)
    + r"\n"
    + r"    \(function \(\) \{[\s\S]*?"
    + re.escape(COCKPIT_REFRESH_END)
    + r"\n?",
    re.MULTILINE,
)

COCKPIT_WIDGET_ANCHOR = """      initAllocationWidget({
        graphId: 'insight-daily-alloc-graph',"""


def patch_widget_return(text: str) -> str:
    if "setDisabled: function ()" in text:
        return text
    if WIDGET_RETURN_OLD not in text:
        return text
    return text.replace(WIDGET_RETURN_OLD, WIDGET_RETURN_NEW, 1)


def _replace_first(text: str, variants: list[str], new: str, label: str) -> str:
    for old in variants:
        if old in text:
            return text.replace(old, new, 1)
    raise SystemExit(f"{label} patch miss")


def patch_cockpit_widgets(text: str) -> str:
    if "window.__area1CockpitWidgets.dailyAch" in text:
        if "window.__area1CockpitWidgets.monthlyAch" not in text:
            anchor = """      window.__area1CockpitWidgets.dailyAch = initAllocationWidget({
        graphId: 'annual-achievement-graph',"""
            if anchor not in text:
                raise SystemExit("cockpit daily widget registered but anchor miss")
            # Re-find end of dailyAch block — insert monthly/annual before insight-daily-alloc
            insert_before = "      initAllocationWidget({\n        graphId: 'insight-daily-alloc-graph',"
            if insert_before not in text:
                raise SystemExit("insight-daily-alloc anchor miss for group5 insert")
            insert = (
                COCKPIT_MONTHLY_WIDGET_NEW.replace(
                    "      window.__area1CockpitWidgets.monthlyAch",
                    "      window.__area1CockpitWidgets.monthlyAch",
                )
                + "\n"
                + COCKPIT_ANNUAL_WIDGET_NEW
                + "\n"
            )
            text = text.replace(insert_before, insert + insert_before, 1)
        return text
    text = _replace_first(
        text,
        [COCKPIT_DAILY_WIDGET_OLD, COCKPIT_DAILY_WIDGET_OLD_EN],
        COCKPIT_DAILY_WIDGET_NEW,
        "cockpit daily widget",
    )
    if "window.__area1CockpitWidgets.monthlyAch" not in text:
        insert_before = "      initAllocationWidget({\n        graphId: 'insight-daily-alloc-graph',"
        if insert_before in text:
            insert = COCKPIT_MONTHLY_WIDGET_NEW + "\n" + COCKPIT_ANNUAL_WIDGET_NEW + "\n"
            text = text.replace(insert_before, insert + insert_before, 1)
        else:
            text = _replace_first(
                text,
                [COCKPIT_MONTHLY_WIDGET_OLD, COCKPIT_MONTHLY_WIDGET_OLD_EN],
                COCKPIT_MONTHLY_WIDGET_NEW,
                "cockpit monthly widget",
            )
            text = _replace_first(
                text,
                [COCKPIT_ANNUAL_WIDGET_OLD, COCKPIT_ANNUAL_WIDGET_OLD_EN],
                COCKPIT_ANNUAL_WIDGET_NEW,
                "cockpit annual widget",
            )
    else:
        text = _replace_first(
            text,
            [COCKPIT_MONTHLY_WIDGET_OLD, COCKPIT_MONTHLY_WIDGET_OLD_EN],
            COCKPIT_MONTHLY_WIDGET_NEW,
            "cockpit monthly widget",
        )
        text = _replace_first(
            text,
            [COCKPIT_ANNUAL_WIDGET_OLD, COCKPIT_ANNUAL_WIDGET_OLD_EN],
            COCKPIT_ANNUAL_WIDGET_NEW,
            "cockpit annual widget",
        )
    return text


def inject_cockpit_compute(text: str) -> str:
    if "/* KPI-FOCUS-TW-METRICS */" in text:
        return text
    block = cockpit_tw_compute_js().rstrip() + "\n"
    if COCKPIT_TW_MARKER in text:
        # Relocate compute above cockpit refresh if it was injected too late.
        start = text.find(f"    {COCKPIT_TW_MARKER}")
        end = text.find(f"    {COCKPIT_TW_END}", start)
        if start >= 0 and end >= 0:
            end += len(f"    {COCKPIT_TW_END}") + 1
            text = text[:start] + text[end:]
    if COCKPIT_COMPUTE_ANCHOR not in text:
        raise SystemExit("cockpit compute anchor miss")
    if COCKPIT_TW_MARKER in text:
        return text
    return text.replace(COCKPIT_COMPUTE_ANCHOR, block + COCKPIT_COMPUTE_ANCHOR, 1)


def remove_legacy_area1_iife(text: str) -> str:
    if "refreshArea1Cockpit" in text:
        m = LEGACY_AREA1_RE.search(text)
        if m:
            return text[: m.start()] + text[m.end() :]
        return text
    m = LEGACY_AREA1_RE.search(text)
    if not m:
        if "function formatCurrency(value)" in text and "annual-difference-value" in text:
            raise SystemExit("legacy cockpit IIFE miss")
        return text
    return text[: m.start()] + text[m.end() :]


def inject_cockpit_refresh(text: str) -> str:
    block = cockpit_refresh_js().rstrip() + "\n"
    if COCKPIT_REFRESH_BLOCK_RE.search(text):
        return COCKPIT_REFRESH_BLOCK_RE.sub(block, text, count=1)
    if DIFF_STEP4_BLOCK_RE.search(text):
        return DIFF_STEP4_BLOCK_RE.sub(block, text, count=1)
    if COCKPIT_WIDGET_ANCHOR not in text:
        raise SystemExit("cockpit refresh inject anchor miss")
    return text.replace(COCKPIT_WIDGET_ANCHOR, block + COCKPIT_WIDGET_ANCHOR, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_widget_return(text)
    text = inject_cockpit_compute(text)
    text = patch_cockpit_widgets(text)
    text = remove_legacy_area1_iife(text)
    text = inject_cockpit_refresh(text)
    if "refreshArea1Cockpit" not in text or "window.__area1CockpitWidgets" not in text:
        raise SystemExit(f"cockpit refresh not applied: {path}")
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

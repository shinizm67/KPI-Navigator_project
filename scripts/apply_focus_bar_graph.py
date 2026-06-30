#!/usr/bin/env python3
"""Wire Focus Bar Graph popover to KpiYearStore / TW metrics (Phase 9)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402
from focus_bar_graph_client import (  # noqa: E402
    EDITABLE_HTML_NEW,
    EDITABLE_HTML_OLD,
    FORMAT_DIFF_NEW,
    FORMAT_DIFF_OLD,
    GRAPH_FMT_NEW,
    GRAPH_FMT_OLD,
    GRAPH_STORE_MARKER,
    MANUAL_VARS_NEW,
    MANUAL_VARS_OLD,
    PARSE_BLOCK_NEW,
    PARSE_BLOCK_OLD,
    PROMPT_EDIT_BLOCK,
    REFRESH_GRAPH_NEW,
    REFRESH_GRAPH_OLD,
    STORE_LISTENERS_ANCHOR,
    STORE_LISTENERS_NEW,
    STR_EN_TAIL_NEW,
    STR_EN_TAIL_OLD,
    STR_JA_NEW,
    STR_JA_OLD,
    SYNC_LABELS_NEW,
    SYNC_LABELS_OLD,
    TW_FMT_REVERT_NEW,
    TW_FMT_REVERT_OLD,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def _replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new.split("\n", 1)[0].strip() in text or GRAPH_STORE_MARKER in text:
            return text
        raise SystemExit(f"{label} patch miss")
    return text.replace(old, new, 1)


def patch_graph_popover_js(text: str) -> str:
    if GRAPH_STORE_MARKER in text and REFRESH_GRAPH_NEW in text:
        text = text
    else:
        text = _replace(text, STR_JA_OLD, STR_JA_NEW, "STR JA")
        text = _replace(text, STR_EN_TAIL_OLD, STR_EN_TAIL_NEW, "STR EN")
        text = _replace(text, MANUAL_VARS_OLD, MANUAL_VARS_NEW, "manual vars")
        text = _replace(text, GRAPH_FMT_OLD, GRAPH_FMT_NEW, "graph fmtMoney")
        text = _replace(text, FORMAT_DIFF_OLD, FORMAT_DIFF_NEW, "formatSignedDiff")
        text = _replace(text, PARSE_BLOCK_OLD, PARSE_BLOCK_NEW, "parse/scrape block")
        text = _replace(text, REFRESH_GRAPH_OLD, REFRESH_GRAPH_NEW, "refreshGraphContent")
        text = _replace(text, SYNC_LABELS_OLD, SYNC_LABELS_NEW, "syncLabels")
        if PROMPT_EDIT_BLOCK in text:
            text = text.replace(PROMPT_EDIT_BLOCK, "", 1)
    if TW_FMT_REVERT_OLD in text:
        text = text.replace(TW_FMT_REVERT_OLD, TW_FMT_REVERT_NEW, 1)
    if "refreshGraphPopoverFromStore" not in text:
        if STORE_LISTENERS_ANCHOR not in text:
            raise SystemExit("graph popover listeners anchor miss")
        text = text.replace(STORE_LISTENERS_ANCHOR, STORE_LISTENERS_NEW, 1)
    return text


def patch_editable_html(text: str) -> str:
    return text.replace(EDITABLE_HTML_OLD, EDITABLE_HTML_NEW)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "__computeTwMetricsForIso" not in text:
        raise SystemExit(f"__computeTwMetricsForIso missing in {path} — run apply_focus_tw_metrics.py")
    text = patch_graph_popover_js(text)
    text = patch_editable_html(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_focus_tw(path)
    for path in PAGES:
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

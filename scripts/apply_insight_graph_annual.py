#!/usr/bin/env python3
"""Insight Graph → Annual Graph1 のみ: 累計折れ線実データ化.

CSS / Graph2 / 棒グラフは変更しない。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402
from insight_trend_annual_graph1_client import (  # noqa: E402
    MARKER_ANNUAL_BUILDER,
    MARKER_BUILD_STORE,
    MARKER_RESOLVE_ISO,
    TREND_BUILD_STORE_NEW,
    TREND_BUILD_STORE_OLD,
    TREND_GET_FOCUS_NEW,
    TREND_GET_FOCUS_OLD,
    TREND_LISTENERS_NEW,
    TREND_LISTENERS_OLD,
    TREND_RENDER_PAYLOAD_NEW,
    TREND_RENDER_PAYLOAD_OLD,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

G1_START = "function initGraphAnnualCumulativeTrendGraph1()"
G2_START = "function initGraphAnnualCumulativeTrendGraph2()"


def patch_graph1_block(text: str) -> str:
    i1 = text.find(G1_START)
    i2 = text.find(G2_START)
    if i1 < 0 or i2 < 0 or i2 <= i1:
        raise SystemExit("Graph1/Graph2 anchors miss")
    head = text[:i1]
    block = text[i1:i2]
    tail = text[i2:]

    if MARKER_RESOLVE_ISO in block and MARKER_BUILD_STORE in block and TREND_RENDER_PAYLOAD_NEW in block:
        if "insight:dateChanged" in block:
            return text  # already patched

    if TREND_GET_FOCUS_OLD not in block:
        if MARKER_RESOLVE_ISO not in block:
            raise SystemExit("Graph1 getFocusYearContext patch miss")
    else:
        block = block.replace(TREND_GET_FOCUS_OLD, TREND_GET_FOCUS_NEW, 1)

    if TREND_BUILD_STORE_OLD not in block:
        if MARKER_BUILD_STORE not in block:
            raise SystemExit("Graph1 buildStorePayload patch miss")
    else:
        block = block.replace(TREND_BUILD_STORE_OLD, TREND_BUILD_STORE_NEW, 1)

    if TREND_RENDER_PAYLOAD_OLD in block:
        block = block.replace(TREND_RENDER_PAYLOAD_OLD, TREND_RENDER_PAYLOAD_NEW, 1)
    elif TREND_RENDER_PAYLOAD_NEW not in block:
        raise SystemExit("Graph1 render payload patch miss")

    return head + block + tail


def patch_listeners(text: str) -> str:
    if TREND_LISTENERS_OLD in text:
        return text.replace(TREND_LISTENERS_OLD, TREND_LISTENERS_NEW, 1)
    if "insight:dateChanged" in text and MARKER_BUILD_STORE in text:
        return text
    raise SystemExit("Graph1 listeners patch miss")


def patch_page(path: Path) -> None:
    patch_focus_tw(path)
    text = path.read_text(encoding="utf-8")
    text = patch_graph1_block(text)
    text = patch_listeners(text)
    if MARKER_ANNUAL_BUILDER not in text:
        raise SystemExit(f"{MARKER_ANNUAL_BUILDER} missing after focus_tw: {path}")
    if MARKER_BUILD_STORE not in text:
        raise SystemExit(f"buildStorePayload missing: {path}")
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

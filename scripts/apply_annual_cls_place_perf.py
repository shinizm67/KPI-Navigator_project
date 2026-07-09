#!/usr/bin/env python3
"""Annual CLS + placeTargetSalesGroup perf (JA + EN)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from annual_cls_place_perf_client import (  # noqa: E402
    ANNUAL_CLS_MARKER,
    ANNUAL_PLACE_MARKER,
    AREA_CLOSE_IMG_EN_NEW,
    AREA_CLOSE_IMG_EN_OLD,
    AREA_CLOSE_IMG_NEW,
    AREA_CLOSE_IMG_OLD,
    BODY_BOOT_NEW,
    BODY_BOOT_NEW_EN,
    BODY_BOOT_OLD,
    FOCUS_BAR_IMG_EN_OLD,
    FOCUS_BAR_IMG_OLD,
    FOCUS_BAR_INIT_EN_NEW,
    FOCUS_BAR_INIT_NEW,
    FOCUS_BAR_INIT_OLD,
    FRAME_IMG_CSS_NEW,
    FRAME_IMG_CSS_OLD,
    HEAD_PRELOAD_EN_NEW,
    HEAD_PRELOAD_EN_OLD,
    HEAD_PRELOAD_NEW,
    HEAD_PRELOAD_OLD,
    PLACE_FN_NEW,
    PLACE_FN_OLD,
    PLACE_LISTENERS_NEW,
    PLACE_LISTENERS_OLD,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def _replace(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if ANNUAL_CLS_MARKER in text and label in ("frame img css", "head preload"):
        return text
    if "KPI-ANNUAL-CLS-BOOT" in text and label == "body boot":
        return text
    if ANNUAL_PLACE_MARKER in text and label in ("place fn", "place listeners"):
        return text
    if "__placeTargetSalesRaf" in text and label == "place listeners":
        return text
    if "fetchpriority=\"high\"" in text and label == "area close img":
        return text
    if "rel=\"preload\" as=\"image\"" in text and label == "head preload":
        return text
    if "alreadyExpanded" in text and label == "focus bar init":
        return text
    raise SystemExit(f"{label} patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_en = "/en/" in str(path)
    text = _replace(
        text,
        HEAD_PRELOAD_EN_OLD if is_en else HEAD_PRELOAD_OLD,
        HEAD_PRELOAD_EN_NEW if is_en else HEAD_PRELOAD_NEW,
        "head preload",
    )
    text = _replace(
        text,
        BODY_BOOT_OLD,
        BODY_BOOT_NEW_EN if is_en else BODY_BOOT_NEW,
        "body boot",
    )
    text = _replace(text, FRAME_IMG_CSS_OLD, FRAME_IMG_CSS_NEW, "frame img css")
    text = _replace(
        text,
        AREA_CLOSE_IMG_EN_OLD if is_en else AREA_CLOSE_IMG_OLD,
        AREA_CLOSE_IMG_EN_NEW if is_en else AREA_CLOSE_IMG_NEW,
        "area close img",
    )
    text = _replace(text, PLACE_FN_OLD, PLACE_FN_NEW, "place fn")
    text = _replace(text, PLACE_LISTENERS_OLD, PLACE_LISTENERS_NEW, "place listeners")
    text = _replace(
        text,
        FOCUS_BAR_INIT_OLD,
        FOCUS_BAR_INIT_EN_NEW if is_en else FOCUS_BAR_INIT_NEW,
        "focus bar init",
    )
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

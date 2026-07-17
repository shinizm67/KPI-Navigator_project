#!/usr/bin/env python3
"""Apply Monthly CLS fixes (JA + EN)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from monthly_cls_fix_client import (  # noqa: E402
    AREA_CLOSE_IMG_EN_NEW,
    AREA_CLOSE_IMG_EN_OLD,
    AREA_CLOSE_IMG_NEW,
    AREA_CLOSE_IMG_OLD,
    BODY_BOOT_NEW,
    BODY_BOOT_OLD,
    BODY_BOOT_SCRIPT_NEW,
    BODY_BOOT_SCRIPT_OLD,
    DASH_ROW6_NEW,
    DASH_ROW6_OLD,
    FOCUS_BAR_IMG_HTML_EN_NEW,
    FOCUS_BAR_IMG_HTML_EN_OLD,
    FOCUS_BAR_IMG_HTML_NEW,
    FOCUS_BAR_IMG_HTML_OLD,
    FOCUS_BAR_INIT_NEW,
    FOCUS_BAR_INIT_OLD,
    FRAME_IMG_CSS_NEW,
    FRAME_IMG_CSS_OLD,
    HTML_ROOT_EN_NEW,
    HTML_ROOT_EN_OLD,
    HTML_ROOT_NEW,
    HTML_ROOT_OLD,
    HYDRATE_VISIBILITY_NEW,
    HYDRATE_VISIBILITY_OLD,
    MONTHLY_CLS_MARKER,
    MONTHLY_CELL_CSS_NEW,
    MONTHLY_CELL_CSS_OLD,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def _replace(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if MONTHLY_CLS_MARKER in text and label in (
        "frame img css",
        "monthly cell css",
        "hydrate visibility",
    ):
        return text
    if "KPI-MONTHLY-CLS-BOOT" in text and label == "body boot":
        if BODY_BOOT_SCRIPT_NEW.strip() in text:
            return text
        if BODY_BOOT_SCRIPT_OLD in text:
            return text.replace(BODY_BOOT_SCRIPT_OLD, BODY_BOOT_SCRIPT_NEW, 1)
        return text
    if 'data-monthly-tw-hydrated="0"' in text and label == "html root":
        return text
    if "fmtTwMoney(0)" in text and label == "dash row6":
        return text
    if "alreadyExpanded" in text and label.startswith("focus bar init"):
        return text
    if "fetchpriority=\"high\"" in text and label == "focus bar img html":
        return text
    if BODY_BOOT_SCRIPT_NEW.strip() in text and label == "body boot script":
        return text
    raise SystemExit(f"{label} patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_en = "/en/" in str(path)
    text = _replace(
        text,
        HTML_ROOT_EN_OLD if is_en else HTML_ROOT_OLD,
        HTML_ROOT_EN_NEW if is_en else HTML_ROOT_NEW,
        "html root",
    )
    if "KPI-MONTHLY-CLS-BOOT" not in text:
        text = _replace(text, BODY_BOOT_OLD, BODY_BOOT_NEW, "body boot")
    else:
        text = _replace(text, BODY_BOOT_SCRIPT_OLD, BODY_BOOT_SCRIPT_NEW, "body boot script")
    text = _replace(text, FRAME_IMG_CSS_OLD, FRAME_IMG_CSS_NEW, "frame img css")
    text = _replace(text, HYDRATE_VISIBILITY_OLD, HYDRATE_VISIBILITY_NEW, "hydrate visibility")
    text = _replace(text, MONTHLY_CELL_CSS_OLD, MONTHLY_CELL_CSS_NEW, "monthly cell css")
    text = _replace(
        text,
        AREA_CLOSE_IMG_EN_OLD if is_en else AREA_CLOSE_IMG_OLD,
        AREA_CLOSE_IMG_EN_NEW if is_en else AREA_CLOSE_IMG_NEW,
        "area close img",
    )
    text = _replace(
        text,
        FOCUS_BAR_IMG_HTML_EN_OLD if is_en else FOCUS_BAR_IMG_HTML_OLD,
        FOCUS_BAR_IMG_HTML_EN_NEW if is_en else FOCUS_BAR_IMG_HTML_NEW,
        "focus bar img html",
    )
    text = _replace(text, DASH_ROW6_OLD, DASH_ROW6_NEW, "dash row6")
    text = _replace(text, FOCUS_BAR_INIT_OLD, FOCUS_BAR_INIT_NEW, "focus bar init ja")
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

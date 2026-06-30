#!/usr/bin/env python3
"""Apply H/L Season% stepper UI to Sales Data Analyze (Annual JA/EN)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sdm_hl_stepper_client import (  # noqa: E402
    EN_TABLE_PATCHES,
    JA_TABLE_PATCHES,
    OPEN_MODAL_NEW,
    OPEN_MODAL_OLD,
    PAST_SALES_RENDER_REVERT_NEW,
    PAST_SALES_RENDER_REVERT_OLD,
    RENDER_ALLOC_NEW,
    RENDER_ALLOC_OLD,
    RENDER_TARGET_NEW,
    RENDER_TARGET_OLD,
    SDM_HL_STEPPER_CSS_NEW,
    SDM_HL_STEPPER_CSS_OLD,
    SDM_HL_STEPPER_END,
    SDM_HL_STEPPER_MARKER,
    SDM_HL_TIP_CSS_NEW,
    SDM_HL_TIP_CSS_OLD,
    STORE_DEFAULTS_NEW,
    STORE_DEFAULTS_OLD,
    sdm_hl_stepper_js,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

HL_BLOCK_OLD_START = "      function parseSdmPercentText(text) {"
HL_BLOCK_OLD_END = "        td.appendChild(inp);\n      }"


def replace_hl_js_block(text: str) -> str:
    block = sdm_hl_stepper_js().rstrip() + "\n"
    if SDM_HL_STEPPER_MARKER in text:
        pattern = (
            re.escape(SDM_HL_STEPPER_MARKER)
            + r"[\s\S]*?"
            + re.escape(SDM_HL_STEPPER_END)
            + r"\n?"
        )
        return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
    start = text.find(HL_BLOCK_OLD_START)
    if start < 0:
        raise SystemExit("H/L JS block start not found")
    end = text.find(HL_BLOCK_OLD_END, start)
    if end < 0:
        raise SystemExit("H/L JS block end not found")
    end += len(HL_BLOCK_OLD_END)
    return text[:start] + block + text[end:]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def apply_table_patches(text: str, patches: dict[str, str]) -> str:
    for old, new in patches.items():
        if old in text:
            text = text.replace(old, new, 1)
        elif new in text:
            continue
        else:
            raise SystemExit(f"table patch miss: {old[:60]!r}")
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, SDM_HL_STEPPER_CSS_OLD, SDM_HL_STEPPER_CSS_NEW, "css")
    text = replace_once(text, SDM_HL_TIP_CSS_OLD, SDM_HL_TIP_CSS_NEW, "tip css")
    text = replace_hl_js_block(text)
    text = replace_once(text, STORE_DEFAULTS_OLD, STORE_DEFAULTS_NEW, "store defaults")
    text = replace_once(text, OPEN_MODAL_OLD, OPEN_MODAL_NEW, "open modal")
    text = replace_once(text, RENDER_ALLOC_OLD, RENDER_ALLOC_NEW, "render alert")
    text = replace_once(text, RENDER_TARGET_OLD, RENDER_TARGET_NEW, "target sales")
    text = replace_once(
        text, PAST_SALES_RENDER_REVERT_OLD, PAST_SALES_RENDER_REVERT_NEW, "past sales render"
    )
    if path == ROOT / "app/annual/index.html":
        text = apply_table_patches(text, JA_TABLE_PATCHES)
    elif path == ROOT / "en/app/annual/index.html":
        text = apply_table_patches(text, EN_TABLE_PATCHES)
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

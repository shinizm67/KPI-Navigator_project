#!/usr/bin/env python3
"""Apply Past Sales modal zero-default patches (replace demo 1234 with 0)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from past_sales_zero_default_client import (  # noqa: E402
    PSM_BASE_ROW_DEFAULTS_NEW,
    PSM_BASE_ROW_DEFAULTS_OLD,
    PSM_PERSIST_ROW_STATE_NEW,
    PSM_PERSIST_ROW_STATE_OLD,
    PSM_RENDER_TABLE_NEW,
    PSM_RENDER_TABLE_OLD,
    PSM_ROW_APPLY_OFF_NEW,
    PSM_ROW_APPLY_OFF_OLD,
)

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

PATCHES = [
    (PSM_BASE_ROW_DEFAULTS_OLD, PSM_BASE_ROW_DEFAULTS_NEW, "baseRowDefaults"),
    (PSM_ROW_APPLY_OFF_OLD, PSM_ROW_APPLY_OFF_NEW, "pastSalesRowApplyOffState"),
    (PSM_PERSIST_ROW_STATE_OLD, PSM_PERSIST_ROW_STATE_NEW, "persistRowState/getRowDefaults"),
    (PSM_RENDER_TABLE_OLD, PSM_RENDER_TABLE_NEW, "renderPastSalesTable"),
]


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new, label in PATCHES:
        if old in text:
            text = text.replace(old, new, 1)
        elif new.split("\n")[1] in text:
            print(f"skip (already patched): {path.name} — {label}", file=sys.stderr)
        else:
            raise SystemExit(f"patch anchor missing in {path}: {label}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

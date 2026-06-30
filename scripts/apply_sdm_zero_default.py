#!/usr/bin/env python3
"""Sales Data modal: default unentered sales cells to zero."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sdm_zero_default_client import (  # noqa: E402
    SDM_BASE_ROW_DEFAULTS_NEW,
    SDM_BASE_ROW_DEFAULTS_OLD,
    SDM_BASE_ROW_MAP_READ_NEW,
    SDM_BASE_ROW_MAP_READ_OLD,
    SDM_GET_ROW_DEFAULTS_NEW,
    SDM_GET_ROW_DEFAULTS_OLD,
    SDM_PERSIST_ROW_STATE_NEW,
    SDM_PERSIST_ROW_STATE_OLD,
    SDM_RENDER_TABLE_NEW,
    SDM_RENDER_TABLE_OLD,
    SDM_ROW_APPLY_OFF_NEW,
    SDM_ROW_APPLY_OFF_OLD,
    SDM_SAVE_MODAL_NEW,
    SDM_SAVE_MODAL_OLD,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

PATCHES = [
    (SDM_BASE_ROW_DEFAULTS_OLD, SDM_BASE_ROW_DEFAULTS_NEW, "baseRowDefaults"),
    (SDM_BASE_ROW_MAP_READ_OLD, SDM_BASE_ROW_MAP_READ_NEW, "baseRowDefaults map read"),
    (SDM_GET_ROW_DEFAULTS_OLD, SDM_GET_ROW_DEFAULTS_NEW, "getRowDefaults"),
    (SDM_PERSIST_ROW_STATE_OLD, SDM_PERSIST_ROW_STATE_NEW, "persistRowState"),
    (SDM_ROW_APPLY_OFF_OLD, SDM_ROW_APPLY_OFF_NEW, "salesDataRowApplyOffState"),
    (SDM_RENDER_TABLE_OLD, SDM_RENDER_TABLE_NEW, "renderSalesDataTable"),
    (SDM_SAVE_MODAL_OLD, SDM_SAVE_MODAL_NEW, "saveSalesDataModal"),
]


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "ensureSalesDataDaily" not in text:
        raise SystemExit(f"sales data modal not found in {path}")
    changed = False
    for old, new, label in PATCHES:
        if old not in text:
            if new in text:
                continue
            raise SystemExit(f"{label} block not found in {path}")
        text = text.replace(old, new, 1)
        changed = True
    if not changed:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for page in PAGES:
        patch_page(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

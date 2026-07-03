#!/usr/bin/env python3
"""Fix Sales Data checkbox Save + reduce post-save refresh lag."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sales_data_save_fix_client import (  # noqa: E402
    CB_CHANGE_TAIL_NEW,
    CB_CHANGE_TAIL_OLD,
    GET_ROW_DEFAULTS_LIVE_NEW,
    GET_ROW_DEFAULTS_LIVE_OLD,
    PERSIST_FROM_ANNUAL_DAILY_NEW,
    PERSIST_FROM_ANNUAL_DAILY_OLD,
    SAVE_MODAL_BODY_NEW,
    SAVE_MODAL_BODY_OLD,
)

ANNUAL_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

STORE_PAGES = ANNUAL_PAGES + [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new.split("\n")[0].strip() in text and old.split("\n")[0].strip() not in text:
        return text
    if old not in text:
        if new in text:
            return text
        raise SystemExit(f"{label} patch block missing")
    return text.replace(old, new, 1)


def patch_sales_data_modal(text: str) -> str:
    text = replace_once(text, GET_ROW_DEFAULTS_LIVE_OLD, GET_ROW_DEFAULTS_LIVE_NEW, "getSalesDataRowDefaultsLive")
    text = replace_once(text, SAVE_MODAL_BODY_OLD, SAVE_MODAL_BODY_NEW, "saveSalesDataModal")
    if CB_CHANGE_TAIL_OLD in text:
        text = text.replace(CB_CHANGE_TAIL_OLD, CB_CHANGE_TAIL_NEW, 1)
    return text


def patch_store(text: str) -> str:
    if "function persistSalesDataModalSave" in text:
        return text
    return replace_once(text, PERSIST_FROM_ANNUAL_DAILY_OLD, PERSIST_FROM_ANNUAL_DAILY_NEW, "persistFromAnnualDaily")


def main() -> int:
    for path in ANNUAL_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        if "function saveSalesDataModal" not in text:
            raise SystemExit(f"saveSalesDataModal missing: {path}")
        text = patch_sales_data_modal(text)
        path.write_text(text, encoding="utf-8")
        print(f"wrote modal {path.relative_to(ROOT)}")

    for path in STORE_PAGES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "function persistFromAnnualDaily" not in text:
            continue
        text2 = patch_store(text)
        if text2 != text:
            path.write_text(text2, encoding="utf-8")
            print(f"wrote store {path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

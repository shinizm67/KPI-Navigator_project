#!/usr/bin/env python3
"""Apply Sales Data Input tab fixes after apply_sales_data_modal.py."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sales_data_input_fixup_client import (  # noqa: E402
    BTN_ENABLED_EN,
    BTN_ENABLED_JA,
    BTN_HIDDEN_EN_OLD,
    BTN_HIDDEN_OLD,
    CALENDAR_LISTENER_NEW,
    CALENDAR_LISTENER_OLD,
    CLOSE_CHOOSER_ARIA_JA,
    CLOSE_CHOOSER_ARIA_OLD,
    CLOSE_MODAL_NEW,
    CLOSE_MODAL_OLD,
    DATE_CHANGE_NEW,
    DATE_CHANGE_OLD,
    MODAL_ARIA_EN,
    MODAL_ARIA_EN_OLD,
    MODAL_ARIA_JA,
    MODAL_ARIA_OLD,
    OPEN_MODAL_NEW,
    OPEN_MODAL_OLD,
    SDM_THEME_NEW,
    SDM_THEME_OLD,
    STASH_REF_NEW,
    STASH_REF_OLD,
    TAB_BAR_EN,
    TAB_BAR_EN_OLD,
    TAB_BAR_JA,
    TAB_BAR_OLD,
    YEAR_NAV_NEW,
    YEAR_NAV_OLD,
    YEAR_SELECT_BLOCK_NEW,
    YEAR_SELECT_BLOCK_OLD,
    YM_CSS_ANCHOR,
    YM_CSS_NEW,
    YM_YEAR_EN,
    YM_YEAR_EN_OLD,
    YM_YEAR_JA,
    YM_YEAR_OLD,
)

TARGETS = {
    ROOT / "app/annual/index.html": {
        "btn_old": BTN_HIDDEN_OLD,
        "btn_new": BTN_ENABLED_JA,
        "tab_old": TAB_BAR_OLD,
        "tab_new": TAB_BAR_JA,
        "ym_old": YM_YEAR_OLD,
        "ym_new": YM_YEAR_JA,
        "modal_old": MODAL_ARIA_OLD,
        "modal_new": MODAL_ARIA_JA,
        "close_aria": CLOSE_CHOOSER_ARIA_OLD,
        "close_aria_new": CLOSE_CHOOSER_ARIA_JA,
    },
    ROOT / "en/app/annual/index.html": {
        "btn_old": BTN_HIDDEN_EN_OLD,
        "btn_new": BTN_ENABLED_EN,
        "tab_old": TAB_BAR_EN_OLD,
        "tab_new": TAB_BAR_EN,
        "ym_old": YM_YEAR_EN_OLD,
        "ym_new": YM_YEAR_EN,
        "modal_old": MODAL_ARIA_EN_OLD,
        "modal_new": MODAL_ARIA_EN,
        "close_aria": CLOSE_CHOOSER_ARIA_OLD.replace(
            "売上データを閉じます", "Close Sales Data"
        ),
        "close_aria_new": CLOSE_CHOOSER_ARIA_JA.replace(
            "売上データを閉じます", "Close Sales Data"
        ),
    },
}

COMMON = [
    (SDM_THEME_OLD, SDM_THEME_NEW, "theme"),
    (YEAR_NAV_OLD, YEAR_NAV_NEW, "year-nav"),
    (STASH_REF_OLD, STASH_REF_NEW, "stash-ref"),
    (DATE_CHANGE_OLD, DATE_CHANGE_NEW, "date-change"),
    (YEAR_SELECT_BLOCK_OLD, YEAR_SELECT_BLOCK_NEW, "year-select-block"),
    (OPEN_MODAL_OLD, OPEN_MODAL_NEW, "open-modal"),
    (CLOSE_MODAL_OLD, CLOSE_MODAL_NEW, "close-modal"),
    (CALENDAR_LISTENER_OLD, CALENDAR_LISTENER_NEW, "calendar-listener"),
    (YM_CSS_ANCHOR, YM_CSS_NEW, "ym-css"),
]


def patch_file(path: Path, labels: dict) -> None:
    text = path.read_text(encoding="utf-8")
    if "sales-data-year-label" in text and "syncYearLabel" in text:
        print(f"skip (already patched): {path.relative_to(ROOT)}", file=sys.stderr)
        return
    per_file = [
        (labels["btn_old"], labels["btn_new"], "btn"),
        (labels["tab_old"], labels["tab_new"], "tab-bar"),
        (labels["ym_old"], labels["ym_new"], "ym-year"),
        (labels["modal_old"], labels["modal_new"], "modal-aria"),
        (labels["close_aria"], labels["close_aria_new"], "close-chooser-aria"),
    ]
    for old, new, label in per_file + COMMON:
        if old not in text:
            raise SystemExit(f"patch anchor missing in {path}: {label}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path, labels in TARGETS.items():
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_file(path, labels)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

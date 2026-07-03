#!/usr/bin/env python3
"""Remove misplaced Past Sales view/edit toggle; add month B.Day count in ym row."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sdm_ym_bd_count_client import (  # noqa: E402
    PAST_SALES_CB_NEW,
    PAST_SALES_CB_OLD,
    PAST_SALES_GET_ROW_NEW,
    PAST_SALES_GET_ROW_OLD,
    PAST_SALES_YM_BD_EN,
    PAST_SALES_YM_BD_JA,
    PAST_SALES_YM_OLD,
    PAST_SALES_YM_OLD_EN,
    REFRESH_PAST_NEW,
    REFRESH_PAST_OLD,
    REFRESH_SDM_NEW,
    REFRESH_SDM_OLD,
    REFRESH_SDM_TOTALS_NEW,
    REFRESH_SDM_TOTALS_OLD,
    SALES_DATA_CB_NEW,
    SALES_DATA_CB_OLD,
    SALES_DATA_GET_ROW_NEW,
    SALES_DATA_GET_ROW_OLD,
    SALES_DATA_YM_BD_EN,
    SALES_DATA_YM_BD_JA,
    SALES_DATA_YM_OLD,
    YM_GRID_CSS_PSM,
    YM_GRID_CSS_PSM_OLD,
    YM_GRID_CSS_SDM,
    YM_GRID_CSS_SDM_OLD,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

EDIT_MODE_HTML_RE = re.compile(
    r"\n        <div\n          class=\"past-sales-modal__edit-mode\"[\s\S]*?\n        </div>",
    re.MULTILINE,
)

EDIT_MODE_CSS_RE = re.compile(
    r"\n    \.past-sales-modal__edit-mode \{[\s\S]*?\n    \}\n    \.past-sales-modal__edit-mode-btn\.is-active \{[\s\S]*?\n    \}",
    re.MULTILINE,
)


def remove_edit_toggle(text: str) -> str:
    text = EDIT_MODE_HTML_RE.sub("", text, count=1)
    text = EDIT_MODE_CSS_RE.sub("", text, count=1)
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "en/app/annual" not in str(path).replace("\\", "/")

    text = remove_edit_toggle(text)

    if YM_GRID_CSS_PSM_OLD in text:
        text = text.replace(YM_GRID_CSS_PSM_OLD, YM_GRID_CSS_PSM, 1)
    if YM_GRID_CSS_SDM_OLD in text:
        text = text.replace(YM_GRID_CSS_SDM_OLD, YM_GRID_CSS_SDM, 1)

    ym_old = PAST_SALES_YM_OLD if is_ja else PAST_SALES_YM_OLD_EN
    if "past-sales-ym-bd-count" not in text:
        if ym_old not in text:
            if 'past-sales-modal__ym-cell--year' in text and "past-sales-ym-bd-count" not in text:
                pass  # year class already set; insert bd cell only below
            else:
                raise SystemExit(f"past-sales ym anchor not found in {path}")
        else:
            ym_new = ym_old.replace(
                'class="past-sales-modal__ym-cell"',
                'class="past-sales-modal__ym-cell past-sales-modal__ym-cell--year"',
                1,
            )
            text = text.replace(ym_old, ym_new, 1)
        needle = '          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--month">'
        if needle in text and "past-sales-ym-bd-count" not in text:
            bd = PAST_SALES_YM_BD_JA if is_ja else PAST_SALES_YM_BD_EN
            text = text.replace(
                "          </div>\n" + needle,
                bd + "\n" + needle,
                1,
            )

    if "sales-data-ym-bd-count" not in text:
        if SALES_DATA_YM_OLD not in text:
            raise SystemExit(f"sales-data ym anchor not found in {path}")
        needle = '          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--month">'
        bd = SALES_DATA_YM_BD_JA if is_ja else SALES_DATA_YM_BD_EN
        text = text.replace(
            "          </div>\n" + needle,
            bd + "\n" + needle,
            1,
        )

    if "function updatePastSalesYmBdCount()" not in text:
        if PAST_SALES_GET_ROW_OLD not in text:
            raise SystemExit(f"past-sales getRowDefaults anchor not found in {path}")
        text = text.replace(PAST_SALES_GET_ROW_OLD, PAST_SALES_GET_ROW_NEW, 1)

    if "function updateSalesDataYmBdCount()" not in text:
        if SALES_DATA_GET_ROW_OLD not in text:
            raise SystemExit(f"sales-data getRowDefaults anchor not found in {path}")
        text = text.replace(SALES_DATA_GET_ROW_OLD, SALES_DATA_GET_ROW_NEW, 1)

    if REFRESH_PAST_OLD in text and "updatePastSalesYmBdCount();" not in text.split("renderPastSalesTable")[1][:800]:
        text = text.replace(REFRESH_PAST_OLD, REFRESH_PAST_NEW, 1)

    if REFRESH_SDM_OLD in text and "updateSalesDataYmBdCount();" not in text.split("renderSalesDataTable")[1][:800]:
        text = text.replace(REFRESH_SDM_OLD, REFRESH_SDM_NEW, 1)

    if REFRESH_SDM_TOTALS_OLD in text:
        text = text.replace(REFRESH_SDM_TOTALS_OLD, REFRESH_SDM_TOTALS_NEW, 1)

    if PAST_SALES_CB_OLD in text:
        text = text.replace(PAST_SALES_CB_OLD, PAST_SALES_CB_NEW, 1)

    if SALES_DATA_CB_OLD in text:
        text = text.replace(SALES_DATA_CB_OLD, SALES_DATA_CB_NEW, 1)

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

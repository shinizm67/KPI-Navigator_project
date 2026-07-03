#!/usr/bin/env python3
"""Apply ym row layout: Total B.Days title | count | Annual|Month nav split."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sdm_ym_nav_layout_client import (  # noqa: E402
    PAST_SALES_YM_BLOCK_EN,
    PAST_SALES_YM_BLOCK_JA,
    PAST_SALES_YM_BLOCK_OLD,
    PAST_SALES_YM_BLOCK_OLD_EN,
    PSM_ANALYZE_YM_NEW,
    PSM_ANALYZE_YM_OLD,
    PSM_BD_COUNT_CSS_NEW,
    PSM_BD_COUNT_CSS_TRIM,
    SALES_DATA_YM_BLOCK_EN,
    SALES_DATA_YM_BLOCK_JA,
    SALES_DATA_YM_BLOCK_OLD,
    SALES_DATA_YM_BLOCK_OLD_EN,
    SDM_ANALYZE_YM_NEW,
    SDM_ANALYZE_YM_OLD,
    SDM_BD_COUNT_CSS_NEW,
    SDM_BD_COUNT_CSS_TRIM,
    YM_NAV_CSS_PSM,
    YM_NAV_CSS_SDM,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "en/app/annual" not in str(path).replace("\\", "/")

    ps_old = PAST_SALES_YM_BLOCK_OLD if is_ja else PAST_SALES_YM_BLOCK_OLD_EN
    ps_block = PAST_SALES_YM_BLOCK_JA if is_ja else PAST_SALES_YM_BLOCK_EN
    if ps_old in text:
        text = text.replace(ps_old, ps_block, 1)
    elif "past-sales-modal__ym-cell--bd-title" not in text:
        raise SystemExit(f"past-sales ym block not found in {path}")

    sdm_old = SALES_DATA_YM_BLOCK_OLD if is_ja else SALES_DATA_YM_BLOCK_OLD_EN
    sdm_block = SALES_DATA_YM_BLOCK_JA if is_ja else SALES_DATA_YM_BLOCK_EN
    if sdm_old in text:
        text = text.replace(sdm_old, sdm_block, 1)
    elif "sales-data-modal__ym-cell--bd-title" not in text:
        raise SystemExit(f"sales-data ym block not found in {path}")

    if PSM_BD_COUNT_CSS_TRIM in text:
        text = text.replace(PSM_BD_COUNT_CSS_TRIM, PSM_BD_COUNT_CSS_NEW, 1)
    elif PSM_BD_COUNT_CSS_NEW not in text:
        anchor = ".past-sales-modal__ym-cell--bd-count {"
        if anchor in text and "ym-cell--bd-title" not in text.split(anchor)[0][-200:]:
            text = text.replace(anchor, PSM_BD_COUNT_CSS_NEW.strip() + "\n    " + anchor, 1)

    if SDM_BD_COUNT_CSS_TRIM in text:
        text = text.replace(SDM_BD_COUNT_CSS_TRIM, SDM_BD_COUNT_CSS_NEW, 1)

    if PSM_ANALYZE_YM_OLD in text:
        text = text.replace(PSM_ANALYZE_YM_OLD, PSM_ANALYZE_YM_NEW, 1)
    if SDM_ANALYZE_YM_OLD in text:
        text = text.replace(SDM_ANALYZE_YM_OLD, SDM_ANALYZE_YM_NEW, 1)

    if ".past-sales-modal__ym-nav {" not in text:
        anchor = ".past-sales-modal__ym-cell--bd-count {"
        if anchor not in text:
            raise SystemExit(f"psm bd-count css anchor not found in {path}")
        text = text.replace(anchor, YM_NAV_CSS_PSM.strip() + "\n    " + anchor, 1)

    if ".sales-data-modal__ym-nav {" not in text:
        anchor = ".sales-data-modal__ym-cell--bd-count {"
        if anchor not in text:
            raise SystemExit(f"sdm bd-count css anchor not found in {path}")
        text = text.replace(anchor, YM_NAV_CSS_SDM.strip() + "\n    " + anchor, 1)

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

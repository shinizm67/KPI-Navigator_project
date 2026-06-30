#!/usr/bin/env python3
"""Apply Phase 8 read-surface sync patches."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from kpi_year_store_client import KPI_YEAR_STORE_MARKER, kpi_year_store_js  # noqa: E402
from read_surface_sync_client import (  # noqa: E402
    MEP_REFRESH_BLOCK,
    PAST_SALES_BASE_NEW,
    PAST_SALES_BASE_OLD,
    PAST_SALES_OPEN_NEW,
    PAST_SALES_OPEN_OLD,
    READ_SURFACE_MARKER,
    READ_SURFACE_MONTHLY_BLOCK,
    READ_SURFACE_TW_FINAL_NEW,
    READ_SURFACE_TW_FINAL_OLD,
    READ_SURFACE_TW_REFRESH,
    STORE_DISPATCH_NEW,
    STORE_DISPATCH_OLD,
    STORE_INIT_NEW,
    STORE_INIT_OLD,
)
from focus_tw_metrics_client import FOCUS_TW_END  # noqa: E402

ANNUAL = [ROOT / "app/annual/index.html", ROOT / "en/app/annual/index.html"]
MONTHLY = [ROOT / "app/monthly/index.html", ROOT / "en/app/monthly/index.html"]
MEP = [ROOT / "app/monthly/edit/index.html", ROOT / "en/app/monthly/edit/index.html"]


def inject_store(text: str) -> str:
    block = kpi_year_store_js().rstrip() + "\n"
    pattern = (
        re.escape(KPI_YEAR_STORE_MARKER)
        + r"[\s\S]*?window\.KpiYearStore[\s\S]*?\}\)\(\);\n"
    )
    if not re.search(pattern, text):
        raise SystemExit("KPI-YEAR-STORE block not found")
    return re.sub(pattern, lambda _m: block, text, count=1)


def patch_annual(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_store(text)
    if READ_SURFACE_MARKER not in text:
        anchor = FOCUS_TW_END
        if anchor not in text:
            raise SystemExit(f"FOCUS_TW_END missing: {path}")
        text = text.replace(
            anchor,
            anchor + "\n" + READ_SURFACE_TW_REFRESH + "\n      " + READ_SURFACE_MARKER,
            1,
        )
    if READ_SURFACE_TW_FINAL_OLD in text:
        text = text.replace(READ_SURFACE_TW_FINAL_OLD, READ_SURFACE_TW_FINAL_NEW, 1)
    if PAST_SALES_OPEN_OLD in text:
        text = text.replace(PAST_SALES_OPEN_OLD, PAST_SALES_OPEN_NEW, 1)
    if PAST_SALES_BASE_OLD in text:
        text = text.replace(PAST_SALES_BASE_OLD, PAST_SALES_BASE_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_monthly(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_store(text)
    if READ_SURFACE_MARKER not in text:
        anchor = "      document.addEventListener('annual:salesMapChanged', function () {"
        if anchor not in text:
            raise SystemExit(f"monthly salesMap anchor missing: {path}")
        text = text.replace(anchor, READ_SURFACE_MONTHLY_BLOCK + "\n" + anchor, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_mep(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_store(text)
    if "refreshMepSalesFromStore" not in text:
        anchor = "      document.addEventListener('kpi:mepDataChanged', function (ev) {"
        if anchor not in text:
            raise SystemExit(f"mep anchor missing: {path}")
        text = text.replace(anchor, MEP_REFRESH_BLOCK + "\n" + anchor, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_store_source() -> None:
    print("store source: kpi_year_store_client.py (patched in repo)")


def main() -> int:
    patch_store_source()
    for p in ANNUAL:
        patch_annual(p)
    for p in MONTHLY:
        patch_monthly(p)
    for p in MEP:
        patch_mep(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

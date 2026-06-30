#!/usr/bin/env python3
"""Apply Phase 3 analyze refresh hooks + reinject KpiYearStore."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from kpi_year_store_client import KPI_YEAR_STORE_MARKER, kpi_year_store_js  # noqa: E402
from phase3_analyze_refresh_client import (  # noqa: E402
    PHASE3_ANALYZE_BLOCK,
    PHASE3_ANALYZE_END,
    PHASE3_ANALYZE_MARKER,
)

ANNUAL = [ROOT / "app/annual/index.html", ROOT / "en/app/annual/index.html"]


def inject_store(text: str) -> str:
    block = kpi_year_store_js().rstrip() + "\n"
    pattern = (
        re.escape(KPI_YEAR_STORE_MARKER)
        + r"[\s\S]*?window\.KpiYearStore[\s\S]*?\}\)\(\);\n"
    )
    if not re.search(pattern, text):
        raise SystemExit("KPI-YEAR-STORE block not found")
    return re.sub(pattern, lambda _m: block, text, count=1)


def replace_phase3_block(text: str) -> str:
    block = PHASE3_ANALYZE_BLOCK.rstrip() + "\n"
    if PHASE3_ANALYZE_MARKER not in text:
        anchor = "      /* END KPI-SDM-ANALYZE-PAST-SEASONALITY */"
        if anchor not in text:
            raise SystemExit("analyze anchor missing")
        return text.replace(anchor, anchor + "\n\n" + block.rstrip(), 1)
    if PHASE3_ANALYZE_END in text:
        pattern = (
            re.escape(PHASE3_ANALYZE_MARKER)
            + r"[\s\S]*?"
            + re.escape(PHASE3_ANALYZE_END)
            + r"\n?"
        )
    else:
        pattern = (
            re.escape(PHASE3_ANALYZE_MARKER)
            + r"[\s\S]*?\}\)\(\);\n"
        )
    return re.sub(pattern, lambda _m: block, text, count=1)


def patch_annual(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_store(text)
    text = replace_phase3_block(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for p in ANNUAL:
        patch_annual(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

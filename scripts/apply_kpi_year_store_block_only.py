#!/usr/bin/env python3
"""Re-inject KpiYearStore block only (past-sales merge / 1234 fixes)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from kpi_year_store_client import KPI_YEAR_STORE_MARKER, kpi_year_store_js  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]


def patch_store_block(text: str) -> str:
    block = kpi_year_store_js().rstrip() + "\n"
    if KPI_YEAR_STORE_MARKER not in text:
        raise SystemExit("KPI-YEAR-STORE marker missing")
    pattern = (
        re.escape(KPI_YEAR_STORE_MARKER) + r"[\s\S]*?window\.KpiYearStore[\s\S]*?\}\)\(\);\n"
    )
    if not re.search(pattern, text):
        raise SystemExit("KPI-YEAR-STORE block boundary not matched")
    return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)


def main() -> int:
    for path in TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        text = patch_store_block(text)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

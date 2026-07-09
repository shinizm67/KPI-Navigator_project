#!/usr/bin/env python3
"""Re-inject KpiYearStore block only (Phase 11 weekday APIs). Does not touch page patches."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_kpi_year_store import (  # noqa: E402
    ANNUAL_TARGETS,
    GATEWAY_ANNUAL_ANCHOR,
    GATEWAY_MEP_ANCHOR,
    GATEWAY_MONTHLY_ANCHOR,
    MEP_TARGETS,
    MONTHLY_TARGETS,
    inject_store,
)
from fix_orphan_kpi_store_duplicate import fix_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    pairs = [
        (ANNUAL_TARGETS, GATEWAY_ANNUAL_ANCHOR),
        (MONTHLY_TARGETS, GATEWAY_MONTHLY_ANCHOR),
        (MEP_TARGETS, GATEWAY_MEP_ANCHOR),
    ]
    for targets, anchor in pairs:
        for path in targets:
            text = path.read_text(encoding="utf-8")
            text = inject_store(text, anchor)
            text, _notes = fix_text(text)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

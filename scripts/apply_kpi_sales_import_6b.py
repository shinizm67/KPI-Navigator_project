#!/usr/bin/env python3
"""Unit 6B: inject Sales CSV Business Type gate into Annual / MEP import pages only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from apply_daily_sales_import import (  # noqa: E402
    ANNUAL_PAGES,
    MEP_PAGES,
    MEP_SALES_CSV_HELPER,
    inject_import_js,
    patch_mep_apply_food_drink,
    upsert_function_before,
)


def patch_annual(path: Path) -> None:
    text = inject_import_js(path.read_text(encoding="utf-8"))
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT).as_posix()}")


def patch_mep(path: Path) -> None:
    text = inject_import_js(path.read_text(encoding="utf-8"))
    text = upsert_function_before(
        text,
        MEP_SALES_CSV_HELPER,
        "persistMepSalesCsvByYear",
        "applyDailyImportMapsToOpenYear",
    )
    text = patch_mep_apply_food_drink(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT).as_posix()}")


def main() -> int:
    for path in ANNUAL_PAGES + MEP_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
    for path in ANNUAL_PAGES:
        patch_annual(path)
    for path in MEP_PAGES:
        patch_mep(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

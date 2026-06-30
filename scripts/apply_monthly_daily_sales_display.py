#!/usr/bin/env python3
"""Monthly Table Window: unset daily sales display as zero."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from monthly_daily_sales_display_client import (  # noqa: E402
    MONTHLY_RESOLVE_DAILY_SALES_NEW,
    MONTHLY_RESOLVE_DAILY_SALES_OLD,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MONTHLY_RESOLVE_DAILY_SALES_NEW in text:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return
    if MONTHLY_RESOLVE_DAILY_SALES_OLD not in text:
        raise SystemExit(f"resolveDailySalesText block not found in {path}")
    text = text.replace(MONTHLY_RESOLVE_DAILY_SALES_OLD, MONTHLY_RESOLVE_DAILY_SALES_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for page in PAGES:
        patch_page(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

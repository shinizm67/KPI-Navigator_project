#!/usr/bin/env python3
"""Dispatch annual:dailyDateChanged from Monthly cockpit applyDailySelection."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from monthly_daily_date_sync_client import (  # noqa: E402
    MONTHLY_APPLY_DAILY_SELECTION_NEW,
    MONTHLY_APPLY_DAILY_SELECTION_OLD,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MONTHLY_APPLY_DAILY_SELECTION_NEW in text:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return
    if MONTHLY_APPLY_DAILY_SELECTION_OLD not in text:
        raise SystemExit(f"monthly applyDailySelection block not found in {path}")
    text = text.replace(MONTHLY_APPLY_DAILY_SELECTION_OLD, MONTHLY_APPLY_DAILY_SELECTION_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for page in PAGES:
        patch_page(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

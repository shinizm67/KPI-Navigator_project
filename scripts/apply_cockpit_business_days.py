#!/usr/bin/env python3
"""Cockpit Total Business Days: count explicit Sales Data B.DAY true only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cockpit_business_days_client import (  # noqa: E402
    COCKPIT_BUSINESS_DAYS_MARKER,
    SYNC_BUSINESS_DAY_IS_FN_NEW,
    SYNC_BUSINESS_DAY_IS_FN_OLD_ANNUAL,
    SYNC_BUSINESS_DAY_IS_FN_OLD_EN_ANNUAL,
    SYNC_BUSINESS_DAY_IS_FN_OLD_MONTHLY,
    SYNC_BUSINESS_DAY_LISTENERS_APPEND_ANNUAL,
    SYNC_BUSINESS_DAY_LISTENERS_APPEND_ANNUAL_NEW,
    SYNC_BUSINESS_DAY_LISTENERS_NEW_MONTHLY,
    SYNC_BUSINESS_DAY_LISTENERS_OLD_MONTHLY,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def patch_sync_business_day_block(text: str, path: Path) -> str:
    if COCKPIT_BUSINESS_DAYS_MARKER in text and "resolveBusinessDayMapForCockpit" in text:
        if "annual-total-bd-value" not in text:
            raise SystemExit(f"sync business day block marker without bd el: {path}")
        return text

    is_monthly = "/monthly/" in str(path)
    candidates = (
        [SYNC_BUSINESS_DAY_IS_FN_OLD_MONTHLY]
        if is_monthly
        else [SYNC_BUSINESS_DAY_IS_FN_OLD_ANNUAL, SYNC_BUSINESS_DAY_IS_FN_OLD_EN_ANNUAL]
    )
    old_fn = next((c for c in candidates if c in text), None)
    if not old_fn:
        raise SystemExit(f"sync business day isCalendarBusinessDay block missing: {path}")

    text = text.replace(old_fn, SYNC_BUSINESS_DAY_IS_FN_NEW, 1)

    if is_monthly:
        if SYNC_BUSINESS_DAY_LISTENERS_OLD_MONTHLY not in text:
            if "annual:salesDataSaved" in text.split("syncBusinessDayDisplayFromDailyMap")[1][:800]:
                pass
            else:
                raise SystemExit(f"monthly sync listeners block missing: {path}")
        else:
            text = text.replace(
                SYNC_BUSINESS_DAY_LISTENERS_OLD_MONTHLY,
                SYNC_BUSINESS_DAY_LISTENERS_NEW_MONTHLY,
                1,
            )
    elif SYNC_BUSINESS_DAY_LISTENERS_APPEND_ANNUAL in text:
        if "annual:salesDataSaved', function () {\n        syncBusinessDayDisplayFromDailyMap" not in text:
            text = text.replace(
                SYNC_BUSINESS_DAY_LISTENERS_APPEND_ANNUAL,
                SYNC_BUSINESS_DAY_LISTENERS_APPEND_ANNUAL_NEW,
                1,
            )

    if COCKPIT_BUSINESS_DAYS_MARKER not in text:
        raise SystemExit(f"patch not applied: {path}")
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "syncBusinessDayDisplayFromDailyMap" not in text:
        raise SystemExit(f"syncBusinessDayDisplayFromDailyMap missing: {path}")
    text = patch_sync_business_day_block(text, path)
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

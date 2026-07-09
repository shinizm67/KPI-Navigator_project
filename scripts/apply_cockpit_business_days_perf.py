#!/usr/bin/env python3
"""Monthly-only: optimize cockpit business-day counting (load perf)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cockpit_business_days_perf_client import (  # noqa: E402
    COCKPIT_BD_BLOCK_NEW,
    COCKPIT_BD_BLOCK_OLD,
    COCKPIT_BD_PERF_MARKER,
    GATHER_MONTH_FN_NEW,
    GATHER_MONTH_FN_OLD,
    GATHER_MONTHLY_SALES_NEW,
    GATHER_MONTHLY_SALES_OLD,
    SCHEDULE_SYNC_BD_CALL_NEW,
    SCHEDULE_SYNC_BD_CALL_OLD,
    YEAR_SYNC_IS_FN_NEW,
    YEAR_SYNC_IS_FN_OLD,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def _replace(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if COCKPIT_BD_PERF_MARKER in text and label == "cockpit bd block":
        return text
    if "function isCalendarBusinessDay(y, m0, day, bmap)" in text and label == "year sync is fn":
        return text
    if "var yearPrefix = String(year) + '-';" in text and "gatherMonthlySales" in text and label == "gather monthly sales":
        return text
    if "var monthPrefix = String(year)" in text and label == "gather month fn":
        return text
    if "scheduleSyncBusinessDayDisplayFromDailyMap" in text and label == "schedule sync bd call":
        return text
    raise SystemExit(f"{label} patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if COCKPIT_BD_PERF_MARKER not in text:
        text = _replace(text, COCKPIT_BD_BLOCK_OLD, COCKPIT_BD_BLOCK_NEW, "cockpit bd block")
    else:
        marker = "      /* KPI-COCKPIT-BUSINESS-DAYS */\n"
        start = text.find(marker)
        end = text.find(
            "    })();\n    (function () {\n      var targetEl = document.getElementById('annual-target-sales-value');",
            start,
        )
        if start < 0 or end < 0:
            raise SystemExit("cockpit bd block refresh miss")
        text = text[:start] + COCKPIT_BD_BLOCK_NEW + text[end:]
    text = _replace(text, YEAR_SYNC_IS_FN_OLD, YEAR_SYNC_IS_FN_NEW, "year sync is fn")
    text = _replace(text, GATHER_MONTHLY_SALES_OLD, GATHER_MONTHLY_SALES_NEW, "gather monthly sales")
    text = _replace(text, GATHER_MONTH_FN_OLD, GATHER_MONTH_FN_NEW, "gather month fn")
    text = _replace(text, SCHEDULE_SYNC_BD_CALL_OLD, SCHEDULE_SYNC_BD_CALL_NEW, "schedule sync bd call")
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

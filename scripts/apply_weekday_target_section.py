#!/usr/bin/env python3
"""Patch KPI-WEEKDAY-TARGET section in KpiYearStore (avoids full store re-inject on Annual)."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from weekday_target_kpi_client import WEEKDAY_TARGET_KPI_MARKER, weekday_target_kpi_js  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

STORE_ASSIGN_ANCHOR = "        window.KpiYearStore = {"

def patch_exports(text: str) -> str:
    if "assessWeekdayTargetQuality: assessWeekdayTargetQuality" in text:
        return text
    patterns = [
        (
            """          weekdayTargetDataReady: weekdayTargetDataReady,
          computeFlatDailyTargetByIso: computeFlatDailyTargetByIso,
          resolveDailyTargetRawByIso: resolveDailyTargetRawByIso,""",
            """          weekdayTargetDataReady: weekdayTargetDataReady,
          assessWeekdayTargetQuality: assessWeekdayTargetQuality,
          computeFlatDailyTargetByIso: computeFlatDailyTargetByIso,
          resolveDailyTargetRawByIso: resolveDailyTargetRawByIso,""",
        ),
        (
            """          weekdayTargetDataReady: weekdayTargetDataReady,
          computeFlatDailyTargetByIso: computeFlatDailyTargetByIso,
          resolveDailyTargetByIso: resolveDailyTargetByIso,""",
            """          weekdayTargetDataReady: weekdayTargetDataReady,
          assessWeekdayTargetQuality: assessWeekdayTargetQuality,
          computeFlatDailyTargetByIso: computeFlatDailyTargetByIso,
          resolveDailyTargetByIso: resolveDailyTargetByIso,""",
        ),
    ]
    for old, new in patterns:
        if old in text:
            return text.replace(old, new, 1)
    raise SystemExit("KpiYearStore weekday exports anchor missing")


def patch_page(text: str) -> str:
    start = text.find(WEEKDAY_TARGET_KPI_MARKER)
    if start < 0:
        raise SystemExit("weekday marker missing")
    end = text.find(STORE_ASSIGN_ANCHOR, start)
    if end < 0:
        raise SystemExit("KpiYearStore assign anchor missing")
    new_block = weekday_target_kpi_js().rstrip() + "\n\n        "
    text = text[:start] + new_block + text[end:]
    return patch_exports(text)


def main() -> int:
    for path in TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        text = patch_page(text)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

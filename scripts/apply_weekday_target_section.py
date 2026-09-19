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
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

STORE_ASSIGN_ANCHOR = "        window.KpiYearStore = {"

EXPORT_OLD = """          readWeekdayBaselineYears: readWeekdayBaselineYears,
          writeWeekdayBaselineYears: writeWeekdayBaselineYears,
          getDefaultWeekdayBaselineYears: getDefaultWeekdayBaselineYears,
          listEligibleWeekdayBaselineYears: listEligibleWeekdayBaselineYears,"""

EXPORT_NEW = """          readWeekdayBaselineYears: readWeekdayBaselineYears,
          writeWeekdayBaselineYears: writeWeekdayBaselineYears,
          readWeekdayBaselineExcludedYears: readWeekdayBaselineExcludedYears,
          getDefaultWeekdayBaselineYears: getDefaultWeekdayBaselineYears,
          listEligibleWeekdayBaselineYears: listEligibleWeekdayBaselineYears,
          assessSeasonalityAnomalies: assessSeasonalityAnomalies,"""


def patch_exports(text: str) -> str:
    if "assessSeasonalityAnomalies: assessSeasonalityAnomalies" in text:
        if "readWeekdayBaselineExcludedYears: readWeekdayBaselineExcludedYears" in text:
            return text
    if EXPORT_OLD in text:
        return text.replace(EXPORT_OLD, EXPORT_NEW, 1)
    if "assessWeekdayTargetQuality: assessWeekdayTargetQuality" not in text:
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
                text = text.replace(old, new, 1)
                break
    if EXPORT_OLD in text:
        text = text.replace(EXPORT_OLD, EXPORT_NEW, 1)
    if "assessSeasonalityAnomalies: assessSeasonalityAnomalies" not in text:
        raise SystemExit("KpiYearStore weekday anomaly exports missing")
    return text


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

#!/usr/bin/env python3
"""CSV / multi-year bulk refresh perf: coalesce store events + longer TW/Cockpit debounce.

1) Re-inject KpiYearStore (mergeDailyMaps / mergePastSalesMaps → 1 event per kind)
2) scheduleRenderAnnualDailyTimeline 32ms → 120ms
3) onArea1CockpitRefresh 0ms → 100ms (coalesce dual dailySales+salesMap storms)
4) monthlyTwRebuildKeepFocus → 120ms debounce (reduce TW blink vs rebuildColumns)

Sources of truth also patched:
  scripts/kpi_year_store_client.py
  scripts/focus_tw_metrics_client.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_kpi_year_store_block_only import patch_store_block  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MARKER = "KPI-BULK-REFRESH-PERF"

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

TW_SCHEDULE_RE = re.compile(
    r"(__twTimelineRefreshTimer = window\.setTimeout\(function \(\) \{\s*"
    r"__twTimelineRefreshTimer = null;\s*"
    r"renderAnnualDailyTimeline\(cy, opts\);\s*"
    r"\}, )32(\);)",
    re.M,
)

TW_SCHEDULE_REPL = (
    r"\g<1>120\2 /* KPI-BULK-REFRESH-PERF */"
)

COCKPIT_0_RE = re.compile(
    r"(function onArea1CockpitRefresh\(\) \{\s*"
    r"if \(__area1CockpitRefreshTimer != null\) window\.clearTimeout\(__area1CockpitRefreshTimer\);\s*"
    r"__area1CockpitRefreshTimer = window\.setTimeout\(function \(\) \{\s*"
    r"__area1CockpitRefreshTimer = null;\s*"
    r"refreshArea1Cockpit\(resolveArea1Iso\(\)\);\s*"
    r"\}, )0(\);)",
    re.M,
)

COCKPIT_0_REPL = r"\g<1>100\2 /* KPI-BULK-REFRESH-PERF */"

MONTHLY_TW_REBUILD_OLD = """      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();
        if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();
        var keepIso =
          currentFocusIso ||
          readDailySelectedIso() ||
          toISODateLocal(new Date(state.year, state.month0, 1));
        scheduleRebuildColumns(keepIso);
      }"""

MONTHLY_TW_REBUILD_NEW = """      var __monthlyTwRebuildTimer = null;
      function monthlyTwRebuildKeepFocus() {
        /* KPI-BULK-REFRESH-PERF: coalesce CSV / dual-event column rebuilds */
        if (__monthlyTwRebuildTimer != null) window.clearTimeout(__monthlyTwRebuildTimer);
        __monthlyTwRebuildTimer = window.setTimeout(function () {
          __monthlyTwRebuildTimer = null;
          invalidateMonthlyMepMetricsCache();
          invalidateGroup1TwCache();
          if (typeof window.clearTwMetricsCache === 'function') window.clearTwMetricsCache();
          var keepIso =
            currentFocusIso ||
            readDailySelectedIso() ||
            toISODateLocal(new Date(state.year, state.month0, 1));
          scheduleRebuildColumns(keepIso);
        }, 120);
      }"""


def patch_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    notes: list[str] = []

    if "/* KPI-YEAR-STORE */" in text or "KPI-YEAR-STORE" in text:
        try:
            text2 = patch_store_block(text)
            if text2 != text:
                text = text2
                notes.append("store-block")
        except SystemExit as e:
            notes.append(f"store-skip:{e}")

    text, n_tw = TW_SCHEDULE_RE.subn(TW_SCHEDULE_REPL, text, count=1)
    if n_tw:
        notes.append("tw-120")

    text, n_ck = COCKPIT_0_RE.subn(COCKPIT_0_REPL, text, count=1)
    if n_ck:
        notes.append("cockpit-100")

    if MONTHLY_TW_REBUILD_OLD in text and "KPI-BULK-REFRESH-PERF: coalesce CSV" not in text:
        text = text.replace(MONTHLY_TW_REBUILD_OLD, MONTHLY_TW_REBUILD_NEW, 1)
        notes.append("monthly-tw-debounce")

    if notes:
        path.write_text(text, encoding="utf-8")
    return notes


def main() -> int:
    any_fail = False
    for path in TARGETS:
        if not path.is_file():
            print(f"missing {path.relative_to(ROOT)}", file=sys.stderr)
            any_fail = True
            continue
        notes = patch_file(path)
        print(f"{path.relative_to(ROOT)}: {', '.join(notes) if notes else 'no-op'}")
    print(f"marker {MARKER} applied where matched")
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

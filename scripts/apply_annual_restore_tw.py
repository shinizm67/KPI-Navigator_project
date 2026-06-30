#!/usr/bin/env python3
"""Restore Annual page Table Window (TW) from Monthly reference — Annual only."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    (ROOT / "app/monthly/index.html", ROOT / "app/annual/index.html"),
    (ROOT / "en/app/monthly/index.html", ROOT / "en/app/annual/index.html"),
]

COCKPIT_COMPUTE_RE = re.compile(
    r"\n    /\* KPI-COCKPIT-TW-COMPUTE \*/[\s\S]*?/\* END KPI-COCKPIT-TW-COMPUTE \*/\n",
    re.MULTILINE,
)
COCKPIT_REFRESH_RE = re.compile(
    r"\n    /\* KPI-COCKPIT-REFRESH \*/[\s\S]*?/\* END KPI-COCKPIT-REFRESH \*/\n",
    re.MULTILINE,
)

WIDGET_RETURN_NEW_SNIP = """          setDisabled: function () {
            if (percentEl) percentEl.textContent = '—';
            var markerColor = options.achievementAlertColors
              ? getAchievementMarkerColor(100)
              : getAllocationMarkerColor();
            varRoot.style.setProperty('--kgi-x', '0px');
            varRoot.style.setProperty('--fill-w', '0px');
            varRoot.style.setProperty('--marker-color', markerColor);
            currentPercent = 0;
          },
          percentEl: percentEl,
          graphEl: graphEl,
"""

WIDGET_RETURN_OLD = """          getPercent: function () {
            return currentPercent;
          }
        };"""

WIDGET_RETURN_REVERT = """          getPercent: function () {
            return currentPercent;
          }
        };"""

COCKPIT_WIDGET_RE = re.compile(
    r"      window\.__area1CockpitWidgets = window\.__area1CockpitWidgets \|\| \{\};\n"
    r"      window\.__area1CockpitWidgets\.dailyAch = initAllocationWidget\(\{[\s\S]*?"
    r"      window\.__area1CockpitWidgets\.annualAch = initAllocationWidget\(\{[\s\S]*?"
    r"        fallbackPercent: 108\n"
    r"      \}\);",
    re.MULTILINE,
)

COCKPIT_DAILY_ONLY = """      initAllocationWidget({
        graphId: 'annual-achievement-graph',
        percentId: 'annual-achievement-percent',
        dataKey: 'achievementPercent',
        promptLabel: '達成率',
        editable: true,
        achievementAlertColors: true
      });"""

COCKPIT_DAILY_ONLY_EN = """      initAllocationWidget({
        graphId: 'annual-achievement-graph',
        percentId: 'annual-achievement-percent',
        dataKey: 'achievementPercent',
        promptLabel: 'Achievement',
        editable: true,
        achievementAlertColors: true
      });"""

MONTHLY_WIDGET_TAIL = """      window.__area1CockpitWidgets.monthlyAch = initAllocationWidget({
        graphId: 'annual-group5-monthly-achievement-graph',
        percentId: 'annual-group5-monthly-achievement-percent',
        dataKey: 'group5MonthlyAchievementPercent',
        promptLabel: '達成率（月次累積）',
        editable: true,
        achievementAlertColors: true,
        fallbackPercent: 108
      });
      window.__area1CockpitWidgets.annualAch = initAllocationWidget({
        graphId: 'annual-group5-annual-achievement-graph',
        percentId: 'annual-group5-annual-achievement-percent',
        dataKey: 'group5AnnualAchievementPercent',
        promptLabel: '達成率（年次累積）',
        editable: true,
        achievementAlertColors: true,
        fallbackPercent: 108
      });
      initAllocationWidget({
        graphId: 'insight-daily-alloc-graph',"""


def strip_cockpit_patches(text: str, is_en: bool) -> str:
    text = COCKPIT_COMPUTE_RE.sub("\n", text, count=1)
    text = COCKPIT_REFRESH_RE.sub("\n", text, count=1)
    if WIDGET_RETURN_NEW_SNIP in text:
        text = text.replace(
            WIDGET_RETURN_NEW_SNIP + "\n",
            "",
        )
    m = COCKPIT_WIDGET_RE.search(text)
    if m:
        daily = COCKPIT_DAILY_ONLY_EN if is_en else COCKPIT_DAILY_ONLY
        text = text[: m.start()] + daily + text[m.end() :]
    if MONTHLY_WIDGET_TAIL in text:
        text = text.replace(
            MONTHLY_WIDGET_TAIL,
            "      initAllocationWidget({\n        graphId: 'insight-daily-alloc-graph',",
            1,
        )
    text = text.replace("window.refreshArea1Cockpit", "/* removed refreshArea1Cockpit */")
    return text


def extract_tw_block(monthly_text: str) -> str:
    start = monthly_text.find("      function computeFocusTimelineBounds(anchorYear)")
    if start < 0:
        raise SystemExit("computeFocusTimelineBounds missing in monthly source")
    end_marker = "      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);"
    end = monthly_text.find(end_marker, start)
    if end < 0:
        raise SystemExit("renderAnnualDailyTimeline init missing in monthly source")
    end += len(end_marker)
    block = monthly_text[start:end]
    block = COCKPIT_REFRESH_RE.sub("\n", block, count=1)
    return block


def replace_annual_tw(annual_text: str, tw_block: str) -> str:
    if "/* KPI-FOCUS-TW-METRICS */" in annual_text:
        print("  skip TW (already has KPI-FOCUS-TW-METRICS)")
        return annual_text
    old_start = annual_text.find("      function renderAnnualDailyTable(year) {")
    if old_start < 0:
        raise SystemExit("renderAnnualDailyTable missing in annual target")
    old_end_marker = "      renderAnnualDailyTable(window.__ANNUAL_DATA.calendarYear);"
    old_end = annual_text.find(old_end_marker, old_start)
    if old_end < 0:
        raise SystemExit("renderAnnualDailyTable init missing in annual target")
    old_end += len(old_end_marker)
    return annual_text[:old_start] + tw_block + annual_text[old_end:]


def patch_pair(monthly_path: Path, annual_path: Path) -> None:
    is_en = "/en/" in str(annual_path)
    monthly_text = monthly_path.read_text(encoding="utf-8")
    annual_text = annual_path.read_text(encoding="utf-8")
    annual_text = strip_cockpit_patches(annual_text, is_en)
    tw_block = extract_tw_block(monthly_text)
    annual_text = replace_annual_tw(annual_text, tw_block)
    if "renderAnnualDailyTimeline" not in annual_text:
        raise SystemExit(f"TW restore failed: {annual_path}")
    annual_path.write_text(annual_text, encoding="utf-8")
    print(f"wrote {annual_path.relative_to(ROOT)}")


def main() -> int:
    for monthly_path, annual_path in PAIRS:
        if not monthly_path.is_file() or not annual_path.is_file():
            print(f"missing {monthly_path} or {annual_path}", file=sys.stderr)
            return 1
        patch_pair(monthly_path, annual_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

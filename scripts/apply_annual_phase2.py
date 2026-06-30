#!/usr/bin/env python3
"""Annual phase-2 safe patches: TW diff severity CSS + HL plan read-only cockpit."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_diff_step1 import patch_css, patch_focus_bar_sync  # noqa: E402

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

HL_OLD_RE = re.compile(
    r"      var hlSeasonCells = document\.querySelectorAll\('\.annual-open-table tbody td:nth-child\(4\)'\);\n"
    r"      function normalizeWeightInput\(raw\) \{[\s\S]*?"
    r"      recalcMonthlyAllocationTotal\(\);\n"
    r"    \}\)\(\);",
    re.MULTILINE,
)

HL_NEW = """      var hlSeasonCells = document.querySelectorAll('.annual-open-table tbody td:nth-child(4)');
      var isJaHl = document.documentElement.getAttribute('lang') === 'ja';
      var hlPlanReadOnlyTitle = isJaHl
        ? '計画繁閑%（閲覧のみ。Sales Data で編集）'
        : 'Plan H/L % (read-only). Edit in Sales Data.';
      function applyHlWeightsToCells(weights) {
        if (!weights || weights.length !== 12) return;
        hlSeasonCells.forEach(function (cell, idx) {
          var n = Number(weights[idx]);
          cell.textContent = (Number.isFinite(n) ? n : 100) + '%';
        });
      }
      function recalcMonthlyAllocationTotal() {
        if (!monthlyAllocationWidget || !hlSeasonCells.length) return;
        var sum = 0;
        hlSeasonCells.forEach(function (cell) {
          var parsed = parsePercentText(cell.textContent);
          sum += Number.isFinite(parsed) ? parsed : 100;
        });
        monthlyAllocationWidget.setPercent(sum / 12);
      }
      function refreshHlPlanFromStore() {
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function') {
          window.__ANNUAL_UI.syncCockpitForCalendarYear();
          return;
        }
        if (!window.KpiYearStore || !hlSeasonCells.length) return;
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = KpiYearStore.getOperatingYear();
        var weights = KpiYearStore.readMonthlyHlWeights(cy);
        if (weights) applyHlWeightsToCells(weights);
        recalcMonthlyAllocationTotal();
      }
      if (window.KpiYearStore && hlSeasonCells.length) {
        var hlCy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(hlCy)) hlCy = KpiYearStore.getOperatingYear();
        var hlWeights = KpiYearStore.readMonthlyHlWeights(hlCy);
        if (hlWeights) applyHlWeightsToCells(hlWeights);
      }
      hlSeasonCells.forEach(function (cell) {
        cell.setAttribute('title', hlPlanReadOnlyTitle);
        cell.classList.add('kpi-hl-plan-readonly');
      });
      document.addEventListener('kpi:annualPlanChanged', refreshHlPlanFromStore);
      document.addEventListener('annual:calendarYearChanged', refreshHlPlanFromStore);
      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.refreshHlPlanFromStore = refreshHlPlanFromStore;
      window.__ANNUAL_UI.recalcMonthlyAllocationTotal = recalcMonthlyAllocationTotal;
      recalcMonthlyAllocationTotal();
    })();"""


def patch_hl_readonly(text: str) -> str:
    if "kpi-hl-plan-readonly" in text and "Sales Data" in text:
        return text
    if not HL_OLD_RE.search(text):
        raise SystemExit("HL season editable block not found (already patched?)")
    return HL_OLD_RE.sub(HL_NEW, text, count=1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_css(text)
    text = patch_focus_bar_sync(text)
    text = patch_hl_readonly(text)
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

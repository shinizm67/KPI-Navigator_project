#!/usr/bin/env python3
"""Inject Cockpit open-table sync for Focus Bar / year-picker calendar year changes."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cockpit_year_sync_client import COCKPIT_YEAR_SYNC_MARKER, cockpit_year_sync_js  # noqa: E402

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

REFRESH_HL_OLD = """      function refreshHlPlanFromStore() {
        if (!window.KpiYearStore || !hlSeasonCells.length) return;
        var oy = KpiYearStore.getOperatingYear();
        var weights = KpiYearStore.readMonthlyHlWeights(oy);
        if (weights) applyHlWeightsToCells(weights);
        recalcMonthlyAllocationTotal();
      }"""

REFRESH_HL_NEW = """      function refreshHlPlanFromStore() {
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
      }"""

EXPOSE_RECALC_OLD = """      window.__ANNUAL_UI.refreshHlPlanFromStore = refreshHlPlanFromStore;
      window.__ANNUAL_UI.openHlWeightsEditor = openHlWeightsEditor;
      recalcMonthlyAllocationTotal();"""

EXPOSE_RECALC_NEW = """      window.__ANNUAL_UI.refreshHlPlanFromStore = refreshHlPlanFromStore;
      window.__ANNUAL_UI.openHlWeightsEditor = openHlWeightsEditor;
      window.__ANNUAL_UI.recalcMonthlyAllocationTotal = recalcMonthlyAllocationTotal;
      recalcMonthlyAllocationTotal();"""

MONTHLY_TARGET_SEED_JA_OLD = """      if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function') {
        window.__ANNUAL_UI.syncCockpitForCalendarYear();
      }
    })();
    (function () {
      /** 達成率のみ: 100%以上は黄、50〜100%は10%刻みでアンバー→赤、50%未満は濃い赤 */
      function getAchievementMarkerColor(percent) {"""

MONTHLY_TARGET_SEED_JA_NEW = """      if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function') {
        window.__ANNUAL_UI.syncCockpitForCalendarYear();
      }
    })();
    (function () {
      /** 達成率のみ: 100%以上は黄、50〜100%は10%刻みでアンバー→赤、50%未満は濃い赤 */
      function getAchievementMarkerColor(percent) {"""

MONTHLY_TARGET_SEED_EN_OLD = MONTHLY_TARGET_SEED_JA_OLD
MONTHLY_TARGET_SEED_EN_NEW = MONTHLY_TARGET_SEED_JA_NEW

ANNUAL_TARGET_SEED_JA_OLD = """    (function () {
      var targetEl = document.getElementById('annual-target-sales-value');
      if (!targetEl) return;
      var fallback = 652528.55;
      var raw = fallback;
      if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.targetSales != null) {
        raw = window.__ANNUAL_DATA.targetSales;
      }
      if (typeof raw === 'number' && Number.isFinite(raw)) {
        targetEl.textContent = '¥' + raw.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      } else {
        targetEl.textContent = String(raw);
      }
    })();"""

ANNUAL_TARGET_SEED_JA_NEW = """    (function () {
      if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function') {
        window.__ANNUAL_UI.syncCockpitForCalendarYear();
      }
    })();"""

ANNUAL_TARGET_SEED_EN_OLD = """    (function () {
      var targetEl = document.getElementById('annual-target-sales-value');
      if (!targetEl) return;
      var fallback = 652528.55;
      var raw = fallback;
      if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.targetSales != null) {
        raw = window.__ANNUAL_DATA.targetSales;
      }
      if (typeof raw === 'number' && Number.isFinite(raw)) {
        targetEl.textContent = '$' + raw.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      } else {
        targetEl.textContent = String(raw);
      }
    })();"""

ANNUAL_TARGET_SEED_EN_NEW = ANNUAL_TARGET_SEED_JA_NEW

COMMIT_REFERENCE_OLD = """      function commitReferenceForYear(y) {
        if (!isFinite(y)) return;
        var ps = ensurePastSalesDaily();
        ps.referenceAnnualSalesByYear = ps.referenceAnnualSalesByYear || {};
        var parsed = getReferenceFromInputEl();
        if (parsed == null) {
          delete ps.referenceAnnualSalesByYear[String(y)];
        } else {
          ps.referenceAnnualSalesByYear[String(y)] = parsed;
        }
        persistPastSalesShared();
      }"""

COMMIT_REFERENCE_NEW = """      function commitReferenceForYear(y) {
        if (!isFinite(y)) return;
        var ps = ensurePastSalesDaily();
        ps.referenceAnnualSalesByYear = ps.referenceAnnualSalesByYear || {};
        var parsed = getReferenceFromInputEl();
        if (parsed == null) {
          delete ps.referenceAnnualSalesByYear[String(y)];
        } else {
          ps.referenceAnnualSalesByYear[String(y)] = parsed;
        }
        persistPastSalesShared();
        document.dispatchEvent(new CustomEvent('annual:targetSalesChanged', {
          detail: { year: y, targetSales: parsed, source: 'past-sales-reference' }
        }));
      }"""


def inject_cockpit_sync(text: str) -> str:
    block = cockpit_year_sync_js().rstrip() + "\n"
    if COCKPIT_YEAR_SYNC_MARKER in text:
        pattern = (
            re.escape(COCKPIT_YEAR_SYNC_MARKER) + r"[\s\S]*?\}\)\(\);\n"
        )
        if re.search(pattern, text):
            return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
        raise SystemExit("KPI-COCKPIT-YEAR-SYNC marker found but block boundary not matched")

    anchor = "/* KPI-EDIT-GUARDS */"
    if anchor not in text:
        anchor = "/* KPI-YEAR-STORE */"
    if anchor not in text:
        raise SystemExit("inject anchor missing (KPI-EDIT-GUARDS / KPI-YEAR-STORE)")

    m = re.search(
        re.escape(anchor) + r"[\s\S]*?\}\)\(\);\n",
        text,
    )
    if not m:
        raise SystemExit(f"could not find end of block after {anchor}")
    insert_at = m.end()
    return text[:insert_at] + "\n" + block + text[insert_at:]


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_cockpit_sync(text)
    if REFRESH_HL_OLD in text:
        text = text.replace(REFRESH_HL_OLD, REFRESH_HL_NEW, 1)
    elif REFRESH_HL_NEW.split("\n")[1] not in text:
        print(f"warn: refreshHlPlanFromStore patch skipped in {path.name}", file=sys.stderr)
    if EXPOSE_RECALC_OLD in text:
        text = text.replace(EXPOSE_RECALC_OLD, EXPOSE_RECALC_NEW, 1)
    elif "recalcMonthlyAllocationTotal = recalcMonthlyAllocationTotal" not in text:
        print(f"warn: recalc expose patch skipped in {path.name}", file=sys.stderr)
    if "monthly" in str(path):
        seed_marker = (
            "window.__ANNUAL_DATA.targetSales = raw;\n"
            "      }\n"
            "      if (typeof raw === 'number'"
        )
        if MONTHLY_TARGET_SEED_JA_OLD in text:
            text = text.replace(MONTHLY_TARGET_SEED_JA_OLD, MONTHLY_TARGET_SEED_JA_NEW, 1)
        elif seed_marker in text and "syncCockpitForCalendarYear();" not in text.split(seed_marker)[1].split("})();")[0]:
            print(f"warn: monthly target seed patch skipped in {path.name}", file=sys.stderr)
    if "annual" in str(path):
        if ANNUAL_TARGET_SEED_JA_OLD in text:
            text = text.replace(ANNUAL_TARGET_SEED_JA_OLD, ANNUAL_TARGET_SEED_JA_NEW, 1)
        elif ANNUAL_TARGET_SEED_EN_OLD in text:
            text = text.replace(ANNUAL_TARGET_SEED_EN_OLD, ANNUAL_TARGET_SEED_EN_NEW, 1)
        elif "syncCockpitForCalendarYear();" not in text:
            print(f"warn: annual target seed patch skipped in {path.name}", file=sys.stderr)
        if COMMIT_REFERENCE_OLD in text:
            text = text.replace(COMMIT_REFERENCE_OLD, COMMIT_REFERENCE_NEW, 1)
        elif "source: 'past-sales-reference'" not in text:
            print(f"warn: commitReferenceForYear patch skipped in {path.name}", file=sys.stderr)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

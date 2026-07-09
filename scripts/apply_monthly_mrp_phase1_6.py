#!/usr/bin/env python3
"""MRP Phase 1.6 — Monthly only: buffer diff styling + faster Group1 snapshot (no full-year loop per cell)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE1-6 */"

CSS_ANCHOR = """    .monthly-data-column--buffer .monthly-data-column__cell {
      color: rgba(88, 225, 243, 0.15);
      border-bottom-color: rgba(88, 225, 243, 0.14);
    }"""

CSS_BLOCK = f"""    .monthly-data-column--buffer .monthly-data-column__cell {{
      color: rgba(88, 225, 243, 0.15);
      border-bottom-color: rgba(88, 225, 243, 0.14);
    }}
    {MARKER}
    .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--win,
    .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--neutral,
    .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-90,
    .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-80,
    .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-70,
    .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-60,
    .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-50,
    .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-below {{
      color: rgba(88, 225, 243, 0.15);
    }}
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--win,
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--neutral,
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-90,
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-80,
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-70,
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-60,
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-50,
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell.tw-diff--sev-below {{
      color: rgba(88, 225, 243, 0.15);
    }}"""

SNAPSHOT_OLD = """      function readGroup1TwSnapshot(iso) {
        if (__group1TwCache[iso]) return __group1TwCache[iso];
        var sales = dailySalesAmount(iso);
        var targetText = '—';
        var diffText = '—';
        var achText = '—';
        var diffActual = NaN;
        var diffTarget = NaN;
        if (typeof window.__computeTwMetricsForIso === 'function') {
          if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
            KpiYearStore.syncToAnnualDaily();
          }
          var m = window.__computeTwMetricsForIso(iso);
          if (m) {
            sales = Number(m.dailySales) || 0;
            if (m.dailyTarget != null && Number.isFinite(Number(m.dailyTarget))) {
              diffTarget = Number(m.dailyTarget);
              targetText = fmtTwMoney(diffTarget);
              diffActual = sales;
              diffText =
                typeof window.__twFmtDiff === 'function'
                  ? window.__twFmtDiff(diffActual, diffTarget)
                  : fmtTwMoney(diffActual - diffTarget);
              achText =
                typeof window.__twFmtAchPct === 'function'
                  ? window.__twFmtAchPct(diffActual, diffTarget)
                  : '—';
            }
          }
        }
        var snap = {
          sales: sales,
          targetText: targetText,
          diffText: diffText,
          achText: achText,
          diffActual: diffActual,
          diffTarget: diffTarget,
        };
        __group1TwCache[iso] = snap;
        return snap;
      }

      function decorateMonthlyGroup1Cell(cell, cellIndex, iso) {
        if (!cell) return;
        if (cellIndex === 3) {
          cell.classList.add('monthly-data-column__cell--plan-target');
        }
        if (cellIndex !== 4) return;
        var snap = readGroup1TwSnapshot(iso);
        applyMonthlyTwDiffClass(cell, snap.diffActual, snap.diffTarget);
      }"""

SNAPSHOT_NEW = f"""      {MARKER}
      function parseIsoYear(iso) {{
        var p = String(iso || '').split('-');
        return Number(p[0]);
      }}
      function getMonthlyTwTargetMapForYear(y) {{
        y = Number(y);
        if (!Number.isFinite(y)) return null;
        window.__monthlyTwTargetMapsByYear = window.__monthlyTwTargetMapsByYear || {{}};
        if (window.__monthlyTwTargetMapsByYear[y]) return window.__monthlyTwTargetMapsByYear[y];
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var bmap = (daily && daily.businessDayByDate) || {{}};
        var map = null;
        if (typeof window.__buildDailyTargetMapForYear === 'function') {{
          map = window.__buildDailyTargetMapForYear(y, bmap);
        }}
        window.__monthlyTwTargetMapsByYear[y] = map || {{}};
        return window.__monthlyTwTargetMapsByYear[y];
      }}
      function clearMonthlyTwTargetMapsByYear() {{
        window.__monthlyTwTargetMapsByYear = {{}};
      }}
      function readGroup1TwSnapshot(iso) {{
        if (__group1TwCache[iso]) return __group1TwCache[iso];
        var sales = dailySalesAmount(iso);
        var targetText = '—';
        var diffText = '—';
        var achText = '—';
        var diffActual = NaN;
        var diffTarget = NaN;
        var y = parseIsoYear(iso);
        var tgtMap = Number.isFinite(y) ? getMonthlyTwTargetMapForYear(y) : null;
        if (tgtMap && Object.prototype.hasOwnProperty.call(tgtMap, iso)) {{
          var tgtVal = Number(tgtMap[iso]);
          if (Number.isFinite(tgtVal) && tgtVal > 0) {{
            diffTarget = tgtVal;
            targetText = fmtTwMoney(diffTarget);
            diffActual = sales;
            diffText =
              typeof window.__twFmtDiff === 'function'
                ? window.__twFmtDiff(diffActual, diffTarget)
                : fmtTwMoney(diffActual - diffTarget);
            achText =
              typeof window.__twFmtAchPct === 'function'
                ? window.__twFmtAchPct(diffActual, diffTarget)
                : '—';
          }}
        }} else if (typeof window.__computeTwMetricsForIso === 'function') {{
          var m = window.__computeTwMetricsForIso(iso);
          if (m) {{
            sales = Number(m.dailySales) || 0;
            if (m.dailyTarget != null && Number.isFinite(Number(m.dailyTarget))) {{
              diffTarget = Number(m.dailyTarget);
              targetText = fmtTwMoney(diffTarget);
              diffActual = sales;
              diffText =
                typeof window.__twFmtDiff === 'function'
                  ? window.__twFmtDiff(diffActual, diffTarget)
                  : fmtTwMoney(diffActual - diffTarget);
              achText =
                typeof window.__twFmtAchPct === 'function'
                  ? window.__twFmtAchPct(diffActual, diffTarget)
                  : '—';
            }}
          }}
        }}
        var snap = {{
          sales: sales,
          targetText: targetText,
          diffText: diffText,
          achText: achText,
          diffActual: diffActual,
          diffTarget: diffTarget,
        }};
        __group1TwCache[iso] = snap;
        return snap;
      }}

      function decorateMonthlyGroup1Cell(cell, cellIndex, iso, skipDiffDecor) {{
        if (!cell || skipDiffDecor) return;
        if (cellIndex === 3) {{
          cell.classList.add('monthly-data-column__cell--plan-target');
        }}
        if (cellIndex !== 4) return;
        var snap = readGroup1TwSnapshot(iso);
        applyMonthlyTwDiffClass(cell, snap.diffActual, snap.diffTarget);
      }}"""

PRIME_OLD = """      function primeMonthlyTwTargetCache(y) {
        y = Number(y);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = null;
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var bmap = (daily && daily.businessDayByDate) || {};
        if (typeof window.__buildDailyTargetMapForYear === 'function') {
          window.__monthlyTwTargetCache = window.__buildDailyTargetMapForYear(y, bmap);
        }
      }"""

PRIME_NEW = """      function primeMonthlyTwTargetCache(y) {
        y = Number(y);
        clearMonthlyTwTargetMapsByYear();
        getMonthlyTwTargetMapForYear(y);
        getMonthlyTwTargetMapForYear(y - 1);
        getMonthlyTwTargetMapForYear(y + 1);
        window.__monthlyTwTargetCacheYear = y;
        window.__monthlyTwTargetCache = window.__monthlyTwTargetMapsByYear[y] || null;
      }"""

MAKE_GROUP_OLD = """          if (groupNo === 1) decorateMonthlyGroup1Cell(cell, i, iso);
          div.appendChild(cell);"""

MAKE_GROUP_NEW = """          if (groupNo === 1) decorateMonthlyGroup1Cell(cell, i, iso, buffer);
          div.appendChild(cell);"""

REBUILD_HEAD_OLD = """      /* KPI-MRP-PHASE1-5 */
      function rebuildColumns() {
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);"""

REBUILD_HEAD_NEW = """      /* KPI-MRP-PHASE1-5 */
      function rebuildColumns() {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already applied) {path.relative_to(ROOT)}")
        return
    for old, new, label in (
        (CSS_ANCHOR, CSS_BLOCK, "css"),
        (SNAPSHOT_OLD, SNAPSHOT_NEW, "snapshot"),
        (PRIME_OLD, PRIME_NEW, "prime"),
        (MAKE_GROUP_OLD, MAKE_GROUP_NEW, "makeGroup"),
        (REBUILD_HEAD_OLD, REBUILD_HEAD_NEW, "rebuild"),
    ):
        if old not in text:
            raise SystemExit(f"phase1.6 {label} anchor miss: {path}")
        text = text.replace(old, new, 1)
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

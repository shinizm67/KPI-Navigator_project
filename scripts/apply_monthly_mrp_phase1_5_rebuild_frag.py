#!/usr/bin/env python3
"""MRP Phase 1.5 — Monthly only: rebuildColumns via DocumentFragment (less layout thrash)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE1-5 */"

REBUILD_OLD = """      function rebuildColumns() {
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);
        invalidateGroup1TwCache();
        isoToIndex = {};
        trackDate.innerHTML = '';
        trackGroup1.innerHTML = '';
        trackGroup2.innerHTML = '';
        trackGroup3.innerHTML = '';
        trackProfit.innerHTML = '';
        var y = state.year;
        var m0 = state.month0;
        var first = new Date(y, m0, 1);
        var prevMonthLast = new Date(y, m0, 0);
        var prevMonthDays = prevMonthLast.getDate();
        var anchorX = getFocusAnchorXInViewport();
        var neededLeading = Math.max(1, Math.ceil((anchorX - COL_W / 2) / COL_STEP));
        var baselineStart = Math.min(PREV_MONTH_START_DAY, prevMonthDays);
        var baselineLeading = prevMonthDays - baselineStart + 1;
        var startDay = baselineStart;
        if (baselineLeading < neededLeading) {
          startDay = Math.max(1, prevMonthDays - neededLeading + 1);
        }
        var start = new Date(y, m0 - 1, startDay);
        var end = new Date(y, m0 + 1, NEXT_MONTH_END_DAY);
        var g1Label = useJa ? 'グループ1' : 'Group 1';
        var g2Label = useJa ? 'グループ2' : 'Group 2';
        var g3Label = useJa ? 'グループ3' : 'Group 3';
        var i = 0;
        for (var d = new Date(start.getFullYear(), start.getMonth(), start.getDate()); d <= end; d = addDays(d, 1), i++) {
          var iso = toISODateLocal(d);
          var inMonth = d.getMonth() === m0 && d.getFullYear() === y;
          var buffer = !inMonth;
          var off = !isBusinessDayByIso(iso, d);
          isoToIndex[iso] = i;
          var p = document.createElement('p');
          p.className = 'monthly-date-header-cell';
          if (off) p.classList.add('monthly-date-header-cell--off');
          if (buffer) p.classList.add('monthly-date-header-cell--buffer');
          p.setAttribute('data-iso', iso);
          p.textContent = dateLabelText(d);
          p.setAttribute('aria-label', ariaDateLabel(d, inMonth));
          trackDate.appendChild(p);
          var colNum = i + 1;
          trackGroup1.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g1Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
              1
            )
          );
          trackGroup2.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g2Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
              2
            )
          );
          trackGroup3.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g3Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
              3
            )
          );
          trackProfit.appendChild(
            makeProfitColumn(
              buffer,
              off,
              iso,
              (useJa ? 'Profit 列' : 'Profit column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : '')
            )
          );
        }
        scheduleVFocusUpdate();
      }"""

REBUILD_NEW = f"""      {MARKER}
      function rebuildColumns() {{
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);
        invalidateGroup1TwCache();
        isoToIndex = {{}};
        var fragDate = document.createDocumentFragment();
        var fragGroup1 = document.createDocumentFragment();
        var fragGroup2 = document.createDocumentFragment();
        var fragGroup3 = document.createDocumentFragment();
        var fragProfit = document.createDocumentFragment();
        var y = state.year;
        var m0 = state.month0;
        var first = new Date(y, m0, 1);
        var prevMonthLast = new Date(y, m0, 0);
        var prevMonthDays = prevMonthLast.getDate();
        var anchorX = getFocusAnchorXInViewport();
        var neededLeading = Math.max(1, Math.ceil((anchorX - COL_W / 2) / COL_STEP));
        var baselineStart = Math.min(PREV_MONTH_START_DAY, prevMonthDays);
        var baselineLeading = prevMonthDays - baselineStart + 1;
        var startDay = baselineStart;
        if (baselineLeading < neededLeading) {{
          startDay = Math.max(1, prevMonthDays - neededLeading + 1);
        }}
        var start = new Date(y, m0 - 1, startDay);
        var end = new Date(y, m0 + 1, NEXT_MONTH_END_DAY);
        var g1Label = useJa ? 'グループ1' : 'Group 1';
        var g2Label = useJa ? 'グループ2' : 'Group 2';
        var g3Label = useJa ? 'グループ3' : 'Group 3';
        var i = 0;
        for (var d = new Date(start.getFullYear(), start.getMonth(), start.getDate()); d <= end; d = addDays(d, 1), i++) {{
          var iso = toISODateLocal(d);
          var inMonth = d.getMonth() === m0 && d.getFullYear() === y;
          var buffer = !inMonth;
          var off = !isBusinessDayByIso(iso, d);
          isoToIndex[iso] = i;
          var p = document.createElement('p');
          p.className = 'monthly-date-header-cell';
          if (off) p.classList.add('monthly-date-header-cell--off');
          if (buffer) p.classList.add('monthly-date-header-cell--buffer');
          p.setAttribute('data-iso', iso);
          p.textContent = dateLabelText(d);
          p.setAttribute('aria-label', ariaDateLabel(d, inMonth));
          fragDate.appendChild(p);
          var colNum = i + 1;
          fragGroup1.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g1Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
              1
            )
          );
          fragGroup2.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g2Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
              2
            )
          );
          fragGroup3.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g3Label + ' ' + (useJa ? '列' : 'column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : ''),
              3
            )
          );
          fragProfit.appendChild(
            makeProfitColumn(
              buffer,
              off,
              iso,
              (useJa ? 'Profit 列' : 'Profit column ') + colNum + ((buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : '')
            )
          );
        }}
        trackDate.replaceChildren(fragDate);
        trackGroup1.replaceChildren(fragGroup1);
        trackGroup2.replaceChildren(fragGroup2);
        trackGroup3.replaceChildren(fragGroup3);
        trackProfit.replaceChildren(fragProfit);
        scheduleVFocusUpdate();
      }}"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already applied) {path.relative_to(ROOT)}")
        return
    if REBUILD_OLD not in text:
        raise SystemExit(f"phase1.5 rebuild anchor miss: {path}")
    text = text.replace(REBUILD_OLD, REBUILD_NEW, 1)
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

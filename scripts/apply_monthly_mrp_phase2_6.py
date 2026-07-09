#!/usr/bin/env python3
"""MRP Phase 2.6 — Skeleton-first TW paint: no blank wait, hydrate metrics in background."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-6 */"

CSS_ANCHOR_OLD = """    .monthly-scroll-data__track--group {
      height: var(--monthly-data-group-outer-h);
      flex: 0 0 var(--monthly-data-group-outer-h);
    }"""

CSS_ANCHOR_NEW = f"""    {MARKER}
    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--group .monthly-data-column__cell,
    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--profit .monthly-data-column__cell {{
      opacity: 0.5;
    }}
    .monthly-scroll-data__track--group {{
      height: var(--monthly-data-group-outer-h);
      flex: 0 0 var(--monthly-data-group-outer-h);
    }}"""

MAKE_GROUP_OLD = """      function makeGroupColumn(buffer, off, iso, aria, groupNo, metrics) {
        var div = document.createElement('div');
        div.className =
          'monthly-data-column monthly-data-column--group' +
          (buffer ? ' monthly-data-column--buffer' : '') +
          (off ? ' monthly-data-column--off' : '');
        div.setAttribute('role', 'presentation');
        div.setAttribute('data-iso', iso);
        div.setAttribute('aria-label', aria);
        var values;
        if (!off && metrics) {
          if (groupNo === 1) values = metrics.g1;
          else if (groupNo === 2) values = metrics.g2;
          else values = metrics.g3;
        } else {
          values = getMonthlyGroupCellValues(groupNo, off, iso);
        }"""

MAKE_GROUP_NEW = f"""      function makeGroupColumn(buffer, off, iso, aria, groupNo, metrics, skeleton) {{
        var div = document.createElement('div');
        div.className =
          'monthly-data-column monthly-data-column--group' +
          (buffer ? ' monthly-data-column--buffer' : '') +
          (off ? ' monthly-data-column--off' : '');
        div.setAttribute('role', 'presentation');
        div.setAttribute('data-iso', iso);
        div.setAttribute('aria-label', aria);
        var values;
        {MARKER}
        if (skeleton) {{
          values = dashRow6();
        }} else if (!off && metrics) {{
          if (groupNo === 1) values = metrics.g1;
          else if (groupNo === 2) values = metrics.g2;
          else values = metrics.g3;
        }} else {{
          values = getMonthlyGroupCellValues(groupNo, off, iso);
        }}"""

MAKE_PROFIT_OLD = """        var cell = document.createElement('span');
        cell.className = 'monthly-data-column__cell';
        cell.setAttribute('aria-hidden', 'true');
        if (!off && metrics) {
          cell.textContent = metrics.profit;
        } else {
          cell.textContent = getMonthlyProfitCellValue(off, iso);
        }"""

MAKE_PROFIT_NEW = f"""        var cell = document.createElement('span');
        cell.className = 'monthly-data-column__cell';
        cell.setAttribute('aria-hidden', 'true');
        {MARKER}
        if (skeleton) {{
          cell.textContent = OFF_CELL_DASH;
        }} else if (!off && metrics) {{
          cell.textContent = metrics.profit;
        }} else {{
          cell.textContent = getMonthlyProfitCellValue(off, iso);
        }}"""

MAKE_PROFIT_FN_OLD = """      function makeProfitColumn(buffer, off, iso, aria, metrics) {"""

MAKE_PROFIT_FN_NEW = """      function makeProfitColumn(buffer, off, iso, aria, metrics, skeleton) {"""

REBUILD_CHUNKED_OLD = """      function rebuildColumnsChunked(runToken, onDone) {
        /* KPI-MRP-PHASE2-5 */
        window.__monthlyTwColumnsBusy = true;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);
        invalidateGroup1TwCache();
        isoToIndex = {};
        var fragDate = document.createDocumentFragment();
        var fragGroup1 = document.createDocumentFragment();
        var fragGroup2 = document.createDocumentFragment();
        var fragGroup3 = document.createDocumentFragment();
        var fragProfit = document.createDocumentFragment();
        var y = state.year;
        var m0 = state.month0;
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
        var days = [];
        for (var d = new Date(start.getFullYear(), start.getMonth(), start.getDate()); d <= end; d = addDays(d, 1)) {
          days.push(new Date(d.getFullYear(), d.getMonth(), d.getDate()));
        }
        var metricsByIso = Object.create(null);
        var g1Label = useJa ? 'グループ1' : 'Group 1';
        var g2Label = useJa ? 'グループ2' : 'Group 2';
        var g3Label = useJa ? 'グループ3' : 'Group 3';
        var cursor = 0;
        var FRAME_BUDGET_MS = 10;
        function buildChunk() {
          if (runToken !== __monthlyRebuildRunToken) return;
          var t0 =
            typeof performance !== 'undefined' && performance.now
              ? performance.now()
              : 0;
          while (cursor < days.length) {
            var dayObj = days[cursor];
            var iso = toISODateLocal(dayObj);
            var inMonth = dayObj.getMonth() === m0 && dayObj.getFullYear() === y;
            var buffer = !inMonth;
            var off = !isBusinessDayByIso(iso, dayObj);
            var metrics = getMonthlyRebuildMetrics(metricsByIso, dayObj);
            isoToIndex[iso] = cursor;
            var p = document.createElement('p');
            p.className = 'monthly-date-header-cell';
            if (off) p.classList.add('monthly-date-header-cell--off');
            if (buffer) p.classList.add('monthly-date-header-cell--buffer');
            p.setAttribute('data-iso', iso);
            p.textContent = dateLabelText(dayObj);
            p.setAttribute('aria-label', ariaDateLabel(dayObj, inMonth));
            fragDate.appendChild(p);
            var colNum = cursor + 1;
            var inactiveSuffix = (buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : '';
            fragGroup1.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g1Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
                1,
                metrics
              )
            );
            fragGroup2.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g2Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
                2,
                metrics
              )
            );
            fragGroup3.appendChild(
              makeGroupColumn(
                buffer,
                off,
                iso,
                g3Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
                3,
                metrics
              )
            );
            fragProfit.appendChild(
              makeProfitColumn(
                buffer,
                off,
                iso,
                (useJa ? 'Profit 列' : 'Profit column ') + colNum + inactiveSuffix,
                metrics
              )
            );
            cursor += 1;
            if (FRAME_BUDGET_MS > 0 && t0 > 0 && performance.now() - t0 >= FRAME_BUDGET_MS) {
              break;
            }
          }
          if (cursor < days.length) {
            window.requestAnimationFrame(buildChunk);
            return;
          }
          if (runToken !== __monthlyRebuildRunToken) return;
          function commitTracksStep(step) {
            if (runToken !== __monthlyRebuildRunToken) return;
            if (step === 0) trackDate.replaceChildren(fragDate);
            else if (step === 1) trackGroup1.replaceChildren(fragGroup1);
            else if (step === 2) trackGroup2.replaceChildren(fragGroup2);
            else if (step === 3) trackGroup3.replaceChildren(fragGroup3);
            else if (step === 4) trackProfit.replaceChildren(fragProfit);
            else {
              scheduleVFocusUpdate();
              if (typeof onDone === 'function') onDone();
              return;
            }
            window.requestAnimationFrame(function () {
              commitTracksStep(step + 1);
            });
          }
          window.requestAnimationFrame(function () {
            commitTracksStep(0);
          });
        }
        window.requestAnimationFrame(buildChunk);
      }"""

REBUILD_CHUNKED_NEW = f"""      {MARKER}
      function hydrateMonthlyColumnCells(colEl, groupNo, metrics, iso, buffer, off) {{
        if (!colEl) return;
        var cells = colEl.querySelectorAll('.monthly-data-column__cell');
        var values;
        if (off || !metrics || metrics.off) {{
          values = getMonthlyGroupCellValues(groupNo, off, iso);
        }} else if (groupNo === 1) {{
          values = metrics.g1;
        }} else if (groupNo === 2) {{
          values = metrics.g2;
        }} else {{
          values = metrics.g3;
        }}
        for (var hi = 0; hi < 6; hi++) {{
          if (!cells[hi]) continue;
          cells[hi].textContent = values[hi] || '';
          if (groupNo === 1) decorateMonthlyGroup1Cell(cells[hi], hi, iso, buffer);
        }}
      }}
      function hydrateMonthlyProfitCell(colEl, metrics, off, iso) {{
        if (!colEl) return;
        var cell = colEl.querySelector('.monthly-data-column__cell');
        if (!cell) return;
        if (off || !metrics || metrics.off) {{
          cell.textContent = getMonthlyProfitCellValue(off, iso);
        }} else {{
          cell.textContent = metrics.profit;
        }}
      }}
      function commitMonthlyTracksSync(fragDate, fragGroup1, fragGroup2, fragGroup3, fragProfit) {{
        trackDate.replaceChildren(fragDate);
        trackGroup1.replaceChildren(fragGroup1);
        trackGroup2.replaceChildren(fragGroup2);
        trackGroup3.replaceChildren(fragGroup3);
        trackProfit.replaceChildren(fragProfit);
      }}
      function scheduleMonthlyTwHydrate(runToken, days, y, m0) {{
        var metricsByIso = Object.create(null);
        var hydrateCursor = 0;
        var HYDRATE_BUDGET_MS = 10;
        function hydrateChunk() {{
          if (runToken !== __monthlyRebuildRunToken) return;
          var t0 =
            typeof performance !== 'undefined' && performance.now
              ? performance.now()
              : 0;
          while (hydrateCursor < days.length) {{
            var dayObj = days[hydrateCursor];
            var iso = toISODateLocal(dayObj);
            var inMonth = dayObj.getMonth() === m0 && dayObj.getFullYear() === y;
            var buffer = !inMonth;
            var off = !isBusinessDayByIso(iso, dayObj);
            var metrics = getMonthlyRebuildMetrics(metricsByIso, dayObj);
            var colIdx = hydrateCursor;
            hydrateMonthlyColumnCells(
              trackGroup1.children[colIdx],
              1,
              metrics,
              iso,
              buffer,
              off
            );
            hydrateMonthlyColumnCells(
              trackGroup2.children[colIdx],
              2,
              metrics,
              iso,
              buffer,
              off
            );
            hydrateMonthlyColumnCells(
              trackGroup3.children[colIdx],
              3,
              metrics,
              iso,
              buffer,
              off
            );
            hydrateMonthlyProfitCell(trackProfit.children[colIdx], metrics, off, iso);
            hydrateCursor += 1;
            if (HYDRATE_BUDGET_MS > 0 && t0 > 0 && performance.now() - t0 >= HYDRATE_BUDGET_MS) {{
              break;
            }}
          }}
          if (hydrateCursor < days.length) {{
            window.requestAnimationFrame(hydrateChunk);
            return;
          }}
          if (runToken !== __monthlyRebuildRunToken) return;
          document.documentElement.setAttribute('data-monthly-tw-hydrated', '1');
          scheduleVFocusUpdate();
        }}
        window.requestAnimationFrame(hydrateChunk);
      }}
      function rebuildColumnsChunked(runToken, onDone) {{
        /* KPI-MRP-PHASE2-5 */
        window.__monthlyTwColumnsBusy = true;
        document.documentElement.setAttribute('data-monthly-tw-hydrated', '0');
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        isoToIndex = {{}};
        var fragDate = document.createDocumentFragment();
        var fragGroup1 = document.createDocumentFragment();
        var fragGroup2 = document.createDocumentFragment();
        var fragGroup3 = document.createDocumentFragment();
        var fragProfit = document.createDocumentFragment();
        var y = state.year;
        var m0 = state.month0;
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
        var days = [];
        for (var d = new Date(start.getFullYear(), start.getMonth(), start.getDate()); d <= end; d = addDays(d, 1)) {{
          days.push(new Date(d.getFullYear(), d.getMonth(), d.getDate()));
        }}
        var g1Label = useJa ? 'グループ1' : 'Group 1';
        var g2Label = useJa ? 'グループ2' : 'Group 2';
        var g3Label = useJa ? 'グループ3' : 'Group 3';
        for (var cursor = 0; cursor < days.length; cursor++) {{
          var dayObj = days[cursor];
          var iso = toISODateLocal(dayObj);
          var inMonth = dayObj.getMonth() === m0 && dayObj.getFullYear() === y;
          var buffer = !inMonth;
          var off = !isBusinessDayByIso(iso, dayObj);
          isoToIndex[iso] = cursor;
          var p = document.createElement('p');
          p.className = 'monthly-date-header-cell';
          if (off) p.classList.add('monthly-date-header-cell--off');
          if (buffer) p.classList.add('monthly-date-header-cell--buffer');
          p.setAttribute('data-iso', iso);
          p.textContent = dateLabelText(dayObj);
          p.setAttribute('aria-label', ariaDateLabel(dayObj, inMonth));
          fragDate.appendChild(p);
          var colNum = cursor + 1;
          var inactiveSuffix = (buffer || off) ? (useJa ? '（非アクティブ）' : ' (inactive)') : '';
          fragGroup1.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g1Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
              1,
              null,
              true
            )
          );
          fragGroup2.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g2Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
              2,
              null,
              true
            )
          );
          fragGroup3.appendChild(
            makeGroupColumn(
              buffer,
              off,
              iso,
              g3Label + ' ' + (useJa ? '列' : 'column ') + colNum + inactiveSuffix,
              3,
              null,
              true
            )
          );
          fragProfit.appendChild(
            makeProfitColumn(
              buffer,
              off,
              iso,
              (useJa ? 'Profit 列' : 'Profit column ') + colNum + inactiveSuffix,
              null,
              true
            )
          );
        }}
        if (runToken !== __monthlyRebuildRunToken) return;
        commitMonthlyTracksSync(fragDate, fragGroup1, fragGroup2, fragGroup3, fragProfit);
        scheduleVFocusUpdate();
        if (typeof onDone === 'function') onDone();
        loadMonthlyMepMetricsForYear(state.year);
        primeMonthlyTwTargetCache(state.year);
        invalidateGroup1TwCache();
        scheduleMonthlyTwHydrate(runToken, days, y, m0);
      }}"""


def apply_replacements(text: str) -> str:
    pairs = [
        (CSS_ANCHOR_OLD, CSS_ANCHOR_NEW),
        (MAKE_GROUP_OLD, MAKE_GROUP_NEW),
        (MAKE_PROFIT_FN_OLD, MAKE_PROFIT_FN_NEW),
        (MAKE_PROFIT_OLD, MAKE_PROFIT_NEW),
        (REBUILD_CHUNKED_OLD, REBUILD_CHUNKED_NEW),
    ]
    for old, new in pairs:
        if old not in text:
            raise ValueError(f"anchor not found ({old[:72]}...)")
        text = text.replace(old, new, 1)
    return text


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"MISSING: {path}", file=sys.stderr)
            return 1
        original = path.read_text(encoding="utf-8")
        if MARKER in original:
            print(f"SKIP (already applied): {path}")
            continue
        updated = apply_replacements(original)
        path.write_text(updated, encoding="utf-8")
        print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

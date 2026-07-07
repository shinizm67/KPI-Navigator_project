#!/usr/bin/env python3
"""MRP Phase 3.2 — Reduce monthly cockpit sync cost under slow CPU."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]
MARKER = "/* KPI-MRP-PHASE3-2 */"

TICK_OLD = """        function scheduleCockpitChunkTick(fn) {
          if (typeof window.requestIdleCallback === 'function') {
            window.requestIdleCallback(fn, { timeout: 56 });
          } else {
            window.setTimeout(fn, 16);
          }
        }"""

TICK_NEW = f"""        {MARKER}
        function scheduleCockpitChunkTick(fn) {{
          if (typeof window.requestIdleCallback === 'function') {{
            window.requestIdleCallback(fn, {{ timeout: 40 }});
          }} else {{
            window.setTimeout(fn, 12);
          }}
        }}
        function resolveBusinessDayMapForCockpitFast(year) {{
          var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
          var bmap = daily && daily.businessDayByDate;
          if (bmap && typeof bmap === 'object') return bmap;
          return resolveBusinessDayMapForCockpit();
        }}"""

SYNC_START_OLD = """        function scheduleSyncCockpitChunked(explicitYear) {
          __syncCockpitChunkToken += 1;
          var token = __syncCockpitChunkToken;
          var year = resolveCalendarYear(explicitYear);
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
          }
          var annualTarget = resolveAnnualTarget(year);"""

SYNC_START_NEW = f"""        function scheduleSyncCockpitChunked(explicitYear) {{
          __syncCockpitChunkToken += 1;
          var token = __syncCockpitChunkToken;
          var year = resolveCalendarYear(explicitYear);
          var annualTarget = resolveAnnualTarget(year);"""

BMAP_OLD = """          var bmap = resolveBusinessDayMapForCockpit();
          var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var monthlySales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var monthlyAny = [false, false, false, false, false, false, false, false, false, false, false, false];
          var totalBD = 0;
          Object.keys(bmap || {}).forEach(function (iso) {
            if (!bmap[iso]) return;
            if (String(iso).slice(0, 4) !== String(year)) return;
            var m = Number(String(iso).slice(5, 7)) - 1;
            if (!Number.isFinite(m) || m < 0 || m > 11) return;
            monthlyBD[m] += 1;
            totalBD += 1;
            var amtDay = readDailySalesAmount(iso);
            if (Number.isFinite(amtDay) && amtDay > 0) {
              monthlySales[m] += amtDay;
              monthlyAny[m] = true;
            }
          });"""

BMAP_NEW = """          var bmap = resolveBusinessDayMapForCockpitFast(year);
          if (
            (!bmap || !Object.keys(bmap).length) &&
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
            bmap = resolveBusinessDayMapForCockpitFast(year);
          }
          var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var monthlySales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var monthlyAny = [false, false, false, false, false, false, false, false, false, false, false, false];
          var totalBD = 0;
          var yearPrefix = String(year) + '-';
          Object.keys(bmap || {}).forEach(function (iso) {
            if (!bmap[iso]) return;
            if (String(iso).indexOf(yearPrefix) !== 0) return;
            var m = Number(String(iso).slice(5, 7)) - 1;
            if (!Number.isFinite(m) || m < 0 || m > 11) return;
            monthlyBD[m] += 1;
            totalBD += 1;
            var amtDay = readDailySalesAmount(iso);
            if (Number.isFinite(amtDay) && amtDay > 0) {
              monthlySales[m] += amtDay;
              monthlyAny[m] = true;
            }
          });"""

BUDGET_OLD = """          var monthCursor = 0;
          var COCKPIT_CHUNK_BUDGET_MS = 6;"""
BUDGET_NEW = """          var monthCursor = 0;
          var COCKPIT_CHUNK_BUDGET_MS = 3;"""


def apply(text: str) -> str:
    for old, new in [
        (TICK_OLD, TICK_NEW),
        (SYNC_START_OLD, SYNC_START_NEW),
        (BMAP_OLD, BMAP_NEW),
        (BUDGET_OLD, BUDGET_NEW),
    ]:
        if old not in text:
            raise ValueError(f"anchor not found: {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text


def main() -> int:
    for page in PAGES:
        src = page.read_text(encoding="utf-8")
        if MARKER in src:
            print(f"SKIP: {page}")
            continue
        out = apply(src)
        page.write_text(out, encoding="utf-8")
        print(f"OK: {page}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


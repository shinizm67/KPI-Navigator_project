#!/usr/bin/env python3
"""MRP Phase 3.1 — Fast cockpit chunk precompute + field selector cache."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]
MARKER = "/* KPI-MRP-PHASE3-1 */"

SET_FIELD_OLD = """        function setField(monthKey, field, text) {
          var el = document.querySelector(
            '[data-field="annual.table.' + monthKey + '.' + field + '"]'
          );
          if (el) el.textContent = text;
        }"""

SET_FIELD_NEW = f"""        {MARKER}
        var __cockpitFieldCache = Object.create(null);
        function setField(monthKey, field, text) {{
          var key = monthKey + '.' + field;
          var el = __cockpitFieldCache[key];
          if (!el) {{
            el = document.querySelector(
              '[data-field="annual.table.' + monthKey + '.' + field + '"]'
            );
            if (el) __cockpitFieldCache[key] = el;
          }}
          if (el) el.textContent = text;
        }}"""

PRECOMPUTE_OLD = """          syncAnnualTargetDisplay(year, hasPlan ? Number(annualTarget) : null);
          var monthlyBD = [];
          var totalBD = 0;
          for (var mi = 0; mi < 12; mi++) {
            var bd = countBusinessDaysInMonth(year, mi);
            monthlyBD.push(bd);
            totalBD += bd;
          }
          var ctx = {
            year: year,
            annualTarget: annualTarget,
            weights: weights,
            hasPlan: hasPlan,
            monthlyBD: monthlyBD,
            totalBD: totalBD,
            salesAmt: 0,
            gatheredAny: false,
          };"""

PRECOMPUTE_NEW = """          syncAnnualTargetDisplay(year, hasPlan ? Number(annualTarget) : null);
          var bmap = resolveBusinessDayMapForCockpit();
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
          });
          var ctx = {
            year: year,
            annualTarget: annualTarget,
            weights: weights,
            hasPlan: hasPlan,
            monthlyBD: monthlyBD,
            monthlySales: monthlySales,
            monthlyAny: monthlyAny,
            totalBD: totalBD,
            salesAmt: 0,
            gatheredAny: false,
          };"""

LOOP_OLD = """              var gatheredMonth = gatherMonthlySalesForMonth(year, monthCursor);
              ctx.salesAmt = gatheredMonth.sum;
              ctx.gatheredAny = gatheredMonth.any;
              applyCockpitMonthRow(monthCursor, ctx);"""

LOOP_NEW = """              ctx.salesAmt = ctx.monthlySales[monthCursor] || 0;
              ctx.gatheredAny = !!ctx.monthlyAny[monthCursor];
              applyCockpitMonthRow(monthCursor, ctx);"""


def apply(text: str) -> str:
    pairs = [
        (SET_FIELD_OLD, SET_FIELD_NEW),
        (PRECOMPUTE_OLD, PRECOMPUTE_NEW),
        (LOOP_OLD, LOOP_NEW),
    ]
    for old, new in pairs:
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

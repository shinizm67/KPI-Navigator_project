#!/usr/bin/env python3
"""MRP Phase 2.8 — Chunked Cockpit sync on Monthly; defer until TW ready; pause on interaction."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-8 */"

GATHER_MONTH_FN = f"""        document.addEventListener('annual:pastSalesSaved', clearGatheredMonthlySalesCache);

        {MARKER}
        function gatherMonthlySalesForMonth(year, m0) {{
          year = Number(year);
          m0 = Number(m0);
          var cached = __gatheredMonthlySalesByYear[year];
          if (cached) {{
            var amt = cached.sales[m0];
            return {{
              sum: amt,
              any: cached.any && Number.isFinite(amt) && amt > 0,
            }};
          }}
          var sum = 0;
          var any = false;
          var dc = new Date(year, m0 + 1, 0).getDate();
          for (var day = 1; day <= dc; day++) {{
            if (!isCalendarBusinessDay(year, m0, day)) continue;
            var iso = year + '-' + pad2(m0 + 1) + '-' + pad2(day);
            var amtDay = readDailySalesAmount(iso);
            if (Number.isFinite(amtDay) && amtDay > 0) {{
              sum += amtDay;
              any = true;
            }}
          }}
          return {{ sum: sum, any: any }};
        }}
        function scheduleCockpitChunkTick(fn) {{
          if (typeof window.requestIdleCallback === 'function') {{
            window.requestIdleCallback(fn, {{ timeout: 56 }});
          }} else {{
            window.setTimeout(fn, 16);
          }}
        }}
        var __syncCockpitChunkToken = 0;
        function applyCockpitMonthRow(m0, ctx) {{
          var mk = MONTH_KEYS[m0];
          var bdCount = ctx.monthlyBD[m0];
          setField(mk, 'businessDay', String(bdCount));
          if (!ctx.hasPlan) {{
            setField(mk, 'monthlyAverageTarget', DASH);
            setField(mk, 'hlSeasonPct', DASH);
            setField(mk, 'monthlyTarget', DASH);
            setField(mk, 'dailyTarget', DASH);
            setField(mk, 'monthlyProfit', DASH);
            setField(mk, 'monthlyKgi', DASH);
            setField(mk, 'hlSeasonActualPct', DASH);
            setField(mk, 'hlPercent', DASH);
            return;
          }}
          var hl = ctx.weights && ctx.weights[m0] != null ? Number(ctx.weights[m0]) : 100;
          var monthlyAvg =
            ctx.totalBD > 0 ? (Number(ctx.annualTarget) * bdCount) / ctx.totalBD : NaN;
          var monthlyTarget =
            Number.isFinite(monthlyAvg) ? (monthlyAvg * hl) / 100 : NaN;
          var dailyTarget =
            bdCount > 0 && Number.isFinite(monthlyTarget)
              ? monthlyTarget / bdCount
              : NaN;
          setField(mk, 'monthlyAverageTarget', fmtMoney(monthlyAvg));
          setField(mk, 'hlSeasonPct', Number.isFinite(hl) ? hl + '%' : DASH);
          setField(mk, 'monthlyTarget', fmtMoney(monthlyTarget));
          setField(mk, 'dailyTarget', fmtMoney(dailyTarget));
          var salesAmt = ctx.salesAmt;
          if (ctx.gatheredAny && Number.isFinite(salesAmt) && salesAmt > 0) {{
            setField(mk, 'monthlyProfit', fmtMoney(salesAmt));
            setField(mk, 'monthlyKgi', fmtSignedMoney(salesAmt - monthlyTarget));
            setField(
              mk,
              'hlSeasonActualPct',
              monthlyAvg > 0 ? fmtPct((salesAmt / monthlyAvg) * 100) : DASH
            );
            setField(
              mk,
              'hlPercent',
              monthlyTarget > 0 ? fmtPct((salesAmt / monthlyTarget) * 100) : DASH
            );
          }} else {{
            setField(mk, 'monthlyProfit', DASH);
            setField(mk, 'monthlyKgi', DASH);
            setField(mk, 'hlSeasonActualPct', DASH);
            setField(mk, 'hlPercent', DASH);
          }}
        }}
        function scheduleSyncCockpitChunked(explicitYear) {{
          __syncCockpitChunkToken += 1;
          var token = __syncCockpitChunkToken;
          var year = resolveCalendarYear(explicitYear);
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {{
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
          }}
          var annualTarget = resolveAnnualTarget(year);
          var weights = null;
          if (window.KpiYearStore) {{
            weights = KpiYearStore.readMonthlyHlWeights(year);
          }}
          var hasPlan =
            annualTarget != null &&
            Number.isFinite(Number(annualTarget)) &&
            Number(annualTarget) > 0;
          if (!weights && hasPlan) weights = DEFAULT_HL_WEIGHTS.slice();
          syncAnnualTargetDisplay(year, hasPlan ? Number(annualTarget) : null);
          var monthlyBD = [];
          var totalBD = 0;
          for (var mi = 0; mi < 12; mi++) {{
            var bd = countBusinessDaysInMonth(year, mi);
            monthlyBD.push(bd);
            totalBD += bd;
          }}
          var ctx = {{
            year: year,
            annualTarget: annualTarget,
            weights: weights,
            hasPlan: hasPlan,
            monthlyBD: monthlyBD,
            totalBD: totalBD,
            salesAmt: 0,
            gatheredAny: false,
          }};
          var monthCursor = 0;
          var COCKPIT_CHUNK_BUDGET_MS = 6;
          function chunkTick() {{
            if (token !== __syncCockpitChunkToken) return;
            if (
              window.__monthlyTwHydratePaused ||
              window.__monthlyTwColumnsBusy
            ) {{
              scheduleCockpitChunkTick(chunkTick);
              return;
            }}
            var t0 =
              typeof performance !== 'undefined' && performance.now
                ? performance.now()
                : 0;
            while (monthCursor < 12) {{
              var gatheredMonth = gatherMonthlySalesForMonth(year, monthCursor);
              ctx.salesAmt = gatheredMonth.sum;
              ctx.gatheredAny = gatheredMonth.any;
              applyCockpitMonthRow(monthCursor, ctx);
              monthCursor += 1;
              if (
                COCKPIT_CHUNK_BUDGET_MS > 0 &&
                t0 > 0 &&
                performance.now() - t0 >= COCKPIT_CHUNK_BUDGET_MS
              ) {{
                break;
              }}
            }}
            if (monthCursor < 12) {{
              scheduleCockpitChunkTick(chunkTick);
              return;
            }}
            if (token !== __syncCockpitChunkToken) return;
            if (
              window.__ANNUAL_UI &&
              typeof window.__ANNUAL_UI.recalcMonthlyAllocationTotal === 'function'
            ) {{
              window.__ANNUAL_UI.recalcMonthlyAllocationTotal();
            }}
            if (typeof window.refreshArea1Cockpit === 'function') {{
              window.refreshArea1Cockpit();
            }}
          }}
          scheduleCockpitChunkTick(chunkTick);
        }}

        function parseTargetFromDom() {{"""

GATHER_MONTH_ANCHOR_OLD = """        document.addEventListener('annual:pastSalesSaved', clearGatheredMonthlySalesCache);

        function parseTargetFromDom() {"""

CORE_ROUTE_OLD = """        function syncCockpitForCalendarYearCore(explicitYear) {
          var year = resolveCalendarYear(explicitYear);
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
          }"""

CORE_ROUTE_NEW = f"""        function syncCockpitForCalendarYearCore(explicitYear) {{
          {MARKER}
          if (document.body.classList.contains('monthly-page')) {{
            scheduleSyncCockpitChunked(explicitYear);
            return;
          }}
          var year = resolveCalendarYear(explicitYear);
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {{
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
          }}"""

PAGE_READY_OLD = """            document.addEventListener(
              'monthly:pageReady',
              function () {
                /* KPI-MRP-PHASE2-5 */
                /* 初回 Cockpit 同期は idle に退避し、矢印操作とのメインスレッド競合を避ける */
                var runSync = function () {
                  syncCockpitForCalendarYear();
                };
                if (typeof window.requestIdleCallback === 'function') {
                  window.requestIdleCallback(runSync, { timeout: 800 });
                } else {
                  window.setTimeout(runSync, 400);
                }
              },
              { once: true }
            );"""

PAGE_READY_NEW = f"""            document.addEventListener(
              'monthly:pageReady',
              function () {{
                {MARKER}
                /* Area1 ストリップのみ即時。12ヶ月表は TW 準備後にチャンク同期 */
                window.requestAnimationFrame(function () {{
                  if (typeof window.refreshArea1Cockpit === 'function') {{
                    window.refreshArea1Cockpit();
                  }}
                }});
                var runChunkedSync = function () {{
                  scheduleSyncCockpitChunked();
                }};
                var twWaitStarted =
                  typeof performance !== 'undefined' && performance.now
                    ? performance.now()
                    : 0;
                var waitTwThenSync = function () {{
                  if (document.documentElement.getAttribute('data-monthly-tw-hydrated') === '1') {{
                    scheduleCockpitChunkTick(runChunkedSync);
                    return;
                  }}
                  if (
                    twWaitStarted > 0 &&
                    performance.now() - twWaitStarted > 4000
                  ) {{
                    scheduleCockpitChunkTick(runChunkedSync);
                    return;
                  }}
                  scheduleCockpitChunkTick(waitTwThenSync);
                }};
                if (typeof window.requestIdleCallback === 'function') {{
                  window.requestIdleCallback(waitTwThenSync, {{ timeout: 2800 }});
                }} else {{
                  window.setTimeout(waitTwThenSync, 900);
                }}
              }},
              {{ once: true }}
            );"""


def apply_replacements(text: str) -> str:
    pairs = [
        (GATHER_MONTH_ANCHOR_OLD, GATHER_MONTH_FN),
        (CORE_ROUTE_OLD, CORE_ROUTE_NEW),
        (PAGE_READY_OLD, PAGE_READY_NEW),
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

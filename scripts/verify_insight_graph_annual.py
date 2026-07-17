#!/usr/bin/env python3
"""検証: Graph Annual Graph1 が Store 実データ + Insight 日付追従すること.

Graph2 はデモのまま残す。Graph Monthly も壊れていないこと。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]
YEAR = 2026
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def build_seed() -> dict:
    import datetime

    daily_sales = {}
    business_days = {}
    d = datetime.date(YEAR, 1, 1)
    end = datetime.date(YEAR, 7, 14)
    while d <= end:
        iso = d.isoformat()
        wk = d.weekday() >= 5
        business_days[iso] = not wk
        if not wk:
            daily_sales[iso] = 1000 + d.timetuple().tm_yday * 3
        d += datetime.timedelta(days=1)
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": YEAR,
            "legacyMigrated": True,
            "selectedDate": f"{YEAR}-07-14",
        },
        "timeline": {"dailySales": daily_sales, "businessDays": business_days},
        "years": {
            str(YEAR): {
                "year": YEAR,
                "status": "open",
                "plan": {
                    "targetSales": 600000,
                    "monthlyHlWeights": [100] * 12,
                },
            }
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    seed = build_seed()
    page.add_init_script(
        "window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);"
        % json.dumps(json.dumps(seed))
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.__buildAnnualCumulativeTrendPayload === 'function' && "
        "typeof window.renderInsightTwDiffs === 'function'",
        timeout=20000,
    )

    result = page.evaluate(
        """() => {
          const isoA = '2026-06-30';
          const isoB = '2026-07-14';
          const builtA = window.__buildAnnualCumulativeTrendPayload(2026, isoA);
          const builtB = window.__buildAnnualCumulativeTrendPayload(2026, isoB);

          // open insight if needed
          const openBtn = document.getElementById('global-nav-index-btn');
          if (openBtn) openBtn.click();

          // force insight date + re-render graphs via event path
          window.__INSIGHT_SELECTED_ISO = isoA;
          document.dispatchEvent(new CustomEvent('insight:dateChanged', { detail: { iso: isoA } }));

          const frame = document.querySelector('#insight-graph-annual-graph1 .insight-graph-annual-trend__frame');
          const stateA = frame && frame.__trendChartState;
          const periodA = document.getElementById('insight-graph-annual-graph1-period');

          window.__INSIGHT_SELECTED_ISO = isoB;
          document.dispatchEvent(new CustomEvent('insight:dateChanged', { detail: { iso: isoB } }));
          const stateB = frame && frame.__trendChartState;

          const html = document.documentElement.innerHTML;
          const g2i = html.indexOf('function initGraphAnnualCumulativeTrendGraph2');
          const g2slice = g2i >= 0 ? html.slice(g2i, g2i + 12000) : '';
          const hasMonthlyStore = typeof window.__buildMonthlyCumulativeTrendPayload === 'function';

          return {
            builtA: builtA ? {
              dim: builtA.target.length,
              todayDay: builtA.todayDay,
              aAt: builtA.actual[builtA.todayDay - 1],
              tAt: builtA.target[builtA.todayDay - 1],
            } : null,
            builtB: builtB ? {
              dim: builtB.target.length,
              todayDay: builtB.todayDay,
              aAt: builtB.actual[builtB.todayDay - 1],
            } : null,
            stateA: stateA ? {
              todayDay: stateA.payload.todayDay,
              aAt: stateA.payload.actual[stateA.payload.todayDay - 1],
              tAt: stateA.payload.target[stateA.payload.todayDay - 1],
              year: stateA.ctx.year,
            } : null,
            stateB: stateB ? {
              todayDay: stateB.payload.todayDay,
              aAt: stateB.payload.actual[stateB.payload.todayDay - 1],
            } : null,
            periodText: periodA ? periodA.textContent : null,
            graph2Wired:
              g2slice.indexOf('buildStoreComparePayload') >= 0 &&
              g2slice.indexOf('buildComparePayload') >= 0,
            hasMonthlyStore,
            seriesCount: document.querySelectorAll('#insight-graph-annual-graph1-chart .insight-graph-annual-trend__series path').length,
          };
        }"""
    )

    if not result.get("builtA") or not result.get("builtB"):
        problems.append(f"{url}: builder null")
        return problems

    if result["builtA"]["dim"] not in (365, 366):
        problems.append(f"{url}: dim={result['builtA']['dim']}")

    # June 30 2026 is day-of-year 181
    if result["builtA"]["todayDay"] != 181:
        problems.append(f"{url}: June30 todayDay={result['builtA']['todayDay']} != 181")
    if result["builtB"]["todayDay"] != 195:
        problems.append(f"{url}: July14 todayDay={result['builtB']['todayDay']} != 195")

    sa = result.get("stateA")
    sb = result.get("stateB")
    if not sa or not sb:
        problems.append(f"{url}: chart state missing {result}")
        return problems

    if sa["todayDay"] != result["builtA"]["todayDay"]:
        problems.append(f"{url}: stateA todayDay {sa['todayDay']} != built {result['builtA']['todayDay']}")
    if abs(sa["aAt"] - result["builtA"]["aAt"]) > 0.01:
        problems.append(f"{url}: stateA actual {sa['aAt']} != built {result['builtA']['aAt']}")
    if abs(sa["tAt"] - result["builtA"]["tAt"]) > 0.01:
        problems.append(f"{url}: stateA target {sa['tAt']} != built {result['builtA']['tAt']}")

    if sb["todayDay"] != result["builtB"]["todayDay"]:
        problems.append(f"{url}: stateB todayDay mismatch")
    if abs(sb["aAt"] - result["builtB"]["aAt"]) > 0.01:
        problems.append(f"{url}: stateB actual mismatch")

    if result.get("periodText") != "2026":
        problems.append(f"{url}: period={result.get('periodText')!r}")

    if not result.get("graph2Wired"):
        problems.append(f"{url}: Graph2 store compare wiring missing")

    if not result.get("hasMonthlyStore"):
        problems.append(f"{url}: Monthly builder missing")

    if result.get("seriesCount", 0) < 1:
        problems.append(f"{url}: no series paths drawn")

    # demo amounts are ~millions yen; store seed cumulatives are much smaller
    if sa["aAt"] > 500000:
        problems.append(f"{url}: looks like demo actual still in use aAt={sa['aAt']}")

    print(f"  {url.split('/kpi-navigator/')[-1]}")
    print(f"    builtA={result['builtA']} stateA={sa}")
    print(f"    builtB={result['builtB']} stateB={sb}")
    return problems


def main() -> int:
    launch_kwargs = {"headless": True}
    if EXE.exists():
        launch_kwargs["executable_path"] = str(EXE)

    all_problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        for page_path in PAGES:
            context = browser.new_context()
            page = context.new_page()
            try:
                all_problems += verify_page(page, page_path.as_uri())
            except Exception as e:  # noqa: BLE001
                all_problems.append(f"{page_path}: EXCEPTION {e}")
            finally:
                context.close()
        browser.close()

    print("\n=== RESULT ===")
    if all_problems:
        for pr in all_problems:
            print("NG:", pr)
        return 1
    print("OK: Graph Annual Graph1 = Store + Insight日付追従（Graph2 wiring も確認）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""検証: Graph Annual Graph2 実データ + Insight 日付追従。Graph1 回帰も確認。"""

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
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def build_seed() -> dict:
    import datetime

    daily_sales = {}
    business_days = {}

    def fill_year(year, daily_base):
        d = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
        while d <= end:
            iso = d.isoformat()
            wk = d.weekday() >= 5
            business_days[iso] = not wk
            if not wk:
                daily_sales[iso] = daily_base + d.timetuple().tm_yday
            d += datetime.timedelta(days=1)

    # 2025 = best (higher base), 2024 lower, 2026 current mid
    fill_year(2024, 800)
    fill_year(2025, 2000)
    fill_year(2026, 1000)

    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {"dailySales": daily_sales, "businessDays": business_days},
        "years": {
            "2024": {"year": 2024, "status": "closed", "plan": {"targetSales": 500000, "monthlyHlWeights": [100] * 12}},
            "2025": {"year": 2025, "status": "closed", "plan": {"targetSales": 550000, "monthlyHlWeights": [100] * 12}},
            "2026": {"year": 2026, "status": "open", "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12}},
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
        "() => typeof window.__buildAnnualCompareTrendPayload === 'function' && "
        "typeof window.__buildAnnualCumulativeTrendPayload === 'function'",
        timeout=20000,
    )

    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const built = window.__buildAnnualCompareTrendPayload(2026, iso);
          const g1 = window.__buildAnnualCumulativeTrendPayload(2026, iso);

          document.getElementById('global-nav-index-btn').click();
          window.__INSIGHT_SELECTED_ISO = iso;
          document.dispatchEvent(new CustomEvent('insight:dateChanged', { detail: { iso } }));

          const frame2 = document.querySelector('#insight-graph-annual-graph2 .insight-graph-annual-trend__frame');
          const frame1 = document.querySelector('#insight-graph-annual-graph1 .insight-graph-annual-trend__frame');
          const st2 = frame2 && frame2.__trendChartState;
          const st1 = frame1 && frame1.__trendChartState;

          window.__INSIGHT_SELECTED_ISO = '2026-06-30';
          document.dispatchEvent(new CustomEvent('insight:dateChanged', { detail: { iso: '2026-06-30' } }));
          const st2b = frame2 && frame2.__trendChartState;
          const st1b = frame1 && frame1.__trendChartState;

          const html = document.documentElement.innerHTML;
          const g1i = html.indexOf('function initGraphAnnualCumulativeTrendGraph1');
          const g2i = html.indexOf('function initGraphAnnualCumulativeTrendGraph2');
          const g1slice = html.slice(g1i, g2i);
          const openSlice = html.slice(
            html.indexOf(\"var dateBtnEl = document.getElementById('insight-overlay-date-btn')\"),
            html.indexOf(\"var dateBtnEl = document.getElementById('insight-overlay-date-btn')\") + 8000
          );

          return {
            built: built && {
              todayDay: built.todayDay,
              bestYear: built.bestYear,
              curEnd: built.current[built.current.length - 1],
              lyEnd: built.lastYear[built.lastYear.length - 1],
              bestEnd: built.best[built.best.length - 1],
              dim: built.lastYear.length,
            },
            g1End: g1 && g1.actual[g1.todayDay - 1],
            st2: st2 && {
              todayDay: st2.payload.todayDay,
              curEnd: st2.payload.current[st2.payload.current.length - 1],
              bestEnd: st2.payload.best[st2.dim - 1],
            },
            st1: st1 && {
              todayDay: st1.payload.todayDay,
              aAt: st1.payload.actual[st1.payload.todayDay - 1],
            },
            st2bToday: st2b && st2b.payload.todayDay,
            st1bToday: st1b && st1b.payload.todayDay,
            g1HasStore: g1slice.indexOf('buildStorePayload(ctx, dim)') >= 0,
            g2HasStore: html.indexOf('buildStoreComparePayload(ctx, dim)') >= 0,
            openIsCockpit:
              openSlice.indexOf('selectedIso = selectedIso || window.__INSIGHT_SELECTED_ISO') < 0 &&
              openSlice.indexOf('selectedIso = resolveIso();') >= 0,
          };
        }"""
    )

    b = result.get("built")
    if not b:
        problems.append(f"{url}: builder null")
        return problems
    if b["bestYear"] != 2025:
        problems.append(f"{url}: bestYear={b['bestYear']} want 2025")
    if not (b["lyEnd"] > 0 and b["bestEnd"] >= b["lyEnd"]):
        problems.append(f"{url}: best/ly order fail {b}")
    # 前年が最高年なら bestEnd == lyEnd でよい
    if b["bestYear"] == 2025 and abs(b["bestEnd"] - b["lyEnd"]) > 0.01:
        problems.append(f"{url}: best should match 2025(=lastYear) totals")
    if abs(b["curEnd"] - result["g1End"]) > 0.01:
        problems.append(f"{url}: Graph2 current != Graph1 actual")

    st2 = result.get("st2")
    if not st2 or abs(st2["curEnd"] - b["curEnd"]) > 0.01:
        problems.append(f"{url}: chart state mismatch {st2}")
    if result.get("st2bToday") != 181:
        problems.append(f"{url}: date follow fail today={result.get('st2bToday')}")

    if not result.get("st1"):
        problems.append(f"{url}: Graph1 state missing on first render")
    if result.get("st1bToday") != 181:
        problems.append(f"{url}: Graph1 date follow regress today={result.get('st1bToday')}")

    if not result.get("g1HasStore"):
        problems.append(f"{url}: Graph1 store wiring missing")
    if not result.get("g2HasStore"):
        problems.append(f"{url}: Graph2 store wiring missing")
    if not result.get("openIsCockpit"):
        problems.append(f"{url}: Insight open() not back to Cockpit resolveIso")

    # demo amounts are huge; store seeded totals should be below ~1e6 for ytd mid-year
    if st2 and st2["curEnd"] > 2000000:
        problems.append(f"{url}: looks like demo still {st2}")

    print(f"  {url.split('/kpi-navigator/')[-1]} built={b} st2bToday={result.get('st2bToday')}")
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
    print("OK: Graph2 store + date follow / Graph1 intact / Insight open=Cockpit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

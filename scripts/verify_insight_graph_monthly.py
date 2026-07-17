#!/usr/bin/env python3
"""4/4 検証: Graph Monthly 累計折れ線が Insight 内日付 + Store 実データに追従."""

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


def build_seed() -> dict:
    import datetime

    daily_sales = {}
    business_days = {}
    d = datetime.date(YEAR, 6, 1)
    while d.month == 6:
        iso = d.isoformat()
        wk = d.weekday() >= 5
        business_days[iso] = not wk
        if not wk:
            daily_sales[iso] = 3000 + d.day * 100
        d += datetime.timedelta(days=1)
    # Cockpit 側は 7 月を選択している想定（Insight だけ 6 月）
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": YEAR,
            "legacyMigrated": True,
            "selectedDate": f"{YEAR}-07-15",
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
        "() => typeof window.__buildMonthlyCumulativeTrendPayload === 'function' && "
        "typeof document.getElementById('insight-graph-monthly-trend-period') !== 'undefined'",
        timeout=15000,
    )

    result = page.evaluate(
        """() => {
          // Cockpit/Store は 7 月、Insight は 6/30 を選択
          window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
          window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {};
          window.__ANNUAL_DATA.daily.selectedDate = '2026-07-15';
          window.__INSIGHT_SELECTED_ISO = '2026-06-30';
          document.dispatchEvent(new CustomEvent('insight:dateChanged', { detail: { iso: '2026-06-30' } }));

          const periodEl = document.getElementById('insight-graph-monthly-trend-period');
          const period = periodEl ? periodEl.textContent.trim() : '';
          const built = window.__buildMonthlyCumulativeTrendPayload(2026, 6, '2026-06-30');
          const demoBase = 400000;
          const usesReal = built && built.actual && built.actual[29] > 0 && built.actual[29] !== demoBase;
          const cockpitMonth = (() => {
            const iso = window.__ANNUAL_DATA.daily.selectedDate;
            const m = Number(String(iso).split('-')[1]);
            return m;
          })();
          return {
            period,
            cockpitMonth,
            builtTodayDay: built ? built.todayDay : null,
            builtActual30: built ? built.actual[29] : null,
            usesReal,
          };
        }"""
    )

    if result.get("period") != "2026.6":
        problems.append(f"{url}: period={result.get('period')!r} expected '2026.6'")
    if result.get("cockpitMonth") == 6:
        problems.append(f"{url}: store month should be 7 for isolation test")
    if result.get("builtTodayDay") != 30:
        problems.append(f"{url}: todayDay={result.get('builtTodayDay')!r} expected 30")
    if not result.get("usesReal"):
        problems.append(f"{url}: payload still looks like demo/empty")

    print(f"  {url.split('/kpi-navigator/')[-1]}")
    print(f"    period={result.get('period')} builtTodayDay={result.get('builtTodayDay')} actual[29]={result.get('builtActual30')}")
    return problems


def main() -> int:
    all_problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for page_path in PAGES:
            context = browser.new_context()
            page = context.new_page()
            url = page_path.as_uri()
            try:
                all_problems += verify_page(page, url)
            except Exception as e:  # noqa: BLE001
                all_problems.append(f"{url}: EXCEPTION {e}")
            finally:
                context.close()
        browser.close()

    print("\n=== RESULT ===")
    if all_problems:
        for pr in all_problems:
            print("NG:", pr)
        return 1
    print("OK: Graph Monthly は Insight 日付(6月) + Store 実データで描画（全4ファイル）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

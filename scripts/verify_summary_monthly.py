#!/usr/bin/env python3
"""2/4 検証: Insight Summary → Monthly の累計売上 + 進捗3行が compute 出力と一致."""

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
            daily_sales[iso] = 2000 + d.day * 10
        d += datetime.timedelta(days=1)
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": YEAR,
            "legacyMigrated": True,
            "selectedDate": f"{YEAR}-06-26",
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
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "typeof window.__computeTwMetricsForIso === 'function'",
        timeout=15000,
    )

    result = page.evaluate(
        """() => {
          const iso = '2026-06-26';
          const m = window.__computeTwMetricsForIso(iso);
          window.renderInsightTwDiffs(iso);
          const section = document.getElementById('insight-jump-summary-monthly');
          const kpiVal = section.querySelector('.insight-monthly-kpi__value');
          const progRows = section.querySelectorAll('.insight-monthly-progress__row');
          const prog = (i) => progRows[i] && progRows[i].querySelector('.insight-monthly-progress__value').textContent.trim();
          const analyzeSales = document.querySelector('.insight-monthly-sales-summary .insight-monthly-sales-summary__value');
          const fmtMoney = window.__twFmtMoney;
          const monthlyNeed = m && m.hasPlan && Number.isFinite(m.monthlyFullTarget) ? m.monthlyFullTarget - m.mtdA : null;
          const expected = m ? {
            cumulative: fmtMoney(m.mtdA),
            remainingBD: String(Math.round(m.monthRemainingBD)),
            need: monthlyNeed != null && Number.isFinite(monthlyNeed) ? fmtMoney(monthlyNeed) : '—',
            dailyNeed: m.hasPlan && m.monthlyDailyNeed != null ? fmtMoney(m.monthlyDailyNeed) : '—',
          } : null;
          return {
            metrics: m ? { mtdA: m.mtdA, monthRemainingBD: m.monthRemainingBD, monthlyFullTarget: m.monthlyFullTarget, monthlyDailyNeed: m.monthlyDailyNeed, hasPlan: m.hasPlan } : null,
            dom: { cumulative: kpiVal.textContent.trim(), remainingBD: prog(0), need: prog(1), dailyNeed: prog(2) },
            analyzeSales: analyzeSales ? analyzeSales.textContent.trim() : null,
            expected,
          };
        }"""
    )

    if not result.get("metrics"):
        problems.append(f"{url}: metrics null")
        return problems

    dom = result["dom"]
    exp = result["expected"]
    for k in ("cumulative", "remainingBD", "need", "dailyNeed"):
        if dom[k] != exp[k]:
            problems.append(f"{url}: {k} DOM={dom[k]!r} != expected={exp[k]!r}")

    if dom["cumulative"] != result.get("analyzeSales"):
        problems.append(
            f"{url}: Summary cumulative {dom['cumulative']!r} != Analyze Sales {result.get('analyzeSales')!r}"
        )

    print(f"  {url.split('/kpi-navigator/')[-1]}")
    print(f"    metrics : {result['metrics']}")
    print(f"    DOM     : {dom}")
    print(f"    Analyze : {result.get('analyzeSales')}")
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
    print("OK: Summary Monthly 累計売上 + 進捗3行は compute / Analyze と一致（全4ファイル）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

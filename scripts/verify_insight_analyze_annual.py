#!/usr/bin/env python3
"""優先度2 検証: Insight Analyze → Annual の残り KPI 行."""

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
    d = datetime.date(YEAR, 1, 1)
    end = datetime.date(YEAR, 6, 26)
    while d <= end:
        iso = d.isoformat()
        wk = d.weekday() >= 5
        business_days[iso] = not wk
        if not wk:
            daily_sales[iso] = 1500 + d.timetuple().tm_yday * 5
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
          const section = document.getElementById('insight-jump-analyze-annual');
          if (!section) return { error: 'missing #insight-jump-analyze-annual' };
          const salesRows = section.querySelectorAll('.insight-annual-sales-summary__row');
          const salesVal = (i) =>
            salesRows[i] && salesRows[i].querySelector('.insight-annual-sales-summary__value').textContent.trim();
          const progRows = section.querySelectorAll('.insight-annual-current-progress__row');
          const progVal = (i) =>
            progRows[i] && progRows[i].querySelector('.insight-annual-current-progress__value').textContent.trim();
          const fmtMoney = window.__twFmtMoney;
          const fmtDiff = window.__twFmtDiff;
          const fmtAch = window.__twFmtAchPct;
          const fmtGapPct = (a, t) => {
            if (!Number.isFinite(a) || !Number.isFinite(t) || t <= 0) return '—';
            return Math.round(((a - t) / t) * 100) + '%';
          };
          const expected = m ? {
            remainingBD: String(Math.round(m.yearRemainingBD)),
            dailyNeed: m.hasPlan && m.annualDailyNeed != null ? fmtMoney(m.annualDailyNeed) : '—',
            ytdT: m.hasPlan ? fmtMoney(m.ytdT) : '—',
            gap: m.hasPlan ? fmtDiff(m.ytdA, m.ytdT) : '—',
            ach: m.hasPlan ? fmtAch(m.ytdA, m.ytdT) : '—',
            gapPct: m.hasPlan ? fmtGapPct(m.ytdA, m.ytdT) : '—',
          } : null;
          return {
            metrics: m ? {
              ytdA: m.ytdA, ytdT: m.ytdT, yearRemainingBD: m.yearRemainingBD,
              annualDailyNeed: m.annualDailyNeed, hasPlan: m.hasPlan,
            } : null,
            dom: {
              remainingBD: salesVal(4), dailyNeed: salesVal(5),
              ytdT: progVal(0), gap: progVal(1), ach: progVal(2), gapPct: progVal(3),
            },
            expected,
            placeholder: salesVal(5) === '$123,456' || progVal(0) === '$123,456',
          };
        }"""
    )

    if result.get("error"):
        problems.append(f"{url}: {result['error']}")
        return problems

    if not result.get("metrics"):
        problems.append(f"{url}: metrics null")
        return problems

    if result.get("placeholder"):
        problems.append(f"{url}: placeholder values still present")

    dom = result["dom"]
    exp = result["expected"]
    for k in dom:
        if dom[k] != exp[k]:
            problems.append(f"{url}: {k} DOM={dom[k]!r} != expected={exp[k]!r}")

    print(f"  {url.split('/kpi-navigator/')[-1]}")
    print(f"    metrics : {result['metrics']}")
    print(f"    dom     : {dom}")
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
    print("OK: Analyze Annual 残り KPI は compute と一致（全4ファイル）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

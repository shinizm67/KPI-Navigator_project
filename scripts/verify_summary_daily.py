#!/usr/bin/env python3
"""1/4 検証: Insight Summary → Daily の Sales / Target / Difference が
Cockpit と同一ソース (__computeTwMetricsForIso / __ANNUAL_DATA.daily) で
駆動されていることを、seed データを注入したヘッドレス Chromium で確認する。

HEAD 時点で renderInsightTwDiffs が .insight-daily-kpi(Summary) を patch 済み
であることの回帰確認であり、コードは一切変更しない。
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


def build_seed() -> dict:
    daily_sales = {}
    business_days = {}
    # 6月の平日にダミー実績を入れる
    import datetime

    d = datetime.date(YEAR, 6, 1)
    while d.month == 6:
        iso = d.isoformat()
        wk = d.weekday() >= 5  # 5,6 = Sat,Sun
        business_days[iso] = not wk
        if not wk:
            daily_sales[iso] = 2000 + d.day * 10
        d += datetime.timedelta(days=1)
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": YEAR,
            "legacyMigrated": True,
            "selectedDate": f"{YEAR}-06-30",
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
        "() => typeof window.__computeTwMetricsForIso === 'function' && typeof window.renderInsightTwDiffs === 'function'",
        timeout=15000,
    )

    result = page.evaluate(
        """() => {
          const iso = '2026-06-27'; // 平日 (土日以外) を選ぶ
          // 6/27 は土曜なので営業日にした 6/26(金) を使う
          const pick = '2026-06-26';
          const m = window.__computeTwMetricsForIso(pick);
          window.renderInsightTwDiffs(pick);
          const root = document.getElementById('insight-overlay');
          const block = root.querySelector('.insight-daily-kpi');
          const rows = block.querySelectorAll('.insight-daily-kpi__row');
          const val = (i) => rows[i] && rows[i].querySelector('.insight-daily-kpi__value').textContent.trim();
          const fmtMoney = window.__twFmtMoney;
          const fmtDiff = window.__twFmtDiff;
          const hasPlan = m && m.isBusinessToday && m.dailyTarget != null;
          return {
            iso: pick,
            metrics: m ? { dailySales: m.dailySales, dailyTarget: m.dailyTarget, isBusinessToday: m.isBusinessToday } : null,
            dom: { sales: val(0), target: val(1), diff: val(2) },
            expected: m ? {
              sales: hasPlan ? fmtMoney(m.dailySales) : '—',
              target: hasPlan ? fmtMoney(m.dailyTarget) : '—',
              diff: hasPlan ? fmtDiff(m.dailySales, m.dailyTarget) : '—',
            } : null,
          };
        }"""
    )

    if not result.get("metrics"):
        problems.append(f"{url}: metrics null")
        return problems
    dom = result["dom"]
    exp = result["expected"]
    for k in ("sales", "target", "diff"):
        if dom[k] != exp[k]:
            problems.append(
                f"{url}: {k} DOM={dom[k]!r} != expected(compute)={exp[k]!r}"
            )
    print(f"  {url.split('/kpi-navigator/')[-1]}")
    print(f"    metrics: {result['metrics']}")
    print(f"    DOM     : {dom}")
    print(f"    expected: {exp}")
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
    print("OK: Summary Daily の Sales/Target/Difference は compute 出力と一致（全4ファイル）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

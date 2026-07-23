#!/usr/bin/env python3
"""検証: Insight → Graph → Daily が Store 実データに追従."""

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

    def put(y, m, d, amt, biz=True):
        iso = datetime.date(y, m, d).isoformat()
        business_days[iso] = biz
        if biz:
            daily_sales[iso] = amt

    # 2026-07-14 = Tue. same weekday: -364 → 2025-07-15, -728 → 2024-07-16, -1092 → 2023-07-18
    put(2026, 7, 14, 4000)
    put(2025, 7, 15, 2500)
    put(2024, 7, 16, 1800)
    put(2023, 7, 18, 1200)
    # Neighbors as non-biz weekends around them aren’t needed; mark some OFF day
    # Ensure business maps exist for nearby days used by plan calc
    for y in (2023, 2024, 2025, 2026):
        d = datetime.date(y, 7, 1)
        while d.month == 7:
            iso = d.isoformat()
            if iso not in business_days:
                business_days[iso] = d.weekday() < 5
            d += datetime.timedelta(days=1)

    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {"dailySales": daily_sales, "businessDays": business_days},
        "years": {
            str(y): {
                "year": y,
                "status": "open" if y == 2026 else "closed",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
            }
            for y in (2023, 2024, 2025, 2026)
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
        "() => typeof window.__computeTwMetricsForIso === 'function' && "
        "typeof window.__sameWeekdayIso === 'function' && "
        "typeof window.renderInsightTwDiffs === 'function' && "
        "window.__insightGraphDailyWidgets && "
        "window.__insightGraphDailyWidgets.targetActual",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const m = window.__computeTwMetricsForIso(iso);
          const paneSummary = document.getElementById('insight-pane-summary');
          const paneAnalyze = document.getElementById('insight-pane-analyze');
          const paneGraph = document.getElementById('insight-pane-graph');
          if (paneSummary) paneSummary.hidden = true;
          if (paneAnalyze) paneAnalyze.hidden = true;
          if (paneGraph) paneGraph.hidden = false;
          window.renderInsightTwDiffs(iso);
          const section = document.getElementById('insight-jump-graph-daily');
          const row1 = section.querySelector('.insight-graph-daily__row--target-actual');
          const row2 = section.querySelector('.insight-graph-daily__row--last-year-weekday');
          const caps1 = [...row1.querySelectorAll('.insight-graph-daily__marker-cap-value')].map(
            (el) => el.textContent.trim()
          );
          const caps2 = [...row2.querySelectorAll('.insight-graph-daily__marker-cap-value')].map(
            (el) => el.textContent.trim()
          );
          const pct1 = document.getElementById('insight-graph-daily-target-actual-pct').textContent.trim();
          const pct2 = document
            .getElementById('insight-graph-daily-last-year-weekday-pct')
            .textContent.trim();
          const hist = [...document.querySelectorAll(
            '#insight-graph-daily-historical .insight-graph-daily-historical__item'
          )].map((item) => ({
            year: item.querySelector('.insight-graph-daily-historical__year').textContent.trim(),
            value: item.querySelector('.insight-graph-daily-historical__value').textContent.trim(),
            off: item.classList.contains('insight-graph-daily-historical__item--off'),
            amount: item.getAttribute('data-amount'),
          }));
          const lyIso = window.__sameWeekdayIso(iso, 1);
          const lySales = window.__readTwDaySales(lyIso);
          const fmt = window.__twFmtMoney;
          const expectedPct1 =
            m && m.dailyTarget > 0
              ? (Math.round((m.dailySales / m.dailyTarget) * 1000) / 10).toLocaleString('en-US', {
                  maximumFractionDigits: 1,
                }) + '%'
              : '—';
          const expectedPct2 =
            lySales > 0
              ? (Math.round((m.dailySales / lySales) * 1000) / 10).toLocaleString('en-US', {
                  maximumFractionDigits: 1,
                }) + '%'
              : '—';
          return {
            dailySales: m && m.dailySales,
            dailyTarget: m && m.dailyTarget,
            isBusinessToday: m && m.isBusinessToday,
            lyIso,
            lySales,
            caps1,
            caps2,
            pct1,
            pct2,
            expectedCaps1: [fmt(m.dailySales), fmt(m.dailyTarget)],
            expectedCaps2: [fmt(m.dailySales), fmt(lySales)],
            expectedPct1,
            expectedPct2,
            hist,
            stillPlaceholder:
              caps1.concat(caps2).some(
                (v) =>
                  v === '$100,456' ||
                  v === '$123,456' ||
                  v === '$123,789' ||
                  v === '¥100,456' ||
                  v === '¥123,456' ||
                  v === '¥123,789'
              ) ||
              pct1 === '89%' ||
              pct2 === '118%',
          };
        }"""
    )
    if result.get("stillPlaceholder"):
        problems.append(f"{url}: still placeholder {result}")
    if not result.get("isBusinessToday"):
        problems.append(f"{url}: expected business day")
    for i, (e, g) in enumerate(
        zip(result.get("expectedCaps1") or [], result.get("caps1") or [])
    ):
        if e != g:
            problems.append(f"{url}: row1 cap{i} got={g!r} expected={e!r}")
    for i, (e, g) in enumerate(
        zip(result.get("expectedCaps2") or [], result.get("caps2") or [])
    ):
        if e != g:
            problems.append(f"{url}: row2 cap{i} got={g!r} expected={e!r}")
    if result.get("pct1") != result.get("expectedPct1"):
        problems.append(
            f"{url}: pct1 got={result.get('pct1')!r} expected={result.get('expectedPct1')!r}"
        )
    if result.get("pct2") != result.get("expectedPct2"):
        problems.append(
            f"{url}: pct2 got={result.get('pct2')!r} expected={result.get('expectedPct2')!r}"
        )
    hist = result.get("hist") or []
    if len(hist) != 4:
        problems.append(f"{url}: hist count {len(hist)}")
    else:
        # years should be 2026,2025,2024,2023 for iso
        years = [h["year"] for h in hist]
        if years != ["2026", "2025", "2024", "2023"]:
            problems.append(f"{url}: hist years {years}")
        # amounts for biz days
        for h, exp_amt in zip(hist, ["4000", "2500", "1800", "1200"]):
            if h.get("off"):
                problems.append(f"{url}: hist {h['year']} unexpectedly OFF")
            elif h.get("amount") != exp_amt:
                problems.append(
                    f"{url}: hist {h['year']} amount={h.get('amount')!r} expected={exp_amt!r}"
                )
    rel = url.split("/kpi-navigator/")[-1]
    print(
        f"  {rel} sales={result.get('dailySales')} tgt={result.get('dailyTarget')} "
        f"ly={result.get('lyIso')}:{result.get('lySales')}"
    )
    print(f"    caps1={result.get('caps1')} pct1={result.get('pct1')}")
    print(f"    caps2={result.get('caps2')} pct2={result.get('pct2')}")
    print(f"    hist={hist}")
    return problems


def main() -> int:
    import os

    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
            url = path.as_uri()
            problems.extend(verify_page(page, url))
            page.close()
        browser.close()
    if problems:
        print("FAIL:")
        for pr in problems:
            print(" ", pr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""検証(Phase 1): kpiYearStore の dailyIncome 純追加 — 既存(dailySales/dailyExpenses)無影響.

- writeDailyIncome / readDailyIncome の往復・0削除
- localStorage の years.{Y}.dailyIncome[streamId][iso] 反映
- bulkPersistMepYear の dailyIncome 保存 & loadMepYearPayload での復帰
- income 書込が timeline.dailySales(=総売上) を一切変えない
- dailyExpenses と併存(相互干渉なし)
- 過去年ロック時は書込拒否(canEditIso)
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
# KpiYearStore を内蔵するページ(MEP)で API を検証する。
PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)

YEAR = 2026
STORE_KEY = "kpiNavigator.kpiYearStore"


def store_seed() -> dict:
    return {
        "meta": {"schemaVersion": 4, "operatingYear": YEAR, "legacyMigrated": True},
        "timeline": {
            "dailySales": {f"{YEAR}-07-01": 100000, f"{YEAR}-07-02": 150000},
            "businessDays": {},
        },
        "years": {
            str(YEAR): {
                "year": YEAR,
                "status": "open",
                "plan": {"targetSales": 600000},
                "dailyExpenses": {},
                "dailyIncome": {},
                "dailyMeta": {"memos": {}, "flags": {}, "weather": {}},
            },
            # 過去年ロック(書込拒否テスト用)
            "2024": {
                "year": 2024,
                "status": "locked",
                "plan": {},
                "dailyExpenses": {},
                "dailyIncome": {},
                "dailyMeta": {"memos": {}, "flags": {}, "weather": {}},
            },
        },
    }


def seed(page) -> None:
    page.evaluate(
        """({ store, key }) => {
          localStorage.clear();
          localStorage.setItem(key, JSON.stringify(store));
        }""",
        {"store": store_seed(), "key": STORE_KEY},
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    url = f"{url}{'&' if '?' in url else '?'}year={YEAR}"

    page.goto(url, wait_until="load")
    seed(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => window.KpiYearStore && typeof KpiYearStore.writeDailyIncome === 'function'",
        timeout=15000,
    )

    result = page.evaluate(
        """() => {
          const KYS = window.KpiYearStore;
          const out = { problems: [], events: 0 };
          document.addEventListener('kpi:mepDataChanged', () => { out.events++; });

          // A) write / read round trip
          KYS.writeDailyIncome('sales_a', '2026-07-04', 12000, { source: 'test' });
          KYS.writeDailyIncome('sales_a', '2026-07-15', 8000, { source: 'test' });
          if (KYS.readDailyIncome('sales_a', '2026-07-04') !== 12000)
            out.problems.push('readDailyIncome 07-04 != 12000');
          if (KYS.readDailyIncome('sales_a', '2026-07-15') !== 8000)
            out.problems.push('readDailyIncome 07-15 != 8000');
          if (KYS.readDailyIncome('sales_a', '2026-07-09') !== null)
            out.problems.push('absent iso should be null');
          if (KYS.readDailyIncome('sales_b', '2026-07-04') !== null)
            out.problems.push('absent stream should be null');

          // A2) delete-on-zero
          KYS.writeDailyIncome('sales_a', '2026-07-04', 0, { source: 'test' });
          if (KYS.readDailyIncome('sales_a', '2026-07-04') !== null)
            out.problems.push('zero write should delete entry');

          // B) localStorage path
          const raw = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore'));
          const di = raw.years['2026'].dailyIncome || {};
          if (!di.sales_a || di.sales_a['2026-07-15'] !== 8000)
            out.problems.push('localStorage dailyIncome.sales_a 07-15 != 8000');
          if (di.sales_a && '2026-07-04' in di.sales_a)
            out.problems.push('localStorage should not keep deleted 07-04');

          // C) bulkPersistMepYear stores income + expenses independently
          KYS.bulkPersistMepYear(
            2026,
            {
              dailyExpenses: { exp_food_cost: { '2026-07-02': 500 } },
              dailyIncome: { sales_b: { '2026-07-03': 7000 } },
            },
            { source: 'test' }
          );
          const payload = KYS.loadMepYearPayload(2026);
          if (!payload.dailyIncome || !payload.dailyIncome.sales_b ||
              payload.dailyIncome.sales_b['2026-07-03'] !== 7000)
            out.problems.push('bulk dailyIncome.sales_b 07-03 != 7000');
          if (!payload.dailyExpenses || !payload.dailyExpenses.exp_food_cost ||
              payload.dailyExpenses.exp_food_cost['2026-07-02'] !== 500)
            out.problems.push('bulk dailyExpenses.exp_food_cost 07-02 != 500');

          // D) timeline.dailySales(=総売上) は income 書込で不変
          const raw2 = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore'));
          const ds = raw2.timeline.dailySales || {};
          if (ds['2026-07-01'] !== 100000 || ds['2026-07-02'] !== 150000)
            out.problems.push('timeline.dailySales must be unchanged by income writes');
          if ('2026-07-03' in ds || '2026-07-15' in ds)
            out.problems.push('income writes must not leak into timeline.dailySales');

          // E) 過去年ロックは拒否
          const okLocked = KYS.writeDailyIncome('sales_a', '2024-07-01', 5000, { source: 'test' });
          if (okLocked !== false)
            out.problems.push('locked past year write should return false');
          if (KYS.readDailyIncome('sales_a', '2024-07-01') !== null)
            out.problems.push('locked past year must not persist income');

          if (out.events < 1)
            out.problems.push('kpi:mepDataChanged should fire on write');

          return out;
        }"""
    )
    problems.extend(result.get("problems", []))
    return problems


def main() -> int:
    if not EXE.exists():
        print(f"Chrome missing: {EXE}", file=sys.stderr)
        return 2
    fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
            try:
                problems = verify_page(page, path.as_uri())
            except Exception as e:  # noqa: BLE001
                problems = [f"exception: {e}"]
            page.close()
            if problems:
                fail += 1
                print(f"FAIL {path}: {problems}")
            else:
                print(f"OK   {path}")
        browser.close()
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

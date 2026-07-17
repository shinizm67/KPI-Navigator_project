#!/usr/bin/env python3
"""検証: PL Phase C — 月次(÷営業日) → MEP dailyExpenses 書込（monthly のみ・再配分・daily不変）."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)

YEAR = 2026
MONTH0 = 6  # July
FIXED_LINE = "exp_rent"
DAILY_LINE = "exp_food_cost"
AMOUNT = 220007  # not divisible by 22 → remainder on last biz day
OFF_DAYS = [5, 6, 12, 13, 19, 20, 26, 27, 31]  # 31-9 = 22 biz days in July


def store_seed() -> dict:
    biz = {f"{YEAR}-07-{d:02d}": False for d in OFF_DAYS}
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": YEAR,
            "legacyMigrated": True,
            "selectedDate": f"{YEAR}-07-14",
        },
        "timeline": {"dailySales": {}, "businessDays": biz},
        "years": {
            str(YEAR): {
                "year": YEAR,
                "status": "open",
                "plan": {"targetSales": 600000},
                # pre-existing MEP daily entry for a DAILY line — must survive
                "dailyExpenses": {
                    DAILY_LINE: {f"{YEAR}-07-01": 1000, f"{YEAR}-07-10": 2000},
                    # stale monthly allocation from a previous save — must be replaced
                    FIXED_LINE: {f"{YEAR}-07-03": 99999, f"{YEAR}-08-01": 5555},
                },
                "dailyMeta": {"memos": {}, "flags": {}, "weather": {}},
            }
        },
    }


def biz_isos() -> list[str]:
    off = set(OFF_DAYS)
    return [f"{YEAR}-07-{d:02d}" for d in range(1, 32) if d not in off]


def seed(page) -> None:
    biz = {f"{YEAR}-07-{d:02d}": False for d in OFF_DAYS}
    page.evaluate(
        """({ store, key, plKey, dailyKey, biz, line, month0, amount }) => {
          localStorage.clear();
          localStorage.setItem(key, JSON.stringify(store));
          localStorage.setItem(
            dailyKey,
            JSON.stringify({ businessDayByDate: biz, targetSalesByDate: {} })
          );
          const map = {};
          map[line + ':' + month0] = amount;
          localStorage.setItem(plKey, JSON.stringify(map));
        }""",
        {
            "store": store_seed(),
            "key": "kpiNavigator.kpiYearStore",
            "plKey": f"kpi-pl-expenses-v1:{YEAR}",
            "dailyKey": "kpiNavigator.annualDailyShared",
            "biz": biz,
            "line": FIXED_LINE,
            "month0": MONTH0,
            "amount": AMOUNT,
        },
    )


def read_line(page, line_id: str) -> dict:
    return page.evaluate(
        """(lineId) => {
          const raw = localStorage.getItem('kpiNavigator.kpiYearStore');
          const store = raw ? JSON.parse(raw) : {};
          const rec = (store.years || {})['2026'] || {};
          const de = rec.dailyExpenses || {};
          return de[lineId] || null;
        }""",
        line_id,
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    if "?" in url:
        url = f"{url}&year={YEAR}"
    else:
        url = f"{url}?year={YEAR}"

    page.goto(url, wait_until="load")
    seed(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => typeof window.__plWriteMonthlyExpenseAllocationToMep === 'function'",
        timeout=15000,
    )

    result = page.evaluate(
        "() => window.__plWriteMonthlyExpenseAllocationToMep({ year: 2026 })"
    )
    if not result.get("ok"):
        problems.append(f"write not ok: {result}")
    if result.get("wrote") is not True:
        problems.append(f"expected wrote true: {result}")
    if FIXED_LINE not in (result.get("monthlyLineIds") or []):
        problems.append(f"exp_rent should be monthly line: {result.get('monthlyLineIds')}")
    if DAILY_LINE in (result.get("monthlyLineIds") or []):
        problems.append("exp_food_cost must not be monthly line")

    fixed = read_line(page, FIXED_LINE) or {}
    expected = biz_isos()
    got_july = {k: v for k, v in fixed.items() if k.startswith(f"{YEAR}-07-")}
    if sorted(got_july.keys()) != sorted(expected):
        problems.append(
            f"July isos mismatch: have {len(got_july)} want {len(expected)}"
        )
    total = sum(got_july.values())
    if total != AMOUNT:
        problems.append(f"July sum {total} != {AMOUNT}")
    # stale July-03 (99999) must be gone / replaced
    if got_july.get(f"{YEAR}-07-03") == 99999:
        problems.append("stale July-03 not replaced")
    # last biz day gets remainder
    base = AMOUNT // 22
    rem = AMOUNT % 22
    if got_july.get(expected[-1]) != base + rem:
        problems.append(f"last biz day {expected[-1]} = {got_july.get(expected[-1])}")
    # off day must have no entry
    if f"{YEAR}-07-05" in got_july:
        problems.append("off day 07-05 should not be allocated")

    # stale August entry for monthly line: full-year run clears it (Aug amount 0)
    aug = {k: v for k, v in fixed.items() if k.startswith(f"{YEAR}-08-")}
    if aug:
        problems.append(f"August stale entry not cleared: {aug}")

    # DAILY line must be untouched
    daily = read_line(page, DAILY_LINE) or {}
    if daily.get(f"{YEAR}-07-01") != 1000 or daily.get(f"{YEAR}-07-10") != 2000:
        problems.append(f"daily line mutated: {daily}")

    # timeline / sales untouched
    timeline_ok = page.evaluate(
        """() => {
          const store = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore'));
          const t = store.timeline || {};
          const ds = t.dailySales || {};
          return Object.keys(ds).length === 0;
        }"""
    )
    if not timeline_ok:
        problems.append("timeline.dailySales mutated")

    # Insight read reflects the allocation (fixed bucket total for full July)
    insight = page.evaluate(
        """() => {
          const raw = localStorage.getItem('kpiNavigator.kpiYearStore');
          const store = JSON.parse(raw);
          const de = (store.years['2026'] || {}).dailyExpenses || {};
          const row = de['exp_rent'] || {};
          let sum = 0;
          Object.keys(row).forEach((iso) => {
            if (iso.indexOf('2026-07-') === 0) sum += Number(row[iso]) || 0;
          });
          return sum;
        }"""
    )
    if insight != AMOUNT:
        problems.append(f"insight-visible July fixed sum {insight} != {AMOUNT}")

    # --- re-allocation: change amount to 0 and re-run → July cleared ---
    page.evaluate(
        """({ plKey, line, month0 }) => {
          const map = JSON.parse(localStorage.getItem(plKey) || '{}');
          map[line + ':' + month0] = 0;
          localStorage.setItem(plKey, JSON.stringify(map));
        }""",
        {"plKey": f"kpi-pl-expenses-v1:{YEAR}", "line": FIXED_LINE, "month0": MONTH0},
    )
    page.evaluate("() => window.__plWriteMonthlyExpenseAllocationToMep({ year: 2026 })")
    after = read_line(page, FIXED_LINE) or {}
    july_after = {k: v for k, v in after.items() if k.startswith(f"{YEAR}-07-")}
    if july_after:
        problems.append(f"amount 0 should clear July: {july_after}")

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

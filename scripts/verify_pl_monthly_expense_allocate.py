#!/usr/bin/env python3
"""検証: PL Phase B — 月次÷営業日 按分プレビュー（MEP 未書込）."""

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
LINE = "exp_rent"
AMOUNT = 220007  # not divisible evenly → remainder on last day


def seed_storage(page) -> None:
    # 22 biz days in July by turning off 9 calendar days (31-9=22)
    off_days = [5, 6, 12, 13, 19, 20, 26, 27, 31]
    bmap = {f"{YEAR}-07-{d:02d}": False for d in off_days}
    page.evaluate(
        """({ year, line, month0, amount, bmap }) => {
          localStorage.clear();
          localStorage.setItem(
            'kpiNavigator.annualDailyShared',
            JSON.stringify({ businessDayByDate: bmap, targetSalesByDate: {} })
          );
          const key = 'kpi-pl-expenses-v1:' + year;
          const map = {};
          map[line + ':' + month0] = amount;
          localStorage.setItem(key, JSON.stringify(map));
        }""",
        {
            "year": YEAR,
            "line": LINE,
            "month0": MONTH0,
            "amount": AMOUNT,
            "bmap": bmap,
        },
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    if "?" in url:
        url = f"{url}&year={YEAR}"
    else:
        url = f"{url}?year={YEAR}"

    page.goto(url, wait_until="load")
    seed_storage(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => typeof window.__plPreviewMonthlyExpenseAllocation === 'function'",
        timeout=15000,
    )

    result = page.evaluate(
        """({ year, month0, line }) => {
          const out = window.__plPreviewMonthlyExpenseAllocation({
            year,
            month0,
            lineId: line,
          });
          const mepBefore = localStorage.getItem('kpiNavigator.kpiYearStore');
          return { out, mepBefore, mepAfter: localStorage.getItem('kpiNavigator.kpiYearStore') };
        }""",
        {"year": YEAR, "month0": MONTH0, "line": LINE},
    )

    out = result["out"]
    if out.get("wroteToMep") is not False:
        problems.append(f"wroteToMep flag wrong: {out.get('wroteToMep')}")
    if result["mepBefore"] != result["mepAfter"]:
        problems.append("kpiYearStore mutated (must not write MEP)")

    if LINE not in (out.get("skippedDailyLineIds") or []) and "exp_food_cost" not in (
        out.get("skippedDailyLineIds") or []
    ):
        # food should be in skipped daily after catalog bootstrap
        pass

    months = out.get("months") or []
    if len(months) != 1:
        problems.append(f"expected 1 month block: {len(months)}")
        return problems

    block = months[0]
    if block.get("bizDayCount") != 22:
        problems.append(f"bizDayCount expected 22: {block.get('bizDayCount')}")

    line = (block.get("lines") or {}).get(LINE) or {}
    if line.get("monthlyAmount") != AMOUNT:
        problems.append(f"monthlyAmount: {line.get('monthlyAmount')}")

    by_date = line.get("byDate") or {}
    if len(by_date) != 22:
        problems.append(f"byDate size: {len(by_date)}")

    total = sum(by_date.values())
    if total != AMOUNT:
        problems.append(f"sum mismatch: {total} != {AMOUNT}")

    base = line.get("perDayBase")
    rem = line.get("remainder")
    if base != AMOUNT // 22:
        problems.append(f"perDayBase: {base}")
    if rem != AMOUNT % 22:
        problems.append(f"remainder: {rem}")

    # last biz day gets base+remainder
    last_iso = (block.get("bizDays") or [])[-1] if block.get("bizDays") else None
    if last_iso and by_date.get(last_iso) != base + rem:
        problems.append(f"last day amount: {by_date.get(last_iso)} vs {base + rem}")

    # daily line must not appear in lines for this month preview when filtering lineId
    # check full preview includes food in skippedDaily
    full = page.evaluate(
        """(year) => window.__plPreviewMonthlyExpenseAllocation({ year, month0: 6 })""",
        YEAR,
    )
    skipped = full.get("skippedDailyLineIds") or []
    if "exp_food_cost" not in skipped:
        problems.append(f"exp_food_cost should be skipped daily: {skipped[:8]}")
    if LINE in skipped:
        problems.append("exp_rent must not be skipped as daily")

    # unit smoke on allocate helper
    unit = page.evaluate(
        """() => {
          const r = window.__plAllocateAmountAcrossBizDays(10, ['a','b','c']);
          return r;
        }"""
    )
    if unit.get("byDate") != {"a": 3, "b": 3, "c": 4}:
        problems.append(f"unit allocate wrong: {unit}")

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

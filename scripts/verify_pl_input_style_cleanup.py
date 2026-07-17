#!/usr/bin/env python3
"""検証: 入力元切替時に使わなくなる側の旧データを掃除する.

- daily → monthly: years.{Y}.dailyExpenses[lineId] を削除
- monthly → daily: kpi-pl-expenses-v1:{year} の lineId:* を削除
- 同スタイル再設定ではデータを消さない
"""

from __future__ import annotations

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
STORE_KEY = "kpiNavigator.kpiYearStore"
EXP_KEY = f"kpi-pl-expenses-v1:{YEAR}"
CATALOG_KEY = "kpiNavigator.plLineCatalog"
LINE = "exp_food_cost"  # default daily, switchable


def seed(page) -> None:
    page.evaluate(
        """({ storeKey, expKey, catalogKey, year, lineId }) => {
          localStorage.clear();
          const store = {
            meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
            timeline: { dailySales: {}, businessDays: {} },
            years: {
              [String(year)]: {
                year,
                status: 'open',
                plan: {},
                dailyExpenses: {
                  [lineId]: {
                    [year + '-07-01']: 3000,
                    [year + '-07-02']: 2000,
                  },
                },
                dailyIncome: {},
                dailyMeta: { memos: {}, flags: {}, weather: {} },
              },
            },
          };
          localStorage.setItem(storeKey, JSON.stringify(store));
          localStorage.setItem(expKey, JSON.stringify({ [lineId + ':6']: 9000 }));
          // leave catalog empty → page seeds defaults (food = daily)
          void catalogKey;
        }""",
        {
            "storeKey": STORE_KEY,
            "expKey": EXP_KEY,
            "catalogKey": CATALOG_KEY,
            "year": YEAR,
            "lineId": LINE,
        },
    )


def daily_expense_count(page) -> int:
    return page.evaluate(
        """({ key, year, lineId }) => {
          const store = JSON.parse(localStorage.getItem(key) || '{}');
          const rec = store.years && (store.years[year] || store.years[String(year)]);
          const map = rec && rec.dailyExpenses && rec.dailyExpenses[lineId];
          return map && typeof map === 'object' ? Object.keys(map).length : 0;
        }""",
        {"key": STORE_KEY, "year": YEAR, "lineId": LINE},
    )


def pl_monthly_amount(page) -> int | None:
    return page.evaluate(
        """({ key, lineId }) => {
          const map = JSON.parse(localStorage.getItem(key) || '{}');
          const v = map[lineId + ':6'];
          return v == null ? null : Number(v);
        }""",
        {"key": EXP_KEY, "lineId": LINE},
    )


def line_style(page) -> str | None:
    return page.evaluate(
        """({ key, lineId }) => {
          const raw = localStorage.getItem(key);
          if (!raw) return null;
          const lines = (JSON.parse(raw).lines || []);
          const line = lines.find((l) => l.lineId === lineId);
          return line ? (line.resolvedInputStyle || line.inputStyle) : null;
        }""",
        {"key": CATALOG_KEY, "lineId": LINE},
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.goto(f"{url}?year={YEAR}", wait_until="load")
    seed(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => typeof window.__plSetLineInputStyle === 'function'",
        timeout=15000,
    )

    if daily_expense_count(page) != 2:
        problems.append(f"seed dailyExpenses count {daily_expense_count(page)} want 2")
    if pl_monthly_amount(page) != 9000:
        problems.append(f"seed PL monthly {pl_monthly_amount(page)} want 9000")

    # same style → keep both
    page.evaluate(
        """({ lineId }) => window.__plSetLineInputStyle(lineId, 'daily')""",
        {"lineId": LINE},
    )
    page.wait_for_timeout(50)
    if daily_expense_count(page) != 2:
        problems.append("same-style reapply cleared dailyExpenses")
    if pl_monthly_amount(page) != 9000:
        problems.append("same-style reapply cleared PL monthly")

    # daily → monthly clears dailyExpenses, keeps PL monthly map
    page.evaluate(
        """({ lineId }) => window.__plSetLineInputStyle(lineId, 'monthly')""",
        {"lineId": LINE},
    )
    page.wait_for_timeout(50)
    if line_style(page) != "monthly":
        problems.append(f"style after daily→monthly {line_style(page)!r}")
    if daily_expense_count(page) != 0:
        problems.append(
            f"daily→monthly should clear dailyExpenses, got {daily_expense_count(page)}"
        )
    if pl_monthly_amount(page) != 9000:
        problems.append("daily→monthly should keep PL monthly amounts")

    # restore dailyExpenses and switch monthly → daily
    page.evaluate(
        """({ key, year, lineId }) => {
          const store = JSON.parse(localStorage.getItem(key));
          store.years[String(year)].dailyExpenses[lineId] = {
            [year + '-07-10']: 1111,
          };
          localStorage.setItem(key, JSON.stringify(store));
        }""",
        {"key": STORE_KEY, "year": YEAR, "lineId": LINE},
    )
    page.evaluate(
        """({ lineId }) => window.__plSetLineInputStyle(lineId, 'daily')""",
        {"lineId": LINE},
    )
    page.wait_for_timeout(50)
    if line_style(page) != "daily":
        problems.append(f"style after monthly→daily {line_style(page)!r}")
    if pl_monthly_amount(page) is not None:
        problems.append(
            f"monthly→daily should clear PL monthly, got {pl_monthly_amount(page)}"
        )
    if daily_expense_count(page) != 1:
        problems.append(
            f"monthly→daily should keep dailyExpenses, got {daily_expense_count(page)}"
        )

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

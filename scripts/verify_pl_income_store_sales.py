#!/usr/bin/env python3
"""検証: PL 収入ブロック(読取専用) — 店舗売上=日次売上の月合計、A/B=dailyIncome集計、合計=和."""

from __future__ import annotations

import re
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

# 新モデル: timeline.dailySales = 総売上(店舗 + A + B)。PL は
#   合計      = dailySales(月合計)
#   Sales A/B = dailyIncome[streamId](月合計)
#   店舗売上   = 合計 − (A + B)
# July (month0=6) 総売上 = 100000 + 150000 + 50000 = 300000 (1234 placeholder 除外)
DAILY_SALES = {
    f"{YEAR}-07-01": 100000,
    f"{YEAR}-07-02": 150000,
    f"{YEAR}-07-05": 1234,       # legacy placeholder → excluded
    f"{YEAR}-07-10": 50000,
    f"{YEAR}-08-03": 200000,     # August (month0=7)
}
JULY_TOTAL = 300000
AUG_TOTAL = 200000
# Sales A daily income (July) = 12000 + 8000 = 20000
DAILY_INCOME_A = {f"{YEAR}-07-04": 12000, f"{YEAR}-07-15": 8000}
JULY_A = 20000
JULY_STORE = JULY_TOTAL - JULY_A  # 280000
AUG_STORE = AUG_TOTAL            # A/B 無 → 店舗 = 合計


def store_seed() -> dict:
    return {
        "meta": {"schemaVersion": 4, "operatingYear": YEAR, "legacyMigrated": True},
        "timeline": {"dailySales": dict(DAILY_SALES), "businessDays": {}},
        "years": {
            str(YEAR): {
                "year": YEAR,
                "status": "open",
                "plan": {"targetSales": 600000},
                "dailyExpenses": {},
                "dailyIncome": {"sales_a": dict(DAILY_INCOME_A)},
                "dailyMeta": {"memos": {}, "flags": {}, "weather": {}},
            }
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


def cell_int(page, rid: str, month0: int):
    txt = page.evaluate(
        """({ rid, m }) => {
          const cell =
            document.querySelector(
              '[data-field="amount"][data-row="' + rid + '"][data-month="' + m + '"] .pl-amt-cell__text'
            ) ||
            document.querySelector(
              '.pl-month-cell[data-row="' + rid + '"][data-month="' + m + '"] .pl-month-cell__text'
            );
          return cell ? cell.textContent : null;
        }""",
        {"rid": rid, "m": month0},
    )
    if txt is None:
        return "MISSING"
    s = txt.strip()
    if s in ("", "—", "-"):
        return None
    digits = re.sub(r"[^0-9]", "", s)
    return int(digits) if digits else None


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    url = f"{url}{'&' if '?' in url else '?'}year={YEAR}"

    page.goto(url, wait_until="load")
    seed(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => typeof window.__plRefreshIncomeBlock === 'function'", timeout=15000
    )
    page.wait_for_selector(
        '[data-field="amount"][data-row="store_sales"][data-month="6"]', timeout=15000
    )

    # 店舗売上 = 総売上 − (A+B)
    if cell_int(page, "store_sales", 6) != JULY_STORE:
        problems.append(f"store_sales July {cell_int(page, 'store_sales', 6)} != {JULY_STORE}")
    if cell_int(page, "store_sales", 7) != AUG_STORE:
        problems.append(f"store_sales Aug {cell_int(page, 'store_sales', 7)} != {AUG_STORE}")
    if cell_int(page, "store_sales", 0) is not None:
        problems.append("store_sales Jan should be em-dash")

    # Sales A from dailyIncome; Sales B has no data → em-dash
    if cell_int(page, "sales_a", 6) != JULY_A:
        problems.append(f"sales_a July {cell_int(page, 'sales_a', 6)} != {JULY_A}")
    if cell_int(page, "sales_a", 0) is not None:
        problems.append("sales_a Jan should be em-dash")
    if cell_int(page, "sales_b", 6) is not None:
        problems.append("sales_b July should be em-dash (no data)")

    # 合計 = 総売上(dailySales)
    if cell_int(page, "sales_total", 6) != JULY_TOTAL:
        problems.append(f"total July {cell_int(page, 'sales_total', 6)} != {JULY_TOTAL}")
    if cell_int(page, "sales_total", 7) != AUG_TOTAL:
        problems.append(f"total Aug {cell_int(page, 'sales_total', 7)} != {AUG_TOTAL}")
    if cell_int(page, "sales_total", 0) is not None:
        problems.append("total Jan should be em-dash")

    # ALL income rows read-only (no contenteditable, no income-editable inputs)
    editability = page.evaluate(
        """() => {
          const rows = ['store_sales', 'sales_a', 'sales_b', 'sales_total'];
          const res = {};
          rows.forEach((rid) => {
            const span =
              document.querySelector(
                '[data-field="amount"][data-row="' + rid + '"][data-month="6"] .pl-amt-cell__text'
              ) ||
              document.querySelector(
                '.pl-month-cell[data-row="' + rid + '"][data-month="6"] .pl-month-cell__text'
              );
            res[rid] = span ? span.getAttribute('contenteditable') : 'none';
          });
          res._anyEditable = document.querySelectorAll('[data-pl-income-editable="1"]').length;
          return res;
        }"""
    )
    for rid in ("store_sales", "sales_a", "sales_b", "sales_total"):
        if editability.get(rid) == "true":
            problems.append(f"{rid} must be read-only (not contenteditable)")
    if editability.get("_anyEditable"):
        problems.append("no income cell should be editable (green input removed)")

    # live: 店舗売上を増やす → dailySales(総売上) 増 → 店舗↑・合計↑・A 不変
    page.evaluate(
        """({ key }) => {
          const store = JSON.parse(localStorage.getItem(key));
          store.timeline.dailySales['2026-07-20'] = 25000;
          localStorage.setItem(key, JSON.stringify(store));
          document.dispatchEvent(new CustomEvent('kpi:dailySalesChanged', { detail: {} }));
        }""",
        {"key": STORE_KEY},
    )
    if cell_int(page, "store_sales", 6) != JULY_STORE + 25000:
        problems.append(f"after dailySalesChanged store {cell_int(page, 'store_sales', 6)}")
    if cell_int(page, "sales_total", 6) != JULY_TOTAL + 25000:
        problems.append(f"after dailySalesChanged total {cell_int(page, 'sales_total', 6)}")
    if cell_int(page, "sales_a", 6) != JULY_A:
        problems.append(f"after dailySalesChanged sales_a should be unchanged {cell_int(page, 'sales_a', 6)}")

    # live: Sales B を追加(不変条件を維持: dailySales も同額増やす=MEP の挙動)
    #   → sales_b 表示・合計↑・店舗は不変(合計と B が同額増えるため)
    page.evaluate(
        """({ key }) => {
          const store = JSON.parse(localStorage.getItem(key));
          store.timeline.dailySales['2026-07-25'] = 5000; // 総売上に B 分を反映
          const rec = store.years['2026'];
          rec.dailyIncome = rec.dailyIncome || {};
          rec.dailyIncome['sales_b'] = { '2026-07-25': 5000 };
          localStorage.setItem(key, JSON.stringify(store));
          document.dispatchEvent(new CustomEvent('kpi:mepDataChanged', { detail: { year: 2026 } }));
        }""",
        {"key": STORE_KEY},
    )
    if cell_int(page, "sales_b", 6) != 5000:
        problems.append(f"after mepDataChanged sales_b {cell_int(page, 'sales_b', 6)} != 5000")
    if cell_int(page, "sales_total", 6) != JULY_TOTAL + 25000 + 5000:
        problems.append(f"after mepDataChanged total {cell_int(page, 'sales_total', 6)}")
    if cell_int(page, "store_sales", 6) != JULY_STORE + 25000:
        problems.append(f"after mepDataChanged store should stay {JULY_STORE + 25000}, got {cell_int(page, 'store_sales', 6)}")

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

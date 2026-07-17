#!/usr/bin/env python3
"""検証: PL Phase D — MEP dailyExpenses の月次合計を PL の daily 行に読取表示."""

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
DAILY_LINE = "exp_food_cost"       # default: variable / daily
MONTHLY_LINE = "exp_rent"          # default: fixed / monthly (editable, must be untouched)

# July (month0=6): 1000 + 2000 = 3000, August (month0=7): 500, other months: none
JULY = {f"{YEAR}-07-01": 1000, f"{YEAR}-07-10": 2000}
AUG = {f"{YEAR}-08-05": 500}


def store_seed() -> dict:
    de = {}
    de[DAILY_LINE] = {**JULY, **AUG}
    return {
        "meta": {"schemaVersion": 4, "operatingYear": YEAR, "legacyMigrated": True},
        "timeline": {"dailySales": {}, "businessDays": {}},
        "years": {
            str(YEAR): {
                "year": YEAR,
                "status": "open",
                "plan": {"targetSales": 600000},
                "dailyExpenses": de,
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
        {"store": store_seed(), "key": "kpiNavigator.kpiYearStore"},
    )


def cell_int(page, line_id: str, month0: int):
    """Return int value of a daily-readonly cell, or None if em-dash/empty."""
    txt = page.evaluate(
        """({ lineId, m }) => {
          const cell = document.querySelector(
            '.pl-amt-cell--pl-daily-readonly[data-row="' + lineId +
            '"][data-month="' + m + '"] .pl-amt-cell__text'
          );
          return cell ? cell.textContent : null;
        }""",
        {"lineId": line_id, "m": month0},
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
        "() => typeof window.__plFillDailyExpenseRowsFromMep === 'function'",
        timeout=15000,
    )
    # ensure detail table is rendered
    page.wait_for_selector(
        f'.pl-amt-cell--pl-daily-readonly[data-row="{DAILY_LINE}"][data-month="6"]',
        timeout=15000,
    )

    # July aggregate = 3000
    v_jul = cell_int(page, DAILY_LINE, 6)
    if v_jul != 3000:
        problems.append(f"July daily-row aggregate {v_jul} != 3000")
    # August aggregate = 500
    v_aug = cell_int(page, DAILY_LINE, 7)
    if v_aug != 500:
        problems.append(f"August daily-row aggregate {v_aug} != 500")
    # January (no data) = em-dash / None
    v_jan = cell_int(page, DAILY_LINE, 0)
    if v_jan is not None:
        problems.append(f"January should be em-dash, got {v_jan}")

    # daily-readonly cell is NOT editable and has the tooltip hint
    editable = page.evaluate(
        """(lineId) => {
          const inner = document.querySelector(
            '.pl-amt-cell--pl-daily-readonly[data-row="' + lineId +
            '"][data-month="6"] .pl-amt-cell__text'
          );
          const td = document.querySelector(
            '.pl-amt-cell--pl-daily-readonly[data-row="' + lineId + '"][data-month="6"]'
          );
          return {
            editable: inner ? inner.getAttribute('contenteditable') : 'none',
            title: td ? td.getAttribute('title') : null
          };
        }""",
        DAILY_LINE,
    )
    if editable.get("editable") == "true":
        problems.append("daily row cell must not be contenteditable")
    if not (editable.get("title") or "").strip():
        problems.append("daily row cell missing tooltip title")

    # monthly (editable) line must remain editable and untouched by the fill
    monthly_editable = page.evaluate(
        """(lineId) => {
          const inner = document.querySelector(
            '.pl-amt-cell--pl-monthly-editable[data-row="' + lineId +
            '"][data-month="6"] .pl-amt-cell__text'
          );
          return inner ? inner.getAttribute('contenteditable') : 'none';
        }""",
        MONTHLY_LINE,
    )
    if monthly_editable != "true":
        problems.append(f"monthly line should stay editable: {monthly_editable}")

    # live update via kpi:mepDataChanged: add 07-20 = 1500 → July becomes 4500
    page.evaluate(
        """({ key, line }) => {
          const store = JSON.parse(localStorage.getItem(key));
          store.years['2026'].dailyExpenses[line]['2026-07-20'] = 1500;
          localStorage.setItem(key, JSON.stringify(store));
          document.dispatchEvent(
            new CustomEvent('kpi:mepDataChanged', { detail: { year: 2026 } })
          );
        }""",
        {"key": "kpiNavigator.kpiYearStore", "line": DAILY_LINE},
    )
    v_jul2 = cell_int(page, DAILY_LINE, 6)
    if v_jul2 != 4500:
        problems.append(f"after mepDataChanged July {v_jul2} != 4500")

    # event for a different year must be ignored
    page.evaluate(
        """() => {
          document.dispatchEvent(
            new CustomEvent('kpi:mepDataChanged', { detail: { year: 2099 } })
          );
        }"""
    )
    v_jul3 = cell_int(page, DAILY_LINE, 6)
    if v_jul3 != 4500:
        problems.append(f"other-year event should not change July {v_jul3}")

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

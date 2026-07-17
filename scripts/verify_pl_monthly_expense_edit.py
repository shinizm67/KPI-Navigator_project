#!/usr/bin/env python3
"""検証: PL 支出明細の monthly セル入力 → kpi-pl-expenses-v1 保存/読込."""

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
LINE_ID = "exp_rent"
MONTH_IDX = 6  # July
DAILY_LINE = "exp_food_cost"


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    storage_key = f"kpi-pl-expenses-v1:{YEAR}"
    # year via query so storage key matches without forcing select-change navigation
    if "?" in url:
        url = f"{url}&year={YEAR}"
    else:
        url = f"{url}?year={YEAR}"

    # Clear once on the page origin, then reload (do not use add_init_script —
    # it would wipe storage again on reload).
    page.goto(url, wait_until="load")
    page.evaluate("() => localStorage.clear()")
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => document.querySelectorAll('[data-pl-editable=\"1\"]').length > 0",
        timeout=15000,
    )

    counts = page.evaluate(
        """() => {
          const editable = document.querySelectorAll('[data-pl-editable="1"]');
          const dailyReadonly = document.querySelectorAll(
            '.pl-amt-cell--pl-daily-readonly .pl-amt-cell__text'
          );
          const dashCount = Array.from(dailyReadonly).filter(
            (el) => (el.textContent || '').trim() === '—'
          ).length;
          const rentEditable = document.querySelectorAll(
            '[data-pl-editable="1"][data-row="exp_rent"]'
          ).length;
          const foodEditable = document.querySelectorAll(
            '[data-pl-editable="1"][data-row="exp_food_cost"]'
          ).length;
          return {
            editable: editable.length,
            dailyReadonly: dailyReadonly.length,
            dailyDash: dashCount,
            rentEditable,
            foodEditable,
            year: document.getElementById('pl-year-select')?.value || null,
          };
        }"""
    )
    if counts.get("year") != str(YEAR):
        problems.append(f"year mismatch: {counts}")
    if counts["rentEditable"] != 12:
        problems.append(f"rent monthly editable expected 12: {counts}")
    if counts["foodEditable"] != 0:
        problems.append(f"food daily must not be editable: {counts}")
    if counts["dailyReadonly"] < 12 or counts["dailyDash"] < 12:
        problems.append(f"daily readonly dashes missing: {counts}")

    cell_sel = (
        f'[data-pl-editable="1"][data-row="{LINE_ID}"][data-month="{MONTH_IDX}"]'
    )
    cell = page.locator(cell_sel).first
    if cell.count() == 0:
        problems.append(f"missing editable cell {cell_sel}")
        return problems

    cell.click()
    page.keyboard.press("Meta+A")
    page.keyboard.type("123456")
    cell.blur()

    text_after = cell.inner_text().strip()
    digits = "".join(ch for ch in text_after if ch.isdigit())
    if digits != "123456":
        problems.append(f"format after blur unexpected: {text_after!r}")

    page.once("dialog", lambda d: d.accept())
    page.click("#pl-save")

    stored = page.evaluate(
        f"() => JSON.parse(localStorage.getItem({json.dumps(storage_key)}) || '{{}}')"
    )
    key = f"{LINE_ID}:{MONTH_IDX}"
    if stored.get(key) != 123456:
        problems.append(f"storage missing/wrong {key}: {stored!r}")

    page.reload(wait_until="load")
    page.wait_for_function(
        f"() => {{"
        f"  const el = document.querySelector({json.dumps(cell_sel)});"
        f"  return !!(el && /123/.test((el.textContent || '').replace(/,/g, '')));"
        f"}}",
        timeout=15000,
    )
    restored = page.locator(cell_sel).first.inner_text().strip()
    restored_digits = "".join(ch for ch in restored if ch.isdigit())
    if restored_digits != "123456":
        problems.append(f"reload restore failed: {restored!r}")

    daily_editable = page.evaluate(
        f"""() => document.querySelectorAll(
          '[data-pl-editable="1"][data-row="{DAILY_LINE}"]'
        ).length"""
    )
    if daily_editable != 0:
        problems.append(f"daily line should not be editable: {daily_editable}")

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

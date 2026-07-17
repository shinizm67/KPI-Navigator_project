#!/usr/bin/env python3
"""検証: 固定費 monthly — 他月空なら黙って全月反映 / 差があれば confirm."""

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
FIXED_LINE = "exp_rent"
VAR_MONTHLY = "exp_electric"


def row_amounts(page, line_id: str) -> list[int]:
    return page.evaluate(
        """(lineId) => {
          const cells = Array.from(
            document.querySelectorAll(`[data-pl-editable="1"][data-row="${lineId}"]`)
          );
          cells.sort(
            (a, b) => Number(a.getAttribute('data-month')) - Number(b.getAttribute('data-month'))
          );
          return cells.map((c) => {
            const raw = String(c.textContent || '').replace(/[^\\d.-]/g, '');
            const n = parseInt(raw, 10);
            return Number.isFinite(n) ? n : 0;
          });
        }""",
        line_id,
    )


def set_row_amounts(page, line_id: str, amounts: list[int]) -> None:
    page.evaluate(
        """({ lineId, amounts }) => {
          amounts.forEach((n, mi) => {
            const cell = document.querySelector(
              `[data-pl-editable="1"][data-row="${lineId}"][data-month="${mi}"]`
            );
            if (!cell) return;
            const isJa = document.documentElement.lang === 'ja';
            const formatted = (isJa ? '¥' : '$') + Number(n).toLocaleString('en-US');
            cell.textContent = formatted;
          });
        }""",
        {"lineId": line_id, "amounts": amounts},
    )


def type_into_cell(page, line_id: str, month: int, text: str) -> None:
    sel = f'[data-pl-editable="1"][data-row="{line_id}"][data-month="{month}"]'
    cell = page.locator(sel).first
    cell.click()
    page.keyboard.press("Meta+A")
    page.keyboard.type(text)
    cell.blur()


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    if "?" in url:
        url = f"{url}&year={YEAR}"
    else:
        url = f"{url}?year={YEAR}"

    page.goto(url, wait_until="load")
    page.evaluate("() => localStorage.clear()")
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => document.querySelectorAll('[data-pl-editable=\"1\"]').length > 0",
        timeout=15000,
    )

    # --- Case 1: empty others → silent fill ---
    type_into_cell(page, FIXED_LINE, 0, "50000")
    amounts = row_amounts(page, FIXED_LINE)
    if amounts != [50000] * 12:
        problems.append(f"silent fill failed: {amounts}")

    # --- Case 2: differing months → confirm Yes ---
    set_row_amounts(page, FIXED_LINE, [50000, 60000] + [50000] * 10)
    dialogs: list[str] = []

    def on_dialog(d):
        dialogs.append(d.message)
        d.accept()

    page.on("dialog", on_dialog)
    type_into_cell(page, FIXED_LINE, 0, "70000")
    page.remove_listener("dialog", on_dialog)
    amounts = row_amounts(page, FIXED_LINE)
    if not dialogs:
        problems.append("expected confirm when months differ (Yes path)")
    elif "all months" not in dialogs[0].lower() and "全ての月" not in dialogs[0]:
        problems.append(f"unexpected confirm text: {dialogs[0]!r}")
    if amounts != [70000] * 12:
        problems.append(f"confirm Yes fill failed: {amounts}")

    # --- Case 3: differing months → confirm No ---
    set_row_amounts(page, FIXED_LINE, [70000, 80000] + [70000] * 10)
    dialogs_no: list[str] = []

    def on_dialog_no(d):
        dialogs_no.append(d.message)
        d.dismiss()

    page.on("dialog", on_dialog_no)
    type_into_cell(page, FIXED_LINE, 0, "90000")
    page.remove_listener("dialog", on_dialog_no)
    amounts = row_amounts(page, FIXED_LINE)
    if not dialogs_no:
        problems.append("expected confirm when months differ (No path)")
    if amounts[0] != 90000:
        problems.append(f"No path: edited month wrong: {amounts}")
    if amounts[1] != 80000 or any(a != 70000 for a in amounts[2:]):
        problems.append(f"No path should not rewrite others: {amounts}")

    # --- Case 4: variable monthly must NOT auto-fill ---
    set_row_amounts(page, VAR_MONTHLY, [0] * 12)
    type_into_cell(page, VAR_MONTHLY, 0, "11111")
    var_amounts = row_amounts(page, VAR_MONTHLY)
    if var_amounts[0] != 11111:
        problems.append(f"variable monthly type failed: {var_amounts}")
    if any(a != 0 for a in var_amounts[1:]):
        problems.append(f"variable monthly must not fill all: {var_amounts}")

    # --- Case 5: already uniform → no dialog ---
    set_row_amounts(page, FIXED_LINE, [1000] * 12)
    quiet: list[str] = []

    def on_quiet(d):
        quiet.append(d.message)
        d.dismiss()

    page.on("dialog", on_quiet)
    type_into_cell(page, FIXED_LINE, 3, "1000")
    page.remove_listener("dialog", on_quiet)
    if quiet:
        problems.append(f"should not confirm when already uniform: {quiet}")

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

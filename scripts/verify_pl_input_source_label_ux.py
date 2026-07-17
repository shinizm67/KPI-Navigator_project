#!/usr/bin/env python3
"""検証: PL 支出明細は統合モーダル（ラベル＋入力元）。Don't ask again なし・各行トグルなし.

- 変動費ラベルをダブルクリック → pl-expense-label-edit-modal が開く
- 科目名入力欄と入力元ラジオがある（Don't ask again は無い）
- 入力元を monthly にして決定 → 行が --input-monthly、カタログも monthly
- 固定費ラベルでは入力元ラジオが隠れる
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
CATALOG_KEY = "kpiNavigator.plLineCatalog"
FOOD = "exp_food_cost"
RENT = "exp_rent"


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.goto(f"{url}?year={YEAR}", wait_until="load")
    page.evaluate("() => localStorage.clear()")
    page.reload(wait_until="load")
    page.wait_for_selector(
        f'[data-pl-label-editable="1"][data-label-id="{FOOD}"]',
        timeout=15000,
    )

    if page.locator(".pl-input-source-toggle, [data-pl-input-source-toggle]").count():
        problems.append("per-row input toggle should not exist")

    page.locator(f'[data-pl-label-editable="1"][data-label-id="{FOOD}"]').dblclick()
    page.wait_for_selector("#pl-expense-label-edit-modal:not([hidden])", timeout=5000)

    # Don't ask again は統合モーダルに無い
    if page.locator("#pl-expense-label-edit-modal #pl-input-source-skip").count():
        problems.append("unified modal must not include Don't-ask-again")
    if page.locator("#pl-expense-label-edit-input").count() != 1:
        problems.append("unified modal must include label input")
    if page.locator("#pl-expense-label-edit-source:not([hidden])").count() != 1:
        problems.append("variable row must show input-source choices")

    page.locator('input[name="pl-expense-label-edit-source"][value="monthly"]').click(
        force=True
    )
    page.locator(
        '#pl-expense-label-edit-modal button[data-pl-label-edit-action="confirm"]'
    ).click()
    page.wait_for_function(
        "() => { const m = document.getElementById('pl-expense-label-edit-modal'); return m && m.hidden; }",
        timeout=5000,
    )

    row_cls = page.evaluate(
        """({ id }) => {
          const tr = document.querySelector('tr[data-line-id=\"' + id + '\"]');
          return tr ? tr.className : '';
        }""",
        {"id": FOOD},
    )
    if "pl-expense-detail-row--input-monthly" not in row_cls:
        problems.append(f"food row should become monthly, class={row_cls!r}")

    style = page.evaluate(
        """({ key, id }) => {
          const raw = localStorage.getItem(key);
          if (!raw) return null;
          const line = (JSON.parse(raw).lines || []).find((l) => l.lineId === id);
          return line ? (line.resolvedInputStyle || line.inputStyle) : null;
        }""",
        {"key": CATALOG_KEY, "id": FOOD},
    )
    if style != "monthly":
        problems.append(f"catalog {FOOD} style={style!r} want monthly")

    # 固定費: 入力元セクションは hidden
    rent = page.locator(f'[data-pl-label-editable="1"][data-label-id="{RENT}"]')
    if rent.count() == 0:
        problems.append("rent label not found")
        return problems
    rent.dblclick()
    page.wait_for_selector("#pl-expense-label-edit-modal:not([hidden])", timeout=5000)
    source_hidden = page.evaluate(
        "() => { const fs = document.getElementById('pl-expense-label-edit-source'); return !fs || fs.hidden; }"
    )
    if not source_hidden:
        problems.append("fixed-cost modal must hide input-source choices")
    page.locator(
        '#pl-expense-label-edit-modal button[data-pl-label-edit-action="cancel"]'
    ).click()
    page.wait_for_function(
        "() => { const m = document.getElementById('pl-expense-label-edit-modal'); return m && m.hidden; }",
        timeout=5000,
    )

    badge_count = page.evaluate(
        "() => document.querySelectorAll('.pl-input-badge').length"
    )
    if badge_count:
        problems.append(f"row DAILY/MONTHLY badges should be removed, found {badge_count}")

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

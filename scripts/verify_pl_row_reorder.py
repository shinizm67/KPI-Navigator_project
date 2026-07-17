#!/usr/bin/env python3
"""検証: PL 支出明細の ▲▼ 行並べ替え（同バケット内・永続化）。"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app/profit/pl/index.html"
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)
CATALOG_KEY = "kpiNavigator.plLineCatalog"


def active_fixed_ids(page) -> list[str]:
    return page.evaluate(
        """() => Array.from(
          document.querySelectorAll(
            '#pl-expense-detail-data-body tr[data-bucket="fixed"][data-line-id]'
          )
        ).map((tr) => tr.getAttribute('data-line-id'))"""
    )


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: chromium missing {EXE}", file=sys.stderr)
        return 2
    errs: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page()
        page.goto(PAGE.resolve().as_uri(), wait_until="domcontentloaded")
        page.evaluate("() => localStorage.clear()")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(600)

        before = active_fixed_ids(page)
        if len(before) < 2:
            errs.append(f"need >=2 fixed rows, got {before}")
        else:
            second = before[1]
            page.click(
                f'#pl-expense-detail-label-body button[data-action="move-up"][data-line-id="{second}"]'
            )
            page.wait_for_timeout(300)
            after = active_fixed_ids(page)
            if after[0] != second:
                errs.append(f"move-up failed: before={before} after={after}")
            stored = page.evaluate(
                """(key) => {
                  const raw = localStorage.getItem(key);
                  const parsed = raw ? JSON.parse(raw) : null;
                  const fixed = (parsed && parsed.lines || [])
                    .filter((l) => l.bucket === 'fixed' && l.active)
                    .sort((a, b) => a.sortOrder - b.sortOrder)
                    .map((l) => l.lineId);
                  return fixed;
                }""",
                CATALOG_KEY,
            )
            if stored[:2] != after[:2]:
                errs.append(f"catalog sortOrder mismatch UI={after[:2]} store={stored[:2]}")

            page.click(
                f'#pl-expense-detail-label-body button[data-action="move-down"][data-line-id="{second}"]'
            )
            page.wait_for_timeout(300)
            back = active_fixed_ids(page)
            if back != before:
                errs.append(f"move-down restore failed: want {before} got {back}")
        browser.close()

    if errs:
        print("FAIL")
        for e in errs:
            print(" -", e)
        return 1
    print("OK: PL expense row reorder")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

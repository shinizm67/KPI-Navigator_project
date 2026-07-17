#!/usr/bin/env python3
"""Phase 3 verify: edit Sales A/B labels on MEP and reflect on PL."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]
PL_PAGES = [
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


def seed(page) -> None:
    page.evaluate(
        """({ key, year }) => {
          localStorage.clear();
          localStorage.setItem('kpiNavigator.subscriptionTier', 'pro');
          // keep minimal year store so MEP boot has expected shape
          localStorage.setItem(
            'kpiNavigator.kpiYearStore',
            JSON.stringify({
              meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
              timeline: { dailySales: {}, businessDays: {} },
              years: { [String(year)]: { year, status: 'open', plan: {}, dailyExpenses: {}, dailyIncome: {}, dailyMeta: { memos: {}, flags: {}, weather: {} } } },
            })
          );
          void key;
        }""",
        {"key": CATALOG_KEY, "year": YEAR},
    )


def verify_pair(browser, mep_url: str, pl_url: str, *, is_ja: bool) -> list[str]:
    problems: list[str] = []
    mep = browser.new_page()
    pl = browser.new_page()
    label = "客席売上A" if is_ja else "Seat Sales A"
    try:
        mep.goto(f"{mep_url}?year={YEAR}&month=7", wait_until="load")
        seed(mep)
        mep.reload(wait_until="load")
        mep.wait_for_selector('[data-action="edit-label"][data-row-id="sales_a"]', timeout=15000)

        # edit Sales A label on MEP
        mep.click('[data-action="edit-label"][data-row-id="sales_a"]')
        mep.wait_for_selector('input.monthly-edit-float__label-edit-input', timeout=5000)
        mep.fill('input.monthly-edit-float__label-edit-input', label)
        mep.press('input.monthly-edit-float__label-edit-input', "Enter")
        mep.wait_for_timeout(150)

        # storage write check
        wrote = mep.evaluate(
            """({ key }) => {
              const raw = localStorage.getItem(key);
              if (!raw) return null;
              const lines = (JSON.parse(raw).lines || []);
              const a = lines.find((l) => l.lineId === 'sales_a');
              return a ? { ja: a.labelJa, en: a.labelEn } : null;
            }""",
            {"key": CATALOG_KEY},
        )
        expect_key = "ja" if is_ja else "en"
        if not wrote or wrote.get(expect_key) != label:
            problems.append(f"MEP did not persist sales_a label to catalog: {wrote!r}")

        # file:// origins do not share localStorage across paths — copy catalog into PL.
        catalog_raw = mep.evaluate(
            """({ key }) => localStorage.getItem(key)""",
            {"key": CATALOG_KEY},
        )

        # open PL and verify reflected label
        pl.goto(f"{pl_url}?year={YEAR}", wait_until="load")
        pl.evaluate(
            """({ key, raw, year }) => {
              localStorage.setItem('kpiNavigator.subscriptionTier', 'pro');
              if (raw) localStorage.setItem(key, raw);
              localStorage.setItem(
                'kpiNavigator.kpiYearStore',
                JSON.stringify({
                  meta: { schemaVersion: 4, operatingYear: year, legacyMigrated: true },
                  timeline: { dailySales: {}, businessDays: {} },
                  years: { [String(year)]: { year, status: 'open', plan: {}, dailyExpenses: {}, dailyIncome: {}, dailyMeta: { memos: {}, flags: {}, weather: {} } } },
                })
              );
            }""",
            {"key": CATALOG_KEY, "raw": catalog_raw, "year": YEAR},
        )
        pl.reload(wait_until="load")
        pl.wait_for_selector('[data-pl-label-editable="1"][data-label-id="sales_a"]', timeout=15000)
        text = pl.evaluate(
            """() => {
              const el = document.querySelector('[data-pl-label-editable="1"][data-label-id="sales_a"]');
              return el ? String(el.textContent || '').trim() : '';
            }"""
        )
        if text != label:
            problems.append(f"PL sales_a label not reflected, got {text!r}")

    finally:
        mep.close()
        pl.close()
    return problems


def main() -> int:
    if not EXE.exists():
        print(f"Chrome missing: {EXE}", file=sys.stderr)
        return 2
    fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for mep_path, pl_path in zip(MEP_PAGES, PL_PAGES):
            is_ja = "/en/" not in str(mep_path)
            try:
                problems = verify_pair(
                    browser, mep_path.as_uri(), pl_path.as_uri(), is_ja=is_ja
                )
            except Exception as e:  # noqa: BLE001
                problems = [f"exception: {e}"]
            if problems:
                fail += 1
                print(f"FAIL {mep_path}: {problems}")
            else:
                print(f"OK   {mep_path}")
        browser.close()
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())


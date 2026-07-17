#!/usr/bin/env python3
"""検証: Daily FW 日付ナビが押しっぱなしで連打する."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def build_seed() -> dict:
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {"dailySales": {}, "businessDays": {}},
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
            }
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    seed = build_seed()
    page.add_init_script(
        "window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);"
        % json.dumps(json.dumps(seed))
    )
    page.goto(url, wait_until="load")
    page.wait_for_selector("#global-nav-daily-btn", state="attached", timeout=20000)
    page.wait_for_selector("#daily-overlay-next-day", state="attached", timeout=20000)
    # open daily overlay via nav
    page.click("#global-nav-daily-btn")
    page.wait_for_selector("#daily-overlay:not([hidden])", timeout=10000)
    page.wait_for_selector("#daily-overlay-next-day", state="visible", timeout=10000)
    page.wait_for_function(
        "() => document.getElementById('daily-overlay-date-btn') && "
        "document.getElementById('daily-overlay-date-btn').textContent && "
        "document.getElementById('daily-overlay-date-btn').textContent !== '—'",
        timeout=10000,
    )
    # Ensure marker present
    has_marker = page.evaluate(
        "() => String(document.documentElement.innerHTML).includes('bindDailyOverlayDateHoldRepeat')"
    )
    if not has_marker:
        problems.append(f"{url}: bindDailyOverlayDateHoldRepeat missing")

    # Set known iso via input path inside overlay IIFE is hard; use next then check advance via hold
    next_btn = page.locator("#daily-overlay-next-day")
    date_btn = page.locator("#daily-overlay-date-btn")
    before = date_btn.inner_text()

    # Hold next for ~700ms → initial step + at least one interval (400 delay + 75)
    next_btn.dispatch_event("pointerdown", {"button": 0, "pointerType": "mouse", "pointerId": 1})
    page.wait_for_timeout(700)
    next_btn.dispatch_event("pointerup", {"button": 0, "pointerType": "mouse", "pointerId": 1})
    after = date_btn.inner_text()
    if after == before:
        problems.append(f"{url}: date did not change on hold (before={before!r} after={after!r})")

    # Brief click-equivalent: pointerdown+up quickly should step once
    mid = date_btn.inner_text()
    next_btn.dispatch_event("pointerdown", {"button": 0, "pointerType": "mouse", "pointerId": 2})
    next_btn.dispatch_event("pointerup", {"button": 0, "pointerType": "mouse", "pointerId": 2})
    page.wait_for_timeout(50)
    after_tap = date_btn.inner_text()
    if after_tap == mid:
        problems.append(f"{url}: single tap did not advance (mid={mid!r})")

    # Confirm hold advanced more than 1 day from before (700ms > 400+75)
    advanced = page.evaluate(
        """([beforeText, afterText]) => {
          function parseLoose(t) {
            const m = String(t).match(/(\\d{4})\\/(\\d{1,2})\\/(\\d{1,2})/);
            if (!m) return null;
            return new Date(+m[1], +m[2]-1, +m[3]);
          }
          const a = parseLoose(beforeText);
          const b = parseLoose(afterText);
          if (!a || !b) return { ok: false, days: null };
          const days = Math.round((b - a) / 86400000);
          return { ok: days >= 2, days };
        }""",
        [before, after],
    )
    if not advanced.get("ok"):
        problems.append(
            f"{url}: hold should advance >=2 days, got days={advanced.get('days')} "
            f"({before!r} → {after!r})"
        )

    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} {before!r} --hold--> {after!r} (days={advanced.get('days')}) tap->{after_tap!r}")
    return problems


def main() -> int:
    import os

    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
            url = path.as_uri()
            problems.extend(verify_page(page, url))
            page.close()
        browser.close()
    if problems:
        print("FAIL:")
        for pr in problems:
            print(" ", pr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

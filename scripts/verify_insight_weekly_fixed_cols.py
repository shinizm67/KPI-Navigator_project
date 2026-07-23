#!/usr/bin/env python3
"""Verify Weekly Insight column widths stay fixed when memo text is long."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)

MEMO_ROWS = [
    {"id": "memo_store", "labelJa": "Store Event", "labelEn": "Store Event"},
    {"id": "memo_area", "labelJa": "Area Event", "labelEn": "Area Event"},
    {"id": "memo_social", "labelJa": "Social Media", "labelEn": "Social Media"},
    {"id": "memo_marketing", "labelJa": "Marketing", "labelEn": "Marketing"},
    {"id": "memo_promo", "labelJa": "Promo Conversion", "labelEn": "Promo Conversion"},
    {"id": "memo_reservation", "labelJa": "Reservation", "labelEn": "Reservation"},
]

EXPECTED_W = {
    "date": 170,
    "weather": 114,
    "store": 128,
    "area": 128,
    "social": 168,
    "marketing": 208,
    "promo": 128,
    "reservation": 156,
}


def seed() -> dict:
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-18",
        },
        "timeline": {
            "dailySales": {"2026-07-18": 10000},
            "businessDays": {"2026-07-18": True},
        },
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
                "mepMemoRows": MEMO_ROWS,
                "dailyMeta": {
                    "memos": {
                        "memo_store": {"2026-07-18": "S" * 60},
                        "memo_area": {"2026-07-18": ""},
                        "memo_social": {"2026-07-18": "G" * 40},
                        "memo_marketing": {"2026-07-18": "M" * 100},
                        "memo_promo": {"2026-07-18": "P" * 40},
                        "memo_reservation": {"2026-07-18": "R" * 40},
                    },
                    "flags": {"2026-07-18": True},
                    "weather": {"2026-07-18": "sunny"},
                },
            }
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.add_init_script(
        "window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);"
        % json.dumps(json.dumps(seed()))
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          document.getElementById('global-nav-index-btn').click();
          document.getElementById('insight-tab-analyze').click();
          const weekly = document.querySelector('#insight-pane-analyze .insight-analyze-weekly');
          if (weekly) weekly.__weeklyAnchorIso = '2026-07-18';
          document.dispatchEvent(new CustomEvent('insight:dateChanged', { detail: { iso: '2026-07-18' } }));
          return new Promise((resolve) => {
            requestAnimationFrame(() => requestAnimationFrame(() => {
              const scroll = weekly.querySelector('.insight-analyze-weekly__table-scroll');
              const headers = {};
              const widths = {};
              ['date','weather','store','area','social','marketing','promo','reservation'].forEach((c) => {
                const th = weekly.querySelector('thead th.insight-analyze-weekly__col--' + c);
                headers[c] = th ? (th.textContent || '').trim() : '';
                widths[c] = th ? Math.round(th.getBoundingClientRect().width) : 0;
              });
              resolve({
                scrollWidth: scroll.scrollWidth,
                headers,
                widths,
                hasTableW: getComputedStyle(weekly).getPropertyValue('--insight-weekly-table-w').trim(),
              });
            }));
          });
        }"""
    )
    if abs(result["scrollWidth"] - 1200) > 2:
        problems.append(f"{url}: scrollWidth={result['scrollWidth']} (want 1200)")
    for col, want in EXPECTED_W.items():
        got = result["widths"].get(col, 0)
        if abs(got - want) > 2:
            problems.append(f"{url}: {col} width {got} != {want}")
    if not result["headers"].get("promo"):
        problems.append(f"{url}: Promo header text empty")
    if not result["headers"].get("reservation"):
        problems.append(f"{url}: Reservation header text empty")
    if "1200px" not in result.get("hasTableW", ""):
        problems.append(f"{url}: --insight-weekly-table-w missing ({result.get('hasTableW')!r})")
    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} sw={result['scrollWidth']} widths={result['widths']}")
    return problems


def main() -> int:
    import os

    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    # static marker check on all 4
    for path in [
        ROOT / "app/monthly/index.html",
        ROOT / "en/app/monthly/index.html",
        ROOT / "app/annual/index.html",
        ROOT / "en/app/annual/index.html",
    ]:
        text = path.read_text(encoding="utf-8")
        if "--insight-weekly-table-w: 1200px" not in text:
            print(f"FAIL marker {path.name}", file=sys.stderr)
            return 1
        if "width: max-content" in text and "insight-analyze-weekly__table" in text:
            # ensure weekly table no longer uses max-content
            idx = text.find(".insight-pane--analyze .insight-analyze-weekly__table")
            chunk = text[idx : idx + 350]
            if "max-content" in chunk:
                print(f"FAIL max-content still on weekly table: {path.name}", file=sys.stderr)
                return 1

    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            problems.extend(verify_page(page, path.as_uri()))
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

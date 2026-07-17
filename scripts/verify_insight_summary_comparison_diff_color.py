#!/usr/bin/env python3
"""検証: Summary Comparison 差分に tw-diff クラス＋色が付く."""

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
    import datetime

    daily_sales = {}
    business_days = {}

    def fill_month(year, month, base):
        d = datetime.date(year, month, 1)
        while d.month == month:
            iso = d.isoformat()
            wk = d.weekday() >= 5
            business_days[iso] = not wk
            if not wk:
                daily_sales[iso] = base + d.day * 10
            d += datetime.timedelta(days=1)

    for y, base in ((2025, 5000), (2026, 2000)):  # 2026 < 2025 → negative difference
        for mo in range(1, 8):
            fill_month(y, mo, base + mo * 100)

    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {"dailySales": daily_sales, "businessDays": business_days},
        "years": {
            str(y): {
                "year": y,
                "status": "open" if y == 2026 else "closed",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
            }
            for y in (2025, 2026)
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
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          window.renderInsightTwDiffs(iso);
          const mRows = [...document.querySelectorAll(
            '.insight-monthly-comparison .insight-monthly-comparison__value'
          )];
          const aRows = [...document.querySelectorAll(
            '.insight-annual-comparison .insight-annual-comparison__value'
          )];
          const mDiff = mRows[2];
          const aDiff = aRows[2];
          function info(el) {
            if (!el) return null;
            const cs = getComputedStyle(el);
            return {
              text: el.textContent.trim(),
              className: el.className,
              color: cs.color,
              hasSev: /tw-diff--sev-/.test(el.className) || /tw-diff--win/.test(el.className),
            };
          }
          // css rule presence
          const sheetHas =
            [...document.styleSheets].some((ss) => {
              try {
                return [...ss.cssRules].some(
                  (r) =>
                    r.selectorText &&
                    r.selectorText.includes('insight-monthly-comparison__value.tw-diff')
                );
              } catch (_e) {
                return false;
              }
            });
          return {
            m: info(mDiff),
            a: info(aDiff),
            sheetHas,
            m0class: mRows[0] && mRows[0].className,
          };
        }"""
    )
    if not result.get("sheetHas"):
        problems.append(f"{url}: CSS rule for comparison tw-diff missing")
    for key in ("m", "a"):
        info = result.get(key) or {}
        if not info.get("hasSev"):
            problems.append(f"{url}: {key} diff missing tw-diff class {info}")
        # negative seed → should not be pure cyan win if severely behind
        # rgb of sev colors are warmer; win/neutral is cyan-ish
        color = info.get("color") or ""
        if "tw-diff--win" in (info.get("className") or ""):
            problems.append(f"{url}: {key} expected negative severity, got win {info}")
        if color in ("rgb(88, 225, 243)", "rgba(88, 225, 243, 1)"):
            # might still be sev with different color; only flag if no sev class
            if "tw-diff--sev-" not in (info.get("className") or ""):
                problems.append(f"{url}: {key} still cyan without severity {info}")
    # row0 sales should typically not keep a severity class after patch (only diff gets meta)
    # actually setRow only applies class when arguments >= 4, rows 0-1 don't — ok
    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} monthly={result.get('m')} annual={result.get('a')}")
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

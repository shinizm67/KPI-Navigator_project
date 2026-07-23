#!/usr/bin/env python3
"""Verify Analyze tab switch defers heavy render (markers + cache behavior)."""

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

MARKERS = [
    "__INSIGHT_TAB_PENDING",
    "runInsightAnalyzePatches",
    "__INSIGHT_PANE_CACHE",
    "mode: pendingTab",
]


def main() -> int:
    import os

    failed = 0
    for path in [
        ROOT / "app/monthly/index.html",
        ROOT / "en/app/monthly/index.html",
        ROOT / "app/annual/index.html",
        ROOT / "en/app/annual/index.html",
    ]:
        text = path.read_text(encoding="utf-8")
        for needle in MARKERS:
            if needle not in text:
                print(f"FAIL {path.name}: missing {needle}", file=sys.stderr)
                failed += 1
        if (
            "window.renderInsightTwDiffs(window.__INSIGHT_SELECTED_ISO);" in text
            and "__INSIGHT_TAB_PENDING" in text
        ):
            # sync call in setInsightTab should be gone
            sync_in_tab = (
                "if (which === 'analyze' || which === 'graph') {\n"
                "          try {\n"
                "            if (window.__INSIGHT_SELECTED_ISO && typeof window.renderInsightTwDiffs === 'function') {\n"
                "              window.renderInsightTwDiffs(window.__INSIGHT_SELECTED_ISO);"
            )
            if sync_in_tab in text:
                print(f"FAIL {path.name}: sync tab render still present", file=sys.stderr)
                failed += 1

    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    seed = {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {
            "dailySales": {"2026-07-14": 10000},
            "businessDays": {"2026-07-14": True},
        },
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
            }
        },
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
            page.add_init_script(
                "window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);"
                % json.dumps(json.dumps(seed))
            )
            page.goto(path.as_uri(), wait_until="load")
            page.wait_for_function(
                "() => typeof window.renderInsightTwDiffs === 'function'",
                timeout=20000,
            )
            result = page.evaluate(
                """() => {
                  document.getElementById('global-nav-index-btn').click();
                  const tab = document.getElementById('insight-tab-analyze');
                  const before = performance.now();
                  tab.click();
                  const afterClick = performance.now();
                  const pane = document.getElementById('insight-pane-analyze');
                  const shown = pane && !pane.hidden;
                  const cacheBefore = (window.__INSIGHT_PANE_CACHE || {}).analyzeIso || null;
                  return {
                    clickMs: afterClick - before,
                    shown: shown,
                    cacheBefore: cacheBefore,
                    hasPending: !!window.__INSIGHT_TAB_PENDING || !!window.__INSIGHT_TAB_SCHED,
                  };
                }"""
            )
            # Wait for async analyze to finish
            page.wait_for_function(
                "() => window.__INSIGHT_PANE_CACHE && "
                "window.__INSIGHT_PANE_CACHE.analyzeIso === window.__INSIGHT_SELECTED_ISO",
                timeout=15000,
            )
            # Second click should be cache hit (near-instant, no pending)
            result2 = page.evaluate(
                """() => {
                  document.getElementById('insight-tab-summary').click();
                  const t0 = performance.now();
                  document.getElementById('insight-tab-analyze').click();
                  const t1 = performance.now();
                  return {
                    clickMs: t1 - t0,
                    cache: (window.__INSIGHT_PANE_CACHE || {}).analyzeIso,
                    pending: window.__INSIGHT_TAB_PENDING,
                  };
                }"""
            )
            rel = str(path.relative_to(ROOT))
            print(f"  {rel} first={result} second={result2}")
            if not result.get("shown"):
                print(f"FAIL {rel}: analyze pane not shown immediately", file=sys.stderr)
                failed += 1
            if result.get("clickMs", 999) > 50:
                # click handler itself should be cheap (defer work)
                print(
                    f"FAIL {rel}: click handler too slow {result.get('clickMs')}ms",
                    file=sys.stderr,
                )
                failed += 1
            if result2.get("pending"):
                print(f"FAIL {rel}: cache hit still scheduled work", file=sys.stderr)
                failed += 1
            page.close()
        browser.close()

    if failed:
        print(f"{failed} check(s) failed", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

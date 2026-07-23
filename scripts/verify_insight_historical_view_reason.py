#!/usr/bin/env python3
"""検証: Historical Insight Access の View Reason が MEP メモを集約する."""

from __future__ import annotations

import json
import os
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
    {"id": "memo_store", "labelJa": "店舗イベント", "labelEn": "Store Event"},
    {"id": "memo_area", "labelJa": "エリア", "labelEn": "Area Event"},
    {"id": "memo_social", "labelJa": "SNS", "labelEn": "Social Media"},
    {"id": "memo_marketing", "labelJa": "マーケ", "labelEn": "Marketing"},
    {"id": "memo_promo", "labelJa": "プロモ", "labelEn": "Promo Conversion"},
    {"id": "memo_reservation", "labelJa": "予約", "labelEn": "Reservation"},
]


def seed_store() -> dict:
    # Best same-month July among past years: 2025 has higher sales than 2024.
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {
            "dailySales": {
                "2025-07-01": 90000,
                "2025-07-10": 50000,
                "2024-07-01": 10000,
            },
            "businessDays": {},
        },
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
                "mepMemoRows": MEMO_ROWS,
                "dailyMeta": {"memos": {}, "weather": {}, "flags": {}},
                "monthlyStrategyUserNotes": {},
            },
            "2025": {
                "year": 2025,
                "status": "closed",
                "plan": {"targetSales": 500000, "monthlyHlWeights": [100] * 12},
                "mepMemoRows": MEMO_ROWS,
                "monthlyStrategyUserNotes": {"6": "July strategy: terrace open"},
                "dailyMeta": {
                    "memos": {
                        "memo_store": {
                            "2025-07-01": "Tasting menu",
                            "2025-07-10": "Festival set",
                        },
                        "memo_area": {"2025-07-01": "Street market"},
                    },
                    "weather": {"2025-07-01": "sunny", "2025-07-10": "rain"},
                    "flags": {},
                },
            },
            "2024": {
                "year": 2024,
                "status": "closed",
                "plan": {"targetSales": 400000, "monthlyHlWeights": [100] * 12},
                "mepMemoRows": MEMO_ROWS,
                "dailyMeta": {
                    "memos": {"memo_store": {"2024-07-01": "Quiet month"}},
                    "weather": {"2024-07-01": "cloudy"},
                    "flags": {},
                },
            },
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    store = seed_store()
    page.add_init_script(
        """
        window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);
        """
        % (json.dumps(json.dumps(store)),)
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function'",
        timeout=20000,
    )
    # expose build via evaluate of internal - it's not on window.
    # Instead read DOM after render.
    result = page.evaluate(
        """() => {
          const paneSummary = document.getElementById('insight-pane-summary');
          const paneAnalyze = document.getElementById('insight-pane-analyze');
          const paneGraph = document.getElementById('insight-pane-graph');
          if (paneSummary) paneSummary.hidden = true;
          if (paneAnalyze) paneAnalyze.hidden = false;
          if (paneGraph) paneGraph.hidden = true;
          window.renderInsightTwDiffs('2026-07-14');
          const best = document.querySelector(
            '#insight-jump-analyze-monthly [data-insight-month-key="best"]'
          );
          const worst = document.querySelector(
            '#insight-jump-analyze-monthly [data-insight-month-key="worst"]'
          );
          function pop(group) {
            if (!group) return null;
            const title = (group.querySelector(
              '.insight-historical-insight-access__popover-title'
            ) || {}).textContent;
            const items = Array.from(
              group.querySelectorAll('.insight-historical-insight-access__popover-item')
            ).map((el) => el.textContent.trim());
            return { title: (title || '').trim(), items };
          }
          return { best: pop(best), worst: pop(worst) };
        }"""
    )
    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} {result}")
    best = result.get("best") or {}
    worst = result.get("worst") or {}
    best_items = best.get("items") or []
    worst_items = worst.get("items") or []
    joined_best = " | ".join(best_items)
    joined_worst = " | ".join(worst_items)

    if any("Memo not linked yet" in x for x in best_items + worst_items):
        problems.append(f"{url}: still Memo not linked yet")
    if best.get("title") != "2025/07":
        problems.append(f"{url}: best title want 2025/07 got {best.get('title')}")
    if worst.get("title") != "2024/07":
        problems.append(f"{url}: worst title want 2024/07 got {worst.get('title')}")
    if "Tasting menu" not in joined_best and "Festival set" not in joined_best:
        problems.append(f"{url}: best popover missing store memos: {best_items}")
    if "terrace open" not in joined_best and "戦略" not in joined_best and "User Note" not in joined_best:
        # strategy note should appear
        if "July strategy" not in joined_best and "terrace" not in joined_best:
            problems.append(f"{url}: best missing strategy note: {best_items}")
    if "Quiet month" not in joined_worst:
        problems.append(f"{url}: worst missing Quiet month: {worst_items}")
    return problems


def main() -> int:
    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
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

#!/usr/bin/env python3
"""検証: Analyze Dual Insight（Today / Last Year DOW）が MEP メモを読む."""

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
    {"id": "memo_store", "labelJa": "店舗イベント", "labelEn": "Store Event"},
    {"id": "memo_area", "labelJa": "エリア", "labelEn": "Area Event"},
    {"id": "memo_social", "labelJa": "SNS", "labelEn": "Social Media"},
    {"id": "memo_marketing", "labelJa": "マーケ", "labelEn": "Marketing"},
    {"id": "memo_promo", "labelJa": "プロモ", "labelEn": "Promo Conversion"},
    {"id": "memo_reservation", "labelJa": "予約", "labelEn": "Reservation"},
]


def seed_store() -> dict:
    # 2026-07-14 = Tue → same weekday 1y ≈ 2025-07-15
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {
            "dailySales": {"2026-07-14": 10000, "2025-07-15": 8000},
            "businessDays": {"2026-07-14": True, "2025-07-15": True},
        },
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {},
                "mepMemoRows": MEMO_ROWS,
                "dailyMeta": {
                    "memos": {
                        "memo_store": {"2026-07-14": "Tasting menu"},
                        "memo_area": {"2026-07-14": ""},
                        "memo_social": {"2026-07-14": "TikTok live"},
                        "memo_marketing": {"2026-07-14": "LINE"},
                        "memo_promo": {"2026-07-14": "Flyer"},
                        "memo_reservation": {"2026-07-14": "12 Group / 80 customers"},
                    },
                    "flags": {"2026-07-14": True},
                    "weather": {"2026-07-14": "sunny"},
                },
            },
            "2025": {
                "year": 2025,
                "status": "closed",
                "plan": {"targetSales": 500000, "monthlyHlWeights": [100] * 12},
                "dailyExpenses": {},
                "mepMemoRows": MEMO_ROWS,
                "dailyMeta": {
                    "memos": {
                        "memo_store": {"2025-07-15": "None special"},
                        "memo_area": {"2025-07-15": "Street market"},
                        "memo_social": {"2025-07-15": "IG Reels"},
                        "memo_marketing": {"2025-07-15": "X"},
                        "memo_promo": {"2025-07-15": "LINE only"},
                        "memo_reservation": {"2025-07-15": "8 Group / 52 customers"},
                    },
                    "flags": {"2025-07-15": True},
                    "weather": {"2025-07-15": "cloudy"},
                },
            },
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.add_init_script(
        "window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);"
        % json.dumps(json.dumps(seed_store()))
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "typeof window.__sameWeekdayIso === 'function' && "
        "window.KpiYearStore && typeof window.KpiYearStore.loadMepYearPayload === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const ly = window.__sameWeekdayIso(iso, 1);
          window.renderInsightTwDiffs(iso);
          const block = document.querySelector(
            '#insight-jump-analyze-daily .insight-analyze-dual-insight'
          );
          function col(sel) {
            const c = block && block.querySelector(sel);
            if (!c) return null;
            return Array.from(c.querySelectorAll('.insight-analyze-dual-insight__row dd')).map(
              (dd) => dd.textContent.trim()
            );
          }
          return {
            lyIso: ly,
            today: col('.insight-analyze-dual-insight__col--today'),
            lastYear: col('.insight-analyze-dual-insight__col--last-year'),
          };
        }"""
    )
    today = result.get("today") or []
    ly = result.get("lastYear") or []
    # weather, store, area, social, marketing, promo, reservation
    if not today or today[0] not in ("Sunny", "晴れ"):
        problems.append(f"{url}: today weather={today[:1]}")
    if len(today) < 7 or today[1] != "Tasting menu":
        problems.append(f"{url}: today store={today[1] if len(today) > 1 else None}")
    if len(today) < 7 or today[3] != "TikTok live":
        problems.append(f"{url}: today social={today[3] if len(today) > 3 else None}")
    if today and today[0] == "Fine":
        problems.append(f"{url}: still mock Fine")
    if not ly or ly[0] not in ("Cloudy", "曇り"):
        problems.append(f"{url}: ly weather={ly[:1]} lyIso={result.get('lyIso')}")
    if len(ly) < 7 or ly[2] != "Street market":
        problems.append(f"{url}: ly area={ly[2] if len(ly) > 2 else None}")

    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} lyIso={result.get('lyIso')} today={today} lastYear={ly}")
    return problems


def main() -> int:
    import os

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

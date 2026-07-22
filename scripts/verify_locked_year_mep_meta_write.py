#!/usr/bin/env python3
"""検証: locked 過去年でもメモ/天気は bulkPersistMepYear で保存できる."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "en/app/monthly/edit/index.html"
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def seed() -> dict:
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {
            "dailySales": {"2025-04-01": 3012, "2026-01-15": 1000},
            "businessDays": {},
        },
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
            },
            "2025": {
                "year": 2025,
                "status": "locked",
                "lockedAt": "2026-01-01T00:00:00.000Z",
                "plan": {"targetSales": 500000, "monthlyHlWeights": [100] * 12},
                "mepMemoRows": [
                    {"id": "memo_store", "labelJa": "店舗イベント", "labelEn": "Store Event"}
                ],
                "dailyMeta": {"memos": {}, "weather": {}, "flags": {}},
                "dailyExpenses": {},
            },
        },
    }


def main() -> int:
    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page()
        page.add_init_script(
            "window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);"
            % json.dumps(json.dumps(seed()))
        )
        page.goto(PAGE.as_uri() + "?year=2026", wait_until="load")
        page.wait_for_function(
            "() => window.KpiYearStore && typeof KpiYearStore.bulkPersistMepYear === 'function'",
            timeout=20000,
        )
        result = page.evaluate(
            """() => {
              const K = window.KpiYearStore;
              const okMeta = K.canWriteMepMetaYear(2025);
              const okFull = K.canWriteMepYear(2025);
              const wrote = K.bulkPersistMepYear(
                2025,
                {
                  dailyMeta: {
                    memos: { memo_store: { '2025-04-01': 'TEST 0722' } },
                    weather: { '2025-04-01': 'sunny' },
                    flags: { '2025-04-01': true },
                  },
                  dailyExpenses: { exp_rent: { '2025-04-01': 999 } },
                },
                { source: 'test-locked-meta' }
              );
              const payload = K.loadMepYearPayload(2025);
              return {
                okMeta,
                okFull,
                wrote,
                memo: payload && payload.dailyMeta && payload.dailyMeta.memos &&
                  payload.dailyMeta.memos.memo_store &&
                  payload.dailyMeta.memos.memo_store['2025-04-01'],
                weather: payload && payload.dailyMeta && payload.dailyMeta.weather &&
                  payload.dailyMeta.weather['2025-04-01'],
                expense:
                  payload &&
                  payload.dailyExpenses &&
                  payload.dailyExpenses.exp_rent &&
                  payload.dailyExpenses.exp_rent['2025-04-01'],
              };
            }"""
        )
        browser.close()
    print(result)
    problems = []
    if not result.get("okMeta"):
        problems.append("canWriteMepMetaYear(2025) false")
    if result.get("okFull"):
        problems.append("canWriteMepYear(2025) should be false when locked")
    if not result.get("wrote"):
        problems.append("bulkPersist returned false")
    if result.get("memo") != "TEST 0722":
        problems.append(f"memo not saved: {result.get('memo')}")
    if result.get("weather") != "sunny":
        problems.append(f"weather not saved: {result.get('weather')}")
    if result.get("expense") == 999:
        problems.append("expense should stay blocked on locked year")
    if problems:
        print("FAIL:")
        for pr in problems:
            print(" ", pr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

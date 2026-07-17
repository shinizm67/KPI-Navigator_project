#!/usr/bin/env python3
"""検証: PL 営業日数行 — kpiYearStore.timeline を真実源に Annual/MEP と同一判定.

判定ルール（Annual/Insight/MEP と同一）:
  1. timeline.businessDays[iso] が明示されていれば その真偽。
  2. なければ timeline.dailySales[iso] === 0 は休業（>0 は営業）。
  3. どちらもなければ 土日は既定休、平日は既定営業。
"""

from __future__ import annotations

import calendar
import re
import sys
from datetime import date
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
STORE_KEY = "kpiNavigator.kpiYearStore"

# 明示の営業日オーバーライド:
#   07-04(土)を営業に、07-06(月)を休業に。
BUSINESS_DAYS = {
    f"{YEAR}-07-04": True,
    f"{YEAR}-07-06": False,
}
# 日次売上: 07-07(火)=0 は休業、07-11(土)=5000 は営業、08-03 は通常。
DAILY_SALES = {
    f"{YEAR}-07-07": 0,
    f"{YEAR}-07-11": 5000,
    f"{YEAR}-08-03": 200000,
}


def store_seed() -> dict:
    return {
        "meta": {"schemaVersion": 4, "operatingYear": YEAR, "legacyMigrated": True},
        "timeline": {
            "dailySales": dict(DAILY_SALES),
            "businessDays": dict(BUSINESS_DAYS),
        },
        "years": {
            str(YEAR): {
                "year": YEAR,
                "status": "open",
                "plan": {"targetSales": 600000},
                "dailyExpenses": {},
                "dailyIncome": {},
                "dailyMeta": {"memos": {}, "flags": {}, "weather": {}},
            }
        },
    }


def _is_biz(y: int, m0: int, day: int, bmap: dict, smap: dict) -> bool:
    d = date(y, m0 + 1, day)
    is_weekend = d.weekday() in (5, 6)  # Sat=5, Sun=6
    iso = f"{y}-{m0 + 1:02d}-{day:02d}"
    if iso in bmap:
        return bool(bmap[iso])
    if iso in smap:
        try:
            n = float(smap[iso])
        except (TypeError, ValueError):
            return not is_weekend
        if n != n:  # NaN
            return not is_weekend
        return n != 0
    return not is_weekend


def expected_biz_days(y: int, m0: int, bmap: dict, smap: dict) -> int:
    dim = calendar.monthrange(y, m0 + 1)[1]
    return sum(1 for day in range(1, dim + 1) if _is_biz(y, m0, day, bmap, smap))


def seed(page, store: dict) -> None:
    page.evaluate(
        """({ store, key }) => {
          localStorage.clear();
          localStorage.setItem(key, JSON.stringify(store));
        }""",
        {"store": store, "key": STORE_KEY},
    )


def bizdays_cell(page, m0: int):
    txt = page.evaluate(
        """(m) => {
          const cell = document.querySelector('[data-pl-bizdays-month="' + m + '"]');
          if (!cell) return null;
          const span = cell.querySelector('.pl-span-cell__text, .pl-amt-cell__text');
          return span ? span.textContent : null;
        }""",
        m0,
    )
    if txt is None:
        return "MISSING"
    digits = re.sub(r"[^0-9]", "", txt.strip())
    return int(digits) if digits else None


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    url = f"{url}{'&' if '?' in url else '?'}year={YEAR}"

    page.goto(url, wait_until="load")
    seed(page, store_seed())
    page.reload(wait_until="load")
    page.wait_for_selector('[data-pl-bizdays-month="1"]', timeout=15000)
    page.wait_for_function(
        """() => {
          const c = document.querySelector('[data-pl-bizdays-month="1"] .pl-span-cell__text');
          return c && /[0-9]/.test(c.textContent || '');
        }""",
        timeout=15000,
    )

    bmap = dict(BUSINESS_DAYS)
    smap = dict(DAILY_SALES)

    # 全12ヶ月をルール一致で検証。
    for m0 in range(12):
        want = expected_biz_days(YEAR, m0, bmap, smap)
        got = bizdays_cell(page, m0)
        if got != want:
            problems.append(f"month {m0 + 1}: got {got} want {want}")

    # 「暦日そのまま」ではないこと（=土日既定休が効いている）を明示確認。
    # 2月(m0=1)はオーバーライドなし → 平日のみ、暦日数(28/29)より小さいはず。
    feb_days = calendar.monthrange(YEAR, 2)[1]
    feb_got = bizdays_cell(page, 1)
    if isinstance(feb_got, int) and feb_got >= feb_days:
        problems.append(f"Feb should exclude weekends: got {feb_got} >= calendar {feb_days}")

    # ライブ更新: businessDay を変更 → kpi:businessDayChanged で再同期。
    page.evaluate(
        """({ key }) => {
          const store = JSON.parse(localStorage.getItem(key));
          // 07-13(月)を休業に切替。
          store.timeline.businessDays['2026-07-13'] = false;
          localStorage.setItem(key, JSON.stringify(store));
          document.dispatchEvent(new CustomEvent('kpi:businessDayChanged', { detail: { year: 2026 } }));
        }""",
        {"key": STORE_KEY},
    )
    bmap2 = dict(bmap)
    bmap2[f"{YEAR}-07-13"] = False
    want_july2 = expected_biz_days(YEAR, 6, bmap2, smap)
    got_july2 = bizdays_cell(page, 6)
    if got_july2 != want_july2:
        problems.append(
            f"after businessDayChanged July: got {got_july2} want {want_july2}"
        )

    # ライブ更新: dailySales=0 で休業反映（kpi:dailySalesChanged）。
    page.evaluate(
        """({ key }) => {
          const store = JSON.parse(localStorage.getItem(key));
          store.timeline.dailySales['2026-08-04'] = 0; // 08-04(火)を休業
          localStorage.setItem(key, JSON.stringify(store));
          document.dispatchEvent(new CustomEvent('kpi:dailySalesChanged', { detail: {} }));
        }""",
        {"key": STORE_KEY},
    )
    smap2 = dict(smap)
    smap2[f"{YEAR}-08-04"] = 0
    want_aug2 = expected_biz_days(YEAR, 7, bmap, smap2)
    got_aug2 = bizdays_cell(page, 7)
    if got_aug2 != want_aug2:
        problems.append(f"after dailySalesChanged Aug: got {got_aug2} want {want_aug2}")

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

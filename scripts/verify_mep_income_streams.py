#!/usr/bin/env python3
"""検証(Phase 2b): MEP の Sales A/B 日次入力 → dailyIncome へ保存(独立フック).

- MEP のグリッドで sales_a / sales_b の money-input に入力し、確定(Confirm)後に
  years.{Y}.dailyIncome[streamId][iso] へ保存されることを確認。
- 収入は総売上にも合算されるため timeline.dailySales[iso] にも反映される(不変条件)。
- 値を空にして確定すると dailyIncome から当該エントリが削除される(0削除)。
- 二重注入の MEP-STORE ブロックには触れない実装であることの間接確認(全経路が
  persistMepToYearStore→kpi:mepDataChanged 経由でフックされる)。
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)

YEAR = 2026
STORE_KEY = "kpiNavigator.kpiYearStore"
ISO_A = f"{YEAR}-07-07"  # Tue (weekday → open)
ISO_B = f"{YEAR}-07-08"  # Wed (weekday → open)
VAL_A = 30000
VAL_B = 15000


def store_seed() -> dict:
    return {
        "meta": {"schemaVersion": 4, "operatingYear": YEAR, "legacyMigrated": True},
        "timeline": {
            "dailySales": {},
            # 週末揺れ回避のため対象日を明示的に営業日にしておく
            "businessDays": {ISO_A: True, ISO_B: True},
        },
        "years": {
            str(YEAR): {
                "year": YEAR,
                "status": "open",
                "plan": {"targetSales": 600000},
                "dailyExpenses": {},
                "dailyIncome": {},
                "dailyMeta": {"memos": {}, "flags": {}, "weather": {}},
            },
        },
    }


def seed(page) -> None:
    page.evaluate(
        """({ store, key }) => {
          localStorage.clear();
          localStorage.setItem(key, JSON.stringify(store));
        }""",
        {"store": store_seed(), "key": STORE_KEY},
    )


def set_money(page, row_id: str, iso: str, value) -> bool:
    """money-input に値を設定して change を発火(buildGrid が再描画するので都度取得)。"""
    return page.evaluate(
        """({ rowId, iso, value }) => {
          const sel = 'input[data-action="money-input"][data-row-id="' + rowId +
            '"][data-iso="' + iso + '"]';
          const el = document.querySelector(sel);
          if (!el) return false;
          el.value = value;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        }""",
        {"rowId": row_id, "iso": iso, "value": value},
    )


def read_store(page) -> dict:
    return page.evaluate(
        "({ key }) => JSON.parse(localStorage.getItem(key))", {"key": STORE_KEY}
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    url = f"{url}?year={YEAR}&month=7"

    page.goto(url, wait_until="load")
    seed(page)
    page.reload(wait_until="load")
    page.wait_for_function(
        "() => window.KpiYearStore && typeof KpiYearStore.bulkPersistMepYear === 'function'",
        timeout=15000,
    )
    # MEP から売上/収入を入力できる状態にする(入力パス=mep + 編集リース保有)。
    page.evaluate(
        """() => {
          KpiYearStore.acquireEditLease('daily-sales', { source: 'test' });
          KpiYearStore.setDailySalesInputPath('mep');
        }"""
    )
    page.wait_for_timeout(200)
    # グリッド(sales_a の入力セル)が描画されるまで待つ
    try:
        page.wait_for_selector(
            f'input[data-action="money-input"][data-row-id="sales_a"][data-iso="{ISO_A}"]',
            timeout=15000,
        )
    except Exception as e:  # noqa: BLE001
        return [f"sales_a input not rendered: {e}"]

    # --- 1入力→確定→検証(実利用に近い流れ) ---
    # (1) Sales A を入力して確定
    if not set_money(page, "sales_a", ISO_A, VAL_A):
        return ["failed to set sales_a input"]
    page.click("#monthly-edit-float-confirm")
    page.wait_for_timeout(300)
    store = read_store(page)
    di = ((store.get("years") or {}).get(str(YEAR)) or {}).get("dailyIncome") or {}
    ds = (store.get("timeline") or {}).get("dailySales") or {}
    if (di.get("sales_a") or {}).get(ISO_A) != VAL_A:
        problems.append(f"dailyIncome.sales_a[{ISO_A}] = {(di.get('sales_a') or {}).get(ISO_A)} != {VAL_A}")
    # 収入のみの日: 総売上 = A（店舗0）。再確定しても増えないこと（二重計上回帰）。
    if ds.get(ISO_A) != VAL_A:
        problems.append(f"timeline.dailySales[{ISO_A}] = {ds.get(ISO_A)} != {VAL_A}")
    page.click("#monthly-edit-float-confirm")
    page.wait_for_timeout(300)
    store_r = read_store(page)
    ds_r = (store_r.get("timeline") or {}).get("dailySales") or {}
    if ds_r.get(ISO_A) != VAL_A:
        problems.append(
            f"second Confirm must not inflate dailySales[{ISO_A}]: {ds_r.get(ISO_A)} != {VAL_A}"
        )

    # (2) Sales B を入力して確定 — A は不変
    if not set_money(page, "sales_b", ISO_B, VAL_B):
        return problems + ["failed to set sales_b input"]
    page.click("#monthly-edit-float-confirm")
    page.wait_for_timeout(300)
    store = read_store(page)
    di = ((store.get("years") or {}).get(str(YEAR)) or {}).get("dailyIncome") or {}
    ds = (store.get("timeline") or {}).get("dailySales") or {}
    if (di.get("sales_b") or {}).get(ISO_B) != VAL_B:
        problems.append(f"dailyIncome.sales_b[{ISO_B}] = {(di.get('sales_b') or {}).get(ISO_B)} != {VAL_B}")
    if (di.get("sales_a") or {}).get(ISO_A) != VAL_A:
        problems.append(f"dailyIncome.sales_a[{ISO_A}] changed unexpectedly = {(di.get('sales_a') or {}).get(ISO_A)}")
    if ds.get(ISO_B) != VAL_B:
        problems.append(f"timeline.dailySales[{ISO_B}] = {ds.get(ISO_B)} != {VAL_B}")
    if ds.get(ISO_A) != VAL_A:
        problems.append(f"after sales_b confirm dailySales[{ISO_A}] = {ds.get(ISO_A)} != {VAL_A}")
    # (3) Sales A を空にして確定 → dailyIncome から消える(0削除)。B は残る
    if not set_money(page, "sales_a", ISO_A, ""):
        problems.append("failed to clear sales_a input")
    else:
        page.click("#monthly-edit-float-confirm")
        page.wait_for_timeout(300)
        store2 = read_store(page)
        di2 = ((store2.get("years") or {}).get(str(YEAR)) or {}).get("dailyIncome") or {}
        if ISO_A in (di2.get("sales_a") or {}):
            problems.append(f"cleared sales_a[{ISO_A}] should be removed from dailyIncome")
        if (di2.get("sales_b") or {}).get(ISO_B) != VAL_B:
            problems.append("clearing sales_a must not affect sales_b")

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

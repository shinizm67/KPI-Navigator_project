#!/usr/bin/env python3
"""検証: 支出カタログの入力元デフォルト（FL 方針）.

- 新規カタログ: 食材/ドリンク/アルバイト = daily、備品/雑費/光熱費など = monthly
- schema v6→v7 移行: 旧デフォルトのままの行だけ新デフォルトへ
"""

from __future__ import annotations

import sys
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
CATALOG_KEY = "kpiNavigator.plLineCatalog"

EXPECT_DAILY = ("exp_food_cost", "exp_drink_cost", "exp_variable_labor")
EXPECT_MONTHLY = (
    "exp_supplies",
    "exp_misc",
    "exp_electric",
    "exp_gas",
    "exp_water",
    "exp_rent",
)


def styles_map(page) -> dict:
    return page.evaluate(
        """({ key }) => {
          const raw = localStorage.getItem(key);
          if (!raw) return {};
          const lines = JSON.parse(raw).lines || [];
          const out = {};
          lines.forEach((l) => {
            if (!l || !l.lineId) return;
            out[l.lineId] = l.resolvedInputStyle || l.inputStyle || null;
          });
          return out;
        }""",
        {"key": CATALOG_KEY},
    )


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.goto(f"{url}?year={YEAR}", wait_until="load")

    # A) fresh catalog
    page.evaluate("() => localStorage.clear()")
    page.reload(wait_until="load")
    page.wait_for_selector('tr[data-line-id="exp_food_cost"]', timeout=15000)
    page.wait_for_timeout(100)
    styles = styles_map(page)
    for lid in EXPECT_DAILY:
        if styles.get(lid) != "daily":
            problems.append(f"fresh {lid} style={styles.get(lid)!r} want daily")
    for lid in EXPECT_MONTHLY:
        if styles.get(lid) != "monthly":
            problems.append(f"fresh {lid} style={styles.get(lid)!r} want monthly")

    # B) migrate v6 catalog that still has old defaults
    page.evaluate(
        """({ key }) => {
          const raw = localStorage.getItem(key);
          const parsed = raw ? JSON.parse(raw) : { lines: [] };
          const lines = parsed.lines || [];
          const byId = {};
          lines.forEach((l) => { byId[l.lineId] = l; });
          // force old defaults
          ['exp_supplies', 'exp_misc'].forEach((id) => {
            if (!byId[id]) return;
            byId[id].inputStyle = 'daily';
            byId[id].resolvedInputStyle = 'daily';
          });
          if (byId.exp_variable_labor) {
            byId.exp_variable_labor.inputStyle = 'monthly';
            byId.exp_variable_labor.resolvedInputStyle = 'monthly';
          }
          // user override should be preserved
          if (byId.exp_food_cost) {
            byId.exp_food_cost.inputStyle = 'monthly';
            byId.exp_food_cost.resolvedInputStyle = 'monthly';
          }
          localStorage.setItem(key, JSON.stringify({
            lines,
            schemaVersion: 6,
            updatedAt: Date.now(),
          }));
        }""",
        {"key": CATALOG_KEY},
    )
    page.reload(wait_until="load")
    page.wait_for_selector('tr[data-line-id="exp_food_cost"]', timeout=15000)
    page.wait_for_timeout(100)
    styles2 = styles_map(page)
    if styles2.get("exp_supplies") != "monthly":
        problems.append(f"migrate supplies {styles2.get('exp_supplies')!r} want monthly")
    if styles2.get("exp_misc") != "monthly":
        problems.append(f"migrate misc {styles2.get('exp_misc')!r} want monthly")
    if styles2.get("exp_variable_labor") != "daily":
        problems.append(
            f"migrate variable_labor {styles2.get('exp_variable_labor')!r} want daily"
        )
    if styles2.get("exp_food_cost") != "monthly":
        problems.append(
            f"user override food_cost should stay monthly, got {styles2.get('exp_food_cost')!r}"
        )

    ver = page.evaluate(
        """({ key }) => {
          const raw = localStorage.getItem(key);
          return raw ? JSON.parse(raw).schemaVersion : null;
        }""",
        {"key": CATALOG_KEY},
    )
    if ver != 7:
        problems.append(f"schemaVersion after migrate {ver!r} want 7")

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

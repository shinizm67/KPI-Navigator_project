# -*- coding: utf-8 -*-
"""BR-POST-HORIZONTAL-WORKBOOK-PARSER — generic detector + Barca 2025-11 fixture."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from daily_sales_import_client import daily_sales_import_js  # noqa: E402

FAILED = 0
PASSED = 0

BARCA = ROOT / "fixtures" / "import" / "horizontal" / "barca_2025_11_data.csv"
GENERIC = ROOT / "fixtures" / "import" / "horizontal" / "generic_lunch_fullday.csv"
VERTICAL_SAMPLE = [
    ["日付", "日次売上", "トータル客数", "トータル組数", "フード売上", "ドリンク売上"],
    ["2026-01-03", "120000", "20", "8", "70000", "50000"],
    ["2026-01-04", "88000", "14", "6", "50000", "38000"],
]


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def node_bin() -> str:
    env = os.environ.get("KPI_TEST_NODE")
    if env and Path(env).is_file():
        return env
    found = shutil.which("node")
    if found:
        return found
    cursor_node = Path.home() / "AppData/Local/Programs/cursor/resources/app/resources/helpers/node.exe"
    if cursor_node.is_file():
        return str(cursor_node)
    raise SystemExit("node not found")


def run_maps(csv_text: str | None, rows: list | None) -> dict:
    payload = {
        "importer": daily_sales_import_js(),
        "csvText": csv_text,
        "rows": rows,
    }
    driver = r"""
const fs = require('fs');
const vm = require('vm');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const ctx = {
  window: null,
  document: {
    documentElement: { getAttribute: () => 'ja' },
    createElement: () => ({ async: true, src: '', onload: null, onerror: null }),
    head: { appendChild() {} },
    body: { appendChild() {} },
    addEventListener() {},
  },
  Date, Number, String, Math, Object, Array, JSON, Error, Promise, console,
  parseInt, parseFloat, isNaN, encodeURIComponent,
};
ctx.window = ctx;
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(payload.importer, ctx);
const api = ctx.__KPI_DAILY_IMPORT;
let rows = payload.rows;
if (payload.csvText) rows = api.parseDelimitedText(payload.csvText);
const layout = api.detectLayout(rows);
let maps = null;
let error = null;
try {
  maps = api.rowsToMaps(rows);
} catch (e) {
  error = e && (e.message || String(e));
}
const out = { layout, error, maps };
process.stdout.write(JSON.stringify(out));
"""
    result = subprocess.run(
        [node_bin(), "-e", driver],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        raise SystemExit("node harness failed")
    return json.loads(result.stdout)


def main() -> int:
    assert_true(BARCA.is_file(), "Barca fixture copied (excel/ original untouched)")
    assert_true("KpiWorkbookLayout" in daily_sales_import_js(), "sales importer embeds shared layout")

    generic_text = GENERIC.read_text(encoding="utf-8")
    g = run_maps(generic_text, None)
    assert_true(g.get("error") is None, "generic horizontal parses: " + str(g.get("error")))
    assert_true(g.get("layout") == "horizontal", "generic detected as horizontal")
    gm = g.get("maps") or {}
    assert_true(gm.get("salesByDate", {}).get("2026-01-01") == 500, "generic day1 full-day sales")
    assert_true(gm.get("totalCustomersByDate", {}).get("2026-01-01") == 5, "generic day1 customers")
    assert_true(gm.get("totalGroupsByDate", {}).get("2026-01-01") == 3, "generic day1 parties")
    assert_true(gm.get("lunchSalesByDate", {}).get("2026-01-01") == 100, "generic day1 lunch")
    assert_true(gm.get("dinnerSalesByDate", {}).get("2026-01-01") == 400, "generic dinner = full - lunch")
    assert_true(gm.get("salesByDate", {}).get("2026-01-02") == 800, "generic day2 sales")

    v = run_maps(None, VERTICAL_SAMPLE)
    assert_true(v.get("error") is None, "vertical sample parses: " + str(v.get("error")))
    assert_true(v.get("layout") == "vertical", "vertical sample stays vertical")
    vm_ = v.get("maps") or {}
    assert_true(vm_.get("salesByDate", {}).get("2026-01-03") == 120000, "vertical sales unchanged")
    assert_true(vm_.get("totalCustomersByDate", {}).get("2026-01-03") == 20, "vertical customers unchanged")
    assert_true(vm_.get("foodByDate", {}).get("2026-01-03") == 70000, "vertical food unchanged")

    barca_text = BARCA.read_text(encoding="utf-8")
    b = run_maps(barca_text, None)
    assert_true(b.get("error") is None, "Barca parses: " + str(b.get("error")))
    assert_true(b.get("layout") == "horizontal", "Barca detected as horizontal")
    bm = b.get("maps") or {}
    sales = bm.get("salesByDate") or {}
    cust = bm.get("totalCustomersByDate") or {}
    parties = bm.get("totalGroupsByDate") or {}
    assert_true(sales.get("2025-11-01") == 60930, "Barca 11/1 sales 60930 got " + str(sales.get("2025-11-01")))
    assert_true(cust.get("2025-11-01") == 13, "Barca 11/1 customers 13 got " + str(cust.get("2025-11-01")))
    assert_true(parties.get("2025-11-01") == 9, "Barca 11/1 parties 9 got " + str(parties.get("2025-11-01")))
    assert_true(sales.get("2025-11-04") == 144600, "Barca 11/4 sales 144600 got " + str(sales.get("2025-11-04")))
    assert_true(cust.get("2025-11-04") == 22, "Barca 11/4 customers 22")
    assert_true(parties.get("2025-11-04") == 5, "Barca 11/4 parties 5")
    food = bm.get("foodByDate") or {}
    drink = bm.get("drinkByDate") or {}
    assert_true(food.get("2025-11-01") == 36880, "Barca 11/1 food 36880 got " + str(food.get("2025-11-01")))
    assert_true(drink.get("2025-11-01") == 24050, "Barca 11/1 drink 24050 got " + str(drink.get("2025-11-01")))
    lunch = bm.get("lunchSalesByDate") or {}
    assert_true(lunch.get("2025-11-01") == 0, "Barca 11/1 lunch sales 0")
    unknown = bm.get("unmatchedMetrics") or []
    expense_labels = {u.get("label") for u in unknown if u.get("kind") == "expense"}
    assert_true("日次食材仕入額" in expense_labels, "Barca food purchase preserved as unmatched expense")
    assert_true(not any("推定" in str(u.get("label") or "") for u in unknown), "estimated rows not mapped as amounts")
    assert_true(bm.get("imported", 0) >= 8, "Barca imported several populated days")
    if "2025-11-02" in sales:
        assert_true(sales.get("2025-11-02") == 0, "Barca 11/2 stays 0 when the sheet writes 0")


    html_needles = [
        ROOT / "app/annual/index.html",
        ROOT / "app/monthly/edit/index.html",
        ROOT / "app/profit/pl/index.html",
    ]
    for path in html_needles:
        text = path.read_text(encoding="utf-8")
        assert_true("kpi-workbook-layout.js?v=20260926-hwb" in text, f"{path.name} loads layout script")

    print(f"PASSED={PASSED} FAILED={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

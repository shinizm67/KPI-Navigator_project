# -*- coding: utf-8 -*-
"""BR-POST-HISTORICAL-IMPORT-CALENDAR-COMPLETION — final business-day contract."""

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
VERTICAL_SAMPLE = [
    ["日付", "日次売上", "トータル客数", "トータル組数", "フード売上", "ドリンク売上"],
    ["2026-01-03", "120000", "20", "8", "70000", "50000"],
    ["2026-01-04", "88000", "14", "6", "50000", "38000"],
]
OPTS = {"operatingYear": 2026, "today": "2026-09-26"}


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


def run_case(case: dict) -> dict:
    payload = {"importer": daily_sales_import_js(), "case": case}
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
const layout = ctx.KpiWorkbookLayout;
const c = payload.case || {};
const out = { error: null };

function persistMerge(existingBiz, existingSales, maps) {
  const biz = Object.assign({}, existingBiz || {});
  const sales = Object.assign({}, existingSales || {});
  Object.keys((maps && maps.salesByDate) || {}).forEach((iso) => {
    const n = Number(maps.salesByDate[iso]);
    sales[iso] = Number.isFinite(n) ? n : 0;
  });
  Object.keys((maps && maps.businessDayByDate) || {}).forEach((iso) => {
    if (Object.prototype.hasOwnProperty.call(maps.businessDayByDate, iso)) {
      biz[iso] = !!maps.businessDayByDate[iso];
    }
  });
  return { biz, sales };
}

try {
  if (c.op === 'completeMaps') {
    const maps = c.maps;
    out.maps = layout.completeHistoricalImport(maps, c.opts || {});
    if (c.existingBiz) {
      out.persisted = persistMerge(c.existingBiz, c.existingSales || {}, out.maps);
    }
  } else if (c.op === 'parseThenComplete') {
    let rows = c.rows;
    if (c.csvText) rows = api.parseDelimitedText(c.csvText);
    out.layout = api.detectLayout(rows);
    out.before = api.rowsToMaps(rows);
    const cloned = JSON.parse(JSON.stringify(out.before));
    out.after = layout.completeHistoricalImport(cloned, c.opts || {});
  } else if (c.op === 'parseOnly') {
    let rows = c.rows;
    if (c.csvText) rows = api.parseDelimitedText(c.csvText);
    out.layout = api.detectLayout(rows);
    out.maps = api.rowsToMaps(rows);
  } else if (c.op === 'lastDay') {
    out.lastDay = layout.lastDayOfMonth(c.y, c.m);
    out.invalid = layout.isoFromYmd(c.y, c.m, c.invalidDay || 0);
  } else if (c.op === 'applyToRowState') {
    const rowState = c.rowState || {};
    api.applyToRowState(rowState, c.maps, c.yearFilter);
    out.rowState = rowState;
  }
} catch (e) {
  out.error = e && (e.message || String(e));
}
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


def biz(maps: dict, iso: str):
    return ((maps or {}).get("businessDayByDate") or {}).get(iso)


def has_biz(maps: dict, iso: str) -> bool:
    return iso in ((maps or {}).get("businessDayByDate") or {})


def main() -> int:
    src = daily_sales_import_js()
    assert_true("completeHistoricalImport" in src, "importer embed includes completion")
    begin = src.split("function beginImport(options)", 1)[-1]
    assert_true("completeHistoricalImport" in begin, "beginImport calls completion")
    assert_true(
        "persistByCsvYear &&" not in begin.split("completeHistoricalImport", 1)[0],
        "BD inference is not entry-point gated",
    )
    assert_true(BARCA.is_file(), "Barca fixture present")

    # 1. sales > 0 → business day
    t1 = run_case({"op": "completeMaps", "opts": OPTS, "maps": {"salesByDate": {"2025-11-01": 60930}}})
    assert_true(biz(t1.get("maps"), "2025-11-01") is True, "1 sales>0 open")

    # 2. sales < 0 → business day
    t2 = run_case({"op": "completeMaps", "opts": OPTS, "maps": {"salesByDate": {"2025-11-08": -1200}}})
    assert_true(biz(t2.get("maps"), "2025-11-08") is True, "2 negative sales still open")

    # 3. customers > 0 → business day
    t3 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS,
            "maps": {"salesByDate": {"2025-11-11": 0}, "totalCustomersByDate": {"2025-11-11": 4}},
        }
    )
    assert_true(biz(t3.get("maps"), "2025-11-11") is True, "3 customers>0 open")

    # 4. parties > 0 → business day
    t4 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS,
            "maps": {"salesByDate": {"2025-11-12": 0}, "totalGroupsByDate": {"2025-11-12": 2}},
        }
    )
    assert_true(biz(t4.get("maps"), "2025-11-12") is True, "4 parties>0 open")

    # 5. expense only → does NOT force business day
    t5 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS,
            "maps": {
                "salesByDate": {"2025-11-10": 0},
                "unmatchedMetrics": [
                    {"iso": "2025-11-10", "label": "仕入", "amount": 18000, "kind": "expense"}
                ],
            },
        }
    )
    assert_true(biz(t5.get("maps"), "2025-11-10") is not True, "5 expense-only does not open")
    assert_true(not has_biz(t5.get("maps"), "2025-11-10"), "5 expense-only omits BD key")

    # 6. no activity + existing business day → preserve
    t6 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS,
            "maps": {"salesByDate": {"2025-11-02": 0}},
            "existingBiz": {"2025-11-02": True},
            "existingSales": {"2025-11-02": 88000},
        }
    )
    assert_true(not has_biz(t6.get("maps"), "2025-11-02"), "6 inference omits BD when no activity")
    assert_true((t6.get("persisted") or {}).get("biz", {}).get("2025-11-02") is True, "6 persist preserves open")
    assert_true((t6.get("persisted") or {}).get("sales", {}).get("2025-11-02") == 0, "6 sales 0 overwrites stale independently")

    # 7. no activity + existing closed day → preserve
    t7 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS,
            "maps": {"salesByDate": {"2025-11-03": 0}},
            "existingBiz": {"2025-11-03": False},
            "existingSales": {"2025-11-03": 120227},
        }
    )
    assert_true(not has_biz(t7.get("maps"), "2025-11-03"), "7 inference omits BD when no activity")
    assert_true((t7.get("persisted") or {}).get("biz", {}).get("2025-11-03") is False, "7 persist preserves closed")
    assert_true((t7.get("persisted") or {}).get("sales", {}).get("2025-11-03") == 0, "7 stale sales cleared independently")

    row_open = run_case(
        {
            "op": "applyToRowState",
            "rowState": {"2025-11-03": {"off": False, "last": "120227"}},
            "maps": {"salesByDate": {"2025-11-03": 0}, "businessDayByDate": {}},
        }
    )
    rs_open = (row_open.get("rowState") or {}).get("2025-11-03") or {}
    assert_true(rs_open.get("off") is False and rs_open.get("last") == "0", "7 grid preserves open, sales last=0")

    row_closed = run_case(
        {
            "op": "applyToRowState",
            "rowState": {"2025-11-03": {"off": True, "last": "120227"}},
            "maps": {"salesByDate": {"2025-11-03": 0}, "businessDayByDate": {}},
        }
    )
    rs_closed = (row_closed.get("rowState") or {}).get("2025-11-03") or {}
    assert_true(rs_closed.get("off") is True and rs_closed.get("last") == "0", "7 grid preserves closed, sales last=0")

    # 8. current-month historical import works
    t8 = run_case(
        {
            "op": "completeMaps",
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
            "maps": {"salesByDate": {"2026-09-25": 44000, "2026-09-26": 100}},
        }
    )
    assert_true(biz(t8.get("maps"), "2026-09-25") is True, "8 current-month yesterday open")
    assert_true(biz(t8.get("maps"), "2026-09-26") is True, "8 current-month today open")

    # 9. past-month current-year import works
    t9 = run_case(
        {
            "op": "completeMaps",
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
            "maps": {"salesByDate": {"2026-08-03": 50000}},
        }
    )
    assert_true(biz(t9.get("maps"), "2026-08-03") is True, "9 past month in operating year open")

    # 10. previous-year import works
    t10 = run_case(
        {
            "op": "completeMaps",
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
            "maps": {"salesByDate": {"2025-11-01": 60930}},
        }
    )
    assert_true(biz(t10.get("maps"), "2025-11-01") is True, "10 previous-year open")

    # 11. future-date settings are not altered
    t11 = run_case(
        {
            "op": "completeMaps",
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
            "maps": {
                "salesByDate": {"2026-10-01": 99999, "2026-09-27": 50},
                "businessDayByDate": {"2026-10-01": True, "2026-09-27": True},
            },
            "existingBiz": {"2026-10-01": False, "2026-09-27": False},
        }
    )
    assert_true(not has_biz(t11.get("maps"), "2026-10-01"), "11 future month BD omitted")
    assert_true(not has_biz(t11.get("maps"), "2026-09-27"), "11 tomorrow BD omitted")
    persisted11 = (t11.get("persisted") or {}).get("biz") or {}
    assert_true(persisted11.get("2026-10-01") is False, "11 future month existing BD preserved")
    assert_true(persisted11.get("2026-09-27") is False, "11 tomorrow existing BD preserved")

    cal = run_case({"op": "lastDay", "y": 2025, "m": 11, "invalidDay": 31})
    assert_true(cal.get("lastDay") == 30, "calendar Nov has 30 days")
    assert_true(cal.get("invalid") is None, "calendar Nov 31 rejected")
    cal_leap = run_case({"op": "lastDay", "y": 2024, "m": 2, "invalidDay": 30})
    assert_true(cal_leap.get("lastDay") == 29, "calendar leap Feb 29")
    cal_feb = run_case({"op": "lastDay", "y": 2025, "m": 2, "invalidDay": 29})
    assert_true(cal_feb.get("lastDay") == 28 and cal_feb.get("invalid") is None, "calendar non-leap Feb")

    # 12. Vertical Import regression
    t12 = run_case({"op": "parseThenComplete", "rows": VERTICAL_SAMPLE, "opts": OPTS})
    assert_true(t12.get("layout") != "horizontal", "12 vertical not misdetected")
    assert_true((t12.get("before") or {}).get("imported") == 2, "12 vertical parse 2 days")
    assert_true((t12.get("before") or {}).get("salesByDate", {}).get("2026-01-03") == 120000, "12 vertical sales intact")
    after12 = t12.get("after") or {}
    assert_true(after12.get("imported") == 31, "12 vertical current-year Jan fills calendar axis")
    assert_true((after12.get("salesByDate") or {}).get("2026-01-03") == 120000, "12 vertical sales intact after fill")
    assert_true(biz(after12, "2026-01-03") is True, "12 Jan 3 inferred open")
    assert_true(biz(after12, "2026-01-02") is not True, "12 missing Jan 2 not forced open")
    assert_true(not has_biz(after12, "2026-01-02"), "12 missing Jan 2 BD omitted")

    t12past = run_case(
        {
            "op": "parseThenComplete",
            "rows": [["日付", "日次売上", "トータル客数", "トータル組数"], ["2025-03-02", "12345", "4", "2"]],
            "opts": OPTS,
        }
    )
    assert_true((t12past.get("before") or {}).get("imported") == 1, "12 past vertical parse 1 day")
    assert_true((t12past.get("after") or {}).get("imported") == 31, "12 past vertical fills March")
    assert_true((t12past.get("after") or {}).get("salesByDate", {}).get("2025-03-02") == 12345, "12 past vertical sales kept")
    assert_true(biz(t12past.get("after"), "2025-03-02") is True, "12 past vertical inferred open")
    assert_true(not has_biz(t12past.get("after"), "2025-03-01"), "12 Mar 1 BD omitted")

    # 13. Horizontal Import regression + Barca
    t13 = run_case({"op": "parseThenComplete", "csvText": BARCA.read_text(encoding="utf-8"), "opts": OPTS})
    before13 = t13.get("before") or {}
    after13 = t13.get("after") or {}
    assert_true(t13.get("layout") == "horizontal", "13 Barca still horizontal")
    assert_true(before13.get("salesByDate", {}).get("2025-11-01") == 60930, "13 parse Nov1 sales")
    assert_true(before13.get("imported") == 30, "13 parse 30 real Nov days")
    assert_true(after13.get("imported") == 30, "13 complete keeps 30 days")
    assert_true(biz(after13, "2025-11-01") is True, "Barca 11/1 business day")
    assert_true(biz(after13, "2025-11-04") is True, "Barca 11/4 business day")
    assert_true(biz(after13, "2025-11-02") is not True, "Barca 11/2 not forced open")
    assert_true(biz(after13, "2025-11-03") is not True, "Barca 11/3 not forced open")
    assert_true(not has_biz(after13, "2025-11-02"), "Barca 11/2 BD omitted (preserve existing)")
    assert_true(not has_biz(after13, "2025-11-03"), "Barca 11/3 BD omitted (preserve existing)")
    assert_true((after13.get("salesByDate") or {}).get("2025-11-03") == 0, "Barca 11/3 sales 0 independent of BD")
    assert_true("2025-12-01" not in (after13.get("salesByDate") or {}), "Barca no Dec overflow")

    print(f"PASSED={PASSED} FAILED={FAILED}")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

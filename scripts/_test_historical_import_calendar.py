# -*- coding: utf-8 -*-
"""BR-POST-HISTORICAL-IMPORT-CALENDAR-COMPLETION — 13 required tests + Barca."""

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
OPTS_PAST = {"operatingYear": 2026, "today": "2026-09-26"}


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
    payload = {
        "importer": daily_sales_import_js(),
        "case": case,
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
const layout = ctx.KpiWorkbookLayout;
const c = payload.case || {};
const out = { error: null };

function parseRows(rows) {
  return api.rowsToMaps(rows);
}

try {
  if (c.op === 'completeMaps') {
    const maps = c.maps;
    out.maps = layout.completeHistoricalImport(maps, c.opts || {});
  } else if (c.op === 'parseThenComplete') {
    let rows = c.rows;
    if (c.csvText) rows = api.parseDelimitedText(c.csvText);
    out.layout = api.detectLayout(rows);
    out.before = parseRows(rows);
    const cloned = JSON.parse(JSON.stringify(out.before));
    out.after = layout.completeHistoricalImport(cloned, c.opts || {});
  } else if (c.op === 'parseOnly') {
    let rows = c.rows;
    if (c.csvText) rows = api.parseDelimitedText(c.csvText);
    out.layout = api.detectLayout(rows);
    out.maps = parseRows(rows);
  } else if (c.op === 'lastDay') {
    out.lastDay = layout.lastDayOfMonth(c.y, c.m);
    out.invalid = layout.isoFromYmd(c.y, c.m, c.invalidDay || 0);
  } else if (c.op === 'applyToRowState') {
    const rowState = c.rowState || {};
    api.applyToRowState(rowState, c.maps, c.yearFilter);
    out.rowState = rowState;
  } else if (c.op === 'infer') {
    out.open = layout.inferHistoricalBusinessDay(c.maps, c.iso);
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


def days_of(maps: dict, prefix: str) -> list[str]:
    sales = (maps or {}).get("salesByDate") or {}
    return sorted(k for k in sales if k.startswith(prefix))


def main() -> int:
    src = daily_sales_import_js()
    assert_true("completeHistoricalImport" in src, "importer embed includes calendar completion")
    assert_true("persistByCsvYear" in src and "completeHistoricalImport" in src, "beginImport wires completion")
    assert_true(BARCA.is_file(), "Barca fixture present (excel/ untouched)")

    # 1. 日付あり + 売上 > 0 → 営業日
    t1 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {"salesByDate": {"2025-11-01": 60930}},
        }
    )
    m1 = t1.get("maps") or {}
    assert_true(t1.get("error") is None, "t1 no error")
    assert_true((m1.get("businessDayByDate") or {}).get("2025-11-01") is True, "1 sales>0 open")

    # 2. 日付あり + 全値0 → 店休日
    t2 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {
                "salesByDate": {"2025-11-02": 0},
                "totalCustomersByDate": {"2025-11-02": 0},
                "totalGroupsByDate": {"2025-11-02": 0},
            },
        }
    )
    m2 = t2.get("maps") or {}
    assert_true((m2.get("businessDayByDate") or {}).get("2025-11-02") is False, "2 all-zero closed")
    assert_true((m2.get("salesByDate") or {}).get("2025-11-02") == 0, "2 sales stay 0")

    # 3. 日付あり + 全値空 → 店休日
    t3 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {"salesByDate": {"2025-11-03": None}, "totalCustomersByDate": {}},
        }
    )
    m3 = t3.get("maps") or {}
    assert_true((m3.get("businessDayByDate") or {}).get("2025-11-03") is False, "3 empty closed")
    assert_true((m3.get("salesByDate") or {}).get("2025-11-03") == 0, "3 empty overwritten to 0")

    # 4. 売上0 + 支出 > 0 → 営業日
    t4 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {
                "salesByDate": {"2025-11-10": 0},
                "unmatchedMetrics": [
                    {"iso": "2025-11-10", "label": "仕入", "amount": 18000, "kind": "expense"}
                ],
            },
        }
    )
    m4 = t4.get("maps") or {}
    assert_true((m4.get("businessDayByDate") or {}).get("2025-11-10") is True, "4 expense>0 open")
    assert_true((m4.get("salesByDate") or {}).get("2025-11-10") == 0, "4 sales remain 0")

    # 5. 売上0 + 客数 > 0 → 営業日
    t5 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {"salesByDate": {"2025-11-11": 0}, "totalCustomersByDate": {"2025-11-11": 4}},
        }
    )
    m5 = t5.get("maps") or {}
    assert_true((m5.get("businessDayByDate") or {}).get("2025-11-11") is True, "5 customers>0 open")

    row5 = run_case(
        {
            "op": "applyToRowState",
            "maps": {
                "salesByDate": {"2025-11-11": 0},
                "businessDayByDate": {"2025-11-11": True},
            },
        }
    )
    rs5 = (row5.get("rowState") or {}).get("2025-11-11") or {}
    assert_true(rs5.get("off") is False, "5 grid stays open when biz true and sales 0")
    assert_true(rs5.get("last") == "0", "5 grid last is 0")

    # 6. 欠損日 → 過去月なら店休日補完
    t6 = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {
                "salesByDate": {
                    "2025-11-01": 60930,
                    "2025-11-04": 144600,
                    "2025-11-05": 195550,
                }
            },
        }
    )
    m6 = t6.get("maps") or {}
    nov6 = days_of(m6, "2025-11-")
    biz6 = m6.get("businessDayByDate") or {}
    assert_true(len(nov6) == 30, "6 November filled to 30 days")
    assert_true("2025-11-02" in nov6 and "2025-11-03" in nov6, "6 missing 11/2 and 11/3 filled")
    assert_true(biz6.get("2025-11-01") is True, "6 11/1 open")
    assert_true(biz6.get("2025-11-02") is False, "6 11/2 closed fill")
    assert_true(biz6.get("2025-11-03") is False, "6 11/3 closed fill")
    assert_true(biz6.get("2025-11-04") is True, "6 11/4 open")
    assert_true(biz6.get("2025-11-05") is True, "6 11/5 open")
    assert_true((m6.get("salesByDate") or {}).get("2025-11-03") == 0, "6 filled 11/3 sales 0")
    assert_true("2025-12-01" not in (m6.get("salesByDate") or {}), "6 no Nov overflow into Dec")

    # 7. 30日月
    t7 = run_case({"op": "lastDay", "y": 2025, "m": 4, "invalidDay": 31})
    assert_true(t7.get("lastDay") == 30, "7 April has 30 days")
    assert_true(t7.get("invalid") is None, "7 April 31 rejected")
    t7c = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {"salesByDate": {"2025-04-01": 1}},
        }
    )
    assert_true(len(days_of(t7c.get("maps"), "2025-04-")) == 30, "7 April completed 30")
    assert_true("2025-05-01" not in ((t7c.get("maps") or {}).get("salesByDate") or {}), "7 no roll to May")

    # 8. 31日月
    t8 = run_case({"op": "lastDay", "y": 2025, "m": 1, "invalidDay": 32})
    assert_true(t8.get("lastDay") == 31, "8 January has 31 days")
    t8c = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {"salesByDate": {"2025-01-31": 10}},
        }
    )
    assert_true(len(days_of(t8c.get("maps"), "2025-01-")) == 31, "8 January completed 31")
    assert_true(((t8c.get("maps") or {}).get("businessDayByDate") or {}).get("2025-01-31") is True, "8 Jan 31 open")

    # 9. 通常年2月
    t9 = run_case({"op": "lastDay", "y": 2025, "m": 2, "invalidDay": 29})
    assert_true(t9.get("lastDay") == 28, "9 non-leap Feb 28")
    assert_true(t9.get("invalid") is None, "9 2025-02-29 rejected")
    t9c = run_case(
        {
            "op": "completeMaps",
            "opts": OPTS_PAST,
            "maps": {"salesByDate": {"2025-02-01": 1}},
        }
    )
    feb9 = (t9c.get("maps") or {}).get("salesByDate") or {}
    assert_true(len(days_of(t9c.get("maps"), "2025-02-")) == 28, "9 Feb 2025 completed 28")
    assert_true("2025-02-29" not in feb9 and "2025-03-01" not in feb9, "9 no leap overflow")

    # 10. 閏年2月
    t10 = run_case({"op": "lastDay", "y": 2024, "m": 2, "invalidDay": 30})
    assert_true(t10.get("lastDay") == 29, "10 leap Feb 29")
    t10c = run_case(
        {
            "op": "completeMaps",
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
            "maps": {"salesByDate": {"2024-02-29": 290}},
        }
    )
    assert_true(len(days_of(t10c.get("maps"), "2024-02-")) == 29, "10 Feb 2024 completed 29")
    assert_true(((t10c.get("maps") or {}).get("businessDayByDate") or {}).get("2024-02-29") is True, "10 leap 29 open")
    assert_true("2024-03-01" not in ((t10c.get("maps") or {}).get("salesByDate") or {}), "10 no roll to March")

    # 11. 現在月 / 未来月にはこの補完を適用しない
    t11now = run_case(
        {
            "op": "completeMaps",
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
            "maps": {"salesByDate": {"2026-09-01": 100, "2026-09-03": 200}},
        }
    )
    sep = (t11now.get("maps") or {}).get("salesByDate") or {}
    assert_true(sorted(sep.keys()) == ["2026-09-01", "2026-09-03"], "11 current month not filled")
    assert_true("2026-09-02" not in sep, "11 current-month gap left missing")

    t11fut = run_case(
        {
            "op": "completeMaps",
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
            "maps": {"salesByDate": {"2026-10-01": 50}},
        }
    )
    octm = (t11fut.get("maps") or {}).get("salesByDate") or {}
    assert_true(list(octm.keys()) == ["2026-10-01"], "11 future month not filled")

    t11oy = run_case(
        {
            "op": "completeMaps",
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
            "maps": {"salesByDate": {"2026-01-02": 70}},
        }
    )
    jan = (t11oy.get("maps") or {}).get("salesByDate") or {}
    assert_true(list(jan.keys()) == ["2026-01-02"], "11 operating-year month not filled")

    # 12. Vertical Import regression (parser unchanged; completion is post-parse)
    t12 = run_case({"op": "parseOnly", "rows": VERTICAL_SAMPLE})
    v12 = t12.get("maps") or {}
    assert_true(t12.get("error") is None, "12 vertical parse ok")
    assert_true(t12.get("layout") != "horizontal", "12 vertical not misdetected")
    assert_true(v12.get("imported") == 2, "12 vertical imported 2 days pre-completion")
    assert_true(v12.get("salesByDate", {}).get("2026-01-03") == 120000, "12 vertical sales intact")
    t12c = run_case(
        {
            "op": "parseThenComplete",
            "rows": VERTICAL_SAMPLE,
            "opts": {"operatingYear": 2026, "today": "2026-09-26"},
        }
    )
    assert_true((t12c.get("after") or {}).get("imported") == 2, "12 operating-year vertical not completed")

    t12past = run_case(
        {
            "op": "parseThenComplete",
            "rows": [
                ["日付", "日次売上", "トータル客数", "トータル組数"],
                ["2025-03-02", "12345", "4", "2"],
            ],
            "opts": OPTS_PAST,
        }
    )
    before12 = t12past.get("before") or {}
    after12 = t12past.get("after") or {}
    assert_true(before12.get("imported") == 1, "12 past vertical parse still 1 day")
    assert_true(after12.get("imported") == 31, "12 past vertical completed to 31")
    assert_true((after12.get("salesByDate") or {}).get("2025-03-02") == 12345, "12 past vertical sales kept")
    assert_true((after12.get("businessDayByDate") or {}).get("2025-03-01") is False, "12 Mar 1 filled closed")

    # 13. Horizontal Import regression
    t13 = run_case({"op": "parseThenComplete", "csvText": BARCA.read_text(encoding="utf-8"), "opts": OPTS_PAST})
    before13 = t13.get("before") or {}
    after13 = t13.get("after") or {}
    assert_true(t13.get("layout") == "horizontal", "13 Barca still horizontal")
    assert_true(before13.get("salesByDate", {}).get("2025-11-01") == 60930, "13 parse Nov1 sales")
    assert_true(before13.get("imported") == 30, "13 parse already 30 calendar days")
    assert_true(after13.get("imported") == 30, "13 complete keeps 30 real Nov days")
    biz13 = after13.get("businessDayByDate") or {}
    sales13 = after13.get("salesByDate") or {}
    assert_true(biz13.get("2025-11-01") is True, "Barca 11/1 open")
    assert_true(biz13.get("2025-11-02") is False, "Barca 11/2 closed")
    assert_true(biz13.get("2025-11-03") is False, "Barca 11/3 closed")
    assert_true(biz13.get("2025-11-04") is True, "Barca 11/4 open")
    assert_true(sales13.get("2025-11-03") == 0, "Barca 11/3 sales 0 overwrites stale")
    assert_true("2025-12-01" not in sales13, "Barca no Dec overflow")

    row_closed = run_case(
        {
            "op": "applyToRowState",
            "rowState": {"2025-11-03": {"off": False, "last": "120227"}},
            "maps": {
                "salesByDate": {"2025-11-03": 0},
                "businessDayByDate": {"2025-11-03": False},
            },
        }
    )
    rs3 = (row_closed.get("rowState") or {}).get("2025-11-03") or {}
    assert_true(rs3.get("off") is True and rs3.get("last") == "0", "stale 11/3 row reconstructed closed")

    print(f"PASSED={PASSED} FAILED={FAILED}")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

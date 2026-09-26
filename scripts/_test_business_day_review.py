# -*- coding: utf-8 -*-
"""BR-POST-DATA-READINESS-BUSINESS-DAY-REVIEW — unresolved day receptacle."""

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
from kpi_year_store_client import kpi_year_store_js  # noqa: E402
from planning_readiness_lib import STATE_PROVISIONAL, STATE_READY, evaluate  # noqa: E402

FAILED = 0
PASSED = 0
OPTS = {"operatingYear": 2026, "today": "2026-09-26"}
JS = ROOT / "js/kpi-planning-readiness.js"
STORE = ROOT / "scripts/kpi_year_store_client.py"
HOSTS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]
LAYOUT_HOSTS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
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
const layout = ctx.KpiWorkbookLayout;
const c = payload.case || {};
const out = { error: null };
try {
  out.maps = layout.completeHistoricalImport(c.maps, c.opts || {});
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


def unresolved(maps: dict, iso: str):
    return ((maps or {}).get("unresolvedBusinessDayByDate") or {}).get(iso)


def main() -> int:
    js = JS.read_text(encoding="utf-8")
    store = STORE.read_text(encoding="utf-8")
    importer = daily_sales_import_js()

    assert_true("businessDayUnresolved" in store, "store empty timeline has unresolved map")
    assert_true("ingestHistoricalBusinessDayReview" in store, "store ingest API")
    assert_true("resolveAllUnresolvedBusinessDays" in store, "store bulk resolve API")
    assert_true("listUnresolvedBusinessDays" in store, "store list API")
    assert_true("ingestHistoricalBusinessDayReview" in importer, "importer calls ingest")
    assert_true("kpi-pr-alert-dismissed" in js, "session dismiss key")
    assert_true("reasonHistBd" in js, "readiness item key")
    assert_true("startHistChoose" in js, "choose flow")
    assert_true("startHistOneByOne" in js, "one-by-one flow")
    assert_true("hist-all-closed" in js and "hist-all-open" in js, "bulk actions")
    assert_true("hist-guess" not in js, "no fabricated recommendation bulk")
    assert_true("推定どおり一括確定" not in js, "guess copy removed")
    assert_true("diffHistoricalImport" in importer, "replace-contract diff helper")
    assert_true("上書きして続行" in importer, "overwrite confirm JP")
    assert_true("body:not(.office-mode) .kpi-pr-alert.is-hist-done" in js, "Sci-Fi done styling")
    assert_true("kpi-pr-alert-fw" in js, "reuses existing alert id")

    r0 = evaluate(
        year=2026,
        annual_target=10_000_000,
        business_days_map={"2026-01-01": True},
        hl_weights=[85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115],
        pr={
            "businessDaysConfirmedSignature": "x",
            "seasonalityConfirmedSignature": "y",
        },
        unresolved_count=0,
    )
    # signatures won't match → still provisional from BD/season; isolate count flags:
    assert_true(r0["unresolvedCount"] == 0, "evaluate 0 count")
    assert_true(r0["needsHistBdAction"] is False, "evaluate 0 no item")

    r1 = evaluate(
        year=2026,
        annual_target=10_000_000,
        business_days_map={"2026-01-01": True},
        hl_weights=[85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115],
        pr={
            "businessDaysConfirmedSignature": "x",
            "seasonalityConfirmedSignature": "y",
        },
        unresolved_count=1,
    )
    assert_true(r1["unresolvedCount"] == 1, "evaluate 1 count")
    assert_true(r1["needsHistBdAction"] is True, "evaluate 1 item")
    assert_true("historicalBusinessDays" in r1["provisionalReasons"], "evaluate 1 reason")

    rN = evaluate(
        year=2026,
        annual_target=10_000_000,
        business_days_map={"2026-01-01": True},
        hl_weights=[85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115],
        pr={
            "businessDaysConfirmedSignature": "x",
            "seasonalityConfirmedSignature": "y",
        },
        unresolved_count=7,
    )
    assert_true(rN["unresolvedCount"] == 7, "evaluate many count")
    assert_true(rN["state"] == STATE_PROVISIONAL, "evaluate many still provisional")

    t_open = run_case(
        {
            "opts": OPTS,
            "maps": {
                "salesByDate": {"2025-11-01": 60930},
                "unmatchedMetrics": [
                    {"iso": "2025-11-01", "label": "仕入", "amount": 800, "kind": "expense"}
                ],
            },
        }
    )
    assert_true(not t_open.get("error"), "open+expense no error")
    assert_true(biz(t_open.get("maps"), "2025-11-01") is True, "activity wins: open")
    assert_true(unresolved(t_open.get("maps"), "2025-11-01") is None, "activity not unresolved")

    t_closed = run_case({"opts": OPTS, "maps": {"salesByDate": {"2025-11-02": 0}}})
    assert_true(biz(t_closed.get("maps"), "2025-11-02") is False, "present zero auto-close")
    assert_true(unresolved(t_closed.get("maps"), "2025-11-02") is None, "present zero not unresolved")

    t_un = run_case(
        {
            "opts": OPTS,
            "maps": {
                "salesByDate": {"2025-11-03": 0},
                "totalCustomersByDate": {"2025-11-03": 0},
                "expenseByDate": {"2025-11-03": 8400},
            },
        }
    )
    assert_true(not has_biz(t_un.get("maps"), "2025-11-03"), "expense-only omits BD")
    u = unresolved(t_un.get("maps"), "2025-11-03") or {}
    assert_true(u.get("reason") == "expense-only", "expense-only unresolved")
    assert_true(u.get("expense") == 8400, "expense snapshot")
    assert_true(u.get("sales") == 0 and u.get("customers") == 0, "activity snapshot zeros")

    t_miss = run_case(
        {
            "opts": OPTS,
            "maps": {"salesByDate": {"2025-11-04": 10000}},
        }
    )
    assert_true((t_miss.get("maps") or {}).get("salesByDate", {}).get("2025-11-05") == 0, "missing filled 0")
    assert_true(biz(t_miss.get("maps"), "2025-11-05") is False, "imported calendar zero → closed")
    assert_true(unresolved(t_miss.get("maps"), "2025-11-05") is None, "missing not unresolved")

    for path in HOSTS:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-planning-readiness.js?v=20260926-bdr2" in text, f"{rel} readiness cache bdr2")
        assert_true("ingestHistoricalBusinessDayReview" in text, f"{rel} store ingest injected")
        assert_true("businessDayUnresolved" in text, f"{rel} unresolved map injected")

    for path in LAYOUT_HOSTS:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-workbook-layout.js?v=20260926-bdr2" in text, f"{rel} layout cache bdr2")

    print(f"PASSED={PASSED} FAILED={FAILED}")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

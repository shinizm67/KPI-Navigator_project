# -*- coding: utf-8 -*-
"""KPI-BD-FALSE-PROPAGATE — explicit false must survive persist/hydrate/Past Sales render."""

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
LAYOUT = ROOT / "js" / "kpi-workbook-layout.js"
SYNC = ROOT / "js" / "kpi-daily-inputs-sync.js"
ANNUAL = ROOT / "app" / "annual" / "index.html"
OPTS = {"operatingYear": 2026, "today": "2026-09-26"}
WANT = {
    "2025-11-01": {"biz": True, "sales": 60930},
    "2025-11-02": {"biz": False, "sales": 0},
    "2025-11-03": {"biz": False, "sales": 0},
    "2025-11-04": {"biz": True, "sales": 144600},
    "2025-11-09": {"biz": False, "sales": 0},
}


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


def run_node(payload: dict) -> dict:
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
    dispatchEvent() { return true; },
  },
  Date, Number, String, Math, Object, Array, JSON, Error, Promise, console,
  parseInt, parseFloat, isNaN, encodeURIComponent, setTimeout, clearTimeout,
};
ctx.window = ctx;
ctx.globalThis = ctx;
ctx.localStorage = {
  _d: {},
  getItem(k) { return Object.prototype.hasOwnProperty.call(this._d, k) ? this._d[k] : null; },
  setItem(k, v) { this._d[k] = String(v); },
  removeItem(k) { delete this._d[k]; },
};
vm.createContext(ctx);
vm.runInContext(payload.importer, ctx);
if (payload.layoutSrc) vm.runInContext(payload.layoutSrc, ctx);
if (payload.syncSrc) vm.runInContext(payload.syncSrc, ctx);
const api = ctx.__KPI_DAILY_IMPORT;
const layout = ctx.KpiWorkbookLayout;
const c = payload.case || {};
const out = { error: null };

function hasOwn(obj, key) {
  return !!(obj && Object.prototype.hasOwnProperty.call(obj, key));
}

function persistCopy(maps, oy) {
  const sales = {};
  const biz = {};
  Object.keys(maps.salesByDate || {}).forEach((iso) => {
    const y = Number(String(iso).slice(0, 4));
    if (Number.isFinite(oy) && y >= oy) return;
    const n = Number(maps.salesByDate[iso]);
    sales[iso] = Number.isFinite(n) ? n : 0;
  });
  Object.keys(maps.businessDayByDate || {}).forEach((iso) => {
    const y = Number(String(iso).slice(0, 4));
    if (Number.isFinite(oy) && y >= oy) return;
    if (!hasOwn(maps.businessDayByDate, iso)) return;
    biz[iso] = !!maps.businessDayByDate[iso];
  });
  return { sales, biz };
}

function ingest(timeline, maps) {
  const bizMap = maps.businessDayByDate || {};
  const openMap = maps.unresolvedBusinessDayByDate || {};
  Object.keys(bizMap).forEach((iso) => {
    if (hasOwn(bizMap, iso)) timeline.businessDays[iso] = !!bizMap[iso];
  });
  Object.keys(openMap).forEach((iso) => {
    if (hasOwn(timeline.businessDays, iso)) delete timeline.businessDays[iso];
  });
  return timeline;
}

function syncPast(timeline, oy) {
  const ps = { salesByDate: {}, businessDayByDate: {} };
  Object.keys(timeline.dailySales || {}).forEach((iso) => {
    if (Number(String(iso).slice(0, 4)) < oy) ps.salesByDate[iso] = timeline.dailySales[iso];
  });
  Object.keys(timeline.businessDays || {}).forEach((iso) => {
    if (Number(String(iso).slice(0, 4)) < oy) ps.businessDayByDate[iso] = timeline.businessDays[iso];
  });
  return ps;
}

function baseRowDefaults(ps, iso) {
  const bmap = ps.businessDayByDate || {};
  const map = ps.salesByDate || {};
  if (hasOwn(bmap, iso)) {
    const isBusiness = !!bmap[iso];
    if (!isBusiness) return { off: true, last: '0', checked: false };
    const bn = Number(map[iso]);
    return { off: false, last: String(Math.round(Number.isFinite(bn) ? bn : 0)), checked: true };
  }
  let last = '0';
  if (hasOwn(map, iso)) {
    const n = Number(map[iso]);
    if (Number.isFinite(n)) last = String(Math.round(n));
  }
  return { off: false, last: last, checked: true };
}

function applyInputRows(store, rows) {
  rows.forEach((row) => {
    if (!row || !row.iso) return;
    const sales = Number(row.sales);
    store.timeline.dailySales[row.iso] = Number.isFinite(sales) ? sales : 0;
    const rawBiz = hasOwn(row, 'businessDay') ? row.businessDay : undefined;
    if (rawBiz === true || rawBiz === 1 || rawBiz === '1') {
      store.timeline.businessDays[row.iso] = true;
    } else if (rawBiz === false || rawBiz === 0 || rawBiz === '0') {
      store.timeline.businessDays[row.iso] = false;
    } else if (hasOwn(store.timeline.businessDays, row.iso)) {
      delete store.timeline.businessDays[row.iso];
    }
  });
}

function rowsFromMaps(salesMap, bizMap, isos) {
  return isos.map((iso) => {
    const sales = Number(salesMap[iso]);
    const row = { iso: iso, sales: Number.isFinite(sales) ? sales : 0 };
    if (hasOwn(bizMap, iso)) row.businessDay = !!bizMap[iso];
    return row;
  });
}

try {
  if (c.op === 'helpers') {
    const overlay = layout.overlayBusinessDaysPreserveExplicit;
    const staleTrue = { '2025-11-03': true, '2025-11-01': true };
    const timeline = { '2025-11-03': false, '2025-11-01': true };
    const merged = overlay(staleTrue, timeline);
    out.trueSurvives = merged['2025-11-01'] === true && hasOwn(merged, '2025-11-01');
    out.falseSurvives = merged['2025-11-03'] === false && hasOwn(merged, '2025-11-03');
    const onlyFallback = overlay({ '2025-11-10': true }, {});
    out.absentUnchanged = hasOwn(onlyFallback, '2025-11-10') && onlyFallback['2025-11-10'] === true;
    const empty = overlay({}, {});
    out.absentDistinct = !hasOwn(empty, '2025-11-03') && !hasOwn(timeline, 'missing');
    const jsonRound = JSON.parse(JSON.stringify({ businessDays: { a: true, b: false } }));
    out.jsonTrue = jsonRound.businessDays.a === true && hasOwn(jsonRound.businessDays, 'a');
    out.jsonFalse = jsonRound.businessDays.b === false && hasOwn(jsonRound.businessDays, 'b');
    out.jsonAbsent = !hasOwn(jsonRound.businessDays, 'c');
  } else if (c.op === 'barcaPath') {
    let rows = api.parseDelimitedText(c.csvText);
    const before = api.rowsToMaps(rows);
    const maps = layout.completeHistoricalImport(JSON.parse(JSON.stringify(before)), c.opts || {});
    const copied = persistCopy(maps, 2026);
    const timeline = { dailySales: Object.assign({}, copied.sales), businessDays: {} };
    ingest(timeline, { businessDayByDate: copied.biz, unresolvedBusinessDayByDate: maps.unresolvedBusinessDayByDate });
    const jsonStore = JSON.parse(JSON.stringify(timeline));
    const store = { timeline: { dailySales: Object.assign({}, jsonStore.dailySales), businessDays: Object.assign({}, jsonStore.businessDays) } };
    const putRows = rowsFromMaps(store.timeline.dailySales, store.timeline.businessDays, Object.keys(copied.sales));
    const putJson = JSON.parse(JSON.stringify({ rows: putRows }));
    const hydrated = { timeline: { dailySales: {}, businessDays: {} } };
    applyInputRows(hydrated, putJson.rows);
    const ps = syncPast(hydrated.timeline, 2026);
    const staleShared = { '2025-11-03': true, '2025-11-02': true, '2025-11-09': true };
    ps.businessDayByDate = layout.overlayBusinessDaysPreserveExplicit(staleShared, ps.businessDayByDate);
    const rowState = {};
    api.applyToRowState(rowState, maps, 2025);
    out.classify = {};
    out.render = {};
    out.rowState = {};
    out.putHasFalse = {};
    (c.isos || []).forEach((iso) => {
      out.classify[iso] = {
        hasBiz: hasOwn(maps.businessDayByDate, iso),
        biz: hasOwn(maps.businessDayByDate, iso) ? maps.businessDayByDate[iso] : null,
        unresolved: hasOwn(maps.unresolvedBusinessDayByDate, iso),
        sales: maps.salesByDate[iso],
        persistHas: hasOwn(copied.biz, iso),
        persistBiz: hasOwn(copied.biz, iso) ? copied.biz[iso] : null,
        timelineHas: hasOwn(jsonStore.businessDays, iso),
        timelineBiz: hasOwn(jsonStore.businessDays, iso) ? jsonStore.businessDays[iso] : null,
        hydrateHas: hasOwn(hydrated.timeline.businessDays, iso),
        hydrateBiz: hasOwn(hydrated.timeline.businessDays, iso) ? hydrated.timeline.businessDays[iso] : null,
        psHas: hasOwn(ps.businessDayByDate, iso),
        psBiz: hasOwn(ps.businessDayByDate, iso) ? ps.businessDayByDate[iso] : null,
      };
      out.render[iso] = baseRowDefaults(ps, iso);
      out.rowState[iso] = rowState[iso] || null;
      const putRow = putJson.rows.find((r) => r.iso === iso);
      out.putHasFalse[iso] = putRow && hasOwn(putRow, 'businessDay') ? putRow.businessDay : 'ABSENT';
    });
    out.absentProbe = {
      has: hasOwn(ps.businessDayByDate, '1999-01-01'),
      render: baseRowDefaults(ps, '1999-01-01'),
    };
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
        timeout=40,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        raise SystemExit("node harness failed")
    return json.loads(result.stdout)


def main() -> int:
    src = daily_sales_import_js()
    annual = ANNUAL.read_text(encoding="utf-8")
    layout_src = LAYOUT.read_text(encoding="utf-8")
    assert_true("KPI-BD-FALSE-PROPAGATE" in layout_src, "layout helper marker")
    assert_true("overlayBusinessDaysPreserveExplicit" in layout_src, "layout overlay export")
    assert_true("KPI-BD-FALSE-PROPAGATE" in src, "importer applyToRowState marker")
    assert_true("KPI-BD-FALSE-PROPAGATE" in annual, "annual persist/hydrate marker")
    assert_true("parsed.businessDayByDate, ps.businessDayByDate" in annual, "hydrate timeline wins")
    assert_true("syncToAnnualDaily === 'function'" in annual, "ingest syncs Past Sales memory")
    assert_true("pastSalesImportHasYear" in annual, "applyMaps does not rely on maps.years type")

    helpers = run_node(
        {
            "importer": src,
            "layoutSrc": layout_src,
            "case": {"op": "helpers"},
        }
    )
    assert_true(not helpers.get("error"), "helpers no error: " + str(helpers.get("error")))
    assert_true(helpers.get("trueSurvives") is True, "1 true survives overlay")
    assert_true(helpers.get("falseSurvives") is True, "2 false survives overlay (stale true does not win)")
    assert_true(helpers.get("absentUnchanged") is True, "3 absent remains fillable from fallback")
    assert_true(helpers.get("jsonTrue") is True, "1 JSON true survives stringify")
    assert_true(helpers.get("jsonFalse") is True, "2 JSON false survives stringify")
    assert_true(helpers.get("jsonAbsent") is True, "3 JSON absent stays absent")

    barca = run_node(
        {
            "importer": src,
            "layoutSrc": layout_src,
            "case": {
                "op": "barcaPath",
                "csvText": BARCA.read_text(encoding="utf-8"),
                "opts": OPTS,
                "isos": list(WANT.keys()),
            },
        }
    )
    assert_true(not barca.get("error"), "barcaPath no error: " + str(barca.get("error")))
    for iso, want in WANT.items():
        rec = (barca.get("classify") or {}).get(iso) or {}
        rend = (barca.get("render") or {}).get(iso) or {}
        rs = (barca.get("rowState") or {}).get(iso) or {}
        putv = (barca.get("putHasFalse") or {}).get(iso)
        assert_true(rec.get("hasBiz") is True, f"{iso} classified key present")
        assert_true(rec.get("biz") is want["biz"], f"{iso} classified biz={want['biz']}")
        assert_true(rec.get("unresolved") is False, f"{iso} not unresolved")
        assert_true(rec.get("sales") == want["sales"], f"{iso} sales={want['sales']}")
        assert_true(rec.get("persistHas") is True, f"{iso} persist copy has key")
        assert_true(rec.get("persistBiz") is want["biz"], f"{iso} persist biz={want['biz']}")
        assert_true(rec.get("timelineHas") is True, f"{iso} timeline JSON has key")
        assert_true(rec.get("timelineBiz") is want["biz"], f"{iso} timeline JSON biz={want['biz']}")
        assert_true(rec.get("hydrateHas") is True, f"{iso} daily-inputs hydrate has key")
        assert_true(rec.get("hydrateBiz") is want["biz"], f"{iso} daily-inputs hydrate biz={want['biz']}")
        assert_true(rec.get("psHas") is True, f"{iso} Past Sales map has key")
        assert_true(rec.get("psBiz") is want["biz"], f"{iso} Past Sales biz={want['biz']}")
        assert_true(putv is want["biz"], f"{iso} PUT payload businessDay={want['biz']}")
        assert_true(rend.get("checked") is want["biz"], f"{iso} Past Sales checkbox checked={want['biz']}")
        assert_true(rs.get("off") is (not want["biz"]), f"{iso} rowState off={not want['biz']}")
        assert_true(rs.get("bizTouched") is True, f"{iso} rowState bizTouched")

    absent = barca.get("absentProbe") or {}
    assert_true(absent.get("has") is False, "3 absent iso stays absent on Past Sales map")
    assert_true((absent.get("render") or {}).get("checked") is True, "5 absent still uses existing open fallback")

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

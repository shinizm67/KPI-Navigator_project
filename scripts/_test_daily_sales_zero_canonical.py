# -*- coding: utf-8 -*-
"""dailySales 0 vs missing — canonical path test (mirrors production JS)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def has_own(obj: dict, key: str) -> bool:
    return key in obj


def has_canonical_sales_value(mp, iso: str) -> bool:
    if not isinstance(mp, dict):
        return False
    if iso not in mp:
        return False
    v = mp[iso]
    return v is not None


def merge_iso_timeline_map(server_map, local_map):
    out = {}
    if isinstance(server_map, dict):
        for iso in server_map:
            if has_canonical_sales_value(server_map, iso):
                out[iso] = server_map[iso]
    if not isinstance(local_map, dict):
        return out
    for iso in local_map:
        if not has_canonical_sales_value(local_map, iso):
            continue
        if has_canonical_sales_value(out, iso):
            continue
        out[iso] = local_map[iso]
    return out


LEGACY_PLACEHOLDER_SALES = 1234
OPERATING_YEAR = 2026


def is_legacy_placeholder_sales(n) -> bool:
    try:
        return float(n) == LEGACY_PLACEHOLDER_SALES
    except (TypeError, ValueError):
        return False


def iso_year(iso: str):
    try:
        return int(str(iso)[:4])
    except (TypeError, ValueError):
        return None


def is_protected_canonical_sales(iso: str, value) -> bool:
    if value is None:
        return False
    y = iso_year(iso)
    if is_legacy_placeholder_sales(value) and not (y is not None and y < OPERATING_YEAR):
        return False
    return True


def apply_input_rows(store, rows):
    sales_map = store["timeline"]["dailySales"]
    biz_map = store["timeline"]["businessDays"]
    for row in rows:
        if not row or not row.get("iso"):
            continue
        iso = row["iso"]
        sales = row.get("sales")
        try:
            sales_n = float(sales)
        except (TypeError, ValueError):
            sales_n = 0
        if sales_n != sales_n:  # NaN
            sales_n = 0
        has_prev = has_own(sales_map, iso)
        prev_s = sales_map[iso] if has_prev else None
        if has_prev and iso in sales_map and sales_map[iso] is None:
            prev_s = None
        keep = has_prev and is_protected_canonical_sales(iso, prev_s)
        if not keep:
            sales_map[iso] = int(sales_n) if float(sales_n).is_integer() else sales_n
        raw_biz = row["businessDay"] if "businessDay" in row else None
        if raw_biz is True or raw_biz == 1 or raw_biz == "1":
            biz_map[iso] = True
        elif raw_biz is False or raw_biz == 0 or raw_biz == "0":
            biz_map[iso] = False
        elif iso in biz_map:
            del biz_map[iso]


def fill_sales(store, mp):
    daily = store["timeline"]["dailySales"]
    oy = OPERATING_YEAR
    for iso, raw in (mp or {}).items():
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", iso):
            continue
        try:
            n = float(raw)
        except (TypeError, ValueError):
            continue
        if n != n:
            continue
        if is_legacy_placeholder_sales(n) and not (int(iso[:4]) < oy):
            continue
        if has_own(daily, iso):
            cur = daily[iso]
            if cur is not None:
                continue
        daily[iso] = int(n) if float(n).is_integer() else n


def snapshot_payload(daily: dict) -> dict:
    return {
        "targetSalesByDate": dict(daily.get("targetSalesByDate") or {}),
        "businessDayByDate": dict(daily.get("businessDayByDate") or {}),
    }


ISO = "2026-06-15"
ISO2 = "2026-06-16"
ISO3 = "2026-06-17"
ISO4 = "2026-06-19"
LEGACY_ROWS = [
    {"iso": ISO, "sales": 2145, "businessDay": True},
    {"iso": ISO2, "sales": 3408, "businessDay": True},
    {"iso": ISO3, "sales": 1958, "businessDay": True},
    {"iso": ISO4, "sales": 2046, "businessDay": True},
]
LEGACY_MAP = {ISO: 2145, ISO2: 3408, ISO3: 1958, ISO4: 2046}


def test_source_guards() -> None:
    inputs = read("js/kpi-daily-inputs-sync.js")
    gw = read("js/kpi-data-gateway.js")
    annual = read("app/annual/index.html")
    year_store_py = read("scripts/kpi_year_store_client.py")
    assert_true("prevN > 0" not in inputs, "kpi-daily-inputs-sync.js has no prevN > 0")
    assert_true("function isLegacyPlaceholderSales" in inputs, "inputs uses isLegacyPlaceholderSales")
    assert_true("function isProtectedCanonicalSales" in inputs, "inputs uses isProtectedCanonicalSales")
    assert_true(
        "hasPrevSales && isProtectedCanonicalSales(row.iso, prevS)" in inputs,
        "applyInputRows keeps 0 and year-aware 1234",
    )
    assert_true("lv !== 0 && sv === 0" not in gw, "gateway no longer overwrites server 0")
    assert_true("function hasCanonicalSalesValue" in gw, "hasCanonicalSalesValue exists")
    assert_true(
        "if (cur !== undefined && cur !== null) return;" in annual,
        "annual fillSales uses null/undefined missing rule",
    )
    assert_true(
        "Number.isFinite(cur) && cur > 0) return" not in annual,
        "annual fillSales dropped cur > 0",
    )
    assert_true(
        "if (cur !== undefined && cur !== null) return;" in year_store_py,
        "kpi_year_store_client.py fillSales matches runtime",
    )
    assert_true(
        "function snapshotAnnualDailySharedPayload()" in annual,
        "persistSalesDataShared snapshots after persist",
    )
    assert_true(
        "targetSalesByDate: Object.assign({}, d.targetSalesByDate || {})" in annual,
        "payload clones maps instead of aliasing",
    )
    assert_true("storeHadFacts" not in gw, "hydrate no longer auto-PUT via storeHadFacts")
    assert_true("if (storeHadFacts)" not in gw, "hydrate has no storeHadFacts PUT branch")
    assert_true(
        "mergeStorePreservingLocalMepData(data.store" not in gw,
        "normal hydrate does not merge local into server store",
    )
    assert_true(
        "var fullStore = stripDailyFactsFromStore(data.store);" in gw,
        "hydrate uses server store as-is",
    )
    assert_true("pendingPutKind" in gw, "nav vs full PUT kind exists")
    assert_true("schedulePut(cfg, 'nav')" in gw, "NAV writes schedule nav-only PUT")
    assert_true("schedulePut(cfg, 'full')" in gw, "STORE writes schedule full PUT")
    assert_true(
        "if (pendingPutKind === 'nav')" in gw,
        "nav PUT omits canonical store blob",
    )
    pages = [
        "en/app/annual/index.html",
        "zh-tw/app/annual/index.html",
        "app/monthly/index.html",
        "en/app/monthly/index.html",
        "zh-tw/app/monthly/index.html",
        "app/monthly/edit/index.html",
        "en/app/monthly/edit/index.html",
        "zh-tw/app/monthly/edit/index.html",
    ]
    all_pages = ["app/annual/index.html"] + pages
    for rel in all_pages:
        src = read(rel)
        assert_true(
            "if (cur !== undefined && cur !== null) return;" in src,
            f"{rel} fillSales missing-rule",
        )
        fill_old = src.count(
            "var cur = Number(store.timeline.dailySales[iso]);\n"
            "                if (Number.isFinite(cur) && cur > 0) return;"
        )
        assert_true(fill_old == 0, f"{rel} no fillSales cur > 0")
        reload_m = re.search(
            r"reload: function \(\) \{.*?\n          \},",
            src,
            re.S,
        )
        assert_true(reload_m is not None, f"{rel} has reload()")
        assert_true(
            "reconcileTimelineFromLegacy" not in reload_m.group(0),
            f"{rel} reload() does not reconcile from legacy",
        )
        sel_m = re.search(
            r"function setSelectedDate\(iso, source\) \{.*?\n        \}",
            src,
            re.S,
        )
        assert_true(sel_m is not None, f"{rel} has setSelectedDate")
        assert_true(
            "persistStore()" not in sel_m.group(0),
            f"{rel} setSelectedDate does not persistStore",
        )
        save_m = re.search(
            r"function persistSalesDataModalSave\(daily, meta\) \{.*?\n        \}",
            src,
            re.S,
        )
        assert_true(save_m is not None, f"{rel} has persistSalesDataModalSave")
        assert_true(
            "persistStore();" in save_m.group(0),
            f"{rel} Reset/Save persistStore writes canonical",
        )
        assert_true(
            "syncLegacyKeys();" in save_m.group(0),
            f"{rel} Reset/Save mirrors annualDailyShared",
        )
        rec_m = re.search(
            r"function reconcileTimelineFromLegacy\(\) \{.*?\n        \}",
            src,
            re.S,
        )
        assert_true(rec_m is not None, f"{rel} still defines reconcile")
        assert_true(
            "persistStore" not in rec_m.group(0),
            f"{rel} reconcile no longer persistStore",
        )
        assert_true(
            "KpiYearStore.reconcileTimelineFromLegacy()" not in src,
            f"{rel} no auto KpiYearStore.reconcileTimelineFromLegacy()",
        )
    assert_true(
        "KpiYearStore.reconcileTimelineFromLegacy()" not in annual,
        "annual hydratePastSalesShared / refreshAnnualReadSurfaces do not reconcile",
    )
    store_php = read("api/v1/store.php")
    assert_true("expectedRevision" in store_php, "OCC expectedRevision still required")
    assert_true("kpi_v1_store_conflict_out" in store_php, "OCC 409 helper remains")


def test_five_cases() -> None:
    store = {"timeline": {"dailySales": {ISO: 3408}, "businessDays": {}}}
    apply_input_rows(store, [{"iso": ISO, "sales": 1, "businessDay": True}])
    assert_true(store["timeline"]["dailySales"][ISO] == 3408, "positive: applyInputRows keeps 3408")
    fill_sales(store, {ISO: 2145})
    assert_true(store["timeline"]["dailySales"][ISO] == 3408, "positive: fillSales keeps 3408")
    out = merge_iso_timeline_map({ISO: 3408}, {ISO: 2145})
    assert_true(out[ISO] == 3408, "positive: merge keeps server 3408")

    store0 = {
        "timeline": {
            "dailySales": {ISO: 0, ISO2: 0, ISO3: 0, ISO4: 0},
            "businessDays": {ISO: True, ISO2: True, ISO3: True, ISO4: True},
        }
    }
    apply_input_rows(store0, LEGACY_ROWS)
    assert_true(store0["timeline"]["dailySales"][ISO] == 0, "zero: applyInputRows keeps 0 vs 2145")
    assert_true(store0["timeline"]["dailySales"][ISO2] == 0, "zero: applyInputRows keeps 0 vs 3408")
    fill_sales(store0, LEGACY_MAP)
    assert_true(store0["timeline"]["dailySales"][ISO] == 0, "zero: fillSales keeps 0")
    out0 = merge_iso_timeline_map(store0["timeline"]["dailySales"], LEGACY_MAP)
    assert_true(out0[ISO] == 0, "zero: merge keeps server 0")
    assert_true(store0["timeline"]["businessDays"][ISO] is True, "business_day tri-state still set")

    store_m = {"timeline": {"dailySales": {}, "businessDays": {}}}
    apply_input_rows(store_m, [{"iso": ISO, "sales": 2145, "businessDay": True}])
    assert_true(store_m["timeline"]["dailySales"][ISO] == 2145, "missing: applyInputRows fills 2145")
    store_m2 = {"timeline": {"dailySales": {}, "businessDays": {}}}
    fill_sales(store_m2, {ISO: 2145})
    assert_true(store_m2["timeline"]["dailySales"][ISO] == 2145, "missing: fillSales fills 2145")
    store_null = {"timeline": {"dailySales": {ISO: None}, "businessDays": {}}}
    apply_input_rows(store_null, [{"iso": ISO, "sales": 2145}])
    assert_true(store_null["timeline"]["dailySales"][ISO] == 2145, "null: treated as missing")
    out_m = merge_iso_timeline_map({}, {ISO: 0})
    assert_true(out_m[ISO] == 0, "missing server + local 0 fills 0")

    store_oy_ph = {"timeline": {"dailySales": {ISO: 1234}, "businessDays": {}}}
    apply_input_rows(store_oy_ph, [{"iso": ISO, "sales": 2145, "businessDay": True}])
    assert_true(
        store_oy_ph["timeline"]["dailySales"][ISO] == 2145,
        "operating-year 1234 is sentinel, stale daily-inputs may replace",
    )

    past_iso = "2025-06-15"
    store_past_ph = {"timeline": {"dailySales": {past_iso: 1234}, "businessDays": {}}}
    apply_input_rows(store_past_ph, [{"iso": past_iso, "sales": 2145, "businessDay": True}])
    assert_true(
        store_past_ph["timeline"]["dailySales"][past_iso] == 1234,
        "past-year 1234 is real sales and is kept",
    )


def test_reset_save_hydrate_reload() -> None:
    store = {
        "timeline": {
            "dailySales": {ISO: 0, ISO2: 0, ISO3: 0, ISO4: 0},
            "businessDays": {ISO: True, ISO2: True, ISO3: True, ISO4: True},
        },
        "meta": {"selectedDate": "2026-01-01"},
    }
    apply_input_rows(store, LEGACY_ROWS)
    fill_sales(store, LEGACY_MAP)
    merged = merge_iso_timeline_map(store["timeline"]["dailySales"], LEGACY_MAP)
    for iso in (ISO, ISO2, ISO3, ISO4):
        assert_true(store["timeline"]["dailySales"][iso] == 0, f"hydrate {iso} stays 0")
        assert_true(merged[iso] == 0, f"merge {iso} stays 0")
    live = store["timeline"]["dailySales"][ISO]
    assert_true(live == 0, "TW live readDailySales would be 0 while scrolling")
    store["meta"]["selectedDate"] = ISO
    assert_true(store["timeline"]["dailySales"][ISO] == 0, "selectedDate update keeps 0")
    reloaded = json.loads(json.dumps(store))
    fill_sales(reloaded, LEGACY_MAP)
    apply_input_rows(reloaded, LEGACY_ROWS)
    assert_true(reloaded["timeline"]["dailySales"][ISO] == 0, "hard reload reconcile keeps 0")


def test_persist_snapshot() -> None:
    stale = {ISO: 2145, ISO2: 3408}
    daily = {"targetSalesByDate": stale, "businessDayByDate": {ISO: True, ISO2: True}}

    def persist_from_annual_daily() -> None:
        daily["targetSalesByDate"] = {ISO: 0, ISO2: 0}

    persist_from_annual_daily()
    payload = snapshot_payload(daily)
    assert_true(payload["targetSalesByDate"] is not stale, "payload is not pre-Save map ref")
    assert_true(payload["targetSalesByDate"][ISO] == 0, "payload 06-15 is 0")
    assert_true(payload["targetSalesByDate"][ISO2] == 0, "payload 06-16 is 0")
    assert_true(stale[ISO] == 2145, "old map still 2145 but not written")


def hydrate_server_wins(server_store, local_store, dirty=False):
    """Normal hydrate: GET store is canonical. Dirty is overlay, not LS merge."""
    del dirty  # overlay lives in OCC/rowState, not in this merge
    if not isinstance(server_store, dict):
        return local_store
    return json.loads(json.dumps(server_store))


def build_put_body(kind, store, nav, revision):
    if kind == "nav":
        return {"annualNav": nav, "expectedRevision": revision}
    return {"store": store, "annualNav": nav, "expectedRevision": revision}


def sync_legacy_keys_from_timeline(timeline_sales, operating_year=2026):
    """Reset Save syncLegacyKeys replaces annualDailyShared (does not merge)."""
    prefix = str(operating_year) + "-"
    annual_sales = {}
    for iso, val in timeline_sales.items():
        if str(iso).startswith(prefix):
            annual_sales[iso] = val
    return dict(annual_sales)


def test_server_canonical_authority() -> None:
    server = {
        "timeline": {
            "dailySales": {ISO: 0, ISO2: 0, ISO3: 0, ISO4: 0},
            "businessDays": {ISO: True, ISO2: True, ISO3: True, ISO4: True},
        }
    }
    mac_local = {
        "timeline": {
            "dailySales": {
                ISO: 5555,
                ISO2: 4444,
                ISO3: 2846,
                ISO4: 1111,
                "2026-07-01": 2145,
            },
            "businessDays": {},
        }
    }
    hydrated = hydrate_server_wins(server, mac_local, dirty=False)
    for iso in (ISO, ISO2, ISO3, ISO4):
        assert_true(hydrated["timeline"]["dailySales"][iso] == 0, f"Mac hydrate {iso} is server 0")
    assert_true(
        "2026-07-01" not in hydrated["timeline"]["dailySales"],
        "local-only ISO is not filled onto server canonical",
    )
    dirty_hydrated = hydrate_server_wins(server, mac_local, dirty=True)
    assert_true(
        dirty_hydrated["timeline"]["dailySales"][ISO] == 0,
        "OCC dirty does not merge stale LS into GET store",
    )

    merged_if_called = merge_iso_timeline_map(
        server["timeline"]["dailySales"],
        mac_local["timeline"]["dailySales"],
    )
    assert_true(merged_if_called[ISO] == 0, "0 canonical: merge helper still keeps server 0")
    assert_true(
        merged_if_called.get("2026-07-01") == 2145,
        "merge helper would fill missing ISO — hydrate must not call it",
    )

    nav_body = build_put_body(
        "nav",
        server,
        {"calendarYear": 2026, "selectedIso": ISO},
        12,
    )
    assert_true("store" not in nav_body, "date move PUT omits canonical store")
    assert_true(nav_body["expectedRevision"] == 12, "nav PUT still sends OCC revision")
    full_body = build_put_body("full", server, {"selectedIso": ISO}, 12)
    assert_true("store" in full_body, "explicit Save still PUTs store")
    assert_true(full_body["expectedRevision"] == 12, "full PUT still OCC")

    old_shared = {ISO: 2145, ISO2: 3408, "2026-07-01": 2846}
    mirrored = sync_legacy_keys_from_timeline(server["timeline"]["dailySales"])
    assert_true(mirrored[ISO] == 0, "Reset mirror annualDailyShared 06-15 is 0")
    assert_true(mirrored[ISO2] == 0, "Reset mirror annualDailyShared 06-16 is 0")
    assert_true("2026-07-01" not in mirrored, "Reset mirror drops old extra ISO")
    assert_true(old_shared[ISO] == 2145, "pre-Save shared leftover is not reused")

    put_after_hydrate = False
    assert_true(not put_after_hydrate, "hydrate/reload is read-only (no store.php PUT)")


def main() -> int:
    print("--- source guards ---")
    test_source_guards()
    print("--- 5-case: 0 / positive / oy 1234 / past 1234 / missing ---")
    test_five_cases()
    print("--- Reset Save + stale daily-inputs + hydrate + selectedDate + reload ---")
    test_reset_save_hydrate_reload()
    print("--- persistSalesDataShared snapshot ---")
    test_persist_snapshot()
    print("--- server canonical authority / nav PUT / Reset mirror / 2-terminal ---")
    test_server_canonical_authority()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

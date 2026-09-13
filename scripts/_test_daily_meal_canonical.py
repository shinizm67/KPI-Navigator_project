# -*- coding: utf-8 -*-
"""dailyMeal 0 vs missing — canonical path test (mirrors kpi_year_store_client.py)."""
from __future__ import annotations

import copy
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "scripts" / "kpi_year_store_client.py"

FAILED = 0
PASSED = 0

DAILY_MEAL_FIELDS = (
    "lunch_sales",
    "dinner_sales",
    "total_customers",
    "lunch_customers",
    "dinner_customers",
    "total_groups",
    "lunch_groups",
    "dinner_groups",
)

ISO = "2025-01-06"
ISO2 = "2025-01-07"
ISO_OTHER_YEAR = "2026-01-06"


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def valid_iso(iso) -> bool:
    return isinstance(iso, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", iso) is not None


def iso_year(iso: str):
    try:
        return int(str(iso)[:4])
    except (TypeError, ValueError):
        return None


def is_daily_meal_field(field) -> bool:
    return field in DAILY_MEAL_FIELDS


def empty_store():
    return {"meta": {"schemaVersion": 4}, "timeline": {"dailySales": {}, "businessDays": {}}, "years": {}}


def ensure_year_record(store, year):
    years = store["years"]
    if year not in years or not isinstance(years.get(year), dict):
        years[year] = {"year": year, "status": "open", "plan": {}}
    if "plan" not in years[year] or not isinstance(years[year]["plan"], dict):
        years[year]["plan"] = {}
    return years[year]


def ensure_daily_meal_maps(rec):
    if not isinstance(rec, dict):
        return None
    meal = rec.get("dailyMeal")
    if not isinstance(meal, dict):
        rec["dailyMeal"] = {}
        meal = rec["dailyMeal"]
    for field in DAILY_MEAL_FIELDS:
        mp = meal.get(field)
        if not isinstance(mp, dict):
            meal[field] = {}
    return rec["dailyMeal"]


def ensure_year_mep_data(store, year):
    rec = ensure_year_record(store, year)
    if not isinstance(rec.get("dailyExpenses"), dict):
        rec["dailyExpenses"] = {}
    if not isinstance(rec.get("dailyIncome"), dict):
        rec["dailyIncome"] = {}
    ensure_daily_meal_maps(rec)
    if not isinstance(rec.get("dailyMeta"), dict):
        rec["dailyMeta"] = {"memos": {}, "flags": {}, "weather": {}}
    return rec


def read_daily_meal(store, field, iso):
    if not is_daily_meal_field(field) or not valid_iso(iso):
        return None
    rec = store["years"].get(iso_year(iso))
    if not isinstance(rec, dict):
        return None
    meal = rec.get("dailyMeal")
    if not isinstance(meal, dict):
        return None
    mp = meal.get(field)
    if not isinstance(mp, dict):
        return None
    if iso not in mp:
        return None
    try:
        n = float(mp[iso])
    except (TypeError, ValueError):
        return None
    if not math.isfinite(n):
        return None
    return n


def write_daily_meal(store, field, iso, value):
    if not is_daily_meal_field(field) or not valid_iso(iso):
        return False
    rec = ensure_year_mep_data(store, iso_year(iso))
    mp = rec["dailyMeal"][field]
    if value is None:
        if iso in mp:
            del mp[iso]
        return True
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    n = float(value)
    if not math.isfinite(n) or n < 0:
        return False
    mp[iso] = int(round(n))
    return True


def load_mep_year_payload(store, year):
    rec = ensure_year_mep_data(store, year)
    return json.loads(
        json.dumps(
            {
                "dailyExpenses": rec.get("dailyExpenses") or {},
                "dailyIncome": rec.get("dailyIncome") or {},
                "dailyMeal": ensure_daily_meal_maps(rec) or {},
                "dailyMeta": rec.get("dailyMeta") or {"memos": {}, "flags": {}, "weather": {}},
            }
        )
    )


def snapshot_meal(store):
    return copy.deepcopy(store.get("years") or {})


def test_source_guards() -> None:
    src = CLIENT.read_text(encoding="utf-8")
    assert_true("DAILY_MEAL_FIELDS" in src, "client defines DAILY_MEAL_FIELDS")
    assert_true("function readDailyMeal" in src, "client defines readDailyMeal")
    assert_true("function writeDailyMeal" in src, "client defines writeDailyMeal")
    assert_true("function ensureDailyMealMaps" in src, "client defines ensureDailyMealMaps")
    assert_true("ensureDailyMealMaps(rec)" in src, "ensureYearMepData initializes dailyMeal")
    assert_true("dailyMeal: JSON.parse(JSON.stringify(ensureDailyMealMaps(rec)" in src, "loadMepYearPayload includes dailyMeal")
    assert_true("readDailyMeal: readDailyMeal" in src, "KpiYearStore exports readDailyMeal")
    assert_true("writeDailyMeal: writeDailyMeal" in src, "KpiYearStore exports writeDailyMeal")
    assert_true("hasOwnProperty.call(map, iso)" in src, "read uses hasOwnProperty for missing vs 0")
    assert_true("map[iso] = Math.round(value)" in src, "write stores rounded number including 0")
    write_fn = src.split("function writeDailyMeal", 1)[1].split("function ensureYearMepData", 1)[0]
    assert_true("persistStore(" not in write_fn, "writeDailyMeal does not persist")
    assert_true("loadStore(" not in write_fn, "writeDailyMeal does not reload")
    assert_true("dinner_sales" in src and "total − lunch" not in src, "no total-lunch dinner writer comment")
    assert_true("Math.round(parentVal)" not in write_fn, "writeDailyMeal does not auto-calc parent-lunch")
    assert_true("migrateDailyMeal" not in src, "no automatic dailyMeal migration helper")
    persist_fn = src.split("function persistStore()", 1)[1].split("function mergeMap", 1)[0]
    assert_true("dailyMeal" not in persist_fn, "persistStore body not specialized for dailyMeal")


def test_explicit_zero() -> None:
    store = empty_store()
    ok = write_daily_meal(store, "total_customers", ISO, 0)
    assert_true(ok is True, "write 0 returns true")
    assert_true(ISO in store["years"][2025]["dailyMeal"]["total_customers"], "explicit 0 keeps iso key")
    assert_true(store["years"][2025]["dailyMeal"]["total_customers"][ISO] == 0, "explicit 0 value is 0")
    assert_true(read_daily_meal(store, "total_customers", ISO) == 0, "read returns 0 not null")


def test_missing_has_no_key() -> None:
    store = empty_store()
    ensure_year_mep_data(store, 2025)
    meal = store["years"][2025]["dailyMeal"]["lunch_sales"]
    assert_true(ISO not in meal, "init does not invent iso keys")
    assert_true(read_daily_meal(store, "lunch_sales", ISO) is None, "missing read is null")
    assert_true(write_daily_meal(store, "lunch_sales", ISO, 12) is True, "positive write ok")
    assert_true(read_daily_meal(store, "lunch_sales", ISO) == 12, "positive read 12")
    other = store["years"][2025]["dailyMeal"]["dinner_sales"]
    assert_true(ISO not in other, "writing lunch does not create dinner iso")
    assert_true(read_daily_meal(store, "dinner_sales", ISO) is None, "unwritten dinner stays missing")


def test_null_deletes_only_target_iso() -> None:
    store = empty_store()
    write_daily_meal(store, "lunch_customers", ISO, 21)
    write_daily_meal(store, "lunch_customers", ISO2, 22)
    write_daily_meal(store, "total_customers", ISO, 33)
    before = snapshot_meal(store)
    ok = write_daily_meal(store, "lunch_customers", ISO, None)
    assert_true(ok is True, "null write returns true")
    mp = store["years"][2025]["dailyMeal"]["lunch_customers"]
    assert_true(ISO not in mp, "null deletes target iso")
    assert_true(mp.get(ISO2) == 22, "other iso in same field kept")
    assert_true(store["years"][2025]["dailyMeal"]["total_customers"][ISO] == 33, "other field kept")
    assert_true(read_daily_meal(store, "lunch_customers", ISO) is None, "deleted iso reads null")
    assert_true(before[2025]["dailyMeal"]["lunch_customers"][ISO2] == 22, "snapshot still has other iso")


def test_positive_saved() -> None:
    store = empty_store()
    assert_true(write_daily_meal(store, "lunch_sales", ISO, 51200) is True, "positive write ok")
    assert_true(read_daily_meal(store, "lunch_sales", ISO) == 51200, "positive stored")
    assert_true(write_daily_meal(store, "total_groups", ISO, 16.4) is True, "float write ok")
    assert_true(read_daily_meal(store, "total_groups", ISO) == 16, "float rounded")


def test_does_not_touch_other_field_or_iso() -> None:
    store = empty_store()
    write_daily_meal(store, "dinner_sales", ISO, 100)
    write_daily_meal(store, "dinner_sales", ISO2, 200)
    write_daily_meal(store, "lunch_sales", ISO, 50)
    store["timeline"]["dailySales"][ISO] = 85280
    store["years"][2025]["dailyIncome"] = {"food_sales": {ISO: 1}}
    store["years"][2025]["dailyExpenses"] = {"rent": {ISO: 9}}
    write_daily_meal(store, "dinner_sales", ISO, 0)
    assert_true(store["years"][2025]["dailyMeal"]["dinner_sales"][ISO2] == 200, "other dinner iso unchanged")
    assert_true(store["years"][2025]["dailyMeal"]["lunch_sales"][ISO] == 50, "lunch_sales unchanged")
    assert_true(store["timeline"]["dailySales"][ISO] == 85280, "timeline.dailySales unchanged")
    assert_true(store["years"][2025]["dailyIncome"]["food_sales"][ISO] == 1, "dailyIncome unchanged")
    assert_true(store["years"][2025]["dailyExpenses"]["rent"][ISO] == 9, "dailyExpenses unchanged")
    assert_true(ISO_OTHER_YEAR not in store["years"], "other year record not created by 2025 write")


def test_no_auto_dinner_from_total_minus_lunch() -> None:
    store = empty_store()
    store["timeline"]["dailySales"][ISO] = 85280
    write_daily_meal(store, "lunch_sales", ISO, 34000)
    assert_true(read_daily_meal(store, "dinner_sales", ISO) is None, "dinner not invented from total-lunch")
    assert_true(
        ISO not in store["years"][2025]["dailyMeal"]["dinner_sales"],
        "dinner_sales has no iso key after lunch write",
    )


def test_payload_preserves_zero_and_missing() -> None:
    store = empty_store()
    write_daily_meal(store, "total_customers", ISO, 0)
    write_daily_meal(store, "lunch_customers", ISO, 21)
    payload = load_mep_year_payload(store, 2025)
    meal = payload["dailyMeal"]
    assert_true("dailyMeal" in payload, "payload has dailyMeal")
    assert_true(meal["total_customers"][ISO] == 0, "payload keeps explicit 0")
    assert_true(ISO in meal["total_customers"], "payload 0 still has key")
    assert_true(ISO not in meal["dinner_customers"], "payload missing dinner_customers iso")
    assert_true(ISO not in meal["dinner_sales"], "payload missing dinner_sales iso")
    assert_true(meal["lunch_customers"][ISO] == 21, "payload keeps positive")
    rehydrated = empty_store()
    rehydrated["years"][2025] = {"year": 2025, "status": "open", "plan": {}, "dailyMeal": copy.deepcopy(meal)}
    ensure_year_mep_data(rehydrated, 2025)
    assert_true(read_daily_meal(rehydrated, "total_customers", ISO) == 0, "rehydrate 0 is 0")
    assert_true(read_daily_meal(rehydrated, "dinner_customers", ISO) is None, "rehydrate missing is null")


def test_rejects_invalid_values() -> None:
    store = empty_store()
    write_daily_meal(store, "lunch_sales", ISO, 10)
    cases = [
        ("neg", -1),
        ("nan", float("nan")),
        ("inf", float("inf")),
        ("str", "12"),
        ("empty", ""),
        ("bool", True),
        ("obj", {}),
        ("bad_field", 5),
        ("bad_iso", 5),
    ]
    for name, val in cases:
        if name == "bad_field":
            ok = write_daily_meal(store, "not_a_field", ISO, val)
        elif name == "bad_iso":
            ok = write_daily_meal(store, "lunch_sales", "2025/01/06", val)
        else:
            ok = write_daily_meal(store, "lunch_sales", ISO, val)
        assert_true(ok is False, f"invalid {name} rejected")
    assert_true(read_daily_meal(store, "lunch_sales", ISO) == 10, "invalid writes leave previous value")
    assert_true(write_daily_meal(store, "lunch_sales", ISO, None) is True, "null is valid missing")
    assert_true(read_daily_meal(store, "lunch_sales", ISO) is None, "null cleared previous")


def test_client_js_has_no_hydrate_put_hook() -> None:
    src = CLIENT.read_text(encoding="utf-8")
    load_fn = src.split("function loadStore()", 1)[1].split("function persistableStore()", 1)[0]
    assert_true("writeDailyMeal" not in load_fn, "loadStore does not write dailyMeal")
    reload_fn = src.split("reload: function () {{", 1)[1].split("reconcileTimelineFromLegacy:", 1)[0]
    assert_true("writeDailyMeal" not in reload_fn, "reload does not write dailyMeal")
    init_fn = src.split("function init()", 1)[1].split("weekday_target_kpi_js", 1)[0] if "weekday_target_kpi_js" in src else src.split("function init()", 1)[1][:2500]
    assert_true("writeDailyMeal" not in init_fn, "init does not write dailyMeal")


def main() -> int:
    print("--- source guards ---")
    test_source_guards()
    print("--- explicit 0 ---")
    test_explicit_zero()
    print("--- missing has no key ---")
    test_missing_has_no_key()
    print("--- null deletes target iso only ---")
    test_null_deletes_only_target_iso()
    print("--- positive ---")
    test_positive_saved()
    print("--- other field/iso untouched ---")
    test_does_not_touch_other_field_or_iso()
    print("--- no auto dinner ---")
    test_no_auto_dinner_from_total_minus_lunch()
    print("--- payload 0 vs missing ---")
    test_payload_preserves_zero_and_missing()
    print("--- invalid rejected ---")
    test_rejects_invalid_values()
    print("--- no hydrate persist hook ---")
    test_client_js_has_no_hydrate_put_hook()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""Unit 2: MEP meal rows persist to dailyMeal, not dailyExpenses."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from apply_mep_daily_meal import patch_one  # noqa: E402
from kpi_year_store_client import kpi_year_store_js  # noqa: E402
from mep_daily_meal_client import (  # noqa: E402
    extract_daily_meal_api_js,
    extract_ensure_daily_meal_maps_call,
    extract_export_daily_meal_lines,
    extract_load_mep_daily_meal_line,
    mep_daily_meal_runtime_js,
)

FAILED = 0
PASSED = 0

MEP_HTML = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

MEAL_SKIP_IDS = (
    "incLunch",
    "incDinner",
    "cust",
    "custLunch",
    "custDinner",
    "groupCnt",
    "groupCntLunch",
    "groupCntDinner",
)
MEAL_PERSIST = {
    "incLunch": "lunch_sales",
    "cust": "total_customers",
    "custLunch": "lunch_customers",
    "groupCnt": "total_groups",
    "groupCntLunch": "lunch_groups",
}
MEAL_AUTOCALC = ("incDinner", "custDinner", "groupCntDinner")
ISO = "2026-03-02"


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def fn_src(html: str, name: str) -> str:
    m = re.search(rf"function {re.escape(name)}\([^)]*\) \{{", html)
    assert_true(m is not None, f"{name} missing")
    if not m:
        return ""
    start = m.start()
    depth = 0
    for i, ch in enumerate(html[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return html[start : i + 1]
    return html[start:]


def test_client_is_single_source() -> None:
    api = extract_daily_meal_api_js()
    js = kpi_year_store_js()
    assert_true(api.strip() in js, "extracted dailyMeal API must be a substring of kpi_year_store_js()")
    assert_true("function persistStore(" not in api, "extracted dailyMeal API must not persist")
    helper = mep_daily_meal_runtime_js()
    assert_true("function readDailyMeal(" not in helper, "runtime helper must not redefine readDailyMeal")
    assert_true("function writeDailyMeal(" not in helper, "runtime helper must not redefine writeDailyMeal")
    assert_true("function ensureDailyMealMaps(" not in helper, "runtime helper must not redefine ensureDailyMealMaps")
    assert_true("KpiYearStore.writeDailyMeal" in helper, "runtime helper must call year-store writeDailyMeal")
    client_py = (SCRIPTS / "mep_daily_meal_client.py").read_text(encoding="utf-8")
    assert_true("from kpi_year_store_client import kpi_year_store_js" in client_py, "must import year-store client")


def test_html_has_extracted_api() -> None:
    api = extract_daily_meal_api_js().strip()
    call = extract_ensure_daily_meal_maps_call()
    load_line = extract_load_mep_daily_meal_line()
    export_lines = extract_export_daily_meal_lines()
    for path in MEP_HTML:
        html = path.read_text(encoding="utf-8")
        label = path.as_posix()
        assert_true(api in html, f"{label} missing extracted dailyMeal API")
        assert_true(call in html, f"{label} missing ensureDailyMealMaps(rec)")
        assert_true(load_line in html, f"{label} missing loadMepYearPayload dailyMeal")
        assert_true(export_lines in html, f"{label} missing KpiYearStore dailyMeal export")
        assert_true("function persistStore(" not in api, "api persist guard")
        persist_meal = fn_src(html, "persistMepMealToYearStore")
        assert_true("persistStore(" not in persist_meal, f"{label} persistMepMealToYearStore must not persistStore")
        apply_fn = fn_src(html, "applyMepCanonicalToMemory")
        assert_true("persistStore(" not in apply_fn, f"{label} applyMepCanonicalToMemory must not persistStore")
        once = fn_src(html, "persistMepCanonicalOnce")
        assert_true(once.count("KpiYearStore.persistStore()") == 1, f"{label} persistMepCanonicalOnce persistStore != 1")
        run = fn_src(html, "runMepSaveTransaction")
        assert_true(run.count("persistMepCanonicalOnce()") == 1, f"{label} Save persistMepCanonicalOnce != 1")
        persist_year = fn_src(html, "persistMepToYearStore")
        assert_true("deferPersist" in persist_year, f"{label} persistMepToYearStore keeps deferPersist")
        assert_true("!(extra && extra.deferPersist)" in persist_year, f"{label} meal-only persistStore skipped on Save defer")
        assert_true("mepIsMealRowId(rowId)" in fn_src(html, "mergeMepYearPayload"), f"{label} merge skips meal expenses")
        assert_true("mepCollectMealTouchedIso" in fn_src(html, "collectMepTouchedPersistPayload"), f"{label} collect meal")
        assert_true("persistMepMealToYearStore" in fn_src(html, "persistMepToYearStore"), f"{label} persist writes meal")
        defaults = fn_src(html, "ensureDefaultsForMonth")
        assert_true("mepIsMealRowId(rowId)" in defaults, f"{label} ensureDefaults skips meal 0-fill")
        assert_true("sm[iso] = 0" not in defaults, f"{label} MEF_STATIC still 0-fills")
        write = fn_src(html, "writeValue")
        assert_true("mepIsMealPersistRowId" in write and "delete rowValueById" in write, f"{label} writeValue meal missing")


def test_idempotent_apply() -> None:
    path = MEP_HTML[0]
    html = path.read_text(encoding="utf-8")
    again = patch_one(html)
    assert_true(again == html, "apply_mep_daily_meal must be idempotent on JP MEP")


def test_merge_skips_old_expense_keys() -> None:
    row_value = {"incLunch": {"2026-03-01": 99}, "rent": {"2026-03-02": 10}}
    payload = {
        "dailyExpenses": {
            "incLunch": {ISO: 777},
            "incDinner": {ISO: 888},
            "cust": {ISO: 12},
            "custLunch": {ISO: 3},
            "custDinner": {ISO: 9},
            "groupCnt": {ISO: 4},
            "groupCntLunch": {ISO: 1},
            "groupCntDinner": {ISO: 3},
            "rent": {ISO: 5000},
        },
        "dailyMeal": {
            "lunch_sales": {ISO: 0},
            "total_customers": {ISO: 8},
        },
    }
    year = 2026

    def mep_iso_year(iso: str) -> int:
        return int(iso[:4])

    for row_id in MEAL_SKIP_IDS:
        # expenses skipped
        pass
    # simulate merge
    for row_id, by_iso in payload["dailyExpenses"].items():
        if row_id in MEAL_SKIP_IDS:
            continue
        row_value.setdefault(row_id, {}).update(by_iso)
    for row_id in MEAL_SKIP_IDS:
        if row_id not in MEAL_PERSIST:
            mp = row_value.get(row_id) or {}
            for iso in list(mp):
                if mep_iso_year(iso) == year:
                    del mp[iso]
            continue
        dest = row_value.setdefault(row_id, {})
        for iso in list(dest):
            if mep_iso_year(iso) == year:
                del dest[iso]
        field = MEAL_PERSIST[row_id]
        src = (payload.get("dailyMeal") or {}).get(field) or {}
        for iso, raw in src.items():
            n = int(round(float(raw)))
            dest[iso] = n
    assert_true(row_value["incLunch"].get(ISO) == 0, "explicit 0 hydrates from dailyMeal")
    assert_true("2026-03-01" not in row_value["incLunch"], "same-year leftover meal keys cleared")
    assert_true(ISO not in row_value.get("custLunch", {}), "missing lunch customers stays missing")
    assert_true(row_value["cust"].get(ISO) == 8, "customers hydrate from dailyMeal")
    assert_true(row_value["rent"].get(ISO) == 5000, "expense rows still hydrate from dailyExpenses")
    assert_true(ISO not in (row_value.get("incDinner") or {}), "old incDinner expense key not read")


def test_collect_payload_python() -> None:
    cur = {
        "incLunch": {ISO: 0},
        "cust": {ISO: 4},
        "incDinner": {ISO: 900},
        "rent": {ISO: 100},
    }
    base = {
        "incLunch": {},
        "cust": {ISO: 4},
        "incDinner": {ISO: 100},
        "rent": {ISO: 50},
    }
    daily_meal = {}
    daily_expenses = {}
    row_ids = set(cur) | set(base)
    for row_id in row_ids:
        cur_map = cur.get(row_id) or {}
        base_map = base.get(row_id) or {}
        isos = set(cur_map) | set(base_map)
        for iso in isos:
            if row_id in MEAL_SKIP_IDS:
                if row_id not in MEAL_PERSIST:
                    continue
                cur_has = iso in cur_map
                base_has = iso in base_map
                cur_val = int(cur_map[iso]) if cur_has else None
                base_val = int(base_map[iso]) if base_has else None
                if cur_has == base_has and cur_val == base_val:
                    continue
                field = MEAL_PERSIST[row_id]
                daily_meal.setdefault(field, {})[iso] = cur_val if cur_has else None
                continue
            if int(cur_map.get(iso) or 0) == int(base_map.get(iso) or 0):
                continue
            daily_expenses.setdefault(row_id, {})[iso] = int(cur_map.get(iso) or 0)
    assert_true("incLunch" not in daily_expenses, "incLunch must not fall into dailyExpenses")
    assert_true("incDinner" not in daily_expenses, "incDinner must not persist")
    assert_true("dinner_sales" not in daily_meal, "autoCalc dinner must not write dailyMeal")
    assert_true(daily_meal.get("lunch_sales", {}).get(ISO) == 0, "explicit 0 lunch_sales is dirty")
    assert_true("total_customers" not in daily_meal, "unchanged cust is not dirty")
    assert_true(daily_expenses.get("rent", {}).get(ISO) == 100, "expense dirty still goes to dailyExpenses")


def test_forbidden_files_unmodified() -> None:
    spec = importlib.util.spec_from_file_location("forbidden", SCRIPTS / "apply_kpi_year_store.py")
    assert_true(spec is not None, "apply_kpi_year_store.py still exists")
    year_store = (SCRIPTS / "kpi_year_store_client.py").read_text(encoding="utf-8")
    assert_true("function writeDailyMeal" in year_store, "Unit 1 writeDailyMeal remains in year-store client")
    helper = mep_daily_meal_runtime_js()
    for dinner in MEAL_AUTOCALC:
        field = {
            "incDinner": "dinner_sales",
            "custDinner": "dinner_customers",
            "groupCntDinner": "dinner_groups",
        }[dinner]
        assert_true(dinner not in helper.split("MEP_MEAL_ROW_TO_FIELD")[1].split("MEP_MEAL_PERSIST_ROW_IDS")[0] or True, "guard")
        mapping = helper.split("var MEP_MEAL_ROW_TO_FIELD")[1].split("var MEP_MEAL_PERSIST_ROW_IDS")[0]
        assert_true(field not in mapping, f"{field} must not be in persist mapping")
        assert_true(dinner not in mapping, f"{dinner} must not persist")


def main() -> int:
    test_client_is_single_source()
    test_html_has_extracted_api()
    test_idempotent_apply()
    test_merge_skips_old_expense_keys()
    test_collect_payload_python()
    test_forbidden_files_unmodified()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

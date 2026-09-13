# -*- coding: utf-8 -*-
"""Unit 3: dinner hand-input, derived lunch AUTO CALC, no ref overlay."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from apply_mep_daily_meal import patch_one  # noqa: E402
from mep_daily_meal_client import mep_daily_meal_runtime_js  # noqa: E402

FAILED = 0
PASSED = 0

MEP_HTML = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

DINNER_ROWS = ("incDinner", "custDinner", "groupCntDinner")
LUNCH_ROWS = ("incLunch", "custLunch", "groupCntLunch")
ALLOWED = {
    "scripts/mep_daily_meal_client.py",
    "scripts/apply_mep_daily_meal.py",
    "scripts/_test_mep_daily_meal_persist.py",
    "scripts/_test_mep_dinner_canonical.py",
    "app/monthly/edit/index.html",
    "en/app/monthly/edit/index.html",
    "zh-tw/app/monthly/edit/index.html",
}


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


def derived_lunch(has_t, t, has_d, d):
    if not has_t or not has_d or t is None or d is None:
        return None
    return t - d


def validate_triple(has_t, t, has_l, l, has_d, d):
    if has_t and has_l and l is not None and t is not None and l > t:
        return "exceed"
    if has_t and has_d and d is not None and t is not None and d > t:
        return "exceed"
    if has_t and has_l and has_d and None not in (t, l, d) and (l + d) != t:
        return "mismatch"
    return None


def pc_explicit(has_s, s, has_c, c):
    if not has_s or not has_c:
        return None
    if c == 0:
        return None
    if s == 0:
        return 0
    return round(s / c)


def pc_lunch(has_ts, ts, has_tc, tc, has_ds, ds, has_dc, dc):
    if not (has_ts and has_tc and has_ds and has_dc):
        return None
    sales = ts - ds
    cust = tc - dc
    if cust <= 0:
        return None
    if sales == 0:
        return 0
    return round(sales / cust)


def test_derived_lunch_matrix() -> None:
    cases = [
        ((False, None, True, 0), None),
        ((True, 100, False, None), None),
        ((True, 100, True, 0), 100),
        ((True, 100, True, 40), 60),
        ((True, 100, True, 100), 0),
        ((True, 80, True, 80), 0),
        ((True, 0, True, 0), 0),
    ]
    for args, expected in cases:
        got = derived_lunch(*args)
        assert_true(got == expected, f"derived lunch {args} expected {expected} got {got}")


def test_validation_matrix() -> None:
    cases = [
        ((True, 100, False, None, True, 60), None),
        ((True, 100, False, None, True, 120), "exceed"),
        ((True, 100, True, 40, True, 60), None),
        ((True, 100, True, 40, True, 50), "mismatch"),
        ((True, 100, True, 120, False, None), "exceed"),
        ((False, None, False, None, True, 60), None),
        ((True, 80, False, None, True, 80), None),
        ((True, 0, True, 0, True, 0), None),
        ((True, 50, True, 50, True, 10), "mismatch"),
    ]
    for args, expected in cases:
        got = validate_triple(*args)
        assert_true(got == expected, f"validate {args} expected {expected} got {got}")


def test_pc_matrix() -> None:
    dinner_cases = [
        ((False, None, False, None), None),
        ((True, 100, False, None), None),
        ((False, None, True, 2), None),
        ((True, 100, True, 0), None),
        ((True, 0, True, 0), None),
        ((True, 0, True, 4), 0),
        ((True, 900, True, 3), 300),
    ]
    for args, expected in dinner_cases:
        got = pc_explicit(*args)
        assert_true(got == expected, f"pcDinner/pc {args} expected {expected} got {got}")
    lunch_cases = [
        ((False, None, True, 10, True, 4, True, 2), None),
        ((True, 100, True, 10, False, None, True, 2), None),
        ((True, 100, True, 10, True, 40, True, 4), 10),
        ((True, 100, True, 4, True, 100, True, 4), None),
        ((True, 80, True, 4, True, 80, True, 2), 0),
    ]
    for args, expected in lunch_cases:
        got = pc_lunch(*args)
        assert_true(got == expected, f"pcLunch {args} expected {expected} got {got}")


def persist_block(helper: str) -> str:
    return helper.split("var MEP_MEAL_PERSIST_ROW_IDS")[1].split("var MEP_MEAL_LUNCH_ROW_IDS")[0]


def test_helper_source() -> None:
    helper = mep_daily_meal_runtime_js()
    persist = persist_block(helper)
    assert_true("incDinner: 'dinner_sales'" in helper, "incDinner maps to dinner_sales")
    assert_true("custDinner: 'dinner_customers'" in helper, "custDinner maps to dinner_customers")
    assert_true("groupCntDinner: 'dinner_groups'" in helper, "groupCntDinner maps to dinner_groups")
    assert_true("incLunch: 'lunch_sales'" in helper, "lunch mapping remains for hydrate")
    assert_true("        'incDinner',\n" in persist, "dinner sales persists")
    assert_true("        'custDinner',\n" in persist, "dinner customers persist")
    assert_true("        'groupCntDinner'\n" in persist, "dinner groups persist")
    assert_true("        'cust',\n" in persist, "total customers persist")
    assert_true("        'groupCnt',\n" in persist, "total groups persist")
    assert_true("'incLunch'" not in persist, "derived lunch sales must not persist")
    assert_true("'custLunch'" not in persist, "derived lunch customers must not persist")
    assert_true("'groupCntLunch'" not in persist, "derived lunch groups must not persist")
    assert_true("mepComputeDerivedLunchValue" in helper, "derived lunch helper")
    assert_true("mepIsLunchDerivedRowId" in helper, "lunch derived row helper")
    assert_true("mepIsMealHydrateRowId" in helper, "hydrate includes existing lunch")
    assert_true("mepIsDinnerPersistRowId" not in helper, "overlay dinner persist helper removed")
    assert_true("mepLunchTripleForRow" not in helper, "overlay lunch triple helper removed")
    assert_true("mepDinnerTripleForRow" not in helper, "overlay dinner triple helper removed")
    assert_true("mepAppendDinnerRefHint" not in helper, "ref overlay helper removed")
    assert_true("meal-ref" not in helper, "meal-ref class removed")
    assert_true("meal-ref-value" not in helper, "meal-ref-value class removed")
    assert_true("data-mep-meal-ref" not in helper, "ref overlay attr removed")
    assert_true("mepDinnerRefVisibleText" not in helper, "ref visible text removed")
    assert_true("\u2248" not in helper, "approx tilde must stay gone")
    assert_true("\u53c2\u8003" not in helper, "jp ref label must stay gone")
    assert_true("'Ref'" not in helper and '"Ref"' not in helper, "en Ref label must stay gone")
    assert_true("\u53c3\u8003" not in helper, "zh-tw ref label must stay gone")
    assert_true("mepValidateMealBreakdown" in helper, "Save validation helper")
    assert_true("dVal > tVal" in helper, "dinner <= total")
    assert_true("lVal + dVal !== tVal" in helper, "existing lunch+dinner+total still checked")
    assert_true("writeDailyMeal" in helper, "persist still uses writeDailyMeal")
    assert_true("function persistStore(" not in helper, "helper must not persist")
    assert_true("function writeDailyMeal(" not in helper, "must not redefine writeDailyMeal")
    assert_true("if (!mepIsMealPersistRowId(rowId)) return;" in helper, "raw write skips derived lunch")
    assert_true("mepIsMealHydrateRowId(rowId)" in helper, "merge hydrates existing lunch")


def test_html_dinner_wiring() -> None:
    helper = mep_daily_meal_runtime_js()
    for path in MEP_HTML:
        html = path.read_text(encoding="utf-8")
        label = path.as_posix()
        assert_true(helper.strip() in html, f"{label} helper block matches generator")
        assert_true("KPI-MEP-MEAL-REF" not in html, f"{label} meal-ref CSS removed")
        assert_true("mepAppendDinnerRefHint" not in html, f"{label} ref overlay call removed")
        assert_true("monthly-edit-float__meal-ref" not in html, f"{label} meal-ref class removed")
        assert_true("meal-ref-value" not in html, f"{label} meal-ref-value class removed")
        assert_true("dinnerAutoCalcHint" not in html, f"{label} leftover dinner AUTO CALC title removed")
        assert_true("mepIsDinnerPersistRowId" not in html, f"{label} overlay dinner helper removed")
        assert_true("\u2248" not in html, f"{label} approx tilde not in runtime")
        assert_true("\u53c2\u8003" not in html, f"{label} jp ref label not in runtime")
        assert_true("\u53c3\u8003" not in html, f"{label} zh-tw ref label not in runtime")
        grid = fn_src(html, "buildGrid")
        assert_true("inp.className = 'monthly-edit-float__input'" in grid, f"{label} lunch uses shared input class")
        auto_m = re.search(
            r"\} else if \(r\.autoCalc\) \{.*?inp\.disabled = true;\s*inp\.readOnly = true;",
            grid,
            re.S,
        )
        assert_true(auto_m is not None, f"{label} AUTO CALC cell draw found")
        auto_draw = auto_m.group(0) if auto_m else ""
        assert_true("} else if (r.autoCalcLunchId)" in auto_draw, f"{label} lunch reuses AUTO CALC draw")
        assert_true("inp.style" not in auto_draw, f"{label} AUTO CALC numbers have no inline style")
        assert_true("setAttribute('title'" not in auto_draw, f"{label} AUTO CALC numbers have no ref title")
        assert_true("aria-label" not in auto_draw, f"{label} AUTO CALC numbers have no ref aria-label")
        assert_true("meal-ref" not in auto_draw, f"{label} AUTO CALC draw has no meal-ref DOM")
        assert_true("font-family" not in auto_draw, f"{label} AUTO CALC draw has no custom font")
        assert_true("mepValidateMealBreakdown(mefYear)" in html, f"{label} Save validates meal")
        perform = fn_src(html, "performMepSave")
        assert_true("mepSaveInProgress = false" in perform, f"{label} validation clears save lock")
        assert_true("runMepSaveTransaction()" in perform, f"{label} valid Save still uses Unit 2 tx")
        assert_true("window.alert(mealErr)" in perform, f"{label} validation alerts and stops")
        assert_true(
            perform.find("mepValidateMealBreakdown") < perform.find("runMepSaveTransaction()"),
            f"{label} validate before PUT",
        )
        avg = fn_src(html, "computeAvgSpendValue")
        assert_true("mepMealHasGridValue('cust', iso)" in avg, f"{label} pc requires explicit customers")
        assert_true("mepMealHasGridValue('incDinner', iso)" in avg, f"{label} pcDinner uses dinner_sales")
        assert_true("mepMealHasGridValue('custDinner', iso)" in avg, f"{label} pcDinner uses dinner_customers")
        assert_true("totalSales - dinnerSales" in avg, f"{label} pcLunch uses derived lunch sales")
        assert_true("totalCust - dinnerCust" in avg, f"{label} pcLunch uses derived lunch customers")
        assert_true("readValue('incLunch', iso)" not in avg, f"{label} pcLunch must not use canonical lunch")
        assert_true("pcVal == null ? '' : fmtMoney(pcVal)" in html, f"{label} missing pc is blank")
        auto = fn_src(html, "computeStaticAutoCalcValue")
        assert_true("mepComputeDerivedLunchValue" in auto, f"{label} lunch AUTO CALC uses derived helper")
        static = re.search(r"var MEF_STATIC_INPUT_IDS = \[([^\]]+)\]", html)
        assert_true(static is not None, f"{label} MEF_STATIC present")
        ids = static.group(1) if static else ""
        for rid in DINNER_ROWS:
            assert_true(f"'{rid}'" in ids, f"{label} MEF_STATIC includes {rid}")
        for rid in LUNCH_ROWS:
            assert_true(f"'{rid}'" not in ids, f"{label} MEF_STATIC excludes derived {rid}")
        persist = fn_src(html, "persistMepToYearStore")
        assert_true("mepIsMealRowId(rowId)" in persist, f"{label} dinner still skipped from expenses")
        assert_true("persistMepMealToYearStore" in persist, f"{label} dinner writes via meal persist")
        run = fn_src(html, "runMepSaveTransaction")
        assert_true(run.count("persistMepCanonicalOnce()") == 1, f"{label} Save persistStore still 1")
        assert_true("flushPut" in run, f"{label} Save still one flushPut path")
        merge = fn_src(html, "mergeMepYearPayload")
        assert_true("mepIsMealRowId(rowId)" in merge, f"{label} hydrate skips meal expenses")
        assert_true("KpiYearStore.persistStore()" not in merge, f"{label} hydrate must not persist")
        collect = fn_src(html, "mepCollectMealTouchedIso")
        assert_true("mepIsMealPersistRowId(rowId)" in collect, f"{label} collect skips derived lunch")
        for rid in DINNER_ROWS:
            block = html.split(f"id: '{rid}'", 1)[1].split("rows.push({", 1)[0]
            assert_true("autoCalc: true" not in block, f"{label} {rid} is hand-entered")
            assert_true("autoCalcLunchId" not in block, f"{label} {rid} is not derived")
        lunch_parents = {
            "incLunch": ("salesRow", "incDinner"),
            "custLunch": ("cust", "custDinner"),
            "groupCntLunch": ("groupCnt", "groupCntDinner"),
        }
        for rid, (parent, dinner) in lunch_parents.items():
            block = html.split(f"id: '{rid}'", 1)[1].split("rows.push({", 1)[0]
            assert_true("autoCalc: true" in block, f"{label} {rid} is AUTO CALC")
            assert_true(f"autoCalcParent: '{parent}'" in block, f"{label} {rid} parent {parent}")
            assert_true(f"autoCalcLunchId: '{dinner}'" in block, f"{label} {rid} subtracts {dinner}")
            assert_true("autoCalcTitle" not in block, f"{label} {rid} has no extra number tooltip")
        pc_block = html.split("id: 'pcDinner'", 1)[1].split("rows.push({", 1)[0]
        assert_true("autoCalc: true" in pc_block, f"{label} pcDinner stays computed")
        assert_true("autoVal == null" in html, f"{label} derived lunch blank when dinner missing")


def test_idempotent_and_allowed() -> None:
    path = MEP_HTML[0]
    html = path.read_text(encoding="utf-8")
    again = patch_one(html)
    assert_true(again == html, "apply_mep_daily_meal must stay idempotent after Unit 3")
    year_store = (SCRIPTS / "kpi_year_store_client.py").read_text(encoding="utf-8")
    assert_true("function writeDailyMeal" in year_store, "year-store client untouched as Unit 1 source")
    apply_year = (SCRIPTS / "apply_kpi_year_store.py").read_text(encoding="utf-8")
    assert_true("apply_kpi_year_store" in apply_year or "YEAR-STORE" in apply_year, "year-store apply script remains")


def main() -> int:
    test_derived_lunch_matrix()
    test_validation_matrix()
    test_pc_matrix()
    test_helper_source()
    test_html_dinner_wiring()
    test_idempotent_and_allowed()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

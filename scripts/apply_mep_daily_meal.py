#!/usr/bin/env python3
"""Wire MEP meal rows to dailyMeal without replacing the YEAR-STORE IIFE.

Unit 1 APIs are extracted from kpi_year_store_client.py and injected locally.
Does not run apply_kpi_year_store.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from mep_daily_meal_client import (  # noqa: E402
    MEP_DAILY_MEAL_BEGIN,
    MEP_DAILY_MEAL_END,
    extract_daily_meal_api_js,
    extract_ensure_daily_meal_maps_call,
    extract_export_daily_meal_lines,
    extract_load_mep_daily_meal_line,
    mep_daily_meal_runtime_js,
)

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

RUNTIME_ANCHOR = """      function mergeMepIncomeStreamsFromPayload(payload) {"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        if text.count(old) != 1:
            raise ValueError(f"patch not unique ({label}): {text.count(old)}")
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise ValueError(f"patch miss ({label})")


def patch_year_store_daily_meal_api(text: str) -> str:
    api = extract_daily_meal_api_js().rstrip() + "\n"
    if "        var DAILY_MEAL_FIELDS = [" in text:
        pattern = re.compile(
            r"        var DAILY_MEAL_FIELDS = \[[\s\S]*?(?=\n        function ensureYearMepData\(year\))"
        )
        if not pattern.search(text):
            raise ValueError("DAILY_MEAL_FIELDS present but ensureYearMepData boundary not matched")
        return pattern.sub(lambda _m: api, text, count=1)
    needle = "        function ensureYearMepData(year) {"
    if text.count(needle) != 1:
        raise ValueError("ensureYearMepData missing or not unique")
    return text.replace(needle, api + needle, 1)


def patch_ensure_year_mep_data(text: str) -> str:
    call = extract_ensure_daily_meal_maps_call()
    old = (
        "          if (!rec.dailyIncome || typeof rec.dailyIncome !== 'object') rec.dailyIncome = {};\n"
        "          if (!rec.dailyMeta || typeof rec.dailyMeta !== 'object') {"
    )
    new = (
        "          if (!rec.dailyIncome || typeof rec.dailyIncome !== 'object') rec.dailyIncome = {};\n"
        f"{call}\n"
        "          if (!rec.dailyMeta || typeof rec.dailyMeta !== 'object') {"
    )
    return replace_once(text, old, new, "ensureYearMepData dailyMeal")


def patch_load_mep_year_payload(text: str) -> str:
    line = extract_load_mep_daily_meal_line()
    old = (
        "            dailyIncome: JSON.parse(JSON.stringify(rec.dailyIncome || {})),\n"
        "            dailyMeta: JSON.parse("
    )
    new = (
        "            dailyIncome: JSON.parse(JSON.stringify(rec.dailyIncome || {})),\n"
        f"{line}\n"
        "            dailyMeta: JSON.parse("
    )
    return replace_once(text, old, new, "loadMepYearPayload dailyMeal")


def patch_year_store_export(text: str) -> str:
    export_lines = extract_export_daily_meal_lines()
    old = "          readDailyIncome: readDailyIncome,\n          readDailySales: readDailySales,"
    new = (
        "          readDailyIncome: readDailyIncome,\n"
        f"{export_lines}\n"
        "          readDailySales: readDailySales,"
    )
    return replace_once(text, old, new, "KpiYearStore dailyMeal export")


def inject_runtime_helpers(text: str) -> str:
    block = mep_daily_meal_runtime_js().rstrip() + "\n"
    if MEP_DAILY_MEAL_BEGIN in text:
        pattern = re.compile(
            r"[ \t]*"
            + re.escape(MEP_DAILY_MEAL_BEGIN)
            + r"[\s\S]*?"
            + re.escape(MEP_DAILY_MEAL_END)
            + r"\n"
        )
        if not pattern.search(text):
            raise ValueError("KPI-MEP-DAILY-MEAL BEGIN present but block not matched")
        return pattern.sub(lambda _m: block, text, count=1)
    if RUNTIME_ANCHOR not in text:
        raise ValueError("runtime helper anchor missing")
    if text.count(RUNTIME_ANCHOR) != 1:
        raise ValueError("runtime helper anchor not unique")
    return text.replace(RUNTIME_ANCHOR, block + RUNTIME_ANCHOR, 1)


def patch_merge_payload(text: str) -> str:
    old_loop = """        Object.keys(payload.dailyExpenses || {}).forEach(function (rowId) {
          if (!rowValueById[rowId]) rowValueById[rowId] = {};
          Object.assign(rowValueById[rowId], payload.dailyExpenses[rowId]);
        });"""
    new_loop = """        Object.keys(payload.dailyExpenses || {}).forEach(function (rowId) {
          if (typeof mepIsMealRowId === 'function' && mepIsMealRowId(rowId)) return;
          if (!rowValueById[rowId]) rowValueById[rowId] = {};
          Object.assign(rowValueById[rowId], payload.dailyExpenses[rowId]);
        });
        if (typeof mergeMepDailyMealFromPayload === 'function') {
          mergeMepDailyMealFromPayload(payload, year);
        }"""
    text = replace_once(text, old_loop, new_loop, "mergeMepYearPayload skip meal expenses")
    old_sig = "      function mergeMepYearPayload(payload) {"
    new_sig = "      function mergeMepYearPayload(payload, year) {"
    text = replace_once(text, old_sig, new_sig, "mergeMepYearPayload year arg")
    old_call = "        mergeMepYearPayload(KpiYearStore.loadMepYearPayload(year));"
    new_call = "        mergeMepYearPayload(KpiYearStore.loadMepYearPayload(year), year);"
    return replace_once(text, old_call, new_call, "loadMepFromYearStore merge year")


def patch_collect_touched(text: str) -> str:
    old_out = """        var out = {
          dailyExpenses: {},
          dailyIncome: {},
          memos: {},"""
    new_out = """        var out = {
          dailyExpenses: {},
          dailyIncome: {},
          dailyMeal: {},
          memos: {},"""
    text = replace_once(text, old_out, new_out, "collectMepTouched dailyMeal out")
    old_iso = """          Object.keys(isos).forEach(function (iso) {
            if (Number.isFinite(y) && mepIsoYear(iso) !== y) return;
            if (mepNormMoney(curMap[iso]) === mepNormMoney(baseMap[iso])) return;
            var n = mepNormMoney(curMap[iso]);
            if (isIncome) {"""
    new_iso = """          Object.keys(isos).forEach(function (iso) {
            if (Number.isFinite(y) && mepIsoYear(iso) !== y) return;
            if (typeof mepCollectMealTouchedIso === 'function' && mepCollectMealTouchedIso(out, rowId, iso, curMap, baseMap)) {
              return;
            }
            if (mepNormMoney(curMap[iso]) === mepNormMoney(baseMap[iso])) return;
            var n = mepNormMoney(curMap[iso]);
            if (isIncome) {"""
    return replace_once(text, old_iso, new_iso, "collectMepTouched meal iso")


def patch_persist_mep_to_year_store(text: str) -> str:
    old = """        var payload = {
          dailyExpenses: touched.dailyExpenses || {},
          dailyMeta: {
            memos: touched.memos || {},
            weather: touched.weather || {},
            flags: touched.flags || {}
          }
        };
        if (touched.memoRowsChanged) payload.mepMemoRows = rowSnapshot(state.memoItems);
        if (touched.strategyNotes && Object.keys(touched.strategyNotes).length) {
          payload.monthlyStrategyUserNotes = touched.strategyNotes;
        }
        var hasExp = Object.keys(payload.dailyExpenses).length > 0;
        var hasMeta =
          Object.keys(payload.dailyMeta.memos).length > 0 ||
          Object.keys(payload.dailyMeta.weather).length > 0 ||
          Object.keys(payload.dailyMeta.flags).length > 0 ||
          !!payload.mepMemoRows ||
          !!payload.monthlyStrategyUserNotes;
        if (!hasExp && !hasMeta) return true;
        return KpiYearStore.bulkPersistMepYear(year, payload, {
          source: 'monthly-edit-float',
          forceExpenses: !!(extra && extra.forceExpenses),
          deferPersist: !!(extra && extra.deferPersist)
        });"""
    new = """        if (typeof persistMepMealToYearStore === 'function') persistMepMealToYearStore(touched);
        var rawExp = touched.dailyExpenses || {};
        var dailyExpenses = {};
        Object.keys(rawExp).forEach(function (rowId) {
          if (typeof mepIsMealRowId === 'function' && mepIsMealRowId(rowId)) return;
          dailyExpenses[rowId] = rawExp[rowId];
        });
        var payload = {
          dailyExpenses: dailyExpenses,
          dailyMeta: {
            memos: touched.memos || {},
            weather: touched.weather || {},
            flags: touched.flags || {}
          }
        };
        if (touched.memoRowsChanged) payload.mepMemoRows = rowSnapshot(state.memoItems);
        if (touched.strategyNotes && Object.keys(touched.strategyNotes).length) {
          payload.monthlyStrategyUserNotes = touched.strategyNotes;
        }
        var hasExp = Object.keys(payload.dailyExpenses).length > 0;
        var hasMeta =
          Object.keys(payload.dailyMeta.memos).length > 0 ||
          Object.keys(payload.dailyMeta.weather).length > 0 ||
          Object.keys(payload.dailyMeta.flags).length > 0 ||
          !!payload.mepMemoRows ||
          !!payload.monthlyStrategyUserNotes;
        var hasMeal = typeof mepTouchedDailyMealHasValues === 'function' && mepTouchedDailyMealHasValues(touched);
        if (!hasExp && !hasMeta) {
          if (
            hasMeal &&
            !(extra && extra.deferPersist) &&
            window.KpiYearStore &&
            typeof KpiYearStore.persistStore === 'function'
          ) {
            KpiYearStore.persistStore();
          }
          return true;
        }
        return KpiYearStore.bulkPersistMepYear(year, payload, {
          source: 'monthly-edit-float',
          forceExpenses: !!(extra && extra.forceExpenses),
          deferPersist: !!(extra && extra.deferPersist)
        });"""
    return replace_once(text, old, new, "persistMepToYearStore meal")


def patch_build_mep_persist_payload(text: str) -> str:
    pattern = re.compile(
        r"          if \(typeof mepIsIncomeCanonicalRowId === 'function' && mepIsIncomeCanonicalRowId\(rowId\)\) \{\n"
        r"            return;\n"
        r"          \}(?:\n          if \(typeof mepIsMealRowId === 'function' && mepIsMealRowId\(rowId\)\) \{\n"
        r"            return;\n"
        r"          \})*\n"
        r"          var filtered = mepFilterIsoMap\(rowValueById\[rowId\], y\);"
    )
    new = (
        "          if (typeof mepIsIncomeCanonicalRowId === 'function' && mepIsIncomeCanonicalRowId(rowId)) {\n"
        "            return;\n"
        "          }\n"
        "          if (typeof mepIsMealRowId === 'function' && mepIsMealRowId(rowId)) {\n"
        "            return;\n"
        "          }\n"
        "          var filtered = mepFilterIsoMap(rowValueById[rowId], y);"
    )
    if not pattern.search(text):
        if new in text:
            return text
        raise ValueError("patch miss (buildMepPersistPayload skip meal)")
    return pattern.sub(new, text, count=1)


def patch_ensure_defaults(text: str) -> str:
    old_loop = """        Object.keys(rowValueById).forEach(function (rowId) {
          var m = rowValueById[rowId] || {};
          isoList.forEach(function (iso) {
            if (m[iso] == null) m[iso] = 0;
          });
          rowValueById[rowId] = m;
        });"""
    new_loop = """        Object.keys(rowValueById).forEach(function (rowId) {
          if (typeof mepIsMealRowId === 'function' && mepIsMealRowId(rowId)) return;
          var m = rowValueById[rowId] || {};
          isoList.forEach(function (iso) {
            if (m[iso] == null) m[iso] = 0;
          });
          rowValueById[rowId] = m;
        });"""
    text = replace_once(text, old_loop, new_loop, "ensureDefaults skip meal 0-fill")
    old_static = """        MEF_STATIC_INPUT_IDS.forEach(function (sid) {
          if (!rowValueById[sid]) rowValueById[sid] = {};
          var sm = rowValueById[sid];
          isoList.forEach(function (iso) {
            if (sm[iso] == null) sm[iso] = 0;
          });
          rowValueById[sid] = sm;
        });"""
    new_static = """        MEF_STATIC_INPUT_IDS.forEach(function (sid) {
          if (!rowValueById[sid]) rowValueById[sid] = {};
        });"""
    return replace_once(text, old_static, new_static, "ensureDefaults skip MEF_STATIC 0-fill")


def patch_read_write_value(text: str) -> str:
    old = """      function readValue(rowId, iso) {
        var byIso = rowValueById[rowId] || {};
        return Number(byIso[iso] || 0);
      }
      function writeValue(rowId, iso, v) {
        if (!rowValueById[rowId]) rowValueById[rowId] = {};
        rowValueById[rowId][iso] = Number(v) || 0;
      }"""
    new = """      function readValue(rowId, iso) {
        var byIso = rowValueById[rowId] || {};
        return Number(byIso[iso] || 0);
      }
      function writeValue(rowId, iso, v) {
        if (typeof mepIsMealPersistRowId === 'function' && mepIsMealPersistRowId(rowId)) {
          if (!rowValueById[rowId]) rowValueById[rowId] = {};
          if (v === undefined || v === null) {
            delete rowValueById[rowId][iso];
            return;
          }
          var mealN = Number(v);
          if (!Number.isFinite(mealN) || mealN < 0) return;
          rowValueById[rowId][iso] = Math.round(mealN);
          return;
        }
        if (!rowValueById[rowId]) rowValueById[rowId] = {};
        rowValueById[rowId][iso] = Number(v) || 0;
      }"""
    return replace_once(text, old, new, "writeValue meal 0 vs missing")


def patch_flush_inputs(text: str) -> str:
    old = """      function flushPendingMoneyInputsFromDom() {
        if (!root) return;
        root.querySelectorAll('input[data-action="money-input"]').forEach(function (inp) {
          var rowId = inp.getAttribute('data-row-id');
          var iso = inp.getAttribute('data-iso');
          if (!rowId || !iso) return;
          if (inp.disabled || inp.readOnly) return;
          writeValue(rowId, iso, parseMoney(inp.value));
        });
      }"""
    new = """      function flushPendingMoneyInputsFromDom() {
        if (!root) return;
        root.querySelectorAll('input[data-action="money-input"], input[data-action="count-input"]').forEach(function (inp) {
          var rowId = inp.getAttribute('data-row-id');
          var iso = inp.getAttribute('data-iso');
          if (!rowId || !iso) return;
          if (inp.disabled || inp.readOnly) return;
          if (typeof mepIsMealPersistRowId === 'function' && mepIsMealPersistRowId(rowId)) {
            mepWriteMealFromRawInput(rowId, iso, inp.value);
            return;
          }
          if (inp.getAttribute('data-action') === 'count-input') return;
          writeValue(rowId, iso, parseMoney(inp.value));
        });
      }"""
    return replace_once(text, old, new, "flushPendingMoneyInputsFromDom meal")


def patch_input_handlers(text: str) -> str:
    money_new = (
        "          pushUndo();\n"
        "          if (typeof mepIsMealPersistRowId === 'function' && mepIsMealPersistRowId(rowId)) {\n"
        "            mepWriteMealFromRawInput(rowId, iso2, target.value);\n"
        "          } else {\n"
        "            writeValue(rowId, iso2, parseMoney(target.value));\n"
        "          }\n"
        "          var streamIdForRow ="
    )
    money_orig = (
        "          pushUndo();\n"
        "          writeValue(rowId, iso2, parseMoney(target.value));\n"
        "          var streamIdForRow ="
    )
    money_nested = re.compile(
        r"          pushUndo\(\);\n"
        r"(?: *if \(typeof mepIsMealPersistRowId === 'function' && mepIsMealPersistRowId\(rowId\)\) \{\n"
        r" *mepWriteMealFromRawInput\(rowId, iso2, target\.value\);\n"
        r" *\} else \{\n)+"
        r" *writeValue\(rowId, iso2, parseMoney\(target\.value\)\);\n"
        r"(?: *\}\n)+"
        r"          var streamIdForRow ="
    )
    if money_orig in text:
        if text.count(money_orig) != 1:
            raise ValueError("money-input meal write orig not unique")
        text = text.replace(money_orig, money_new, 1)
    elif money_nested.search(text):
        text = money_nested.sub(money_new, text, count=1)
    elif money_new in text:
        pass
    else:
        raise ValueError("patch miss (money-input meal write)")

    count_new = (
        "          pushUndo();\n"
        "          if (typeof mepIsMealPersistRowId === 'function' && mepIsMealPersistRowId(rowIdC)) {\n"
        "            mepWriteMealFromRawInput(rowIdC, isoC, target.value);\n"
        "          } else {\n"
        "            writeValue(rowIdC, isoC, parseCount(target.value));\n"
        "          }\n"
        "          markDirty();"
    )
    count_orig = (
        "          pushUndo();\n"
        "          writeValue(rowIdC, isoC, parseCount(target.value));\n"
        "          markDirty();"
    )
    count_nested = re.compile(
        r"          pushUndo\(\);\n"
        r"(?: *if \(typeof mepIsMealPersistRowId === 'function' && mepIsMealPersistRowId\(rowIdC\)\) \{\n"
        r" *mepWriteMealFromRawInput\(rowIdC, isoC, target\.value\);\n"
        r" *\} else \{\n)+"
        r" *writeValue\(rowIdC, isoC, parseCount\(target\.value\)\);\n"
        r"(?: *\}\n)+"
        r"          markDirty\(\);"
    )
    if count_orig in text:
        if text.count(count_orig) != 1:
            raise ValueError("count-input meal write orig not unique")
        text = text.replace(count_orig, count_new, 1)
    elif count_nested.search(text):
        text = count_nested.sub(count_new, text, count=1)
    elif count_new in text:
        pass
    else:
        raise ValueError("patch miss (count-input meal write)")
    return text


def patch_dinner_row_defs(text: str) -> str:
    replacements = [
        (
            "            autoCalc: true,\n"
            "            autoCalcParent: 'salesRow',\n"
            "            autoCalcLunchId: 'incLunch',\n"
            "            valueKind: 'money',\n"
            "            autoCalcTitle: dinnerAutoCalcHint()",
            "            valueKind: 'money'",
            "incDinner autoCalc off",
        ),
        (
            "            autoCalc: true,\n"
            "            autoCalcParent: 'cust',\n"
            "            autoCalcLunchId: 'custLunch',\n"
            "            valueKind: 'count',\n"
            "            autoCalcTitle: dinnerAutoCalcHint()",
            "            valueKind: 'count'",
            "custDinner autoCalc off",
        ),
        (
            "            autoCalc: true,\n"
            "            autoCalcParent: 'groupCnt',\n"
            "            autoCalcLunchId: 'groupCntLunch',\n"
            "            valueKind: 'count',\n"
            "            autoCalcTitle: dinnerAutoCalcHint()",
            "            valueKind: 'count'",
            "groupCntDinner autoCalc off",
        ),
        (
            "            autoCalc: true,\n"
            "            autoCalcParent: 'pc',\n"
            "            autoCalcLunchId: 'pcLunch',\n"
            "            valueKind: 'money',\n"
            "            autoCalcTitle: dinnerAutoCalcHint()",
            "            autoCalc: true,\n"
            "            valueKind: 'money'",
            "pcDinner keep autoCalc drop parent-lunch",
        ),
    ]
    for old, new, label in replacements:
        if old not in text:
            continue
        text = replace_once(text, old, new, label)
    return text


def patch_lunch_row_defs(text: str) -> str:
    specs = [
        ("incLunch", "salesRow", "incDinner", "money"),
        ("custLunch", "cust", "custDinner", "count"),
        ("groupCntLunch", "groupCnt", "groupCntDinner", "count"),
    ]
    for row_id, parent, dinner_id, kind in specs:
        if f"autoCalcLunchId: '{dinner_id}'" in text and f"id: '{row_id}'" in text:
            block = text.split(f"id: '{row_id}'", 1)[1].split("rows.push({", 1)[0]
            if f"autoCalcLunchId: '{dinner_id}'" in block:
                continue
        pattern = re.compile(
            rf"(id: '{row_id}',(?:(?!rows\.push).)*?sub: true,\n)(            valueKind: '{kind}')",
            re.DOTALL,
        )
        repl = (
            rf"\1            autoCalc: true,\n"
            rf"            autoCalcParent: '{parent}',\n"
            rf"            autoCalcLunchId: '{dinner_id}',\n"
            rf"\2"
        )
        new_text, n = pattern.subn(repl, text, count=1)
        if n != 1:
            raise ValueError(f"patch miss ({row_id} derived autoCalc)")
        text = new_text
    return text


def patch_mef_static_input_ids(text: str) -> str:
    target = (
        "      var MEF_STATIC_INPUT_IDS = ['incDinner', 'cust', 'custDinner',"
        " 'groupCnt', 'groupCntDinner'];"
    )
    if target in text:
        return text
    candidates = [
        "      var MEF_STATIC_INPUT_IDS = ['incLunch', 'incDinner', 'cust', 'custLunch',"
        " 'custDinner', 'groupCnt', 'groupCntLunch', 'groupCntDinner'];",
        "      var MEF_STATIC_INPUT_IDS = ['incLunch', 'cust', 'custLunch', 'groupCnt', 'groupCntLunch'];",
    ]
    for old in candidates:
        if old in text:
            return replace_once(text, old, target, "MEF_STATIC_INPUT_IDS dinner hand input")
    raise ValueError("patch miss (MEF_STATIC_INPUT_IDS dinner hand input)")


def patch_pc_total_and_lunch_calc(text: str) -> str:
    old = """        if (rowId === 'pc') {
          sales =
            typeof mepIncomeReadValue === 'function'
              ? mepIncomeReadValue('store_sales', iso)
              : Math.round(Number(readValue(primarySalesRowId() || 'store_sales', iso)) || 0);
          cust = Math.round(Number(readValue('cust', iso)) || 0);
        } else if (rowId === 'pcLunch') {
          sales = Math.round(Number(readValue('incLunch', iso)) || 0);
          cust = Math.round(Number(readValue('custLunch', iso)) || 0);
        } else if (rowId === 'pcDinner') {"""
    new = """        if (rowId === 'pc') {
          if (
            typeof mepHasExplicitMealOrIncome !== 'function' ||
            typeof mepMealHasGridValue !== 'function' ||
            !mepHasExplicitMealOrIncome('store_sales', iso) ||
            !mepMealHasGridValue('cust', iso)
          ) {
            return null;
          }
          sales =
            typeof mepExplicitRoundedValue === 'function'
              ? mepExplicitRoundedValue('store_sales', iso)
              : Math.round(Number(readValue(primarySalesRowId() || 'store_sales', iso)) || 0);
          cust =
            typeof mepExplicitRoundedValue === 'function'
              ? mepExplicitRoundedValue('cust', iso)
              : Math.round(Number(readValue('cust', iso)) || 0);
          if (sales == null || cust == null) return null;
          if (!(cust > 0)) return null;
          if (!(sales > 0)) return 0;
          return Math.round(sales / cust);
        } else if (rowId === 'pcLunch') {
          if (
            typeof mepHasExplicitMealOrIncome !== 'function' ||
            typeof mepMealHasGridValue !== 'function' ||
            !mepHasExplicitMealOrIncome('store_sales', iso) ||
            !mepMealHasGridValue('cust', iso) ||
            !mepMealHasGridValue('incDinner', iso) ||
            !mepMealHasGridValue('custDinner', iso)
          ) {
            return null;
          }
          var totalSales =
            typeof mepExplicitRoundedValue === 'function'
              ? mepExplicitRoundedValue('store_sales', iso)
              : Math.round(Number(readValue(primarySalesRowId() || 'store_sales', iso)) || 0);
          var totalCust =
            typeof mepExplicitRoundedValue === 'function'
              ? mepExplicitRoundedValue('cust', iso)
              : Math.round(Number(readValue('cust', iso)) || 0);
          var dinnerSales =
            typeof mepExplicitRoundedValue === 'function'
              ? mepExplicitRoundedValue('incDinner', iso)
              : Math.round(Number(readValue('incDinner', iso)) || 0);
          var dinnerCust =
            typeof mepExplicitRoundedValue === 'function'
              ? mepExplicitRoundedValue('custDinner', iso)
              : Math.round(Number(readValue('custDinner', iso)) || 0);
          if (totalSales == null || totalCust == null || dinnerSales == null || dinnerCust == null) {
            return null;
          }
          sales = totalSales - dinnerSales;
          cust = totalCust - dinnerCust;
          if (!(cust > 0)) return null;
          if (!(sales > 0)) return 0;
          return Math.round(sales / cust);
        } else if (rowId === 'pcDinner') {"""
    if new in text and old not in text:
        return text
    return replace_once(text, old, new, "computeAvgSpendValue pc and pcLunch")


def patch_compute_static_auto_calc(text: str) -> str:
    old = """      function computeStaticAutoCalcValue(r, iso) {
        if (!r || !r.autoCalcLunchId) return 0;
        var lunchVal = readValue(r.autoCalcLunchId, iso);
        var parentVal = 0;
        if (r.autoCalcParent === 'salesRow') {
          parentVal =
            typeof mepIncomeReadValue === 'function'
              ? mepIncomeReadValue('store_sales', iso)
              : (function () {
                  var sid = primarySalesRowId();
                  return sid ? readValue(sid, iso) : 0;
                })();
        } else if (r.autoCalcParent) {
          parentVal = readValue(r.autoCalcParent, iso);
        }
        return Math.round(Number(parentVal) || 0) - Math.round(Number(lunchVal) || 0);
      }"""
    new = """      function computeStaticAutoCalcValue(r, iso) {
        if (!r || !r.autoCalcLunchId) return 0;
        if (typeof mepComputeDerivedLunchValue === 'function') {
          return mepComputeDerivedLunchValue(r, iso);
        }
        var lunchVal = readValue(r.autoCalcLunchId, iso);
        var parentVal = 0;
        if (r.autoCalcParent === 'salesRow') {
          parentVal =
            typeof mepIncomeReadValue === 'function'
              ? mepIncomeReadValue('store_sales', iso)
              : (function () {
                  var sid = primarySalesRowId();
                  return sid ? readValue(sid, iso) : 0;
                })();
        } else if (r.autoCalcParent) {
          parentVal = readValue(r.autoCalcParent, iso);
        }
        return Math.round(Number(parentVal) || 0) - Math.round(Number(lunchVal) || 0);
      }"""
    if new in text and old not in text:
        return text
    return replace_once(text, old, new, "computeStaticAutoCalcValue derived lunch")


def patch_grid_autocalc_empty(text: str) -> str:
    old = """                } else if (r.autoCalcLunchId) {
                  var autoVal = computeStaticAutoCalcValue(r, iso);
                  inp.value = autoKind === 'count' ? fmtCount(autoVal) : fmtMoney(autoVal);"""
    new = """                } else if (r.autoCalcLunchId) {
                  var autoVal = computeStaticAutoCalcValue(r, iso);
                  inp.value =
                    autoVal == null
                      ? ''
                      : autoKind === 'count'
                        ? fmtCount(autoVal)
                        : fmtMoney(autoVal);"""
    if new in text and old not in text:
        return text
    return replace_once(text, old, new, "autoCalc lunch empty when dinner missing")


def patch_pc_dinner_calc(text: str) -> str:
    old = """        } else if (rowId === 'pcDinner') {
          var store =
            typeof mepIncomeReadValue === 'function'
              ? mepIncomeReadValue('store_sales', iso)
              : Math.round(Number(readValue(primarySalesRowId() || 'store_sales', iso)) || 0);
          var lunch = Math.round(Number(readValue('incLunch', iso)) || 0);
          var custAll = Math.round(Number(readValue('cust', iso)) || 0);
          var custL = Math.round(Number(readValue('custLunch', iso)) || 0);
          sales = store - lunch;
          cust = custAll - custL;
        } else {
          return 0;
        }
        if (!(cust > 0) || !(sales > 0)) return 0;
        return Math.round(sales / cust);"""
    new = """        } else if (rowId === 'pcDinner') {
          if (
            typeof mepMealHasGridValue !== 'function' ||
            !mepMealHasGridValue('incDinner', iso) ||
            !mepMealHasGridValue('custDinner', iso)
          ) {
            return null;
          }
          var dinnerSalesMap = rowValueById.incDinner || {};
          var dinnerCustMap = rowValueById.custDinner || {};
          sales =
            typeof mepNormMealPersistValue === 'function'
              ? mepNormMealPersistValue(dinnerSalesMap[iso])
              : Math.round(Number(dinnerSalesMap[iso]));
          cust =
            typeof mepNormMealPersistValue === 'function'
              ? mepNormMealPersistValue(dinnerCustMap[iso])
              : Math.round(Number(dinnerCustMap[iso]));
          if (sales == null || cust == null) return null;
          if (!(cust > 0)) return null;
          if (!(sales > 0)) return 0;
          return Math.round(sales / cust);
        } else {
          return 0;
        }
        if (!(cust > 0) || !(sales > 0)) return 0;
        return Math.round(sales / cust);"""
    return replace_once(text, old, new, "computeAvgSpendValue pcDinner")


def patch_pc_dinner_display(text: str) -> str:
    old = """                if (r.id === 'pc' || r.id === 'pcLunch' || r.id === 'pcDinner') {
                  inp.value = fmtMoney(computeAvgSpendValue(r.id, iso));"""
    new = """                if (r.id === 'pc' || r.id === 'pcLunch' || r.id === 'pcDinner') {
                  var pcVal = computeAvgSpendValue(r.id, iso);
                  inp.value = pcVal == null ? '' : fmtMoney(pcVal);"""
    return replace_once(text, old, new, "pcDinner empty vs explicit 0")


MEP_MEAL_REF_CSS_BEGIN = "    /* KPI-MEP-MEAL-REF */"
MEP_MEAL_REF_CSS_END = "    /* /KPI-MEP-MEAL-REF */"


def patch_meal_ref_css(text: str) -> str:
    if MEP_MEAL_REF_CSS_BEGIN not in text:
        return text
    pattern = re.compile(
        re.escape(MEP_MEAL_REF_CSS_BEGIN)
        + r"[\s\S]*?"
        + re.escape(MEP_MEAL_REF_CSS_END)
        + r"\n"
    )
    if not pattern.search(text):
        raise ValueError("KPI-MEP-MEAL-REF BEGIN present but block not matched")
    return pattern.sub("", text, count=1)


def patch_dinner_ref_hint(text: str) -> str:
    injected = """              td.appendChild(inp);
              if (
                typeof mepIsDinnerPersistRowId === 'function' &&
                mepIsDinnerPersistRowId(r.id) &&
                typeof mepAppendDinnerRefHint === 'function'
              ) {
                mepAppendDinnerRefHint(td, r.id, iso);
              }
              if (isMepUiBusinessDay(iso)) {"""
    original = """              td.appendChild(inp);
              if (isMepUiBusinessDay(iso)) {"""
    if injected not in text:
        return text
    return replace_once(text, injected, original, "remove dinner ref hint")


def patch_unused_dinner_auto_calc_hint(text: str) -> str:
    pattern = re.compile(
        r"      function dinnerAutoCalcHint\(\) \{\n"
        r"        return t\([^)]+\);\n"
        r"      \}\n"
    )
    if not pattern.search(text):
        return text
    return pattern.sub("", text, count=1)


def patch_perform_mep_save_validation(text: str) -> str:
    old = """      function performMepSave() {
        return Promise.resolve()
          .then(function () {
            return runMepSaveTransaction();
          })"""
    new = """      function performMepSave() {
        return Promise.resolve()
          .then(function () {
            try {
              if (typeof flushPendingMoneyInputsFromDom === 'function') flushPendingMoneyInputsFromDom();
              if (typeof flushPendingMemoEditsFromDom === 'function') flushPendingMemoEditsFromDom();
              var mealErr =
                typeof mepValidateMealBreakdown === 'function' ? mepValidateMealBreakdown(mefYear) : null;
              if (mealErr) {
                mepSaveInProgress = false;
                window.alert(mealErr);
                return { ok: false };
              }
            } catch (_mealVal) {
              mepSaveInProgress = false;
              throw _mealVal;
            }
            return runMepSaveTransaction();
          })"""
    return replace_once(text, old, new, "performMepSave meal validation")


def patch_grid_display(text: str) -> str:
    old = """                if (kind === 'count') {
                  inp.value = fmtCount(readValue(r.id, iso));
                  inp.setAttribute('data-action', 'count-input');
                } else {
                  inp.value = fmtMoney(readValue(r.id, iso));
                  inp.setAttribute('data-action', 'money-input');
                }"""
    new = """                if (kind === 'count') {
                  inp.value =
                    typeof mepIsMealPersistRowId === 'function' &&
                    mepIsMealPersistRowId(r.id) &&
                    typeof mepMealHasGridValue === 'function' &&
                    !mepMealHasGridValue(r.id, iso)
                      ? ''
                      : fmtCount(readValue(r.id, iso));
                  inp.setAttribute('data-action', 'count-input');
                } else {
                  inp.value =
                    typeof mepIsMealPersistRowId === 'function' &&
                    mepIsMealPersistRowId(r.id) &&
                    typeof mepMealHasGridValue === 'function' &&
                    !mepMealHasGridValue(r.id, iso)
                      ? ''
                      : fmtMoney(readValue(r.id, iso));
                  inp.setAttribute('data-action', 'money-input');
                }"""
    return replace_once(text, old, new, "buildGrid meal missing display")


def patch_current_rows_business_type(text: str) -> str:
    """Skip generating restaurant meal / food-drink rows for non-restaurant BTs.

    Hide-only: currentRows omits rows so the grid reflows. dailyMeal is not deleted.
    """
    old_income = """          state.incomeItems.forEach(function (r) {
            rows.push({ type: 'moneyRow', row: r, section: 'income' });
          });"""
    new_income = """          state.incomeItems.forEach(function (r) {
            if (
              typeof mepEditShouldShowRestaurantMealUi === 'function' &&
              !mepEditShouldShowRestaurantMealUi() &&
              typeof mepEditIsRestaurantIncomeLineId === 'function' &&
              mepEditIsRestaurantIncomeLineId(r.lineId || r.id)
            ) {
              return;
            }
            rows.push({ type: 'moneyRow', row: r, section: 'income' });
          });"""
    text = replace_once(text, old_income, new_income, "currentRows skip restaurant income")

    meal_ui_open = (
        "          if (typeof mepEditShouldShowRestaurantMealUi !== 'function' || "
        "mepEditShouldShowRestaurantMealUi()) {\n"
    )
    lunch_open = """          rows.push({
            type: 'moneyStatic',
            id: 'incLunch',"""
    lunch_wrapped = meal_ui_open + lunch_open
    if lunch_wrapped not in text:
        text = replace_once(text, lunch_open, lunch_wrapped, "currentRows wrap lunch/dinner open")

    dinner_to_target = re.compile(
        r"(id: 'incDinner',[\s\S]*?          \}\);\n)"
        r"(          rows.push\(\{\n            type: 'moneyStatic',\n            id: 'target',)"
    )
    if dinner_to_target.search(text):
        text, n = dinner_to_target.subn(r"\1          }\n\2", text, count=1)
        if n != 1:
            raise ValueError("patch miss (currentRows wrap lunch/dinner close)")
    elif meal_ui_open in text and "id: 'incDinner'" in text:
        pass
    else:
        raise ValueError("patch miss (currentRows wrap lunch/dinner close)")

    cust_open = """          rows.push({
            type: 'moneyStatic',
            id: 'cust',"""
    cust_wrapped = meal_ui_open + cust_open
    if cust_wrapped not in text:
        text = replace_once(text, cust_open, cust_wrapped, "currentRows wrap customer/group open")

    group_to_exp = re.compile(
        r"(id: 'groupCntDinner',[\s\S]*?          \}\);\n)"
        r"(        \}\n        rows.push\(\{ type: 'group', id: 'g-exp')"
    )
    if group_to_exp.search(text):
        text, n = group_to_exp.subn(r"\1          }\n\2", text, count=1)
        if n != 1:
            raise ValueError("patch miss (currentRows wrap customer/group close)")
    elif "id: 'groupCntDinner'" in text and meal_ui_open in text:
        pass
    else:
        raise ValueError("patch miss (currentRows wrap customer/group close)")
    return text


def patch_one(text: str) -> str:
    text = patch_year_store_daily_meal_api(text)
    text = patch_ensure_year_mep_data(text)
    text = patch_load_mep_year_payload(text)
    text = patch_year_store_export(text)
    text = inject_runtime_helpers(text)
    text = patch_merge_payload(text)
    text = patch_collect_touched(text)
    text = patch_persist_mep_to_year_store(text)
    text = patch_build_mep_persist_payload(text)
    text = patch_ensure_defaults(text)
    text = patch_read_write_value(text)
    text = patch_flush_inputs(text)
    text = patch_input_handlers(text)
    text = patch_grid_display(text)
    text = patch_grid_autocalc_empty(text)
    text = patch_dinner_row_defs(text)
    text = patch_lunch_row_defs(text)
    text = patch_mef_static_input_ids(text)
    text = patch_pc_dinner_calc(text)
    text = patch_pc_total_and_lunch_calc(text)
    text = patch_pc_dinner_display(text)
    text = patch_compute_static_auto_calc(text)
    text = patch_dinner_ref_hint(text)
    text = patch_meal_ref_css(text)
    text = patch_unused_dinner_auto_calc_hint(text)
    text = patch_perform_mep_save_validation(text)
    text = patch_current_rows_business_type(text)
    return text


def main() -> int:
    extract_daily_meal_api_js()
    for t in TARGETS:
        if not t.is_file():
            print(f"missing: {t}", file=sys.stderr)
            return 1
        before = t.read_text(encoding="utf-8")
        after = patch_one(before)
        t.write_text(after, encoding="utf-8")
        print(f"patched {t.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

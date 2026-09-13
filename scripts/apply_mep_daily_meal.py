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

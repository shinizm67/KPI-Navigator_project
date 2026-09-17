# -*- coding: utf-8 -*-
"""MEP dailyMeal wiring — extract Unit 1 APIs from kpi_year_store_client.py.

readDailyMeal / writeDailyMeal の正本は kpi_year_store_client.py のみ。
このファイルは抽出と MEP 行マッピングだけを持ち、API 本体を複製しない。
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from kpi_year_store_client import kpi_year_store_js  # noqa: E402

MEP_DAILY_MEAL_BEGIN = "/* KPI-MEP-DAILY-MEAL */"
MEP_DAILY_MEAL_END = "/* /KPI-MEP-DAILY-MEAL */"

_DAILY_MEAL_API_START = "        var DAILY_MEAL_FIELDS = ["
_ENSURE_YEAR_MEP_DATA = "        function ensureYearMepData(year)"


def extract_daily_meal_api_js() -> str:
    """Return the Unit 1 dailyMeal function block from kpi_year_store_js()."""
    js = kpi_year_store_js()
    start = js.find(_DAILY_MEAL_API_START)
    end = js.find(_ENSURE_YEAR_MEP_DATA)
    if start < 0 or end < 0 or end <= start:
        raise ValueError("dailyMeal API block missing in kpi_year_store_client.py")
    block = js[start:end].rstrip()
    if "function readDailyMeal(" not in block or "function writeDailyMeal(" not in block:
        raise ValueError("extracted dailyMeal API is incomplete")
    if "function persistStore(" in block:
        raise ValueError("extracted dailyMeal API must not persist")
    return block + "\n"


def extract_ensure_daily_meal_maps_call() -> str:
    js = kpi_year_store_js()
    line = "          ensureDailyMealMaps(rec);"
    if line not in js:
        raise ValueError("ensureDailyMealMaps(rec) missing in kpi_year_store_client.py")
    return line


def extract_load_mep_daily_meal_line() -> str:
    js = kpi_year_store_js()
    line = "            dailyMeal: JSON.parse(JSON.stringify(ensureDailyMealMaps(rec) || {})),"
    if line not in js:
        raise ValueError("loadMepYearPayload dailyMeal line missing in kpi_year_store_client.py")
    return line


def extract_export_daily_meal_lines() -> str:
    js = kpi_year_store_js()
    block = "          readDailyMeal: readDailyMeal,\n          writeDailyMeal: writeDailyMeal,"
    if block not in js:
        raise ValueError("KpiYearStore dailyMeal exports missing in kpi_year_store_client.py")
    return block


def mep_daily_meal_runtime_js() -> str:
    """MEP grid mapping / hydrate / persist helpers. Does not reimplement year-store APIs."""
    return f"""      {MEP_DAILY_MEAL_BEGIN}
      var MEP_MEAL_ROW_TO_FIELD = {{
        incLunch: 'lunch_sales',
        incDinner: 'dinner_sales',
        cust: 'total_customers',
        custLunch: 'lunch_customers',
        custDinner: 'dinner_customers',
        groupCnt: 'total_groups',
        groupCntLunch: 'lunch_groups',
        groupCntDinner: 'dinner_groups'
      }};
      var MEP_MEAL_PERSIST_ROW_IDS = [
        'incDinner',
        'cust',
        'custDinner',
        'groupCnt',
        'groupCntDinner'
      ];
      var MEP_MEAL_LUNCH_ROW_IDS = ['incLunch', 'custLunch', 'groupCntLunch'];
      var MEP_MEAL_DINNER_ROW_IDS = ['incDinner', 'custDinner', 'groupCntDinner'];
      var MEP_MEAL_BREAKDOWN_TRIPLES = [
        {{ total: 'store_sales', lunch: 'incLunch', dinner: 'incDinner', kind: 'money' }},
        {{ total: 'cust', lunch: 'custLunch', dinner: 'custDinner', kind: 'count' }},
        {{ total: 'groupCnt', lunch: 'groupCntLunch', dinner: 'groupCntDinner', kind: 'count' }}
      ];
      var MEP_MEAL_SKIP_EXPENSE_ROW_IDS = [
        'incLunch',
        'incDinner',
        'cust',
        'custLunch',
        'custDinner',
        'groupCnt',
        'groupCntLunch',
        'groupCntDinner'
      ];
      function mepIsMealRowId(rowId) {{
        return MEP_MEAL_SKIP_EXPENSE_ROW_IDS.indexOf(String(rowId || '')) >= 0;
      }}
      function mepEditIsRestaurantLike() {{
        try {{
          if (window.KpiBusinessType && typeof window.KpiBusinessType.isRestaurantLike === 'function') {{
            return !!window.KpiBusinessType.isRestaurantLike();
          }}
        }} catch (_eRest) {{}}
        return true;
      }}
      function mepEditShouldShowRestaurantMealUi() {{
        return mepEditIsRestaurantLike();
      }}
      function mepEditIsRestaurantIncomeLineId(lineId) {{
        var id = String(lineId || '');
        return id === 'food_sales' || id === 'drink_sales';
      }}
      function mepEditIsRestaurantMealUiRowId(rowId) {{
        var id = String(rowId || '');
        if (mepIsMealRowId(id)) return true;
        return id === 'pc' || id === 'pcLunch' || id === 'pcDinner';
      }}
      function mepIsMealPersistRowId(rowId) {{
        return MEP_MEAL_PERSIST_ROW_IDS.indexOf(String(rowId || '')) >= 0;
      }}
      function mepNormMealPersistValue(v) {{
        var n = Number(v);
        if (!Number.isFinite(n) || n < 0) return null;
        return Math.round(n);
      }}
      function mepMealHasGridValue(rowId, iso) {{
        var byIso = rowValueById[rowId];
        return !!(byIso && Object.prototype.hasOwnProperty.call(byIso, iso));
      }}
      function mepMealRawIsBlank(text) {{
        return String(text == null ? '' : text).replace(/[^\\d.-]/g, '') === '';
      }}
      function mepWriteMealFromRawInput(rowId, iso, rawText) {{
        if (!mepIsMealPersistRowId(rowId)) return;
        if (mepMealRawIsBlank(rawText)) {{
          writeValue(rowId, iso, null);
          return;
        }}
        if (rowId === 'incDinner') writeValue(rowId, iso, parseMoney(rawText));
        else writeValue(rowId, iso, parseCount(rawText));
      }}
      function mepIsLunchDerivedRowId(rowId) {{
        return MEP_MEAL_LUNCH_ROW_IDS.indexOf(String(rowId || '')) >= 0;
      }}
      function mepIsMealHydrateRowId(rowId) {{
        return Object.prototype.hasOwnProperty.call(MEP_MEAL_ROW_TO_FIELD, String(rowId || ''));
      }}
      function mepComputeDerivedLunchValue(r, iso) {{
        if (!r || !r.autoCalcLunchId) return null;
        var dinnerId = r.autoCalcLunchId;
        var hasD = mepMealHasGridValue(dinnerId, iso);
        var hasT =
          r.autoCalcParent === 'salesRow'
            ? mepHasExplicitMealOrIncome('store_sales', iso)
            : mepMealHasGridValue(r.autoCalcParent, iso);
        if (!hasT || !hasD) return null;
        var tVal =
          r.autoCalcParent === 'salesRow'
            ? mepExplicitRoundedValue('store_sales', iso)
            : mepExplicitRoundedValue(r.autoCalcParent, iso);
        var dVal = mepExplicitRoundedValue(dinnerId, iso);
        if (tVal == null || dVal == null) return null;
        return tVal - dVal;
      }}
      function mepHasExplicitMealOrIncome(rowId, iso) {{
        if (rowId === 'store_sales') {{
          var rid = typeof mepStreamRowId === 'function' ? mepStreamRowId('store_sales') : 'store_sales';
          var byIso = rowValueById[rid] || rowValueById.store_sales;
          if (byIso && Object.prototype.hasOwnProperty.call(byIso, iso)) return true;
          try {{
            if (window.KpiYearStore && typeof KpiYearStore.readDailyIncome === 'function') {{
              return KpiYearStore.readDailyIncome('store_sales', iso) != null;
            }}
          }} catch (_eInc) {{}}
          return false;
        }}
        return mepMealHasGridValue(rowId, iso);
      }}
      function mepExplicitRoundedValue(rowId, iso) {{
        if (rowId === 'store_sales') {{
          if (typeof mepIncomeReadValue === 'function') {{
            return Math.round(Number(mepIncomeReadValue('store_sales', iso)) || 0);
          }}
          return Math.round(Number(typeof readValue === 'function' ? readValue('store_sales', iso) : 0) || 0);
        }}
        var map = rowValueById[rowId] || {{}};
        return mepNormMealPersistValue(map[iso]);
      }}
      function mepMealBreakdownErrorMessage() {{
        return t(
          '合計と内訳が一致しません。値は自動修正しません。',
          'Total and breakdown do not match. Values are not auto-corrected.',
          '合計與明細不一致。不會自動修正。'
        );
      }}
      function mepMealExceedsTotalMessage() {{
        return t(
          '内訳が合計を超えています。',
          'Breakdown exceeds total.',
          '明細超過合計。'
        );
      }}
      function mepValidateMealTripleIso(triple, iso) {{
        var hasT = mepHasExplicitMealOrIncome(triple.total, iso);
        var hasL = mepHasExplicitMealOrIncome(triple.lunch, iso);
        var hasD = mepHasExplicitMealOrIncome(triple.dinner, iso);
        var tVal = hasT ? mepExplicitRoundedValue(triple.total, iso) : null;
        var lVal = hasL ? mepExplicitRoundedValue(triple.lunch, iso) : null;
        var dVal = hasD ? mepExplicitRoundedValue(triple.dinner, iso) : null;
        if (hasT && hasL && lVal != null && tVal != null && lVal > tVal) return mepMealExceedsTotalMessage();
        if (hasT && hasD && dVal != null && tVal != null && dVal > tVal) return mepMealExceedsTotalMessage();
        if (
          hasT &&
          hasL &&
          hasD &&
          tVal != null &&
          lVal != null &&
          dVal != null &&
          lVal + dVal !== tVal
        ) {{
          return mepMealBreakdownErrorMessage();
        }}
        return null;
      }}
      function mepValidateMealBreakdown(year) {{
        if (typeof mepEditShouldShowRestaurantMealUi === 'function' && !mepEditShouldShowRestaurantMealUi()) {{
          return null;
        }}
        var y = Number(year);
        if (!Number.isFinite(y)) y = typeof mefYear !== 'undefined' ? Number(mefYear) : NaN;
        if (!Number.isFinite(y) || typeof monthIsoList !== 'function') return null;
        for (var m0 = 0; m0 < 12; m0++) {{
          var isos = monthIsoList(y, m0);
          for (var i = 0; i < isos.length; i++) {{
            var iso = isos[i];
            for (var ti = 0; ti < MEP_MEAL_BREAKDOWN_TRIPLES.length; ti++) {{
              var err = mepValidateMealTripleIso(MEP_MEAL_BREAKDOWN_TRIPLES[ti], iso);
              if (err) return iso + ' — ' + err;
            }}
          }}
        }}
        return null;
      }}
      function mepTouchedDailyMealHasValues(touched) {{
        var meal = touched && touched.dailyMeal;
        if (!meal || typeof meal !== 'object') return false;
        var fields = Object.keys(meal);
        for (var i = 0; i < fields.length; i++) {{
          var byIso = meal[fields[i]];
          if (byIso && typeof byIso === 'object' && Object.keys(byIso).length) return true;
        }}
        return false;
      }}
      function mepCollectMealTouchedIso(out, rowId, iso, curMap, baseMap) {{
        if (!mepIsMealRowId(rowId)) return false;
        if (typeof mepEditShouldShowRestaurantMealUi === 'function' && !mepEditShouldShowRestaurantMealUi()) {{
          return true;
        }}
        if (!mepIsMealPersistRowId(rowId)) return true;
        var curHas = Object.prototype.hasOwnProperty.call(curMap, iso);
        var baseHas = Object.prototype.hasOwnProperty.call(baseMap, iso);
        var curVal = curHas ? mepNormMealPersistValue(curMap[iso]) : null;
        var baseVal = baseHas ? mepNormMealPersistValue(baseMap[iso]) : null;
        if (curHas === baseHas && curVal === baseVal) return true;
        var field = MEP_MEAL_ROW_TO_FIELD[rowId];
        if (!field) return true;
        if (!out.dailyMeal) out.dailyMeal = {{}};
        if (!out.dailyMeal[field]) out.dailyMeal[field] = {{}};
        out.dailyMeal[field][iso] = curHas ? curVal : null;
        return true;
      }}
      function mergeMepDailyMealFromPayload(payload, year) {{
        var y = Number(year);
        if (!Number.isFinite(y) && typeof mefYear !== 'undefined') y = Number(mefYear);
        MEP_MEAL_SKIP_EXPENSE_ROW_IDS.forEach(function (rowId) {{
          if (!mepIsMealHydrateRowId(rowId)) {{
            if (rowValueById[rowId] && Number.isFinite(y)) {{
              Object.keys(rowValueById[rowId]).forEach(function (iso) {{
                if (typeof mepIsoYear === 'function' && mepIsoYear(iso) === y) {{
                  delete rowValueById[rowId][iso];
                }}
              }});
            }}
            return;
          }}
          if (!rowValueById[rowId]) rowValueById[rowId] = {{}};
          var dest = rowValueById[rowId];
          if (Number.isFinite(y)) {{
            Object.keys(dest).forEach(function (iso) {{
              if (typeof mepIsoYear === 'function' && mepIsoYear(iso) === y) delete dest[iso];
            }});
          }}
          var field = MEP_MEAL_ROW_TO_FIELD[rowId];
          var src = payload && payload.dailyMeal && payload.dailyMeal[field];
          if (!src || typeof src !== 'object') return;
          Object.keys(src).forEach(function (iso) {{
            if (!Object.prototype.hasOwnProperty.call(src, iso)) return;
            if (Number.isFinite(y) && typeof mepIsoYear === 'function' && mepIsoYear(iso) !== y) return;
            var n = Number(src[iso]);
            if (!Number.isFinite(n)) return;
            dest[iso] = Math.round(n);
          }});
        }});
      }}
      function persistMepMealToYearStore(touched) {{
        var meal = touched && touched.dailyMeal;
        if (!meal || typeof meal !== 'object') return true;
        if (typeof mepEditShouldShowRestaurantMealUi === 'function' && !mepEditShouldShowRestaurantMealUi()) {{
          return true;
        }}
        if (!window.KpiYearStore || typeof KpiYearStore.writeDailyMeal !== 'function') return false;
        Object.keys(meal).forEach(function (field) {{
          var byIso = meal[field];
          if (!byIso || typeof byIso !== 'object') return;
          Object.keys(byIso).forEach(function (iso) {{
            KpiYearStore.writeDailyMeal(field, iso, byIso[iso]);
          }});
        }});
        return true;
      }}
      {MEP_DAILY_MEAL_END}
"""

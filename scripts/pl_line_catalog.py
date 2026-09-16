"""Shared income / expense line catalog for PL table and Monthly Edit Page.

PL is the parent expense master. MEP mirrors the selected PL catalog.
Business Type selects a PL default-expense *preset*; it does not create a
second MEP master.

Unit 5B-1: restaurant preset is the current production set. Other canonical
types are registered as unset so 5B-2 can drop in real titles later without
inventing placeholder names in the UI.
"""

from __future__ import annotations

import json
from typing import Any

# Bump when default line list / isDefault / expenseAttribute / active / inputStyle defaults change.
CATALOG_SCHEMA_VERSION = 8

# Same 6 codes as js/kpi-business-type.js.
BUSINESS_TYPE_CANONICAL: tuple[str, ...] = (
    "restaurant",
    "retail",
    "hair_salon",
    "fitness",
    "hotel",
    "other",
)
FALLBACK_BUSINESS_TYPE = "restaurant"
BUSINESS_TYPE_LEGACY: dict[str, str] = {
    "restaurant": "restaurant",
    "cafe": "restaurant",
    "wear_shop": "retail",
    "retail": "retail",
    "personal_trainer": "fitness",
    "fitness": "fitness",
}

# (attrId, labelJa, labelEn) — fixed expense attributes for FL / KPI grouping
FIXED_EXPENSE_ATTRIBUTES: list[tuple[str, str, str]] = [
    ("occupancy", "店舗物件費", "Occupancy"),
    ("property_tax", "資産税", "Property Tax"),
    ("salaries_wages", "給与・賃金", "Salaries & Wages"),
    ("lease", "リース料", "Lease"),
    ("depreciation", "減価償却費", "Depreciation"),
    ("insurance", "保険料", "Insurance"),
    ("labor_related", "人件費関連費", "Labor-Related Costs"),
]

# (attrId, labelJa, labelEn) — variable expense attributes (UI edit: next phase)
VARIABLE_EXPENSE_ATTRIBUTES: list[tuple[str, str, str]] = [
    ("food_cost", "食材仕入費", "Food Cost"),
    ("drink_cost", "ドリンク仕入費", "Drink Cost"),
    ("supplies", "備品・消耗品費", "Supplies & Consumables"),
    ("miscellaneous", "雑費", "Miscellaneous Expenses"),
    ("utilities", "光熱水道費", "Utilities"),
    ("variable_labor", "変動人件費", "Variable Labor"),
    ("communication", "通信費", "Communication"),
    ("advertising", "広告・マーケティング費", "Advertising"),
    ("uniforms", "制服・業務用被服費", "Uniforms & Workwear"),
    ("payment_fees", "決済手数料", "Payment Processing Fees"),
    ("labor_related", "人件費関連費", "Labor-Related Costs"),
    ("taxes", "税金", "Taxes"),
]

# (lineId, labelJa, labelEn, editableLabel, isTotal)
INCOME_ROWS_V1: list[tuple[str, str, str, bool, bool]] = [
    ("store_sales", "店舗売上", "Store Sales", False, False),
    ("sales_a", "売上A", "Sales A", True, False),
    ("sales_b", "売上B", "Sales B", True, False),
    ("food_sales", "フード売上", "Food Sales", False, False),
    ("drink_sales", "ドリンク売上", "Drink Sales", False, False),
    ("sales_total", "売上合計", "Total Sales", False, True),
]

# Food/Drink は MEP 日次入力＋PL Analyze 配線用。PL 収入ブロック（店舗/A/B/合計）には出さない。
PL_INCOME_TABLE_EXCLUDE: frozenset[str] = frozenset({"food_sales", "drink_sales"})

# MEP 上の drink_sales は Store − Food の AUTO CALC（緑行ではない）
MEP_INCOME_AUTO_CALC_IDS: frozenset[str] = frozenset({"drink_sales"})

EXPENSES_SUMMARY_ROWS_V1: list[tuple[str, str, str, bool, bool]] = [
    ("expense_fixed", "固定費", "Fixed", False, False),
    ("expense_expected", "変動費", "Expected", False, False),
    ("expenses_total", "総支出", "Total Expenses", False, True),
]

# (lineId, labelJa, labelEn, bucket, inputStyle, isDefault, expenseAttribute)
# inputStyle: daily = MEP 日次 / monthly = PL 月次（緑背景）
# expenseAttribute: see FIXED_EXPENSE_ATTRIBUTES / VARIABLE_EXPENSE_ATTRIBUTES
# PDF ver4 支出項目リスト準拠
EXPENSE_DETAIL_LINES_V1: list[tuple[str, str, str, str, str, bool, str | None]] = [
    # --- 固定費（すべて PL 月次 = 緑） ---
    ("exp_rent", "家賃", "Rent", "fixed", "monthly", True, "occupancy"),
    ("exp_fixed_asset_tax", "固定資産税", "Fixed asset tax", "fixed", "monthly", False, "labor_related"),
    ("exp_fixed_labor", "固定人件費", "Fixed Labor", "fixed", "monthly", True, "salaries_wages"),
    ("exp_lease", "リース料", "Lease", "fixed", "monthly", False, "lease"),
    ("exp_depreciable_asset_tax", "償却資産税", "Depreciable asset tax", "fixed", "monthly", False, "property_tax"),
    ("exp_depreciation", "減価償却費", "Depreciation expenses", "fixed", "monthly", False, "depreciation"),
    ("exp_non_life_insurance", "損害保険", "Non-life insurance", "fixed", "monthly", True, "insurance"),
    ("exp_social_insurance", "社会保険", "social insurance", "fixed", "monthly", False, "insurance"),
    # --- 変動費 ---
    # FL 近傍（日次が本命・月次切替可）: 食材 / ドリンク / アルバイト
    # それ以外の変動費・固定費は月次請求が自然 → monthly
    ("exp_food_cost", "食材仕入れ費", "Food cost", "variable", "daily", True, "food_cost"),
    ("exp_drink_cost", "ドリンク仕入れ費", "Drink Cost", "variable", "daily", True, "drink_cost"),
    ("exp_supplies", "備品・消耗品仕入費", "Supplies & Consumables", "variable", "monthly", True, "supplies"),
    ("exp_misc", "雑費・小口精算費", "Miscellaneous Expense", "variable", "monthly", True, "miscellaneous"),
    ("exp_electric", "電気代", "Electricity Cost", "variable", "monthly", True, "utilities"),
    ("exp_gas", "ガス代", "Gas Cost", "variable", "monthly", True, "utilities"),
    ("exp_water", "水道代", "Water Cost", "variable", "monthly", True, "utilities"),
    ("exp_variable_labor", "アルバイト人件費", "Variable Labor", "variable", "daily", True, "variable_labor"),
    ("exp_telecom", "通信費", "Communication", "variable", "monthly", True, "communication"),
    ("exp_advertising", "広告宣伝費", "Advertising", "variable", "monthly", True, "advertising"),
    ("exp_uniforms", "被服費", "Uniforms & Workwear", "variable", "monthly", False, "uniforms"),
    ("exp_payment_fees", "クレジットカード手数料", "Payment Processing Fees", "variable", "monthly", True, "payment_fees"),
    ("exp_employment_insurance", "雇用保険", "employment insurance", "variable", "monthly", False, "labor_related"),
    ("exp_workers_comp", "労災保険", "Worker's compensation insurance", "variable", "monthly", False, "labor_related"),
    ("exp_consumption_tax", "消費税", "consumption tax", "variable", "monthly", False, "taxes"),
]

# Restaurant alias — existing call sites and generators keep using EXPENSE_DETAIL_LINES_V1.
RESTAURANT_EXPENSE_DETAIL_LINES = EXPENSE_DETAIL_LINES_V1

# Unit 5B-2: replace None with a tuple list of the same 7-field contract.
# None means "preset unset" — do not invent UI titles, do not copy restaurant Food/Drink.
EXPENSE_PRESET_LINES: dict[str, list[tuple[str, str, str, str, str, bool, str | None]] | None] = {
    "restaurant": EXPENSE_DETAIL_LINES_V1,
    "retail": None,
    "hair_salon": None,
    "fitness": None,
    "hotel": None,
    "other": None,
}


def resolve_input_style(raw: str, line_id: str, bucket: str) -> str:
    if raw == "daily":
        return "daily"
    return "monthly"


def normalize_business_type_for_preset(business_type: str | None) -> str:
    """Unknown / empty → restaurant. Canonical codes pass through (even if unset)."""
    raw = str(business_type or "").strip()
    if raw in BUSINESS_TYPE_CANONICAL:
        return raw
    mapped = BUSINESS_TYPE_LEGACY.get(raw) or BUSINESS_TYPE_LEGACY.get(raw.lower())
    if mapped:
        return mapped
    return FALLBACK_BUSINESS_TYPE


def has_defined_expense_preset(business_type: str | None) -> bool:
    key = normalize_business_type_for_preset(business_type)
    return EXPENSE_PRESET_LINES.get(key) is not None


def get_default_expense_lines(
    business_type: str | None = FALLBACK_BUSINESS_TYPE,
) -> list[tuple[str, str, str, str, str, bool, str | None]]:
    """Return the default expense *tuples* for a Business Type.

    restaurant / unknown → current restaurant set (full backward compatibility).
    canonical with unset preset → empty list (no placeholder names).
    """
    key = normalize_business_type_for_preset(business_type)
    preset = EXPENSE_PRESET_LINES.get(key)
    if preset is None:
        return []
    return list(preset)


def catalog_from_expense_tuples(
    rows: list[tuple[str, str, str, str, str, bool, str | None]],
) -> list[dict[str, Any]]:
    fixed_i = 0
    var_i = 0
    out: list[dict[str, Any]] = []
    for lid, ja, en, bucket, input_style, is_default, expense_attr in rows:
        if bucket == "fixed":
            order = fixed_i
            fixed_i += 1
        else:
            order = var_i
            var_i += 1
        resolved = resolve_input_style(input_style, lid, bucket)
        entry: dict[str, Any] = {
            "lineId": lid,
            "labelJa": ja,
            "labelEn": en,
            "bucket": bucket,
            "inputStyle": input_style,
            "resolvedInputStyle": resolved,
            "isDefault": is_default,
            "active": is_default,
            "sortOrder": order,
        }
        if expense_attr is not None:
            entry["expenseAttribute"] = expense_attr
        out.append(entry)
    return out


def expense_detail_default_catalog(
    business_type: str | None = FALLBACK_BUSINESS_TYPE,
) -> list[dict[str, Any]]:
    return catalog_from_expense_tuples(get_default_expense_lines(business_type))


def expense_presets_payload() -> dict[str, Any]:
    """JSON-serializable preset map for the runtime selector (5B-2 fills unset)."""
    out: dict[str, Any] = {}
    for code in BUSINESS_TYPE_CANONICAL:
        preset = EXPENSE_PRESET_LINES.get(code)
        if preset is None:
            out[code] = {"status": "unset", "lines": []}
        else:
            out[code] = {"status": "defined", "lines": catalog_from_expense_tuples(list(preset))}
    return out


def reconcile_catalog_lines(
    old_lines: list[dict[str, Any]] | None,
    business_type: str | None = FALLBACK_BUSINESS_TYPE,
    *,
    localized_defaults: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Merge stored catalog with the selected preset.

    - Current-preset defaults are upserted (user active/inputStyle/labels kept).
    - Custom ``exp_custom_*`` lines are kept.
    - Previous defaults missing from the new preset are kept with active=false
      (``presetOrphan``) so amounts keyed by lineId are not dropped.
    """
    defaults = (
        localized_defaults
        if localized_defaults is not None
        else expense_detail_default_catalog(business_type)
    )
    default_label_keys: set[str] = set()
    for d in defaults:
        default_label_keys.add(f"{d.get('bucket')}\0{str(d.get('labelEn') or '').lower()}")
        default_label_keys.add(f"{d.get('bucket')}\0{str(d.get('labelJa') or '')}")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    old = list(old_lines or [])
    for defn in defaults:
        prev = next((l for l in old if l.get("lineId") == defn.get("lineId")), None)
        line = json.loads(json.dumps(defn))
        if prev:
            if prev.get("presetOrphan"):
                line["active"] = defn.get("active")
            elif isinstance(prev.get("active"), bool):
                line["active"] = prev["active"]
            if isinstance(prev.get("sortOrder"), (int, float)):
                line["sortOrder"] = prev["sortOrder"]
            if prev.get("labelJa"):
                line["labelJa"] = prev["labelJa"]
            if prev.get("labelEn"):
                line["labelEn"] = prev["labelEn"]
            if prev.get("expenseAttribute"):
                line["expenseAttribute"] = prev["expenseAttribute"]
            if prev.get("inputStyle") in ("daily", "monthly"):
                line["inputStyle"] = prev["inputStyle"]
            if prev.get("resolvedInputStyle") in ("daily", "monthly"):
                line["resolvedInputStyle"] = prev["resolvedInputStyle"]
            elif line.get("inputStyle") in ("daily", "monthly"):
                line["resolvedInputStyle"] = line["inputStyle"]
        if line.get("expenseAttribute") is None:
            line.pop("expenseAttribute", None)
        line.pop("presetOrphan", None)
        out.append(line)
        seen.add(str(line.get("lineId") or ""))
    for line in old:
        lid = str(line.get("lineId") or "")
        if not lid or lid in seen:
            continue
        if lid.startswith("exp_custom_"):
            key_en = f"{line.get('bucket')}\0{str(line.get('labelEn') or '').lower()}"
            key_ja = f"{line.get('bucket')}\0{str(line.get('labelJa') or '')}"
            if key_en in default_label_keys or key_ja in default_label_keys:
                continue
            kept = json.loads(json.dumps(line))
            kept["isDefault"] = False
            if not kept.get("resolvedInputStyle"):
                kept["resolvedInputStyle"] = "daily" if kept.get("inputStyle") == "daily" else "monthly"
            out.append(kept)
            seen.add(lid)
            continue
        kept = json.loads(json.dumps(line))
        kept["active"] = False
        kept["presetOrphan"] = True
        if not kept.get("resolvedInputStyle"):
            kept["resolvedInputStyle"] = "daily" if kept.get("inputStyle") == "daily" else "monthly"
        out.append(kept)
        seen.add(lid)
    return out


def mep_catalog_entries(
    business_type: str | None = FALLBACK_BUSINESS_TYPE,
) -> list[dict[str, Any]]:
    """Catalog rows rendered on Monthly Edit (structure mirrors PL; daily rows editable)."""
    rows: list[dict[str, Any]] = []
    for lid, ja, en, editable, is_total in INCOME_ROWS_V1:
        if is_total:
            continue
        auto_calc = lid in MEP_INCOME_AUTO_CALC_IDS
        rows.append(
            {
                "lineId": lid,
                "section": "income",
                "bucket": None,
                "labelJa": ja,
                "labelEn": en,
                "editableLabel": editable,
                "inputStyle": "daily",
                "resolvedInputStyle": "daily",
                "mepEditable": not auto_calc,
                "mepAutoCalc": auto_calc,
            }
        )
    for item in expense_detail_default_catalog(business_type):
        rows.append(
            {
                "lineId": item["lineId"],
                "section": "expense",
                "bucket": item["bucket"],
                "labelJa": item["labelJa"],
                "labelEn": item["labelEn"],
                "editableLabel": False,
                "inputStyle": item["inputStyle"],
                "resolvedInputStyle": item["resolvedInputStyle"],
                "mepEditable": item["resolvedInputStyle"] == "daily",
                "active": item.get("active", True),
            }
        )
    return rows


def mep_catalog_js() -> str:
    return json.dumps(mep_catalog_entries(), ensure_ascii=False, indent=2)


def presets_runtime_js() -> str:
    """Runtime selector consumed by PL / MEP. 5B-2 only needs to fill EXPENSE_PRESET_LINES."""
    payload = json.dumps(expense_presets_payload(), ensure_ascii=False)
    canonical = json.dumps(list(BUSINESS_TYPE_CANONICAL), ensure_ascii=False)
    fallback = json.dumps(FALLBACK_BUSINESS_TYPE)
    legacy = json.dumps(BUSINESS_TYPE_LEGACY, ensure_ascii=False)
    return f"""/**
 * PL expense preset selector (Unit 5B-1).
 * Source of truth: scripts/pl_line_catalog.py — regenerate with
 * scripts/build_kpi_pl_expense_presets.py (this file only).
 *
 * Restaurant lines match EXPENSE_DETAIL_LINES_V1. Non-restaurant presets
 * are status=unset until Unit 5B-2 fills titles. Do not invent names here.
 */
(function (global) {{
  'use strict';

  if (global.KpiPlExpensePresets && global.KpiPlExpensePresets.__ready) {{
    return;
  }}

  var CANONICAL = {canonical};
  var FALLBACK = {fallback};
  var LEGACY = {legacy};
  var PRESETS = {payload};

  function resolveBusinessType() {{
    if (global.KpiBusinessType && typeof global.KpiBusinessType.getBusinessType === 'function') {{
      try {{
        var fromHelper = global.KpiBusinessType.getBusinessType();
        if (fromHelper) return String(fromHelper);
      }} catch (_e) {{}}
    }}
    return FALLBACK;
  }}

  function presetKey(businessType) {{
    var key = String(businessType || '').trim();
    if (global.KpiBusinessType && typeof global.KpiBusinessType.normalizeBusinessType === 'function') {{
      try {{
        var n = global.KpiBusinessType.normalizeBusinessType(key);
        if (n) key = String(n);
      }} catch (_eNorm) {{}}
    }}
    if (CANONICAL.indexOf(key) >= 0) return key;
    if (LEGACY[key]) return LEGACY[key];
    if (LEGACY[key.toLowerCase()]) return LEGACY[key.toLowerCase()];
    return FALLBACK;
  }}

  function hasDefinedPreset(businessType) {{
    var rec = PRESETS[presetKey(businessType == null ? resolveBusinessType() : businessType)];
    return !!(rec && rec.status === 'defined');
  }}

  function getDefaultExpenseLines(businessType) {{
    var rec = PRESETS[presetKey(businessType == null ? resolveBusinessType() : businessType)];
    var lines = (rec && rec.lines) || [];
    try {{
      return JSON.parse(JSON.stringify(lines));
    }} catch (_eCopy) {{
      return [];
    }}
  }}

  function isCustomLineId(lineId) {{
    return String(lineId || '').indexOf('exp_custom_') === 0;
  }}

  function keepDefaultLabels() {{
    try {{
      var lang = String(
        (global.document && global.document.documentElement &&
          global.document.documentElement.getAttribute('lang')) || ''
      ).toLowerCase();
      return lang.indexOf('zh') === 0;
    }} catch (_eLang) {{
      return false;
    }}
  }}

  function reconcileCatalogLines(oldLines, businessType, localizedDefaults) {{
    var defaults = Array.isArray(localizedDefaults)
      ? localizedDefaults
      : getDefaultExpenseLines(businessType);
    var freezeLabels = keepDefaultLabels();
    var defaultLabelKeys = {{}};
    defaults.forEach(function (d) {{
      defaultLabelKeys[d.bucket + '\\0' + String(d.labelEn || '').toLowerCase()] = true;
      defaultLabelKeys[d.bucket + '\\0' + String(d.labelJa || '')] = true;
    }});
    var out = [];
    var seenIds = {{}};
    defaults.forEach(function (def) {{
      var prev = (oldLines || []).find(function (l) {{ return l && l.lineId === def.lineId; }});
      var line = JSON.parse(JSON.stringify(def));
      if (prev) {{
        if (prev.presetOrphan) {{
          line.active = def.active;
        }} else if (typeof prev.active === 'boolean') {{
          line.active = prev.active;
        }}
        if (typeof prev.sortOrder === 'number') line.sortOrder = prev.sortOrder;
        if (freezeLabels) {{
          line.labelJa = def.labelJa;
          if (def.labelZh) line.labelZh = def.labelZh;
          line.labelEn = def.labelEn;
        }} else {{
          if (prev.labelJa) line.labelJa = prev.labelJa;
          if (prev.labelEn) line.labelEn = prev.labelEn;
        }}
        if (prev.expenseAttribute) line.expenseAttribute = prev.expenseAttribute;
        if (prev.inputStyle === 'daily' || prev.inputStyle === 'monthly') {{
          line.inputStyle = prev.inputStyle;
        }}
        if (prev.resolvedInputStyle === 'daily' || prev.resolvedInputStyle === 'monthly') {{
          line.resolvedInputStyle = prev.resolvedInputStyle;
        }} else if (line.inputStyle === 'daily' || line.inputStyle === 'monthly') {{
          line.resolvedInputStyle = line.inputStyle;
        }}
      }}
      if (line.expenseAttribute == null) {{
        delete line.expenseAttribute;
      }}
      delete line.presetOrphan;
      out.push(line);
      seenIds[line.lineId] = true;
    }});
    (oldLines || []).forEach(function (line) {{
      if (!line || !line.lineId || seenIds[line.lineId]) return;
      if (isCustomLineId(line.lineId)) {{
        var keyEn = line.bucket + '\\0' + String(line.labelEn || '').toLowerCase();
        var keyJa = line.bucket + '\\0' + String(line.labelJa || '');
        if (defaultLabelKeys[keyEn] || defaultLabelKeys[keyJa]) return;
        var custom = JSON.parse(JSON.stringify(line));
        custom.isDefault = false;
        if (!custom.resolvedInputStyle) {{
          custom.resolvedInputStyle = custom.inputStyle === 'daily' ? 'daily' : 'monthly';
        }}
        out.push(custom);
        seenIds[custom.lineId] = true;
        return;
      }}
      var kept = JSON.parse(JSON.stringify(line));
      kept.active = false;
      kept.presetOrphan = true;
      if (!kept.resolvedInputStyle) {{
        kept.resolvedInputStyle = kept.inputStyle === 'daily' ? 'daily' : 'monthly';
      }}
      out.push(kept);
      seenIds[kept.lineId] = true;
    }});
    return out;
  }}

  global.KpiPlExpensePresets = {{
    __ready: true,
    CANONICAL: CANONICAL.slice(),
    FALLBACK: FALLBACK,
    PRESETS: PRESETS,
    resolveBusinessType: resolveBusinessType,
    hasDefinedPreset: hasDefinedPreset,
    getDefaultExpenseLines: getDefaultExpenseLines,
    reconcileCatalogLines: reconcileCatalogLines,
  }};
}})(typeof window !== 'undefined' ? window : this);
"""


if __name__ == "__main__":
    print(mep_catalog_js())

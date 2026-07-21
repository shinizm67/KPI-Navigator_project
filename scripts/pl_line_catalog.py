"""Shared income / expense line catalog for PL table and Monthly Edit Page."""

from __future__ import annotations

import json
from typing import Any

# Bump when default line list / isDefault / expenseAttribute / active / inputStyle defaults change.
CATALOG_SCHEMA_VERSION = 8

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


def resolve_input_style(raw: str, line_id: str, bucket: str) -> str:
    if raw == "daily":
        return "daily"
    return "monthly"


def expense_detail_default_catalog() -> list[dict[str, Any]]:
    fixed_i = 0
    var_i = 0
    out: list[dict[str, Any]] = []
    for lid, ja, en, bucket, input_style, is_default, expense_attr in EXPENSE_DETAIL_LINES_V1:
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


def mep_catalog_entries() -> list[dict[str, Any]]:
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
    for item in expense_detail_default_catalog():
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


if __name__ == "__main__":
    print(mep_catalog_js())

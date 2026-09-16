# -*- coding: utf-8 -*-
"""Unit 5B-2 — Business Type expense presets + deferred custom classification."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pl_line_catalog import (  # noqa: E402
    BUSINESS_TYPE_CANONICAL,
    EXPENSE_DETAIL_LINES_V1,
    NON_RESTAURANT_ONLY_ATTRIBUTES,
    RESTAURANT_ONLY_ATTRIBUTES,
    UNCLASSIFIED_ATTRIBUTE,
    VARIABLE_EXPENSE_ATTRIBUTES,
    catalog_from_expense_tuples,
    expense_detail_default_catalog,
    get_default_expense_lines,
    has_defined_expense_preset,
    mep_catalog_entries,
    reconcile_catalog_lines,
)

FAILED = 0
PASSED = 0

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]
MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

EXPECTED_JA = {
    "retail": {
        "fixed": ["家賃", "電気代", "水道代", "通信費", "保険料"],
        "variable": [
            "商品仕入",
            "包装・梱包資材",
            "配送・発送費",
            "スタッフ人件費",
            "広告宣伝費",
            "決済手数料",
            "消耗品費",
        ],
    },
    "hair_salon": {
        "fixed": ["家賃", "電気代", "水道代", "ガス代", "通信費"],
        "variable": [
            "薬剤・施術材料費",
            "店販商品仕入",
            "タオル・リネン費",
            "スタッフ人件費",
            "広告宣伝費",
            "決済手数料",
            "消耗品費",
            "設備・美容機器メンテナンス",
        ],
    },
    "fitness": {
        "fixed": ["家賃", "電気代", "水道代", "通信費", "保険料", "トレーニング機器購入・リース"],
        "variable": [
            "ジム・施設利用料",
            "スタッフ人件費",
            "広告宣伝費",
            "決済手数料",
            "衛生・消耗品費",
            "機器メンテナンス",
        ],
    },
    "hotel": {
        "fixed": ["家賃・賃借料", "電気代", "水道代", "ガス代", "通信費", "保険料"],
        "variable": [
            "リネン・クリーニング費",
            "アメニティ費",
            "清掃用品費",
            "清掃外注費",
            "OTA・予約手数料",
            "スタッフ人件費",
            "広告宣伝費",
            "決済手数料",
            "設備修繕・メンテナンス",
        ],
    },
    "other": {
        "fixed": ["家賃", "電気代", "水道代", "ガス代", "通信費", "保険料"],
        "variable": [
            "材料・仕入費",
            "外注費",
            "スタッフ人件費",
            "広告宣伝費",
            "決済手数料",
            "消耗品費",
        ],
    },
}


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def labels_for(code: str, bucket: str) -> list[str]:
    return [row[1] for row in get_default_expense_lines(code) if row[3] == bucket]


def allow_attribute_id(attr_id: str, bucket: str, restaurant: bool) -> bool:
    if not attr_id or attr_id == UNCLASSIFIED_ATTRIBUTE:
        return False
    if not restaurant and attr_id in RESTAURANT_ONLY_ATTRIBUTES:
        return False
    if restaurant and attr_id in NON_RESTAURANT_ONLY_ATTRIBUTES:
        return False
    if restaurant and bucket == "variable" and attr_id == "occupancy":
        return False
    return True


def bucket_totals(lines: list[dict], amounts: dict[str, int], month: int = 0) -> tuple[int, int, int]:
    fixed = 0
    variable = 0
    for line in lines:
        if line.get("active") is False:
            continue
        amt = int(amounts.get(f"{line['lineId']}:{month}", 0) or 0)
        if line.get("bucket") == "fixed":
            fixed += amt
        elif line.get("bucket") == "variable":
            variable += amt
    return fixed, variable, fixed + variable


def test_a_restaurant_frozen() -> None:
    frozen = list(EXPENSE_DETAIL_LINES_V1)
    got = list(get_default_expense_lines("restaurant"))
    assert_true(got == frozen, "A restaurant tuples match EXPENSE_DETAIL_LINES_V1")
    cat = expense_detail_default_catalog("restaurant")
    assert_true(cat == catalog_from_expense_tuples(frozen), "A restaurant catalog dicts match")
    assert_true(all(len(row) == 7 for row in frozen), "A restaurant stays 7-field")
    assert_true(all("labelZh" not in row for row in cat), "A restaurant catalog has no extra labelZh")


def test_b_to_f_presets_on_pl() -> None:
    for code, expected in EXPECTED_JA.items():
        assert_true(has_defined_expense_preset(code) is True, f"{code} preset defined")
        assert_true(labels_for(code, "fixed") == expected["fixed"], f"{code} fixed JP labels")
        assert_true(labels_for(code, "variable") == expected["variable"], f"{code} variable JP labels")
        ids = {row[0] for row in get_default_expense_lines(code)}
        assert_true("exp_food_cost" not in ids, f"{code} has no restaurant food")
        assert_true("exp_drink_cost" not in ids, f"{code} has no restaurant drink")
        cat = expense_detail_default_catalog(code)
        assert_true(all(row.get("labelJa") for row in cat), f"{code} PL catalog has JP labels")
        assert_true(all(row.get("labelEn") for row in cat), f"{code} PL catalog has EN labels")
        assert_true(all(row.get("labelZh") for row in cat), f"{code} PL catalog has ZH labels")


def test_g_every_row_fixed_or_variable() -> None:
    for code in BUSINESS_TYPE_CANONICAL:
        for row in get_default_expense_lines(code):
            assert_true(row[3] in ("fixed", "variable"), f"G {code} {row[0]} has bucket")
            assert_true(row[3] != UNCLASSIFIED_ATTRIBUTE, f"G {code} {row[0]} bucket is not unclassified")


def test_h_pl_mep_sync() -> None:
    for code in BUSINESS_TYPE_CANONICAL:
        pl_ids = [row[0] for row in get_default_expense_lines(code)]
        mep_ids = [r["lineId"] for r in mep_catalog_entries(code) if r["section"] == "expense"]
        assert_true(mep_ids == pl_ids, f"H {code} MEP expense ids follow PL parent")
        income = [r["lineId"] for r in mep_catalog_entries(code) if r["section"] == "income"]
        assert_true(len(income) == 5, f"H {code} MEP income contract kept")


def test_i_switch_preserves_custom_and_amounts() -> None:
    restaurant = expense_detail_default_catalog("restaurant")
    custom = {
        "lineId": "exp_custom_fixed_keepme",
        "labelJa": "独自固定",
        "labelEn": "Custom fixed",
        "bucket": "fixed",
        "inputStyle": "monthly",
        "resolvedInputStyle": "monthly",
        "isDefault": False,
        "active": True,
        "sortOrder": 99,
        "expenseAttribute": UNCLASSIFIED_ATTRIBUTE,
    }
    old = json.loads(json.dumps(restaurant))
    old.append(custom)
    amounts = {
        "exp_food_cost:0": 1111,
        "exp_rent:0": 2222,
        "exp_custom_fixed_keepme:0": 3333,
    }
    snapshot = json.loads(json.dumps(amounts))
    switched = reconcile_catalog_lines(old, "retail")
    food = next(row for row in switched if row["lineId"] == "exp_food_cost")
    custom_kept = next(row for row in switched if row["lineId"] == "exp_custom_fixed_keepme")
    rent = next(row for row in switched if row["lineId"] == "exp_rent")
    assert_true(food.get("presetOrphan") is True, "I restaurant default becomes orphan")
    assert_true(food.get("active") is False, "I orphan is hidden")
    assert_true(custom_kept["lineId"] == "exp_custom_fixed_keepme", "I custom lineId kept")
    assert_true(custom_kept.get("active") is True, "I custom stays active")
    assert_true(rent["lineId"] == "exp_rent", "I shared rent lineId kept")
    assert_true(amounts == snapshot, "I amount map not mutated")
    assert_true(custom_kept.get("expenseAttribute") == UNCLASSIFIED_ATTRIBUTE, "I custom attr kept")
    back = reconcile_catalog_lines(switched, "restaurant")
    food_back = next(row for row in back if row["lineId"] == "exp_food_cost")
    custom_back = next(row for row in back if row["lineId"] == "exp_custom_fixed_keepme")
    assert_true(food_back.get("active") is True, "I returning restores restaurant default")
    assert_true(custom_back["lineId"] == "exp_custom_fixed_keepme", "I custom survives round-trip")


def test_j_k_custom_create_no_popup() -> None:
    client = (_SCRIPTS / "pl_expense_detail_client.py").read_text(encoding="utf-8")
    assert_true("openCreateLineLabelModal(bucket)" in client, "J/K create opens label modal")
    assert_true("function promptAddLine(bucket)" in client, "J/K promptAddLine exists")
    prompt = client.split("function promptAddLine(bucket)", 1)[1].split("function ", 1)[0]
    assert_true("openExpenseAttributeModal" not in prompt, "J/K create no longer forces attribute popup")
    assert_true("addLine(bucket, style, UNCLASSIFIED_ATTR)" in client, "J/K create uses unclassified")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        prompt_html = html.split("function promptAddLine(bucket)", 1)[1].split("function ", 1)[0]
        assert_true("openCreateLineLabelModal(bucket)" in prompt_html, f"J/K {rel} prompt uses label modal")
        assert_true("openExpenseAttributeModal" not in prompt_html, f"J/K {rel} prompt has no attribute popup")


def test_l_unclassified_attr() -> None:
    assert_true(UNCLASSIFIED_ATTRIBUTE == "unclassified", "L canonical unclassified id")
    assert_true(UNCLASSIFIED_ATTRIBUTE != "miscellaneous", "L unclassified is not misc")
    client = (_SCRIPTS / "pl_expense_detail_client.py").read_text(encoding="utf-8")
    assert_true("UNCLASSIFIED_ATTR = 'unclassified'" in client, "L client stores unclassified")
    assert_true("entry.expenseAttribute = UNCLASSIFIED_ATTR" in client, "L addLine writes unclassified")


def test_m_unclassified_in_totals() -> None:
    lines = expense_detail_default_catalog("retail")
    custom = {
        "lineId": "exp_custom_variable_unc",
        "labelJa": "未分類費目",
        "labelEn": "Unclassified custom",
        "bucket": "variable",
        "active": True,
        "expenseAttribute": UNCLASSIFIED_ATTRIBUTE,
    }
    lines = json.loads(json.dumps(lines)) + [custom]
    amounts = {"exp_rent:0": 100, "exp_custom_variable_unc:0": 40}
    fixed, variable, total = bucket_totals(lines, amounts)
    assert_true(fixed == 100, "M unclassified does not drop fixed")
    assert_true(variable == 40, "M unclassified custom is in variable total")
    assert_true(total == 140, "M unclassified is in total expenses")
    graph = (_SCRIPTS / "pl_bottom_graph_data_client.py").read_text(encoding="utf-8")
    assert_true("expenseAttribute" not in graph, "M graph totals ignore attribute")
    insight = (_SCRIPTS / "insight_expense_read_client.py").read_text(encoding="utf-8")
    assert_true("unclassified" not in insight, "M Insight FL mapping not remapped to misc")


def test_n_o_p_warning_and_popup() -> None:
    client = (_SCRIPTS / "pl_expense_detail_client.py").read_text(encoding="utf-8")
    assert_true("function rowUnclassifiedWarn" in client, "N warning helper exists")
    assert_true("isUnclassifiedCustom(line)" in client, "N warning only for unclassified custom")
    assert_true("⚠" in client, "N warning glyph")
    assert_true("data-action=\"unclassified-warn\"" in client, "N warning button")
    assert_true("action === 'unclassified-warn'" in client, "O warning click handler")
    click = client.split("action === 'unclassified-warn'", 1)[1].split("function ", 1)[0]
    assert_true("editLineAttribute" in click, "O warning click opens attribute popup")
    assert_true("function editLineAttribute" in client, "O existing attr edit kept")
    assert_true("line.expenseAttribute = attrId" in client, "P setting attr writes expenseAttribute")
    assert_true("return !a || a === UNCLASSIFIED_ATTR" in client, "P classified custom drops warning")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("rowUnclassifiedWarn" in html, f"N {rel} renders warning")
        assert_true("unclassified-warn" in html, f"O {rel} warning click")
        assert_true("pl-row-unclassified__btn" in html, f"N {rel} warning CSS")
    ja = (ROOT / "app/profit/pl/index.html").read_text(encoding="utf-8")
    en = (ROOT / "en/app/profit/pl/index.html").read_text(encoding="utf-8")
    zh = (ROOT / "zh-tw/app/profit/pl/index.html").read_text(encoding="utf-8")
    assert_true("分析カテゴリが未設定です" in ja, "N JP tooltip")
    assert_true("Analysis category is not set" in en, "N EN tooltip")
    assert_true("尚未設定分析類別" in zh, "N ZH-TW tooltip")


def test_q_attribute_filter() -> None:
    var_ids = [row[0] for row in VARIABLE_EXPENSE_ATTRIBUTES]
    assert_true("food_cost" in var_ids and "drink_cost" in var_ids, "Q restaurant still has Food/Drink attrs")
    assert_true(allow_attribute_id("food_cost", "variable", True), "Q restaurant can pick Food")
    assert_true(allow_attribute_id("drink_cost", "variable", True), "Q restaurant can pick Drink")
    assert_true(not allow_attribute_id("food_cost", "variable", False), "Q non-restaurant hides Food")
    assert_true(not allow_attribute_id("drink_cost", "variable", False), "Q non-restaurant hides Drink")
    assert_true(allow_attribute_id("inventory", "variable", False), "Q non-restaurant can pick inventory")
    assert_true(allow_attribute_id("variable_labor", "variable", False), "Q non-restaurant can pick labor")
    assert_true(not allow_attribute_id(UNCLASSIFIED_ATTRIBUTE, "variable", False), "Q unclassified is not a radio")
    client = (_SCRIPTS / "pl_expense_detail_client.py").read_text(encoding="utf-8")
    assert_true("function rebuildAttributeChoices" in client, "Q popup rebuilds by Business Type")
    assert_true("RESTAURANT_ONLY_ATTRIBUTES" in client, "Q filters restaurant-only attrs")
    js = (ROOT / "js" / "kpi-pl-expense-presets.js").read_text(encoding="utf-8")
    assert_true('"food_cost"' in js and '"drink_cost"' in js, "Q runtime lists Food/Drink")
    assert_true("restaurantOnly" in js, "Q runtime exposes restaurant-only list")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("rebuildAttributeChoices" in html, f"Q {rel} rebuilds attr choices")
        assert_true("allowAttributeId" in html, f"Q {rel} filters attr ids")


def test_labor_follows_restaurant_variable() -> None:
    rest = next(row for row in get_default_expense_lines("restaurant") if row[0] == "exp_variable_labor")
    assert_true(rest[3] == "variable" and rest[4] == "daily" and rest[6] == "variable_labor", "labor restaurant contract")
    for code in ("retail", "hair_salon", "fitness", "hotel", "other"):
        labor = next(row for row in get_default_expense_lines(code) if row[0] == "exp_variable_labor")
        assert_true(labor[3] == "variable", f"{code} staff labor is variable")
        assert_true(labor[4] == "daily", f"{code} staff labor is daily like restaurant アルバイト")
        assert_true(labor[6] == "variable_labor", f"{code} staff labor uses variable_labor attr")


def test_runtime_and_mep_pages() -> None:
    js = (ROOT / "js" / "kpi-pl-expense-presets.js").read_text(encoding="utf-8")
    for code in ("retail", "hair_salon", "fitness", "hotel", "other"):
        assert_true(f'"{code}"' in js, f"runtime includes {code}")
        assert_true('"status": "defined"' in js, "runtime marks presets defined")
    assert_true("UNCLASSIFIED" in js, "runtime exposes unclassified")
    apply_mep = (_SCRIPTS / "apply_mep_pl_catalog.py").read_text(encoding="utf-8")
    assert_true("getDefaultExpenseLines(bt)" in apply_mep, "MEP generator syncs non-restaurant from PL preset")
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("getDefaultExpenseLines(bt)" in html, f"{rel} MEP embeds selected preset")
        assert_true("kpi-pl-expense-presets.js" in html, f"{rel} loads preset JS")


def test_attribute_edit_does_not_change_bucket() -> None:
    client = (_SCRIPTS / "pl_expense_detail_client.py").read_text(encoding="utf-8")
    setter = client.split("function setLineExpenseAttribute", 1)[1].split("function editLineAttribute", 1)[0]
    assert_true("line.bucket =" not in setter, "attribute setter does not rewrite bucket")
    assert_true("line.expenseAttribute = attrId" in setter, "attribute setter only writes attr")


def test_no_mep_own_preset() -> None:
    src = (_SCRIPTS / "pl_line_catalog.py").read_text(encoding="utf-8")
    assert_true("PL is the parent expense master" in src, "PL remains parent")
    assert_true("MEP is the parent" not in src, "MEP is not parent")
    mep_apply = (_SCRIPTS / "apply_mep_pl_catalog.py").read_text(encoding="utf-8")
    assert_true("MEP_EXPENSE_PRESET" not in mep_apply, "no MEP-only expense preset map")


def main() -> int:
    test_a_restaurant_frozen()
    test_b_to_f_presets_on_pl()
    test_g_every_row_fixed_or_variable()
    test_h_pl_mep_sync()
    test_i_switch_preserves_custom_and_amounts()
    test_j_k_custom_create_no_popup()
    test_l_unclassified_attr()
    test_m_unclassified_in_totals()
    test_n_o_p_warning_and_popup()
    test_q_attribute_filter()
    test_labor_follows_restaurant_variable()
    test_runtime_and_mep_pages()
    test_attribute_edit_does_not_change_bucket()
    test_no_mep_own_preset()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

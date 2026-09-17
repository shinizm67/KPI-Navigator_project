# -*- coding: utf-8 -*-
"""Unit 6D: Business Type + active catalog CSV template generator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from csv_sales_schema import COMMON_KEYS, RESTAURANT_ONLY_KEYS  # noqa: E402
from csv_template_generator import (  # noqa: E402
    EXPENSE_DAILY_MACHINE_HEADER,
    EXPENSE_MONTHLY_MACHINE_HEADER,
    SALES_LABELS,
    build_expense_template,
    build_sales_template,
    default_catalog_lines,
    parse_csv_text,
    sales_field_keys,
    select_active_expense_lines,
)
from pl_line_catalog import (  # noqa: E402
    BUSINESS_TYPE_CANONICAL,
    reconcile_catalog_lines,
)

FAILED = 0
PASSED = 0

CHROME_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def custom_line(
    line_id: str = "exp_custom_variable_warehouse",
    *,
    label_ja: str = "倉庫利用料",
    label_en: str = "Warehouse fee",
    label_zh: str = "倉庫使用費",
    style: str = "monthly",
    active: bool = True,
    orphan: bool = False,
) -> dict:
    row = {
        "lineId": line_id,
        "labelJa": label_ja,
        "labelEn": label_en,
        "labelZh": label_zh,
        "bucket": "variable",
        "inputStyle": style,
        "resolvedInputStyle": style,
        "isDefault": False,
        "active": active,
        "sortOrder": 99,
        "expenseAttribute": "occupancy",
    }
    if orphan:
        row["presetOrphan"] = True
    return row


def test_sales_restaurant_and_retail() -> None:
    rest = build_sales_template("restaurant", "ja")
    retail = build_sales_template("retail", "ja")
    rows_r = parse_csv_text(rest["text"])
    rows_t = parse_csv_text(retail["text"])
    assert_true(rest["keys"][:3] == COMMON_KEYS, "Restaurant sales starts with COMMON")
    assert_true(tuple(rest["keys"][3:]) == RESTAURANT_ONLY_KEYS, "Restaurant sales has meal/customer/group/Food/Drink")
    assert_true("lunch_sales" in rest["keys"] and "food_sales" in rest["keys"], "Restaurant extension present")
    assert_true(retail["keys"] == COMMON_KEYS, "Retail sales is COMMON only")
    assert_true("lunch_sales" not in retail["keys"], "Retail has no lunch_sales")
    assert_true("food_sales" not in retail["keys"], "Retail has no food_sales")
    assert_true(rows_r[0] == list(rest["keys"]), "Sales row 0 is machine keys")
    assert_true(rows_r[1][0] == "日付" and rows_r[1][2] == "日次売上", "JA sales labels on row 1")
    assert_true(rows_t[0] == ["date", "business_day", "daily_sales"], "Retail machine keys")
    cafe = sales_field_keys("cafe")
    assert_true("dinner_sales" in cafe, "cafe maps to restaurant-like sales")
    wear = sales_field_keys("wear_shop")
    assert_true(wear == COMMON_KEYS, "wear_shop maps to retail COMMON sales")


def test_sales_locales_share_machine_keys() -> None:
    keys = None
    for lang in ("ja", "en", "zh-tw"):
        rec = build_sales_template("restaurant", lang)
        if keys is None:
            keys = rec["keys"]
        assert_true(rec["keys"] == keys, f"{lang} sales machine keys identical")
        rows = parse_csv_text(rec["text"])
        assert_true(rows[0] == list(keys), f"{lang} row 0 is machine keys")
        assert_true(rows[1] == list(rec["labels"]), f"{lang} row 1 is localized labels")
    ja = build_sales_template("restaurant", "ja")["labels"]
    en = build_sales_template("restaurant", "en")["labels"]
    zh = build_sales_template("restaurant", "zh-tw")["labels"]
    assert_true(ja[2] == "日次売上", "JP daily_sales label")
    assert_true(en[2] == "daily sales", "EN daily_sales label")
    assert_true(zh[2] == "日次銷售", "ZH-TW daily_sales label")
    assert_true(ja != en and en != zh, "localized sales labels differ by locale")
    assert_true(SALES_LABELS["ja"]["lunch_sales"] == "ランチ売上", "JP lunch label")
    assert_true(SALES_LABELS["en"]["lunch_sales"] == "lunch sales", "EN lunch label")
    assert_true(SALES_LABELS["zh-tw"]["lunch_sales"] == "午餐銷售", "ZH lunch label")


def test_expense_presets_all_business_types() -> None:
    expected_ja = {
        "restaurant": {"daily": ["食材仕入れ費", "ドリンク仕入れ費", "アルバイト人件費"], "monthly": ["家賃"]},
        "retail": {"daily": ["スタッフ人件費"], "monthly": ["商品仕入", "包装・梱包資材", "配送・発送費"]},
        "hair_salon": {"daily": ["スタッフ人件費"], "monthly": ["薬剤・施術材料費"]},
        "fitness": {"daily": ["スタッフ人件費"], "monthly": ["ジム・施設利用料"]},
        "hotel": {"daily": ["スタッフ人件費"], "monthly": ["OTA・予約手数料"]},
        "other": {"daily": ["スタッフ人件費"], "monthly": ["材料・仕入費", "外注費"]},
    }
    for code in BUSINESS_TYPE_CANONICAL:
        daily = build_expense_template(None, style="daily", lang="ja", business_type=code)
        monthly = build_expense_template(None, style="monthly", lang="ja", business_type=code)
        daily_labels = [row["labelJa"] for row in daily["lines"]]
        monthly_labels = [row["labelJa"] for row in monthly["lines"]]
        for label in expected_ja[code]["daily"]:
            assert_true(label in daily_labels, f"{code} daily includes {label}")
        for label in expected_ja[code]["monthly"]:
            assert_true(label in monthly_labels, f"{code} monthly includes {label}")
        daily_ids = set(daily["lineIds"])
        monthly_ids = set(monthly["lineIds"])
        assert_true(not (daily_ids & monthly_ids), f"{code} does not dailyize monthly lines")
        assert_true(daily["text"].splitlines()[0] == ",".join(EXPENSE_DAILY_MACHINE_HEADER), f"{code} daily machine header")
        assert_true(monthly["text"].splitlines()[0] == ",".join(EXPENSE_MONTHLY_MACHINE_HEADER), f"{code} monthly machine header")
        inactive = [
            row["lineId"]
            for row in default_catalog_lines(code)
            if row.get("active") is False
        ]
        for lid in inactive:
            assert_true(lid not in daily["lineIds"] and lid not in monthly["lineIds"], f"{code} drops inactive {lid}")


def test_custom_add_rename_delete() -> None:
    retail = default_catalog_lines("retail")
    added = retail + [custom_line()]
    rec = build_expense_template(added, style="monthly", lang="ja", business_type="retail")
    assert_true("exp_custom_variable_warehouse" in rec["lineIds"], "custom add appears in DL")
    assert_true("倉庫利用料" in [row[2] for row in parse_csv_text(rec["text"])[2:]], "custom JA label in CSV")

    renamed = retail + [custom_line(label_ja="イベント什器費", label_en="Event fixture", label_zh="活動展具費")]
    rec2 = build_expense_template(renamed, style="monthly", lang="ja", business_type="retail")
    assert_true(rec2["lineIds"].count("exp_custom_variable_warehouse") == 1, "rename keeps same lineId")
    body = [row[2] for row in parse_csv_text(rec2["text"])[2:]]
    assert_true("イベント什器費" in body, "rename updates label")
    assert_true("倉庫利用料" not in body, "old custom label is gone")

    rec3 = build_expense_template(retail, style="monthly", lang="ja", business_type="retail")
    assert_true("exp_custom_variable_warehouse" not in rec3["lineIds"], "deleted custom drops from next DL")

    extra_daily = retail + [custom_line(line_id="exp_custom_variable_ads", label_ja="独自広告費", style="daily")]
    daily = build_expense_template(extra_daily, style="daily", lang="ja", business_type="retail")
    monthly = build_expense_template(extra_daily, style="monthly", lang="ja", business_type="retail")
    assert_true("exp_custom_variable_ads" in daily["lineIds"], "daily custom goes to daily template")
    assert_true("exp_custom_variable_ads" not in monthly["lineIds"], "daily custom is not monthly-ized")


def test_orphan_and_inactive_excluded() -> None:
    restaurant = default_catalog_lines("restaurant")
    switched = reconcile_catalog_lines(restaurant, "retail")
    orphans = [row for row in switched if row.get("presetOrphan")]
    assert_true(any(row["lineId"] == "exp_food_cost" for row in orphans), "food becomes presetOrphan on retail")
    monthly = build_expense_template(switched, style="monthly", lang="ja", business_type="retail")
    daily = build_expense_template(switched, style="daily", lang="ja", business_type="retail")
    all_ids = set(monthly["lineIds"]) | set(daily["lineIds"])
    assert_true("exp_food_cost" not in all_ids, "presetOrphan excluded from DL")
    assert_true("exp_inventory_cogs" in monthly["lineIds"], "retail merchandise remains")
    hidden = [row for row in switched if row.get("active") is False]
    for row in hidden:
        assert_true(row["lineId"] not in all_ids, f"inactive {row['lineId']} excluded")
    catalog = switched + [custom_line(active=False, line_id="exp_custom_variable_hidden")]
    rec = build_expense_template(catalog, style="monthly", lang="ja", business_type="retail")
    assert_true("exp_custom_variable_hidden" not in rec["lineIds"], "inactive custom excluded")
    selected = select_active_expense_lines(catalog)
    assert_true(all(row.get("active") is not False for row in selected), "select_active drops active:false")
    assert_true(all(not row.get("presetOrphan") for row in selected), "select_active drops presetOrphan")


def test_expense_locales_and_lineid_column() -> None:
    catalog = default_catalog_lines("retail") + [custom_line()]
    machine = None
    ids = None
    for lang in ("ja", "en", "zh-tw"):
        rec = build_expense_template(catalog, style="monthly", lang=lang, business_type="retail")
        rows = parse_csv_text(rec["text"])
        if machine is None:
            machine = tuple(rows[0])
            ids = rec["lineIds"]
        assert_true(tuple(rows[0]) == machine, f"{lang} expense machine header identical")
        assert_true(rec["lineIds"] == ids, f"{lang} lineIds identical")
        assert_true(rows[0][1] == "item", "item column is machine key")
        body_ids = [row[1] for row in rows[2:]]
        assert_true("exp_custom_variable_warehouse" in body_ids, f"{lang} keeps canonical lineId")
        assert_true("exp_inventory_cogs" in body_ids, f"{lang} retail merchandise lineId")
    ja = parse_csv_text(build_expense_template(catalog, style="monthly", lang="ja", business_type="retail")["text"])
    en = parse_csv_text(build_expense_template(catalog, style="monthly", lang="en", business_type="retail")["text"])
    zh = parse_csv_text(build_expense_template(catalog, style="monthly", lang="zh-tw", business_type="retail")["text"])
    ja_custom = next(row[2] for row in ja[2:] if row[1] == "exp_custom_variable_warehouse")
    en_custom = next(row[2] for row in en[2:] if row[1] == "exp_custom_variable_warehouse")
    zh_custom = next(row[2] for row in zh[2:] if row[1] == "exp_custom_variable_warehouse")
    assert_true(ja_custom == "倉庫利用料", "JP custom label")
    assert_true(en_custom == "Warehouse fee", "EN custom label")
    assert_true(zh_custom == "倉庫使用費", "ZH-TW custom label")


def test_runtime_js_mirrors_python() -> None:
    js = (ROOT / "js" / "kpi-csv-templates.js").read_text(encoding="utf-8")
    assert_true("KpiCsvTemplates" in js, "runtime exposes KpiCsvTemplates")
    assert_true("buildSalesTemplate" in js and "buildExpenseTemplate" in js, "runtime builders exist")
    assert_true("selectActiveExpenseLines" in js, "runtime filters active catalog")
    assert_true("presetOrphan" in js and "active === false" in js, "runtime excludes orphan/inactive")
    assert_true("exp_custom_" in js, "runtime recognizes custom lineId prefix")
    assert_true("kpiNavigator.plLineCatalog" in js, "runtime reads current catalog")
    assert_true("KpiPlExpensePresets" in js, "runtime uses preset engine")
    assert_true("KpiBusinessType" in js, "runtime uses Business Type")
    for key in COMMON_KEYS + RESTAURANT_ONLY_KEYS:
        assert_true(f"'{key}'" in js, f"JS lists sales key {key}")
    chrome = (SCRIPTS / "site_chrome.py").read_text(encoding="utf-8")
    assert_true("kpi-csv-templates.js" in chrome, "site chrome loads template JS")
    assert_true("data-kpi-csv-template=\"sales\"" in chrome, "chrome has sales DL")
    assert_true("data-kpi-csv-template=\"expense-daily\"" in chrome, "chrome has daily expense DL")
    assert_true("data-kpi-csv-template=\"expense-monthly\"" in chrome, "chrome has monthly expense DL")
    assert_true("{img}excel/{L['dl_daily_file']}" not in chrome, "chrome no longer static-hrefs daily excel")
    assert_true("{img}excel/{L['dl_monthly_file']}" not in chrome, "chrome no longer static-hrefs monthly excel")


def test_pages_use_dynamic_download() -> None:
    for path in CHROME_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-csv-templates.js" in html, f"{rel} loads csv templates")
        assert_true('data-kpi-csv-template="sales"' in html, f"{rel} has sales button")
        assert_true('data-kpi-csv-template="expense-daily"' in html, f"{rel} has daily expense button")
        assert_true('data-kpi-csv-template="expense-monthly"' in html, f"{rel} has monthly expense button")
        assert_true("支出入力_日次_雛形.csv" not in html, f"{rel} dropped JA static daily excel href")
        assert_true("expense-import_daily_template.csv" not in html, f"{rel} dropped EN static daily excel href")


def test_parsers_untouched_and_6a_green() -> None:
    sales_parser = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
    expense_parser = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
    assert_true("KpiCsvTemplates" not in sales_parser, "sales parser unchanged by 6D")
    assert_true("getBusinessType" not in sales_parser, "sales parser has no BT gate")
    assert_true("KpiCsvTemplates" not in expense_parser, "expense parser unchanged by 6D")
    assert_true("function detectColumns(rows)" in expense_parser, "expense detectColumns kept")
    assert_true("DATE_KEYS = ['日付', '年月日', '年月', 'date', 'day', 'month', 'ym', 'ymd']" in expense_parser, "expense date aliases kept")
    u4 = load_module("u4_daily_sales_meal_csv_import", SCRIPTS / "_test_daily_sales_meal_csv_import.py")
    before = u4.FAILED
    maps = u4.rows_to_maps(
        u4.csv_rows(
            ["年月日", "日次売上", "ディナー売上", "ランチ売上"],
            [["2026-01-01", "132000", "100000", "32000"]],
        )
    )
    assert_true(maps["salesByDate"]["2026-01-01"] == 132000, "legacy Restaurant header still imports")
    assert_true(maps["dinnerSalesByDate"]["2026-01-01"] == 100000, "legacy dinner column still imports")
    u6a = load_module("u6a_csv_sales_schema", SCRIPTS / "_test_csv_sales_schema_6a.py")
    rc = u6a.main()
    assert_true(rc == 0, "Unit 6A still green")
    assert_true(u4.FAILED == before, "Unit 4 helper not dirtied")


def test_excel_dir_not_written() -> None:
    gen = (SCRIPTS / "csv_template_generator.py").read_text(encoding="utf-8")
    js = (ROOT / "js" / "kpi-csv-templates.js").read_text(encoding="utf-8")
    assert_true("Path(" not in gen and "write_text" not in gen, "generator is in-memory only")
    assert_true("xlsx" not in gen.lower(), "Python generator does not emit xlsx")
    assert_true("XLSX" not in js, "JS template generator does not emit xlsx")
    assert_true("open(" not in gen, "generator does not open files")


def main() -> int:
    print("--- 6D sales templates ---")
    test_sales_restaurant_and_retail()
    test_sales_locales_share_machine_keys()
    print("--- 6D expense presets ---")
    test_expense_presets_all_business_types()
    print("--- 6D custom / orphan ---")
    test_custom_add_rename_delete()
    test_orphan_and_inactive_excluded()
    test_expense_locales_and_lineid_column()
    print("--- 6D runtime / chrome ---")
    test_runtime_js_mirrors_python()
    test_pages_use_dynamic_download()
    print("--- 6D regression ---")
    test_parsers_untouched_and_6a_green()
    test_excel_dir_not_written()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

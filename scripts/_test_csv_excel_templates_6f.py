# -*- coding: utf-8 -*-
"""Unit 6F: Business Type + Custom Expense Excel template generator."""

from __future__ import annotations

import importlib.util
import io
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from csv_sales_schema import COMMON_KEYS, RESTAURANT_ONLY_KEYS  # noqa: E402
from csv_excel_template_generator import (  # noqa: E402
    EXCEL_DIR,
    FixturePathError,
    assert_safe_dest,
    build_excel_spec,
    read_workbook,
    workbook_bytes,
    write_xlsx,
)
from csv_template_generator import (  # noqa: E402
    EXPENSE_DAILY_MACHINE_HEADER,
    EXPENSE_MONTHLY_MACHINE_HEADER,
    build_expense_template,
    build_sales_template,
    default_catalog_lines,
    parse_csv_text,
)
from pl_line_catalog import BUSINESS_TYPE_CANONICAL, reconcile_catalog_lines  # noqa: E402

FAILED = 0
PASSED = 0

TMP = ROOT / "tests" / "tmp" / "unit6f"

CHROME_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]

EXPECTED_JA = {
    "restaurant": {"daily": ["食材仕入れ費", "ドリンク仕入れ費", "アルバイト人件費"], "monthly": ["家賃"]},
    "retail": {"daily": ["スタッフ人件費"], "monthly": ["商品仕入", "包装・梱包資材", "配送・発送費"]},
    "hair_salon": {"daily": ["スタッフ人件費"], "monthly": ["薬剤・施術材料費"]},
    "fitness": {"daily": ["スタッフ人件費"], "monthly": ["ジム・施設利用料"]},
    "hotel": {"daily": ["スタッフ人件費"], "monthly": ["OTA・予約手数料"]},
    "other": {"daily": ["スタッフ人件費"], "monthly": ["材料・仕入費", "外注費"]},
}


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


def sheet_by_kind(spec: dict, kind: str) -> dict:
    return next(sheet for sheet in spec["sheets"] if sheet["kind"] == kind)


def body_ids(rows: list[list[str]]) -> list[str]:
    return [row[1] for row in rows[2:] if len(row) > 1 and row[1]]


def body_labels(rows: list[list[str]]) -> list[str]:
    return [row[2] for row in rows[2:] if len(row) > 2]


def test_restaurant_workbook() -> None:
    spec = build_excel_spec("restaurant", "ja")
    assert_true(len(spec["sheets"]) == 3, "Restaurant workbook has 3 sheets")
    assert_true(spec["sheets"][0]["kind"] == "sales", "Sales is first sheet")
    assert_true([s["kind"] for s in spec["sheets"]] == ["sales", "expense-daily", "expense-monthly"], "sheet kinds")
    sales = sheet_by_kind(spec, "sales")
    assert_true(tuple(sales["keys"][:3]) == COMMON_KEYS, "Restaurant sales starts with COMMON")
    assert_true(tuple(sales["keys"][3:]) == RESTAURANT_ONLY_KEYS, "Restaurant sales has meal/customer/group/Food/Drink")
    assert_true("lunch_sales" in sales["keys"] and "food_sales" in sales["keys"], "Restaurant extension present")
    assert_true(sales["rows"][0] == list(sales["keys"]), "Sales row 0 is machine keys")
    assert_true(sales["rows"][1][0] == "日付" and sales["rows"][1][2] == "日次売上", "JA sales labels on row 1")
    daily = sheet_by_kind(spec, "expense-daily")
    monthly = sheet_by_kind(spec, "expense-monthly")
    assert_true(tuple(daily["rows"][0]) == EXPENSE_DAILY_MACHINE_HEADER, "daily machine header")
    assert_true(tuple(monthly["rows"][0]) == EXPENSE_MONTHLY_MACHINE_HEADER, "monthly machine header")
    for label in EXPECTED_JA["restaurant"]["daily"]:
        assert_true(label in body_labels(daily["rows"]), f"Restaurant daily includes {label}")
    for label in EXPECTED_JA["restaurant"]["monthly"]:
        assert_true(label in body_labels(monthly["rows"]), f"Restaurant monthly includes {label}")
    assert_true(not (set(daily["lineIds"]) & set(monthly["lineIds"])), "Restaurant does not mix daily/monthly")


def test_retail_workbook() -> None:
    spec = build_excel_spec("retail", "ja")
    sales = sheet_by_kind(spec, "sales")
    assert_true(tuple(sales["keys"]) == COMMON_KEYS, "Retail sales is COMMON only")
    assert_true("lunch_sales" not in sales["keys"], "Retail has no lunch_sales")
    assert_true("food_sales" not in sales["keys"], "Retail has no food_sales")
    daily = sheet_by_kind(spec, "expense-daily")
    monthly = sheet_by_kind(spec, "expense-monthly")
    for label in EXPECTED_JA["retail"]["daily"]:
        assert_true(label in body_labels(daily["rows"]), f"Retail daily includes {label}")
    for label in EXPECTED_JA["retail"]["monthly"]:
        assert_true(label in body_labels(monthly["rows"]), f"Retail monthly includes {label}")
    assert_true("exp_inventory_cogs" in monthly["lineIds"], "Retail merchandise lineId")


def test_other_business_types() -> None:
    for code in BUSINESS_TYPE_CANONICAL:
        spec = build_excel_spec(code, "ja")
        sales = sheet_by_kind(spec, "sales")
        daily = sheet_by_kind(spec, "expense-daily")
        monthly = sheet_by_kind(spec, "expense-monthly")
        if code == "restaurant":
            assert_true("dinner_sales" in sales["keys"], f"{code} restaurant extension")
        else:
            assert_true(tuple(sales["keys"]) == COMMON_KEYS, f"{code} sales COMMON only")
        for label in EXPECTED_JA[code]["daily"]:
            assert_true(label in body_labels(daily["rows"]), f"{code} daily includes {label}")
        for label in EXPECTED_JA[code]["monthly"]:
            assert_true(label in body_labels(monthly["rows"]), f"{code} monthly includes {label}")
        assert_true(not (set(daily["lineIds"]) & set(monthly["lineIds"])), f"{code} no daily/monthly mix")


def test_custom_add_rename_delete() -> None:
    retail = default_catalog_lines("retail")
    added = retail + [custom_line()]
    spec = build_excel_spec("retail", "ja", added)
    monthly = sheet_by_kind(spec, "expense-monthly")
    assert_true("exp_custom_variable_warehouse" in monthly["lineIds"], "custom add appears in Excel")
    assert_true("倉庫利用料" in body_labels(monthly["rows"]), "custom JA label in Excel")

    renamed = retail + [custom_line(label_ja="イベント什器費", label_en="Event fixture", label_zh="活動展具費")]
    spec2 = build_excel_spec("retail", "ja", renamed)
    monthly2 = sheet_by_kind(spec2, "expense-monthly")
    assert_true(monthly2["lineIds"].count("exp_custom_variable_warehouse") == 1, "rename keeps same lineId")
    labels = body_labels(monthly2["rows"])
    assert_true("イベント什器費" in labels, "rename updates Excel label")
    assert_true("倉庫利用料" not in labels, "old custom label is gone")

    spec3 = build_excel_spec("retail", "ja", retail)
    monthly3 = sheet_by_kind(spec3, "expense-monthly")
    assert_true("exp_custom_variable_warehouse" not in monthly3["lineIds"], "deleted custom drops from next Excel")

    extra_daily = retail + [custom_line(line_id="exp_custom_variable_ads", label_ja="独自広告費", style="daily")]
    spec4 = build_excel_spec("retail", "ja", extra_daily)
    daily4 = sheet_by_kind(spec4, "expense-daily")
    monthly4 = sheet_by_kind(spec4, "expense-monthly")
    assert_true("exp_custom_variable_ads" in daily4["lineIds"], "daily custom goes to daily sheet")
    assert_true("exp_custom_variable_ads" not in monthly4["lineIds"], "daily custom is not monthly-ized")

    hidden = retail + [custom_line(active=False, line_id="exp_custom_variable_hidden")]
    spec5 = build_excel_spec("retail", "ja", hidden)
    all_ids = set(sheet_by_kind(spec5, "expense-daily")["lineIds"]) | set(
        sheet_by_kind(spec5, "expense-monthly")["lineIds"]
    )
    assert_true("exp_custom_variable_hidden" not in all_ids, "inactive custom excluded")

    switched = reconcile_catalog_lines(default_catalog_lines("restaurant"), "retail")
    spec6 = build_excel_spec("retail", "ja", switched)
    all_ids6 = set(sheet_by_kind(spec6, "expense-daily")["lineIds"]) | set(
        sheet_by_kind(spec6, "expense-monthly")["lineIds"]
    )
    assert_true("exp_food_cost" not in all_ids6, "presetOrphan excluded from Excel")
    assert_true("exp_inventory_cogs" in sheet_by_kind(spec6, "expense-monthly")["lineIds"], "current BT catalog only")


def test_locales_share_machine_keys() -> None:
    catalog = default_catalog_lines("retail") + [custom_line()]
    sales_keys = None
    daily_ids = None
    monthly_ids = None
    daily_header = None
    monthly_header = None
    for lang in ("ja", "en", "zh-tw"):
        spec = build_excel_spec("retail", lang, catalog)
        sales = sheet_by_kind(spec, "sales")
        daily = sheet_by_kind(spec, "expense-daily")
        monthly = sheet_by_kind(spec, "expense-monthly")
        if sales_keys is None:
            sales_keys = tuple(sales["keys"])
            daily_ids = daily["lineIds"]
            monthly_ids = monthly["lineIds"]
            daily_header = tuple(daily["rows"][0])
            monthly_header = tuple(monthly["rows"][0])
        assert_true(tuple(sales["keys"]) == sales_keys, f"{lang} sales machine keys identical")
        assert_true(tuple(sales["rows"][0]) == sales_keys, f"{lang} sales row 0 is machine keys")
        assert_true(daily["lineIds"] == daily_ids, f"{lang} daily lineIds identical")
        assert_true(monthly["lineIds"] == monthly_ids, f"{lang} monthly lineIds identical")
        assert_true(tuple(daily["rows"][0]) == daily_header, f"{lang} daily header identical")
        assert_true(tuple(monthly["rows"][0]) == monthly_header, f"{lang} monthly header identical")
        assert_true("exp_custom_variable_warehouse" in monthly["lineIds"], f"{lang} custom lineId kept")
    ja = build_excel_spec("retail", "ja", catalog)
    en = build_excel_spec("retail", "en", catalog)
    zh = build_excel_spec("retail", "zh-tw", catalog)
    ja_custom = next(
        row[2] for row in sheet_by_kind(ja, "expense-monthly")["rows"][2:] if row[1] == "exp_custom_variable_warehouse"
    )
    en_custom = next(
        row[2] for row in sheet_by_kind(en, "expense-monthly")["rows"][2:] if row[1] == "exp_custom_variable_warehouse"
    )
    zh_custom = next(
        row[2] for row in sheet_by_kind(zh, "expense-monthly")["rows"][2:] if row[1] == "exp_custom_variable_warehouse"
    )
    assert_true(ja_custom == "倉庫利用料", "JP custom label")
    assert_true(en_custom == "Warehouse fee", "EN custom label")
    assert_true(zh_custom == "倉庫使用費", "ZH-TW custom label")
    assert_true(sheet_by_kind(ja, "sales")["name"] == "売上", "JP sales sheet name")
    assert_true(sheet_by_kind(en, "sales")["name"] == "Sales", "EN sales sheet name")
    assert_true(sheet_by_kind(zh, "sales")["name"] == "銷售", "ZH-TW sales sheet name")


def test_csv_schema_parity() -> None:
    for code in BUSINESS_TYPE_CANONICAL:
        csv_sales = build_sales_template(code, "ja")
        csv_daily = build_expense_template(None, style="daily", lang="ja", business_type=code)
        csv_monthly = build_expense_template(None, style="monthly", lang="ja", business_type=code)
        spec = build_excel_spec(code, "ja")
        sales = sheet_by_kind(spec, "sales")
        daily = sheet_by_kind(spec, "expense-daily")
        monthly = sheet_by_kind(spec, "expense-monthly")
        csv_sales_rows = parse_csv_text(csv_sales["text"])
        assert_true(sales["rows"][0] == csv_sales_rows[0], f"{code} sales keys match CSV")
        assert_true(sales["rows"][1] == csv_sales_rows[1], f"{code} sales labels match CSV")
        assert_true(daily["rows"] == parse_csv_text(csv_daily["text"]), f"{code} daily sheet == CSV")
        assert_true(monthly["rows"] == parse_csv_text(csv_monthly["text"]), f"{code} monthly sheet == CSV")
        assert_true(daily["lineIds"] == csv_daily["lineIds"], f"{code} daily lineIds match CSV")
        assert_true(monthly["lineIds"] == csv_monthly["lineIds"], f"{code} monthly lineIds match CSV")


def test_xlsx_valid_and_readback() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    spec = build_excel_spec("restaurant", "ja")
    data = workbook_bytes(spec)
    assert_true(data[:2] == b"PK", "xlsx is a zip")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = set(zf.namelist())
        zf.testzip()
        assert_true("xl/workbook.xml" in names, "workbook.xml present")
        assert_true("xl/worksheets/sheet1.xml" in names, "sheet1 present")
        assert_true("xl/worksheets/sheet2.xml" in names, "sheet2 present")
        assert_true("xl/worksheets/sheet3.xml" in names, "sheet3 present")
        assert_true("[Content_Types].xml" in names, "content types present")
        bad = zf.testzip()
        assert_true(bad is None, "zip members not corrupt")
    sheets = read_workbook(data)
    assert_true(list(sheets.keys()) == [s["name"] for s in spec["sheets"]], "readback sheet names")
    sales_name = spec["sheets"][0]["name"]
    assert_true(sheets[sales_name][0] == list(spec["sheets"][0]["keys"]), "readback sales machine keys")
    dest = write_xlsx(spec, TMP / "kpi_template_restaurant.xlsx")
    assert_true(dest.is_file() and dest.stat().st_size > 0, "file written under tests/tmp")
    opened = read_workbook(dest.read_bytes())
    assert_true(len(opened) == 3, "written file has 3 sheets")

    retail_spec = build_excel_spec("retail", "en", default_catalog_lines("retail") + [custom_line()])
    retail_path = write_xlsx(retail_spec, TMP / "kpi_template_retail.xlsx")
    retail_sheets = read_workbook(retail_path.read_bytes())
    sales_rows = retail_sheets["Sales"]
    assert_true(sales_rows[0] == ["date", "business_day", "daily_sales"], "retail readback COMMON only")
    monthly_rows = retail_sheets["Monthly Expenses"]
    assert_true("exp_custom_variable_warehouse" in body_ids(monthly_rows), "custom survives write/read")


def test_dest_guards() -> None:
    raised = False
    try:
        assert_safe_dest(EXCEL_DIR / "kpi_template_restaurant.xlsx")
    except FixturePathError:
        raised = True
    assert_true(raised, "excel/ dest is forbidden")
    raised2 = False
    try:
        write_xlsx(build_excel_spec("restaurant", "ja"), ROOT / "excel" / "nope.xlsx")
    except FixturePathError:
        raised2 = True
    assert_true(raised2, "write_xlsx refuses excel/")
    ok = assert_safe_dest(TMP / "ok.xlsx")
    assert_true(ok.parent == TMP.resolve() or TMP.resolve() in ok.parents, "tests/tmp dest allowed")


def test_runtime_js_and_chrome() -> None:
    js = (ROOT / "js" / "kpi-excel-templates.js").read_text(encoding="utf-8")
    csv_js = (ROOT / "js" / "kpi-csv-templates.js").read_text(encoding="utf-8")
    gen_csv = (SCRIPTS / "csv_template_generator.py").read_text(encoding="utf-8")
    assert_true("KpiExcelTemplates" in js, "runtime exposes KpiExcelTemplates")
    assert_true("buildExcelSpec" in js and "workbookFromSpec" in js, "runtime builders exist")
    assert_true("KpiCsvTemplates" in js, "Excel reuses CSV templates")
    assert_true("xlsx@0.18.5" in js, "reuses existing SheetJS 0.18.5")
    assert_true("XLSX" not in csv_js, "6D JS freeze: csv templates still xlsx-free")
    assert_true("xlsx" not in gen_csv.lower(), "6D Python freeze: csv generator still xlsx-free")
    chrome = (SCRIPTS / "site_chrome.py").read_text(encoding="utf-8")
    assert_true("kpi-excel-templates.js" in chrome, "site chrome loads excel JS")
    assert_true('data-kpi-excel-template="workbook"' in chrome, "chrome has Excel DL")
    assert_true("Excel雛形をダウンロード" in chrome, "JP Excel label")
    assert_true("Download Excel Template" in chrome, "EN Excel label")
    assert_true("下載 Excel 範本" in chrome, "ZH-TW Excel label")
    assert_true("{img}excel/" not in chrome, "chrome has no static excel href")


def test_pages_use_dynamic_excel_download() -> None:
    for path in CHROME_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-excel-templates.js" in html, f"{rel} loads excel templates")
        assert_true('data-kpi-excel-template="workbook"' in html, f"{rel} has Excel button")
        assert_true("kpi-csv-templates.js" in html, f"{rel} still loads csv templates")
        menu = html.split('class="template-dl-menu"', 1)[-1].split("</details>", 1)[0]
        assert_true(".xlsx" not in menu, f"{rel} download menu has no static xlsx href")


def test_parsers_presets_untouched() -> None:
    sales_parser = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
    expense_parser = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
    presets = (SCRIPTS / "pl_line_catalog.py").read_text(encoding="utf-8")
    bt = (ROOT / "js" / "kpi-business-type.js").read_text(encoding="utf-8")
    store = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
    assert_true("KpiExcelTemplates" not in sales_parser, "sales parser unchanged")
    assert_true("KpiExcelTemplates" not in expense_parser, "expense parser unchanged")
    assert_true("csv_excel_template" not in presets, "presets unchanged by 6F")
    assert_true("KpiExcelTemplates" not in bt, "BT canonical unchanged")
    assert_true("KpiExcelTemplates" not in store, "store.php untouched")


def test_excel_dir_untouched() -> None:
    gen = (SCRIPTS / "csv_excel_template_generator.py").read_text(encoding="utf-8")
    apply = (SCRIPTS / "apply_kpi_excel_templates.py").read_text(encoding="utf-8")
    assert_true("excel/ is forbidden" in gen, "generator documents excel/ forbidden")
    assert_true('if "excel" in path.parts' in apply, "apply skips excel/")
    assert_true((ROOT / "excel").exists(), "excel/ directory still present and untouched by generator")


def test_regression_1_to_6e() -> None:
    suites = [
        ("5A", "_test_business_type_foundation.py"),
        ("5B", "_test_pl_mep_preset_engine.py"),
        ("presets", "_test_business_expense_presets.py"),
        ("6A", "_test_csv_sales_schema_6a.py"),
        ("6B", "_test_sales_csv_business_type_6b.py"),
        ("6C", "_test_expense_csv_import_6c.py"),
        ("6D", "_test_csv_templates_6d.py"),
        ("6E", "_test_csv_smoke_fixtures_6e.py"),
    ]
    for label, fname in suites:
        mod = load_module(f"reg_{label}", SCRIPTS / fname)
        rc = mod.main()
        assert_true(rc == 0, f"Unit {label} still green")


def main() -> int:
    print("--- 6F restaurant / retail ---")
    test_restaurant_workbook()
    test_retail_workbook()
    print("--- 6F other BT ---")
    test_other_business_types()
    print("--- 6F custom / locale / CSV parity ---")
    test_custom_add_rename_delete()
    test_locales_share_machine_keys()
    test_csv_schema_parity()
    print("--- 6F xlsx / dest ---")
    test_xlsx_valid_and_readback()
    test_dest_guards()
    print("--- 6F runtime / chrome ---")
    test_runtime_js_and_chrome()
    test_pages_use_dynamic_excel_download()
    print("--- 6F freeze ---")
    test_parsers_presets_untouched()
    test_excel_dir_untouched()
    print("--- 6F regression 1-6E ---")
    test_regression_1_to_6e()
    if TMP.exists():
        shutil.rmtree(TMP, ignore_errors=True)
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

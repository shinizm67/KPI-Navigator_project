# -*- coding: utf-8 -*-
"""Unit 6C: expense CSV import maps by canonical lineId first."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from csv_template_generator import (  # noqa: E402
    build_expense_template,
    csv_dumps,
    default_catalog_lines,
    parse_csv_text,
)
from pl_line_catalog import BUSINESS_TYPE_CANONICAL, reconcile_catalog_lines  # noqa: E402

FAILED = 0
PASSED = 0

PL_JS = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
SHARED_JS = (ROOT / "js" / "kpi-expense-csv-import.js").read_text(encoding="utf-8")
SALES_PARSER = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")

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


def norm_text(v) -> str:
    return re.sub(r"\s+", "", str("" if v is None else v)).lower()


def looks_like_line_id(raw: str) -> bool:
    return bool(re.match(r"^exp_[a-z0-9_]+$", str(raw or "").strip(), re.I))


def is_importable(line: dict) -> bool:
    return bool(line and line.get("lineId") and line.get("active") is not False and not line.get("presetOrphan"))


def is_header_item(raw: str) -> bool:
    return norm_text(raw) in ("lineid", "item", "label")


def make_resolver(lines, aliases=None):
    importable = [row for row in (lines or []) if is_importable(row)]
    by_id = {str(row["lineId"]): row for row in importable}
    by_id_norm = {norm_text(row["lineId"]): row for row in importable}
    by_label = {}
    for row in importable:
        for key in ("labelJa", "labelEn", "labelZh", "labelZhTw"):
            k = norm_text(row.get(key))
            if k and k not in by_label and k not in by_id_norm:
                by_label[k] = row
    aliases = aliases or {}

    def resolve(display):
        raw = str(display or "").strip()
        if not raw or is_header_item(raw):
            return None
        if raw in by_id:
            return by_id[raw]
        k = norm_text(raw)
        if k in by_id_norm:
            return by_id_norm[k]
        if k in by_label:
            return by_label[k]
        aid = aliases.get(k)
        if aid and str(aid) in by_id:
            return by_id[str(aid)]
        return None

    return resolve


def detect_columns(rows):
    header = [norm_text(c) for c in (rows[0] if rows else [])]
    date_keys = ("日付", "年月日", "年月", "date", "day", "month", "ym", "ymd")
    item_keys = ("費目", "項目", "科目", "勘定科目", "item", "category", "account", "name", "lineid")
    amt_keys = ("金額", "額", "値", "amount", "value", "price", "cost")

    def find(keys):
        for i, h in enumerate(header):
            if h in keys:
                return i
        return -1

    date_col = find(date_keys)
    item_col = find(item_keys)
    amt_col = find(amt_keys)
    confident = date_col >= 0 and item_col >= 0 and amt_col >= 0
    if confident:
        return {"dateCol": date_col, "itemCol": item_col, "amtCol": amt_col, "start": 1, "confident": True}
    fallback_amt = 3 if len(rows[0] if rows else []) >= 4 else 2
    return {
        "dateCol": 0 if date_col < 0 else date_col,
        "itemCol": 1 if item_col < 0 else item_col,
        "amtCol": fallback_amt if amt_col < 0 else amt_col,
        "start": 1,
        "confident": False,
    }


def parse_amount(v) -> int:
    if isinstance(v, (int, float)):
        return int(round(float(v)))
    raw = re.sub(r"[^0-9.\-]", "", str("" if v is None else v))
    if not raw or raw in ("-", "."):
        return 0
    try:
        return int(round(float(raw)))
    except ValueError:
        return 0


def norm_date(v):
    s = str("" if v is None else v).strip().replace("/", "-").replace(".", "-")
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r"^(\d{4})-(\d{1,2})$", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    return None


def build_plan(rows, lines, aliases=None):
    cols = detect_columns(rows)
    resolve = make_resolver(lines, aliases)
    monthly = {}
    daily = {}
    unmatched = {}
    mismatched = []
    parsed = 0
    skipped = 0
    start = cols["start"]
    for row in rows[start:]:
        date = norm_date(row[cols["dateCol"]] if cols["dateCol"] < len(row) else "")
        item = str(row[cols["itemCol"]] if cols["itemCol"] < len(row) else "").strip()
        amount = parse_amount(row[cols["amtCol"]] if cols["amtCol"] < len(row) else "")
        if not date or not item or is_header_item(item):
            skipped += 1
            continue
        parsed += 1
        is_daily = len(date) == 10
        line = resolve(item)
        if not line:
            unmatched[norm_text(item)] = item
            continue
        style = line.get("resolvedInputStyle") or line.get("inputStyle") or "monthly"
        line_id = str(line["lineId"])
        year = int(date[:4])
        month0 = int(date[5:7]) - 1
        if style == "daily":
            if not is_daily:
                mismatched.append({"item": item, "need": "daily"})
                continue
            daily.setdefault(year, {}).setdefault(line_id, {})
            daily[year][line_id][date] = daily[year][line_id].get(date, 0) + amount
        else:
            monthly.setdefault(year, {})
            key = f"{line_id}:{month0}"
            monthly[year][key] = monthly[year].get(key, 0) + amount
    return {
        "monthlyByYear": monthly,
        "dailyByYear": daily,
        "unmatched": unmatched,
        "mismatched": mismatched,
        "parsed": parsed,
        "skippedNoData": skipped,
        "cols": cols,
    }


def custom_line(line_id="exp_custom_variable_warehouse", **kwargs):
    row = {
        "lineId": line_id,
        "labelJa": "倉庫利用料",
        "labelEn": "Warehouse fee",
        "labelZh": "倉庫使用費",
        "bucket": "variable",
        "inputStyle": "monthly",
        "resolvedInputStyle": "monthly",
        "active": True,
        "isDefault": False,
        "sortOrder": 99,
    }
    row.update(kwargs)
    return row


def filled_template(business_type, style, lang, values, catalog=None):
    rec = build_expense_template(catalog, style=style, lang=lang, business_type=business_type)
    rows = parse_csv_text(rec["text"])
    for row in rows[2:]:
        lid = row[1]
        if lid in values:
            row[0] = values[lid][0]
            row[3] = str(values[lid][1])
    return rows, rec


def test_lineid_priority_and_rename() -> None:
    catalog = default_catalog_lines("retail") + [
        custom_line(labelJa="イベント什器費", labelEn="Event fixture", labelZh="活動展具費")
    ]
    resolve = make_resolver(catalog)
    hit = resolve("exp_inventory_cogs")
    assert_true(hit is not None and hit["lineId"] == "exp_inventory_cogs", "Retail merchandise maps by lineId")
    hit2 = resolve("商品仕入")
    assert_true(hit2 is not None and hit2["lineId"] == "exp_inventory_cogs", "JA label still maps")
    hit3 = resolve("Merchandise purchases")
    assert_true(hit3 is not None and hit3["lineId"] == "exp_inventory_cogs", "EN label still maps")
    custom = resolve("exp_custom_variable_warehouse")
    assert_true(custom is not None, "renamed custom maps by lineId")
    assert_true(custom["labelJa"] == "イベント什器費", "same lineId after rename")
    assert_true(resolve("倉庫利用料") is None, "old custom label is not required")
    colliding = catalog + [custom_line(line_id="exp_custom_variable_ads", labelJa="商品仕入", labelEn="Ads")]
    resolve2 = make_resolver(colliding)
    assert_true(resolve2("exp_custom_variable_ads")["lineId"] == "exp_custom_variable_ads", "lineId wins over shared label")
    assert_true(resolve2("exp_inventory_cogs")["lineId"] == "exp_inventory_cogs", "canonical lineId not stolen by custom label")


def test_inactive_orphan_unknown() -> None:
    restaurant = default_catalog_lines("restaurant")
    retail = reconcile_catalog_lines(restaurant, "retail")
    retail = retail + [
        custom_line(line_id="exp_custom_variable_hidden", active=False),
        custom_line(line_id="exp_custom_variable_ok"),
    ]
    resolve = make_resolver(retail)
    assert_true(resolve("exp_food_cost") is None, "presetOrphan food is not importable")
    assert_true(resolve("exp_custom_variable_hidden") is None, "inactive custom is not resurrected")
    assert_true(resolve("exp_custom_variable_ok") is not None, "active custom imports")
    assert_true(resolve("exp_unknown_zzzz") is None, "unknown lineId does not map")
    assert_true(looks_like_line_id("exp_unknown_zzzz"), "unknown machine key is recognized as lineId-like")
    plan = build_plan(
        [
            ["month", "item", "label", "amount"],
            ["年月", "lineId", "費目", "金額"],
            ["2026-03", "exp_unknown_zzzz", "謎", "100"],
            ["2026-03", "exp_inventory_cogs", "商品仕入", "50"],
        ],
        retail,
    )
    assert_true("exp_unknown_zzzz" in plan["unmatched"], "unknown goes unmatched")
    assert_true(plan["monthlyByYear"][2026].get("exp_inventory_cogs:2") == 50, "known line still imports")
    assert_true("exp_food_cost:2" not in plan["monthlyByYear"].get(2026, {}), "orphan not written")


def test_business_type_representative_ids() -> None:
    samples = {
        "retail": ("exp_inventory_cogs", "exp_packaging", "exp_shipping", "monthly"),
        "hair_salon": ("exp_treatment_materials", None, None, "monthly"),
        "fitness": ("exp_facility_fee", None, None, "monthly"),
        "hotel": ("exp_ota_fees", None, None, "monthly"),
        "other": ("exp_materials", "exp_outsourcing", None, "monthly"),
    }
    for code, (a, b, c, style) in samples.items():
        catalog = default_catalog_lines(code)
        resolve = make_resolver(catalog)
        for lid in (a, b, c):
            if not lid:
                continue
            hit = resolve(lid)
            assert_true(hit is not None and hit["lineId"] == lid, f"{code} maps {lid}")
            assert_true((hit.get("resolvedInputStyle") or hit.get("inputStyle")) == style, f"{code} {lid} stays {style}")
        labor = resolve("exp_variable_labor")
        assert_true(labor is not None and (labor.get("resolvedInputStyle") or labor.get("inputStyle")) == "daily", f"{code} labor is daily")


def test_daily_monthly_separation() -> None:
    catalog = default_catalog_lines("retail")
    daily_rows, _ = filled_template(
        "retail",
        "daily",
        "ja",
        {"exp_variable_labor": ("2026-03-02", 1200)},
        catalog,
    )
    plan = build_plan(daily_rows, catalog)
    assert_true(plan["dailyByYear"][2026]["exp_variable_labor"]["2026-03-02"] == 1200, "daily labor writes dailyExpenses path")
    assert_true(plan["monthlyByYear"] == {}, "daily template does not write monthly map")

    monthly_rows, _ = filled_template(
        "retail",
        "monthly",
        "ja",
        {"exp_inventory_cogs": ("2026-03", 8000), "exp_packaging": ("2026-03", 300)},
        catalog,
    )
    plan_m = build_plan(monthly_rows, catalog)
    assert_true(plan_m["monthlyByYear"][2026]["exp_inventory_cogs:2"] == 8000, "monthly merchandise writes kpi-pl-expenses path")
    assert_true(plan_m["dailyByYear"] == {}, "monthly template does not dailyize")

    mixed_daily_file = [
        ["date", "item", "label", "amount"],
        ["日付", "lineId", "費目", "金額"],
        ["2026-03-02", "exp_inventory_cogs", "商品仕入", "10"],
    ]
    plan_mix = build_plan(mixed_daily_file, catalog)
    assert_true(plan_mix["dailyByYear"] == {}, "monthly lineId is not dailyized")
    assert_true(plan_mix["monthlyByYear"][2026].get("exp_inventory_cogs:2") == 10, "monthly line + daily date stays monthly (legacy)")

    daily_on_month = [
        ["month", "item", "label", "amount"],
        ["年月", "lineId", "費目", "金額"],
        ["2026-03", "exp_variable_labor", "スタッフ人件費", "9"],
    ]
    plan_bad = build_plan(daily_on_month, catalog)
    assert_true(plan_bad["mismatched"] and plan_bad["mismatched"][0]["need"] == "daily", "daily line + YYYY-MM is skipped")
    assert_true(plan_bad["monthlyByYear"] == {} and plan_bad["dailyByYear"] == {}, "daily line is not monthly-ized")


def test_locales_and_legacy_labels() -> None:
    catalog = default_catalog_lines("retail") + [custom_line()]
    ja_rows, _ = filled_template("retail", "monthly", "ja", {"exp_inventory_cogs": ("2026-04", 1)}, catalog)
    en_rows, _ = filled_template("retail", "monthly", "en", {"exp_inventory_cogs": ("2026-04", 2)}, catalog)
    zh_rows, _ = filled_template("retail", "monthly", "zh-tw", {"exp_inventory_cogs": ("2026-04", 3)}, catalog)
    assert_true(ja_rows[0] == en_rows[0] == zh_rows[0], "machine header identical across locales")
    for rows, amt in ((ja_rows, 1), (en_rows, 2), (zh_rows, 3)):
        plan = build_plan(rows, catalog)
        assert_true(plan["monthlyByYear"][2026]["exp_inventory_cogs:3"] == amt, "machine key maps regardless of label locale")

    legacy_ja = [["日付", "費目", "金額"], ["2026-05", "商品仕入", "40"]]
    legacy_en = [["date", "item", "amount"], ["2026-05", "Merchandise purchases", "41"]]
    restaurant = default_catalog_lines("restaurant")
    rest_legacy = [["日付", "費目", "金額"], ["2026-01-03", "食材仕入れ費", "500"], ["2026-01", "家賃", "120000"]]
    assert_true(build_plan(legacy_ja, catalog)["monthlyByYear"][2026]["exp_inventory_cogs:4"] == 40, "legacy JA label CSV")
    assert_true(build_plan(legacy_en, catalog)["monthlyByYear"][2026]["exp_inventory_cogs:4"] == 41, "legacy EN label CSV")
    rest_plan = build_plan(rest_legacy, restaurant)
    assert_true(rest_plan["dailyByYear"][2026]["exp_food_cost"]["2026-01-03"] == 500, "legacy Restaurant daily food")
    assert_true(rest_plan["monthlyByYear"][2026]["exp_rent:0"] == 120000, "legacy Restaurant monthly rent")


def test_zero_blank_duplicate() -> None:
    catalog = default_catalog_lines("retail")
    rows = [
        ["month", "item", "label", "amount"],
        ["年月", "lineId", "費目", "金額"],
        ["2026-06", "exp_inventory_cogs", "商品仕入", "0"],
        ["2026-06", "exp_packaging", "包装・梱包資材", ""],
        ["2026-06", "exp_shipping", "配送・発送費", "abc"],
        ["2026-07", "exp_inventory_cogs", "商品仕入", "10"],
        ["2026-07", "exp_inventory_cogs", "商品仕入", "15"],
        ["", "exp_inventory_cogs", "商品仕入", "99"],
    ]
    plan = build_plan(rows, catalog)
    assert_true(plan["monthlyByYear"][2026]["exp_inventory_cogs:5"] == 0, "explicit 0 is stored")
    assert_true(plan["monthlyByYear"][2026]["exp_packaging:5"] == 0, "blank amount follows existing parseAmount=0")
    assert_true(plan["monthlyByYear"][2026]["exp_shipping:5"] == 0, "invalid amount follows existing parseAmount=0")
    assert_true(plan["monthlyByYear"][2026]["exp_inventory_cogs:6"] == 25, "duplicate same month+lineId is summed in-file")
    assert_true(plan["skippedNoData"] >= 1, "blank date skipped")


def test_save_targets_and_sources() -> None:
    catalog = default_catalog_lines("hotel")
    rows, _ = filled_template("hotel", "monthly", "ja", {"exp_ota_fees": ("2026-08", 7000)}, catalog)
    plan = build_plan(rows, catalog)
    assert_true("exp_ota_fees:7" in plan["monthlyByYear"][2026], "Hotel OTA writes lineId:month0")
    daily_rows, _ = filled_template("hotel", "daily", "en", {"exp_variable_labor": ("2026-08-09", 2500)}, catalog)
    dplan = build_plan(daily_rows, catalog)
    assert_true(dplan["dailyByYear"][2026]["exp_variable_labor"]["2026-08-09"] == 2500, "daily save target is years[Y].dailyExpenses[lineId][iso]")

    assert_true("lineId first" in SHARED_JS or "canonical lineId" in SHARED_JS, "shared JS documents lineId priority")
    assert_true("makeResolver" in SHARED_JS and "labelZh" in SHARED_JS, "shared JS indexes localized labels")
    assert_true("KpiExpenseCsvImport" in PL_JS, "PL client delegates to shared resolver")
    assert_true("looksLikeLineId(info.display) ? null" in PL_JS, "unknown machine keys are not fuzzy-assigned")
    assert_true("presetOrphan" in PL_JS, "PL import excludes orphans")
    assert_true("getBusinessType" not in SALES_PARSER, "Sales parser untouched")
    assert_true("KpiExpenseCsvImport" not in SALES_PARSER, "Sales parser has no expense resolver")


def test_pages_load_shared_resolver() -> None:
    for path in PL_PAGES + MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-expense-csv-import.js" in html, f"{rel} loads shared resolver")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("KpiExpenseCsvImport.makeResolver" in html, f"{rel} uses shared makeResolver")
        assert_true("looksLikeLineId(info.display) ? null" in html, f"{rel} skips fuzzy for machine keys")
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("labelMap.resolve" in html, f"{rel} MEP resolves via lineId-first helper")
        assert_true("h === 'month'" in html, f"{rel} MEP detects Unit 6D month header")
        assert_true("style === 'daily' && date.length !== 10" in html, f"{rel} MEP does not monthly-ize daily lines")


def test_regression_1_to_6d() -> None:
    u6d = load_module("u6d_csv_templates", SCRIPTS / "_test_csv_templates_6d.py")
    before = u6d.FAILED
    u6d.test_sales_restaurant_and_retail()
    u6d.test_custom_add_rename_delete()
    u6d.test_parsers_untouched_and_6a_green()
    assert_true(u6d.FAILED == before, "Unit 6D + 6A stay green")


def main() -> int:
    print("--- 6C lineId / custom ---")
    test_lineid_priority_and_rename()
    test_inactive_orphan_unknown()
    print("--- 6C business types ---")
    test_business_type_representative_ids()
    print("--- 6C daily/monthly ---")
    test_daily_monthly_separation()
    print("--- 6C locale / legacy ---")
    test_locales_and_legacy_labels()
    print("--- 6C zero / save / pages ---")
    test_zero_blank_duplicate()
    test_save_targets_and_sources()
    test_pages_load_shared_resolver()
    print("--- 6C regression ---")
    test_regression_1_to_6d()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""Unit 4: Sales CSV dailyMeal import — tri-state biz + meal parse/persist."""

from __future__ import annotations

import csv
import importlib.util
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from daily_sales_import_client import daily_sales_import_js  # noqa: E402

FAILED = 0
PASSED = 0

ANNUAL_HTML = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]
MEP_HTML = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]
ALL_HTML = ANNUAL_HTML + MEP_HTML
OFFICIAL_CSV = ROOT / "excel" / "2025_sales_official.csv"

MEAL_PERSIST_PAIRS = [
    ("dinnerSalesByDate", "dinner_sales"),
    ("totalCustomersByDate", "total_customers"),
    ("dinnerCustomersByDate", "dinner_customers"),
    ("totalGroupsByDate", "total_groups"),
    ("dinnerGroupsByDate", "dinner_groups"),
]
LUNCH_MAPS = ("lunchSalesByDate", "lunchCustomersByDate", "lunchGroupsByDate")
LUNCH_FIELDS = ("lunch_sales", "lunch_customers", "lunch_groups")
MEAL_GRID_ROWS = ("incDinner", "cust", "custDinner", "groupCnt", "groupCntDinner")
LUNCH_GRID_ROWS = ("incLunch", "custLunch", "groupCntLunch")


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def src_js() -> str:
    return daily_sales_import_js()


def helper_src() -> str:
    spec = importlib.util.spec_from_file_location(
        "apply_daily_sales_import", SCRIPTS / "apply_daily_sales_import.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_header(raw) -> str:
    s = str(raw or "").replace("\ufeff", "").strip().lower()
    return re.sub(r"[\s_]+", "", s)


def match_key(norm: str, keys: list[str]) -> bool:
    for key in keys:
        k = normalize_header(key)
        if k and (norm == k or k in norm):
            return True
    return False


def match_exact(norm: str, keys: list[str]) -> bool:
    return any(normalize_header(key) == norm for key in keys if normalize_header(key))


DATE_KEYS = ["date", "日付", "日にち", "年月日", "営業日付", "transactiondate", "salesdate"]
BIZ_KEYS = [
    "営業日",
    "営業日フラグ",
    "営業フラグ",
    "businessday",
    "businessdayflag",
    "bizday",
    "bday",
    "open",
    "isopen",
    "openflag",
    "closed",
    "closeday",
    "dayoff",
    "off",
    "店休",
    "店休日",
    "休業",
    "休業日",
    "営業",
]
SALES_KEYS = [
    "店舗売上",
    "storesales",
    "売上",
    "売上高",
    "売上金額",
    "sales",
    "amount",
    "netsales",
    "dailysales",
    "grosssales",
]
DAILY_SALES_EXACT = ["日次売上", "店舗売上", "storesales", "dailysales"]
LUNCH_SALES_KEYS = ["ランチ売上", "lunchsales", "lunchsale"]
DINNER_SALES_KEYS = ["ディナー売上", "dinnersales", "dinnersale"]
LUNCH_CUST_KEYS = ["ランチ客数", "lunchcustomers", "lunchcustomer"]
DINNER_CUST_KEYS = ["ディナー客数", "dinnercustomers", "dinnercustomer"]
TOTAL_CUST_KEYS = ["トータル客数", "総客数", "totalcustomers", "totalcustomer"]
LUNCH_GROUP_KEYS = ["ランチ組数", "lunchgroups", "lunchgroup", "lunchparties"]
DINNER_GROUP_KEYS = ["ディナー組数", "dinnergroups", "dinnergroup", "dinnerparties"]
TOTAL_GROUP_KEYS = ["トータル組数", "総組数", "totalgroups", "totalgroup", "totalparties"]
FOOD_KEYS = ["フード売上", "食売上", "foodsales", "food_sales", "foodsale", "food"]
DRINK_KEYS = ["ドリンク売上", "飲料売上", "drinksales", "drink_sales", "drinksale", "beveragesales", "beverage", "drink"]


def detect_columns(header_row):
    idx = {
        "dateIdx": -1,
        "bizIdx": -1,
        "salesIdx": -1,
        "foodIdx": -1,
        "drinkIdx": -1,
        "lunchSalesIdx": -1,
        "dinnerSalesIdx": -1,
        "lunchCustIdx": -1,
        "dinnerCustIdx": -1,
        "totalCustIdx": -1,
        "lunchGroupsIdx": -1,
        "dinnerGroupsIdx": -1,
        "totalGroupsIdx": -1,
    }

    def set_if(key, c):
        if idx[key] < 0:
            idx[key] = c

    for c, raw in enumerate(header_row):
        norm = normalize_header(raw)
        if not norm:
            continue
        if idx["lunchSalesIdx"] < 0 and match_exact(norm, LUNCH_SALES_KEYS):
            set_if("lunchSalesIdx", c)
        elif idx["dinnerSalesIdx"] < 0 and match_exact(norm, DINNER_SALES_KEYS):
            set_if("dinnerSalesIdx", c)
        elif idx["lunchCustIdx"] < 0 and match_exact(norm, LUNCH_CUST_KEYS):
            set_if("lunchCustIdx", c)
        elif idx["dinnerCustIdx"] < 0 and match_exact(norm, DINNER_CUST_KEYS):
            set_if("dinnerCustIdx", c)
        elif idx["totalCustIdx"] < 0 and match_exact(norm, TOTAL_CUST_KEYS):
            set_if("totalCustIdx", c)
        elif idx["lunchGroupsIdx"] < 0 and match_exact(norm, LUNCH_GROUP_KEYS):
            set_if("lunchGroupsIdx", c)
        elif idx["dinnerGroupsIdx"] < 0 and match_exact(norm, DINNER_GROUP_KEYS):
            set_if("dinnerGroupsIdx", c)
        elif idx["totalGroupsIdx"] < 0 and match_exact(norm, TOTAL_GROUP_KEYS):
            set_if("totalGroupsIdx", c)
        elif idx["foodIdx"] < 0 and match_key(norm, FOOD_KEYS):
            idx["foodIdx"] = c
        elif idx["drinkIdx"] < 0 and match_key(norm, DRINK_KEYS):
            idx["drinkIdx"] = c
        elif idx["dateIdx"] < 0 and match_key(norm, DATE_KEYS):
            idx["dateIdx"] = c
        elif idx["bizIdx"] < 0 and match_key(norm, BIZ_KEYS):
            idx["bizIdx"] = c
        elif idx["salesIdx"] < 0 and match_exact(norm, DAILY_SALES_EXACT):
            idx["salesIdx"] = c
        elif (
            idx["salesIdx"] < 0
            and match_key(norm, SALES_KEYS)
            and not match_key(norm, FOOD_KEYS)
            and not match_key(norm, DRINK_KEYS)
            and not (match_exact(norm, LUNCH_SALES_KEYS) or match_exact(norm, DINNER_SALES_KEYS))
        ):
            idx["salesIdx"] = c
    return idx


def parse_biz_cell(raw):
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        if raw != raw:  # NaN
            return None
        return False if raw == 0 else True
    s = str(raw).strip().lower()
    if not s:
        return None
    if s in ("0", "false", "no", "off", "休", "店休", "×", "x"):
        return False
    if s in ("1", "true", "yes", "on", "営業", "○", "◯"):
        return True
    try:
        n = float(s)
    except ValueError:
        return None
    if s == "":
        return None
    return False if n == 0 else True


def parse_date_cell(raw):
    if raw is None or raw == "":
        return None
    s = str(raw).strip()
    m = re.match(r"^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})", s)
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{y:04d}-{mo:02d}-{d:02d}"


def parse_sales_cell(raw):
    if raw is None or raw == "":
        return 0
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return raw if raw == raw else 0
    s = re.sub(r"[¥$,\s]", "", str(raw))
    if s in ("", "-"):
        return 0
    try:
        return float(s)
    except ValueError:
        return 0


def cell_has_value(row, idx):
    if idx < 0 or not row or idx >= len(row):
        return False
    raw = row[idx]
    if raw is None:
        return False
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return raw == raw
    return str(raw).strip() != ""


def read_meal_cell(row, idx, as_count: bool):
    if idx < 0 or not cell_has_value(row, idx):
        return {"missing": True}
    raw = row[idx]
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        n = float(raw)
    else:
        s = re.sub(r"[¥$,\s]", "", str(raw)).strip()
        if s in ("", "-"):
            return {"missing": True}
        if not re.match(r"^-?\d+(\.\d+)?$", s):
            return {"error": "invalid"}
        n = float(s)
    if n != n or n < 0:
        return {"error": "invalid"}
    if as_count and n != int(n):
        return {"error": "invalid"}
    return {"value": int(round(n))}


class MealInvalid(Exception):
    def __init__(self, iso, kind, reason):
        self.iso = iso
        self.kind = kind
        self.reason = reason
        super().__init__("meal-invalid")


def validate_triple(iso, kind, total, lunch, dinner):
    has_l = bool(lunch and not lunch.get("missing") and lunch.get("error") != "invalid")
    has_d = bool(dinner and not dinner.get("missing") and dinner.get("error") != "invalid")
    has_t = bool(total and not total.get("missing") and total.get("error") != "invalid")
    if has_l and not (has_t and has_d):
        raise MealInvalid(iso, kind, "lunch-only")
    if has_t and has_d and dinner["value"] > total["value"]:
        raise MealInvalid(iso, kind, "dinner-gt-total")
    if (
        has_t
        and has_l
        and has_d
        and lunch["value"] + dinner["value"] != total["value"]
    ):
        raise MealInvalid(iso, kind, "mismatch")


def put_meal(mp, iso, cell):
    if not cell or cell.get("missing") or cell.get("error") == "invalid":
        return
    mp[iso] = cell["value"]


def rows_to_maps(rows):
    if not rows:
        raise ValueError("empty")
    cols = detect_columns(rows[0])
    if cols["dateIdx"] < 0 or cols["salesIdx"] < 0:
        raise ValueError("columns")
    pending = []
    errors = []
    for row in rows[1:]:
        if not row:
            continue
        iso = parse_date_cell(row[cols["dateIdx"]] if cols["dateIdx"] < len(row) else None)
        if not iso:
            continue
        sales_missing = not cell_has_value(row, cols["salesIdx"])
        sales = int(round(parse_sales_cell(row[cols["salesIdx"]] if cols["salesIdx"] < len(row) else 0)))
        biz = parse_biz_cell(row[cols["bizIdx"]] if cols["bizIdx"] >= 0 and cols["bizIdx"] < len(row) else None)
        lunch_s = read_meal_cell(row, cols["lunchSalesIdx"], False)
        dinner_s = read_meal_cell(row, cols["dinnerSalesIdx"], False)
        lunch_c = read_meal_cell(row, cols["lunchCustIdx"], True)
        dinner_c = read_meal_cell(row, cols["dinnerCustIdx"], True)
        total_c = read_meal_cell(row, cols["totalCustIdx"], True)
        lunch_g = read_meal_cell(row, cols["lunchGroupsIdx"], True)
        dinner_g = read_meal_cell(row, cols["dinnerGroupsIdx"], True)
        total_g = read_meal_cell(row, cols["totalGroupsIdx"], True)
        for cell, kind in (
            (lunch_s, "sales"),
            (dinner_s, "sales"),
            (lunch_c, "customers"),
            (dinner_c, "customers"),
            (total_c, "customers"),
            (lunch_g, "groups"),
            (dinner_g, "groups"),
            (total_g, "groups"),
        ):
            if cell.get("error") == "invalid":
                errors.append(MealInvalid(iso, kind, "invalid"))
        lunch_s_on = bool(lunch_s and not lunch_s.get("missing") and lunch_s.get("error") != "invalid")
        dinner_s_on = bool(dinner_s and not dinner_s.get("missing") and dinner_s.get("error") != "invalid")
        if (lunch_s_on or dinner_s_on) and sales_missing:
            errors.append(MealInvalid(iso, "sales", "sales-total-missing"))
        sales_total = {"missing": True} if sales_missing else {"value": sales, "missing": False}
        try:
            validate_triple(iso, "sales", sales_total, lunch_s, dinner_s)
            validate_triple(iso, "customers", total_c, lunch_c, dinner_c)
            validate_triple(iso, "groups", total_g, lunch_g, dinner_g)
        except MealInvalid as err:
            errors.append(err)
        pending.append(
            {
                "iso": iso,
                "sales": sales,
                "biz": biz,
                "lunch_s": lunch_s,
                "dinner_s": dinner_s,
                "lunch_c": lunch_c,
                "dinner_c": dinner_c,
                "total_c": total_c,
                "lunch_g": lunch_g,
                "dinner_g": dinner_g,
                "total_g": total_g,
            }
        )
    if errors:
        raise errors[0]
    maps = {
        "salesByDate": {},
        "businessDayByDate": {},
        "dinnerSalesByDate": {},
        "lunchSalesByDate": {},
        "totalCustomersByDate": {},
        "lunchCustomersByDate": {},
        "dinnerCustomersByDate": {},
        "totalGroupsByDate": {},
        "lunchGroupsByDate": {},
        "dinnerGroupsByDate": {},
        "dailyIncome": {},
        "dailyExpenses": {},
    }
    for rec in pending:
        iso = rec["iso"]
        maps["salesByDate"][iso] = rec["sales"]
        if rec["biz"] is not None:
            maps["businessDayByDate"][iso] = bool(rec["biz"])
        put_meal(maps["lunchSalesByDate"], iso, rec["lunch_s"])
        put_meal(maps["dinnerSalesByDate"], iso, rec["dinner_s"])
        put_meal(maps["lunchCustomersByDate"], iso, rec["lunch_c"])
        put_meal(maps["dinnerCustomersByDate"], iso, rec["dinner_c"])
        put_meal(maps["totalCustomersByDate"], iso, rec["total_c"])
        put_meal(maps["lunchGroupsByDate"], iso, rec["lunch_g"])
        put_meal(maps["dinnerGroupsByDate"], iso, rec["dinner_g"])
        put_meal(maps["totalGroupsByDate"], iso, rec["total_g"])
    maps["imported"] = len(pending)
    return maps


class MealPersist(Exception):
    pass


class FakeStore:
    def __init__(self, existing=None):
        self.dailyMeal = existing or {}
        self.dailyIncome = {}
        self.dailyExpenses = {}
        self.persist_count = 0
        self.write_log = []
        self.years = {}

    def writeDailyMeal(self, field, iso, value):
        self.write_log.append((field, iso, value))
        if field not in self.dailyMeal:
            self.dailyMeal[field] = {}
        if value is None:
            self.dailyMeal[field].pop(iso, None)
            return True
        self.dailyMeal[field][iso] = int(value)
        return True

    def persistStore(self):
        self.persist_count += 1

    def persistFromAnnualDaily(self, daily, meta=None):
        self.persist_count += 1
        return True

    def persistFromPastSales(self, ps, meta=None):
        self.persist_count += 1
        return True


class AnnualLikeStore:
    """Mirrors Annual HTML: getStore + persistFromAnnualDaily, no writeDailyMeal export."""

    def __init__(self):
        self.store = {"years": {}}
        self.persist_count = 0
        self.write_log = []

    def getStore(self):
        return self.store

    def persistFromAnnualDaily(self, daily, meta=None):
        self.persist_count += 1
        return True


def write_daily_meal_via_get_store(store_obj, field, iso, value) -> bool:
    store = store_obj.getStore()
    if not store or not isinstance(store, dict):
        return False
    y = int(str(iso)[:4])
    years = store.setdefault("years", {})
    rec = years.get(y) or years.get(str(y))
    if not isinstance(rec, dict):
        rec = {"year": y, "plan": {}}
        years[y] = rec
    meal = rec.get("dailyMeal")
    if not isinstance(meal, dict):
        rec["dailyMeal"] = {}
        meal = rec["dailyMeal"]
    if not isinstance(meal.get(field), dict):
        meal[field] = {}
    meal[field][iso] = int(value)
    store_obj.write_log.append((field, iso, value))
    return True


def persist_daily_meal_from_maps(maps, store) -> int:
    ops = []
    for map_key, field in MEAL_PERSIST_PAIRS:
        src = maps.get(map_key) or {}
        for iso, val in src.items():
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(iso)):
                raise MealInvalid(iso, "sales", "invalid")
            if not isinstance(val, (int, float)) or isinstance(val, bool) or val != val or val < 0:
                raise MealInvalid(iso, "sales", "invalid")
            ops.append((field, str(iso), int(round(val))))
    if not ops:
        return 0
    has_write = callable(getattr(store, "writeDailyMeal", None))
    has_store = callable(getattr(store, "getStore", None))
    if not has_write and not has_store:
        raise MealPersist("no-write")
    wrote = 0
    for field, iso, val in ops:
        if has_write:
            ok = store.writeDailyMeal(field, iso, val)
        else:
            ok = write_daily_meal_via_get_store(store, field, iso, val)
        if not ok:
            raise MealPersist("write-false")
        wrote += 1
    return wrote


def persist_annual_csv_from_maps(maps, store):
    persist_daily_meal_from_maps(maps, store)
    store.persistFromAnnualDaily(
        {
            "targetSalesByDate": maps.get("salesByDate") or {},
            "businessDayByDate": maps.get("businessDayByDate") or {},
        },
        {"source": "annual-edit-csv-import"},
    )


def csv_rows(header, data_rows):
    return [header] + data_rows


def test_source_tristate() -> None:
    js = src_js()
    assert_true("function parseBizCell(raw) {" in js, "parseBizCell is unary")
    assert_true("parseBizCell(raw, salesAmount)" not in js, "no salesAmount parseBizCell")
    assert_true("Never infer from sales" in js, "tri-state comment")
    assert_true("if (rec.biz !== null) businessDayByDate[rec.iso] = !!rec.biz" in js, "biz key only when parsed")
    assert_true("if (!biz) sales = 0" not in js, "closed day does not zero sales")
    assert_true("KPI-BIZDAY-IMPORT-DD" in js, "applyToRowState DD marker")
    assert_true(
        "Object.prototype.hasOwnProperty.call(bizMap0, iso)" in js,
        "applyToRowState uses key presence",
    )
    assert_true("Number(salesAmount) > 0" not in js, "source no longer infers biz from sales")
    helper = helper_src()
    apply_text = (SCRIPTS / "apply_daily_sales_import.py").read_text(encoding="utf-8")
    assert_true("persistDailyMealFromMaps" in apply_text, "apply helper calls persistDailyMealFromMaps")
    assert_true("writeMealGrid('incLunch'" not in apply_text, "MEP grid does not write incLunch")
    assert_true("writeMealGrid('custLunch'" not in apply_text, "MEP grid does not write custLunch")
    assert_true("writeMealGrid('groupCntLunch'" not in apply_text, "MEP grid does not write groupCntLunch")
    for row_id in MEAL_GRID_ROWS:
        assert_true(f"writeMealGrid('{row_id}'" in apply_text, f"MEP grid writes {row_id}")
    assert_true("lunch_sales" not in helper.MEP_SALES_CSV_HELPER, "MEP persist helper has no lunch_sales")
    assert_true("persistDailyMealFromMaps(mealMaps)" in helper.PAST_SALES_CSV_HELPER, "Past Sales persist meal")
    assert_true("persistDailyMealFromMaps(maps)" in helper.MEP_SALES_CSV_HELPER, "MEP persist meal")
    assert_true("persistDailyMealFromMaps(maps)" in helper.AEM_CSV_NEW, "Annual edit persist meal")
    assert_true("persistDailyMealFromMaps(maps)" in helper.SDM_CSV_NEW, "Sales Data persist meal")
    assert_true("KpiYearStore.persistStore" not in helper.AEM_APPLY_NEW, "Annual edit does not call persistStore")
    assert_true("KpiYearStore.persistStore" not in helper.SDM_APPLY_NEW, "Sales Data does not call persistStore")
    assert_true("persistFromAnnualDaily" in helper.AEM_APPLY_NEW, "Annual edit uses persistFromAnnualDaily")
    assert_true("persistFromAnnualDaily" in helper.SDM_APPLY_NEW, "Sales Data uses persistFromAnnualDaily")
    assert_true("persistFromAnnualDaily" in helper.MEP_SALES_CSV_HELPER, "MEP uses persistFromAnnualDaily")
    assert_true("persistFromPastSales" in helper.PAST_SALES_CSV_HELPER, "Past Sales uses persistFromPastSales")
    assert_true(
        helper.AEM_APPLY_NEW.find("persistFromAnnualDaily !== 'function'")
        < helper.AEM_APPLY_NEW.find("persistDailyMealFromMaps"),
        "Annual persist API checked before meal writes",
    )
    assert_true(
        helper.SDM_APPLY_NEW.find("persistFromAnnualDaily !== 'function'")
        < helper.SDM_APPLY_NEW.find("persistDailyMealFromMaps"),
        "Sales Data persist API checked before meal writes",
    )
    _ = helper


def test_headers_and_order() -> None:
    official = detect_columns(
        [
            "年月日",
            "営業日",
            "日次売上",
            "ランチ売上",
            "ディナー売上",
            "ランチ客数",
            "ディナー客数",
            "トータル客数",
            "ランチ組数",
            "ディナー組数",
            "トータル組数",
        ]
    )
    pipe = detect_columns(
        ["年月日", "営業日|店休日", "日次売上", "ランチ客数", "ディナー客数", "トータル客数"]
    )
    shuffled = detect_columns(
        [
            "ランチ売上",
            "ディナー売上",
            "年月日",
            "日次売上",
            "営業日",
            "トータル客数",
            "ランチ客数",
            "ディナー客数",
        ]
    )
    assert_true(official["bizIdx"] == 1, "営業日 header detected")
    assert_true(pipe["bizIdx"] == 1, "営業日|店休日 header detected")
    assert_true(official["salesIdx"] == 2, "日次売上 is salesIdx")
    assert_true(official["lunchSalesIdx"] == 3, "ランチ売上 not sales")
    assert_true(official["dinnerSalesIdx"] == 4, "ディナー売上 not sales")
    assert_true(shuffled["salesIdx"] == 3, "column order does not steal 日次売上")
    assert_true(shuffled["lunchSalesIdx"] == 0, "lunch sales exact even when first")
    assert_true(shuffled["dinnerSalesIdx"] == 1, "dinner sales exact even when early")
    js = src_js()
    assert_true("matchExact(norm, LUNCH_SALES_KEYS)" in js, "JS exact-matches lunch sales")
    assert_true("matchExact(norm, DAILY_SALES_EXACT_KEYS)" in js, "JS exact-matches daily sales first")


def test_biz_tristate_behavior() -> None:
    rows = csv_rows(
        ["年月日", "営業日", "日次売上"],
        [
            ["2025-01-01", "", 900],
            ["2025-01-02", "0", 800],
            ["2025-01-03", "1", 700],
            ["2025-01-04", "0", 500],
        ],
    )
    maps = rows_to_maps(rows)
    assert_true("2025-01-01" not in maps["businessDayByDate"], "blank biz is missing")
    assert_true(maps["businessDayByDate"]["2025-01-02"] is False, "explicit 0 is false")
    assert_true(maps["businessDayByDate"]["2025-01-03"] is True, "explicit 1 is true")
    assert_true(maps["salesByDate"]["2025-01-01"] == 900, "blank biz does not infer from sales")
    assert_true(maps["salesByDate"]["2025-01-04"] == 500, "closed day keeps daily sales")
    assert_true(parse_biz_cell("") is None, "parseBizCell blank is null")
    assert_true(parse_biz_cell("不明") is None, "unparseable biz is null")


def test_missing_vs_zero_and_validation() -> None:
    ok = rows_to_maps(
        csv_rows(
            ["年月日", "営業日", "日次売上", "ランチ売上", "ディナー売上", "ランチ客数", "ディナー客数", "トータル客数", "ランチ組数", "ディナー組数", "トータル組数"],
            [["2025-01-10", "1", "103730", "", "", "24", "13", "37", "11", "6", "17"]],
        )
    )
    assert_true("2025-01-10" not in ok["lunchSalesByDate"], "blank lunch sales missing")
    assert_true("2025-01-10" not in ok["dinnerSalesByDate"], "blank dinner sales missing")
    assert_true(ok["lunchCustomersByDate"]["2025-01-10"] == 24, "lunch cust parsed for validation")
    assert_true(ok["dinnerCustomersByDate"]["2025-01-10"] == 13, "dinner cust 13")
    assert_true(ok["totalCustomersByDate"]["2025-01-10"] == 37, "total cust 37")
    assert_true(ok["salesByDate"]["2025-01-10"] == 103730, "daily sales unchanged by meal")

    zero = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "ディナー客数", "トータル客数"],
            [["2025-01-01", "0", "0", "0"]],
        )
    )
    assert_true(zero["dinnerCustomersByDate"]["2025-01-01"] == 0, "explicit 0 keeps key")
    assert_true(zero["totalCustomersByDate"]["2025-01-01"] == 0, "explicit 0 total keeps key")

    dinner_only = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "ディナー客数", "トータル客数"],
            [["2025-02-01", "100", "13", "37"]],
        )
    )
    assert_true("2025-02-01" not in dinner_only["lunchCustomersByDate"], "lunch missing allowed")
    assert_true(dinner_only["dinnerCustomersByDate"]["2025-02-01"] == 13, "dinner kept")

    mismatch = None
    try:
        rows_to_maps(
            csv_rows(
                ["年月日", "日次売上", "ランチ客数", "ディナー客数", "トータル客数"],
                [["2025-03-01", "100", "40", "13", "37"]],
            )
        )
    except MealInvalid as err:
        mismatch = err
    assert_true(mismatch is not None and mismatch.reason == "mismatch", "40+13!=37 stops")
    assert_true(mismatch.iso == "2025-03-01", "mismatch names the date")

    lunch_only = None
    try:
        rows_to_maps(
            csv_rows(
                ["年月日", "日次売上", "ランチ客数", "トータル客数"],
                [["2025-03-02", "100", "24", "37"]],
            )
        )
    except MealInvalid as err:
        lunch_only = err
    assert_true(lunch_only is not None and lunch_only.reason == "lunch-only", "lunch without dinner stops")


def test_invalid_no_partial() -> None:
    store = FakeStore({"dinner_sales": {"2025-01-01": 9}})
    cases = [
        [["2025-04-01", "100", "abc", "1", "2"]],
        [["2025-04-02", "100", "-1", "1", "2"]],
        [["2025-04-03", "100", "1.5", "1", "2"]],
        [
            ["2025-04-04", "100", "1", "1", "2"],
            ["2025-04-05", "100", "x", "1", "2"],
        ],
    ]
    headers = ["年月日", "日次売上", "ランチ客数", "ディナー客数", "トータル客数"]
    for data in cases:
        caught = None
        try:
            maps = rows_to_maps(csv_rows(headers, data))
            persist_daily_meal_from_maps(maps, store)
        except MealInvalid as err:
            caught = err
        assert_true(caught is not None, f"invalid rows stop: {data[0]}")
        assert_true(store.persist_count == 0, "no persistStore on invalid")
        assert_true(store.write_log == [], "no writeDailyMeal on invalid")
        assert_true(store.dailyMeal["dinner_sales"]["2025-01-01"] == 9, "existing canonical kept")


def test_persist_five_fields_only() -> None:
    store = FakeStore(
        {
            "dinner_sales": {"2025-01-09": 111},
            "lunch_sales": {"2025-01-09": 50},
        }
    )
    maps = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "ランチ売上", "ディナー売上", "ランチ客数", "ディナー客数", "トータル客数", "ランチ組数", "ディナー組数", "トータル組数"],
            [
                ["2025-01-10", "100", "", "40", "24", "13", "37", "11", "6", "17"],
                ["2025-01-11", "80", "", "", "0", "0", "0", "0", "0", "0"],
            ],
        )
    )
    assert_true(maps["salesByDate"]["2025-01-10"] == 100, "meal dinner 40 does not overwrite daily 100")
    wrote = persist_daily_meal_from_maps(maps, store)
    assert_true(wrote == 9, f"persist writes 9 explicit meal cells, got {wrote}")
    payload = store.dailyMeal
    assert_true(payload.get("dinner_sales", {}).get("2025-01-10") == 40, "dinner_sales saved")
    assert_true("2025-01-11" not in payload.get("dinner_sales", {}), "blank dinner sales does not write")
    assert_true(payload.get("dinner_sales", {}).get("2025-01-09") == 111, "blank col does not delete existing")
    assert_true(payload.get("lunch_sales", {}).get("2025-01-09") == 50, "existing lunch canonical untouched")
    assert_true("2025-01-10" not in payload.get("lunch_sales", {}), "lunch_sales not saved from CSV")
    assert_true(payload["total_customers"]["2025-01-10"] == 37, "total_customers saved")
    assert_true(payload["dinner_customers"]["2025-01-10"] == 13, "dinner_customers saved")
    assert_true(payload["total_groups"]["2025-01-10"] == 17, "total_groups saved")
    assert_true(payload["dinner_groups"]["2025-01-10"] == 6, "dinner_groups saved")
    assert_true(payload["total_customers"]["2025-01-11"] == 0, "explicit 0 customers saved")
    assert_true("2025-01-10" not in payload.get("lunch_customers", {}), "lunch_customers not persisted")
    assert_true("2025-01-10" not in payload.get("lunch_groups", {}), "lunch_groups not persisted")
    assert_true(store.dailyIncome == {}, "meal not written to dailyIncome")
    assert_true(store.dailyExpenses == {}, "meal not written to dailyExpenses")
    fields_written = {f for f, _iso, _v in store.write_log}
    assert_true(fields_written <= {p[1] for p in MEAL_PERSIST_PAIRS}, "only 5 persist fields")
    assert_true(not (fields_written & set(LUNCH_FIELDS)), "no lunch_* writes")
    js = src_js()
    for map_key, field in MEAL_PERSIST_PAIRS:
        assert_true(f"'{map_key}', '{field}'" in js, f"JS persist pair {field}")
    assert_true("['lunchSalesByDate', 'lunch_sales']" not in js, "JS does not persist lunch_sales")


def test_official_csv() -> None:
    assert_true(OFFICIAL_CSV.is_file(), "official csv exists for read-only parse")
    text = OFFICIAL_CSV.read_text(encoding="utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    maps = rows_to_maps(rows)
    assert_true(maps["imported"] == 365, "official 365 data rows")
    assert_true(maps["lunchSalesByDate"] == {}, "official lunch sales not stored")
    assert_true(maps["dinnerSalesByDate"] == {}, "official dinner sales not stored")
    assert_true(len(maps["totalCustomersByDate"]) == 365, "official total customers all days")
    assert_true(len(maps["dinnerCustomersByDate"]) == 365, "official dinner customers all days")
    assert_true(len(maps["totalGroupsByDate"]) == 365, "official total groups all days")
    assert_true(len(maps["dinnerGroupsByDate"]) == 365, "official dinner groups all days")
    assert_true(maps["salesByDate"]["2025-01-10"] == 103730, "official daily sales")
    assert_true(maps["dinnerCustomersByDate"]["2025-01-10"] == 13, "official dinner cust")
    assert_true(maps["totalCustomersByDate"]["2025-01-10"] == 37, "official total cust")
    assert_true(maps["lunchCustomersByDate"]["2025-01-10"] == 24, "lunch cust validation-only in maps")
    store = FakeStore()
    persist_daily_meal_from_maps(maps, store)
    assert_true("lunch_sales" not in store.dailyMeal or store.dailyMeal.get("lunch_sales") == {}, "no lunch_sales persist")
    assert_true("dinner_sales" not in store.dailyMeal or store.dailyMeal.get("dinner_sales") == {}, "no dinner_sales persist")
    assert_true(store.dailyMeal["total_customers"]["2025-01-10"] == 37, "official total_customers persisted")
    assert_true(store.dailyMeal["dinner_customers"]["2025-01-10"] == 13, "official dinner_customers persisted")
    assert_true(store.dailyMeal["total_groups"]["2025-01-10"] == 17, "official total_groups persisted")
    assert_true(store.dailyMeal["dinner_groups"]["2025-01-10"] == 6, "official dinner_groups persisted")
    assert_true("2025-01-10" not in store.dailyMeal.get("lunch_customers", {}), "lunch customers not persisted")
    lunch_writes = [t for t in store.write_log if t[0] in LUNCH_FIELDS]
    assert_true(lunch_writes == [], "official lunch_* validation only")


def extract_import_block(html: str) -> str:
    m = re.search(r"/\* KPI-DAILY-SALES-IMPORT \*/[\s\S]*?\}\)\(\);", html)
    return m.group(0) if m else ""


def test_runtime_html() -> None:
    js = src_js().strip()
    marker = "/* KPI-DAILY-SALES-IMPORT */"
    for path in ALL_HTML:
        html = path.read_text(encoding="utf-8")
        block = extract_import_block(html)
        assert_true(marker in html, f"{path.name} has import marker")
        assert_true("function parseBizCell(raw) {" in block, f"{path} unary parseBizCell")
        assert_true("Never infer from sales" in block, f"{path} never infer")
        assert_true("if (!biz) sales = 0" not in block, f"{path} does not zero closed sales")
        assert_true("persistDailyMealFromMaps" in block, f"{path} exports persistDailyMealFromMaps")
        assert_true("meal-invalid" in block, f"{path} meal-invalid alert path")
        assert_true("Lunch requires both total and dinner." in block, f"{path} EN lunch-only")
        assert_true("匯入午餐需要合計與晚餐。" in block, f"{path} ZH lunch-only")
        assert_true("ランチを取り込むには合計とディナーの両方が必要です。" in block, f"{path} JA lunch-only")
        src_core = js.replace("      /* KPI-DAILY-SALES-IMPORT */", marker)
        assert_true(marker in src_core and "persistDailyMealFromMaps" in src_core, "source ready")
    helper = helper_src()
    for path in ALL_HTML:
        html = path.read_text(encoding="utf-8")
        assert_true("persistDailyMealFromMaps(" in html, f"{path} apply/persist calls meal persist")
    for path in MEP_HTML:
        html = path.read_text(encoding="utf-8")
        assert_true("writeMealGrid('incDinner'" in html, f"{path} MEP dinner grid")
        assert_true("writeMealGrid('incLunch'" not in html, f"{path} no lunch grid write")
        apply_fn = helper.MEP_APPLY_IMPORT_NEW
        assert_true("writeMealGrid('incLunch'" not in apply_fn, "apply template no lunch")
    annual_ja = (ROOT / "app/annual/index.html").read_text(encoding="utf-8")
    assert_true("refreshSalesDataTableTotals();" in annual_ja, "sales data totals helper still present")
    sdm = annual_ja.split("btnSave.addEventListener('click', saveSalesDataModal)")[1].split("document.addEventListener('annual:businessDayMapChanged'")[0]
    assert_true("persistDailyMealFromMaps" in sdm, "Sales Data CSV persist meal")
    ja = (ROOT / "app/monthly/edit/index.html").read_text(encoding="utf-8")
    en = (ROOT / "en/app/monthly/edit/index.html").read_text(encoding="utf-8")
    zh = (ROOT / "zh-tw/app/monthly/edit/index.html").read_text(encoding="utf-8")
    ja_block = extract_import_block(ja)
    en_block = extract_import_block(en)
    zh_block = extract_import_block(zh)
    assert_true(ja_block == en_block == zh_block, "JP/EN/ZH-TW import IIFE identical")
    src_block = extract_import_block(js if js.startswith("/*") else "      " + js)
    # Compare HTML block to generator output (strip leading spaces differences via marker content)
    gen_block = extract_import_block("      " + js if "KPI-DAILY-SALES-IMPORT" in js else js)
    if not gen_block:
        gen_block = js[js.find(marker) : js.rfind("})();") + 5] if marker in js else ""
    html_norm = re.sub(r"\r\n", "\n", ja_block).strip()
    gen_norm = re.sub(r"\r\n", "\n", gen_block).strip()
    assert_true(html_norm == gen_norm, "runtime HTML import block matches generator source")
    _ = src_block


def test_error_i18n() -> None:
    js = src_js()
    assert_true("合計と内訳が一致しません。値は自動修正しません。" in js, "JA mismatch copy")
    assert_true("Total and breakdown do not match. Values are not auto-corrected." in js, "EN mismatch copy")
    assert_true("合計與明細不一致。不會自動修正。" in js, "ZH mismatch copy")
    assert_true("Dinner exceeds total. Values are not auto-corrected." in js, "EN dinner-gt-total")
    assert_true("code === 'meal-invalid'" in js, "alert path for meal-invalid")
    assert_true("code === 'meal-persist'" in js, "alert path for meal-persist")


def expect_stop(rows, reason) -> None:
    caught = None
    try:
        rows_to_maps(rows)
    except MealInvalid as err:
        caught = err
    assert_true(caught is not None and caught.reason == reason, f"expected {reason}, got {getattr(caught, 'reason', None)}")


def test_lunch_incomplete_and_dinner_gt_total() -> None:
    lunch_dinner_no_total = csv_rows(
        ["年月日", "日次売上", "ランチ客数", "ディナー客数"],
        [["2025-05-01", "100", "24", "13"]],
    )
    expect_stop(lunch_dinner_no_total, "lunch-only")

    total_lunch_no_dinner = csv_rows(
        ["年月日", "日次売上", "ランチ客数", "トータル客数"],
        [["2025-05-02", "100", "24", "37"]],
    )
    expect_stop(total_lunch_no_dinner, "lunch-only")

    lunch_only = csv_rows(
        ["年月日", "日次売上", "ランチ客数"],
        [["2025-05-03", "100", "24"]],
    )
    expect_stop(lunch_only, "lunch-only")

    dinner_gt = csv_rows(
        ["年月日", "日次売上", "ディナー客数", "トータル客数"],
        [["2025-05-04", "100", "11", "10"]],
    )
    expect_stop(dinner_gt, "dinner-gt-total")

    dinner_eq = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "ディナー客数", "トータル客数"],
            [["2025-05-05", "100", "10", "10"]],
        )
    )
    assert_true(dinner_eq["dinnerCustomersByDate"]["2025-05-05"] == 10, "equal dinner accepted")
    assert_true(dinner_eq["totalCustomersByDate"]["2025-05-05"] == 10, "equal total accepted")
    assert_true("2025-05-05" not in dinner_eq["lunchCustomersByDate"], "derived lunch not stored")

    zero_eq = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "ディナー客数", "トータル客数"],
            [["2025-05-06", "0", "0", "0"]],
        )
    )
    assert_true(zero_eq["dinnerCustomersByDate"]["2025-05-06"] == 0, "0/0 dinner accepted")
    assert_true(zero_eq["totalCustomersByDate"]["2025-05-06"] == 0, "0/0 total accepted")

    blank_daily_dinner = csv_rows(
        ["年月日", "日次売上", "ランチ売上", "ディナー売上"],
        [["2025-05-07", "", "", "40"]],
    )
    expect_stop(blank_daily_dinner, "sales-total-missing")

    blank_daily_no_meal = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "ランチ売上", "ディナー売上"],
            [["2025-05-08", "", "", ""]],
        )
    )
    assert_true(blank_daily_no_meal["salesByDate"]["2025-05-08"] == 0, "blank daily stays 0 when meal sales blank")
    assert_true("2025-05-08" not in blank_daily_no_meal["dinnerSalesByDate"], "blank dinner sales missing")
    assert_true("2025-05-08" not in blank_daily_no_meal["lunchSalesByDate"], "blank lunch sales missing")


def test_annual_persist_path() -> None:
    maps = rows_to_maps(
        csv_rows(
            ["年月日", "日次売上", "ディナー客数", "トータル客数"],
            [["2025-06-01", "100", "13", "37"]],
        )
    )
    annual = AnnualLikeStore()
    persist_annual_csv_from_maps(maps, annual)
    assert_true(annual.persist_count == 1, "Annual valid import persistFromAnnualDaily once")
    meal = annual.store["years"][2025]["dailyMeal"]
    assert_true(meal["dinner_customers"]["2025-06-01"] == 13, "Annual getStore dinner_customers")
    assert_true(meal["total_customers"]["2025-06-01"] == 37, "Annual getStore total_customers")
    assert_true("lunch_customers" not in meal or "2025-06-01" not in meal.get("lunch_customers", {}), "Annual no lunch field")

    bad = AnnualLikeStore()
    caught = None
    try:
        rows_to_maps(
            csv_rows(
                ["年月日", "日次売上", "ディナー客数", "トータル客数"],
                [["2025-06-02", "100", "11", "10"]],
            )
        )
        persist_annual_csv_from_maps({}, bad)
    except MealInvalid as err:
        caught = err
    assert_true(caught is not None and caught.reason == "dinner-gt-total", "Annual invalid stops before persist")
    assert_true(bad.persist_count == 0, "Annual invalid PUT 0")
    assert_true(bad.write_log == [], "Annual invalid store writes 0")
    assert_true(bad.store["years"] == {}, "Annual invalid years unchanged")


def test_persist_fields_match_across_entries() -> None:
    helper = helper_src()
    js = src_js()
    for map_key, field in MEAL_PERSIST_PAIRS:
        needle = f"'{map_key}', '{field}'"
        assert_true(needle in js, f"JS pair {field}")
        assert_true(needle in helper.MEP_SALES_CSV_HELPER or "MEAL_PERSIST_PAIRS" in js, f"shared field {field}")
    assert_true("writeMealGrid('incDinner'" in helper.MEP_APPLY_IMPORT_NEW, "MEP dinner sales grid")
    assert_true("writeMealGrid('cust'" in helper.MEP_APPLY_IMPORT_NEW, "MEP total customers grid")
    assert_true("writeMealGrid('custDinner'" in helper.MEP_APPLY_IMPORT_NEW, "MEP dinner customers grid")
    assert_true("writeMealGrid('groupCnt'" in helper.MEP_APPLY_IMPORT_NEW, "MEP total groups grid")
    assert_true("writeMealGrid('groupCntDinner'" in helper.MEP_APPLY_IMPORT_NEW, "MEP dinner groups grid")
    for lunch_row in LUNCH_GRID_ROWS:
        assert_true(f"writeMealGrid('{lunch_row}'" not in helper.MEP_APPLY_IMPORT_NEW, f"no {lunch_row}")


def test_generator_main_scope() -> None:
    helper = helper_src()
    src = (SCRIPTS / "apply_daily_sales_import.py").read_text(encoding="utf-8")
    main_src = src.split("def main() -> int:", 1)[1].split('if __name__ == "__main__":', 1)[0]
    assert_true("apply_csv_upload_tooltip_css" not in main_src, "main does not call tooltip CSS")
    assert_true("subprocess" not in main_src, "main has no subprocess")
    assert_true("profit/pl" not in main_src, "main does not mention PL")
    assert_true("ANNUAL_PAGES + MEP_PAGES" in main_src or (
        "for path in ANNUAL_PAGES:" in main_src and "for path in MEP_PAGES:" in main_src
    ), "main patches annual + mep")
    assert_true(len(helper.ANNUAL_PAGES) == 3, "3 annual pages")
    assert_true(len(helper.MEP_PAGES) == 3, "3 mep pages")
    assert_true("app/profit/pl/index.html" not in src.split("def main()", 1)[1], "PL not in main remainder")
    css_call = "apply_csv_upload_tooltip_css.py"
    after_main = src.split("def main() -> int:", 1)[1]
    assert_true(css_call not in after_main, "tooltip css script not invoked after main")


def test_click_time_api_lookup() -> None:
    js = src_js()
    begin = js.split("function beginImport(options)", 1)[1].split("function bindButton", 1)[0]
    assert_true("function getDailyImportApi()" in js, "getDailyImportApi exists")
    assert_true("var api = window.__KPI_DAILY_IMPORT;" in js, "getDailyImportApi reads window")
    assert_true("function beginImport(options)" in js, "beginImport exists")
    assert_true("var live = getDailyImportApi();" in begin, "beginImport re-gets API on file select")
    assert_true("live.parseFile(file)" in begin, "beginImport uses live.parseFile")
    assert_true(
        "parseFile(file)" not in begin.replace("live.parseFile(file)", ""),
        "beginImport does not close over parseFile",
    )
    assert_true(
        "CSV取込エンジンの読み込みに失敗しました。ページを再読み込みしてください。" in js,
        "existing JA engine-fail copy",
    )
    assert_true("CSV import engine failed to load. Please reload the page." in js, "existing EN engine-fail copy")
    assert_true("CSV 匯入引擎載入失敗，請重新整理頁面。" in js, "existing ZH engine-fail copy")
    bind = js.split("function bindButton(btn, options)", 1)[1].split("window.__KPI_DAILY_IMPORT =", 1)[0]
    assert_true("beginImport(options);" in bind, "bindButton click calls beginImport")
    helper = helper_src()
    for name, block in (
        ("Annual Edit", helper.AEM_CSV_NEW),
        ("Past Sales", helper.PSM_CSV_NEW),
        ("Sales Data", helper.SDM_CSV_NEW),
        ("MEP", helper.MEP_CSV_INNER_NEW),
    ):
        assert_true("var api = window.__KPI_DAILY_IMPORT;" in block, f"{name} click re-reads API")
        assert_true("typeof api.parseFile !== 'function'" in block, f"{name} requires parseFile at click")
        assert_true("api.beginImport(" in block, f"{name} click uses beginImport")
        assert_true("data-kpi-import-bound" in block, f"{name} avoids double picker")
        assert_true(
            "if (btnCsv && window.__KPI_DAILY_IMPORT)" not in block,
            f"{name} does not skip bind when API missing",
        )
    assert_true("} else {" not in helper.MEP_CSV_INNER_NEW, "MEP has no bind-time else fail handler")

    alerts = []
    parse_used = []

    class FakeBtn:
        def __init__(self):
            self.attrs = {}
            self.listeners = []

        def getAttribute(self, key):
            return self.attrs.get(key)

        def setAttribute(self, key, value):
            self.attrs[key] = value

        def addEventListener(self, _ev, fn):
            self.listeners.append(fn)

        def click(self):
            for fn in list(self.listeners):
                fn()

    def attach_wrapper(btn, opts, window_obj):
        def on_click():
            api = window_obj.get("__KPI_DAILY_IMPORT")
            if btn.getAttribute("data-kpi-import-bound") == "1":
                return
            if not api or not callable(api.get("parseFile")) or not callable(api.get("beginImport")):
                alerts.append("engine-missing")
                return
            api["bindButton"](btn, opts)
            api["beginImport"](opts)

        btn.addEventListener("click", on_click)

    def make_api(window_obj, tag):
        def get_daily():
            api = window_obj.get("__KPI_DAILY_IMPORT")
            if (
                not api
                or not callable(api.get("parseFile"))
                or not callable(api.get("rowsToMaps"))
                or not callable(api.get("applyToRowState"))
            ):
                return None
            return api

        def begin_import(_opts):
            live = get_daily()
            if not live:
                alerts.append("engine-missing")
                return
            parse_used.append(live["parseFile"]())

        def bind_button(btn, opts):
            if btn.getAttribute("data-kpi-import-bound") == "1":
                return
            btn.setAttribute("data-kpi-import-bound", "1")
            btn.addEventListener("click", lambda: begin_import(opts))

        return {
            "parseFile": lambda: tag,
            "rowsToMaps": lambda: None,
            "applyToRowState": lambda: None,
            "beginImport": begin_import,
            "bindButton": bind_button,
        }

    for entry in ("MEP", "Annual Edit", "Sales Data", "Past Sales"):
        alerts.clear()
        parse_used.clear()
        window_obj = {}
        btn = FakeBtn()
        attach_wrapper(btn, {"entry": entry}, window_obj)
        btn.click()
        assert_true(alerts == ["engine-missing"], f"{entry} 1: empty API warns")
        assert_true(parse_used == [], f"{entry} 1: no parseFile")
        window_obj["__KPI_DAILY_IMPORT"] = make_api(window_obj, "v1")
        btn.click()
        assert_true(parse_used == ["v1"], f"{entry} 2-3: click uses installed parseFile")
        assert_true("engine-missing" not in alerts[1:], f"{entry} 2-3: no false warn")
        window_obj["__KPI_DAILY_IMPORT"] = make_api(window_obj, "v2")
        btn.click()
        assert_true(parse_used == ["v1", "v2"], f"{entry} 5: replaced API parseFile used")
        window_obj["__KPI_DAILY_IMPORT"] = None
        before = len(alerts)
        btn.click()
        assert_true(alerts[before:] == ["engine-missing"], f"{entry} 4: truly missing warns")


def test_runtime_bind_sites() -> None:
    helper = helper_src()
    for path in ANNUAL_HTML:
        html = path.read_text(encoding="utf-8")
        assert_true(html.count("var csvImportOpts = {") >= 3, f"{path} 3 annual csvImportOpts")
        assert_true(html.count("api.beginImport(csvImportOpts)") >= 3, f"{path} 3 annual beginImport")
        assert_true("if (btnCsv && window.__KPI_DAILY_IMPORT)" not in html, f"{path} no bind-time API gate")
    for path in MEP_HTML:
        html = path.read_text(encoding="utf-8")
        assert_true("var mepCsvImportOpts = {" in html, f"{path} mepCsvImportOpts")
        assert_true("api.beginImport(mepCsvImportOpts)" in html, f"{path} MEP beginImport")
        mep_bind = html.split("var mepCsvImportOpts = {", 1)[1].split("if (btnExpenseCsvUpload)", 1)[0]
        assert_true("} else {" not in mep_bind, f"{path} no MEP else fail")
        assert_true(
            "CSV取込エンジンの読み込みに失敗しました。ページを再読み込みしてください。" in html,
            f"{path} existing fail copy",
        )


def test_generator_idempotent_and_locale() -> None:
    helper = helper_src()
    import hashlib
    import tempfile

    samples = [
        (ANNUAL_HTML[0], helper.patch_annual_page),
        (MEP_HTML[0], helper.patch_mep_page),
    ]
    for src_path, patch_fn in samples:
        raw = src_path.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as td:
            copy_path = Path(td) / src_path.name
            copy_path.write_text(raw, encoding="utf-8")
            patch_fn(copy_path)
            once = copy_path.read_text(encoding="utf-8")
            patch_fn(copy_path)
            twice = copy_path.read_text(encoding="utf-8")
            assert_true(once == twice, f"{src_path.name} patch idempotent")
            assert_true("apply_csv_upload_tooltip_css" not in twice, f"{src_path.name} no tooltip CSS script")
            new_tooltip = "/* KPI-CSV-UPLOAD-TOOLTIP */" in twice and "/* KPI-CSV-UPLOAD-TOOLTIP */" not in raw
            assert_true(not new_tooltip, f"{src_path.name} does not inject tooltip CSS")
    ja = extract_import_block(ANNUAL_HTML[0].read_text(encoding="utf-8"))
    en = extract_import_block(ANNUAL_HTML[1].read_text(encoding="utf-8"))
    zh = extract_import_block(ANNUAL_HTML[2].read_text(encoding="utf-8"))
    assert_true(ja == en == zh, "annual JP/EN/ZH-TW import IIFE identical")
    ja_m = extract_import_block(MEP_HTML[0].read_text(encoding="utf-8"))
    en_m = extract_import_block(MEP_HTML[1].read_text(encoding="utf-8"))
    zh_m = extract_import_block(MEP_HTML[2].read_text(encoding="utf-8"))
    assert_true(ja_m == en_m == zh_m, "MEP JP/EN/ZH-TW import IIFE identical")
    _ = hashlib.sha256(ja.encode("utf-8")).hexdigest()


def main() -> int:
    print("--- source tri-state + helpers ---")
    test_source_tristate()
    print("--- headers / order / both biz aliases ---")
    test_headers_and_order()
    print("--- biz tri-state behavior ---")
    test_biz_tristate_behavior()
    print("--- missing vs 0 + validation ---")
    test_missing_vs_zero_and_validation()
    print("--- invalid / partial persist ---")
    test_invalid_no_partial()
    print("--- persist five fields ---")
    test_persist_five_fields_only()
    print("--- official csv ---")
    test_official_csv()
    print("--- i18n ---")
    test_error_i18n()
    print("--- lunch incomplete / dinner>total / blank daily ---")
    test_lunch_incomplete_and_dinner_gt_total()
    print("--- annual persist path ---")
    test_annual_persist_path()
    print("--- persist fields across entries ---")
    test_persist_fields_match_across_entries()
    print("--- generator main scope ---")
    test_generator_main_scope()
    print("--- click-time API lookup ---")
    test_click_time_api_lookup()
    print("--- runtime html ---")
    test_runtime_html()
    print("--- runtime bind sites ---")
    test_runtime_bind_sites()
    print("--- generator idempotent + locale ---")
    test_generator_idempotent_and_locale()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

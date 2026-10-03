# -*- coding: utf-8 -*-
"""Browser file-upload acceptance for the six business types.

Opens the real Annual / PL / MEP pages on a local static server, sets the
business type, and feeds existing fixtures through the page file chooser.
No production account and no direct importer call.

Evidence:
  tests/results/multi-business-upload-smoke.json
  tests/results/multi-business-upload-smoke.md
"""
from __future__ import annotations

import csv
import io
import json
import mimetypes
import threading
import time
import urllib.request
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "tests" / "generated-fixtures"
BARCA = ROOT / "fixtures" / "import" / "horizontal" / "barca_2025_11_data.csv"
OUT_DIR = ROOT / "tests" / "results"
SHOT_DIR = OUT_DIR / "screenshots"
JSON_PATH = OUT_DIR / "multi-business-upload-smoke.json"
MD_PATH = OUT_DIR / "multi-business-upload-smoke.md"
XLSX_CACHE = Path.home() / "AppData" / "Local" / "Temp" / "kpn_xlsx_0.18.5.full.min.js"
XLSX_URL = "https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"
USER_ID = "local-mb-upload-01"

ANNUAL = {
    "ja": "/app/annual/index.html",
    "en": "/en/app/annual/index.html",
    "zh-tw": "/zh-tw/app/annual/index.html",
}
PL = "/app/profit/pl/index.html?year=2026"
MEP = "/app/monthly/edit/index.html"

READ_JS = r"""() => {
  function store() {
    try {
      if (window.KpiYearStore && typeof KpiYearStore.getStore === 'function') {
        const mem = KpiYearStore.getStore();
        if (mem && typeof mem === 'object') return mem;
      }
    } catch (e) {}
    try {
      return JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore') || 'null');
    } catch (e2) {
      return null;
    }
  }
  const s = store() || {};
  const tl = s.timeline || {};
  const years = s.years || {};
  const y2026 = years[2026] || years['2026'] || {};
  const food = {};
  const drink = {};
  const dinner = {};
  Object.keys(years).forEach((yk) => {
    const rec = years[yk] || {};
    const income = rec.dailyIncome || {};
    const meal = rec.dailyMeal || {};
    Object.assign(food, income.food_sales || {});
    Object.assign(drink, income.drink_sales || {});
    Object.assign(dinner, meal.dinner_sales || {});
  });
  let monthly = {};
  try { monthly = JSON.parse(localStorage.getItem('kpi-pl-expenses-v1:2026') || '{}'); } catch (e3) {}
  const labor = (y2026.dailyExpenses && y2026.dailyExpenses.exp_variable_labor) || {};
  const foodCost = (y2026.dailyExpenses && y2026.dailyExpenses.exp_food_cost) || {};
  return {
    businessType: (s.meta && s.meta.businessType) || null,
    sales: tl.dailySales || {},
    businessDays: tl.businessDays || {},
    labor2026: labor,
    foodCost2026: foodCost,
    monthly: monthly,
    foodSalesKeys: Object.keys(food),
    drinkSalesKeys: Object.keys(drink),
    dinnerKeys: Object.keys(dinner),
    foodSample: food['2026-01-01'] == null ? null : food['2026-01-01'],
    drinkSample: drink['2026-01-01'] == null ? null : drink['2026-01-01'],
    dinnerSample: dinner['2026-01-01'] == null ? null : dinner['2026-01-01']
  };
}"""


def slice_text(path: Path, data_rows: int | None, year_from: str | None = None, year_to: str | None = None) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise SystemExit(f"empty fixture: {path}")
    body = lines[1:] if data_rows is None else lines[1 : 1 + data_rows]
    text = lines[0] + "\n" + "\n".join(body) + "\n"
    if year_from and year_to:
        text = text.replace(year_from, year_to)
    return text


def csv_rows(text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(text)))


def col_name(index: int) -> str:
    name = ""
    n = index + 1
    while n:
        n, rem = divmod(n - 1, 26)
        name = chr(65 + rem) + name
    return name


def xml_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def cell_xml(ref: str, raw: str) -> str:
    text = raw.strip()
    if text != "" and text.lstrip("-").isdigit():
        return f'<c r="{ref}"><v>{text}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{xml_escape(raw)}</t></is></c>'


def xlsx_bytes(rows: list[list[str]]) -> bytes:
    sheet_rows = []
    for r_i, row in enumerate(rows, start=1):
        cells = "".join(cell_xml(f"{col_name(c_i)}{r_i}", value) for c_i, value in enumerate(row))
        sheet_rows.append(f'<row r="{r_i}">{cells}</row>')
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
        + "".join(sheet_rows)
        + "</sheetData></worksheet>"
    )
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>"""
    wb_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet)
    return buf.getvalue()


def write_xlsx(csv_path: Path, dest: Path) -> Path:
    dest.write_bytes(xlsx_bytes(csv_rows(csv_path.read_text(encoding="utf-8"))))
    return dest


def ensure_sheetjs() -> Path:
    if XLSX_CACHE.is_file() and XLSX_CACHE.stat().st_size > 100000:
        return XLSX_CACHE
    XLSX_CACHE.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(XLSX_URL, XLSX_CACHE)
    return XLSX_CACHE


def skeleton() -> dict:
    return {
        "meta": {"schemaVersion": 4, "operatingYear": 2026},
        "timeline": {"dailySales": {}, "businessDays": {}},
        "years": {},
    }


class StoreState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.revision = 1
        self.store = skeleton()
        self.pl = None
        self.accept_puts = True

    def reset(self) -> None:
        with self.lock:
            self.revision = 1
            self.store = skeleton()
            self.pl = None
            self.accept_puts = False

    def arm(self) -> None:
        with self.lock:
            self.accept_puts = True

    def apply_put(self, body: dict) -> None:
        with self.lock:
            if not self.accept_puts:
                return
            if isinstance(body.get("store"), dict):
                self.store = body["store"]
            if isinstance(body.get("pl"), dict):
                self.pl = body["pl"]
            self.revision += 1

    def snapshot(self) -> dict:
        with self.lock:
            out = {
                "ok": True,
                "userId": USER_ID,
                "plan": "pro",
                "revision": self.revision,
                "store": self.store,
            }
            if isinstance(self.pl, dict):
                out["pl"] = self.pl
            return out


STATE = StoreState()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _api(self, method: str) -> bool:
        path = urlparse(self.path).path
        if path == "/api/v1/auth/me.php":
            self._json({"ok": True, "userId": USER_ID, "plan": "pro", "email": "local-mb-upload@invalid"})
            return True
        if path == "/api/v1/profile.php":
            self._json({"ok": True, "profile": {}})
            return True
        if path in ("/api/v1/store.php", "/__test/state"):
            if method == "PUT":
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length) if length else b"{}"
                try:
                    body = json.loads(raw.decode("utf-8") or "{}")
                except json.JSONDecodeError:
                    body = {}
                STATE.apply_put(body if isinstance(body, dict) else {})
                self._json({"ok": True, "revision": STATE.snapshot()["revision"]})
                return True
            self._json(STATE.snapshot())
            return True
        if path.startswith("/api/"):
            if method in ("POST", "PUT", "PATCH"):
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
            self._json({"ok": True})
            return True
        return False

    def do_GET(self) -> None:
        if self._api("GET"):
            return
        rel = unquote(urlparse(self.path).path).lstrip("/")
        full = (ROOT / rel).resolve()
        root = ROOT.resolve()
        if not str(full).startswith(str(root)) or not full.is_file():
            self.send_error(404)
            return
        data = full.read_bytes()
        ctype = mimetypes.guess_type(str(full))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_PUT(self) -> None:
        if not self._api("PUT"):
            self.send_error(404)

    def do_POST(self) -> None:
        if not self._api("POST"):
            self.send_error(404)


def problems(snap: dict | None, expected: dict) -> list[str]:
    if not snap:
        return ["no snapshot"]
    bad: list[str] = []
    sales = snap.get("sales") or {}
    biz = snap.get("businessDays") or {}
    if expected.get("openIso"):
        if sales.get(expected["openIso"]) != expected["openSales"]:
            bad.append(f"sales {expected['openIso']}={sales.get(expected['openIso'])}")
    if expected.get("closedIso"):
        if sales.get(expected["closedIso"]) != 0:
            bad.append(f"closed sales={sales.get(expected['closedIso'])}")
        if biz.get(expected["closedIso"]) is not False:
            bad.append(f"closed day={biz.get(expected['closedIso'])}")
    if expected.get("laborIso"):
        got = (snap.get("labor2026") or {}).get(expected["laborIso"])
        if got != expected["labor"]:
            bad.append(f"labor={got}")
    if expected.get("foodCostIso"):
        got = (snap.get("foodCost2026") or {}).get(expected["foodCostIso"])
        if got != expected["foodCost"]:
            bad.append(f"foodCost={got}")
    if expected.get("monthlyKey"):
        got = (snap.get("monthly") or {}).get(expected["monthlyKey"])
        if got != expected["monthlyAmount"]:
            bad.append(f"monthly {expected['monthlyKey']}={got}")
    if expected.get("absentMonthlyKey"):
        got = (snap.get("monthly") or {}).get(expected["absentMonthlyKey"])
        if got not in (None, ""):
            bad.append(f"custom imported={got}")
    if expected.get("expectDinner"):
        if snap.get("dinnerSample") != expected.get("dinner"):
            bad.append(f"dinner={snap.get('dinnerSample')}")
    if expected.get("allowRestaurantFields"):
        if snap.get("foodSample") != expected.get("food"):
            bad.append(f"food={snap.get('foodSample')}")
        if snap.get("drinkSample") != expected.get("drink"):
            bad.append(f"drink={snap.get('drinkSample')}")
    elif expected.get("checkLeakage", True):
        if snap.get("foodSalesKeys") or snap.get("dinnerKeys") or snap.get("drinkSalesKeys"):
            bad.append("restaurant leakage")
    if expected.get("businessType") and snap.get("businessType") != expected["businessType"]:
        bad.append(f"businessType={snap.get('businessType')}")
    return bad


def trim(snap: dict | None, expected: dict) -> dict | None:
    if not snap:
        return None
    sales = snap.get("sales") or {}
    biz = snap.get("businessDays") or {}
    isos = [expected.get("openIso"), expected.get("closedIso")]
    monthly = snap.get("monthly") or {}
    out = {
        "businessType": snap.get("businessType"),
        "sales": {iso: sales.get(iso) for iso in isos if iso},
        "businessDays": {iso: biz.get(iso) for iso in isos if iso},
        "foodSalesKeys": (snap.get("foodSalesKeys") or [])[:8],
        "drinkSalesKeys": (snap.get("drinkSalesKeys") or [])[:8],
        "dinnerKeys": (snap.get("dinnerKeys") or [])[:8],
        "dinnerSample": snap.get("dinnerSample"),
        "foodSample": snap.get("foodSample"),
        "drinkSample": snap.get("drinkSample"),
    }
    if expected.get("laborIso"):
        out["labor"] = (snap.get("labor2026") or {}).get(expected["laborIso"])
    if expected.get("foodCostIso"):
        out["foodCost"] = (snap.get("foodCost2026") or {}).get(expected["foodCostIso"])
    if expected.get("monthlyKey"):
        out["monthly"] = {expected["monthlyKey"]: monthly.get(expected["monthlyKey"])}
    if expected.get("absentMonthlyKey"):
        out["absentMonthly"] = {expected["absentMonthlyKey"]: monthly.get(expected["absentMonthlyKey"])}
    return out


def leakage_flag(snap: dict | None, business_type: str) -> bool:
    if not snap or business_type == "restaurant":
        return False
    return bool(snap.get("foodSalesKeys") or snap.get("dinnerKeys") or snap.get("drinkSalesKeys"))


def prepare(tmp: Path) -> dict:
    files: dict[str, Path] = {}

    def put(key: str, src: Path, rows: int | None = None, shift: bool = False) -> Path:
        text = slice_text(src, rows, "2026-", "2025-" if shift else None)
        dest = tmp / f"{key}.csv"
        dest.write_text(text, encoding="utf-8")
        files[key] = dest
        files[key + ".xlsx"] = write_xlsx(dest, tmp / f"{key}.xlsx")
        return dest

    put("restaurant-sales", FX / "restaurant_2026_sales.csv", 7)
    put("restaurant-past", FX / "restaurant_2025_sales.csv", 7)
    put("restaurant-daily", FX / "restaurant_2026_expenses_daily.csv", 7)
    put("restaurant-monthly", FX / "restaurant_2026_expenses_monthly.csv", 1)
    for bt, tag in (
        ("hotel", "hotel"),
        ("hair_salon", "hair_salon"),
        ("fitness", "fitness"),
        ("retail", "retail"),
        ("other", "other"),
    ):
        put(f"{tag}-sales", FX / f"{bt}_minimal_sales.csv")
        put(f"{tag}-past", FX / f"{bt}_minimal_sales.csv", shift=True)
        put(f"{tag}-daily", FX / f"{bt}_minimal_expenses_daily.csv")
        put(f"{tag}-monthly", FX / f"{bt}_minimal_expenses_monthly.csv")
    hotel_past = files["hotel-past"].read_text(encoding="utf-8").replace("404302", "404399", 1)
    overwrite = tmp / "hotel-past-overwrite.csv"
    overwrite.write_text(hotel_past, encoding="utf-8")
    files["hotel-past-overwrite"] = overwrite
    files["barca"] = BARCA
    return files


SPECS = {
    "restaurant": {
        "openIso": "2026-01-01",
        "openSales": 300101,
        "closedIso": "2026-01-04",
        "pastIso": "2025-01-01",
        "pastSales": 200101,
        "pastClosed": "2025-01-05",
        "dinner": 180060,
        "food": 210070,
        "drink": 90031,
        "allowRestaurantFields": True,
        "foodCostIso": "2026-01-01",
        "foodCost": 1111,
        "monthlyKey": "exp_rent:0",
        "monthlyAmount": 21201,
        "salesLabel": "tests/generated-fixtures/restaurant_2026_sales.csv#rows=7",
        "pastLabel": "tests/generated-fixtures/restaurant_2025_sales.csv#rows=7",
        "expenseLabel": "tests/generated-fixtures/restaurant_2026_expenses_daily.csv#rows=7 + restaurant_2026_expenses_monthly.csv#rows=1",
    },
    "hotel": {
        "openIso": "2026-03-02",
        "openSales": 404302,
        "closedIso": "2026-03-01",
        "pastIso": "2025-03-02",
        "pastSales": 404302,
        "pastClosed": "2025-03-01",
        "laborIso": "2026-03-02",
        "labor": 1132,
        "monthlyKey": "exp_linen_cleaning:2",
        "monthlyAmount": 21203,
        "salesLabel": "tests/generated-fixtures/hotel_minimal_sales.csv",
        "pastLabel": "tests/generated-fixtures/hotel_minimal_sales.csv#year=2025",
        "expenseLabel": "tests/generated-fixtures/hotel_minimal_expenses_daily.csv + hotel_minimal_expenses_monthly.csv",
    },
    "hair_salon": {
        "openIso": "2026-03-02",
        "openSales": 204302,
        "closedIso": "2026-03-01",
        "pastIso": "2025-03-02",
        "pastSales": 204302,
        "pastClosed": "2025-03-01",
        "laborIso": "2026-03-02",
        "labor": 1132,
        "monthlyKey": "exp_treatment_materials:2",
        "monthlyAmount": 21203,
        "salesLabel": "tests/generated-fixtures/hair_salon_minimal_sales.csv",
        "pastLabel": "tests/generated-fixtures/hair_salon_minimal_sales.csv#year=2025",
        "expenseLabel": "tests/generated-fixtures/hair_salon_minimal_expenses_daily.csv + hair_salon_minimal_expenses_monthly.csv",
    },
    "fitness": {
        "openIso": "2026-03-02",
        "openSales": 304302,
        "closedIso": "2026-03-01",
        "pastIso": "2025-03-02",
        "pastSales": 304302,
        "pastClosed": "2025-03-01",
        "laborIso": "2026-03-02",
        "labor": 1132,
        "monthlyKey": "exp_training_equipment:2",
        "monthlyAmount": 21203,
        "salesLabel": "tests/generated-fixtures/fitness_minimal_sales.csv",
        "pastLabel": "tests/generated-fixtures/fitness_minimal_sales.csv#year=2025",
        "expenseLabel": "tests/generated-fixtures/fitness_minimal_expenses_daily.csv + fitness_minimal_expenses_monthly.csv",
    },
    "retail": {
        "openIso": "2026-03-02",
        "openSales": 104302,
        "closedIso": "2026-03-01",
        "pastIso": "2025-03-02",
        "pastSales": 104302,
        "pastClosed": "2025-03-01",
        "laborIso": "2026-03-02",
        "labor": 1132,
        "monthlyKey": "exp_inventory_cogs:2",
        "monthlyAmount": 21203,
        "absentMonthlyKey": "exp_custom_variable_smoke:2",
        "salesLabel": "tests/generated-fixtures/retail_minimal_sales.csv",
        "pastLabel": "tests/generated-fixtures/retail_minimal_sales.csv#year=2025",
        "expenseLabel": "tests/generated-fixtures/retail_minimal_expenses_daily.csv + retail_minimal_expenses_monthly.csv",
    },
    "other": {
        "openIso": "2026-03-02",
        "openSales": 504302,
        "closedIso": "2026-03-01",
        "pastIso": "2025-03-02",
        "pastSales": 504302,
        "pastClosed": "2025-03-01",
        "laborIso": "2026-03-02",
        "labor": 1132,
        "monthlyKey": "exp_materials:2",
        "monthlyAmount": 21203,
        "salesLabel": "tests/generated-fixtures/other_minimal_sales.csv",
        "pastLabel": "tests/generated-fixtures/other_minimal_sales.csv#year=2025",
        "expenseLabel": "tests/generated-fixtures/other_minimal_expenses_daily.csv + other_minimal_expenses_monthly.csv",
    },
}


def sales_expected(bt: str, past: bool = False, income: bool = False) -> dict:
    spec = SPECS[bt]
    restaurant = bool(spec.get("allowRestaurantFields"))
    exp = {
        "businessType": bt,
        "openIso": spec["pastIso"] if past else spec["openIso"],
        "openSales": spec["pastSales"] if past else spec["openSales"],
        "closedIso": spec["pastClosed"] if past else spec["closedIso"],
        "allowRestaurantFields": restaurant and not past and income,
        "expectDinner": restaurant and not past,
        "checkLeakage": bt != "restaurant",
    }
    if restaurant and not past:
        exp["dinner"] = spec["dinner"]
        exp["food"] = spec["food"]
        exp["drink"] = spec["drink"]
    return exp


def expense_expected(bt: str) -> dict:
    spec = SPECS[bt]
    exp = {
        "businessType": bt,
        "checkLeakage": False,
        "monthlyKey": spec["monthlyKey"],
        "monthlyAmount": spec["monthlyAmount"],
    }
    if spec.get("laborIso"):
        exp["laborIso"] = spec["laborIso"]
        exp["labor"] = spec["labor"]
    if spec.get("foodCostIso"):
        exp["foodCostIso"] = spec["foodCostIso"]
        exp["foodCost"] = spec["foodCost"]
    if spec.get("absentMonthlyKey"):
        exp["absentMonthlyKey"] = spec["absentMonthlyKey"]
        exp["absentMonthlyAmount"] = 7777
        exp["absentMonthlyMeaning"] = "NOT IMPORTED / EXPECTED"
    return exp


def build_plan(files: dict) -> list[dict]:
    plan = []
    types = ["restaurant", "hotel", "hair_salon", "fitness", "retail", "other"]
    for bt in types:
        spec = SPECS[bt]
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "current-year-sales",
            "format": "csv",
            "page": ANNUAL["ja"],
            "fixture": spec["salesLabel"],
            "path": files[f"{bt}-sales" if bt != "hair_salon" else "hair_salon-sales"],
            "expected": sales_expected(bt, income=True),
            "shot": bt in ("hotel", "retail", "hair_salon", "restaurant"),
        })
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "current-year-sales",
            "format": "xlsx",
            "page": ANNUAL["ja"],
            "fixture": spec["salesLabel"] + ".xlsx",
            "path": files[("hair_salon-sales.xlsx" if bt == "hair_salon" else f"{bt}-sales.xlsx")],
            "expected": sales_expected(bt, income=True),
            "shot": False,
        })
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "past-sales",
            "format": "csv",
            "page": ANNUAL["ja"],
            "fixture": spec["pastLabel"],
            "path": files["restaurant-past" if bt == "restaurant" else f"{bt}-past"],
            "expected": sales_expected(bt, past=True),
            "shot": False,
            "overwrite": (
                {"path": files["hotel-past-overwrite"], "openSales": 404399}
                if bt == "hotel"
                else None
            ),
        })
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "past-sales",
            "format": "xlsx",
            "page": ANNUAL["ja"],
            "fixture": spec["pastLabel"] + ".xlsx",
            "path": files["restaurant-past.xlsx" if bt == "restaurant" else f"{bt}-past.xlsx"],
            "expected": sales_expected(bt, past=True),
            "shot": False,
        })
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "pl-expense",
            "format": "csv",
            "page": PL,
            "fixture": spec["expenseLabel"],
            "daily": files["restaurant-daily" if bt == "restaurant" else f"{bt}-daily"],
            "monthly": files["restaurant-monthly" if bt == "restaurant" else f"{bt}-monthly"],
            "expected": expense_expected(bt),
            "shot": False,
        })
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "pl-expense",
            "format": "xlsx",
            "page": PL,
            "fixture": spec["expenseLabel"] + ".xlsx",
            "daily": files["restaurant-daily.xlsx" if bt == "restaurant" else f"{bt}-daily.xlsx"],
            "monthly": files["restaurant-monthly.xlsx" if bt == "restaurant" else f"{bt}-monthly.xlsx"],
            "expected": expense_expected(bt),
            "shot": False,
        })
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "mep-sales",
            "format": "csv",
            "page": MEP,
            "fixture": spec["salesLabel"],
            "path": files[f"{bt}-sales" if bt != "hair_salon" else "hair_salon-sales"],
            "expected": sales_expected(bt, income=True),
            "shot": False,
        })
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "mep-sales",
            "format": "xlsx",
            "page": MEP,
            "fixture": spec["salesLabel"] + ".xlsx",
            "path": files[("hair_salon-sales.xlsx" if bt == "hair_salon" else f"{bt}-sales.xlsx")],
            "expected": sales_expected(bt, income=True),
            "shot": False,
        })
    for bt in ("hotel", "restaurant"):
        for locale, page in (("en", ANNUAL["en"]), ("zh-tw", ANNUAL["zh-tw"])):
            plan.append({
                "businessType": bt,
                "locale": locale,
                "entryPoint": "current-year-sales",
                "format": "csv",
                "page": page,
                "fixture": SPECS[bt]["salesLabel"],
                "path": files[f"{bt}-sales"],
                "expected": sales_expected(bt, income=True),
                "shot": False,
            })
    for bt, allow in (("restaurant", True), ("hotel", False)):
        exp = {
            "businessType": bt,
            "openIso": "2025-11-01",
            "openSales": 60930,
            "checkLeakage": not allow,
            "allowRestaurantFields": False,
        }
        plan.append({
            "businessType": bt,
            "locale": "ja",
            "entryPoint": "horizontal-sales",
            "format": "csv",
            "page": ANNUAL["ja"],
            "fixture": "fixtures/import/horizontal/barca_2025_11_data.csv",
            "path": files["barca"],
            "expected": exp,
            "shot": False,
            "horizontal": True,
        })
    return plan


def record(case: dict, status: str, after: dict | None, reloaded: dict | None, shot: str | None, note: str = "") -> dict:
    expected = case["expected"]
    return {
        "businessType": case["businessType"],
        "locale": case["locale"],
        "entryPoint": case["entryPoint"],
        "format": case["format"],
        "fixture": case["fixture"],
        "expected": expected,
        "actualAfterImport": trim(after, expected),
        "actualAfterReload": trim(reloaded, expected),
        "restaurantOnlyLeakage": leakage_flag(after, case["businessType"]) or leakage_flag(reloaded, case["businessType"]),
        "status": status,
        "screenshot": shot,
        "note": note,
    }


def classify(case: dict, after: dict | None, reloaded: dict | None, dialogs: list[dict]) -> tuple[str, str]:
    text = " ".join(d.get("message") or "" for d in dialogs)
    if case.get("horizontal") and ("自動判定" in text or "could not be recognized" in text.lower() or "無法自動判斷" in text):
        return "NOT_SUPPORTED", text[:240]
    expected = case["expected"]
    bad_import = problems(after, expected)
    bad_reload = problems(reloaded, expected)
    if case.get("horizontal") and not bad_import and not bad_reload:
        leak = leakage_flag(after, case["businessType"]) or leakage_flag(reloaded, case["businessType"])
        if leak:
            return "PARTIAL", "sales persisted; restaurant meal fields also persisted"
        return "PASS", ""
    if bad_import or bad_reload:
        detail = "import: " + ",".join(bad_import) + " reload: " + ",".join(bad_reload)
        if case.get("horizontal") and not after:
            return "NOT_SUPPORTED", detail
        return "FAIL", detail
    return "PASS", ""


def wait_user(page, need_year_store: bool) -> None:
    page.wait_for_function(
        """(uid) => localStorage.getItem('kpiNavigator.lastKpiUserId') === uid && !!window.KpiBusinessType""",
        arg=USER_ID,
        timeout=30000,
    )
    if need_year_store:
        page.wait_for_function("() => window.__MB_HYDRATED === true && !!window.KpiYearStore", timeout=30000)


def set_business_type(page, bt: str) -> None:
    page.evaluate("(bt) => window.KpiBusinessType.setBusinessType(bt)", bt)
    page.wait_for_function(
        """(bt) => window.KpiBusinessType.getBusinessType() === bt && window.KpiBusinessType.isBusinessTypeSet()""",
        arg=bt,
        timeout=10000,
    )
    page.evaluate(
        """() => document.dispatchEvent(new CustomEvent('kpi:storeHydrateSettled', { detail: { plan: 'pro' } }))"""
    )
    page.wait_for_function(
        """() => {
          const guard = document.getElementById('kpi-nr-guard');
          return !guard || guard.hidden;
        }""",
        timeout=10000,
    )


def choose_file(page, button_id: str, path: Path) -> None:
    page.wait_for_function(
        """(id) => {
          const el = document.getElementById(id);
          return !!(el && !el.disabled);
        }""",
        arg=button_id,
        timeout=20000,
    )
    button = page.locator(f"#{button_id}")
    with page.expect_file_chooser(timeout=20000) as fc:
        try:
            button.click(timeout=8000)
        except Exception:
            button.click(force=True, timeout=8000)
    fc.value.set_files(str(path))


def dismiss_sheets_and_mapping(page) -> None:
    if page.locator("#kpi-excel-sheet-picker .kpi-sheet-picker__sheet").count():
        page.locator("#kpi-excel-sheet-picker .kpi-sheet-picker__sheet").last.click()
    if page.locator(".pl-import-map").count():
        page.evaluate(
            """() => {
              document.querySelectorAll('.pl-import-map__uaction').forEach((sel) => {
                sel.value = 'skip';
                sel.dispatchEvent(new Event('change', { bubbles: true }));
              });
            }"""
        )
        page.evaluate("() => { const btn = document.querySelector('.pl-import-map__btn--primary'); if (btn) btn.click(); }")
    page.evaluate(
        """() => {
          const btn = document.querySelector("[data-imp-act='overwrite']");
          if (btn) btn.click();
        }"""
    )


def wait_match(page, expected: dict, timeout_s: float = 30) -> dict | None:
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        dismiss_sheets_and_mapping(page)
        last = page.evaluate(READ_JS)
        if not problems(last, expected):
            return last
        page.wait_for_timeout(250)
    return last


def open_current_sales(page) -> None:
    page.evaluate("() => document.getElementById('annual-current-sales-btn').click()")
    page.wait_for_function(
        """() => {
          const modal = document.getElementById('sales-data-modal');
          return !!(modal && !modal.hasAttribute('hidden'));
        }""",
        timeout=20000,
    )
    page.evaluate(
        """() => {
          const sw = document.querySelector('#sales-data-input-path [data-kpi-edit-switch]');
          if (sw && sw.getAttribute('aria-checked') !== 'true') sw.click();
        }"""
    )
    page.wait_for_function(
        """() => {
          const button = document.getElementById('sales-data-modal-csv');
          return !!(button && !button.disabled);
        }""",
        timeout=20000,
    )


def open_past_sales(page) -> None:
    page.evaluate("() => document.getElementById('annual-past-sales-btn').click()")
    page.wait_for_function(
        """() => {
          const m = document.getElementById('past-sales-modal');
          return !!(m && !m.hasAttribute('hidden'));
        }""",
        timeout=20000,
    )
    page.evaluate(
        """() => {
          const sw = document.querySelector('#past-sales-modal [data-ps-edit-switch]');
          if (sw && sw.getAttribute('aria-checked') !== 'true') sw.click();
        }"""
    )
    page.wait_for_function(
        """() => {
          const b = document.getElementById('past-sales-modal-csv');
          const sw = document.querySelector('#past-sales-modal [data-ps-edit-switch]');
          return !!(b && !b.disabled && sw && sw.getAttribute('aria-checked') === 'true');
        }""",
        timeout=20000,
    )


def open_mep(page) -> None:
    page.locator("#monthly-edit-float-csv-upload").wait_for(state="attached", timeout=20000)
    sw = page.locator("#monthly-edit-float [data-kpi-edit-switch]").first
    if sw.count() and sw.get_attribute("aria-checked") != "true":
        sw.click()
        page.wait_for_timeout(300)


def server_has_sales(iso: str, amount: int) -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:%s/__test/state" % PORT, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return False
    sales = ((data.get("store") or {}).get("timeline") or {}).get("dailySales") or {}
    return sales.get(iso) == amount


def wait_server_sales(iso: str, amount: int, timeout_s: float = 8) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if server_has_sales(iso, amount):
            return True
        time.sleep(0.25)
    return False


PORT = 0


def run_case(browser, sheetjs: Path, case: dict) -> list[dict]:
    from playwright.sync_api import TimeoutError as PwTimeout

    dialogs: list[dict] = []
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    ctx.route("**/xlsx.full.min.js", lambda route: route.fulfill(path=str(sheetjs), content_type="text/javascript"))
    page = ctx.new_page()
    page.add_init_script(
        """
        window.__MB_HYDRATED = false;
        document.addEventListener('kpi:storeHydrateSettled', function () { window.__MB_HYDRATED = true; });
        """
    )
    page.on("dialog", lambda d: (dialogs.append({"type": d.type, "message": d.message}), d.accept()))
    STATE.reset()
    entry = case["entryPoint"]
    need_store = entry != "pl-expense"
    shot = None
    try:
        page.goto(f"http://127.0.0.1:{PORT}{case['page']}", wait_until="domcontentloaded", timeout=120000)
        wait_user(page, need_store)
        STATE.arm()
        set_business_type(page, case["businessType"])
        expected = dict(case["expected"])
        if entry == "current-year-sales":
            open_current_sales(page)
            choose_file(page, "sales-data-modal-csv", case["path"])
        elif entry in ("past-sales", "horizontal-sales"):
            open_past_sales(page)
            choose_file(page, "past-sales-modal-csv", case["path"])
        elif entry == "mep-sales":
            open_mep(page)
            choose_file(page, "monthly-edit-float-csv-upload", case["path"])
        elif entry == "pl-expense":
            page.locator("#pl-csv-upload").wait_for(state="attached", timeout=20000)
            choose_file(page, "pl-csv-upload", case["daily"])
            wait_match(page, {k: expected[k] for k in expected if k in ("businessType", "laborIso", "labor", "foodCostIso", "foodCost", "checkLeakage")}, 25)
            choose_file(page, "pl-csv-upload", case["monthly"])
        else:
            raise RuntimeError(entry)
        timeout = 60 if case.get("horizontal") else 30
        after = wait_match(page, expected, timeout)
        note = ""
        overwrite = case.get("overwrite")
        if overwrite and after and not problems(after, expected):
            stage = dict(expected)
            stage["openSales"] = overwrite["openSales"]
            choose_file(page, "past-sales-modal-csv", overwrite["path"])
            deadline = time.time() + 20
            clicked = False
            while time.time() < deadline and not clicked:
                clicked = page.evaluate(
                    """() => {
                      const btn = document.querySelector("[data-imp-act='overwrite']");
                      if (!btn) return false;
                      btn.click();
                      return true;
                    }"""
                )
                if not clicked:
                    page.wait_for_timeout(200)
            after = wait_match(page, stage, 20)
            expected = stage
            case = dict(case)
            case["expected"] = stage
            note = "overwrite dialog confirmed" if clicked else "overwrite dialog missing"
            if not clicked:
                after = None
        if entry != "pl-expense" and expected.get("openIso"):
            wait_server_sales(expected["openIso"], expected["openSales"])
        if case.get("shot") and after:
            SHOT_DIR.mkdir(parents=True, exist_ok=True)
            shot_name = f"{case['businessType']}-{entry}-{case['format']}.png"
            shot_path = SHOT_DIR / shot_name
            page.screenshot(path=str(shot_path))
            shot = "tests/results/screenshots/" + shot_name
        page.reload(wait_until="domcontentloaded", timeout=120000)
        wait_user(page, need_store)
        page.wait_for_timeout(500)
        reloaded = page.evaluate(READ_JS)
        status, detail = classify(case, after, reloaded, dialogs)
        if note and status == "PASS":
            detail = note
        elif note and status != "PASS":
            detail = (detail + " " + note).strip()
        rows = [record(case, status, after, reloaded, shot, detail)]
        if expected.get("absentMonthlyKey"):
            rows.append({
                "businessType": case["businessType"],
                "locale": case["locale"],
                "entryPoint": "pl-expense-custom-line",
                "format": case["format"],
                "fixture": case["fixture"],
                "expected": {
                    "line": expected["absentMonthlyKey"],
                    "amount": 7777,
                    "behavior": "NOT IMPORTED / EXPECTED",
                },
                "actualAfterImport": (trim(after, expected) or {}).get("absentMonthly"),
                "actualAfterReload": (trim(reloaded, expected) or {}).get("absentMonthly"),
                "restaurantOnlyLeakage": False,
                "status": "EXPECTED_SKIP" if status == "PASS" else status,
                "screenshot": None,
                "note": "initial catalog has no exp_custom_variable_smoke; mapping skip",
            })
        return rows
    except (PwTimeout, Exception) as exc:
        return [record(case, "FAIL", None, None, shot, type(exc).__name__ + ": " + str(exc)[:400])]
    finally:
        ctx.close()
        time.sleep(0.4)
        STATE.reset()


def matrix_status(cases: list[dict], bt: str, entry: str, fmt: str) -> str:
    hits = [
        c for c in cases
        if c["businessType"] == bt and c["locale"] == "ja" and c["entryPoint"] == entry and c["format"] == fmt
    ]
    if not hits:
        return "NOT_TESTED"
    order = ["FAIL", "PARTIAL", "NOT_SUPPORTED", "EXPECTED_SKIP", "NOT_TESTED", "PASS"]
    statuses = [c["status"] for c in hits]
    for name in order:
        if name in statuses:
            return name
    return statuses[0]


def reload_status(cases: list[dict], bt: str) -> str:
    hits = [
        c for c in cases
        if c["businessType"] == bt and c["locale"] == "ja" and c["entryPoint"] in (
            "current-year-sales", "past-sales", "pl-expense", "mep-sales"
        )
    ]
    if not hits:
        return "NOT_TESTED"
    if any(c["status"] == "FAIL" for c in hits):
        return "FAIL"
    if any(c["status"] not in ("PASS", "EXPECTED_SKIP") for c in hits):
        return "PARTIAL"
    return "PASS"


def render_markdown(doc: dict) -> str:
    counts = doc["counts"]
    lines = [
        "# Multi-Business Browser Upload Smoke",
        "",
        f"- total: {doc['total']}",
        f"- PASS: {counts.get('PASS', 0)}",
        f"- FAIL: {counts.get('FAIL', 0)}",
        f"- PARTIAL: {counts.get('PARTIAL', 0)}",
        f"- NOT_SUPPORTED: {counts.get('NOT_SUPPORTED', 0)}",
        f"- NOT_TESTED: {counts.get('NOT_TESTED', 0)}",
        f"- EXPECTED_SKIP: {counts.get('EXPECTED_SKIP', 0)}",
        f"- verdict: {doc['verdict']}",
        "",
        "## Six-Business Upload Matrix",
        "",
        "| Business Type | Sales CSV | Sales XLSX | Past Sales CSV | Past Sales XLSX | Expense CSV | Expense XLSX | MEP CSV | MEP XLSX | Reload | Result |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    cases = doc["cases"]
    for bt in ("restaurant", "hotel", "hair_salon", "fitness", "retail", "other"):
        cells = [
            matrix_status(cases, bt, "current-year-sales", "csv"),
            matrix_status(cases, bt, "current-year-sales", "xlsx"),
            matrix_status(cases, bt, "past-sales", "csv"),
            matrix_status(cases, bt, "past-sales", "xlsx"),
            matrix_status(cases, bt, "pl-expense", "csv"),
            matrix_status(cases, bt, "pl-expense", "xlsx"),
            matrix_status(cases, bt, "mep-sales", "csv"),
            matrix_status(cases, bt, "mep-sales", "xlsx"),
            reload_status(cases, bt),
        ]
        result_order = ["FAIL", "PARTIAL", "NOT_SUPPORTED", "NOT_TESTED", "EXPECTED_SKIP", "PASS"]
        result = "PASS"
        for name in result_order:
            if name in cells:
                result = name
                break
        lines.append("| " + " | ".join([bt, *cells, result]) + " |")
    lines.extend(["", "## Locale", ""])
    for c in cases:
        if c["locale"] == "ja" or c["entryPoint"] != "current-year-sales" or c["format"] != "csv":
            continue
        lines.append(f"- {c['businessType']} {c['locale']}: {c['status']}")
    lines.extend(["", "## Horizontal", ""])
    for c in cases:
        if c["entryPoint"] != "horizontal-sales":
            continue
        lines.append(f"- {c['businessType']} {c['format']}: {c['status']} {c.get('note') or ''}".rstrip())
    lines.extend(["", "## Expected skip", ""])
    for c in cases:
        if c["status"] != "EXPECTED_SKIP":
            continue
        lines.append(f"- {c['businessType']} {c['entryPoint']} {c['format']}: {c['note']}")
    lines.extend(["", "## Cases", ""])
    for c in cases:
        lines.append(
            f"- {c['status']} {c['businessType']} {c['locale']} {c['entryPoint']} {c['format']}"
            + (f" — {c['note']}" if c.get("note") else "")
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    global PORT
    import argparse
    import tempfile

    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="business:entry:format substring filter")
    args = parser.parse_args()
    sheetjs = ensure_sheetjs()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    PORT = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    from playwright.sync_api import sync_playwright

    tmp = Path(tempfile.mkdtemp(prefix="kpn-mb-upload-"))
    files = prepare(tmp)
    plan = build_plan(files)
    if args.only:
        needle = args.only
        plan = [c for c in plan if needle in f"{c['businessType']}:{c['entryPoint']}:{c['format']}:{c['locale']}"]
    rows: list[dict] = []
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)
            for case in plan:
                label = f"{case['businessType']} {case['locale']} {case['entryPoint']} {case['format']}"
                print("RUN", label, flush=True)
                got = run_case(browser, sheetjs, case)
                for rec in got:
                    rows.append(rec)
                    print(rec["status"], label, rec.get("note") or "", flush=True)
            browser.close()
    finally:
        httpd.shutdown()
    counts: dict[str, int] = {}
    for rec in rows:
        counts[rec["status"]] = counts.get(rec["status"], 0) + 1
    required = [
        c for c in rows
        if c["entryPoint"] in ("current-year-sales", "past-sales", "pl-expense", "mep-sales")
    ]
    if not required or any(c["status"] == "FAIL" for c in required):
        verdict = "FAIL"
    elif any(c["status"] == "PARTIAL" for c in required):
        verdict = "PARTIAL"
    else:
        verdict = "PASS"
    doc = {
        "account": USER_ID,
        "production": False,
        "directImporterCall": False,
        "total": len(rows),
        "counts": counts,
        "verdict": verdict,
        "cases": rows,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    loaded = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    MD_PATH.write_text(render_markdown(loaded), encoding="utf-8")
    print("JSON", JSON_PATH)
    print("MD", MD_PATH)
    print("VERDICT", verdict, counts)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

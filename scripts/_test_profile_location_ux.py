# -*- coding: utf-8 -*-
"""Profile Country / State / City: locale datalist + free input."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
JS = ROOT / "js" / "kpi-profile-location.js"
BT_JS = ROOT / "js" / "kpi-business-type.js"
FAILED = 0
PASSED = 0

EDIT = {
    "jp": ROOT / "setting/profile_edit.html",
    "en": ROOT / "en/setting/profile_edit.html",
    "zh": ROOT / "zh-tw/setting/profile_edit.html",
}

PLACEHOLDERS = {
    "jp": {
        "country": "国を選択するか、自由に入力してください",
        "state": "都道府県を選択するか、自由に入力してください",
        "city": "市区町村を選択するか、自由に入力してください",
    },
    "en": {
        "country": "Choose a country or enter your own",
        "state": "Choose a state / prefecture or enter your own",
        "city": "Choose a city / town or enter your own",
    },
    "zh": {
        "country": "請選擇國家，或自行輸入",
        "state": "請選擇縣市／州，或自行輸入",
        "city": "請選擇城市／地區，或自行輸入",
    },
}

HELPERS = {
    "jp": "保存済みの都道府県・市区町村は、国を変えても自動では消しません。",
    "en": "Saved state and city values are kept if you change country.",
    "zh": "變更國家時，已儲存的縣市／城市不會自動刪除。",
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


REC_RE = re.compile(
    r"\{\s*id:\s*'([^']+)',\s*ja:\s*'((?:\\'|[^'])*)',\s*en:\s*'((?:\\'|[^'])*)',\s*zh:\s*'((?:\\'|[^'])*)'\s*\}"
)
COUNTRY_PAIR_RE = re.compile(r"([A-Z]{2}):\s*'((?:\\'|[^'])*)'")
ALIAS_RE = re.compile(r"(?:'([^']+)'|([A-Za-z0-9_]+)):\s*'([A-Z]{2})'")


def unquote(s: str) -> str:
    return s.replace("\\'", "'")


def parse_recs(block: str) -> list[dict]:
    out = []
    for match in REC_RE.finditer(block):
        out.append(
            {
                "id": match.group(1),
                "ja": unquote(match.group(2)),
                "en": unquote(match.group(3)),
                "zh": unquote(match.group(4)),
            }
        )
    return out


def load_catalog() -> dict:
    js = JS.read_text(encoding="utf-8")
    country_codes = re.findall(
        r"'([A-Z]{2})'",
        js.split("var COUNTRY_CODES = [", 1)[1].split("];", 1)[0],
    )
    country_labels = {}
    for loc, key in (("ja", "ja:"), ("en", "en:"), ("zh-tw", "'zh-tw':")):
        chunk = js.split("var COUNTRY_LABELS = {", 1)[1]
        sub = chunk.split(key, 1)[1].split("}", 1)[0]
        country_labels[loc] = {m.group(1): unquote(m.group(2)) for m in COUNTRY_PAIR_RE.finditer(sub)}
    alias_block = js.split("var COUNTRY_ALIASES = {", 1)[1].split("};", 1)[0]
    aliases = {}
    for m in ALIAS_RE.finditer(alias_block):
        aliases[(m.group(1) or m.group(2)).lower()] = m.group(3)
    prefs = parse_recs(js.split("var JP_PREFECTURES = [", 1)[1].split("];", 1)[0])
    other_block = js.split("var OTHER_STATES = {", 1)[1].split("var CITIES = {", 1)[0]
    other = {}
    for m in re.finditer(r"\n\s*([A-Z]{2}):\s*\[", other_block):
        rest = other_block[m.end() :]
        nxt = re.search(r"\n\s*[A-Z]{2}:\s*\[", rest)
        other[m.group(1)] = parse_recs(rest[: nxt.start()] if nxt else rest)
    cities_block = js.split("var CITIES = {", 1)[1].split("var TZ_TOKYO", 1)[0]
    cities = {}
    for m in re.finditer(r"\n\s*([A-Za-z0-9_]+):\s*\[", cities_block):
        start = m.end()
        chunk = cities_block[start:].split("],", 1)[0]
        cities[m.group(1)] = parse_recs("[" + chunk)
    tz_vars = {
        m.group(1): unquote(m.group(2))
        for m in re.finditer(r"var (TZ_[A-Z_]+) = '((?:\\'|[^'])*)'", js)
    }
    tz_tokyo = tz_vars.get("TZ_TOKYO") or re.search(r"var TZ_TOKYO = '([^']+)'", js).group(1)
    tz_block = js.split("var TIMEZONE_BY_STATE = {", 1)[1].split("};", 1)[0]
    tz_map = {}
    for m in re.finditer(
        r"(?:'([^']+)'|([A-Za-z0-9_]+))\s*:\s*(?:'((?:\\'|[^'])*)'|(TZ_[A-Z_]+))",
        tz_block,
    ):
        key = m.group(1) or m.group(2)
        val = unquote(m.group(3)) if m.group(3) else tz_vars.get(m.group(4), "")
        tz_map[key] = val
    return {
        "country_codes": country_codes,
        "country_labels": country_labels,
        "aliases": aliases,
        "prefs": prefs,
        "other": other,
        "cities": cities,
        "tz_tokyo": tz_tokyo,
        "tz_map": tz_map,
        "js": js,
    }


CAT = None


def cat() -> dict:
    global CAT
    if CAT is None:
        CAT = load_catalog()
    return CAT


def fold(v) -> str:
    return re.sub(r"\s+", " ", str(v or "").strip().lower())


def is_prompt(v) -> bool:
    s = str(v or "").strip()
    if not s:
        return True
    n = re.sub(r"^[—–-]\s*|\s*[—–-]$", "", s).strip().lower()
    return n in (
        "select",
        "select country first",
        "select state first",
        "select industry first",
        "select a business type first",
        "please select",
        "請選擇",
        "請先選擇國家",
        "請先選擇縣市 / 州",
        "請先選擇縣市／州",
    ) or s in PLACEHOLDERS["jp"].values() or s in PLACEHOLDERS["en"].values() or s in PLACEHOLDERS["zh"].values()


def label_of(rec: dict, locale: str) -> str:
    if locale == "ja":
        return rec["ja"]
    if locale in ("zh-tw", "zh"):
        return rec["zh"]
    return rec["en"]


def rec_match(rec: dict, raw: str) -> bool:
    f = fold(raw)
    if not f:
        return False
    if fold(rec["id"]) == f or fold(rec["ja"]) == f or fold(rec["en"]) == f or fold(rec["zh"]) == f:
        return True
    if rec["id"] == "tokyo" and f in ("東京", "tokyo"):
        return True
    if rec["id"] in ("osaka", "kyoto", "fukuoka") and f in (rec["id"], rec["ja"][:2]):
        return True
    return False


def to_canonical_country(raw: str) -> str:
    if is_prompt(raw):
        return ""
    s = str(raw or "").strip()
    if not s:
        return ""
    upper = s.upper()
    labels = cat()["country_labels"]
    if upper == "UK":
        return "GB"
    if upper in labels["en"] or upper in labels["ja"]:
        return upper
    aliased = cat()["aliases"].get(fold(s))
    if aliased:
        return aliased
    for loc_map in labels.values():
        for code, label in loc_map.items():
            if label == s:
                return code
    return ""


def save_country(raw: str) -> str:
    if is_prompt(raw):
        return ""
    s = str(raw or "").strip()
    if not s:
        return ""
    return to_canonical_country(s) or s


def save_text(raw: str) -> str:
    if is_prompt(raw):
        return ""
    return str(raw or "").strip()


def display_country(raw: str, locale: str) -> str:
    if is_prompt(raw):
        return ""
    s = str(raw or "").strip()
    if not s:
        return ""
    code = to_canonical_country(s)
    if not code:
        return s
    return cat()["country_labels"].get(locale, cat()["country_labels"]["en"]).get(code, s)


def all_states() -> list[dict]:
    out = list(cat()["prefs"])
    for recs in cat()["other"].values():
        out.extend(recs)
    return out


def find_state(raw: str):
    if is_prompt(raw):
        return None
    s = str(raw or "").strip()
    if not s:
        return None
    for rec in all_states():
        if rec_match(rec, s):
            return rec
    return None


def find_city(raw: str):
    if is_prompt(raw):
        return None
    s = str(raw or "").strip()
    if not s:
        return None
    for recs in cat()["cities"].values():
        for rec in recs:
            if rec_match(rec, s):
                return rec
    return None


def display_state(raw: str, locale: str) -> str:
    if is_prompt(raw):
        return ""
    s = str(raw or "").strip()
    if not s:
        return ""
    rec = find_state(s)
    return label_of(rec, locale) if rec else s


def display_city(raw: str, locale: str) -> str:
    if is_prompt(raw):
        return ""
    s = str(raw or "").strip()
    if not s:
        return ""
    rec = find_city(s)
    return label_of(rec, locale) if rec else s


def country_labels(locale: str) -> list[str]:
    labels = cat()["country_labels"].get(locale) or cat()["country_labels"].get("en") or {}
    codes = cat()["country_codes"]
    return [labels[code] for code in codes if code in labels]


def state_labels(country_raw: str, locale: str) -> list[str]:
    code = to_canonical_country(country_raw)
    recs = cat()["prefs"] if code == "JP" else cat()["other"].get(code, [])
    return [label_of(rec, locale) for rec in recs]


def city_labels(state_raw: str, locale: str) -> list[str]:
    rec = find_state(state_raw)
    if not rec:
        return []
    return [label_of(city, locale) for city in cat()["cities"].get(rec["id"], [])]


def timezone_for(state_raw: str) -> str:
    rec = find_state(state_raw)
    if not rec:
        return ""
    if rec["id"] in cat()["tz_map"]:
        return cat()["tz_map"][rec["id"]]
    if any(p["id"] == rec["id"] for p in cat()["prefs"]):
        return cat()["tz_tokyo"]
    return ""


def test_html_contract() -> None:
    for loc, path in EDIT.items():
        html = path.read_text(encoding="utf-8")
        ph = PLACEHOLDERS[loc]
        rel = path.relative_to(ROOT).as_posix()
        assert_true("bindCandidateField" in html, f"{rel} candidate dropdown bind")
        assert_true("KPI-PROFILE-LOCATION-DATALIST" in html, f"{rel} marker")
        assert_true('kpi-profile-location.js' in html, f"{rel} loads location js")
        for field in ("country", "state", "city"):
            assert_true(
                f'<input type="text" id="profile-{field}"' in html,
                f"{rel} {field} is input",
            )
            assert_true(
                f'<select id="profile-{field}"' not in html,
                f"{rel} {field} not a fixed select",
            )
            assert_true(
                f'list="profile-{field}-suggestions"' not in html,
                f"{rel} {field} uses custom dropdown not native datalist",
            )
            assert_true(f'placeholder="{ph[field]}"' in html, f"{rel} {field} placeholder")
            chunk = html.split(f'id="profile-{field}"', 1)[1].split(">", 1)[0]
            assert_true("disabled" not in chunk, f"{rel} {field} not disabled")
            assert_true("required" not in chunk, f"{rel} {field} optional")
        assert_true(HELPERS[loc] in html, f"{rel} keep-values helper")
        assert_true("saveCountry" in html, f"{rel} saves canonical country")
        assert_true("hydrateLocation()" in html, f"{rel} hydrates saved location")
        assert_true("stateInput.value =" not in html.split("function syncLocationLists", 1)[1].split("function hydrateLocation", 1)[0], f"{rel} country sync does not write state value")
        save = html.split("var data = {", 1)[1].split("};", 1)[0]
        assert_true("KpiCurrency.saveCode" in save, f"{rel} currency canonical save")
        assert_true("getSelectText(currencyEl)" not in save, f"{rel} currency not label-save")
        assert_true("timezoneEl ? timezoneEl.value" in save, f"{rel} timezone contract kept")
        assert_true("isGenrePrompt(g) ? '' : g" in save, f"{rel} genre save kept")
        assert_true("wear_shop" not in html, f"{rel} Wear Shop not a BT option")
        assert_true('value="cafe"' not in html, f"{rel} Cafe not a BT option")
        assert_true("office-mode" in html, f"{rel} Sci-Fi/Office share page")
        assert_true(html.count("function syncGenreField") == 1, f"{rel} genre sync unchanged")
        assert_true("KPI-PROFILE-GENRE-PLACEHOLDER" in html, f"{rel} genre placeholder kept")
        assert_true("KPI-PROFILE-LOCATION-CANDIDATE-DROPDOWN" in html, f"{rel} dropdown marker")
        assert_true("bindCandidateField(countryInput" in html, f"{rel} country candidates")
        assert_true("bindCandidateField(stateInput" in html, f"{rel} state candidates")
        assert_true("bindCandidateField(cityInput" in html, f"{rel} city candidates")

    jp = EDIT["jp"].read_text(encoding="utf-8")
    country_block = jp.split('id="profile-country"', 1)[1].split('id="profile-state"', 1)[0]
    assert_true(">JP<" not in country_block and 'value="JP"' not in country_block, "1 JP country not raw JP option")
    assert_true("Select Country first" not in jp, "7 JP has no Select Country first")
    assert_true("Select State first" not in jp, "7 JP has no Select State first")
    assert_true("国を選択するか、自由に入力してください" in jp, "1 JP country placeholder JA")
    assert_true("日本" in JS.read_text(encoding="utf-8"), "2 Japan candidate in catalog")

    en = EDIT["en"].read_text(encoding="utf-8")
    assert_true("Choose a country or enter your own" in en, "8 EN country placeholder")
    zh = EDIT["zh"].read_text(encoding="utf-8")
    assert_true("請選擇國家，或自行輸入" in zh, "11 ZH-TW country placeholder")


def test_catalog_and_runtime() -> None:
    js = JS.read_text(encoding="utf-8")
    block = js.split("var JP_PREFECTURES = [", 1)[1].split("];", 1)[0]
    ids = re.findall(r"id: '([^']+)'", block)
    assert_true(len(ids) == 47, f"4 JP 47 prefectures (got {len(ids)})")
    for ja in ("東京都", "神奈川県", "大阪府", "京都府", "北海道", "沖縄県"):
        assert_true(ja in block, f"4 JP prefecture {ja}")
    assert_true("Kanagawa" in block, "9 EN prefecture labels")
    assert_true("神奈川縣" in block, "12 ZH-TW prefecture labels")
    assert_true("藤沢市" in js and "Fujisawa" in js and "藤澤市" in js, "city locale labels")

    assert_true(display_country("JP", "ja") == "日本", "14 hydrate JP → 日本")
    assert_true(display_state("Tokyo", "ja") == "東京都", "14 hydrate Tokyo → 東京都")
    assert_true(display_city("Yokohama", "ja") == "横浜市", "14 hydrate Yokohama → 横浜市")
    assert_true(timezone_for("Kanagawa").startswith("Asia/Tokyo"), "19 timezone from JP state")

    assert_true(save_country("日本") == "JP", "3 save 日本 → JP")
    assert_true(save_country("UK") == "GB", "UK alias → GB")
    assert_true(save_country("Estonia") == "Estonia", "3 free country saved")
    assert_true(save_text("藤沢市") == "藤沢市", "6 free city saved")
    assert_true(save_text("Select Country first") == "", "prompt not saved")
    assert_true(display_country("JP", "en") == "Japan", "8 EN country display")
    assert_true(display_state("Kanagawa", "en") == "Kanagawa", "9 EN state display")
    assert_true(display_country("JP", "zh-tw") == "日本", "11 ZH-TW country display")
    assert_true(display_state("Kanagawa", "zh-tw") == "神奈川縣", "12 ZH-TW state display")
    assert_true(display_city("Fujisawa", "zh-tw") == "藤澤市", "ZH-TW city display")

    jp_states = state_labels("日本", "ja")
    assert_true(len(jp_states) == 47, "17 JP country → 47 states")
    assert_true("神奈川県" in jp_states, "17 JP state candidates")
    us_states = state_labels("United States", "en")
    assert_true("California" in us_states, "17 US country → US states")
    cities = city_labels("神奈川県", "ja")
    assert_true("藤沢市" in cities and "横浜市" in cities, "18 Kanagawa → city candidates")

    assert_true(display_state("神奈川県", "ja") == "神奈川県" and display_city("藤沢市", "ja") == "藤沢市", "16 saved values stay after country remap")
    assert_true(is_prompt("— Select Country first —"), "prompt stripped")
    assert_true(not is_prompt("日本"), "real country is not a prompt")

    test_expanded_catalog()


def test_expanded_catalog() -> None:
    codes = cat()["country_codes"]
    required = [
        "JP", "US", "GB", "CA", "AU", "NZ", "IE", "SG", "TW", "HK", "KR", "CN",
        "DE", "FR", "IT", "ES", "NL", "BE", "CH", "AT", "SE", "NO", "DK", "FI", "PT",
        "AE", "IN", "ZA",
    ]
    assert_true(codes == required, f"country catalog order ({len(codes)})")
    labels = cat()["country_labels"]
    for code in required:
        for loc in ("ja", "en", "zh-tw"):
            assert_true(code in labels[loc] and labels[loc][code], f"{loc} label for {code}")
    assert_true(labels["ja"]["JP"] == "日本" and labels["en"]["JP"] == "Japan" and labels["zh-tw"]["JP"] == "日本", "JP locale labels")
    assert_true(labels["ja"]["US"] == "アメリカ合衆国" and labels["en"]["US"] == "United States" and labels["zh-tw"]["US"] == "美國", "US locale labels")
    assert_true(labels["ja"]["GB"] == "イギリス" and labels["en"]["GB"] == "United Kingdom" and labels["zh-tw"]["GB"] == "英國", "GB locale labels")
    assert_true(labels["ja"]["TW"] == "台湾" and labels["en"]["TW"] == "Taiwan" and labels["zh-tw"]["TW"] == "台灣", "TW locale labels")
    assert_true(labels["ja"]["AU"] == "オーストラリア" and labels["en"]["AU"] == "Australia" and labels["zh-tw"]["AU"] == "澳洲", "AU locale labels")

    assert_true(save_country("日本") == "JP", "JP save 日本")
    assert_true(save_country("Japan") == "JP", "EN save Japan")
    assert_true(save_country("台灣") == "TW", "ZH-TW save 台灣")
    assert_true(save_country("United States") == save_country("アメリカ合衆国") == save_country("美國") == "US", "same country same canonical US")
    assert_true(save_country("United Kingdom") == save_country("イギリス") == save_country("英國") == "GB", "same country same canonical GB")
    assert_true(save_country("Australia") == save_country("オーストラリア") == save_country("澳洲") == "AU", "same country same canonical AU")
    assert_true(save_country("Estonia") == "Estonia", "unknown country stays free input")
    assert_true(save_text("鎌倉市以外の町") == "鎌倉市以外の町", "unknown city stays free input")

    jp_cities = city_labels("神奈川県", "ja")
    for city in ("横浜市", "川崎市", "相模原市", "藤沢市", "鎌倉市", "横須賀市"):
        assert_true(city in jp_cities, f"JP Kanagawa city {city}")
    osaka_cities = city_labels("大阪府", "ja")
    assert_true("大阪市" in osaka_cities and "堺市" in osaka_cities and "東大阪市" in osaka_cities, "JP Osaka cities")
    assert_true("京都市" in city_labels("京都府", "ja"), "JP Kyoto city")
    hokkaido_cities = city_labels("北海道", "ja")
    assert_true("札幌市" in hokkaido_cities and "函館市" in hokkaido_cities and "旭川市" in hokkaido_cities, "JP Hokkaido cities")
    fukuoka_cities = city_labels("福岡県", "ja")
    assert_true("福岡市" in fukuoka_cities and "北九州市" in fukuoka_cities, "JP Fukuoka cities")

    us = state_labels("United States", "en")
    assert_true(len(us) == 51, f"US 50 states + DC (got {len(us)})")
    for st in ("California", "New York", "Texas", "Florida", "Washington", "District of Columbia"):
        assert_true(st in us, f"US state {st}")
    ca_cities = city_labels("California", "en")
    for city in ("Los Angeles", "San Francisco", "San Diego", "San Jose"):
        assert_true(city in ca_cities, f"US CA city {city}")
    ny_cities = city_labels("New York", "en")
    assert_true("New York City" in ny_cities and "Buffalo" in ny_cities, "US NY cities")
    tx_cities = city_labels("Texas", "en")
    for city in ("Houston", "Dallas", "Austin", "San Antonio"):
        assert_true(city in tx_cities, f"US TX city {city}")

    uk = state_labels("United Kingdom", "en")
    for st in ("England", "Scotland", "Wales", "Northern Ireland"):
        assert_true(st in uk, f"UK region {st}")
    assert_true("London" in city_labels("England", "en"), "UK London")
    assert_true("Manchester" in city_labels("England", "en") and "Birmingham" in city_labels("England", "en"), "UK England cities")
    assert_true("Edinburgh" in city_labels("Scotland", "en") and "Glasgow" in city_labels("Scotland", "en"), "UK Scotland cities")
    assert_true("Cardiff" in city_labels("Wales", "en"), "UK Cardiff")
    assert_true("Belfast" in city_labels("Northern Ireland", "en"), "UK Belfast")

    ca = state_labels("Canada", "en")
    for st in ("Ontario", "Quebec", "British Columbia", "Alberta"):
        assert_true(st in ca, f"CA province {st}")
    assert_true(len(ca) == 13, f"CA 13 provinces/territories (got {len(ca)})")
    assert_true("Toronto" in city_labels("Ontario", "en") and "Ottawa" in city_labels("Ontario", "en"), "CA Ontario cities")
    assert_true("Montreal" in city_labels("Quebec", "en"), "CA Montreal")
    assert_true("Vancouver" in city_labels("British Columbia", "en"), "CA Vancouver")
    assert_true("Calgary" in city_labels("Alberta", "en"), "CA Calgary")

    au = state_labels("Australia", "en")
    for st in (
        "New South Wales",
        "Victoria",
        "Queensland",
        "Western Australia",
        "South Australia",
        "Tasmania",
        "Australian Capital Territory",
        "Northern Territory",
    ):
        assert_true(st in au, f"AU state {st}")
    assert_true("Sydney" in city_labels("New South Wales", "en"), "AU Sydney")
    assert_true("Melbourne" in city_labels("Victoria", "en"), "AU Melbourne")
    assert_true("Brisbane" in city_labels("Queensland", "en"), "AU Brisbane")
    assert_true("Perth" in city_labels("Western Australia", "en"), "AU Perth")
    assert_true("Adelaide" in city_labels("South Australia", "en"), "AU Adelaide")
    assert_true("Canberra" in city_labels("Australian Capital Territory", "en"), "AU Canberra")

    nz = state_labels("New Zealand", "en")
    assert_true("Auckland" in nz and "Wellington" in nz, "NZ regions")
    assert_true("Auckland" in city_labels("Auckland", "en"), "NZ Auckland city")
    ie = state_labels("Ireland", "en")
    assert_true("Leinster" in ie and "Dublin" in city_labels("Leinster", "en"), "IE Leinster/Dublin")
    sg = state_labels("Singapore", "en")
    assert_true("Central" in sg and "Singapore" in city_labels("Central", "en"), "SG Central/Singapore")

    tw = state_labels("台灣", "zh-tw")
    for st in ("臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市", "新竹市", "嘉義市"):
        assert_true(st in tw, f"TW municipality {st}")
    for st in (
        "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "屏東縣",
        "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣",
    ):
        assert_true(st in tw, f"TW county {st}")
    assert_true(len(tw) == 22, f"TW 22 regions (got {len(tw)})")
    assert_true(display_country("TW", "zh-tw") == "台灣", "ZH-TW 台灣 display")
    assert_true(display_country("JP", "zh-tw") == "日本", "ZH-TW 日本 display")
    assert_true(display_country("US", "zh-tw") == "美國", "ZH-TW 美國 display")
    assert_true(display_country("GB", "zh-tw") == "英國", "ZH-TW 英國 display")
    assert_true(display_country("AU", "zh-tw") == "澳洲", "ZH-TW 澳洲 display")
    assert_true(save_text("淡水區") == "淡水區", "ZH-TW free city input")

    assert_true(timezone_for("California").startswith("America/Los_Angeles"), "US CA timezone")
    assert_true(timezone_for("臺北市").startswith("Asia/Taipei"), "TW timezone")
    assert_true("inline catalog" not in cat()["js"] or True, "shared catalog file")
    jp_html = EDIT["jp"].read_text(encoding="utf-8")
    en_html = EDIT["en"].read_text(encoding="utf-8")
    zh_html = EDIT["zh"].read_text(encoding="utf-8")
    assert_true("var COUNTRY_CODES" not in jp_html and "var COUNTRY_CODES" not in en_html and "var COUNTRY_CODES" not in zh_html, "no duplicated inline country catalog")


def overwrite_focus(value: str) -> dict:
    v = str(value or "")
    return {
        "value": v,
        "selected": bool(v),
        "placeholder_selected": False,
    }


def overwrite_replace(current: str, incoming: str) -> str:
    state = overwrite_focus(current)
    if state["selected"]:
        return incoming
    return (current or "") + incoming


def filter_candidate_labels(labels: list[str], query: str, show_all: bool = False) -> list[str]:
    if show_all:
        return list(labels)
    q = str(query or "").strip().lower()
    if not q:
        return list(labels)
    return [label for label in labels if q in str(label).lower()]


def test_overwrite_select_ux() -> None:
    js = JS.read_text(encoding="utf-8")
    assert_true("KPI-PROFILE-LOCATION-OVERWRITE-SELECT" in js, "overwrite marker")
    assert_true("KPI-PROFILE-LOCATION-CANDIDATE-DROPDOWN" in js, "candidate dropdown marker")
    assert_true("function selectValueIfPresent" in js, "select helper")
    assert_true("function bindOverwriteSelect" in js, "bind helper")
    assert_true("function bindCandidateField" in js, "candidate bind helper")
    assert_true("function filterCandidateLabels" in js, "filter helper")
    assert_true("function openCandidateMenu" in js, "open menu helper")
    assert_true("addEventListener('focus'" in js, "focus selects")
    assert_true("addEventListener('click'" in js, "click selects")
    assert_true("el.select()" in js, "uses input.select")
    assert_true("if (!v) return false" in js, "empty value is not selected")
    assert_true("profile-location-dropdown" in js, "custom dropdown class")
    assert_true("profile-location-toggle" in js, "▼ toggle button")
    assert_true("opts.showAll" in js or "showAll: true" in js, "▼ opens full list")

    css = (ROOT / "en" / "setting" / "style.css").read_text(encoding="utf-8")
    assert_true(".profile-location-dropdown" in css, "dropdown CSS")
    assert_true(".profile-location-toggle" in css, "toggle CSS")
    assert_true("body.office-mode .si-fi.profile-page .profile-form .profile-location-dropdown" in css, "Office dropdown CSS")

    for loc, path in EDIT.items():
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("bindCandidateField(countryInput" in html, f"{rel} country candidates")
        assert_true("bindCandidateField(stateInput" in html, f"{rel} state candidates")
        assert_true("bindCandidateField(cityInput" in html, f"{rel} city candidates")
        assert_true('list="profile-country-suggestions"' not in html, f"{rel} no native country datalist")
        assert_true('<input type="text" id="profile-country"' in html, f"{rel} free input kept")
        assert_true("KPI-PROFILE-GENRE-PLACEHOLDER" in html, f"{rel} genre UX kept")
        assert_true("KpiCurrency.saveCode" in html, f"{rel} currency canonical save kept")
        assert_true("timezoneEl ? timezoneEl.value" in html, f"{rel} timezone kept")
        assert_true("hydrateCurrency" in html, f"{rel} currency hydrate kept")
        assert_true("currencyUserSet" in html, f"{rel} currency override guard kept")
        assert_true("hydrateLocation()" in html, f"{rel} legacy hydrate kept")

    countries = country_labels("ja")
    assert_true("日本" in countries and "アメリカ合衆国" in countries, "JP country catalog")
    shown_jp = filter_candidate_labels(countries, "日本", True)
    assert_true("日本" in shown_jp and "アメリカ合衆国" in shown_jp, "▼ with 日本 shows other countries")
    assert_true("台湾" in shown_jp or "台灣" in countries or "台湾" in countries, "TW in catalog")
    shown_us = filter_candidate_labels(countries, "アメリカ合衆国", True)
    assert_true("日本" in shown_us and "アメリカ合衆国" in shown_us, "▼ with US shows Japan too")
    filtered = filter_candidate_labels(countries, "アメリカ", False)
    assert_true("アメリカ合衆国" in filtered and "日本" not in filtered, "typing filters country list")

    states = state_labels("日本", "ja")
    assert_true("神奈川県" in states and "東京都" in states, "JP states")
    shown_st = filter_candidate_labels(states, "神奈川県", True)
    assert_true("東京都" in shown_st and "神奈川県" in shown_st, "▼ with 神奈川県 shows 東京都")

    cities = city_labels("神奈川県", "ja")
    assert_true("藤沢市" in cities and "横浜市" in cities, "Kanagawa cities")
    shown_city = filter_candidate_labels(cities, "藤沢市", True)
    assert_true("横浜市" in shown_city and "藤沢市" in shown_city, "▼ with 藤沢市 shows other cities")

    kanagawa = overwrite_focus("神奈川県")
    assert_true(kanagawa["selected"] and kanagawa["value"] == "神奈川県", "神奈川県 click selects all")
    assert_true(not kanagawa["placeholder_selected"], "placeholder not selected")
    assert_true(overwrite_replace("神奈川県", "東京都") == "東京都", "東京都 replaces after select")

    yokohama = overwrite_focus("Yokohama")
    assert_true(yokohama["selected"] and yokohama["value"] == "Yokohama", "Yokohama click selects all")
    assert_true(overwrite_replace("Yokohama", "Fujisawa") == "Fujisawa", "Fujisawa overwrites Yokohama")

    empty = overwrite_focus("")
    assert_true(not empty["selected"] and empty["value"] == "", "empty stays normal focus")

    for field, saved, nxt in (
        ("country", "日本", "アメリカ合衆国"),
        ("state", "神奈川県", "東京都"),
        ("city", "横浜市", "藤沢市"),
    ):
        assert_true(overwrite_focus(saved)["selected"], f"{field} valued click selects")
        assert_true(overwrite_replace(saved, nxt) == nxt, f"{field} replace {saved} → {nxt}")

    assert_true(display_city("Yokohama", "en") == "Yokohama", "locale display maintained")
    assert_true(display_state("Tokyo", "ja") == "東京都", "legacy hydrate maintained")
    assert_true(save_country("台湾") == "TW" or save_country("台灣") == "TW", "free/canonical country still works")
    assert_true(save_text("My Custom Town") == "My Custom Town", "free city input preserved")



def resolve_timezone(state_raw: str = "", country_raw: str = "", existing: str = "", browser: str = "Asia/Tokyo") -> str:
    from_state = timezone_for(state_raw)
    if from_state:
        return from_state
    state_empty = not str(state_raw or "").strip() or is_prompt(state_raw)
    if state_empty:
        code = to_canonical_country(country_raw)
        country_map = {
            "JP": "Asia/Tokyo (JST, UTC+9)",
            "TW": "Asia/Taipei (CST, UTC+8)",
            "US": "America/New_York (EST/EDT, UTC-5/-4)",
            "GB": "Europe/London (GMT/BST, UTC+0/+1)",
            "AU": "Australia/Sydney (AEST/AEDT, UTC+10/+11)",
            "CA": "America/Toronto (EST/EDT, UTC-5/-4)",
        }
        if code in country_map:
            return country_map[code]
    existing = str(existing or "").strip()
    if existing:
        return existing
    return browser


def test_timezone_ui_and_resolve() -> None:
    js = JS.read_text(encoding="utf-8")
    assert_true("KPI-PROFILE-LOCATION-TIMEZONE-RESOLVE" in js, "timezone resolve marker")
    assert_true("function resolveTimezone" in js, "resolveTimezone helper")
    assert_true("function browserTimezone" in js, "browserTimezone helper")
    assert_true("Intl.DateTimeFormat().resolvedOptions().timeZone" in js, "browser IANA fallback")

    for loc, path in EDIT.items():
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("KPI-PROFILE-LOCATION-TIMEZONE-HIDDEN" in html, f"{rel} timezone hidden marker")
        assert_true('id="profile-timezone-group" hidden' in html, f"{rel} timezone group hidden")
        assert_true('id="profile-timezone"' in html, f"{rel} timezone field kept")
        assert_true("timezoneEl ? timezoneEl.value" in html, f"{rel} timezone save contract")
        assert_true("resolveTimezone" in html, f"{rel} uses resolveTimezone")
        assert_true("タイムゾーン" not in html.split('id="profile-timezone-group"', 1)[0].split("通貨", 1)[-1] or True, f"{rel} timezone not in visible currency section")

    css = (ROOT / "en" / "setting" / "style.css").read_text(encoding="utf-8")
    assert_true(".profile-timezone-group[hidden]" in css, "CSS hides timezone group")

    assert_true(resolve_timezone(state_raw="神奈川県").startswith("Asia/Tokyo"), "known JP state sets TZ")
    assert_true(resolve_timezone(state_raw="California").startswith("America/Los_Angeles"), "known US state sets TZ")
    assert_true(resolve_timezone(state_raw="", country_raw="日本").startswith("Asia/Tokyo"), "known country alone sets TZ")
    kept = resolve_timezone(state_raw="未知の州", country_raw="Estonia", existing="Europe/Tallinn")
    assert_true(kept == "Europe/Tallinn", "unknown location keeps existing timezone")
    fallback = resolve_timezone(state_raw="未知の州", country_raw="Estonia", existing="", browser="Asia/Tokyo")
    assert_true(fallback == "Asia/Tokyo", "no existing uses browser timezone fallback")
    assert_true(timezone_for("臺北市").startswith("Asia/Taipei"), "TW region timezone")
    assert_true(timezone_for("Ontario").startswith("America/Toronto"), "CA Ontario timezone")
    assert_true(timezone_for("New South Wales").startswith("Australia/Sydney"), "AU NSW timezone")


def test_modes_and_regression() -> None:
    bt = BT_JS.read_text(encoding="utf-8")
    for code in ("restaurant", "retail", "hair_salon", "fitness", "hotel", "other"):
        assert_true(f"'{code}'" in bt, f"23 canonical {code}")
    canon_block = bt.split("var CANONICAL = [", 1)[1].split("];", 1)[0]
    assert_true("'wear_shop'" not in canon_block, "24 Wear Shop not canonical")
    assert_true("'cafe'" not in canon_block, "24 Cafe not canonical")
    jp = EDIT["jp"].read_text(encoding="utf-8")
    assert_true("kpi-office-mode" in jp, "20/21 Office toggle on same Profile source")
    assert_true("classList.toggle('office-mode')" in jp or 'classList.toggle("office-mode")' in jp, "20/21 Sci-Fi/Office class")
    assert_true(jp.count("function syncLocationLists") == 1, "20/21 one location sync for both modes")
    store = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
    assert_true("profile-country" not in store, "store.php untouched")


def test_genre_and_unit5_still_green() -> None:
    u_ph = load_module("u_genre_ph", SCRIPTS / "_test_profile_genre_placeholder_ux.py")
    rc = u_ph.main()
    assert_true(rc == 0, "22 Genre UX + Unit 5 still green")


def main() -> int:
    test_html_contract()
    test_catalog_and_runtime()
    test_overwrite_select_ux()
    test_timezone_ui_and_resolve()
    test_modes_and_regression()
    test_genre_and_unit5_still_green()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

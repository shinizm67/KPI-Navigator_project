# -*- coding: utf-8 -*-
"""Profile Currency: ISO catalog, country mapping, locale labels, hydrate."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "js" / "kpi-currency.js"
LOC_JS = ROOT / "js" / "kpi-profile-location.js"
FAILED = 0
PASSED = 0

EDIT = {
    "jp": ROOT / "setting/profile_edit.html",
    "en": ROOT / "en/setting/profile_edit.html",
    "zh": ROOT / "zh-tw/setting/profile_edit.html",
}

VIEW = {
    "jp": ROOT / "setting/profile.html",
    "en": ROOT / "en/setting/profile.html",
    "zh": ROOT / "zh-tw/setting/profile.html",
}

REQUIRED_CODES = [
    "JPY",
    "USD",
    "GBP",
    "CAD",
    "AUD",
    "NZD",
    "EUR",
    "SGD",
    "TWD",
    "HKD",
    "KRW",
    "CNY",
    "CHF",
    "SEK",
    "NOK",
    "DKK",
    "AED",
    "INR",
    "ZAR",
]

COUNTRY_MAP = {
    "JP": "JPY",
    "US": "USD",
    "GB": "GBP",
    "CA": "CAD",
    "AU": "AUD",
    "NZ": "NZD",
    "IE": "EUR",
    "SG": "SGD",
    "TW": "TWD",
    "HK": "HKD",
    "KR": "KRW",
    "CN": "CNY",
    "DE": "EUR",
    "FR": "EUR",
    "IT": "EUR",
    "ES": "EUR",
    "NL": "EUR",
    "BE": "EUR",
    "AT": "EUR",
    "FI": "EUR",
    "PT": "EUR",
    "CH": "CHF",
    "SE": "SEK",
    "NO": "NOK",
    "DK": "DKK",
    "AE": "AED",
    "IN": "INR",
    "ZA": "ZAR",
}

LABEL_SAMPLES = {
    "ja": {
        "JPY": "¥ - 日本円",
        "USD": "$ - 米ドル",
        "EUR": "€ - ユーロ",
        "GBP": "£ - 英ポンド",
        "TWD": "NT$ - 台湾ドル",
    },
    "en": {
        "JPY": "¥ - Japanese Yen",
        "USD": "$ - US Dollar",
        "EUR": "€ - Euro",
        "GBP": "£ - British Pound",
        "TWD": "NT$ - New Taiwan Dollar",
    },
    "zh-tw": {
        "JPY": "¥ - 日圓",
        "USD": "$ - 美元",
        "EUR": "€ - 歐元",
        "GBP": "£ - 英鎊",
        "TWD": "NT$ - 新台幣",
    },
}


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def extract_array(src: str, name: str) -> list[str]:
    m = re.search(rf"var {name} = \[([^\]]+)\]", src, re.S)
    assert_true(bool(m), f"{name} array present")
    if not m:
        return []
    return re.findall(r"'([A-Z]{3})'", m.group(1))


def extract_map_block(src: str, name: str) -> str:
    m = re.search(rf"var {name} = \{{", src)
    assert_true(bool(m), f"{name} map present")
    if not m:
        return ""
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        ch = src[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return src[start : i + 1]
    return ""


def map_pairs(block: str) -> dict[str, str]:
    return dict(re.findall(r"([A-Z]{2,3}):\s*'((?:\\'|[^'])*)'", block))


def locale_label_block(src: str, locale: str) -> dict[str, str]:
    # LABELS_BY_LOCALE = { ja: { ... }, en: { ... }, 'zh-tw': { ... } }
    key = f"'{locale}'" if "-" in locale else locale
    m = re.search(rf"{key}:\s*\{{", src)
    assert_true(bool(m), f"labels locale {locale}")
    if not m:
        return {}
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        ch = src[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return map_pairs(src[start : i + 1])
    return {}


def main() -> int:
    js = JS.read_text(encoding="utf-8")
    loc_js = LOC_JS.read_text(encoding="utf-8")

    assert_true("KPI-PROFILE-CURRENCY-CATALOG" in js, "currency catalog marker")
    codes = extract_array(js, "CURRENCY_CODES")
    for code in REQUIRED_CODES:
        assert_true(code in codes, f"catalog has {code}")
    assert_true(len(codes) == len(set(codes)), "currency codes unique")

    country_block = extract_map_block(js, "COUNTRY_CURRENCY")
    cmap = map_pairs(country_block)
    for cc, cur in COUNTRY_MAP.items():
        assert_true(cmap.get(cc) == cur, f"map {cc}->{cur}")

    # Country catalog coverage: every location country maps to a currency
    loc_countries = re.search(r"var COUNTRY_CODES = \[([^\]]+)\]", loc_js, re.S)
    assert_true(bool(loc_countries), "location COUNTRY_CODES")
    if loc_countries:
        for cc in re.findall(r"'([A-Z]{2})'", loc_countries.group(1)):
            assert_true(cc in cmap, f"location country {cc} has currency map")
            assert_true(cmap[cc] in REQUIRED_CODES, f"location country {cc} maps to catalog")

    for loc, samples in LABEL_SAMPLES.items():
        labels = locale_label_block(js, loc)
        for code, text in samples.items():
            assert_true(labels.get(code) == text, f"{loc} label {code}")

    assert_true("function normalizeCode" in js, "normalizeCode")
    assert_true("function saveCode" in js, "saveCode")
    assert_true("function currencyForCountry" in js, "currencyForCountry")
    assert_true("function fillSelect" in js, "fillSelect")
    assert_true("function maybeSuggestFromCountry" in js, "maybeSuggestFromCountry")
    assert_true("function displayLabel" in js, "displayLabel")
    assert_true("opts.userSet" in js, "user override guard in suggest")

    # Legacy hydrate samples encoded as aliases / labels
    assert_true("'¥ - yen': 'JPY'" in js or "'¥ - Yen'" in js or "japanese yen" in js.lower(), "legacy yen alias")
    assert_true("日本円" in js, "legacy JP label hydrate")
    assert_true("新台幣" in js, "legacy ZH label hydrate")

    for loc, path in EDIT.items():
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-currency.js" in html, f"{rel} loads kpi-currency")
        assert_true("KPI-PROFILE-CURRENCY-CATALOG" in html, f"{rel} currency marker")
        assert_true('id="profile-currency"' in html, f"{rel} currency visible")
        assert_true("profile-timezone-group\" hidden" in html or 'id="profile-timezone-group" hidden' in html, f"{rel} timezone still hidden")
        assert_true("KpiCurrency.saveCode" in html, f"{rel} canonical save")
        assert_true("getSelectText(currencyEl)" not in html.split("var data = {", 1)[1].split("};", 1)[0], f"{rel} save not label")
        assert_true("hydrateCurrency" in html, f"{rel} hydrateCurrency")
        assert_true("currencyUserSet" in html, f"{rel} override flag")
        assert_true("maybeCurrencyFromCountry" in html, f"{rel} country linkage")
        assert_true("fillCurrencySelect" in html, f"{rel} fill select")
        assert_true("KPI-PROFILE-LOCATION-DATALIST" in html, f"{rel} location kept")
        assert_true("KPI-PROFILE-GENRE-PLACEHOLDER" in html, f"{rel} genre kept")
        assert_true("office-mode" in html, f"{rel} Sci-Fi/Office kept")
        # Currency must stay visible (not hidden like timezone)
        cur_chunk = html.split('id="profile-currency"', 1)[0][-200:]
        assert_true("hidden" not in cur_chunk.split("form-group")[-1], f"{rel} currency group not hidden")

    for loc, path in VIEW.items():
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-currency.js" in html, f"{rel} loads currency for display")
        assert_true("KpiCurrency.displayLabel" in html, f"{rel} displays label")
        assert_true("fixed-currency" in html, f"{rel} currency field")

    # Required mapping smoke list from spec
    for cc, cur in (
        ("JP", "JPY"),
        ("US", "USD"),
        ("GB", "GBP"),
        ("TW", "TWD"),
        ("AU", "AUD"),
        ("CA", "CAD"),
        ("DE", "EUR"),
        ("CH", "CHF"),
        ("SE", "SEK"),
        ("AE", "AED"),
    ):
        assert_true(cmap.get(cc) == cur, f"required map {cc}->{cur}")

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

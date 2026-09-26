# -*- coding: utf-8 -*-
"""Unit 5A — Business Type Foundation."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "js" / "kpi-business-type.js").read_text(encoding="utf-8")
ENTITLEMENT = (ROOT / "api" / "v1" / "_entitlement.php").read_text(encoding="utf-8")
SCHEMA = (ROOT / "api" / "v1" / "schema.sql").read_text(encoding="utf-8")
STORE_PHP = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
YEAR_STORE = (ROOT / "scripts" / "kpi_year_store_client.py").read_text(encoding="utf-8")
PL_CATALOG = (ROOT / "scripts" / "pl_line_catalog.py").read_text(encoding="utf-8")
MEAL_CLIENT = (ROOT / "scripts" / "mep_daily_meal_client.py").read_text(encoding="utf-8")

FAILED = 0
PASSED = 0

CANONICAL = (
    "restaurant",
    "retail",
    "hair_salon",
    "fitness",
    "hotel",
    "other",
)

LEGACY = {
    "restaurant": "restaurant",
    "cafe": "restaurant",
    "wear_shop": "retail",
    "retail": "retail",
    "personal_trainer": "fitness",
    "fitness": "fitness",
}


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def normalize(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if s in CANONICAL:
        return s
    lower = s.lower()
    if lower in LEGACY:
        return LEGACY[lower]
    aliases = {
        "restaurant": "restaurant",
        "cafe": "restaurant",
        "wear shop": "retail",
        "wear_shop": "retail",
        "retail": "retail",
        "飲食店": "restaurant",
        "レストラン": "restaurant",
        "カフェ": "restaurant",
        "服飾店": "retail",
        "小売": "retail",
        "零售": "retail",
        "餐廳": "restaurant",
        "咖啡廳": "restaurant",
        "Restaurant": "restaurant",
        "Cafe": "restaurant",
        "Wear Shop": "retail",
        "Retail": "retail",
        "personal_trainer": "fitness",
        "Personal Trainer": "fitness",
        "パーソナルトレーナー": "fitness",
        "私人教練": "fitness",
        "Fitness / Gym / Personal Training": "fitness",
    }
    return aliases.get(s) or aliases.get(lower)


def get_business_type(meta_value=None, legacy_value=None):
    persisted = normalize(meta_value) or normalize(legacy_value)
    return persisted or "restaurant"


def set_business_type(store, value):
    nxt = normalize(value)
    if not nxt:
        return False
    if not isinstance(store, dict):
        store = {"meta": {}, "timeline": {"dailySales": {}, "businessDays": {}}, "years": {}}
    if not isinstance(store.get("meta"), dict):
        store["meta"] = {}
    store["meta"]["businessType"] = nxt
    return True


def test_canonical_and_legacy() -> None:
    for code in CANONICAL:
        assert_true(normalize(code) == code, f"canonical {code} saves as itself")
    assert_true(normalize("cafe") == "restaurant", "cafe -> restaurant")
    assert_true(normalize("wear_shop") == "retail", "wear_shop -> retail")
    assert_true(normalize("Cafe") == "restaurant", "Cafe label -> restaurant")
    assert_true(normalize("Wear Shop") == "retail", "Wear Shop label -> retail")
    assert_true(normalize("餐廳") == "restaurant", "zh restaurant label maps")
    assert_true(normalize("服飾店") == "retail", "ja wear shop label maps")
    assert_true(get_business_type(None, None) == "restaurant", "missing -> restaurant fallback")
    assert_true(get_business_type("", "cafe") == "restaurant", "legacy cafe hydrates as restaurant")
    assert_true(get_business_type(None, "wear_shop") == "retail", "legacy wear_shop hydrates as retail")
    assert_true(normalize("personal_trainer") == "fitness", "personal_trainer -> fitness")
    assert_true(normalize("fitness") == "fitness", "fitness stays fitness")
    assert_true(get_business_type("personal_trainer", None) == "fitness", "saved personal_trainer hydrates as fitness")
    assert_true(get_business_type(None, "personal_trainer") == "fitness", "legacy personal_trainer hydrates as fitness")
    store = {"meta": {}, "years": {"2026": {"dailyExpenses": {"exp_food_cost": {"2026-01-01": 50}}}}}
    snapshot_years = json.loads(json.dumps(store["years"]))
    assert_true(set_business_type(store, "fitness"), "fitness save succeeds")
    assert_true(store["meta"]["businessType"] == "fitness", "fitness written to meta")
    assert_true(set_business_type(store, "personal_trainer"), "legacy personal_trainer save normalizes")
    assert_true(store["meta"]["businessType"] == "fitness", "personal_trainer save stores fitness")
    assert_true(store["years"] == snapshot_years, "hydrate/save does not drop years")


def test_js_source_contract() -> None:
    for code in CANONICAL:
        assert_true(f"'{code}'" in JS, f"js lists canonical {code}")
    assert_true("cafe: 'restaurant'" in JS, "js maps cafe")
    assert_true("wear_shop: 'retail'" in JS, "js maps wear_shop")
    assert_true("personal_trainer: 'fitness'" in JS, "js maps personal_trainer")
    canon_m = re.search(r"var CANONICAL = \[([\s\S]*?)\];", JS)
    assert_true(canon_m is not None, "js CANONICAL array present")
    if canon_m:
        canon_block = canon_m.group(1)
        assert_true("'fitness'" in canon_block, "js CANONICAL includes fitness")
        assert_true("'personal_trainer'" not in canon_block, "js CANONICAL does not include personal_trainer")
    assert_true("Fitness / Gym / Personal Training" in JS, "en fitness label")
    assert_true("フィットネス / ジム / パーソナルトレーニング" in JS, "ja fitness label")
    assert_true("健身 / 健身房 / 私人教練" in JS, "zh fitness label")
    assert_true("function getBusinessType" in JS, "js getBusinessType")
    assert_true("function isBusinessTypeSet" in JS, "js isBusinessTypeSet")
    assert_true("function hydrateFromServerProfile" in JS, "js hydrates BT from profile.php")
    assert_true("hydrateFromServerProfile: hydrateFromServerProfile" in JS, "js exports profile hydrate")
    assert_true("function readPersistedBusinessType" in JS, "js readPersistedBusinessType")
    assert_true("isBusinessTypeSet: isBusinessTypeSet" in JS, "js exports isBusinessTypeSet")
    assert_true("function isRestaurantLike" in JS, "js isRestaurantLike")
    assert_true("function setBusinessType" in JS, "js setBusinessType")
    assert_true("function confirmRegistration" in JS, "js registration dialog")
    assert_true("function confirmChange" in JS, "js change dialog")
    assert_true("function promptIndustryRequiredForImport" in JS, "js industry-missing import dialog")
    assert_true("function resolveDialogHost" in JS, "js mounts BT dialog in active FW host")
    assert_true(".sales-data-modal" in JS, "js Sales Data FW is a dialog host")
    assert_true(".past-sales-modal" in JS, "js Past Sales FW is a dialog host")
    assert_true("kpi-bt-dialog-overlay--hosted" in JS, "js marks hosted overlay")
    assert_true("function resolveProfileEditHref" in JS, "js reuses Profile edit href")
    assert_true("account-settings-item" in JS, "js Profile href comes from chrome contract")
    assert_true("promptIndustryRequiredForImport: promptIndustryRequiredForImport" in JS, "js exports industry-missing prompt")
    assert_true("resolveProfileEditHref: resolveProfileEditHref" in JS, "js exports Profile edit href resolver")
    assert_true("store.meta.businessType" in JS, "js writes store.meta.businessType")
    assert_true("kpiNavigator.kpiYearStore" in JS, "js uses year-store key")
    assert_true("=== 'restaurant'" in JS, "isRestaurantLike is restaurant-only")


def test_set_does_not_delete_payload() -> None:
    store = {
        "meta": {"schemaVersion": 4, "operatingYear": 2026},
        "timeline": {"dailySales": {"2026-01-01": 1000}, "businessDays": {"2026-01-01": True}},
        "years": {
            "2026": {
                "dailyMeal": {"dinner_sales": {"2026-01-01": 400}},
                "dailyExpenses": {"exp_food_cost": {"2026-01-01": 50}},
                "dailyIncome": {"food_sales": {"2026-01-01": 200}},
            }
        },
    }
    pl = {"catalog": {"lines": [{"lineId": "exp_food_cost"}]}, "expensesByYear": {"2026": {"exp_rent:0": 1}}}
    snapshot = json.loads(json.dumps({"store": store, "pl": pl}))
    assert_true(set_business_type(store, "retail"), "set retail succeeds")
    assert_true(store["meta"]["businessType"] == "retail", "meta updated")
    assert_true(store["timeline"]["dailySales"]["2026-01-01"] == 1000, "sales kept")
    assert_true(store["years"]["2026"]["dailyMeal"]["dinner_sales"]["2026-01-01"] == 400, "meal kept")
    assert_true(store["years"]["2026"]["dailyExpenses"]["exp_food_cost"]["2026-01-01"] == 50, "expense kept")
    assert_true(store["years"]["2026"]["dailyIncome"]["food_sales"]["2026-01-01"] == 200, "income kept")
    assert_true(pl == snapshot["pl"], "pl payload untouched")
    assert_true(
        store["years"] == snapshot["store"]["years"],
        "years object not rebuilt away",
    )


def test_basic_entitlement_keeps_meta() -> None:
    assert_true("dailyExpenses" in ENTITLEMENT, "entitlement still about dailyExpenses")
    assert_true("businessType" not in ENTITLEMENT, "entitlement does not strip businessType")
    # Business Type must not be a year-store / kpi_users column. Profile may store
    # business_type (Admin Profile Sync) — strip that table before asserting.
    schema_wo_profile = re.sub(
        r"create\s+table\s+if\s+not\s+exists\s+kpi_user_profiles\b.*?;",
        "",
        SCHEMA,
        flags=re.I | re.S,
    )
    assert_true("business_type" not in schema_wo_profile.lower(), "no business_type column outside profiles")
    assert_true("revenue_mode" not in SCHEMA.lower(), "no revenue_mode column")
    docs = (ROOT / "docs" / "backend-phase-a-store-api.md").read_text(encoding="utf-8")
    assert_true("中身を解釈せず" in docs, "store API remains opaque JSON")
    assert_true("kpi_v1_entitlement_strip_pro_from_store" in STORE_PHP, "store.php still uses entitlement strip")
    strip = re.search(
        r"function kpi_v1_entitlement_strip_pro_from_store[\s\S]+?^}",
        ENTITLEMENT,
        re.M,
    )
    assert_true(strip is not None, "found strip_pro function")
    if strip:
        assert_true("dailyExpenses" in strip.group(0), "strip only dailyExpenses")
        assert_true("businessType" not in strip.group(0), "strip does not touch businessType")


def test_surfaces() -> None:
    jp_reg = (ROOT / "register" / "registration_si-fi_jp" / "registration_si-fi_jp.html").read_text(encoding="utf-8")
    en_reg = (ROOT / "en" / "register" / "registration_si-fi_en.html").read_text(encoding="utf-8")
    zh_reg = (ROOT / "zh-tw" / "register" / "registration_si-fi_zh-tw.html").read_text(encoding="utf-8")
    for label, html in (("jp", jp_reg), ("en", en_reg), ("zh", zh_reg)):
        assert_true('id="business-type"' in html, f"{label} register has business-type")
        assert_true("kpi-business-type.js" in html, f"{label} register includes helper")
        assert_true("required" in html.split('id="business-type"', 1)[1][:120], f"{label} BT required")
    jp_js = (ROOT / "register" / "script.js").read_text(encoding="utf-8")
    en_js = (ROOT / "en" / "register" / "script.js").read_text(encoding="utf-8")
    zh_js = (ROOT / "zh-tw" / "register" / "script.js").read_text(encoding="utf-8")
    for label, js in (("jp", jp_js), ("en", en_js), ("zh", zh_js)):
        assert_true("confirmRegistration" in js, f"{label} register waits for confirm dialog")
        assert_true("registrationConfirmed" in js, f"{label} register does not save immediately")
        assert_true("setBusinessType" in js, f"{label} register writes canonical after 201")
        assert_true("isBusinessTypeOk" in js, f"{label} register requires BT")
        assert_true("applyHint" in js, f"{label} register plan hint")

    jp_edit = (ROOT / "setting" / "profile_edit.html").read_text(encoding="utf-8")
    en_edit = (ROOT / "en" / "setting" / "profile_edit.html").read_text(encoding="utf-8")
    zh_edit = (ROOT / "zh-tw" / "setting" / "profile_edit.html").read_text(encoding="utf-8")
    for label, html in (("jp", jp_edit), ("en", en_edit), ("zh", zh_edit)):
        # BR-LAUNCH-01-A Option B: UI hydrates from meta.businessType only (unset ≠ restaurant)
        assert_true("readMetaBusinessType()" in html, f"{label} profile hydrates from meta BT")
        assert_true("syncIndustrySelectFromMeta" in html, f"{label} profile re-syncs select from meta")
        assert_true("ensureUserScopeBound" in html, f"{label} profile waits for user-scope bind")
        assert_true("initialBusinessType" in html, f"{label} profile snapshots loaded BT")
        assert_true("currentType !== canonicalType" in html, f"{label} warning compares effective type")
        assert_true(
            "getBusinessType()" not in html.split("var initialBusinessType", 1)[1][:500],
            f"{label} hydrate does not silent-default via getBusinessType",
        )
        assert_true("confirmChange" in html, f"{label} profile change warning")
        assert_true("profileSaveConfirmed" in html, f"{label} profile does not save change immediately")
        assert_true("setBusinessType" in html, f"{label} profile writes store.meta")
        assert_true("wear_shop" not in html, f"{label} old wear_shop genre gone")
        assert_true("kpi-business-type.js" in html, f"{label} profile edit includes helper")
        assert_true("maybeFocusIndustryFromHash" in html, f"{label} profile edit honors #profile-industry")
        assert_true('id="profile-industry"' in html, f"{label} profile edit has industry field")

    jp_view = (ROOT / "setting" / "profile.html").read_text(encoding="utf-8")
    en_view = (ROOT / "en" / "setting" / "profile.html").read_text(encoding="utf-8")
    zh_view = (ROOT / "zh-tw" / "setting" / "profile.html").read_text(encoding="utf-8")
    for label, html in (("jp", jp_view), ("en", en_view), ("zh", zh_view)):
        assert_true("KpiBusinessType.label" in html, f"{label} profile view shows localized label")
        assert_true("readMetaBusinessType" in html, f"{label} profile view Option B unset-safe")

def test_unit5a_did_not_touch_mep_pl_meal() -> None:
    assert_true("exp_food_cost" in PL_CATALOG, "PL catalog still food default")
    assert_true("incDinner" in MEAL_CLIENT, "MEP meal client untouched")
    assert_true("function writeDailyMeal" in YEAR_STORE, "year store meal APIs remain")
    assert_true("getBusinessType" not in YEAR_STORE, "year-store client not widened in 5A")


def test_chrome_helper_for_later_units() -> None:
    chrome = (ROOT / "scripts" / "site_chrome.py").read_text(encoding="utf-8")
    assert_true("kpi-business-type.js" in chrome, "site chrome exposes helper to later units")


def main() -> int:
    test_canonical_and_legacy()
    test_js_source_contract()
    test_set_does_not_delete_payload()
    test_basic_entitlement_keeps_meta()
    test_surfaces()
    test_unit5a_did_not_touch_mep_pl_meal()
    test_chrome_helper_for_later_units()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""Server profile sync finalization — static contract tests."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        print(f"PASS  {name}")
    else:
        FAILED += 1
        print(f"FAIL  {name}" + (f" — {detail}" if detail else ""))


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> None:
    schema = read("api/v1/schema_admin_console_foundation.add.sql")
    for col in [
        "business_name",
        "company_name",
        "business_type",
        "genre",
        "locale",
        "country",
        "state_region",
        "city",
        "currency",
        "updated_at",
    ]:
        check(f"schema has {col}", col in schema)

    profile_api = read("api/v1/profile.php")
    check("profile GET path", "REQUEST_METHOD" in profile_api and "kpi_v1_profile_read" in profile_api)
    check("profile requires session", "kpi_v1_auth_current_user_id" in profile_api)
    check("profile write uses session uid", "kpi_v1_profile_write($cfg, $uid" in profile_api)
    check("profile ignores client userId", "unset($body['userId']" in profile_api)
    check("profile no password fields", "password" not in profile_api.lower() or "password_hash" not in profile_api)

    store = read("api/v1/_admin_store.php")
    check("empty profile synced false", "'synced' => false" in store)
    check("row profile synced true", "'synced' => true" in store)
    check("profile upsert", "ON DUPLICATE KEY UPDATE" in store)

    js = read("js/kpi-profile-server.js")
    check("JS saveServerProfile", "function saveServerProfile" in js)
    check("JS loadServerProfile", "function loadServerProfile" in js)
    check("JS hydrateEditForm", "function hydrateEditForm" in js)
    check("JS mergePreferServer", "function mergePreferServer" in js)
    check("JS auth gate before save", "isAuthenticatedSession" in js)
    check("JS inflight save guard", "saveInflight" in js)
    check("JS sync result stash", "kpi-profile-server-sync" in js)
    check("JS does not wipe on unsynced", "!serverProfile.synced" in js or "serverProfile.synced" in js)
    check("JS locale normalize", "normalizeLocale" in js)
    check("JS mapping businessName", "businessName" in js)
    check("JS mapping companyName", "companyName" in js)
    check("JS mapping stateRegion", "stateRegion" in js)

    # mergePreferServer must require non-empty server field
    check(
        "merge only non-empty server fields",
        "hasText(s[k])" in js,
    )

    users = read("api/v1/admin/users.php")
    check("admin users joins profile", "kpi_v1_profile_read" in users)
    check("admin users profileSynced", "profileSynced" in users)
    users_code = "\n".join(
        line
        for line in users.splitlines()
        if not line.strip().startswith("*") and not line.strip().startswith("//") and not line.strip().startswith("#")
    )
    check("admin users no password_hash", "password_hash" not in users_code and "passwordHash" not in users_code)

    detail = read("api/v1/admin/user-detail.php")
    check("admin detail returns profile", "'profile' => $profile" in detail or '"profile"' in detail)
    check("admin detail founder gate", "kpi_v1_auth_require_founder_superadmin" in detail)

    admin_js = read("admin/admin.js")
    check("admin users Not synced", "Not synced" in admin_js)
    check("admin detail Business Profile", "Business Profile" in admin_js)
    check("admin detail Location", "Location" in admin_js)
    check("admin detail shows currency", "Currency" in admin_js)

    for rel in [
        "setting/profile_edit.html",
        "en/setting/profile_edit.html",
        "zh-tw/setting/profile_edit.html",
    ]:
        t = read(rel)
        check(f"{rel} loads profile-server js", "kpi-profile-server.js" in t)
        check(f"{rel} calls saveServerProfile", "saveServerProfile" in t)
        check(f"{rel} calls hydrateEditForm", "hydrateEditForm" in t)
        check(f"{rel} local save before server", "kpi-profile-last" in t and t.find("kpi-profile-last") < t.find("saveServerProfile"))
        check(
            f"{rel} server fail still navigates",
            "saveServerProfile(data).then(goProfile).catch(goProfile)" in t,
        )

    # Country / currency canonical still owned by existing helpers on save path
    jp = read("setting/profile_edit.html")
    check("JP save uses saveCountry", "saveCountry" in jp)
    check("JP save uses saveCode", "saveCode" in jp or "KpiCurrency.saveCode" in jp)

    # Regression: business types still present
    bt = read("js/kpi-business-type.js")
    for tname in ["restaurant", "retail", "hair_salon", "fitness", "hotel", "other"]:
        check(f"business type {tname}", tname in bt)

    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()

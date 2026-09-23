# -*- coding: utf-8 -*-
"""C2-C stale-tab / expected-user guard. No excel. No Demo fixture rewrite."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FAILED = 0
PASSED = 0


def check(name: str, cond: bool) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        print("PASS", name)
    else:
        FAILED += 1
        print("FAIL", name)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    auth = read("js/kpi-auth-client.js")
    gw = read("js/kpi-data-gateway.js")
    inputs = read("js/kpi-daily-inputs-sync.js")
    facts = read("js/kpi-daily-facts-sync.js")
    profile_js = read("js/kpi-profile-server.js")
    auth_php = read("api/v1/_auth.php")
    store = read("api/v1/store.php")
    daily = read("api/v1/daily-inputs.php")
    profile_php = read("api/v1/profile.php")
    facts_php = read("api/v1/daily-facts.php")
    rebuild = read("api/v1/rebuild-year-facts.php")
    set_plan = read("api/v1/auth/set-plan.php")

    check("auth snapshot marker", "KPI-C2-C-STALE-ACCOUNT" in auth)
    check("pageUserId snapshot", "var pageUserId" in auth and "function snapshotPageUserId" in auth)
    check("storage lastKpiUserId", "ev.key !== LAST_USER_KEY" in auth)
    check("stale JP copy", "別のタブでログイン中のアカウントが変更されました" in auth)
    check("stale EN copy", "The signed-in account changed in another tab" in auth)
    check("stale ZH copy", "其他分頁的登入帳號已變更" in auth)
    check("no silent reload on stale", "location.reload" not in auth.split("KPI-C2-C-STALE-ACCOUNT", 1)[-1][:4000])
    check("assertCanMutate exported", "assertCanMutateUserData: assertCanMutateUserData" in auth)
    check("login still public", "/auth/login" in auth and "publicPath" in auth)

    check("gateway holdPutsForStaleAccount", "holdPutsForStaleAccount" in gw)
    check("gateway expectedUserId on PUT", "attachExpectedUser" in gw and "buildPutBody" in gw)
    check("gateway stale 403 is not OCC", "data.error === 'stale_account'" in gw)
    check("gateway OCC conflict still 409", "res.status === 409 || data.error === 'conflict'" in gw)
    check("gateway L5 stripPro still present", "stripProFromStore" in gw)

    check("daily-inputs blocks stale", "stale_account" in inputs and "attachExpectedUser" in inputs)
    check("profile save blocks stale", "stale_account" in profile_js)
    check("facts/rebuild guarded", "stale_account" in facts and "withExpectedUser" in facts)

    check("php helper exists", "function kpi_v1_require_expected_user" in auth_php)
    check("php mismatch 403 stale_account", "'stale_account'" in auth_php)
    check("php missing 428", "precondition_required" in auth_php)
    check("php does not use expected as destination", "return $uid;" in auth_php)
    check("store.php calls helper", "kpi_v1_require_expected_user($userId, $body)" in store)
    check("store.php still session resolve", "kpi_v1_store_resolve_user_id" in store)
    check("store.php OCC unchanged", "kpi_v1_parse_expected_revision" in store)
    check("daily-inputs helper", "kpi_v1_require_expected_user($userId, $body)" in daily)
    check("profile helper", "kpi_v1_require_expected_user($uid, $body)" in profile_php)
    check("profile still unsets client userId", "unset($body['userId']" in profile_php)
    check("daily-facts helper", "kpi_v1_require_expected_user($userId, $body)" in facts_php)
    check("rebuild helper", "kpi_v1_require_expected_user($userId, $body)" in rebuild)
    check("set-plan self helper", "kpi_v1_require_expected_user($uid, $body)" in set_plan)
    check("CORS expected-user header", "X-KPI-Expected-User" in auth_php)

    annual = read("app/annual/index.html")
    check("annual cache-bust auth c2c", "kpi-auth-client.js?v=20260923-c2c" in annual)
    check("annual cache-bust gateway c2c", "kpi-data-gateway.js?v=20260923-c2c" in annual)
    check("lease still independent", "kpiNavigator.kpiEditLeases" in annual)

    if FAILED:
        print(f"\nFAILED {FAILED}  PASSED {PASSED}")
        return 1
    print(f"\nALL PASS {PASSED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

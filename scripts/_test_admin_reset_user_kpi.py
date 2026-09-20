# -*- coding: utf-8 -*-
"""BR-LAUNCH-01-B — Admin reset-user-kpi contract tests.

Static source contracts + in-memory isolation logic. No production DB. No secrets.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

CONFIRM = "RESET_KPN_DATA"


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


# --- In-memory mirrors ---


def safe_user_id(user_id: str) -> Optional[str]:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "", str(user_id))
    if safe == "" or safe.startswith("_"):
        return None
    return safe


def self_target_error(actor_id: str, target_id: str) -> Optional[str]:
    if actor_id and actor_id == target_id:
        return "self_target_forbidden"
    return None


def resolve_target(
    users_by_id: dict[str, dict],
    email_index: dict[str, str],
    email: Optional[str],
    user_id: Optional[str],
) -> dict[str, Any]:
    has_email = bool(email and str(email).strip())
    has_id = bool(user_id and str(user_id).strip())
    if not has_email and not has_id:
        return {"ok": False, "error": "missing_target"}
    u_email = None
    u_id = None
    if has_email:
        em = str(email).strip().lower()
        if "@" not in em:
            return {"ok": False, "error": "invalid_email"}
        uid = email_index.get(em)
        if not uid or uid not in users_by_id:
            return {"ok": False, "error": "user_not_found"}
        u_email = users_by_id[uid]
    if has_id:
        sid = safe_user_id(str(user_id))
        if sid is None:
            return {"ok": False, "error": "invalid_id"}
        if sid not in users_by_id:
            return {"ok": False, "error": "user_not_found"}
        u_id = users_by_id[sid]
    if u_email is not None and u_id is not None and u_email["userId"] != u_id["userId"]:
        return {"ok": False, "error": "ambiguous_target"}
    return {"ok": True, "user": u_email or u_id}


def reset_user_kpi(
    actor_id: str,
    target: dict,
    stores: dict[str, dict],
    profiles: dict[str, dict],
    daily_inputs: dict[str, list],
    daily_facts: dict[str, list],
    epochs: dict[str, int],
    confirm: str,
) -> dict[str, Any]:
    if confirm != CONFIRM:
        return {"ok": False, "error": "confirm_required"}
    tid = target["userId"]
    err = self_target_error(actor_id, tid)
    if err:
        return {"ok": False, "error": err}
    # wipe only target
    stores[tid] = {"store": None, "annualNav": None, "pl": None}
    profiles.pop(tid, None)
    daily_inputs[tid] = []
    daily_facts[tid] = []
    epochs[tid] = epochs.get(tid, 0) + 1
    return {
        "ok": True,
        "userId": tid,
        "email": target.get("email", ""),
        "sessionEpoch": epochs[tid],
        "reset": {
            "store": True,
            "profile": True,
            "dailyInputs": True,
            "dailyFacts": True,
            "sessionRevoked": True,
        },
    }


def run_logic_tests() -> None:
    users = {
        "founder1": {
            "userId": "founder1",
            "email": "founder@example.com",
            "passwordHash": "FOUNDER_HASH",
            "plan": "pro",
            "role": "founder_superadmin",
            "disabled": False,
        },
        "smoke01": {
            "userId": "smoke01",
            "email": "kpn_empty_state_smoke01@trial.forge-laboratory.com",
            "passwordHash": "SMOKE_HASH_KEEP",
            "plan": "pro",
            "role": "user",
            "disabled": False,
            "parentUserId": None,
        },
        "other02": {
            "userId": "other02",
            "email": "other@example.com",
            "passwordHash": "OTHER_HASH",
            "plan": "pro",
            "role": "user",
            "disabled": False,
        },
    }
    email_index = {u["email"]: u["userId"] for u in users.values()}
    stores = {
        "smoke01": {"store": {"meta": {"businessType": "restaurant"}, "years": {"2026": {}}}, "annualNav": {"x": 1}, "pl": {"y": 1}},
        "other02": {"store": {"meta": {"businessType": "retail"}, "years": {"2026": {"keep": True}}}, "annualNav": {"o": 1}, "pl": {"o": 1}},
    }
    profiles = {
        "smoke01": {"businessType": "restaurant", "businessName": "Temp"},
        "other02": {"businessType": "retail", "businessName": "Keep"},
    }
    daily_inputs = {
        "smoke01": [{"iso": "2026-01-01", "sales": 100}],
        "other02": [{"iso": "2026-01-01", "sales": 999}],
    }
    daily_facts = {
        "smoke01": [{"iso": "2026-01-01", "sales": 100}],
        "other02": [{"iso": "2026-01-01", "sales": 999}],
    }
    epochs: dict[str, int] = {"smoke01": 0, "other02": 3}
    plan_history = [{"userId": "smoke01", "new_plan": "pro"}]

    # bad confirm
    r = resolve_target(users, email_index, "kpn_empty_state_smoke01@trial.forge-laboratory.com", None)
    check("resolve smoke by email", r["ok"] and r["user"]["userId"] == "smoke01")
    bad = reset_user_kpi(
        "founder1", r["user"], stores, profiles, daily_inputs, daily_facts, epochs, "WRONG"
    )
    check("bad confirm rejected", bad.get("error") == "confirm_required")
    check("bad confirm did not wipe store", stores["smoke01"]["store"] is not None)

    # unknown user
    miss = resolve_target(users, email_index, "missing@example.com", None)
    check("unknown email 404 shape", miss.get("error") == "user_not_found")

    # ambiguous
    amb = resolve_target(users, email_index, "kpn_empty_state_smoke01@trial.forge-laboratory.com", "other02")
    check("ambiguous email+userId rejected", amb.get("error") == "ambiguous_target")

    # missing target
    miss_t = resolve_target(users, email_index, None, None)
    check("missing target rejected", miss_t.get("error") == "missing_target")

    # self target
    self_r = reset_user_kpi(
        "founder1",
        users["founder1"],
        stores,
        profiles,
        daily_inputs,
        daily_facts,
        epochs,
        CONFIRM,
    )
    check("self target forbidden", self_r.get("error") == "self_target_forbidden")

    # happy path by email
    before_other_store = json_clone(stores["other02"])
    before_other_prof = json_clone(profiles["other02"])
    before_other_in = list(daily_inputs["other02"])
    before_other_fa = list(daily_facts["other02"])
    before_hash = users["smoke01"]["passwordHash"]
    before_plan = users["smoke01"]["plan"]
    before_role = users["smoke01"]["role"]
    before_disabled = users["smoke01"]["disabled"]
    before_email = users["smoke01"]["email"]
    before_history = list(plan_history)

    ok = reset_user_kpi(
        "founder1",
        users["smoke01"],
        stores,
        profiles,
        daily_inputs,
        daily_facts,
        epochs,
        CONFIRM,
    )
    check("reset ok", ok.get("ok") is True)
    check("store wiped", stores["smoke01"]["store"] is None and stores["smoke01"]["pl"] is None)
    check("profile wiped", "smoke01" not in profiles)
    check("BT unset via profile gone", "smoke01" not in profiles)
    check("daily_inputs target 0", daily_inputs["smoke01"] == [])
    check("daily_facts target 0", daily_facts["smoke01"] == [])
    check("session revoked bump", epochs["smoke01"] == 1)
    check("plan remains pro", users["smoke01"]["plan"] == before_plan == "pro")
    check("email unchanged", users["smoke01"]["email"] == before_email)
    check("password_hash unchanged", users["smoke01"]["passwordHash"] == before_hash)
    check("role unchanged", users["smoke01"]["role"] == before_role)
    check("disabled unchanged", users["smoke01"]["disabled"] == before_disabled)
    check("other store unchanged", stores["other02"] == before_other_store)
    check("other profile unchanged", profiles["other02"] == before_other_prof)
    check("other daily inputs unchanged", daily_inputs["other02"] == before_other_in)
    check("other daily facts unchanged", daily_facts["other02"] == before_other_fa)
    check("plan_history preserved", plan_history == before_history)
    check("response has reset flags", ok["reset"]["store"] and ok["reset"]["sessionRevoked"])
    check("no password in response", "password" not in ok and "passwordHash" not in ok)

    # matching email+userId ok
    stores["smoke01"] = {"store": {"meta": {"businessType": "hotel"}}, "annualNav": None, "pl": None}
    profiles["smoke01"] = {"businessType": "hotel"}
    daily_inputs["smoke01"] = [{"iso": "2026-02-01"}]
    daily_facts["smoke01"] = [{"iso": "2026-02-01"}]
    both = resolve_target(
        users,
        email_index,
        "kpn_empty_state_smoke01@trial.forge-laboratory.com",
        "smoke01",
    )
    check("email+userId same user ok", both.get("ok") is True)
    ok2 = reset_user_kpi(
        "__plan_admin_token__",
        both["user"],
        stores,
        profiles,
        daily_inputs,
        daily_facts,
        epochs,
        CONFIRM,
    )
    check("token actor can reset", ok2.get("ok") is True)
    check("second reset store empty", stores["smoke01"]["store"] is None)
    check("epoch bumped again", epochs["smoke01"] == 2)

    # empty store contract shape
    empty = stores["smoke01"]
    check(
        "empty store contract",
        empty.get("store") is None and empty.get("annualNav") is None and empty.get("pl") is None,
    )


def json_clone(obj: Any) -> Any:
    import json

    return json.loads(json.dumps(obj))


def run_source_tests() -> None:
    api_path = ROOT / "api/v1/admin/reset-user-kpi.php"
    helper_path = ROOT / "api/v1/_admin_reset_kpi.php"
    check("endpoint file exists", api_path.is_file())
    check("helper file exists", helper_path.is_file())
    api = read("api/v1/admin/reset-user-kpi.php")
    helper = read("api/v1/_admin_reset_kpi.php")
    admin_auth = read("api/v1/_admin.php")
    bootstrap = read("api/v1/_bootstrap.php")
    auth_client = read("js/kpi-auth-client.js")
    ops = read("docs/free-trial-account-ops.md")
    path = read("docs/development-path.md")

    check("confirm constant", "RESET_KPN_DATA" in helper and "KPI_V1_ADMIN_RESET_CONFIRM" in api)
    check("founder or token auth", "kpi_v1_admin_reset_require_actor" in api)
    check("token match helper", "kpi_v1_auth_admin_token_matches" in helper)
    check("founder gate available", "kpi_v1_auth_require_founder_superadmin" in helper)
    check("unauthorized 401 in founder gate", "unauthorized" in admin_auth and "401" in admin_auth)
    check("forbidden 403 in founder gate", "forbidden" in admin_auth and "403" in admin_auth)
    check("transaction begin", "beginTransaction" in helper)
    check("transaction rollback", "rollBack" in helper)
    check("store wipe NULL cols", "store_json = NULL" in helper and "annual_nav_json = NULL" in helper and "pl_json = NULL" in helper)
    check("profile DELETE", "DELETE FROM kpi_user_profiles WHERE user_id = ?" in helper)
    check("daily_inputs DELETE by user_id", "DELETE FROM kpi_daily_inputs WHERE user_id = ?" in helper)
    check("daily_facts DELETE by user_id", "DELETE FROM kpi_daily_facts WHERE user_id = ?" in helper)
    check("session revoke bump", "kpi_v1_session_revoke_bump" in helper)
    check("no broad DELETE inputs", not re.search(r"DELETE FROM kpi_daily_inputs\s*;", helper))
    check("no broad DELETE facts", not re.search(r"DELETE FROM kpi_daily_facts\s*;", helper))
    check("ambiguous_target handled", "ambiguous_target" in helper)
    check("missing_target handled", "missing_target" in helper)
    check("self_target via admin_actions", "kpi_v1_admin_actions_self_target_error" in helper)
    # Success payload keys only (docblock may mention password_hash as "never return")
    success_block = api[api.rfind("kpi_v1_json_out(200") :]
    check(
        "200 payload omits secrets",
        "password" not in success_block.lower()
        and "token" not in success_block.lower()
        and "'userId'" in success_block
        and "'reset'" in success_block,
    )
    check("clearUserScopedLocalData exported", "clearUserScopedLocalData: clearUserScopedLocalData" in auth_client)
    check("lastKpiUserId key present", "kpiNavigator.lastKpiUserId" in auth_client)
    check("same uid bind keeps LS", "Same userId → keep LS" in auth_client or "prev !== uid" in auth_client)
    check("docs Smoke Reset section", "New User Smoke Reset" in ops)
    check("docs reset-user-kpi path", "admin/reset-user-kpi.php" in ops)
    check("docs PowerShell clear flow", "clearUserScopedLocalData" in ops)
    check("path mentions 01-B", "BR-LAUNCH-01-B" in path)
    check("plan_history not deleted", "DELETE FROM kpi_plan_history" not in helper)
    check("kpi_users not deleted", "DELETE FROM kpi_users" not in helper)
    check("soft missing inputs table", "kpi_v1_db_inputs_table_missing" in helper)
    check("soft missing facts table", "kpi_v1_db_facts_table_missing" in helper)
    check("empty store blob contract", "'store' => null" in bootstrap and "'annualNav' => null" in bootstrap)
    check("POST required", "kpi_v1_auth_require_post" in api)
    check("confirm_required on bad confirm", "confirm_required" in api)


def main() -> None:
    run_source_tests()
    run_logic_tests()
    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()

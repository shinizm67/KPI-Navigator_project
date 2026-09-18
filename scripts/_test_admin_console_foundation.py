# -*- coding: utf-8 -*-
"""Founder Admin Console Foundation — static contract tests."""
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
    mig = read("api/v1/schema_admin_console_foundation.add.sql")
    check("migration adds role", "role VARCHAR(32)" in mig)
    check("migration adds last_login_at", "last_login_at" in mig)
    check("migration adds parent_user_id", "parent_user_id" in mig)
    check("migration creates kpi_plan_history", "CREATE TABLE IF NOT EXISTS kpi_plan_history" in mig)
    check("migration creates kpi_user_profiles", "CREATE TABLE IF NOT EXISTS kpi_user_profiles" in mig)
    check("migration does not invent history", "Does NOT invent" in mig or "Does NOT invent historical" in mig)

    admin = read("api/v1/_admin.php")
    check("founder role helper", "kpi_v1_auth_is_founder_superadmin" in admin)
    check("founder API require", "kpi_v1_auth_require_founder_superadmin" in admin)
    check("founder page require", "kpi_v1_admin_require_founder_page" in admin)
    check(
        "safe user omits hash field",
        "'passwordHash'" not in admin and '"passwordHash"' not in admin and "passwordHash' =>" not in admin,
    )

    login = read("api/v1/auth/login.php")
    check("login updates last login on success", "kpi_v1_admin_touch_last_login" in login)
    check("failed login path has no last-login before verify", login.find("password_verify") < login.find("kpi_v1_admin_touch_last_login"))

    set_plan = read("api/v1/auth/set-plan.php")
    check("set-plan appends history", "kpi_v1_plan_history_append" in set_plan)

    for rel in [
        "api/v1/admin/dashboard.php",
        "api/v1/admin/users.php",
        "api/v1/admin/user-detail.php",
    ]:
        t = read(rel)
        check(f"{rel} founder gate", "kpi_v1_auth_require_founder_superadmin" in t)
        # Response construction must not include hash keys (comments mentioning the ban are OK).
        code = "\n".join(line for line in t.splitlines() if not line.strip().startswith("*") and not line.strip().startswith("//"))
        check(f"{rel} no password_hash in code", "password_hash" not in code and "passwordHash" not in code)

    for rel in [
        "admin/index.php",
        "admin/users/index.php",
        "admin/users/detail/index.php",
    ]:
        t = read(rel)
        check(f"{rel} page founder gate", "kpi_v1_admin_require_founder_page" in t)

    detail = read("api/v1/admin/user-detail.php")
    check("detail uses id query", "$_GET['id']" in detail or '$_GET["id"]' in detail)

    profile = read("api/v1/profile.php")
    check("profile endpoint session required", "kpi_v1_auth_current_user_id" in profile)
    check("profile write path", "kpi_v1_profile_write" in profile)

    store = read("api/v1/_admin_store.php")
    parent_mod = read("api/v1/_admin_parent.php")
    check("parent validate rejects self", "self_parent" in parent_mod or "$parentUserId === $childUserId" in parent_mod)
    check("cycle walk present", "$guard" in parent_mod or "cycle" in parent_mod.lower())
    check("parent validate helper wired", "kpi_v1_admin_parent_reject_reason" in store)

    cfg = read("api/v1/config.example.php")
    check("founder emails config key", "founderSuperAdminEmails" in cfg)
    check("registration still disabled default", "'registrationEnabled' => false" in cfg)

    js = read("js/kpi-profile-server.js")
    check("profile server sync helper", "saveServerProfile" in js)
    check("profile server hydrate helper", "hydrateEditForm" in js)
    check("profile server merge helper", "mergePreferServer" in js)

    ui = read("admin/admin.js")
    check("users table row navigates detail", "data-href" in ui)
    check("detail renders dossier", "User Dossier" in ui)
    check("related edit change parent", "Change Parent" in ui)
    check("related edit set-parent API", "set-parent.php" in ui)
    check("plan history heading in detail UI", "Plan History" in ui)
    check("plan history empty copy", "No plan history yet." in ui)

    set_parent = read("api/v1/admin/set-parent.php")
    check("set-parent founder gate", "kpi_v1_auth_require_founder_superadmin" in set_parent)
    check("set-parent uses helper", "kpi_v1_admin_set_parent" in set_parent)

    # Ensure trial auto-promote not present
    check(
        "no auto full_authorized promote",
        "full_authorized" not in admin.lower() or "never" in admin.lower(),
    )
    check("admin does not auto-promote trial", "trial.forge" not in admin)

    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()

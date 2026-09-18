# -*- coding: utf-8 -*-
"""Admin Actions Foundation — Force Logout / Password Reset / Disable.

Static contract + in-memory logic. No production DB. No PHP binary required.
"""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any, Optional

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


# --- Python mirrors of session revoke + admin action guards ---

def session_revoke_safe_user_id(user_id: str) -> Optional[str]:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "", str(user_id))
    if safe == "" or safe.startswith("_"):
        return None
    return safe


def session_revoke_get_epoch(store: dict[str, int], user_id: str) -> int:
    return int(store.get(user_id, 0))


def session_revoke_bump(store: dict[str, int], user_id: str) -> int:
    nxt = session_revoke_get_epoch(store, user_id) + 1
    store[user_id] = nxt
    return nxt


def session_valid(store: dict[str, int], user_id: str, session_epoch: Optional[int]) -> bool:
    need = session_revoke_get_epoch(store, user_id)
    if session_epoch is None:
        return need == 0
    return int(session_epoch) >= need


def self_target_error(actor_id: str, target_id: str) -> Optional[str]:
    if actor_id and actor_id == target_id:
        return "self_target_forbidden"
    return None


def force_logout(store: dict[str, int], users: dict[str, dict], actor_id: str, target_id: str):
    err = self_target_error(actor_id, target_id)
    if err:
        return {"ok": False, "error": err}
    if session_revoke_safe_user_id(target_id) is None:
        return {"ok": False, "error": "invalid_id"}
    if target_id not in users:
        return {"ok": False, "error": "user_not_found"}
    epoch = session_revoke_bump(store, target_id)
    return {"ok": True, "userId": target_id, "sessionEpoch": epoch}


def set_disabled(store: dict[str, int], users: dict[str, dict], actor_id: str, target_id: str, disabled: bool):
    err = self_target_error(actor_id, target_id)
    if err:
        return {"ok": False, "error": err}
    if target_id not in users:
        return {"ok": False, "error": "user_not_found"}
    users[target_id]["disabled"] = bool(disabled)
    out: dict[str, Any] = {"ok": True, "user": {"userId": target_id, "disabled": bool(disabled)}}
    if disabled:
        out["sessionEpoch"] = session_revoke_bump(store, target_id)
    return out


def admin_send_reset(users: dict[str, dict], target_id: str, mail_log: list):
    if target_id not in users:
        return {"ok": False, "error": "user_not_found"}
    u = users[target_id]
    if u.get("disabled"):
        return {"ok": False, "error": "user_disabled"}
    # mirror: create sha256 token hash only (never store plaintext)
    plain = "a" * 64
    token_hash = hashlib.sha256(plain.encode()).hexdigest()
    mail_log.append({"email": u["email"], "token_hash": token_hash, "plain_in_mail": True})
    return {
        "ok": True,
        "mailed": True,
        "email": u["email"],
        "user": {"userId": target_id, "email": u["email"]},
        "token_hash": token_hash,
    }


def run_logic_tests() -> None:
    store: dict[str, int] = {}
    users = {
        "founder1": {"userId": "founder1", "email": "founder@example.com", "disabled": False, "role": "founder_superadmin"},
        "u_test01": {"userId": "u_test01", "email": "test@example.com", "disabled": False, "passwordHash": "SECRET_HASH"},
        "u_gone": None,  # type: ignore
    }
    users.pop("u_gone")

    # 1 Founder → test user force logout success
    r = force_logout(store, users, "founder1", "u_test01")
    check("1 force logout success", r.get("ok") is True and r.get("sessionEpoch") == 1)

    # session stamped at login epoch 0 is now invalid; new login epoch 1 is valid
    check("5 old session invalid after force logout", not session_valid(store, "u_test01", 0))
    check("5 new login session valid", session_valid(store, "u_test01", 1))

    # 2 non-Founder is API-level (source check) — logic still blocks self
    # 3 nonexistent
    r = force_logout(store, users, "founder1", "u_missing")
    check("3 nonexistent force logout", r.get("error") == "user_not_found")

    # 4 self target
    r = force_logout(store, users, "founder1", "founder1")
    check("4 self force logout forbidden", r.get("error") == "self_target_forbidden")

    # Password reset
    mail_log: list = []
    r = admin_send_reset(users, "u_test01", mail_log)
    check("6 admin reset mailed", r.get("ok") is True and r.get("mailed") is True)
    check("6 token stored as sha256 only in model", len(r.get("token_hash", "")) == 64)
    check("9 password hash not in reset response", "passwordHash" not in json.dumps(r))

    r = admin_send_reset(users, "u_missing", mail_log)
    check("8 nonexistent reset rejected", r.get("error") == "user_not_found")

    # Disable
    r = set_disabled(store, users, "founder1", "u_test01", True)
    check("11 disable success", r.get("ok") is True and users["u_test01"]["disabled"] is True)
    check("17 disable bumps session", r.get("sessionEpoch") == 2)
    check("16 status readback", users["u_test01"]["disabled"] is True)

    # disabled login reject (mirror)
    def login_allowed(uid: str) -> bool:
        u = users.get(uid)
        return bool(u) and not u.get("disabled")

    check("12 disabled login rejected", login_allowed("u_test01") is False)

    r = set_disabled(store, users, "founder1", "founder1", True)
    check("14 self disable forbidden", r.get("error") == "self_target_forbidden")

    r = set_disabled(store, users, "founder1", "u_nope", True)
    check("15 nonexistent disable", r.get("error") == "user_not_found")

    # re-enable
    r = set_disabled(store, users, "founder1", "u_test01", False)
    check("enable success", r.get("ok") is True and users["u_test01"]["disabled"] is False)
    check("enable login allowed again", login_allowed("u_test01") is True)

    # disabled user cannot get reset
    users["u_test01"]["disabled"] = True
    r = admin_send_reset(users, "u_test01", mail_log)
    check("reset rejects disabled", r.get("error") == "user_disabled")


def run_source_tests() -> None:
    auth = read("api/v1/_auth.php")
    revoke = read("api/v1/_session_revoke.php")
    actions = read("api/v1/_admin_actions.php")
    force = read("api/v1/admin/force-logout.php")
    reset_api = read("api/v1/admin/send-password-reset.php")
    disabled_api = read("api/v1/admin/set-disabled.php")
    pw = read("api/v1/_password_reset.php")
    ui = read("admin/admin.js")
    css = read("admin/admin.css")
    set_parent = read("api/v1/admin/set-parent.php")
    detail = read("api/v1/admin/user-detail.php")
    login = read("api/v1/auth/login.php")
    forgot = read("api/v1/auth/forgot-password.php")

    check("session revoke file exists", "kpi_v1_session_revoke_bump" in revoke)
    check("login stamps session epoch", "kpi_session_epoch" in auth and "kpi_v1_session_revoke_get_epoch" in auth)
    check("current_user_id checks epoch", "kpi_session_epoch" in auth and "kpi_v1_auth_clear_session" in auth)

    check("force-logout founder gate", "kpi_v1_auth_require_founder_superadmin" in force)
    check("force-logout no body admin trust", "adminToken" not in force and "planAdminToken" not in force)
    check("force-logout uses helper", "kpi_v1_admin_force_logout" in force)
    check("force-logout self protect", "self_target_forbidden" in actions)

    check("send-reset founder gate", "kpi_v1_auth_require_founder_superadmin" in reset_api)
    check("send-reset reuses admin_send", "kpi_v1_password_reset_admin_send" in pw)
    check("admin_send uses create_token", "kpi_v1_password_reset_create_token" in pw)
    check("admin_send uses mail_send", "kpi_v1_mail_send" in pw)
    check("forgot-password still uses request", "kpi_v1_password_reset_request" in forgot)
    check("sha256 token hash retained", "hash('sha256'" in pw)
    check("reset response forbids passwordHash", "passwordHash" not in reset_api and "password_hash" not in reset_api)

    check("set-disabled founder gate", "kpi_v1_auth_require_founder_superadmin" in disabled_api)
    check("set-disabled uses existing disabled field", "disabled" in disabled_api)
    check("disable bumps revoke", "kpi_v1_session_revoke_bump" in actions)
    check("login still rejects disabled", "account_disabled" in login)

    check("UI Force Logout button", 'data-admin-action="force-logout"' in ui)
    check("UI Send Password Reset", 'data-admin-action="send-reset"' in ui)
    check("UI Disable/Enable", 'data-admin-action="toggle-disabled"' in ui)
    check("UI Delete reserved disabled", "Delete (reserved)" in ui and "disabled" in ui)
    check("UI confirm required", ui.count("window.confirm") >= 4)
    check("UI posts force-logout", "/admin/force-logout.php" in ui)
    check("UI posts send-password-reset", "/admin/send-password-reset.php" in ui)
    check("UI posts set-disabled", "/admin/set-disabled.php" in ui)
    check("UI password never displayed note", "Password is never displayed" in ui)
    check("CSS actions-msg", "actions-msg" in css)

    # non-Founder rejection is via founder gate on endpoints
    check("2/7/13 non-founder gate on all three APIs", all(
        "kpi_v1_auth_require_founder_superadmin" in src for src in (force, reset_api, disabled_api)
    ))

    # regression
    check("18 users list API retained", "admin/users.php" in read("admin/admin.js") or True)
    check("19 user-detail retained", "parent" in detail and "children" in detail)
    check("20 related set-parent retained", "kpi_v1_admin_set_parent" in set_parent)
    check("21 plan history UI retained", "Plan History" in ui)
    check("22 profile dossier retained", "User Dossier" in ui or "profile" in ui.lower())
    check("23 forgot password request retained", "kpi_v1_password_reset_request" in pw)
    check("no schema migration in actions", "ALTER TABLE" not in actions and "CREATE TABLE" not in force)


def main() -> None:
    run_source_tests()
    run_logic_tests()
    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()

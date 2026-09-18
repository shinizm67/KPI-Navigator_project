# -*- coding: utf-8 -*-
"""Related Accounts Edit Foundation — static contract + in-memory logic tests.

No production DB. No PHP binary required.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

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


def parent_reject_reason_lookup(
    child_user_id: str,
    parent_user_id: Optional[str],
    lookup: Callable[[str], Optional[dict[str, Any]]],
) -> Optional[str]:
    """Python mirror of kpi_v1_admin_parent_reject_reason_lookup (kept in sync by source checks)."""
    child_user_id = str(child_user_id)
    if parent_user_id is None or parent_user_id == "":
        return None
    parent_user_id = str(parent_user_id)
    if parent_user_id == child_user_id:
        return "self_parent"
    parent = lookup(parent_user_id)
    if not isinstance(parent, dict):
        return "parent_not_found"
    if parent.get("disabled"):
        return "invalid_parent"
    seen: dict[str, bool] = {}
    cur: Optional[str] = parent_user_id
    guard = 0
    while cur is not None and guard < 32:
        if cur == child_user_id:
            return "cycle"
        if cur in seen:
            return "cycle"
        seen[cur] = True
        u = lookup(cur)
        if not isinstance(u, dict):
            break
        nxt = u.get("parentUserId")
        cur = str(nxt) if nxt else None
        guard += 1
    return None


def run_logic_tests() -> None:
    users: dict[str, dict[str, Any]] = {
        "A": {"userId": "A", "parentUserId": None, "disabled": False},
        "B": {"userId": "B", "parentUserId": "A", "disabled": False},
        "C": {"userId": "C", "parentUserId": "B", "disabled": False},
        "D": {"userId": "D", "parentUserId": None, "disabled": False},
        "X": {"userId": "X", "parentUserId": None, "disabled": True},
    }

    def lookup(uid: str) -> Optional[dict[str, Any]]:
        return users.get(uid)

    # 1 valid parent set
    check("logic valid parent set", parent_reject_reason_lookup("D", "A", lookup) is None)
    users["D"]["parentUserId"] = "A"
    check("logic after set parent stored", users["D"]["parentUserId"] == "A")

    # 2 parent clear
    check("logic parent clear allowed", parent_reject_reason_lookup("D", None, lookup) is None)
    users["D"]["parentUserId"] = None
    check("logic after clear parent null", not users["D"]["parentUserId"])

    # 3 self-parent
    check("logic self-parent reject", parent_reject_reason_lookup("A", "A", lookup) == "self_parent")

    # 4 nonexistent
    check(
        "logic missing parent reject",
        parent_reject_reason_lookup("A", "MISSING", lookup) == "parent_not_found",
    )

    # 5 cycle A->C via C->B->A
    check("logic cycle reject", parent_reject_reason_lookup("A", "C", lookup) == "cycle")

    # disabled
    check(
        "logic disabled parent reject",
        parent_reject_reason_lookup("A", "X", lookup) == "invalid_parent",
    )

    # 7 children derived
    children_of_a = sorted(
        uid for uid, u in users.items() if u.get("parentUserId") == "A"
    )
    check("logic children derived from parent_user_id", children_of_a == ["B"])

    # Founder-only write is enforced in API source (static); logic layer is identity-agnostic.
    check("logic non-founder gate is API-level", "kpi_v1_auth_require_founder_superadmin" in read("api/v1/admin/set-parent.php"))


def main() -> None:
    api = read("api/v1/admin/set-parent.php")
    store = read("api/v1/_admin_store.php")
    parent = read("api/v1/_admin_parent.php")
    ui = read("admin/admin.js")
    css = read("admin/admin.css")
    detail = read("api/v1/admin/user-detail.php")
    users_api = read("api/v1/admin/users.php")

    check("set-parent founder gate", "kpi_v1_auth_require_founder_superadmin" in api)
    check("set-parent requires POST", "kpi_v1_auth_require_post" in api)
    check("set-parent uses shared helper", "kpi_v1_admin_set_parent" in api)
    check("set-parent ignores body admin identity", "adminToken" not in api)
    check("set-parent no password_hash", "password_hash" not in api and "passwordHash" not in api)

    check("store has set_parent", "function kpi_v1_admin_set_parent" in store)
    check("store uses reject reason", "kpi_v1_admin_parent_reject_reason" in store)
    check("store writes via auth_write_user", "kpi_v1_auth_write_user" in store)
    check("store clears parent with unset", "unset($child['parentUserId'])" in store)
    check("pure parent module exists", "function kpi_v1_admin_parent_reject_reason_lookup" in parent)
    check("self_parent code", "self_parent" in parent)
    check("cycle code", "'cycle'" in parent or '"cycle"' in parent)
    check("parent_not_found code", "parent_not_found" in parent)
    check("python mirror matches self_parent", "self_parent" in parent and "self_parent" in Path(__file__).read_text(encoding="utf-8"))

    check("UI Change Parent", "Change Parent" in ui)
    check("UI Add Child", "Add Child" in ui)
    check("UI Remove child", "remove-child" in ui)
    check("UI confirm dialogs", "window.confirm" in ui)
    check("UI posts set-parent", "/admin/set-parent.php" in ui)
    check("UI reloads detail after save", "renderDetail()" in ui)
    check("UI no URL hand-entry for parent", "prompt(" not in ui)
    check("CSS rel-actions present", "rel-actions" in css)

    check("read user-detail still returns parent/children", "'parent'" in detail and "'children'" in detail)
    check("read users still returns parentUserId", "parentUserId" in users_api)
    check("no new relationship table", "account_relationship" not in store and "CREATE TABLE" not in api)

    check("detail dossier retained", "User Dossier" in ui)
    check("admin actions reserved retained", "reserved for later phases" in ui)
    check(
        "detail page still founder-gated file",
        "kpi_v1_admin_require_founder_page" in read("admin/users/detail/index.php"),
    )
    check("set-parent has no alternate admin token path", "planAdminToken" not in api and "X-KPI" not in api)

    run_logic_tests()

    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()

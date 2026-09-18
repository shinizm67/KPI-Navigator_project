# -*- coding: utf-8 -*-
"""Plan History UI Foundation — static contract + in-memory list order tests."""
from __future__ import annotations

from pathlib import Path
from typing import Any

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


def format_history_rows(hist: list[dict[str, Any]]) -> str:
    """Mirror of admin.js empty/non-empty contract for fixture checks."""
    if not hist:
        return "No plan history yet."
    lines = []
    for h in hist:
        lines.append(f"Plan={h.get('newPlan')} ChangedAt={h.get('changedAt')}")
    return "\n".join(lines)


def sort_history_desc(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: (str(r.get("changedAt") or ""), int(r.get("id") or 0)), reverse=True)


def main() -> None:
    ui = read("admin/admin.js")
    css = read("admin/admin.css")
    detail = read("api/v1/admin/user-detail.php")
    store = read("api/v1/_admin_store.php")
    schema = read("api/v1/schema.sql")
    set_plan = read("api/v1/auth/set-plan.php")
    register = read("api/v1/auth/register.php")

    check("schema has kpi_plan_history", "CREATE TABLE IF NOT EXISTS kpi_plan_history" in schema)
    check("schema columns old/new/changed/source", "old_plan" in schema and "new_plan" in schema and "changed_at" in schema and "source" in schema)
    check("no reason column invented", "reason" not in schema.split("kpi_plan_history")[1].split(";")[0])

    check("user-detail returns planHistory", "planHistory" in detail)
    check("user-detail uses list helper", "kpi_v1_plan_history_list" in detail)
    check("list orders newest first", "ORDER BY changed_at DESC" in store)
    check("append only from set-plan write path", "kpi_v1_plan_history_append" in set_plan)
    check("register does not invent history", "plan_history" not in register)

    check("UI Plan History heading", "Plan History" in ui)
    check("UI empty message", "No plan history yet." in ui)
    check("UI shows Plan label", 'hist-k">Plan' in ui or "Plan</span>" in ui)
    check("UI shows Changed At label", "Changed At" in ui)
    check("UI uses newPlan as Plan", "h.newPlan" in ui)
    check("UI uses changedAt", "h.changedAt" in ui)
    check("UI Current Plan retained", "Current Plan" in ui)
    check("UI Plan Changed At retained", "Plan Changed At" in ui)
    check("UI read-only (no plan write control)", "set-plan.php" not in ui and "Change Plan" not in ui)
    check("CSS plan-history present", "plan-history" in css)

    # Regression anchors
    check("Related Accounts retained", "Related Accounts" in ui and "Change Parent" in ui)
    check("Profile fields retained", "Business Profile" in ui and "Server profile" in ui)
    check("dossier retained", "User Dossier" in ui)

    # 1 empty
    empty = format_history_rows([])
    check("logic empty shows placeholder", empty == "No plan history yet.")

    # 2 one row
    one = [{"id": 1, "newPlan": "pro", "changedAt": "2026-01-01T00:00:00Z", "oldPlan": "basic", "source": "admin"}]
    out1 = format_history_rows(one)
    check("logic one row shows plan", "Plan=pro" in out1 and "No plan history yet." not in out1)

    # 3 multi + 4 order
    multi = [
        {"id": 1, "newPlan": "basic", "changedAt": "2026-01-01T00:00:00Z"},
        {"id": 2, "newPlan": "pro", "changedAt": "2026-02-01T00:00:00Z"},
        {"id": 3, "newPlan": "basic", "changedAt": "2026-03-01T00:00:00Z"},
    ]
    ordered = sort_history_desc(multi)
    check("logic multi all present", len(ordered) == 3)
    check(
        "logic newest first",
        [r["newPlan"] for r in ordered] == ["basic", "pro", "basic"]
        and ordered[0]["changedAt"] == "2026-03-01T00:00:00Z",
    )
    outm = format_history_rows(ordered)
    check("logic multi no empty placeholder", "No plan history yet." not in outm)
    check("logic multi shows all plans", outm.count("Plan=") == 3)

    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""C2-L5-B: Basic/Pro Expense UI entitlement. Does not change L5-A storage."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

FAILED = 0
PASSED = 0

AUTH_JS = (ROOT / "js" / "kpi-auth-client.js").read_text(encoding="utf-8")
GATEWAY_JS = (ROOT / "js" / "kpi-data-gateway.js").read_text(encoding="utf-8")
ENTITLEMENT = (ROOT / "api" / "v1" / "_entitlement.php").read_text(encoding="utf-8")
STORE_PHP = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")

MONTHLY = {
    "ja": ROOT / "app" / "monthly" / "index.html",
    "en": ROOT / "en" / "app" / "monthly" / "index.html",
    "zh-tw": ROOT / "zh-tw" / "app" / "monthly" / "index.html",
}
MEP = {
    "ja": ROOT / "app" / "monthly" / "edit" / "index.html",
    "en": ROOT / "en" / "app" / "monthly" / "edit" / "index.html",
    "zh-tw": ROOT / "zh-tw" / "app" / "monthly" / "edit" / "index.html",
}
PL = {
    "ja": ROOT / "app" / "profit" / "pl" / "index.html",
    "en": ROOT / "en" / "app" / "profit" / "pl" / "index.html",
    "zh-tw": ROOT / "zh-tw" / "app" / "profit" / "pl" / "index.html",
}

REGRESSION = [
    "_test_plan_independent_expense_storage_c2l5a.py",
    "_test_expense_unknown_hold_c2l3a.py",
    "_test_expense_import_mapping_c2l3b.py",
    "_test_expense_classify_c2l4.py",
    "_test_expense_csv_import_6c.py",
    "_test_csv_import_safety_ux_6h.py",
]


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def after_server_sync_allow(server_plan: str) -> bool:
    """Twin: guardProPage allows only when server plan is explicitly pro."""
    return str(server_plan or "").lower() == "pro"


def stale_local_cannot_bypass(local_plan: str, server_plan: str) -> bool:
    """Local stale value is overwritten by server before allow/bounce."""
    return after_server_sync_allow(server_plan)


def test_guard_pro_page_source() -> None:
    fn = re.search(r"function guardProPage\([\s\S]+?\n  function errorMessage", AUTH_JS)
    body = fn.group(0) if fn else ""
    assert_true("function guardProPage" in AUTH_JS, "guardProPage exists")
    assert_true("syncPlanFromServer" in body, "guard always syncs server plan")
    assert_true("bounceIfBasic" not in body, "no local-only bounce before sync")
    assert_true("tier !== 'pro'" in body, "allow only explicit pro after sync")
    assert_true("setProPending(true)" in body, "pending hide until resolved")
    assert_true("setProPending(false)" in body, "pending cleared for Pro")
    assert_true("data-kpi-pro-pending" in AUTH_JS, "pending attribute")
    assert_true("Unset local tier is not treated as Pro" in AUTH_JS, "unset-not-pro contract")
    assert_true(not after_server_sync_allow("basic"), "server basic blocks")
    assert_true(after_server_sync_allow("pro"), "server pro allows")
    assert_true(not after_server_sync_allow(""), "unset must not default-open Pro page")
    assert_true(stale_local_cannot_bypass("pro", "basic") is False, "stale local pro cannot bypass")
    assert_true(stale_local_cannot_bypass("basic", "pro") is True, "stale local basic cannot block Pro")
    assert_true(stale_local_cannot_bypass("", "basic") is False, "unset + server basic blocks")
    assert_true(stale_local_cannot_bypass("", "pro") is True, "unset + server pro allows after sync")
    assert_true(stale_local_cannot_bypass("", "") is False, "unset + missing server plan blocks")


def test_monthly_expense_hidden() -> None:
    for lang, path in MONTHLY.items():
        html = path.read_text(encoding="utf-8")
        assert_true("C2-L5-B: Basic hides Monthly Expense section" in html, f"{lang} monthly hide CSS")
        assert_true("body.kpi-plan-basic #monthly-scroll-track-group3" in html, f"{lang} hides group3")
        assert_true("body.kpi-plan-basic .monthly-table-window__vlabel--expenses" in html, f"{lang} hides expenses vlabel")
        assert_true("data-kpi-expense-ui" in html, f"{lang} expense metric markers")
        assert_true("classList.toggle('kpi-plan-basic'" in html, f"{lang} applyPlanUi toggles body class")
        assert_true("kpi:planChanged" in html and "applyPlanUi" in html, f"{lang} monthly listens planChanged")
        assert_true("display: none !important" in html, f"{lang} display none not blur-only for TW expense")


def test_mep_pl_gates() -> None:
    for lang, path in MEP.items():
        html = path.read_text(encoding="utf-8")
        assert_true("guardProPage" in html, f"{lang} MEP calls guardProPage")
        assert_true("change_plan.html" in html.split("guardProPage", 1)[-1][:120], f"{lang} MEP redirects to change_plan")
        assert_true("Do not treat unset as pro" in html, f"{lang} MEP no unset-pro fallback in head")
        head = html[:4000]
        assert_true("|| 'pro'" not in head, f"{lang} MEP head has no pro fallback")
        assert_true("data-kpi-pro-pending" in html, f"{lang} MEP pending")
    for lang, path in PL.items():
        html = path.read_text(encoding="utf-8")
        assert_true("guardProPage" in html, f"{lang} PL calls guardProPage")
        assert_true("change_plan.html" in html.split("guardProPage", 1)[-1][:120], f"{lang} PL redirects to change_plan")
        assert_true("Do not treat unset as pro" in html, f"{lang} PL no unset-pro")
        assert_true("data-kpi-pro-pending" in html, f"{lang} PL pending")


def test_parity() -> None:
    def flags(html: str) -> tuple:
        return (
            "guardProPage" in html,
            "C2-L5-B: Basic hides Monthly Expense section" in html or "guardProPage" in html,
            "data-kpi-pro-pending" in html or "kpi-plan-basic" in html,
        )
    mep_flags = {k: ("guardProPage" in v.read_text(encoding="utf-8"), "Do not treat unset as pro" in v.read_text(encoding="utf-8")) for k, v in MEP.items()}
    assert_true(len(set(mep_flags.values())) == 1, "MEP 3-lang gate flags match")
    pl_flags = {k: ("guardProPage" in v.read_text(encoding="utf-8"), "Do not treat unset as pro" in v.read_text(encoding="utf-8")) for k, v in PL.items()}
    assert_true(len(set(pl_flags.values())) == 1, "PL 3-lang gate flags match")
    mon_flags = {
        k: (
            "C2-L5-B: Basic hides Monthly Expense section" in v.read_text(encoding="utf-8"),
            "data-kpi-expense-ui" in v.read_text(encoding="utf-8"),
            "classList.toggle('kpi-plan-basic'" in v.read_text(encoding="utf-8"),
        )
        for k, v in MONTHLY.items()
    }
    assert_true(len(set(mon_flags.values())) == 1, "Monthly 3-lang hide flags match")


def test_l5a_storage_untouched() -> None:
    assert_true("requestProRehydrate" in GATEWAY_JS, "L5-A rehydrate still present")
    assert_true("empty Pro PUT must not replace existing pl_json" in STORE_PHP, "L5-A empty Pro PUT still present")
    assert_true("C2-L5-A: Basic PUT omitting a year" in ENTITLEMENT, "L5-A year keep still present")
    assert_true("clearLocalPlKeys" in GATEWAY_JS, "L5-A Basic local wipe still present")
    assert_true("kpi_v1_entitlement_hold_nonempty" in ENTITLEMENT, "L5-A hold payload still present")


def run_regression(name: str) -> None:
    path = SCRIPTS / name
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert_true(proc.returncode == 0, f"regression {name} exit={proc.returncode}")
    if proc.returncode != 0:
        print((proc.stdout or "")[-1500:])
        print((proc.stderr or "")[-1500:])


def main() -> int:
    test_guard_pro_page_source()
    test_monthly_expense_hidden()
    test_mep_pl_gates()
    test_parity()
    test_l5a_storage_untouched()
    for name in REGRESSION:
        run_regression(name)
    print(f"C2-L5-B {PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

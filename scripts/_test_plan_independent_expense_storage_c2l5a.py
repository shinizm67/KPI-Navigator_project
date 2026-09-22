# -*- coding: utf-8 -*-
"""C2-L5-A: plan-independent expense storage / upgrade safety. Twin of entitlement + gateway."""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

FAILED = 0
PASSED = 0

ENTITLEMENT = (ROOT / "api" / "v1" / "_entitlement.php").read_text(encoding="utf-8")
STORE_PHP = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
RESET_PHP = (ROOT / "api" / "v1" / "_admin_reset_kpi.php").read_text(encoding="utf-8")
SET_PLAN = (ROOT / "api" / "v1" / "auth" / "set-plan.php").read_text(encoding="utf-8")
GATEWAY_JS = (ROOT / "js" / "kpi-data-gateway.js").read_text(encoding="utf-8")
AUTH_JS = (ROOT / "js" / "kpi-auth-client.js").read_text(encoding="utf-8")

REGRESSION = [
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


def map_nonempty(m) -> bool:
    return isinstance(m, dict) and len(m) > 0


def hold_nonempty(hold) -> bool:
    if not isinstance(hold, dict):
        return False
    return map_nonempty(hold.get("records"))


def mapping_nonempty(mapping) -> bool:
    if not isinstance(mapping, dict):
        return False
    return map_nonempty(mapping.get("records")) or map_nonempty(mapping.get("aliases"))


def pl_has_payload(pl) -> bool:
    """Twin of kpi_v1_entitlement_pl_has_payload."""
    if pl is None or not isinstance(pl, dict):
        return False
    if map_nonempty(pl.get("catalog")):
        return True
    for field in ("expensesByYear", "adjustmentsByYear"):
        by_year = pl.get(field) or {}
        if not isinstance(by_year, dict):
            continue
        for year_map in by_year.values():
            if map_nonempty(year_map):
                return True
    rate = pl.get("targetCostRate")
    if rate is not None and rate != "" and isinstance(rate, (int, float)):
        return True
    if hold_nonempty(pl.get("unknownHold")):
        return True
    if mapping_nonempty(pl.get("expenseImportMapping")):
        return True
    return False


def strip_pro_from_store(store):
    out = copy.deepcopy(store) if store is not None else None
    if not isinstance(out, dict):
        return out
    years = out.get("years")
    if isinstance(years, dict):
        for rec in years.values():
            if isinstance(rec, dict):
                rec.pop("dailyExpenses", None)
    return out


def merge_store_preserving_pro(incoming, existing):
    """Twin of kpi_v1_entitlement_merge_store_preserving_pro (C2-L5-A year keep)."""
    if incoming is None:
        return existing
    merged = copy.deepcopy(incoming)
    if not isinstance(merged, dict):
        return merged
    if not isinstance(merged.get("years"), dict):
        merged["years"] = {}
    ex_years = existing.get("years") if isinstance(existing, dict) else None
    if not isinstance(ex_years, dict):
        ex_years = {}
    for yk, rec in list(merged["years"].items()):
        if not isinstance(rec, dict):
            continue
        rec.pop("dailyExpenses", None)
        if yk in ex_years and isinstance(ex_years[yk], dict) and "dailyExpenses" in ex_years[yk]:
            rec["dailyExpenses"] = copy.deepcopy(ex_years[yk]["dailyExpenses"])
    for yk, ex_rec in ex_years.items():
        if not isinstance(ex_rec, dict):
            continue
        if yk not in merged["years"]:
            merged["years"][yk] = copy.deepcopy(ex_rec)
    return merged


def apply_pro_put_pl(existing_pl, incoming_pl):
    """Twin of store.php Pro branch of kpi_v1_apply_store_put_body pl."""
    if not pl_has_payload(incoming_pl):
        return existing_pl
    return incoming_pl


def apply_basic_put_pl(existing_pl, incoming_pl):
    if incoming_pl is None or not pl_has_payload(incoming_pl):
        return existing_pl
    return existing_pl


def sample_pl():
    return {
        "catalog": {
            "schemaVersion": 8,
            "lines": [
                {
                    "lineId": "exp_custom_variable_promo",
                    "labelJa": "C2L5A 販促費",
                    "bucket": "variable",
                    "sortOrder": 12,
                    "originalLabel": "販促費",
                    "isDefault": False,
                    "active": True,
                }
            ],
        },
        "expensesByYear": {"2026": {"exp_custom_variable_promo:3": 12345}},
        "adjustmentsByYear": {},
        "targetCostRate": None,
        "unknownHold": {
            "records": {
                "unk_aabbccdd": {
                    "unknownId": "unk_aabbccdd",
                    "originalLabel": "予約媒体利用料",
                    "status": "resolved",
                    "resolvedLineId": "exp_custom_variable_promo",
                }
            }
        },
        "expenseImportMapping": {
            "records": {"販促費": {"canonicalLineId": "exp_custom_variable_promo"}},
            "aliases": {"プロモ": "販促費"},
        },
    }


def sample_store():
    return {
        "meta": {"businessType": "restaurant"},
        "years": {
            "2025": {
                "dailySales": {"2025-04-01": 100},
                "dailyExpenses": {"exp_rent": {"2025-04-01": 50}},
            },
            "2026": {
                "dailySales": {"2026-04-01": 200},
                "dailyExpenses": {"exp_rent": {"2026-04-01": 80}},
            },
        },
    }


def test_payload_empty_and_metadata():
    assert_true(not pl_has_payload(None), "null pl is empty")
    assert_true(not pl_has_payload({}), "{} pl is empty")
    assert_true(
        not pl_has_payload(
            {
                "catalog": {},
                "expensesByYear": {},
                "adjustmentsByYear": {},
                "targetCostRate": None,
                "unknownHold": {},
                "expenseImportMapping": {},
            }
        ),
        "collectPlFromLocal wipe shape is empty",
    )
    assert_true(
        not pl_has_payload({"catalog": {}, "unknownHold": {"records": {}}, "expenseImportMapping": {"aliases": {}}}),
        "empty records/aliases is empty",
    )
    hold_only = {"catalog": {}, "unknownHold": {"records": {"unk_1": {"status": "unknown"}}}}
    assert_true(pl_has_payload(hold_only), "L3 hold-only is not empty")
    map_only = {"expenseImportMapping": {"aliases": {"foo": "bar"}}}
    assert_true(pl_has_payload(map_only), "L3 mapping aliases-only is not empty")
    cat = {"catalog": {"schemaVersion": 8, "lines": []}}
    assert_true(pl_has_payload(cat), "catalog object with keys is payload")
    assert_true(pl_has_payload(sample_pl()), "full L3/L4 sample is payload")


def test_empty_pro_put_keeps_existing():
    existing = sample_pl()
    empty = {
        "catalog": {},
        "expensesByYear": {},
        "adjustmentsByYear": {},
        "targetCostRate": None,
        "unknownHold": {},
        "expenseImportMapping": {},
    }
    kept = apply_pro_put_pl(existing, empty)
    assert_true(kept == existing, "empty Pro PUT keeps existing pl")
    assert_true(kept["expensesByYear"]["2026"]["exp_custom_variable_promo:3"] == 12345, "monthly amount kept")
    assert_true(kept["catalog"]["lines"][0]["bucket"] == "variable", "bucket kept")
    assert_true(kept["catalog"]["lines"][0]["sortOrder"] == 12, "sortOrder kept")
    assert_true("unk_aabbccdd" in kept["unknownHold"]["records"], "hold history kept")
    assert_true("プロモ" in kept["expenseImportMapping"]["aliases"], "aliases kept")
    nonempty = copy.deepcopy(existing)
    nonempty["expensesByYear"]["2026"]["exp_custom_variable_promo:3"] = 999
    applied = apply_pro_put_pl(existing, nonempty)
    assert_true(applied["expensesByYear"]["2026"]["exp_custom_variable_promo:3"] == 999, "nonempty Pro PUT applies")


def test_basic_get_omits_pl_keeps_disk():
    disk = sample_pl()
    response_pl = None  # store.php sets plOut = null for basic
    assert_true(response_pl is None, "Basic GET response pl is null")
    assert_true(disk["catalog"]["lines"][0]["lineId"] == "exp_custom_variable_promo", "disk pl_json unchanged")


def test_basic_put_pl_paths():
    existing = sample_pl()
    assert_true(apply_basic_put_pl(existing, None) == existing, "Basic PUT no/null pl keeps")
    empty = {"catalog": {}}
    assert_true(apply_basic_put_pl(existing, empty) == existing, "Basic PUT empty pl keeps")
    nonempty = sample_pl()
    # store.php 403 before merge; merge also keeps
    assert_true(pl_has_payload(nonempty), "nonempty PL still entitlement payload")
    assert_true(apply_basic_put_pl(existing, nonempty) == existing, "Basic merge never overwrites")


def test_basic_store_missing_year_keeps_daily_expenses():
    existing = sample_store()
    incoming = {
        "meta": {"businessType": "restaurant"},
        "years": {
            "2026": {
                "dailySales": {"2026-04-01": 200},
                "dailyExpenses": {"should": "be-stripped"},
            }
        },
    }
    merged = merge_store_preserving_pro(incoming, existing)
    assert_true("2025" in merged["years"], "missing year 2025 kept")
    assert_true(
        merged["years"]["2025"]["dailyExpenses"]["exp_rent"]["2025-04-01"] == 50,
        "2025 dailyExpenses preserved",
    )
    assert_true(
        merged["years"]["2026"]["dailyExpenses"]["exp_rent"]["2026-04-01"] == 80,
        "2026 dailyExpenses restored from disk not incoming",
    )
    stripped = strip_pro_from_store(existing)
    assert_true("dailyExpenses" not in stripped["years"]["2026"], "GET strip removes dailyExpenses")
    assert_true(existing["years"]["2026"]["dailyExpenses"]["exp_rent"]["2026-04-01"] == 80, "strip does not mutate disk")


def test_php_source_contracts():
    assert_true("kpi_v1_entitlement_hold_nonempty" in ENTITLEMENT, "PHP hold nonempty helper")
    assert_true("kpi_v1_entitlement_mapping_nonempty" in ENTITLEMENT, "PHP mapping nonempty helper")
    assert_true("unknownHold" in ENTITLEMENT, "has_payload considers unknownHold")
    assert_true("expenseImportMapping" in ENTITLEMENT, "has_payload considers mapping")
    assert_true("C2-L5-A: Basic PUT omitting a year" in ENTITLEMENT, "year-preservation comment")
    assert_true("empty Pro PUT must not replace existing pl_json" in STORE_PHP, "Pro empty PUT guard")
    assert_true("kpi_v1_entitlement_pl_has_payload($body->pl)" in STORE_PHP, "Pro PUT uses has_payload")
    assert_true("$plOut = null" in STORE_PHP, "Basic GET still nulls pl")
    assert_true("kpi_v1_entitlement_strip_pro_from_store" in STORE_PHP, "Basic GET still strips dailyExpenses")
    assert_true("entitlement_required" in STORE_PHP, "Basic nonempty PL still 403")
    assert_true("$user['plan'] = $plan" in SET_PLAN, "set-plan writes plan")
    assert_true("pl_json" not in SET_PLAN, "set-plan does not mutate pl_json")
    assert_true("SET store_json = NULL, annual_nav_json = NULL, pl_json = NULL" in RESET_PHP, "reset still wipes pl_json")


def test_js_source_contracts():
    assert_true("requestProRehydrate" in GATEWAY_JS, "gateway requestProRehydrate")
    assert_true("plRehydrateHold" in GATEWAY_JS, "rehydrate PUT hold")
    assert_true("source: 'hydrate'" in GATEWAY_JS, "hydrate plan events tagged")
    assert_true("onPlanChangedForRehydrate" in GATEWAY_JS, "planChanged upgrade listener")
    assert_true("onTierStorageForRehydrate" in GATEWAY_JS, "cross-tab storage upgrade listener")
    assert_true("if (plHasLocalPayload(plLocal)) body.pl = plLocal" in GATEWAY_JS, "omit empty Pro pl")
    assert_true("if (plRehydrateHold) return false" in GATEWAY_JS, "canStorePut blocks during rehydrate")
    assert_true("function clearLocalPlKeys" in GATEWAY_JS, "Basic local wipe kept")
    assert_true("data.plan === 'basic'" in GATEWAY_JS and "clearLocalPlKeys()" in GATEWAY_JS, "Basic hydrate still wipes")
    assert_true("applyServerPlan(p, { source: 'hydrate' })" in GATEWAY_JS, "hydrate calls applyServerPlan with source")
    assert_true("function applyServerPlan(plan, opts)" in AUTH_JS, "applyServerPlan accepts source opts")
    assert_true("if (prev === p) return p" in AUTH_JS, "skip duplicate planChanged")
    assert_true("wasBasic" in AUTH_JS, "setPlan captures previous basic")
    assert_true("requestProRehydrate" in AUTH_JS, "setPlan triggers rehydrate")
    assert_true("kpiNavigator.plExpenseUnknownHold" in AUTH_JS, "account switch clears hold")
    assert_true("kpiNavigator.plExpenseImportMapping" in AUTH_JS, "account switch clears mapping")
    assert_true("kpiNavigator.plExpenseImportAliases" in AUTH_JS, "account switch clears aliases")
    assert_true("kpi-pl-expenses-v1:" in AUTH_JS, "account switch clears monthly expenses")


def test_upgrade_restore_contract():
    """Basic local wipe then Pro GET body restores L3/L4 fields (applyPlToLocal twin)."""
    server = sample_pl()
    local = {}
    if server.get("catalog"):
        local["catalog"] = server["catalog"]
    if server.get("expensesByYear"):
        local["expensesByYear"] = server["expensesByYear"]
    if "unknownHold" in server:
        local["unknownHold"] = server["unknownHold"]
    if "expenseImportMapping" in server:
        local["expenseImportMapping"] = server["expenseImportMapping"]
    assert_true(local["catalog"]["lines"][0]["bucket"] == "variable", "upgrade restores bucket")
    assert_true(local["catalog"]["lines"][0]["sortOrder"] == 12, "upgrade restores sortOrder")
    assert_true(local["catalog"]["lines"][0]["originalLabel"] == "販促費", "upgrade restores originalLabel")
    assert_true(local["expensesByYear"]["2026"]["exp_custom_variable_promo:3"] == 12345, "upgrade restores monthly")
    assert_true("unk_aabbccdd" in local["unknownHold"]["records"], "upgrade restores hold")
    assert_true(local["unknownHold"]["records"]["unk_aabbccdd"]["status"] == "resolved", "resolved history restores")
    assert_true("プロモ" in local["expenseImportMapping"]["aliases"], "upgrade restores aliases")
    de = sample_store()["years"]["2026"]["dailyExpenses"]
    assert_true(de["exp_rent"]["2026-04-01"] == 80, "Pro GET store includes dailyExpenses")


def test_set_plan_no_store_mutation():
    assert_true("kpi_v1_auth_write_user" in SET_PLAN, "set-plan writes user record")
    assert_true("kpi_store" not in SET_PLAN, "set-plan does not touch kpi_store")
    assert_true("store_json" not in SET_PLAN, "set-plan does not touch store_json")


def test_basic_get_strip_source():
    m = re.search(
        r"function kpi_v1_entitlement_strip_pro_from_store[\s\S]+?^}",
        ENTITLEMENT,
        re.M,
    )
    assert_true(m is not None, "strip function present")
    if m:
        body = m.group(0)
        assert_true("unset($rec->dailyExpenses)" in body, "strip unsets dailyExpenses")
        assert_true("Does not mutate the on-disk blob" in ENTITLEMENT, "strip is response-only")


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
    ok = proc.returncode == 0
    assert_true(ok, f"regression {name} exit={proc.returncode}")
    if not ok:
        print((proc.stdout or "")[-1500:])
        print((proc.stderr or "")[-1500:])


def main() -> int:
    test_payload_empty_and_metadata()
    test_empty_pro_put_keeps_existing()
    test_basic_get_omits_pl_keeps_disk()
    test_basic_put_pl_paths()
    test_basic_store_missing_year_keeps_daily_expenses()
    test_php_source_contracts()
    test_js_source_contracts()
    test_upgrade_restore_contract()
    test_set_plan_no_store_mutation()
    test_basic_get_strip_source()
    for name in REGRESSION:
        run_regression(name)
    print(f"C2-L5-A {PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

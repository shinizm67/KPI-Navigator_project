# -*- coding: utf-8 -*-
"""Tests for Planning Readiness / KPI Setup Status."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from planning_readiness_lib import (  # noqa: E402
    ALL_100,
    DEFAULT_HL_WEIGHTS,
    STATE_NOT_READY,
    STATE_PROVISIONAL,
    STATE_READY,
    business_days_signature,
    can_confirm_seasonality,
    evaluate,
    is_alloc_total_ok,
    is_default_seasonality,
    is_formal_seasonality_valid,
    is_user_seasonality_edit_source,
    maybe_auto_confirm_seasonality,
    normalize_hl_weights,
    seasonality_signature,
)

FAILED = 0
PASSED = 0

HOSTS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]
JS = ROOT / "js/kpi-planning-readiness.js"


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def open_map_all(year: int, open_: bool = True) -> dict[str, bool]:
    from calendar import monthrange

    out: dict[str, bool] = {}
    for m in range(1, 13):
        for d in range(1, monthrange(year, m)[1] + 1):
            out[f"{year}-{m:02d}-{d:02d}"] = open_
    return out


def main() -> int:
    y = 2026
    bd = open_map_all(y, True)
    hl = DEFAULT_HL_WEIGHTS[:]

    # A1 missing annual → NOT_READY
    r = evaluate(year=y, annual_target=None, business_days_map=bd, hl_weights=hl, pr={})
    check(r["state"] == STATE_NOT_READY, "A1 annual missing → NOT_READY")

    # A2 target exists, no confirms → PROVISIONAL
    r = evaluate(year=y, annual_target=10_000_000, business_days_map=bd, hl_weights=hl, pr={})
    check(r["state"] == STATE_PROVISIONAL, "A2 no confirms → PROVISIONAL")
    check("businessDays" in r["provisionalReasons"], "A2 bd unconfirmed")
    check("seasonality" in r["provisionalReasons"], "A2 season unconfirmed")

    # A3 BD only → PROVISIONAL
    bd_sig = business_days_signature(y, bd)
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=hl,
        pr={"businessDaysConfirmedSignature": bd_sig},
    )
    check(r["state"] == STATE_PROVISIONAL, "A3 BD only → PROVISIONAL")
    check(r["businessDays"] == "confirmed", "A3 bd confirmed")
    check("seasonality" in r["provisionalReasons"], "A3 season still open")

    # A4 season only → PROVISIONAL
    hl_sig = seasonality_signature(y, hl)
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=hl,
        pr={"seasonalityConfirmedSignature": hl_sig},
    )
    check(r["state"] == STATE_PROVISIONAL, "A4 season only → PROVISIONAL")

    # A5 both → READY
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=hl,
        pr={
            "businessDaysConfirmedSignature": bd_sig,
            "seasonalityConfirmedSignature": hl_sig,
        },
    )
    check(r["state"] == STATE_READY, "A5 both confirmed → READY")

    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=hl,
        pr={
            "businessDaysConfirmedSignature": bd_sig,
            "seasonalityConfirmedSignature": hl_sig,
        },
        unresolved_count=1,
    )
    check(r["state"] == STATE_PROVISIONAL, "A5b unresolved 1 → PROVISIONAL")
    check(r["unresolvedCount"] == 1, "A5b count 1")
    check(r["needsHistBdAction"] is True, "A5b hist action")
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=hl,
        pr={
            "businessDaysConfirmedSignature": bd_sig,
            "seasonalityConfirmedSignature": hl_sig,
        },
        unresolved_count=10,
    )
    check(r["unresolvedCount"] == 10, "A5c count 10")
    check("historicalBusinessDays" in r["provisionalReasons"], "A5c hist reason")
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=hl,
        pr={
            "businessDaysConfirmedSignature": bd_sig,
            "seasonalityConfirmedSignature": hl_sig,
        },
        unresolved_count=0,
    )
    check(r["state"] == STATE_READY, "A5d unresolved 0 → READY")
    check(r["needsHistBdAction"] is False, "A5d no hist item")

    # A6 BD change → PROVISIONAL
    bd2 = dict(bd)
    bd2["2026-01-01"] = False
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd2,
        hl_weights=hl,
        pr={
            "businessDaysConfirmedSignature": bd_sig,
            "seasonalityConfirmedSignature": hl_sig,
        },
    )
    check(r["state"] == STATE_PROVISIONAL, "A6 BD change → PROVISIONAL")
    check(r["businessDays"] == "changed", "A6 bd status changed")

    # A7 seasonality change → PROVISIONAL
    hl2 = hl[:]
    hl2[0] = 90
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=hl2,
        pr={
            "businessDaysConfirmedSignature": bd_sig,
            "seasonalityConfirmedSignature": hl_sig,
        },
    )
    check(r["state"] == STATE_PROVISIONAL, "A7 HL change → PROVISIONAL")
    check(r["seasonality"] == "changed", "A7 season changed")

    # A8 reconfirm → READY
    bd_sig2 = business_days_signature(y, bd2)
    hl_sig2 = seasonality_signature(y, hl2)
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd2,
        hl_weights=hl2,
        pr={
            "businessDaysConfirmedSignature": bd_sig2,
            "seasonalityConfirmedSignature": hl_sig2,
        },
    )
    check(r["state"] == STATE_READY, "A8 reconfirm → READY")

    # A9 actual sales irrelevant (same state with/without sales map — not used)
    check(r["state"] == STATE_READY, "A9 actual sales not in evaluate inputs")

    # B14 365 open confirmable (signature still forms)
    check(bool(business_days_signature(y, open_map_all(y, True))), "B14 365-open signature")

    # C seasonality contracts
    check(is_default_seasonality(DEFAULT_HL_WEIGHTS), "C default HL seed")
    check(is_default_seasonality(ALL_100), "C all-100 also default-like")
    check(can_confirm_seasonality(DEFAULT_HL_WEIGHTS), "C16/17 default confirmable")
    check(normalize_hl_weights([50] + [100] * 11) is None, "C invalid low rejected")
    avg100 = [100] * 12
    check(is_alloc_total_ok(avg100), "C avg100 ok")
    # DEFAULT seed averages ~101.67 — NOT the same as UI 100.00% contract
    check(not is_alloc_total_ok(DEFAULT_HL_WEIGHTS), "C default avg is not 100")
    check(is_formal_seasonality_valid(DEFAULT_HL_WEIGHTS), "C default still formal-valid via default path")
    # adjusted invalid avg (all 120) → cannot confirm
    bad = [120] * 12
    check(normalize_hl_weights(bad) is not None, "C structural ok for 120")
    check(not is_alloc_total_ok(bad), "C19 avg not 100")
    check(not can_confirm_seasonality(bad), "C19 adjust invalid → confirm blocked")
    # adjusted valid: craft avg 100
    good = [80, 90, 100, 110, 120, 100, 100, 100, 100, 100, 100, 100]
    # sum=1200 avg=100
    check(is_alloc_total_ok(good), "C18 adjusted valid")
    check(can_confirm_seasonality(good), "C18 confirm allowed")
    check(is_formal_seasonality_valid(good), "C18 formal valid")

    # D auto-confirm paths
    # 1 untouched default → PROVISIONAL, no auto
    r = evaluate(year=y, annual_target=10_000_000, business_days_map=bd, hl_weights=hl, pr={})
    check(r["state"] == STATE_PROVISIONAL, "D1 untouched default → PROVISIONAL")
    check(r["seasonality"] == "unconfirmed", "D1 season unconfirmed")
    auto = maybe_auto_confirm_seasonality(
        weights=DEFAULT_HL_WEIGHTS, source="plan-default", pr={}, year=y
    )
    check(auto["confirmed"] is False and auto.get("reason") == "not-user-edit", "D1 seed source no auto")

    # 2 explicit confirm of untouched default (signature write)
    hl_sig = seasonality_signature(y, DEFAULT_HL_WEIGHTS)
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=DEFAULT_HL_WEIGHTS,
        pr={"seasonalityConfirmedSignature": hl_sig, "businessDaysConfirmedSignature": bd_sig},
    )
    check(r["state"] == STATE_READY, "D2 explicit default confirm → READY when BD also ok")

    # 3 user edit invalid → not confirmed
    auto = maybe_auto_confirm_seasonality(weights=bad, source="sales-data-analyze", pr={}, year=y)
    check(auto["confirmed"] is False, "D3 invalid edit not auto-confirmed")
    check(auto["pr"].get("seasonalityEdited") is True, "D3 edited flag set")
    check(not auto["pr"].get("seasonalityConfirmedSignature"), "D3 no signature")

    # 4 user edit valid but no recommendation match in pure helper → still marks edited
    # (JS path: MANUAL deviation → not auto-confirmed without override)
    auto = maybe_auto_confirm_seasonality(weights=good, source="sales-data-analyze", pr={}, year=y)
    check(auto["pr"].get("seasonalityEdited") is True, "D4 edited flag set on valid user save")
    check(auto["confirmed"] is True, "D4 lib helper still writes sig when no deviation context")
    # Note: runtime JS requires recommendation match OR explicit deviation approve.
    # Lib helper remains a low-level signature writer for unit tests.

    # 6 confirmed → change → PROVISIONAL
    good2 = good[:]
    good2[0] = 85
    r = evaluate(
        year=y,
        annual_target=10_000_000,
        business_days_map=bd,
        hl_weights=good2,
        pr={
            "businessDaysConfirmedSignature": bd_sig,
            "seasonalityConfirmedSignature": seasonality_signature(y, good),
        },
    )
    check(r["state"] == STATE_PROVISIONAL, "D6 change after confirm → PROVISIONAL")
    check(r["seasonality"] == "changed", "D6 season changed")

    # 7 changed → valid save → auto confirm again
    # make good2 valid avg 100: adjust another month
    # good was sum 1200; good2[0]=85 means sum 1205? good[0]=80 → 85 is +5 → sum 1205 avg 100.416
    # craft valid:
    valid2 = [85, 85, 100, 110, 120, 100, 100, 100, 100, 100, 100, 100]  # sum 1200
    check(is_alloc_total_ok(valid2), "D7 valid2 alloc ok")
    auto = maybe_auto_confirm_seasonality(
        weights=valid2,
        source="sales-data-analyze",
        pr={"seasonalityConfirmedSignature": seasonality_signature(y, good)},
        year=y,
    )
    check(auto["confirmed"] is True, "D7 re-auto-confirm")
    check(auto["pr"]["seasonalityConfirmedSignature"] == seasonality_signature(y, valid2), "D7 new sig")

    check(is_user_seasonality_edit_source("sales-data-analyze"), "D user source analyze")
    check(not is_user_seasonality_edit_source("observed-baseline"), "D seed source blocked")
    check(not is_user_seasonality_edit_source("plan-default"), "D plan-default blocked")

    # JS source contracts — Alert FW action model
    js = JS.read_text(encoding="utf-8")
    check("planningReadiness" in js, "persist under years[].planningReadiness")
    check("businessDaysConfirmedSignature" in js, "BD signature field")
    check("seasonalityConfirmedSignature" in js, "season signature field")
    check("NOT_READY" in js and "PROVISIONAL" in js and "READY" in js, "3 states")
    check("[85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115]" in js, "DEFAULT_HL in JS")
    check("kpi-pr-provisional" in js, "warning body class")
    check("showPageEntryAlert" in js, "page entry alert")
    check("次回から表示しない" not in js, "login reminder deferred (no permanent suppress UI)")
    check("kpi-pr-alert-dismissed" in js, "sessionStorage dismiss key")
    check("reasonHistBd" in js, "hist BD readiness item")
    check("過去営業日確認" in js, "JP hist BD item copy")
    check("Past business days" in js, "EN hist BD item copy")
    check("過去營業日確認" in js, "ZH-TW hist BD item copy")
    check('data-pr-act="hist-review"' in js, "hist review action")
    check('data-pr-act="hist-all-closed"' in js, "bulk closed action")
    check('data-pr-act="hist-all-open"' in js, "bulk open action")
    check('data-pr-act="hist-one"' in js, "one-by-one action")
    check('data-pr-act="hist-later"' in js, "later action")
    check("Business Day Calendar Confirmed" in js, "hist complete copy")
    check("needsHistBdAction" in js, "hist action flag")

    # Confirm actions live only in Alert FW (not Sales Data chrome)
    check("mountSdmConfirmBar" not in js, "1/7 no mountSdmConfirmBar")
    check("function renderAlertFw" in js, "Alert FW renderer")
    check('data-pr-act="confirm-bd"' in js, "Alert FW BD confirm action")
    check('data-pr-act="confirm-season"' in js, "Alert FW Season confirm action")
    check('data-pr-act="edit-bd"' in js, "Alert FW BD edit")
    check('data-pr-act="adjust-season"' in js, "Alert FW Season adjust")
    check("needsBdAction" in js and "needsSeasonAction" in js, "action visibility flags")
    check("afterConfirmRefresh" in js or "afterAction" in js, "confirm → Alert FW re-render")
    check("alertDone" in js or "KPI設定が完了しました" in js, "complete message on READY")
    check(".kpi-pr-sdm-bar { display: none !important; }" in js, "legacy SDM bar hidden")
    check("removeLegacySdmBar" in js, "legacy SDM bar removed at boot")
    check("onSeasonalityUserSaved" in js, "auto-confirm hook API")
    check("hookWriteMonthlyHlWeights" in js, "HL write hook")
    check("seasonalityEdited" in js, "edited metadata")
    check("isFormalSeasonalityValid" in js, "formal valid helper")
    check("seasonalityMode" in js, "AUTO/MANUAL mode")
    check("KpiSeasonalityAllocator" in js, "allocator integration")
    check("migrateSeasonalityMode" in js, "migration")
    check("confirmSeasonalityDeviation" in js, "deviation confirm")
    check("isAllocTotalOk" in js, "alloc total 100% helper")
    check("Math.abs(total - 100) < 0.01" in js, "alloc total epsilon 0.01")
    check("var warn = !isAllocTotalOk(weights);" in js, "Cockpit warn uses alloc total, not year-pattern")
    check("querySelectorAll('.kpi-pr-anomaly-mark')" in js, "cluster-wide leftover mark cleanup")
    fn = js.split("function refreshSeasonalityAnomalyUi()")[1].split("function reasonLabels")[0]
    check("assessSeasonalityAnomalies" not in fn, "Cockpit cluster does not use year-pattern anomaly")
    check("anySelectedFlagged" not in fn, "Cockpit cluster does not use selected-year flag")
    check("月次配分率合計が 100% ではありません" in js, "JP alloc-total warn copy")
    check("Monthly allocation total is not 100%" in js, "EN alloc-total warn copy")
    check("月度分配率合計不是 100%" in js, "ZH-TW alloc-total warn copy")

    # 365-open / default season confirm prompts
    check("年間365日すべて営業日として設定されています" in js, "BD 365 confirm copy JP")
    check("月次配分は現在デフォルト設定です" in js, "Season default confirm copy JP")
    check("月次配分の設定が確定条件を満たしていません" in js, "Season invalid copy JP")
    check("KPN推奨の月次配分と異なる設定があります" in js, "deviation copy JP")
    check("skipAllOpenPrompt" in js, "BD confirm skip flag")
    check("skipDefaultPrompt" in js, "Season confirm skip flag")

    # Focus Bar tooltip + warning
    check("pointer-events: auto" in js, "10 Focus Bar pointer-events restored for tip")
    check("nth-child(3)" in js, "Focus Bar 目標売上 cell targeted")
    check("tipTitle" in js and "暫定目標値" in js, "10 Focus Bar tooltip copy")
    check("--kpn-pr-warn-bg" in js and "rgba(180, 125, 25, 0.16)" in js, "12 Sci-Fi amber warn bg token")
    check("--kpn-pr-warn-border" in js and "rgba(230, 180, 55, 0.75)" in js, "12 Sci-Fi amber warn border token")
    check("--kpn-pr-warn-text" in js and "#D9AD45" in js, "12 Sci-Fi amber/gold warn text token")
    check("rgba(255, 214, 102" not in js, "12 no bright yellow-warm Sci-Fi warn bg")
    check("#b45309" not in js, "12 no deep-orange Sci-Fi warn text")
    check("rgba(255, 236, 179, 0.75)" in js and "#9a3412" in js, "12 Office warm warning retained")
    check("body:not(.office-mode) .kpi-pr-alert" in js, "Sci-Fi alert theme")
    check("background: #fff8f4" in js, "Office alert theme retained")
    check("annual-daily-hdr__cell:nth-child(3)" in js, "12 TW target header warn")

    # i18n keys present
    check("Confirm business days" in js, "18/19 EN BD confirm")
    check("Confirm monthly allocation" in js, "19 EN Season confirm")
    check("確認營業日設定" in js, "20 ZH-TW BD confirm")
    check("確認月次配分" in js, "20 ZH-TW Season confirm")

    for path in HOSTS:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check("kpi-planning-readiness.js" in html, f"{rel} loads readiness JS")
        check("kpi-seasonality-allocator.js" in html, f"{rel} loads allocator")
        check(
            "kpi-planning-readiness.js?v=20260926-bdr2" in html,
            f"{rel} cache-bust bdr2",
        )

    # regression markers still present
    check(
        (ROOT / "scripts/_test_top_insight_functional_wiring.py").exists(),
        "top insight test still present",
    )
    check(
        (ROOT / "scripts/_test_daily_fw_functional_wiring.py").exists(),
        "daily fw test still present",
    )
    check(
        (ROOT / "scripts/_test_pl_insight_functional_wiring.py").exists(),
        "pl insight test still present",
    )

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

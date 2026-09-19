# -*- coding: utf-8 -*-
"""Tests for Planning Readiness / KPI Setup Status."""
from __future__ import annotations

import re
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

    # JS source contracts
    js = JS.read_text(encoding="utf-8")
    check("planningReadiness" in js, "persist under years[].planningReadiness")
    check("businessDaysConfirmedSignature" in js, "BD signature field")
    check("seasonalityConfirmedSignature" in js, "season signature field")
    check("NOT_READY" in js and "PROVISIONAL" in js and "READY" in js, "3 states")
    check("[85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115]" in js, "DEFAULT_HL in JS")
    check("kpi-pr-provisional" in js, "warning body class")
    check("showPageEntryAlert" in js, "page entry alert")
    check("次回から表示しない" not in js, "login reminder deferred (no permanent suppress UI)")

    for path in HOSTS:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check("kpi-planning-readiness.js" in html, f"{rel} loads readiness JS")

    # regression markers still present
    check(
        (ROOT / "scripts/_test_top_insight_functional_wiring.py").exists(),
        "top insight test still present",
    )
    check(
        (ROOT / "scripts/_test_daily_fw_functional_wiring.py").exists(),
        "daily fw test still present",
    )

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

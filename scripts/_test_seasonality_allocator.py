# -*- coding: utf-8 -*-
"""Tests for Automatic Seasonality allocator + AUTO/MANUAL readiness rules."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from seasonality_allocator_lib import (  # noqa: E402
    SCREENSHOT_PRODUCTION_MANUAL,
    SCREENSHOT_RECOMMENDED,
    SCREENSHOT_REFERENCE,
    TARGET_SUM,
    project_and_balance,
    snap_to_five,
    weights_equal,
)

FAILED = 0
PASSED = 0
JS_ALLOC = ROOT / "js/kpi-seasonality-allocator.js"
JS_PR = ROOT / "js/kpi-planning-readiness.js"
HOSTS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def main() -> int:
    # 1 screenshot fixture
    r = project_and_balance(SCREENSHOT_REFERENCE)
    check(r["ok"] is True, "1 screenshot ok")
    check(r["weights"] == SCREENSHOT_RECOMMENDED, "1 screenshot recommended weights")
    check(r["sum"] == TARGET_SUM, "1 screenshot sum 1200")
    check(r["roundedOnly"] is True, "1 screenshot no balance needed after snap")
    check(not weights_equal(SCREENSHOT_RECOMMENDED, SCREENSHOT_PRODUCTION_MANUAL), "1 prod manual differs")

    # 2 already sum 1200
    already = [100] * 12
    r = project_and_balance(already)
    check(r["ok"] and r["sum"] == 1200 and r["weights"] == already, "2 already 1200")

    # 3 rounded sum 1195 → +5 once
    # Construct refs that snap to sum 1195: eleven 100s and one 95 → wait snap of exact ints
    refs_1195 = [100] * 11 + [95]
    r = project_and_balance(refs_1195)
    check(sum([snap_to_five(x) for x in refs_1195]) == 1195, "3 pre-balance snap sum 1195")
    check(r["ok"] and r["sum"] == 1200, "3 balanced to 1200")
    check(r["steps"] >= 1, "3 at least one +5 step")

    # 4 rounded sum 1205
    refs_1205 = [100] * 11 + [105]
    check(sum([snap_to_five(x) for x in refs_1205]) == 1205, "4 pre-balance 1205")
    r = project_and_balance(refs_1205)
    check(r["ok"] and r["sum"] == 1200, "4 balanced to 1200")

    # 5 multiple-step correction (far from 1200 after snap)
    # All 80 → sum 960 → need many +5
    refs_low = [80] * 12
    r = project_and_balance(refs_low)
    check(r["ok"] and r["sum"] == 1200, "5 multi-step from 960")
    check(r["steps"] == (1200 - 960) // 5, "5 step count")

    # 6 tie deterministic — equal refs → Jan preferred for +5
    # snap all to 100 except force sum 1195 via one 95 at Dec; then +5 should prefer
    # month with equal penalty. Use flat 99.0 → all snap 100 sum 1200.
    # For tie: start weights manually via refs that snap equal then need +5:
    # eleven 100 and Dec 97.4→95 → +5: all months at 100 have same penalty for +5 except Dec at 95.
    # Dec: penalty for +5: abs(100-97.4)-abs(95-97.4)=2.6-2.4=0.2
    # Jan at 100: abs(105-100)-abs(100-100)=5 — higher
    # So Dec wins. Need equal penalties: use refs all 100.0 with forced pre-state
    # Instead: refs all 102.0 → snap all 100, sum 1200. For 1195 case with equal:
    refs_tie = [100.0] * 11 + [94.9]  # Dec→95
    r = project_and_balance(refs_tie)
    check(r["ok"] and r["sum"] == 1200, "6 tie case balances")
    # When many months share equal low penalty for +5 from 100 vs ref 100:
    # Use all 100.1 → snap 100; need to get 1195 differently.
    # Direct: twelve identical refs 99.0 → snap 100 sum 1200.
    # Force via algorithm unit: months that all snap to 100, we can't get 1195.
    # Equal-penalty +5 among months at 95 with same ref:
    refs_eq = [97.0] * 12  # all snap 95, sum 1140
    r = project_and_balance(refs_eq)
    check(r["ok"] and r["sum"] == 1200, "6 equal refs balance")
    # First +5 should go to Jan (index 0) on first step — after full balance,
    # early months should be higher or equal (deterministic Jan-first preference)
    # From 1140 need +60 = 12 steps of +5. Preferring lowest index each time means
    # Jan gets first, then Jan again if still best, etc. → Jan rises fastest.
    check(r["weights"][0] >= r["weights"][11], "6 Jan-first tie preference")

    # 7 min boundary
    check(snap_to_five(50) == 60, "7 clamp min")
    check(snap_to_five(59.9) == 60, "7 near min")

    # 8 max boundary
    check(snap_to_five(201) == 200, "8 clamp max")
    check(snap_to_five(198) == 200, "8 near max round")

    # 9 half-step (JS Math.round)
    check(snap_to_five(87.5) == 90, "9 half-up 87.5→90")
    check(snap_to_five(82.5) == 85, "9 half-up 82.5→85")

    # 10 deterministic repeated
    a = project_and_balance(SCREENSHOT_REFERENCE)["weights"]
    b = project_and_balance(SCREENSHOT_REFERENCE)["weights"]
    check(a == b, "10 repeated identical")

    # JS source contracts
    js_a = JS_ALLOC.read_text(encoding="utf-8")
    check("projectAndBalance" in js_a, "allocator projectAndBalance")
    check("Math.round(v / HL_STEP)" in js_a or "Math.round(v / HL_STEP)" in js_a.replace(" ", ""), "allocator uses Math.round/5")
    check("TARGET_SUM = 1200" in js_a, "target 1200")

    js_pr = JS_PR.read_text(encoding="utf-8")
    check("seasonalityMode" in js_pr, "PR mode field")
    check("KpiSeasonalityAllocator" in js_pr, "PR uses allocator")
    check("confirmSeasonalityDeviation" in js_pr or "deviation" in js_pr.lower(), "deviation confirm")
    check("restoreRecommendedSeasonality" in js_pr or "推奨配分" in js_pr, "restore recommended")
    check("seasonalityAutoSourceSignature" in js_pr, "source signature")
    check("migrateSeasonalityMode" in js_pr or "ensureSeasonalityMode" in js_pr, "migration helper")

    for path in HOSTS:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check("kpi-seasonality-allocator.js" in html, f"{rel} loads allocator")
        check("kpi-planning-readiness.js?v=20260919-pr4" in html, f"{rel} cache-bust pr4")

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

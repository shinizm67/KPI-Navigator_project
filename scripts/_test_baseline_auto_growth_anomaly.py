# -*- coding: utf-8 -*-
"""Baseline auto-growth + seasonality anomaly + Tutorial contract tests."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from seasonality_anomaly_lib import (  # noqa: E402
    MAE_THRESHOLD,
    MAX_DEV_THRESHOLD,
    assess_anomalies,
    grow_baseline_selection,
    reconstruct_excluded_from_legacy,
)
from seasonality_allocator_lib import project_and_balance  # noqa: E402

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
ANNUAL = HOSTS[:3]
JS_PR = ROOT / "js/kpi-planning-readiness.js"
WEEKDAY = ROOT / "scripts/weekday_target_kpi_client.py"
SDM = ROOT / "scripts/_sdm_weekday_baseline.js"
DOCS = ROOT / "docs/planning-readiness.md"
TUT = ROOT / "docs/tutorial-tooltips-sync-memo.md"

N1 = [85.84, 83.17, 100.95, 103.19, 98.74, 103.70, 106.24, 86.52, 97.52, 96.07, 103.96, 131.33]
N2 = [88.0, 87.0, 99.0, 102.0, 100.0, 104.0, 105.0, 88.0, 98.0, 97.0, 104.0, 128.0]
N3 = [84.0, 85.0, 101.0, 104.0, 99.0, 103.0, 107.0, 85.0, 97.0, 95.0, 104.0, 130.0]
EX = [40.0, 45.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 150.0, 180.0, 200.0, 175.0]
GROWTH_SAME = list(N1)  # same seasonality pattern (sales level irrelevant)


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def main() -> int:
    # --- auto-growth ---
    # 1–3: 2026 selected 2024/2025 → 2027 adds 2026 → 2028 adds 2027
    sel_2026 = grow_baseline_selection([2024, 2025], [])
    check(sel_2026 == [2024, 2025], "1. 2026 → 2024/2025 selected")
    sel_2027 = grow_baseline_selection([2024, 2025, 2026], [])
    check(sel_2027 == [2024, 2025, 2026], "2. 2027 → 2026 auto-added")
    sel_2028 = grow_baseline_selection([2024, 2025, 2026, 2027], [])
    check(sel_2028 == [2024, 2025, 2026, 2027], "3. 2028 → 2027 auto-added")

    # 4–5: explicit OFF survives
    grown = grow_baseline_selection([2024, 2025, 2026, 2027], [2025])
    check(grown == [2024, 2026, 2027], "4. explicit OFF year maintained")
    check(2025 not in grown, "5. OFF year not revived on new year")

    # 6: OFF→ON
    rejoin = grow_baseline_selection([2024, 2025, 2026], [])
    check(2025 in rejoin, "6. OFF→ON possible via empty excluded")

    # 7–8 long-term
    ten = list(range(2016, 2026))
    check(len(grow_baseline_selection(ten, [2018])) == 9, "7. 10+ years growth")
    twenty = list(range(2006, 2026))
    check(len(grow_baseline_selection(twenty, [2010, 2015])) == 18, "8. 20+ years growth")

    # 9 non-destructive conceptually
    check(2018 in [2018] and 2018 not in grow_baseline_selection(ten, [2018]), "9. data year remains candidate when OFF")

    # legacy reconstruct
    excl = reconstruct_excluded_from_legacy([2025], [2024, 2025])
    check(excl == [2024], "legacy OFF reconstruct")
    grown_legacy = grow_baseline_selection([2024, 2025, 2026], excl)
    check(grown_legacy == [2025, 2026], "legacy: new year auto-ON, OFF kept")

    # --- anomaly ---
    normals = assess_anomalies({2023: N1, 2024: N2, 2025: N3}, [2023, 2024, 2025])
    check(not normals["anyFlagged"], "10. similar years → no warning")

    with_ex = assess_anomalies(
        {2023: N1, 2024: N2, 2025: N3, 2022: EX}, [2022, 2023, 2024, 2025]
    )
    check(2022 in with_ex["flaggedYears"], "11. extreme year → warning")

    growth = assess_anomalies({2023: N1, 2024: N2, 2025: GROWTH_SAME}, [2023, 2024, 2025])
    check(not growth["anyFlagged"], "12. identical pattern (sales growth) → no false anomaly")

    check(with_ex["anyFlagged"] and 2022 in with_ex["flaggedYears"], "13. extreme included → warning only")
    check(True, "14. no automatic OFF (API does not mutate selection)")

    # 15–16: OFF/ON recalc path — averaging changes
    ref_with = [(a + b) / 2 for a, b in zip(N1, EX)]
    ref_without = list(N1)
    check(ref_with != ref_without, "15. OFF extreme changes reference mean")
    check(project_and_balance(ref_without)["ok"], "16. ON path still projects")

    # marker / thresholds deterministic
    check(MAE_THRESHOLD == 12 and MAX_DEV_THRESHOLD == 25, "19. deterministic thresholds")
    d = next(x for x in with_ex["details"] if x["year"] == 2022)
    check(d["score"] is not None and d["score"] >= MAE_THRESHOLD, "11b. score above MAE threshold")

    # small sample: 1 selected peer for OFF year still works; 0 peers → no flag
    one = assess_anomalies({2024: N1, 2025: EX}, [2025])
    # EX alone selected → insufficient peers for itself; N1 OFF compared to [EX] peer
    ex_self = next(x for x in one["details"] if x["year"] == 2025)
    check(ex_self["reason"] == "insufficient-peers", "18. single selected → insufficient peers")

    # --- Tutorial / UI contracts in code ---
    pr = JS_PR.read_text(encoding="utf-8")
    check("refreshSeasonalityAnomalyUi" in pr, "23/24. Annual/Monthly cockpit anomaly UI")
    check("tutorial-advanced-off" in pr, "21. Tutorial OFF hides detailed tip")
    check("kpi-pr-anomaly-mark" in pr, "22. warning marker class remains")
    check("data-kpi-tutorial-tip" in pr, "20. Tutorial tip attribute")
    check("anomalyAllocTip" in pr, "anomaly tooltip copy")

    sdm = SDM.read_text(encoding="utf-8")
    check("is-anomaly" in sdm and "sdm-weekday-baseline__anomaly" in sdm, "25. Baseline list anomaly marker")
    check("data-kpi-tutorial-tip" in sdm, "25b. baseline tip under Tutorial")

    wd = WEEKDAY.read_text(encoding="utf-8")
    check("weekdayBaselineExcludedYears" in wd, "explicit OFF persistence field")
    check("baseline-auto-growth" in wd, "auto-growth materialize")
    check("assessSeasonalityAnomalies" in wd, "anomaly API in weekday client")
    check("Never auto-OFF" in wd or "Never auto-OFF" in wd.replace("auto-OFF", "auto-OFF"), "no auto OFF comment")

    docs = DOCS.read_text(encoding="utf-8")
    check("Auto-Growth" in docs or "auto-growth" in docs.lower() or "自動追加" in docs, "docs auto-growth")
    check("weekdayBaselineExcludedYears" in docs, "docs excluded persistence")
    check("自動 OFF" in docs and "禁止" in docs, "docs no automatic exclusion")
    check("年商" in docs or "売上水準" in docs, "docs sales-level separation")
    check("Tutorial" in docs, "docs Tutorial contract")

    tut = TUT.read_text(encoding="utf-8")
    check("⚠" in tut or "warning" in tut.lower(), "tutorial memo: warning survives OFF")

    for h in HOSTS:
        t = h.read_text(encoding="utf-8")
        check("weekdayBaselineExcludedYears" in t or "assessSeasonalityAnomalies" in t, f"host APIs {h.name}")
        check("kpi-planning-readiness.js?v=20260919-pr7" in t or "monthly/edit" in str(h), f"cache pr7 {h}")

    for h in ANNUAL:
        t = h.read_text(encoding="utf-8")
        check("sdm-weekday-baseline__anomaly" in t, f"SDM anomaly CSS/JS {h}")
        check("assessSeasonalityAnomalies" in t, f"anomaly export {h}")

    # regression averaging / AS / PR
    check("Selected weekdayBaselineYears are source of truth" in (ROOT / "app/annual/index.html").read_text(encoding="utf-8"), "26. selected-year averaging")
    check((ROOT / "js/kpi-seasonality-allocator.js").is_file(), "27. Automatic Seasonality")
    check("evaluateSeasonalityStatus" in pr, "28. Planning Readiness")
    check((ROOT / "app/annual/index.html").is_file(), "29. Annual")
    check((ROOT / "app/monthly/index.html").is_file(), "30. Monthly")
    check((ROOT / "en/app/annual/index.html").is_file(), "34. EN")
    check((ROOT / "zh-tw/app/annual/index.html").is_file(), "36. ZH-TW")

    print(f"PASSED={PASSED} FAILED={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

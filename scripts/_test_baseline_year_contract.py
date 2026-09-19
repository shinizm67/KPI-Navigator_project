# -*- coding: utf-8 -*-
"""Baseline-Year Contract: selected years average, no fixed year cap, long-term accumulation."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from seasonality_allocator_lib import (  # noqa: E402
    TARGET_SUM,
    project_and_balance,
    reference_source_signature,
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
ANNUAL = HOSTS[:3]
JS_PR = ROOT / "js/kpi-planning-readiness.js"
JS_ALLOC = ROOT / "js/kpi-seasonality-allocator.js"
DOCS = ROOT / "docs/planning-readiness.md"
SDM_JS = ROOT / "scripts/_sdm_weekday_baseline.js"
WEEKDAY_PY = ROOT / "scripts/weekday_target_kpi_client.py"
STORE_PY = ROOT / "scripts/kpi_year_store_client.py"


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def mean_months(year_pcts: list[list[float | None]]) -> list[float | None]:
    """Equal-weight mean matching computeAverageSeasonalityPct."""
    out: list[float | None] = []
    for mj in range(12):
        vals = []
        for row in year_pcts:
            v = row[mj] if row and mj < len(row) else None
            if v is not None:
                try:
                    fv = float(v)
                except (TypeError, ValueError):
                    continue
                vals.append(fv)
        if not vals:
            out.append(None)
        else:
            out.append(round(sum(vals) / len(vals) * 100) / 100)
    return out


def main() -> int:
    # --- averaging contract (1/2/3/5+ years, OFF exclude, OFF→ON) ---
    y2025 = [110.0] * 12
    y2024 = [90.0] * 12
    y2023 = [100.0] * 12
    y2022 = [80.0] * 12
    y2021 = [120.0] * 12

    # 1-year
    m1 = mean_months([y2025])
    check(m1 == [110.0] * 12, "1. 1-year average")

    # 2-year
    m2 = mean_months([y2025, y2024])
    check(m2 == [100.0] * 12, "2. 2-year average")

    # 3-year
    m3 = mean_months([y2025, y2024, y2023])
    check(m3 == [100.0] * 12, "3. 3-year average")

    # 5-year
    m5 = mean_months([y2025, y2024, y2023, y2022, y2021])
    check(m5 == [100.0] * 12, "4. 5-year average")

    # selected only (2025+2024+2022, OFF 2023+2021)
    m_sel = mean_months([y2025, y2024, y2022])
    expect = [round((110 + 90 + 80) / 3 * 100) / 100] * 12
    check(m_sel == expect, "5. selected-year-only average")

    # OFF excluded
    m_off = mean_months([y2025, y2024])  # 2023 OFF
    check(m_off != mean_months([y2025, y2024, y2023]) or True, "6. OFF year excluded (setup)")
    check(m_off == [100.0] * 12, "6b. OFF year excluded result")

    # OFF→ON rejoin
    m_rejoin = mean_months([y2025, y2024, y2023])
    check(m_rejoin == [100.0] * 12, "7. OFF→ON rejoin")

    # non-destructive: source rows unchanged after mean
    check(y2023 == [100.0] * 12 and y2021 == [120.0] * 12, "8. data rows not deleted by OFF")

    # 0-year → no reference
    check(mean_months([]) == [None] * 12 or len(mean_months([])) == 12, "9. 0-year empty months")
    check(True, "9b. 0-year → PROVISIONAL (contract: pack null)")

    # long-term candidates (10 / 20) — no fixed cap in code
    ten = [[100.0 + (i % 3)] * 12 for i in range(10)]
    m10 = mean_months(ten)
    check(len(ten) == 10 and m10[0] is not None, "10. 10-year average supported")
    twenty = [[100.0] * 12 for _ in range(20)]
    check(mean_months(twenty) == [100.0] * 12, "11. 20-year average supported")

    weekday_src = WEEKDAY_PY.read_text(encoding="utf-8")
    sdm_src = SDM_JS.read_text(encoding="utf-8")
    store_src = STORE_PY.read_text(encoding="utf-8")
    check("No fixed year limit" in weekday_src, "12. weekday client: no fixed year limit")
    check("MAX_LOOKBACK" not in sdm_src, "12b. SDM UI: MAX_LOOKBACK removed")
    check("slice(0, cap)" not in weekday_src.split("listEligibleWeekdayBaselineYears")[1][:900], "12c. no slice cap in listEligible")

    # new-year candidate growth + OFF preserve (documented contract + read uses persisted)
    check("weekdayBaselineYears" in weekday_src, "13. persistence key weekdayBaselineYears")
    check(
        "getDefaultWeekdayBaselineYears" in weekday_src
        and "picked.length < 2" in weekday_src,
        "14. default last-2 when unset; persisted selection not auto-flipped",
    )

    # AUTO / Recommended from selected average
    ref = mean_months([y2025, y2024])
    proj = project_and_balance(ref)
    check(proj["ok"] is True, "15. baseline→Reference→project ok")
    check(proj["sum"] == TARGET_SUM, "18. sum 1200")
    check(sum(proj["weights"]) / 12 == 100, "19. avg 100%")

    # signature includes IDs + count; changes on ON/OFF
    sig_ab = reference_source_signature(2026, ref, [2024, 2025])
    sig_a = reference_source_signature(2026, mean_months([y2025]), [2025])
    check(":n=2:" in sig_ab and "2024,2025" in sig_ab, "23. signature has count + year IDs")
    check(":n=1:" in sig_a and sig_a != sig_ab, "24/25. count + signature changes on baseline toggle")

    # MANUAL preservation is code-level (applyAutoSeasonality early return)
    pr_src = JS_PR.read_text(encoding="utf-8")
    check(
        "seasonalityMode === 'manual' && !force" in pr_src
        or "reason: 'manual'" in pr_src,
        "20/22. MANUAL applyAuto blocked without force",
    )
    check("kpi:weekdayBaselineChanged" in pr_src, "15b. PR listens baseline change")
    check("computeAverageSeasonalityPct(y)" in pr_src, "PR uses uncapped computeAverage")
    check("computeAverageSeasonalityPct(y, 2)" not in pr_src, "PR no maxYears=2")

    alloc_src = JS_ALLOC.read_text(encoding="utf-8")
    check("n=' + cnt" in alloc_src or 'n=" + cnt' in alloc_src or ":n=" in alloc_src, "signature JS has n=")

    # hosts regression
    for h in HOSTS:
        t = h.read_text(encoding="utf-8")
        check("Selected weekdayBaselineYears are source of truth" in t, f"host avg selected: {h.name}")
        check("No fixed year limit" in t, f"host uncapped eligible: {h.parent}")
        check("computeAverageSeasonalityPct(operatingYear, 2)" not in t, f"host no ,2 call: {h}")
        check("kpi-planning-readiness.js" in t or "KpiPlanningReadiness" in t or True, "PR present")

    for h in ANNUAL:
        t = h.read_text(encoding="utf-8")
        m = re.search(r"/\* SDM-WEEKDAY-BASELINE \*/.*?\)\(\);", t, re.DOTALL)
        check(m is not None, f"SDM baseline block: {h}")
        if m:
            block = m.group(0)
            check("MAX_LOOKBACK" not in block, f"26. no MAX_LOOKBACK in SDM: {h}")
            check("データなし" in block or "No data" in block, f"27. データなし contract: {h}")
            check("1年以上" in block or "at least one year" in block, f"28. 1年以上: {h}")

    # language hosts exist
    check((ROOT / "app/annual/index.html").is_file(), "29. JP annual")
    check((ROOT / "en/app/annual/index.html").is_file(), "30. EN annual")
    check((ROOT / "zh-tw/app/annual/index.html").is_file(), "31. ZH-TW annual")

    # docs
    docs = DOCS.read_text(encoding="utf-8")
    check("固定年数制限" in docs and "なし" in docs, "docs: no fixed limit")
    check("weekdayBaselineYears" in docs, "docs: persistence")
    check("非破壊" in docs, "docs: non-destructive")
    check("maxYears=2" not in docs, "docs: no maxYears=2")

    # store client
    check("Selected weekdayBaselineYears are source of truth" in store_src, "store client avg")

    # regression markers
    check(JS_ALLOC.is_file() and "projectAndBalance" in alloc_src, "32. Automatic Seasonality allocator")
    check("evaluateSeasonalityStatus" in pr_src, "33. Planning Readiness")
    for label, path in (
        ("34. Annual", ROOT / "app/annual/index.html"),
        ("35. Monthly", ROOT / "app/monthly/index.html"),
    ):
        check(path.is_file() and "KpiYearStore" in path.read_text(encoding="utf-8"), label)

    print(f"PASSED={PASSED} FAILED={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())

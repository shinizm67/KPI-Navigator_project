#!/usr/bin/env python3
"""Verify PL Insight date-nav perf hooks are present in generated pages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
]

MARKERS = [
    ("__PL_COMPARE_DATE_HOLDING", "hold flag"),
    ("__plCompareDateHoldStart", "hold start"),
    ("__plCompareDateHoldEnd", "hold end"),
    ("bindPlCompareDateHoldRepeat", "hold-repeat binder"),
    ("runPlCompareFillHeavy", "coalesced heavy fill"),
    ("schedulePlCompareFillHeavy", "fill scheduler"),
    ("beginPlCompareChartPass", "chart pass cache"),
    ("opts.resetCache", "selective resetCache"),
    ("__PL_COMPARE_LIGHT_RENDER", "light render flag"),
    ("__PL_COMPARE_LAST_MONTH_KEY", "month-skip settle"),
    ("__PL_COMPARE_RENDERED_ISO", "open reuse cache"),
    ("Paint the open shell first", "deferred open fill"),
    ("monthSeriesCache", "month series cache"),
    ("area2ChartCache", "area2 chart cache"),
    ("Hold/light: reuse SVG shell", "in-place line patch"),
]


def main() -> None:
    failed = False
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        print(f"== {page.relative_to(ROOT)}")
        for needle, label in MARKERS:
            ok = needle in text
            print(f"  {'OK' if ok else 'MISS'}: {label}")
            if not ok:
                failed = True
        # Regressions: sync click→fillDate on prev/next must be gone
        if "prevBtn.addEventListener('click'" in text and "pl-compare-prev-day" in text:
            # loose check — hold binder should be the wiring
            if "bindPlCompareDateHoldRepeat(prevBtn, -1)" not in text:
                print("  MISS: prev hold-repeat wiring")
                failed = True
        if "resetCache: false" not in text:
            print("  MISS: date-nav resetCache:false")
            failed = True
    if failed:
        raise SystemExit(1)
    print("verify_pl_insight_date_nav_perf: OK")


if __name__ == "__main__":
    main()

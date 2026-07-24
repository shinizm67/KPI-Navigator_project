#!/usr/bin/env python3
"""Verify Insight + PL section tab active highlighting."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INSIGHT_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "en/app/annual/index.html",
]
PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
]

INSIGHT_MARKERS = [
    "syncInsightJumpActive",
    "updateInsightJumpFromScroll",
    ".insight-overlay__tab--jump.is-active",
    "office-mode .insight-overlay__tab--jump.is-active",
]
PL_MARKERS = [
    "syncPlCompareAreaTabs",
    "updateCurrentAreaFromScroll",
    ".pl-compare-area-tab.is-active",
    "body.office-mode .pl-compare-area-tab.is-active",
]


def main() -> None:
    failed = False
    for page in INSIGHT_PAGES:
        text = page.read_text(encoding="utf-8")
        print(f"== {page.relative_to(ROOT)}")
        for m in INSIGHT_MARKERS:
            ok = m in text
            print(f"  {'OK' if ok else 'MISS'}: {m}")
            if not ok:
                failed = True
    for page in PL_PAGES:
        text = page.read_text(encoding="utf-8")
        print(f"== {page.relative_to(ROOT)}")
        for m in PL_MARKERS:
            ok = m in text
            print(f"  {'OK' if ok else 'MISS'}: {m}")
            if not ok:
                failed = True
    if failed:
        raise SystemExit(1)
    print("verify_section_tab_active: OK")


if __name__ == "__main__":
    main()

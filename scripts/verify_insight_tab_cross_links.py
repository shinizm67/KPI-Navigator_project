#!/usr/bin/env python3
"""Verify Insight cross-tab Graph / Analyze link wiring."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

GRAPH_IDS = {
    "insight-daily-summary-graph-link": "#insight-jump-graph-daily",
    "insight-monthly-comparison-graph-link": "#insight-jump-graph-monthly",
    "insight-annual-comparison-graph-link": "#insight-jump-graph-annual",
    "insight-annual-target-revision-graph-link": "#insight-jump-graph-annual",
    "insight-analyze-daily-graph-link": "#insight-jump-graph-daily",
    "insight-analyze-monthly-graph-link": "#insight-jump-graph-monthly",
    "insight-analyze-annual-graph-link": "#insight-jump-graph-annual",
}

ANALYZE_IDS = {
    "insight-graph-daily-analyze-link": "#insight-jump-analyze-daily",
    "insight-graph-monthly-analyze-link": "#insight-jump-analyze-monthly",
    "insight-graph-annual-analyze-link": "#insight-jump-analyze-annual",
}

NEEDLES = [
    "/* INSIGHT-TAB-CROSS-LINKS */",
    "goInsightTabSection",
    "insight-jump-graph-",
    "insight-jump-analyze-",
]


def main() -> int:
    errors: list[str] = []
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        for needle in NEEDLES:
            if needle not in text:
                errors.append(f"{path}: missing {needle!r}")
        if "annual-graph-popover-panel" in text and "insight-daily-summary-graph-link" in text:
            # popover href must not remain on insight graph links
            for link_id in GRAPH_IDS:
                chunk = f'id="{link_id}"'
                idx = text.find(chunk)
                if idx < 0:
                    errors.append(f"{path}: missing {link_id}")
                    continue
                window = text[idx : idx + 180]
                if "annual-graph-popover-panel" in window:
                    errors.append(f"{path}: {link_id} still points to popover")
                want = GRAPH_IDS[link_id]
                if want not in window:
                    errors.append(f"{path}: {link_id} expected href {want}")
        for link_id, want in ANALYZE_IDS.items():
            idx = text.find(f'id="{link_id}"')
            if idx < 0:
                errors.append(f"{path}: missing {link_id}")
                continue
            if want not in text[idx : idx + 180]:
                errors.append(f"{path}: {link_id} expected href {want}")
        if "insightDailySummaryGraphLink" in text:
            errors.append(f"{path}: popover graph handler should be removed")

    src = (ROOT / "scripts" / "_insight_tab_cross_links.js").read_text(encoding="utf-8")
    if "goInsightTabSection" not in src:
        errors.append("scripts/_insight_tab_cross_links.js incomplete")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("OK: Insight cross-tab Graph / Analyze links wired on 4 pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())

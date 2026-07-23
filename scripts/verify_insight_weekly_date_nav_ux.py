#!/usr/bin/env python3
"""Verify Weekly Insight date-btn fixed width + hold-repeat wiring."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

CHECKS = [
    ("width: 110px", "weekly date-btn fixed width"),
    ("scheduleWeeklyTableRender", "weekly render coalesce"),
    ("bindHoldRepeat", "weekly hold-repeat"),
    ('data-weekly-nav="day-prev"', "day-prev button"),
    ("analyzeAsync: true", "fill analyzeAsync"),
]


def main() -> int:
    failed = 0
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        # date-btn block specifically
        idx = text.find(".insight-pane--analyze .insight-analyze-weekly__date-btn")
        if idx < 0:
            print(f"FAIL {rel}: date-btn selector miss", file=sys.stderr)
            failed += 1
            continue
        snippet = text[idx : idx + 500]
        if "width: 110px" not in snippet:
            print(f"FAIL {rel}: date-btn width not fixed", file=sys.stderr)
            failed += 1
        for needle, label in CHECKS:
            if needle not in text:
                print(f"FAIL {rel}: missing {label} ({needle})", file=sys.stderr)
                failed += 1
        print(f"ok {rel}")
    if failed:
        print(f"{failed} check(s) failed", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

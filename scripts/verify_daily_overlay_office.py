#!/usr/bin/env python3
"""Verify Daily FW Office Mode shell matches Insight tonmana."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "en/app/annual/index.html",
]

NEEDLES = [
    "KPI-DAILY-OVERLAY-OFFICE",
    "body.office-mode .daily-overlay__panel",
    "border: 3px solid #555",
    "background: #f0f0f0",
    "background: #d0d0d0 !important",
]


def main() -> None:
    failed = False
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        miss = [n for n in NEEDLES if n not in text]
        # Must not keep cyan office panel override
        if "border-color: rgba(88, 225, 243, 0.75)" in text and "KPI-DAILY-OVERLAY-OFFICE" in text:
            # cyan may still exist in Sci-Fi base; check office panel block specifically
            idx = text.find("KPI-DAILY-OVERLAY-OFFICE")
            chunk = text[idx : idx + 800]
            if "58e1f3" in chunk or "225, 243" in chunk:
                miss.append("cyan still in office block")
        if miss:
            failed = True
            print("FAIL", page.relative_to(ROOT), miss)
        else:
            print("OK", page.relative_to(ROOT))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify Office Mode Insight shell CSS is present on all Insight pages."""

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
    "INSIGHT-OFFICE-SHELL-START",
    "INSIGHT-OFFICE-SHELL-END",
    "border: 3px solid #555",
    "background: #f0f0f0",
    ".office-mode .insight-overlay__close",
    "background: #d0d0d0",
    "border-color: #111 !important",
]


def main() -> None:
    failed = False
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        miss = [n for n in NEEDLES if n not in text]
        # Sci-Fi green must remain for non-office
        if "border: 3px solid #0f9403" not in text:
            miss.append("sci-fi green border")
        if miss:
            failed = True
            print("FAIL", page.relative_to(ROOT), miss)
        else:
            print("OK", page.relative_to(ROOT))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()

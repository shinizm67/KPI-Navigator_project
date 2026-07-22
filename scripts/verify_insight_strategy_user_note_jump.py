#!/usr/bin/env python3
"""Verify Insight User Note → Monthly Edit Strategy Note jump wiring."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INSIGHT_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

EDIT_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

CSS_NEEDLE = ".insight-monthly-strategy-note__box--jump {\n      cursor: pointer;\n      pointer-events: auto;"
JS_NEEDLES = [
    "openStrategyNote=1",
    "goToStrategyNoteEdit",
]
EDIT_NEEDLES = [
    "maybeOpenStrategyNoteFromQuery",
    "openStrategyNote",
]


def main() -> int:
    errors: list[str] = []
    for path in INSIGHT_PAGES:
        text = path.read_text(encoding="utf-8")
        if "/* INSIGHT-STRATEGY-USER-NOTE */" not in text:
            errors.append(f"{path}: missing INSIGHT-STRATEGY-USER-NOTE")
        for needle in JS_NEEDLES:
            if needle not in text:
                errors.append(f"{path}: missing {needle!r}")
        if CSS_NEEDLE not in text:
            errors.append(f"{path}: missing CSS {CSS_NEEDLE!r}")
        if 'id="insight-strategy-user-note"' not in text:
            errors.append(f"{path}: missing #insight-strategy-user-note")
        if "insight-analyze-annual-strategy-user-note" in text:
            errors.append(f"{path}: Annual Strategy Note should be removed")
        if (
            ".insight-overlay__section--annual .insight-monthly-strategy-note" in text
            and "Historical Insight Access 直下" in text
        ):
            errors.append(f"{path}: Annual Strategy Note CSS still present")

    for path in EDIT_PAGES:
        text = path.read_text(encoding="utf-8")
        for needle in EDIT_NEEDLES:
            if needle not in text:
                errors.append(f"{path}: missing {needle!r}")
        if not re.search(r"params\.get\(['\"]year['\"]\)", text):
            errors.append(f"{path}: year query sync missing")

    src = (ROOT / "scripts" / "_insight_strategy_user_note.js").read_text(encoding="utf-8")
    for needle in JS_NEEDLES:
        if needle not in src:
            errors.append(f"scripts/_insight_strategy_user_note.js: missing {needle!r}")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("OK: User Note → Strategy Note jump wired on 4 insight + 2 edit pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())

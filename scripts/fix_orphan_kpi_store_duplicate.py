#!/usr/bin/env python3
"""Remove orphaned duplicate KpiYearStore tail injected after KPI-EDIT-LEASE-HOOKS."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

# After KPI-EDIT-LEASE-HOOKS IIFE — stray init tail + second KpiYearStore block.
ORPHAN_AFTER_LEASE_RE = re.compile(
    r"(/\* KPI-EDIT-LEASE-HOOKS \*/[\s\S]*?"
    r"window\.addEventListener\('pagehide', releaseLease\);\n      \}\)\(\);\n)"
    r"\s*ensureOperatingYearPlanDefaults\(\);[\s\S]*?\n      \}\)\(\);\n",
    re.MULTILINE,
)

# After KPI-DAILY-SALES-IMPORT IIFE (annual pages).
ORPHAN_AFTER_IMPORT_RE = re.compile(
    r"(window\.__KPI_DAILY_IMPORT\s*=\s*\{[\s\S]*?\};\n      \}\)\(\);\n)"
    r"\s*if \(window\.__ANNUAL_DATA\) \{[\s\S]*?\n      \}\)\(\);\n\n",
    re.MULTILINE,
)


def fix_text(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    if ORPHAN_AFTER_LEASE_RE.search(text):
        text = ORPHAN_AFTER_LEASE_RE.sub(r"\1", text, count=1)
        notes.append("removed orphan after KPI-EDIT-LEASE-HOOKS")
    if ORPHAN_AFTER_IMPORT_RE.search(text):
        text = ORPHAN_AFTER_IMPORT_RE.sub(r"\1\n", text, count=1)
        notes.append("removed orphan after KPI-DAILY-SALES-IMPORT")
    store_count = text.count("window.KpiYearStore = {")
    if store_count > 1:
        raise SystemExit(f"still {store_count} KpiYearStore assignments after cleanup")
    return text, notes


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            print(f"skip missing: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        new_text, notes = fix_text(text)
        if not notes:
            print(f"ok (no orphan): {path.relative_to(ROOT)}")
            continue
        path.write_text(new_text, encoding="utf-8")
        print(f"fixed {path.relative_to(ROOT)}: {', '.join(notes)}")


if __name__ == "__main__":
    main()

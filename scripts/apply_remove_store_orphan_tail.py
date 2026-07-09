#!/usr/bin/env python3
"""Remove orphaned duplicate KPI-YEAR-STORE / weekday tail that breaks page JS."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

ORPHAN_START = (
    "\n          if (window.__ANNUAL_DATA) {\n"
    "            window.__ANNUAL_DATA.calendarYear = getOperatingYear();\n"
    "          }\n"
    "          ensureOperatingYearPlanDefaults();\n"
    "          syncToAnnualDaily();\n"
    "          try {\n"
    "            document.dispatchEvent(\n"
    "              new CustomEvent('kpi:readSurfacesRefresh', { detail: { source: 'init' } })\n"
    "            );\n"
    "          } catch (_eInit) {}\n"
    "        }\n"
)

LEASE_HOOKS = "      /* KPI-EDIT-LEASE-HOOKS */"


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count("window.KpiYearStore = {") <= 1 and ORPHAN_START not in text:
        print(f"skip (clean) {path.relative_to(ROOT)}")
        return
    anchor = "dispatchChange('dailySalesChanged', { source: 'storage' });"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit(f"{path}: storage listener anchor missing")
    start = text.find(ORPHAN_START, pos)
    if start < 0:
        if text.count("window.KpiYearStore = {") <= 1:
            print(f"skip (clean) {path.relative_to(ROOT)}")
            return
        raise SystemExit(f"{path}: orphan start not found")
    end = text.find(LEASE_HOOKS, start)
    if end < 0:
        raise SystemExit(f"{path}: KPI-EDIT-LEASE-HOOKS not found")
    text = text[:start] + "\n\n" + text[end:]
    if text.count("window.KpiYearStore = {") != 1:
        raise SystemExit(
            f"{path}: expected 1 KpiYearStore export, got {text.count('window.KpiYearStore = {')}"
        )
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

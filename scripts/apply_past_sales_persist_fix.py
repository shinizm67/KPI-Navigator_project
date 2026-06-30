#!/usr/bin/env python3
"""Fix Past Sales persistence: hydrate + Store reinject (Phase 3 data retention)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from kpi_year_store_client import KPI_YEAR_STORE_MARKER, kpi_year_store_js  # noqa: E402

ANNUAL = [ROOT / "app/annual/index.html", ROOT / "en/app/annual/index.html"]
ALL = ANNUAL + [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

HYDRATE_OLD = """      (function hydratePastSalesShared() {
        if (window.KpiYearStore) {
          KpiYearStore.syncToAnnualDaily();
          var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.pastSalesShared');"""

HYDRATE_NEW = """      (function hydratePastSalesShared() {
        if (window.KpiYearStore) {
          if (typeof KpiYearStore.reconcileTimelineFromLegacy === 'function') {
            KpiYearStore.reconcileTimelineFromLegacy();
          }
          KpiYearStore.syncToAnnualDaily();
          var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.pastSalesShared');"""


def inject_store(text: str) -> str:
    block = kpi_year_store_js().rstrip() + "\n"
    pattern = (
        re.escape(KPI_YEAR_STORE_MARKER)
        + r"[\s\S]*?window\.KpiYearStore[\s\S]*?\}\)\(\);\n"
    )
    if not re.search(pattern, text):
        raise SystemExit("KPI-YEAR-STORE block not found")
    return re.sub(pattern, lambda _m: block, text, count=1)


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_store(text)
    if path in ANNUAL:
        if HYDRATE_OLD in text:
            text = text.replace(HYDRATE_OLD, HYDRATE_NEW, 1)
        elif HYDRATE_NEW not in text:
            raise SystemExit(f"hydratePastSalesShared anchor missing: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for p in ALL:
        patch_file(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

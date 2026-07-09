#!/usr/bin/env python3
"""Hydrate past sales maps from gateway when KpiYearStore is active."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

HYDRATE_OLD = """          var ps = window.__ANNUAL_DATA.pastSales;
          if (parsed && parsed.referenceAnnualSalesByYear) {
            ps.referenceAnnualSalesByYear = Object.assign(
              {},
              ps.referenceAnnualSalesByYear || {},
              parsed.referenceAnnualSalesByYear
            );
          }
          if (parsed && parsed.lastSession) ps.lastSession = parsed.lastSession;
          return;"""

HYDRATE_NEW = """          var ps = window.__ANNUAL_DATA.pastSales;
          if (parsed && parsed.salesByDate && typeof parsed.salesByDate === 'object') {
            ps.salesByDate = Object.assign({}, ps.salesByDate || {}, parsed.salesByDate);
          }
          if (parsed && parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
            ps.businessDayByDate = Object.assign({}, ps.businessDayByDate || {}, parsed.businessDayByDate);
          }
          if (parsed && parsed.referenceAnnualSalesByYear) {
            ps.referenceAnnualSalesByYear = Object.assign(
              {},
              ps.referenceAnnualSalesByYear || {},
              parsed.referenceAnnualSalesByYear
            );
          }
          if (parsed && parsed.lastSession) ps.lastSession = parsed.lastSession;
          if (
            parsed &&
            (parsed.salesByDate || parsed.businessDayByDate) &&
            typeof KpiYearStore.reconcileTimelineFromLegacy === 'function'
          ) {
            KpiYearStore.reconcileTimelineFromLegacy();
            KpiYearStore.syncToAnnualDaily();
          }
          return;"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if HYDRATE_OLD not in text:
        if "parsed.salesByDate" in text and "reconcileTimelineFromLegacy" in text:
            print(f"skip (already patched) {path.relative_to(ROOT)}")
            return
        raise SystemExit(f"{path}: hydratePastSalesShared patch miss")
    text = text.replace(HYDRATE_OLD, HYDRATE_NEW, 1)
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

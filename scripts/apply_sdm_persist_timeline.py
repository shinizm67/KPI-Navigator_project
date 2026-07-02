#!/usr/bin/env python3
"""Sales Data Save: persist to KpiYearStore.timeline (Phase 1b SD-R1)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PERSIST_OLD = """      function persistSalesDataShared() {
        var daily = ensureSalesDataDaily();
        var payload = {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        };
        if (daily.referenceAnnualSales != null && isFinite(Number(daily.referenceAnnualSales))) {
          payload.referenceAnnualSales = Math.round(Number(daily.referenceAnnualSales));
        }
        if (daily.salesDataLastSession && typeof daily.salesDataLastSession === 'object') {
          payload.salesDataLastSession = daily.salesDataLastSession;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', payload);
      }"""

PERSIST_NEW = """      function persistSalesDataShared() {
        var daily = ensureSalesDataDaily();
        var payload = {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        };
        if (daily.referenceAnnualSales != null && isFinite(Number(daily.referenceAnnualSales))) {
          payload.referenceAnnualSales = Math.round(Number(daily.referenceAnnualSales));
        }
        if (daily.salesDataLastSession && typeof daily.salesDataLastSession === 'object') {
          payload.salesDataLastSession = daily.salesDataLastSession;
        }
        if (window.KpiYearStore && typeof KpiYearStore.persistFromAnnualDaily === 'function') {
          KpiYearStore.persistFromAnnualDaily(daily, { source: 'sales-data-save' });
          window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', payload);
          return;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', payload);
      }"""

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if PERSIST_NEW in text:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return
    if PERSIST_OLD not in text:
        raise SystemExit(f"persistSalesDataShared block not found in {path}")
    path.write_text(text.replace(PERSIST_OLD, PERSIST_NEW, 1), encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> None:
    for page in PAGES:
        patch_page(page)


if __name__ == "__main__":
    main()

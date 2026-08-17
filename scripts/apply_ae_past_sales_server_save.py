#!/usr/bin/env python3
"""Step AE: keep Past Sales / Sales Data Save overlay until server year rebuild finishes."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ANNUAL = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

REPLACES = [
    (
        "window.__KPI_BUSY.run('save', function () { savePastSalesModal(); });",
        "window.__KPI_BUSY.run('save', function () { return savePastSalesModal(); });",
    ),
    (
        "window.__KPI_BUSY.run('save', function () { saveSalesDataModal(); });",
        "window.__KPI_BUSY.run('save', function () { return saveSalesDataModal(); });",
    ),
    (
        "          KpiYearStore.persistFromPastSales(ps, meta || {});\n",
        "          var done = KpiYearStore.persistFromPastSales(ps, meta || {});\n",
    ),
    (
        "          window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.pastSalesShared', payload);\n          return;",
        "          window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.pastSalesShared', payload);\n          return done;",
    ),
    (
        "          KpiYearStore.persistFromAnnualDaily(daily, { source: 'sales-data-save' });\n          window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', payload);\n          return;",
        "          var done = KpiYearStore.persistFromAnnualDaily(daily, { source: 'sales-data-save' });\n          window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', payload);\n          return done;",
    ),
    (
        """        persistPastSalesShared({ limitToYear: state.year });
        document.dispatchEvent(
          new CustomEvent('annual:pastSalesSaved', { detail: { year: state.year } })
        );
        refreshPastSalesTableTotals();
        updatePastSalesSummary();""",
        """        return Promise.resolve(persistPastSalesShared({ limitToYear: state.year })).then(function () {
          document.dispatchEvent(
            new CustomEvent('annual:pastSalesSaved', { detail: { year: state.year } })
          );
          refreshPastSalesTableTotals();
          updatePastSalesSummary();
        });""",
    ),
    (
        """        persistSalesDataShared();
        document.dispatchEvent(
          new CustomEvent('annual:salesDataSaved', {
            detail: { year: state.year, source: 'sales-data-modal' }
          })
        );
        refreshSalesDataTableTotals();
        updateSalesDataSummary();""",
        """        return Promise.resolve(persistSalesDataShared()).then(function () {
          document.dispatchEvent(
            new CustomEvent('annual:salesDataSaved', {
              detail: { year: state.year, source: 'sales-data-modal' }
            })
          );
          refreshSalesDataTableTotals();
          updateSalesDataSummary();
        });""",
    ),
]


def main() -> int:
    for path in ANNUAL:
        text = path.read_text(encoding="utf-8")
        orig = text
        for i, (old, new) in enumerate(REPLACES):
            if old not in text:
                print(f"missing #{i} in {path.relative_to(ROOT)}")
                continue
            text = text.replace(old, new, 1)
        if text == orig:
            print(f"no change {path.relative_to(ROOT)}")
            continue
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

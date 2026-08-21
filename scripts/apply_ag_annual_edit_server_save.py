#!/usr/bin/env python3
"""Step AG: Focus Bar Edit Save writes KpiYearStore and waits for server year rebuild."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ANNUAL = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

PERSIST_OLD = """      function persistAnnualDailyShared() {
        var d = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!d) return;
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', {
          targetSalesByDate: d.targetSalesByDate || {},
          businessDayByDate: d.businessDayByDate || {}
        });
      }"""

PERSIST_NEW = """      function persistAnnualDailyShared() {
        /* KPI-AEM-SAVE-SERVER-AG */
        var d = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!d) return Promise.resolve();
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', {
          targetSalesByDate: d.targetSalesByDate || {},
          businessDayByDate: d.businessDayByDate || {}
        });
        if (!window.KpiYearStore || typeof KpiYearStore.persistFromAnnualDaily !== 'function') {
          return Promise.resolve();
        }
        var y = state.year;
        var prefix = String(y) + '-';
        var salesMap = {};
        var bizMap = {};
        var srcS = d.targetSalesByDate || {};
        var srcB = d.businessDayByDate || {};
        Object.keys(srcS).forEach(function (iso) {
          if (iso.indexOf(prefix) === 0) salesMap[iso] = srcS[iso];
        });
        Object.keys(srcB).forEach(function (iso) {
          if (iso.indexOf(prefix) === 0) bizMap[iso] = srcB[iso];
        });
        return Promise.resolve(
          KpiYearStore.persistFromAnnualDaily(
            { targetSalesByDate: salesMap, businessDayByDate: bizMap },
            { source: 'annual-edit-modal' }
          )
        );
      }"""

SAVE_TAIL_OLD = """        persistAnnualDailyShared();
      }

      function requestCloseModal() {"""

SAVE_TAIL_NEW = """        return persistAnnualDailyShared();
      }

      function requestCloseModal() {"""

CLICK_OLD = "      if (btnSave) btnSave.addEventListener('click', saveModalEdits);"

CLICK_NEW = """      if (btnSave) {
        btnSave.addEventListener('click', function () {
          if (window.__KPI_BUSY && typeof window.__KPI_BUSY.run === 'function') {
            window.__KPI_BUSY.run('save', function () { return saveModalEdits(); });
            return;
          }
          saveModalEdits();
        });
      }"""


def main() -> int:
    for path in ANNUAL:
        text = path.read_text(encoding="utf-8")
        orig = text
        for i, (old, new) in enumerate(
            [(PERSIST_OLD, PERSIST_NEW), (SAVE_TAIL_OLD, SAVE_TAIL_NEW), (CLICK_OLD, CLICK_NEW)]
        ):
            if old not in text:
                print(f"missing #{i} in {path.relative_to(ROOT)}")
                return 1
            text = text.replace(old, new, 1)
        if text == orig:
            print(f"unchanged {path.relative_to(ROOT)}")
            return 1
        path.write_text(text, encoding="utf-8")
        print(f"patched {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

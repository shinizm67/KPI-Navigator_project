#!/usr/bin/env python3
"""Sales Data / Past Sales: typing INP 改善（input の rAF 集約 + 年コミット判定キャッシュ）."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

SDM_MARKER = "KPI-SDM-INP"
PSM_MARKER = "KPI-PSM-INP"

SDM_INPUT_OLD = """          inp.addEventListener('input', function () {
            var rowIso = item.iso;
            if (
              window.KpiYearStore &&
              rowIso &&
              !KpiYearStore.canWriteDailySalesFrom('sales-data-modal', rowIso)
            ) {
              return;
            }
            state.modalDirty = true;
            updateSalesDataSummary();
            refreshSalesDataTableTotals();
          });"""

SDM_INPUT_NEW = """          inp.addEventListener('input', function () {
            var rowIso = item.iso;
            if (
              window.KpiYearStore &&
              rowIso &&
              !KpiYearStore.canWriteDailySalesFrom('sales-data-modal', rowIso)
            ) {
              return;
            }
            state.modalDirty = true;
            var raw = String(inp.value || '').replace(/[^\\d.-]/g, '');
            if (raw !== '') inp.setAttribute('data-last-active', String(Number(raw)));
            else inp.removeAttribute('data-last-active');
            scheduleSalesDataInputRefresh();
          });"""

PSM_INPUT_OLD = """          inp.addEventListener('input', function () {
            state.modalDirty = true;
            updatePastSalesSummary();
            refreshPastSalesTableTotals();
          });"""

PSM_INPUT_NEW = """          inp.addEventListener('input', function () {
            state.modalDirty = true;
            var raw = String(inp.value || '').replace(/[^\\d.-]/g, '');
            if (raw !== '') inp.setAttribute('data-last-active', String(Number(raw)));
            else inp.removeAttribute('data-last-active');
            schedulePastSalesInputRefresh();
          });"""

SDM_REF_INPUT_OLD = """      if (summaryReferenceInput) {
        summaryReferenceInput.addEventListener('input', function () {
          state.modalDirty = true;
          updateSalesDataSummary();
        });"""

SDM_REF_INPUT_NEW = """      if (summaryReferenceInput) {
        summaryReferenceInput.addEventListener('input', function () {
          state.modalDirty = true;
          scheduleSalesDataInputRefresh();
        });"""

# Scheduler near refresh*TableTotals; committed-year cache before has*RowInputSource
SDM_SCHED_ANCHOR = "      function refreshSalesDataTableTotals() {"
SDM_SCHED_BLOCK = """      /* KPI-SDM-INP: キー入力は rAF 集約（summary+totals をキー毎同期実行しない） */
      var __sdmInputRefreshRaf = 0;
      function scheduleSalesDataInputRefresh() {
        if (__sdmInputRefreshRaf) return;
        __sdmInputRefreshRaf = requestAnimationFrame(function () {
          __sdmInputRefreshRaf = 0;
          __sdmCommittedYearCache = Object.create(null);
          updateSalesDataSummary();
          refreshSalesDataTableTotals();
        });
      }
      function refreshSalesDataTableTotals() {"""

PSM_SCHED_ANCHOR = "      function refreshPastSalesTableTotals() {"
PSM_SCHED_BLOCK = """      /* KPI-PSM-INP: キー入力は rAF 集約（summary+totals をキー毎同期実行しない） */
      var __psmInputRefreshRaf = 0;
      function schedulePastSalesInputRefresh() {
        if (__psmInputRefreshRaf) return;
        __psmInputRefreshRaf = requestAnimationFrame(function () {
          __psmInputRefreshRaf = 0;
          __psmCommittedYearCache = Object.create(null);
          updatePastSalesSummary();
          refreshPastSalesTableTotals();
        });
      }
      function refreshPastSalesTableTotals() {"""

SDM_COMMITTED_OLD = """      function hasSalesDataRowInputSource(iso) {
        if (state.rowStateByIso[iso]) return true;
        var y = isoYearFromIso(iso);
        if (!salesDataYearHasCommittedData(y)) return false;"""

SDM_COMMITTED_NEW = """      /* KPI-SDM-INP: year committed 判定を totals 走査中にキャッシュ */
      var __sdmCommittedYearCache = Object.create(null);
      function hasSalesDataRowInputSource(iso) {
        if (state.rowStateByIso[iso]) return true;
        var y = isoYearFromIso(iso);
        var committed;
        if (Object.prototype.hasOwnProperty.call(__sdmCommittedYearCache, y)) {
          committed = __sdmCommittedYearCache[y];
        } else {
          committed = salesDataYearHasCommittedData(y);
          __sdmCommittedYearCache[y] = committed;
        }
        if (!committed) return false;"""

SDM_BUILD_OLD = """      function buildSalesDataTotalsMap(y) {
        var all = gatherYearDays(y);"""

SDM_BUILD_NEW = """      function buildSalesDataTotalsMap(y) {
        __sdmCommittedYearCache = Object.create(null);
        var all = gatherYearDays(y);"""

PSM_COMMITTED_OLD = """      function hasPastSalesRowInputSource(iso) {
        if (state.rowStateByIso[iso]) return true;
        var y = isoYearFromIso(iso);
        if (!pastSalesYearHasCommittedData(y)) return false;"""

PSM_COMMITTED_NEW = """      /* KPI-PSM-INP: year committed 判定を totals 走査中にキャッシュ */
      var __psmCommittedYearCache = Object.create(null);
      function hasPastSalesRowInputSource(iso) {
        if (state.rowStateByIso[iso]) return true;
        var y = isoYearFromIso(iso);
        var committed;
        if (Object.prototype.hasOwnProperty.call(__psmCommittedYearCache, y)) {
          committed = __psmCommittedYearCache[y];
        } else {
          committed = pastSalesYearHasCommittedData(y);
          __psmCommittedYearCache[y] = committed;
        }
        if (!committed) return false;"""

PSM_BUILD_OLD = """      function buildPastSalesTotalsMap(y) {
        var all = gatherYearDays(y);"""

PSM_BUILD_NEW = """      function buildPastSalesTotalsMap(y) {
        __psmCommittedYearCache = Object.create(null);
        var all = gatherYearDays(y);"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    changed = False

    if SDM_MARKER not in text:
        if SDM_SCHED_ANCHOR not in text:
            raise SystemExit(f"SDM refresh anchor miss: {path}")
        if SDM_INPUT_OLD not in text:
            raise SystemExit(f"SDM input handler miss: {path}")
        if SDM_COMMITTED_OLD not in text:
            raise SystemExit(f"SDM hasSalesDataRowInputSource miss: {path}")
        if SDM_BUILD_OLD not in text:
            raise SystemExit(f"SDM buildSalesDataTotalsMap miss: {path}")
        text = text.replace(SDM_SCHED_ANCHOR, SDM_SCHED_BLOCK, 1)
        text = text.replace(SDM_INPUT_OLD, SDM_INPUT_NEW, 1)
        text = text.replace(SDM_COMMITTED_OLD, SDM_COMMITTED_NEW, 1)
        text = text.replace(SDM_BUILD_OLD, SDM_BUILD_NEW, 1)
        if SDM_REF_INPUT_OLD in text:
            text = text.replace(SDM_REF_INPUT_OLD, SDM_REF_INPUT_NEW, 1)
        changed = True
    else:
        print(f"skip SDM (already) {path.relative_to(ROOT)}")

    if PSM_MARKER not in text:
        if PSM_SCHED_ANCHOR not in text:
            raise SystemExit(f"PSM refresh anchor miss: {path}")
        if PSM_INPUT_OLD not in text:
            raise SystemExit(f"PSM input handler miss: {path}")
        if PSM_COMMITTED_OLD not in text:
            raise SystemExit(f"PSM hasPastSalesRowInputSource miss: {path}")
        if PSM_BUILD_OLD not in text:
            raise SystemExit(f"PSM buildPastSalesTotalsMap miss: {path}")
        text = text.replace(PSM_SCHED_ANCHOR, PSM_SCHED_BLOCK, 1)
        text = text.replace(PSM_INPUT_OLD, PSM_INPUT_NEW, 1)
        text = text.replace(PSM_COMMITTED_OLD, PSM_COMMITTED_NEW, 1)
        text = text.replace(PSM_BUILD_OLD, PSM_BUILD_NEW, 1)
        changed = True
    else:
        print(f"skip PSM (already) {path.relative_to(ROOT)}")

    if changed:
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

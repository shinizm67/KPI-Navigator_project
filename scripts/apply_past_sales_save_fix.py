#!/usr/bin/env python3
"""Fix Past Sales modal: save live input values + debounce TW refresh on save."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

READ_LAST_VAL_HELPER = """      function readPastSalesRowLastVal(inp, cb) {
        if (!cb || !cb.checked) return '0';
        if (inp) {
          var raw = String(inp.value || '').replace(/[^\\d.-]/g, '');
          if (raw !== '') {
            var n = Number(raw);
            if (Number.isFinite(n)) return String(Math.round(n));
          }
          var last = inp.getAttribute('data-last-active');
          if (last != null && last !== '') return String(last);
        }
        return '0';
      }

"""

PERSIST_ROW_STATE_OLD = """      function persistRowState(tr) {
        var cb = tr.querySelector('.past-sales-modal__cb');
        var inp = tr.querySelector('.past-sales-modal__sales-input');
        if (!cb) return;
        var iso = cb.getAttribute('data-iso-date');
        if (!iso) return;
        var lastVal =
          inp && inp.getAttribute('data-last-active') != null && inp.getAttribute('data-last-active') !== ''
            ? String(inp.getAttribute('data-last-active'))
            : '0';
        var offNow = !cb.checked;
        var base = baseRowDefaults(iso, isWeekendIso(iso));
        if (offNow === !!base.off && lastVal === String(base.last)) {
          delete state.rowStateByIso[iso];
        } else {
          state.rowStateByIso[iso] = { off: offNow, last: lastVal };
        }
        recomputeModalDirty();
      }"""

PERSIST_ROW_STATE_NEW = """      function persistRowState(tr) {
        var cb = tr.querySelector('.past-sales-modal__cb');
        var inp = tr.querySelector('.past-sales-modal__sales-input');
        if (!cb) return;
        var iso = cb.getAttribute('data-iso-date');
        if (!iso) return;
        var lastVal = readPastSalesRowLastVal(inp, cb);
        var offNow = !cb.checked;
        var base = baseRowDefaults(iso, isWeekendIso(iso));
        if (offNow === !!base.off && lastVal === String(base.last)) {
          delete state.rowStateByIso[iso];
        } else {
          state.rowStateByIso[iso] = { off: offNow, last: lastVal };
        }
        recomputeModalDirty();
      }"""

SAVE_MODAL_OLD = """      function savePastSalesModal() {
        var ps = ensurePastSalesDaily();
        ps.salesByDate = ps.salesByDate || {};
        ps.businessDayByDate = ps.businessDayByDate || {};
        var map = ps.salesByDate;
        var bmap = ps.businessDayByDate;
        var all = gatherYearDays(state.year);
        for (var i = 0; i < all.length; i++) {
          var item = all[i];
          var defs = getRowDefaults(item.iso, item.isWk);
          map[item.iso] = defs.off ? 0 : Math.round(Number(defs.last));
          bmap[item.iso] = !defs.off;
        }
        state.rowStateByIso = {};
        state.modalDirty = false;
        undoStack = [];
        syncUndoButton();
        sessionSaved = true;
        persistPastSalesShared();
        document.dispatchEvent(
          new CustomEvent('annual:pastSalesSaved', { detail: { year: state.year } })
        );
        document.dispatchEvent(
          new CustomEvent('annual:businessDayMapChanged', {
            detail: { year: state.year, source: 'past-sales-modal' }
          })
        );
        document.dispatchEvent(
          new CustomEvent('annual:salesMapChanged', {
            detail: { year: state.year, source: 'past-sales-modal' }
          })
        );
        renderPastSalesTable();
        updatePastSalesSummary();
      }"""

SAVE_MODAL_NEW = """      function savePastSalesModal() {
        var ps = ensurePastSalesDaily();
        ps.salesByDate = ps.salesByDate || {};
        ps.businessDayByDate = ps.businessDayByDate || {};
        var map = ps.salesByDate;
        var bmap = ps.businessDayByDate;
        var all = gatherYearDays(state.year);
        for (var i = 0; i < all.length; i++) {
          var item = all[i];
          var defs = getPastSalesRowDefaultsLive(item.iso, item.isWk);
          map[item.iso] = defs.off ? 0 : Math.round(Number(defs.last));
          bmap[item.iso] = !defs.off;
        }
        state.rowStateByIso = {};
        state.modalDirty = false;
        undoStack = [];
        syncUndoButton();
        sessionSaved = true;
        persistPastSalesShared({ limitToYear: state.year });
        document.dispatchEvent(
          new CustomEvent('annual:pastSalesSaved', { detail: { year: state.year } })
        );
        refreshPastSalesTableTotals();
        updatePastSalesSummary();
      }"""

TW_LISTENER_BLOCK_OLD = """      document.addEventListener('annual:businessDayMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:salesMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:dailySalesChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:businessDayChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:annualPlanChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:dailyTargetModeChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:weekdayBaselineChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastSalesSaved', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastSalesMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastBusinessDayMapChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);"""

TW_LISTENER_BLOCK_NEW = TW_LISTENER_BLOCK_OLD.replace(
    "renderAnnualDailyTimeline(cy, { preserveScroll: true });",
    "scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });",
)

MARKER_PARSE_SALES = "      function parseSalesInputRaw(inp) {"


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    if "readPastSalesRowLastVal" not in text:
        idx = text.find(MARKER_PARSE_SALES)
        if idx < 0:
            raise SystemExit(f"{path}: parseSalesInputRaw anchor missing")
        text = text[:idx] + READ_LAST_VAL_HELPER + text[idx:]

    if PERSIST_ROW_STATE_OLD not in text:
        if "readPastSalesRowLastVal(inp, cb)" in text:
            pass
        else:
            raise SystemExit(f"{path}: persistRowState block missing")
    else:
        text = text.replace(PERSIST_ROW_STATE_OLD, PERSIST_ROW_STATE_NEW, 1)

    if SAVE_MODAL_OLD not in text:
        if "getPastSalesRowDefaultsLive(item.iso, item.isWk)" in text and "refreshPastSalesTableTotals();" in text:
            pass
        else:
            raise SystemExit(f"{path}: savePastSalesModal block missing")
    else:
        text = text.replace(SAVE_MODAL_OLD, SAVE_MODAL_NEW, 1)

    if TW_LISTENER_BLOCK_OLD in text:
        text = text.replace(TW_LISTENER_BLOCK_OLD, TW_LISTENER_BLOCK_NEW, 1)
    elif "scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });" not in text:
        raise SystemExit(f"{path}: TW listener block missing")

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

#!/usr/bin/env python3
"""Sync MEP date-rail column widths to match table body columns (zoom-safe)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

CSS_OLD = """    .monthly-edit-float__date-rail-scroll {
      overflow-x: auto;
      overflow-y: hidden;
      box-sizing: border-box;
    }"""

CSS_NEW = """    .monthly-edit-float__date-rail-scroll {
      overflow-x: auto;
      overflow-y: hidden;
      box-sizing: border-box;
      padding: 0 10px 0 0;
    }"""

CSS_TABLE_OLD = """    .monthly-edit-float__date-rail-table {
      border-collapse: separate;
      border-spacing: 0;
    }"""

CSS_TABLE_NEW = """    .monthly-edit-float__date-rail-table {
      border-collapse: separate;
      border-spacing: 0;
      table-layout: fixed;
    }"""

JS_OLD = """      function syncDateRailScroll() {
        if (!dateRailScroll || !scroller) return;
        dateRailScroll.scrollLeft = scroller.scrollLeft;
      }"""

JS_NEW = """      function syncDateRailScroll() {
        if (!dateRailScroll || !scroller) return;
        dateRailScroll.scrollLeft = scroller.scrollLeft;
      }
      var __mefDateRailColSyncRaf = 0;
      function syncDateRailColumnWidths() {
        if (!tbl || !dateRailScale) return;
        var ths = dateRailScale.querySelectorAll('.monthly-edit-float__date-rail-th');
        if (!ths || !ths.length) return;
        var refRow = null;
        var trs = tbl.querySelectorAll('tbody tr');
        for (var ri = 0; ri < trs.length; ri++) {
          var tr = trs[ri];
          if (tr.classList.contains('monthly-edit-float__strip-row')) continue;
          if (tr.classList.contains('monthly-edit-float__bottom-spacer')) continue;
          var cells = tr.querySelectorAll(':scope > td');
          if (cells.length === ths.length) {
            refRow = tr;
            break;
          }
        }
        if (!refRow) return;
        var tds = refRow.querySelectorAll(':scope > td');
        var z = currentScale > 0 ? currentScale : 1;
        var tableLeft = tbl.getBoundingClientRect().left;
        var firstTdLeft = tds[0].getBoundingClientRect().left;
        var borderPad = Math.max(0, Math.round((firstTdLeft - tableLeft) / z));
        dateRailScale.style.paddingLeft = borderPad ? borderPad + 'px' : '';
        for (var i = 0; i < ths.length; i++) {
          var w = Math.max(1, Math.round(tds[i].getBoundingClientRect().width / z));
          ths[i].style.width = w + 'px';
          ths[i].style.minWidth = w + 'px';
          ths[i].style.maxWidth = w + 'px';
        }
        var dateRailTable = dateRailScale.querySelector('.monthly-edit-float__date-rail-table');
        if (dateRailTable) {
          dateRailTable.style.width = Math.max(1, Math.round(tbl.getBoundingClientRect().width / z)) + 'px';
        }
      }
      function queueSyncDateRailColumnWidths() {
        if (__mefDateRailColSyncRaf) cancelAnimationFrame(__mefDateRailColSyncRaf);
        __mefDateRailColSyncRaf = requestAnimationFrame(function () {
          __mefDateRailColSyncRaf = requestAnimationFrame(function () {
            __mefDateRailColSyncRaf = 0;
            syncDateRailColumnWidths();
            syncDateRailScroll();
          });
        });
      }"""

APPLY_ZOOM_OLD = """        syncLabelScroll();
        pinLabelsToRight();
      }
      function bindZoomStepButton(btn, sign) {"""

APPLY_ZOOM_NEW = """        syncLabelScroll();
        pinLabelsToRight();
        queueSyncDateRailColumnWidths();
      }
      function bindZoomStepButton(btn, sign) {"""

BUILD_GRID_OLD = """        syncDateRailScroll();
        if (!tbl.hasAttribute('data-kpi-fill-bound')) {"""

BUILD_GRID_NEW = """        queueSyncDateRailColumnWidths();
        if (!tbl.hasAttribute('data-kpi-fill-bound')) {"""

INIT_ZOOM_OLD = """      if (zoom) {
        zoom.addEventListener('input', applyZoom);
        zoom.addEventListener('change', applyZoom);
        applyZoom();
      }"""

INIT_ZOOM_NEW = """      if (typeof ResizeObserver !== 'undefined' && tbl) {
        try {
          var __mefColResizeObs = new ResizeObserver(function () {
            queueSyncDateRailColumnWidths();
          });
          __mefColResizeObs.observe(tbl);
        } catch (_mefObsErr) {}
      }
      window.addEventListener('resize', function () {
        queueSyncDateRailColumnWidths();
      });
      if (zoom) {
        zoom.addEventListener('input', applyZoom);
        zoom.addEventListener('change', applyZoom);
      }"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n", 1)[0].strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, CSS_OLD, CSS_NEW, "date-rail-scroll padding")
    text = replace_once(text, CSS_TABLE_OLD, CSS_TABLE_NEW, "date-rail-table layout")
    text = replace_once(text, JS_OLD, JS_NEW, "syncDateRailColumnWidths")
    text = replace_once(text, APPLY_ZOOM_OLD, APPLY_ZOOM_NEW, "applyZoom queue")
    text = replace_once(text, BUILD_GRID_OLD, BUILD_GRID_NEW, "buildGrid queue")
    text = replace_once(text, INIT_ZOOM_OLD, INIT_ZOOM_NEW, "resize observer")
    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> None:
    for path in TARGETS:
        patch(path)


if __name__ == "__main__":
    main()

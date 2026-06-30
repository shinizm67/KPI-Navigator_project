#!/usr/bin/env python3
"""Fix Sales Data path toggle guards (Phase 5c regression after openModal guard hook)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "app/annual/index.html", ROOT / "en/app/annual/index.html"]

SALES_OPEN_OLD = """          if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
            window.__KPI_SALES_INPUT_PATH_UI.sync();
          }
          if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
            window.__KPI_EDIT_GUARDS.applyAll();
          }
          modal.removeAttribute('hidden');
          document.body.style.overflow = 'hidden';"""

SALES_OPEN_NEW = """          if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
            window.__KPI_SALES_INPUT_PATH_UI.sync();
          }
          modal.removeAttribute('hidden');
          document.body.style.overflow = 'hidden';
          if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
            window.__KPI_EDIT_GUARDS.applyAll();
          }"""

RENDER_TAIL_OLD = """        updateFilterToggleActive();
        updateSalesDataSummary();
      }

      function scrollToViewMonth() {"""

RENDER_TAIL_NEW = """        updateFilterToggleActive();
        updateSalesDataSummary();
        if (
          modal &&
          !modal.hasAttribute('hidden') &&
          window.__KPI_EDIT_GUARDS &&
          typeof window.__KPI_EDIT_GUARDS.applyAll === 'function'
        ) {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
      }

      function scrollToViewMonth() {"""

ROW_OFF_OLD = """        if (off) {
          inp.readOnly = true;
          inp.value = fmtSalesInput(0);
        } else {
          inp.readOnly = false;
          var last = inp.getAttribute('data-last-active');
          inp.value = fmtSalesInput(last != null && last !== '' ? Number(last) : 0);
        }
        persistRowState(tr);
        applySalesDataTotalsToTable();
      }

      function onSalesDataTableInput(ev) {"""

ROW_OFF_NEW = """        var pathBlocked =
          window.__KPI_EDIT_GUARDS &&
          typeof window.__KPI_EDIT_GUARDS.mepSalesPathActive === 'function' &&
          window.__KPI_EDIT_GUARDS.mepSalesPathActive();
        if (off) {
          inp.readOnly = true;
          inp.value = fmtSalesInput(0);
        } else if (pathBlocked) {
          inp.readOnly = true;
          var lastBlocked = inp.getAttribute('data-last-active');
          inp.value = fmtSalesInput(
            lastBlocked != null && lastBlocked !== '' ? Number(lastBlocked) : 0
          );
        } else {
          inp.readOnly = false;
          var last = inp.getAttribute('data-last-active');
          inp.value = fmtSalesInput(last != null && last !== '' ? Number(last) : 0);
        }
        persistRowState(tr);
        applySalesDataTotalsToTable();
      }

      function onSalesDataTableInput(ev) {"""

INPUT_GUARD_OLD = """      function onSalesDataTableInput(ev) {
        var t = ev.target;
        if (!t || !t.classList || !t.classList.contains('sales-data-modal__sales-input')) return;
        var tr2 = t.closest('tr[data-iso-date]');
        if (!tr2) return;"""

INPUT_GUARD_NEW = """      function onSalesDataTableInput(ev) {
        var t = ev.target;
        if (!t || !t.classList || !t.classList.contains('sales-data-modal__sales-input')) return;
        var tr2 = t.closest('tr[data-iso-date]');
        if (!tr2) return;
        var isoIn = tr2.getAttribute('data-iso-date');
        if (
          window.KpiYearStore &&
          isoIn &&
          !KpiYearStore.canWriteDailySalesFrom('sales-data-modal', isoIn)
        ) {
          return;
        }"""

CB_GUARD_OLD = """        if (t.classList.contains('sales-data-modal__cb')) {
          pushUndoSnapshot();
          var tr = t.closest('tr[data-iso-date]');
          if (tr) {
            noteSalesDataEditedIso(tr.getAttribute('data-iso-date'));
            salesDataRowApplyOffState(tr);
          }
          return;
        }"""

CB_GUARD_NEW = """        if (t.classList.contains('sales-data-modal__cb')) {
          var trCb = t.closest('tr[data-iso-date]');
          var isoCb = trCb && trCb.getAttribute('data-iso-date');
          if (
            window.KpiYearStore &&
            isoCb &&
            !KpiYearStore.canWriteBusinessDayFrom('sales-data-modal', isoCb)
          ) {
            var defsCb = getRowDefaults(isoCb, isWeekendIso(isoCb));
            t.checked = !defsCb.off;
            return;
          }
          pushUndoSnapshot();
          var tr = trCb;
          if (tr) {
            noteSalesDataEditedIso(tr.getAttribute('data-iso-date'));
            salesDataRowApplyOffState(tr);
          }
          return;
        }"""

ANNUAL_EDIT_OPEN_OLD = """        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');"""

ANNUAL_EDIT_OPEN_NEW = """        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }"""

PATCHES = [
    (SALES_OPEN_OLD, SALES_OPEN_NEW, "sales-data openModal guard order"),
    (RENDER_TAIL_OLD, RENDER_TAIL_NEW, "renderSalesDataTable guard reapply"),
    (ROW_OFF_OLD, ROW_OFF_NEW, "salesDataRowApplyOffState path block"),
    (INPUT_GUARD_OLD, INPUT_GUARD_NEW, "onSalesDataTableInput canWrite guard"),
    (CB_GUARD_OLD, CB_GUARD_NEW, "onSalesDataTableChange cb canWrite guard"),
    (ANNUAL_EDIT_OPEN_OLD, ANNUAL_EDIT_OPEN_NEW, "annual-edit openModal guard order"),
]


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new, label in PATCHES:
        if old not in text:
            if new in text:
                continue
            raise SystemExit(f"{path.relative_to(ROOT)}: missing patch anchor ({label})")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for p in TARGETS:
        patch_file(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

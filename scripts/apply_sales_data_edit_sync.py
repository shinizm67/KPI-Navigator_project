#!/usr/bin/env python3
"""Edit path guards + lease hooks + Sales Data modal open/save fixes (Annual + Monthly)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_kpi_edit_guards import inject_edit_guards_js, KPI_EDIT_GUARDS_MARKER  # noqa: E402
from kpi_phase5_client import KPI_EDIT_LEASE_HOOKS_MARKER, edit_lease_hooks_js  # noqa: E402

ANNUAL_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]
MONTHLY_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

SALES_DATA_OPEN_OLD = """      function openModal() {
        lastFocusEl = document.activeElement;
        state.rowStateByIso = {};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();
        setSalesDataTab('input');
        updateSalesDataSummary();
        renderSalesDataTable();
        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
          window.__KPI_SALES_INPUT_PATH_UI.sync();
        }
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }"""

SALES_DATA_OPEN_NEW = """      function openModal() {
        lastFocusEl = document.activeElement;
        state.rowStateByIso = {};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();
        setSalesDataTab('input');
        updateSalesDataSummary();
        renderSalesDataTable();
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function') {
          if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '売上データ' : 'Sales Data')) {
            return;
          }
        }
        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
          window.__KPI_SALES_INPUT_PATH_UI.sync();
        }
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }"""

ANNUAL_EDIT_OPEN_OLD = """      function openModal() {
        lastFocusEl = document.activeElement;
        state.rowStateByIso = {};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();
        renderTable();
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        scrollToViewMonth();
        state.modalDirty = false;
        if (btnClose) btnClose.focus();
      }"""

ANNUAL_EDIT_OPEN_NEW = """      function openModal() {
        lastFocusEl = document.activeElement;
        state.rowStateByIso = {};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();
        renderTable();
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function') {
          if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '年次編集' : 'Annual Edit')) {
            return;
          }
        }
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
        document.body.style.overflow = 'hidden';
        scrollToViewMonth();
        state.modalDirty = false;
        if (btnClose) btnClose.focus();
      }"""

ANNUAL_EDIT_CLOSE_OLD = """      function closeModal() {
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
        else btnEdit.focus();
      }"""

ANNUAL_PAGE_EDIT_OPEN_OLD = """        renderTable();
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
        document.body.style.overflow = 'hidden';
        scrollToViewMonth();
        state.modalDirty = false;
        sessionSaved = false;"""

ANNUAL_PAGE_EDIT_OPEN_NEW = """        renderTable();
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function') {
          if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '年次編集' : 'Annual Edit')) {
            return;
          }
        }
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
        document.body.style.overflow = 'hidden';
        scrollToViewMonth();
        state.modalDirty = false;
        sessionSaved = false;"""

ANNUAL_PAGE_EDIT_CLOSE_OLD = """      function closeModal() {
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
        else btnEdit.focus();
      }

      btnEdit.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
      });
      if (btnClose) btnClose.addEventListener('click', requestCloseModal);
      if (backdrop) backdrop.addEventListener('click', requestCloseModal);
      if (btnSave) btnSave.addEventListener('click', saveModalEdits);"""

ANNUAL_PAGE_EDIT_CLOSE_NEW = """      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
        else btnEdit.focus();
      }

      btnEdit.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
      });
      if (btnClose) btnClose.addEventListener('click', requestCloseModal);
      if (backdrop) backdrop.addEventListener('click', requestCloseModal);
      if (btnSave) btnSave.addEventListener('click', saveModalEdits);"""

COMMITTED_DATA_OLD = """      function salesDataYearHasCommittedData(y) {
        y = Number(y);
        if (!isFinite(y)) return false;
        var prefix = y + '-';
        var ps = ensureSalesDataDaily();
        var map = ps.targetSalesByDate || {};
        for (var k in map) {
          if (Object.prototype.hasOwnProperty.call(map, k) && k.indexOf(prefix) === 0) return true;
        }
        var row = state.rowStateByIso || {};
        for (var iso in row) {
          if (Object.prototype.hasOwnProperty.call(row, iso) && iso.indexOf(prefix) === 0) return true;
        }
        return false;
      }"""

COMMITTED_DATA_NEW = """      function salesDataYearHasCommittedData(y) {
        y = Number(y);
        if (!isFinite(y)) return false;
        var prefix = y + '-';
        var ps = ensureSalesDataDaily();
        var map = ps.targetSalesByDate || {};
        for (var k in map) {
          if (Object.prototype.hasOwnProperty.call(map, k) && k.indexOf(prefix) === 0) return true;
        }
        var bmap = ps.businessDayByDate || {};
        for (var bk in bmap) {
          if (Object.prototype.hasOwnProperty.call(bmap, bk) && bk.indexOf(prefix) === 0) return true;
        }
        var row = state.rowStateByIso || {};
        for (var iso in row) {
          if (Object.prototype.hasOwnProperty.call(row, iso) && iso.indexOf(prefix) === 0) return true;
        }
        return false;
      }"""


ANNUAL_EDIT_CLOSE_NEW = """      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
        else btnEdit.focus();
      }"""


STORE_CAN_WRITE_OLD = """          if (path !== getDailySalesInputPath()) return false;
          return holdsEditLease('daily-sales');
        }"""

STORE_CAN_WRITE_NEW = """          if (path !== getDailySalesInputPath()) return false;
          if (src.indexOf('sales-data-save') >= 0) return true;
          return holdsEditLease('daily-sales');
        }"""

ALL_STORE_PAGES = ANNUAL_PAGES + MONTHLY_PAGES + [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]


def patch_store_can_write(text: str) -> str:
    if STORE_CAN_WRITE_NEW.split("\n")[1].strip() in text:
        return text
    if STORE_CAN_WRITE_OLD not in text:
        raise SystemExit("canWriteDailySalesFrom patch block missing")
    return text.replace(STORE_CAN_WRITE_OLD, STORE_CAN_WRITE_NEW, 1)


def inject_guards_if_missing(text: str) -> str:
    if KPI_EDIT_GUARDS_MARKER in text and "window.__KPI_EDIT_GUARDS" in text:
        return text
    return inject_edit_guards_js(text)


def inject_lease_if_missing(text: str) -> str:
    if KPI_EDIT_LEASE_HOOKS_MARKER in text and "window.__KPI_EDIT_LEASE" in text:
        return text
    block = edit_lease_hooks_js().rstrip() + "\n"
    anchor = KPI_EDIT_GUARDS_MARKER
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("KPI-EDIT-GUARDS anchor not found for lease inject")
    end = text.find("})();", pos)
    if end < 0:
        raise SystemExit("KPI-EDIT-GUARDS block end not found")
    end = text.find("\n", end) + 1
    return text[:end] + "\n" + block + text[end:]


def patch_annual_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_guards_if_missing(text)
    text = inject_lease_if_missing(text)
    if SALES_DATA_OPEN_OLD in text:
        text = text.replace(SALES_DATA_OPEN_OLD, SALES_DATA_OPEN_NEW, 1)
    elif "tryAcquire(isJa ? '売上データ'" not in text:
        raise SystemExit(f"sales data openModal patch missing: {path}")
    if COMMITTED_DATA_OLD in text:
        text = text.replace(COMMITTED_DATA_OLD, COMMITTED_DATA_NEW, 1)
    elif "businessDayByDate || {}" not in text.split("salesDataYearHasCommittedData")[1][:600]:
        raise SystemExit(f"salesDataYearHasCommittedData patch missing: {path}")
    if ANNUAL_PAGE_EDIT_OPEN_OLD in text:
        text = text.replace(ANNUAL_PAGE_EDIT_OPEN_OLD, ANNUAL_PAGE_EDIT_OPEN_NEW, 1)
    if ANNUAL_PAGE_EDIT_CLOSE_OLD in text:
        text = text.replace(ANNUAL_PAGE_EDIT_CLOSE_OLD, ANNUAL_PAGE_EDIT_CLOSE_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote annual {path.relative_to(ROOT)}")


def patch_monthly_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_guards_if_missing(text)
    text = inject_lease_if_missing(text)
    if ANNUAL_EDIT_OPEN_OLD in text:
        text = text.replace(ANNUAL_EDIT_OPEN_OLD, ANNUAL_EDIT_OPEN_NEW, 1)
    elif "tryAcquire(isJa ? '年次編集'" not in text:
        raise SystemExit(f"monthly annual-edit openModal patch missing: {path}")
    if ANNUAL_EDIT_CLOSE_OLD in text:
        text = text.replace(ANNUAL_EDIT_CLOSE_OLD, ANNUAL_EDIT_CLOSE_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote monthly {path.relative_to(ROOT)}")


def main() -> int:
    for path in ANNUAL_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_annual_page(path)
    for path in MONTHLY_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_monthly_page(path)
    for path in ALL_STORE_PAGES:
        text = path.read_text(encoding="utf-8")
        if "function canWriteDailySalesFrom" not in text:
            continue
        text2 = patch_store_can_write(text)
        if text2 != text:
            path.write_text(text2, encoding="utf-8")
            print(f"wrote store {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

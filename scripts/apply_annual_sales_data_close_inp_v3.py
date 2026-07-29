#!/usr/bin/env python3
"""Sales Data close/open INP v3: defer 365-row skip until after open paint; restore after focus."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

MARKER = "KPI-SDM-CLOSE-INP-V3"

OPEN_OLD = """        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        document.body.style.overflow = 'hidden';
        document.body.classList.add('sales-data-modal-open');
        syncUndoButton();
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            if (!modal || modal.hasAttribute('hidden')) return;
            syncYearMonthFromApp();
            syncColheadDatePickerValue();
            clearDateFilterUi();
            closeSalesSortPanel();
            setSalesDataTab('input');
            updateSalesDataSummary();
            renderSalesDataTable();
            if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
              window.__KPI_SALES_INPUT_PATH_UI.sync();
            }
            if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.sync === 'function') {
              window.__SDM_DAILY_TARGET_MODE.sync();
            }
            if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {
              window.__SDM_DAILY_TARGET_MODE.closePanel();
            }
            if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
              window.__KPI_EDIT_GUARDS.applyAll();
            }
            scrollToViewMonth();
            if (btnClose) btnClose.focus();
          });
        });
      }"""

OPEN_NEW = """        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        document.body.style.overflow = 'hidden';
        syncUndoButton();
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            if (!modal || modal.hasAttribute('hidden')) return;
            syncYearMonthFromApp();
            syncColheadDatePickerValue();
            clearDateFilterUi();
            closeSalesSortPanel();
            setSalesDataTab('input');
            updateSalesDataSummary();
            renderSalesDataTable();
            if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
              window.__KPI_SALES_INPUT_PATH_UI.sync();
            }
            if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.sync === 'function') {
              window.__SDM_DAILY_TARGET_MODE.sync();
            }
            if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {
              window.__SDM_DAILY_TARGET_MODE.closePanel();
            }
            if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
              window.__KPI_EDIT_GUARDS.applyAll();
            }
            scrollToViewMonth();
            if (btnClose) btnClose.focus();
            /* 開くINPの後で背面365行をスキップ（閉じる用の準備） */
            document.body.classList.add('sales-data-modal-open');
          });
        });
      }"""

CLOSE_OLD = """      /* KPI-SDM-CLOSE-INP-V2: 殻だけ先に消す → 次ペイント後に365行復帰・後処理 */
      function closeModal() {
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            hideSalesDataCloseChooser();
            closeDateFilterPanel();
            closeSalesSortPanel();
            if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {
              window.__SDM_DAILY_TARGET_MODE.closePanel();
            }
            document.body.classList.remove('sales-data-modal-open');
            if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
            else if (openBtn) openBtn.focus();
            if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
              window.__KPI_EDIT_LEASE.release();
            }
            if (
              window.__ANNUAL_UI &&
              typeof window.__ANNUAL_UI.scheduleSyncBusinessDayDisplayFromDailyMap === 'function'
            ) {
              window.__ANNUAL_UI.scheduleSyncBusinessDayDisplayFromDailyMap();
            } else if (
              window.__ANNUAL_UI &&
              typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
            ) {
              window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
            }
          });
        });
      }"""

CLOSE_NEW = """      /* KPI-SDM-CLOSE-INP-V3: 殻だけ先に消す → フォーカス復帰後に365行復帰（keyboard INP分離） */
      function closeModal() {
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            hideSalesDataCloseChooser();
            closeDateFilterPanel();
            closeSalesSortPanel();
            if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {
              window.__SDM_DAILY_TARGET_MODE.closePanel();
            }
            /* 365行はまだスキップしたまま focus（keyboard 次描画を軽く保つ） */
            if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
            else if (openBtn) openBtn.focus();
            if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
              window.__KPI_EDIT_LEASE.release();
            }
            if (
              window.__ANNUAL_UI &&
              typeof window.__ANNUAL_UI.scheduleSyncBusinessDayDisplayFromDailyMap === 'function'
            ) {
              window.__ANNUAL_UI.scheduleSyncBusinessDayDisplayFromDailyMap();
            } else if (
              window.__ANNUAL_UI &&
              typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
            ) {
              window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
            }
            requestAnimationFrame(function () {
              document.body.classList.remove('sales-data-modal-open');
            });
          });
        });
      }"""

CSS_NOTE_OLD = "    /* KPI-SDM-CLOSE-INP-V2: モーダル表示中は日次365行の描画をスキップ（閉じるINP用） */"
CSS_NOTE_NEW = "    /* KPI-SDM-CLOSE-INP-V3: モーダル表示中は日次365行の描画をスキップ（閉じるINP用・開く後に付与） */"


def patch_page(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already) {rel}")
        return
    if OPEN_OLD not in text:
        raise SystemExit(f"open block miss: {rel}")
    if CLOSE_OLD not in text:
        raise SystemExit(f"close block miss: {rel}")
    text = text.replace(OPEN_OLD, OPEN_NEW, 1)
    text = text.replace(CLOSE_OLD, CLOSE_NEW, 1)
    if CSS_NOTE_OLD in text:
        text = text.replace(CSS_NOTE_OLD, CSS_NOTE_NEW, 1)
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing after patch: {rel}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {rel}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

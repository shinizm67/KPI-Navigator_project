#!/usr/bin/env python3
"""Sales Data close INP v2: skip 365-row repaint on close (content-visibility + double rAF)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

MARKER = "KPI-SDM-CLOSE-INP-V2"

CSS_ANCHOR = """    body.kpi-mode-switching #annual-daily-rows,
    body.kpi-mode-switching .annual-daily-focus-scroll,
    body.kpi-mode-switching .annual-daily-focus-global-scroll {
      content-visibility: hidden;
      contain: strict;
    }
    .annual-frame-img {"""

CSS_NEW = """    body.kpi-mode-switching #annual-daily-rows,
    body.kpi-mode-switching .annual-daily-focus-scroll,
    body.kpi-mode-switching .annual-daily-focus-global-scroll {
      content-visibility: hidden;
      contain: strict;
    }
    /* KPI-SDM-CLOSE-INP-V2: モーダル表示中は日次365行の描画をスキップ（閉じるINP用） */
    body.sales-data-modal-open #annual-daily-rows,
    body.sales-data-modal-open .annual-daily-focus-scroll,
    body.sales-data-modal-open .annual-daily-focus-global-scroll {
      content-visibility: hidden;
      contain: strict;
    }
    .annual-frame-img {"""

OPEN_OVERFLOW_OLD = """        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        document.body.style.overflow = 'hidden';
        syncUndoButton();"""

OPEN_OVERFLOW_NEW = """        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        document.body.style.overflow = 'hidden';
        document.body.classList.add('sales-data-modal-open');
        syncUndoButton();"""

CLOSE_OLD = """      /* KPI-SDM-CLOSE-INP: 先に閉じる描画を完了し、営業日再計算は schedule へ */
      function closeModal() {
        hideSalesDataCloseChooser();
        closeDateFilterPanel();
        closeSalesSortPanel();
        if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {
          window.__SDM_DAILY_TARGET_MODE.closePanel();
        }
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
        else if (openBtn) openBtn.focus();
        requestAnimationFrame(function () {
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
      }"""

CLOSE_NEW = """      /* KPI-SDM-CLOSE-INP-V2: 殻だけ先に消す → 次ペイント後に365行復帰・後処理 */
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


def patch_page(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already) {rel}")
        return
    if CSS_ANCHOR not in text:
        raise SystemExit(f"CSS anchor miss: {rel}")
    if OPEN_OVERFLOW_OLD not in text:
        raise SystemExit(f"openModal overflow block miss: {rel}")
    if CLOSE_OLD not in text:
        raise SystemExit(f"closeModal block miss: {rel}")
    text = text.replace(CSS_ANCHOR, CSS_NEW, 1)
    text = text.replace(OPEN_OVERFLOW_OLD, OPEN_OVERFLOW_NEW, 1)
    text = text.replace(CLOSE_OLD, CLOSE_NEW, 1)
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

#!/usr/bin/env python3
"""Annual Sales Data close INP: cockpit BD O(n) + defer sync after modal hide."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cockpit_business_days_perf_client import (  # noqa: E402
    COCKPIT_BD_BLOCK_NEW,
    COCKPIT_BD_PERF_MARKER,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

MARKER = "KPI-SDM-CLOSE-INP"

# Match through the FINAL standalone init call only (not listener bodies).
BD_BLOCK_RE = re.compile(
    r"      /\* KPI-COCKPIT-BUSINESS-DAYS \*/\n"
    r"(?!      /\* KPI-COCKPIT-BUSINESS-DAYS-PERF \*/)"
    r"[\s\S]*?"
    r"\n      syncBusinessDayDisplayFromDailyMap\(\);\n"
    r"(?=    \}\)\(\);\n)",
    re.M,
)

ANNUAL_BD_NEW = COCKPIT_BD_BLOCK_NEW.replace(
    "      document.addEventListener('annual:editModalSaved', scheduleSyncBusinessDayDisplayFromDailyMap);",
    "      document.addEventListener('annual:calendarYearChanged', scheduleSyncBusinessDayDisplayFromDailyMap);\n"
    "      document.addEventListener('annual:editModalSaved', scheduleSyncBusinessDayDisplayFromDailyMap);",
    1,
)
# Ensure trailing newline like OLD (without swallowing the following `})();`)
if not ANNUAL_BD_NEW.endswith("\n"):
    ANNUAL_BD_NEW += "\n"

SDM_CLOSE_OLD = """      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        hideSalesDataCloseChooser();
        closeDateFilterPanel();
        closeSalesSortPanel();
        if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {
          window.__SDM_DAILY_TARGET_MODE.closePanel();
        }
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function') {
          window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
        }
        if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
        else if (openBtn) openBtn.focus();
      }"""

SDM_CLOSE_NEW = """      /* KPI-SDM-CLOSE-INP: 先に閉じる描画を完了し、営業日再計算は schedule へ */
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

SDM_REQUEST_CLOSE_OLD = """      function requestCloseModal() {
        requestSalesDataLeaveNavigation().then(function (ok) {
          if (ok) closeModal();
        });
      }"""

SDM_REQUEST_CLOSE_NEW = """      function requestCloseModal() {
        /* KPI-SDM-CLOSE-INP: 未保存なしは Promise を挟まず即 close */
        if (!hasSalesDataUnsavedChanges()) {
          closeModal();
          return;
        }
        requestSalesDataLeaveNavigation().then(function (ok) {
          if (ok) closeModal();
        });
      }"""


def patch_bd(text: str, rel: str) -> str:
    if COCKPIT_BD_PERF_MARKER in text:
        print(f"skip BD perf (already) {rel}")
        return text
    new_text, n = BD_BLOCK_RE.subn(ANNUAL_BD_NEW, text, count=1)
    if n != 1:
        raise SystemExit(f"annual BD block miss: {rel}")
    return new_text


def patch_close(text: str, rel: str) -> str:
    if MARKER in text:
        print(f"skip close INP (already) {rel}")
        return text
    if SDM_CLOSE_OLD not in text:
        raise SystemExit(f"sales-data closeModal miss: {rel}")
    if SDM_REQUEST_CLOSE_OLD not in text:
        raise SystemExit(f"sales-data requestCloseModal miss: {rel}")
    text = text.replace(SDM_CLOSE_OLD, SDM_CLOSE_NEW, 1)
    text = text.replace(SDM_REQUEST_CLOSE_OLD, SDM_REQUEST_CLOSE_NEW, 1)
    return text


def patch_page(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    before = text
    text = patch_bd(text, rel)
    text = patch_close(text, rel)
    if text != before:
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

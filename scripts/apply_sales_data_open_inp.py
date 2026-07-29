#!/usr/bin/env python3
"""Sales Data open INP: show shell first, defer year-table build to rAF + DocumentFragment."""

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

MARKER = "KPI-SDM-OPEN-INP"

OPEN_RE = re.compile(
    r"      function openModal\(\) \{\n"
    r"        lastFocusEl = document\.activeElement;\n"
    r"        state\.rowStateByIso = \{\};\n"
    r"        state\.salesPinnedAmount = null;\n"
    r"        state\.salesAmountSort = null;\n"
    r"        syncYearMonthFromApp\(\);\n"
    r"        syncColheadDatePickerValue\(\);\n"
    r"        clearDateFilterUi\(\);\n"
    r"        closeSalesSortPanel\(\);\n"
    r"        setSalesDataTab\('input'\);\n"
    r"        updateSalesDataSummary\(\);\n"
    r"        renderSalesDataTable\(\);\n"
    r"        if \(window\.__KPI_EDIT_LEASE && typeof window\.__KPI_EDIT_LEASE\.tryAcquire === 'function'\) \{\n"
    r"          if \(!window\.__KPI_EDIT_LEASE\.tryAcquire\((?P<lease>.+?)\)\) \{\n"
    r"            return;\n"
    r"          \}\n"
    r"        \}\n"
    r"        modal\.removeAttribute\('hidden'\);\n"
    r"        modal\.removeAttribute\('aria-hidden'\);\n"
    r"        if \(window\.__KPI_SALES_INPUT_PATH_UI && typeof window\.__KPI_SALES_INPUT_PATH_UI\.sync === 'function'\) \{\n"
    r"          window\.__KPI_SALES_INPUT_PATH_UI\.sync\(\);\n"
    r"        \}\n"
    r"        if \(window\.__SDM_DAILY_TARGET_MODE && typeof window\.__SDM_DAILY_TARGET_MODE\.sync === 'function'\) \{\n"
    r"          window\.__SDM_DAILY_TARGET_MODE\.sync\(\);\n"
    r"        \}\n"
    r"        if \(window\.__SDM_DAILY_TARGET_MODE && typeof window\.__SDM_DAILY_TARGET_MODE\.closePanel === 'function'\) \{\n"
    r"          window\.__SDM_DAILY_TARGET_MODE\.closePanel\(\);\n"
    r"        \}\n"
    r"        if \(window\.__KPI_EDIT_GUARDS && typeof window\.__KPI_EDIT_GUARDS\.applyAll === 'function'\) \{\n"
    r"          window\.__KPI_EDIT_GUARDS\.applyAll\(\);\n"
    r"        \}\n"
    r"        document\.body\.style\.overflow = 'hidden';\n"
    r"        scrollToViewMonth\(\);\n"
    r"        state\.modalDirty = false;\n"
    r"        sessionSaved = false;\n"
    r"        sdmHlAllocWarnShown = false;\n"
    r"        undoStack = \[\];\n"
    r"        syncUndoButton\(\);\n"
    r"        if \(btnClose\) btnClose\.focus\(\);\n"
    r"      \}",
    re.M,
)

FRAG_OLD = """        syncSalesDataTableColgroup(showMonthCol);
        var tbodies = modalTable.querySelectorAll('tbody');
        for (var tb = 0; tb < tbodies.length; tb++) {
          modalTable.removeChild(tbodies[tb]);
        }

        var tbodySeg = null;
        function ensureTbodySeg() {
          if (!tbodySeg) {
            tbodySeg = document.createElement('tbody');
            modalTable.appendChild(tbodySeg);
          }
        }

        var totalsMap = buildSalesDataTotalsMap(state.year);"""

FRAG_NEW = """        syncSalesDataTableColgroup(showMonthCol);
        var tbodies = modalTable.querySelectorAll('tbody');
        for (var tb = 0; tb < tbodies.length; tb++) {
          modalTable.removeChild(tbodies[tb]);
        }

        /* KPI-SDM-OPEN-INP: 行は DocumentFragment に構築して1回挿入 */
        var __sdmRowsFrag = document.createDocumentFragment();
        var tbodySeg = null;
        function ensureTbodySeg() {
          if (!tbodySeg) {
            tbodySeg = document.createElement('tbody');
            __sdmRowsFrag.appendChild(tbodySeg);
          }
        }

        var totalsMap = buildSalesDataTotalsMap(state.year);"""

FRAG_APPEND_OLD = """          tbodySeg.appendChild(tr);
        }
        updateFilterToggleActive();
        updateSalesSortToggleActive();
        updateSalesDataYmBdCount();
        if (
          modal &&
          !modal.hasAttribute('hidden') &&
          window.__KPI_EDIT_GUARDS &&
          typeof window.__KPI_EDIT_GUARDS.applyAll === 'function'
        ) {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
      }

      function scrollToViewMonth() {
        if (!scrollEl) return;
        var target = modalTable.querySelector('tr[data-month-idx="' + state.viewMonth + '"]');
        if (target) target.scrollIntoView({ block: 'start', behavior: 'auto' });
        else scrollEl.scrollTop = 0;
      }"""

FRAG_APPEND_NEW = """          tbodySeg.appendChild(tr);
        }
        modalTable.appendChild(__sdmRowsFrag);
        updateFilterToggleActive();
        updateSalesSortToggleActive();
        updateSalesDataYmBdCount();
        if (
          modal &&
          !modal.hasAttribute('hidden') &&
          window.__KPI_EDIT_GUARDS &&
          typeof window.__KPI_EDIT_GUARDS.applyAll === 'function'
        ) {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
      }

      function scrollToViewMonth() {
        if (!scrollEl) return;
        var target = modalTable.querySelector('tr[data-month-idx="' + state.viewMonth + '"]');
        if (target) target.scrollIntoView({ block: 'start', behavior: 'auto' });
        else scrollEl.scrollTop = 0;
      }"""


def open_modal_new(lease: str) -> str:
    return f"""      /* KPI-SDM-OPEN-INP: 先に殻を表示し、年次テーブル構築は次フレームへ */
      function openModal() {{
        lastFocusEl = document.activeElement;
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function') {{
          if (!window.__KPI_EDIT_LEASE.tryAcquire({lease})) {{
            return;
          }}
        }}
        state.rowStateByIso = {{}};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();
        setSalesDataTab('input');
        if (modalTable) {{
          var tbodiesOpen = modalTable.querySelectorAll('tbody');
          for (var tbOpen = 0; tbOpen < tbodiesOpen.length; tbOpen++) {{
            modalTable.removeChild(tbodiesOpen[tbOpen]);
          }}
        }}
        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        document.body.style.overflow = 'hidden';
        state.modalDirty = false;
        sessionSaved = false;
        sdmHlAllocWarnShown = false;
        undoStack = [];
        syncUndoButton();
        requestAnimationFrame(function () {{
          if (!modal || modal.hasAttribute('hidden')) return;
          updateSalesDataSummary();
          renderSalesDataTable();
          if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {{
            window.__KPI_SALES_INPUT_PATH_UI.sync();
          }}
          if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.sync === 'function') {{
            window.__SDM_DAILY_TARGET_MODE.sync();
          }}
          if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {{
            window.__SDM_DAILY_TARGET_MODE.closePanel();
          }}
          if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {{
            window.__KPI_EDIT_GUARDS.applyAll();
          }}
          scrollToViewMonth();
          if (btnClose) btnClose.focus();
        }});
      }}"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT))
    if MARKER in text:
        print(f"skip (already) {rel}")
        return

    m = OPEN_RE.search(text)
    if not m:
        raise SystemExit(f"sales-data openModal miss: {path}")
    text = OPEN_RE.sub(open_modal_new(m.group("lease")), text, count=1)

    if FRAG_OLD not in text:
        raise SystemExit(f"sales-data fragment anchor miss: {path}")
    text = text.replace(FRAG_OLD, FRAG_NEW, 1)

    if FRAG_APPEND_OLD not in text:
        raise SystemExit(f"sales-data fragment append miss: {path}")
    text = text.replace(FRAG_APPEND_OLD, FRAG_APPEND_NEW, 1)

    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing after patch: {path}")
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

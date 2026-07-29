#!/usr/bin/env python3
"""Sales Data open INP v2: show shell first; heavy setup+fill after next paint."""

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

MARKER = "KPI-SDM-OPEN-INP-V2"

# Match from comment through end of openModal, keep locale-specific lease line inside.
OPEN_RE = re.compile(
    r"/\* KPI-SDM-OPEN-INP: 先に殻を表示し、年次テーブル構築は次フレームへ \*/\n"
    r"      function openModal\(\) \{\n"
    r"        lastFocusEl = document\.activeElement;\n"
    r"        if \(window\.__KPI_EDIT_LEASE && typeof window\.__KPI_EDIT_LEASE\.tryAcquire === 'function'\) \{\n"
    r"          if \(!window\.__KPI_EDIT_LEASE\.tryAcquire\([^\n]+\)\) \{\n"
    r"            return;\n"
    r"          \}\n"
    r"        \}\n"
    r"        state\.rowStateByIso = \{\};\n"
    r"        state\.salesPinnedAmount = null;\n"
    r"        state\.salesAmountSort = null;\n"
    r"        syncYearMonthFromApp\(\);\n"
    r"        syncColheadDatePickerValue\(\);\n"
    r"        clearDateFilterUi\(\);\n"
    r"        closeSalesSortPanel\(\);\n"
    r"        setSalesDataTab\('input'\);\n"
    r"        if \(modalTable\) \{\n"
    r"          var tbodiesOpen = modalTable\.querySelectorAll\('tbody'\);\n"
    r"          for \(var tbOpen = 0; tbOpen < tbodiesOpen\.length; tbOpen\+\+\) \{\n"
    r"            modalTable\.removeChild\(tbodiesOpen\[tbOpen\]\);\n"
    r"          \}\n"
    r"        \}\n"
    r"        modal\.removeAttribute\('hidden'\);\n"
    r"        modal\.removeAttribute\('aria-hidden'\);\n"
    r"        document\.body\.style\.overflow = 'hidden';\n"
    r"        state\.modalDirty = false;\n"
    r"        sessionSaved = false;\n"
    r"        sdmHlAllocWarnShown = false;\n"
    r"        undoStack = \[\];\n"
    r"        syncUndoButton\(\);\n"
    r"        requestAnimationFrame\(function \(\) \{\n"
    r"          if \(!modal \|\| modal\.hasAttribute\('hidden'\)\) return;\n"
    r"          updateSalesDataSummary\(\);\n"
    r"          renderSalesDataTable\(\);\n"
    r"          if \(window\.__KPI_SALES_INPUT_PATH_UI && typeof window\.__KPI_SALES_INPUT_PATH_UI\.sync === 'function'\) \{\n"
    r"            window\.__KPI_SALES_INPUT_PATH_UI\.sync\(\);\n"
    r"          \}\n"
    r"          if \(window\.__SDM_DAILY_TARGET_MODE && typeof window\.__SDM_DAILY_TARGET_MODE\.sync === 'function'\) \{\n"
    r"            window\.__SDM_DAILY_TARGET_MODE\.sync\(\);\n"
    r"          \}\n"
    r"          if \(window\.__SDM_DAILY_TARGET_MODE && typeof window\.__SDM_DAILY_TARGET_MODE\.closePanel === 'function'\) \{\n"
    r"            window\.__SDM_DAILY_TARGET_MODE\.closePanel\(\);\n"
    r"          \}\n"
    r"          if \(window\.__KPI_EDIT_GUARDS && typeof window\.__KPI_EDIT_GUARDS\.applyAll === 'function'\) \{\n"
    r"            window\.__KPI_EDIT_GUARDS\.applyAll\(\);\n"
    r"          \}\n"
    r"          scrollToViewMonth\(\);\n"
    r"          if \(btnClose\) btnClose\.focus\(\);\n"
    r"        \}\);\n"
    r"      \}\n"
)


def build_open(lease_call: str) -> str:
    return f"""/* KPI-SDM-OPEN-INP-V2: 殻を即表示 → 次ペイント後に重い準備・年次テーブル構築 */
      function openModal() {{
        lastFocusEl = document.activeElement;
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function') {{
          if (!window.__KPI_EDIT_LEASE.tryAcquire({lease_call})) {{
            return;
          }}
        }}
        state.rowStateByIso = {{}};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        state.modalDirty = false;
        sessionSaved = false;
        sdmHlAllocWarnShown = false;
        undoStack = [];
        if (modalTable) {{
          var tbodiesOpen = modalTable.querySelectorAll('tbody');
          for (var tbOpen = 0; tbOpen < tbodiesOpen.length; tbOpen++) {{
            modalTable.removeChild(tbodiesOpen[tbOpen]);
          }}
        }}
        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        document.body.style.overflow = 'hidden';
        syncUndoButton();
        requestAnimationFrame(function () {{
          requestAnimationFrame(function () {{
            if (!modal || modal.hasAttribute('hidden')) return;
            syncYearMonthFromApp();
            syncColheadDatePickerValue();
            clearDateFilterUi();
            closeSalesSortPanel();
            setSalesDataTab('input');
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
        }});
      }}
"""


LEASE = {
    "app/annual/index.html": "isJa ? '売上データ' : 'Sales Data'",
    "en/app/annual/index.html": "isJa ? '売上データ' : 'Sales Data'",
    "zh-tw/app/annual/index.html": "isJa ? '売上データ' : (String(document.documentElement.getAttribute('lang')||'').indexOf('zh')===0 ? '營業額資料' : 'Sales Data')",
}


def patch_page(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already) {rel}")
        return
    m = OPEN_RE.search(text)
    if not m:
        raise SystemExit(f"openModal miss: {rel}")
    lease = LEASE[rel]
    text = text[: m.start()] + build_open(lease) + text[m.end() :]
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

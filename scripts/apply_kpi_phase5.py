#!/usr/bin/env python3
"""Phase 5: Figma daily-input-path toggle (Sales Data + MEP) + edit lease hooks."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_kpi_year_store import GATEWAY_ANNUAL_ANCHOR, GATEWAY_MONTHLY_ANCHOR, inject_store, patch_mep  # noqa: E402
from kpi_phase5_client import (  # noqa: E402
    KPI_EDIT_LEASE_HOOKS_MARKER,
    KPI_SALES_INPUT_PATH_MARKER,
    PHASE5_TOGGLE_CSS,
    edit_lease_hooks_js,
    replace_or_insert_toggle,
    sales_input_path_client_js,
)
from kpi_year_store_client import KPI_YEAR_STORE_MARKER  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

ANNUAL_TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]
MONTHLY_TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]
MEP_TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

SDM_TAB_BAR_ANCHOR = '      <div class="sales-data-modal__tab-bar">'

MEP_AFTER_TODAY_JA = """      <button type="button" class="monthly-edit-float__today" id="monthly-edit-float-today" aria-label="本日に移動">
        本日
      </button>
"""
MEP_AFTER_TODAY_EN = """      <button type="button" class="monthly-edit-float__today" id="monthly-edit-float-today" aria-label="Jump to today">
        Today
      </button>
"""

SALES_DATA_OPEN_OLD = """          if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function') {
            window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '売上データ' : 'Sales Data');
          }
          if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
            window.__KPI_EDIT_GUARDS.applyAll();
          }
          modal.removeAttribute('hidden');"""

SALES_DATA_OPEN_NEW = """          if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function') {
            window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '売上データ' : 'Sales Data');
          }
          if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
            window.__KPI_SALES_INPUT_PATH_UI.sync();
          }
          if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
            window.__KPI_EDIT_GUARDS.applyAll();
          }
          modal.removeAttribute('hidden');"""

SALES_DATA_CLOSE_OLD = """      function closeModal() {
        hideCloseChooser();
        modal.setAttribute('hidden', '');"""

SALES_DATA_CLOSE_NEW = """      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        hideCloseChooser();
        modal.setAttribute('hidden', '');"""

ANNUAL_EDIT_OPEN_OLD = """        renderTable();
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
        modal.hidden = false;"""

ANNUAL_EDIT_OPEN_NEW = """        renderTable();
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function') {
          window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '年次編集' : 'Annual Edit');
        }
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
        modal.hidden = false;"""

ANNUAL_EDIT_CLOSE_OLD = """      function closeModal() {
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.hidden = true;"""

ANNUAL_EDIT_CLOSE_NEW = """      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.hidden = true;"""

MEP_INIT_OLD = """        onMepYearContextChanged(mefYear);
        if (
          window.KpiYearStore &&
          KpiYearStore.getDailySalesInputPath() === 'mep' &&
          window.__KPI_EDIT_LEASE &&
          typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function'
        ) {
          window.__KPI_EDIT_LEASE.tryAcquire(useJa ? 'Monthly Edit' : 'Monthly Edit');
        }
        buildGrid();"""

MEP_INIT_NEW = """        onMepYearContextChanged(mefYear);
        if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
          window.__KPI_SALES_INPUT_PATH_UI.sync();
        }
        if (
          window.KpiYearStore &&
          KpiYearStore.getDailySalesInputPath() === 'mep' &&
          window.__KPI_EDIT_LEASE &&
          typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function'
        ) {
          window.__KPI_EDIT_LEASE.tryAcquire(useJa ? 'Monthly Edit' : 'Monthly Edit');
        }
        buildGrid();"""

MEP_LEAVE_OLD = """      function navigateBackToMonthly() {
        closeMonthPicker();
        window.location.href = '../index.html';
      }"""

MEP_LEAVE_NEW = """      function navigateBackToMonthly() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        closeMonthPicker();
        window.location.href = '../index.html';
      }"""

EDIT_GUARDS_LISTENER_OLD = """        document.addEventListener('kpi:dailySalesInputPathChanged', applyAllGuards);
        document.addEventListener('kpi:pastSalesEditChanged', applyAllGuards);
        document.addEventListener('kpi:editGuardsRefresh', applyAllGuards);"""

EDIT_GUARDS_LISTENER_NEW = """        document.addEventListener('kpi:dailySalesInputPathChanged', applyAllGuards);
        document.addEventListener('kpi:pastSalesEditChanged', applyAllGuards);
        document.addEventListener('kpi:editLeaseChanged', applyAllGuards);
        document.addEventListener('kpi:editGuardsRefresh', applyAllGuards);"""

STALE_TOGGLE_RE = re.compile(
    r"\n        <div\n          class=\"kpi-(?:sales-input-path|daily-input-path)[^\"]*\""
    r"[\s\S]*?\n        </div>",
    re.MULTILINE,
)

BROKEN_MONTHLY_EDIT_BTN_RE = re.compile(
    r"(<button\n          type=\"button\"\n          class=\"monthly-access-btn monthly-access-btn--edit\"\n"
    r"          id=\"monthly-top-edit-btn\"\n        )<div[\s\S]*?</div>\n          (aria-label=\"Edit\"\n        >)",
    re.MULTILINE,
)


SALES_PATH_IIFE_RE = re.compile(
    r"\s*(?:/\* KPI-SALES-INPUT-PATH \*/\s*)?"
    r"\(function \(\) \{\n        function storeReady\(\) \{\n"
    r"          return !!\(window\.KpiYearStore && KpiYearStore\.getDailySalesInputPath\);[\s\S]*?"
    r"window\.__KPI_SALES_INPUT_PATH_UI = \{ sync: syncToggleUi \};\n      \}\)\(\);\n",
    re.MULTILINE,
)

LEASE_HOOKS_IIFE_RE = re.compile(
    r"\s*(?:/\* KPI-EDIT-LEASE-HOOKS \*/\s*)?"
    r"\(function \(\) \{\n        var LEASE_SURFACE = 'daily-sales';[\s\S]*?"
    r"window\.addEventListener\('pagehide', releaseLease\);\n      \}\)\(\);\n",
    re.MULTILINE,
)


def remove_stale_toggle_ui(text: str) -> str:
    text = BROKEN_MONTHLY_EDIT_BTN_RE.sub(r"\1\2", text)
    return STALE_TOGGLE_RE.sub("", text)


def inject_phase5_js(text: str) -> str:
    text = SALES_PATH_IIFE_RE.sub("\n", text)
    text = LEASE_HOOKS_IIFE_RE.sub("\n", text)
    lease_block = edit_lease_hooks_js().rstrip() + "\n"
    sales_block = sales_input_path_client_js().rstrip() + "\n"
    anchor = KPI_EDIT_LEASE_HOOKS_MARKER
    pos = text.find(anchor)
    if pos < 0:
        anchor = "/* KPI-EDIT-GUARDS */"
        pos = text.find(anchor)
    if pos < 0:
        anchor = KPI_YEAR_STORE_MARKER
        pos = text.find(anchor)
    if pos < 0:
        raise ValueError("inject anchor missing for phase5 JS")
    end = text.find("})();", pos)
    if end < 0:
        raise ValueError("store/guards block end missing")
    end = text.find("\n", end) + 1
    return text[:end] + "\n" + lease_block + sales_block + text[end:]


TOGGLE_CSS_MARKED_RE = re.compile(
    r"    /\* KPI-PHASE5-TOGGLE-CSS \*/[\s\S]*?    /\* /KPI-PHASE5-TOGGLE-CSS \*/\n?",
    re.MULTILINE,
)
TOGGLE_CSS_BLOCK_RE = re.compile(
    r"\n[ \t]*\.kpi-daily-input-path \{[\s\S]*?"
    r"body\.office-mode \.kpi-daily-input-path__knob \{[\s\S]*?\n[ \t]*\}\n?",
    re.MULTILINE,
)
TOGGLE_CSS_ORPHAN_RE = re.compile(
    r"\}[ \t]*\.kpi-daily-input-path \{[\s\S]*?"
    r"body\.office-mode \.kpi-daily-input-path__knob \{[\s\S]*?\n[ \t]*\}\n?",
    re.MULTILINE,
)


def scrub_toggle_css(text: str) -> str:
    while True:
        text, n_marked = TOGGLE_CSS_MARKED_RE.subn("", text)
        text, n_block = TOGGLE_CSS_BLOCK_RE.subn("", text)
        text, n_orphan = TOGGLE_CSS_ORPHAN_RE.subn("}\n", text, count=1)
        if n_marked + n_block + n_orphan == 0:
            return text


def inject_toggle_css(text: str) -> str:
    css_block = PHASE5_TOGGLE_CSS.strip() + "\n"
    text = scrub_toggle_css(text)
    for anchor in (
        ".sales-data-modal__tab-bar {",
        ".monthly-edit-float__month-btn.is-active {",
    ):
        if anchor in text:
            return text.replace(anchor, css_block + "\n    " + anchor, 1)
    raise ValueError("phase5 CSS anchor missing")


def inject_sales_data_toggle(text: str, lang: str) -> str:
    return replace_or_insert_toggle(
        text, "sales-data", lang, SDM_TAB_BAR_ANCHOR, insert_before=True
    )


def inject_mep_toggle(text: str, lang: str) -> str:
    anchor = MEP_AFTER_TODAY_JA if lang == "ja" else MEP_AFTER_TODAY_EN
    return replace_or_insert_toggle(text, "mep", lang, anchor)


def page_lang(path: Path) -> str:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    return "en" if rel.startswith("en/") else "ja"


def replace_once(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n")[0] in text:
        return text
    raise ValueError(f"patch miss: {old[:72]!r}")


    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n")[0] in text:
        return text
    raise ValueError(f"patch miss: {old[:72]!r}")


def patch_annual(path: Path) -> None:
    lang = page_lang(path)
    text = path.read_text(encoding="utf-8")
    text = remove_stale_toggle_ui(text)
    text = inject_store(text, GATEWAY_ANNUAL_ANCHOR)
    text = inject_toggle_css(text)
    text = inject_sales_data_toggle(text, lang)
    text = inject_phase5_js(text)
    text = replace_once(text, SALES_DATA_OPEN_OLD, SALES_DATA_OPEN_NEW)
    text = replace_once(text, SALES_DATA_CLOSE_OLD, SALES_DATA_CLOSE_NEW)
    text = replace_once(text, ANNUAL_EDIT_OPEN_OLD, ANNUAL_EDIT_OPEN_NEW)
    text = replace_once(text, ANNUAL_EDIT_CLOSE_OLD, ANNUAL_EDIT_CLOSE_NEW)
    if EDIT_GUARDS_LISTENER_OLD in text:
        text = replace_once(text, EDIT_GUARDS_LISTENER_OLD, EDIT_GUARDS_LISTENER_NEW)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_monthly(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = remove_stale_toggle_ui(text)
    text = SALES_PATH_IIFE_RE.sub("\n", text)
    text = LEASE_HOOKS_IIFE_RE.sub("\n", text)
    text = inject_store(text, GATEWAY_MONTHLY_ANCHOR)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_mep_page(path: Path) -> None:
    lang = page_lang(path)
    patch_mep(path)
    text = path.read_text(encoding="utf-8")
    text = remove_stale_toggle_ui(text)
    text = inject_toggle_css(text)
    text = inject_mep_toggle(text, lang)
    text = inject_phase5_js(text)
    text = replace_once(text, MEP_INIT_OLD, MEP_INIT_NEW)
    text = replace_once(text, MEP_LEAVE_OLD, MEP_LEAVE_NEW)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in ANNUAL_TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_annual(path)
    for path in MONTHLY_TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_monthly(path)
    for path in MEP_TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_mep_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

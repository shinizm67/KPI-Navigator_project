#!/usr/bin/env python3
"""Remove Cockpit annual-target Edit; enable inline edit in Sales Data + Annual Edit modals."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from annual_target_edit_surfaces_client import (  # noqa: E402
    ANNUAL_TARGET_EDIT_MARKER,
    annual_target_edit_surfaces_js,
)

ALL_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

ANNUAL_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

COCKPIT_EDIT_BTN_JA = (
    '            <button type="button" class="annual-target-inline-edit" '
    'id="annual-target-edit-btn" aria-label="年次目標売上を編集">'
    '<span class="annual-target-inline-edit-text">編集</span></button>\n'
)
COCKPIT_EDIT_BTN_EN = (
    '            <button type="button" class="annual-target-inline-edit" '
    'id="annual-target-edit-btn" aria-label="Edit annual target sales">'
    '<span class="annual-target-inline-edit-text">Edit</span></button>\n'
)

COCKPIT_EDIT_IIFE_RE = re.compile(
    r"    \(function \(\) \{\n"
    r"      var targetEl = document\.getElementById\('annual-target-sales-value'\);\n"
    r"      var editBtn = document\.getElementById\('annual-target-edit-btn'\);\n"
    r"      if \(!targetEl \|\| !editBtn\) return;[\s\S]*?"
    r"      \}\);\n"
    r"    \}\)\(\);\n",
    re.MULTILINE,
)

SDM_TARGET_ROW_JA_OLD = """        <div class="sales-data-modal__summary-row sales-data-modal__summary-row--cols-2">
          <p
            class="sales-data-modal__summary-label"
            tabindex="0"
            data-tooltip="コックピットの「年次目標売上」から読み込んで表示します。変更する場合はコックピットの「編集」から行ってください。"
          >
            年次目標売上
          </p>
          <p
            class="sales-data-modal__summary-value"
            id="sales-data-summary-target-sales"
            tabindex="0"
            data-tooltip="コックピットの「年次目標売上」から読み込んで表示します。変更する場合はコックピットの「編集」から行ってください。"
          >
            —
          </p>
        </div>"""

SDM_TARGET_ROW_JA_NEW = """        <div class="sales-data-modal__summary-row sales-data-modal__summary-row--cols-2 sales-data-modal__summary-row--reference-input">
          <p
            class="sales-data-modal__summary-label"
            tabindex="0"
            data-tooltip="当該年の年次目標売上です。右のセルをクリックして金額を入力・編集してください。"
          >
            年次目標売上
          </p>
          <input
            type="text"
            class="sales-data-modal__summary-value sales-data-modal__summary-reference-input"
            id="sales-data-summary-target-sales"
            inputmode="numeric"
            autocomplete="off"
            spellcheck="false"
            aria-label="年次目標売上を入力"
            placeholder="—"
          />
        </div>"""

SDM_TARGET_ROW_EN_OLD = """        <div class="sales-data-modal__summary-row sales-data-modal__summary-row--cols-2">
          <p
            class="sales-data-modal__summary-label"
            tabindex="0"
            data-tooltip="Read from Annual Target Sales on the cockpit. To change it, use Edit on the cockpit."
          >
            Annual Target Sales
          </p>
          <p
            class="sales-data-modal__summary-value"
            id="sales-data-summary-target-sales"
            tabindex="0"
            data-tooltip="Read from Annual Target Sales on the cockpit. To change it, use Edit on the cockpit."
          >
            —
          </p>
        </div>"""

SDM_TARGET_ROW_EN_NEW = """        <div class="sales-data-modal__summary-row sales-data-modal__summary-row--cols-2 sales-data-modal__summary-row--reference-input">
          <p
            class="sales-data-modal__summary-label"
            tabindex="0"
            data-tooltip="Annual target sales for this year. Click the cell on the right to enter or edit the amount."
          >
            Annual Target Sales
          </p>
          <input
            type="text"
            class="sales-data-modal__summary-value sales-data-modal__summary-reference-input"
            id="sales-data-summary-target-sales"
            inputmode="numeric"
            autocomplete="off"
            spellcheck="false"
            aria-label="Enter annual target sales"
            placeholder="—"
          />
        </div>"""

SDM_CSS_ANCHOR = """    .sales-data-modal__summary-row--cols-3 .sales-data-modal__summary-pct {
      border-right: 0;
    }"""

SDM_CSS_NEW = """    .sales-data-modal__summary-row--reference-input .sales-data-modal__summary-label {
      background: var(--sdm-bg-inactive);
    }
    .sales-data-modal__summary-row--reference-input .sales-data-modal__summary-reference-input {
      background: var(--sdm-bg-active-editable);
    }
    .sales-data-modal__summary-reference-input {
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 0 10px;
      border: 0;
      background: transparent;
      color: var(--sdm-cyan);
      font-size: var(--sdm-fs-body);
      font-family: inherit;
      font-weight: 400;
      line-height: 1.3;
      text-align: center;
      box-sizing: border-box;
      font-variant-numeric: tabular-nums;
      -webkit-appearance: none;
      appearance: none;
    }
    .sales-data-modal__summary-reference-input::placeholder {
      color: rgba(88, 225, 243, 0.45);
    }
    .sales-data-modal__summary-reference-input:focus {
      outline: 1px solid var(--sdm-cyan);
      outline-offset: -1px;
      background: var(--sdm-bg-active-focus);
    }
    .sales-data-modal__summary-row--cols-3 .sales-data-modal__summary-pct {
      border-right: 0;
    }"""

AEM_TARGET_ROW_JA_OLD = """      <div class="annual-edit-modal__ym">"""
AEM_TARGET_ROW_JA_NEW = """      <div class="annual-edit-modal__target-row annual-edit-modal__input-only">
        <p class="annual-edit-modal__target-label">年次目標売上</p>
        <input
          type="text"
          class="annual-edit-modal__target-input"
          id="annual-edit-annual-target-input"
          inputmode="numeric"
          autocomplete="off"
          spellcheck="false"
          aria-label="年次目標売上を入力"
          placeholder="—"
        />
      </div>
      <div class="annual-edit-modal__ym">"""

AEM_TARGET_ROW_EN_OLD = """      <div class="annual-edit-modal__ym">"""
AEM_TARGET_ROW_EN_NEW = """      <div class="annual-edit-modal__target-row annual-edit-modal__input-only">
        <p class="annual-edit-modal__target-label">Annual Target Sales</p>
        <input
          type="text"
          class="annual-edit-modal__target-input"
          id="annual-edit-annual-target-input"
          inputmode="numeric"
          autocomplete="off"
          spellcheck="false"
          aria-label="Enter annual target sales"
          placeholder="—"
        />
      </div>
      <div class="annual-edit-modal__ym">"""

AEM_CSS_ANCHOR = """    .annual-edit-modal__ym {"""
AEM_CSS_NEW = """    .annual-edit-modal__target-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0;
      margin: 0 0 8px;
      border: 1px solid var(--aem-line);
    }
    .annual-edit-modal__target-label {
      margin: 0;
      padding: 8px 10px;
      background: var(--aem-bg-inactive);
      color: var(--aem-cyan);
      font-size: var(--aem-fs-body);
      line-height: 1.3;
      text-align: center;
    }
    .annual-edit-modal__target-input {
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 0 8px;
      border: 0;
      background: var(--aem-bg-active-editable);
      color: var(--aem-cyan);
      font-size: var(--aem-fs-body);
      font-family: inherit;
      line-height: 1.3;
      text-align: center;
      box-sizing: border-box;
      font-variant-numeric: tabular-nums;
    }
    .annual-edit-modal__target-input::placeholder {
      color: rgba(88, 225, 243, 0.45);
    }
    .annual-edit-modal__target-input:focus {
      outline: 1px solid var(--aem-cyan);
      outline-offset: -1px;
      background: var(--aem-bg-active-focus);
    }
    .annual-edit-modal--path-blocked .annual-edit-modal__target-input {
      pointer-events: none;
      opacity: 0.55;
    }
    .annual-edit-modal__ym {"""

SDM_SYNC_OLD = """      function syncTargetSalesDisplay() {
        if (!summaryTargetSalesEl) return;
        var target = getCockpitAnnualTargetSales();
        summaryTargetSalesEl.textContent = target != null ? formatAmountCell(target) : '—';
      }"""

SDM_SYNC_NEW = """      function syncTargetSalesDisplay() {
        if (!summaryTargetSalesEl) return;
        if (
          window.__ANNUAL_UI &&
          typeof window.__ANNUAL_UI.readAnnualTargetForYear === 'function'
        ) {
          var fromHelper = window.__ANNUAL_UI.readAnnualTargetForYear(getOperatingYear());
          if (fromHelper != null) {
            summaryTargetSalesEl.value = window.__ANNUAL_UI.formatAnnualTargetDisplay(fromHelper);
            return;
          }
        }
        var target = getCockpitAnnualTargetSales();
        summaryTargetSalesEl.value =
          target != null
            ? (window.__ANNUAL_UI && window.__ANNUAL_UI.formatAnnualTargetDisplay
                ? window.__ANNUAL_UI.formatAnnualTargetDisplay(target)
                : formatAmountCell(target))
            : '';
      }"""

SDM_BIND_OLD = """      if (tabInput) {
        tabInput.addEventListener('click', function (ev) {
          ev.preventDefault();
          setSalesDataTab('input');
        });
      }"""

SDM_BIND_NEW = """      if (
        summaryTargetSalesEl &&
        window.__ANNUAL_UI &&
        typeof window.__ANNUAL_UI.bindAnnualTargetInput === 'function'
      ) {
        window.__ANNUAL_UI.bindAnnualTargetInput(
          summaryTargetSalesEl,
          function () {
            return getOperatingYear();
          },
          'sales-data-modal'
        );
      }

      if (tabInput) {
        tabInput.addEventListener('click', function (ev) {
          ev.preventDefault();
          setSalesDataTab('input');
        });
      }"""

AEM_BIND_OLD = """      if (!modal || !modalTable || !btnEdit) return;"""

AEM_BIND_NEW = """      if (!modal || !modalTable || !btnEdit) return;

      var annualTargetInput = document.getElementById('annual-edit-annual-target-input');
      var syncAnnualEditTargetInput = null;
      if (
        annualTargetInput &&
        window.__ANNUAL_UI &&
        typeof window.__ANNUAL_UI.bindAnnualTargetInput === 'function'
      ) {
        syncAnnualEditTargetInput = window.__ANNUAL_UI.bindAnnualTargetInput(
          annualTargetInput,
          function () {
            return yearSelect ? Number(yearSelect.value) : new Date().getFullYear();
          },
          'annual-edit-modal'
        );
      }"""

AEM_YEAR_OLD = """      if (yearSelect) {
        yearSelect.addEventListener('change', function () {
          var y = Number(yearSelect.value);
          if (!isFinite(y)) return;
          state.rowStateByIso = {};
          state.modalDirty = false;
          undoStack = [];
          syncUndoButton();
          state.salesPinnedAmount = null;
          state.salesAmountSort = null;
          state.year = clampYear(y);
          yearSelect.value = String(state.year);
          syncColheadDatePickerValue();
          renderTable();
          scrollToViewMonth();
        });
      }"""

AEM_YEAR_NEW = """      if (yearSelect) {
        yearSelect.addEventListener('change', function () {
          var y = Number(yearSelect.value);
          if (!isFinite(y)) return;
          state.rowStateByIso = {};
          state.modalDirty = false;
          undoStack = [];
          syncUndoButton();
          state.salesPinnedAmount = null;
          state.salesAmountSort = null;
          state.year = clampYear(y);
          yearSelect.value = String(state.year);
          if (typeof syncAnnualEditTargetInput === 'function') syncAnnualEditTargetInput();
          syncColheadDatePickerValue();
          renderTable();
          scrollToViewMonth();
        });
      }"""

GUARD_OLD = """            '.annual-edit-modal__sales-input, .annual-edit-modal__bizday-toggle'"""
GUARD_NEW = """            '.annual-edit-modal__sales-input, .annual-edit-modal__bizday-toggle, .annual-edit-modal__target-input'"""


def inject_helper(text: str) -> str:
    block = annual_target_edit_surfaces_js().rstrip() + "\n"
    if ANNUAL_TARGET_EDIT_MARKER in text:
        pattern = re.escape(ANNUAL_TARGET_EDIT_MARKER) + r"[\s\S]*?\}\)\(\);\n"
        if re.search(pattern, text):
            return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
        raise SystemExit("annual target edit marker found but block boundary missing")
    anchor = "/* KPI-COCKPIT-YEAR-SYNC */"
    if anchor not in text:
        raise SystemExit(f"inject anchor missing: {anchor}")
    m = re.search(re.escape(anchor) + r"[\s\S]*?\}\)\(\);\n", text)
    if not m:
        raise SystemExit("cockpit year sync block end not found")
    insert_at = m.end()
    return text[:insert_at] + "\n" + block + text[insert_at:]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n")[0] in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def patch_all_pages(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "/app/annual/" in str(path) or "/app/monthly/" in str(path)
    if COCKPIT_EDIT_BTN_JA in text:
        text = text.replace(COCKPIT_EDIT_BTN_JA, "", 1)
    elif COCKPIT_EDIT_BTN_EN in text:
        text = text.replace(COCKPIT_EDIT_BTN_EN, "", 1)
    elif "annual-target-edit-btn" not in text:
        pass
    else:
        raise SystemExit(f"cockpit edit button patch miss in {path}")
    text, n = COCKPIT_EDIT_IIFE_RE.subn("", text, count=1)
    if n == 0 and "annual-target-edit-btn" in text:
        raise SystemExit(f"cockpit edit IIFE patch miss in {path}")
    if path in ANNUAL_PAGES:
        text = inject_helper(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_annual_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "/en/" not in str(path)
    if is_ja:
        text = replace_once(text, SDM_TARGET_ROW_JA_OLD, SDM_TARGET_ROW_JA_NEW, "sdm target row ja")
        if AEM_TARGET_ROW_JA_OLD in text and "annual-edit-annual-target-input" not in text:
            text = text.replace(AEM_TARGET_ROW_JA_OLD, AEM_TARGET_ROW_JA_NEW, 1)
    else:
        text = replace_once(text, SDM_TARGET_ROW_EN_OLD, SDM_TARGET_ROW_EN_NEW, "sdm target row en")
        if AEM_TARGET_ROW_EN_OLD in text and "annual-edit-annual-target-input" not in text:
            text = text.replace(AEM_TARGET_ROW_EN_OLD, AEM_TARGET_ROW_EN_NEW, 1)
    if ".sales-data-modal__summary-row--reference-input .sales-data-modal__summary-label" not in text:
        text = replace_once(text, SDM_CSS_ANCHOR, SDM_CSS_NEW, "sdm css")
    if "annual-edit-modal__target-row" not in text:
        text = replace_once(text, AEM_CSS_ANCHOR, AEM_CSS_NEW, "aem css")
    text = replace_once(text, SDM_SYNC_OLD, SDM_SYNC_NEW, "sdm sync")
    if "'sales-data-modal'\n        );" not in text:
        text = replace_once(text, SDM_BIND_OLD, SDM_BIND_NEW, "sdm bind")
    if "'annual-edit-modal'\n        );" not in text:
        text = replace_once(text, AEM_BIND_OLD, AEM_BIND_NEW, "aem bind")
    if "syncAnnualEditTargetInput()" not in text:
        text = replace_once(text, AEM_YEAR_OLD, AEM_YEAR_NEW, "aem year")
    if GUARD_OLD in text and GUARD_NEW not in text:
        text = text.replace(GUARD_OLD, GUARD_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} (annual surfaces)")


def main() -> int:
    for path in ALL_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_all_pages(path)
    for path in ANNUAL_PAGES:
        patch_annual_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

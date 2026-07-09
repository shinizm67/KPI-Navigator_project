#!/usr/bin/env python3
"""Inject Past Sales Edit toggle (View | switch | Edit) into Annual pages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ANNUAL_TARGETS = [
    (ROOT / "app/annual/index.html", True),
    (ROOT / "en/app/annual/index.html", False),
]
MONTHLY_TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

KPI_EDIT_GUARDS_MARKER = "/* KPI-EDIT-GUARDS */"
TOGGLE_CSS_MARKER = "/* KPI-PAST-SALES-EDIT-TOGGLE-CSS */"
TOGGLE_END_MARKER = "/* /KPI-PAST-SALES-EDIT-TOGGLE-CSS */"

PAST_SALES_TOGGLE_JA = """        <div
          class="kpi-past-sales-edit-mode"
          id="past-sales-edit-mode"
          aria-label="過去データ編集モード"
        >
          <p class="kpi-past-sales-edit-mode__title">過去データ編集</p>
          <div class="kpi-past-sales-edit-mode__row">
            <span class="kpi-past-sales-edit-mode__side is-active" data-ps-edit-side="view">閲覧</span>
            <button
              type="button"
              class="kpi-past-sales-edit-mode__switch"
              data-ps-edit-switch
              role="switch"
              aria-checked="false"
              aria-label="過去データを閲覧と編集で切り替え"
              data-kpi-guard-ignore
              title="閲覧: 読み取り専用。編集: 過去売上・営業日を変更（Analyze・Seasonality に影響）"
            >
              <span class="kpi-past-sales-edit-mode__knob" aria-hidden="true"></span>
            </button>
            <span class="kpi-past-sales-edit-mode__side is-inactive" data-ps-edit-side="edit">編集</span>
          </div>
        </div>"""

PAST_SALES_TOGGLE_EN = """        <div
          class="kpi-past-sales-edit-mode"
          id="past-sales-edit-mode"
          aria-label="Past data edit mode"
        >
          <p class="kpi-past-sales-edit-mode__title">Past Data Edit</p>
          <div class="kpi-past-sales-edit-mode__row">
            <span class="kpi-past-sales-edit-mode__side is-active" data-ps-edit-side="view">View</span>
            <button
              type="button"
              class="kpi-past-sales-edit-mode__switch"
              data-ps-edit-switch
              role="switch"
              aria-checked="false"
              aria-label="Switch past data between view and edit"
              data-kpi-guard-ignore
              title="View: read-only. Edit: change past sales and business days (affects Analyze and seasonality)."
            >
              <span class="kpi-past-sales-edit-mode__knob" aria-hidden="true"></span>
            </button>
            <span class="kpi-past-sales-edit-mode__side is-inactive" data-ps-edit-side="edit">Edit</span>
          </div>
        </div>"""

PAST_SALES_TOGGLE_CSS = """
    /* KPI-PAST-SALES-EDIT-TOGGLE-CSS */
    .kpi-past-sales-edit-mode {
      box-sizing: border-box;
      position: absolute;
      top: calc(var(--psm-tab-top) - 30px);
      right: 22px;
      z-index: 7;
      color: #58e1f3;
      font-family: 'Orbitron', sans-serif;
      user-select: none;
      width: auto;
      min-width: 172px;
    }
    .kpi-past-sales-edit-mode__title {
      margin: 0 0 5px;
      text-align: center;
      color: #58e1f3;
      font-size: 11px;
      line-height: 1;
      letter-spacing: 0.06em;
      font-weight: 500;
    }
    .kpi-past-sales-edit-mode__row {
      display: grid;
      grid-template-columns: auto 52px auto;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .kpi-past-sales-edit-mode__side {
      font-size: 10px;
      line-height: 1.1;
      color: #58e1f3;
      text-align: center;
      white-space: nowrap;
    }
    .kpi-past-sales-edit-mode__side.is-active {
      opacity: 1;
      font-weight: 600;
    }
    .kpi-past-sales-edit-mode__side.is-inactive {
      opacity: 0.34;
      font-weight: 500;
    }
    .kpi-past-sales-edit-mode__switch {
      position: relative;
      width: 52px;
      height: 17px;
      border: 1.5px solid #58e1f3;
      border-radius: 999px;
      background: rgba(0, 0, 0, 0.2);
      cursor: pointer;
      padding: 0;
      margin: 0 auto;
      flex-shrink: 0;
    }
    .kpi-past-sales-edit-mode__knob {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 13px;
      height: 13px;
      border-radius: 999px;
      background: #58e1f3;
      box-shadow: 0 0 8px rgba(88, 225, 243, 0.35);
      transition: transform 0.2s ease;
    }
    .kpi-past-sales-edit-mode.is-edit .kpi-past-sales-edit-mode__knob {
      transform: translateX(31px);
    }
    .kpi-past-sales-edit-mode__switch:focus-visible {
      outline: 2px solid rgba(88, 225, 243, 0.8);
      outline-offset: 2px;
    }
    body.office-mode .kpi-past-sales-edit-mode {
      color: #4a4a4a;
    }
    body.office-mode .kpi-past-sales-edit-mode__title,
    body.office-mode .kpi-past-sales-edit-mode__side.is-active {
      color: #4a4a4a;
    }
    body.office-mode .kpi-past-sales-edit-mode__side.is-inactive {
      color: #7a7a7a;
      opacity: 0.55;
    }
    body.office-mode .kpi-past-sales-edit-mode__switch {
      border-color: #4a4a4a;
      background: #f2f2f2;
    }
    body.office-mode .kpi-past-sales-edit-mode__knob {
      background: #5a5a5a;
      box-shadow: none;
    }
    .past-sales-modal__input-stack--view-only .past-sales-modal__ym-select,
    .past-sales-modal__input-stack--view-only .past-sales-modal__ym-arrow {
      pointer-events: auto;
      opacity: 1;
    }
    .past-sales-modal__input-stack--view-only .past-sales-modal__cb,
    .past-sales-modal__input-stack--view-only .past-sales-modal__sales-input,
    .past-sales-modal__pane--view-only .past-sales-modal__cb,
    .past-sales-modal__pane--view-only .past-sales-modal__sales-input {
      pointer-events: none;
    }
    .past-sales-modal__pane--view-only .past-sales-modal__sales-input,
    .sales-data-modal__pane--path-blocked .sales-data-modal__sales-input,
    .sales-data-modal__pane--path-blocked .sales-data-modal__cb,
    .annual-edit-modal--path-blocked .annual-edit-modal__sales-input,
    .annual-edit-modal--path-blocked .annual-edit-modal__cb {
      opacity: 0.72;
    }
    /* /KPI-PAST-SALES-EDIT-TOGGLE-CSS */
"""

PAST_SALES_YM_NAV_IDS = [
    "past-sales-year-select",
    "past-sales-month-select",
    "past-sales-year-prev",
    "past-sales-year-next",
    "past-sales-month-prev",
    "past-sales-month-next",
]

PAST_SALES_OPEN_OLD = """        updatePastSalesSummary();
        renderPastSalesTable();
        if (window.KpiYearStore && typeof KpiYearStore.setPastSalesEditEnabled === 'function') {
          KpiYearStore.setPastSalesEditEnabled(false);
        }
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
        modal.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';"""

PAST_SALES_OPEN_ALT = """        updatePastSalesSummary();
        renderPastSalesTable();
        modal.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';"""

PAST_SALES_OPEN_NEW = """        updatePastSalesSummary();
        if (window.KpiYearStore && typeof KpiYearStore.setPastSalesEditEnabled === 'function') {
          KpiYearStore.setPastSalesEditEnabled(false);
        }
        renderPastSalesTable();
        modal.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }"""

RENDER_PS_GUARD_OLD = """        updateFilterToggleActive();
        updateSalesSortToggleActive();
        updatePastSalesYmBdCount();
      }

      function scrollToViewMonth() {"""

RENDER_PS_GUARD_NEW = """        updateFilterToggleActive();
        updateSalesSortToggleActive();
        updatePastSalesYmBdCount();
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyPastSales === 'function') {
          window.__KPI_EDIT_GUARDS.applyPastSales();
        }
      }

      function scrollToViewMonth() {"""

SET_PS_TAB_OLD = """        if (t === 'analyze') renderPastSalesAnalyze();
      }"""

SET_PS_TAB_NEW = """        if (t === 'analyze') renderPastSalesAnalyze();
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyPastSales === 'function') {
          window.__KPI_EDIT_GUARDS.applyPastSales();
        }
      }"""


def inject_ym_nav_guard_ignore(text: str) -> str:
    for nav_id in PAST_SALES_YM_NAV_IDS:
        needle = f'id="{nav_id}"'
        if needle not in text:
            continue
        if f'id="{nav_id}" data-kpi-guard-ignore' in text:
            continue
        text = text.replace(needle, f'{needle} data-kpi-guard-ignore', 1)
    return text


def inject_edit_guards_js(text: str) -> str:
    guards = (ROOT / "scripts" / "_kpi_edit_guards.js").read_text(encoding="utf-8")
    if KPI_EDIT_GUARDS_MARKER not in text:
        raise SystemExit("KPI-EDIT-GUARDS marker not found")
    pattern = re.compile(
        r"/\* KPI-EDIT-GUARDS \*/.*?\n      \(function \(\) \{.*?\n      \}\)\(\);\n",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit("KPI-EDIT-GUARDS block not found")
    return pattern.sub(guards.rstrip() + "\n", text, count=1)


def remove_legacy_toggle(text: str) -> str:
    text = re.sub(
        r"\n        <div\n          class=\"(?:past-sales-modal__edit-mode|kpi-past-sales-edit-mode)\"[\s\S]*?\n        </div>",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"\n    \.past-sales-modal__edit-mode \{[\s\S]*?\n    \}\n    \.past-sales-modal__edit-mode-btn\.is-active \{[\s\S]*?\n    \}",
        "",
        text,
        count=1,
    )
    return text


def inject_toggle_html(text: str, ja: bool) -> str:
    if 'id="past-sales-edit-mode"' in text:
        return text
    toggle = PAST_SALES_TOGGLE_JA if ja else PAST_SALES_TOGGLE_EN
    anchor = 'id="past-sales-modal-save"'
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("past-sales-modal-save anchor not found")
    end = text.find("</button>", pos)
    if end < 0:
        raise SystemExit("past-sales-modal-save closing tag not found")
    end += len("</button>")
    return text[:end] + "\n" + toggle + text[end:]


def inject_toggle_css(text: str) -> str:
    if TOGGLE_CSS_MARKER in text:
        pattern = re.compile(
            r"/\* KPI-PAST-SALES-EDIT-TOGGLE-CSS \*/[\s\S]*?/\* /KPI-PAST-SALES-EDIT-TOGGLE-CSS \*/\n",
        )
        return pattern.sub(PAST_SALES_TOGGLE_CSS.lstrip(), text, count=1)
    anchor = "/* /KPI-PHASE5-TOGGLE-CSS */"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("KPI-PHASE5-TOGGLE-CSS end marker not found")
    insert_at = pos + len(anchor)
    return text[:insert_at] + "\n" + PAST_SALES_TOGGLE_CSS.lstrip() + text[insert_at:]


def patch_annual(path: Path, ja: bool) -> None:
    text = path.read_text(encoding="utf-8")
    text = remove_legacy_toggle(text)
    text = inject_toggle_html(text, ja)
    text = inject_ym_nav_guard_ignore(text)
    text = inject_toggle_css(text)
    if PAST_SALES_OPEN_OLD in text:
        text = text.replace(PAST_SALES_OPEN_OLD, PAST_SALES_OPEN_NEW, 1)
    elif PAST_SALES_OPEN_ALT in text:
        text = text.replace(PAST_SALES_OPEN_ALT, PAST_SALES_OPEN_NEW, 1)
    if RENDER_PS_GUARD_OLD in text:
        text = text.replace(RENDER_PS_GUARD_OLD, RENDER_PS_GUARD_NEW, 1)
    if SET_PS_TAB_OLD in text:
        text = text.replace(SET_PS_TAB_OLD, SET_PS_TAB_NEW, 1)
    text = inject_edit_guards_js(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_monthly(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_edit_guards_js(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path, ja in ANNUAL_TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_annual(path, ja)
    for path in MONTHLY_TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_monthly(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

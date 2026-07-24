#!/usr/bin/env python3
"""Fix Annual cockpit centering (extra </div>) and Past Sales modal CSS conflicts (PS-1 vs AEM clone)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [ROOT / "app/annual/index.html", ROOT / "en/app/annual/index.html"]

# Shell chrome missing from PS-1 (clone had position:absolute + overrides).
BUTTON_CHROME_CSS = """
    .past-sales-modal__close,
    .past-sales-modal__csv,
    .past-sales-modal__undo,
    .past-sales-modal__save {
      position: absolute;
      padding: 0;
      margin: 0;
      border: 1px solid var(--psm-line);
      border-radius: 2px;
      background: var(--psm-bg-inactive);
      color: var(--psm-cyan);
      font-weight: 600;
      line-height: 1;
      letter-spacing: 0.02em;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
      font-family: inherit;
    }
    .past-sales-modal__undo:disabled {
      opacity: 0.35;
      cursor: default;
    }
    .past-sales-modal__close:hover,
    .past-sales-modal__close:focus-visible,
    .past-sales-modal__csv:hover,
    .past-sales-modal__csv:focus-visible,
    .past-sales-modal__undo:hover,
    .past-sales-modal__undo:focus-visible,
    .past-sales-modal__save:hover,
    .past-sales-modal__save:focus-visible {
      background: var(--psm-bg-active-70);
      outline: none;
    }
"""

# Table / colhead-detail rules from AEM clone — kept without layout-shell overrides.
PSM_DETAIL_CSS = """
    /* Past Sales modal — table & colhead detail (PS-1 supplement) */
    .past-sales-modal__colhead-date-merged {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      flex-wrap: nowrap;
      min-height: 40px;
      min-width: 0;
      max-width: 100%;
      position: relative;
      font-size: var(--psm-fs-colhead);
    }
    .past-sales-modal__colhead-date-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      margin: 0;
      padding: 4px 6px;
      border: 0;
      background: none;
      color: inherit;
      font-family: inherit;
      font-size: var(--psm-fs-colhead);
      line-height: 1;
      cursor: pointer;
      text-decoration: underline;
      text-decoration-color: rgba(88, 225, 243, 0.75);
      text-underline-offset: 3px;
    }
    .past-sales-modal__colhead-date-btn:hover,
    .past-sales-modal__colhead-date-btn:focus-visible {
      color: #9ef6ff;
      text-decoration-color: var(--psm-cyan);
      outline: none;
    }
    .past-sales-modal__colhead-date-native {
      position: absolute;
      left: 0;
      top: 0;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: 0;
      border: 0;
      opacity: 0;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
    }
    .past-sales-modal__colhead-sales {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;
      min-height: 40px;
      font-size: var(--psm-fs-colhead);
    }
    .past-sales-modal__sales-sort {
      position: relative;
      display: inline-flex;
      align-items: center;
    }
    .past-sales-modal__sales-sort-toggle {
      margin: 0;
    }
    .past-sales-modal__sales-sort-orders {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-bottom: 8px;
    }
    .past-sales-modal__sales-sort-section-label {
      font-size: 11px;
      line-height: 1.3;
      color: var(--psm-cyan);
      opacity: 0.85;
      margin: 0 0 6px;
    }
    .past-sales-modal__sales-sort-btn {
      display: block;
      width: 100%;
      margin-top: 6px;
      padding: 8px 10px;
      box-sizing: border-box;
      border: 1px solid var(--psm-line);
      border-radius: 2px;
      background: rgba(88, 225, 243, 0.15);
      color: var(--psm-cyan);
      font-family: inherit;
      font-size: 11px;
      line-height: 1.35;
      text-align: left;
      cursor: pointer;
    }
    .past-sales-modal__sales-sort-amounts {
      max-height: min(50vh, 280px);
      overflow-y: auto;
      margin: 0 0 8px;
    }
    .past-sales-modal__sales-sort-amounts .past-sales-modal__sales-sort-btn {
      margin-top: 6px;
    }
    .past-sales-modal__sales-sort-amounts .past-sales-modal__sales-sort-btn:first-child {
      margin-top: 0;
    }
    .past-sales-modal__sales-sort-btn:hover,
    .past-sales-modal__sales-sort-btn:focus-visible {
      background: rgba(88, 225, 243, 0.3);
      outline: none;
    }
    .past-sales-modal__sales-sort-btn.is-active {
      background: rgba(88, 225, 243, 0.38);
      box-shadow: 0 0 0 1px var(--psm-cyan);
    }
    .past-sales-modal__colhead-dayoff {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
      min-height: 40px;
      padding: 4px 2px;
    }
    .past-sales-modal__colhead-dayoff-title {
      font-size: var(--psm-fs-colhead);
      line-height: 1;
    }
    .past-sales-modal__select-all {
      padding: 0;
      border: 0;
      background: none;
      color: var(--psm-cyan);
      font-size: var(--psm-fs-colhead);
      line-height: 1;
      text-decoration: underline;
      cursor: pointer;
      font-family: inherit;
    }
    .past-sales-modal__select-all:hover,
    .past-sales-modal__select-all:focus-visible {
      color: #9ef6ff;
      outline: none;
    }
    .past-sales-modal__sort-icon {
      font-size: 9px;
      opacity: 0.85;
    }
    .past-sales-modal__date-filter {
      position: relative;
      display: inline-flex;
      align-items: center;
    }
    .past-sales-modal__date-filter-toggle {
      margin: 0 0 0 2px;
      padding: 2px 8px;
      border: 1px solid var(--psm-line);
      border-radius: 2px;
      background: rgba(88, 225, 243, 0.15);
      color: var(--psm-cyan);
      font-family: inherit;
      font-size: 10px;
      line-height: 1.2;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .past-sales-modal__date-filter-toggle:hover,
    .past-sales-modal__date-filter-toggle:focus-visible {
      background: rgba(88, 225, 243, 0.32);
      outline: none;
    }
    .past-sales-modal__date-filter-toggle.is-active {
      background: rgba(88, 225, 243, 0.38);
      box-shadow: 0 0 0 1px var(--psm-cyan);
    }
    .past-sales-modal__date-filter-panel {
      position: absolute;
      top: calc(100% + 6px);
      left: 50%;
      transform: translateX(-50%);
      min-width: 220px;
      z-index: 20;
      padding: 10px 12px 12px;
      box-sizing: border-box;
      background: #2f2f2f;
      border: 1px solid var(--psm-line);
      border-radius: 3px;
      box-shadow: 0 10px 32px rgba(0, 0, 0, 0.55);
      color: var(--psm-cyan);
    }
    .past-sales-modal__date-filter-panel[hidden] {
      display: none !important;
    }
    .past-sales-modal__filter-row {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 5px 0;
      font-size: 12px;
      cursor: pointer;
    }
    .past-sales-modal__filter-row input {
      width: 14px;
      height: 14px;
      margin: 0;
      flex-shrink: 0;
      cursor: pointer;
      accent-color: #0f9403;
    }
    .past-sales-modal__filter-clear {
      display: block;
      width: 100%;
      margin-top: 10px;
      padding: 6px 8px;
      box-sizing: border-box;
      border: 1px solid var(--psm-line);
      border-radius: 2px;
      background: rgba(88, 225, 243, 0.18);
      color: var(--psm-cyan);
      font-family: inherit;
      font-size: 11px;
      cursor: pointer;
    }
    .past-sales-modal__filter-clear:hover,
    .past-sales-modal__filter-clear:focus-visible {
      background: rgba(88, 225, 243, 0.35);
      outline: none;
    }
    .past-sales-modal__scroll:hover::-webkit-scrollbar,
    .past-sales-modal__scroll.is-scrolling::-webkit-scrollbar {
      width: var(--psm-scrollbar-w);
    }
    .past-sales-modal__scroll:hover::-webkit-scrollbar-track,
    .past-sales-modal__scroll.is-scrolling::-webkit-scrollbar-track {
      background: rgba(88, 225, 243, 0.15);
    }
    .past-sales-modal__scroll:hover::-webkit-scrollbar-thumb,
    .past-sales-modal__scroll.is-scrolling::-webkit-scrollbar-thumb {
      background: #0f9403;
      border-radius: 3px;
    }
    .past-sales-modal__table {
      width: 100%;
      max-width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      table-layout: fixed;
    }
    .past-sales-modal__col-g-month {
      width: calc(100% * 40 / 929);
    }
    .past-sales-modal__col-g-date {
      width: calc(100% * 150 / 929);
    }
    .past-sales-modal__col-g-date-merged {
      width: calc(100% * 190 / 929);
    }
    .past-sales-modal__col-g-bday {
      width: calc(100% * 90 / 929);
    }
    .past-sales-modal__col-g-sales {
      width: calc(100% * 215 / 929);
    }
    .past-sales-modal__col-g-monthly {
      width: calc(100% * 215 / 929);
    }
    .past-sales-modal__col-g-annual {
      width: calc(100% * 219 / 929);
    }
    .past-sales-modal__table td {
      border: solid var(--psm-line);
      border-width: 0 1px 1px 0;
      box-sizing: border-box;
      vertical-align: middle;
      background: var(--psm-bg-inactive);
      color: var(--psm-cyan);
    }
    .past-sales-modal__table tbody:first-child tr:first-child td {
      border-top-width: 1px;
    }
    .past-sales-modal__table tr td:first-child {
      border-left-width: 1px;
    }
    .past-sales-modal__table tr.past-sales-modal__row--off td {
      background: var(--psm-row-off-fill);
    }
    .past-sales-modal__table td.past-sales-modal__month-td {
      width: var(--psm-col-month);
      padding: 0;
      vertical-align: top;
      text-align: center;
      position: relative;
      background: var(--psm-bg-inactive);
    }
    .past-sales-modal__table tr.past-sales-modal__row--off td.past-sales-modal__month-td {
      background: var(--psm-bg-inactive);
    }
    .past-sales-modal__month-td-label {
      position: -webkit-sticky;
      position: sticky;
      top: 0;
      z-index: 2;
      display: block;
      box-sizing: border-box;
      width: var(--psm-col-month);
      margin: 0 auto;
      padding: 12px 2px 10px;
      text-align: center;
      background: transparent;
      border: none;
      box-shadow: none;
      outline: none;
      color: var(--psm-cyan);
      font-size: var(--psm-fs-month);
      line-height: 1.1;
      letter-spacing: 0.14em;
      writing-mode: vertical-rl;
      text-orientation: upright;
      transform: none;
    }
    .past-sales-modal__date-td {
      width: var(--psm-col-date);
      height: 40px;
      padding: 0 8px;
      font-size: var(--psm-fs-body);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .past-sales-modal__table--no-month .past-sales-modal__date-td {
      width: var(--psm-col-date-merged);
    }
    .past-sales-modal__cb-td {
      width: var(--psm-col-bday);
      height: 40px;
      text-align: center;
    }
    .past-sales-modal__cb {
      width: 16px;
      height: 16px;
      margin: 0;
      cursor: pointer;
      accent-color: #0f9403;
    }
    .past-sales-modal__sales-td {
      width: var(--psm-col-sales);
      height: 40px;
      padding: 0 8px;
    }
    .past-sales-modal__monthly-td,
    .past-sales-modal__annual-td {
      height: 40px;
      padding: 0 8px;
      font-size: var(--psm-fs-body);
      text-align: right;
    }
    .past-sales-modal__monthly-td {
      width: var(--psm-col-monthly);
    }
    .past-sales-modal__annual-td {
      width: var(--psm-col-annual);
    }
    .past-sales-modal__sales-input {
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
      border: 0;
      background: transparent;
      color: var(--psm-cyan);
      font-size: var(--psm-fs-body);
      line-height: 1.2;
      font-family: inherit;
      text-align: right;
      padding: 2px 0;
    }
    .past-sales-modal__sales-input:focus {
      outline: 1px solid var(--psm-cyan);
      outline-offset: 1px;
    }
    body.office-mode .past-sales-modal__close,
    body.office-mode .past-sales-modal__undo,
    body.office-mode .past-sales-modal__save,
    body.office-mode .past-sales-modal__csv,
    body.office-mode .past-sales-modal__ym-cell {
      border-color: #333;
      color: #111;
    }
    body.office-mode .past-sales-modal__close,
    body.office-mode .past-sales-modal__undo,
    body.office-mode .past-sales-modal__save,
    body.office-mode .past-sales-modal__csv {
      background: #f0f0f0;
    }
    body.office-mode .past-sales-modal__ym-arrow {
      border-color: #333;
      color: #111;
      background: #e8e8e8;
    }
    body.office-mode .past-sales-modal__ym-arrow:hover,
    body.office-mode .past-sales-modal__ym-arrow:focus-visible {
      background: #ddd;
    }
    body.office-mode .past-sales-modal__close:hover,
    body.office-mode .past-sales-modal__close:focus-visible,
    body.office-mode .past-sales-modal__undo:hover,
    body.office-mode .past-sales-modal__undo:focus-visible,
    body.office-mode .past-sales-modal__save:hover,
    body.office-mode .past-sales-modal__save:focus-visible,
    body.office-mode .past-sales-modal__csv:hover,
    body.office-mode .past-sales-modal__csv:focus-visible {
      background: #ddd;
    }
    body.office-mode .past-sales-modal__ym-select {
      color: #111;
      background: transparent;
      text-decoration-color: rgba(0, 0, 0, 0.45);
    }
    body.office-mode .past-sales-modal__ym-select:hover {
      text-decoration-color: #111;
    }
    body.office-mode .past-sales-modal__ym-select option {
      background: #fff;
      color: #111;
    }
    body.office-mode .past-sales-modal__backdrop {
      background: rgba(0, 0, 0, 0.35);
    }
    body.office-mode .past-sales-modal {
      font-family: 'BIZ UDPGothic', sans-serif !important;
    }
    body.office-mode .past-sales-modal__select-all {
      color: #111;
    }
    body.office-mode .past-sales-modal__colhead-date-btn {
      color: #111;
      text-decoration-color: rgba(0, 0, 0, 0.45);
    }
    body.office-mode .past-sales-modal__colhead-date-btn:hover,
    body.office-mode .past-sales-modal__colhead-date-btn:focus-visible {
      color: #000;
      text-decoration-color: #111;
    }
    body.office-mode .past-sales-modal__date-filter-toggle {
      border-color: #333;
      color: #111;
      background: #e8e8e8;
    }
    body.office-mode .past-sales-modal__date-filter-panel {
      background: #fff;
      border-color: #333;
      color: #111;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    body.office-mode .past-sales-modal__filter-clear {
      border-color: #333;
      color: #111;
      background: #eee;
    }
    body.office-mode .past-sales-modal__scroll:hover,
    body.office-mode .past-sales-modal__scroll.is-scrolling {
      scrollbar-color: #555 #ddd;
    }
    body.office-mode .past-sales-modal__scroll:hover::-webkit-scrollbar-thumb,
    body.office-mode .past-sales-modal__scroll.is-scrolling::-webkit-scrollbar-thumb {
      background: #555;
    }
"""

DUPLICATE_CSS_RE = re.compile(
    r"\n    /\* Past Sales モーダル[^\n]*\*/\s*\n"
    r"    \.past-sales-modal \{[^}]+\}\n"
    r".*?"
    r"    body\.office-mode \.past-sales-modal__scroll::-webkit-scrollbar-thumb \{[^}]+\}\n",
    re.DOTALL,
)

PS1_MARKER = "/* Past Sales modal — PS-1 shell"

EXTRA_DIV_RE = re.compile(
    r"(      </div>\n)      </div>\n(      <section class=\"annual-monthly-data\" id=\"annual-monthly-data\">)"
)

MARKER_BUTTON_CHROME = "    .past-sales-modal__close,\n    .past-sales-modal__csv,"
MARKER_DETAIL = "    /* Past Sales modal — table & colhead detail (PS-1 supplement) */"


def _psm_css_bundle() -> str:
    from build_past_sales_modal import COCKPIT_CSS, PS_LAYOUT_CSS  # noqa: WPS433

    return PS_LAYOUT_CSS + PSM_DETAIL_CSS + COCKPIT_CSS


def patch_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    original = text
    changes: list[str] = []

    if EXTRA_DIV_RE.search(text):
        text = EXTRA_DIV_RE.sub(r"\1\2", text, count=1)
        changes.append("removed extra </div> before cockpit")

    m = DUPLICATE_CSS_RE.search(text)
    if m:
        text = text[: m.start()] + text[m.end() :]
        changes.append("removed duplicate Past Sales AEM-clone CSS")

    if PS1_MARKER not in text:
        anchor = re.search(r"    /\* Annual Edit", text)
        if anchor:
            text = text[: anchor.start()] + _psm_css_bundle() + "\n" + text[anchor.start() :]
            changes.append("restored PS-1 + detail + cockpit CSS")

    if MARKER_BUTTON_CHROME not in text:
        anchor = "    .past-sales-modal__close {\n      top: 22px;"
        if anchor in text:
            text = text.replace(anchor, BUTTON_CHROME_CSS + anchor, 1)
            changes.append("added button chrome CSS")

    if MARKER_DETAIL not in text:
        anchor = "    .past-sales-modal__colhead-bday,\n    .past-sales-modal__colhead-sales {"
        if anchor in text:
            insert_after = (
                "    .past-sales-modal__colhead-bday,\n"
                "    .past-sales-modal__colhead-sales {\n"
                "      background: var(--psm-bg-active-55);\n"
                "    }"
            )
            if insert_after in text:
                text = text.replace(insert_after, insert_after + PSM_DETAIL_CSS, 1)
                changes.append("added table/detail CSS supplement")

    if text != original:
        path.write_text(text, encoding="utf-8")
    return {"path": str(path), "changed": text != original, "changes": changes}


def main() -> int:
    for path in PATHS:
        result = patch_file(path)
        status = ", ".join(result["changes"]) if result["changes"] else "no changes"
        print(f"{path.name}: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

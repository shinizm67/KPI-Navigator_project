#!/usr/bin/env python3
"""Inject Past Sales modal + cockpit controls into annual index.html (JA + EN). PS-1 milestone."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_kpi_year_store import HYDRATE_PAST_NEW  # noqa: E402

JA_PATH = ROOT / "app/annual/index.html"
EN_PATH = ROOT / "en/app/annual/index.html"

MARKER = 'id="past-sales-modal"'

TEXT = {
    "ja": {
        "cockpit_aria": "年次売上コントロール",
        "past_label": "過去売上",
        "past_aria": "過去売上 — 過去の日次売上を入力します",
        "past_title": "過去の日次売上のみ。今年は編集しない",
        "sales_label": "売上",
        "sales_aria": "売上 — 当年の日次売上（準備中）",
        "sales_title": "当年の日次売上（準備中）",
        "modal_title": "過去売上データ",
        "close": "閉じる",
        "csv": "CSV取込",
        "undo": "戻る",
        "save": "保存",
        "tablist": "過去売上ビュー",
        "tab_input": "Input",
        "tab_analyze": "Analyze",
        "summary_aria": "過去売上サマリー",
        "sum1_label": "累計入力売上",
        "sum2_label": "参考年間売上",
        "sum3_label": "残り／入力進捗",
        "year": "年",
        "month": "月",
        "year_prev": "前年",
        "year_next": "翌年",
        "month_prev": "前月",
        "month_next": "翌月",
        "col_date": "日付",
        "col_bday": "営業日",
        "col_sales": "売上",
        "col_monthly": "月次合計",
        "col_annual": "年間合計",
        "select_all": "すべて選択",
        "filter_holiday": "祝日（休日カレンダー連携時）",
        "filter_clear": "フィルターを解除",
        "date_filter_aria": "曜日・祝日で表示を絞り込む",
        "date_filter_group": "表示する曜日・祝日",
        "date_pick": "日付を選んで一覧の先頭へ",
        "table_aria": "過去売上日次一覧",
        "analyze_placeholder": "Analyze（準備中）",
        "csv_stub": "CSV取込は次フェーズで実装予定です。",
        "unsaved_close": "変更が保存されていません。保存せずに閉じますか？",
        "dow": ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"],
        "img_prefix": "../../images/",
    },
    "en": {
        "cockpit_aria": "Annual sales controls",
        "past_label": "Past Sales",
        "past_aria": "Past Sales — Enter historical daily sales",
        "past_title": "Historical daily sales only. Current year is not edited here.",
        "sales_label": "Sales",
        "sales_aria": "Sales — This year's daily sales (coming soon)",
        "sales_title": "This year's daily sales (coming soon)",
        "modal_title": "Past Sales Data",
        "close": "Close",
        "csv": "Import CSV",
        "undo": "UNDO",
        "save": "Save",
        "tablist": "Past sales views",
        "tab_input": "Input",
        "tab_analyze": "Analyze",
        "summary_aria": "Past sales summary",
        "sum1_label": "Cumulative Input Sales",
        "sum2_label": "Reference Annual Sales",
        "sum3_label": "Remaining / Input Progress",
        "year": "Year",
        "month": "Month",
        "year_prev": "Previous year",
        "year_next": "Next year",
        "month_prev": "Previous month",
        "month_next": "Next month",
        "col_date": "Date",
        "col_bday": "B. DAY",
        "col_sales": "Sales",
        "col_monthly": "Monthly Total",
        "col_annual": "Annual Total",
        "select_all": "Select all",
        "filter_holiday": "National holidays (when calendar linked)",
        "filter_clear": "Clear filter",
        "date_filter_aria": "Filter by weekday or holiday",
        "date_filter_group": "Weekdays and holidays to show",
        "date_pick": "Pick a date to scroll the list",
        "table_aria": "Past sales daily list",
        "analyze_placeholder": "Analyze (coming soon)",
        "csv_stub": "CSV import will be implemented in a coming phase.",
        "unsaved_close": "You have unsaved changes. Close without saving?",
        "dow": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "img_prefix": "../../../images/",
    },
}

COCKPIT_CSS = """
    .monthly-access-controls {
      width: min(100%, 1020px);
      margin: 8px auto 0;
      padding-bottom: 50px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-height: 46px;
    }
    .monthly-access-controls__spacer {
      flex: 1 1 auto;
      min-width: 12px;
    }
    .monthly-access-btn {
      position: relative;
      width: 112px;
      height: 46px;
      border: 0;
      padding: 0;
      background: transparent;
      color: #58e1f3;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-family: 'Orbitron', sans-serif;
      font-size: 14px;
      line-height: 1;
      letter-spacing: 0.02em;
      cursor: pointer;
    }
    .monthly-access-btn__frame {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      display: block;
      pointer-events: none;
    }
    .monthly-access-btn__label {
      position: relative;
      z-index: 1;
      transform: translateY(0.5px);
      white-space: nowrap;
    }
    .monthly-access-btn--past-sales:hover .monthly-access-btn__label,
    .monthly-access-btn--past-sales:focus-visible .monthly-access-btn__label {
      text-shadow: 0 0 8px rgba(55, 10, 255, 0.45);
    }
    .monthly-access-btn--current-sales:hover .monthly-access-btn__label,
    .monthly-access-btn--current-sales:focus-visible .monthly-access-btn__label {
      text-shadow: 0 0 8px rgba(88, 225, 243, 0.45);
    }
    .office-mode .monthly-access-btn--past-sales {
      color: #0a2a5c;
    }
    .office-mode .monthly-access-btn--past-sales .monthly-access-btn__frame {
      filter: none;
    }
"""

PS_LAYOUT_CSS = """
    /* Past Sales modal — PS-1 shell (see docs/past-sales-floating-window-memo.md) */
    .past-sales-modal {
      --psm-cyan: #58e1f3;
      --psm-line: #58e1f3;
      --psm-bg-inactive: rgba(88, 225, 243, 0.44);
      --psm-bg-active-55: rgba(88, 225, 243, 0.55);
      --psm-bg-active-70: rgba(88, 225, 243, 0.7);
      --psm-row-off-fill: rgba(88, 225, 243, 0.22);
      --psm-panel-bg: #100052;
      --psm-frame: #370aff;
      --psm-panel-w: 1100px;
      --psm-inner-w: 1020px;
      --psm-pad-x: calc((var(--psm-panel-w) - var(--psm-inner-w)) / 2);
      --psm-title-top: 29px;
      --psm-tab-top: 122px;
      --psm-tab-left: 106px;
      --psm-tab-gap: 5px;
      --psm-body-top: 152px;
      --psm-fs-body: 16px;
      --psm-fs-colhead: 13px;
      --psm-fs-title: 25px;
      --psm-close-size: 20px;
      --psm-header-btn-h: 40px;
      --psm-header-btn-top: 22px;
      --psm-summary-label-w: calc(var(--psm-inner-w) * 429 / 925);
      --psm-summary-value-w: calc(var(--psm-inner-w) * 496 / 925);
      --psm-summary-value-mid-w: calc(var(--psm-summary-value-w) * 3.5 / 5);
      --psm-summary-value-pct-w: calc(var(--psm-summary-value-w) * 1.5 / 5);
      --psm-summary-row-h: 40px;
      --psm-fs-month: 20px;
      --psm-scrollbar-w: 8px;
      --psm-col-month: calc(var(--psm-inner-w) * 40 / 929);
      --psm-col-date: calc(var(--psm-inner-w) * 150 / 929);
      --psm-col-date-merged: calc(var(--psm-col-month) + var(--psm-col-date));
      --psm-col-bday: calc(var(--psm-inner-w) * 90 / 929);
      --psm-col-sales: calc(var(--psm-inner-w) * 215 / 929);
      --psm-col-monthly: calc(var(--psm-inner-w) * 215 / 929);
      --psm-col-annual: calc(var(--psm-inner-w) * 219 / 929);
      --psm-table-w: var(--psm-inner-w);
      font-family: 'BIZ UDPGothic', sans-serif;
      box-sizing: border-box;
    }
    html[lang='en'] body.si-fi:not(.office-mode) .past-sales-modal {
      font-family: 'Orbitron', sans-serif;
    }
    .past-sales-modal[hidden] {
      display: none !important;
    }
    .past-sales-modal {
      position: fixed;
      inset: 0;
      z-index: 20055;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      box-sizing: border-box;
    }
    .past-sales-modal__backdrop {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.52);
      cursor: pointer;
    }
    .past-sales-modal__panel {
      position: relative;
      width: var(--psm-panel-w);
      height: min(1100px, calc(100vh - 32px));
      max-width: calc(100vw - 32px);
      max-height: calc(100vh - 32px);
      box-sizing: border-box;
      background: var(--psm-panel-bg);
      border: 2px solid var(--psm-frame);
      border-radius: 3px;
      display: flex;
      flex-direction: column;
      padding: 0 var(--psm-pad-x) 14px;
      box-shadow: 0 12px 48px rgba(0, 0, 0, 0.45);
      z-index: 1;
      color: var(--psm-cyan);
      overflow: hidden;
    }
    .past-sales-modal__title {
      position: absolute;
      top: var(--psm-title-top);
      left: 0;
      right: 0;
      margin: 0;
      text-align: center;
      font-size: var(--psm-fs-title);
      font-weight: 700;
      line-height: 1.2;
      pointer-events: none;
    }
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
      font-size: var(--psm-fs-body);
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
    .past-sales-modal__close {
      position: absolute;
      padding: 0;
      margin: 0;
      border: 1px solid var(--psm-line);
      border-radius: 2px;
      background: var(--psm-bg-inactive);
      color: var(--psm-cyan);
      font-size: 14px;
      font-weight: 600;
      line-height: 1;
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
    .past-sales-modal__close {
      top: calc(
        var(--psm-header-btn-top) + (var(--psm-header-btn-h) - var(--psm-close-size)) / 2
      );
      left: 26px;
      width: var(--psm-close-size);
      height: var(--psm-close-size);
    }
    .past-sales-modal__csv {
      top: var(--psm-header-btn-top);
      left: 92px;
      width: 142px;
      height: var(--psm-header-btn-h);
    }
    .past-sales-modal__undo {
      top: var(--psm-header-btn-top);
      right: 206px;
      width: 118px;
      height: var(--psm-header-btn-h);
    }
    .past-sales-modal__save {
      top: var(--psm-header-btn-top);
      right: 84px;
      width: 118px;
      height: var(--psm-header-btn-h);
    }
    .past-sales-modal__tabs {
      position: absolute;
      top: var(--psm-tab-top);
      left: var(--psm-tab-left);
      display: flex;
      align-items: flex-end;
      gap: var(--psm-tab-gap);
      margin-bottom: -1px;
      z-index: 3;
    }
    .past-sales-modal__tab {
      border: 0;
      border-radius: 5px 5px 0 0;
      color: var(--psm-cyan);
      font-family: inherit;
      cursor: pointer;
      padding: 0;
      width: 118px;
      height: 27px;
      font-size: 16px;
      background: rgba(88, 225, 243, 0.33);
    }
    .past-sales-modal__tab.is-active {
      width: 131px;
      height: 30px;
      font-size: 20px;
      background: rgba(88, 225, 243, 0.7);
    }
    .past-sales-modal__body {
      margin-top: var(--psm-body-top);
      display: flex;
      flex-direction: column;
      align-items: stretch;
      flex: 1;
      min-height: 0;
      width: 100%;
    }
    .past-sales-modal__input-stack {
      display: flex;
      flex-direction: column;
      align-items: stretch;
      flex: 1;
      min-height: 0;
      min-width: 0;
      width: 100%;
    }
    .past-sales-modal__input-stack > .past-sales-modal__summary,
    .past-sales-modal__input-stack > .past-sales-modal__ym,
    .past-sales-modal__input-stack > .past-sales-modal__colhead,
    .past-sales-modal__input-stack > .past-sales-modal__scroll,
    .past-sales-modal__input-stack > .past-sales-modal__analyze-scroll {
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
    }
    .past-sales-modal__summary {
      flex-shrink: 0;
      border: 1px solid var(--psm-line);
      border-top: 1px solid #58e1f3;
      background: var(--psm-bg-inactive);
      box-sizing: border-box;
    }
    .past-sales-modal__summary-row {
      display: grid;
      align-items: stretch;
      width: 100%;
      height: var(--psm-summary-row-h);
      min-height: var(--psm-summary-row-h);
      border-bottom: 1px solid var(--psm-line);
      box-sizing: border-box;
    }
    .past-sales-modal__summary-row:last-child {
      border-bottom: 0;
    }
    .past-sales-modal__summary-row--cols-2 {
      grid-template-columns: calc(100% * 429 / 925) calc(100% * 496 / 925);
    }
    .past-sales-modal__summary-row--cols-3 {
      grid-template-columns:
        calc(100% * 429 / 925)
        calc(100% * 347.2 / 925)
        calc(100% * 148.8 / 925);
    }
    .past-sales-modal__summary-row > * {
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      min-height: var(--psm-summary-row-h);
      padding: 0 8px;
      font-size: var(--psm-fs-body);
      border-right: 1px solid var(--psm-line);
      box-sizing: border-box;
    }
    .past-sales-modal__summary-row--reference > * {
      background: var(--psm-bg-active-55);
    }
    .past-sales-modal__summary-row--reference {
      background: var(--psm-bg-active-55);
    }
    .past-sales-modal__summary-reference-input {
      width: 100%;
      height: var(--psm-summary-row-h);
      min-height: var(--psm-summary-row-h);
      margin: 0;
      border: 0;
      border-radius: 0;
      background-color: var(--psm-bg-active-55);
      -webkit-appearance: none;
      appearance: none;
      color: var(--psm-cyan);
      font-size: var(--psm-fs-body);
      font-family: inherit;
      font-weight: 600;
      text-align: center;
      padding: 0 8px;
      box-sizing: border-box;
    }
    .past-sales-modal__summary-reference-input::placeholder {
      color: var(--psm-cyan);
      opacity: 0.85;
    }
    .past-sales-modal__summary-reference-input:focus {
      outline: 1px solid var(--psm-cyan);
      outline-offset: -1px;
      background: var(--psm-bg-active-70);
    }
    .past-sales-modal__summary-row > *:last-child {
      border-right: 0;
    }
    .past-sales-modal__ym {
      display: grid;
      grid-template-columns: 5fr 5fr;
      margin: 0;
      flex-shrink: 0;
      border: 1px solid var(--psm-line);
      border-top: 0;
      border-bottom: 0;
      box-sizing: border-box;
    }
    .past-sales-modal__ym-cell {
      min-width: 0;
      height: 40px;
      box-sizing: border-box;
      border: 0;
      border-right: 1px solid var(--psm-line);
      background: var(--psm-bg-active-55);
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;
      font-size: var(--psm-fs-body);
      line-height: 1;
      color: var(--psm-cyan);
    }
    .past-sales-modal__ym-cell:last-child {
      border-right: 0;
    }
    .past-sales-modal__ym-arrow,
    .past-sales-modal__ym-select {
      border: none;
      background: transparent;
      color: inherit;
      font-family: inherit;
      font-size: var(--psm-fs-body);
      cursor: pointer;
    }
    .past-sales-modal__ym-select {
      text-decoration: underline;
      appearance: none;
      -webkit-appearance: none;
    }
    .past-sales-modal__colhead {
      display: grid;
      grid-template-columns:
        minmax(0, 190fr)
        minmax(0, 90fr)
        minmax(0, 215fr)
        minmax(0, 215fr)
        minmax(0, 219fr);
      flex-shrink: 0;
      width: 100%;
      overflow: hidden;
      border: 1px solid var(--psm-line);
      border-bottom: 0;
      box-sizing: border-box;
    }
    .past-sales-modal__colhead > div {
      box-sizing: border-box;
      min-width: 0;
      overflow: hidden;
      border-right: 1px solid var(--psm-line);
      background: var(--psm-bg-inactive);
      color: var(--psm-cyan);
      font-size: var(--psm-fs-colhead);
      min-height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
    }
    .past-sales-modal__colhead > div:last-child {
      border-right: 0;
    }
    .past-sales-modal__colhead-bday,
    .past-sales-modal__colhead-sales {
      background: var(--psm-bg-active-55);
    }
    .past-sales-modal__scroll {
      position: relative;
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      overflow-x: hidden;
      border: 1px solid var(--psm-line);
      box-sizing: border-box;
      background: var(--psm-bg-inactive);
      font-size: var(--psm-fs-body);
    }
    .past-sales-modal__scroll:not(:hover):not(.is-scrolling) {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
    .past-sales-modal__scroll:not(:hover):not(.is-scrolling)::-webkit-scrollbar {
      display: none;
      width: 0 !important;
      height: 0 !important;
    }
    .past-sales-modal__scroll:hover,
    .past-sales-modal__scroll.is-scrolling {
      scrollbar-width: thin;
      scrollbar-color: #0f9403 rgba(88, 225, 243, 0.15);
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
    .past-sales-modal__analyze-scroll {
      flex: 1;
      min-height: 0;
      overflow: auto;
      padding: 24px;
      font-size: var(--psm-fs-body);
      color: var(--psm-cyan);
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__input-only {
      display: none !important;
    }
    .past-sales-modal__panel[data-psm-tab='input'] #past-sales-pane-analyze {
      display: none !important;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] #past-sales-pane-analyze {
      display: block;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-cell--month {
      display: none;
    }
    body.office-mode .past-sales-modal__panel {
      border-color: #2b6cb0;
      color: #111;
      --psm-cyan: #111;
      --psm-line: #333;
      --psm-bg-inactive: rgba(0, 0, 0, 0.06);
      --psm-bg-active-55: rgba(0, 0, 0, 0.1);
      --psm-bg-active-70: rgba(0, 0, 0, 0.14);
      --psm-row-off-fill: rgba(0, 0, 0, 0.04);
      --psm-panel-bg: #e8f2ff;
      --psm-frame: #2b6cb0;
    }
    .office-mode .monthly-access-btn--past-sales {
      background: #dcecff;
      border-radius: 2px;
    }
"""

def _psm_detail_css() -> str:
    from patch_annual_ps_layout import PSM_DETAIL_CSS  # noqa: WPS433

    return PSM_DETAIL_CSS


PERSIST_PAST_FN = """      function persistPastSalesShared() {
        var ps = ensurePastSalesDaily();
        if (window.KpiYearStore) {
          KpiYearStore.persistFromPastSales(ps);
          var payload = {
            salesByDate: ps.salesByDate || {},
            businessDayByDate: ps.businessDayByDate || {},
            referenceAnnualSalesByYear: ps.referenceAnnualSalesByYear || {}
          };
          if (ps.lastSession && typeof ps.lastSession === 'object') {
            payload.lastSession = ps.lastSession;
          }
          window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.pastSalesShared', payload);
          return;
        }
        var payload = {
          salesByDate: ps.salesByDate || {},
          businessDayByDate: ps.businessDayByDate || {},
          referenceAnnualSalesByYear: ps.referenceAnnualSalesByYear || {}
        };
        if (ps.lastSession && typeof ps.lastSession === 'object') {
          payload.lastSession = ps.lastSession;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.pastSalesShared', payload);
      }"""


def extract_aem_css(text: str) -> str | None:
    m = re.search(r"    /\* Annual Edit[^\n]*\*/\s*\n    \.annual-edit-modal \{", text)
    if not m:
        return None
    start = m.start()
    end_m = re.search(
        r"    body\.office-mode \.annual-edit-modal__scroll::-webkit-scrollbar-thumb \{[^}]+\}\n",
        text[start:],
    )
    if not end_m:
        return None
    return text[start : start + end_m.end()]


def transform_aem_css_to_psm(block: str) -> str:
    out = block.replace("Annual Edit モーダル", "Past Sales モーダル")
    out = re.sub(r"Annual Edit modal[^\n]*", "Past Sales modal", out, count=1)
    out = out.replace("annual-edit-modal", "past-sales-modal")
    out = out.replace("--aem-", "--psm-")
    out = out.replace("var(--psm-cell-fill)", "var(--psm-bg-inactive)")
    out = out.replace("var(--psm-grid-w)", "var(--psm-inner-w)")
    out = out.replace("data-aem-", "data-psm-")
    return out


def build_cockpit_html(lang: str) -> str:
    t = TEXT[lang]
    p = t["img_prefix"]
    return f"""      <div class="monthly-access-controls" aria-label="{t["cockpit_aria"]}">
        <button
          type="button"
          class="monthly-access-btn monthly-access-btn--past-sales"
          id="annual-past-sales-btn"
          aria-label="{t["past_aria"]}"
          title="{t["past_title"]}"
        >
          <img
            src="{p}past_sales_button.svg"
            alt=""
            class="monthly-access-btn__frame"
            width="112"
            height="46"
            decoding="async"
            aria-hidden="true"
          >
          <span class="monthly-access-btn__label">{t["past_label"]}</span>
        </button>
        <div class="monthly-access-controls__spacer" aria-hidden="true"></div>
        <button
          type="button"
          class="monthly-access-btn monthly-access-btn--current-sales"
          id="annual-current-sales-btn"
          aria-label="{t["sales_aria"]}"
          title="{t["sales_title"]}"
          hidden
          disabled
        >
          <img
            src="{p}monthly_decoration_frame_edit.svg"
            alt=""
            class="monthly-access-btn__frame"
            width="112"
            height="46"
            decoding="async"
            aria-hidden="true"
          >
          <span class="monthly-access-btn__label">{t["sales_label"]}</span>
        </button>
      </div>
"""


def build_modal_html(lang: str) -> str:
    t = TEXT[lang]
    dow_rows = ""
    for i, label in enumerate(t["dow"]):
        dow_rows += (
            f'              <label class="past-sales-modal__filter-row">'
            f'<input type="checkbox" class="past-sales-modal__filter-dow" value="{i}" /> {label}</label>\n'
        )
    return f"""  <div
    class="past-sales-modal"
    id="past-sales-modal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="past-sales-modal-title"
    hidden
  >
    <div class="past-sales-modal__backdrop" id="past-sales-modal-backdrop" aria-hidden="true"></div>
    <div class="past-sales-modal__panel" id="past-sales-modal-body" role="document" data-psm-tab="input">
      <h2 id="past-sales-modal-title" class="past-sales-modal__title">{t["modal_title"]}</h2>
      <button type="button" class="past-sales-modal__close" id="past-sales-modal-close" aria-label="{t["close"]}">
        ×
      </button>
      <button type="button" class="past-sales-modal__csv" id="past-sales-modal-csv" aria-label="{t["csv"]}">
        {t["csv"]}
      </button>
      <button type="button" class="past-sales-modal__undo" id="past-sales-modal-undo" aria-label="{t["undo"]}" disabled>
        {t["undo"]}
      </button>
      <button type="button" class="past-sales-modal__save" id="past-sales-modal-save" aria-label="{t["save"]}">
        {t["save"]}
      </button>
      <div class="past-sales-modal__tabs" role="tablist" aria-label="{t["tablist"]}">
        <button
          type="button"
          class="past-sales-modal__tab is-active"
          id="past-sales-tab-input"
          role="tab"
          aria-selected="true"
          data-psm-tab="input"
        >
          {t["tab_input"]}
        </button>
        <button
          type="button"
          class="past-sales-modal__tab"
          id="past-sales-tab-analyze"
          role="tab"
          aria-selected="false"
          data-psm-tab="analyze"
        >
          {t["tab_analyze"]}
        </button>
      </div>
      <div class="past-sales-modal__body">
        <div class="past-sales-modal__input-stack">
        <div class="past-sales-modal__summary past-sales-modal__input-only" aria-label="{t["summary_aria"]}">
          <div class="past-sales-modal__summary-row past-sales-modal__summary-row--cols-2">
            <span>{t["sum1_label"]}</span>
            <span id="past-sales-summary-cumulative">—</span>
          </div>
          <div class="past-sales-modal__summary-row past-sales-modal__summary-row--cols-2 past-sales-modal__summary-row--reference">
            <span>{t["sum2_label"]}</span>
            <input
              type="text"
              class="past-sales-modal__summary-reference-input"
              id="past-sales-summary-reference"
              inputmode="numeric"
              placeholder="—"
              aria-label="{t["sum2_label"]}"
            />
          </div>
          <div class="past-sales-modal__summary-row past-sales-modal__summary-row--cols-3">
            <span>{t["sum3_label"]}</span>
            <span id="past-sales-summary-remaining">—</span>
            <span class="past-sales-modal__summary-pct" id="past-sales-summary-progress-pct">—</span>
          </div>
        </div>
        <div class="past-sales-modal__ym past-sales-modal__input-only">
          <div class="past-sales-modal__ym-cell">
            <label class="past-sales-modal__sr-only" for="past-sales-year-select">{t["year"]}</label>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="{t["year_prev"]}">
              ◀︎
            </button>
            <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="{t["year"]}"></select>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="{t["year_next"]}">
              ▶︎
            </button>
          </div>
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--month">
            <label class="past-sales-modal__sr-only" for="past-sales-month-select">{t["month"]}</label>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="{t["month_prev"]}">
              ◀︎
            </button>
            <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="{t["month"]}"></select>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="{t["month_next"]}">
              ▶︎
            </button>
          </div>
        </div>
        <div class="past-sales-modal__colhead past-sales-modal__input-only" aria-hidden="false">
          <div class="past-sales-modal__colhead-date-merged">
            <button type="button" class="past-sales-modal__colhead-date-btn" id="past-sales-date-header-btn">{t["col_date"]}</button>
            <div class="past-sales-modal__date-filter" id="past-sales-date-filter-wrap">
              <button
                type="button"
                class="past-sales-modal__date-filter-toggle"
                id="past-sales-date-filter-toggle"
                aria-expanded="false"
                aria-haspopup="true"
                aria-controls="past-sales-date-filter-panel"
                aria-label="{t["date_filter_aria"]}"
              >
                <span class="past-sales-modal__sort-icon" aria-hidden="true">▼</span>
              </button>
              <div
                id="past-sales-date-filter-panel"
                class="past-sales-modal__date-filter-panel"
                role="group"
                aria-label="{t["date_filter_group"]}"
                hidden
              >
{dow_rows}              <label class="past-sales-modal__filter-row">
                <input type="checkbox" id="past-sales-filter-holiday" /> {t["filter_holiday"]}
              </label>
              <button type="button" class="past-sales-modal__filter-clear" id="past-sales-filter-clear">
                {t["filter_clear"]}
              </button>
            </div>
          </div>
            <input
              type="date"
              id="past-sales-colhead-date-input"
              class="past-sales-modal__colhead-date-native"
              tabindex="-1"
              aria-label="{t["date_pick"]}"
            />
          </div>
          <div class="past-sales-modal__colhead-dayoff past-sales-modal__colhead-bday">
            <span class="past-sales-modal__colhead-dayoff-title">{t["col_bday"]}</span>
            <button type="button" class="past-sales-modal__select-all" id="past-sales-select-all">
              {t["select_all"]}
            </button>
          </div>
          <div class="past-sales-modal__colhead-sales">{t["col_sales"]}</div>
          <div class="past-sales-modal__colhead-monthly">{t["col_monthly"]}</div>
          <div class="past-sales-modal__colhead-annual">{t["col_annual"]}</div>
        </div>
        <div class="past-sales-modal__scroll past-sales-modal__input-only" id="past-sales-pane-input">
          <table class="past-sales-modal__table" id="past-sales-modal-table" aria-label="{t["table_aria"]}"></table>
        </div>
        <div class="past-sales-modal__analyze-scroll" id="past-sales-pane-analyze" hidden>
          <p>{t["analyze_placeholder"]}</p>
        </div>
        </div>
      </div>
    </div>
  </div>

"""


def extract_aem_js(text: str) -> str | None:
    m = re.search(
        r"<script>\s*\n    \(function \(\) \{\s*\n      var modal = document\.getElementById\('annual-edit-modal'\);",
        text,
    )
    if not m:
        return None
    end = text.find("})();\n  </script>", m.start())
    if end < 0:
        return None
    return text[m.start() : end + len("})();\n  </script>")]


AEM_PERSIST_FN = """      function persistAnnualDailyShared() {
        var d = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!d) return;
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', {
          targetSalesByDate: d.targetSalesByDate || {},
          businessDayByDate: d.businessDayByDate || {}
        });
      }"""

PSM_ENSURE_AND_PERSIST = """      function ensurePastSalesDaily() {
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.pastSales = window.__ANNUAL_DATA.pastSales || {
          salesByDate: {},
          businessDayByDate: {},
          referenceAnnualSalesByYear: {}
        };
        var ps = window.__ANNUAL_DATA.pastSales;
        ps.salesByDate = ps.salesByDate || {};
        ps.businessDayByDate = ps.businessDayByDate || {};
        ps.referenceAnnualSalesByYear = ps.referenceAnnualSalesByYear || {};
        return ps;
      }
""" + PERSIST_PAST_FN


def extract_psm_js(text: str) -> str | None:
    m = re.search(
        r"<script>\s*\n    \(function \(\) \{\s*\n      var modal = document\.getElementById\('past-sales-modal'\);",
        text,
    )
    if not m:
        return None
    end = text.find("})();\n  </script>", m.start())
    if end < 0:
        return None
    return text[m.start() : end + len("})();\n  </script>")]


def transform_aem_js_to_psm(block: str, lang: str) -> str:
    t = TEXT[lang]
    out = block

    out = out.replace(AEM_PERSIST_FN, PSM_ENSURE_AND_PERSIST)

    out = out.replace(
        """      function baseRowDefaults(iso, isWk) {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var bmap = daily && daily.businessDayByDate;
        var map = daily && daily.targetSalesByDate;""",
        """      function baseRowDefaults(iso, isWk) {
        var ps = ensurePastSalesDaily();
        var bmap = ps.businessDayByDate;
        var map = ps.salesByDate;""",
    )

    out = out.replace(
        """      function saveModalEdits() {
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {};
        window.__ANNUAL_DATA.daily.targetSalesByDate = window.__ANNUAL_DATA.daily.targetSalesByDate || {};
        window.__ANNUAL_DATA.daily.businessDayByDate = window.__ANNUAL_DATA.daily.businessDayByDate || {};
        var map = window.__ANNUAL_DATA.daily.targetSalesByDate;
        var bmap = window.__ANNUAL_DATA.daily.businessDayByDate;""",
        """      function savePastSalesModal() {
        var ps = ensurePastSalesDaily();
        ps.salesByDate = ps.salesByDate || {};
        ps.businessDayByDate = ps.businessDayByDate || {};
        var map = ps.salesByDate;
        var bmap = ps.businessDayByDate;""",
    )

    out = out.replace(
        """      function getCalendarYear() {
        var d = window.__ANNUAL_DATA;
        if (d && d.calendarYear != null) return Number(d.calendarYear);
        return new Date().getFullYear();
      }

      function clampYear(yr) {
        var minY = 2000;
        var maxY = new Date().getFullYear() + 5;
        return Math.max(minY, Math.min(maxY, yr));
      }""",
        """      function getOperatingYear() {
        var d = window.__ANNUAL_DATA;
        if (d && d.calendarYear != null && isFinite(Number(d.calendarYear))) {
          return Number(d.calendarYear);
        }
        return new Date().getFullYear();
      }

      function clampPastSalesYear(yr) {
        var cy = getOperatingYear();
        return Math.max(cy - 10, Math.min(cy - 1, yr));
      }""",
    )

    out = out.replace(
        """      function ensureYearOptions() {
        if (!yearSelect) return;
        var minY = 2000;
        var maxY = new Date().getFullYear() + 5;
        var rebuild = yearSelect.options.length === 0;
        if (!rebuild) {
          var lo = Number(yearSelect.options[0].value);
          var hi = Number(yearSelect.options[yearSelect.options.length - 1].value);
          if (lo !== minY || hi !== maxY) rebuild = true;
        }
        if (rebuild) {
          yearSelect.innerHTML = '';
          for (var y = minY; y <= maxY; y++) {
            var opt = document.createElement('option');
            opt.value = String(y);
            opt.textContent = String(y);
            yearSelect.appendChild(opt);
          }
        }
      }""",
        """      function ensureYearOptions() {
        if (!yearSelect) return;
        var cy = getOperatingYear();
        var minY = cy - 10;
        var maxY = cy - 1;
        var rebuild = yearSelect.options.length === 0;
        if (!rebuild) {
          var lo = Number(yearSelect.options[0].value);
          var hi = Number(yearSelect.options[yearSelect.options.length - 1].value);
          if (lo !== minY || hi !== maxY) rebuild = true;
        }
        if (rebuild) {
          yearSelect.innerHTML = '';
          for (var y = minY; y <= maxY; y++) {
            var opt = document.createElement('option');
            opt.value = String(y);
            opt.textContent = isJa ? String(y) + '年' : String(y);
            yearSelect.appendChild(opt);
          }
        }
      }""",
    )

    out = out.replace(
        """      function syncYearMonthFromApp() {
        state.year = clampYear(getCalendarYear());
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var iso = daily && daily.selectedDate;
        state.viewMonth = 0;
        if (iso && typeof iso === 'string') {
          var p = iso.split('-');
          if (p.length >= 2) {
            var m = Number(p[1]);
            if (m >= 1 && m <= 12) state.viewMonth = m - 1;
          }
        }
        syncSelectsFromState();
      }""",
        """      function syncYearMonthFromApp() {
        var cy = getOperatingYear();
        state.year = clampPastSalesYear(cy - 1);
        state.viewMonth = 0;
        syncSelectsFromState();
      }""",
    )

    out = out.replace(
        """      function syncColheadDatePickerBounds() {
        if (!dateInput) return;
        var minY = 2000;
        var maxY = new Date().getFullYear() + 5;
        dateInput.min = minY + '-01-01';
        dateInput.max = maxY + '-12-31';
      }""",
        """      function syncColheadDatePickerBounds() {
        if (!dateInput) return;
        var cy = getOperatingYear();
        dateInput.min = cy - 10 + '-01-01';
        dateInput.max = cy - 1 + '-12-31';
      }""",
    )

    out = out.replace(
        """        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var isoPick = daily && daily.selectedDate;""",
        """        var isoPick = null;""",
    )

    out = out.replace("annual-edit-modal", "past-sales-modal")
    out = out.replace("annual-edit-", "past-sales-")
    out = out.replace("data-aem-", "data-psm-")
    out = out.replace("annual:editModalSaved", "annual:pastSalesSaved")
    out = out.replace("source: 'annual-edit-modal'", "source: 'past-sales-modal'")
    out = out.replace(
        "var btnEdit = document.getElementById('annual-daily-focus-edit-btn');",
        "var openBtn = document.getElementById('annual-past-sales-btn');",
    )
    out = out.replace("if (!modal || !modalTable || !btnEdit) return;", "if (!modal || !modalTable || !openBtn) return;")
    out = out.replace("btnEdit.addEventListener('click'", "openBtn.addEventListener('click'")
    out = out.replace("else btnEdit.focus();", "else if (openBtn) openBtn.focus();")
    out = out.replace("function renderTable()", "function renderPastSalesTable()")
    out = out.replace("renderTable();", "renderPastSalesTable();")
    out = out.replace("function rowApplyOffState(", "function pastSalesRowApplyOffState(")
    out = out.replace("rowApplyOffState(", "pastSalesRowApplyOffState(")
    out = out.replace("saveModalEdits", "savePastSalesModal")
    out = out.replace("persistAnnualDailyShared()", "persistPastSalesShared()")
    out = out.replace("clampYear(", "clampPastSalesYear(")
    out = out.replace("getCalendarYear()", "getOperatingYear()")

    out = out.replace(
        "MSG_UNSAVED_CLOSE = isJa\n        ? '変更が保存されていません。保存せずに閉じますか？'\n        : 'You have unsaved changes. Close without saving?';",
        f"MSG_UNSAVED_CLOSE = isJa ? {repr(t['unsaved_close'])} : 'You have unsaved changes. Close without saving?';",
    )
    csv_ja = "CSV取込は次フェーズで実装予定です。"
    csv_en = "CSV import will be implemented in a coming phase."
    out = out.replace(
        f"window.alert('{csv_ja}');",
        f"window.alert(isJa ? '{csv_ja}' : '{csv_en}');",
    )
    out = out.replace(
        f"window.alert('{csv_en}');",
        f"window.alert(isJa ? '{csv_ja}' : '{csv_en}');",
    )

    tab_js = """
      function setPastSalesTab(tab) {
        var t = tab === 'analyze' ? 'analyze' : 'input';
        var panel = modal.querySelector('.past-sales-modal__panel');
        var body = document.getElementById('past-sales-modal-body');
        if (panel) panel.setAttribute('data-psm-tab', t);
        if (body) body.setAttribute('data-psm-tab', t);
        var tabInput = document.getElementById('past-sales-tab-input');
        var tabAnalyze = document.getElementById('past-sales-tab-analyze');
        if (tabInput) {
          tabInput.classList.toggle('is-active', t === 'input');
          tabInput.setAttribute('aria-selected', t === 'input' ? 'true' : 'false');
        }
        if (tabAnalyze) {
          tabAnalyze.classList.toggle('is-active', t === 'analyze');
          tabAnalyze.setAttribute('aria-selected', t === 'analyze' ? 'true' : 'false');
        }
        var paneAnalyze = document.getElementById('past-sales-pane-analyze');
        if (paneAnalyze) paneAnalyze.hidden = t !== 'analyze';
      }

      function updatePastSalesSummary() {
        var cumEl = document.getElementById('past-sales-summary-cumulative');
        if (cumEl) cumEl.textContent = '—';
      }

      function renderPastSalesAnalyze() {
        /* PS-1 placeholder */
      }
"""

    if "function setPastSalesTab" not in out:
        out = out.replace("function pad2(n)", tab_js + "\n      function pad2(n)", 1)

    open_patch = """        setPastSalesTab('input');
        updatePastSalesSummary();
        renderPastSalesTable();
        modal.removeAttribute('hidden');"""
    out = out.replace(
        """        renderPastSalesTable();
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');""",
        open_patch,
    )
    out = out.replace(
        """        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');""",
        """        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');""",
    )
    out = out.replace("if (!modal || modal.hidden)", "if (!modal || modal.hasAttribute('hidden'))")
    out = out.replace("modal.hidden = false", "modal.removeAttribute('hidden')")
    out = out.replace("modal.hidden = true", "modal.setAttribute('hidden', '')")

    tab_bind = """
      var tabInputBtn = document.getElementById('past-sales-tab-input');
      var tabAnalyzeBtn = document.getElementById('past-sales-tab-analyze');
      if (tabInputBtn) tabInputBtn.addEventListener('click', function () { setPastSalesTab('input'); });
      if (tabAnalyzeBtn) tabAnalyzeBtn.addEventListener('click', function () { setPastSalesTab('analyze'); });
"""
    out = out.replace("openBtn.addEventListener('click'", tab_bind + "\n      openBtn.addEventListener('click'", 1)

    return out


def inject_hydrate(text: str) -> tuple[str, bool]:
    if "hydratePastSalesShared" in text:
        return text, False
    anchor = """      (function hydrateAnnualDailyShared() {
        var parsed = window.__KPI_DATA_GATEWAY.getJson('kpiNavigator.annualDailyShared');
        if (!parsed) return;
        var daily = window.__ANNUAL_DATA.daily || {};
        if (parsed.targetSalesByDate && typeof parsed.targetSalesByDate === 'object') {
          daily.targetSalesByDate = Object.assign({}, daily.targetSalesByDate || {}, parsed.targetSalesByDate);
        }
        if (parsed.businessDayByDate && typeof parsed.businessDayByDate === 'object') {
          daily.businessDayByDate = Object.assign({}, daily.businessDayByDate || {}, parsed.businessDayByDate);
        }
        window.__ANNUAL_DATA.daily = daily;
      })();"""
    if anchor not in text:
        return text, False
    return text.replace(anchor, anchor + "\n" + HYDRATE_PAST_NEW, 1), True


def repair_psm_js(text: str, lang: str) -> tuple[str, bool]:
    """Replace existing past-sales script with a freshly transformed annual-edit script."""
    old = extract_psm_js(text)
    aem = extract_aem_js(text)
    if not old or not aem:
        return text, False
    new = transform_aem_js_to_psm(aem, lang)
    if old == new:
        return text, False
    return text.replace(old, new, 1), True


def apply_file(path: Path, lang: str) -> dict:
    result = {"path": str(path), "skipped": False, "lines_added": 0, "anchors_failed": [], "repaired_js": False}
    original = path.read_text(encoding="utf-8")
    if MARKER in original:
        text = original
        text, repaired = repair_psm_js(text, lang)
        from patch_annual_ps_layout import patch_file as repair_annual_ps_layout  # noqa: WPS433

        layout = repair_annual_ps_layout(path)
        if layout["changed"]:
            print(f"repaired layout: {path} ({', '.join(layout['changes'])})")
            text = path.read_text(encoding="utf-8")
        if repaired:
            result["repaired_js"] = True
            result["lines_added"] = text.count("\n") - original.count("\n")
            print(f"repaired JS: {path}")
        else:
            print(f"skip (already applied): {path}")
        text, _ = inject_hydrate(text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            if not result["repaired_js"]:
                result["lines_added"] = text.count("\n") - original.count("\n")
        elif result["repaired_js"]:
            path.write_text(text, encoding="utf-8")
        result["skipped"] = True
        return result

    text = original
    before_lines = text.count("\n")

    aem_css = extract_aem_css(text)
    psm_css = PS_LAYOUT_CSS + _psm_detail_css() + COCKPIT_CSS
    css_anchor = re.search(r"    /\* Annual Edit", text)
    if not css_anchor:
        result["anchors_failed"].append("Annual Edit CSS insert anchor")
    else:
        text = text[: css_anchor.start()] + psm_css + "\n" + text[css_anchor.start() :]

    cockpit_anchor = '      <section class="annual-monthly-data" id="annual-monthly-data">'
    if cockpit_anchor not in text:
        result["anchors_failed"].append("cockpit insert anchor (workspace-selector-wrap)")
    else:
        text = text.replace(cockpit_anchor, build_cockpit_html(lang) + cockpit_anchor, 1)

    html_anchor = '  <div\n    class="annual-edit-modal"'
    if html_anchor not in text:
        html_anchor2 = '  <div class="annual-edit-modal"'
        if html_anchor2 not in text:
            result["anchors_failed"].append("annual-edit-modal HTML anchor")
        else:
            text = text.replace(html_anchor2, build_modal_html(lang) + html_anchor2, 1)
    else:
        text = text.replace(html_anchor, build_modal_html(lang) + html_anchor, 1)

    aem_js = extract_aem_js(text)
    if not aem_js:
        result["anchors_failed"].append("annual-edit JS block")
    else:
        psm_js = transform_aem_js_to_psm(aem_js, lang)
        js_anchor = aem_js
        if js_anchor not in text:
            result["anchors_failed"].append("annual-edit JS insert anchor")
        else:
            text = text.replace(js_anchor, psm_js + "\n" + js_anchor, 1)

    text, hydrate_ok = inject_hydrate(text)
    if not hydrate_ok and "hydratePastSalesShared" not in text:
        result["anchors_failed"].append("hydrateAnnualDailyShared anchor")

    if result["anchors_failed"]:
        print(f"FAILED anchors in {path}: {result['anchors_failed']}", file=sys.stderr)
        return result

    path.write_text(text, encoding="utf-8")
    result["lines_added"] = text.count("\n") - before_lines
    print(f"applied: {path} (+{result['lines_added']} lines)")
    return result


def main() -> int:
    results = []
    for path, lang in ((JA_PATH, "ja"), (EN_PATH, "en")):
        results.append(apply_file(path, lang))

    failed = [r for r in results if r.get("anchors_failed")]
    if failed:
        return 1

    for path in (JA_PATH, EN_PATH):
        text = path.read_text(encoding="utf-8")
        psm = len(re.findall(r"past-sales-modal", text))
        btn = len(re.findall(r"annual-past-sales-btn", text))
        print(f"verify {path.name}: past-sales-modal={psm}, annual-past-sales-btn={btn}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""HTML/CSS for Sales Data daily target mode dropdown (Phase 11-2)."""

from __future__ import annotations

TIP_COMBINED_JA = (
    "日次目標の配分方法を選びます。"
    "【月内均等】当月の営業日数で均等割り。すべての日が同額です。"
    "【曜日加重】過去実績の曜日傾向を反映（推奨）。過去データ不足の月は自動で月内均等に切り替わります。"
    "状況に合わせてお選びください。"
)
TIP_COMBINED_EN = (
    "Choose how daily targets are allocated. "
    "[Flat] Divide each month evenly across business days—every day gets the same target. "
    "[Weekday] Apply past weekday patterns (recommended). Months with insufficient data fall back to flat. "
    "Pick the option that fits your situation."
)

CSS = """
    /* SDM-DAILY-TARGET-MODE-CSS */
    .sdm-daily-target-mode {
      position: absolute;
      top: var(--sdm-header-btn-top);
      left: 242px;
      z-index: 8;
      box-sizing: border-box;
    }
    .sdm-daily-target-mode__trigger {
      box-sizing: border-box;
      position: relative;
      display: inline-flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      width: 130px;
      height: var(--sdm-header-btn-h);
      padding: 0 8px;
      margin: 0;
      border: 1px solid var(--sdm-line);
      border-radius: 2px;
      background: var(--sdm-bg-inactive);
      color: var(--sdm-cyan);
      font-size: var(--sdm-fs-body);
      font-weight: 600;
      line-height: 1.15;
      letter-spacing: 0.02em;
      cursor: pointer;
      font-family: inherit;
      text-align: left;
    }
    .sdm-daily-target-mode__trigger:hover,
    .sdm-daily-target-mode__trigger:focus-visible {
      background: var(--sdm-bg-active-70);
      outline: none;
    }
    .sdm-daily-target-mode__label {
      flex: 1;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .sdm-daily-target-mode__caret {
      flex-shrink: 0;
      font-size: 10px;
      opacity: 0.85;
    }
    .sdm-daily-target-mode__trigger[data-tooltip]:hover::after,
    .sdm-daily-target-mode__trigger[data-tooltip]:focus-visible::after {
      content: attr(data-tooltip);
      position: absolute;
      left: calc(100% + 10px);
      top: 0;
      transform: none;
      padding: 8px 10px;
      border: 1px solid var(--sdm-line);
      border-radius: 3px;
      background: #102932;
      color: var(--sdm-cyan);
      font-size: 12px;
      font-weight: 400;
      line-height: 1.45;
      text-align: left;
      white-space: normal;
      width: max-content;
      max-width: min(300px, 85vw);
      z-index: 220;
      pointer-events: none;
      box-shadow: 0 4px 14px rgba(16, 0, 82, 0.35);
    }
    .sdm-daily-target-mode__trigger[aria-expanded="true"]:hover::after,
    .sdm-daily-target-mode__trigger[aria-expanded="true"]:focus-visible::after {
      content: none;
    }
    .sdm-daily-target-mode__panel {
      position: absolute;
      top: calc(100% + 6px);
      left: 0;
      min-width: 130px;
      padding: 4px;
      margin: 0;
      border: 1px solid var(--sdm-line);
      border-radius: 3px;
      background: #102932;
      box-shadow: 0 8px 24px rgba(16, 0, 82, 0.45);
      box-sizing: border-box;
      overflow: visible;
    }
    .sdm-daily-target-mode__panel[hidden] {
      display: none !important;
    }
    .sdm-daily-target-mode__option {
      display: block;
      width: 100%;
      margin: 0 0 4px;
      padding: 8px 10px;
      border: 1px solid rgba(88, 225, 243, 0.35);
      border-radius: 3px;
      background: rgba(88, 225, 243, 0.06);
      color: var(--sdm-cyan);
      font-family: inherit;
      font-size: var(--sdm-fs-body);
      font-weight: 600;
      line-height: 1.2;
      text-align: left;
      cursor: pointer;
      box-sizing: border-box;
      white-space: nowrap;
    }
    .sdm-daily-target-mode__option:last-child {
      margin-bottom: 0;
    }
    .sdm-daily-target-mode__option:hover,
    .sdm-daily-target-mode__option:focus-visible {
      background: rgba(88, 225, 243, 0.16);
      outline: none;
    }
    .sdm-daily-target-mode__option.is-selected {
      border-color: rgba(88, 225, 243, 0.85);
      background: rgba(88, 225, 243, 0.2);
    }
    body.office-mode .sdm-daily-target-mode__trigger {
      background: #fff;
      color: #0a4a8a;
      border-color: rgba(10, 74, 138, 0.35);
    }
    body.office-mode .sdm-daily-target-mode__trigger:hover,
    body.office-mode .sdm-daily-target-mode__trigger:focus-visible {
      background: #e8f2ff;
    }
    body.office-mode .sdm-daily-target-mode__trigger[data-tooltip]:hover::after,
    body.office-mode .sdm-daily-target-mode__trigger[data-tooltip]:focus-visible::after {
      background: #fff;
      color: #0a4a8a;
      border-color: rgba(10, 74, 138, 0.35);
      box-shadow: 0 4px 14px rgba(10, 74, 138, 0.15);
    }
    body.office-mode .sdm-daily-target-mode__panel {
      background: #fff;
      border-color: rgba(10, 74, 138, 0.35);
      box-shadow: 0 8px 24px rgba(10, 74, 138, 0.15);
    }
    body.office-mode .sdm-daily-target-mode__option {
      color: #0a4a8a;
      border-color: rgba(10, 74, 138, 0.25);
      background: rgba(10, 74, 138, 0.04);
    }
    body.office-mode .sdm-daily-target-mode__option.is-selected {
      background: rgba(10, 74, 138, 0.12);
      border-color: rgba(10, 74, 138, 0.55);
    }
    /* /SDM-DAILY-TARGET-MODE-CSS */
"""

HTML_JA = f"""      <div class="sdm-daily-target-mode" id="sdm-daily-target-mode" data-kpi-guard-ignore>
        <button
          type="button"
          class="sdm-daily-target-mode__trigger"
          id="sdm-daily-target-mode-trigger"
          aria-haspopup="listbox"
          aria-expanded="false"
          aria-controls="sdm-daily-target-mode-panel"
          aria-label="日次目標の配分方法"
          data-tooltip="{TIP_COMBINED_JA}"
          data-kpi-guard-ignore
        >
          <span class="sdm-daily-target-mode__label">曜日加重</span>
          <span class="sdm-daily-target-mode__caret" aria-hidden="true">▼</span>
        </button>
        <div
          class="sdm-daily-target-mode__panel"
          id="sdm-daily-target-mode-panel"
          role="listbox"
          aria-label="日次目標の配分方法"
          hidden
        >
          <button
            type="button"
            class="sdm-daily-target-mode__option"
            role="option"
            data-dtm-mode="monthly-flat"
            data-kpi-guard-ignore
          >月内均等</button>
          <button
            type="button"
            class="sdm-daily-target-mode__option is-selected"
            role="option"
            data-dtm-mode="weekday-weighted"
            data-kpi-guard-ignore
          >曜日加重</button>
        </div>
      </div>"""

HTML_EN = f"""      <div class="sdm-daily-target-mode" id="sdm-daily-target-mode" data-kpi-guard-ignore>
        <button
          type="button"
          class="sdm-daily-target-mode__trigger"
          id="sdm-daily-target-mode-trigger"
          aria-haspopup="listbox"
          aria-expanded="false"
          aria-controls="sdm-daily-target-mode-panel"
          aria-label="Daily target allocation method"
          data-tooltip="{TIP_COMBINED_EN}"
          data-kpi-guard-ignore
        >
          <span class="sdm-daily-target-mode__label">Weekday</span>
          <span class="sdm-daily-target-mode__caret" aria-hidden="true">▼</span>
        </button>
        <div
          class="sdm-daily-target-mode__panel"
          id="sdm-daily-target-mode-panel"
          role="listbox"
          aria-label="Daily target allocation method"
          hidden
        >
          <button
            type="button"
            class="sdm-daily-target-mode__option"
            role="option"
            data-dtm-mode="monthly-flat"
            data-kpi-guard-ignore
          >Flat</button>
          <button
            type="button"
            class="sdm-daily-target-mode__option is-selected"
            role="option"
            data-dtm-mode="weekday-weighted"
            data-kpi-guard-ignore
          >Weekday</button>
        </div>
      </div>"""

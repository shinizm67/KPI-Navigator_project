#!/usr/bin/env python3
"""HTML/CSS for Sales Data weekday baseline years UI (Phase 11-3)."""

from __future__ import annotations

CSS = """
    /* SDM-WEEKDAY-BASELINE-CSS */
    .sdm-weekday-baseline[hidden] {
      display: none !important;
    }
    .sdm-weekday-baseline {
      margin-top: var(--sdm-analyze-table-chart-gap, 48px);
      margin-bottom: var(--sdm-season-gap-to-outer, 24px);
      padding: 14px 16px 16px;
      border: 2px solid rgba(88, 225, 243, 0.55);
      background: rgba(0, 0, 0, 0.22);
      box-sizing: border-box;
      width: 100%;
    }
    .sdm-weekday-baseline__head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 8px;
    }
    .sdm-weekday-baseline__title {
      margin: 0;
      font-size: var(--sdm-season-title-fs, 15px);
      font-weight: 700;
      letter-spacing: 0.04em;
      line-height: 1.25;
      color: var(--sdm-cyan);
    }
    .sdm-weekday-baseline__reset {
      margin: 0;
      padding: 0;
      border: 0;
      background: none;
      color: var(--sdm-cyan);
      font: inherit;
      font-size: 12px;
      font-weight: 600;
      text-decoration: underline;
      cursor: pointer;
      white-space: nowrap;
    }
    .sdm-weekday-baseline__reset:hover,
    .sdm-weekday-baseline__reset:focus-visible {
      opacity: 0.85;
      outline: 2px solid rgba(88, 225, 243, 0.55);
      outline-offset: 2px;
    }
    .sdm-weekday-baseline__note {
      margin: 0 0 10px;
      font-size: 12px;
      line-height: 1.45;
      color: rgba(88, 225, 243, 0.82);
    }
    .sdm-weekday-baseline__list {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .sdm-weekday-baseline__row {
      display: grid;
      grid-template-columns: 20px minmax(56px, 72px) minmax(0, 1fr);
      align-items: center;
      gap: 8px;
      min-height: 28px;
      padding: 4px 6px;
      border: 1px solid rgba(88, 225, 243, 0.22);
      border-radius: 2px;
      background: rgba(88, 225, 243, 0.04);
      box-sizing: border-box;
    }
    .sdm-weekday-baseline__row.is-disabled {
      opacity: 0.55;
    }
    .sdm-weekday-baseline__cb {
      width: 16px;
      height: 16px;
      margin: 0;
      cursor: pointer;
      accent-color: #0f9403;
    }
    .sdm-weekday-baseline__row.is-disabled .sdm-weekday-baseline__cb {
      cursor: not-allowed;
    }
    .sdm-weekday-baseline__year {
      font-size: var(--sdm-fs-body, 14px);
      font-weight: 700;
      color: var(--sdm-cyan);
      font-variant-numeric: tabular-nums;
    }
    .sdm-weekday-baseline__hint {
      font-size: 12px;
      line-height: 1.35;
      color: rgba(88, 225, 243, 0.78);
      text-align: left;
    }
    .sdm-weekday-baseline__status {
      margin: 10px 0 0;
      font-size: 12px;
      line-height: 1.4;
      color: #ffb347;
    }
    .sdm-weekday-baseline__status[hidden] {
      display: none !important;
    }
    body.office-mode .sdm-weekday-baseline {
      border-color: rgba(10, 74, 138, 0.35);
      background: rgba(10, 74, 138, 0.04);
    }
    body.office-mode .sdm-weekday-baseline__title,
    body.office-mode .sdm-weekday-baseline__reset,
    body.office-mode .sdm-weekday-baseline__note,
    body.office-mode .sdm-weekday-baseline__year,
    body.office-mode .sdm-weekday-baseline__hint {
      color: #0a4a8a;
    }
    body.office-mode .sdm-weekday-baseline__row {
      border-color: rgba(10, 74, 138, 0.2);
      background: rgba(10, 74, 138, 0.03);
    }
    body.office-mode .sdm-weekday-baseline__status {
      color: #b45309;
    }
    /* /SDM-WEEKDAY-BASELINE-CSS */
"""

HTML_JA = """            <section
              class="sdm-weekday-baseline"
              id="sdm-weekday-baseline"
              aria-label="曜日配分のベースライン年"
              data-kpi-guard-ignore
            >
              <div class="sdm-weekday-baseline__head">
                <h3 class="sdm-weekday-baseline__title">曜日配分のベースライン年</h3>
                <button
                  type="button"
                  class="sdm-weekday-baseline__reset"
                  id="sdm-weekday-baseline-reset"
                  data-kpi-guard-ignore
                >
                  直近2年に戻す
                </button>
              </div>
              <p class="sdm-weekday-baseline__note">
                異常な売上の年（休業・改装等）はチェックを外してください。1年以上の選択が必要です。
              </p>
              <div
                class="sdm-weekday-baseline__list"
                id="sdm-weekday-baseline-list"
                role="group"
                aria-label="ベースライン年の選択"
              ></div>
              <p class="sdm-weekday-baseline__status" id="sdm-weekday-baseline-status" hidden></p>
            </section>"""

HTML_EN = """            <section
              class="sdm-weekday-baseline"
              id="sdm-weekday-baseline"
              aria-label="Weekday baseline years"
              data-kpi-guard-ignore
            >
              <div class="sdm-weekday-baseline__head">
                <h3 class="sdm-weekday-baseline__title">Weekday baseline years</h3>
                <button
                  type="button"
                  class="sdm-weekday-baseline__reset"
                  id="sdm-weekday-baseline-reset"
                  data-kpi-guard-ignore
                >
                  Reset to last 2 years
                </button>
              </div>
              <p class="sdm-weekday-baseline__note">
                Uncheck years with abnormal sales (closures, renovations, etc.). Select at least one year.
              </p>
              <div
                class="sdm-weekday-baseline__list"
                id="sdm-weekday-baseline-list"
                role="group"
                aria-label="Baseline year selection"
              ></div>
              <p class="sdm-weekday-baseline__status" id="sdm-weekday-baseline-status" hidden></p>
            </section>"""

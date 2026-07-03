"""Sales Data / Past Sales — ym row: Total B.Days label | count | Annual|Month split."""

from __future__ import annotations

PAST_SALES_YM_BLOCK_OLD = """        <div class="past-sales-modal__ym">
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--year">
            <label class="past-sales-modal__sr-only" for="past-sales-year-select">年</label>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="前年">
              ◀︎
            </button>
            <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="年"></select>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="翌年">
              ▶︎
            </button>
          </div>
          <div
            class="past-sales-modal__ym-cell past-sales-modal__ym-cell--bd-count"
            aria-live="polite"
            title="表示中の月でチェックされた営業日数"
          >
            <span class="past-sales-modal__ym-bd-label">営業日</span>
            <span class="past-sales-modal__ym-bd-value" id="past-sales-ym-bd-count">—</span>
          </div>
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--month">
            <label class="past-sales-modal__sr-only" for="past-sales-month-select">月</label>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="前月">
              ◀︎
            </button>
            <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="月"></select>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="翌月">
              ▶︎
            </button>
          </div>
        </div>"""

PAST_SALES_YM_BLOCK_JA = """        <div class="past-sales-modal__ym">
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--bd-title">
            <span class="past-sales-modal__ym-bd-title">総営業日数</span>
          </div>
          <div
            class="past-sales-modal__ym-cell past-sales-modal__ym-cell--bd-count"
            aria-live="polite"
            title="表示中の月でチェックされた営業日数"
          >
            <span class="past-sales-modal__ym-bd-value" id="past-sales-ym-bd-count">—</span>
          </div>
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--nav-split">
            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--annual">
              <label class="past-sales-modal__sr-only" for="past-sales-year-select">年</label>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="前年">
                ◀︎
              </button>
              <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="年"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="翌年">
                ▶︎
              </button>
            </div>
            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--month">
              <label class="past-sales-modal__sr-only" for="past-sales-month-select">月</label>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="前月">
                ◀︎
              </button>
              <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="月"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="翌月">
                ▶︎
              </button>
            </div>
          </div>
        </div>"""

PAST_SALES_YM_BLOCK_OLD_EN = """        <div class="past-sales-modal__ym">
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--year">
            <label class="past-sales-modal__sr-only" for="past-sales-year-select">Year</label>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="Previous year">
              ◀︎
            </button>
            <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="Year"></select>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="Next year">
              ▶︎
            </button>
          </div>
          <div
            class="past-sales-modal__ym-cell past-sales-modal__ym-cell--bd-count"
            aria-live="polite"
            title="Checked business days in the displayed month"
          >
            <span class="past-sales-modal__ym-bd-label">B.Day</span>
            <span class="past-sales-modal__ym-bd-value" id="past-sales-ym-bd-count">—</span>
          </div>
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--month">
            <label class="past-sales-modal__sr-only" for="past-sales-month-select">Month</label>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="Previous month">
              ◀︎
            </button>
            <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="Month"></select>
            <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="Next month">
              ▶︎
            </button>
          </div>
        </div>"""

SALES_DATA_YM_BLOCK_OLD_EN = """        <div class="sales-data-modal__ym">
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-fixed" aria-live="polite">
            <span id="sales-data-year-label" class="sales-data-modal__ym-year-label"></span>
          </div>
          <div
            class="sales-data-modal__ym-cell sales-data-modal__ym-cell--bd-count"
            aria-live="polite"
            title="Checked business days in the displayed month"
          >
            <span class="sales-data-modal__ym-bd-label">B.Day</span>
            <span class="sales-data-modal__ym-bd-value" id="sales-data-ym-bd-count">—</span>
          </div>
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--month">
            <label class="sales-data-modal__sr-only" for="sales-data-month-select">Month</label>
            <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="Previous month">
              ◀︎
            </button>
            <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="Month"></select>
            <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="Next month">
              ▶︎
            </button>
          </div>
        </div>"""

PAST_SALES_YM_BLOCK_EN = """        <div class="past-sales-modal__ym">
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--bd-title">
            <span class="past-sales-modal__ym-bd-title">Total B. Days</span>
          </div>
          <div
            class="past-sales-modal__ym-cell past-sales-modal__ym-cell--bd-count"
            aria-live="polite"
            title="Checked business days in the displayed month"
          >
            <span class="past-sales-modal__ym-bd-value" id="past-sales-ym-bd-count">—</span>
          </div>
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--nav-split">
            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--annual">
              <label class="past-sales-modal__sr-only" for="past-sales-year-select">Year</label>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-prev" aria-label="Previous year">
                ◀︎
              </button>
              <select id="past-sales-year-select" class="past-sales-modal__ym-select" aria-label="Year"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-year-next" aria-label="Next year">
                ▶︎
              </button>
            </div>
            <div class="past-sales-modal__ym-nav past-sales-modal__ym-nav--month">
              <label class="past-sales-modal__sr-only" for="past-sales-month-select">Month</label>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-prev" aria-label="Previous month">
                ◀︎
              </button>
              <select id="past-sales-month-select" class="past-sales-modal__ym-select" aria-label="Month"></select>
              <button type="button" class="past-sales-modal__ym-arrow" id="past-sales-month-next" aria-label="Next month">
                ▶︎
              </button>
            </div>
          </div>
        </div>"""

SALES_DATA_YM_BLOCK_OLD = """        <div class="sales-data-modal__ym">
          <div
            class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-fixed"
            aria-live="polite"
          >
            <span id="sales-data-year-label" class="sales-data-modal__ym-year-label"></span>
          </div>
          <div
            class="sales-data-modal__ym-cell sales-data-modal__ym-cell--bd-count"
            aria-live="polite"
            title="表示中の月でチェックされた営業日数"
          >
            <span class="sales-data-modal__ym-bd-label">営業日</span>
            <span class="sales-data-modal__ym-bd-value" id="sales-data-ym-bd-count">—</span>
          </div>
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--month">
            <label class="sales-data-modal__sr-only" for="sales-data-month-select">月</label>
            <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="前月">
              ◀︎
            </button>
            <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="月"></select>
            <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="翌月">
              ▶︎
            </button>
          </div>
        </div>"""

SALES_DATA_YM_BLOCK_JA = """        <div class="sales-data-modal__ym">
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--bd-title">
            <span class="sales-data-modal__ym-bd-title">総営業日数</span>
          </div>
          <div
            class="sales-data-modal__ym-cell sales-data-modal__ym-cell--bd-count"
            aria-live="polite"
            title="表示中の月でチェックされた営業日数"
          >
            <span class="sales-data-modal__ym-bd-value" id="sales-data-ym-bd-count">—</span>
          </div>
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--nav-split">
            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--annual" aria-live="polite">
              <span id="sales-data-year-label" class="sales-data-modal__ym-year-label"></span>
            </div>
            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--month">
              <label class="sales-data-modal__sr-only" for="sales-data-month-select">月</label>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="前月">
                ◀︎
              </button>
              <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="月"></select>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="翌月">
                ▶︎
              </button>
            </div>
          </div>
        </div>"""

SALES_DATA_YM_BLOCK_EN = """        <div class="sales-data-modal__ym">
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--bd-title">
            <span class="sales-data-modal__ym-bd-title">Total B. Days</span>
          </div>
          <div
            class="sales-data-modal__ym-cell sales-data-modal__ym-cell--bd-count"
            aria-live="polite"
            title="Checked business days in the displayed month"
          >
            <span class="sales-data-modal__ym-bd-value" id="sales-data-ym-bd-count">—</span>
          </div>
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--nav-split">
            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--annual" aria-live="polite">
              <span id="sales-data-year-label" class="sales-data-modal__ym-year-label"></span>
            </div>
            <div class="sales-data-modal__ym-nav sales-data-modal__ym-nav--month">
              <label class="sales-data-modal__sr-only" for="sales-data-month-select">Month</label>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-prev" aria-label="Previous month">
                ◀︎
              </button>
              <select id="sales-data-month-select" class="sales-data-modal__ym-select" aria-label="Month"></select>
              <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-month-next" aria-label="Next month">
                ▶︎
              </button>
            </div>
          </div>
        </div>"""

YM_NAV_CSS_PSM = """
    .past-sales-modal__ym-cell--bd-title {
      font-size: var(--psm-fs-colhead);
      font-weight: 600;
      text-align: center;
    }
    .past-sales-modal__ym-bd-title {
      line-height: 1.15;
    }
    .past-sales-modal__ym-cell--nav-split {
      display: grid;
      grid-template-columns: 1fr 1fr;
      padding: 0;
      gap: 0;
    }
    .past-sales-modal__ym-nav {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;
      min-width: 0;
      height: 100%;
      box-sizing: border-box;
      border-right: 1px solid var(--psm-line);
    }
    .past-sales-modal__ym-nav--month {
      border-right: 0;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-nav--month {
      display: none;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-cell--nav-split {
      grid-template-columns: 1fr;
    }"""

YM_NAV_CSS_SDM = """
    .sales-data-modal__ym-cell--bd-title {
      font-size: var(--sdm-fs-colhead);
      font-weight: 600;
      text-align: center;
    }
    .sales-data-modal__ym-bd-title {
      line-height: 1.15;
    }
    .sales-data-modal__ym-cell--nav-split {
      display: grid;
      grid-template-columns: 1fr 1fr;
      padding: 0;
      gap: 0;
    }
    .sales-data-modal__ym-nav {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;
      min-width: 0;
      height: 100%;
      box-sizing: border-box;
      border-right: 1px solid var(--sdm-line);
    }
    .sales-data-modal__ym-nav--month {
      border-right: 0;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-nav--month {
      display: none;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-cell--nav-split {
      grid-template-columns: 1fr;
    }"""

PSM_ANALYZE_YM_OLD = """    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-cell--month {
      display: none;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym {
      grid-template-columns: 1fr;
      flex-shrink: 0;
    }"""

PSM_ANALYZE_YM_NEW = """    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym {
      flex-shrink: 0;
    }"""

SDM_ANALYZE_YM_OLD = """    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-cell--month {
      display: none;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym {
      grid-template-columns: 1fr;
      flex-shrink: 0;
    }"""

SDM_ANALYZE_YM_NEW = """    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym {
      flex-shrink: 0;
    }"""

PSM_BD_COUNT_CSS_TRIM = """    .past-sales-modal__ym-cell--bd-count {
      flex-direction: column;
      gap: 1px;
      padding: 2px 4px;
      line-height: 1.1;
    }
    .past-sales-modal__ym-bd-label {
      font-size: 10px;
      opacity: 0.88;
    }
    .past-sales-modal__ym-bd-value {
      font-size: var(--psm-fs-body);
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-cell--bd-count {
      display: none;
    }"""

PSM_BD_COUNT_CSS_NEW = """    .past-sales-modal__ym-cell--bd-count {
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .past-sales-modal__ym-bd-value {
      font-size: var(--psm-fs-body);
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }"""

SDM_BD_COUNT_CSS_TRIM = """    .sales-data-modal__ym-cell--bd-count {
      flex-direction: column;
      gap: 1px;
      padding: 2px 4px;
      line-height: 1.1;
    }
    .sales-data-modal__ym-bd-label {
      font-size: 10px;
      opacity: 0.88;
    }
    .sales-data-modal__ym-bd-value {
      font-size: var(--sdm-fs-body);
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-cell--bd-count {
      display: none;
    }"""

SDM_BD_COUNT_CSS_NEW = """    .sales-data-modal__ym-cell--bd-count {
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .sales-data-modal__ym-bd-value {
      font-size: var(--sdm-fs-body);
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }"""

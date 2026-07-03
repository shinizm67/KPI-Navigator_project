"""Sales Data / Past Sales — month B.Day count in year/month header row."""

from __future__ import annotations

YM_BD_MARKER = "/* KPI-SDM-YM-BD-COUNT */"
YM_BD_END = "/* END KPI-SDM-YM-BD-COUNT */"

PAST_SALES_YM_OLD = """        <div class="past-sales-modal__ym">
          <div class="past-sales-modal__ym-cell">
            <label class="past-sales-modal__sr-only" for="past-sales-year-select">年</label>"""

PAST_SALES_YM_OLD_EN = """        <div class="past-sales-modal__ym">
          <div class="past-sales-modal__ym-cell">
            <label class="past-sales-modal__sr-only" for="past-sales-year-select">Year</label>"""

PAST_SALES_YM_YEAR_CLASS = """        <div class="past-sales-modal__ym">
          <div class="past-sales-modal__ym-cell past-sales-modal__ym-cell--year">"""

PAST_SALES_YM_BD_JA = """          </div>
          <div
            class="past-sales-modal__ym-cell past-sales-modal__ym-cell--bd-count"
            aria-live="polite"
            title="選択中の年の営業日数（通年）"
          >
            <span class="past-sales-modal__ym-bd-label">営業日</span>
            <span class="past-sales-modal__ym-bd-value" id="past-sales-ym-bd-count">—</span>
          </div>"""

PAST_SALES_YM_BD_EN = """          </div>
          <div
            class="past-sales-modal__ym-cell past-sales-modal__ym-cell--bd-count"
            aria-live="polite"
            title="Checked business days in the displayed month"
          >
            <span class="past-sales-modal__ym-bd-label">B.Day</span>
            <span class="past-sales-modal__ym-bd-value" id="past-sales-ym-bd-count">—</span>
          </div>"""

SALES_DATA_YM_OLD = """        <div class="sales-data-modal__ym">
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-fixed" aria-live="polite">"""

SALES_DATA_YM_JA = """        <div class="sales-data-modal__ym">
          <div
            class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-fixed"
            aria-live="polite"
          >"""

SALES_DATA_YM_BD_JA = """          </div>
          <div
            class="sales-data-modal__ym-cell sales-data-modal__ym-cell--bd-count"
            aria-live="polite"
            title="今年の営業日数（通年）"
          >
            <span class="sales-data-modal__ym-bd-label">営業日</span>
            <span class="sales-data-modal__ym-bd-value" id="sales-data-ym-bd-count">—</span>
          </div>"""

SALES_DATA_YM_BD_EN = """          </div>
          <div
            class="sales-data-modal__ym-cell sales-data-modal__ym-cell--bd-count"
            aria-live="polite"
            title="Total business days this year"
          >
            <span class="sales-data-modal__ym-bd-label">B.Day</span>
            <span class="sales-data-modal__ym-bd-value" id="sales-data-ym-bd-count">—</span>
          </div>"""

YM_GRID_CSS_PSM = """    .past-sales-modal__ym {
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 649fr);
      margin: 0;
      flex-shrink: 0;
      border: 1px solid var(--psm-line);
      border-top: 0;
      border-bottom: 0;
      box-sizing: border-box;
    }
    .past-sales-modal__ym-cell--bd-count {
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

YM_GRID_CSS_PSM_OLD = """    .past-sales-modal__ym {
      display: grid;
      grid-template-columns: 5fr 5fr;
      margin: 0;
      flex-shrink: 0;
      border: 1px solid var(--psm-line);
      border-top: 0;
      border-bottom: 0;
      box-sizing: border-box;
    }"""

YM_GRID_CSS_SDM = """    .sales-data-modal__ym {
      display: grid;
      grid-template-columns: minmax(0, 190fr) minmax(0, 90fr) minmax(0, 649fr);
      margin: 0;
      flex-shrink: 0;
      border: 1px solid var(--sdm-line);
      border-top: 0;
      border-bottom: 0;
      box-sizing: border-box;
    }
    .sales-data-modal__ym-cell--bd-count {
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

YM_GRID_CSS_SDM_OLD = """    .sales-data-modal__ym {
      display: grid;
      grid-template-columns: 5fr 5fr;
      margin: 0;
      flex-shrink: 0;
      border: 1px solid var(--sdm-line);
      border-top: 0;
      border-bottom: 0;
      box-sizing: border-box;
    }"""

PAST_SALES_JS = """
      function pastSalesYearHasBdData(y) {
        if (pastSalesYearHasCommittedData(y)) return true;
        y = Number(y);
        if (!isFinite(y)) return false;
        var prefix = y + '-';
        var bmap = (ensurePastSalesDaily().businessDayByDate) || {};
        for (var k in bmap) {
          if (Object.prototype.hasOwnProperty.call(bmap, k) && k.indexOf(prefix) === 0) return true;
        }
        return false;
      }

      function updatePastSalesYmBdCount() {
        var el = document.getElementById('past-sales-ym-bd-count');
        if (!el) return;
        var y = state.year;
        if (!Number.isFinite(y)) {
          el.textContent = '—';
          return;
        }
        if (!pastSalesYearHasBdData(y)) {
          el.textContent = '—';
          return;
        }
        var all = gatherYearDays(y);
        var n = 0;
        for (var i = 0; i < all.length; i++) {
          var defs = getRowDefaults(all[i].iso, all[i].isWk);
          if (!defs.off) n++;
        }
        el.textContent = String(n);
      }"""

SALES_DATA_JS = """
      function updateSalesDataYmBdCount() {
        var el = document.getElementById('sales-data-ym-bd-count');
        if (!el) return;
        var y = getOperatingYear();
        if (!Number.isFinite(y)) {
          el.textContent = '—';
          return;
        }
        var all = gatherYearDays(y);
        var n = 0;
        for (var i = 0; i < all.length; i++) {
          var defs = getSalesDataRowDefaultsLive(all[i].iso, all[i].isWk);
          if (!defs.off) n++;
        }
        el.textContent = String(n);
      }"""

REFRESH_PAST_OLD = """        updateFilterToggleActive();
        updateSalesSortToggleActive();
      }

      function scrollToViewMonth() {
        if (!scrollEl) return;
        var target = modalTable.querySelector('tr[data-month-idx="' + state.viewMonth + '"]');
        if (target) target.scrollIntoView({ block: 'start', behavior: 'auto' });
        else scrollEl.scrollTop = 0;
      }

      function openModal() {
        lastFocusEl = document.activeElement;
        state.rowStateByIso = {};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();
        setPastSalesTab('input');
        updatePastSalesSummary();
        renderPastSalesTable();"""

REFRESH_PAST_NEW = REFRESH_PAST_OLD.replace(
    "updateSalesSortToggleActive();\n      }",
    "updateSalesSortToggleActive();\n        updatePastSalesYmBdCount();\n      }",
).replace(
    "            updatePastSalesSummary();\n            refreshPastSalesTableTotals();",
    "            updatePastSalesSummary();\n            refreshPastSalesTableTotals();\n            updatePastSalesYmBdCount();",
)

REFRESH_SDM_OLD = """        updateFilterToggleActive();
        updateSalesSortToggleActive();
      }

      function scrollToViewMonth() {
        if (!scrollEl) return;
        var target = modalTable.querySelector('tr[data-month-idx="' + state.viewMonth + '"]');
        if (target) target.scrollIntoView({ block: 'start', behavior: 'auto' });
        else scrollEl.scrollTop = 0;
      }

      function openModal() {
        lastFocusEl = document.activeElement;
        state.rowStateByIso = {};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();"""

REFRESH_SDM_NEW = REFRESH_SDM_OLD.replace(
    "updateSalesSortToggleActive();\n      }",
    "updateSalesSortToggleActive();\n        updateSalesDataYmBdCount();\n      }",
)

REFRESH_SDM_TOTALS_OLD = """      function refreshSalesDataTableTotals() {
        if (!modalTable) return;
        var totalsMap = buildSalesDataTotalsMap(state.year);"""

REFRESH_SDM_TOTALS_NEW = """      function refreshSalesDataTableTotals() {
        if (!modalTable) return;
        updateSalesDataYmBdCount();
        var totalsMap = buildSalesDataTotalsMap(state.year);"""

PAST_SALES_GET_ROW_OLD = """      function getRowDefaults(iso, isWk) {
        var s = state.rowStateByIso[iso];
        if (s) {
          return {
            off: !!s.off,
            last: s.last != null && s.last !== '' ? String(s.last) : '0'
          };
        }
        return baseRowDefaults(iso, isWk);
      }

      function savePastSalesModal() {"""

PAST_SALES_GET_ROW_NEW = PAST_SALES_GET_ROW_OLD.replace(
    "      function savePastSalesModal() {",
    PAST_SALES_JS + "\n\n      function savePastSalesModal() {",
)

SALES_DATA_GET_ROW_OLD = """      function getRowDefaults(iso, isWk) {
        var s = state.rowStateByIso[iso];
        if (s) {
          return {
            off: !!s.off,
            last: s.last != null && s.last !== '' ? String(s.last) : '0'
          };
        }
        return baseRowDefaults(iso, isWk);
      }

      function saveSalesDataModal() {"""

SALES_DATA_GET_ROW_NEW = SALES_DATA_GET_ROW_OLD.replace(
    "      function saveSalesDataModal() {",
    SALES_DATA_JS + "\n\n      function saveSalesDataModal() {",
)

PAST_SALES_CB_OLD = """            pastSalesRowApplyOffState(tr, cb, tdDate);
            updatePastSalesSummary();
            refreshPastSalesTableTotals();"""

PAST_SALES_CB_NEW = """            pastSalesRowApplyOffState(tr, cb, tdDate);
            updatePastSalesSummary();
            refreshPastSalesTableTotals();
            updatePastSalesYmBdCount();"""

SALES_DATA_CB_OLD = """            salesDataRowApplyOffState(tr, cb, tdDate);
            state.modalDirty = true;
            updateSalesDataSummary();
            refreshSalesDataTableTotals();"""

SALES_DATA_CB_NEW = """            salesDataRowApplyOffState(tr, cb, tdDate);
            state.modalDirty = true;
            updateSalesDataSummary();
            refreshSalesDataTableTotals();
            updateSalesDataYmBdCount();"""

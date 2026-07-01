"""Sales Data Input tab — post-modal fixes (year fixed, green theme, no summary toggle)."""

from __future__ import annotations

FIXUP_MARKER = "sdm-input-fixup-v1"

# Broken merge after apply_sales_data_modal (orphan salesData block + duplicate persist tail)
BROKEN_ENSURE_PERSIST_OLD = """      function ensureSalesDataDaily() {
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {
          targetSalesByDate: {},
          businessDayByDate: {}
        };
        var daily = window.__ANNUAL_DATA.daily;
        daily.targetSalesByDate = daily.targetSalesByDate || {};
        daily.businessDayByDate = daily.businessDayByDate || {};
        return daily;
      }
        };
        var ps = window.__ANNUAL_DATA.salesData;
        ps.targetSalesByDate = ps.targetSalesByDate || {};
        ps.businessDayByDate = ps.businessDayByDate || {};
        ps.referenceAnnualSalesByYear = ps.referenceAnnualSalesByYear || {};
        return ps;
      }
      function persistSalesDataShared() {
        var daily = ensureSalesDataDaily();
        var payload = {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        };
        if (daily.referenceAnnualSales != null && isFinite(Number(daily.referenceAnnualSales))) {
          payload.referenceAnnualSales = Math.round(Number(daily.referenceAnnualSales));
        }
        if (daily.salesDataLastSession && typeof daily.salesDataLastSession === 'object') {
          payload.salesDataLastSession = daily.salesDataLastSession;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', payload);
      };
          if (ps.lastSession && typeof ps.lastSession === 'object') {
            payload.lastSession = ps.lastSession;
          }
          window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.salesDataShared', payload);
          return;
        }
        var payload = {
          targetSalesByDate: ps.targetSalesByDate || {},
          businessDayByDate: ps.businessDayByDate || {},
          referenceAnnualSalesByYear: ps.referenceAnnualSalesByYear || {}
        };
        if (ps.lastSession && typeof ps.lastSession === 'object') {
          payload.lastSession = ps.lastSession;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.salesDataShared', payload);
      }"""

BROKEN_ENSURE_PERSIST_NEW = """      function ensureSalesDataDaily() {
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {
          targetSalesByDate: {},
          businessDayByDate: {}
        };
        var daily = window.__ANNUAL_DATA.daily;
        daily.targetSalesByDate = daily.targetSalesByDate || {};
        daily.businessDayByDate = daily.businessDayByDate || {};
        return daily;
      }
      function persistSalesDataShared() {
        var daily = ensureSalesDataDaily();
        var payload = {
          targetSalesByDate: daily.targetSalesByDate || {},
          businessDayByDate: daily.businessDayByDate || {}
        };
        if (daily.referenceAnnualSales != null && isFinite(Number(daily.referenceAnnualSales))) {
          payload.referenceAnnualSales = Math.round(Number(daily.referenceAnnualSales));
        }
        if (daily.salesDataLastSession && typeof daily.salesDataLastSession === 'object') {
          payload.salesDataLastSession = daily.salesDataLastSession;
        }
        window.__KPI_DATA_GATEWAY.setJson('kpiNavigator.annualDailyShared', payload);
      }"""

SDM_THEME_OLD = """      --sdm-row-off-fill: rgba(88, 225, 243, 0.22);
      --sdm-panel-bg: #100052;
      --sdm-frame: #370aff;"""

SDM_THEME_NEW = """      --sdm-row-off-fill: rgba(15, 148, 3, 0.18);
      --sdm-panel-bg: #000000;
      --sdm-frame: #0f9403;"""

BTN_HIDDEN_OLD = """          id="annual-current-sales-btn"
          aria-label="売上 — 当年の日次売上を入力します"
          title="当年の日次売上を入力します"
          hidden
          disabled
        >"""

BTN_HIDDEN_EN_OLD = """          id="annual-current-sales-btn"
          aria-label="Sales — Enter this year's daily sales"
          title="Enter this year's daily sales"
          hidden
          disabled
        >"""

BTN_ENABLED_JA = """          id="annual-current-sales-btn"
          aria-label="売上 — 当年の日次売上を入力します"
          title="当年の日次売上を入力します"
        >"""

BTN_ENABLED_EN = """          id="annual-current-sales-btn"
          aria-label="Sales — Enter this year's daily sales"
          title="Enter this year's daily sales"
        >"""

TAB_BAR_OLD = """      <div class="sales-data-modal__tab-bar">
        <button
          type="button"
          class="sales-data-modal__summary-toggle sales-data-modal__input-only"
          id="sales-data-summary-toggle"
          aria-expanded="true"
          aria-controls="past-sales-summary-panel"
          aria-label="サマリーを折りたたむ"
          title="サマリーを折りたたむ"
        >
          ▼
        </button>
        <div class="sales-data-modal__tabs" role="tablist" aria-label="売上データビュー">"""

TAB_BAR_JA = """      <div class="sales-data-modal__tab-bar">
        <div class="sales-data-modal__tabs" role="tablist" aria-label="売上データビュー">"""

TAB_BAR_EN_OLD = """      <div class="sales-data-modal__tab-bar">
        <button
          type="button"
          class="sales-data-modal__summary-toggle sales-data-modal__input-only"
          id="sales-data-summary-toggle"
          aria-expanded="true"
          aria-controls="past-sales-summary-panel"
          aria-label="Collapse summary"
          title="Collapse summary"
        >
          ▼
        </button>
        <div class="sales-data-modal__tabs" role="tablist" aria-label="Sales data views">"""

TAB_BAR_EN = """      <div class="sales-data-modal__tab-bar">
        <div class="sales-data-modal__tabs" role="tablist" aria-label="Sales data views">"""

YM_YEAR_OLD = """        <div class="sales-data-modal__ym">
          <div class="sales-data-modal__ym-cell">
            <label class="sales-data-modal__sr-only" for="sales-data-year-select">年</label>
            <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-year-prev" aria-label="前年">
              ◀︎
            </button>
            <select id="sales-data-year-select" class="sales-data-modal__ym-select" aria-label="年"></select>
            <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-year-next" aria-label="翌年">
              ▶︎
            </button>
          </div>"""

YM_YEAR_JA = """        <div class="sales-data-modal__ym">
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-fixed" aria-live="polite">
            <span id="sales-data-year-label" class="sales-data-modal__ym-year-label"></span>
          </div>"""

YM_YEAR_EN_OLD = """        <div class="sales-data-modal__ym">
          <div class="sales-data-modal__ym-cell">
            <label class="sales-data-modal__sr-only" for="sales-data-year-select">Year</label>
            <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-year-prev" aria-label="Previous year">
              ◀︎
            </button>
            <select id="sales-data-year-select" class="sales-data-modal__ym-select" aria-label="Year"></select>
            <button type="button" class="sales-data-modal__ym-arrow" id="sales-data-year-next" aria-label="Next year">
              ▶︎
            </button>
          </div>"""

YM_YEAR_EN = """        <div class="sales-data-modal__ym">
          <div class="sales-data-modal__ym-cell sales-data-modal__ym-cell--year-fixed" aria-live="polite">
            <span id="sales-data-year-label" class="sales-data-modal__ym-year-label"></span>
          </div>"""

MODAL_ARIA_OLD = """    aria-labelledby="past-sales-modal-title"
    hidden
  >
    <div class="sales-data-modal__backdrop" id="sales-data-modal-backdrop" aria-hidden="true"></div>
    <div class="sales-data-modal__panel" id="sales-data-modal-body" role="document" data-sdm-tab="input">
      <h2 id="sales-data-modal-title" class="sales-data-modal__title">売上データ</h2>"""

MODAL_ARIA_JA = """    aria-labelledby="sales-data-modal-title"
    hidden
  >
    <div class="sales-data-modal__backdrop" id="sales-data-modal-backdrop" aria-hidden="true"></div>
    <div class="sales-data-modal__panel" id="sales-data-modal-body" role="document" data-sdm-tab="input">
      <h2 id="sales-data-modal-title" class="sales-data-modal__title">売上データ</h2>"""

MODAL_ARIA_EN_OLD = """    aria-labelledby="past-sales-modal-title"
    hidden
  >
    <div class="sales-data-modal__backdrop" id="sales-data-modal-backdrop" aria-hidden="true"></div>
    <div class="sales-data-modal__panel" id="sales-data-modal-body" role="document" data-sdm-tab="input">
      <h2 id="sales-data-modal-title" class="sales-data-modal__title">Sales Data</h2>"""

MODAL_ARIA_EN = """    aria-labelledby="sales-data-modal-title"
    hidden
  >
    <div class="sales-data-modal__backdrop" id="sales-data-modal-backdrop" aria-hidden="true"></div>
    <div class="sales-data-modal__panel" id="sales-data-modal-body" role="document" data-sdm-tab="input">
      <h2 id="sales-data-modal-title" class="sales-data-modal__title">Sales Data</h2>"""

CLOSE_CHOOSER_ARIA_OLD = """    aria-labelledby="past-sales-close-chooser-title"
    hidden
  >
    <div class="sales-data-modal__close-chooser-scrim" id="sales-data-close-chooser-scrim" aria-hidden="true"></div>
    <div class="sales-data-modal__close-chooser-panel">
      <p id="sales-data-close-chooser-title" class="sales-data-modal__close-chooser-title">売上データを閉じます</p>"""

CLOSE_CHOOSER_ARIA_JA = CLOSE_CHOOSER_ARIA_OLD.replace(
    "past-sales-close-chooser-title", "sales-data-close-chooser-title"
)

YM_CSS_ANCHOR = """    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-cell--month {
      display: none;
    }"""

YM_CSS_NEW = """    .sales-data-modal__ym-cell--year-fixed {
      flex: 1 1 auto;
      justify-content: center;
      min-width: 0;
    }
    .sales-data-modal__ym-year-label {
      font-size: var(--sdm-fs-body);
      color: var(--sdm-cyan);
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__ym-cell--month {
      display: none;
    }"""

YEAR_NAV_OLD = """      var PAST_SALES_MIN_YEAR = 2000;

      function clampSalesDataYear(yr) {
        var cy = getOperatingYear();
        return Math.max(PAST_SALES_MIN_YEAR, Math.min(cy - 1, yr));
      }

      function ensureYearOptions() {
        if (!yearSelect) return;
        var cy = getOperatingYear();
        var minY = PAST_SALES_MIN_YEAR;
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
      }

      function ensureMonthOptions() {
        if (!monthSelect || monthSelect.options.length === 12) return;
        monthSelect.innerHTML = '';
        var labels = isJa ? MONTHS_JA : MONTHS_EN;
        for (var i = 0; i < 12; i++) {
          var opt = document.createElement('option');
          opt.value = String(i);
          opt.textContent = labels[i];
          monthSelect.appendChild(opt);
        }
      }

      function syncSelectsFromState() {
        ensureYearOptions();
        ensureMonthOptions();
        if (yearSelect) {
          var y = clampSalesDataYear(state.year);
          state.year = y;
          yearSelect.value = String(y);
        }
        if (monthSelect) {
          monthSelect.value = String(state.viewMonth);
        }
      }

      function syncYearMonthFromApp() {
        var cy = getOperatingYear();
        state.year = clampSalesDataYear(cy - 1);
        state.viewMonth = 0;
        syncSelectsFromState();
      }

      function syncColheadDatePickerBounds() {
        if (!dateInput) return;
        var cy = getOperatingYear();
        dateInput.min = PAST_SALES_MIN_YEAR + '-01-01';
        dateInput.max = cy - 1 + '-12-31';
      }"""

YEAR_NAV_NEW = """      function syncYearLabel() {
        var el = document.getElementById('sales-data-year-label');
        if (!el) return;
        var y = getOperatingYear();
        el.textContent = isJa ? String(y) + '年' : String(y);
      }

      function ensureMonthOptions() {
        if (!monthSelect || monthSelect.options.length === 12) return;
        monthSelect.innerHTML = '';
        var labels = isJa ? MONTHS_JA : MONTHS_EN;
        for (var i = 0; i < 12; i++) {
          var opt = document.createElement('option');
          opt.value = String(i);
          opt.textContent = labels[i];
          monthSelect.appendChild(opt);
        }
      }

      function syncSelectsFromState() {
        var cy = getOperatingYear();
        state.year = cy;
        syncYearLabel();
        ensureMonthOptions();
        if (monthSelect) {
          monthSelect.value = String(state.viewMonth);
        }
      }

      function syncYearMonthFromApp() {
        var cy = getOperatingYear();
        state.year = cy;
        state.viewMonth = 0;
        syncSelectsFromState();
      }

      function syncColheadDatePickerBounds() {
        if (!dateInput) return;
        var cy = getOperatingYear();
        dateInput.min = cy + '-01-01';
        dateInput.max = cy + '-12-31';
      }"""

STASH_REF_OLD = """      function stashReferenceForYear(y) {
        if (!isFinite(y)) return;
        var ps = ensureSalesDataDaily();
        ps.referenceAnnualSalesByYear = ps.referenceAnnualSalesByYear || {};
        var parsed = getReferenceFromInputEl();
        if (parsed == null) {
          delete ps.referenceAnnualSalesByYear[String(y)];
        } else {
          ps.referenceAnnualSalesByYear[String(y)] = parsed;
        }
      }"""

STASH_REF_NEW = """      function stashReferenceForYear(y) {
        if (!isFinite(y) || y !== getOperatingYear()) return;
        var daily = ensureSalesDataDaily();
        var parsed = getReferenceFromInputEl();
        if (parsed == null) {
          daily.referenceAnnualSales = null;
        } else {
          daily.referenceAnnualSales = parsed;
        }
      }"""

DATE_CHANGE_OLD = """          var p = v.split('-');
          var y = clampSalesDataYear(Number(p[0]));
          var m = Number(p[1]);
          var d = Number(p[2]);
          if (!isFinite(m) || !isFinite(d) || m < 1 || m > 12) return;
          var dim = daysInMonth(y, m - 1);
          if (d < 1 || d > dim) return;
          var iso = y + '-' + pad2(m) + '-' + pad2(d);
          var prevYear = state.year;
          state.year = y;
          state.viewMonth = m - 1;
          if (yearSelect) yearSelect.value = String(state.year);
          if (monthSelect) monthSelect.value = String(state.viewMonth);
          if (prevYear !== state.year) {
            commitReferenceBeforeYearChange();
            state.rowStateByIso = {};
            state.modalDirty = false;
            undoStack = [];
            syncUndoButton();
            state.salesPinnedAmount = null;
            state.salesAmountSort = null;
            renderSalesDataTable();
            updateSalesDataSummary();
          }"""

DATE_CHANGE_NEW = """          var p = v.split('-');
          var y = getOperatingYear();
          var m = Number(p[1]);
          var d = Number(p[2]);
          if (Number(p[0]) !== y) return;
          if (!isFinite(m) || !isFinite(d) || m < 1 || m > 12) return;
          var dim = daysInMonth(y, m - 1);
          if (d < 1 || d > dim) return;
          var iso = y + '-' + pad2(m) + '-' + pad2(d);
          state.year = y;
          state.viewMonth = m - 1;
          if (monthSelect) monthSelect.value = String(state.viewMonth);
          syncYearLabel();"""

YEAR_SELECT_BLOCK_OLD = """      if (yearSelect) {
        yearSelect.addEventListener('change', function () {
          var y = Number(yearSelect.value);
          if (!isFinite(y)) return;
          commitReferenceBeforeYearChange();
          state.rowStateByIso = {};
          state.modalDirty = false;
          undoStack = [];
          syncUndoButton();
          state.salesPinnedAmount = null;
          state.salesAmountSort = null;
          state.year = clampSalesDataYear(y);
          yearSelect.value = String(state.year);
          syncColheadDatePickerValue();
          renderSalesDataTable();
          updateSalesDataSummary();
          scrollToViewMonth();
        });
      }
      if (monthSelect) {"""

YEAR_SELECT_BLOCK_NEW = """      if (monthSelect) {"""

CALENDAR_LISTENER_OLD = """      openBtn.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
      });"""

CALENDAR_LISTENER_NEW = """      openBtn.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
      });
      document.addEventListener('annual:calendarYearChanged', function () {
        if (modal.hasAttribute('hidden')) return;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        renderSalesDataTable();
        updateSalesDataSummary();
      });"""

OPEN_MODAL_OLD = """      function openModal() {
        lastFocusEl = document.activeElement;
        state.rowStateByIso = {};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();
        setSalesDataTab('input');
        updateSalesDataSummary();
        renderSalesDataTable();
        modal.removeAttribute('hidden');"""

OPEN_MODAL_NEW = """      function openModal() {
        lastFocusEl = document.activeElement;
        state.rowStateByIso = {};
        state.salesPinnedAmount = null;
        state.salesAmountSort = null;
        syncYearMonthFromApp();
        syncColheadDatePickerValue();
        clearDateFilterUi();
        closeSalesSortPanel();
        setSalesDataTab('input');
        updateSalesDataSummary();
        renderSalesDataTable();
        modal.removeAttribute('hidden');
        modal.removeAttribute('aria-hidden');
        if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
          window.__KPI_SALES_INPUT_PATH_UI.sync();
        }
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }"""

CLOSE_MODAL_OLD = """      function closeModal() {
        hideSalesDataCloseChooser();
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.setAttribute('hidden', '');"""

CLOSE_MODAL_NEW = """      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        hideSalesDataCloseChooser();
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.setAttribute('hidden', '');"""

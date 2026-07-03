"""Cockpit Business Days: live preview while Sales Data modal is open."""

from __future__ import annotations

RESOLVE_BMAP_OLD = """      function resolveBusinessDayMapForCockpit() {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        return (daily && daily.businessDayByDate) || {};
      }"""

RESOLVE_BMAP_NEW = """      function resolveBusinessDayMapForCockpit() {
        var sdm = document.getElementById('sales-data-modal');
        var sdmTable = document.getElementById('sales-data-modal-table');
        var modalLive = sdm && !sdm.hasAttribute('hidden') && sdmTable;
        if (!modalLive && window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var bmap = Object.assign({}, (daily && daily.businessDayByDate) || {});
        if (modalLive) {
          sdmTable.querySelectorAll('.sales-data-modal__cb[data-iso-date]').forEach(function (cb) {
            var iso = cb.getAttribute('data-iso-date');
            if (iso) bmap[iso] = !!cb.checked;
          });
        }
        return bmap;
      }"""

YEAR_SYNC_RESOLVE_OLD = """        function resolveBusinessDayMapForCockpit() {
          if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
            KpiYearStore.syncToAnnualDaily();
          }
          var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
          return (daily && daily.businessDayByDate) || {};
        }"""

YEAR_SYNC_RESOLVE_NEW = """        function resolveBusinessDayMapForCockpit() {
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.resolveBusinessDayMapForCockpit === 'function'
          ) {
            return window.__ANNUAL_UI.resolveBusinessDayMapForCockpit();
          }
          if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
            KpiYearStore.syncToAnnualDaily();
          }
          var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
          return (daily && daily.businessDayByDate) || {};
        }"""

UI_EXPOSE_OLD = """      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap = syncBusinessDayDisplayFromDailyMap;"""

UI_EXPOSE_NEW = """      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap = syncBusinessDayDisplayFromDailyMap;
      window.__ANNUAL_UI.resolveBusinessDayMapForCockpit = resolveBusinessDayMapForCockpit;"""

SYNC_COCKPIT_CALL = """            if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function') {
              window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
            }"""

CB_CHANGE_BEFORE = """            salesDataRowApplyOffState(tr, cb, tdDate);
            state.modalDirty = true;
            updateSalesDataSummary();
            refreshSalesDataTableTotals();"""

CB_CHANGE_AFTER = """            salesDataRowApplyOffState(tr, cb, tdDate);
            state.modalDirty = true;
            updateSalesDataSummary();
            refreshSalesDataTableTotals();
            if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function') {
              window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
            }"""

CLOSE_MODAL_OLD = """      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        hideSalesDataCloseChooser();
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
        else if (openBtn) openBtn.focus();
      }"""

CLOSE_MODAL_NEW = """      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        hideSalesDataCloseChooser();
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function') {
          window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
        }
        if (lastFocusEl && typeof lastFocusEl.focus === 'function') lastFocusEl.focus();
        else if (openBtn) openBtn.focus();
      }"""

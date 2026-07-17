"""Phase 8 — read surfaces refresh when KpiYearStore timeline changes."""

from __future__ import annotations

READ_SURFACE_MARKER = "/* KPI-READ-SURFACE-SYNC */"

READ_SURFACE_TW_REFRESH = """      function refreshAnnualReadSurfaces(opts) {
        opts = opts || {};
        if (window.KpiYearStore) {
          if (typeof KpiYearStore.reconcileTimelineFromLegacy === 'function') {
            KpiYearStore.reconcileTimelineFromLegacy();
          }
          if (typeof KpiYearStore.syncToAnnualDaily === 'function') {
            KpiYearStore.syncToAnnualDaily();
          }
        }
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        if (typeof renderAnnualDailyTimeline === 'function') {
          renderAnnualDailyTimeline(cy, { preserveScroll: !!opts.preserveScroll });
        }
      }
      document.addEventListener('kpi:readSurfacesRefresh', function () {
        refreshAnnualReadSurfaces({ preserveScroll: true });
      });"""

READ_SURFACE_TW_FINAL_OLD = """      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);
    })();"""

READ_SURFACE_TW_FINAL_NEW = """      refreshAnnualReadSurfaces({ preserveScroll: false });
    })();"""

READ_SURFACE_MONTHLY_BLOCK = """      /* KPI-READ-SURFACE-SYNC */
      document.addEventListener('kpi:readSurfacesRefresh', function () {
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        invalidateMonthlyMepMetricsCache();
        var keepIso =
          currentFocusIso ||
          readDailySelectedIso() ||
          toISODateLocal(new Date(state.year, state.month0, 1));
        rebuildColumns();
        scheduleScroll(keepIso);
      });
      window.addEventListener('storage', function (ev) {
        if (!ev || !ev.key) return;
        if (
          ev.key === 'kpiNavigator.kpiYearStore' ||
          ev.key === 'kpiNavigator.annualDailyShared' ||
          ev.key === 'kpiNavigator.pastSalesShared'
        ) {
          if (window.KpiYearStore && typeof KpiYearStore.reload === 'function') {
            KpiYearStore.reload();
          }
          invalidateMonthlyMepMetricsCache();
          var isoKeep =
            currentFocusIso ||
            readDailySelectedIso() ||
            toISODateLocal(new Date(state.year, state.month0, 1));
          rebuildColumns();
          scheduleScroll(isoKeep);
        }
      });"""

PAST_SALES_OPEN_OLD = """      function openModal() {
        lastFocus = document.activeElement;
        state.rowStateByIso = {};
        state.referenceByYear = {};
        state.lastEditedIso = null;
        state.modalDirty = false;
        sessionSaved = false;
        undoStack = [];
        syncUndoButton();
        hideCloseChooser();
        clearDateFilterUi();
        clearSalesSortState();
        var savedUi = getPastSalesLastSession();"""

PAST_SALES_OPEN_NEW = """      function openModal() {
        lastFocus = document.activeElement;
        if (window.KpiYearStore) {
          if (typeof KpiYearStore.reconcileTimelineFromLegacy === 'function') {
            KpiYearStore.reconcileTimelineFromLegacy();
          }
          if (typeof KpiYearStore.syncToAnnualDaily === 'function') {
            KpiYearStore.syncToAnnualDaily();
          }
        }
        state.rowStateByIso = {};
        state.referenceByYear = {};
        state.lastEditedIso = null;
        state.modalDirty = false;
        sessionSaved = false;
        undoStack = [];
        syncUndoButton();
        hideCloseChooser();
        clearDateFilterUi();
        clearSalesSortState();
        var savedUi = getPastSalesLastSession();"""

PAST_SALES_BASE_OLD = """          return { off: false, last: '1234' };
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) n = 0;
          if (n === 0) return { off: true, last: '0' };
          return { off: false, last: String(Math.round(n)) };
        }
        return { off: !!isWk, last: isWk ? '0' : '1234' };
      }

      function getRowDefaults(iso, isWk) {
        var s = state.rowStateByIso[iso];
        if (s) {
          var off = !!s.off;
          return {
            off: off,
            last:
              s.last != null && s.last !== ''
                ? String(s.last)
                : '0'
          };
        }
        return baseRowDefaults(iso, isWk);
      }

      function flushPastSalesRowStateFromTable()"""

PAST_SALES_BASE_NEW = """          return { off: false, last: '0' };
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) n = 0;
          if (n === 0) return { off: true, last: '0' };
          return { off: false, last: String(Math.round(n)) };
        }
        return { off: !!isWk, last: '0' };
      }

      function getRowDefaults(iso, isWk) {
        var s = state.rowStateByIso[iso];
        if (s) {
          var off = !!s.off;
          return {
            off: off,
            last:
              s.last != null && s.last !== ''
                ? String(s.last)
                : '0'
          };
        }
        return baseRowDefaults(iso, isWk);
      }

      function flushPastSalesRowStateFromTable()"""

STORE_DISPATCH_OLD = """        function dispatchChange(kind, detail) {
          try {
            document.dispatchEvent(new CustomEvent('kpi:' + kind, { detail: detail || {} }));
          } catch (_e) {}
          if (kind === 'dailySalesChanged') {"""

STORE_DISPATCH_NEW = """        function dispatchChange(kind, detail) {
          try {
            document.dispatchEvent(new CustomEvent('kpi:' + kind, { detail: detail || {} }));
          } catch (_e) {}
          if (kind === 'dailySalesChanged' || kind === 'businessDayChanged') {
            try {
              document.dispatchEvent(
                new CustomEvent('kpi:readSurfacesRefresh', {
                  detail: Object.assign({ kind: kind }, detail || {}),
                })
              );
            } catch (_e2) {}
          }
          if (kind === 'dailySalesChanged') {"""

STORE_INIT_OLD = """          ensureOperatingYearPlanDefaults();
          syncToAnnualDaily();
        }}

        window.KpiYearStore = {{"""

STORE_INIT_NEW = """          ensureOperatingYearPlanDefaults();
          syncToAnnualDaily();
          try {
            document.dispatchEvent(new CustomEvent('kpi:readSurfacesRefresh', { detail: { source: 'init' } }));
          } catch (_eInit) {}
        }}

        window.KpiYearStore = {{"""

MEP_REFRESH_BLOCK = """      function refreshMepSalesFromStore(ev) {
        if (root.hidden) return;
        var src = ev && ev.detail && ev.detail.source;
        /* Confirm 自己発火の再hydrateは二重計上の原因なのでスキップ */
        if (src === 'monthly-edit-float' || src === 'mep') return;
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        if (typeof syncBizDayFromAnnualStoreForMonth === 'function') {
          syncBizDayFromAnnualStoreForMonth();
        }
        if (typeof syncMonthlySalesFromAnnualStoreForMonth === 'function') {
          syncMonthlySalesFromAnnualStoreForMonth();
        }
        if (typeof buildGrid === 'function') buildGrid();
      }
      document.addEventListener('kpi:readSurfacesRefresh', refreshMepSalesFromStore);
      document.addEventListener('kpi:dailySalesChanged', refreshMepSalesFromStore);
      document.addEventListener('kpi:businessDayChanged', refreshMepSalesFromStore);
      document.addEventListener('annual:pastSalesSaved', refreshMepSalesFromStore);
      document.addEventListener('annual:salesDataSaved', refreshMepSalesFromStore);
"""

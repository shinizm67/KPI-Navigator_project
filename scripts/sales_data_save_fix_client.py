"""Sales Data modal Save: live DOM read + quiet store persist + lighter post-save refresh."""

from __future__ import annotations

PERSIST_FROM_ANNUAL_DAILY_OLD = """        function persistFromAnnualDaily(daily, meta) {
          if (!daily) return;
          var m = Object.assign({ source: 'annual-daily-compat' }, meta || {});
          mergeDailyMaps(daily.targetSalesByDate, daily.businessDayByDate, m);
          syncToAnnualDaily();
        }"""

PERSIST_FROM_ANNUAL_DAILY_NEW = """        function persistSalesDataModalSave(daily, meta) {
          if (!daily) return;
          if (getDailySalesInputPath() !== 'annual') return;
          var oy = getOperatingYear();
          var prefix = oy + '-';
          var salesMap = daily.targetSalesByDate || {};
          var bizMap = daily.businessDayByDate || {};
          var yearTouched = false;
          Object.keys(salesMap).forEach(function (iso) {
            if (!validIso(iso) || iso.indexOf(prefix) !== 0) return;
            if (!canEditIso(iso)) return;
            var n = Number(salesMap[iso]);
            if (isLegacyPlaceholderSales(n)) {
              delete store.timeline.dailySales[iso];
            } else {
              store.timeline.dailySales[iso] = Number.isFinite(n) ? n : 0;
            }
            yearTouched = true;
          });
          Object.keys(bizMap).forEach(function (iso) {
            if (!validIso(iso) || iso.indexOf(prefix) !== 0) return;
            if (!canEditIso(iso)) return;
            store.timeline.businessDays[iso] = !!bizMap[iso];
            yearTouched = true;
          });
          if (!yearTouched) return;
          sanitizePlaceholderSalesMap(store.timeline.dailySales);
          persistStore();
          syncLegacyKeys();
          maybeRefreshObservedAfterTimelineChange({ [String(oy)]: true });
        }

        function persistFromAnnualDaily(daily, meta) {
          if (!daily) return;
          var m = Object.assign({ source: 'annual-daily-compat' }, meta || {});
          if (m.source === 'sales-data-save') {
            persistSalesDataModalSave(daily, m);
            return;
          }
          mergeDailyMaps(daily.targetSalesByDate, daily.businessDayByDate, m);
          syncToAnnualDaily();
        }"""

GET_ROW_DEFAULTS_LIVE_OLD = """      function getSalesDataRowDefaultsLive(iso, isWk) {
        if (modalTable && modal && !modal.hasAttribute('hidden')) {
          var inp = modalTable.querySelector(
            '.sales-data-modal__sales-input[data-iso-date="' + iso + '"]'
          );
          if (inp) {
            var tr = inp.closest('tr');
            var cb = tr && tr.querySelector('.sales-data-modal__cb');
            if (cb) {
              if (!cb.checked) return { off: true, last: '0' };
              var raw = String(inp.value || '').replace(/[^\\d.-]/g, '');
              if (raw !== '') {
                var n = Number(raw);
                if (isFinite(n)) return { off: false, last: String(Math.round(n)) };
              }
            }
          }
        }
        return getRowDefaults(iso, isWk);
      }"""

GET_ROW_DEFAULTS_LIVE_NEW = """      function getSalesDataRowDefaultsLive(iso, isWk) {
        if (modalTable && modal && !modal.hasAttribute('hidden')) {
          var tr = modalTable.querySelector('tr[data-iso-date="' + iso + '"]');
          if (tr) {
            var cb = tr.querySelector('.sales-data-modal__cb');
            var inp = tr.querySelector('.sales-data-modal__sales-input');
            if (cb) {
              if (!cb.checked) return { off: true, last: '0' };
              var last = '0';
              if (inp) {
                var la = inp.getAttribute('data-last-active');
                if (la != null && la !== '') {
                  var ln = Number(la);
                  if (isFinite(ln)) last = String(Math.round(ln));
                } else {
                  var raw = String(inp.value || '').replace(/[^\\d.-]/g, '');
                  if (raw !== '') {
                    var n = Number(raw);
                    if (isFinite(n)) last = String(Math.round(n));
                  }
                }
              }
              return { off: false, last: last };
            }
          }
        }
        return getRowDefaults(iso, isWk);
      }"""

SAVE_MODAL_BODY_OLD = """        var all = gatherYearDays(state.year);
        for (var i = 0; i < all.length; i++) {
          var item = all[i];
          var defs = getRowDefaults(item.iso, item.isWk);
          map[item.iso] = defs.off ? 0 : Math.round(Number(defs.last));
          bmap[item.iso] = !defs.off;
        }
        state.rowStateByIso = {};
        state.modalDirty = false;
        undoStack = [];
        syncUndoButton();
        sessionSaved = true;
        document.dispatchEvent(
          new CustomEvent('annual:salesDataSaved', { detail: { year: state.year } })
        );
        document.dispatchEvent(
          new CustomEvent('annual:businessDayMapChanged', {
            detail: { year: state.year, source: 'sales-data-modal' }
          })
        );
        document.dispatchEvent(
          new CustomEvent('annual:salesMapChanged', {
            detail: { year: state.year, source: 'sales-data-modal' }
          })
        );
        persistSalesDataShared();
        renderSalesDataTable();
        updateSalesDataSummary();
      }"""

SAVE_MODAL_BODY_NEW = """        var all = gatherYearDays(state.year);
        for (var i = 0; i < all.length; i++) {
          var item = all[i];
          var defs = getSalesDataRowDefaultsLive(item.iso, item.isWk);
          map[item.iso] = defs.off ? 0 : Math.round(Number(defs.last));
          bmap[item.iso] = !defs.off;
        }
        state.rowStateByIso = {};
        state.modalDirty = false;
        undoStack = [];
        syncUndoButton();
        sessionSaved = true;
        persistSalesDataShared();
        document.dispatchEvent(
          new CustomEvent('annual:salesDataSaved', {
            detail: { year: state.year, source: 'sales-data-modal' }
          })
        );
        refreshSalesDataTableTotals();
        updateSalesDataSummary();
      }"""

CB_CHANGE_TAIL_OLD = """            salesDataRowApplyOffState(tr, cb, tdDate);
            updateSalesDataSummary();
            refreshSalesDataTableTotals();"""

CB_CHANGE_TAIL_NEW = """            salesDataRowApplyOffState(tr, cb, tdDate);
            state.modalDirty = true;
            updateSalesDataSummary();
            refreshSalesDataTableTotals();"""

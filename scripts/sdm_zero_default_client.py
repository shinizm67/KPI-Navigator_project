"""Sales Data modal: unentered / zero sales default to 0 (not demo 1234)."""

SDM_BASE_ROW_DEFAULTS_OLD = """      function baseRowDefaults(iso, isWk) {
        var daily = ensureSalesDataDaily();
        var bmap = daily.businessDayByDate;
        var map = daily.targetSalesByDate;
        if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {
          var isBusiness = !!bmap[iso];
          if (!isBusiness) return { off: true, last: '0' };
          if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
            var bn = Number(map[iso]);
            if (isFinite(bn) && bn > 0) {
              return { off: false, last: String(Math.round(bn)) };
            }
          }
          return { off: false, last: '1234' };
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) n = 0;
          if (n === 0) return { off: true, last: '0' };
          return { off: false, last: String(Math.round(n)) };
        }
        return { off: !!isWk, last: isWk ? '0' : '1234' };
      }"""

SDM_BASE_ROW_DEFAULTS_NEW = """      function baseRowDefaults(iso, isWk) {
        var daily = ensureSalesDataDaily();
        var bmap = daily.businessDayByDate;
        var map = daily.targetSalesByDate;
        if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {
          var isBusiness = !!bmap[iso];
          if (!isBusiness) return { off: true, last: '0' };
          if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
            var bn = Number(map[iso]);
            if (!isFinite(bn)) bn = 0;
            return { off: false, last: String(Math.round(bn)) };
          }
          return { off: false, last: '0' };
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) n = 0;
          if (n === 0) return { off: true, last: '0' };
          return { off: false, last: String(Math.round(n)) };
        }
        return { off: !!isWk, last: '0' };
      }"""

SDM_GET_ROW_DEFAULTS_OLD = """        return { off: !!isWk, last: '0' };
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
                : off
                  ? '0'
                  : '1234'
          };
        }
        return baseRowDefaults(iso, isWk);
      }

      function flushSalesDataRowStateFromTable() {"""

SDM_GET_ROW_DEFAULTS_NEW = """        return { off: !!isWk, last: '0' };
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

      function flushSalesDataRowStateFromTable() {"""

SDM_PERSIST_ROW_STATE_OLD = """        } else {
          lastVal =
            inp &&
            inp.getAttribute('data-last-active') != null &&
            inp.getAttribute('data-last-active') !== ''
              ? String(inp.getAttribute('data-last-active'))
              : '1234';
        }
        var base = baseRowDefaults(iso, isWeekendIso(iso));
        if (offNow === !!base.off && lastVal === String(base.last)) {
          delete state.rowStateByIso[iso];
        } else {
          state.rowStateByIso[iso] = { off: offNow, last: lastVal };
        }
        recomputeModalDirty();
      }

      function isNationalHolidayIso(iso) {"""

SDM_PERSIST_ROW_STATE_NEW = """        } else {
          lastVal =
            inp &&
            inp.getAttribute('data-last-active') != null &&
            inp.getAttribute('data-last-active') !== ''
              ? String(inp.getAttribute('data-last-active'))
              : '0';
        }
        var base = baseRowDefaults(iso, isWeekendIso(iso));
        if (offNow === !!base.off && lastVal === String(base.last)) {
          delete state.rowStateByIso[iso];
        } else {
          state.rowStateByIso[iso] = { off: offNow, last: lastVal };
        }
        recomputeModalDirty();
      }

      function isNationalHolidayIso(iso) {"""

SDM_ROW_APPLY_OFF_OLD = """        } else {
          inp.readOnly = false;
          var last = inp.getAttribute('data-last-active');
          inp.value = fmtSalesInput(last != null && last !== '' ? Number(last) : 1234);
        }
        persistRowState(tr);
        applySalesDataTotalsToTable();
      }

      function onSalesDataTableInput(ev) {"""

SDM_ROW_APPLY_OFF_NEW = """        } else {
          inp.readOnly = false;
          var last = inp.getAttribute('data-last-active');
          inp.value = fmtSalesInput(last != null && last !== '' ? Number(last) : 0);
        }
        persistRowState(tr);
        applySalesDataTotalsToTable();
      }

      function onSalesDataTableInput(ev) {"""

SDM_RENDER_TABLE_OLD = """          } else {
            inp.value = fmtSalesInput(defs.last != null && defs.last !== '' ? Number(defs.last) : 1234);
            inp.readOnly = false;
          }
          tdSales.appendChild(inp);

          var tdMonthly = document.createElement('td');
          tdMonthly.className = 'sales-data-modal__monthly-td';"""

SDM_RENDER_TABLE_NEW = """          } else {
            inp.value = fmtSalesInput(defs.last != null && defs.last !== '' ? Number(defs.last) : 0);
            inp.readOnly = false;
          }
          tdSales.appendChild(inp);

          var tdMonthly = document.createElement('td');
          tdMonthly.className = 'sales-data-modal__monthly-td';"""

SDM_SAVE_MODAL_OLD = """      function saveSalesDataModal() {
        flushSalesDataRowStateFromTable();
        var lastSessionSnap = captureSalesDataUiState();
        var daily = ensureSalesDataDaily();
        var map = daily.targetSalesByDate;
        var bmap = daily.businessDayByDate;
        var all = gatherYearDays(state.year);
        for (var i = 0; i < all.length; i++) {
          var item = all[i];
          var defs = getRowDefaults(item.iso, item.isWk);
          map[item.iso] = defs.off ? 0 : Math.round(Number(defs.last));
          bmap[item.iso] = !defs.off;
        }
        state.rowStateByIso = {};
        state.modalDirty = false;"""

SDM_SAVE_MODAL_NEW = """      function saveSalesDataModal() {
        flushSalesDataRowStateFromTable();
        var lastSessionSnap = captureSalesDataUiState();
        var daily = ensureSalesDataDaily();
        var map = daily.targetSalesByDate;
        var bmap = daily.businessDayByDate;
        var all = gatherYearDays(state.year);
        for (var i = 0; i < all.length; i++) {
          var item = all[i];
          var defs = getRowDefaults(item.iso, item.isWk);
          bmap[item.iso] = !defs.off;
          if (defs.off) {
            map[item.iso] = 0;
            continue;
          }
          var amt = Math.round(Number(defs.last));
          if (!Number.isFinite(amt) || amt === 1234) amt = 0;
          var explicit = Object.prototype.hasOwnProperty.call(state.rowStateByIso, item.iso);
          if (explicit) {
            if (amt > 0) map[item.iso] = amt;
            else delete map[item.iso];
          } else if (amt > 0) {
            map[item.iso] = amt;
          } else {
            delete map[item.iso];
          }
        }
        state.rowStateByIso = {};
        state.modalDirty = false;"""

SDM_BASE_ROW_MAP_READ_OLD = """          if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
            var bn = Number(map[iso]);
            if (!isFinite(bn)) bn = 0;
            return { off: false, last: String(Math.round(bn)) };
          }
          return { off: false, last: '0' };
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) n = 0;
          if (n === 0) return { off: true, last: '0' };
          return { off: false, last: String(Math.round(n)) };
        }"""

SDM_BASE_ROW_MAP_READ_NEW = """          if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
            var bn = Number(map[iso]);
            if (!isFinite(bn) || bn === 1234) bn = 0;
            return { off: false, last: String(Math.round(bn)) };
          }
          return { off: false, last: '0' };
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) n = 0;
          if (n === 1234) return { off: !!isWk, last: '0' };
          if (n === 0) return { off: true, last: '0' };
          return { off: false, last: String(Math.round(n)) };
        }"""

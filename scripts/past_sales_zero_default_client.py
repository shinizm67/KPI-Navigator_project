"""Past Sales modal: unentered sales default to 0 (not demo 1234)."""

PSM_BASE_ROW_DEFAULTS_OLD = """      function baseRowDefaults(iso, isWk) {
        var ps = ensurePastSalesDaily();
        var bmap = ps.businessDayByDate;
        var map = ps.salesByDate;
        if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {
          var isBusiness = !!bmap[iso];
          if (!isBusiness) return { off: true, last: '1234' };
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
          if (n === 0) {
            return { off: true, last: '1234' };
          }
          return { off: false, last: String(Math.round(n)) };
        }
        return { off: !!isWk, last: '1234' };
      }"""

PSM_BASE_ROW_DEFAULTS_NEW = """      function baseRowDefaults(iso, isWk) {
        var ps = ensurePastSalesDaily();
        var bmap = ps.businessDayByDate;
        var map = ps.salesByDate;
        if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {
          var isBusiness = !!bmap[iso];
          if (!isBusiness) return { off: true, last: '0' };
          if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
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
          if (n === 0) {
            return { off: true, last: '0' };
          }
          return { off: false, last: String(Math.round(n)) };
        }
        return { off: true, last: '0' };
      }"""

PSM_ROW_APPLY_OFF_OLD = """        } else {
          inp.readOnly = false;
          var last = inp.getAttribute('data-last-active');
          inp.value = fmtSalesInput(last != null && last !== '' ? Number(last) : 1234);
        }
        persistRowState(tr);
      }

      function persistRowState(tr) {
        var cb = tr.querySelector('.past-sales-modal__cb');"""

PSM_ROW_APPLY_OFF_NEW = """        } else {
          inp.readOnly = false;
          var last = inp.getAttribute('data-last-active');
          var n = last != null && last !== '' ? Number(last) : 0;
          if (!Number.isFinite(n) || n === 1234) n = 0;
          inp.value = fmtSalesInput(n);
        }
        persistRowState(tr);
      }

      function persistRowState(tr) {
        var cb = tr.querySelector('.past-sales-modal__cb');"""

PSM_PERSIST_ROW_STATE_OLD = """        var lastVal =
          inp && inp.getAttribute('data-last-active') != null && inp.getAttribute('data-last-active') !== ''
            ? String(inp.getAttribute('data-last-active'))
            : '1234';
        var offNow = !cb.checked;
        var base = baseRowDefaults(iso, isWeekendIso(iso));
        if (offNow === !!base.off && lastVal === String(base.last)) {
          delete state.rowStateByIso[iso];
        } else {
          state.rowStateByIso[iso] = { off: offNow, last: lastVal };
        }
        recomputeModalDirty();
      }

      function getRowDefaults(iso, isWk) {
        var s = state.rowStateByIso[iso];
        if (s) {
          return {
            off: !!s.off,
            last: s.last != null && s.last !== '' ? String(s.last) : '1234'
          };
        }
        return baseRowDefaults(iso, isWk);
      }

      function savePastSalesModal() {"""

PSM_PERSIST_ROW_STATE_NEW = """        var lastVal =
          inp && inp.getAttribute('data-last-active') != null && inp.getAttribute('data-last-active') !== ''
            ? String(inp.getAttribute('data-last-active'))
            : '0';
        var offNow = !cb.checked;
        var base = baseRowDefaults(iso, isWeekendIso(iso));
        if (offNow === !!base.off && lastVal === String(base.last)) {
          delete state.rowStateByIso[iso];
        } else {
          state.rowStateByIso[iso] = { off: offNow, last: lastVal };
        }
        recomputeModalDirty();
      }

      function getRowDefaults(iso, isWk) {
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

PSM_RENDER_TABLE_OLD = """          } else {
            inp.value = fmtSalesInput(
              defs.last != null && defs.last !== '' ? Number(defs.last) : 1234
            );
            inp.readOnly = false;
          }
          tdSales.appendChild(inp);

          var totalsEntry = totalsMap[item.iso];
          let tdMonthly = document.createElement('td');
          tdMonthly.className = 'past-sales-modal__monthly-td';"""

PSM_RENDER_TABLE_NEW = """          } else {
            var salesN =
              defs.last != null && defs.last !== '' ? Number(defs.last) : 0;
            if (!Number.isFinite(salesN) || salesN === 1234) salesN = 0;
            inp.value = fmtSalesInput(salesN);
            inp.readOnly = false;
          }
          tdSales.appendChild(inp);

          var totalsEntry = totalsMap[item.iso];
          let tdMonthly = document.createElement('td');
          tdMonthly.className = 'past-sales-modal__monthly-td';"""

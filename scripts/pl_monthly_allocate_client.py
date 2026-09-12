"""PL Phase B — monthly expense ÷ business days (preview only, no MEP write)."""

from __future__ import annotations


def pl_monthly_allocate_client_js() -> str:
    """JS snippet inserted via f-string expression (single braces; already resolved)."""
    return """
      function listBizDayIsosInMonth(year, month0, bmap, tmap) {
        var daysInMonth = new Date(year, month0 + 1, 0).getDate();
        var list = [];
        for (var day = 1; day <= daysInMonth; day++) {
          var iso = year + '-' + pad2(month0 + 1) + '-' + pad2(day);
          if (isBizDayIso(iso, bmap, tmap)) list.push(iso);
        }
        return list;
      }

      function loadPlExpenseAmountMap(year) {
        try {
          var raw = localStorage.getItem(PL_STORAGE_PREFIX + year);
          if (!raw) return {};
          var map = JSON.parse(raw);
          return map && typeof map === 'object' ? map : {};
        } catch (_e) {
          return {};
        }
      }

      function loadMonthlyExpenseLineIdsFromCatalog() {
        var ids = [];
        var seen = {};
        try {
          var raw = localStorage.getItem('kpiNavigator.plLineCatalog');
          if (raw) {
            var parsed = JSON.parse(raw);
            var lines = parsed && Array.isArray(parsed.lines) ? parsed.lines : [];
            lines.forEach(function (line) {
              if (!line || !line.lineId) return;
              if (line.active === false) return;
              var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
              if (style === 'daily') return;
              if (seen[line.lineId]) return;
              seen[line.lineId] = true;
              ids.push(String(line.lineId));
            });
          }
        } catch (_e) {}
        if (ids.length) return ids;
        document.querySelectorAll('.pl-data-row--expense-detail.pl-expense-detail-row--input-monthly').forEach(
          function (tr) {
            var id = tr.getAttribute('data-line-id');
            if (!id || seen[id]) return;
            seen[id] = true;
            ids.push(id);
          }
        );
        return ids;
      }

      function loadDailyExpenseLineIdsFromCatalog() {
        var ids = [];
        try {
          var raw = localStorage.getItem('kpiNavigator.plLineCatalog');
          if (!raw) return ids;
          var parsed = JSON.parse(raw);
          var lines = parsed && Array.isArray(parsed.lines) ? parsed.lines : [];
          lines.forEach(function (line) {
            if (!line || !line.lineId) return;
            if (line.active === false) return;
            var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
            if (style === 'daily') ids.push(String(line.lineId));
          });
        } catch (_e) {}
        return ids;
      }

      /** Floor + remainder on last biz day so monthly sum stays exact. */
      function allocateAmountAcrossBizDays(monthlyAmount, bizIsos) {
        var api = window.KpiPlMonthlyAllocate;
        if (!api || typeof api.allocateAmountAcrossBizDays !== 'function') {
          return { byDate: {}, perDayBase: 0, remainder: 0, sum: 0, skipped: 'no_shared_allocate' };
        }
        return api.allocateAmountAcrossBizDays(monthlyAmount, bizIsos);
      }

      /**
       * Phase B preview: monthly PL → per-biz-day. Does NOT write MEP.
       * Shared helper: js/kpi-pl-monthly-allocate.js
       */
      function previewMonthlyExpenseAllocation(opts) {
        opts = opts || {};
        if (opts.year == null) opts = Object.assign({}, opts, { year: plYear });
        var api = window.KpiPlMonthlyAllocate;
        if (!api || typeof api.previewMonthlyExpenseAllocation !== 'function') {
          return {
            year: opts.year,
            months: [],
            monthlyLineIds: [],
            skippedDailyLineIds: [],
            wroteToMep: false
          };
        }
        return api.previewMonthlyExpenseAllocation(opts);
      }

      window.__plAllocateAmountAcrossBizDays = allocateAmountAcrossBizDays;
      window.__plPreviewMonthlyExpenseAllocation = previewMonthlyExpenseAllocation;

      var PL_MEP_STORE_KEY = 'kpiNavigator.kpiYearStore';

      /**
       * Phase C: write monthly PL amounts (÷ biz days) into MEP dailyExpenses.
       * Shared helper: js/kpi-pl-monthly-allocate.js
       */
      function writeMonthlyExpenseAllocationToMep(opts) {
        opts = opts || {};
        if (opts.year == null) opts = Object.assign({}, opts, { year: plYear });
        var api = window.KpiPlMonthlyAllocate;
        if (!api || typeof api.writeMonthlyExpenseAllocationToMep !== 'function') {
          return { ok: false, reason: 'no_shared_allocate', wrote: false, year: opts.year };
        }
        return api.writeMonthlyExpenseAllocationToMep(opts);
      }

      window.__plWriteMonthlyExpenseAllocationToMep = writeMonthlyExpenseAllocationToMep;

      /* Phase D: read-only aggregate of MEP daily entries → PL daily expense rows. */
      function readMepDailyExpenseMap(year) {
        var gw = window.__KPI_DATA_GATEWAY;
        if (!gw || typeof gw.getJson !== 'function') return {};
        var store = gw.getJson(PL_MEP_STORE_KEY);
        if (!store || typeof store !== 'object' || !store.years) return {};
        var rec = store.years[year] || store.years[String(year)];
        return (rec && rec.dailyExpenses) || {};
      }

      function sumMepExpenseMonth(byRow, year, month0) {
        if (!byRow || typeof byRow !== 'object') return { sum: 0, hasData: false };
        var prefix = year + '-' + pad2(month0 + 1) + '-';
        var sum = 0;
        var hasData = false;
        Object.keys(byRow).forEach(function (iso) {
          if (iso.indexOf(prefix) !== 0) return;
          var n = Number(byRow[iso]);
          if (Number.isFinite(n)) {
            sum += n;
            hasData = true;
          }
        });
        return { sum: Math.round(sum), hasData: hasData };
      }

      /**
       * Fill PL daily-style expense rows with MEP monthly aggregate + optional
       * monthly adjustment (Daily Aggregate + Adjustment).
       * Displayed amount = dailySum + adjustment. Daily entries stay in MEP.
       */
      var PL_ADJ_STORAGE_PREFIX = 'kpi-pl-expense-adjustments-v1:';
      var plAdjPending = null;

      function plAdjStorageKey(year) {
        return PL_ADJ_STORAGE_PREFIX + year;
      }

      function loadPlExpenseAdjustments(year) {
        try {
          var raw = localStorage.getItem(plAdjStorageKey(year));
          if (!raw) return {};
          var map = JSON.parse(raw);
          return map && typeof map === 'object' ? map : {};
        } catch (_e) {
          return {};
        }
      }

      function savePlExpenseAdjustments(year, map) {
        try {
          localStorage.setItem(plAdjStorageKey(year), JSON.stringify(map || {}));
          return true;
        } catch (_e) {
          return false;
        }
      }

      function getPlExpenseAdjustment(lineId, month0, year) {
        var y = year != null ? year : plYear;
        var map = loadPlExpenseAdjustments(y);
        var n = Number(map[lineId + ':' + month0]);
        return Number.isFinite(n) ? n : 0;
      }

      function setPlExpenseAdjustment(lineId, month0, value, year) {
        var y = year != null ? year : plYear;
        var map = loadPlExpenseAdjustments(y);
        var key = lineId + ':' + month0;
        var n = Number(value);
        if (!Number.isFinite(n) || n === 0) {
          delete map[key];
        } else {
          map[key] = Math.round(n);
        }
        return savePlExpenseAdjustments(y, map);
      }

      function clearPlExpenseAdjustmentsForLine(lineId) {
        if (!lineId) return;
        try {
          for (var si = 0; si < localStorage.length; si++) {
            var storageKey = localStorage.key(si);
            if (!storageKey || storageKey.indexOf(PL_ADJ_STORAGE_PREFIX) !== 0) continue;
            var map = JSON.parse(localStorage.getItem(storageKey) || '{}');
            if (!map || typeof map !== 'object') continue;
            var prefix = lineId + ':';
            var changed = false;
            Object.keys(map).forEach(function (k) {
              if (k.indexOf(prefix) === 0) {
                delete map[k];
                changed = true;
              }
            });
            if (changed) localStorage.setItem(storageKey, JSON.stringify(map));
          }
        } catch (_e) {}
      }

      function fillDailyExpenseRowsFromMep() {
        var dataBody = document.getElementById('pl-expense-detail-data-body');
        if (!dataBody) return;
        var de = readMepDailyExpenseMap(plYear);
        var seen = {};
        var dailyIds = [];
        dataBody
          .querySelectorAll('.pl-amt-cell--pl-daily-readonly[data-line-id]')
          .forEach(function (cell) {
            var id = cell.getAttribute('data-line-id');
            if (!id || seen[id]) return;
            seen[id] = true;
            dailyIds.push(id);
          });
        dailyIds.forEach(function (lineId) {
          var byRow = de[lineId] || null;
          for (var mi = 0; mi < 12; mi++) {
            var td = dataBody.querySelector(
              '.pl-amt-cell--pl-daily-readonly[data-row="' +
                lineId +
                '"][data-month="' +
                mi +
                '"]'
            );
            if (!td) continue;
            var cell = td.querySelector('.pl-amt-cell__text');
            if (!cell) continue;
            var agg = sumMepExpenseMonth(byRow, plYear, mi);
            var adj = getPlExpenseAdjustment(lineId, mi, plYear);
            var has = agg.hasData || adj !== 0;
            var total = (agg.hasData ? agg.sum : 0) + adj;
            cell.textContent = has ? formatMoney(total) : '\\u2014';
            var dailyLabel = isJa ? '日次合計' : 'Daily total';
            var adjLabel = isJa ? '調整' : 'Adj';
            var hint = isJa
              ? 'MEP（月次編集）で日次入力。ダブルクリック / F2 で調整額'
              : 'Enter daily on Monthly Edit. Double-click / F2 for adjustment';
            td.title =
              hint +
              (has
                ? ' — ' +
                  dailyLabel +
                  ' ' +
                  formatMoney(agg.hasData ? agg.sum : 0) +
                  ' / ' +
                  adjLabel +
                  ' ' +
                  formatMoney(adj)
                : '');
            td.setAttribute('data-pl-adj-editable', '1');
            cell.setAttribute('tabindex', '0');
            cell.setAttribute('role', 'button');
            cell.setAttribute(
              'aria-label',
              isJa ? '調整額を編集' : 'Edit adjustment'
            );
          }
        });
      }

      function closePlAdjModal() {
        var modal = document.getElementById('pl-expense-adj-modal');
        if (!modal || modal.hidden) return;
        modal.hidden = true;
        document.body.classList.remove('pl-expense-adj-modal-open');
        plAdjPending = null;
      }

      function refreshPlAdjModalResult() {
        if (!plAdjPending) return;
        var dailyEl = document.getElementById('pl-expense-adj-daily');
        var adjInput = document.getElementById('pl-expense-adj-input');
        var resultEl = document.getElementById('pl-expense-adj-result');
        if (!dailyEl || !adjInput || !resultEl) return;
        var daily = Number(plAdjPending.dailySum) || 0;
        var raw = String(adjInput.value || '').replace(/[^\\d.-]/g, '');
        var adj = raw === '' || raw === '-' || raw === '.' ? 0 : Number(raw);
        if (!Number.isFinite(adj)) adj = 0;
        resultEl.textContent = formatMoney(daily + adj);
      }

      function openPlAdjModal(lineId, month0) {
        var modal = document.getElementById('pl-expense-adj-modal');
        var dailyEl = document.getElementById('pl-expense-adj-daily');
        var adjInput = document.getElementById('pl-expense-adj-input');
        var resultEl = document.getElementById('pl-expense-adj-result');
        if (!modal || !dailyEl || !adjInput || !resultEl) return;
        var de = readMepDailyExpenseMap(plYear);
        var agg = sumMepExpenseMonth(de[lineId] || null, plYear, month0);
        var adj = getPlExpenseAdjustment(lineId, month0, plYear);
        plAdjPending = {
          lineId: lineId,
          month0: month0,
          dailySum: agg.hasData ? agg.sum : 0,
        };
        dailyEl.textContent = formatMoney(plAdjPending.dailySum);
        adjInput.value = adj === 0 ? '' : String(adj);
        resultEl.textContent = formatMoney(plAdjPending.dailySum + adj);
        modal.hidden = false;
        document.body.classList.add('pl-expense-adj-modal-open');
        adjInput.focus();
        adjInput.select();
      }

      function commitPlAdjModal() {
        if (!plAdjPending) return false;
        var adjInput = document.getElementById('pl-expense-adj-input');
        if (!adjInput) return false;
        var raw = String(adjInput.value || '').replace(/[^\\d.-]/g, '');
        var adj = raw === '' || raw === '-' || raw === '.' ? 0 : Number(raw);
        if (!Number.isFinite(adj)) adj = 0;
        setPlExpenseAdjustment(plAdjPending.lineId, plAdjPending.month0, adj, plYear);
        closePlAdjModal();
        fillDailyExpenseRowsFromMep();
        if (typeof refreshPlRatios === 'function') refreshPlRatios();
        return true;
      }

      function bindPlAdjModal() {
        var modal = document.getElementById('pl-expense-adj-modal');
        if (!modal || modal.getAttribute('data-pl-adj-bound') === '1') return;
        modal.setAttribute('data-pl-adj-bound', '1');
        var adjInput = document.getElementById('pl-expense-adj-input');
        if (adjInput) {
          adjInput.addEventListener('input', refreshPlAdjModalResult);
        }
        modal.addEventListener('click', function (e) {
          var btn =
            e.target && e.target.closest
              ? e.target.closest('[data-pl-adj-action]')
              : null;
          if (!btn) return;
          var action = btn.getAttribute('data-pl-adj-action');
          if (action === 'cancel') {
            e.preventDefault();
            closePlAdjModal();
            return;
          }
          if (action === 'confirm') {
            e.preventDefault();
            commitPlAdjModal();
          }
        });
        modal.addEventListener('keydown', function (e) {
          if (modal.hidden) return;
          if (e.key === 'Escape') {
            e.preventDefault();
            closePlAdjModal();
            return;
          }
          if (e.key === 'Enter') {
            e.preventDefault();
            commitPlAdjModal();
          }
        });
        var dataBody = document.getElementById('pl-expense-detail-data-body');
        if (dataBody && dataBody.getAttribute('data-pl-adj-cell-bound') !== '1') {
          dataBody.setAttribute('data-pl-adj-cell-bound', '1');
          dataBody.addEventListener('dblclick', function (e) {
            var td =
              e.target && e.target.closest
                ? e.target.closest('.pl-amt-cell--pl-daily-readonly[data-pl-adj-editable="1"]')
                : null;
            if (!td) return;
            var lineId = td.getAttribute('data-line-id') || td.getAttribute('data-row');
            var mi = Number(td.getAttribute('data-month'));
            if (!lineId || !Number.isFinite(mi)) return;
            e.preventDefault();
            openPlAdjModal(lineId, mi);
          });
          dataBody.addEventListener('keydown', function (e) {
            if (e.key !== 'F2') return;
            var td =
              e.target && e.target.closest
                ? e.target.closest('.pl-amt-cell--pl-daily-readonly[data-pl-adj-editable="1"]')
                : null;
            if (!td) return;
            var lineId = td.getAttribute('data-line-id') || td.getAttribute('data-row');
            var mi = Number(td.getAttribute('data-month'));
            if (!lineId || !Number.isFinite(mi)) return;
            e.preventDefault();
            openPlAdjModal(lineId, mi);
          });
        }
      }

      window.__plFillDailyExpenseRowsFromMep = fillDailyExpenseRowsFromMep;
      window.__plSetExpenseAdjustment = setPlExpenseAdjustment;
      window.__plGetExpenseAdjustment = getPlExpenseAdjustment;
      window.__plClearExpenseAdjustmentsForLine = clearPlExpenseAdjustmentsForLine;
      window.__plOpenExpenseAdjModal = openPlAdjModal;
      bindPlAdjModal();
"""

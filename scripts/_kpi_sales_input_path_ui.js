      /* KPI-SALES-INPUT-PATH-UI */
      (function () {
        function storeReady() {
          return !!(window.KpiYearStore && KpiYearStore.getDailySalesInputPath);
        }
        function t(ja, en, zh) {
          var lang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
          if (lang.indexOf('zh') === 0) return zh || en;
          if (lang.indexOf('ja') === 0) return ja;
          return en;
        }
        function holdsDailySalesLease() {
          return !!(
            window.KpiYearStore &&
            typeof KpiYearStore.holdsEditLease === 'function' &&
            KpiYearStore.holdsEditLease('daily-sales')
          );
        }
        function editPathForWrap(wrap) {
          if (wrap && wrap.classList && wrap.classList.contains('kpi-daily-input-path--mep')) {
            return 'mep';
          }
          return 'annual';
        }
        function leaseLabelForPath(path) {
          if (path === 'mep') return 'Monthly Edit';
          return t('売上データ', 'Sales Data', '營業額資料');
        }
        function tryAcquireForPath(path) {
          if (!window.__KPI_EDIT_LEASE || typeof window.__KPI_EDIT_LEASE.tryAcquire !== 'function') {
            return true;
          }
          return !!window.__KPI_EDIT_LEASE.tryAcquire(leaseLabelForPath(path));
        }
        function releaseOwnLease() {
          if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
            window.__KPI_EDIT_LEASE.release();
          }
        }
        function applyWrapState(wrap) {
          var holds = holdsDailySalesLease();
          wrap.classList.toggle('is-edit', holds);
          wrap.classList.toggle('is-mep', holds);
          var sw = wrap.querySelector('[data-kpi-path-switch], [data-kpi-edit-switch]');
          if (sw) {
            sw.setAttribute('aria-checked', holds ? 'true' : 'false');
          }
          wrap.querySelectorAll('[data-kpi-edit-side], [data-kpi-path-side]').forEach(function (el) {
            var side = el.getAttribute('data-kpi-edit-side') || el.getAttribute('data-kpi-path-side');
            var isEditSide = side === 'edit' || side === 'mep';
            var active = isEditSide ? holds : !holds;
            el.classList.toggle('is-active', active);
            el.classList.toggle('is-inactive', !active);
          });
        }
        function syncToggleUi() {
          document.querySelectorAll('[data-kpi-sales-input-path]').forEach(function (wrap) {
            wrap.hidden = false;
            applyWrapState(wrap);
          });
        }
        function refreshGuards() {
          syncToggleUi();
          document.dispatchEvent(new CustomEvent('kpi:editGuardsRefresh'));
        }
        function enterEdit(wrap) {
          if (!storeReady()) return Promise.resolve(false);
          if (holdsDailySalesLease()) {
            refreshGuards();
            return Promise.resolve(true);
          }
          var next = editPathForWrap(wrap);
          if (!tryAcquireForPath(next)) {
            refreshGuards();
            return Promise.resolve(false);
          }
          if (typeof KpiYearStore.setDailySalesInputPath === 'function') {
            KpiYearStore.setDailySalesInputPath(next);
          }
          refreshGuards();
          return Promise.resolve(true);
        }
        function enterView() {
          releaseOwnLease();
          refreshGuards();
          return Promise.resolve(true);
        }
        function requestEditMode(wantEdit, wrap) {
          if (wantEdit) return enterEdit(wrap);
          return enterView();
        }
        function bindToggles() {
          document.querySelectorAll('[data-kpi-sales-input-path]').forEach(function (wrap) {
            if (wrap.getAttribute('data-kpi-path-bound') === '1') return;
            wrap.setAttribute('data-kpi-path-bound', '1');
            wrap.addEventListener('click', function (ev) {
              var tgt = ev.target;
              var sideEl =
                tgt && tgt.closest
                  ? tgt.closest('[data-kpi-edit-side], [data-kpi-path-side]')
                  : null;
              var swEl =
                tgt && tgt.closest
                  ? tgt.closest('[data-kpi-path-switch], [data-kpi-edit-switch]')
                  : null;
              if (!sideEl && !swEl) return;
              if (sideEl && !wrap.contains(sideEl)) return;
              if (swEl && !wrap.contains(swEl)) return;
              ev.preventDefault();
              var wantEdit;
              if (sideEl) {
                var side = sideEl.getAttribute('data-kpi-edit-side') || sideEl.getAttribute('data-kpi-path-side');
                wantEdit = side === 'edit' || side === 'mep';
              } else {
                wantEdit = !holdsDailySalesLease();
              }
              requestEditMode(wantEdit, wrap);
            });
          });
        }
        bindToggles();
        syncToggleUi();
        document.addEventListener('kpi:dailySalesInputPathChanged', syncToggleUi);
        document.addEventListener('kpi:editLeaseChanged', syncToggleUi);
        window.__KPI_SALES_INPUT_PATH_UI = {
          sync: syncToggleUi,
          requestPathChange: function (next) {
            var wrap = document.querySelector('[data-kpi-sales-input-path]');
            if (next === 'view') return enterView();
            return requestEditMode(true, wrap);
          },
        };
      })();

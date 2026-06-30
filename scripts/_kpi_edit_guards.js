      /* KPI-EDIT-GUARDS */
      (function () {
        function storeReady() {
          return !!(window.KpiYearStore && KpiYearStore.getDailySalesInputPath);
        }
        function isJa() {
          return String(document.documentElement.getAttribute('lang') || '')
            .toLowerCase()
            .indexOf('ja') === 0;
        }
        function annualSalesPathActive() {
          return !storeReady() || KpiYearStore.getDailySalesInputPath() === 'annual';
        }
        function mepSalesPathActive() {
          return storeReady() && KpiYearStore.getDailySalesInputPath() === 'mep';
        }
        function pastSalesEditable() {
          return storeReady() && KpiYearStore.getPastSalesEditEnabled();
        }
        function setInputsReadOnly(root, readOnly, selector) {
          if (!root) return;
          root.querySelectorAll(selector || 'input, textarea, select, button').forEach(function (el) {
            if (el.matches('[data-kpi-guard-ignore]')) return;
            if (el.matches('.past-sales-modal__close, .sales-data-modal__close, .annual-edit-modal__close')) return;
            if (el.matches('[role="tab"]')) return;
            if (readOnly) {
              if (!el.hasAttribute('data-kpi-guard-was-disabled')) {
                el.setAttribute('data-kpi-guard-was-disabled', el.disabled ? '1' : '0');
              }
              el.disabled = true;
              if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.readOnly = true;
              }
            } else if (el.hasAttribute('data-kpi-guard-was-disabled')) {
              el.disabled = el.getAttribute('data-kpi-guard-was-disabled') === '1';
              el.removeAttribute('data-kpi-guard-was-disabled');
              if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.readOnly = false;
              }
            }
          });
        }
        function applyPastSalesGuards() {
          var modal = document.getElementById('past-sales-modal');
          if (!modal || modal.hidden) return;
          var inputTab = modal.getAttribute('data-psm-tab') === 'input';
          var viewOnly = inputTab && !pastSalesEditable();
          var pane = document.getElementById('past-sales-pane-input');
          if (pane) {
            pane.classList.toggle('past-sales-modal__pane--view-only', viewOnly);
            setInputsReadOnly(
              pane,
              viewOnly,
              '.past-sales-modal__sales-input, .past-sales-modal__cb, .past-sales-modal__summary-reference-input, .past-sales-modal__filter-row input'
            );
          }
          ['past-sales-modal-save', 'past-sales-modal-undo', 'past-sales-modal-csv'].forEach(function (id) {
            var btn = document.getElementById(id);
            if (!btn) return;
            if (viewOnly) {
              if (!btn.hasAttribute('data-kpi-guard-was-disabled')) {
                btn.setAttribute('data-kpi-guard-was-disabled', btn.disabled ? '1' : '0');
              }
              btn.disabled = true;
            } else if (btn.hasAttribute('data-kpi-guard-was-disabled')) {
              btn.disabled = btn.getAttribute('data-kpi-guard-was-disabled') === '1';
              btn.removeAttribute('data-kpi-guard-was-disabled');
            }
          });
        }
        function applySalesDataGuards() {
          var modal = document.getElementById('sales-data-modal');
          if (!modal || modal.hidden) return;
          var pane = document.getElementById('sales-data-pane-input');
          if (!pane) return;
          var blocked = mepSalesPathActive();
          pane.classList.toggle('sales-data-modal__pane--path-blocked', blocked);
          setInputsReadOnly(
            pane,
            blocked,
            '.sales-data-modal__sales-input, .sales-data-modal__cb, .sales-data-modal__summary-reference-input'
          );
          var save = document.getElementById('sales-data-modal-save');
          if (save) {
            if (blocked) {
              if (!save.hasAttribute('data-kpi-guard-was-disabled')) {
                save.setAttribute('data-kpi-guard-was-disabled', save.disabled ? '1' : '0');
              }
              save.disabled = true;
            } else if (save.hasAttribute('data-kpi-guard-was-disabled')) {
              save.disabled = save.getAttribute('data-kpi-guard-was-disabled') === '1';
              save.removeAttribute('data-kpi-guard-was-disabled');
            }
          }
        }
        function applyAnnualEditGuards() {
          var modal = document.getElementById('annual-edit-modal');
          if (!modal || modal.hidden) return;
          var blocked = mepSalesPathActive();
          modal.classList.toggle('annual-edit-modal--path-blocked', blocked);
          setInputsReadOnly(
            modal,
            blocked,
            '.annual-edit-modal__sales-input, .annual-edit-modal__cb'
          );
        }
        function syncPastSalesEditToggleUi() {
          var wrap = document.getElementById('past-sales-edit-mode');
          if (!wrap) return;
          var on = pastSalesEditable();
          wrap.querySelectorAll('[data-ps-edit-mode]').forEach(function (btn) {
            var mode = btn.getAttribute('data-ps-edit-mode');
            var active = (mode === 'edit') === on;
            btn.classList.toggle('is-active', active);
            btn.setAttribute('aria-pressed', active ? 'true' : 'false');
          });
        }
        function applyAllGuards() {
          syncPastSalesEditToggleUi();
          applyPastSalesGuards();
          applySalesDataGuards();
          applyAnnualEditGuards();
          document.dispatchEvent(new CustomEvent('kpi:editGuardsApplied'));
        }
        function bindPastSalesEditToggle() {
          var wrap = document.getElementById('past-sales-edit-mode');
          if (!wrap || wrap.getAttribute('data-kpi-bound') === '1') return;
          wrap.setAttribute('data-kpi-bound', '1');
          wrap.addEventListener('click', function (ev) {
            var btn = ev.target.closest('[data-ps-edit-mode]');
            if (!btn || !storeReady()) return;
            var mode = btn.getAttribute('data-ps-edit-mode');
            if (mode === 'edit' && !KpiYearStore.getPastSalesEditEnabled()) {
              var ok = window.confirm(
                isJa()
                  ? '過去売上データの編集モードに切り替えます。確定済みの年は編集できません。'
                  : 'Switch to edit mode for past sales. Locked years remain read-only.'
              );
              if (!ok) return;
            }
            KpiYearStore.setPastSalesEditEnabled(mode === 'edit');
            applyAllGuards();
          });
        }
        bindPastSalesEditToggle();
        document.addEventListener('kpi:dailySalesInputPathChanged', applyAllGuards);
        document.addEventListener('kpi:pastSalesEditChanged', applyAllGuards);
        document.addEventListener('kpi:editLeaseChanged', applyAllGuards);
        document.addEventListener('kpi:editGuardsRefresh', applyAllGuards);
        window.__KPI_EDIT_GUARDS = {
          applyAll: applyAllGuards,
          annualSalesPathActive: annualSalesPathActive,
          mepSalesPathActive: mepSalesPathActive,
          pastSalesEditable: pastSalesEditable,
        };
        applyAllGuards();
      })();

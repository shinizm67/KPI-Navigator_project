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
        function modalIsOpen(modal) {
          return !!(modal && !modal.hasAttribute('hidden'));
        }
        function dailySalesPathBlockTitle() {
          return isJa()
            ? '日次売上・営業日の入力経路は Monthly（MEP）です。トグルで Annual に切り替えてください。'
            : 'Daily sales and business days are entered on Monthly (MEP). Switch the toggle to Annual.';
        }
        function setGuardButtonsDisabled(ids, blocked) {
          ids.forEach(function (id) {
            var btn = document.getElementById(id);
            if (!btn) return;
            if (blocked) {
              if (!btn.hasAttribute('data-kpi-guard-was-disabled')) {
                btn.setAttribute('data-kpi-guard-was-disabled', btn.disabled ? '1' : '0');
              }
              btn.disabled = true;
              btn.title = dailySalesPathBlockTitle();
            } else if (btn.hasAttribute('data-kpi-guard-was-disabled')) {
              btn.disabled = btn.getAttribute('data-kpi-guard-was-disabled') === '1';
              btn.removeAttribute('data-kpi-guard-was-disabled');
              btn.removeAttribute('title');
            }
          });
        }
        var PAST_SALES_YM_NAV_IDS = [
          'past-sales-year-select',
          'past-sales-month-select',
          'past-sales-year-prev',
          'past-sales-year-next',
          'past-sales-month-prev',
          'past-sales-month-next',
        ];
        function restorePastSalesYmNavigation() {
          PAST_SALES_YM_NAV_IDS.forEach(function (id) {
            var el = document.getElementById(id);
            if (!el) return;
            if (el.hasAttribute('data-kpi-guard-was-disabled')) {
              el.disabled = el.getAttribute('data-kpi-guard-was-disabled') === '1';
              el.removeAttribute('data-kpi-guard-was-disabled');
            } else {
              el.disabled = false;
            }
          });
        }
        function setInputsReadOnly(root, readOnly, selector) {
          if (!root) return;
          root.querySelectorAll(selector || 'input, textarea, select, button').forEach(function (el) {
            if (el.matches('[data-kpi-guard-ignore], [data-kpi-ps-nav]')) return;
            if (el.matches('.past-sales-modal__ym-select, .past-sales-modal__ym-arrow')) return;
            if (el.matches('.past-sales-modal__close, .sales-data-modal__close, .annual-edit-modal__close')) return;
            if (el.matches('[role="tab"]')) return;
            if (readOnly) {
              if (!el.hasAttribute('data-kpi-guard-was-disabled')) {
                el.setAttribute('data-kpi-guard-was-disabled', el.disabled ? '1' : '0');
              }
              if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                if (!el.hasAttribute('data-kpi-guard-was-readonly')) {
                  el.setAttribute('data-kpi-guard-was-readonly', el.readOnly ? '1' : '0');
                }
              }
              el.disabled = true;
              if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.readOnly = true;
              }
            } else if (el.hasAttribute('data-kpi-guard-was-disabled')) {
              el.disabled = el.getAttribute('data-kpi-guard-was-disabled') === '1';
              el.removeAttribute('data-kpi-guard-was-disabled');
              if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                if (el.hasAttribute('data-kpi-guard-was-readonly')) {
                  el.readOnly = el.getAttribute('data-kpi-guard-was-readonly') === '1';
                  el.removeAttribute('data-kpi-guard-was-readonly');
                } else {
                  el.readOnly = false;
                }
              }
            }
          });
        }
        function pastSalesOnInputTab(modal) {
          var panel = document.getElementById('past-sales-modal-body');
          if (!panel && modal) {
            panel = modal.querySelector('.past-sales-modal__panel');
          }
          return !panel || panel.getAttribute('data-psm-tab') !== 'analyze';
        }
        function applyPastSalesGuards() {
          var modal = document.getElementById('past-sales-modal');
          if (!modal || !modalIsOpen(modal)) return;
          var inputTab = pastSalesOnInputTab(modal);
          var viewOnly = inputTab && !pastSalesEditable();
          var inputStack = modal.querySelector('.past-sales-modal__input-stack');
          var pane = document.getElementById('past-sales-pane-input');
          var summaryPanel = document.getElementById('past-sales-summary-panel');
          var colhead = modal.querySelector('.past-sales-modal__colhead.past-sales-modal__input-only');
          var viewTitle = isJa()
            ? '閲覧モードです。編集するには「過去データ編集」を編集に切り替えてください。'
            : 'View mode. Switch Past Data Edit to Edit to change values.';
          var bizTitle = isJa()
            ? '営業日の変更は Analyze・Seasonality に影響します。'
            : 'Changing business days affects Analyze and seasonality.';
          if (inputStack) {
            inputStack.classList.toggle('past-sales-modal__input-stack--view-only', viewOnly);
          }
          if (pane) {
            pane.classList.toggle('past-sales-modal__pane--view-only', viewOnly);
            setInputsReadOnly(
              pane,
              viewOnly,
              '.past-sales-modal__sales-input, .past-sales-modal__cb'
            );
            pane.querySelectorAll('.past-sales-modal__sales-input').forEach(function (el) {
              el.title = viewOnly ? viewTitle : '';
            });
            pane.querySelectorAll('.past-sales-modal__cb').forEach(function (cb) {
              cb.title = viewOnly ? viewTitle : pastSalesEditable() ? bizTitle : '';
            });
          }
          if (summaryPanel) {
            setInputsReadOnly(summaryPanel, viewOnly, '.past-sales-modal__summary-reference-input');
            summaryPanel.querySelectorAll('.past-sales-modal__summary-reference-input').forEach(function (el) {
              el.title = viewOnly ? viewTitle : '';
            });
          }
          if (colhead) {
            setInputsReadOnly(
              colhead,
              viewOnly,
              '.past-sales-modal__filter-row input, .past-sales-modal__sales-sort-btn, #past-sales-select-all'
            );
          }
          restorePastSalesYmNavigation();
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
          if (!modal) return;
          var pane = document.getElementById('sales-data-pane-input');
          if (!pane) return;
          var blocked = mepSalesPathActive();
          var open = modalIsOpen(modal);
          pane.classList.toggle('sales-data-modal__pane--path-blocked', blocked);
          modal.classList.toggle('sales-data-modal--path-blocked', blocked && open);
          if (!open) return;
          var blockTitle = dailySalesPathBlockTitle();
          setInputsReadOnly(
            pane,
            blocked,
            '.sales-data-modal__sales-input, .sales-data-modal__cb, .sales-data-modal__summary-reference-input'
          );
          pane.querySelectorAll('.sales-data-modal__sales-input, .sales-data-modal__cb').forEach(function (el) {
            el.title = blocked ? blockTitle : '';
          });
          setGuardButtonsDisabled(
            ['sales-data-modal-save', 'sales-data-modal-undo', 'sales-data-modal-csv'],
            blocked
          );
        }
        function applyAnnualEditGuards() {
          var modal = document.getElementById('annual-edit-modal');
          if (!modal || !modalIsOpen(modal)) return;
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
          wrap.classList.toggle('is-edit', on);
          var sw = wrap.querySelector('[data-ps-edit-switch]');
          if (sw) sw.setAttribute('aria-checked', on ? 'true' : 'false');
          wrap.querySelectorAll('[data-ps-edit-side]').forEach(function (el) {
            var side = el.getAttribute('data-ps-edit-side');
            var active = side === 'edit' ? on : !on;
            el.classList.toggle('is-active', active);
            el.classList.toggle('is-inactive', !active);
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
          var sw = wrap.querySelector('[data-ps-edit-switch]');
          if (!sw) return;
          sw.addEventListener('click', function () {
            if (!storeReady()) return;
            if (KpiYearStore.getPastSalesEditEnabled()) {
              KpiYearStore.setPastSalesEditEnabled(false);
              applyAllGuards();
              return;
            }
            var ok = window.confirm(
              isJa()
                ? '過去売上・営業日を編集します。Analyze・Seasonality など過去指標に影響します。続けますか？'
                : 'You will edit past sales and business days. This affects Analyze, seasonality, and related KPIs. Continue?'
            );
            if (!ok) return;
            KpiYearStore.setPastSalesEditEnabled(true);
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
          applyPastSales: applyPastSalesGuards,
          annualSalesPathActive: annualSalesPathActive,
          mepSalesPathActive: mepSalesPathActive,
          pastSalesEditable: pastSalesEditable,
        };
        applyAllGuards();
      })();

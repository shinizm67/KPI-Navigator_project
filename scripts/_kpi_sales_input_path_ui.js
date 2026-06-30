      /* KPI-SALES-INPUT-PATH-UI */
      (function () {
        function storeReady() {
          return !!(window.KpiYearStore && KpiYearStore.getDailySalesInputPath);
        }
        function isJa() {
          return (
            String(document.documentElement.getAttribute('lang') || '')
              .toLowerCase()
              .indexOf('ja') === 0
          );
        }
        function t(ja, en) {
          return isJa() ? ja : en;
        }
        function isPro() {
          return !storeReady() || KpiYearStore.isProSubscription();
        }
        function pathLabel(path) {
          if (path === 'mep') return t('Monthly（MEP）', 'Monthly (MEP)');
          return t('Annual / Sales Data', 'Annual / Sales Data');
        }
        function applyWrapState(wrap, path) {
          var isMep = path === 'mep';
          wrap.classList.toggle('is-mep', isMep);
          var sw = wrap.querySelector('[data-kpi-path-switch]');
          if (sw) {
            sw.setAttribute('aria-checked', isMep ? 'true' : 'false');
          }
          wrap.querySelectorAll('[data-kpi-path-side]').forEach(function (el) {
            var side = el.getAttribute('data-kpi-path-side');
            var active = side === 'mep' ? isMep : !isMep;
            el.classList.toggle('is-active', active);
            el.classList.toggle('is-inactive', !active);
          });
        }
        function syncToggleUi() {
          var path = storeReady() ? KpiYearStore.getDailySalesInputPath() : 'annual';
          var pro = isPro();
          document.querySelectorAll('[data-kpi-sales-input-path]').forEach(function (wrap) {
            wrap.hidden = !pro;
            applyWrapState(wrap, path);
          });
        }
        var chooser = document.getElementById('kpi-path-change-chooser');
        var chooserScrim = document.getElementById('kpi-path-change-chooser-scrim');
        var chooserSave = document.getElementById('kpi-path-change-save');
        var chooserDiscard = document.getElementById('kpi-path-change-discard');
        var chooserCancel = document.getElementById('kpi-path-change-cancel');
        var chooserReturnFocus = null;
        var chooserResolve = null;
        var pendingPath = null;

        function hideChooser() {
          if (!chooser || chooser.hasAttribute('hidden')) return;
          chooser.setAttribute('hidden', '');
          var el = chooserReturnFocus;
          chooserReturnFocus = null;
          if (el && typeof el.focus === 'function') el.focus();
        }
        function finishChooser(ok, action) {
          var next = pendingPath;
          var resolve = chooserResolve;
          pendingPath = null;
          chooserResolve = null;
          hideChooser();
          if (!resolve) return;
          resolve({ ok: !!ok, action: action || null, next: next });
        }
        function showChooser(next) {
          return new Promise(function (resolve) {
            pendingPath = next;
            chooserResolve = resolve;
            if (!chooser) {
              resolve({ ok: false, action: 'cancel', next: next });
              return;
            }
            chooserReturnFocus = document.activeElement;
            chooser.removeAttribute('hidden');
            if (chooserCancel) chooserCancel.focus();
          });
        }
        if (chooserSave) {
          chooserSave.addEventListener('click', function () {
            finishChooser(true, 'save');
          });
        }
        if (chooserDiscard) {
          chooserDiscard.addEventListener('click', function () {
            finishChooser(true, 'discard');
          });
        }
        if (chooserCancel) {
          chooserCancel.addEventListener('click', function () {
            finishChooser(false, 'cancel');
          });
        }
        if (chooserScrim) {
          chooserScrim.addEventListener('click', function () {
            finishChooser(false, 'cancel');
          });
        }

        function hooks() {
          return window.__KPI_PATH_CHANGE_HOOKS__ || {};
        }
        function hasUnsavedViaHooks() {
          var h = hooks();
          if (typeof h.hasUnsaved === 'function') return !!h.hasUnsaved();
          return false;
        }
        function runHook(name) {
          var h = hooks();
          if (typeof h[name] !== 'function') return Promise.resolve(true);
          try {
            var result = h[name]();
            if (result && typeof result.then === 'function') return result;
            return Promise.resolve(result !== false);
          } catch (_e) {
            return Promise.resolve(false);
          }
        }
        function confirmPathSwitch(next) {
          var msg = t(
            '日次売上・営業日の入力面を「' +
              pathLabel(next) +
              '」に切り替えます。\nもう一方は日次売上・営業日のみ閲覧（Read-Only）になります。\n\n支出・Daily Notes など MEP 固有項目は Monthly 側で引き続き編集できます。',
            'Switch daily sales and business-day input to "' +
              pathLabel(next) +
              '".\nThe other surface becomes read-only for those fields only.\n\nMEP-only fields (expenses, Daily Notes, etc.) remain editable on Monthly.'
          );
          return Promise.resolve(window.confirm(msg));
        }
        function applyPathChange(next) {
          if (!storeReady() || !isPro()) return Promise.resolve(false);
          var cur = KpiYearStore.getDailySalesInputPath();
          if (next === cur) return Promise.resolve(true);
          KpiYearStore.setDailySalesInputPath(next);
          syncToggleUi();
          document.dispatchEvent(new CustomEvent('kpi:editGuardsRefresh'));
          return Promise.resolve(true);
        }
        function requestPathChange(next) {
          if (!storeReady() || !isPro()) return Promise.resolve(false);
          var cur = KpiYearStore.getDailySalesInputPath();
          if (next === cur) return Promise.resolve(true);
          var flow = confirmPathSwitch(next).then(function (confirmed) {
            if (!confirmed) return false;
            if (!hasUnsavedViaHooks()) return applyPathChange(next);
            return showChooser(next).then(function (choice) {
              if (!choice.ok || choice.action === 'cancel') return false;
              if (choice.action === 'save') {
                return runHook('save').then(function (ok) {
                  if (!ok) return false;
                  return applyPathChange(next);
                });
              }
              if (choice.action === 'discard') {
                return runHook('discard').then(function (ok) {
                  if (!ok) return false;
                  return applyPathChange(next);
                });
              }
              return false;
            });
          });
          return flow;
        }
        function bindToggles() {
          document.querySelectorAll('[data-kpi-sales-input-path]').forEach(function (wrap) {
            if (wrap.getAttribute('data-kpi-path-bound') === '1') return;
            wrap.setAttribute('data-kpi-path-bound', '1');
            var sw = wrap.querySelector('[data-kpi-path-switch]');
            if (!sw) return;
            sw.addEventListener('click', function (ev) {
              ev.preventDefault();
              if (!storeReady() || !isPro()) return;
              var cur = KpiYearStore.getDailySalesInputPath();
              requestPathChange(cur === 'mep' ? 'annual' : 'mep');
            });
          });
        }
        bindToggles();
        syncToggleUi();
        document.addEventListener('kpi:dailySalesInputPathChanged', syncToggleUi);
        window.__KPI_SALES_INPUT_PATH_UI = { sync: syncToggleUi, requestPathChange: requestPathChange };
      })();

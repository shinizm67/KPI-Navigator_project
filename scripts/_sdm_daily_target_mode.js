      /* SDM-DAILY-TARGET-MODE */
      (function () {
        var root = document.getElementById('sdm-daily-target-mode');
        if (!root) return;

        var trigger = document.getElementById('sdm-daily-target-mode-trigger');
        var panel = document.getElementById('sdm-daily-target-mode-panel');

        function storeReady() {
          return !!(
            window.KpiYearStore &&
            typeof KpiYearStore.readDailyTargetMode === 'function' &&
            typeof KpiYearStore.writeDailyTargetMode === 'function'
          );
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

        function getYear() {
          if (storeReady() && typeof KpiYearStore.getOperatingYear === 'function') {
            return KpiYearStore.getOperatingYear();
          }
          return new Date().getFullYear();
        }

        function modeLabel(mode) {
          if (mode === 'monthly-flat') {
            return t('月内均等', 'Flat');
          }
          return t('曜日加重', 'Weekday');
        }

        function closePanel() {
          if (!panel || panel.hasAttribute('hidden')) return;
          panel.setAttribute('hidden', '');
          if (trigger) trigger.setAttribute('aria-expanded', 'false');
        }

        function openPanel() {
          if (!panel) return;
          panel.removeAttribute('hidden');
          if (trigger) trigger.setAttribute('aria-expanded', 'true');
        }

        function togglePanel() {
          if (!panel) return;
          if (panel.hasAttribute('hidden')) openPanel();
          else closePanel();
        }

        function sync() {
          if (!storeReady()) return;
          var mode = KpiYearStore.readDailyTargetMode(getYear());
          var labelEl = root.querySelector('.sdm-daily-target-mode__label');
          if (labelEl) labelEl.textContent = modeLabel(mode);
          root.querySelectorAll('[data-dtm-mode]').forEach(function (btn) {
            var m = btn.getAttribute('data-dtm-mode');
            var selected = m === mode;
            btn.classList.toggle('is-selected', selected);
            btn.setAttribute('aria-selected', selected ? 'true' : 'false');
          });
        }

        function selectMode(mode) {
          if (!storeReady()) return;
          var next = mode === 'monthly-flat' ? 'monthly-flat' : 'weekday-weighted';
          KpiYearStore.writeDailyTargetMode(getYear(), next, { source: 'sales-data-header' });
          sync();
          closePanel();
          if (trigger && typeof trigger.focus === 'function') trigger.focus();
        }

        if (trigger) {
          trigger.addEventListener('click', function (e) {
            e.stopPropagation();
            togglePanel();
          });
        }

        root.querySelectorAll('[data-dtm-mode]').forEach(function (btn) {
          btn.addEventListener('click', function (e) {
            e.stopPropagation();
            selectMode(btn.getAttribute('data-dtm-mode'));
          });
        });

        document.addEventListener('click', function (e) {
          if (!root.contains(e.target)) closePanel();
        });

        document.addEventListener('keydown', function (e) {
          if (e.key === 'Escape') closePanel();
        });

        document.addEventListener('kpi:dailyTargetModeChanged', function () {
          sync();
        });

        window.__SDM_DAILY_TARGET_MODE = { sync: sync, closePanel: closePanel };
        sync();
      })();

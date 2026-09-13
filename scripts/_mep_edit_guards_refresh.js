      /* KPI-EDIT-GUARDS */
      (function () {
        function mepDailySalesPathBlocked() {
          if (!window.KpiYearStore || !KpiYearStore.getDailySalesInputPath) return false;
          if (KpiYearStore.getDailySalesInputPath() !== 'mep') return true;
          if (typeof KpiYearStore.holdsEditLease === 'function') {
            return !KpiYearStore.holdsEditLease('daily-sales');
          }
          return false;
        }
        function applyMepDailySalesPathGuards() {
          var mepRoot = document.getElementById('monthly-edit-float');
          if (mepRoot) {
            mepRoot.classList.toggle('monthly-edit-float--daily-sales-path-blocked', mepDailySalesPathBlocked());
          }
        }
        function refreshMepSalesGuards() {
          var mepRoot = document.getElementById('monthly-edit-float');
          if (mepRoot && mepRoot.hidden) return;
          applyMepDailySalesPathGuards();
          if (typeof buildGrid === 'function') buildGrid();
          if (typeof syncMepScreenEditToolbar === 'function') syncMepScreenEditToolbar();
          var memoRoot = document.getElementById('memo-float-modal');
          if (
            typeof renderMemoFloatDayPanel === 'function' &&
            memoRoot &&
            !memoRoot.hasAttribute('hidden')
          ) {
            renderMemoFloatDayPanel();
          }
        }
        document.addEventListener('kpi:dailySalesInputPathChanged', function () {
          refreshMepSalesGuards();
        });
        document.addEventListener('kpi:editGuardsApplied', refreshMepSalesGuards);
        document.addEventListener('kpi:editGuardsRefresh', refreshMepSalesGuards);
        document.addEventListener('kpi:editLeaseChanged', refreshMepSalesGuards);
        applyMepDailySalesPathGuards();
      })();

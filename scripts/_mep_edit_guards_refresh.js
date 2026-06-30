      /* KPI-EDIT-GUARDS */
      (function () {
        function isJa() {
          return (
            String(document.documentElement.getAttribute('lang') || '')
              .toLowerCase()
              .indexOf('ja') === 0
          );
        }
        function tryMepLeaseForPath() {
          if (
            window.KpiYearStore &&
            KpiYearStore.getDailySalesInputPath() === 'mep' &&
            window.__KPI_EDIT_LEASE &&
            typeof window.__KPI_EDIT_LEASE.tryAcquire === 'function'
          ) {
            window.__KPI_EDIT_LEASE.tryAcquire(isJa() ? 'Monthly Edit' : 'Monthly Edit');
          }
        }
        function refreshMepSalesGuards() {
          if (typeof buildGrid === 'function') buildGrid();
        }
        document.addEventListener('kpi:dailySalesInputPathChanged', function () {
          tryMepLeaseForPath();
          refreshMepSalesGuards();
        });
        document.addEventListener('kpi:editGuardsApplied', refreshMepSalesGuards);
        document.addEventListener('kpi:editGuardsRefresh', refreshMepSalesGuards);
        document.addEventListener('kpi:editLeaseChanged', refreshMepSalesGuards);
      })();

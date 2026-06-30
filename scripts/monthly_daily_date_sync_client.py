"""Monthly cockpit ↔ Table Window / Focus Bar date sync."""

MONTHLY_APPLY_DAILY_SELECTION_OLD = """        updatePastKpiByIso(iso);
        if (window.KpiYearStore && typeof KpiYearStore.setSelectedDate === 'function') {
          KpiYearStore.setSelectedDate(iso, source || 'annual-ui');
        }
        return true;
      }
      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.setDailyDateByISO = function (iso, source) {"""

MONTHLY_APPLY_DAILY_SELECTION_NEW = """        updatePastKpiByIso(iso);
        document.dispatchEvent(
          new CustomEvent('annual:dailyDateChanged', {
            detail: { isoDate: iso, date: d, targetSales: target, source: source || 'selection' }
          })
        );
        if (window.KpiYearStore && typeof KpiYearStore.setSelectedDate === 'function') {
          KpiYearStore.setSelectedDate(iso, source || 'annual-ui');
        }
        return true;
      }
      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.setDailyDateByISO = function (iso, source) {"""

"""Phase 3 — refresh Sales Data / Past Sales Analyze when observed data changes."""

from __future__ import annotations

PHASE3_ANALYZE_MARKER = "/* KPI-PHASE3-ANALYZE-REFRESH */"
PHASE3_ANALYZE_END = "/* END KPI-PHASE3-ANALYZE-REFRESH */"

PHASE3_ANALYZE_BLOCK = """      /* KPI-PHASE3-ANALYZE-REFRESH */
      (function () {
        function refreshSalesDataAnalyzeIfOpen(ev) {
          if (ev && ev.detail && ev.detail.source === 'sales-data-analyze') return;
          var modal = document.getElementById('sales-data-modal');
          if (!modal || modal.hasAttribute('hidden')) return;
          if (typeof renderSalesDataAnalyze !== 'function') return;
          var scrollEl = document.getElementById('sales-data-pane-analyze');
          var scrollTop = scrollEl ? scrollEl.scrollTop : 0;
          try {
            renderSalesDataAnalyze();
          } catch (err) {
            console.error('[phase3] renderSalesDataAnalyze failed', err);
            return;
          }
          if (scrollEl) scrollEl.scrollTop = scrollTop;
        }
        function refreshPastSalesAnalyzeIfOpen() {
          var modal = document.getElementById('past-sales-modal');
          if (!modal || modal.hasAttribute('hidden')) return;
          if (typeof renderPastSalesAnalyze === 'function') {
            try {
              renderPastSalesAnalyze();
            } catch (err) {
              console.error('[phase3] renderPastSalesAnalyze failed', err);
            }
          }
        }
        function refreshAnalyzeSurfaces() {
          refreshSalesDataAnalyzeIfOpen();
          refreshPastSalesAnalyzeIfOpen();
        }
        document.addEventListener('kpi:observedChanged', refreshAnalyzeSurfaces);
        document.addEventListener('kpi:dailySalesChanged', function (ev) {
          var d = ev && ev.detail;
          if (!d || !d.year) return;
          refreshAnalyzeSurfaces();
        });
        document.addEventListener('annual:pastSalesSaved', refreshAnalyzeSurfaces);
        document.addEventListener('annual:salesDataSaved', refreshAnalyzeSurfaces);
        document.addEventListener('kpi:annualPlanChanged', refreshSalesDataAnalyzeIfOpen);
      })();
      /* END KPI-PHASE3-ANALYZE-REFRESH */"""

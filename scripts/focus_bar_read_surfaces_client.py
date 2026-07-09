"""Phase 11-5 — Focus Bar / Graph popover refresh on daily target mode & baseline changes."""

from __future__ import annotations

FOCUS_BAR_READ_SURFACES_MARKER = "/* KPI-FOCUS-BAR-READ-SURFACES-11-5 */"

FOCUS_BAR_REFRESH_BEFORE_115 = """      document.addEventListener('annual:calendarYearChanged', function () {
        setTimeout(refreshLower, 0);
      });
      document.addEventListener('annual:timelineRowsRendered', function () {
        setTimeout(refreshLower, 0);
      });
      setTimeout(refreshLower, 0);"""

FOCUS_BAR_REFRESH_AFTER_115 = f"""      document.addEventListener('annual:calendarYearChanged', function () {{
        setTimeout(refreshLower, 0);
      }});
      document.addEventListener('annual:timelineRowsRendered', function () {{
        setTimeout(refreshLower, 0);
      }});
      {FOCUS_BAR_READ_SURFACES_MARKER}
      document.addEventListener('kpi:dailyTargetModeChanged', function () {{
        setTimeout(refreshLower, 0);
      }});
      document.addEventListener('kpi:weekdayBaselineChanged', function () {{
        setTimeout(refreshLower, 0);
      }});
      setTimeout(refreshLower, 0);"""

GRAPH_LISTENERS_BEFORE_115 = """      document.addEventListener('kpi:readSurfacesRefresh', refreshGraphPopoverFromStore);
      document.addEventListener('annual:timelineRowsRendered', refreshGraphPopoverFromStore);

      syncLabels();"""

GRAPH_LISTENERS_AFTER_115 = f"""      document.addEventListener('kpi:readSurfacesRefresh', refreshGraphPopoverFromStore);
      document.addEventListener('annual:timelineRowsRendered', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:dailyTargetModeChanged', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:weekdayBaselineChanged', refreshGraphPopoverFromStore);

      syncLabels();"""

GRAPH_POPOVER_INJECT_OLD = """      window.addEventListener(
        'resize',
        function () {
          if (!root.hidden) positionPanel();
        },
        { passive: true }
      );

      syncLabels();
    })();
  </script>
  <script>
    (function () {
      var modal = document.getElementById('past-sales-modal');"""

GRAPH_POPOVER_INJECT_NEW = f"""      window.addEventListener(
        'resize',
        function () {{
          if (!root.hidden) positionPanel();
        }},
        {{ passive: true }}
      );

      function refreshGraphPopoverFromStore() {{
        if (!root.hidden) refreshGraphContent();
      }}
      document.addEventListener('kpi:dailySalesChanged', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:businessDayChanged', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:annualPlanChanged', refreshGraphPopoverFromStore);
      document.addEventListener('annual:salesMapChanged', refreshGraphPopoverFromStore);
      document.addEventListener('annual:salesDataSaved', refreshGraphPopoverFromStore);
      document.addEventListener('annual:pastSalesSaved', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:readSurfacesRefresh', refreshGraphPopoverFromStore);
      document.addEventListener('annual:timelineRowsRendered', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:dailyTargetModeChanged', refreshGraphPopoverFromStore);
      document.addEventListener('kpi:weekdayBaselineChanged', refreshGraphPopoverFromStore);

      syncLabels();
    }})();
  </script>
  <script>
    (function () {{
      var modal = document.getElementById('past-sales-modal');"""

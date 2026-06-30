"""Shared commit helper + Sales Data / Annual Edit annual-target input wiring."""

from __future__ import annotations

ANNUAL_TARGET_EDIT_MARKER = "/* KPI-ANNUAL-TARGET-EDIT-SURFACES */"


def annual_target_edit_surfaces_js() -> str:
    return f"""      {ANNUAL_TARGET_EDIT_MARKER}
      (function () {{
        function isJa() {{
          return String(document.documentElement.getAttribute('lang') || '')
            .toLowerCase()
            .indexOf('ja') === 0;
        }}

        function parseAnnualTargetInput(raw) {{
          var normalized = String(raw || '').replace(/[¥$,\\s]/g, '');
          var value = Number(normalized);
          return Number.isFinite(value) && value >= 0 ? value : NaN;
        }}

        function formatAnnualTargetDisplay(value) {{
          var n = Number(value);
          if (!Number.isFinite(n)) return '—';
          if (isJa()) {{
            return '\\u00a5' + n.toLocaleString('en-US', {{
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }});
          }}
          return '$' + n.toLocaleString('en-US', {{
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }});
        }}

        function resolveTargetYear(explicitYear) {{
          var y = explicitYear != null ? Number(explicitYear) : NaN;
          if (!Number.isFinite(y) && window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear != null) {{
            y = Number(window.__ANNUAL_DATA.calendarYear);
          }}
          if (!Number.isFinite(y) && window.KpiYearStore) {{
            y = Number(KpiYearStore.getOperatingYear());
          }}
          if (!Number.isFinite(y)) y = new Date().getFullYear();
          return y;
        }}

        function commitAnnualTargetSales(value, year, source) {{
          var y = resolveTargetYear(year);
          var n = Number(value);
          if (!Number.isFinite(n) || n < 0) return false;
          window.__ANNUAL_DATA = window.__ANNUAL_DATA || {{}};
          var oy = window.KpiYearStore ? Number(KpiYearStore.getOperatingYear()) : NaN;
          var cy =
            window.__ANNUAL_DATA.calendarYear != null
              ? Number(window.__ANNUAL_DATA.calendarYear)
              : NaN;
          if (y === oy || y === cy) {{
            window.__ANNUAL_DATA.targetSales = n;
          }}
          if (window.KpiYearStore && typeof KpiYearStore.writeAnnualTarget === 'function') {{
            KpiYearStore.writeAnnualTarget(y, n, {{ source: source || 'modal-target-edit' }});
          }}
          document.dispatchEvent(
            new CustomEvent('annual:targetSalesChanged', {{
              detail: {{
                targetSales: n,
                display: formatAnnualTargetDisplay(n),
                year: y,
                source: source || 'modal-target-edit',
              }},
            }})
          );
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function'
          ) {{
            window.__ANNUAL_UI.syncCockpitForCalendarYear(y);
          }}
          return true;
        }}

        function readAnnualTargetForYear(year) {{
          year = resolveTargetYear(year);
          if (window.KpiYearStore && typeof KpiYearStore.readAnnualTarget === 'function') {{
            var fromStore = KpiYearStore.readAnnualTarget(year);
            if (fromStore != null && Number.isFinite(Number(fromStore)) && Number(fromStore) > 0) {{
              return Number(fromStore);
            }}
          }}
          var oy = window.KpiYearStore ? Number(KpiYearStore.getOperatingYear()) : NaN;
          var cy =
            window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear != null
              ? Number(window.__ANNUAL_DATA.calendarYear)
              : NaN;
          if (
            (year === oy || year === cy) &&
            window.__ANNUAL_DATA &&
            window.__ANNUAL_DATA.targetSales != null
          ) {{
            var mem = Number(window.__ANNUAL_DATA.targetSales);
            if (Number.isFinite(mem) && mem > 0) return mem;
          }}
          var cockpitEl = document.getElementById('annual-target-sales-value');
          if (cockpitEl && (year === oy || year === cy)) {{
            var parsed = parseAnnualTargetInput(cockpitEl.textContent);
            if (Number.isFinite(parsed) && parsed > 0) return parsed;
          }}
          return null;
        }}

        function bindAnnualTargetInput(input, getYear, source) {{
          if (!input || input.getAttribute('data-kpi-target-bound') === '1') return;
          input.setAttribute('data-kpi-target-bound', '1');

          function syncInputFromStore() {{
            var y = getYear();
            var target = readAnnualTargetForYear(y);
            input.value = target != null ? formatAnnualTargetDisplay(target) : '';
            input.placeholder = '—';
          }}

          function commitFromInput() {{
            var y = getYear();
            var raw = parseAnnualTargetInput(input.value);
            if (!Number.isFinite(raw)) {{
              syncInputFromStore();
              return;
            }}
            commitAnnualTargetSales(raw, y, source);
            input.value = formatAnnualTargetDisplay(raw);
          }}

          input.addEventListener('change', commitFromInput);
          input.addEventListener('blur', commitFromInput);
          input.addEventListener('keydown', function (ev) {{
            if (ev.key === 'Enter') {{
              ev.preventDefault();
              input.blur();
            }}
          }});
          document.addEventListener('annual:targetSalesChanged', syncInputFromStore);
          document.addEventListener('kpi:annualPlanChanged', syncInputFromStore);
          syncInputFromStore();
          return syncInputFromStore;
        }}

        window.__ANNUAL_UI = window.__ANNUAL_UI || {{}};
        window.__ANNUAL_UI.commitAnnualTargetSales = commitAnnualTargetSales;
        window.__ANNUAL_UI.readAnnualTargetForYear = readAnnualTargetForYear;
        window.__ANNUAL_UI.bindAnnualTargetInput = bindAnnualTargetInput;
        window.__ANNUAL_UI.formatAnnualTargetDisplay = formatAnnualTargetDisplay;
      }})();
"""

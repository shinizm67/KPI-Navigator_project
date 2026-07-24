"""Cockpit open table + annual target sync when calendar year changes (Focus Bar scroll)."""

from __future__ import annotations

COCKPIT_YEAR_SYNC_MARKER = "/* KPI-COCKPIT-YEAR-SYNC */"

MONTH_KEYS = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]

DEFAULT_HL_WEIGHTS = [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115]


def cockpit_year_sync_js() -> str:
    month_keys_js = ", ".join(f'"{k}"' for k in MONTH_KEYS)
    default_hl_js = ", ".join(str(n) for n in DEFAULT_HL_WEIGHTS)
    return f"""      {COCKPIT_YEAR_SYNC_MARKER}
      (function () {{
        var MONTH_KEYS = [{month_keys_js}];
        var DEFAULT_HL_WEIGHTS = [{default_hl_js}];
        var DASH = '—';

        function isJa() {{
          return String(document.documentElement.getAttribute('lang') || '')
            .toLowerCase()
            .indexOf('ja') === 0;
        }}

        function pad2(n) {{
          return n < 10 ? '0' + n : String(n);
        }}

        function resolveCalendarYear(explicit) {{
          var y = explicit != null ? Number(explicit) : NaN;
          if (!Number.isFinite(y) && window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear != null) {{
            y = Number(window.__ANNUAL_DATA.calendarYear);
          }}
          if (!Number.isFinite(y) && window.KpiYearStore) {{
            y = Number(KpiYearStore.getOperatingYear());
          }}
          if (!Number.isFinite(y)) y = new Date().getFullYear();
          return y;
        }}

        function resolveBusinessDayMapForCockpit() {{
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.resolveBusinessDayMapForCockpit === 'function'
          ) {{
            return window.__ANNUAL_UI.resolveBusinessDayMapForCockpit();
          }}
          if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
            KpiYearStore.syncToAnnualDaily();
          }}
          var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
          return (daily && daily.businessDayByDate) || {{}};
        }}

        /** Cockpit: Sales Data B.DAY が明示的に true の日のみ */
        function isCalendarBusinessDay(y, m0, day) {{
          var d = new Date(y, m0, day);
          if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
          var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
          var bmap = resolveBusinessDayMapForCockpit();
          if (!Object.prototype.hasOwnProperty.call(bmap, iso)) return false;
          return !!bmap[iso];
        }}

        function countBusinessDaysInMonth(y, m0) {{
          var dc = new Date(y, m0 + 1, 0).getDate();
          var c = 0;
          for (var day = 1; day <= dc; day++) {{
            if (isCalendarBusinessDay(y, m0, day)) c++;
          }}
          return c;
        }}

        function fmtMoney(n) {{
          if (n == null || !Number.isFinite(Number(n))) return DASH;
          var v = Math.round(Number(n) * 100) / 100;
          if (window.KpiCurrency) {{
            return KpiCurrency.format(v, {{
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }});
          }}
          if (isJa()) {{
            return '\\u00a5' + v.toLocaleString('ja-JP', {{
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }});
          }}
          return '$' + v.toLocaleString('en-US', {{
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }});
        }}

        function fmtSignedMoney(n) {{
          if (n == null || !Number.isFinite(Number(n))) return DASH;
          var v = Math.round(Number(n) * 100) / 100;
          var abs = Math.abs(v);
          var body = fmtMoney(abs);
          if (body === DASH) return DASH;
          return v < 0 ? '-' + body : body;
        }}

        function fmtPct(n) {{
          if (n == null || !Number.isFinite(Number(n))) return DASH;
          return (Math.round(Number(n) * 100) / 100).toFixed(2) + '%';
        }}

        function setField(monthKey, field, text) {{
          var el = document.querySelector(
            '[data-field="annual.table.' + monthKey + '.' + field + '"]'
          );
          if (el) el.textContent = text;
        }}

        function readDailySalesAmount(iso) {{
          if (window.KpiYearStore && typeof KpiYearStore.readDailySales === 'function') {{
            var fromStore = KpiYearStore.readDailySales(iso);
            if (fromStore != null && Number.isFinite(Number(fromStore))) {{
              return Number(fromStore);
            }}
          }}
          var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
          var map = daily && daily.targetSalesByDate;
          if (map && Object.prototype.hasOwnProperty.call(map, iso)) {{
            return Number(map[iso]);
          }}
          return NaN;
        }}

        function gatherMonthlySales(year) {{
          var sales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var any = false;
          for (var m0 = 0; m0 < 12; m0++) {{
            var dc = new Date(year, m0 + 1, 0).getDate();
            for (var day = 1; day <= dc; day++) {{
              if (!isCalendarBusinessDay(year, m0, day)) continue;
              var iso = year + '-' + pad2(m0 + 1) + '-' + pad2(day);
              var amt = readDailySalesAmount(iso);
              if (Number.isFinite(amt) && amt > 0) {{
                sales[m0] += amt;
                any = true;
              }}
            }}
          }}
          return {{ sales: sales, any: any }};
        }}

        function parseTargetFromDom() {{
          var el = document.getElementById('annual-target-sales-value');
          if (!el) return null;
          var raw = String(el.textContent || '').trim();
          if (!raw || raw === DASH || raw === '-') return null;
          var n = Number(raw.replace(/[^\\d.-]/g, ''));
          if (!Number.isFinite(n) || n <= 0) return null;
          return n;
        }}

        function resolveAnnualTarget(year) {{
          year = Number(year);
          if (!Number.isFinite(year)) return null;
          var target = null;
          if (window.KpiYearStore && typeof KpiYearStore.readAnnualTarget === 'function') {{
            target = KpiYearStore.readAnnualTarget(year);
            if (target != null && Number.isFinite(Number(target)) && Number(target) > 0) {{
              return Number(target);
            }}
          }}
          var oy = window.KpiYearStore ? Number(KpiYearStore.getOperatingYear()) : NaN;
          var cy = resolveCalendarYear();
          if (year === oy || year === cy) {{
            if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.targetSales != null) {{
              var mem = Number(window.__ANNUAL_DATA.targetSales);
              if (Number.isFinite(mem) && mem > 0) return mem;
            }}
            var dom = parseTargetFromDom();
            if (dom != null) return dom;
          }}
          var past = window.__ANNUAL_DATA && window.__ANNUAL_DATA.pastSales;
          if (
            past &&
            past.referenceAnnualSalesByYear &&
            past.referenceAnnualSalesByYear[year] != null
          ) {{
            var pastTarget = Number(past.referenceAnnualSalesByYear[year]);
            if (Number.isFinite(pastTarget) && pastTarget > 0) return pastTarget;
          }}
          return null;
        }}

        function syncAnnualTargetDisplay(year, annualTarget) {{
          var el = document.getElementById('annual-target-sales-value');
          if (!el) return;
          var n = annualTarget;
          if (n == null || !Number.isFinite(Number(n)) || Number(n) <= 0) {{
            n = resolveAnnualTarget(year);
          }}
          if (n == null || !Number.isFinite(Number(n)) || Number(n) <= 0) {{
            el.textContent = DASH;
            return;
          }}
          el.textContent = fmtMoney(Number(n));
          if (window.__ANNUAL_DATA) {{
            var oy = window.KpiYearStore ? Number(KpiYearStore.getOperatingYear()) : NaN;
            var cy = resolveCalendarYear();
            if (year === oy || year === cy) {{
              window.__ANNUAL_DATA.targetSales = Number(n);
            }}
          }}
        }}

        function syncCockpitForCalendarYear(explicitYear) {{
          var year = resolveCalendarYear(explicitYear);
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {{
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
          }}

          var annualTarget = resolveAnnualTarget(year);
          var weights = null;
          if (window.KpiYearStore) {{
            weights = KpiYearStore.readMonthlyHlWeights(year);
          }}
          var hasPlan =
            annualTarget != null && Number.isFinite(Number(annualTarget)) && Number(annualTarget) > 0;
          if (!weights && hasPlan) weights = DEFAULT_HL_WEIGHTS.slice();

          syncAnnualTargetDisplay(year, hasPlan ? Number(annualTarget) : null);

          var monthlyBD = [];
          var totalBD = 0;
          for (var mi = 0; mi < 12; mi++) {{
            var bd = countBusinessDaysInMonth(year, mi);
            monthlyBD.push(bd);
            totalBD += bd;
          }}

          var gathered = gatherMonthlySales(year);
          var monthlySales = gathered.sales;

          for (var m0 = 0; m0 < 12; m0++) {{
            var mk = MONTH_KEYS[m0];
            var bdCount = monthlyBD[m0];
            setField(mk, 'businessDay', String(bdCount));

            if (!hasPlan) {{
              setField(mk, 'monthlyAverageTarget', DASH);
              setField(mk, 'hlSeasonPct', DASH);
              setField(mk, 'monthlyTarget', DASH);
              setField(mk, 'dailyTarget', DASH);
            }} else {{
              var hl = weights && weights[m0] != null ? Number(weights[m0]) : 100;
              var monthlyAvg =
                totalBD > 0 ? (Number(annualTarget) * bdCount) / totalBD : NaN;
              var monthlyTarget =
                Number.isFinite(monthlyAvg) ? (monthlyAvg * hl) / 100 : NaN;
              var dailyTarget =
                bdCount > 0 && Number.isFinite(monthlyTarget)
                  ? monthlyTarget / bdCount
                  : NaN;
              setField(mk, 'monthlyAverageTarget', fmtMoney(monthlyAvg));
              setField(mk, 'hlSeasonPct', Number.isFinite(hl) ? hl + '%' : DASH);
              setField(mk, 'monthlyTarget', fmtMoney(monthlyTarget));
              setField(mk, 'dailyTarget', fmtMoney(dailyTarget));

              var salesAmt = monthlySales[m0];
              if (gathered.any && Number.isFinite(salesAmt) && salesAmt > 0) {{
                setField(mk, 'monthlyProfit', fmtMoney(salesAmt));
                setField(
                  mk,
                  'monthlyKgi',
                  fmtSignedMoney(salesAmt - monthlyTarget)
                );
                setField(
                  mk,
                  'hlSeasonActualPct',
                  monthlyAvg > 0 ? fmtPct((salesAmt / monthlyAvg) * 100) : DASH
                );
                setField(
                  mk,
                  'hlPercent',
                  monthlyTarget > 0 ? fmtPct((salesAmt / monthlyTarget) * 100) : DASH
                );
              }} else {{
                setField(mk, 'monthlyProfit', DASH);
                setField(mk, 'monthlyKgi', DASH);
                setField(mk, 'hlSeasonActualPct', DASH);
                setField(mk, 'hlPercent', DASH);
              }}
              continue;
            }}

            setField(mk, 'monthlyProfit', DASH);
            setField(mk, 'monthlyKgi', DASH);
            setField(mk, 'hlSeasonActualPct', DASH);
            setField(mk, 'hlPercent', DASH);
          }}

          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.recalcMonthlyAllocationTotal === 'function'
          ) {{
            window.__ANNUAL_UI.recalcMonthlyAllocationTotal();
          }}
          if (typeof window.refreshArea1Cockpit === 'function') {{
            window.refreshArea1Cockpit();
          }}
        }}

        window.__ANNUAL_UI = window.__ANNUAL_UI || {{}};
        window.__ANNUAL_UI.syncCockpitForCalendarYear = syncCockpitForCalendarYear;

        document.addEventListener('annual:calendarYearChanged', function () {{
          syncCockpitForCalendarYear();
        }});
        document.addEventListener('annual:salesMapChanged', function () {{
          syncCockpitForCalendarYear();
        }});
        document.addEventListener('annual:businessDayMapChanged', function () {{
          syncCockpitForCalendarYear();
        }});
        document.addEventListener('kpi:annualPlanChanged', function () {{
          syncCockpitForCalendarYear();
        }});
        document.addEventListener('annual:targetSalesChanged', function () {{
          syncCockpitForCalendarYear();
        }});
        document.addEventListener('annual:pastSalesSaved', function () {{
          syncCockpitForCalendarYear();
        }});
        // Defer so calendarYear, __ANNUAL_DATA.targetSales, and DOM fallbacks exist.
        function scheduleInitialCockpitSync() {{
          setTimeout(function () {{
            syncCockpitForCalendarYear();
          }}, 0);
        }}
        scheduleInitialCockpitSync();
      }})();
"""

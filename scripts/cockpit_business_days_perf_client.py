"""Monthly perf — business-day counts: single bmap pass + cache + deferred init."""

from __future__ import annotations

COCKPIT_BD_PERF_MARKER = "/* KPI-COCKPIT-BUSINESS-DAYS-PERF */"

COCKPIT_BD_BLOCK_OLD = """      /* KPI-COCKPIT-BUSINESS-DAYS */
      function resolveBusinessDayMapForCockpit() {
        var sdm = document.getElementById('sales-data-modal');
        var sdmTable = document.getElementById('sales-data-modal-table');
        var modalLive = sdm && !sdm.hasAttribute('hidden') && sdmTable;
        if (!modalLive && window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
          KpiYearStore.syncToAnnualDaily();
        }
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var bmap = Object.assign({}, (daily && daily.businessDayByDate) || {});
        if (modalLive) {
          sdmTable.querySelectorAll('.sales-data-modal__cb[data-iso-date]').forEach(function (cb) {
            var iso = cb.getAttribute('data-iso-date');
            if (iso) bmap[iso] = !!cb.checked;
          });
        }
        return bmap;
      }

      /** Cockpit 営業日数: Sales Data の B.DAY が明示的に true の日のみ（平日フォールバックなし） */
      function isCalendarBusinessDay(y, m0, day) {
        var d = new Date(y, m0, day);
        if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
        var bmap = resolveBusinessDayMapForCockpit();
        if (!Object.prototype.hasOwnProperty.call(bmap, iso)) return false;
        return !!bmap[iso];
      }

      function countBusinessDaysInMonth(y, m0) {
        var dc = new Date(y, m0 + 1, 0).getDate();
        var c = 0;
        for (var day = 1; day <= dc; day++) {
          if (isCalendarBusinessDay(y, m0, day)) c++;
        }
        return c;
      }

      function countBusinessDaysInYear(y) {
        y = Number(y);
        if (!isFinite(y)) return 0;
        var c = 0;
        for (var m0 = 0; m0 < 12; m0++) c += countBusinessDaysInMonth(y, m0);
        return c;
      }

      function syncBusinessDayDisplayFromDailyMap() {
        var cy =
          window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear != null
            ? Number(window.__ANNUAL_DATA.calendarYear)
            : new Date().getFullYear();
        if (!isFinite(cy)) cy = new Date().getFullYear();
        var total = countBusinessDaysInYear(cy);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.totalBusinessDay = total;
        bdEl.textContent = String(total);

        var rows = document.querySelectorAll('.annual-open-table tbody tr');
        for (var i = 0; i < rows.length && i < 12; i++) {
          var cells = rows[i].getElementsByTagName('td');
          if (cells.length >= 2) cells[1].textContent = String(countBusinessDaysInMonth(cy, i));
        }
      }

      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap = syncBusinessDayDisplayFromDailyMap;
      window.__ANNUAL_UI.resolveBusinessDayMapForCockpit = resolveBusinessDayMapForCockpit;

      document.addEventListener('annual:editModalSaved', function () {
        syncBusinessDayDisplayFromDailyMap();
      });
      document.addEventListener('annual:businessDayMapChanged', function () {
        syncBusinessDayDisplayFromDailyMap();
      });
      document.addEventListener('annual:salesMapChanged', function () {
        syncBusinessDayDisplayFromDailyMap();
      });
      document.addEventListener('annual:salesDataSaved', function () {
        syncBusinessDayDisplayFromDailyMap();
      });

      syncBusinessDayDisplayFromDailyMap();"""

COCKPIT_BD_BLOCK_NEW = f"""      /* KPI-COCKPIT-BUSINESS-DAYS */
      {COCKPIT_BD_PERF_MARKER}
      var __cockpitBmapCache = null;
      var __cockpitBmapCacheModalLive = false;
      var __businessDayCountsCache = Object.create(null);

      function invalidateCockpitBusinessDayCache() {{
        __cockpitBmapCache = null;
        __cockpitBmapCacheModalLive = false;
        __businessDayCountsCache = Object.create(null);
      }}

      function resolveBusinessDayMapForCockpit() {{
        var sdm = document.getElementById('sales-data-modal');
        var sdmTable = document.getElementById('sales-data-modal-table');
        var modalLive = sdm && !sdm.hasAttribute('hidden') && sdmTable;
        if (!modalLive && __cockpitBmapCache && !__cockpitBmapCacheModalLive) {{
          return __cockpitBmapCache;
        }}
        if (!modalLive && window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var base = (daily && daily.businessDayByDate) || {{}};
        var bmap;
        if (modalLive) {{
          bmap = Object.assign({{}}, base);
          sdmTable.querySelectorAll('.sales-data-modal__cb[data-iso-date]').forEach(function (cb) {{
            var iso = cb.getAttribute('data-iso-date');
            if (iso) bmap[iso] = !!cb.checked;
          }});
          __cockpitBmapCache = null;
          __cockpitBmapCacheModalLive = true;
        }} else {{
          bmap = base;
          __cockpitBmapCache = bmap;
          __cockpitBmapCacheModalLive = false;
        }}
        return bmap;
      }}

      /** Cockpit 営業日数: Sales Data の B.DAY が明示的に true の日のみ（平日フォールバックなし） */
      function isCalendarBusinessDay(y, m0, day, bmap) {{
        var d = new Date(y, m0, day);
        if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
        var map = bmap || resolveBusinessDayMapForCockpit();
        if (!Object.prototype.hasOwnProperty.call(map, iso)) return false;
        return !!map[iso];
      }}

      function computeBusinessDayCountsForYear(y, bmap) {{
        y = Number(y);
        if (!isFinite(y)) {{
          return {{ total: 0, monthly: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] }};
        }}
        if (!bmap && __businessDayCountsCache[y]) return __businessDayCountsCache[y];
        var map = bmap || resolveBusinessDayMapForCockpit();
        var monthly = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        var total = 0;
        var yearPrefix = String(y) + '-';
        var isoKeys = Object.keys(map || {{}});
        if (isoKeys.length) {{
          for (var ki = 0; ki < isoKeys.length; ki++) {{
            var iso = isoKeys[ki];
            if (!map[iso]) continue;
            if (String(iso).indexOf(yearPrefix) !== 0) continue;
            var m = Number(String(iso).slice(5, 7)) - 1;
            if (!Number.isFinite(m) || m < 0 || m > 11) continue;
            monthly[m] += 1;
            total += 1;
          }}
          var result = {{ total: total, monthly: monthly }};
          if (!bmap) __businessDayCountsCache[y] = result;
          return result;
        }}
        for (var m0 = 0; m0 < 12; m0++) {{
          var dc = new Date(y, m0 + 1, 0).getDate();
          var mc = 0;
          for (var day = 1; day <= dc; day++) {{
            if (isCalendarBusinessDay(y, m0, day, map)) mc++;
          }}
          monthly[m0] = mc;
          total += mc;
        }}
        var result = {{ total: total, monthly: monthly }};
        if (!bmap) __businessDayCountsCache[y] = result;
        return result;
      }}

      function countBusinessDaysInMonth(y, m0, bmap) {{
        var counts = computeBusinessDayCountsForYear(y, bmap);
        return counts.monthly[Number(m0)] || 0;
      }}

      function countBusinessDaysInYear(y, bmap) {{
        return computeBusinessDayCountsForYear(y, bmap).total;
      }}

      var __syncBdDisplayTimer = null;
      function syncBusinessDayDisplayFromDailyMap() {{
        var cy =
          window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear != null
            ? Number(window.__ANNUAL_DATA.calendarYear)
            : new Date().getFullYear();
        if (!isFinite(cy)) cy = new Date().getFullYear();
        invalidateCockpitBusinessDayCache();
        var bmap = resolveBusinessDayMapForCockpit();
        var counts = computeBusinessDayCountsForYear(cy, bmap);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {{}};
        window.__ANNUAL_DATA.totalBusinessDay = counts.total;
        bdEl.textContent = String(counts.total);

        var rows = document.querySelectorAll('.annual-open-table tbody tr');
        for (var i = 0; i < rows.length && i < 12; i++) {{
          var cells = rows[i].getElementsByTagName('td');
          if (cells.length >= 2) cells[1].textContent = String(counts.monthly[i]);
        }}
      }}

      function scheduleSyncBusinessDayDisplayFromDailyMap() {{
        if (__syncBdDisplayTimer != null) window.clearTimeout(__syncBdDisplayTimer);
        __syncBdDisplayTimer = window.setTimeout(function () {{
          __syncBdDisplayTimer = null;
          syncBusinessDayDisplayFromDailyMap();
        }}, 0);
      }}

      window.__ANNUAL_UI = window.__ANNUAL_UI || {{}};
      window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap = syncBusinessDayDisplayFromDailyMap;
      window.__ANNUAL_UI.scheduleSyncBusinessDayDisplayFromDailyMap =
        scheduleSyncBusinessDayDisplayFromDailyMap;
      window.__ANNUAL_UI.resolveBusinessDayMapForCockpit = resolveBusinessDayMapForCockpit;
      window.__ANNUAL_UI.computeBusinessDayCountsForYear = computeBusinessDayCountsForYear;
      window.__ANNUAL_UI.invalidateCockpitBusinessDayCache = invalidateCockpitBusinessDayCache;

      document.addEventListener('annual:editModalSaved', scheduleSyncBusinessDayDisplayFromDailyMap);
      document.addEventListener('annual:businessDayMapChanged', function () {{
        invalidateCockpitBusinessDayCache();
        scheduleSyncBusinessDayDisplayFromDailyMap();
      }});
      document.addEventListener('annual:salesMapChanged', function () {{
        invalidateCockpitBusinessDayCache();
        scheduleSyncBusinessDayDisplayFromDailyMap();
      }});
      document.addEventListener('annual:salesDataSaved', function () {{
        invalidateCockpitBusinessDayCache();
        scheduleSyncBusinessDayDisplayFromDailyMap();
      }});

      if (typeof window.requestIdleCallback === 'function') {{
        window.requestIdleCallback(syncBusinessDayDisplayFromDailyMap, {{ timeout: 150 }});
      }} else {{
        window.setTimeout(syncBusinessDayDisplayFromDailyMap, 0);
      }}"""

YEAR_SYNC_IS_FN_OLD = """        /** Cockpit: Sales Data B.DAY が明示的に true の日のみ */
        function isCalendarBusinessDay(y, m0, day) {
          var d = new Date(y, m0, day);
          if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
          var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
          var bmap = resolveBusinessDayMapForCockpit();
          if (!Object.prototype.hasOwnProperty.call(bmap, iso)) return false;
          return !!bmap[iso];
        }"""

YEAR_SYNC_IS_FN_NEW = """        /** Cockpit: Sales Data B.DAY が明示的に true の日のみ */
        function isCalendarBusinessDay(y, m0, day, bmap) {
          var d = new Date(y, m0, day);
          if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
          var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
          var map = bmap || resolveBusinessDayMapForCockpit();
          if (!Object.prototype.hasOwnProperty.call(map, iso)) return false;
          return !!map[iso];
        }"""

GATHER_MONTHLY_SALES_OLD = """        function gatherMonthlySales(year) {
          year = Number(year);
          if (__gatheredMonthlySalesByYear[year]) return __gatheredMonthlySalesByYear[year];
          var sales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var any = false;
          for (var m0 = 0; m0 < 12; m0++) {
            var dc = new Date(year, m0 + 1, 0).getDate();
            for (var day = 1; day <= dc; day++) {
              if (!isCalendarBusinessDay(year, m0, day)) continue;
              var iso = year + '-' + pad2(m0 + 1) + '-' + pad2(day);
              var amt = readDailySalesAmount(iso);
              if (Number.isFinite(amt) && amt > 0) {
                sales[m0] += amt;
                any = true;
              }
            }
          }
          var out = { sales: sales, any: any };
          __gatheredMonthlySalesByYear[year] = out;
          return out;
        }"""

GATHER_MONTHLY_SALES_NEW = """        function gatherMonthlySales(year) {
          year = Number(year);
          if (__gatheredMonthlySalesByYear[year]) return __gatheredMonthlySalesByYear[year];
          var sales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var any = false;
          var bmap = resolveBusinessDayMapForCockpitFast(year);
          if (!bmap || !Object.keys(bmap).length) {
            bmap = resolveBusinessDayMapForCockpit();
          }
          var yearPrefix = String(year) + '-';
          Object.keys(bmap || {}).forEach(function (iso) {
            if (!bmap[iso]) return;
            if (String(iso).indexOf(yearPrefix) !== 0) return;
            var m0 = Number(String(iso).slice(5, 7)) - 1;
            if (!Number.isFinite(m0) || m0 < 0 || m0 > 11) return;
            var amt = readDailySalesAmount(iso);
            if (Number.isFinite(amt) && amt > 0) {
              sales[m0] += amt;
              any = true;
            }
          });
          var out = { sales: sales, any: any };
          __gatheredMonthlySalesByYear[year] = out;
          return out;
        }"""

GATHER_MONTH_FN_OLD = """        function gatherMonthlySalesForMonth(year, m0) {
          year = Number(year);
          m0 = Number(m0);
          var cached = __gatheredMonthlySalesByYear[year];
          if (cached) {
            var amt = cached.sales[m0];
            return {
              sum: amt,
              any: cached.any && Number.isFinite(amt) && amt > 0,
            };
          }
          var sum = 0;
          var any = false;
          var dc = new Date(year, m0 + 1, 0).getDate();
          for (var day = 1; day <= dc; day++) {
            if (!isCalendarBusinessDay(year, m0, day)) continue;
            var iso = year + '-' + pad2(m0 + 1) + '-' + pad2(day);
            var amtDay = readDailySalesAmount(iso);
            if (Number.isFinite(amtDay) && amtDay > 0) {
              sum += amtDay;
              any = true;
            }
          }
          return { sum: sum, any: any };
        }"""

GATHER_MONTH_FN_NEW = """        function gatherMonthlySalesForMonth(year, m0) {
          year = Number(year);
          m0 = Number(m0);
          var cached = __gatheredMonthlySalesByYear[year];
          if (cached) {
            var amt = cached.sales[m0];
            return {
              sum: amt,
              any: cached.any && Number.isFinite(amt) && amt > 0,
            };
          }
          var sum = 0;
          var any = false;
          var bmap = resolveBusinessDayMapForCockpitFast(year);
          if (!bmap || !Object.keys(bmap).length) {
            bmap = resolveBusinessDayMapForCockpit();
          }
          var monthPrefix = String(year) + '-' + pad2(m0 + 1) + '-';
          Object.keys(bmap || {}).forEach(function (iso) {
            if (!bmap[iso]) return;
            if (String(iso).indexOf(monthPrefix) !== 0) return;
            var amtDay = readDailySalesAmount(iso);
            if (Number.isFinite(amtDay) && amtDay > 0) {
              sum += amtDay;
              any = true;
            }
          });
          return { sum: sum, any: any };
        }"""

SCHEDULE_SYNC_BD_CALL_OLD = """            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
            bmap = resolveBusinessDayMapForCockpitFast(year);"""

SCHEDULE_SYNC_BD_CALL_NEW = """            if (typeof window.__ANNUAL_UI.scheduleSyncBusinessDayDisplayFromDailyMap === 'function') {
              window.__ANNUAL_UI.scheduleSyncBusinessDayDisplayFromDailyMap();
            } else {
              window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
            }
            bmap = resolveBusinessDayMapForCockpitFast(year);"""

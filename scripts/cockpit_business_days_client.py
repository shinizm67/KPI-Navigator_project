"""Cockpit Total Business Days: count only explicit Sales Data B.DAY === true."""

from __future__ import annotations

COCKPIT_BUSINESS_DAYS_MARKER = "/* KPI-COCKPIT-BUSINESS-DAYS */"

# Replaces isCalendarBusinessDay in syncBusinessDayDisplayFromDailyMap IIFE.
SYNC_BUSINESS_DAY_IS_FN_OLD_ANNUAL = """      /** businessDayByDate があれば最優先。未設定時のみ targetSalesByDate と土日既定へフォールバック。 */
      function isCalendarBusinessDay(y, m0, day) {
        var d = new Date(y, m0, day);
        if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
        var dow = d.getDay();
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var bmap = daily && daily.businessDayByDate;
        var map = daily && daily.targetSalesByDate;
        var isWk = dow === 0 || dow === 6;
        if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {
          return !!bmap[iso];
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) return !isWk;
          if (n === 0) return false;
          return true;
        }
        return !isWk;
      }"""

SYNC_BUSINESS_DAY_IS_FN_OLD_EN_ANNUAL = """      function isCalendarBusinessDay(y, m0, day) {
        var d = new Date(y, m0, day);
        if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
        var dow = d.getDay();
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var bmap = daily && daily.businessDayByDate;
        var map = daily && daily.targetSalesByDate;
        var isWk = dow === 0 || dow === 6;
        if (bmap && Object.prototype.hasOwnProperty.call(bmap, iso)) {
          return !!bmap[iso];
        }
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) return !isWk;
          if (n === 0) return false;
          return true;
        }
        return !isWk;
      }"""

SYNC_BUSINESS_DAY_IS_FN_OLD_MONTHLY = """      /** Edit モーダル save と同じ前提: map にキーがあり 0 なら店休、正の数なら営業。未設定は土日休み・平日営業。 */
      function isCalendarBusinessDay(y, m0, day) {
        var d = new Date(y, m0, day);
        if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
        var dow = d.getDay();
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var map = daily && daily.targetSalesByDate;
        var isWk = dow === 0 || dow === 6;
        if (map && Object.prototype.hasOwnProperty.call(map, iso)) {
          var n = Number(map[iso]);
          if (!isFinite(n)) return !isWk;
          if (n === 0) return false;
          return true;
        }
        return !isWk;
      }"""

SYNC_BUSINESS_DAY_IS_FN_NEW = f"""      {COCKPIT_BUSINESS_DAYS_MARKER}
      function resolveBusinessDayMapForCockpit() {{
        if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
          KpiYearStore.syncToAnnualDaily();
        }}
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        return (daily && daily.businessDayByDate) || {{}};
      }}

      /** Cockpit 営業日数: Sales Data の B.DAY が明示的に true の日のみ（平日フォールバックなし） */
      function isCalendarBusinessDay(y, m0, day) {{
        var d = new Date(y, m0, day);
        if (d.getFullYear() !== y || d.getMonth() !== m0 || d.getDate() !== day) return false;
        var iso = y + '-' + pad2(m0 + 1) + '-' + pad2(day);
        var bmap = resolveBusinessDayMapForCockpit();
        if (!Object.prototype.hasOwnProperty.call(bmap, iso)) return false;
        return !!bmap[iso];
      }}"""

SYNC_BUSINESS_DAY_LISTENERS_OLD_MONTHLY = """      document.addEventListener('annual:editModalSaved', function () {
        syncBusinessDayDisplayFromDailyMap();
      });

      syncBusinessDayDisplayFromDailyMap();"""

SYNC_BUSINESS_DAY_LISTENERS_NEW_MONTHLY = """      document.addEventListener('annual:editModalSaved', function () {
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

SYNC_BUSINESS_DAY_LISTENERS_APPEND_ANNUAL = """      document.addEventListener('annual:salesMapChanged', function () {
        syncBusinessDayDisplayFromDailyMap();
      });

      syncBusinessDayDisplayFromDailyMap();"""

SYNC_BUSINESS_DAY_LISTENERS_APPEND_ANNUAL_NEW = """      document.addEventListener('annual:salesMapChanged', function () {
        syncBusinessDayDisplayFromDailyMap();
      });
      document.addEventListener('annual:salesDataSaved', function () {
        syncBusinessDayDisplayFromDailyMap();
      });

      syncBusinessDayDisplayFromDailyMap();"""

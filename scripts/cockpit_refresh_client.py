"""Cockpit (Area1) live refresh — sales, targets, diffs, achievement bars."""

from __future__ import annotations

from diff_step4_client import DIFF_STEP4_END, DIFF_STEP4_MARKER, diff_step4_tw_helpers_js

COCKPIT_REFRESH_MARKER = "/* KPI-COCKPIT-REFRESH */"
COCKPIT_REFRESH_END = "/* END KPI-COCKPIT-REFRESH */"

WIDGET_RETURN_OLD = """        return {
          setPercent: function (value) {
            renderAllocation(value);
          },
          getPercent: function () {
            return currentPercent;
          }
        };"""

WIDGET_RETURN_NEW = """        return {
          setPercent: function (value) {
            renderAllocation(value);
          },
          getPercent: function () {
            return currentPercent;
          },
          setDisabled: function () {
            if (percentEl) percentEl.textContent = '—';
            var markerColor = options.achievementAlertColors
              ? getAchievementMarkerColor(100)
              : getAllocationMarkerColor();
            varRoot.style.setProperty('--kgi-x', '0px');
            varRoot.style.setProperty('--fill-w', '0px');
            varRoot.style.setProperty('--marker-color', markerColor);
            currentPercent = 0;
          },
          percentEl: percentEl,
          graphEl: graphEl,
        };"""

COCKPIT_DAILY_WIDGET_OLD = """      initAllocationWidget({
        graphId: 'annual-achievement-graph',
        percentId: 'annual-achievement-percent',
        dataKey: 'achievementPercent',
        promptLabel: '達成率',
        editable: true,
        achievementAlertColors: true
      });"""

COCKPIT_DAILY_WIDGET_NEW = """      window.__area1CockpitWidgets = window.__area1CockpitWidgets || {};
      window.__area1CockpitWidgets.dailyAch = initAllocationWidget({
        graphId: 'annual-achievement-graph',
        percentId: 'annual-achievement-percent',
        dataKey: 'achievementPercent',
        promptLabel: '達成率',
        editable: true,
        achievementAlertColors: true
      });"""

COCKPIT_MONTHLY_WIDGET_OLD = """      initAllocationWidget({
        graphId: 'annual-group5-monthly-achievement-graph',
        percentId: 'annual-group5-monthly-achievement-percent',
        dataKey: 'group5MonthlyAchievementPercent',
        promptLabel: '達成率（月次累積）',
        editable: true,
        achievementAlertColors: true,
        fallbackPercent: 108
      });"""

COCKPIT_MONTHLY_WIDGET_NEW = """      window.__area1CockpitWidgets.monthlyAch = initAllocationWidget({
        graphId: 'annual-group5-monthly-achievement-graph',
        percentId: 'annual-group5-monthly-achievement-percent',
        dataKey: 'group5MonthlyAchievementPercent',
        promptLabel: '達成率（月次累積）',
        editable: true,
        achievementAlertColors: true,
        fallbackPercent: 108
      });"""

COCKPIT_ANNUAL_WIDGET_OLD = """      initAllocationWidget({
        graphId: 'annual-group5-annual-achievement-graph',
        percentId: 'annual-group5-annual-achievement-percent',
        dataKey: 'group5AnnualAchievementPercent',
        promptLabel: '達成率（年次累積）',
        editable: true,
        achievementAlertColors: true,
        fallbackPercent: 108
      });"""

COCKPIT_ANNUAL_WIDGET_NEW = """      window.__area1CockpitWidgets.annualAch = initAllocationWidget({
        graphId: 'annual-group5-annual-achievement-graph',
        percentId: 'annual-group5-annual-achievement-percent',
        dataKey: 'group5AnnualAchievementPercent',
        promptLabel: '達成率（年次累積）',
        editable: true,
        achievementAlertColors: true,
        fallbackPercent: 108
      });"""

COCKPIT_DAILY_WIDGET_OLD_EN = """      initAllocationWidget({
        graphId: 'annual-achievement-graph',
        percentId: 'annual-achievement-percent',
        dataKey: 'achievementPercent',
        promptLabel: 'Achievement',
        editable: true,
        achievementAlertColors: true
      });"""

COCKPIT_MONTHLY_WIDGET_OLD_EN = """      initAllocationWidget({
        graphId: 'annual-group5-monthly-achievement-graph',
        percentId: 'annual-group5-monthly-achievement-percent',
        dataKey: 'group5MonthlyAchievementPercent',
        promptLabel: 'Achievement (monthly cumulative)',
        editable: true,
        achievementAlertColors: true,
        fallbackPercent: 108
      });"""

COCKPIT_ANNUAL_WIDGET_OLD_EN = """      initAllocationWidget({
        graphId: 'annual-group5-annual-achievement-graph',
        percentId: 'annual-group5-annual-achievement-percent',
        dataKey: 'group5AnnualAchievementPercent',
        promptLabel: 'Achievement (annual cumulative)',
        editable: true,
        achievementAlertColors: true,
        fallbackPercent: 108
      });"""

COCKPIT_COMPUTE_ANCHOR = """      var monthlyAllocationWidget = initAllocationWidget({
        graphId: 'annual-allocation-graph',"""


def cockpit_refresh_js() -> str:
    helpers = diff_step4_tw_helpers_js()
    return f"""    {COCKPIT_REFRESH_MARKER}
    (function () {{
{helpers}
      var DASH = '—';
      function twAchPct(actual, target) {{
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return NaN;
        return (actual / target) * 100;
      }}
      function resolveArea1Iso() {{
        if (window.KpiYearStore && typeof KpiYearStore.getSelectedDate === 'function') {{
          var iso = KpiYearStore.getSelectedDate();
          if (iso) return iso;
        }}
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (daily && daily.selectedDate) return daily.selectedDate;
        var now = new Date();
        return (
          now.getFullYear() +
          '-' +
          String(now.getMonth() + 1).padStart(2, '0') +
          '-' +
          String(now.getDate()).padStart(2, '0')
        );
      }}
      function fmtArea1Money(n) {{
        if (typeof window.__twFmtMoney === 'function') return window.__twFmtMoney(n);
        if (!Number.isFinite(Number(n))) return DASH;
        var isJa = document.documentElement.getAttribute('lang') === 'ja';
        var v = Math.round(Number(n));
        if (isJa) return '¥' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');
      }}
      function setMoneyCell(el, value, enabled) {{
        if (!el) return;
        el.textContent = enabled && Number.isFinite(Number(value)) ? fmtArea1Money(value) : DASH;
      }}
      function setDiffCell(el, actual, target, hasPlan) {{
        if (!el) return;
        if (!hasPlan || !Number.isFinite(Number(actual)) || !Number.isFinite(Number(target))) {{
          el.textContent = DASH;
          applyTwDiffSurfaceEl(el, NaN, NaN);
          return;
        }}
        var a = Number(actual);
        var t = Number(target);
        el.textContent =
          typeof window.__twFmtDiff === 'function' ? window.__twFmtDiff(a, t) : fmtArea1Money(a - t);
        applyTwDiffSurfaceEl(el, a, t);
      }}
      function setAchWidget(widget, actual, target, enabled) {{
        if (!widget) return;
        if (!enabled) {{
          if (typeof widget.setDisabled === 'function') widget.setDisabled();
          return;
        }}
        var pct = twAchPct(actual, target);
        if (!Number.isFinite(pct)) {{
          if (typeof widget.setDisabled === 'function') widget.setDisabled();
          return;
        }}
        if (typeof widget.setPercent === 'function') widget.setPercent(Math.max(0.1, pct));
      }}
      function refreshArea1Cockpit(iso) {{
        iso = iso || resolveArea1Iso();
        var compute =
          typeof window.__computeTwMetricsForIso === 'function'
            ? window.__computeTwMetricsForIso
            : null;
        var m = compute ? compute(iso) : null;
        var dailySalesEl = document.getElementById('annual-group5-sales-value');
        var dailyTargetEl = document.getElementById('annual-current-sales-value');
        var dailyDiffEl = document.getElementById('annual-difference-value');
        var monthlySalesEl = document.getElementById('annual-group5-monthly-cumulative-sales');
        var monthlyTargetEl = document.getElementById('annual-group5-monthly-cumulative-target');
        var monthlyDiffEl = document.getElementById('annual-group5-monthly-cumulative-diff');
        var annualSalesEl = document.getElementById('annual-group5-annual-cumulative-sales');
        var annualTargetEl = document.getElementById('annual-group5-annual-cumulative-target');
        var annualDiffEl = document.getElementById('annual-group5-annual-cumulative-diff');
        var widgets = window.__area1CockpitWidgets || {{}};
        if (!m) {{
          setMoneyCell(dailySalesEl, NaN, false);
          setMoneyCell(dailyTargetEl, NaN, false);
          setDiffCell(dailyDiffEl, NaN, NaN, false);
          setAchWidget(widgets.dailyAch, NaN, NaN, false);
          setMoneyCell(monthlySalesEl, NaN, false);
          setMoneyCell(monthlyTargetEl, NaN, false);
          setDiffCell(monthlyDiffEl, NaN, NaN, false);
          setAchWidget(widgets.monthlyAch, NaN, NaN, false);
          setMoneyCell(annualSalesEl, NaN, false);
          setMoneyCell(annualTargetEl, NaN, false);
          setDiffCell(annualDiffEl, NaN, NaN, false);
          setAchWidget(widgets.annualAch, NaN, NaN, false);
          return;
        }}
        var hasDailyPlan = m.isBusinessToday && m.dailyTarget != null;
        setMoneyCell(dailySalesEl, m.dailySales, m.isBusinessToday);
        setMoneyCell(dailyTargetEl, m.dailyTarget, hasDailyPlan);
        setDiffCell(dailyDiffEl, m.dailySales, m.dailyTarget, hasDailyPlan);
        setAchWidget(widgets.dailyAch, m.dailySales, m.dailyTarget, hasDailyPlan);
        var hasMonthlyPlan = m.hasPlan;
        setMoneyCell(monthlySalesEl, m.mtdA, hasMonthlyPlan);
        setMoneyCell(monthlyTargetEl, m.mtdT, hasMonthlyPlan);
        setDiffCell(monthlyDiffEl, m.mtdA, m.mtdT, hasMonthlyPlan);
        setAchWidget(widgets.monthlyAch, m.mtdA, m.mtdT, hasMonthlyPlan);
        setMoneyCell(annualSalesEl, m.ytdA, hasMonthlyPlan);
        setMoneyCell(annualTargetEl, m.ytdT, hasMonthlyPlan);
        setDiffCell(annualDiffEl, m.ytdA, m.ytdT, hasMonthlyPlan);
        setAchWidget(widgets.annualAch, m.ytdA, m.ytdT, hasMonthlyPlan);
      }}
      window.refreshArea1Cockpit = refreshArea1Cockpit;
      window.refreshArea1KpiStripDiffs = refreshArea1Cockpit;
      function onArea1CockpitRefresh() {{
        refreshArea1Cockpit(resolveArea1Iso());
      }}
      onArea1CockpitRefresh();
      document.addEventListener('annual:dailyDateChanged', onArea1CockpitRefresh);
      document.addEventListener('kpi:selectedDateChanged', onArea1CockpitRefresh);
      document.addEventListener('kpi:dailySalesChanged', onArea1CockpitRefresh);
      document.addEventListener('kpi:annualPlanChanged', onArea1CockpitRefresh);
      document.addEventListener('kpi:mepDataChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:timelineRowsRendered', onArea1CockpitRefresh);
      document.addEventListener('annual:salesMapChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:businessDayMapChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:calendarYearChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:salesDataSaved', onArea1CockpitRefresh);
      document.addEventListener('annual:targetSalesChanged', onArea1CockpitRefresh);
      document.addEventListener('annual:pastSalesSaved', onArea1CockpitRefresh);
      document.addEventListener('kpi:readSurfacesRefresh', onArea1CockpitRefresh);
    }})();
    {COCKPIT_REFRESH_END}"""

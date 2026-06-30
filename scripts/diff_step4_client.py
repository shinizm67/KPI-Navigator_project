"""Difference Step 4 — Area1 KPI strip + MEP surfaces diff severity."""

from __future__ import annotations

DIFF_STEP4_MARKER = "/* KPI-DIFF-STEP4-SEVERITY */"
DIFF_STEP4_END = "/* END KPI-DIFF-STEP4-SEVERITY */"

AREA1_CSS_ANCHOR = """    .office-mode .annual-kpi-value {
      color: #111;
      font-family: 'BIZ UDPGothic', sans-serif;
    }"""

AREA1_CSS_BLOCK = f"""    {DIFF_STEP4_MARKER}
    .annual-kpi-value.tw-diff--win {{
      color: #58e1f3;
    }}
    .annual-kpi-value.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .annual-kpi-value.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .annual-kpi-value.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .annual-kpi-value.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .annual-kpi-value.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .annual-kpi-value.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .annual-kpi-value.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--win {{
      color: #58e1f3;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .memo-float-modal__row-value.tw-diff--win {{
      color: #58e1f3;
    }}
    .memo-float-modal__row-value.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .memo-float-modal__row-value.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .memo-float-modal__row-value.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .memo-float-modal__row-value.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .memo-float-modal__row-value.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .memo-float-modal__row-value.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .memo-float-modal__row-value.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .office-mode .annual-kpi-value.tw-diff--win,
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--win,
    .office-mode .memo-float-modal__row-value.tw-diff--win {{
      color: #111;
    }}
    .office-mode .annual-kpi-value.tw-diff--neutral,
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--neutral,
    .office-mode .memo-float-modal__row-value.tw-diff--neutral {{
      color: #111;
    }}
    .office-mode .annual-kpi-value.tw-diff--sev-90,
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-90,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-90 {{
      color: #e65100;
    }}
    .office-mode .annual-kpi-value.tw-diff--sev-80,
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-80,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-80 {{
      color: #d84315;
    }}
    .office-mode .annual-kpi-value.tw-diff--sev-70,
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-70,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-70 {{
      color: #c62828;
    }}
    .office-mode .annual-kpi-value.tw-diff--sev-60,
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-60,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-60 {{
      color: #b71c1c;
    }}
    .office-mode .annual-kpi-value.tw-diff--sev-50,
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-50,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-50 {{
      color: #9a0007;
    }}
    .office-mode .annual-kpi-value.tw-diff--sev-below,
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-below,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-below {{
      color: #7f0000;
    }}
    /* END KPI-DIFF-STEP4-CSS */
    .office-mode .annual-kpi-value {{
      color: #111;
      font-family: 'BIZ UDPGothic', sans-serif;
    }}"""

DIFF_STEP4_CSS_END = "/* END KPI-DIFF-STEP4-CSS */"

MEP_KPI_CSS_ANCHOR = """    body.office-mode .monthly-edit-float__kpi-cell-value {
      color: #111;
    }"""

MEP_KPI_CSS_BLOCK = f"""    {DIFF_STEP4_MARKER}
    .monthly-edit-float__kpi-cell-value.tw-diff--win {{
      color: #58e1f3;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .monthly-edit-float__kpi-cell-value.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .memo-float-modal__row-value.tw-diff--win {{
      color: #58e1f3;
    }}
    .memo-float-modal__row-value.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .memo-float-modal__row-value.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .memo-float-modal__row-value.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .memo-float-modal__row-value.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .memo-float-modal__row-value.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .memo-float-modal__row-value.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .memo-float-modal__row-value.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--win,
    .office-mode .memo-float-modal__row-value.tw-diff--win {{
      color: #111;
    }}
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--neutral,
    .office-mode .memo-float-modal__row-value.tw-diff--neutral {{
      color: #111;
    }}
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-90,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-90 {{
      color: #e65100;
    }}
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-80,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-80 {{
      color: #d84315;
    }}
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-70,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-70 {{
      color: #c62828;
    }}
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-60,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-60 {{
      color: #b71c1c;
    }}
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-50,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-50 {{
      color: #9a0007;
    }}
    .office-mode .monthly-edit-float__kpi-cell-value.tw-diff--sev-below,
    .office-mode .memo-float-modal__row-value.tw-diff--sev-below {{
      color: #7f0000;
    }}
    /* END KPI-DIFF-STEP4-CSS */
    body.office-mode .monthly-edit-float__kpi-cell-value {{
      color: #111;
    }}"""


def diff_step4_tw_helpers_js() -> str:
    return """      function ensureTwDiffExports() {
        if (typeof window.__twFmtDiff === 'function') return;
        var isJa = document.documentElement.getAttribute('lang') === 'ja';
        window.__twDiffLevels = [
          'tw-diff--win',
          'tw-diff--neutral',
          'tw-diff--sev-90',
          'tw-diff--sev-80',
          'tw-diff--sev-70',
          'tw-diff--sev-60',
          'tw-diff--sev-50',
          'tw-diff--sev-below',
        ];
        window.__twDiffSeverityClass = function (actual, target) {
          if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) {
            return 'tw-diff--neutral';
          }
          var diff = actual - target;
          if (diff > 0) return 'tw-diff--win';
          if (diff === 0) return 'tw-diff--neutral';
          var ach = (actual / target) * 100;
          if (ach >= 90) return 'tw-diff--sev-90';
          if (ach >= 80) return 'tw-diff--sev-80';
          if (ach >= 70) return 'tw-diff--sev-70';
          if (ach >= 60) return 'tw-diff--sev-60';
          if (ach >= 50) return 'tw-diff--sev-50';
          return 'tw-diff--sev-below';
        };
        window.__twFmtDiff = function (actual, target) {
          if (!Number.isFinite(actual) || !Number.isFinite(target)) return '—';
          var n = actual - target;
          if (n === 0) {
            if (typeof window.__twFmtMoney === 'function') return window.__twFmtMoney(0);
            return isJa ? '¥0' : '$0';
          }
          var r = Math.round(Math.abs(n));
          var body = isJa
            ? '¥' + r.toLocaleString('ja-JP')
            : '$' + r.toLocaleString('en-US');
          return (n > 0 ? '+' : '−') + body;
        };
      }
      function applyTwDiffSurfaceEl(el, actual, target) {
        if (!el) return;
        ensureTwDiffExports();
        var levels = window.__twDiffLevels || [];
        for (var i = 0; i < levels.length; i++) el.classList.remove(levels[i]);
        if (typeof window.__twDiffSeverityClass === 'function') {
          el.classList.add(window.__twDiffSeverityClass(actual, target));
        }
      }
      window.applyTwDiffSurfaceEl = applyTwDiffSurfaceEl;"""


def diff_step4_area1_js() -> str:
    helpers = diff_step4_tw_helpers_js()
    return f"""    {DIFF_STEP4_MARKER}
    (function () {{
{helpers}
      var DASH = '—';
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
      function refreshArea1KpiStripDiffs(iso) {{
        iso = iso || resolveArea1Iso();
        var compute =
          typeof window.__computeTwMetricsForIso === 'function'
            ? window.__computeTwMetricsForIso
            : null;
        var m = compute ? compute(iso) : null;
        var legacyDiff = document.getElementById('annual-difference-value');
        var monthlyDiff = document.getElementById('annual-group5-monthly-cumulative-diff');
        var annualDiff = document.getElementById('annual-group5-annual-cumulative-diff');
        var currentEl = document.getElementById('annual-current-sales-value');
        var dailySalesEl = document.getElementById('annual-group5-sales-value');
        if (!m) {{
          setDiffCell(legacyDiff, NaN, NaN, false);
          setDiffCell(monthlyDiff, NaN, NaN, false);
          setDiffCell(annualDiff, NaN, NaN, false);
          return;
        }}
        if (currentEl && m.hasPlan) currentEl.textContent = fmtArea1Money(m.ytdA);
        if (dailySalesEl && m.isBusinessToday) dailySalesEl.textContent = fmtArea1Money(m.dailySales);
        setDiffCell(legacyDiff, m.ytdA, m.ytdT, m.hasPlan);
        setDiffCell(monthlyDiff, m.mtdA, m.mtdT, m.hasPlan);
        setDiffCell(annualDiff, m.ytdA, m.ytdT, m.hasPlan);
      }}
      window.refreshArea1KpiStripDiffs = refreshArea1KpiStripDiffs;
      refreshArea1KpiStripDiffs();
      document.addEventListener('annual:dailyDateChanged', function () {{
        refreshArea1KpiStripDiffs(resolveArea1Iso());
      }});
      document.addEventListener('kpi:selectedDateChanged', function () {{
        refreshArea1KpiStripDiffs(resolveArea1Iso());
      }});
      document.addEventListener('kpi:dailySalesChanged', function () {{
        refreshArea1KpiStripDiffs(resolveArea1Iso());
      }});
      document.addEventListener('kpi:annualPlanChanged', function () {{
        refreshArea1KpiStripDiffs(resolveArea1Iso());
      }});
      document.addEventListener('kpi:mepDataChanged', function () {{
        refreshArea1KpiStripDiffs(resolveArea1Iso());
      }});
      document.addEventListener('annual:timelineRowsRendered', function () {{
        refreshArea1KpiStripDiffs(resolveArea1Iso());
      }});
    }})();
    {DIFF_STEP4_END}"""

AREA1_LEGACY_IIFE_END_ANCHOR = """    })();
    (function () {
      window.__KPI_DATA_GATEWAY = window.__KPI_DATA_GATEWAY || {"""

MEP_RENDER_KPI_STRIP_DIFF_OLD = """          '<div class="monthly-edit-float__kpi-col">' +
          '<div class="monthly-edit-float__kpi-cell"><div class="monthly-edit-float__kpi-cell-label">' + escapeHtml(labels.annualDiff) + '</div><div class="monthly-edit-float__kpi-cell-value">' + escapeHtml(fmtKpiMoney(kpi.annual.diff)) + '</div></div>' +
          '<div class="monthly-edit-float__kpi-cell"><div class="monthly-edit-float__kpi-cell-label">' + escapeHtml(labels.monthlyDiff) + '</div><div class="monthly-edit-float__kpi-cell-value">' + escapeHtml(fmtKpiMoney(kpi.monthly.diff)) + '</div></div>' +
          '</div>';
      }"""

MEP_RENDER_KPI_STRIP_DIFF_NEW = f"""          '<div class="monthly-edit-float__kpi-col">' +
          '<div class="monthly-edit-float__kpi-cell"><div class="monthly-edit-float__kpi-cell-label">' + escapeHtml(labels.annualDiff) + '</div><div class="monthly-edit-float__kpi-cell-value" id="mep-kpi-annual-diff"></div></div>' +
          '<div class="monthly-edit-float__kpi-cell"><div class="monthly-edit-float__kpi-cell-label">' + escapeHtml(labels.monthlyDiff) + '</div><div class="monthly-edit-float__kpi-cell-value" id="mep-kpi-monthly-diff"></div></div>' +
          '</div>';
        ensureTwDiffExports();
        var annualDiffEl = document.getElementById('mep-kpi-annual-diff');
        var monthlyDiffEl = document.getElementById('mep-kpi-monthly-diff');
        if (annualDiffEl) {{
          annualDiffEl.textContent =
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(kpi.annual.actual, kpi.annual.target)
              : fmtKpiMoney(kpi.annual.diff);
          applyTwDiffSurfaceEl(annualDiffEl, kpi.annual.actual, kpi.annual.target);
        }}
        if (monthlyDiffEl) {{
          monthlyDiffEl.textContent =
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(kpi.monthly.actual, kpi.monthly.target)
              : fmtKpiMoney(kpi.monthly.diff);
          applyTwDiffSurfaceEl(monthlyDiffEl, kpi.monthly.actual, kpi.monthly.target);
        }}
      }}"""

MEP_TW_HELPERS_ANCHOR = """      function renderKpiStrip() {
        if (!kpiStrip) return;"""

MEP_TW_HELPERS_INJECT = f"""{diff_step4_tw_helpers_js()}
      function renderKpiStrip() {{
        if (!kpiStrip) return;"""

MEMO_DIFF_OLD = """        addReadRow(labels.diff, fmtMoney(kpi.diff));"""

MEMO_DIFF_NEW = """        (function () {
          var row = document.createElement('div');
          row.className = 'memo-float-modal__row';
          var lbl = document.createElement('div');
          lbl.className = 'memo-float-modal__row-label';
          lbl.textContent = labels.diff;
          var val = document.createElement('div');
          val.className = 'memo-float-modal__row-value';
          if (typeof window.applyTwDiffSurfaceEl === 'function' && typeof window.__twFmtDiff === 'function') {
            val.textContent = window.__twFmtDiff(kpi.sales, kpi.target);
            window.applyTwDiffSurfaceEl(val, kpi.sales, kpi.target);
          } else {
            val.textContent = fmtMoney(kpi.diff);
          }
          row.appendChild(lbl);
          row.appendChild(val);
          memoFloatDayPanel.appendChild(row);
        })();"""

MEMO_TW_HELPERS_ANCHOR = """      function renderMemoFloatDayPanel() {
        if (!memoFloatDayPanel) return;"""

MEMO_TW_HELPERS_INJECT = f"""{diff_step4_tw_helpers_js()}
      function renderMemoFloatDayPanel() {{
        if (!memoFloatDayPanel) return;"""

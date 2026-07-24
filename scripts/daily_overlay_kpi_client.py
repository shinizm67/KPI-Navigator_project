"""Daily Floating Window (#daily-overlay) — KPI render from TW metrics."""

from __future__ import annotations

DAILY_OVERLAY_KPI_MARKER = "/* KPI-DAILY-OVERLAY-METRICS */"
DAILY_OVERLAY_KPI_END = "/* END KPI-DAILY-OVERLAY-METRICS */"

FILL_OLD = """      function fill(iso) {
        iso = iso || resolveIso();
        dateBtnEl.textContent = fmtDate(iso);
        todayBtnEl.hidden = iso === getTodayIso();
        if (dateInputEl) dateInputEl.value = iso;
      }"""

FILL_WITH_RENDER_OLD = """      function fill(iso) {
        iso = iso || resolveIso();
        dateBtnEl.textContent = fmtDate(iso);
        todayBtnEl.hidden = iso === getTodayIso();
        if (dateInputEl) dateInputEl.value = iso;
        if (typeof window.renderDailyOverlayKpis === 'function') {
          window.renderDailyOverlayKpis(iso);
        }
      }"""

FILL_NEW = """      function fill(iso) {
        iso = iso || resolveIso();
        dateBtnEl.textContent = fmtDate(iso);
        todayBtnEl.hidden = iso === getTodayIso();
        if (dateInputEl) dateInputEl.value = iso;
        try {
          if (typeof window.renderDailyOverlayKpis === 'function') {
            window.renderDailyOverlayKpis(iso);
          }
        } catch (_dailyKpiErr) {}
      }"""

OPEN_OLD = """      function open() {
        lastFocused = document.activeElement;
        selectedIso = resolveIso();
        fill(selectedIso);
        root.hidden = false;
        root.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        btnClose.focus();
      }"""

OPEN_NEW = """      function open() {
        lastFocused = document.activeElement;
        selectedIso = resolveIso();
        root.hidden = false;
        root.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        fill(selectedIso);
        btnClose.focus();
      }"""

OPEN_MONTHLY_OLD = """      function open() {
        lastFocused = document.activeElement;
        selectedIso = resolveIso();
        fill(selectedIso);
        root.hidden = false;
        root.removeAttribute('hidden');
        root.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        var panel = root.querySelector('.daily-overlay__panel');
        if (panel) {
          panel.style.flex = '0 0 auto';
          panel.style.width = '1100px';
          panel.style.maxWidth = 'calc(100vw - 32px)';
          void panel.offsetWidth;
        }
        btnClose.focus();
      }"""

OPEN_MONTHLY_NEW = """      function open() {
        lastFocused = document.activeElement;
        selectedIso = resolveIso();
        root.hidden = false;
        root.removeAttribute('hidden');
        root.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        var panel = root.querySelector('.daily-overlay__panel');
        if (panel) {
          panel.style.flex = '0 0 auto';
          panel.style.width = '1100px';
          panel.style.maxWidth = 'calc(100vw - 32px)';
          void panel.offsetWidth;
        }
        fill(selectedIso);
        btnClose.focus();
      }"""

OVERLAY_LISTENERS_ANCHOR = """      document.addEventListener('annual:dailyDateChanged', function () {
        if (!root.hidden) {
          selectedIso = resolveIso();
          fill(selectedIso);
        }
      });
    })();"""


def daily_overlay_kpi_js() -> str:
    return f"""    {DAILY_OVERLAY_KPI_MARKER}
    (function () {{
      var DASH = '—';

      function fmtOverlayMoney(n) {{
        if (typeof window.__twFmtMoney === 'function') return window.__twFmtMoney(n);
        if (n == null || !isFinite(Number(n))) return DASH;
        var isJa = document.documentElement.getAttribute('lang') === 'ja';
        var v = Math.round(Number(n));
        if (window.KpiCurrency) return KpiCurrency.format(v, {{ round: true }});
        var _isJa = (document.documentElement.lang || '').indexOf('ja') === 0;
        return (_isJa ? '¥' : '$') + Math.round(Number(v)).toLocaleString('en-US');
      }}

      function fmtOverlayDiff(actual, target) {{
        if (typeof window.__twFmtDiff === 'function') return window.__twFmtDiff(actual, target);
        if (!Number.isFinite(actual) || !Number.isFinite(target)) return DASH;
        return fmtOverlayMoney(actual - target);
      }}

      function fmtOverlayAchPct(actual, target) {{
        if (typeof window.__twFmtAchPct === 'function') return window.__twFmtAchPct(actual, target);
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return DASH;
        return Math.round((actual / target) * 100) + '%';
      }}

      function overlayTwDiffLevels() {{
        return (
          window.__twDiffLevels || [
            'tw-diff--win',
            'tw-diff--neutral',
            'tw-diff--sev-90',
            'tw-diff--sev-80',
            'tw-diff--sev-70',
            'tw-diff--sev-60',
            'tw-diff--sev-50',
            'tw-diff--sev-below',
          ]
        );
      }}

      function clearOverlayTwDiffClass(el) {{
        if (!el) return;
        overlayTwDiffLevels().forEach(function (cls) {{
          el.classList.remove(cls);
        }});
      }}

      function applyOverlayTwDiffClass(el, actual, target) {{
        clearOverlayTwDiffClass(el);
        if (!el || typeof window.__twDiffSeverityClass !== 'function') return;
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return;
        el.classList.add(window.__twDiffSeverityClass(actual, target));
      }}

      function setValueBoxes(parent, texts, diffMeta) {{
        if (!parent) return;
        var boxes = parent.querySelectorAll(
          '.daily-overlay__daily-value-box, .daily-overlay__monthly-value-box, .daily-overlay__annual-value-box'
        );
        for (var i = 0; i < boxes.length; i++) {{
          boxes[i].textContent = texts[i] != null ? texts[i] : DASH;
          clearOverlayTwDiffClass(boxes[i]);
          if (
            diffMeta &&
            diffMeta.idx === i &&
            Number.isFinite(diffMeta.actual) &&
            Number.isFinite(diffMeta.target) &&
            diffMeta.target > 0
          ) {{
            applyOverlayTwDiffClass(boxes[i], diffMeta.actual, diffMeta.target);
          }}
        }}
      }}

      function fmtOverlayCount(n) {{
        if (!Number.isFinite(n)) return DASH;
        return String(Math.round(n));
      }}

      function getAchievementMarkerColor(percent) {{
        var p = Number(percent);
        if (!Number.isFinite(p)) return '#E6FF00';
        if (p >= 100) return '#E6FF00';
        if (p >= 90) return '#F9A825';
        if (p >= 80) return '#EF6C00';
        if (p >= 70) return '#E65100';
        if (p >= 60) return '#E53935';
        if (p >= 50) return '#C62828';
        return '#B71C1C';
      }}

      var OVERLAY_GRAPH_W = 523;

      function setOverlayGraph(graphEl, actual, target, hasPlan) {{
        if (!graphEl) return;
        var track = graphEl.querySelector('.daily-overlay__daily-graph-track');
        var rateEl = graphEl.querySelector('.daily-overlay__daily-graph-rate');
        if (!track || !rateEl) return;
        var kpiMarkerX = OVERLAY_GRAPH_W * (2 / 3);
        if (!hasPlan || !Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) {{
          rateEl.textContent = DASH;
          track.style.setProperty('--kpi-x', kpiMarkerX + 'px');
          track.style.setProperty('--kgi-x', '0px');
          track.style.setProperty('--fill-w', '0px');
          track.style.setProperty('--marker-color', '#E6FF00');
          return;
        }}
        var ach = (actual / target) * 100;
        rateEl.textContent = Math.round(ach) + '%';
        var minTailW = OVERLAY_GRAPH_W * 0.10;
        var maxKgiX = OVERLAY_GRAPH_W - minTailW;
        var kgiXRaw = kpiMarkerX * (Math.max(0, ach) / 100);
        var kgiX = Math.max(0, Math.min(maxKgiX, kgiXRaw));
        track.style.setProperty('--kpi-x', kpiMarkerX + 'px');
        track.style.setProperty('--kgi-x', kgiX + 'px');
        track.style.setProperty('--fill-w', kgiX + 'px');
        track.style.setProperty('--marker-color', getAchievementMarkerColor(ach));
      }}

      window.renderDailyOverlayKpis = function (iso) {{
        var root = document.getElementById('daily-overlay');
        if (!root) return;
        var compute =
          typeof window.__computeTwMetricsForIso === 'function'
            ? window.__computeTwMetricsForIso
            : null;
        var m = compute ? compute(iso) : null;
        var dash = DASH;
        var dailyKpi = root.querySelector('.daily-overlay__daily-kpi');
        var monthlyKpi = root.querySelector('.daily-overlay__monthly-kpi');
        var annualG1 = root.querySelector('.daily-overlay__annual-g1');
        var annualG2 = root.querySelector('.daily-overlay__annual-g2');
        var dailyGraph = root.querySelector('.daily-overlay__daily-graph');
        var monthlyGraph = root.querySelector('.daily-overlay__monthly-graph');
        var annualGraph = root.querySelector('.daily-overlay__annual-graph');

        if (!m) {{
          setValueBoxes(dailyKpi, [dash, dash, dash, dash]);
          setValueBoxes(monthlyKpi, [dash, dash, dash, dash, dash, dash]);
          setValueBoxes(annualG1, [dash, dash, dash, dash]);
          setValueBoxes(annualG2, [dash, dash, dash, dash]);
          setOverlayGraph(dailyGraph, NaN, NaN, false);
          setOverlayGraph(monthlyGraph, NaN, NaN, false);
          setOverlayGraph(annualGraph, NaN, NaN, false);
          return;
        }}

        var hasDailyPlan = m.isBusinessToday && m.dailyTarget != null;
        setValueBoxes(
          dailyKpi,
          [
            m.isBusinessToday ? fmtOverlayMoney(m.dailySales) : dash,
            hasDailyPlan ? fmtOverlayMoney(m.dailyTarget) : dash,
            hasDailyPlan ? fmtOverlayDiff(m.dailySales, m.dailyTarget) : dash,
            hasDailyPlan ? fmtOverlayAchPct(m.dailySales, m.dailyTarget) : dash,
          ],
          hasDailyPlan
            ? {{ idx: 2, actual: Number(m.dailySales), target: Number(m.dailyTarget) }}
            : null
        );
        setValueBoxes(
          monthlyKpi,
          [
            fmtOverlayMoney(m.mtdA),
            m.hasPlan ? fmtOverlayMoney(m.mtdT) : dash,
            m.hasPlan ? fmtOverlayDiff(m.mtdA, m.mtdT) : dash,
            m.hasPlan ? fmtOverlayAchPct(m.mtdA, m.mtdT) : dash,
            m.hasPlan && m.monthlyDailyNeed != null ? fmtOverlayMoney(m.monthlyDailyNeed) : dash,
            fmtOverlayCount(m.monthRemainingBD),
          ],
          m.hasPlan && Number.isFinite(Number(m.mtdT)) && Number(m.mtdT) > 0
            ? {{ idx: 2, actual: Number(m.mtdA), target: Number(m.mtdT) }}
            : null
        );
        setValueBoxes(
          annualG1,
          [
            fmtOverlayMoney(m.ytdA),
            m.hasPlan ? fmtOverlayMoney(m.ytdT) : dash,
            m.hasPlan ? fmtOverlayDiff(m.ytdA, m.ytdT) : dash,
            m.hasPlan ? fmtOverlayAchPct(m.ytdA, m.ytdT) : dash,
          ],
          m.hasPlan && Number.isFinite(Number(m.ytdT)) && Number(m.ytdT) > 0
            ? {{ idx: 2, actual: Number(m.ytdA), target: Number(m.ytdT) }}
            : null
        );
        setValueBoxes(annualG2, [
          m.annualTarget != null ? fmtOverlayMoney(m.annualTarget) : dash,
          m.hasPlan && m.annualRemaining != null ? fmtOverlayMoney(m.annualRemaining) : dash,
          fmtOverlayCount(m.yearRemainingBD),
          m.hasPlan && m.annualDailyNeed != null ? fmtOverlayMoney(m.annualDailyNeed) : dash,
        ]);
        setOverlayGraph(dailyGraph, m.dailySales, m.dailyTarget, hasDailyPlan);
        setOverlayGraph(monthlyGraph, m.mtdA, m.mtdT, m.hasPlan);
        setOverlayGraph(annualGraph, m.ytdA, m.ytdT, m.hasPlan);
      }};
    }})();
    {DAILY_OVERLAY_KPI_END}"""


OVERLAY_LISTENERS_NEW = """      document.addEventListener('annual:dailyDateChanged', function () {
        if (!root.hidden) {
          selectedIso = resolveIso();
          fill(selectedIso);
        }
      });
      function refreshDailyOverlayFromStore() {
        if (root.hidden) return;
        fill(selectedIso || resolveIso());
      }
      document.addEventListener('kpi:dailySalesChanged', refreshDailyOverlayFromStore);
      document.addEventListener('kpi:businessDayChanged', refreshDailyOverlayFromStore);
      document.addEventListener('kpi:annualPlanChanged', refreshDailyOverlayFromStore);
      document.addEventListener('annual:salesMapChanged', refreshDailyOverlayFromStore);
      document.addEventListener('annual:salesDataSaved', refreshDailyOverlayFromStore);
      document.addEventListener('annual:pastSalesSaved', refreshDailyOverlayFromStore);
      document.addEventListener('kpi:readSurfacesRefresh', refreshDailyOverlayFromStore);
      document.addEventListener('kpi:dailyTargetModeChanged', refreshDailyOverlayFromStore);
      document.addEventListener('kpi:weekdayBaselineChanged', refreshDailyOverlayFromStore);
    })();"""

OVERLAY_LISTENERS_PRE_115 = """      document.addEventListener('annual:dailyDateChanged', function () {
        if (!root.hidden) {
          selectedIso = resolveIso();
          fill(selectedIso);
        }
      });
      function refreshDailyOverlayFromStore() {
        if (root.hidden) return;
        fill(selectedIso || resolveIso());
      }
      document.addEventListener('kpi:dailySalesChanged', refreshDailyOverlayFromStore);
      document.addEventListener('kpi:businessDayChanged', refreshDailyOverlayFromStore);
      document.addEventListener('kpi:annualPlanChanged', refreshDailyOverlayFromStore);
      document.addEventListener('annual:salesMapChanged', refreshDailyOverlayFromStore);
      document.addEventListener('annual:salesDataSaved', refreshDailyOverlayFromStore);
      document.addEventListener('annual:pastSalesSaved', refreshDailyOverlayFromStore);
      document.addEventListener('kpi:readSurfacesRefresh', refreshDailyOverlayFromStore);
    })();"""

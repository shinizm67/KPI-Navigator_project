"""Focus Bar / Table Window — multi-year timeline scroll (P0 remainder)."""

from __future__ import annotations

TIMELINE_CSS = """
    .annual-daily-row--year-boundary {
      position: relative;
    }
    .annual-daily-row--year-boundary::before {
      content: '';
      position: absolute;
      left: 0;
      right: 0;
      top: 0;
      height: 2px;
      background: rgba(88, 225, 243, 0.55);
      pointer-events: none;
      z-index: 2;
    }
    body.office-mode .annual-daily-row--year-boundary::before {
      background: rgba(15, 148, 3, 0.45);
    }"""

FILL_STATE_HELPERS = """
        var DAILY_DERIVED_KEYS = {
          diff: true,
          ach: true,
          monthlyDiff: true,
          monthlyAch: true,
          annualDiff: true,
          annualAch: true
        };
        function dailyCellMoneyNumber(display, dashToken) {
          if (display === dashToken || display === '—' || display === '-') return NaN;
          var t = String(display || '').trim();
          if (!t) return NaN;
          var n = parseFloat(t.replace(/[¥$,\\s]/g, ''));
          return Number.isFinite(n) ? n : NaN;
        }
        function applyDailyCellFillState(cell, fieldKey, display, isWk, isOy, dashToken) {
          if (!fieldKey) return;
          if (isWk || isOy) {
            cell.removeAttribute('data-fill-state');
            cell.classList.remove('kpi-fill-empty', 'kpi-fill-has');
            return;
          }
          if (DAILY_DERIVED_KEYS[fieldKey]) {
            cell.setAttribute('data-fill-state', 'derived');
            cell.classList.remove('kpi-fill-empty');
            cell.classList.add('kpi-fill-has');
            return;
          }
          var n = dailyCellMoneyNumber(display, dashToken);
          if (!Number.isFinite(n) || n === 0) {
            cell.setAttribute('data-fill-state', 'empty');
            cell.classList.add('kpi-fill-empty');
            cell.classList.remove('kpi-fill-has');
          } else {
            cell.setAttribute('data-fill-state', 'has');
            cell.classList.remove('kpi-fill-empty');
            cell.classList.add('kpi-fill-has');
          }
        }"""


def render_timeline_js(*, with_fill_state: bool) -> str:
    fill_helpers = ""
    sales_cell = "groupBase.appendChild(createCell('sales', !isBusiness || isOutsideYear ? dash : fmtMoney(salesNum)));"
    if with_fill_state:
        fill_helpers = FILL_STATE_HELPERS
        sales_cell = """          var salesDisplay = !isBusiness || isOutsideYear ? dash : fmtMoney(salesNum);
          groupBase.appendChild(createCell('sales', salesDisplay));"""

    return f"""
      function computeFocusTimelineBounds(anchorYear) {{
        anchorYear = Number(anchorYear);
        if (!Number.isFinite(anchorYear)) anchorYear = new Date().getFullYear();
        var minY = anchorYear;
        var maxY = anchorYear;
        var systemYear = new Date().getFullYear();
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var tmap = (daily && daily.targetSalesByDate) || {{}};
        function considerYear(y) {{
          y = Number(y);
          if (!Number.isFinite(y)) return;
          if (y < minY) minY = y;
          if (y > maxY) maxY = y;
        }}
        if (window.KpiYearStore) {{
          KpiYearStore.listYearsWithData().forEach(considerYear);
          considerYear(KpiYearStore.getOperatingYear());
        }}
        Object.keys(tmap).forEach(function (iso) {{
          var m = /^(\\d{{4}})-\\d{{2}}-\\d{{2}}$/.exec(String(iso));
          if (m) considerYear(Number(m[1]));
        }});
        minY = Math.min(minY, anchorYear - 1);
        maxY = Math.max(maxY, anchorYear + 1, systemYear + 1);
        var rangeStart = new Date(minY, 0, 1);
        rangeStart.setDate(rangeStart.getDate() - 14);
        var rangeEnd = new Date(maxY, 11, 31);
        rangeEnd.setDate(rangeEnd.getDate() + 14);
        return {{ rangeStart: rangeStart, rangeEnd: rangeEnd, minYear: minY, maxYear: maxY }};
      }}

      function isTimelineBusinessDay(iso, bmap, isWeekend) {{
        if (Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
        return !isWeekend;
      }}
{fill_helpers}

      function renderAnnualDailyTimeline(anchorYear, opts) {{
        opts = opts || {{}};
        anchorYear = Number(anchorYear);
        if (!Number.isFinite(anchorYear)) anchorYear = new Date().getFullYear();
        var scrollEl = document.getElementById('annual-daily-focus-scroll');
        var prevScroll = opts.preserveScroll && scrollEl ? scrollEl.scrollTop : null;
        var bounds = computeFocusTimelineBounds(anchorYear);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {{}};
        window.__ANNUAL_DATA.calendarYear = anchorYear;
        var daily = window.__ANNUAL_DATA.daily || {{}};
        var tmap = daily.targetSalesByDate || {{}};
        var bmap = daily.businessDayByDate || {{}};
        rowsRoot.innerHTML = '';
        rowsRoot.setAttribute('data-year', String(anchorYear));
        rowsRoot.setAttribute(
          'data-timeline-min-year',
          String(bounds.minYear)
        );
        rowsRoot.setAttribute(
          'data-timeline-max-year',
          String(bounds.maxYear)
        );
        rowsRoot.setAttribute(
          'aria-label',
          isJa
            ? bounds.minYear + '〜' + bounds.maxYear + '年の日次一覧'
            : 'Daily rows ' + bounds.minYear + '–' + bounds.maxYear
        );

        var prevYearMarker = null;
        for (var d = new Date(bounds.rangeStart); d <= bounds.rangeEnd; d.setDate(d.getDate() + 1)) {{
          var iso =
            d.getFullYear() +
            '-' +
            pad2(d.getMonth() + 1) +
            '-' +
            pad2(d.getDate());
          var dow = d.getDay();
          var isWeekend = dow === 0 || dow === 6;
          var isBusiness = isTimelineBusinessDay(iso, bmap, isWeekend);
          var hasSales = Object.prototype.hasOwnProperty.call(tmap, iso);
          var salesNum = hasSales ? Number(tmap[iso]) : NaN;
          if (!Number.isFinite(salesNum)) salesNum = 0;

          var rowYear = d.getFullYear();
          var isOutsideYear = rowYear !== anchorYear;
          var row = document.createElement('div');
          row.className =
            'annual-daily-row' +
            (!isBusiness ? ' annual-daily-row--off' : '') +
            (isOutsideYear ? ' annual-daily-row--outside-year' : '');
          if (d.getMonth() === 0 && d.getDate() === 1 && prevYearMarker !== rowYear) {{
            row.classList.add('annual-daily-row--year-boundary');
            prevYearMarker = rowYear;
          }}
          row.setAttribute('role', 'listitem');
          row.setAttribute('data-iso-date', iso);
          row.setAttribute('data-row-year', String(rowYear));
          row.setAttribute('data-active-year', isOutsideYear ? '0' : '1');

          var dateLabel;
          if (isJa) {{
            dateLabel = d.getMonth() + 1 + '/' + d.getDate() + ' ' + WEEKDAYS_JA[dow];
            if (!isBusiness) dateLabel += ' OFF';
          }} else {{
            dateLabel = d.getMonth() + 1 + '/' + d.getDate() + ' ' + WEEKDAYS_EN[dow];
            if (!isBusiness) dateLabel += ' OFF';
          }}

          var dash = '—';
          function createCell(fieldKey, value, extraClass) {{
            var cell = document.createElement('div');
            cell.className = 'annual-daily-row__cell' + (extraClass ? ' ' + extraClass : '');
            if (fieldKey) {{
              cell.setAttribute('data-field', 'annual.dailyTable.' + iso + '.' + fieldKey);
{('              applyDailyCellFillState(cell, fieldKey, value, !isBusiness, isOutsideYear, dash);' if with_fill_state else '')}
            }}
            cell.textContent = value;
            return cell;
          }}

          var groupBase = document.createElement('div');
          groupBase.className = 'annual-daily-row__group annual-daily-row__group--base';
          groupBase.appendChild(createCell(null, dateLabel, 'annual-daily-row__cell--date'));
{sales_cell}
          groupBase.appendChild(createCell('target', !isBusiness || isOutsideYear ? dash : fmtMoney(salesNum)));
          groupBase.appendChild(createCell('diff', !isBusiness || isOutsideYear ? dash : fmtMoney(0)));
          groupBase.appendChild(createCell('ach', !isBusiness || isOutsideYear ? dash : '100%'));

          var groupMonthly = document.createElement('div');
          groupMonthly.className = 'annual-daily-row__group annual-daily-row__group--monthly';
          groupMonthly.appendChild(createCell('monthlyTarget', !isBusiness || isOutsideYear ? dash : fmtMoney(0)));
          groupMonthly.appendChild(createCell('monthlySales', !isBusiness || isOutsideYear ? dash : fmtMoney(0)));
          groupMonthly.appendChild(createCell('monthlyDiff', !isBusiness || isOutsideYear ? dash : fmtMoney(0)));
          groupMonthly.appendChild(createCell('monthlyAch', !isBusiness || isOutsideYear ? dash : '0%'));

          var groupAnnual = document.createElement('div');
          groupAnnual.className = 'annual-daily-row__group annual-daily-row__group--annual';
          groupAnnual.appendChild(createCell('annualTarget', !isBusiness || isOutsideYear ? dash : fmtMoney(0)));
          groupAnnual.appendChild(createCell('annualSales', !isBusiness || isOutsideYear ? dash : fmtMoney(0)));
          groupAnnual.appendChild(createCell('annualDiff', !isBusiness || isOutsideYear ? dash : fmtMoney(0)));
          groupAnnual.appendChild(createCell('annualAch', !isBusiness || isOutsideYear ? dash : '0%'));

          row.appendChild(groupBase);
          row.appendChild(groupMonthly);
          row.appendChild(groupAnnual);
          rowsRoot.appendChild(row);
        }}

        if (prevScroll != null && scrollEl) {{
          scrollEl.scrollTop = prevScroll;
        }}
        document.dispatchEvent(new CustomEvent('annual:timelineRowsRendered'));
      }}

      function renderAnnualDailyTable(year) {{
        renderAnnualDailyTimeline(year, {{ preserveScroll: false }});
      }}

      window.__renderAnnualDailyTable = renderAnnualDailyTable;
      window.__renderAnnualDailyTimeline = renderAnnualDailyTimeline;

      document.addEventListener('annual:calendarYearChanged', function (ev) {{
        if (ev.detail && ev.detail.skipTableRender) return;
        var y = ev.detail && ev.detail.year;
        if (y != null) renderAnnualDailyTable(Number(y));
      }});
      document.addEventListener('annual:businessDayMapChanged', function () {{
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, {{ preserveScroll: true }});
      }});
      document.addEventListener('annual:salesMapChanged', function () {{
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, {{ preserveScroll: true }});
      }});
"""

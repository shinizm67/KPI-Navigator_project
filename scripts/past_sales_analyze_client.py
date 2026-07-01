"""Past Sales Analyze tab — KPI table, seasonality chart, render hooks."""

from __future__ import annotations

PATCH_MARKER = "psm-analyze-v1"

CSS_VARS_OLD = """      --psm-scrollbar-w: 8px;"""

CSS_VARS_NEW = f"""      --psm-analyze-table-chart-gap: 100px;
      --psm-season-pad-top: 37px;
      --psm-season-title-fs: 23px;
      --psm-season-title-to-bar: 54px;
      --psm-season-row-gap: 48px;
      --psm-season-bar-w: 654px;
      --psm-season-bar-h: 20px;
      --psm-season-fill: #0f9403;
      --psm-season-label-gap-l: 30px;
      --psm-season-label-gap-r: 50px;
      --psm-season-baseline-rim: 2px;
      --psm-season-baseline-bar: 4px;
      --psm-season-pad-bottom: 95px;
      --psm-season-gap-to-outer: 150px;
      --psm-scrollbar-w: 8px;"""

CSS_BLOCK_OLD = """    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-cell--month {
      display: none;
    }
    body.office-mode .past-sales-modal__panel {"""

CSS_BLOCK_NEW = f"""    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym-cell--month {{
      display: none;
    }}
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym {{
      grid-template-columns: 1fr;
      flex-shrink: 0;
    }}
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__csv,
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__undo,
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__save {{
      display: none !important;
    }}
    .past-sales-modal__analyze-scroll {{
      flex: 1;
      min-height: 0;
      overflow: auto;
      padding: 0;
      font-size: var(--psm-fs-body);
      color: var(--psm-cyan);
      background: transparent;
      border: 0;
      box-sizing: border-box;
    }}
    .past-sales-modal__analyze-stack {{
      display: flex;
      flex-direction: column;
      align-items: stretch;
      width: 100%;
      box-sizing: border-box;
      padding: 0;
    }}
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__analyze-data {{
      border-top: 0;
    }}
    .past-sales-modal__analyze-data {{
      border: 1px solid var(--psm-line);
      background: var(--psm-bg-inactive);
      box-sizing: border-box;
      width: 100%;
    }}
    .past-sales-modal__analyze-kpi {{
      display: grid;
      border-bottom: 1px solid var(--psm-line);
      min-height: var(--psm-summary-row-h);
      align-items: stretch;
    }}
    .past-sales-modal__analyze-kpi--2 {{
      grid-template-columns: minmax(0, 5fr) minmax(0, 5fr);
    }}
    .past-sales-modal__analyze-kpi--4 {{
      grid-template-columns: minmax(0, 3fr) minmax(0, 2fr) minmax(0, 3fr) minmax(0, 2fr);
    }}
    .past-sales-modal__analyze-kpi-label,
    .past-sales-modal__analyze-kpi-value {{
      margin: 0;
      padding: 0 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      font-size: var(--psm-fs-body);
      border-right: 1px solid var(--psm-line);
      box-sizing: border-box;
      min-height: var(--psm-summary-row-h);
      font-variant-numeric: tabular-nums;
    }}
    .past-sales-modal__analyze-kpi-value {{
      border-right: 0;
      font-weight: 600;
    }}
    .past-sales-modal__analyze-kpi--4 .past-sales-modal__analyze-kpi-label:nth-child(3),
    .past-sales-modal__analyze-kpi--4 .past-sales-modal__analyze-kpi-value:nth-child(4) {{
      border-right: 0;
    }}
    .past-sales-modal__analyze-kpi--4 .past-sales-modal__analyze-kpi-value:nth-child(2) {{
      border-right: 1px solid var(--psm-line);
    }}
    .past-sales-modal__analyze-table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      font-size: var(--psm-fs-body);
    }}
    .past-sales-modal__analyze-table th:nth-child(1),
    .past-sales-modal__analyze-table td:nth-child(1) {{
      width: 16%;
    }}
    .past-sales-modal__analyze-table th:nth-child(2),
    .past-sales-modal__analyze-table td:nth-child(2) {{
      width: 16%;
    }}
    .past-sales-modal__analyze-table th:nth-child(3),
    .past-sales-modal__analyze-table td:nth-child(3) {{
      width: 25%;
    }}
    .past-sales-modal__analyze-table th:nth-child(4),
    .past-sales-modal__analyze-table td:nth-child(4) {{
      width: 25%;
    }}
    .past-sales-modal__analyze-table th:nth-child(5),
    .past-sales-modal__analyze-table td:nth-child(5) {{
      width: 18%;
    }}
    .past-sales-modal__analyze-table th,
    .past-sales-modal__analyze-table td {{
      border: 1px solid var(--psm-line);
      padding: 8px 6px;
      text-align: center;
      vertical-align: middle;
      box-sizing: border-box;
      font-variant-numeric: tabular-nums;
    }}
    .past-sales-modal__analyze-table thead th {{
      background: var(--psm-bg-active-55);
      font-weight: 700;
      font-size: var(--psm-fs-colhead);
    }}
    .past-sales-modal__analyze-table tbody td {{
      background: var(--psm-bg-inactive);
    }}
    .past-sales-modal__analyze-table tbody td:nth-child(n + 3) {{
      text-align: right;
      padding-right: 10px;
    }}
    .past-sales-modal__analyze-table tbody td:first-child {{
      font-weight: 600;
    }}
    .past-sales-modal__seasonality {{
      margin-top: var(--psm-analyze-table-chart-gap, 100px);
      margin-bottom: var(--psm-season-gap-to-outer);
      padding: var(--psm-season-pad-top) 0 var(--psm-season-pad-bottom);
      border: 2px solid #3dff3d;
      background: rgba(0, 0, 0, 0.22);
      box-sizing: border-box;
      width: 100%;
    }}
    .past-sales-modal__seasonality-title {{
      margin: 0 0 var(--psm-season-title-to-bar);
      text-align: center;
      font-size: var(--psm-season-title-fs);
      font-weight: 700;
      letter-spacing: 0.04em;
      line-height: 1.2;
    }}
    #past-sales-seasonality-bars {{
      display: flex;
      flex-direction: column;
      align-items: stretch;
      width: 100%;
      box-sizing: border-box;
    }}
    .past-sales-modal__season-row {{
      display: grid;
      grid-template-columns: minmax(44px, 10.1%) minmax(0, 1fr) minmax(72px, 10.1%);
      align-items: center;
      width: 100%;
      margin: 0 0 var(--psm-season-row-gap);
      min-height: var(--psm-season-bar-h);
    }}
    .past-sales-modal__season-row:last-child {{
      margin-bottom: 0;
    }}
    .past-sales-modal__season-month {{
      margin: 0 var(--psm-season-label-gap-l) 0 0;
      font-size: var(--psm-fs-body);
      font-weight: 600;
      text-align: right;
      white-space: nowrap;
    }}
    .past-sales-modal__season-track {{
      position: relative;
      width: 100%;
      height: var(--psm-season-bar-h);
      margin-right: var(--psm-season-label-gap-r);
      background: rgba(88, 225, 243, 0.12);
      border: 1px solid rgba(88, 225, 243, 0.35);
      box-sizing: border-box;
      overflow: visible;
    }}
    .past-sales-modal__season-baseline-slot {{
      position: absolute;
      top: 0;
      left: 0;
      display: flex;
      flex-direction: row;
      align-items: stretch;
      width: calc(var(--psm-season-baseline-rim) * 2 + var(--psm-season-baseline-bar));
      height: var(--psm-season-bar-h);
      transform: translateX(-50%);
      z-index: 2;
      pointer-events: none;
    }}
    .past-sales-modal__season-baseline-rim {{
      flex: 0 0 var(--psm-season-baseline-rim);
      width: var(--psm-season-baseline-rim);
      height: 100%;
      background: transparent;
    }}
    .past-sales-modal__season-baseline-bar {{
      flex: 0 0 var(--psm-season-baseline-bar);
      width: var(--psm-season-baseline-bar);
      height: 100%;
      background: #ffe600;
      box-shadow: 0 0 6px rgba(255, 230, 0, 0.65);
    }}
    .past-sales-modal__season-fill {{
      position: absolute;
      left: 0;
      top: 0;
      height: var(--psm-season-bar-h);
      background: var(--psm-season-fill);
      z-index: 1;
      max-width: 100%;
      box-sizing: border-box;
    }}
    .past-sales-modal__season-marker {{
      position: absolute;
      top: -9px;
      width: 0;
      height: 0;
      margin-left: -6px;
      border-left: 6px solid transparent;
      border-right: 6px solid transparent;
      border-top: 8px solid #ffe600;
      z-index: 3;
      pointer-events: none;
      filter: drop-shadow(0 0 4px rgba(255, 230, 0, 0.8));
    }}
    .past-sales-modal__season-pct {{
      margin: 0;
      font-size: var(--psm-fs-body);
      font-weight: 600;
      text-align: left;
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }}
    body.office-mode .past-sales-modal__seasonality {{
      border-color: #2b6cb0;
      background: rgba(255, 255, 255, 0.45);
    }}
    body.office-mode .past-sales-modal__season-fill {{
      background: linear-gradient(90deg, #2b6cb0 0%, #4a90d9 100%);
    }}
    body.office-mode .past-sales-modal__season-baseline-bar {{
      background: #c9a000;
      box-shadow: none;
    }}
    body.office-mode .past-sales-modal__season-marker {{
      border-top-color: #c9a000;
    }}
    body.office-mode .past-sales-modal__panel {{"""

HTML_OLD_JA = """        <div class="past-sales-modal__analyze-scroll" id="past-sales-pane-analyze" hidden>
          <p>Analyze（準備中）</p>
        </div>"""

HTML_OLD_EN = """        <div class="past-sales-modal__analyze-scroll" id="past-sales-pane-analyze" hidden>
          <p>Analyze (coming soon)</p>
        </div>"""

HTML_JA = """        <div class="past-sales-modal__analyze-scroll" id="past-sales-pane-analyze" hidden>
          <div class="past-sales-modal__analyze-stack">
            <div class="past-sales-modal__analyze-data">
              <div class="past-sales-modal__analyze-kpi past-sales-modal__analyze-kpi--2">
                <p class="past-sales-modal__analyze-kpi-label">年間入力売上</p>
                <p class="past-sales-modal__analyze-kpi-value" id="past-sales-analyze-input-sales">—</p>
              </div>
              <div class="past-sales-modal__analyze-kpi past-sales-modal__analyze-kpi--4">
                <p class="past-sales-modal__analyze-kpi-label">総営業日数</p>
                <p class="past-sales-modal__analyze-kpi-value" id="past-sales-analyze-total-bd">—</p>
                <p class="past-sales-modal__analyze-kpi-label">平均日次売上</p>
                <p class="past-sales-modal__analyze-kpi-value" id="past-sales-analyze-avg-daily">—</p>
              </div>
              <table class="past-sales-modal__analyze-table" aria-label="月次繁閑分析">
                <thead>
                  <tr>
                    <th scope="col">月</th>
                    <th scope="col">B. DAY</th>
                    <th scope="col">月次売上</th>
                    <th scope="col">基準月次売上</th>
                    <th scope="col">繁閑期%</th>
                  </tr>
                </thead>
                <tbody id="past-sales-analyze-table-body"></tbody>
              </table>
            </div>
            <section class="past-sales-modal__seasonality" aria-label="月次繁閑期グラフ">
              <h3 class="past-sales-modal__seasonality-title">月次繁閑期%</h3>
              <div id="past-sales-seasonality-bars"></div>
            </section>
          </div>
        </div>"""

HTML_EN = """        <div class="past-sales-modal__analyze-scroll" id="past-sales-pane-analyze" hidden>
          <div class="past-sales-modal__analyze-stack">
            <div class="past-sales-modal__analyze-data">
              <div class="past-sales-modal__analyze-kpi past-sales-modal__analyze-kpi--2">
                <p class="past-sales-modal__analyze-kpi-label">Annual Input Sales</p>
                <p class="past-sales-modal__analyze-kpi-value" id="past-sales-analyze-input-sales">—</p>
              </div>
              <div class="past-sales-modal__analyze-kpi past-sales-modal__analyze-kpi--4">
                <p class="past-sales-modal__analyze-kpi-label">Total Business Days</p>
                <p class="past-sales-modal__analyze-kpi-value" id="past-sales-analyze-total-bd">—</p>
                <p class="past-sales-modal__analyze-kpi-label">Average Daily Sales</p>
                <p class="past-sales-modal__analyze-kpi-value" id="past-sales-analyze-avg-daily">—</p>
              </div>
              <table class="past-sales-modal__analyze-table" aria-label="Monthly seasonality analysis">
                <thead>
                  <tr>
                    <th scope="col">Month</th>
                    <th scope="col">B. DAY</th>
                    <th scope="col">Monthly Sales</th>
                    <th scope="col">Baseline Monthly Sales</th>
                    <th scope="col">Seasonality %</th>
                  </tr>
                </thead>
                <tbody id="past-sales-analyze-table-body"></tbody>
              </table>
            </div>
            <section class="past-sales-modal__seasonality" aria-label="Monthly seasonality chart">
              <h3 class="past-sales-modal__seasonality-title">Monthly Seasonality %</h3>
              <div id="past-sales-seasonality-bars"></div>
            </section>
          </div>
        </div>"""

YM_HTML_OLD = """        <div class="past-sales-modal__ym past-sales-modal__input-only">"""

YM_HTML_NEW = """        <div class="past-sales-modal__ym">"""

STATE_OLD = """      var state = {
        year: 2026,
        viewMonth: 0,
        rowStateByIso: {},
        salesPinnedAmount: null,
        salesAmountSort: null,
        modalDirty: false
      };"""

STATE_NEW = """      var state = {
        year: 2026,
        viewMonth: 0,
        rowStateByIso: {},
        salesPinnedAmount: null,
        salesAmountSort: null,
        modalDirty: false,
        activeTab: 'input'
      };"""

VARS_OLD = """      var summaryPctEl = document.getElementById('past-sales-summary-progress-pct');

      if (!modal || !modalTable || !openBtn) return;"""

VARS_NEW = """      var summaryPctEl = document.getElementById('past-sales-summary-progress-pct');
      var analyzeInputSalesEl = document.getElementById('past-sales-analyze-input-sales');
      var analyzeTotalBdEl = document.getElementById('past-sales-analyze-total-bd');
      var analyzeAvgDailyEl = document.getElementById('past-sales-analyze-avg-daily');
      var analyzeTableBody = document.getElementById('past-sales-analyze-table-body');
      var seasonalityBarsEl = document.getElementById('past-sales-seasonality-bars');
      var MONTHS_SHORT_EN = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];

      if (!modal || !modalTable || !openBtn) return;"""

RENDER_OLD = """      function renderPastSalesAnalyze() {
        /* PS-1 placeholder */
      }"""

RENDER_NEW = f"""      function formatAnalyzeMoney(n) {{
        if (n == null || !isFinite(Number(n))) return '—';
        var v = Math.round(Number(n) * 100) / 100;
        if (isJa) {{
          return '¥' + v.toLocaleString('ja-JP', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
        }}
        return '$' + v.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
      }}

      function formatSeasonalityPct(n) {{
        if (n == null || !isFinite(Number(n))) return '—';
        return (Math.round(Number(n) * 100) / 100).toFixed(2) + '%';
      }}

      function monthLabelShort(m0) {{
        if (isJa) return MONTHS_JA[m0] || String(m0 + 1);
        return MONTHS_SHORT_EN[m0] || String(m0 + 1);
      }}

      function getReferenceAnnualForAnalyze(y) {{
        var fromInput = getReferenceFromInputEl();
        if (fromInput != null) return fromInput;
        return getReferenceForYear(y);
      }}

      function getHlWeightsForPastSalesAnalyze(y) {{
        if (window.KpiYearStore && typeof KpiYearStore.readMonthlyHlWeights === 'function') {{
          var fromStore = KpiYearStore.readMonthlyHlWeights(y);
          if (fromStore && fromStore.length === 12) return fromStore.slice();
        }}
        return [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100];
      }}

      function getMonthlyCumulativeSalesByMonth(y) {{
        var totalsMap = buildPastSalesTotalsMap(y);
        var all = gatherYearDays(y);
        var sales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        for (var i = 0; i < all.length; i++) {{
          var item = all[i];
          var entry = totalsMap[item.iso];
          if (!entry || entry.off || entry.monthly == null || !isFinite(entry.monthly)) continue;
          sales[item.m0] = entry.monthly;
        }}
        return sales;
      }}

      function getSeasonalityChartScale(months) {{
        var peak = 0;
        for (var si = 0; si < months.length; si++) {{
          var sv = months[si].seasonality;
          if (sv != null && isFinite(sv) && sv > peak) peak = sv;
        }}
        var scaleMax = peak > 0 ? Math.max(peak, 100) : 100;
        return {{ scaleMax: scaleMax, baselinePct: (100 / scaleMax) * 100 }};
      }}

      function buildPastSalesAnalyzeModel(y) {{
        var all = gatherYearDays(y);
        var annualTarget = getReferenceAnnualForAnalyze(y);
        var monthlySales = getMonthlyCumulativeSalesByMonth(y);
        var hlWeights = getHlWeightsForPastSalesAnalyze(y);
        var totalBD = 0;
        var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        for (var i = 0; i < all.length; i++) {{
          var item = all[i];
          var defs = getRowDefaults(item.iso, item.isWk);
          if (!defs.off) {{
            totalBD++;
            monthlyBD[item.m0]++;
          }}
        }}
        var avgDaily = annualTarget != null && totalBD > 0 ? annualTarget / totalBD : null;
        var cumulativeInput = getCumulativeInputAnnualTotal(y);
        var months = [];
        for (var m0 = 0; m0 < 12; m0++) {{
          var w = Number(hlWeights[m0]);
          if (!isFinite(w)) w = 100;
          var baseline =
            avgDaily != null && monthlyBD[m0] > 0 ? avgDaily * monthlyBD[m0] * (w / 100) : null;
          var sales = monthlySales[m0];
          var seasonality = baseline != null && baseline > 0 ? (sales / baseline) * 100 : null;
          months.push({{
            m0: m0,
            bd: monthlyBD[m0],
            sales: sales,
            baseline: baseline,
            seasonality: seasonality
          }});
        }}
        return {{
          year: y,
          annualTarget: annualTarget,
          cumulativeInput: cumulativeInput,
          totalBD: totalBD,
          avgDaily: avgDaily,
          months: months
        }};
      }}

      function renderPastSalesAnalyze() {{
        var y = state.year;
        if (!isFinite(y) && yearSelect) y = Number(yearSelect.value);
        if (!isFinite(y)) return;
        var model = buildPastSalesAnalyzeModel(y);
        if (analyzeInputSalesEl) {{
          analyzeInputSalesEl.textContent =
            model.cumulativeInput != null ? formatAnalyzeMoney(model.cumulativeInput) : '—';
        }}
        if (analyzeTotalBdEl) {{
          analyzeTotalBdEl.textContent = model.totalBD > 0 ? String(model.totalBD) : '—';
        }}
        if (analyzeAvgDailyEl) {{
          analyzeAvgDailyEl.textContent =
            model.avgDaily != null ? formatAnalyzeMoney(model.avgDaily) : '—';
        }}
        if (analyzeTableBody) {{
          while (analyzeTableBody.firstChild) analyzeTableBody.removeChild(analyzeTableBody.firstChild);
          for (var mi = 0; mi < model.months.length; mi++) {{
            var row = model.months[mi];
            var tr = document.createElement('tr');
            var td0 = document.createElement('td');
            td0.textContent = monthLabelShort(row.m0);
            var td1 = document.createElement('td');
            td1.textContent = String(row.bd);
            var td2 = document.createElement('td');
            td2.textContent = row.bd > 0 ? formatAnalyzeMoney(row.sales) : '—';
            var td3 = document.createElement('td');
            td3.textContent = row.baseline != null ? formatAnalyzeMoney(row.baseline) : '—';
            var td4 = document.createElement('td');
            td4.textContent = formatSeasonalityPct(row.seasonality);
            tr.appendChild(td0);
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            tr.appendChild(td4);
            analyzeTableBody.appendChild(tr);
          }}
        }}
        if (seasonalityBarsEl) {{
          var barsHtml = '';
          var chartScale = getSeasonalityChartScale(model.months);
          var baselineLeft = chartScale.baselinePct;
          var seasonScaleMax = chartScale.scaleMax;
          for (var bi = 0; bi < model.months.length; bi++) {{
            var bm = model.months[bi];
            var fillW = 0;
            if (bm.seasonality != null && isFinite(bm.seasonality) && seasonScaleMax > 0) {{
              fillW = (bm.seasonality / seasonScaleMax) * 100;
              if (fillW < 0) fillW = 0;
              if (fillW > 100) fillW = 100;
            }}
            var markerLeft = fillW;
            barsHtml +=
              '<div class="past-sales-modal__season-row">' +
              '<span class="past-sales-modal__season-month">' +
              monthLabelShort(bm.m0) +
              '</span>' +
              '<div class="past-sales-modal__season-track">' +
              '<div class="past-sales-modal__season-baseline-slot" style="left:' +
              baselineLeft +
              '%">' +
              '<span class="past-sales-modal__season-baseline-rim" aria-hidden="true"></span>' +
              '<span class="past-sales-modal__season-baseline-bar" aria-hidden="true"></span>' +
              '<span class="past-sales-modal__season-baseline-rim" aria-hidden="true"></span>' +
              '</div>' +
              '<div class="past-sales-modal__season-fill" style="width:' +
              fillW +
              '%"></div>' +
              '<div class="past-sales-modal__season-marker" style="left:' +
              markerLeft +
              '%"></div>' +
              '</div>' +
              '<span class="past-sales-modal__season-pct">' +
              formatSeasonalityPct(bm.seasonality) +
              '</span>' +
              '</div>';
          }}
          seasonalityBarsEl.innerHTML = barsHtml;
        }}
      }}"""

SET_TAB_OLD = """      function setPastSalesTab(tab) {
        var t = tab === 'analyze' ? 'analyze' : 'input';
        var panel = modal.querySelector('.past-sales-modal__panel');
        var body = document.getElementById('past-sales-modal-body');
        if (panel) panel.setAttribute('data-psm-tab', t);
        if (body) body.setAttribute('data-psm-tab', t);
        var tabInput = document.getElementById('past-sales-tab-input');
        var tabAnalyze = document.getElementById('past-sales-tab-analyze');
        if (tabInput) {
          tabInput.classList.toggle('is-active', t === 'input');
          tabInput.setAttribute('aria-selected', t === 'input' ? 'true' : 'false');
        }
        if (tabAnalyze) {
          tabAnalyze.classList.toggle('is-active', t === 'analyze');
          tabAnalyze.setAttribute('aria-selected', t === 'analyze' ? 'true' : 'false');
        }
        var paneAnalyze = document.getElementById('past-sales-pane-analyze');
        if (paneAnalyze) paneAnalyze.hidden = t !== 'analyze';
      }"""

SET_TAB_NEW = """      function setPastSalesTab(tab) {
        var t = tab === 'analyze' ? 'analyze' : 'input';
        state.activeTab = t;
        var panel = modal.querySelector('.past-sales-modal__panel');
        var body = document.getElementById('past-sales-modal-body');
        if (panel) panel.setAttribute('data-psm-tab', t);
        if (body) body.setAttribute('data-psm-tab', t);
        var tabInput = document.getElementById('past-sales-tab-input');
        var tabAnalyze = document.getElementById('past-sales-tab-analyze');
        if (tabInput) {
          tabInput.classList.toggle('is-active', t === 'input');
          tabInput.setAttribute('aria-selected', t === 'input' ? 'true' : 'false');
        }
        if (tabAnalyze) {
          tabAnalyze.classList.toggle('is-active', t === 'analyze');
          tabAnalyze.setAttribute('aria-selected', t === 'analyze' ? 'true' : 'false');
        }
        var paneAnalyze = document.getElementById('past-sales-pane-analyze');
        if (paneAnalyze) paneAnalyze.hidden = t !== 'analyze';
        if (t === 'analyze') renderPastSalesAnalyze();
      }"""

SUMMARY_OLD = """            summaryPctEl.textContent = pct + '%';
          }
        }
      }

      function renderPastSalesAnalyze() {"""

SUMMARY_NEW = """            summaryPctEl.textContent = pct + '%';
          }
        }
        if (state.activeTab === 'analyze') renderPastSalesAnalyze();
      }

      function renderPastSalesAnalyze() {"""

# Remove duplicate analyze-scroll block that conflicts with new styles
CSS_SCROLL_DUP_OLD = """    .past-sales-modal__analyze-scroll {
      flex: 1;
      min-height: 0;
      overflow: auto;
      padding: 24px;
      font-size: var(--psm-fs-body);
      color: var(--psm-cyan);
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__input-only {"""

CSS_SCROLL_DUP_NEW = """    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__input-only {"""

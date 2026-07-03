"""Sales Data Analyze — H/L Season% stepper (▲▼) UI."""

from __future__ import annotations

SDM_HL_STEPPER_MARKER = "/* KPI-SDM-HL-STEPPER-JS */"
SDM_HL_STEPPER_END = "/* END KPI-SDM-HL-STEPPER-JS */"

SDM_HL_STEPPER_CSS_OLD = """    .sales-data-modal__analyze-hl-input {
      display: block;
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
      margin: 0;
      padding: 4px 2px;
      border: 0;
      background: transparent;
      color: var(--sdm-cyan);
      font: inherit;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      text-align: center;
    }
    .sales-data-modal__analyze-hl-input:focus {
      outline: 1px solid var(--sdm-cyan);
      outline-offset: 1px;
    }"""

SDM_HL_STEPPER_CSS_NEW = """    .sales-data-modal__analyze-hl-stepper {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 3px;
      width: 100%;
      box-sizing: border-box;
    }
    .sales-data-modal__analyze-hl-step {
      flex: 0 0 auto;
      width: 24px;
      height: 22px;
      margin: 0;
      padding: 0;
      border: 1px solid rgba(88, 225, 243, 0.45);
      border-radius: 2px;
      background: rgba(0, 0, 0, 0.25);
      color: var(--sdm-cyan);
      font-size: 10px;
      line-height: 1;
      cursor: pointer;
      box-sizing: border-box;
    }
    .sales-data-modal__analyze-hl-step:hover:not(:disabled),
    .sales-data-modal__analyze-hl-step:focus-visible:not(:disabled) {
      background: rgba(88, 225, 243, 0.28);
      outline: none;
    }
    .sales-data-modal__analyze-hl-step:disabled {
      opacity: 0.35;
      cursor: default;
    }
    .sales-data-modal__analyze-hl-value {
      flex: 1 1 auto;
      min-width: 42px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      text-align: center;
    }
    .sales-data-modal__analyze-alloc-total--warn {
      color: #ff7070;
      font-weight: 800;
    }
    body.office-mode .sales-data-modal__analyze-alloc-total--warn {
      color: #c62828;
    }"""

STORE_DEFAULTS_OLD = """          if (existing && existing.length === 12) return;

          var prev = store.years[oy - 1];
          if (
            prev &&
            prev.plan &&
            prev.plan.monthlyHlWeights &&
            prev.plan.monthlyHlWeights.length === 12
          ) {
            rec.plan.monthlyHlWeights = prev.plan.monthlyHlWeights.slice();
          } else {
            rec.plan.monthlyHlWeights = DEFAULT_HL_WEIGHTS.slice();
          }
          rec.plan.updatedAt = Date.now();
          rec.plan.hlSource = 'plan-default';
          persistStore();"""

STORE_DEFAULTS_NEW = """          if (existing && existing.length === 12) return;

          rec.plan.monthlyHlWeights = [
            100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
          ];
          rec.plan.updatedAt = Date.now();
          rec.plan.hlSource = 'plan-default';
          persistStore();"""

OPEN_MODAL_OLD = """          sessionSaved = false;
          undoStack = [];"""

OPEN_MODAL_NEW = """          sessionSaved = false;
          sdmHlAllocWarnShown = false;
          undoStack = [];"""

RENDER_ALLOC_OLD = """          updateSdmAllocTotalDisplay(hlWeights);
        }
        if (seasonalityBarsEl) {"""

RENDER_ALLOC_NEW = """          updateSdmAllocTotalDisplay(hlWeights);
          maybeAlertSdmAllocTotal(hlWeights);
        }
        if (seasonalityBarsEl) {"""

SDM_HL_TIP_CSS_OLD = """    .sales-data-modal__analyze-hl-tip:hover::after,
    .sales-data-modal__analyze-hl-tip:focus-within::after {
      content: attr(data-hl-tip);
      position: absolute;
      z-index: 20;
      right: 6px;
      bottom: calc(100% + 6px);
      width: max-content;
      max-width: 220px;
      padding: 8px 10px;
      border: 1px solid var(--sdm-cyan);
      background: rgba(0, 0, 0, 0.92);
      color: var(--sdm-cyan);
      font-size: 12px;
      font-weight: 600;
      line-height: 1.35;
      text-align: left;
      white-space: normal;
      pointer-events: none;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45);
    }
    .sales-data-modal__analyze-hl-tip--footer:hover::after,
    .sales-data-modal__analyze-hl-tip--footer:focus-within::after {
      max-width: 280px;
    }
    .sales-data-modal__analyze-table tfoot td.sales-data-modal__analyze-hl-tip--footer {
      position: relative;
    }"""

SDM_HL_TIP_CSS_NEW = """    .sales-data-modal__analyze-hl-head-tip {
      position: relative;
      cursor: help;
    }
    .sales-data-modal__analyze-hl-head-tip:hover::after {
      content: attr(data-hl-tip);
      position: absolute;
      z-index: 20;
      left: 50%;
      bottom: calc(100% + 4px);
      transform: translateX(-50%);
      width: max-content;
      max-width: 180px;
      padding: 5px 8px;
      border: 1px solid var(--sdm-cyan);
      background: rgba(0, 0, 0, 0.92);
      color: var(--sdm-cyan);
      font-size: 11px;
      font-weight: 600;
      line-height: 1.3;
      text-align: center;
      white-space: normal;
      pointer-events: none;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45);
    }
    .sales-data-modal__analyze-hl-tip--footer {
      position: relative;
      cursor: help;
    }
    .sales-data-modal__analyze-hl-tip--footer:hover::after {
      content: attr(data-hl-tip);
      position: absolute;
      z-index: 20;
      right: 6px;
      bottom: calc(100% + 4px);
      width: max-content;
      max-width: 180px;
      padding: 5px 8px;
      border: 1px solid var(--sdm-cyan);
      background: rgba(0, 0, 0, 0.92);
      color: var(--sdm-cyan);
      font-size: 11px;
      font-weight: 600;
      line-height: 1.3;
      text-align: center;
      white-space: normal;
      pointer-events: none;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45);
    }"""

RENDER_TARGET_OLD = """          var hlWeights = getSdmHlWeightsForYear(planYear);
          while (analyzeTableBody.firstChild) analyzeTableBody.removeChild(analyzeTableBody.firstChild);
          for (var mi = 0; mi < model.months.length; mi++) {
            var row = model.months[mi];
            var tr = document.createElement('tr');
            var td0 = document.createElement('td');
            td0.textContent = monthLabelShort(row.m0);
            var td1 = document.createElement('td');
            td1.textContent = String(row.bd);
            var td2 = document.createElement('td');
            td2.textContent = row.bd > 0 ? formatAnalyzeMoney(row.sales) : '—';"""

RENDER_TARGET_NEW = """          var hlWeights = getSdmHlWeightsForYear(planYear);
          while (analyzeTableBody.firstChild) analyzeTableBody.removeChild(analyzeTableBody.firstChild);
          for (var mi = 0; mi < model.months.length; mi++) {
            var row = model.months[mi];
            var tr = document.createElement('tr');
            if (row.baseline != null && isFinite(row.baseline)) {
              tr.setAttribute('data-sdm-baseline', String(row.baseline));
            }
            var td0 = document.createElement('td');
            td0.textContent = monthLabelShort(row.m0);
            var td1 = document.createElement('td');
            td1.textContent = String(row.bd);
            var td2 = document.createElement('td');
            var hlPct = Number(hlWeights[row.m0]);
            var targetSales =
              row.baseline != null && isFinite(hlPct)
                ? row.baseline * (hlPct / 100)
                : null;
            td2.textContent =
              targetSales != null && row.bd > 0 ? formatAnalyzeMoney(targetSales) : '—';"""

PAST_SALES_RENDER_REVERT_OLD = """        if (analyzeTableBody) {
          while (analyzeTableBody.firstChild) analyzeTableBody.removeChild(analyzeTableBody.firstChild);
          for (var mi = 0; mi < model.months.length; mi++) {
            var row = model.months[mi];
            var tr = document.createElement('tr');
            if (row.baseline != null && isFinite(row.baseline)) {
              tr.setAttribute('data-sdm-baseline', String(row.baseline));
            }
            var td0 = document.createElement('td');
            td0.textContent = monthLabelShort(row.m0);
            var td1 = document.createElement('td');
            td1.textContent = String(row.bd);
            var td2 = document.createElement('td');
            var hlPct = Number(hlWeights[row.m0]);
            var targetSales =
              row.baseline != null && isFinite(hlPct)
                ? row.baseline * (hlPct / 100)
                : null;
            td2.textContent =
              targetSales != null && row.bd > 0 ? formatAnalyzeMoney(targetSales) : '—';"""

PAST_SALES_RENDER_REVERT_NEW = """        if (analyzeTableBody) {
          while (analyzeTableBody.firstChild) analyzeTableBody.removeChild(analyzeTableBody.firstChild);
          for (var mi = 0; mi < model.months.length; mi++) {
            var row = model.months[mi];
            var tr = document.createElement('tr');
            var td0 = document.createElement('td');
            td0.textContent = monthLabelShort(row.m0);
            var td1 = document.createElement('td');
            td1.textContent = String(row.bd);
            var td2 = document.createElement('td');
            td2.textContent = row.bd > 0 ? formatAnalyzeMoney(row.sales) : '—';"""

JA_TABLE_PATCHES = {
    '<th scope="col">月次売上</th>': '<th scope="col">月次目標売上</th>',
    '<th scope="col" class="sales-data-modal__analyze-hl-head">繁閑期%設定</th>': (
        '<th scope="col" class="sales-data-modal__analyze-hl-head sales-data-modal__analyze-hl-head-tip"'
        ' data-hl-tip="▼左 ▲右 で5%刻み">繁閑期%設定</th>'
    ),
    'class="sales-data-modal__analyze-hl-tip sales-data-modal__analyze-hl-tip--footer"\n'
    '                      data-hl-tip="Monthly Allocated Total が 100% になるよう、各月の繁閑期%を調整してください"':
        'class="sales-data-modal__analyze-hl-tip--footer"\n'
        '                      data-hl-tip="各月%の平均が100%に"',
}

EN_TABLE_PATCHES = {
    '<th scope="col">Monthly Sales</th>': '<th scope="col">Monthly Target Sales</th>',
    '<th scope="col" class="sales-data-modal__analyze-hl-head">H/L Season% Setting</th>': (
        '<th scope="col" class="sales-data-modal__analyze-hl-head sales-data-modal__analyze-hl-head-tip"'
        ' data-hl-tip="▼ left, ▲ right: ±5%">H/L Season% Setting</th>'
    ),
    'class="sales-data-modal__analyze-hl-tip sales-data-modal__analyze-hl-tip--footer"\n'
    '                      data-hl-tip="Adjust monthly H/L % so Monthly Allocated Total reaches 100%"':
        'class="sales-data-modal__analyze-hl-tip--footer"\n'
        '                      data-hl-tip="12-month average → 100%"',
}


def sdm_hl_stepper_js() -> str:
    return f"""      {SDM_HL_STEPPER_MARKER}
      var SDM_HL_MIN = 60;
      var SDM_HL_MAX = 200;
      var SDM_HL_STEP = 5;
      var sdmHlAllocWarnShown = false;
      function sdmDefaultHlWeights() {{
        return [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115];
      }}
      function sdmAll100HlWeights() {{
        return [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100];
      }}
      function clampSdmHlWeight(n) {{
        n = Number(n);
        if (!Number.isFinite(n)) n = 100;
        if (n < SDM_HL_MIN) n = SDM_HL_MIN;
        if (n > SDM_HL_MAX) n = SDM_HL_MAX;
        return Math.round(n / SDM_HL_STEP) * SDM_HL_STEP;
      }}
      function ensureSdmHlWeightsForYear(year) {{
        var y = Number(year);
        if (!Number.isFinite(y) && window.KpiYearStore) y = KpiYearStore.getOperatingYear();
        if (!Number.isFinite(y)) return sdmAll100HlWeights();
        if (!window.KpiYearStore) return sdmAll100HlWeights();
        var fromStore = KpiYearStore.readMonthlyHlWeights(y);
        if (fromStore && fromStore.length === 12) return fromStore.slice();
        if (y === KpiYearStore.getOperatingYear()) {{
          KpiYearStore.ensureOperatingYearPlanDefaults();
          fromStore = KpiYearStore.readMonthlyHlWeights(y);
          if (fromStore && fromStore.length === 12) return fromStore.slice();
        }}
        var baseline =
          typeof KpiYearStore.computeBaselineHlWeights === 'function'
            ? KpiYearStore.computeBaselineHlWeights(y, 2)
            : null;
        if (baseline && baseline.length === 12) {{
          KpiYearStore.writeMonthlyHlWeights(y, baseline, {{ source: 'observed-baseline' }});
          return baseline.slice();
        }}
        var planDefault = sdmDefaultHlWeights();
        KpiYearStore.writeMonthlyHlWeights(y, planDefault, {{ source: 'plan-default' }});
        return planDefault.slice();
      }}
      function getSdmHlWeightsForYear(year) {{
        return ensureSdmHlWeightsForYear(year);
      }}
      function saveSdmHlWeights(year, weights, source) {{
        if (!window.KpiYearStore) return false;
        var y = Number(year);
        if (!Number.isFinite(y)) y = getOperatingYear();
        var payload = weights && weights.length === 12 ? weights.slice() : null;
        if (!payload) return false;
        var ok = KpiYearStore.writeMonthlyHlWeights(y, payload, {{
          source: source || 'sales-data-analyze',
        }});
        if (ok && window.__ANNUAL_UI && typeof window.__ANNUAL_UI.refreshHlPlanFromStore === 'function') {{
          window.__ANNUAL_UI.refreshHlPlanFromStore();
        }}
        return ok;
      }}
      function calcMonthlyAllocatedTotal(weights) {{
        if (!weights || weights.length !== 12) return null;
        var sum = 0;
        for (var i = 0; i < 12; i++) {{
          var n = Number(weights[i]);
          sum += Number.isFinite(n) ? n : 100;
        }}
        return Math.round((sum / 12) * 100) / 100;
      }}
      function isSdmAllocTotalOk(total) {{
        return total != null && Math.abs(total - 100) < 0.01;
      }}
      function updateSdmAllocTotalDisplay(weights) {{
        if (!analyzeAllocTotalEl) return;
        var total = calcMonthlyAllocatedTotal(weights);
        analyzeAllocTotalEl.textContent = total != null ? total.toFixed(2) + '%' : '—';
        analyzeAllocTotalEl.classList.toggle(
          'sales-data-modal__analyze-alloc-total--warn',
          total != null && !isSdmAllocTotalOk(total)
        );
      }}
      function maybeAlertSdmAllocTotal(weights) {{
        if (sdmHlAllocWarnShown) return;
        var total = calcMonthlyAllocatedTotal(weights);
        if (isSdmAllocTotalOk(total)) return;
        sdmHlAllocWarnShown = true;
        window.alert(
          isJa
            ? 'Monthly Allocated Total が ' +
                total.toFixed(2) +
                '% です。\\n左の繁閑期%を参考に ▲▼ で各月を調整し、合計を 100% に近づけてください。'
            : 'Monthly Allocated Total is ' +
                total.toFixed(2) +
                '%.\\nUse ▲▼ to adjust each month (refer to Seasonality % on the left) until the total reaches 100%.'
        );
      }}
      function updateSdmTargetSalesCell(tr, weights, monthIndex) {{
        if (!tr) return;
        var baseline = Number(tr.getAttribute('data-sdm-baseline'));
        if (!isFinite(baseline) || baseline <= 0) return;
        var targetTd = tr.children[2];
        if (!targetTd) return;
        var w = clampSdmHlWeight(weights[monthIndex]);
        targetTd.textContent = formatAnalyzeMoney(baseline * (w / 100));
      }}
      function bindSdmHlCell(td, year, monthIndex, weights) {{
        td.className = 'sales-data-modal__analyze-hl-cell';
        var wrap = document.createElement('div');
        wrap.className = 'sales-data-modal__analyze-hl-stepper';
        var btnDown = document.createElement('button');
        btnDown.type = 'button';
        btnDown.className = 'sales-data-modal__analyze-hl-step sales-data-modal__analyze-hl-step--down';
        btnDown.textContent = '▼';
        btnDown.setAttribute('aria-label', isJa ? '5%減らす' : 'Decrease by 5%');
        var valueEl = document.createElement('span');
        valueEl.className = 'sales-data-modal__analyze-hl-value';
        valueEl.setAttribute('aria-live', 'polite');
        var btnUp = document.createElement('button');
        btnUp.type = 'button';
        btnUp.className = 'sales-data-modal__analyze-hl-step sales-data-modal__analyze-hl-step--up';
        btnUp.textContent = '▲';
        btnUp.setAttribute('aria-label', isJa ? '5%増やす' : 'Increase by 5%');
        wrap.appendChild(btnDown);
        wrap.appendChild(valueEl);
        wrap.appendChild(btnUp);
        function refreshStepper() {{
          var w = clampSdmHlWeight(weights[monthIndex]);
          weights[monthIndex] = w;
          valueEl.textContent = w + '%';
          var locked = window.KpiYearStore && KpiYearStore.isYearLocked(year);
          btnUp.disabled = locked || w >= SDM_HL_MAX;
          btnDown.disabled = locked || w <= SDM_HL_MIN;
        }}
        function step(delta) {{
          if (window.KpiYearStore && KpiYearStore.isYearLocked(year)) {{
            window.alert(
              isJa ? '確定済みの年は繁閑%を編集できません。' : 'Cannot edit H/L % for a locked year.'
            );
            return;
          }}
          var next = clampSdmHlWeight(Number(weights[monthIndex]) + delta);
          if (next === weights[monthIndex]) return;
          var prev = weights[monthIndex];
          weights[monthIndex] = next;
          if (!saveSdmHlWeights(year, weights, 'sales-data-analyze')) {{
            weights[monthIndex] = prev;
            window.alert(isJa ? '保存できませんでした。' : 'Could not save.');
            return;
          }}
          refreshStepper();
          updateSdmAllocTotalDisplay(weights);
          updateSdmTargetSalesCell(td.parentElement, weights, monthIndex);
        }}
        btnUp.addEventListener('click', function () {{ step(SDM_HL_STEP); }});
        btnDown.addEventListener('click', function () {{ step(-SDM_HL_STEP); }});
        refreshStepper();
        td.appendChild(wrap);
      }}
      {SDM_HL_STEPPER_END}
"""

"""Monthly Table Window — MEP-saved metrics only; unset → 0 / $0 / ¥0."""

from __future__ import annotations

MONTHLY_TW_MEP_MARKER = "/* KPI-MONTHLY-TW-MEP-METRICS */"
MONTHLY_TW_MEP_END = "/* END KPI-MONTHLY-TW-MEP-METRICS */"

MONTHLY_TW_MEP_OLD_EN = """      function getActiveDummyGroupValues(groupNo, iso) {
        var sales = resolveDailySalesText(iso);
        if (groupNo === 1) {
          return [sales, demoMoney, demoMoney, sales, demoMoney, '100%'];
        }
        if (groupNo === 2) {
          return ['23', '23', '23', '23', '23', '23'];
        }
        return ['$123,456', '$123,456', '$123,456', '$123,456', '$123,456', '$123,456'];
      }"""

MONTHLY_TW_MEP_OLD_JA = """      function getActiveDummyGroupValues(groupNo, iso) {
        var sales = resolveDailySalesText(iso);
        if (groupNo === 1) {
          return [sales, demoMoney, demoMoney, sales, demoMoney, '100%'];
        }
        if (groupNo === 2) {
          return ['23', '23', '23', '23', '23', '23'];
        }
        return [demoMoney, demoMoney, demoMoney, demoMoney, demoMoney, demoMoney];
      }"""

MONTHLY_TW_MEP_LISTENERS = """      /* KPI-MONTHLY-TW-LISTENERS */
      function monthlyTwRebuildKeepFocus() {
        invalidateMonthlyMepMetricsCache();
        invalidateGroup1TwCache();
        var keepIso =
          currentFocusIso ||
          readDailySelectedIso() ||
          toISODateLocal(new Date(state.year, state.month0, 1));
        rebuildColumns();
        scheduleScroll(keepIso);
      }
      document.addEventListener('kpi:mepDataChanged', monthlyTwRebuildKeepFocus);
      document.addEventListener('monthly:editFloatConfirmed', monthlyTwRebuildKeepFocus);
      document.addEventListener('kpi:dailySalesChanged', monthlyTwRebuildKeepFocus);
      document.addEventListener('kpi:annualPlanChanged', monthlyTwRebuildKeepFocus);
      document.addEventListener('kpi:businessDayChanged', monthlyTwRebuildKeepFocus);
      /* END KPI-MONTHLY-TW-LISTENERS */"""

MONTHLY_TW_LISTENERS_MARKER = "/* KPI-MONTHLY-TW-LISTENERS */"

MAKE_GROUP_COLUMN_OLD = """        for (var i = 0; i < 6; i++) {
          var cell = document.createElement('span');
          cell.className = 'monthly-data-column__cell';
          cell.setAttribute('aria-hidden', 'true');
          cell.textContent = values[i] || '';
          div.appendChild(cell);
        }"""

MAKE_GROUP_COLUMN_NEW = """        for (var i = 0; i < 6; i++) {
          var cell = document.createElement('span');
          cell.className = 'monthly-data-column__cell';
          cell.setAttribute('aria-hidden', 'true');
          cell.textContent = values[i] || '';
          if (groupNo === 1) decorateMonthlyGroup1Cell(cell, i, iso);
          div.appendChild(cell);
        }"""

VFOCUS_CELL_COPY_OLD = """              if (cell) cell.textContent = valuesLane[gi2 * 6 + ci2] || demoMoney;"""

VFOCUS_CELL_COPY_NEW = """              if (cell) {
                cell.textContent = valuesLane[gi2 * 6 + ci2] || demoMoney;
                if (gi2 === 0 && ci2 === 4) {
                  syncMonthlyVfocusDiffClass(cell, colIdx);
                } else if (gi2 === 0) {
                  clearMonthlyTwDiffClasses(cell);
                }
              }"""

MONTHLY_TW_DIFF_CSS_MARKER = "/* KPI-MONTHLY-TW-DIFF-SEVERITY */"

MONTHLY_TW_DIFF_CSS_ANCHOR = """    .monthly-data-column__cell:last-child {
      border-bottom: 0;
    }"""

MONTHLY_TW_DIFF_CSS_BLOCK = f"""    .monthly-data-column__cell:last-child {{
      border-bottom: 0;
    }}
    {MONTHLY_TW_DIFF_CSS_MARKER}
    .monthly-data-column__cell.tw-diff--win,
    .monthly-vfocus-cell.tw-diff--win {{
      color: #58e1f3;
    }}
    .monthly-data-column__cell.tw-diff--neutral,
    .monthly-vfocus-cell.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .monthly-data-column__cell.tw-diff--sev-90,
    .monthly-vfocus-cell.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .monthly-data-column__cell.tw-diff--sev-80,
    .monthly-vfocus-cell.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .monthly-data-column__cell.tw-diff--sev-70,
    .monthly-vfocus-cell.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .monthly-data-column__cell.tw-diff--sev-60,
    .monthly-vfocus-cell.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .monthly-data-column__cell.tw-diff--sev-50,
    .monthly-vfocus-cell.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .monthly-data-column__cell.tw-diff--sev-below,
    .monthly-vfocus-cell.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .office-mode .monthly-data-column__cell.tw-diff--win,
    .office-mode .monthly-vfocus-cell.tw-diff--win {{
      color: #0d7a8c;
    }}
    .office-mode .monthly-data-column__cell.tw-diff--neutral,
    .office-mode .monthly-vfocus-cell.tw-diff--neutral {{
      color: #111;
    }}
    .office-mode .monthly-data-column__cell.tw-diff--sev-90,
    .office-mode .monthly-vfocus-cell.tw-diff--sev-90 {{
      color: #9a6b00;
    }}
    .office-mode .monthly-data-column__cell.tw-diff--sev-80,
    .office-mode .monthly-vfocus-cell.tw-diff--sev-80 {{
      color: #a84300;
    }}
    .office-mode .monthly-data-column__cell.tw-diff--sev-70,
    .office-mode .monthly-vfocus-cell.tw-diff--sev-70 {{
      color: #8f3600;
    }}
    .office-mode .monthly-data-column__cell.tw-diff--sev-60,
    .office-mode .monthly-vfocus-cell.tw-diff--sev-60 {{
      color: #b71c1c;
    }}
    .office-mode .monthly-data-column__cell.tw-diff--sev-50,
    .office-mode .monthly-vfocus-cell.tw-diff--sev-50 {{
      color: #9e1414;
    }}
    .office-mode .monthly-data-column__cell.tw-diff--sev-below,
    .office-mode .monthly-vfocus-cell.tw-diff--sev-below {{
      color: #7a0f0f;
    }}"""


def monthly_tw_mep_metrics_js() -> str:
    return f"""      {MONTHLY_TW_MEP_MARKER}
      var zeroMoney = useJa ? '\\u00a50' : '$0';
      var MEP_CATALOG_KEY = 'kpiNavigator.plLineCatalog';
      var MEP_FALLBACK_FIXED = [
        'exp_rent',
        'exp_fixed_labor',
        'exp_non_life_insurance',
      ];
      var MEP_FALLBACK_VARIABLE = [
        'exp_food_cost',
        'exp_drink_cost',
        'exp_supplies',
        'exp_misc',
        'exp_electric',
        'exp_gas',
        'exp_water',
        'exp_communication',
        'exp_advertising',
        'exp_outsource',
        'exp_repair',
        'exp_travel',
        'exp_entertainment',
        'exp_fee',
        'exp_tax',
        'exp_other',
      ];

      function invalidateMonthlyMepMetricsCache() {{
        window.__MONTHLY_MEP_METRICS__ = null;
      }}

      function plCatalogLines() {{
        try {{
          var raw = window.__KPI_DATA_GATEWAY && window.__KPI_DATA_GATEWAY.getJson(MEP_CATALOG_KEY);
          if (raw && Array.isArray(raw.lines)) return raw.lines;
        }} catch (_e) {{}}
        return null;
      }}

      function lineIdsForBucket(bucket) {{
        var lines = plCatalogLines();
        var out = [];
        if (lines && lines.length) {{
          lines.forEach(function (line) {{
            if (!line || line.active === false) return;
            if (line.bucket === bucket && line.lineId) out.push(String(line.lineId));
          }});
        }}
        if (!out.length) {{
          out = (bucket === 'fixed' ? MEP_FALLBACK_FIXED : MEP_FALLBACK_VARIABLE).slice();
        }}
        return out;
      }}

      function loadMonthlyMepMetricsForYear(year) {{
        var y = Number(year);
        if (!Number.isFinite(y)) return;
        if (
          window.__MONTHLY_MEP_METRICS__ &&
          window.__MONTHLY_MEP_METRICS__.year === y
        ) {{
          return;
        }}
        var payload = null;
        if (window.KpiYearStore && typeof KpiYearStore.loadMepYearPayload === 'function') {{
          if (typeof KpiYearStore.syncToAnnualDaily === 'function') {{
            KpiYearStore.syncToAnnualDaily();
          }}
          payload = KpiYearStore.loadMepYearPayload(y);
        }}
        window.__MONTHLY_MEP_METRICS__ = {{
          year: y,
          payload: payload,
          fixedIds: lineIdsForBucket('fixed'),
          variableIds: lineIdsForBucket('variable'),
        }};
      }}

      function mepDailyMap() {{
        var cache = window.__MONTHLY_MEP_METRICS__;
        if (!cache || !cache.payload || !cache.payload.dailyExpenses) return {{}};
        return cache.payload.dailyExpenses;
      }}

      function mepReadRow(iso, rowId) {{
        if (!rowId) return 0;
        var byRow = mepDailyMap()[rowId];
        if (!byRow || !Object.prototype.hasOwnProperty.call(byRow, iso)) return 0;
        var n = Number(byRow[iso]);
        return Number.isFinite(n) ? n : 0;
      }}

      function mepSumRows(iso, rowIds) {{
        var sum = 0;
        (rowIds || []).forEach(function (rowId) {{
          sum += mepReadRow(iso, rowId);
        }});
        return Math.round(sum);
      }}

      function mepParentMinusLunch(iso, parentId, lunchId) {{
        return Math.max(
          0,
          Math.round(mepReadRow(iso, parentId)) - Math.round(mepReadRow(iso, lunchId))
        );
      }}

      function mepSalesRowMinusLunch(iso, lunchId) {{
        var sales = dailySalesAmount(iso);
        return Math.max(0, Math.round(sales) - Math.round(mepReadRow(iso, lunchId)));
      }}

      function fmtTwMoney(n) {{
        var v = Math.round(Number(n) || 0);
        if (useJa) return '\\u00a5' + v.toLocaleString('ja-JP');
        return '$' + v.toLocaleString('en-US');
      }}

      function fmtTwCount(n) {{
        return String(Math.round(Number(n) || 0));
      }}

      function dailySalesAmount(iso) {{
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var tmap = daily && daily.targetSalesByDate;
        if (!tmap || !Object.prototype.hasOwnProperty.call(tmap, iso)) return 0;
        var n = Number(tmap[iso]);
        if (!Number.isFinite(n) || n === 1234) return 0;
        return Math.round(n);
      }}

      var __group1TwCache = {{}};
      function invalidateGroup1TwCache() {{
        __group1TwCache = {{}};
      }}

      function monthlyTwDiffLevels() {{
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

      function clearMonthlyTwDiffClasses(el) {{
        if (!el) return;
        monthlyTwDiffLevels().forEach(function (cls) {{
          el.classList.remove(cls);
        }});
      }}

      function applyMonthlyTwDiffClass(el, actual, target) {{
        clearMonthlyTwDiffClasses(el);
        if (!el || typeof window.__twDiffSeverityClass !== 'function') return;
        if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) return;
        el.classList.add(window.__twDiffSeverityClass(actual, target));
      }}

      function readGroup1TwSnapshot(iso) {{
        if (__group1TwCache[iso]) return __group1TwCache[iso];
        var sales = dailySalesAmount(iso);
        var targetText = '—';
        var diffText = '—';
        var achText = '—';
        var diffActual = NaN;
        var diffTarget = NaN;
        if (typeof window.__computeTwMetricsForIso === 'function') {{
          if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {{
            KpiYearStore.syncToAnnualDaily();
          }}
          var m = window.__computeTwMetricsForIso(iso);
          if (m) {{
            sales = Number(m.dailySales) || 0;
            if (m.dailyTarget != null && Number.isFinite(Number(m.dailyTarget))) {{
              diffTarget = Number(m.dailyTarget);
              targetText = fmtTwMoney(diffTarget);
              diffActual = sales;
              diffText =
                typeof window.__twFmtDiff === 'function'
                  ? window.__twFmtDiff(diffActual, diffTarget)
                  : fmtTwMoney(diffActual - diffTarget);
              achText =
                typeof window.__twFmtAchPct === 'function'
                  ? window.__twFmtAchPct(diffActual, diffTarget)
                  : '—';
            }}
          }}
        }}
        var snap = {{
          sales: sales,
          targetText: targetText,
          diffText: diffText,
          achText: achText,
          diffActual: diffActual,
          diffTarget: diffTarget,
        }};
        __group1TwCache[iso] = snap;
        return snap;
      }}

      function decorateMonthlyGroup1Cell(cell, cellIndex, iso) {{
        if (!cell || cellIndex !== 4) return;
        var snap = readGroup1TwSnapshot(iso);
        applyMonthlyTwDiffClass(cell, snap.diffActual, snap.diffTarget);
      }}

      function syncMonthlyVfocusDiffClass(cell, colIdx) {{
        if (!cell || !trackGroup1 || !trackGroup1.children) return;
        var srcCol = trackGroup1.children[colIdx];
        if (!srcCol) return;
        var srcCells = srcCol.querySelectorAll('.monthly-data-column__cell');
        var srcDiff = srcCells && srcCells[4] ? srcCells[4] : null;
        clearMonthlyTwDiffClasses(cell);
        if (!srcDiff) return;
        monthlyTwDiffLevels().forEach(function (cls) {{
          if (srcDiff.classList.contains(cls)) cell.classList.add(cls);
        }});
      }}

      function resolveGroup1Values(iso) {{
        var snap = readGroup1TwSnapshot(iso);
        var lunch = mepReadRow(iso, 'incLunch');
        var dinner = mepSalesRowMinusLunch(iso, 'incLunch');
        return [
          fmtTwMoney(snap.sales),
          fmtTwMoney(lunch),
          fmtTwMoney(dinner),
          snap.targetText,
          snap.diffText,
          snap.achText,
        ];
      }}

      function resolveGroup2Values(iso) {{
        var cust = mepReadRow(iso, 'cust');
        var custLunch = mepReadRow(iso, 'custLunch');
        var custDinner = mepParentMinusLunch(iso, 'cust', 'custLunch');
        if (useJa) {{
          var grp = mepReadRow(iso, 'groupCnt');
          var grpLunch = mepReadRow(iso, 'groupCntLunch');
          var grpDinner = mepParentMinusLunch(iso, 'groupCnt', 'groupCntLunch');
          return [
            fmtTwCount(cust),
            fmtTwCount(custLunch),
            fmtTwCount(custDinner),
            fmtTwCount(grp),
            fmtTwCount(grpLunch),
            fmtTwCount(grpDinner),
          ];
        }}
        var pc = mepReadRow(iso, 'pc');
        var pcLunch = mepReadRow(iso, 'pcLunch');
        var pcDinner = mepParentMinusLunch(iso, 'pc', 'pcLunch');
        return [
          fmtTwCount(cust),
          fmtTwCount(custLunch),
          fmtTwCount(custDinner),
          fmtTwMoney(pc),
          fmtTwMoney(pcLunch),
          fmtTwMoney(pcDinner),
        ];
      }}

      function resolveGroup3Values(iso) {{
        var cache = window.__MONTHLY_MEP_METRICS__ || {{}};
        var food = mepReadRow(iso, 'exp_food_cost');
        var bev = mepReadRow(iso, 'exp_drink_cost');
        var misc = mepReadRow(iso, 'exp_misc');
        var fixed = mepSumRows(iso, cache.fixedIds);
        var expected = mepSumRows(iso, cache.variableIds);
        var total = fixed + expected;
        return [
          fmtTwMoney(food),
          fmtTwMoney(bev),
          fmtTwMoney(misc),
          fmtTwMoney(fixed),
          fmtTwMoney(expected),
          fmtTwMoney(total),
        ];
      }}

      function resolveMonthlyProfitValue(iso) {{
        var sales = dailySalesAmount(iso);
        var cache = window.__MONTHLY_MEP_METRICS__ || {{}};
        var expenses =
          mepSumRows(iso, cache.fixedIds) + mepSumRows(iso, cache.variableIds);
        return fmtTwMoney(sales - expenses);
      }}

      function getActiveDummyGroupValues(groupNo, iso) {{
        if (groupNo === 1) return resolveGroup1Values(iso);
        if (groupNo === 2) return resolveGroup2Values(iso);
        return resolveGroup3Values(iso);
      }}
      {MONTHLY_TW_MEP_END}"""


def monthly_tw_mep_rebuild_hook() -> str:
    return """        loadMonthlyMepMetricsForYear(state.year);
"""

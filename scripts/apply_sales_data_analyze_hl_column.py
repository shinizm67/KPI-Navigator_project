#!/usr/bin/env python3
"""Sales Data Analyze tab — H/L plan column, footer total, Cockpit sync."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    ROOT / "app/annual/index.html": {
        "observed_th": "繁閑期%",
        "hl_th": "繁閑期%設定",
        "tfoot_label": "月次配分率合計",
        "aria": "月次繁閑分析",
    },
    ROOT / "en/app/annual/index.html": {
        "observed_th": "Seasonality %",
        "hl_th": "H/L Season% Setting",
        "tfoot_label": "Monthly Allocated Total",
        "aria": "Monthly seasonality analysis",
    },
}

PATCH_MARKER = "sdm-analyze-hl-col-w"

CSS_OLD = """    .sales-data-modal__analyze-table th:nth-child(1),
    .sales-data-modal__analyze-table td:nth-child(1) {
      width: 16%;
    }
    .sales-data-modal__analyze-table th:nth-child(2),
    .sales-data-modal__analyze-table td:nth-child(2) {
      width: 16%;
    }
    .sales-data-modal__analyze-table th:nth-child(3),
    .sales-data-modal__analyze-table td:nth-child(3) {
      width: 25%;
    }
    .sales-data-modal__analyze-table th:nth-child(4),
    .sales-data-modal__analyze-table td:nth-child(4) {
      width: 25%;
    }
    .sales-data-modal__analyze-table th:nth-child(5),
    .sales-data-modal__analyze-table td:nth-child(5) {
      width: 18%;
    }
    .sales-data-modal__analyze-table th,
    .sales-data-modal__analyze-table td {
      border: 1px solid var(--sdm-line);
      padding: 8px 6px;
      text-align: center;
      vertical-align: middle;
      box-sizing: border-box;
      font-variant-numeric: tabular-nums;
    }
    .sales-data-modal__analyze-table thead th {
      background: var(--sdm-bg-active-label);
      font-weight: 700;
      font-size: var(--sdm-fs-colhead);
    }
    .sales-data-modal__analyze-table tbody td {
      background: var(--sdm-bg-inactive);
    }
    .sales-data-modal__analyze-table tbody td:first-child {
      font-weight: 600;
    }"""

CSS_NEW = f"""    .sales-data-modal__analyze-table {{
      --{PATCH_MARKER}: 170px;
      --sdm-analyze-hl-bg: #2f555a;
      --sdm-analyze-head-fs: 14px;
    }}
    .sales-data-modal__analyze-table th:nth-child(1),
    .sales-data-modal__analyze-table td:nth-child(1) {{
      width: 11%;
    }}
    .sales-data-modal__analyze-table th:nth-child(2),
    .sales-data-modal__analyze-table td:nth-child(2) {{
      width: 11%;
    }}
    .sales-data-modal__analyze-table th:nth-child(3),
    .sales-data-modal__analyze-table td:nth-child(3) {{
      width: 20%;
    }}
    .sales-data-modal__analyze-table th:nth-child(4),
    .sales-data-modal__analyze-table td:nth-child(4) {{
      width: 20%;
    }}
    .sales-data-modal__analyze-table th:nth-child(5),
    .sales-data-modal__analyze-table td:nth-child(5) {{
      width: calc(100% - var(--{PATCH_MARKER}) - 62%);
    }}
    .sales-data-modal__analyze-table th:nth-child(6),
    .sales-data-modal__analyze-table td:nth-child(6) {{
      width: var(--{PATCH_MARKER});
      min-width: var(--{PATCH_MARKER});
      max-width: var(--{PATCH_MARKER});
    }}
    .sales-data-modal__analyze-table th,
    .sales-data-modal__analyze-table td {{
      border: 1px solid var(--sdm-line);
      padding: 8px 6px;
      text-align: center;
      vertical-align: middle;
      box-sizing: border-box;
      font-variant-numeric: tabular-nums;
    }}
    .sales-data-modal__analyze-table thead th {{
      background: var(--sdm-bg-active-label);
      font-weight: 700;
      font-size: var(--sdm-analyze-head-fs);
    }}
    .sales-data-modal__analyze-table tbody td {{
      background: var(--sdm-bg-inactive);
    }}
    .sales-data-modal__analyze-table tbody td:first-child {{
      font-weight: 600;
    }}
    .sales-data-modal__analyze-table th.sales-data-modal__analyze-hl-head,
    .sales-data-modal__analyze-table td.sales-data-modal__analyze-hl-cell,
    .sales-data-modal__analyze-table tfoot td {{
      background: var(--sdm-analyze-hl-bg);
    }}
    .sales-data-modal__analyze-table tfoot td {{
      font-weight: 700;
    }}
    .sales-data-modal__analyze-table tfoot td.sales-data-modal__analyze-total-label {{
      text-align: left;
      padding-left: 12px;
    }}
    /* KPI-SDM-ANALYZE-HL-OFFICE — PL Analysis と同系の薄シアン（黒文字が読める） */
    body.office-mode .sales-data-modal__analyze-table {{
      --sdm-analyze-hl-bg: #dff5f8;
    }}
    body.office-mode .sales-data-modal__analyze-table th.sales-data-modal__analyze-hl-head,
    body.office-mode .sales-data-modal__analyze-table td.sales-data-modal__analyze-hl-cell,
    body.office-mode .sales-data-modal__analyze-table tfoot td {{
      color: #111;
      background: #dff5f8 !important;
    }}
    body.office-mode .sales-data-modal__analyze-hl-step {{
      border-color: #111;
      background: #fff;
      color: #111;
    }}
    body.office-mode .sales-data-modal__analyze-hl-step:hover:not(:disabled),
    body.office-mode .sales-data-modal__analyze-hl-step:focus-visible:not(:disabled) {{
      background: #e8e8e8;
    }}
    .sales-data-modal__analyze-hl-btn {{
      display: block;
      width: 100%;
      margin: 0;
      padding: 0;
      border: 0;
      background: transparent;
      color: inherit;
      font: inherit;
      font-variant-numeric: tabular-nums;
      cursor: pointer;
      text-align: center;
    }}
    .sales-data-modal__analyze-hl-btn:hover,
    .sales-data-modal__analyze-hl-btn:focus-visible {{
      text-decoration: underline;
      outline: none;
    }}"""

VARS_OLD = """      var analyzeTableBody = document.getElementById('sales-data-analyze-table-body');
      var seasonalityBarsEl = document.getElementById('sales-data-seasonality-bars');"""

VARS_NEW = """      var analyzeTableBody = document.getElementById('sales-data-analyze-table-body');
      var analyzeAllocTotalEl = document.getElementById('sales-data-analyze-alloc-total');
      var seasonalityBarsEl = document.getElementById('sales-data-seasonality-bars');
      function normalizeSdmHlWeightInput(raw) {
        var value = parsePercentText(raw);
        if (!Number.isFinite(value)) return null;
        if (!Number.isInteger(value)) return null;
        if (value % 5 !== 0) return null;
        if (value < 60 || value > 200) return null;
        return value;
      }
      function getSdmHlWeightsForYear(year) {
        var y = Number(year);
        if (window.KpiYearStore && Number.isFinite(y)) {
          var fromStore = KpiYearStore.readMonthlyHlWeights(y);
          if (fromStore && fromStore.length === 12) return fromStore.slice();
        }
        return [85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115];
      }
      function saveSdmHlWeights(year, weights, source) {
        if (!window.KpiYearStore) return false;
        var ok = KpiYearStore.writeMonthlyHlWeights(year, weights, {
          source: source || 'sales-data-analyze',
        });
        if (ok && window.__ANNUAL_UI && typeof window.__ANNUAL_UI.refreshHlPlanFromStore === 'function') {
          window.__ANNUAL_UI.refreshHlPlanFromStore();
        }
        return ok;
      }
      function calcMonthlyAllocatedTotal(weights) {
        if (!weights || weights.length !== 12) return null;
        var sum = 0;
        for (var i = 0; i < 12; i++) {
          var n = Number(weights[i]);
          sum += Number.isFinite(n) ? n : 100;
        }
        return Math.round((sum / 12) * 100) / 100;
      }
      function updateSdmAllocTotalDisplay(weights) {
        if (!analyzeAllocTotalEl) return;
        var total = calcMonthlyAllocatedTotal(weights);
        analyzeAllocTotalEl.textContent = total != null ? total.toFixed(2) + '%' : '—';
      }
      function bindSdmHlCell(td, year, monthIndex, weights) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'sales-data-modal__analyze-hl-btn';
        var w = Number(weights[monthIndex]);
        btn.textContent = (Number.isFinite(w) ? w : 100) + '%';
        btn.setAttribute(
          'title',
          isJa ? 'クリックで繁閑期%を編集（5%刻み）' : 'Click to edit H/L % (5% steps)'
        );
        btn.addEventListener('click', function () {
          if (window.KpiYearStore && KpiYearStore.isYearLocked(year)) {
            window.alert(
              isJa ? '確定済みの年は繁閑%を編集できません。' : 'Cannot edit H/L % for a locked year.'
            );
            return;
          }
          var current = Number(weights[monthIndex]);
          var input = window.prompt(
            (isJa ? '繁閑期% ' : 'H/L % ') + (monthIndex + 1) + (isJa ? '月' : ''),
            String(Number.isFinite(current) ? current : 100)
          );
          if (input == null) return;
          var next = normalizeSdmHlWeightInput(input);
          if (next == null) {
            window.alert(
              isJa
                ? '5%刻みの整数（60〜200）で入力してください。'
                : 'Please enter an integer in 5% steps (60 to 200).'
            );
            return;
          }
          weights[monthIndex] = next;
          if (!saveSdmHlWeights(year, weights, 'sales-data-analyze')) return;
          btn.textContent = next + '%';
          updateSdmAllocTotalDisplay(weights);
        });
        td.appendChild(btn);
      }"""

RENDER_TABLE_OLD = """        if (analyzeTableBody) {
          while (analyzeTableBody.firstChild) analyzeTableBody.removeChild(analyzeTableBody.firstChild);
          for (var mi = 0; mi < model.months.length; mi++) {
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
          }
        }"""

RENDER_TABLE_NEW = """        if (analyzeTableBody) {
          var hlWeights = getSdmHlWeightsForYear(y);
          while (analyzeTableBody.firstChild) analyzeTableBody.removeChild(analyzeTableBody.firstChild);
          for (var mi = 0; mi < model.months.length; mi++) {
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
            var td5 = document.createElement('td');
            td5.className = 'sales-data-modal__analyze-hl-cell';
            bindSdmHlCell(td5, y, row.m0, hlWeights);
            tr.appendChild(td0);
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            tr.appendChild(td4);
            tr.appendChild(td5);
            analyzeTableBody.appendChild(tr);
          }
          updateSdmAllocTotalDisplay(hlWeights);
        }"""

SESSION_OLD = """      var sessionSaved = false;
      var undoStack = [];

      function ensureSalesDataDaily() {"""

SESSION_NEW = """      var sessionSaved = false;
      var undoStack = [];
      document.addEventListener('kpi:annualPlanChanged', function () {
        if (state.activeTab === 'analyze') renderSalesDataAnalyze();
      });

      function ensureSalesDataDaily() {"""


def html_table_block(labels: dict[str, str]) -> tuple[str, str]:
    old = f"""              <table class="sales-data-modal__analyze-table" aria-label="{labels["aria"]}">
                <thead>
                  <tr>
                    <th scope="col">{'月' if labels['observed_th'] == '繁閑期%' else 'Month'}</th>
                    <th scope="col">B. DAY</th>
                    <th scope="col">{'月次目標売上' if labels['observed_th'] == '繁閑期%' else 'Monthly Target Sales'}</th>
                    <th scope="col">{'基準月次売上' if labels['observed_th'] == '繁閑期%' else 'Baseline Monthly Sales'}</th>
                    <th scope="col">{labels['observed_th']}</th>
                  </tr>
                </thead>
                <tbody id="sales-data-analyze-table-body"></tbody>
              </table>"""
    new = f"""              <table class="sales-data-modal__analyze-table" aria-label="{labels['aria']}">
                <thead>
                  <tr>
                    <th scope="col">{'月' if labels['observed_th'] == '繁閑期%' else 'Month'}</th>
                    <th scope="col">B. DAY</th>
                    <th scope="col">{'月次目標売上' if labels['observed_th'] == '繁閑期%' else 'Monthly Target Sales'}</th>
                    <th scope="col">{'基準月次売上' if labels['observed_th'] == '繁閑期%' else 'Baseline Monthly Sales'}</th>
                    <th scope="col">{labels['observed_th']}</th>
                    <th scope="col" class="sales-data-modal__analyze-hl-head">{labels['hl_th']}</th>
                  </tr>
                </thead>
                <tbody id="sales-data-analyze-table-body"></tbody>
                <tfoot>
                  <tr>
                    <td colspan="5" class="sales-data-modal__analyze-total-label">{labels['tfoot_label']}</td>
                    <td id="sales-data-analyze-alloc-total">—</td>
                  </tr>
                </tfoot>
              </table>"""
    return old, new


def patch_file(path: Path, labels: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    if PATCH_MARKER in text:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return
    html_old, html_new = html_table_block(labels)
    for old, new, label in [
        (CSS_OLD, CSS_NEW, "css"),
        (html_old, html_new, "html"),
        (VARS_OLD, VARS_NEW, "vars"),
        (RENDER_TABLE_OLD, RENDER_TABLE_NEW, "render"),
        (SESSION_OLD, SESSION_NEW, "session"),
    ]:
        if old not in text:
            raise ValueError(f"{label} block missing in {path}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    for path, labels in TARGETS.items():
        patch_file(path, labels)


if __name__ == "__main__":
    main()

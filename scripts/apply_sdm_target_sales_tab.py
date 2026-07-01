#!/usr/bin/env python3
"""Sales Data — Target Sales tab: 6 columns, H/L stepper, Figma-aligned headers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sdm_hl_stepper_client import SDM_HL_STEPPER_END, SDM_HL_STEPPER_MARKER, sdm_hl_stepper_js  # noqa: E402
from sdm_analyze_past_seasonality_client import (  # noqa: E402
    ANALYZE_MODEL_END,
    ANALYZE_MODEL_MARKER,
    analyze_model_js,
)

MARKER = "sdm-analyze-hl-col-w"

PAGES = {
    ROOT / "app/annual/index.html": {
        "tab_label": "Target Sales",
        "kpi_annual_label": "年間目標売上",
        "table_aria": "月次目標売上配分",
        "col_baseline": "基準月次売上",
        "col_target": "月次目標売上",
        "col_season": "前年繁閑期%",
        "col_hl": "繁閑期%設定",
        "col_hl_tip": "▼左 ▲右 で5%刻み",
        "tfoot_label": "Monthly Allocated Total",
        "tfoot_tip": "各月%の平均が100%に",
    },
    ROOT / "en/app/annual/index.html": {
        "tab_label": "Target Sales",
        "kpi_annual_label": "Annual Target Sales",
        "table_aria": "Monthly target sales allocation",
        "col_baseline": "Baseline Monthly Sales",
        "col_target": "Monthly Target Sales",
        "col_season": "Last Year of Seasonality %",
        "col_hl": "H/L Season% Setting",
        "col_hl_tip": "▼ left, ▲ right: ±5%",
        "tfoot_label": "Monthly Allocated Total",
        "tfoot_tip": "12-month average → 100%",
    },
}

CSS_OLD = """    .sales-data-modal__analyze-table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      font-size: var(--sdm-fs-body);
    }
    .sales-data-modal__analyze-table th:nth-child(1),
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
      background: var(--sdm-bg-active-55);
      font-weight: 700;
      font-size: var(--sdm-fs-colhead);
    }
    .sales-data-modal__analyze-table tbody td {
      background: var(--sdm-bg-inactive);
    }
    .sales-data-modal__analyze-table tbody td:nth-child(n + 3) {
      text-align: right;
      padding-right: 10px;
    }
    .sales-data-modal__analyze-table tbody td:first-child {
      font-weight: 600;
    }"""


def css_new() -> str:
    return f"""    .sales-data-modal__analyze-table {{
      --{MARKER}: 170px;
      --sdm-analyze-hl-bg: #2f555a;
      --sdm-analyze-head-fs: 14px;
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      font-size: var(--sdm-fs-body);
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
      width: calc(100% - var(--{MARKER}) - 62%);
    }}
    .sales-data-modal__analyze-table th:nth-child(6),
    .sales-data-modal__analyze-table td:nth-child(6) {{
      width: var(--{MARKER});
      min-width: var(--{MARKER});
      max-width: var(--{MARKER});
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
      background: var(--sdm-bg-active-55);
      font-weight: 700;
      font-size: var(--sdm-analyze-head-fs);
    }}
    .sales-data-modal__analyze-table tbody td {{
      background: var(--sdm-bg-inactive);
    }}
    .sales-data-modal__analyze-table tbody td:nth-child(n + 3):not(.sales-data-modal__analyze-hl-cell) {{
      text-align: right;
      padding-right: 10px;
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
    .sales-data-modal__analyze-hl-stepper {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 3px;
      width: 100%;
      box-sizing: border-box;
    }}
    .sales-data-modal__analyze-hl-step {{
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
    }}
    .sales-data-modal__analyze-hl-step:hover:not(:disabled),
    .sales-data-modal__analyze-hl-step:focus-visible:not(:disabled) {{
      background: rgba(88, 225, 243, 0.28);
      outline: none;
    }}
    .sales-data-modal__analyze-hl-step:disabled {{
      opacity: 0.35;
      cursor: default;
    }}
    .sales-data-modal__analyze-hl-value {{
      flex: 1 1 auto;
      min-width: 42px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      text-align: center;
    }}
    .sales-data-modal__analyze-alloc-total--warn {{
      color: #ff7070;
      font-weight: 800;
    }}
    body.office-mode .sales-data-modal__analyze-alloc-total--warn {{
      color: #c62828;
    }}
    .sales-data-modal__analyze-hl-head-tip {{
      position: relative;
      cursor: help;
    }}
    .sales-data-modal__analyze-hl-head-tip:hover::after {{
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
    }}
    .sales-data-modal__analyze-hl-tip--footer {{
      position: relative;
      cursor: help;
    }}
    .sales-data-modal__analyze-hl-tip--footer:hover::after {{
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
    }}
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__seasonality {{
      display: none;
    }}"""


def table_html(labels: dict[str, str]) -> str:
    month_col = "月" if labels["col_baseline"] == "基準月次売上" else "Month"
    return f"""              <table class="sales-data-modal__analyze-table" aria-label="{labels['table_aria']}">
                <thead>
                  <tr>
                    <th scope="col">{month_col}</th>
                    <th scope="col">B. DAY</th>
                    <th scope="col">{labels['col_baseline']}</th>
                    <th scope="col">{labels['col_target']}</th>
                    <th scope="col">{labels['col_season']}</th>
                    <th scope="col" class="sales-data-modal__analyze-hl-head sales-data-modal__analyze-hl-head-tip" data-hl-tip="{labels['col_hl_tip']}">{labels['col_hl']}</th>
                  </tr>
                </thead>
                <tbody id="sales-data-analyze-table-body"></tbody>
                <tfoot>
                  <tr>
                    <td colspan="5" class="sales-data-modal__analyze-total-label">{labels['tfoot_label']}</td>
                    <td id="sales-data-analyze-alloc-total" class="sales-data-modal__analyze-hl-tip--footer" data-hl-tip="{labels['tfoot_tip']}">—</td>
                  </tr>
                </tfoot>
              </table>"""


TABLE_OLD_RE = re.compile(
    r"<table class=\"sales-data-modal__analyze-table\"[\s\S]*?</table>",
    re.MULTILINE,
)

VARS_OLD = """      var analyzeInputSalesEl = document.getElementById('sales-data-analyze-input-sales');
      var analyzeTotalBdEl = document.getElementById('sales-data-analyze-total-bd');
      var analyzeAvgDailyEl = document.getElementById('sales-data-analyze-avg-daily');
      var analyzeTableBody = document.getElementById('sales-data-analyze-table-body');
      var seasonalityBarsEl = document.getElementById('sales-data-seasonality-bars');"""

VARS_NEW = """      var analyzeAnnualTargetEl = document.getElementById('sales-data-analyze-annual-target');
      var analyzeTotalBdEl = document.getElementById('sales-data-analyze-total-bd');
      var analyzeAvgDailyEl = document.getElementById('sales-data-analyze-avg-daily');
      var analyzeTableBody = document.getElementById('sales-data-analyze-table-body');
      var analyzeAllocTotalEl = document.getElementById('sales-data-analyze-alloc-total');
      var seasonalityBarsEl = document.getElementById('sales-data-seasonality-bars');"""

BUILD_MODEL_OLD = """      function buildSalesDataAnalyzeModel(y) {
        var all = gatherYearDays(y);
        var annualTarget = getReferenceAnnualForAnalyze(y);
        var monthlySales = getMonthlyCumulativeSalesByMonth(y);
        var hlWeights = getHlWeightsForSalesDataAnalyze(y);
        var totalBD = 0;
        var monthlyBD = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        for (var i = 0; i < all.length; i++) {
          var item = all[i];
          var defs = getRowDefaults(item.iso, item.isWk);
          if (!defs.off) {
            totalBD++;
            monthlyBD[item.m0]++;
          }
        }
        var avgDaily = annualTarget != null && totalBD > 0 ? annualTarget / totalBD : null;
        var cumulativeInput = getCumulativeInputAnnualTotal(y);
        var months = [];
        for (var m0 = 0; m0 < 12; m0++) {
          var w = Number(hlWeights[m0]);
          if (!isFinite(w)) w = 100;
          var baseline =
            avgDaily != null && monthlyBD[m0] > 0 ? avgDaily * monthlyBD[m0] * (w / 100) : null;
          var sales = monthlySales[m0];
          var seasonality = baseline != null && baseline > 0 ? (sales / baseline) * 100 : null;
          months.push({
            m0: m0,
            bd: monthlyBD[m0],
            sales: sales,
            baseline: baseline,
            seasonality: seasonality
          });
        }
        return {
          year: y,
          annualTarget: annualTarget,
          cumulativeInput: cumulativeInput,
          totalBD: totalBD,
          avgDaily: avgDaily,
          months: months
        };
      }"""


def analyze_model_patched() -> str:
    block = analyze_model_js().rstrip()
    block = block.replace("getAnnualTargetForAnalyze(y)", "getReferenceAnnualForAnalyze(y)")
    return block + "\n"


RENDER_OLD = """      function renderSalesDataAnalyze() {
        var y = state.year;
        if (!isFinite(y)) y = getOperatingYear();
        if (!isFinite(y)) return;
        var model = buildSalesDataAnalyzeModel(y);
        if (analyzeInputSalesEl) {
          analyzeInputSalesEl.textContent =
            model.cumulativeInput != null ? formatAnalyzeMoney(model.cumulativeInput) : '—';
        }
        if (analyzeTotalBdEl) {
          analyzeTotalBdEl.textContent = model.totalBD > 0 ? String(model.totalBD) : '—';
        }
        if (analyzeAvgDailyEl) {
          analyzeAvgDailyEl.textContent =
            model.avgDaily != null ? formatAnalyzeMoney(model.avgDaily) : '—';
        }
        if (analyzeTableBody) {
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
        }
        if (seasonalityBarsEl) {"""


RENDER_NEW = """      function renderSalesDataAnalyze() {
        var y = state.year;
        if (!isFinite(y)) y = getOperatingYear();
        if (!isFinite(y)) return;
        var planYear = getOperatingYear();
        var model = buildSalesDataAnalyzeModel(y);
        if (analyzeAnnualTargetEl) {
          var annualVal = model.annualSales != null ? model.annualSales : model.annualTarget;
          analyzeAnnualTargetEl.textContent =
            annualVal != null ? formatAnalyzeMoney(annualVal) : '—';
        }
        if (analyzeTotalBdEl) {
          analyzeTotalBdEl.textContent = model.totalBD > 0 ? String(model.totalBD) : '—';
        }
        if (analyzeAvgDailyEl) {
          analyzeAvgDailyEl.textContent =
            model.avgDaily != null ? formatAnalyzeMoney(model.avgDaily) : '—';
        }
        if (analyzeTableBody) {
          var hlWeights = getSdmHlWeightsForYear(planYear);
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
            td2.textContent =
              row.baseline != null && row.bd > 0 ? formatAnalyzeMoney(row.baseline) : '—';
            var td3 = document.createElement('td');
            var hlPct = Number(hlWeights[row.m0]);
            var targetSales =
              row.baseline != null && isFinite(hlPct) ? row.baseline * (hlPct / 100) : null;
            td3.textContent =
              targetSales != null && row.bd > 0 ? formatAnalyzeMoney(targetSales) : '—';
            var td4 = document.createElement('td');
            td4.textContent = formatSeasonalityPct(row.seasonality);
            var td5 = document.createElement('td');
            bindSdmHlCell(td5, planYear, row.m0, hlWeights);
            tr.appendChild(td0);
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            tr.appendChild(td4);
            tr.appendChild(td5);
            analyzeTableBody.appendChild(tr);
          }
          updateSdmAllocTotalDisplay(hlWeights);
          maybeAlertSdmAllocTotal(hlWeights);
        }
        if (seasonalityBarsEl) {"""


def hl_stepper_js_fixed() -> str:
    js = sdm_hl_stepper_js()
    js = js.replace("tr.children[2]", "tr.children[3]")
    return js


SESSION_OLD = """      var sessionSaved = false;
      var undoStack = [];
      var lastFocusEl = null;"""

SESSION_NEW = """      var sessionSaved = false;
      var undoStack = [];
      var lastFocusEl = null;
      document.addEventListener('kpi:annualPlanChanged', function () {
        if (state.activeTab === 'analyze') renderSalesDataAnalyze();
      });"""

OPEN_OLD = """        state.modalDirty = false;
        sessionSaved = false;
        undoStack = [];
        syncUndoButton();
        if (btnClose) btnClose.focus();
      }

      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        hideSalesDataCloseChooser();"""

OPEN_NEW = """        state.modalDirty = false;
        sessionSaved = false;
        sdmHlAllocWarnShown = false;
        undoStack = [];
        syncUndoButton();
        if (btnClose) btnClose.focus();
      }

      function closeModal() {
        if (window.__KPI_EDIT_LEASE && typeof window.__KPI_EDIT_LEASE.release === 'function') {
          window.__KPI_EDIT_LEASE.release();
        }
        hideSalesDataCloseChooser();"""


def patch_page(path: Path, labels: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text and SDM_HL_STEPPER_MARKER in text and labels["tab_label"] in text:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return

    if MARKER not in text:
        if CSS_OLD not in text:
            raise SystemExit(f"CSS block missing in {path}")
        text = text.replace(CSS_OLD, css_new(), 1)

    text = re.sub(TABLE_OLD_RE, table_html(labels), text, count=1)

    text = text.replace("            Analyze\n", f"            {labels['tab_label']}\n", 1)

    kpi_old_patterns = [
        (
            '<p class="sales-data-modal__analyze-kpi-label">年間入力売上</p>\n'
            '                <p class="sales-data-modal__analyze-kpi-value" id="sales-data-analyze-input-sales">—</p>',
            f'<p class="sales-data-modal__analyze-kpi-label">{labels["kpi_annual_label"]}</p>\n'
            f'                <p class="sales-data-modal__analyze-kpi-value" id="sales-data-analyze-annual-target">—</p>',
        ),
        (
            '<p class="sales-data-modal__analyze-kpi-label">Annual Input Sales</p>\n'
            '                <p class="sales-data-modal__analyze-kpi-value" id="sales-data-analyze-input-sales">—</p>',
            f'<p class="sales-data-modal__analyze-kpi-label">{labels["kpi_annual_label"]}</p>\n'
            f'                <p class="sales-data-modal__analyze-kpi-value" id="sales-data-analyze-annual-target">—</p>',
        ),
    ]
    for old, new in kpi_old_patterns:
        if old in text:
            text = text.replace(old, new, 1)
            break

    for old, new, label in [
        (VARS_OLD, VARS_NEW, "vars"),
        (BUILD_MODEL_OLD, analyze_model_patched(), "model"),
        (RENDER_OLD, RENDER_NEW, "render"),
        (SESSION_OLD, SESSION_NEW, "session"),
        (OPEN_OLD, OPEN_NEW, "open"),
    ]:
        if old in text:
            text = text.replace(old, new, 1)
        elif label == "model" and ANALYZE_MODEL_MARKER in text:
            pattern = (
                re.escape(ANALYZE_MODEL_MARKER)
                + r"[\s\S]*?"
                + re.escape(ANALYZE_MODEL_END)
                + r"\n?"
            )
            text = re.sub(pattern, analyze_model_patched().rstrip() + "\n", text, count=1)
        elif label == "render" and "getSdmHlWeightsForYear(planYear)" in text:
            continue
        elif label == "session" and "kpi:annualPlanChanged" in text and "renderSalesDataAnalyze" in text:
            continue
        elif label == "vars" and "analyzeAllocTotalEl" in text:
            continue
        elif label == "open" and "sdmHlAllocWarnShown = false" in text:
            continue
        else:
            raise SystemExit(f"{label} block missing in {path}")

    if SDM_HL_STEPPER_MARKER not in text:
        anchor = "      function renderSalesDataAnalyze() {"
        block = hl_stepper_js_fixed().rstrip() + "\n\n"
        if anchor not in text:
            raise SystemExit(f"render anchor missing in {path}")
        text = text.replace(anchor, block + anchor, 1)

    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path, labels in PAGES.items():
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path, labels)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

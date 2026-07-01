"""Past Sales Analyze layout — flush year row + table, full-width chart scaling."""

from __future__ import annotations

LAYOUT_MARKER = "psm-analyze-layout-v1"

STACK_OLD = """    .past-sales-modal__analyze-stack {
      display: flex;
      flex-direction: column;
      align-items: stretch;
      width: 100%;
      box-sizing: border-box;
      padding: 24px;
    }
    .past-sales-modal__analyze-data {
      border: 1px solid var(--psm-line);
      background: var(--psm-bg-inactive);
      box-sizing: border-box;
    }"""

STACK_NEW = f"""    .past-sales-modal__analyze-stack {{
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
    }}"""

SEASON_OLD = """    .past-sales-modal__seasonality {
      margin-top: var(--psm-analyze-table-chart-gap, 100px);
      margin-bottom: var(--psm-season-gap-to-outer);
      padding: var(--psm-season-pad-top) 10px var(--psm-season-pad-bottom);
      border: 2px solid #3dff3d;
      background: rgba(0, 0, 0, 0.22);
      box-sizing: border-box;
    }
    .past-sales-modal__seasonality-title {
      margin: 0 0 var(--psm-season-title-to-bar);
      text-align: center;
      font-size: var(--psm-season-title-fs);
      font-weight: 700;
      letter-spacing: 0.04em;
      line-height: 1.2;
    }
    #past-sales-seasonality-bars {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      box-sizing: border-box;
    }
    .past-sales-modal__season-row {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      width: 100%;
      margin: 0 0 var(--psm-season-row-gap);
      min-height: var(--psm-season-bar-h);
    }
    .past-sales-modal__season-row:last-child {
      margin-bottom: 0;
    }
    .past-sales-modal__season-month {
      flex: 0 0 auto;
      margin: 0 var(--psm-season-label-gap-l) 0 0;
      font-size: var(--psm-fs-body);
      font-weight: 600;
      text-align: right;
      white-space: nowrap;
    }
    .past-sales-modal__season-track {
      position: relative;
      flex: 0 0 var(--psm-season-bar-w);
      width: var(--psm-season-bar-w);
      height: var(--psm-season-bar-h);
      background: rgba(88, 225, 243, 0.12);
      border: 1px solid rgba(88, 225, 243, 0.35);
      box-sizing: border-box;
      overflow: visible;
    }"""

SEASON_NEW = f"""    .past-sales-modal__seasonality {{
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
    }}"""

PCT_OLD = """    .past-sales-modal__season-pct {
      flex: 0 0 auto;
      margin: 0 0 0 var(--psm-season-label-gap-r);
      font-size: var(--psm-fs-body);
      font-weight: 600;
      text-align: left;
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }"""

PCT_NEW = """    .past-sales-modal__season-pct {
      margin: 0;
      font-size: var(--psm-fs-body);
      font-weight: 600;
      text-align: left;
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }"""

YM_ANALYZE_OLD = """    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym {
      grid-template-columns: 1fr;
    }"""

YM_ANALYZE_NEW = """    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__ym {
      grid-template-columns: 1fr;
      flex-shrink: 0;
    }"""

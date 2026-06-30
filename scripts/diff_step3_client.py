"""Difference Step 3 — Insight target-vs-actual diff severity CSS."""

from __future__ import annotations

DIFF_STEP3_MARKER = "/* KPI-DIFF-STEP3-INSIGHT-SEVERITY */"

INSIGHT_DIFF_CSS_ANCHOR = """    .office-mode .insight-daily-kpi__label,
    .office-mode .insight-daily-kpi__value,
    .office-mode .insight-monthly-kpi__label,"""

INSIGHT_DIFF_CSS_BLOCK = f"""    {DIFF_STEP3_MARKER}
    .insight-daily-kpi__value.tw-diff--win,
    .insight-monthly-sales-summary__value.tw-diff--win,
    .insight-annual-sales-summary__value.tw-diff--win {{
      color: #58e1f3;
    }}
    .insight-daily-kpi__value.tw-diff--neutral,
    .insight-monthly-sales-summary__value.tw-diff--neutral,
    .insight-annual-sales-summary__value.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .insight-daily-kpi__value.tw-diff--sev-90,
    .insight-monthly-sales-summary__value.tw-diff--sev-90,
    .insight-annual-sales-summary__value.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .insight-daily-kpi__value.tw-diff--sev-80,
    .insight-monthly-sales-summary__value.tw-diff--sev-80,
    .insight-annual-sales-summary__value.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .insight-daily-kpi__value.tw-diff--sev-70,
    .insight-monthly-sales-summary__value.tw-diff--sev-70,
    .insight-annual-sales-summary__value.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .insight-daily-kpi__value.tw-diff--sev-60,
    .insight-monthly-sales-summary__value.tw-diff--sev-60,
    .insight-annual-sales-summary__value.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .insight-daily-kpi__value.tw-diff--sev-50,
    .insight-monthly-sales-summary__value.tw-diff--sev-50,
    .insight-annual-sales-summary__value.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .insight-daily-kpi__value.tw-diff--sev-below,
    .insight-monthly-sales-summary__value.tw-diff--sev-below,
    .insight-annual-sales-summary__value.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--win,
    .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--win {{
      color: #58e1f3;
    }}
    .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--neutral,
    .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--neutral {{
      color: #58e1f3;
    }}
    .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-90,
    .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-80,
    .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-70,
    .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-70 {{
      color: #e65100;
    }}
    .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-60,
    .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-60 {{
      color: #e53935;
    }}
    .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-50,
    .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-50 {{
      color: #c62828;
    }}
    .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-below,
    .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .office-mode .insight-daily-kpi__value.tw-diff--win,
    .office-mode .insight-monthly-sales-summary__value.tw-diff--win,
    .office-mode .insight-annual-sales-summary__value.tw-diff--win {{
      color: #111;
    }}
    .office-mode .insight-daily-kpi__value.tw-diff--neutral,
    .office-mode .insight-monthly-sales-summary__value.tw-diff--neutral,
    .office-mode .insight-annual-sales-summary__value.tw-diff--neutral {{
      color: #111;
    }}
    .office-mode .insight-daily-kpi__value.tw-diff--sev-90,
    .office-mode .insight-monthly-sales-summary__value.tw-diff--sev-90,
    .office-mode .insight-annual-sales-summary__value.tw-diff--sev-90 {{
      color: #e65100;
    }}
    .office-mode .insight-daily-kpi__value.tw-diff--sev-80,
    .office-mode .insight-monthly-sales-summary__value.tw-diff--sev-80,
    .office-mode .insight-annual-sales-summary__value.tw-diff--sev-80 {{
      color: #d84315;
    }}
    .office-mode .insight-daily-kpi__value.tw-diff--sev-70,
    .office-mode .insight-monthly-sales-summary__value.tw-diff--sev-70,
    .office-mode .insight-annual-sales-summary__value.tw-diff--sev-70 {{
      color: #c62828;
    }}
    .office-mode .insight-daily-kpi__value.tw-diff--sev-60,
    .office-mode .insight-monthly-sales-summary__value.tw-diff--sev-60,
    .office-mode .insight-annual-sales-summary__value.tw-diff--sev-60 {{
      color: #b71c1c;
    }}
    .office-mode .insight-daily-kpi__value.tw-diff--sev-50,
    .office-mode .insight-monthly-sales-summary__value.tw-diff--sev-50,
    .office-mode .insight-annual-sales-summary__value.tw-diff--sev-50 {{
      color: #9a0007;
    }}
    .office-mode .insight-daily-kpi__value.tw-diff--sev-below,
    .office-mode .insight-monthly-sales-summary__value.tw-diff--sev-below,
    .office-mode .insight-annual-sales-summary__value.tw-diff--sev-below {{
      color: #7f0000;
    }}
    .office-mode .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--win,
    .office-mode .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--win {{
      color: #111;
    }}
    .office-mode .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--neutral,
    .office-mode .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--neutral {{
      color: #111;
    }}
    .office-mode .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-90,
    .office-mode .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-90 {{
      color: #e65100;
    }}
    .office-mode .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-80,
    .office-mode .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-80 {{
      color: #d84315;
    }}
    .office-mode .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-70,
    .office-mode .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-70 {{
      color: #c62828;
    }}
    .office-mode .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-60,
    .office-mode .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-60 {{
      color: #b71c1c;
    }}
    .office-mode .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-50,
    .office-mode .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-50 {{
      color: #9a0007;
    }}
    .office-mode .insight-graph-monthly-trend__tooltip-value[data-field="diff"].tw-diff--sev-below,
    .office-mode .insight-graph-annual-trend__tooltip-value[data-field="diff"].tw-diff--sev-below {{
      color: #7f0000;
    }}"""

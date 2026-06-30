"""Difference Step 2 — Daily FW + Graph popover diff severity CSS."""

from __future__ import annotations

DIFF_STEP2_MARKER = "/* KPI-DIFF-STEP2-SEVERITY */"

OVERLAY_DIFF_CSS_ANCHOR = """    .daily-overlay__daily-value-box,
    .daily-overlay__monthly-value-box,
    .daily-overlay__annual-value-box {
      width: 480px;
      height: 40px;
      box-sizing: border-box;
      border: 1px solid #58e1f3;
      background: rgba(88, 225, 243, 0.44);
      color: #58e1f3;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Orbitron', sans-serif;
      font-size: 16px;
      line-height: 1;
    }"""

OVERLAY_DIFF_CSS_BLOCK = f"""    .daily-overlay__daily-value-box,
    .daily-overlay__monthly-value-box,
    .daily-overlay__annual-value-box {{
      width: 480px;
      height: 40px;
      box-sizing: border-box;
      border: 1px solid #58e1f3;
      background: rgba(88, 225, 243, 0.44);
      color: #58e1f3;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Orbitron', sans-serif;
      font-size: 16px;
      line-height: 1;
    }}
    {DIFF_STEP2_MARKER}
    .daily-overlay__daily-value-box.tw-diff--win,
    .daily-overlay__monthly-value-box.tw-diff--win,
    .daily-overlay__annual-value-box.tw-diff--win {{
      color: #58e1f3;
    }}
    .daily-overlay__daily-value-box.tw-diff--neutral,
    .daily-overlay__monthly-value-box.tw-diff--neutral,
    .daily-overlay__annual-value-box.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .daily-overlay__daily-value-box.tw-diff--sev-90,
    .daily-overlay__monthly-value-box.tw-diff--sev-90,
    .daily-overlay__annual-value-box.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .daily-overlay__daily-value-box.tw-diff--sev-80,
    .daily-overlay__monthly-value-box.tw-diff--sev-80,
    .daily-overlay__annual-value-box.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .daily-overlay__daily-value-box.tw-diff--sev-70,
    .daily-overlay__monthly-value-box.tw-diff--sev-70,
    .daily-overlay__annual-value-box.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .daily-overlay__daily-value-box.tw-diff--sev-60,
    .daily-overlay__monthly-value-box.tw-diff--sev-60,
    .daily-overlay__annual-value-box.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .daily-overlay__daily-value-box.tw-diff--sev-50,
    .daily-overlay__monthly-value-box.tw-diff--sev-50,
    .daily-overlay__annual-value-box.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .daily-overlay__daily-value-box.tw-diff--sev-below,
    .daily-overlay__monthly-value-box.tw-diff--sev-below,
    .daily-overlay__annual-value-box.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .office-mode .daily-overlay__daily-value-box.tw-diff--win,
    .office-mode .daily-overlay__monthly-value-box.tw-diff--win,
    .office-mode .daily-overlay__annual-value-box.tw-diff--win {{
      color: #111;
    }}
    .office-mode .daily-overlay__daily-value-box.tw-diff--neutral,
    .office-mode .daily-overlay__monthly-value-box.tw-diff--neutral,
    .office-mode .daily-overlay__annual-value-box.tw-diff--neutral {{
      color: #111;
    }}
    .office-mode .daily-overlay__daily-value-box.tw-diff--sev-90,
    .office-mode .daily-overlay__monthly-value-box.tw-diff--sev-90,
    .office-mode .daily-overlay__annual-value-box.tw-diff--sev-90 {{
      color: #e65100;
    }}
    .office-mode .daily-overlay__daily-value-box.tw-diff--sev-80,
    .office-mode .daily-overlay__monthly-value-box.tw-diff--sev-80,
    .office-mode .daily-overlay__annual-value-box.tw-diff--sev-80 {{
      color: #d84315;
    }}
    .office-mode .daily-overlay__daily-value-box.tw-diff--sev-70,
    .office-mode .daily-overlay__monthly-value-box.tw-diff--sev-70,
    .office-mode .daily-overlay__annual-value-box.tw-diff--sev-70 {{
      color: #c62828;
    }}
    .office-mode .daily-overlay__daily-value-box.tw-diff--sev-60,
    .office-mode .daily-overlay__monthly-value-box.tw-diff--sev-60,
    .office-mode .daily-overlay__annual-value-box.tw-diff--sev-60 {{
      color: #b71c1c;
    }}
    .office-mode .daily-overlay__daily-value-box.tw-diff--sev-50,
    .office-mode .daily-overlay__monthly-value-box.tw-diff--sev-50,
    .office-mode .daily-overlay__annual-value-box.tw-diff--sev-50 {{
      color: #9a0007;
    }}
    .office-mode .daily-overlay__daily-value-box.tw-diff--sev-below,
    .office-mode .daily-overlay__monthly-value-box.tw-diff--sev-below,
    .office-mode .daily-overlay__annual-value-box.tw-diff--sev-below {{
      color: #7f0000;
    }}"""

GRAPH_DIFF_CSS_ANCHOR = """    .annual-graph-popover--lose .annual-graph-popover__val-actual,
    .annual-graph-popover--lose .annual-graph-popover__val-diff {
      color: #ff6b6b;
    }
    .annual-graph-popover--win .annual-graph-popover__val-actual,
    .annual-graph-popover--win .annual-graph-popover__val-diff {
      color: #58e1f3;
    }
    .annual-graph-popover--neutral .annual-graph-popover__val-actual,
    .annual-graph-popover--neutral .annual-graph-popover__val-diff {
      color: rgba(88, 225, 243, 0.75);
    }"""

GRAPH_DIFF_CSS_BLOCK = f"""    .annual-graph-popover--lose .annual-graph-popover__val-actual {{
      color: #ff6b6b;
    }}
    .annual-graph-popover--win .annual-graph-popover__val-actual {{
      color: #58e1f3;
    }}
    .annual-graph-popover--neutral .annual-graph-popover__val-actual {{
      color: rgba(88, 225, 243, 0.75);
    }}
    {DIFF_STEP2_MARKER}
    .annual-graph-popover__val-diff.tw-diff--win {{
      color: #58e1f3;
    }}
    .annual-graph-popover__val-diff.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .annual-graph-popover__val-diff.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .annual-graph-popover__val-diff.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .annual-graph-popover__val-diff.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .annual-graph-popover__val-diff.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .annual-graph-popover__val-diff.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .annual-graph-popover__val-diff.tw-diff--sev-below {{
      color: #b71c1c;
    }}"""

GRAPH_OFFICE_DIFF_CSS_ANCHOR = """    .office-mode .annual-graph-popover--lose .annual-graph-popover__val-actual,
    .office-mode .annual-graph-popover--lose .annual-graph-popover__val-diff {
      color: #b00020;
    }
    .office-mode .annual-graph-popover--win .annual-graph-popover__val-actual,
    .office-mode .annual-graph-popover--win .annual-graph-popover__val-diff {
      color: #0d5c24;
    }
    .office-mode .annual-graph-popover--neutral .annual-graph-popover__val-actual,
    .office-mode .annual-graph-popover--neutral .annual-graph-popover__val-diff {
      color: #555;
    }"""

GRAPH_OFFICE_DIFF_CSS_BLOCK = f"""    .office-mode .annual-graph-popover--lose .annual-graph-popover__val-actual {{
      color: #b00020;
    }}
    .office-mode .annual-graph-popover--win .annual-graph-popover__val-actual {{
      color: #0d5c24;
    }}
    .office-mode .annual-graph-popover--neutral .annual-graph-popover__val-actual {{
      color: #555;
    }}
    .office-mode .annual-graph-popover__val-diff.tw-diff--win {{
      color: #111;
    }}
    .office-mode .annual-graph-popover__val-diff.tw-diff--neutral {{
      color: #111;
    }}
    .office-mode .annual-graph-popover__val-diff.tw-diff--sev-90 {{
      color: #e65100;
    }}
    .office-mode .annual-graph-popover__val-diff.tw-diff--sev-80 {{
      color: #d84315;
    }}
    .office-mode .annual-graph-popover__val-diff.tw-diff--sev-70 {{
      color: #c62828;
    }}
    .office-mode .annual-graph-popover__val-diff.tw-diff--sev-60 {{
      color: #b71c1c;
    }}
    .office-mode .annual-graph-popover__val-diff.tw-diff--sev-50 {{
      color: #9a0007;
    }}
    .office-mode .annual-graph-popover__val-diff.tw-diff--sev-below {{
      color: #7f0000;
    }}"""

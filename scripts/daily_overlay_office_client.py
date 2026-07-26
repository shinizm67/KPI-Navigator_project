"""Daily Floating Window (#daily-overlay) — Office Mode shell (match Insight tonmana)."""

MARKER = "/* KPI-DAILY-OVERLAY-OFFICE */"
MARKER_END = "/* /KPI-DAILY-OVERLAY-OFFICE */"

STICKY_HEAD_OLD = """    .office-mode .daily-overlay__sticky-head {
      background: rgba(9, 12, 17, 0.98);
    }"""

STICKY_HEAD_NEW = """    .office-mode .daily-overlay__sticky-head {
      background: #f0f0f0;
    }"""

PANEL_OFFICE_OLD = """    .office-mode .daily-overlay__panel {
      border-color: rgba(88, 225, 243, 0.75);
      box-shadow: 0 0 20px rgba(88, 225, 243, 0.18);
    }"""

# Align with Insight Office shell: #555 frame, #f0f0f0 bg, #111 text/lines, white boxes.
PANEL_OFFICE_NEW = f"""    {MARKER}
    body.office-mode .daily-overlay__backdrop {{
      background: rgba(0, 0, 0, 0.28);
    }}
    body.office-mode .daily-overlay__panel {{
      border: 3px solid #555;
      background: #f0f0f0;
      box-shadow: none;
      color: #111;
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .daily-overlay__panel *:not(svg):not(svg *) {{
      color: #111 !important;
    }}
    body.office-mode .daily-overlay__panel *:not(svg):not(svg *):not([class*="tri"]):not([class*="triangle"]) {{
      border-color: #111 !important;
    }}
    body.office-mode .daily-overlay__panel {{
      border-color: #555 !important;
      color: #111 !important;
    }}
    body.office-mode .daily-overlay__panel *,
    html[lang="en"] body.office-mode .daily-overlay__panel * {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .daily-overlay__close {{
      border: 1px solid #111 !important;
      background: #d0d0d0 !important;
      color: #111 !important;
      box-shadow: none;
    }}
    body.office-mode .daily-overlay__close:hover,
    body.office-mode .daily-overlay__close:focus-visible {{
      background: #c0c0c0 !important;
      outline: none;
    }}
    body.office-mode .daily-overlay__sticky-head {{
      background: #f0f0f0 !important;
    }}
    body.office-mode .daily-overlay__scroll {{
      background: #f0f0f0;
      color: #111;
    }}
    body.office-mode .daily-overlay__date-nav,
    body.office-mode .daily-overlay__date-btn {{
      color: #111 !important;
      background: transparent;
    }}
    body.office-mode .daily-overlay__today {{
      border: 1px solid #111 !important;
      background: #d0d0d0 !important;
      color: #111 !important;
      box-shadow: none;
    }}
    body.office-mode .daily-overlay__today:hover,
    body.office-mode .daily-overlay__today:focus-visible {{
      background: #c0c0c0 !important;
    }}
    body.office-mode .daily-overlay__sticky-head::after {{
      border-top-color: #111 !important;
    }}
    body.office-mode .daily-overlay__vline,
    body.office-mode .daily-overlay__hline {{
      border-color: #111 !important;
    }}
    body.office-mode .daily-overlay__vlabel {{
      color: #111 !important;
    }}
    body.office-mode .daily-overlay__daily-title,
    body.office-mode .daily-overlay__monthly-title,
    body.office-mode .daily-overlay__annual-title {{
      color: #111 !important;
    }}
    body.office-mode .daily-overlay__daily-value-box,
    body.office-mode .daily-overlay__monthly-value-box,
    body.office-mode .daily-overlay__annual-value-box {{
      border: 1px solid #111 !important;
      background: #fff !important;
      color: #111 !important;
      box-shadow: none;
    }}
    body.office-mode .daily-overlay__daily-graph-title,
    body.office-mode .daily-overlay__monthly-graph-title,
    body.office-mode .daily-overlay__annual-graph-title,
    body.office-mode .daily-overlay__daily-graph-rate,
    body.office-mode .daily-overlay__monthly-graph-rate,
    body.office-mode .daily-overlay__annual-graph-rate {{
      color: #111 !important;
    }}
    body.office-mode .daily-overlay__daily-graph-track,
    body.office-mode .daily-overlay__monthly-graph-track,
    body.office-mode .daily-overlay__annual-graph-track {{
      border-color: #111 !important;
      background: #e0e0e0 !important;
      box-shadow: none;
    }}
    body.office-mode .daily-overlay__daily-graph-fill,
    body.office-mode .daily-overlay__monthly-graph-fill,
    body.office-mode .daily-overlay__annual-graph-fill {{
      background: #bdbdbd !important;
      box-shadow: none;
    }}
    body.office-mode .daily-overlay__daily-graph-target-line,
    body.office-mode .daily-overlay__monthly-graph-target-line,
    body.office-mode .daily-overlay__annual-graph-target-line {{
      background: #e6ff00 !important;
      box-shadow: none;
    }}
    /* CSS triangles: keep marker yellow (same as Insight Office). */
    body.office-mode .daily-overlay__panel [class*="tri"],
    body.office-mode .daily-overlay__panel [class*="triangle"] {{
      border-left-color: transparent !important;
      border-right-color: transparent !important;
      border-bottom-color: transparent !important;
      border-top-color: var(--marker-color, #e6ff00) !important;
      color: transparent !important;
      filter: none;
    }}
    /* Keep TW / severity colors readable. */
    body.office-mode .daily-overlay__daily-value-box.tw-diff--win,
    body.office-mode .daily-overlay__monthly-value-box.tw-diff--win,
    body.office-mode .daily-overlay__annual-value-box.tw-diff--win {{
      color: #0f9403 !important;
    }}
    body.office-mode .daily-overlay__daily-value-box.tw-diff--neutral,
    body.office-mode .daily-overlay__monthly-value-box.tw-diff--neutral,
    body.office-mode .daily-overlay__annual-value-box.tw-diff--neutral {{
      color: #333 !important;
    }}
    body.office-mode .daily-overlay__daily-value-box.tw-diff--sev-90,
    body.office-mode .daily-overlay__monthly-value-box.tw-diff--sev-90,
    body.office-mode .daily-overlay__annual-value-box.tw-diff--sev-90 {{
      color: #b71c1c !important;
    }}
    body.office-mode .daily-overlay__daily-value-box.tw-diff--sev-80,
    body.office-mode .daily-overlay__monthly-value-box.tw-diff--sev-80,
    body.office-mode .daily-overlay__annual-value-box.tw-diff--sev-80 {{
      color: #c62828 !important;
    }}
    body.office-mode .daily-overlay__daily-value-box.tw-diff--sev-70,
    body.office-mode .daily-overlay__monthly-value-box.tw-diff--sev-70,
    body.office-mode .daily-overlay__annual-value-box.tw-diff--sev-70 {{
      color: #d32f2f !important;
    }}
    body.office-mode .daily-overlay__daily-value-box.tw-diff--sev-60,
    body.office-mode .daily-overlay__monthly-value-box.tw-diff--sev-60,
    body.office-mode .daily-overlay__annual-value-box.tw-diff--sev-60 {{
      color: #e53935 !important;
    }}
    body.office-mode .daily-overlay__daily-value-box.tw-diff--sev-50,
    body.office-mode .daily-overlay__monthly-value-box.tw-diff--sev-50,
    body.office-mode .daily-overlay__annual-value-box.tw-diff--sev-50 {{
      color: #9a0007 !important;
    }}
    body.office-mode .daily-overlay__daily-value-box.tw-diff--sev-below,
    body.office-mode .daily-overlay__monthly-value-box.tw-diff--sev-below,
    body.office-mode .daily-overlay__annual-value-box.tw-diff--sev-below {{
      color: #7f0000 !important;
    }}
    {MARKER_END}"""

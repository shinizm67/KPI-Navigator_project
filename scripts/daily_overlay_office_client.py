"""Daily Floating Window (#daily-overlay) — Office Mode monotone CSS."""

MARKER = "/* KPI-DAILY-OVERLAY-OFFICE */"

STICKY_HEAD_OLD = """    .office-mode .daily-overlay__sticky-head {
      background: rgba(9, 12, 17, 0.98);
    }"""

STICKY_HEAD_NEW = """    .office-mode .daily-overlay__sticky-head {
      background: #ececec;
    }"""

PANEL_OFFICE_OLD = """    .office-mode .daily-overlay__panel {
      border-color: rgba(88, 225, 243, 0.75);
      box-shadow: 0 0 20px rgba(88, 225, 243, 0.18);
    }"""

PANEL_OFFICE_NEW = f"""    {MARKER}
    body.office-mode .daily-overlay__backdrop {{
      background: rgba(0, 0, 0, 0.42);
    }}
    body.office-mode .daily-overlay__panel {{
      border: 3px solid #666;
      background: #f5f5f5;
      box-shadow: 0 4px 22px rgba(0, 0, 0, 0.16);
      color: #111;
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .daily-overlay__panel *,
    html[lang="en"] body.office-mode .daily-overlay__panel * {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    body.office-mode .daily-overlay__close {{
      border: 1px solid #666;
      background: #fff;
      color: #111;
    }}
    body.office-mode .daily-overlay__close:hover,
    body.office-mode .daily-overlay__close:focus-visible {{
      background: #ececec;
      outline: none;
    }}
    body.office-mode .daily-overlay__date-nav,
    body.office-mode .daily-overlay__date-btn {{
      color: #111;
    }}
    body.office-mode .daily-overlay__today {{
      border: 1px solid #666;
      background: #fff;
      color: #111;
    }}
    body.office-mode .daily-overlay__today:hover,
    body.office-mode .daily-overlay__today:focus-visible {{
      background: #ececec;
    }}
    body.office-mode .daily-overlay__sticky-head::after {{
      border-top-color: #666;
    }}
    body.office-mode .daily-overlay__vline {{
      border-left-color: #666;
    }}
    body.office-mode .daily-overlay__hline {{
      border-top-color: #666;
    }}
    body.office-mode .daily-overlay__vlabel {{
      color: #111;
    }}
    body.office-mode .daily-overlay__daily-title,
    body.office-mode .daily-overlay__monthly-title,
    body.office-mode .daily-overlay__annual-title {{
      color: #111;
    }}
    body.office-mode .daily-overlay__daily-value-box,
    body.office-mode .daily-overlay__monthly-value-box,
    body.office-mode .daily-overlay__annual-value-box {{
      border: 1px solid #666;
      background: #fff;
      color: #111;
    }}
    body.office-mode .daily-overlay__daily-graph-title,
    body.office-mode .daily-overlay__monthly-graph-title,
    body.office-mode .daily-overlay__annual-graph-title,
    body.office-mode .daily-overlay__daily-graph-rate {{
      color: #111;
    }}"""

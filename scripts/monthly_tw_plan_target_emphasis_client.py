"""Monthly Table Window (Income grid) — Plan Target Sales row emphasis."""

from __future__ import annotations

from tw_daily_target_emphasis_client import (
    _OFFICE_HEADER_FG,
    _OFFICE_TARGET_BG,
    _OFFICE_TARGET_FG,
    _SCIFI_TARGET_BG,
    _SCIFI_TARGET_BG_FB,
    _SCIFI_TARGET_FG,
)

MONTHLY_TW_PLAN_TARGET_MARKER = "/* KPI-MONTHLY-TW-PLAN-TARGET-EMPHASIS */"
MONTHLY_TW_PLAN_TARGET_END = "/* END KPI-MONTHLY-TW-PLAN-TARGET-EMPHASIS */"
MONTHLY_TW_PLAN_TARGET_ANCHOR = "/* KPI-MONTHLY-TW-DIFF-SEVERITY */"

DECORATE_OLD = """      function decorateMonthlyGroup1Cell(cell, cellIndex, iso) {
        if (!cell || cellIndex !== 4) return;
        var snap = readGroup1TwSnapshot(iso);
        applyMonthlyTwDiffClass(cell, snap.diffActual, snap.diffTarget);
      }"""

DECORATE_NEW = """      function decorateMonthlyGroup1Cell(cell, cellIndex, iso) {
        if (!cell) return;
        if (cellIndex === 3) {
          cell.classList.add('monthly-data-column__cell--plan-target');
        }
        if (cellIndex !== 4) return;
        var snap = readGroup1TwSnapshot(iso);
        applyMonthlyTwDiffClass(cell, snap.diffActual, snap.diffTarget);
      }"""

VFOCUS_CELL_COPY_OLD = """              if (cell) {
                cell.textContent = valuesLane[gi2 * 6 + ci2] || demoMoney;
                if (gi2 === 0 && ci2 === 4) {
                  syncMonthlyVfocusDiffClass(cell, colIdx);
                } else if (gi2 === 0) {
                  clearMonthlyTwDiffClasses(cell);
                }
              }"""

VFOCUS_CELL_COPY_NEW = """              if (cell) {
                cell.textContent = valuesLane[gi2 * 6 + ci2] || demoMoney;
                if (gi2 === 0 && ci2 === 4) {
                  cell.classList.remove('monthly-vfocus-cell--plan-target');
                  syncMonthlyVfocusDiffClass(cell, colIdx);
                } else if (gi2 === 0 && ci2 === 3) {
                  clearMonthlyTwDiffClasses(cell);
                  cell.classList.add('monthly-vfocus-cell--plan-target');
                } else if (gi2 === 0) {
                  clearMonthlyTwDiffClasses(cell);
                  cell.classList.remove('monthly-vfocus-cell--plan-target');
                } else {
                  cell.classList.remove('monthly-vfocus-cell--plan-target');
                }
              }"""

LISTENERS_OLD = """      document.addEventListener('kpi:businessDayChanged', monthlyTwRebuildKeepFocus);
      /* END KPI-MONTHLY-TW-LISTENERS */"""

LISTENERS_NEW = """      document.addEventListener('kpi:businessDayChanged', monthlyTwRebuildKeepFocus);
      document.addEventListener('kpi:dailyTargetModeChanged', monthlyTwRebuildKeepFocus);
      document.addEventListener('kpi:weekdayBaselineChanged', monthlyTwRebuildKeepFocus);
      /* END KPI-MONTHLY-TW-LISTENERS */"""


def monthly_tw_plan_target_emphasis_css() -> str:
    return f"""    {MONTHLY_TW_PLAN_TARGET_MARKER}
    .monthly-data-column__cell.monthly-data-column__cell--plan-target {{
      font-weight: 700;
      font-size: 14px;
      background: {_SCIFI_TARGET_BG};
      color: {_SCIFI_TARGET_FG};
    }}
    .monthly-data-column--off:not(.monthly-data-column--buffer) .monthly-data-column__cell--plan-target,
    .monthly-data-column--buffer .monthly-data-column__cell--plan-target {{
      font-weight: 600;
      font-size: 13px;
      background: transparent;
      color: inherit;
    }}
    .monthly-vfocus-cell.monthly-vfocus-cell--plan-target {{
      font-weight: 700;
      font-size: 16px;
      background: {_SCIFI_TARGET_BG_FB};
      color: {_SCIFI_TARGET_FG};
    }}
    /* vFocus 中央レーン: 非 Target は控えめ（Annual Focus Bar 下段と同系） */
    body:not(.office-mode)
      .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer)
      .monthly-vfocus-cell:not(.monthly-vfocus-cell--plan-target) {{
      background: rgba(114, 117, 117, 0.12);
      color: #58e1f3;
      font-weight: 400;
      font-size: 15px;
    }}
    body:not(.office-mode)
      .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer)
      .monthly-vfocus-cell.monthly-vfocus-cell--plan-target {{
      background: {_SCIFI_TARGET_BG_FB};
      color: {_SCIFI_TARGET_FG};
      font-weight: 700;
      font-size: 16px;
    }}
    body:not(.office-mode)
      .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer)
      .monthly-vfocus-profit-bottom {{
      background: rgba(114, 117, 117, 0.14);
      border-color: #58e1f3;
      color: #58e1f3;
    }}
    .monthly-vfocus-lane--tw-off .monthly-vfocus-cell--plan-target,
    .monthly-vfocus-lane--tw-buffer .monthly-vfocus-cell--plan-target {{
      font-weight: 600;
      font-size: 15px;
      background: transparent;
      color: inherit;
    }}
    .monthly-table-window__metric-col .monthly-table-window__metric-line:nth-child(4) {{
      font-weight: 700;
      color: {_SCIFI_TARGET_FG};
    }}
    .office-mode .monthly-data-column__cell.monthly-data-column__cell--plan-target {{
      font-weight: 700;
      font-size: 14px;
      background: {_OFFICE_TARGET_BG};
      color: {_OFFICE_TARGET_FG};
    }}
    .office-mode .monthly-data-column--off:not(.monthly-data-column--buffer) .monthly-data-column__cell--plan-target,
    .office-mode .monthly-data-column--buffer .monthly-data-column__cell--plan-target {{
      font-weight: 600;
      font-size: 13px;
      background: transparent;
      color: inherit;
    }}
    .office-mode .monthly-vfocus-cell.monthly-vfocus-cell--plan-target {{
      font-weight: 700;
      font-size: 16px;
      background: {_OFFICE_TARGET_BG};
      color: {_OFFICE_TARGET_FG};
    }}
    .office-mode
      .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer)
      .monthly-vfocus-cell:not(.monthly-vfocus-cell--plan-target) {{
      background: rgba(0, 0, 0, 0.04);
      color: #111;
      font-weight: 400;
      font-size: 15px;
    }}
    .office-mode
      .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer)
      .monthly-vfocus-cell.monthly-vfocus-cell--plan-target {{
      background: {_OFFICE_TARGET_BG};
      color: {_OFFICE_TARGET_FG};
      font-weight: 700;
      font-size: 16px;
    }}
    .office-mode
      .monthly-vfocus-lane--center:not(.monthly-vfocus-lane--tw-off):not(.monthly-vfocus-lane--tw-buffer)
      .monthly-vfocus-profit-bottom {{
      background: #f5f5f5;
      border-color: #bbb;
      color: #111;
    }}
    .office-mode .monthly-vfocus-lane--tw-off .monthly-vfocus-cell--plan-target,
    .office-mode .monthly-vfocus-lane--tw-buffer .monthly-vfocus-cell--plan-target {{
      font-weight: 600;
      font-size: 15px;
      background: transparent;
      color: inherit;
    }}
    .office-mode .monthly-table-window__metric-col .monthly-table-window__metric-line:nth-child(4) {{
      font-weight: 700;
      color: {_OFFICE_HEADER_FG};
    }}
    {MONTHLY_TW_PLAN_TARGET_END}"""

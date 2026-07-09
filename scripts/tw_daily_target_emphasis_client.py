"""TW plan Target Sales columns — subtle visual emphasis (Daily / Monthly / Annual)."""

from __future__ import annotations

TW_DAILY_TARGET_EMPHASIS_MARKER = "/* KPI-TW-DAILY-TARGET-EMPHASIS */"
TW_DAILY_TARGET_EMPHASIS_END = "/* END KPI-TW-DAILY-TARGET-EMPHASIS */"

TW_DAILY_TARGET_EMPHASIS_ANCHOR = "/* KPI-TW-DIFF-SEVERITY */"

# Sci-Fi: ~30% darker than initial pass (0.28→0.20, 0.34→0.24)
_SCIFI_TARGET_BG = "rgba(88, 225, 243, 0.20)"
_SCIFI_TARGET_BG_FB = "rgba(88, 225, 243, 0.24)"
_SCIFI_TARGET_FG = "#a8e8f5"

# Office: ~30% darker tint
_OFFICE_TARGET_BG = "#c5dce8"
_OFFICE_TARGET_FG = "#0a3d7a"
_OFFICE_HEADER_FG = "#1256a8"


def tw_daily_target_emphasis_css() -> str:
    tw_target_rows = """
    .annual-daily-row__group--base .annual-daily-row__cell--plan-target,
    .annual-daily-row__group--monthly .annual-daily-row__cell--plan-target,
    .annual-daily-row__group--annual .annual-daily-row__cell--plan-target {
      font-weight: 700;
      font-size: 12px;
      background: %s;
      color: %s;
    }
    .annual-daily-row__cell.annual-daily-row__cell--plan-target.kpi-fill-has,
    .annual-daily-row__cell.annual-daily-row__cell--plan-target.kpi-fill-empty {
      background: %s;
    }""" % (
        _SCIFI_TARGET_BG,
        _SCIFI_TARGET_FG,
        _SCIFI_TARGET_BG,
    )

    tw_target_muted = """
    .annual-daily-row--off .annual-daily-row__cell--plan-target,
    .annual-daily-row--outside-year .annual-daily-row__cell--plan-target {
      font-weight: 600;
      font-size: 11px;
      background: transparent;
      color: inherit;
    }"""

    fb_upper = """
    .annual-daily-focus-bar-upper__group--base .annual-daily-focus-bar-upper__cell:nth-child(3),
    .annual-daily-focus-bar-upper__group--monthly .annual-daily-focus-bar-upper__cell:nth-child(1),
    .annual-daily-focus-bar-upper__group--annual .annual-daily-focus-bar-upper__cell:nth-child(1) {
      font-weight: 700;
      color: %s;
    }""" % (_SCIFI_TARGET_FG,)

    fb_lower = """
    .annual-daily-focus-bar-lower__group--base .annual-daily-focus-bar-lower__cell:nth-child(3),
    .annual-daily-focus-bar-lower__group--monthly .annual-daily-focus-bar-lower__cell:nth-child(1),
    .annual-daily-focus-bar-lower__group--annual .annual-daily-focus-bar-lower__cell:nth-child(1) {
      font-weight: 700;
      font-size: 16px;
      background: %s;
      color: %s;
    }""" % (
        _SCIFI_TARGET_BG_FB,
        _SCIFI_TARGET_FG,
    )

    office_rows = """
    .office-mode .annual-daily-row__group--base .annual-daily-row__cell--plan-target,
    .office-mode .annual-daily-row__group--monthly .annual-daily-row__cell--plan-target,
    .office-mode .annual-daily-row__group--annual .annual-daily-row__cell--plan-target {
      font-weight: 700;
      font-size: 12px;
      background: %s;
      color: %s;
    }
    .office-mode .annual-daily-row__cell.annual-daily-row__cell--plan-target.kpi-fill-has,
    .office-mode .annual-daily-row__cell.annual-daily-row__cell--plan-target.kpi-fill-empty {
      background: %s;
    }""" % (
        _OFFICE_TARGET_BG,
        _OFFICE_TARGET_FG,
        _OFFICE_TARGET_BG,
    )

    office_muted = """
    .office-mode .annual-daily-row--off .annual-daily-row__cell--plan-target,
    .office-mode .annual-daily-row--outside-year .annual-daily-row__cell--plan-target {
      font-weight: 600;
      font-size: 11px;
      background: transparent;
      color: inherit;
    }"""

    office_fb_upper = """
    .office-mode .annual-daily-focus-bar-upper__group--base .annual-daily-focus-bar-upper__cell:nth-child(3),
    .office-mode .annual-daily-focus-bar-upper__group--monthly .annual-daily-focus-bar-upper__cell:nth-child(1),
    .office-mode .annual-daily-focus-bar-upper__group--annual .annual-daily-focus-bar-upper__cell:nth-child(1) {
      font-weight: 700;
      color: %s;
    }""" % (_OFFICE_HEADER_FG,)

    office_fb_lower = """
    .office-mode .annual-daily-focus-bar-lower__group--base .annual-daily-focus-bar-lower__cell:nth-child(3),
    .office-mode .annual-daily-focus-bar-lower__group--monthly .annual-daily-focus-bar-lower__cell:nth-child(1),
    .office-mode .annual-daily-focus-bar-lower__group--annual .annual-daily-focus-bar-lower__cell:nth-child(1) {
      font-weight: 700;
      font-size: 16px;
      background: %s;
      color: %s;
    }""" % (
        _OFFICE_TARGET_BG,
        _OFFICE_TARGET_FG,
    )

    return f"""    {TW_DAILY_TARGET_EMPHASIS_MARKER}
{tw_target_rows}
{tw_target_muted}
{fb_upper}
{fb_lower}
{office_rows}
{office_muted}
{office_fb_upper}
{office_fb_lower}
    {TW_DAILY_TARGET_EMPHASIS_END}"""

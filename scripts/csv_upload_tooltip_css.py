"""CSS for CSV upload button hover tooltips (data-tooltip + ::after)."""

from __future__ import annotations

import re

CSV_UPLOAD_TOOLTIP_MARKER = "/* KPI-CSV-UPLOAD-TOOLTIP */"
CSV_UPLOAD_TOOLTIP_END = "/* END KPI-CSV-UPLOAD-TOOLTIP */"


def _tooltip_after(*selectors: str, line_var: str, color_var: str) -> str:
    joined = ",\n".join(selectors)
    hover = ",\n".join(s + ":hover::after" for s in selectors)
    focus = ",\n".join(s + ":focus-visible::after" for s in selectors)
    return f"""    {joined} {{
      z-index: 2;
    }}
    {hover},
    {focus} {{
      content: attr(data-tooltip);
      position: absolute;
      left: 50%;
      top: calc(100% + 8px);
      transform: translateX(-50%);
      padding: 8px 10px;
      border: 1px solid var({line_var});
      border-radius: 3px;
      background: #102932;
      color: var({color_var});
      font-size: 12px;
      font-weight: 400;
      line-height: 1.45;
      text-align: left;
      white-space: normal;
      width: max-content;
      max-width: min(300px, 85vw);
      z-index: 200;
      pointer-events: none;
      box-shadow: 0 4px 14px rgba(16, 0, 82, 0.35);
    }}"""


def annual_csv_upload_tooltip_css() -> str:
    psm = _tooltip_after(
        ".past-sales-modal__csv[data-tooltip]",
        line_var="--psm-line",
        color_var="--psm-cyan",
    )
    sdm = _tooltip_after(
        ".sales-data-modal__csv[data-tooltip]",
        line_var="--sdm-line",
        color_var="--sdm-cyan",
    )
    aem = _tooltip_after(
        ".annual-edit-modal__csv[data-tooltip]",
        line_var="--aem-line",
        color_var="--aem-cyan",
    )
    return (
        f"    {CSV_UPLOAD_TOOLTIP_MARKER}\n"
        f"{psm}\n"
        f"{sdm}\n"
        f"{aem}\n"
        f"    {CSV_UPLOAD_TOOLTIP_END}\n"
    )


def monthly_csv_upload_tooltip_css() -> str:
    block = _tooltip_after(
        ".monthly-edit-float__csv-upload[data-tooltip]",
        line_var="--mef-line",
        color_var="--mef-cyan",
    )
    return (
        f"    {CSV_UPLOAD_TOOLTIP_MARKER}\n"
        f"{block}\n"
        f"    {CSV_UPLOAD_TOOLTIP_END}\n"
    )


def pl_csv_upload_tooltip_css() -> str:
    block = _tooltip_after(
        "#pl-csv-upload[data-tooltip]",
        line_var="--pl-cyan",
        color_var="--pl-cyan",
    )
    return (
        f"    {CSV_UPLOAD_TOOLTIP_MARKER}\n"
        f"{block}\n"
        f"    {CSV_UPLOAD_TOOLTIP_END}\n"
    )


def inject_or_replace_css(text: str, css_block: str, insert_before: str) -> str:
    pattern = (
        re.escape(CSV_UPLOAD_TOOLTIP_MARKER)
        + r"[\s\S]*?"
        + re.escape(CSV_UPLOAD_TOOLTIP_END)
        + r"\n?"
    )
    if CSV_UPLOAD_TOOLTIP_MARKER in text:
        return re.sub(pattern, css_block.rstrip() + "\n", text, count=1)
    if insert_before not in text:
        raise SystemExit(f"CSS insert anchor missing: {insert_before!r}")
    return text.replace(insert_before, css_block + insert_before, 1)

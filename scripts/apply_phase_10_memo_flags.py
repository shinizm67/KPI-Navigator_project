#!/usr/bin/env python3
"""Phase 10-a/b — daily memo flag read API + TW date-cell markers."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

STORE_PAGES = PAGES + [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

MARKER = "/* KPI-PHASE-10-MEMO-MARKER-CSS */"

CSS_ANCHOR = """    .annual-daily-row__cell--date {
      text-align: left;
      justify-content: flex-start;
      padding-left: 8px;
    }"""

CSS_NEW = f"""    .annual-daily-row__cell--date {{
      text-align: left;
      justify-content: flex-start;
      padding-left: 8px;
    }}
    {MARKER}
    .annual-daily-row__cell--date.annual-daily-row__cell--has-memo {{
      position: relative;
      padding-right: 14px;
    }}
    .annual-daily-row__cell--date.annual-daily-row__cell--has-memo::after {{
      content: '';
      position: absolute;
      right: 5px;
      top: 50%;
      width: 6px;
      height: 6px;
      margin-top: -3px;
      border-radius: 50%;
      background: #58e1f3;
      box-shadow: 0 0 4px rgba(88, 225, 243, 0.65);
      pointer-events: none;
    }}
    body.office-mode .annual-daily-row__cell--date.annual-daily-row__cell--has-memo::after {{
      background: #1565c0;
      box-shadow: none;
    }}"""

MEP_LISTENER_OLD = """      document.addEventListener('kpi:weekdayBaselineChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastSalesSaved', function () {"""

MEP_LISTENER_NEW = """      document.addEventListener('kpi:weekdayBaselineChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('kpi:mepDataChanged', function () {
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });
      });
      document.addEventListener('annual:pastSalesSaved', function () {"""


def patch_css(text: str) -> str:
    if MARKER in text:
        return text
    if CSS_ANCHOR not in text:
        raise SystemExit("TW date cell CSS anchor missing")
    return text.replace(CSS_ANCHOR, CSS_NEW, 1)


def patch_mep_listener(text: str) -> str:
    if "document.addEventListener('kpi:mepDataChanged', function () {" in text:
        if "scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });" in text:
            return text
    if MEP_LISTENER_OLD in text:
        return text.replace(MEP_LISTENER_OLD, MEP_LISTENER_NEW, 1)
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_css(text)
    text = patch_mep_listener(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in STORE_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1

    store_script = _SCRIPTS / "apply_kpi_year_store_block_only.py"
    tw_script = _SCRIPTS / "apply_focus_tw_metrics.py"

    for path in PAGES:
        patch_page(path)

    subprocess.run([sys.executable, str(store_script)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(tw_script)], cwd=ROOT, check=True)

    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if "readDailyMemoFlagMapForYear" not in text:
            print(f"warn: store API not in {path.name} — check store block", file=sys.stderr)
        if "annual-daily-row__cell--has-memo" not in text:
            print(f"warn: memo marker missing in {path.name}", file=sys.stderr)
        if MARKER not in text:
            print(f"warn: memo CSS marker missing in {path.name}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

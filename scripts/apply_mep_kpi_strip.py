#!/usr/bin/env python3
"""Wire MEP Analyze KPI strip to Cockpit-aligned cumulative TW metrics."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from focus_tw_metrics_client import (  # noqa: E402
    FOCUS_TW_END,
    FOCUS_TW_MARKER,
    focus_tw_metrics_js,
)
from mep_kpi_strip_client import (  # noqa: E402
    IS_TIMELINE_BIZ_DAY,
    MEP_KPI_STRIP_END,
    MEP_KPI_STRIP_MARKER,
    mep_kpi_strip_js,
)

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

GET_KPI_OLD = re.compile(
    r"      function getKpiSummary\(\) \{[\s\S]*?\n      \}\n      function getKpiStripDummySummary\(\)",
    re.MULTILINE,
)

GET_KPI_NEW_SUFFIX = (
    mep_kpi_strip_js().rstrip()
    + "\n      function getKpiStripDummySummary()"
)

INIT_OLD = """        buildGrid();
        confirmedSnapshot = buildConfirmedSnapshot();"""

INIT_NEW = """        bindMepKpiStripRefresh();
        buildGrid();
        confirmedSnapshot = buildConfirmedSnapshot();"""


def inject_focus_tw(text: str) -> str:
    if FOCUS_TW_MARKER in text:
        return text
    anchor = "      function sumTargetByDateRange(startDate, endDate) {"
    if anchor not in text:
        raise SystemExit("sumTargetByDateRange anchor not found")
    is_ja = "      var isJa = useJa;\n"
    biz = IS_TIMELINE_BIZ_DAY + "\n\n"
    block = is_ja + biz + focus_tw_metrics_js().rstrip() + "\n\n"
    return text.replace(anchor, block + anchor, 1)


def replace_get_kpi_summary(text: str) -> str:
    if MEP_KPI_STRIP_MARKER in text:
        pattern = (
            r"[\t ]*"
            + re.escape(MEP_KPI_STRIP_MARKER)
            + r"[\s\S]*?"
            + re.escape(MEP_KPI_STRIP_END)
            + r"\n?"
        )
        text = re.sub(pattern, mep_kpi_strip_js().rstrip() + "\n", text, count=1)
        return text
    m = GET_KPI_OLD.search(text)
    if not m:
        raise SystemExit("getKpiSummary block not found")
    return GET_KPI_OLD.sub(GET_KPI_NEW_SUFFIX, text, count=1)


def patch_init(text: str) -> str:
    if "bindMepKpiStripRefresh();" in text:
        return text
    if INIT_OLD not in text:
        raise SystemExit("initEditPage buildGrid anchor not found")
    return text.replace(INIT_OLD, INIT_NEW, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_focus_tw(text)
    text = replace_get_kpi_summary(text)
    text = patch_init(text)
    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing {path}")
        patch_page(path)


if __name__ == "__main__":
    main()

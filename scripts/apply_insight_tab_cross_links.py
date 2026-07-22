#!/usr/bin/env python3
"""Wire Insight Summary/Analyze ▶ Graph and Graph ▶ Analyze cross-tab jumps."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (Path(__file__).resolve().parent / "_insight_tab_cross_links.js").read_text(encoding="utf-8")

TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

GRAPH_HREF_BY_ID = {
    "insight-daily-summary-graph-link": "#insight-jump-graph-daily",
    "insight-monthly-comparison-graph-link": "#insight-jump-graph-monthly",
    "insight-annual-comparison-graph-link": "#insight-jump-graph-annual",
    "insight-annual-target-revision-graph-link": "#insight-jump-graph-annual",
    "insight-analyze-daily-graph-link": "#insight-jump-graph-daily",
    "insight-analyze-monthly-graph-link": "#insight-jump-graph-monthly",
    "insight-analyze-annual-graph-link": "#insight-jump-graph-annual",
}

MARKER = "/* INSIGHT-TAB-CROSS-LINKS */"
INJECT_AFTER = "      bindInsightJumpLink(jumpAnnual);"

POPOVER_HANDLER = re.compile(
    r"\n      var insightDailySummaryGraphLink = document\.getElementById\('insight-daily-summary-graph-link'\);\n"
    r"      if \(insightDailySummaryGraphLink\) \{\n"
    r"        insightDailySummaryGraphLink\.addEventListener\('click', function \(ev\) \{\n"
    r"          ev\.preventDefault\(\);\n"
    r"          ev\.stopPropagation\(\);\n"
    r"          if \(!root\.hidden && activeTriggerBtn === insightDailySummaryGraphLink\) \{\n"
    r"            closePopover\(\);\n"
    r"            return;\n"
    r"          \}\n"
    r"          if \(window\.__ANNUAL_UI && typeof window\.__ANNUAL_UI\.openGraphPopoverForMode === 'function'\) \{\n"
    r"            window\.__ANNUAL_UI\.openGraphPopoverForMode\('daily', insightDailySummaryGraphLink\);\n"
    r"          \}\n"
    r"        \}\);\n"
    r"      \}\n",
    re.M,
)


def patch_graph_hrefs(text: str) -> str:
    for link_id, href in GRAPH_HREF_BY_ID.items():
        pattern = re.compile(
            rf'(id="{re.escape(link_id)}"\s*\n\s*href=")#(?:annual-graph-popover-panel|insight-jump-graph-[^"]+)(")',
            re.M,
        )
        if not pattern.search(text):
            pattern2 = re.compile(
                rf'(id="{re.escape(link_id)}"[^>]*\n\s*href=")#(?:annual-graph-popover-panel|insight-jump-graph-[^"]+)(")',
                re.M,
            )
            text, n = pattern2.subn(rf"\1{href}\2", text, count=1)
            if n == 0:
                raise SystemExit(f"href anchor miss for {link_id}")
        else:
            text = pattern.sub(rf"\1{href}\2", text, count=1)
    return text


def inject_cross_links(text: str) -> str:
    marker_pos = text.find(MARKER)
    if marker_pos >= 0:
        start = text.rfind("\n", 0, marker_pos)
        end = text.find("\n      root.addEventListener('click', function (ev) {", marker_pos)
        if end < 0:
            end = text.find("\n      function open()", marker_pos)
        if end < 0:
            raise SystemExit("cross-links block end not found")
        return text[: start + 1] + JS.rstrip() + "\n" + text[end:]

    if INJECT_AFTER not in text:
        raise SystemExit("bindInsightJumpLink(jumpAnnual) anchor miss")
    return text.replace(INJECT_AFTER, INJECT_AFTER + "\n" + JS.rstrip(), 1)


def remove_popover_graph_handler(text: str) -> str:
    if POPOVER_HANDLER.search(text):
        return POPOVER_HANDLER.sub("\n", text, count=1)
    if "insightDailySummaryGraphLink" in text:
        raise SystemExit("unexpected insightDailySummaryGraphLink block")
    return text


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_graph_hrefs(text)
    text = inject_cross_links(text)
    text = remove_popover_graph_handler(text)
    path.write_text(text, encoding="utf-8")
    print(f"patched: {path.relative_to(ROOT)}")


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path)


if __name__ == "__main__":
    main()

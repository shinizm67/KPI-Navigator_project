#!/usr/bin/env python3
"""Sync Insight Summary layout vars/CSS and Annual Graph block from annual → monthly index."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    (ROOT / "app/annual/index.html", ROOT / "app/monthly/index.html"),
    (ROOT / "en/app/annual/index.html", ROOT / "en/app/monthly/index.html"),
]


def extract_between(text: str, start: str, end: str, label: str) -> str:
    i = text.find(start)
    if i < 0:
        raise ValueError(f"{label}: start marker not found")
    j = text.find(end, i + len(start))
    if j < 0:
        raise ValueError(f"{label}: end marker not found")
    return text[i : j + len(end)]


def replace_between(text: str, start: str, end: str, replacement: str, label: str) -> str:
    i = text.find(start)
    if i < 0:
        raise ValueError(f"{label}: start marker not found in target")
    j = text.find(end, i + len(start))
    if j < 0:
        raise ValueError(f"{label}: end marker not found in target")
    return text[:i] + replacement + text[j + len(end) :]


def main() -> int:
    for src_path, dst_path in PAIRS:
        src = src_path.read_text(encoding="utf-8")
        dst = dst_path.read_text(encoding="utf-8")

        vars_start = "      --insight-section-bottom-pad: 50px;"
        vars_end = (
            "      min-height: max(var(--insight-content-scroll-min), 100%);\n"
            "      padding: 0;\n"
            "      box-sizing: border-box;"
        )
        vars_block = extract_between(src, vars_start, vars_end, "insight vars")
        # Daily Summary: 46px to divider (was 50px via --insight-section-bottom-pad)
        vars_block = vars_block.replace(
            "var(--insight-comparison-tail-inner-h) + var(--insight-section-bottom-pad)\n      );\n"
            "      --insight-band-daily-analyze:",
            "var(--insight-comparison-tail-inner-h) + var(--insight-summary-section-bottom-pad)\n      );\n"
            "      --insight-band-daily-analyze:",
            1,
        )
        dst = replace_between(dst, vars_start, vars_end, vars_block, "insight vars")

        summary_css_start = "    /* Summary タブ: 親 .insight-overlay__content"
        if summary_css_start not in dst:
            anchor = "    .insight-overlay__section--annual {\n      min-height: var(--insight-band-annual);\n    }\n"
            summary_block = extract_between(
                src,
                summary_css_start,
                "    .insight-overlay__section-label {",
                "summary css",
            )
            if anchor not in dst:
                raise ValueError("summary css anchor not found in target")
            dst = dst.replace(anchor, anchor + summary_block, 1)

        # Annual graph CSS (cumulative row + trend charts + .insight-graph-annual min-height)
        if ".insight-pane--graph .insight-graph-annual__row-title {" not in dst:
            css_start = "    .insight-pane--graph .insight-graph-annual__row-title {"
            css_end = "    .insight-pane--graph .insight-graph-monthly-trend {"
            if css_start not in src:
                css_start = "    .insight-pane--graph .insight-graph-annual__row-title {"
            annual_css = extract_between(src, css_start, css_end, "annual graph css")
            insert_before = "    .insight-graph-monthly,\n    .insight-graph-annual {"
            if insert_before not in dst:
                raise ValueError("annual css insert anchor missing")
            dst = dst.replace(insert_before, annual_css + insert_before, 1)

        # Graph tab hline rules (annual uses 実寸 block from annual)
        graph_hline_start = "    /* Graph タブ: 0.5px 横線"
        graph_hline_end = "    .insight-graph-monthly,\n    .insight-graph-annual {"
        if graph_hline_start in src and graph_hline_start in dst:
            hline_block = extract_between(src, graph_hline_start, graph_hline_end, "graph hline css")
            dst = replace_between(dst, graph_hline_start, graph_hline_end, hline_block, "graph hline css")

        # Annual graph HTML
        html_start = (
            '            <section class="insight-overlay__section insight-overlay__section--annual '
            'insight-pane--graph__annual" id="insight-jump-graph-annual"'
        )
        html_end = "            </section>\n          </div>\n        </div>\n      </div>\n    </section>\n  </div>\n  <div class=\"daily-overlay\""
        annual_html = extract_between(src, html_start, html_end, "annual graph html")
        dst = replace_between(dst, html_start, html_end, annual_html, "annual graph html")

        # JS: initGraphAnnual* + fix duplicate monthly init
        js_start = "      function initGraphAnnualCumulativeTrendGraph1() {"
        js_end = "      function initGraphDailyHistoricalWeekday() {"
        if js_start in src and js_start not in dst:
            i = src.find(js_start)
            j = src.find(js_end, i + len(js_start))
            if j < 0:
                raise ValueError("annual graph js: end marker not found")
            js_block = src[i:j]
            dup = (
                "      initGraphMonthlyCumulativeTrend();\n"
                "      initGraphMonthlyCumulativeTrend();\n"
            )
            single = "      initGraphMonthlyCumulativeTrend();\n"
            if dup in dst:
                dst = dst.replace(dup, single + js_block, 1)
            elif single in dst:
                dst = dst.replace(single, single + js_block, 1)
            else:
                anchor = "      function initGraphDailyHistoricalWeekday() {"
                dst = dst.replace(anchor, js_block + anchor, 1)

        # Remove erroneous analyze-link top rule if annual graph uses padding on .insight-graph-annual
        dst = re.sub(
            r"\n    \.insight-pane--graph #insight-jump-graph-annual > \.insight-graph-analyze-link \{[^}]+\}\n",
            "\n",
            dst,
            count=1,
        )

        dst_path.write_text(dst, encoding="utf-8")
        print(f"OK {dst_path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

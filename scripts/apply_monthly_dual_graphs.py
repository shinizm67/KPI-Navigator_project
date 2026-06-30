#!/usr/bin/env python3
"""Merge Monthly Graph1 (KGI/KPI) + Graph2 (compare) into insight HTML files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    (ROOT / "app/monthly/index.html", ROOT / "scripts/_monthly_graphs_ja.html"),
    (ROOT / "en/app/monthly/index.html", ROOT / "scripts/_monthly_graphs_en.html"),
    (ROOT / "app/annual/index.html", ROOT / "scripts/_monthly_graphs_ja.html"),
    (ROOT / "en/app/annual/index.html", ROOT / "scripts/_monthly_graphs_en.html"),
]

GRAPH1_JS = (ROOT / "scripts/_trend_chart_graph1.js").read_text(encoding="utf-8")
GRAPH2_JS = (ROOT / "scripts/_trend_chart_graph2.js").read_text(encoding="utf-8")

OLD_HTML_START = '                <div class="insight-graph-monthly-trend" id="insight-graph-monthly-trend"'
OLD_JS_START = "      function initGraphMonthlyCumulativeTrend() {"
OLD_JS_END = "      initGraphMonthlyCumulativeTrend();"

VARS_OLD = """      --insight-graph-monthly-trend-top: calc(
        var(--insight-graph-monthly-row1-top) + var(--insight-graph-daily-chart-h) +
          var(--insight-graph-monthly-trend-gap-after-bar)
      );
      --insight-graph-monthly-body-h: calc(
        var(--insight-graph-monthly-row1-top) + var(--insight-graph-daily-chart-h) +
          var(--insight-graph-monthly-trend-gap-after-bar) + var(--insight-graph-monthly-trend-block-h)
      );"""

VARS_NEW = """      --insight-graph-monthly-trend-top: calc(
        var(--insight-graph-monthly-row1-top) + var(--insight-graph-daily-chart-h) +
          var(--insight-graph-monthly-trend-gap-after-bar)
      );
      --insight-graph-monthly-trend-gap-between-graphs: 48px;
      --insight-graph-monthly-trend2-top: calc(
        var(--insight-graph-monthly-trend-top) + var(--insight-graph-monthly-trend-block-h) +
          var(--insight-graph-monthly-trend-gap-between-graphs)
      );
      --insight-graph-monthly-body-h: calc(
        var(--insight-graph-monthly-row1-top) + var(--insight-graph-daily-chart-h) +
          var(--insight-graph-monthly-trend-gap-after-bar) + var(--insight-graph-monthly-trend-block-h) * 2 +
          var(--insight-graph-monthly-trend-gap-between-graphs)
      );"""

CSS_POS_OLD = """    .insight-pane--graph .insight-graph-monthly-trend {
      position: absolute;
      left: 50%;
      top: var(--insight-graph-monthly-trend-top);
      width: var(--insight-graph-monthly-trend-frame-w);
      transform: translateX(-50%);
      pointer-events: none;
    }"""

CSS_POS_NEW = """    .insight-pane--graph .insight-graph-monthly-trend {
      position: absolute;
      left: 50%;
      width: var(--insight-graph-monthly-trend-frame-w);
      transform: translateX(-50%);
      pointer-events: none;
    }
    .insight-pane--graph .insight-graph-monthly-trend--graph1 {
      top: var(--insight-graph-monthly-trend-top);
    }
    .insight-pane--graph .insight-graph-monthly-trend--graph2 {
      top: var(--insight-graph-monthly-trend2-top);
    }"""

KGI_KPI_CSS = """
    .insight-pane--graph .insight-graph-monthly-trend__line--kgi {
      fill: none;
      stroke: #58e1f3;
      stroke-width: 2;
      stroke-linejoin: round;
      stroke-linecap: round;
    }
    .insight-pane--graph .insight-graph-monthly-trend__line--kpi {
      fill: none;
      stroke: #f00;
      stroke-width: 2;
      stroke-linejoin: round;
      stroke-linecap: round;
    }
"""

KGI_ENDPOINT_CSS = """
    .insight-pane--graph .insight-graph-monthly-trend__endpoint-label--kgi {
      color: #58e1f3;
    }
    .insight-pane--graph .insight-graph-monthly-trend__endpoint-label--kpi {
      color: #f00;
    }
"""

KGI_LEGEND_CSS = """
    .insight-pane--graph .insight-graph-monthly-trend__legend-item--kgi {
      color: #58e1f3;
    }
    .insight-pane--graph .insight-graph-monthly-trend__legend-item--kpi {
      color: #f00;
    }
    .insight-pane--graph .insight-graph-monthly-trend__legend-item--kgi .insight-graph-monthly-trend__legend-swatch {
      margin-left: 133px;
      background: #58e1f3;
    }
    .insight-pane--graph .insight-graph-monthly-trend__legend-item--kpi .insight-graph-monthly-trend__legend-swatch {
      margin-left: 133px;
      background: #f00;
    }
"""

KGI_HIT_DOT_CSS = """
    .insight-pane--graph .insight-graph-monthly-trend__hit-dot--kgi {
      stroke: #58e1f3;
    }
    .insight-pane--graph .insight-graph-monthly-trend__hit-dot--kpi {
      stroke: #f00;
    }
"""


def extract_html_block(text: str) -> str:
    start = text.find(OLD_HTML_START)
    if start < 0:
        raise ValueError("HTML block start not found")
    end_marker = '                id="insight-graph-monthly-analyze-link"'
    end = text.find(end_marker, start)
    if end < 0:
        raise ValueError("HTML block end not found")
    # back to closing </div> of trend block (before analyze link's section close)
    chunk = text[start:end]
    last_close = chunk.rfind("                </div>\n")
    if last_close < 0:
        raise ValueError("trend closing div not found")
    return text[start : start + last_close + len("                </div>\n")]


def replace_js(text: str) -> str:
    start = text.find(OLD_JS_START)
    if start < 0:
        raise ValueError("JS init start not found")
    end = text.find(OLD_JS_END, start)
    if end < 0:
        raise ValueError("JS init end not found")
    end += len(OLD_JS_END)
    replacement = GRAPH1_JS + "\n" + GRAPH2_JS + "\n      initGraphMonthlyCumulativeTrendGraph1();\n      initGraphMonthlyCumulativeTrendGraph2();"
    return text[:start] + replacement + text[end:]


def patch_css(text: str) -> str:
    if VARS_OLD not in text:
        raise ValueError("CSS vars block not found")
    text = text.replace(VARS_OLD, VARS_NEW, 1)
    if CSS_POS_OLD not in text:
        raise ValueError("CSS position block not found")
    text = text.replace(CSS_POS_OLD, CSS_POS_NEW, 1)
    anchor = "    .insight-pane--graph .insight-graph-monthly-trend__line--current {"
    if anchor not in text:
        raise ValueError("line--current anchor not found")
    if "insight-graph-monthly-trend__line--kgi" not in text:
        text = text.replace(anchor, KGI_KPI_CSS + anchor, 1)
    anchor2 = "    .insight-pane--graph .insight-graph-monthly-trend__endpoint-label--current {"
    if anchor2 in text and "endpoint-label--kgi" not in text:
        text = text.replace(anchor2, KGI_ENDPOINT_CSS + anchor2, 1)
    anchor3 = "    .insight-pane--graph .insight-graph-monthly-trend__legend-item--current {"
    if anchor3 in text and "legend-item--kgi" not in text:
        text = text.replace(anchor3, KGI_LEGEND_CSS + anchor3, 1)
    anchor4 = "    .insight-pane--graph .insight-graph-monthly-trend__hit-dot--current {"
    if anchor4 in text and "hit-dot--kgi" not in text:
        text = text.replace(anchor4, KGI_HIT_DOT_CSS + anchor4, 1)
    return text


def main() -> None:
    for html_path, snippet_path in FILES:
        text = html_path.read_text(encoding="utf-8")
        old_block = extract_html_block(text)
        new_block = snippet_path.read_text(encoding="utf-8")
        if old_block == new_block:
            print(f"skip HTML (already patched): {html_path}")
        else:
            text = text.replace(old_block, new_block, 1)
        text = patch_css(text)
        text = replace_js(text)
        html_path.write_text(encoding="utf-8", data=text)
        print(f"patched: {html_path}")


if __name__ == "__main__":
    main()

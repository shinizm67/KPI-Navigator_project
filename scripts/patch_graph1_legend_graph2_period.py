#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

ENDPOINT_ANCHOR = "    .insight-pane--graph .insight-graph-monthly-trend__endpoint-label--current {"
ENDPOINT_PATCH = (ROOT / "scripts/_patch_graph1_legend_kgi_kpi.css").read_text(encoding="utf-8") + ENDPOINT_ANCHOR

LEGEND_ANCHOR = "    .insight-pane--graph .insight-graph-monthly-trend__legend-item--current {"
LEGEND_PATCH = (ROOT / "scripts/_patch_graph1_legend_items.css").read_text(encoding="utf-8") + LEGEND_ANCHOR

GRAPH2_PERIOD_HTML = """                    <p class="insight-graph-monthly-trend__period" id="insight-graph-monthly-graph2-period">2026.5</p>
"""

JS_PERIOD_VAR = """        var periodEl = document.getElementById('insight-graph-monthly-graph2-period');
"""
JS_PERIOD_SET_GRAPH2 = """          var dim = daysInMonth(ym.year, ym.month);
          if (periodEl) periodEl.textContent = ym.year + '.' + ym.month;

          var payload = buildComparePayload(dim);
"""
JS_PERIOD_SET_GRAPH2_FIXED = """          var dim = daysInMonth(ym.year, ym.month);
          var payload = buildComparePayload(dim);
"""


def main() -> None:
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        if "legend-item--kgi .insight-graph-monthly-trend__legend-swatch" not in text:
            if ENDPOINT_ANCHOR not in text:
                raise SystemExit(f"missing endpoint anchor: {path}")
            text = text.replace(ENDPOINT_ANCHOR, ENDPOINT_PATCH, 1)
            text = text.replace(LEGEND_ANCHOR, LEGEND_PATCH, 1)
        if GRAPH2_PERIOD_HTML in text:
            text = text.replace(GRAPH2_PERIOD_HTML, "", 1)
        if JS_PERIOD_VAR in text:
            text = text.replace(JS_PERIOD_VAR, "", 1)
        if JS_PERIOD_SET_GRAPH2 in text:
            text = text.replace(JS_PERIOD_SET_GRAPH2, JS_PERIOD_SET_GRAPH2_FIXED, 1)
        path.write_text(encoding="utf-8", data=text)
        print(f"patched: {path}")


if __name__ == "__main__":
    main()

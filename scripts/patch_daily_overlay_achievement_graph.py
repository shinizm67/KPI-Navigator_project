#!/usr/bin/env python3
"""Daily Floating Window — achievement bar graphs (Area1 / Insight 同ロジック)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

GRAPH_TRACK_HTML_OLD = """          <span class="daily-overlay__daily-graph-fill"></span>
          <span class="daily-overlay__daily-graph-marker"></span>"""

GRAPH_TRACK_HTML_NEW = """          <span class="daily-overlay__daily-graph-tri" aria-hidden="true"></span>
          <span class="daily-overlay__daily-graph-fill" aria-hidden="true"></span>
          <span class="daily-overlay__daily-graph-target-line" aria-hidden="true"></span>"""

GRAPH_CSS_OLD = """    .daily-overlay__daily-graph-track {
      position: relative;
      width: 523px;
      height: 14px;
      flex: 0 0 523px;
      border: 1px solid rgba(88, 225, 243, 0.26);
      background: rgba(8, 35, 10, 0.72);
      box-sizing: border-box;
    }
    .daily-overlay__daily-graph-fill {
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 89%;
      background: #08b10d;
    }
    .daily-overlay__daily-graph-marker {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 82%;
      width: 1px;
      background: #58e1f3;
    }"""

GRAPH_CSS_NEW = """    .daily-overlay__daily-graph-track {
      position: relative;
      width: 523px;
      height: 14px;
      flex: 0 0 523px;
      margin-top: 14px;
      border: 1px solid rgba(88, 225, 243, 0.26);
      background: rgba(15, 148, 3, 0.33);
      box-sizing: border-box;
      overflow: visible;
      --marker-color: #e6ff00;
      --kpi-x: 348.67px;
      --kgi-x: 0px;
      --fill-w: 0px;
      --marker-triangle-w: 12px;
      --marker-triangle-h: 12px;
      --marker-triangle-half-w: calc(var(--marker-triangle-w) / 2);
    }
    .daily-overlay__daily-graph-fill {
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: var(--fill-w);
      background: #0f9403;
      pointer-events: none;
      z-index: 1;
    }
    .daily-overlay__daily-graph-target-line {
      position: absolute;
      top: 0;
      bottom: 0;
      left: var(--kpi-x);
      transform: translateX(-50%);
      width: 4px;
      background: #e6ff00;
      box-shadow: 0 0 4px color-mix(in srgb, #e6ff00 55%, transparent);
      pointer-events: none;
      z-index: 2;
    }
    .daily-overlay__daily-graph-tri {
      position: absolute;
      left: var(--kgi-x);
      top: calc(-1 * var(--marker-triangle-h));
      transform: translateX(-50%);
      width: 0;
      height: 0;
      border-left: var(--marker-triangle-half-w) solid transparent;
      border-right: var(--marker-triangle-half-w) solid transparent;
      border-top: var(--marker-triangle-h) solid var(--marker-color);
      filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.4));
      pointer-events: none;
      z-index: 3;
    }
    .office-mode .daily-overlay__daily-graph-track {
      border-color: rgba(102, 102, 102, 0.55);
      background: #6e6e6e;
    }
    .office-mode .daily-overlay__daily-graph-fill {
      background: #d2d2d2;
    }
    .office-mode .daily-overlay__daily-graph-target-line {
      background: #e6ff00;
      box-shadow: 0 0 2px color-mix(in srgb, #e6ff00 45%, transparent);
    }
    .office-mode .daily-overlay__daily-graph-tri {
      filter: drop-shadow(0 0 1px rgba(0, 0, 0, 0.55));
    }"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if GRAPH_CSS_NEW in text and GRAPH_TRACK_HTML_NEW in text:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return
    if GRAPH_CSS_OLD not in text:
        raise SystemExit(f"graph CSS patch miss: {path}")
    if GRAPH_TRACK_HTML_OLD not in text:
        raise SystemExit(f"graph HTML patch miss: {path}")
    text = text.replace(GRAPH_CSS_OLD, GRAPH_CSS_NEW, 1)
    text = text.replace(GRAPH_TRACK_HTML_OLD, GRAPH_TRACK_HTML_NEW)
    if text.count(GRAPH_TRACK_HTML_NEW) != 3:
        raise SystemExit(f"expected 3 graph tracks, got {text.count(GRAPH_TRACK_HTML_NEW)}: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Annual ページ Graph タブ: Analyze 帯 min-height が親に残り巨大空白になるのを防ぐ.

Monthly と同様に Graph タブ表示時は content / pane の min-height を auto にし、
誤った scroll-min-graph 強制を外す。Monthly HTML には触れない。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

INSERT_AFTER = """    .insight-overlay__section--annual {
      min-height: var(--insight-band-annual);
    }
"""

GRAPH_HAS_OVERRIDE = """    /* Graph タブ: 親 .insight-overlay__content / .insight-pane の Analyze 用 min-height を無効化 */
    .insight-overlay__content:has(> #insight-pane-graph:not([hidden])) {
      min-height: auto;
      height: auto;
    }
    #insight-pane-graph.insight-pane {
      min-height: auto;
      height: auto;
    }
"""

OLD_FORCE = """    /* Graph タブ: 0.5px 横線（Daily|Monthly|Annual 境界）・各帯 2000px 仮確保 */
    #insight-pane-graph.insight-pane,
    #insight-pane-graph .insight-overlay__content {
      min-height: max(var(--insight-content-scroll-min-graph), 100%);
    }
"""

NEW_FORCE = """    /* Graph タブ: 0.5px 横線（Daily|Monthly|Annual 境界）・各帯 実寸（min-height は各 section / :has で制御） */
"""


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    if ":has(> #insight-pane-graph:not([hidden]))" not in text:
        if INSERT_AFTER not in text:
            raise SystemExit(f"insert anchor miss: {path}")
        text = text.replace(INSERT_AFTER, INSERT_AFTER + GRAPH_HAS_OVERRIDE, 1)

    if OLD_FORCE in text:
        text = text.replace(OLD_FORCE, NEW_FORCE, 1)
    elif "各帯 実寸（min-height は各 section" in text:
        pass
    else:
        raise SystemExit(f"force block miss: {path}")

    if ":has(> #insight-pane-graph:not([hidden]))" not in text:
        raise SystemExit(f"verify :has miss: {path}")
    if "min-height: max(var(--insight-content-scroll-min-graph)" in text:
        # should not remain for the graph pane force (variable may still exist in :root calc)
        # Check specifically the combined selector
        if (
            "#insight-pane-graph.insight-pane,\n    #insight-pane-graph .insight-overlay__content {\n"
            "      min-height: max(var(--insight-content-scroll-min-graph)"
        ) in text or (
            "#insight-pane-graph.insight-pane,\n    #insight-pane-graph .insight-overlay__content {"
            in text
            and "content-scroll-min-graph" in text[
                text.find("#insight-pane-graph.insight-pane,\n    #insight-pane-graph .insight-overlay__content {")
                : text.find("#insight-pane-graph.insight-pane,\n    #insight-pane-graph .insight-overlay__content {")
                + 200
            ]
        ):
            raise SystemExit(f"old force remains: {path}")

    path.write_text(text, encoding="utf-8")
    print(f"OK {path.relative_to(ROOT)}")


def main() -> int:
    for p in PAGES:
        if not p.is_file():
            print(f"missing {p}", file=sys.stderr)
            return 1
        patch(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

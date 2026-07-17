#!/usr/bin/env python3
"""Graph Monthly レイアウト修正 — 折れ線1本用の帯高と ▶分析 位置."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from insight_graph_monthly_layout_client import (  # noqa: E402
    MARKER_ANALYZE_LINK,
    MARKER_BODY_H,
    MONTHLY_ANALYZE_LINK_NEW,
    MONTHLY_ANALYZE_LINK_OLD,
    MONTHLY_BODY_H_COMMENT_NEW,
    MONTHLY_BODY_H_COMMENT_OLD,
    MONTHLY_BODY_H_NEW,
    MONTHLY_BODY_H_OLD,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER_BODY_H in text:
        text = text.replace(MONTHLY_BODY_H_OLD, MONTHLY_BODY_H_NEW, 1)
    elif "var(--insight-graph-monthly-trend-block-h)\n      );" not in text:
        raise SystemExit(f"monthly body-h patch miss: {path}")
    if MONTHLY_BODY_H_COMMENT_OLD in text:
        text = text.replace(MONTHLY_BODY_H_COMMENT_OLD, MONTHLY_BODY_H_COMMENT_NEW, 1)
    if MONTHLY_ANALYZE_LINK_OLD in text:
        text = text.replace(MONTHLY_ANALYZE_LINK_OLD, MONTHLY_ANALYZE_LINK_NEW, 1)
    elif MARKER_ANALYZE_LINK not in text:
        raise SystemExit(f"monthly analyze-link patch miss: {path}")
    if MARKER_BODY_H in text:
        raise SystemExit(f"monthly body-h still dual-graph: {path}")
    if MARKER_ANALYZE_LINK not in text:
        raise SystemExit(f"monthly analyze-link not applied: {path}")
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

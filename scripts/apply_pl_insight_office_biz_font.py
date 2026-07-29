#!/usr/bin/env python3
"""PL Insight Office Mode: force BIZ on entire compare panel (override Orbitron leftovers)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]
BUILD = ROOT / "scripts/build_pl_table_page.py"

MARKER = "KPI-PL-INSIGHT-OFFICE-BIZ"

ANCHOR = """    body.office-mode .pl-graph-overlay__panel {
      border-color: #555 !important;
      color: #111 !important;
    }
    body.office-mode .pl-graph-overlay__close {"""

INSERT = """    body.office-mode .pl-graph-overlay__panel {
      border-color: #555 !important;
      color: #111 !important;
    }
    /* KPI-PL-INSIGHT-OFFICE-BIZ: Office はパネル内を BIZ に統一（Orbitron 残存を上書き） */
    body.office-mode .pl-graph-overlay__panel,
    body.office-mode .pl-graph-overlay__panel *:not(svg):not(svg *) {
      font-family: 'BIZ UDPGothic', sans-serif !important;
    }
    body.office-mode .pl-graph-overlay__close {"""

ANCHOR_BUILD = ANCHOR.replace("{", "{{").replace("}", "}}")
INSERT_BUILD = INSERT.replace("{", "{{").replace("}", "}}")


def patch_file(path: Path, anchor: str, insert: str) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already) {rel}")
        return
    if anchor not in text:
        raise SystemExit(f"anchor miss: {rel}")
    path.write_text(text.replace(anchor, insert, 1), encoding="utf-8")
    print(f"wrote {rel}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_file(path, ANCHOR, INSERT)
    if BUILD.is_file():
        patch_file(BUILD, ANCHOR_BUILD, INSERT_BUILD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fix Weekly Insight: long memo text must not expand fixed columns (headers vanish off-screen)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

OLD_VARS = """      --insight-weekly-date-w: 170px;
      --insight-weekly-scroll-w: 1030px;
      --insight-weekly-today-bg: color-mix(in srgb, #0f9403 15%, #1e1e1e);"""

NEW_VARS = """      --insight-weekly-date-w: 170px;
      --insight-weekly-scroll-w: 1030px;
      --insight-weekly-table-w: 1200px; /* date+weather+6 memo cols (fixed; memo must not grow) */
      --insight-weekly-today-bg: color-mix(in srgb, #0f9403 15%, #1e1e1e);"""

OLD_TABLE = """    .insight-pane--analyze .insight-analyze-weekly__table,
    .insight-pane--graph .insight-analyze-weekly__table {
      width: max-content;
      min-width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      font-size: 16px;
      font-weight: 400;
      line-height: 1.25;
      font-family: 'Orbitron', sans-serif;
      color: #58e1f3;
    }"""

NEW_TABLE = """    .insight-pane--analyze .insight-analyze-weekly__table,
    .insight-pane--graph .insight-analyze-weekly__table {
      width: var(--insight-weekly-table-w);
      min-width: var(--insight-weekly-table-w);
      max-width: var(--insight-weekly-table-w);
      border-collapse: collapse;
      table-layout: fixed;
      font-size: 16px;
      font-weight: 400;
      line-height: 1.25;
      font-family: 'Orbitron', sans-serif;
      color: #58e1f3;
    }"""

OLD_TD = """    .insight-pane--analyze .insight-analyze-weekly__table tbody td,
    .insight-pane--graph .insight-analyze-weekly__table tbody td {
      height: 44px;
      box-sizing: border-box;
      padding: 0 8px;
      text-align: center;
      vertical-align: middle;
      border-bottom: 0.5px solid rgba(88, 225, 243, 0.35);
    }"""

NEW_TD = """    .insight-pane--analyze .insight-analyze-weekly__table tbody td,
    .insight-pane--graph .insight-analyze-weekly__table tbody td {
      height: 44px;
      box-sizing: border-box;
      padding: 0 8px;
      text-align: center;
      vertical-align: middle;
      border-bottom: 0.5px solid rgba(88, 225, 243, 0.35);
      overflow: hidden;
    }"""

OLD_TH = """    .insight-pane--analyze .insight-analyze-weekly__table thead th,
    .insight-pane--graph .insight-analyze-weekly__table thead th {
      height: 40px;
      box-sizing: border-box;
      padding: 0 8px;
      font-weight: 700;
      text-align: center;
      vertical-align: middle;
      border-bottom: 0.5px solid rgba(88, 225, 243, 0.72);
    }"""

NEW_TH = """    .insight-pane--analyze .insight-analyze-weekly__table thead th,
    .insight-pane--graph .insight-analyze-weekly__table thead th {
      height: 40px;
      box-sizing: border-box;
      padding: 0 8px;
      font-weight: 700;
      text-align: center;
      vertical-align: middle;
      border-bottom: 0.5px solid rgba(88, 225, 243, 0.72);
      overflow: hidden;
    }"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "--insight-weekly-table-w: 1200px" in text and "max-width: var(--insight-weekly-table-w)" in text:
        # still allow re-apply of td/th overflow
        pass
    replacements = [
        (OLD_VARS, NEW_VARS),
        (OLD_TABLE, NEW_TABLE),
        (OLD_TH, NEW_TH),
        (OLD_TD, NEW_TD),
    ]
    for old, new in replacements:
        if new.strip() in text and old not in text:
            continue
        if old not in text:
            # already partially applied variants
            if "max-width: var(--insight-weekly-table-w)" in text and old is OLD_TABLE:
                continue
            if "--insight-weekly-table-w" in text and old is OLD_VARS:
                continue
            if "overflow: hidden;" in text and old in (OLD_TD, OLD_TH):
                # check context
                continue
            raise SystemExit(f"block miss in {path}:\n{old[:80]}...")
        text = text.replace(old, new, 1)
    for needle in (
        "--insight-weekly-table-w: 1200px",
        "max-width: var(--insight-weekly-table-w)",
    ):
        if needle not in text:
            raise SystemExit(f"missing {needle} in {path}")
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

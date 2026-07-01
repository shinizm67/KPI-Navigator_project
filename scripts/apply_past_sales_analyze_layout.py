#!/usr/bin/env python3
"""Apply Past Sales Analyze layout alignment (year row = table width, flush join)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from past_sales_analyze_layout_client import (  # noqa: E402
    LAYOUT_MARKER,
    PCT_NEW,
    PCT_OLD,
    SEASON_NEW,
    SEASON_OLD,
    STACK_NEW,
    STACK_OLD,
    YM_ANALYZE_NEW,
    YM_ANALYZE_OLD,
)

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

PATCHES = [
    (STACK_OLD, STACK_NEW, "stack"),
    (SEASON_OLD, SEASON_NEW, "season"),
    (PCT_OLD, PCT_NEW, "pct"),
    (YM_ANALYZE_OLD, YM_ANALYZE_NEW, "ym"),
]


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if LAYOUT_MARKER in text:
        print(f"skip (already patched): {path.relative_to(ROOT)}", file=sys.stderr)
        return
    for old, new, label in PATCHES:
        if old not in text:
            raise SystemExit(f"patch anchor missing in {path}: {label}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

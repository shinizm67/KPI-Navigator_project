#!/usr/bin/env python3
"""Unit 6H: refresh Sales import IIFE after confirm-copy changes.

Does not re-run unrelated daily-sales patches. MEP expense confirm is
applied separately on monthly/edit (inline handler, not this injector).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from apply_daily_sales_import import ANNUAL_PAGES, MEP_PAGES, inject_import_js  # noqa: E402


def main() -> int:
    for path in ANNUAL_PAGES + MEP_PAGES:
        original = path.read_text(encoding="utf-8")
        text = inject_import_js(original)
        if text == original:
            print(f"unchanged {path.relative_to(ROOT).as_posix()}")
            continue
        path.write_text(text, encoding="utf-8")
        print(f"patched {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

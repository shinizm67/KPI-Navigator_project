#!/usr/bin/env python3
"""Repair broken ensureSalesDataDaily / persistSalesDataShared merge in annual pages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sales_data_input_fixup_client import (  # noqa: E402
    BROKEN_ENSURE_PERSIST_NEW,
    BROKEN_ENSURE_PERSIST_OLD,
)

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if BROKEN_ENSURE_PERSIST_OLD not in text:
        print(f"skip (no broken block): {path.relative_to(ROOT)}", file=sys.stderr)
        return False
    text = text.replace(BROKEN_ENSURE_PERSIST_OLD, BROKEN_ENSURE_PERSIST_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")
    return True


def main() -> int:
    changed = False
    for path in TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        changed = patch_file(path) or changed
    return 0 if changed or True else 1


if __name__ == "__main__":
    raise SystemExit(main())

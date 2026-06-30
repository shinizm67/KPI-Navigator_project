#!/usr/bin/env python3
"""Phase 5c: MEP grid refresh on path / lease / editGuardsRefresh."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "scripts" / "_mep_edit_guards_refresh.js").read_text(encoding="utf-8")
MARKER = "/* KPI-EDIT-GUARDS */"

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        raise SystemExit(f"{MARKER} not found in {path}")
    guards_re = re.compile(
        r"/\* KPI-EDIT-GUARDS \*/\n\s*\(function \(\) \{[\s\S]*?\n\s*\}\)\(\);",
        re.MULTILINE,
    )
    if not guards_re.search(text):
        raise SystemExit(f"{MARKER} IIFE not found in {path}")
    text = guards_re.sub(JS.rstrip(), text, count=1)
    path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path)


if __name__ == "__main__":
    main()

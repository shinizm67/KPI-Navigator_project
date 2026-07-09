#!/usr/bin/env python3
"""Revert Monthly Focus Bar ver2 changes (restore pre-ver2 monthly pages)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    files = [
        ROOT / "app/monthly/index.html",
        ROOT / "en/app/monthly/index.html",
    ]
    for path in files:
        if "KPI-VFOCUS-VER2" not in path.read_text(encoding="utf-8"):
            print(f"skip (no ver2 marker): {path}")
            continue
    subprocess.run(
        ["git", "checkout", "--", "app/monthly/index.html", "en/app/monthly/index.html"],
        cwd=ROOT,
        check=True,
    )
    print("reverted monthly pages to last committed state")
    print("SVG ver2 assets in images/ are unchanged; switch src back manually if needed after partial edits")
    return 0


if __name__ == "__main__":
    sys.exit(main())

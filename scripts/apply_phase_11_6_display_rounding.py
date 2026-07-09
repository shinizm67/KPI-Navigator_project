#!/usr/bin/env python3
"""Phase 11-6 — daily target display rounding + last business day remainder."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"


def main() -> int:
    steps = [
        [_SCRIPTS / "apply_weekday_target_section.py"],
        [_SCRIPTS / "apply_focus_tw_metrics.py"],
    ]
    for cmd in steps:
        proc = subprocess.run([sys.executable, str(cmd[0])], cwd=ROOT)
        if proc.returncode != 0:
            return proc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

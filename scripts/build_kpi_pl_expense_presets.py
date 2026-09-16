#!/usr/bin/env python3
"""Write js/kpi-pl-expense-presets.js from pl_line_catalog.py only."""

from __future__ import annotations

from pathlib import Path

from pl_line_catalog import presets_runtime_js

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "js" / "kpi-pl-expense-presets.js"


def main() -> None:
    OUT.write_text(presets_runtime_js(), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

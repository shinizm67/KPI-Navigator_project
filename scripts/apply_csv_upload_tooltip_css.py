#!/usr/bin/env python3
"""Add hover tooltip CSS to all Upload CSV buttons."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from csv_upload_tooltip_css import (  # noqa: E402
    annual_csv_upload_tooltip_css,
    inject_or_replace_css,
    monthly_csv_upload_tooltip_css,
    pl_csv_upload_tooltip_css,
)

ANNUAL_PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
]

ANNUAL_INSERT_BEFORE = """    .annual-edit-modal__csv:hover,
    .annual-edit-modal__csv:focus-visible {
      background: rgba(88, 225, 243, 0.45);
      outline: none;
    }
    .annual-edit-modal__ym {"""
MEP_INSERT_BEFORE = "    .monthly-edit-float__top {"
PL_INSERT_BEFORE = "    .pl-year-label {{"


def patch_file(path: Path, css_block: str, insert_before: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_or_replace_css(text, css_block, insert_before)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    annual_css = annual_csv_upload_tooltip_css()
    mep_css = monthly_csv_upload_tooltip_css()
    pl_css = pl_csv_upload_tooltip_css()

    for path in ANNUAL_PAGES:
        patch_file(path, annual_css, ANNUAL_INSERT_BEFORE)
    for path in MEP_PAGES:
        patch_file(path, mep_css, MEP_INSERT_BEFORE)
    for path in PL_PAGES:
        insert = PL_INSERT_BEFORE.replace("{{", "{").replace("}}", "}")
        patch_file(path, pl_css, insert)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

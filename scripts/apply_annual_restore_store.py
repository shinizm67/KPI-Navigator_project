#!/usr/bin/env python3
"""Inject KpiYearStore into Annual pages only (store block, no hydrate patches)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_kpi_year_store import GATEWAY_ANNUAL_ANCHOR, inject_store  # noqa: E402
from kpi_year_store_client import KPI_YEAR_STORE_MARKER  # noqa: E402

PATH_UI_JS = (ROOT / "scripts" / "_kpi_sales_input_path_ui.js").read_text(encoding="utf-8")
PATH_UI_HTML_JA = (ROOT / "scripts" / "_kpi_path_change_chooser.html.ja").read_text(encoding="utf-8")
PATH_UI_HTML_EN = (ROOT / "scripts" / "_kpi_path_change_chooser.html.en").read_text(encoding="utf-8")
PATH_UI_MARKER = "/* KPI-SALES-INPUT-PATH-UI */"
PATH_UI_ANCHOR = "      var dateBtn = document.getElementById('annual-daily-date-btn');"
CHOOSER_ID = 'id="kpi-path-change-chooser"'

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def inject_sales_path_ui(text: str, chooser_html: str) -> str:
    if PATH_UI_MARKER in text:
        return text
    if PATH_UI_ANCHOR not in text:
        raise SystemExit("sales path UI anchor miss")
    text = text.replace(PATH_UI_ANCHOR, PATH_UI_JS.rstrip() + "\n\n" + PATH_UI_ANCHOR, 1)
    if CHOOSER_ID not in text:
        anchor = '  <div\n    class="sales-data-modal__close-chooser"\n    id="sales-data-close-chooser"'
        if anchor in text:
            text = text.replace(anchor, chooser_html.rstrip() + "\n" + anchor, 1)
        elif "</body>" in text:
            text = text.replace("</body>", chooser_html.rstrip() + "\n</body>", 1)
        else:
            raise SystemExit("path chooser anchor miss")
    return text


def main() -> int:
    pairs = [
        (PAGES[0], PATH_UI_HTML_JA),
        (PAGES[1], PATH_UI_HTML_EN),
    ]
    for path, chooser_html in pairs:
        text = path.read_text(encoding="utf-8")
        if KPI_YEAR_STORE_MARKER not in text:
            if GATEWAY_ANNUAL_ANCHOR not in text:
                raise SystemExit(f"gateway anchor miss: {path}")
            text = inject_store(text, GATEWAY_ANNUAL_ANCHOR)
        text = inject_sales_path_ui(text, chooser_html)
        if KPI_YEAR_STORE_MARKER not in text or PATH_UI_MARKER not in text:
            raise SystemExit(f"annual restore store/path failed: {path}")
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

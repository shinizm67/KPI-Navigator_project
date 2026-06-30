#!/usr/bin/env python3
"""Inject KPI sales input path UI (Phase 5b) — toggle rules + unsaved chooser."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "scripts" / "_kpi_sales_input_path_ui.js").read_text(encoding="utf-8")
HTML_JA = (ROOT / "scripts" / "_kpi_path_change_chooser.html.ja").read_text(encoding="utf-8")
HTML_EN = (ROOT / "scripts" / "_kpi_path_change_chooser.html.en").read_text(encoding="utf-8")

MARKER = "/* KPI-SALES-INPUT-PATH-UI */"
OLD_BLOCK_START = "      /* KPI-SALES-INPUT-PATH */"
OLD_BLOCK_END = "        window.__KPI_SALES_INPUT_PATH_UI = { sync: syncToggleUi };"
CHOOSER_ID = 'id="kpi-path-change-chooser"'

TARGETS = [
    (ROOT / "app/monthly/edit/index.html", HTML_JA),
    (ROOT / "en/app/monthly/edit/index.html", HTML_EN),
    (ROOT / "app/annual/index.html", HTML_JA),
    (ROOT / "en/app/annual/index.html", HTML_EN),
]


def replace_old_path_block(text: str) -> str:
    start = text.find(OLD_BLOCK_START)
    if start < 0:
        if MARKER in text:
            return text
        raise SystemExit("KPI-SALES-INPUT-PATH block not found")
    end = text.find(OLD_BLOCK_END, start)
    if end < 0:
        raise SystemExit("KPI-SALES-INPUT-PATH block end not found")
    end = text.find("\n      })();", end)
    if end < 0:
        raise SystemExit("KPI-SALES-INPUT-PATH IIFE end not found")
    end += len("\n      })();")
    return text[:start] + JS.rstrip() + text[end:]


def sync_js_block(text: str) -> str:
    pos = text.find(MARKER)
    if pos < 0:
        return replace_old_path_block(text)
    start = text.rfind("<script>", 0, pos)
    if start < 0:
        start = text.rfind("\n      (function () {", 0, pos)
    script_start = text.rfind("      /* KPI-SALES-INPUT-PATH", 0, pos)
    if script_start >= 0:
        start = script_start
    else:
        start = text.find(f"      {MARKER}")
    end = text.find("\n      })();", pos)
    if end < 0:
        raise SystemExit("path UI IIFE end not found")
    end += len("\n      })();")
    return text[:start] + JS.rstrip() + text[end:]


def inject_chooser(text: str, html: str) -> str:
    if CHOOSER_ID in text:
        return text
    anchor = '  <div\n    class="sales-data-modal__close-chooser"\n    id="sales-data-close-chooser"'
    if anchor not in text:
        anchor = "</body>"
        if anchor not in text:
            raise SystemExit("chooser anchor not found")
        return text.replace(anchor, html.rstrip() + "\n" + anchor, 1)
    return text.replace(anchor, html.rstrip() + "\n" + anchor, 1)


def patch_file(path: Path, html: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = sync_js_block(text)
    text = inject_chooser(text, html)
    path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def main() -> None:
    for path, html in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path, html)


if __name__ == "__main__":
    main()

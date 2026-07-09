#!/usr/bin/env python3
"""Inject Sales Data daily target mode dropdown (Phase 11-2) into Annual pages."""

from __future__ import annotations

import re
from pathlib import Path

from sdm_daily_target_mode_client import CSS, HTML_EN, HTML_JA

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "scripts" / "_sdm_daily_target_mode.js").read_text(encoding="utf-8")

CSS_START = "/* SDM-DAILY-TARGET-MODE-CSS */"
CSS_END = "/* /SDM-DAILY-TARGET-MODE-CSS */"
JS_MARKER = "/* SDM-DAILY-TARGET-MODE */"
SDM_HTML_ID = 'id="sdm-daily-target-mode"'
SDM_CSV_ID = 'id="sales-data-modal-csv"'

TARGETS = [
    (ROOT / "app/annual/index.html", HTML_JA),
    (ROOT / "en/app/annual/index.html", HTML_EN),
]

OPENMODAL_SYNC_ANCHOR = """        if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
          window.__KPI_SALES_INPUT_PATH_UI.sync();
        }"""

OPENMODAL_SYNC_PATCH = """        if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
          window.__KPI_SALES_INPUT_PATH_UI.sync();
        }
        if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.sync === 'function') {
          window.__SDM_DAILY_TARGET_MODE.sync();
        }
        if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {
          window.__SDM_DAILY_TARGET_MODE.closePanel();
        }"""

CLOSEMODAL_PATCH_ANCHOR = """        hideSalesDataCloseChooser();
        closeDateFilterPanel();
        closeSalesSortPanel();
        modal.setAttribute('hidden', '');"""

CLOSEMODAL_PATCH = """        hideSalesDataCloseChooser();
        closeDateFilterPanel();
        closeSalesSortPanel();
        if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function') {
          window.__SDM_DAILY_TARGET_MODE.closePanel();
        }
        modal.setAttribute('hidden', '');"""

ORPHAN_KPI_STORE_RE = re.compile(
    r"(window\.__KPI_DAILY_IMPORT\s*=\s*\{[\s\S]*?\};\n      \}\)\(\);\n)"
    r"\s*if \(window\.__ANNUAL_DATA\) \{[\s\S]*?\n      \}\)\(\);\n\n\n"
    r"(      window\.__ANNUAL_DATA = window\.__ANNUAL_DATA \|\| \{\};)",
    re.MULTILINE,
)

SDM_HTML_START = '<div class="sdm-daily-target-mode" id="sdm-daily-target-mode"'
SDM_HTML_END = '      </div>\n      <button type="button" class="sales-data-modal__undo"'


def remove_orphan_kpi_store_duplicate(text: str) -> str:
    if not ORPHAN_KPI_STORE_RE.search(text):
        return text
    return ORPHAN_KPI_STORE_RE.sub(r"\1\n\2", text, count=1)


def remove_misplaced_sdm_html(text: str) -> str:
    sd_csv = text.find(SDM_CSV_ID)
    sdm = text.find(SDM_HTML_START)
    if sdm < 0:
        return text
    if sd_csv >= 0 and sdm > sd_csv:
        return text
    end = text.find(SDM_HTML_END, sdm)
    if end < 0:
        raise SystemExit("sdm-daily-target-mode HTML block end anchor not found")
    end += len("      </div>")
    line_start = text.rfind("\n", 0, sdm)
    if line_start < 0:
        line_start = sdm
    return text[:line_start] + text[end:]


def replace_sdm_html(text: str, html: str) -> str:
    sd_csv = text.find(SDM_CSV_ID)
    if sd_csv < 0:
        raise SystemExit("sales-data-modal-csv anchor not found")
    start = text.find(SDM_HTML_START, sd_csv)
    if start >= 0:
        end = text.find(SDM_HTML_END, start)
        if end < 0:
            raise SystemExit("sdm-daily-target-mode HTML block end anchor not found")
        end += len("      </div>")
        line_start = text.rfind("\n", 0, start)
        if line_start < 0:
            line_start = start
        return text[:line_start] + "\n" + html.rstrip() + text[end:]
    csv_end = text.find("</button>", sd_csv)
    if csv_end < 0:
        raise SystemExit("sales-data-modal-csv closing tag not found")
    csv_end += len("</button>")
    return text[:csv_end] + "\n" + html.rstrip() + text[csv_end:]


def sync_css(text: str) -> str:
    block = CSS.strip()
    if CSS_START in text:
        pattern = re.compile(
            re.escape(CSS_START) + r".*?" + re.escape(CSS_END),
            re.DOTALL,
        )
        if not pattern.search(text):
            raise SystemExit("SDM daily target mode CSS block malformed")
        return pattern.sub(block, text, count=1)
    anchor = "    .sales-data-modal__csv {"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("sales-data-modal__csv CSS anchor not found")
    return text[:pos] + block + "\n" + text[pos:]


def sync_html(text: str, html: str) -> str:
    text = remove_misplaced_sdm_html(text)
    return replace_sdm_html(text, html)


def sync_js(text: str) -> str:
    if JS_MARKER in text:
        pattern = re.compile(
            r"      /\* SDM-DAILY-TARGET-MODE \*/\s*\(function \(\) \{.*?\n      \}\)\(\);\n",
            re.DOTALL,
        )
        if not pattern.search(text):
            raise SystemExit("SDM daily target mode JS block malformed")
        return pattern.sub(JS.rstrip() + "\n", text, count=1)
    anchor = "      /* KPI-SALES-INPUT-PATH-UI */"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("KPI-SALES-INPUT-PATH-UI anchor not found for JS injection")
    return text[:pos] + JS.rstrip() + "\n\n" + text[pos:]


def patch_open_modal(text: str) -> str:
    if "__SDM_DAILY_TARGET_MODE.sync" in text:
        return text
    if OPENMODAL_SYNC_ANCHOR not in text:
        raise SystemExit("Sales Data openModal sync anchor not found")
    return text.replace(OPENMODAL_SYNC_ANCHOR, OPENMODAL_SYNC_PATCH, 1)


def patch_close_modal(text: str) -> str:
    if (
        "closeSalesSortPanel();\n"
        "        if (window.__SDM_DAILY_TARGET_MODE && typeof window.__SDM_DAILY_TARGET_MODE.closePanel === 'function')"
        in text
    ):
        return text
    if CLOSEMODAL_PATCH_ANCHOR not in text:
        raise SystemExit("Sales Data closeModal anchor not found")
    return text.replace(CLOSEMODAL_PATCH_ANCHOR, CLOSEMODAL_PATCH, 1)


def patch_file(path: Path, html: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = remove_orphan_kpi_store_duplicate(text)
    text = sync_css(text)
    text = sync_html(text, html)
    text = sync_js(text)
    text = patch_open_modal(text)
    text = patch_close_modal(text)
    path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def main() -> None:
    for path, html in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path, html)


if __name__ == "__main__":
    main()

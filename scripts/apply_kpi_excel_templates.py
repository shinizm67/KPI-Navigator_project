#!/usr/bin/env python3
"""Unit 6F: inject Excel template JS + download button next to CSV templates."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT_RE = re.compile(
    r'(<script src="([^"]*/)kpi-csv-templates\.js"></script>)'
    r'(?!\s*<script src="[^"]*kpi-excel-templates\.js")'
)

MONTHLY_BTN_RE = re.compile(
    r'(<button type="button" class="template-dl-item" '
    r'id="kpi-dl-csv-expense-monthly"[^>]*>[^<]*</button>)'
    r'(?!\s*<button type="button" class="template-dl-item" id="kpi-dl-excel-template")'
)

EXCEL_LABEL = {
    "ja": "Excel雛形をダウンロード",
    "en": "Download Excel Template",
    "zh-tw": "下載 Excel 範本",
}


def lang_of(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("en/") or "/en/" in rel:
        return "en"
    if rel.startswith("zh-tw/") or "/zh-tw/" in rel:
        return "zh-tw"
    return "ja"


def excel_button(lang: str) -> str:
    return (
        '<button type="button" class="template-dl-item" id="kpi-dl-excel-template" '
        f'role="menuitem" data-kpi-excel-template="workbook">{EXCEL_LABEL[lang]}</button>'
    )


def inject_script(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return f'{m.group(1)}\n    <script src="{m.group(2)}kpi-excel-templates.js"></script>'

    return SCRIPT_RE.sub(repl, text, count=1)


def inject_button(text: str, lang: str) -> str:
    if 'id="kpi-dl-excel-template"' in text:
        return text
    btn = excel_button(lang)
    return MONTHLY_BTN_RE.sub(lambda m: m.group(1) + "\n            " + btn, text, count=1)


def patch_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = inject_script(original)
    text = inject_button(text, lang_of(path))
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def target_pages() -> list[Path]:
    out: list[Path] = []
    for path in ROOT.rglob("*.html"):
        if "excel" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "kpi-csv-templates.js" in text:
            out.append(path)
    return sorted(out)


def main() -> int:
    changed = 0
    for path in target_pages():
        if patch_file(path):
            print(f"patched {path.relative_to(ROOT).as_posix()}")
            changed += 1
    print(f"pages patched={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

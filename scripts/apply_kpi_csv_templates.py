#!/usr/bin/env python3
"""Unit 6D: inject CSV template JS into PL pages without regenerating them.

App / settings / monthly-edit chrome is updated by build_site_chrome.py.
PL index.html is owned by build_pl_table_page.py and is patched in place here.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PL_PAGES = [
    (ROOT / "app/profit/pl/index.html", "ja"),
    (ROOT / "en/app/profit/pl/index.html", "en"),
    (ROOT / "zh-tw/app/profit/pl/index.html", "zh-tw"),
]

SALES_LABEL = {
    "ja": "売上雛形をダウンロード",
    "en": "Download Sales Template",
    "zh-tw": "下載銷售範本",
}

SCRIPT_RE = re.compile(
    r'(<script src="([^"]*/)kpi-pl-expense-presets\.js"></script>)'
    r'(?!\s*<script src="[^"]*kpi-csv-templates\.js")'
)

DAILY_A_RE = re.compile(
    r'<a href="[^"]*excel/[^"]*(?:支出入力_日次|expense-import_daily)[^"]*"'
    r' download class="template-dl-item" role="menuitem">([^<]*)</a>'
)
MONTHLY_A_RE = re.compile(
    r'<a href="[^"]*excel/[^"]*(?:支出入力_月次|expense-import_monthly)[^"]*"'
    r' download class="template-dl-item" role="menuitem">([^<]*)</a>'
)
SALES_INSERT_RE = re.compile(
    r'(<div class="template-dl-menu"[^>]*>\s*'
    r'<p class="template-dl-heading">[^<]*</p>\s*)'
)


def inject_script(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        prefix = m.group(2)
        return (
            f'{m.group(1)}\n  <script src="{prefix}kpi-csv-templates.js"></script>'
        )

    return SCRIPT_RE.sub(repl, text)


def expense_button(kind: str, label: str) -> str:
    ident = "kpi-dl-csv-expense-daily" if kind == "daily" else "kpi-dl-csv-expense-monthly"
    data = "expense-daily" if kind == "daily" else "expense-monthly"
    return (
        f'<button type="button" class="template-dl-item" id="{ident}" '
        f'role="menuitem" data-kpi-csv-template="{data}">{label}</button>'
    )


def sales_button(lang: str) -> str:
    return (
        '<button type="button" class="template-dl-item" id="kpi-dl-csv-sales" '
        f'role="menuitem" data-kpi-csv-template="sales">{SALES_LABEL[lang]}</button>'
    )


def replace_excel_links(text: str, lang: str) -> str:
    text = DAILY_A_RE.sub(lambda m: expense_button("daily", m.group(1)), text)
    text = MONTHLY_A_RE.sub(lambda m: expense_button("monthly", m.group(1)), text)
    if 'id="kpi-dl-csv-sales"' not in text:
        btn = sales_button(lang)

        def insert(m: re.Match[str]) -> str:
            return m.group(1) + btn + "\n            "

        text = SALES_INSERT_RE.sub(insert, text, count=1)
    return text


def patch_pl(path: Path, lang: str) -> bool:
    original = path.read_text(encoding="utf-8")
    text = inject_script(original)
    text = replace_excel_links(text, lang)
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for path, lang in PL_PAGES:
        if not path.is_file():
            raise SystemExit(f"missing {path}")
        if patch_pl(path, lang):
            print(f"patched {path.relative_to(ROOT).as_posix()}")
            changed += 1
        else:
            print(f"unchanged {path.relative_to(ROOT).as_posix()}")
    print(f"pl pages patched={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

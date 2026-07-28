#!/usr/bin/env python3
"""Inject MEP+PL Excel export: refresh DL menus + shared client script."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "scripts" / "_kpi_pl_mep_export.js").read_text(encoding="utf-8")
MARKER = "/* KPI-PL-MEP-EXPORT */"

# Pages that get the export script (JA/EN with Global Menu DL).
TARGET_GLOBS = [
    "app/annual/index.html",
    "app/monthly/index.html",
    "app/monthly/edit/index.html",
    "app/profit/index.html",
    "app/profit/pl/index.html",
    "en/app/annual/index.html",
    "zh-tw/app/annual/index.html",
    "en/app/monthly/index.html",
    "zh-tw/app/monthly/index.html",
    "en/app/monthly/edit/index.html",
    "zh-tw/app/monthly/edit/index.html",
    "en/app/profit/index.html",
    "zh-tw/app/profit/index.html",
    "en/app/profit/pl/index.html",
    "zh-tw/app/profit/pl/index.html",
    "setting/*.html",
    "en/setting/*.html",
    "zh-tw/setting/*.html",
]


def inject_script(text: str) -> str:
    block = "  <script>\n" + JS.rstrip() + "\n  </script>"
    if MARKER in text:
        pat = re.compile(
            r"[ \t]*<script>\s*/\* KPI-PL-MEP-EXPORT \*/[\s\S]*?</script>",
            re.MULTILINE,
        )
        if not pat.search(text):
            raise SystemExit("export marker found but script block not matched")
        return pat.sub(lambda _m: block, text, count=1)
    if "</body>" not in text:
        raise SystemExit("no </body>")
    return text.replace("</body>", block + "\n</body>", 1)


def patch_pl_dl_menu(text: str, *, lang: str, base: str, img: str) -> str:
    """Replace legacy DL menu inside PL pages that are not marker-managed."""
    if 'id="kpi-export-pl-mep"' in text:
        return text
    if lang == "ja":
        heading = "雛形"
        daily = "支出雛形をダウンロード（日次）"
        monthly = "支出雛形をダウンロード（月次）"
        daily_file = "支出入力_日次_雛形.csv"
        monthly_file = "支出入力_月次_雛形.csv"
        data_heading = "データ出力"
        export_label = "収支データ（MEP＋PL）"
        export_aria = "MEPとPLの収支データをExcelでダウンロード（Pro）"
        dl_aria = "雛形・収支データのダウンロード"
        menu_aria = "ダウンロードメニュー"
    else:
        heading = "Templates"
        daily = "Download Expense Template (Daily)"
        monthly = "Download Expense Template (Monthly)"
        daily_file = "expense-import_daily_template.csv"
        monthly_file = "expense-import_monthly_template.csv"
        data_heading = "Data export"
        export_label = "P&L data (MEP + PL)"
        export_aria = "Download MEP and PL workbook as Excel (Pro)"
        dl_aria = "Download templates and P&amp;L data"
        menu_aria = "Download menu"

    new_inner = f"""          <div class="template-dl-menu" role="menu" aria-label="{menu_aria}">
            <p class="template-dl-heading">{heading}</p>
            <a href="{img}excel/{daily_file}" download class="template-dl-item" role="menuitem">{daily}</a>
            <a href="{img}excel/{monthly_file}" download class="template-dl-item" role="menuitem">{monthly}</a>
            <hr class="template-dl-sep" aria-hidden="true">
            <p class="template-dl-heading">{data_heading}</p>
            <button type="button" class="template-dl-item template-dl-item--export" id="kpi-export-pl-mep" role="menuitem" data-kpi-change-plan="{base}setting/change_plan.html" aria-label="{export_aria}">{export_label}</button>
          </div>"""

    pat = re.compile(
        r'<div class="template-dl-menu" role="menu"[^>]*>[\s\S]*?</div>\s*</details>',
        re.MULTILINE,
    )
    m = pat.search(text)
    if not m:
        return text
    # Also refresh summary aria if present
    text2 = re.sub(
        r'(<summary class="header-dl-btn" aria-label=")[^"]*(">)',
        rf'\1{dl_aria}\2',
        text,
        count=1,
    )
    return pat.sub(new_inner + "\n        </details>", text2, count=1)


def iter_targets() -> list[Path]:
    out: list[Path] = []
    for g in TARGET_GLOBS:
        out.extend(sorted(ROOT.glob(g)))
    # unique
    seen = set()
    uniq = []
    for p in out:
        if p in seen or not p.is_file():
            continue
        seen.add(p)
        uniq.append(p)
    return uniq


def main() -> None:
    # Refresh marker-managed headers (app / settings / monthly-edit).
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "build_site_chrome.py"), "app", "settings", "generated"],
        cwd=str(ROOT / "scripts"),
    )
    if rc != 0:
        raise SystemExit(f"build_site_chrome failed: {rc}")

    for path in iter_targets():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        if "profit/pl/" in rel:
            lang = "en" if rel.startswith("en/") else "ja"
            # PL depth: app/profit/pl → ../../../
            text = patch_pl_dl_menu(text, lang=lang, base="../../../", img="../../../../" if lang == "en" else "../../../")
            # JA PL asset prefix in existing pages uses ../../../ for both sometimes — detect from excel href
            if lang == "ja" and 'href="../../../excel/' in text:
                pass
            elif lang == "en" and 'href="../../../../excel/' not in text and 'href="../../../excel/' in text:
                text = patch_pl_dl_menu(text, lang=lang, base="../../../", img="../../../")
        text = inject_script(text)
        path.write_text(text, encoding="utf-8")
        print(f"patched: {rel}")


if __name__ == "__main__":
    main()

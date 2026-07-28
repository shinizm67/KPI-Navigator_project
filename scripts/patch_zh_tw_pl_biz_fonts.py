#!/usr/bin/env python3
"""zh-tw PL: apply BIZ UDPGothic for all text and numbers (locale font policy).

Duplicates html[lang='ja'] CSS overrides for zh-TW / zh, and forces the PL table
base font off Orbitron for CJK locales. See docs/font-locale-policy.md.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "profit" / "pl" / "index.html"

MARKER = "/* KPI-PL-ZH-TW-BIZ-FONT */"

TABLE_OVERRIDE = f"""
    {MARKER}
    /* Non-alphabet locales (docs/font-locale-policy.md): labels + numbers → BIZ */
    html[lang='ja'] .pl-table.pl-table--v1,
    html[lang='zh-TW'] .pl-table.pl-table--v1,
    html[lang^='zh'] .pl-table.pl-table--v1,
    html[lang='ja'] .pl-table:not(.pl-table--v1),
    html[lang='zh-TW'] .pl-table:not(.pl-table--v1),
    html[lang^='zh'] .pl-table:not(.pl-table--v1) {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
    /* Toolbar / chrome numbers & copy (year select, buttons, header menus) */
    html[lang='zh-TW'] body.si-fi .pl-year-label,
    html[lang='zh-TW'] body.si-fi .pl-year-select,
    html[lang='zh-TW'] body.si-fi .pl-toolbar__btn,
    html[lang='zh-TW'] body.si-fi .pl-toolbar__back,
    html[lang='zh-TW'] body.si-fi .pl-toolbar__zoom,
    html[lang='zh-TW'] body.si-fi .pl-toolbar__zoom-step,
    html[lang='zh-TW'] body.si-fi .pl-toolbar__zoom-edit,
    html[lang='zh-TW'] body.si-fi .header-dl-btn,
    html[lang='zh-TW'] body.si-fi .template-dl-heading,
    html[lang='zh-TW'] body.si-fi .template-dl-item,
    html[lang='zh-TW'] body.si-fi .account-settings-popup-title,
    html[lang='zh-TW'] body.si-fi .account-settings-heading,
    html[lang='zh-TW'] body.si-fi .account-settings-item,
    html[lang='zh-TW'] body.si-fi .kpi-daily-input-path__title,
    html[lang='zh-TW'] body.si-fi .kpi-daily-input-path__side,
    html[lang='zh-TW'] body.si-fi .btn-mode-text,
    html[lang='zh-TW'] body.si-fi .footer-copy,
    html[lang='zh-TW'] body.si-fi .sales-data-modal__close-chooser-title,
    html[lang='zh-TW'] body.si-fi .sales-data-modal__close-chooser-msg,
    html[lang='zh-TW'] body.si-fi .sales-data-modal__close-chooser-btn,
    html[lang^='zh'] body.si-fi .pl-year-label,
    html[lang^='zh'] body.si-fi .pl-year-select,
    html[lang^='zh'] body.si-fi .pl-toolbar__btn,
    html[lang^='zh'] body.si-fi .pl-toolbar__back,
    html[lang^='zh'] body.si-fi .pl-toolbar__zoom,
    html[lang^='zh'] body.si-fi .pl-toolbar__zoom-step,
    html[lang^='zh'] body.si-fi .pl-toolbar__zoom-edit,
    html[lang^='zh'] body.si-fi .header-dl-btn,
    html[lang^='zh'] body.si-fi .template-dl-heading,
    html[lang^='zh'] body.si-fi .template-dl-item,
    html[lang^='zh'] body.si-fi .account-settings-popup-title,
    html[lang^='zh'] body.si-fi .account-settings-heading,
    html[lang^='zh'] body.si-fi .account-settings-item,
    html[lang^='zh'] body.si-fi .kpi-daily-input-path__title,
    html[lang^='zh'] body.si-fi .kpi-daily-input-path__side,
    html[lang^='zh'] body.si-fi .btn-mode-text,
    html[lang^='zh'] body.si-fi .footer-copy,
    html[lang^='zh'] body.si-fi .sales-data-modal__close-chooser-title,
    html[lang^='zh'] body.si-fi .sales-data-modal__close-chooser-msg,
    html[lang^='zh'] body.si-fi .sales-data-modal__close-chooser-btn {{
      font-family: 'BIZ UDPGothic', sans-serif;
    }}
"""


def patch(text: str) -> str:
    m = re.search(r"(<style[^>]*>)(.*?)(</style>)", text, re.S)
    if not m:
        raise SystemExit("no <style> block")
    css = m.group(2)

    css2 = css
    expanded_rules = 0
    if "html[lang='zh-TW'] .pl-table--v1 .pl-amt-cell__text" not in css:
        out: list[str] = []
        pos = 0
        for rm in re.finditer(r"([^{}@][^{]*)\{([^{}]*)\}", css):
            out.append(css[pos : rm.start()])
            sel, body = rm.group(1), rm.group(2)
            pos = rm.end()

            if "html[lang='ja']" not in sel:
                out.append(rm.group(0))
                continue
            if "html[lang='zh-TW']" in sel or "html[lang^='zh']" in sel:
                out.append(rm.group(0))
                continue

            parts = [p.strip() for p in sel.split(",") if p.strip()]
            extra: list[str] = []
            for p in parts:
                if "html[lang='ja']" not in p:
                    continue
                extra.append(p.replace("html[lang='ja']", "html[lang='zh-TW']", 1))
                extra.append(p.replace("html[lang='ja']", "html[lang^='zh']", 1))
            if not extra:
                out.append(rm.group(0))
                continue
            expanded_rules += 1
            new_sel = ",\n    ".join(parts + extra)
            lead = re.match(r"^\s*", sel).group(0)
            out.append(f"{lead}{new_sel} {{{body}}}")

        out.append(css[pos:])
        css2 = "".join(out)
        print(f"expanded rules: {expanded_rules}")
    else:
        print("ja→zh selector expansion already present")

    needs_chrome = "body.si-fi .footer-copy" not in css2 or "body.si-fi .sales-data-modal__close-chooser-btn" not in css2
    if MARKER not in css2 or needs_chrome:
        # Refresh marker block if an older shorter version exists
        if MARKER in css2:
            css2 = re.sub(
                rf"\n    {re.escape(MARKER)}\n    /\* Non-alphabet locales[\s\S]*?font-family: 'BIZ UDPGothic', sans-serif;\n    \}}",
                "\n" + TABLE_OVERRIDE.rstrip() ,
                css2,
                count=1,
            )
            if "body.si-fi .footer-copy" not in css2:
                raise SystemExit("failed to refresh marker block")
            print("refreshed table/chrome BIZ override")
        else:
            anchor = (
                "    .pl-table.pl-table--v1 {\n"
                "      border-collapse: collapse;\n"
                "      border-spacing: 0;\n"
                "      table-layout: fixed;\n"
                "      border-top: var(--pl-cell-border);\n"
                "      border-bottom: var(--pl-cell-border);\n"
                "      margin: 0;\n"
                "      border-radius: 0;\n"
                "      font-family: 'Orbitron', sans-serif;\n"
                "    }"
            )
            if anchor not in css2:
                raise SystemExit("table Orbitron anchor miss")
            css2 = css2.replace(anchor, anchor + "\n" + TABLE_OVERRIDE, 1)
            print("inserted table/chrome BIZ override")
    else:
        print("chrome BIZ override already present")

    return text[: m.start(2)] + css2 + text[m.end(2) :]


def verify(text: str) -> None:
    style = re.search(r"<style[^>]*>(.*?)</style>", text, re.S).group(1)
    checks = [
        ("marker", MARKER in style),
        ("amt-cell zh-TW", "html[lang='zh-TW'] .pl-table--v1 .pl-amt-cell__text" in style),
        ("ratio-cell zh-TW", "html[lang='zh-TW'] .pl-table--v1 .pl-ratio-cell__text" in style),
        ("month-cell zh-TW", "html[lang='zh-TW'] .pl-table--v1 .pl-month-cell__text" in style),
        ("sub-amt zh-TW", "html[lang='zh-TW'] .pl-table--v1 .pl-sub-amt__text" in style),
        ("table base BIZ", "html[lang='zh-TW'] .pl-table.pl-table--v1" in style),
        ("compare tooltip zh", "html[lang='zh-TW'] .pl-compare-chart-tooltip" in style),
        ("year select BIZ", "body.si-fi .pl-year-select" in style),
        ("toolbar btn BIZ", "body.si-fi .pl-toolbar__btn" in style),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
        if not ok:
            raise SystemExit(1)
    print("verify: ALL OK")


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = patch(DST.read_text(encoding="utf-8"))
    DST.write_text(text, encoding="utf-8")
    verify(DST.read_text(encoding="utf-8"))
    print("patch_zh_tw_pl_biz_fonts: OK")


if __name__ == "__main__":
    main()

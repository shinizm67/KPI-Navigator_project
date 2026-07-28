#!/usr/bin/env python3
"""zh-tw monthly/annual: BIZ UDPGothic for labels AND numbers (Sci-Fi included).

1. Expand html[lang='ja'] font-family overrides → zh-TW / zh
2. Append catch-all BIZ block (overrides remaining Orbitron on numbers)
3. Remove Orbitron from zh-tw/setting Google Fonts links

See docs/font-locale-policy.md
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "zh-tw" / "app" / "monthly" / "index.html",
    ROOT / "zh-tw" / "app" / "annual" / "index.html",
]
SETTING_DIR = ROOT / "zh-tw" / "setting"

MARKER = "/* KPI-MONTHLY-ANNUAL-ZH-TW-BIZ-FONT */"

CATCH_ALL = f"""
    {MARKER}
    /* Non-EN (zh-TW): Sci-Fi でもラベル・数値とも BIZ。Orbitron 個別指定より後段・高特异性で上書き */
    html[lang='zh-TW'] body,
    html[lang='zh-TW'] body *:not(script):not(style),
    html[lang^='zh'] body,
    html[lang^='zh'] body *:not(script):not(style) {{
      font-family: 'BIZ UDPGothic', 'BIZ UDP Gothic', sans-serif;
    }}
"""


def expand_ja_font_rules(text: str) -> tuple[str, int]:
    style_m = re.search(r"(<style[^>]*>)(.*?)(</style>)", text, re.S)
    if not style_m:
        return text, 0
    css = style_m.group(2)

    out: list[str] = []
    pos = 0
    changed = 0
    for rm in re.finditer(r"([^{}@][^{]*)\{([^{}]*)\}", css):
        out.append(css[pos : rm.start()])
        selector = rm.group(1)
        body = rm.group(2)
        pos = rm.end()

        sel_has_ja = ("html[lang='ja']" in selector) or ('html[lang="ja"]' in selector)
        if (not sel_has_ja) or ("font-family" not in body):
            out.append(rm.group(0))
            continue

        if "html[lang='zh-TW']" in selector or 'html[lang="zh-TW"]' in selector:
            out.append(rm.group(0))
            continue

        parts = [p.strip() for p in selector.split(",") if p.strip()]
        extra: list[str] = []
        for p in parts:
            if "html[lang='ja']" in p:
                extra.append(p.replace("html[lang='ja']", "html[lang='zh-TW']", 1))
                extra.append(p.replace("html[lang='ja']", "html[lang^='zh']", 1))
            elif 'html[lang="ja"]' in p:
                extra.append(p.replace('html[lang="ja"]', 'html[lang="zh-TW"]', 1))
                extra.append(p.replace('html[lang="ja"]', 'html[lang^="zh"]', 1))

        if not extra:
            out.append(rm.group(0))
            continue

        lead = re.match(r"^\s*", selector).group(0)
        new_sel = ",\n    ".join(parts + extra)
        out.append(f"{lead}{new_sel} {{{body}}}")
        changed += 1

    out.append(css[pos:])
    css2 = "".join(out)
    return text[: style_m.start(2)] + css2 + text[style_m.end(2) :], changed


def insert_catch_all_biz(text: str) -> tuple[str, bool]:
    style_m = re.search(r"(<style[^>]*>)(.*?)(</style>)", text, re.S)
    if not style_m:
        return text, False
    css = style_m.group(2)
    if MARKER in css:
        css = re.sub(
            rf"\n\s*{re.escape(MARKER)}[\s\S]*?font-family: 'BIZ UDPGothic'.*?\n\s*\}}",
            "",
            css,
            count=1,
        )
    css = css.rstrip() + "\n" + CATCH_ALL + "\n    "
    return text[: style_m.start(2)] + css + text[style_m.end(2) :], True


def cleanup_setting_font_links(text: str) -> tuple[str, int]:
    old = (
        "https://fonts.googleapis.com/css2?"
        "family=BIZ+UDP+Gothic:wght@400;500;700&"
        "family=Orbitron:wght@400;500;600;700&display=swap"
    )
    new = (
        "https://fonts.googleapis.com/css2?"
        "family=BIZ+UDP+Gothic:wght@400;500;700&display=swap"
    )
    count = text.count(old)
    if count == 0:
        return text, 0
    return text.replace(old, new), count


def verify_target(text: str, label: str) -> None:
    style = re.search(r"<style[^>]*>(.*?)</style>", text, re.S)
    if not style:
        raise SystemExit(f"{label}: no <style>")
    css = style.group(1)
    checks = [
        ("marker", MARKER in css),
        ("catch-all zh-TW body", "html[lang='zh-TW'] body," in css),
        ("BIZ in catch-all", "'BIZ UDPGothic', 'BIZ UDP Gothic'" in css),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), label, name)
        if not ok:
            raise SystemExit(1)


def patch_targets() -> None:
    total_rules = 0
    for target in TARGETS:
        src = target.read_text(encoding="utf-8")
        patched, rules = expand_ja_font_rules(src)
        patched, _ = insert_catch_all_biz(patched)
        target.write_text(patched, encoding="utf-8")
        verify_target(patched, str(target.relative_to(ROOT)))
        total_rules += rules
        print(f"{target}: expanded {rules} font override rules + catch-all BIZ")
    print(f"total expanded rules: {total_rules}")


def patch_setting() -> None:
    total_files = 0
    for path in sorted(SETTING_DIR.glob("*.html")):
        src = path.read_text(encoding="utf-8")
        patched, count = cleanup_setting_font_links(src)
        if count > 0:
            path.write_text(patched, encoding="utf-8")
            total_files += 1
    print(f"setting files cleaned: {total_files}")


def main() -> None:
    patch_targets()
    patch_setting()
    print("patch_zh_tw_monthly_annual_biz_fonts: OK")


if __name__ == "__main__":
    main()

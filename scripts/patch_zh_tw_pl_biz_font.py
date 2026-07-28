#!/usr/bin/env python3
"""zh-tw PL: force BIZ UDPGothic for all Sci-Fi UI including numbers.

Product rule (docs/local-dev-notes.md): Orbitron only for alphabet locales (EN).
JA / zh-TW / Office use BIZ for labels AND numeric cells — no mixed fonts.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "profit" / "pl" / "index.html"

MARKER = "/* KPI-PL-ZH-TW-BIZ-FONT */"

CATCH_ALL = """
    """ + MARKER + """
    /* Non-EN (zh-TW): Sci-Fi でもラベル・数値とも BIZ。Orbitron 個別指定より後段・高特异性で上書き */
    html[lang='zh-TW'] body:not(.office-mode),
    html[lang='zh-TW'] body:not(.office-mode) *:not(script):not(style),
    html[lang^='zh'] body:not(.office-mode),
    html[lang^='zh'] body:not(.office-mode) *:not(script):not(style) {
      font-family: 'BIZ UDPGothic', 'BIZ UDP Gothic', sans-serif;
    }
"""


def expand_ja_font_selectors(style: str) -> str:
    """html[lang='ja'] → also zh-TW / zh* when not already expanded on that token."""

    def repl(m: re.Match[str]) -> str:
        # Already part of a multi-lang list that includes zh-TW immediately after
        return (
            "html[lang='ja'],\n    html[lang='zh-TW'],\n    html[lang^='zh']"
        )

    # Only expand standalone html[lang='ja'] that is NOT already followed by zh-TW
    out = []
    i = 0
    key = "html[lang='ja']"
    while True:
        j = style.find(key, i)
        if j < 0:
            out.append(style[i:])
            break
        out.append(style[i:j])
        after = style[j + len(key) : j + len(key) + 80]
        if "zh-TW" in after.split("{")[0] or "lang^='zh'" in after.split("{")[0]:
            out.append(key)
        else:
            out.append(repl(None))  # type: ignore[arg-type]
        i = j + len(key)
    return "".join(out)


def patch(text: str) -> str:
    m = re.search(r"(<style[^>]*>)(.*?)(</style>)", text, re.S | re.I)
    if not m:
        raise SystemExit("no <style> block")
    style = m.group(2)
    style = expand_ja_font_selectors(style)
    if MARKER in style:
        # refresh catch-all: remove old block then re-append
        style = re.sub(
            rf"\n\s*{re.escape(MARKER)}.*?font-family: 'BIZ UDPGothic'.*?\n",
            "\n",
            style,
            count=1,
            flags=re.S,
        )
    style = style.rstrip() + "\n" + CATCH_ALL + "\n    "
    return text[: m.start(2)] + style + text[m.end(2) :]


def verify(text: str) -> None:
    checks = [
        ("marker", MARKER in text),
        ("catch-all zh-TW", "html[lang='zh-TW'] body:not(.office-mode)" in text),
        ("BIZ in catch-all", "'BIZ UDPGothic', 'BIZ UDP Gothic'" in text),
        ("ja expanded sample", "html[lang='zh-TW']" in text),
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
    print(f"patched {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

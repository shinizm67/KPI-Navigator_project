#!/usr/bin/env python3
"""Inject locale-filtered footer language switcher CSS into all pages.

Policy: docs/lang-switcher-locale-policy.md
- ja: JP + EN only (hide TW)
- zh-TW: TW + EN only (hide JA)
- en: hide entire #lang-select-wrap

Preferences #pref-lang keeps full JP/EN/TW (not affected).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MARKER = "KPI-LANG-SWITCHER-LOCALE"

STYLE_BLOCK = f"""  <style id="kpi-lang-switcher-locale">
    /* {MARKER}: footer shortcut = native + EN only (see docs/lang-switcher-locale-policy.md) */
    html[lang='ja'] .lang-option-zh-tw {{
      display: none !important;
    }}
    html[lang='zh-TW'] .lang-option-ja,
    html[lang^='zh'] .lang-option-ja {{
      display: none !important;
    }}
    html[lang='en'] #lang-select-wrap {{
      display: none !important;
    }}
  </style>
"""


def iter_html() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*.html"):
        if any(x in p.parts for x in (".git", "node_modules", ".specstory")):
            continue
        out.append(p)
    return sorted(out)


def patch(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if 'id="lang-select-wrap"' not in text:
        return "skip"
    if MARKER in text:
        # refresh existing block
        import re

        new_text, n = re.subn(
            r'[ \t]*<style id="kpi-lang-switcher-locale">[\s\S]*?</style>\s*',
            STYLE_BLOCK,
            text,
            count=1,
        )
        if n:
            path.write_text(new_text, encoding="utf-8")
            return "refresh"
        return "present"

    if "</head>" not in text:
        return "no-head"

    text = text.replace("</head>", STYLE_BLOCK + "</head>", 1)
    path.write_text(text, encoding="utf-8")
    return "inject"


def main() -> int:
    counts = {"inject": 0, "refresh": 0, "present": 0, "skip": 0, "no-head": 0}
    for path in iter_html():
        status = patch(path)
        counts[status] = counts.get(status, 0) + 1
        if status in ("inject", "refresh"):
            print(f"{status}: {path.relative_to(ROOT)}")
    print("---")
    for k, v in sorted(counts.items()):
        print(f"{k}: {v}")
    if counts["inject"] + counts["refresh"] + counts["present"] == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

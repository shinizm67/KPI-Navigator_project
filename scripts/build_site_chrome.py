#!/usr/bin/env python3
"""Inject canonical Global Menu header + footer into pages (single source).

First run replaces the existing `<header class="site-header">…</header>` and
`<footer class="site-footer">…</footer>` blocks with marker-wrapped generated
markup. Subsequent runs replace only the content between markers, so this is
idempotent and safe to re-run.

Rollout is staged via PAGES groups. Pilot = app body pages only.
Add settings / legal / login / register groups in later increments.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from site_chrome import (
    FOOTER_MARK_END,
    FOOTER_MARK_START,
    HEADER_MARK_END,
    HEADER_MARK_START,
    build_footer,
    build_header,
)

ROOT = Path(__file__).resolve().parents[1]

# Pilot group: hand-authored app body pages (annual / monthly / profit, JA+EN).
# base = path to language root; img = path to repo-root images/.
# daily: "overlay" = page hosts the Daily floating window (annual/monthly);
#        "link"    = page navigates to Annual for Daily (profit).
# profit_label: per-page override to preserve current wording (drift); omit to
#        use the language default.
PAGES_APP = [
    {"path": "app/annual/index.html", "lang": "ja", "base": "../../", "img": "../../", "active": "annual", "daily": "overlay"},
    {"path": "app/monthly/index.html", "lang": "ja", "base": "../../", "img": "../../", "active": "monthly", "daily": "overlay"},
    {"path": "app/profit/index.html", "lang": "ja", "base": "../../", "img": "../../", "active": "profit", "daily": "link"},
    {"path": "en/app/annual/index.html", "lang": "en", "base": "../../", "img": "../../../", "active": "annual", "daily": "overlay"},
    {"path": "en/app/monthly/index.html", "lang": "en", "base": "../../", "img": "../../../", "active": "monthly", "daily": "overlay"},
    {"path": "en/app/profit/index.html", "lang": "en", "base": "../../", "img": "../../../", "active": "profit", "daily": "link", "profit_label": "Profit"},
]

GROUPS = {"app": PAGES_APP}


def _replace_block(text: str, start: str, end: str, raw_re: str, replacement: str, label: str, path: Path) -> str:
    marked = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
    if marked.search(text):
        return marked.sub(lambda _m: replacement, text, count=1)
    raw = re.compile(raw_re)
    if not raw.search(text):
        raise SystemExit(f"{path}: {label} block not found (neither markers nor raw)")
    return raw.sub(lambda _m: replacement, text, count=1)


def patch_page(cfg: dict) -> None:
    path = ROOT / cfg["path"]
    if not path.is_file():
        raise SystemExit(f"missing page: {path}")
    text = path.read_text(encoding="utf-8")

    header = build_header(
        cfg["lang"], cfg["base"], cfg["img"], cfg["active"],
        daily_mode=cfg.get("daily", "overlay"),
        profit_label=cfg.get("profit_label"),
    )
    footer = build_footer(cfg["lang"], cfg["img"])
    header_repl = f"  {HEADER_MARK_START}\n{header}\n  {HEADER_MARK_END}"
    footer_repl = f"  {FOOTER_MARK_START}\n{footer}\n  {FOOTER_MARK_END}"

    text = _replace_block(
        text, HEADER_MARK_START, HEADER_MARK_END,
        r'[ \t]*<header class="site-header">[\s\S]*?</header>',
        header_repl, "header", path,
    )
    text = _replace_block(
        text, FOOTER_MARK_START, FOOTER_MARK_END,
        r'[ \t]*<footer class="site-footer">[\s\S]*?</footer>',
        footer_repl, "footer", path,
    )
    path.write_text(text, encoding="utf-8")
    print(f"patched {cfg['path']}")


def main(argv: list[str]) -> int:
    groups = argv[1:] or ["app"]
    for g in groups:
        if g not in GROUPS:
            print(f"unknown group: {g} (available: {', '.join(GROUPS)})", file=sys.stderr)
            return 2
    for g in groups:
        for cfg in GROUPS[g]:
            patch_page(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

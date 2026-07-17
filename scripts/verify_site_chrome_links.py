#!/usr/bin/env python3
"""Verify every link/asset inside the generated site-chrome resolves to a real file.

For each registered page, extract the header + footer marker regions, collect
all local `href` / `src` / `data-href-pro` / `data-href-basic` targets, resolve
them relative to the page's own directory, and assert the target file exists.
External (http/https), in-page (`#`), and mailto links are skipped.

This is the safety net for the Global Menu commonization: it proves that no
hyperlink was broken by the path normalization.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from build_site_chrome import GROUPS
from site_chrome import (
    FOOTER_MARK_END,
    FOOTER_MARK_START,
    HEADER_MARK_END,
    HEADER_MARK_START,
)

ROOT = Path(__file__).resolve().parents[1]

ATTR_RE = re.compile(r'(?:href|src|data-href-pro|data-href-basic)="([^"]*)"')


def _region(text: str, start: str, end: str) -> str:
    m = re.search(re.escape(start) + r"([\s\S]*?)" + re.escape(end), text)
    return m.group(1) if m else ""


def _is_local(target: str) -> bool:
    if not target:
        return False
    if target.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#", "javascript:")):
        return False
    return True


def check_page(cfg: dict) -> list[str]:
    path = ROOT / cfg["path"]
    errs: list[str] = []
    if not path.is_file():
        return [f"{cfg['path']}: file missing"]
    text = path.read_text(encoding="utf-8")

    header = _region(text, HEADER_MARK_START, HEADER_MARK_END)
    footer = _region(text, FOOTER_MARK_START, FOOTER_MARK_END)
    if not header:
        errs.append(f"{cfg['path']}: header markers not found")
    if not footer:
        errs.append(f"{cfg['path']}: footer markers not found")

    page_dir = path.parent
    seen = set()
    for region_name, region in (("header", header), ("footer", footer)):
        for target in ATTR_RE.findall(region):
            base_target = target.split("#", 1)[0].split("?", 1)[0]
            if not _is_local(base_target):
                continue
            key = (region_name, base_target)
            if key in seen:
                continue
            seen.add(key)
            resolved = (page_dir / base_target).resolve()
            if not resolved.exists():
                errs.append(f"{cfg['path']} [{region_name}]: broken -> {target} ({resolved})")
    return errs


def main(argv: list[str]) -> int:
    groups = argv[1:] or ["app"]
    all_errs: list[str] = []
    checked = 0
    for g in groups:
        if g not in GROUPS:
            print(f"unknown group: {g}", file=sys.stderr)
            return 2
        for cfg in GROUPS[g]:
            all_errs.extend(check_page(cfg))
            checked += 1
    if all_errs:
        print("FAIL: broken site-chrome links")
        for e in all_errs:
            print(" -", e)
        return 1
    print(f"OK: site-chrome links resolve on {checked} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

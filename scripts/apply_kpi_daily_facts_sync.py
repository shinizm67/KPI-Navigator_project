#!/usr/bin/env python3
"""Phase 2c: inject kpi-daily-facts-sync.js next to gateway / busy overlay."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]


def inject_script(text: str) -> str:
    if "kpi-daily-facts-sync.js" in text:
        if "/js/kpi-daily-facts-sync.js" in text or "js/kpi-daily-facts-sync.js" in text:
            return text
        text = re.sub(
            r'src="((?:\.\./)+)kpi-daily-facts-sync\.js"',
            r'src="\1js/kpi-daily-facts-sync.js"',
            text,
        )
        return text
    for needle in (
        "js/kpi-busy-overlay.js",
        "js/kpi-data-gateway.js",
        "js/kpi-currency.js",
    ):
        m = re.search(r'<script src="([^"]+)' + re.escape(needle) + r'"></script>', text)
        if not m:
            continue
        prefix = m.group(1)
        tag = m.group(0)
        injected = tag + f'\n  <script src="{prefix}js/kpi-daily-facts-sync.js"></script>'
        return text[: m.start()] + injected + text[m.end() :]
    raise SystemExit("no script anchor found")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        text2 = inject_script(text)
        if text2 != text:
            path.write_text(text2, encoding="utf-8")
            print(f"script {path.relative_to(ROOT)}")
        else:
            print(f"skip {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

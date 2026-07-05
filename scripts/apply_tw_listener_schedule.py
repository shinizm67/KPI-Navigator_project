#!/usr/bin/env python3
"""Point TW event listeners at scheduleRenderAnnualDailyTimeline (debounced)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

DIRECT = "renderAnnualDailyTimeline(cy, { preserveScroll: true });"
SCHEDULED = "scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true });"


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if DIRECT not in text:
        if SCHEDULED in text:
            print(f"skip (already scheduled) {path.relative_to(ROOT)}")
            return
        raise SystemExit(f"listener pattern not found in {path}")
    count = text.count(DIRECT)
    text = text.replace(DIRECT, SCHEDULED)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({count} listener(s))")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Re-run placeTargetSalesGroup after layout / cockpit refresh."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

ANCHOR_OLD = """      placeTargetSalesGroup();
      window.addEventListener('resize', placeTargetSalesGroup);
      requestAnimationFrame(placeTargetSalesGroup);"""

ANCHOR_NEW = """      placeTargetSalesGroup();
      window.addEventListener('resize', placeTargetSalesGroup);
      requestAnimationFrame(placeTargetSalesGroup);
      document.addEventListener('annual:timelineRowsRendered', placeTargetSalesGroup);
      document.addEventListener('kpi:readSurfacesRefresh', function () {
        requestAnimationFrame(placeTargetSalesGroup);
      });
      setTimeout(placeTargetSalesGroup, 150);"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if ANCHOR_OLD not in text:
        if "annual:timelineRowsRendered', placeTargetSalesGroup" in text:
            print(f"skip (already patched) {path.relative_to(ROOT)}")
            return
        raise SystemExit(f"{path}: placeTargetSalesGroup anchor missing")
    text = text.replace(ANCHOR_OLD, ANCHOR_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

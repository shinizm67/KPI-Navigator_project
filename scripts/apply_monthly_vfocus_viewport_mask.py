#!/usr/bin/env python3
"""Punch a viewport hole in Monthly TW under the vFocus bar. Do not clip columns."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]

OLD = """      overflow-x: auto;
      overflow-y: hidden;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior-x: contain;
      overscroll-behavior-y: auto;
      z-index: 2;
      box-sizing: border-box;"""

NEW = """      overflow-x: auto;
      overflow-y: hidden;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior-x: contain;
      overscroll-behavior-y: auto;
      z-index: 2;
      box-sizing: border-box;
      /* KPI-VFOCUS-MASK: 縦帯の矩形だけ表を描かない。列ごと切らない */
      --monthly-vfocus-cut-left: 303px;
      --monthly-vfocus-cut-right: 438px;
      -webkit-mask-image: linear-gradient(
        to right,
        #000 0,
        #000 var(--monthly-vfocus-cut-left),
        transparent var(--monthly-vfocus-cut-left),
        transparent var(--monthly-vfocus-cut-right),
        #000 var(--monthly-vfocus-cut-right)
      );
      mask-image: linear-gradient(
        to right,
        #000 0,
        #000 var(--monthly-vfocus-cut-left),
        transparent var(--monthly-vfocus-cut-left),
        transparent var(--monthly-vfocus-cut-right),
        #000 var(--monthly-vfocus-cut-right)
      );
      -webkit-mask-size: 100% 100%;
      mask-size: 100% 100%;
      -webkit-mask-repeat: no-repeat;
      mask-repeat: no-repeat;"""


def main() -> int:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        cnt = text.count(OLD)
        if cnt == 0:
            if NEW in text:
                print(f"  skip already {path.relative_to(ROOT)}")
                continue
            raise SystemExit(f"  ERROR not found: {path.relative_to(ROOT)}")
        if cnt != 1:
            raise SystemExit(f"  ERROR found {cnt}: {path.relative_to(ROOT)}")
        print(f"  patch {path.relative_to(ROOT)}")
        path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Stop Monthly vFocus from copying TW numbers. Frame only; table is the single source."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    cnt = text.count(old)
    if cnt == 0:
        if new in text:
            print(f"  skip {label} (already) {path.relative_to(ROOT)}")
            return text
        raise SystemExit(f"  ERROR {label} not found: {path.relative_to(ROOT)}")
    if cnt != 1:
        raise SystemExit(f"  ERROR {label} found {cnt}: {path.relative_to(ROOT)}")
    print(f"  patch {label} {path.relative_to(ROOT)}")
    return text.replace(old, new, 1)


MASK_OLD = """      box-sizing: border-box;
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
      mask-repeat: no-repeat;
      scrollbar-color: #58e1f3 #1f1e1e;"""

MASK_NEW = """      box-sizing: border-box;
      scrollbar-color: #58e1f3 #1f1e1e;"""

FILL_OLD = """      pointer-events: none;
      background: #000;
      isolation: isolate;
    }
    .office-mode .monthly-vfocus-fill {
      background: #2a2a2a;
    }"""

FILL_NEW = """      pointer-events: none;
      background: transparent;
    }
    .office-mode .monthly-vfocus-fill {
      background: transparent;
    }"""

LANES_OLD = """    .monthly-vfocus-lanes {
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      justify-content: flex-start;
      gap: 0;
      width: 300%;
      box-sizing: border-box;
      transform: translateX(-33.333333%);
    }"""

LANES_NEW = """    .monthly-vfocus-lanes {
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      justify-content: flex-start;
      gap: 0;
      width: 300%;
      box-sizing: border-box;
      transform: translateX(-33.333333%);
      visibility: hidden;
    }"""


def main() -> int:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        text = replace_once(text, MASK_OLD, MASK_NEW, "unmask", path)
        text = replace_once(text, FILL_OLD, FILL_NEW, "fill", path)
        text = replace_once(text, LANES_OLD, LANES_NEW, "lanes", path)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

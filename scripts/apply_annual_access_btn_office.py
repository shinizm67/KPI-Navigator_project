#!/usr/bin/env python3
"""Annual Past Sales / Sales: Office Mode = CSS box buttons (no SVG frame)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER_START = "    /* ===== ANNUAL-ACCESS-BTN-OFFICE-START ===== */"
MARKER_END = "    /* ===== ANNUAL-ACCESS-BTN-OFFICE-END ===== */"

# Same shape as Monthly UNLOCKED/EDIT; Past Sales = lavender, Sales = light gray.
BLOCK = f"""{MARKER_START}
    .office-mode .monthly-access-btn {{
      width: auto;
      min-width: 112px;
      height: 40px;
      padding: 0 14px;
      border: 1px solid #000;
      border-radius: 5px;
      background: #e8e8e8;
      color: #000;
      font-family: 'BIZ UDPGothic', sans-serif;
      font-size: 14px;
      letter-spacing: 0.01em;
      box-sizing: border-box;
    }}
    .office-mode .monthly-access-btn__frame {{
      display: none !important;
    }}
    .office-mode .monthly-access-btn__label {{
      color: inherit;
      transform: none;
    }}
    .office-mode .monthly-access-btn--past-sales:hover .monthly-access-btn__label,
    .office-mode .monthly-access-btn--past-sales:focus-visible .monthly-access-btn__label,
    .office-mode .monthly-access-btn--current-sales:hover .monthly-access-btn__label,
    .office-mode .monthly-access-btn--current-sales:focus-visible .monthly-access-btn__label {{
      text-shadow: none;
    }}
    .office-mode .monthly-access-btn--past-sales {{
      background: #dcecff;
      border-color: #2b6cb0;
      color: #0a2a5c;
    }}
    .office-mode .monthly-access-btn--past-sales:hover,
    .office-mode .monthly-access-btn--past-sales:focus-visible {{
      background: #c8daf0;
    }}
    .office-mode .monthly-access-btn--current-sales {{
      background: #f0f0f0;
      border-color: #000;
      color: #000;
    }}
    .office-mode .monthly-access-btn--current-sales:hover,
    .office-mode .monthly-access-btn--current-sales:focus-visible {{
      background: #e0e0e0;
    }}
{MARKER_END}
"""

# Incomplete / conflicting fragments left by earlier partial applies.
FRAGMENTS = [
    re.compile(
        r"\n    \.office-mode \.monthly-access-btn--past-sales \{\n"
        r"      background: #dcecff;\n"
        r"      border-radius: 2px;\n"
        r"    \}",
        re.M,
    ),
    re.compile(
        r"\n    \.office-mode \.monthly-access-btn--past-sales \{\n"
        r"      color: #0a2a5c;\n"
        r"    \}\n"
        r"    \.office-mode \.monthly-access-btn--past-sales \.monthly-access-btn__frame \{\n"
        r"      filter: none;\n"
        r"    \}",
        re.M,
    ),
]


def inject(text: str) -> str:
    for frag in FRAGMENTS:
        text = frag.sub("", text)

    if MARKER_START in text:
        start = text.find(MARKER_START)
        end = text.find(MARKER_END)
        if end < 0:
            raise SystemExit("end marker missing")
        end += len(MARKER_END)
        return text[:start] + BLOCK.rstrip() + "\n" + text[end:].lstrip("\n")

    # Insert once, just before the first Past Sales modal shell comment if present,
    # else before </style>.
    anchors = [
        "    /* Past Sales modal — PS-1 shell",
        "    /* Sales Data modal (current year) — PS-1 shell",
        "  </style>",
    ]
    for a in anchors:
        idx = text.find(a)
        if idx >= 0:
            return text[:idx] + BLOCK + "\n" + text[idx:]
    raise SystemExit("no insert anchor")


def main() -> None:
    for page in PAGES:
        raw = page.read_text(encoding="utf-8")
        page.write_text(inject(raw), encoding="utf-8")
        print("patched", page.relative_to(ROOT))


if __name__ == "__main__":
    main()

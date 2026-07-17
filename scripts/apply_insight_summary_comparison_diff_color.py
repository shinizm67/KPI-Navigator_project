#!/usr/bin/env python3
"""Insight Summary Comparison の差分値に既存 tw-diff 色を適用（CSSのみ・4ページ）."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "insight-monthly-comparison__value.tw-diff--win"

# Add Comparison value selectors beside existing Insight summary severity targets.
# Keep other selectors untouched.
REPLACEMENTS = [
    (
        """.insight-daily-kpi__value.tw-diff--{lvl},
    .insight-monthly-sales-summary__value.tw-diff--{lvl},
    .insight-annual-sales-summary__value.tw-diff--{lvl} {{""",
        """.insight-daily-kpi__value.tw-diff--{lvl},
    .insight-monthly-sales-summary__value.tw-diff--{lvl},
    .insight-annual-sales-summary__value.tw-diff--{lvl},
    .insight-monthly-comparison__value.tw-diff--{lvl},
    .insight-annual-comparison__value.tw-diff--{lvl} {{""",
    ),
    (
        """.office-mode .insight-daily-kpi__value.tw-diff--{lvl},
    .office-mode .insight-monthly-sales-summary__value.tw-diff--{lvl},
    .office-mode .insight-annual-sales-summary__value.tw-diff--{lvl} {{""",
        """.office-mode .insight-daily-kpi__value.tw-diff--{lvl},
    .office-mode .insight-monthly-sales-summary__value.tw-diff--{lvl},
    .office-mode .insight-annual-sales-summary__value.tw-diff--{lvl},
    .office-mode .insight-monthly-comparison__value.tw-diff--{lvl},
    .office-mode .insight-annual-comparison__value.tw-diff--{lvl} {{""",
    ),
]

LEVELS = (
    "win",
    "neutral",
    "sev-90",
    "sev-80",
    "sev-70",
    "sev-60",
    "sev-50",
    "sev-below",
)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already) {path.relative_to(ROOT)}")
        return
    if "/* KPI-DIFF-STEP3-INSIGHT-SEVERITY */" not in text:
        raise SystemExit(f"STEP3 marker miss: {path}")
    changed = 0
    for lvl in LEVELS:
        for old_t, new_t in REPLACEMENTS:
            old = old_t.format(lvl=lvl)
            new = new_t.format(lvl=lvl)
            if old not in text:
                raise SystemExit(f"selector miss lvl={lvl}: {path}\n{old[:80]}...")
            text = text.replace(old, new, 1)
            changed += 1
    if MARKER not in text:
        raise SystemExit(f"patch failed: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({changed} selector groups)")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

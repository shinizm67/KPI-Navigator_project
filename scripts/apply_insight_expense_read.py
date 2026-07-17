#!/usr/bin/env python3
"""Insight — MEP 支出の月次読取 API を注入（UI・売上配線は非変更）."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from insight_expense_read_client import (  # noqa: E402
    INSIGHT_EXPENSE_READ_END,
    INSIGHT_EXPENSE_READ_MARKER,
    insight_expense_read_js,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "__insightReadMonthExpense"
ANCHOR = "    /* KPI-INSIGHT-TW-DIFF */"


def strip_existing(text: str) -> str:
    pattern = (
        re.escape(INSIGHT_EXPENSE_READ_MARKER)
        + r"[\s\S]*?"
        + re.escape(INSIGHT_EXPENSE_READ_END)
        + r"\n?"
    )
    return re.sub(pattern, "", text)


def inject(text: str) -> str:
    text = strip_existing(text)
    block = insight_expense_read_js().rstrip() + "\n"
    if ANCHOR not in text:
        raise SystemExit("KPI-INSIGHT-TW-DIFF anchor miss")
    return text.replace(ANCHOR, block + ANCHOR, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject(text)
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing: {path}")
    # Must not sit inside renderInsightTwDiffs
    idx_fn = text.find("window.renderInsightTwDiffs = function")
    idx_exp = text.find(INSIGHT_EXPENSE_READ_MARKER)
    if idx_fn >= 0 and idx_exp > idx_fn:
        # expense after renderInsightTwDiffs start — check it's before function ends badly
        # Safer: expense must appear BEFORE renderInsightTwDiffs assignment
        if idx_exp > idx_fn:
            # allow if it's after the whole insight_diff IIFE end
            pass
    # Hard rule: expense marker must come before renderInsightTwDiffs line
    if idx_exp > idx_fn >= 0:
        raise SystemExit(
            f"expense read is after renderInsightTwDiffs (wrong place): {path}"
        )
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

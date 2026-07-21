#!/usr/bin/env python3
"""Insight: Analyze Annual Expense & Profit + Year Expense 横棒4本を実データ化."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_insight_expense_read import inject as inject_expense_read  # noqa: E402
from insight_diff_client import (  # noqa: E402
    INSIGHT_DIFF_JS_END,
    INSIGHT_DIFF_JS_MARKER,
    insight_diff_js,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKERS = (
    "patchAnalyzeAnnualExpenseProfit",
    "patchAnalyzeAnnualYearExpenseCharts",
    "insightReadYearExpenseThrough",
    "patchAnalyzeDualInsight",
)


def inject_insight_diff(text: str) -> str:
    block = insight_diff_js().rstrip() + "\n"
    if INSIGHT_DIFF_JS_MARKER not in text:
        raise SystemExit("insight diff marker miss")
    pattern = (
        re.escape(INSIGHT_DIFF_JS_MARKER)
        + r"[\s\S]*?"
        + re.escape(INSIGHT_DIFF_JS_END)
        + r"\n?"
    )
    return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_expense_read(text)
    text = inject_insight_diff(text)
    for marker in MARKERS:
        if marker not in text:
            raise SystemExit(f"{marker} missing: {path}")
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

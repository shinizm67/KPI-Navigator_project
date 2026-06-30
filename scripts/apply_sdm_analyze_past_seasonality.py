#!/usr/bin/env python3
"""Apply past-year averaged Seasonality % to Sales Data Analyze (Annual JA/EN)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sdm_analyze_past_seasonality_client import (  # noqa: E402
    ANALYZE_MODEL_END,
    ANALYZE_MODEL_MARKER,
    ANALYZE_MODEL_OLD,
    analyze_model_js,
)

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def replace_analyze_model(text: str) -> str:
    block = analyze_model_js().rstrip() + "\n"
    if ANALYZE_MODEL_MARKER in text:
        pattern = (
            re.escape(ANALYZE_MODEL_MARKER)
            + r"[\s\S]*?"
            + re.escape(ANALYZE_MODEL_END)
            + r"\n?"
        )
        return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
    if ANALYZE_MODEL_OLD not in text:
        if "computePastAverageDailySales" in text and "computeAverageSeasonalityPct" in text:
            return text
        raise SystemExit("buildSalesDataAnalyzeModel block not found")
    return text.replace(ANALYZE_MODEL_OLD, block.rstrip() + "\n", 1)


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        text = replace_analyze_model(text)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

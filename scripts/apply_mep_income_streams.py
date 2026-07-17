#!/usr/bin/env python3
"""Inject MEP → dailyIncome stream persistence (independent of the MEP-STORE block).

冪等: BEGIN..END マーカー間を丸ごと置換。未注入時のみアンカー直前へ挿入。
アンカー `window.__KPI_PATH_CHANGE_HOOKS__ = {` は MEP メインスクリプト内で一意、
rowValueById / mefYear と同一スコープ。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from mep_income_streams_client import (  # noqa: E402
    MEP_INCOME_STREAMS_BEGIN,
    MEP_INCOME_STREAMS_END,
    mep_income_streams_client_js,
)

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

ANCHOR = "      window.__KPI_PATH_CHANGE_HOOKS__ = {"


def inject(text: str) -> str:
    block = mep_income_streams_client_js().rstrip() + "\n"
    if MEP_INCOME_STREAMS_BEGIN in text:
        pattern = re.compile(
            re.escape(MEP_INCOME_STREAMS_BEGIN)
            + r"[\s\S]*?"
            + re.escape(MEP_INCOME_STREAMS_END)
            + r"\n",
        )
        if not pattern.search(text):
            raise ValueError("BEGIN marker present but BEGIN..END block not matched")
        return pattern.sub(lambda _m: block, text, count=1)
    if ANCHOR not in text:
        raise ValueError(f"anchor missing: {ANCHOR!r}")
    return text.replace(ANCHOR, block + ANCHOR, 1)


def main() -> int:
    for t in TARGETS:
        if not t.is_file():
            print(f"missing: {t}", file=sys.stderr)
            return 1
        text = t.read_text(encoding="utf-8")
        t.write_text(inject(text), encoding="utf-8")
        print(f"patched {t.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

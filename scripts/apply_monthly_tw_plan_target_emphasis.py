#!/usr/bin/env python3
"""Monthly Table Window — Plan Target Sales row emphasis (Income group + vFocus)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_monthly_tw_mep_metrics import patch_page as patch_mep_metrics  # noqa: E402
from monthly_tw_plan_target_emphasis_client import (  # noqa: E402
    DECORATE_NEW,
    DECORATE_OLD,
    LISTENERS_NEW,
    LISTENERS_OLD,
    MONTHLY_TW_PLAN_TARGET_ANCHOR,
    MONTHLY_TW_PLAN_TARGET_END,
    MONTHLY_TW_PLAN_TARGET_MARKER,
    VFOCUS_CELL_COPY_NEW,
    VFOCUS_CELL_COPY_OLD,
    monthly_tw_plan_target_emphasis_css,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]


def inject_css(text: str) -> str:
    block = monthly_tw_plan_target_emphasis_css().rstrip() + "\n"
    if MONTHLY_TW_PLAN_TARGET_MARKER in text:
        pattern = (
            re.escape(MONTHLY_TW_PLAN_TARGET_MARKER)
            + r"[\s\S]*?"
            + re.escape(MONTHLY_TW_PLAN_TARGET_END)
            + r"\n?"
        )
        return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)
    if MONTHLY_TW_PLAN_TARGET_ANCHOR not in text:
        raise SystemExit("KPI-MONTHLY-TW-DIFF-SEVERITY anchor missing")
    return text.replace(
        MONTHLY_TW_PLAN_TARGET_ANCHOR,
        MONTHLY_TW_PLAN_TARGET_ANCHOR + "\n" + block.rstrip(),
        1,
    )


def patch_decorate(text: str) -> str:
    if "monthly-data-column__cell--plan-target" in text and DECORATE_NEW.split("cellIndex === 3")[0] in text:
        return text
    if DECORATE_OLD in text:
        return text.replace(DECORATE_OLD, DECORATE_NEW, 1)
    if DECORATE_NEW in text:
        return text
    raise SystemExit("decorateMonthlyGroup1Cell patch miss")


def patch_vfocus(text: str) -> str:
    if "monthly-vfocus-cell--plan-target" in text and "ci2 === 3" in text:
        return text
    if VFOCUS_CELL_COPY_OLD in text:
        return text.replace(VFOCUS_CELL_COPY_OLD, VFOCUS_CELL_COPY_NEW, 1)
    if VFOCUS_CELL_COPY_NEW in text:
        return text
    raise SystemExit("monthly vfocus target patch miss")


def patch_listeners(text: str) -> str:
    if "kpi:dailyTargetModeChanged', monthlyTwRebuildKeepFocus" in text:
        return text
    if LISTENERS_OLD in text:
        return text.replace(LISTENERS_OLD, LISTENERS_NEW, 1)
    if LISTENERS_NEW in text:
        return text
    raise SystemExit("monthly TW listeners patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_css(text)
    text = patch_decorate(text)
    text = patch_vfocus(text)
    text = patch_listeners(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote CSS/JS {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_mep_metrics(path)
        print(f"wrote MEP {path.relative_to(ROOT)}")
    for path in PAGES:
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

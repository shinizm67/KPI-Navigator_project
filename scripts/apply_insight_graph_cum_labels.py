#!/usr/bin/env python3
"""Insight Graph Monthly/Annual 累計横棒のラベル文言のみ修正（他は非変更）."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

JA_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "app/annual/index.html",
]
EN_PAGES = [
    ROOT / "en/app/monthly/index.html",
    ROOT / "en/app/annual/index.html",
]

# Unique via graph id — Graph Daily の「本日（売上）」にはヒットしない
JA_MONTHLY_OLD = """                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kgi">
                        <span class="insight-graph-daily__marker-cap-line">本日（売上）</span>
                        <span class="insight-graph-daily__marker-cap-value">¥123,456,789</span>
                      </p>
                      <div class="insight-daily-alloc-graph" id="insight-graph-monthly-cumulative-target-actual">
                        <span class="insight-daily-alloc-marker-triangle" aria-hidden="true"></span>
                        <span class="insight-daily-alloc-marker-line" aria-hidden="true"></span>
                      </div>
                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kpi">
                        <span class="insight-graph-daily__marker-cap-line">本日の目標売上</span>
                        <span class="insight-graph-daily__marker-cap-value">¥100,456,789</span>
                      </p>"""

JA_MONTHLY_NEW = """                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kgi">
                        <span class="insight-graph-daily__marker-cap-line">累計実績</span>
                        <span class="insight-graph-daily__marker-cap-value">¥123,456,789</span>
                      </p>
                      <div class="insight-daily-alloc-graph" id="insight-graph-monthly-cumulative-target-actual">
                        <span class="insight-daily-alloc-marker-triangle" aria-hidden="true"></span>
                        <span class="insight-daily-alloc-marker-line" aria-hidden="true"></span>
                      </div>
                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kpi">
                        <span class="insight-graph-daily__marker-cap-line">累計目標</span>
                        <span class="insight-graph-daily__marker-cap-value">¥100,456,789</span>
                      </p>"""

JA_ANNUAL_OLD = """                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kgi">
                        <span class="insight-graph-daily__marker-cap-line">本日（売上）</span>
                        <span class="insight-graph-daily__marker-cap-value">¥123,456,789</span>
                      </p>
                      <div class="insight-daily-alloc-graph" id="insight-graph-annual-cumulative-target-actual">
                        <span class="insight-daily-alloc-marker-triangle" aria-hidden="true"></span>
                        <span class="insight-daily-alloc-marker-line" aria-hidden="true"></span>
                      </div>
                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kpi">
                        <span class="insight-graph-daily__marker-cap-line">本日の目標売上</span>
                        <span class="insight-graph-daily__marker-cap-value">¥100,456,789</span>
                      </p>"""

JA_ANNUAL_NEW = """                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kgi">
                        <span class="insight-graph-daily__marker-cap-line">累計実績</span>
                        <span class="insight-graph-daily__marker-cap-value">¥123,456,789</span>
                      </p>
                      <div class="insight-daily-alloc-graph" id="insight-graph-annual-cumulative-target-actual">
                        <span class="insight-daily-alloc-marker-triangle" aria-hidden="true"></span>
                        <span class="insight-daily-alloc-marker-line" aria-hidden="true"></span>
                      </div>
                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kpi">
                        <span class="insight-graph-daily__marker-cap-line">累計目標</span>
                        <span class="insight-graph-daily__marker-cap-value">¥100,456,789</span>
                      </p>"""

EN_MONTHLY_OLD = """                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kgi">
                        <span class="insight-graph-daily__marker-cap-line">Today (Sales)</span>
                        <span class="insight-graph-daily__marker-cap-value">$123,456,789</span>
                      </p>
                      <div class="insight-daily-alloc-graph" id="insight-graph-monthly-cumulative-target-actual">
                        <span class="insight-daily-alloc-marker-triangle" aria-hidden="true"></span>
                        <span class="insight-daily-alloc-marker-line" aria-hidden="true"></span>
                      </div>
                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kpi">
                        <span class="insight-graph-daily__marker-cap-line">Today's Target Sales</span>
                        <span class="insight-graph-daily__marker-cap-value">$100,456,789</span>
                      </p>"""

EN_MONTHLY_NEW = """                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kgi">
                        <span class="insight-graph-daily__marker-cap-line">Cumulative Actual</span>
                        <span class="insight-graph-daily__marker-cap-value">$123,456,789</span>
                      </p>
                      <div class="insight-daily-alloc-graph" id="insight-graph-monthly-cumulative-target-actual">
                        <span class="insight-daily-alloc-marker-triangle" aria-hidden="true"></span>
                        <span class="insight-daily-alloc-marker-line" aria-hidden="true"></span>
                      </div>
                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kpi">
                        <span class="insight-graph-daily__marker-cap-line">Cumulative Target</span>
                        <span class="insight-graph-daily__marker-cap-value">$100,456,789</span>
                      </p>"""

EN_ANNUAL_OLD = """                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kgi">
                        <span class="insight-graph-daily__marker-cap-line">Today (Sales)</span>
                        <span class="insight-graph-daily__marker-cap-value">$123,456,789</span>
                      </p>
                      <div class="insight-daily-alloc-graph" id="insight-graph-annual-cumulative-target-actual">
                        <span class="insight-daily-alloc-marker-triangle" aria-hidden="true"></span>
                        <span class="insight-daily-alloc-marker-line" aria-hidden="true"></span>
                      </div>
                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kpi">
                        <span class="insight-graph-daily__marker-cap-line">Today's Target Sales</span>
                        <span class="insight-graph-daily__marker-cap-value">$100,456,789</span>
                      </p>"""

EN_ANNUAL_NEW = """                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kgi">
                        <span class="insight-graph-daily__marker-cap-line">Cumulative Actual</span>
                        <span class="insight-graph-daily__marker-cap-value">$123,456,789</span>
                      </p>
                      <div class="insight-daily-alloc-graph" id="insight-graph-annual-cumulative-target-actual">
                        <span class="insight-daily-alloc-marker-triangle" aria-hidden="true"></span>
                        <span class="insight-daily-alloc-marker-line" aria-hidden="true"></span>
                      </div>
                      <p class="insight-graph-daily__marker-cap insight-graph-daily__marker-cap--kpi">
                        <span class="insight-graph-daily__marker-cap-line">Cumulative Target</span>
                        <span class="insight-graph-daily__marker-cap-value">$100,456,789</span>
                      </p>"""


def patch_pair(path: Path, monthly_old: str, monthly_new: str, annual_old: str, annual_new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if "insight-graph-monthly-cumulative-target-actual" in text and "累計実績" in text and "Cumulative Actual" not in monthly_new:
        # Already ja-patched: check labels next to monthly id
        pass
    changed = 0
    if monthly_old in text:
        text = text.replace(monthly_old, monthly_new, 1)
        changed += 1
    elif "id=\"insight-graph-monthly-cumulative-target-actual\"" in text:
        # idempotent check
        if "累計実績" in text[text.find("insight-graph-monthly-cumulative-target-actual") - 200 : text.find("insight-graph-monthly-cumulative-target-actual") + 200] or \
           "Cumulative Actual" in text[text.find("insight-graph-monthly-cumulative-target-actual") - 200 : text.find("insight-graph-monthly-cumulative-target-actual") + 200]:
            print(f"  monthly already ok")
        else:
            raise SystemExit(f"monthly block miss: {path}")
    else:
        raise SystemExit(f"monthly graph id miss: {path}")

    if annual_old in text:
        text = text.replace(annual_old, annual_new, 1)
        changed += 1
    elif "id=\"insight-graph-annual-cumulative-target-actual\"" in text:
        snippet = text[
            text.find("insight-graph-annual-cumulative-target-actual") - 200 : text.find(
                "insight-graph-annual-cumulative-target-actual"
            )
            + 200
        ]
        if "累計実績" in snippet or "Cumulative Actual" in snippet:
            print(f"  annual already ok")
        else:
            raise SystemExit(f"annual block miss: {path}")
    else:
        raise SystemExit(f"annual graph id miss: {path}")

    # Safety: Graph Daily labels must remain
    daily_ok = (
        ('id="insight-graph-daily-target-actual"' in text)
        and (
            ">本日（売上）<" in text
            or ">Today (Sales)<" in text
        )
    )
    if not daily_ok:
        raise SystemExit(f"Graph Daily labels unexpectedly changed: {path}")

    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({changed} blocks)")


def main() -> int:
    for path in JA_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_pair(path, JA_MONTHLY_OLD, JA_MONTHLY_NEW, JA_ANNUAL_OLD, JA_ANNUAL_NEW)
    for path in EN_PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_pair(path, EN_MONTHLY_OLD, EN_MONTHLY_NEW, EN_ANNUAL_OLD, EN_ANNUAL_NEW)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

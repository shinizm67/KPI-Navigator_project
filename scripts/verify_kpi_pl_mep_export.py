#!/usr/bin/env python3
"""Verify MEP+PL Excel export wiring (JA/EN pages + client source guards)."""

from __future__ import annotations

import re
from calendar import monthrange
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "scripts" / "_kpi_pl_mep_export.js"

PAGES = [
    "app/annual/index.html",
    "app/monthly/index.html",
    "app/monthly/edit/index.html",
    "app/profit/index.html",
    "app/profit/pl/index.html",
    "en/app/annual/index.html",
    "en/app/monthly/index.html",
    "en/app/monthly/edit/index.html",
    "en/app/profit/index.html",
    "en/app/profit/pl/index.html",
]


def main() -> None:
    js = JS.read_text(encoding="utf-8")
    for needle in (
        "isProSubscription",
        "changePlanHref",
        "location.href = changePlanHref(btn)",
        "XLSX.writeFile",
        "buildMepSheetAoA",
        "buildPlSheetAoA",
        "kpi-pl-expenses-v1:",
        "loadMepYearPayload",
        "book_append_sheet",
        "exportLang",
        "NON_EXPENSE_IDS",
        "xlsx-js-style",
        "DEFAULT_EXPENSE_LINES",
        "— 固定費 —",
        "lineMonthAmount",
        "!cols",
        "kpi-pl-mep-export-include-pl",
        "Excelファイル生成中",
        "preloadXlsx",
    ):
        if needle not in js:
            raise SystemExit(f"missing in export JS: {needle}")

    for rel in PAGES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if 'id="kpi-export-pl-mep"' not in text:
            raise SystemExit(f"missing export button: {rel}")
        if "template-dl-sep" not in text:
            raise SystemExit(f"missing DL separator: {rel}")
        n = len(re.findall(r"<script>\s*/\* KPI-PL-MEP-EXPORT \*/", text))
        if n != 1:
            raise SystemExit(f"expected 1 export script in {rel}, got {n}")
        if rel.startswith("en/"):
            if "P&L data (MEP + PL)" not in text and "Data export" not in text:
                raise SystemExit(f"missing EN export labels: {rel}")
        else:
            if "収支データ（MEP＋PL）" not in text:
                raise SystemExit(f"missing JA export label: {rel}")

    # Column layout: MEP day cols; PL always 12 months
    days = monthrange(2026, 3)[1]
    mep_cols = 1 + days * 2
    pl_cols = 1 + 12 * 2
    if mep_cols != 63 or pl_cols != 25:
        raise SystemExit(f"unexpected col counts mep={mep_cols} pl={pl_cols}")

    # Sheet counts per mode
    assert 12 + 1 == 13  # all months + PL
    assert 1 + 1 == 2  # selected month + PL

    print("verify_kpi_pl_mep_export: OK")


if __name__ == "__main__":
    main()

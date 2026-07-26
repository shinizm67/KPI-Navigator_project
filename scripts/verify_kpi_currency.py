#!/usr/bin/env python3
"""Verify kpi-currency.js is injected and primary money formatters prefer KpiCurrency."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    "app/annual/index.html",
    "app/monthly/index.html",
    "app/profit/pl/index.html",
    "app/monthly/edit/index.html",
    "en/app/annual/index.html",
    "en/app/monthly/index.html",
    "en/app/profit/pl/index.html",
    "en/app/monthly/edit/index.html",
]

# Hub pages: script inject only (no money formatters on the page itself)
HUB_PAGES = [
    "app/profit/index.html",
    "en/app/profit/index.html",
]


# Functions that must call KpiCurrency before any hardcoded ¥/$ branch.
REQUIRED_FNS = [
    "formatMoney",
    "fmtMoney",
    "formatTargetSalesValue",
    "formatAnalyzeMoney",
    "formatSignedSummaryAmount",
    "formatAxisMoney",
    "formatDetailMoney",
    "fmtTwMoney",
    "resolveDailySalesText",
]


def check_page(rel: str) -> list[str]:
    path = ROOT / rel
    errs: list[str] = []
    if not path.is_file():
        return [f"missing {rel}"]
    text = path.read_text(encoding="utf-8")
    if "js/kpi-currency.js" not in text:
        errs.append(f"{rel}: missing kpi-currency.js script")
    if "KpiCurrency" not in text:
        errs.append(f"{rel}: no KpiCurrency references")

    # Inverted pattern: JA hardcode before KpiCurrency on next line
    bad = re.findall(
        r"if \((?:isJa(?:\(\))?|useJa|langJa)\)[^\n]*return ['\"]¥[^\n]+\n\s*return window\.KpiCurrency",
        text,
    )
    if bad:
        errs.append(f"{rel}: inverted JA-first before KpiCurrency ({len(bad)})")

    for fn in REQUIRED_FNS:
        # find function bodies (non-greedy up to next function at same indent-ish)
        for m in re.finditer(
            rf"function {fn}\s*\([^)]*\)\s*\{{",
            text,
        ):
            start = m.end()
            # take next 500 chars as body sample
            body = text[start : start + 500]
            if "'¥'" in body or '"¥"' in body or "'$'" in body or "\\u00a5" in body:
                if "KpiCurrency" not in body:
                    errs.append(f"{rel}: {fn} uses ¥/$ without KpiCurrency nearby")
    return errs


def main() -> int:
    all_errs: list[str] = []
    for rel in PAGES:
        all_errs.extend(check_page(rel))
    for rel in HUB_PAGES:
        path = ROOT / rel
        if not path.is_file():
            all_errs.append(f"missing {rel}")
            continue
        if "js/kpi-currency.js" not in path.read_text(encoding="utf-8"):
            all_errs.append(f"{rel}: missing kpi-currency.js script")
    helper = ROOT / "js/kpi-currency.js"
    if not helper.is_file():
        all_errs.append("missing js/kpi-currency.js")
    else:
        js = helper.read_text(encoding="utf-8")
        for key in ("JPY", "USD", "EUR", "GBP", "TWD", "format", "symbol", "zero", "guessCode", "arrangeSelect"):
            if key not in js:
                all_errs.append(f"kpi-currency.js missing {key}")
        if "NT$" not in js:
            all_errs.append("kpi-currency.js missing NT$ symbol")

    if all_errs:
        print("FAIL")
        for e in all_errs:
            print(" -", e)
        return 1
    print("OK: kpi-currency wired on", len(PAGES), "pages +", len(HUB_PAGES), "hubs")
    return 0


if __name__ == "__main__":
    sys.exit(main())

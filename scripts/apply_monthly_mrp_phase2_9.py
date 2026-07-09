#!/usr/bin/env python3
"""MRP Phase 2.9 — Skip vertical TW scroll/render on arrow when focus bar collapsed (Monthly)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MARKER = "/* KPI-MRP-PHASE2-9 */"

VERTICAL_TW_SCROLL_OLD = """      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var iso = ev && ev.detail && ev.detail.isoDate;
        var source = ev && ev.detail && ev.detail.source;
        if (!iso) return;
        currentFocusIso = iso;
        if (source === 'focus-sync') return;

        // Year変更やテーブル再描画直後に飛んだ場合に備えて短いリトライを入れる"""

VERTICAL_TW_SCROLL_NEW = f"""      document.addEventListener('annual:dailyDateChanged', function (ev) {{
        var iso = ev && ev.detail && ev.detail.isoDate;
        var source = ev && ev.detail && ev.detail.source;
        if (!iso) return;
        currentFocusIso = iso;
        if (source === 'focus-sync') return;
        {MARKER}
        /* Monthly 横TW操作時: 縦TW未展開なら scroll/render をスキップ（INP 改善） */
        if (
          document.body.classList.contains('monthly-page') &&
          !document.body.classList.contains('annual-focus-bar-expanded')
        ) {{
          return;
        }}

        // Year変更やテーブル再描画直後に飛んだ場合に備えて短いリトライを入れる"""

MONTHLY_ARROW_SCROLL_OLD = """        if (source === 'initial-sync') return;
        var d = parseISODateLocal(iso);
        if (!d) return;
        if (!isDateWithinBounds(d)) return;
        var prevYear = state.year;
        var prevMonth0 = state.month0;
        setStateYearMonth(d.getFullYear(), d.getMonth());
        persistMonthlyLast();
        renderPickerMenu();"""

MONTHLY_ARROW_SCROLL_NEW = f"""        if (source === 'initial-sync') return;
        {MARKER}
        var d = parseISODateLocal(iso);
        if (!d) return;
        if (!isDateWithinBounds(d)) return;
        var prevYear = state.year;
        var prevMonth0 = state.month0;
        var sameMonthNav =
          prevYear === d.getFullYear() && prevMonth0 === d.getMonth();
        setStateYearMonth(d.getFullYear(), d.getMonth());
        if (!sameMonthNav) {{
          persistMonthlyLast();
          renderPickerMenu();
        }}"""


def apply_replacements(text: str) -> str:
    pairs = [
        (VERTICAL_TW_SCROLL_OLD, VERTICAL_TW_SCROLL_NEW),
        (MONTHLY_ARROW_SCROLL_OLD, MONTHLY_ARROW_SCROLL_NEW),
    ]
    for old, new in pairs:
        if old not in text:
            raise ValueError(f"anchor not found ({old[:72]}...)")
        text = text.replace(old, new, 1)
    return text


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"MISSING: {path}", file=sys.stderr)
            return 1
        original = path.read_text(encoding="utf-8")
        if MARKER in original:
            print(f"SKIP (already applied): {path}")
            continue
        updated = apply_replacements(original)
        path.write_text(updated, encoding="utf-8")
        print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

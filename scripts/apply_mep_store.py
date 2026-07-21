#!/usr/bin/env python3
"""Phase 4: MEP dailyExpenses / dailyMeta persistence via KpiYearStore."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from mep_store_client import KPI_MEP_STORE_MARKER, mep_store_client_js  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

MEP_TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

EDIT_GUARDS_END = "      })();\n      /* KPI-EDIT-GUARDS-END */"

INIT_EDIT_OLD = """      function initEditPage() {
        syncFromPage();
        undoStack = [];
        syncUndoButton();
        clearDirty();
        editSessionCommitted = false;
        buildGrid();"""

INIT_EDIT_NEW = """      function initEditPage() {
        syncFromPage();
        undoStack = [];
        syncUndoButton();
        clearDirty();
        editSessionCommitted = false;
        onMepYearContextChanged(mefYear);
        buildGrid();"""

APPLY_MONTH_OLD = """      function applyMonthSelection(month0) {
        mefYear = pickerYear;
        mefMonth0 = month0;"""

APPLY_MONTH_NEW = """      function applyMonthSelection(month0) {
        var prevYear = mefYear;
        mefYear = pickerYear;
        mefMonth0 = month0;
        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);"""

BTN_CONFIRM_OLD = """        btnConfirm.addEventListener('click', function () {
          syncMonthlySalesToAnnualStoreForMonth();
          document.dispatchEvent(new CustomEvent('annual:salesMapChanged', { detail: { year: mefYear, source: 'monthly-edit-float' } }));"""

BTN_CONFIRM_NEW = """        btnConfirm.addEventListener('click', function () {
          syncMonthlySalesToAnnualStoreForMonth();
          persistMepToYearStore(mefYear);
          document.dispatchEvent(new CustomEvent('annual:salesMapChanged', { detail: { year: mefYear, source: 'monthly-edit-float' } }));"""

BTN_PREV_OLD = """      btnPrev && btnPrev.addEventListener('click', function () {
        markDirty();
        mefMonth0 -= 1;
        if (mefMonth0 < 0) {
          mefMonth0 = 11;
          mefYear -= 1;
        }
        buildGrid();"""

BTN_PREV_NEW = """      btnPrev && btnPrev.addEventListener('click', function () {
        markDirty();
        var prevYear = mefYear;
        mefMonth0 -= 1;
        if (mefMonth0 < 0) {
          mefMonth0 = 11;
          mefYear -= 1;
        }
        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        buildGrid();"""

BTN_NEXT_OLD = """      btnNext && btnNext.addEventListener('click', function () {
        markDirty();
        mefMonth0 += 1;
        if (mefMonth0 > 11) {
          mefMonth0 = 0;
          mefYear += 1;
        }
        buildGrid();"""

BTN_NEXT_NEW = """      btnNext && btnNext.addEventListener('click', function () {
        markDirty();
        var prevYear = mefYear;
        mefMonth0 += 1;
        if (mefMonth0 > 11) {
          mefMonth0 = 0;
          mefYear += 1;
        }
        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        buildGrid();"""

JUMP_TODAY_OLD = """      function jumpToToday() {
        var now = new Date();
        mefYear = now.getFullYear();
        mefMonth0 = now.getMonth();
        buildGrid();"""

JUMP_TODAY_NEW = """      function jumpToToday() {
        var now = new Date();
        var prevYear = mefYear;
        mefYear = now.getFullYear();
        mefMonth0 = now.getMonth();
        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        buildGrid();"""

PERSIST_BIZDAY_OLD = """        } else if (!Number.isFinite(cur) || cur <= 0) {
          daily.targetSalesByDate[iso] = 1234;
        }"""

PERSIST_BIZDAY_NEW = """        } else if (!Number.isFinite(cur) || cur <= 0) {
          delete daily.targetSalesByDate[iso];
        }"""

BUILD_GRID_OLD = """      function buildGrid() {
        ensureDefaultsForMonth();"""

BUILD_GRID_NEW = """      function buildGrid() {
        flushPendingMemoEditsFromDom();
        ensureDefaultsForMonth();"""


def inject_mep_store_block(text: str) -> str:
    """Replace or insert the canonical MEP-STORE block.

    Region = from KPI-MEP-STORE marker through just before `var useJa` /
    strategy-note modal. Any `refreshMepSalesFromStore` inside that region is
    preserved and re-appended after the canonical store block (so re-apply is
    idempotent and does not duplicate store functions).
    """
    block = mep_store_client_js().rstrip() + "\n"
    refresh_pat = re.compile(
        r"      function refreshMepSalesFromStore\([^)]*\) \{[\s\S]*?"
        r"document\.addEventListener\('annual:salesDataSaved', refreshMepSalesFromStore\);\n"
    )

    if KPI_MEP_STORE_MARKER in text:
        start = text.find(KPI_MEP_STORE_MARKER)
        line_start = text.rfind("\n", 0, start) + 1
        end_candidates = []
        for needle in (
            "\n      var useJa = ",
            "\n            /* MEP-STRATEGY-NOTE-MODAL */",
            "\n      /* MEP-STRATEGY-NOTE-MODAL */",
            "\n      /* MEP-STRATEGY-USER-NOTE */",
        ):
            i = text.find(needle, start)
            if i >= 0:
                end_candidates.append(i)
        if not end_candidates:
            raise ValueError("end anchor after KPI-MEP-STORE not found")
        region_end = min(end_candidates)
        region = text[line_start:region_end]
        refresh_m = refresh_pat.search(region)
        refresh = refresh_m.group(0) if refresh_m else ""
        return text[:line_start] + block + refresh + text[region_end:]

    anchor = "      /* KPI-EDIT-GUARDS */"
    if anchor not in text:
        raise ValueError("KPI-EDIT-GUARDS anchor not found")
    # Insert after the edit-guards IIFE closes (before next top-level statement).
    guards_close = text.find("      })();\n", text.find(anchor))
    if guards_close < 0:
        raise ValueError("KPI-EDIT-GUARDS IIFE end not found")
    insert_at = guards_close + len("      })();\n")
    return text[:insert_at] + block + text[insert_at:]


def apply_replacements(text: str) -> str:
    for old, new in [
        (INIT_EDIT_OLD, INIT_EDIT_NEW),
        (APPLY_MONTH_OLD, APPLY_MONTH_NEW),
        (BTN_CONFIRM_OLD, BTN_CONFIRM_NEW),
        (BTN_PREV_OLD, BTN_PREV_NEW),
        (BTN_NEXT_OLD, BTN_NEXT_NEW),
        (JUMP_TODAY_OLD, JUMP_TODAY_NEW),
        (PERSIST_BIZDAY_OLD, PERSIST_BIZDAY_NEW),
        (BUILD_GRID_OLD, BUILD_GRID_NEW),
    ]:
        if old not in text:
            # Already applied (new form present) or unrelated drift — skip quietly.
            if new in text or new.split("\n")[0] in text:
                continue
            # Soft-skip: pages already evolved past Phase 4 one-time anchors.
            continue
        text = text.replace(old, new, 1)
    return text


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_mep_store_block(text)
    text = apply_replacements(text)
    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> int:
    for target in MEP_TARGETS:
        if not target.is_file():
            print(f"missing: {target}", file=sys.stderr)
            return 1
        patch_file(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

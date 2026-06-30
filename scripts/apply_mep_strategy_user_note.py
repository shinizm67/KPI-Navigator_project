#!/usr/bin/env python3
"""Inject Strategy User Note input (Phase 6b) into MEP edit pages.

Disabled: inline MEP textarea broke grid layout and caused edit-lease refresh loops.
Insight read path remains; re-enable only with a non-intrusive UI (modal / collapse).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "scripts" / "_mep_strategy_user_note.css").read_text(encoding="utf-8")
JS = (ROOT / "scripts" / "_mep_strategy_user_note.js").read_text(encoding="utf-8")
HTML_JA = (ROOT / "scripts" / "_mep_strategy_user_note.html.ja").read_text(encoding="utf-8")
HTML_EN = (ROOT / "scripts" / "_mep_strategy_user_note.html.en").read_text(encoding="utf-8")

CSS_MARKER = "/* MEP-STRATEGY-USER-NOTE-CSS */"
JS_MARKER = "/* MEP-STRATEGY-USER-NOTE */"
HTML_MARKER = 'class="monthly-edit-float__strategy-note"'

TARGETS = [
    (ROOT / "app/monthly/edit/index.html", HTML_JA),
    (ROOT / "en/app/monthly/edit/index.html", HTML_EN),
]

MERGE_OLD = """        if (payload.mepMemoRows && payload.mepMemoRows.length) {
          restoreMemoRowsFromSnapshot(payload.mepMemoRows);
        }
        syncWeeklyMemoItems();
      }"""

MERGE_NEW = """        if (payload.mepMemoRows && payload.mepMemoRows.length) {
          restoreMemoRowsFromSnapshot(payload.mepMemoRows);
        }
        syncWeeklyMemoItems();
        mergeStrategyNotesFromPayload(payload);
      }"""

PAYLOAD_OLD = """        return {
          dailyExpenses: dailyExpenses,
          dailyMeta: { memos: memos, weather: weather, flags: flags },
          mepMemoRows: rowSnapshot(state.memoItems),
        };
      }"""

PAYLOAD_NEW = """        return {
          dailyExpenses: dailyExpenses,
          dailyMeta: { memos: memos, weather: weather, flags: flags },
          mepMemoRows: rowSnapshot(state.memoItems),
          monthlyStrategyUserNotes: strategyNotesForPersist(),
        };
      }"""

SNAPSHOT_BUILD_OLD = """          memoValueById: sortedNestedMap(memoValueById),
          weatherByIso: sortedIsoMap(weatherByIso)
        });
      }"""

SNAPSHOT_BUILD_NEW = """          memoValueById: sortedNestedMap(memoValueById),
          weatherByIso: sortedIsoMap(weatherByIso),
          strategyUserNotesByMonth: JSON.parse(JSON.stringify(strategyUserNotesByMonth))
        });
      }"""

SNAPSHOT_RESTORE_OLD = """        if (snap.memoItems) restoreMemoRowsFromSnapshot(snap.memoItems);
        clearDirty();
        undoStack = [];
        syncUndoButton();
        syncMonthlySalesToAnnualStoreForYear(mefYear);
        buildGrid();
      }"""

SNAPSHOT_RESTORE_NEW = """        if (snap.memoItems) restoreMemoRowsFromSnapshot(snap.memoItems);
        if (snap.strategyUserNotesByMonth) {
          strategyUserNotesByMonth = JSON.parse(JSON.stringify(snap.strategyUserNotesByMonth));
        }
        loadStrategyNoteFromCache();
        clearDirty();
        undoStack = [];
        syncUndoButton();
        syncMonthlySalesToAnnualStoreForYear(mefYear);
        buildGrid();
      }"""

APPLY_MONTH_OLD = """      function applyMonthSelection(month0) {
        var prevYear = mefYear;
        mefYear = pickerYear;
        mefMonth0 = month0;
        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        closeMonthPicker();
        buildGrid();"""

APPLY_MONTH_NEW = """      function applyMonthSelection(month0) {
        flushStrategyNoteToCache();
        var prevYear = mefYear;
        mefYear = pickerYear;
        mefMonth0 = month0;
        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        closeMonthPicker();
        buildGrid();"""

INIT_OLD = """        onMepYearContextChanged(mefYear);
        if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
          window.__KPI_SALES_INPUT_PATH_UI.sync();
        }"""

INIT_NEW = """        onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        if (window.__KPI_SALES_INPUT_PATH_UI && typeof window.__KPI_SALES_INPUT_PATH_UI.sync === 'function') {
          window.__KPI_SALES_INPUT_PATH_UI.sync();
        }"""

JUMP_TODAY_OLD = """      function jumpToToday() {
        var now = new Date();
        var prevYear = mefYear;
        mefYear = now.getFullYear();
        mefMonth0 = now.getMonth();
        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        buildGrid();"""

JUMP_TODAY_NEW = """      function jumpToToday() {
        flushStrategyNoteToCache();
        var now = new Date();
        var prevYear = mefYear;
        mefYear = now.getFullYear();
        mefMonth0 = now.getMonth();
        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        buildGrid();"""

BTN_PREV_OLD = """      btnPrev && btnPrev.addEventListener('click', function () {
        markDirty();
        var prevYear = mefYear;
        mefMonth0 -= 1;"""

BTN_PREV_NEW = """      btnPrev && btnPrev.addEventListener('click', function () {
        markDirty();
        flushStrategyNoteToCache();
        var prevYear = mefYear;
        mefMonth0 -= 1;"""

BTN_PREV_AFTER_OLD = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        buildGrid();
        persistMefMonth();
      });
      btnNext && btnNext.addEventListener('click', function () {
        markDirty();
        var prevYear = mefYear;
        mefMonth0 += 1;"""

BTN_PREV_AFTER_NEW = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        buildGrid();
        persistMefMonth();
      });
      btnNext && btnNext.addEventListener('click', function () {
        markDirty();
        flushStrategyNoteToCache();
        var prevYear = mefYear;
        mefMonth0 += 1;"""

BTN_NEXT_AFTER_OLD = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        buildGrid();
        persistMefMonth();
      });
      btnToday && btnToday.addEventListener('click', function () {"""

BTN_NEXT_AFTER_NEW = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        buildGrid();
        persistMefMonth();
      });
      btnToday && btnToday.addEventListener('click', function () {"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n", 1)[0].strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def inject_css(text: str) -> str:
    if CSS_MARKER in text:
        return text
    anchor = "  </style>"
    pos = text.find(anchor)
    if pos < 0:
        raise SystemExit("style end not found")
    block = f"\n    {CSS_MARKER}\n{CSS.rstrip()}\n"
    return text[:pos] + block + text[pos:]


def inject_html(text: str, html: str) -> str:
    if HTML_MARKER in text:
        return text
    anchor = (
        "      </div>\n    </div>\n  </div>\n\n\n\n  <div\n    class=\"memo-float-modal\""
    )
    if anchor not in text:
        raise SystemExit("MEP body/html anchor not found")
    strategy_block = html.rstrip() + "\n"
    return text.replace(
        anchor,
        "      </div>\n    </div>\n" + strategy_block + "  </div>\n\n\n\n  <div\n    class=\"memo-float-modal\"",
        1,
    )


def inject_js(text: str) -> str:
    if JS_MARKER in text:
        return text
    anchor = "      var mefYear = new Date().getFullYear();"
    if anchor not in text:
        raise SystemExit("mefYear anchor not found")
    return text.replace(anchor, JS.rstrip() + "\n\n      " + anchor, 1)


def patch_file(path: Path, html: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_css(text)
    text = inject_html(text, html)
    text = inject_js(text)
    text = replace_once(text, MERGE_OLD, MERGE_NEW, "mergeMepYearPayload")
    text = replace_once(text, PAYLOAD_OLD, PAYLOAD_NEW, "buildMepPersistPayload")
    text = replace_once(text, SNAPSHOT_BUILD_OLD, SNAPSHOT_BUILD_NEW, "buildConfirmedSnapshot")
    text = replace_once(text, SNAPSHOT_RESTORE_OLD, SNAPSHOT_RESTORE_NEW, "restoreConfirmedSnapshot")
    text = replace_once(text, APPLY_MONTH_OLD, APPLY_MONTH_NEW, "applyMonthSelection")
    text = replace_once(text, INIT_OLD, INIT_NEW, "initEditPage")
    text = replace_once(text, JUMP_TODAY_OLD, JUMP_TODAY_NEW, "jumpToToday")
    text = replace_once(text, BTN_PREV_OLD, BTN_PREV_NEW, "btnPrev")
    text = replace_once(text, BTN_PREV_AFTER_OLD, BTN_PREV_AFTER_NEW, "btnPrevAfter")
    text = replace_once(text, BTN_NEXT_AFTER_OLD, BTN_NEXT_AFTER_NEW, "btnNextAfter")
    path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def main() -> None:
    print(
        "skip: MEP Strategy Note UI disabled (use apply_mep_revert_strategy_ui.py to restore grid)",
        file=sys.stderr,
    )
    sys.exit(0)
    for path, html in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path, html)


if __name__ == "__main__":
    main()

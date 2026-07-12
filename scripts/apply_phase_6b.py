#!/usr/bin/env python3
"""Phase 6b: Weekly Insight + Strategy User Note (modal) into Insight / MEP pages."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent

CSS = (SCRIPTS / "_mep_strategy_note_modal.css").read_text(encoding="utf-8")
JS = (SCRIPTS / "_mep_strategy_note_modal.js").read_text(encoding="utf-8")
HTML_JA = (SCRIPTS / "_mep_strategy_note_modal.html.ja").read_text(encoding="utf-8")
HTML_EN = (SCRIPTS / "_mep_strategy_note_modal.html.en").read_text(encoding="utf-8")

CSS_MARKER = "/* MEP-STRATEGY-NOTE-MODAL-CSS */"
JS_MARKER = "/* MEP-STRATEGY-NOTE-MODAL */"
HTML_MARKER = 'id="strategy-note-modal"'

MEP_TARGETS = [
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

TOOLBAR_JA_OLD = """        <div class="monthly-edit-float__tool-actions">
        <button type="button" class="monthly-edit-float__pl-btn monthly-edit-float__memo-btn" id="monthly-edit-float-memo" aria-label="日次メモを開く" title="日次メモを開く">
          日次メモ
        </button>
        <button type="button" class="monthly-edit-float__pl-btn monthly-edit-float__strategy-note-btn" id="monthly-edit-float-strategy-note" aria-label="Strategy Note を開く" title="Strategy Note を開く">
          Strategy Note
        </button>
        </div>"""

TOOLBAR_JA_NEW = TOOLBAR_JA_OLD

TOOLBAR_EN_OLD = """        <div class="monthly-edit-float__tool-actions">
        <button type="button" class="monthly-edit-float__pl-btn monthly-edit-float__memo-btn" id="monthly-edit-float-memo" aria-label="Open daily notes" title="Open daily notes">
          Daily Notes
        </button>
        <button type="button" class="monthly-edit-float__pl-btn monthly-edit-float__strategy-note-btn" id="monthly-edit-float-strategy-note" aria-label="Open Strategy Note" title="Open Strategy Note">
          Strategy Note
        </button>
        </div>"""

TOOLBAR_EN_NEW = TOOLBAR_EN_OLD


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
        "  <div\n    class=\"sales-data-modal__close-chooser\"\n    id=\"kpi-path-change-chooser\""
    )
    if anchor not in text:
        raise SystemExit("MEP html anchor not found")
    return text.replace(anchor, html.rstrip() + "\n\n\n  " + anchor, 1)


def inject_js(text: str) -> str:
    if JS_MARKER in text:
        return text
    anchor = "      var mefYear = new Date().getFullYear();"
    if anchor not in text:
        raise SystemExit("mefYear anchor not found")
    return text.replace(anchor, JS.rstrip() + "\n\n      " + anchor, 1)


def inject_toolbar(text: str, is_en: bool) -> str:
    if 'id="monthly-edit-float-strategy-note"' in text:
        return text
    old = TOOLBAR_EN_OLD if is_en else TOOLBAR_JA_OLD
    new = TOOLBAR_EN_NEW if is_en else TOOLBAR_JA_NEW
    if old not in text:
        raise SystemExit("toolbar anchor not found")
    return text.replace(old, new, 1)


def patch_mep(path: Path, html: str, is_en: bool) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_css(text)
    text = inject_html(text, html)
    text = inject_toolbar(text, is_en)
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
    print(f"patched MEP: {path.relative_to(ROOT)}")


def run_script(name: str) -> None:
    path = SCRIPTS / name
    if not path.is_file():
        raise SystemExit(f"missing script: {path}")
    subprocess.run([sys.executable, str(path)], check=True, cwd=str(ROOT))


def main() -> int:
    run_script("apply_insight_weekly_memo.py")
    run_script("apply_insight_strategy_user_note.py")
    for path, html in MEP_TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_mep(path, html, "en/" in str(path))
    print("Phase 6b apply complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

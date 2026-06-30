#!/usr/bin/env python3
"""Remove Strategy Note UI from MEP and restore pre-6b layout hooks."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARDS = (ROOT / "scripts" / "_mep_edit_guards_refresh.js").read_text(encoding="utf-8")

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

STRATEGY_CSS_RE = re.compile(
    r"\n    /\* MEP-STRATEGY-USER-NOTE-CSS \*/\n.*?"
    r"    body\.office-mode \.monthly-edit-float__strategy-note-input \{\n"
    r"      background: #fff;\n"
    r"      border-color: rgba\(0, 0, 0, 0\.2\);\n"
    r"    \}\n",
    re.DOTALL,
)

STRATEGY_HTML_RE = re.compile(
    r"\n    <section class=\"monthly-edit-float__strategy-note\"[\s\S]*?</section>\n",
    re.MULTILINE,
)

STRATEGY_JS_RE = re.compile(
    r"\n      /\* MEP-STRATEGY-USER-NOTE \*/[\s\S]*?"
    r"      if \(strategyNoteInput\) \{[\s\S]*?\n      \}\n",
    re.MULTILINE,
)

BODY_CSS_OLD = """    .monthly-edit-float__body {
      flex: 1 1 auto;
      height: 0;
      min-height: 0;
      display: grid;
      grid-template-columns: var(--mef-label-w) 1fr;
      grid-template-rows: minmax(0, 1fr);
      overflow: hidden;
      box-sizing: border-box;
    }"""

BODY_CSS_NEW = """    .monthly-edit-float__body {
      flex: 1 1 0;
      height: 0;
      min-height: 160px;
      display: grid;
      grid-template-columns: var(--mef-label-w) 1fr;
      grid-template-rows: minmax(0, 1fr);
      overflow: hidden;
      box-sizing: border-box;
    }"""

MERGE_NEW = """        syncWeeklyMemoItems();
        mergeStrategyNotesFromPayload(payload);
      }"""

MERGE_OLD = """        syncWeeklyMemoItems();
      }"""

PAYLOAD_NEW = """          mepMemoRows: rowSnapshot(state.memoItems),
          monthlyStrategyUserNotes: strategyNotesForPersist(),
        };"""

PAYLOAD_OLD = """          mepMemoRows: rowSnapshot(state.memoItems),
        };"""

SNAPSHOT_BUILD_NEW = """          weatherByIso: sortedIsoMap(weatherByIso),
          strategyUserNotesByMonth: JSON.parse(JSON.stringify(strategyUserNotesByMonth))
        });"""

SNAPSHOT_BUILD_OLD = """          weatherByIso: sortedIsoMap(weatherByIso)
        });"""

SNAPSHOT_BUILD_FUNC_NEW = """      function buildConfirmedSnapshot() {
        flushStrategyNoteToCache();
        return JSON.stringify({"""

SNAPSHOT_BUILD_FUNC_OLD = """      function buildConfirmedSnapshot() {
        return JSON.stringify({"""

SNAPSHOT_RESTORE_EXTRA = """        if (snap.strategyUserNotesByMonth) {
          strategyUserNotesByMonth = JSON.parse(JSON.stringify(snap.strategyUserNotesByMonth));
        }
        loadStrategyNoteFromCache();
"""

INIT_NEW = """        onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        if (window.__KPI_SALES_INPUT_PATH_UI"""

INIT_OLD = """        onMepYearContextChanged(mefYear);
        if (window.__KPI_SALES_INPUT_PATH_UI"""

INIT_SCROLL_NEW = """        if (mefPreferredIso) {
          scrollToIsoColumn(mefPreferredIso);
          pushMepSelectedDateToStore(mefPreferredIso);
        } else {
          scrollToPreferredDayLeft();
        }"""

INIT_SCROLL_OLD = """        if (mefPreferredIso) scrollToIsoColumn(mefPreferredIso);
        else scrollToPreferredDayLeft();"""

APPLY_MONTH_FLUSH = """        flushStrategyNoteToCache();
        var prevYear = mefYear;"""

APPLY_MONTH_LOAD = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        closeMonthPicker();"""

APPLY_MONTH_MIDDLE = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        closeMonthPicker();"""

BTN_PREV_FLUSH = """          markDirty();
          flushStrategyNoteToCache();
          var prevYear = mefYear;"""

BTN_PREV_OLD = """          markDirty();
          var prevYear = mefYear;"""

BTN_AFTER_LOAD = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        buildGrid();
        persistMefMonth();
      });
      btnNext && btnNext.addEventListener('click', function () {
        markDirty();
        flushStrategyNoteToCache();
        var prevYear = mefYear;"""

BTN_AFTER_OLD = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        buildGrid();
        persistMefMonth();
      });
      btnNext && btnNext.addEventListener('click', function () {
        markDirty();
        var prevYear = mefYear;"""

JUMP_TODAY_NEW = """      function jumpToToday() {
        flushStrategyNoteToCache();
        var now = new Date();"""

JUMP_TODAY_OLD = """      function jumpToToday() {
        var now = new Date();"""

JUMP_LOAD = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        loadStrategyNoteFromCache();
        buildGrid();"""

JUMP_MIDDLE = """        if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
        buildGrid();"""

GUARDS_RE = re.compile(
    r"\n\s*/\* KPI-EDIT-GUARDS \*/\n\s*\(function \(\) \{[\s\S]*?\n\s*\}\)\(\);\n",
    re.MULTILINE,
)


def replace_optional(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    return text


def patch_guards(text: str) -> str:
    if not GUARDS_RE.search(text):
        raise SystemExit("KPI-EDIT-GUARDS not found")
    return GUARDS_RE.sub("\n" + GUARDS.rstrip() + "\n", text, count=1)


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(BODY_CSS_NEW, BODY_CSS_OLD, 1)
    text = replace_optional(text, MERGE_NEW, MERGE_OLD)
    text = text.replace("        mergeStrategyNotesFromPayload(payload);\n", "")
    text = replace_optional(text, PAYLOAD_NEW, PAYLOAD_OLD)
    text = replace_optional(text, SNAPSHOT_BUILD_NEW, SNAPSHOT_BUILD_OLD)
    text = replace_optional(text, SNAPSHOT_BUILD_FUNC_NEW, SNAPSHOT_BUILD_FUNC_OLD)
    if SNAPSHOT_RESTORE_EXTRA in text:
        text = text.replace(
            "        if (snap.memoItems) restoreMemoRowsFromSnapshot(snap.memoItems);\n"
            + SNAPSHOT_RESTORE_EXTRA,
            "        if (snap.memoItems) restoreMemoRowsFromSnapshot(snap.memoItems);\n",
            1,
        )
    text = replace_optional(text, INIT_NEW, INIT_OLD)
    text = replace_optional(text, INIT_SCROLL_NEW, INIT_SCROLL_OLD)
    text = replace_optional(text, APPLY_MONTH_FLUSH, "        var prevYear = mefYear;")
    text = replace_optional(text, APPLY_MONTH_LOAD, APPLY_MONTH_MIDDLE)
    text = replace_optional(text, BTN_PREV_FLUSH, BTN_PREV_OLD)
    text = replace_optional(text, BTN_AFTER_LOAD, BTN_AFTER_OLD)
    text = replace_optional(text, JUMP_TODAY_NEW, JUMP_TODAY_OLD)
    text = replace_optional(text, JUMP_LOAD, JUMP_MIDDLE)
    text = text.replace("        flushStrategyNoteToCache();\n", "")
    text = text.replace("        loadStrategyNoteFromCache();\n", "")
    text = patch_guards(text)
    text = STRATEGY_CSS_RE.sub("\n", text, count=1)
    text = STRATEGY_HTML_RE.sub("\n", text, count=1)
    text = STRATEGY_JS_RE.sub("\n", text, count=1)
    if "monthly-edit-strategy-user-note" in text or "monthly-edit-float__strategy-note" in text:
        raise SystemExit(f"strategy UI remnants in {path}")
    if "editLeaseChanged', refreshMepSalesGuards" in text:
        raise SystemExit(f"edit guards loop still present in {path}")
    path.write_text(text, encoding="utf-8")
    print(f"reverted: {path}")


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path)


if __name__ == "__main__":
    main()

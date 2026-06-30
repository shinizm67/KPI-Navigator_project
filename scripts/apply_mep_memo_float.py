#!/usr/bin/env python3
"""Inject Memo Floating Window HTML/CSS/JS into MEP edit pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "scripts" / "_mep_memo_float.css").read_text(encoding="utf-8")
JS = (ROOT / "scripts" / "_mep_memo_float.js").read_text(encoding="utf-8")
WEEKLY_ROWS_JS = (ROOT / "scripts" / "_mep_weekly_memo_rows.js").read_text(encoding="utf-8")

WEEKLY_ROWS_MARKER = "/* MEP-WEEKLY-MEMO-ROWS */"
CREATE_INITIAL_NEW = """        syncWeeklyMemoItems();"""
CREATE_INITIAL_OLD_VARIANTS = [
    """        syncSectionFromCatalog(state.variableItems, catalogVariableDefs());
        if (state.memoItems.length === 0)
          state.memoItems.push(makeRow('memo', 'メモ1', 'Memo 1', { editableLabel: true, deletable: true }));""",
    """        syncSectionFromCatalog(state.variableItems, catalogVariableDefs());
        maybeUpgradeLegacyMemoItems();
        ensureWeeklyMemoItems();""",
]
MERGE_MEP_NEW = """        if (payload.mepMemoRows && payload.mepMemoRows.length) {
          restoreMemoRowsFromSnapshot(payload.mepMemoRows);
        }
        syncWeeklyMemoItems();
      }"""
MERGE_MEP_OLD_VARIANTS = [
    """        if (payload.mepMemoRows && payload.mepMemoRows.length) {
          restoreMemoRowsFromSnapshot(payload.mepMemoRows);
        }
      }""",
    """        if (payload.mepMemoRows && payload.mepMemoRows.length) {
          restoreMemoRowsFromSnapshot(payload.mepMemoRows);
        }
        maybeUpgradeLegacyMemoItems();
        ensureWeeklyMemoItems();
      }""",
]
CURRENT_ROWS_OLD = """        rows.push({ type: 'group', id: 'g-memo', labelJa: 'MEMO', labelEn: 'MEMO' });
        rows.push({
          type: 'aggregate',
          id: 'memoHead',
          labelJa: 'メモ',
          labelEn: 'Memo',
          section: 'memo'
        });
        return rows;"""
CURRENT_ROWS_NEW = """        rows.push({ type: 'group', id: 'g-memo', labelJa: '日次メモ', labelEn: 'Daily Notes' });
        rows.push({
          type: 'aggregate',
          id: 'memoHead',
          labelJa: '日次メモ',
          labelEn: 'Daily Notes',
          section: 'memo',
          plusminus: 'memo'
        });
        if (!state.collapsed.memo) {
          syncWeeklyMemoItems();
          state.memoItems.forEach(function (r) {
            rows.push({ type: 'memoRow', row: r, section: 'memo' });
          });
        }
        return rows;"""
CREATE_INITIAL_ANCHOR = "      function createInitialRowsIfNeeded() {"

OLD_OPEN_MEMO = """      function openMemoForIso(iso, allowNonBizDay) {
        if (!iso) return;
        if (!allowNonBizDay && !bizDayByIso[iso]) return;
        document.dispatchEvent(
          new CustomEvent('mep:memoOpenRequested', {
            detail: { year: mefYear, month0: mefMonth0, iso: iso }
          })
        );
      }
"""

HTML_JA = """
  <div
    class="memo-float-modal"
    id="memo-float-modal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="memo-float-title"
    hidden
  >
    <div class="memo-float-modal__backdrop" id="memo-float-backdrop" aria-hidden="true"></div>
    <div class="memo-float-modal__panel">
      <button type="button" class="memo-float-modal__close" id="memo-float-close" aria-label="閉じる">×</button>
      <div class="memo-float-modal__toolbar">
        <button type="button" class="memo-float-modal__undo" id="memo-float-undo" disabled>UNDO</button>
        <button type="button" class="memo-float-modal__save" id="memo-float-save">Save</button>
      </div>
      <h2 class="memo-float-modal__title" id="memo-float-title">日次メモ</h2>
      <div class="memo-float-modal__month-nav">
        <button type="button" id="memo-float-prev-month">先月</button>
        <span class="memo-float-modal__month-label" id="memo-float-month-label"></span>
        <button type="button" id="memo-float-next-month">翌月</button>
        <button type="button" id="memo-float-today">Today</button>
      </div>
      <div class="memo-float-modal__date-scroll">
        <div class="memo-float-modal__date-rail" id="memo-float-date-rail"></div>
      </div>
      <div class="memo-float-modal__body-scroll">
        <div id="memo-float-day-panel"></div>
      </div>
    </div>
  </div>

  <div
    class="sales-data-modal__close-chooser memo-float-modal__close-chooser"
    id="memo-float-close-chooser"
    role="dialog"
    aria-modal="true"
    aria-labelledby="memo-float-close-chooser-title"
    hidden
  >
    <div class="sales-data-modal__close-chooser-scrim" id="memo-float-close-chooser-scrim" aria-hidden="true"></div>
    <div class="sales-data-modal__close-chooser-panel">
      <p id="memo-float-close-chooser-title" class="sales-data-modal__close-chooser-title">日次メモを閉じます</p>
      <p class="sales-data-modal__close-chooser-msg">保存するか、保存せずに閉じるかを選んでください。</p>
      <div class="sales-data-modal__close-chooser-actions">
        <button type="button" class="sales-data-modal__close-chooser-btn sales-data-modal__close-chooser-btn--save" id="memo-float-close-save">
          保存して閉じる
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="memo-float-close-discard">
          保存せずに閉じる
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="memo-float-close-cancel">
          キャンセル
        </button>
      </div>
    </div>
  </div>

"""

HTML_EN = """
  <div
    class="memo-float-modal"
    id="memo-float-modal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="memo-float-title"
    hidden
  >
    <div class="memo-float-modal__backdrop" id="memo-float-backdrop" aria-hidden="true"></div>
    <div class="memo-float-modal__panel">
      <button type="button" class="memo-float-modal__close" id="memo-float-close" aria-label="Close">×</button>
      <div class="memo-float-modal__toolbar">
        <button type="button" class="memo-float-modal__undo" id="memo-float-undo" disabled>UNDO</button>
        <button type="button" class="memo-float-modal__save" id="memo-float-save">Save</button>
      </div>
      <h2 class="memo-float-modal__title" id="memo-float-title">Daily Notes</h2>
      <div class="memo-float-modal__month-nav">
        <button type="button" id="memo-float-prev-month">Prev</button>
        <span class="memo-float-modal__month-label" id="memo-float-month-label"></span>
        <button type="button" id="memo-float-next-month">Next</button>
        <button type="button" id="memo-float-today">Today</button>
      </div>
      <div class="memo-float-modal__date-scroll">
        <div class="memo-float-modal__date-rail" id="memo-float-date-rail"></div>
      </div>
      <div class="memo-float-modal__body-scroll">
        <div id="memo-float-day-panel"></div>
      </div>
    </div>
  </div>

  <div
    class="sales-data-modal__close-chooser memo-float-modal__close-chooser"
    id="memo-float-close-chooser"
    role="dialog"
    aria-modal="true"
    aria-labelledby="memo-float-close-chooser-title"
    hidden
  >
    <div class="sales-data-modal__close-chooser-scrim" id="memo-float-close-chooser-scrim" aria-hidden="true"></div>
    <div class="sales-data-modal__close-chooser-panel">
      <p id="memo-float-close-chooser-title" class="sales-data-modal__close-chooser-title">Close daily notes</p>
      <p class="sales-data-modal__close-chooser-msg">Choose whether to save or discard your changes.</p>
      <div class="sales-data-modal__close-chooser-actions">
        <button type="button" class="sales-data-modal__close-chooser-btn sales-data-modal__close-chooser-btn--save" id="memo-float-close-save">
          Save and close
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="memo-float-close-discard">
          Close without saving
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="memo-float-close-cancel">
          Cancel
        </button>
      </div>
    </div>
  </div>

"""

MARKER_CSS = "    body.office-mode .monthly-edit-float__memo-flag-btn {\n      color: #5a5a5a;\n    }\n\n  </style>"
MARKER_CSS_REPLACEMENT = (
    "    body.office-mode .monthly-edit-float__memo-flag-btn {\n"
    "      color: #5a5a5a;\n"
    "    }\n\n"
    + CSS.rstrip()
    + "\n\n  </style>"
)

MARKER_HTML = '  <div\n    class="sales-data-modal__close-chooser"\n    id="sales-data-close-chooser"'
MARKER_JS = "      initEditPage();"
MARKER_JS_REPLACEMENT = JS.rstrip() + "\n\n      initEditPage();"


def patch_file(path: Path, html_snippet: str) -> None:
    text = path.read_text(encoding="utf-8")
    if "id=\"memo-float-modal\"" in text:
        print(f"skip (already patched): {path}")
        return

    if MARKER_CSS not in text:
        raise SystemExit(f"CSS marker not found in {path}")
    text = text.replace(MARKER_CSS, MARKER_CSS_REPLACEMENT, 1)

    if MARKER_HTML not in text:
        raise SystemExit(f"HTML marker not found in {path}")
    text = text.replace(MARKER_HTML, html_snippet + MARKER_HTML, 1)

    if OLD_OPEN_MEMO not in text:
        raise SystemExit(f"openMemoForIso block not found in {path}")
    text = text.replace(OLD_OPEN_MEMO, "", 1)

    if MARKER_JS not in text:
        raise SystemExit(f"initEditPage marker not found in {path}")
    if "var memoFloatRoot = document.getElementById('memo-float-modal');" in text:
        raise SystemExit(f"memo float JS already present in {path}")
    text = text.replace(MARKER_JS, MARKER_JS_REPLACEMENT, 1)

    path.write_text(text, encoding="utf-8")
    print(f"patched: {path}")


def _replace_first(text: str, old_variants: list[str], new: str, label: str, path: Path) -> str:
    for old in old_variants:
        if old in text:
            return text.replace(old, new, 1)
    raise SystemExit(f"{label} not found in {path}")


def sync_weekly_rows_block(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if WEEKLY_ROWS_MARKER in text:
        start = text.find(f"      {WEEKLY_ROWS_MARKER}")
        end = text.find("\n      function createInitialRowsIfNeeded()", start)
        if start < 0 or end < 0:
            raise SystemExit(f"weekly memo rows block bounds not found in {path}")
        text = text[:start] + WEEKLY_ROWS_JS.rstrip() + text[end:]
    else:
        anchor = text.find(CREATE_INITIAL_ANCHOR)
        if anchor < 0:
            raise SystemExit(f"createInitialRowsIfNeeded anchor not found in {path}")
        text = text[:anchor] + WEEKLY_ROWS_JS.rstrip() + "\n" + text[anchor:]
    create_initial_ok = (
        "syncSectionFromCatalog(state.variableItems, catalogVariableDefs());\n"
        "        syncWeeklyMemoItems();"
    )
    if create_initial_ok not in text:
        text = _replace_first(
            text,
            CREATE_INITIAL_OLD_VARIANTS,
            """        syncSectionFromCatalog(state.variableItems, catalogVariableDefs());
        syncWeeklyMemoItems();""",
            "createInitialRowsIfNeeded memo init",
            path,
        )
    if "        syncWeeklyMemoItems();\n      }\n      function loadMepFromYearStore" not in text:
        text = _replace_first(
            text, MERGE_MEP_OLD_VARIANTS, MERGE_MEP_NEW, "mergeMepYearPayload tail", path
        )
    if CURRENT_ROWS_NEW not in text:
        if 'rows.push({ type: \'memoRow\', row: r, section: \'memo\' });' in text:
            pass
        else:
            text = _replace_first(text, [CURRENT_ROWS_OLD], CURRENT_ROWS_NEW, "currentRows memo block", path)
    path.write_text(text, encoding="utf-8")
    print(f"synced weekly memo rows: {path}")


def sync_css_block(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find("    /* MEMO-FLOAT-MODAL */")
    end = text.find("\n\n  </style>", start)
    if start < 0 or end < 0:
        raise SystemExit(f"memo float CSS block not found in {path}")
    text = text[:start] + CSS.rstrip() + text[end:]
    path.write_text(text, encoding="utf-8")
    print(f"synced CSS: {path}")


def sync_js_block(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find("      /* MEMO-FLOAT-MODAL */")
    end = text.find("\n\n      initEditPage();")
    if start < 0 or end < 0:
        raise SystemExit(f"memo float JS block not found in {path}")
    text = text[:start] + JS.rstrip() + text[end:]
    path.write_text(text, encoding="utf-8")
    print(f"synced JS: {path}")


def main() -> None:
    ja = ROOT / "app" / "monthly" / "edit" / "index.html"
    en = ROOT / "en" / "app" / "monthly" / "edit" / "index.html"
    if ja.read_text(encoding="utf-8").find('id="memo-float-modal"') >= 0:
        sync_css_block(ja)
        sync_css_block(en)
        sync_weekly_rows_block(ja)
        sync_weekly_rows_block(en)
        sync_js_block(ja)
        sync_js_block(en)
        return
    patch_file(ja, HTML_JA)
    patch_file(en, HTML_EN)


if __name__ == "__main__":
    main()

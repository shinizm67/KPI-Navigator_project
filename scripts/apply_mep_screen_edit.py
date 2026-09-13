#!/usr/bin/env python3
"""Apply MEP whole-screen View/Edit lock to monthly/edit HTML (ja/en/zh-tw).

Source of truth for helpers: `_mep_screen_edit.js`.
Idempotent on current runtime HTML (no-op when already patched).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPERS = (ROOT / "scripts" / "_mep_screen_edit.js").read_text(encoding="utf-8")

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

CSS_OLD = """    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table tr.mef-row--sales-path td .monthly-edit-float__input,
    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table .monthly-edit-float__cb[data-action='bizday-toggle'] {
      opacity: 0.72;
    }"""

CSS_NEW = """    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table .monthly-edit-float__input,
    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table .monthly-edit-float__cb,
    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table .monthly-edit-float__select,
    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__label-edit,
    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__mini-btn[data-action='add-row'],
    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__mini-btn[data-action='remove-row'] {
      opacity: 0.72;
    }"""

PAIRS: list[tuple[str, str]] = [
    (
        """      if (strategyNoteInput) {
        strategyNoteInput.addEventListener('input', function () {
          syncStrategyCharCounter();
          markDirty();
        });
      }""",
        """      if (strategyNoteInput) {
        strategyNoteInput.addEventListener('input', function () {
          if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) return;
          syncStrategyCharCounter();
          markDirty();
        });
      }""",
    ),
    (
        """      function syncUndoButton() {
        if (btnUndo) btnUndo.disabled = undoStack.length === 0;
      }""",
        """      function syncUndoButton() {
        if (!btnUndo) return;
        if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) {
          btnUndo.disabled = true;
          return;
        }
        btnUndo.disabled = undoStack.length === 0;
      }""",
    ),
    (
        """            minus.disabled = len <= 1;
            actions.appendChild(minus);""",
        """            minus.disabled = len <= 1;
            if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) {
              plus.disabled = true;
              minus.disabled = true;
            }
            actions.appendChild(minus);""",
    ),
    (
        """              var mepPathBlockedForBiz = isMepDailySalesPathBlocked();
              if (mepPathBlockedForBiz || (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso))) {""",
        """              var mepPathBlockedForBiz = isMepScreenEditBlocked();
              if (mepPathBlockedForBiz || (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso))) {""",
    ),
    (
        """              sel.disabled = !isMepUiBusinessDay(iso);
              sel.setAttribute('data-action', 'weather-select');
              sel.setAttribute('data-iso', iso);
              sel.setAttribute('aria-label', t('天気 ', 'Weather ') + iso);""",
        """              sel.disabled = !isMepUiBusinessDay(iso) || isMepScreenEditBlocked();
              sel.setAttribute('data-action', 'weather-select');
              sel.setAttribute('data-iso', iso);
              sel.setAttribute('aria-label', t('天気 ', 'Weather ') + iso);
              if (isMepScreenEditBlocked()) sel.setAttribute('title', mepPathSwitchHint());""",
    ),
    (
        """              sel.disabled = !isMepUiBusinessDay(iso);
              sel.setAttribute('data-action', 'weather-select');
              sel.setAttribute('data-iso', iso);
              sel.setAttribute('aria-label', t('天気 ', 'Weather ', '天氣 ') + iso);""",
        """              sel.disabled = !isMepUiBusinessDay(iso) || isMepScreenEditBlocked();
              sel.setAttribute('data-action', 'weather-select');
              sel.setAttribute('data-iso', iso);
              sel.setAttribute('aria-label', t('天気 ', 'Weather ', '天氣 ') + iso);
              if (isMepScreenEditBlocked()) sel.setAttribute('title', mepPathSwitchHint());""",
    ),
    (
        """                    var mepPathBlocked = isMepDailySalesEditBlocked();
                    var salesBlocked =
                      mepIncomeSalesPath &&
                      window.KpiYearStore &&
                      iso &&
                      !KpiYearStore.canWriteDailySalesFrom('mep', iso);
                    if (mepIncomeSalesPath && (mepPathBlocked || salesBlocked)) {""",
        """                    var mepPathBlocked = isMepScreenEditBlocked();
                    var salesBlocked =
                      mepIncomeSalesPath &&
                      window.KpiYearStore &&
                      iso &&
                      !KpiYearStore.canWriteDailySalesFrom('mep', iso);
                    if (mepPathBlocked || salesBlocked) {""",
    ),
    (
        "                var pathBlockedStatic = isMepDailySalesEditBlocked();",
        "                var pathBlockedStatic = isMepScreenEditBlocked();",
    ),
    (
        """      if (closeChooserSave) {
        closeChooserSave.addEventListener('click', function () {
          var run = function () {
            return performMepSave().then(function (putResult) {""",
        """      if (closeChooserSave) {
        closeChooserSave.addEventListener('click', function () {
          if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) {
            window.alert(mepPathSwitchHint());
            return;
          }
          var run = function () {
            return performMepSave().then(function (putResult) {""",
    ),
    (
        """      if (btnUndo) {
        btnUndo.addEventListener('click', function () {
          if (!popUndo()) return;""",
        """      if (btnUndo) {
        btnUndo.addEventListener('click', function () {
          if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) return;
          if (!popUndo()) return;""",
    ),
    (
        """        function isMepSalesPathActive() {
          return !!(
            window.KpiYearStore &&
            typeof KpiYearStore.getDailySalesInputPath === 'function' &&
            KpiYearStore.getDailySalesInputPath() === 'mep'
          );
        }""",
        """        function isMepSalesPathActive() {
          return typeof isMepScreenEditBlocked === 'function' && !isMepScreenEditBlocked();
        }""",
    ),
    (
        """        btnExpenseCsvUpload.addEventListener('click', function () {
          var input = ensureExpenseInput();""",
        """        btnExpenseCsvUpload.addEventListener('click', function () {
          if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) return;
          var input = ensureExpenseInput();""",
    ),
    (
        """        btnConfirm.addEventListener('pointerdown', function (ev) {
          if (ev.button != null && ev.button !== 0) return;
          mepSaveInProgress = true;
        });""",
        """        btnConfirm.addEventListener('pointerdown', function (ev) {
          if (ev.button != null && ev.button !== 0) return;
          if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) return;
          mepSaveInProgress = true;
        });""",
    ),
    (
        """        btnConfirm.addEventListener('click', function () {
          /* KPI-BUSY-CSV-CLOSE-DA: Save overlay closes within 20s even if rebuild/flush stalls */""",
        """        btnConfirm.addEventListener('click', function () {
          if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) return;
          /* KPI-BUSY-CSV-CLOSE-DA: Save overlay closes within 20s even if rebuild/flush stalls */""",
    ),
    (
        """        } else if (action === 'add-row') {
          pushUndo();""",
        """        } else if (action === 'add-row') {
          if (isMepScreenEditBlocked()) return;
          pushUndo();""",
    ),
    (
        """        } else if (action === 'remove-row') {
          var sec2 = btn.getAttribute('data-section');""",
        """        } else if (action === 'remove-row') {
          if (isMepScreenEditBlocked()) return;
          var sec2 = btn.getAttribute('data-section');""",
    ),
    (
        """        } else if (action === 'edit-label') {
          var rowId = btn.getAttribute('data-row-id');""",
        """        } else if (action === 'edit-label') {
          if (isMepScreenEditBlocked()) return;
          var rowId = btn.getAttribute('data-row-id');""",
    ),
    (
        """        if (action === 'bizday-toggle') {
          var iso = target.getAttribute('data-iso');
          if (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso)) {
            target.checked = bizDayByIso[iso] !== false;
            return;
          }""",
        """        if (action === 'bizday-toggle') {
          var iso = target.getAttribute('data-iso');
          if (isMepScreenEditBlocked() || (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso))) {
            target.checked = bizDayByIso[iso] !== false;
            return;
          }""",
    ),
    (
        """        } else if (action === 'money-input') {
          var rowId = target.getAttribute('data-row-id');
          var iso2 = target.getAttribute('data-iso');
          if (
            (target.getAttribute('data-mep-daily-input') === '1' && isMepDailySalesEditBlocked()) ||
            (target.getAttribute('data-mep-sales-path') === '1' && isMepDailySalesEditBlocked())
          ) {
            buildGrid();
            return;
          }""",
        """        } else if (action === 'money-input') {
          var rowId = target.getAttribute('data-row-id');
          var iso2 = target.getAttribute('data-iso');
          if (isMepScreenEditBlocked()) {
            buildGrid();
            return;
          }""",
    ),
    (
        """        } else if (action === 'count-input') {
          if (isMepDailySalesEditBlocked()) {
            buildGrid();
            return;
          }""",
        """        } else if (action === 'count-input') {
          if (isMepScreenEditBlocked()) {
            buildGrid();
            return;
          }""",
    ),
    (
        """        } else if (action === 'memo-input') {
          var rowIdM = target.getAttribute('data-row-id');""",
        """        } else if (action === 'memo-input') {
          if (isMepScreenEditBlocked()) {
            buildGrid();
            return;
          }
          var rowIdM = target.getAttribute('data-row-id');""",
    ),
    (
        """        } else if (action === 'weather-select') {
          var isoW = target.getAttribute('data-iso');""",
        """        } else if (action === 'weather-select') {
          if (isMepScreenEditBlocked()) {
            buildGrid();
            return;
          }
          var isoW = target.getAttribute('data-iso');""",
    ),
    (
        """      function saveMemoFloatModal() {
        flushPendingMemoEditsFromDom();""",
        """      function saveMemoFloatModal() {
        if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) {
          window.alert(mepPathSwitchHint());
          return Promise.resolve(false);
        }
        flushPendingMemoEditsFromDom();""",
    ),
    (
        """      function memoFloatAddRow(afterIdx) {
        pushMemoFloatUndo();""",
        """      function memoFloatAddRow(afterIdx) {
        if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) return;
        pushMemoFloatUndo();""",
    ),
    (
        """      function memoFloatRemoveRow(removeIdx) {
        if (isWeeklyFixedMemoIndex(removeIdx)) return;""",
        """      function memoFloatRemoveRow(removeIdx) {
        if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) return;
        if (isWeeklyFixedMemoIndex(removeIdx)) return;""",
    ),
    (
        "        if (!memoFloatBizDay(iso)) ta.disabled = true;",
        """        if (!memoFloatBizDay(iso) || (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked())) {
          ta.disabled = true;
          ta.readOnly = true;
        }""",
    ),
    (
        "          appendMemoFloatBlock(freeSection, state.memoItems[fi], fi, iso, true);",
        "          appendMemoFloatBlock(freeSection, state.memoItems[fi], fi, iso, !isMepScreenEditBlocked());",
    ),
    (
        """        if (
          row.editableLabel !== false &&
          !row.weeklyFixed
        ) {""",
        """        if (
          row.editableLabel !== false &&
          !row.weeklyFixed &&
          !(typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked())
        ) {""",
    ),
]

EDIT_LABEL_PAIRS = [
    (
        """          btnEdit.setAttribute('aria-label', t('費目名を編集', 'Edit label'));
          main.appendChild(btnEdit);""",
        """          btnEdit.setAttribute('aria-label', t('費目名を編集', 'Edit label'));
          if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) {
            btnEdit.disabled = true;
            btnEdit.setAttribute('title', mepPathSwitchHint());
          }
          main.appendChild(btnEdit);""",
    ),
    (
        """          btnEdit.setAttribute('aria-label', t('費目名を編集', 'Edit label', '編輯科目名稱'));
          main.appendChild(btnEdit);""",
        """          btnEdit.setAttribute('aria-label', t('費目名を編集', 'Edit label', '編輯科目名稱'));
          if (typeof isMepScreenEditBlocked === 'function' && isMepScreenEditBlocked()) {
            btnEdit.disabled = true;
            btnEdit.setAttribute('title', mepPathSwitchHint());
          }
          main.appendChild(btnEdit);""",
    ),
]

REQUIRED = [
    "function isMepScreenEditBlocked()",
    "function syncMepScreenEditToolbar()",
    "mepPathBlocked || salesBlocked",
    "isMepScreenEditBlocked()",
    "btnExpenseCsvUpload.disabled",
    "btnConfirm.disabled",
    "strategyNoteInput.readOnly",
    "if (isMepScreenEditBlocked()) return",
    "function saveMemoFloatModal",
]


def replace_helpers(text: str) -> str:
    start_tok = "      function isMepDailySalesPathBlocked() {"
    end_tok = "      function manualInputHint() {"
    start = text.find(start_tok)
    end = text.find(end_tok)
    if start < 0 or end < 0 or end <= start:
        raise SystemExit("MEP screen-edit helper block not found")
    block = HELPERS.rstrip() + "\n"
    return text[:start] + block + text[end:]


def apply_pair(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new)
    return text


def patch_file(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    text = original
    if CSS_OLD in text:
        text = text.replace(CSS_OLD, CSS_NEW)
    text = replace_helpers(text)
    for old, new in PAIRS:
        text = apply_pair(text, old, new)
    for old, new in EDIT_LABEL_PAIRS:
        if old in text:
            text = text.replace(old, new)
    missing = [item for item in REQUIRED if item not in text]
    if missing:
        raise SystemExit(f"{path}: missing {missing}")
    if text == original:
        print(f"unchanged: {path.relative_to(ROOT)}")
        return
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"patched: {path.relative_to(ROOT)}")


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        patch_file(path)


if __name__ == "__main__":
    main()

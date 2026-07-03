#!/usr/bin/env python3
"""Phase 5: edit lock UI + daily sales input path exclusivity (Annual vs MEP)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ANNUAL_TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]
MEP_TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

KPI_EDIT_GUARDS_MARKER = "/* KPI-EDIT-GUARDS */"

EDIT_GUARDS_JS = """      /* KPI-EDIT-GUARDS */
      (function () {
        function storeReady() {
          return !!(window.KpiYearStore && KpiYearStore.getDailySalesInputPath);
        }
        function isJa() {
          return String(document.documentElement.getAttribute('lang') || '')
            .toLowerCase()
            .indexOf('ja') === 0;
        }
        function annualSalesPathActive() {
          return !storeReady() || KpiYearStore.getDailySalesInputPath() === 'annual';
        }
        function mepSalesPathActive() {
          return storeReady() && KpiYearStore.getDailySalesInputPath() === 'mep';
        }
        function pastSalesEditable() {
          return storeReady() && KpiYearStore.getPastSalesEditEnabled();
        }
        function setInputsReadOnly(root, readOnly, selector) {
          if (!root) return;
          root.querySelectorAll(selector || 'input, textarea, select, button').forEach(function (el) {
            if (el.matches('[data-kpi-guard-ignore]')) return;
            if (el.matches('.past-sales-modal__close, .sales-data-modal__close, .annual-edit-modal__close')) return;
            if (el.matches('[role="tab"]')) return;
            if (readOnly) {
              if (!el.hasAttribute('data-kpi-guard-was-disabled')) {
                el.setAttribute('data-kpi-guard-was-disabled', el.disabled ? '1' : '0');
              }
              el.disabled = true;
              if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.readOnly = true;
              }
            } else if (el.hasAttribute('data-kpi-guard-was-disabled')) {
              el.disabled = el.getAttribute('data-kpi-guard-was-disabled') === '1';
              el.removeAttribute('data-kpi-guard-was-disabled');
              if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.readOnly = false;
              }
            }
          });
        }
        function applyPastSalesGuards() {
          var modal = document.getElementById('past-sales-modal');
          if (!modal || modal.hidden) return;
          var inputTab = modal.getAttribute('data-psm-tab') === 'input';
          var viewOnly = inputTab && !pastSalesEditable();
          var pane = document.getElementById('past-sales-pane-input');
          if (pane) {
            pane.classList.toggle('past-sales-modal__pane--view-only', viewOnly);
            setInputsReadOnly(
              pane,
              viewOnly,
              '.past-sales-modal__sales-input, .past-sales-modal__cb, .past-sales-modal__summary-reference-input, .past-sales-modal__filter-row input'
            );
          }
          ['past-sales-modal-save', 'past-sales-modal-undo', 'past-sales-modal-csv'].forEach(function (id) {
            var btn = document.getElementById(id);
            if (!btn) return;
            if (viewOnly) {
              if (!btn.hasAttribute('data-kpi-guard-was-disabled')) {
                btn.setAttribute('data-kpi-guard-was-disabled', btn.disabled ? '1' : '0');
              }
              btn.disabled = true;
            } else if (btn.hasAttribute('data-kpi-guard-was-disabled')) {
              btn.disabled = btn.getAttribute('data-kpi-guard-was-disabled') === '1';
              btn.removeAttribute('data-kpi-guard-was-disabled');
            }
          });
        }
        function applySalesDataGuards() {
          var modal = document.getElementById('sales-data-modal');
          if (!modal || modal.hidden) return;
          var pane = document.getElementById('sales-data-pane-input');
          if (!pane) return;
          var blocked = mepSalesPathActive();
          pane.classList.toggle('sales-data-modal__pane--path-blocked', blocked);
          setInputsReadOnly(
            pane,
            blocked,
            '.sales-data-modal__sales-input, .sales-data-modal__cb, .sales-data-modal__summary-reference-input'
          );
          var save = document.getElementById('sales-data-modal-save');
          if (save) {
            if (blocked) {
              if (!save.hasAttribute('data-kpi-guard-was-disabled')) {
                save.setAttribute('data-kpi-guard-was-disabled', save.disabled ? '1' : '0');
              }
              save.disabled = true;
            } else if (save.hasAttribute('data-kpi-guard-was-disabled')) {
              save.disabled = save.getAttribute('data-kpi-guard-was-disabled') === '1';
              save.removeAttribute('data-kpi-guard-was-disabled');
            }
          }
        }
        function applyAnnualEditGuards() {
          var modal = document.getElementById('annual-edit-modal');
          if (!modal || modal.hidden) return;
          var blocked = mepSalesPathActive();
          modal.classList.toggle('annual-edit-modal--path-blocked', blocked);
          setInputsReadOnly(
            modal,
            blocked,
            '.annual-edit-modal__sales-input, .annual-edit-modal__cb'
          );
        }
        function syncPastSalesEditToggleUi() {
          var wrap = document.getElementById('past-sales-edit-mode');
          if (!wrap) return;
          var on = pastSalesEditable();
          wrap.querySelectorAll('[data-ps-edit-mode]').forEach(function (btn) {
            var mode = btn.getAttribute('data-ps-edit-mode');
            var active = (mode === 'edit') === on;
            btn.classList.toggle('is-active', active);
            btn.setAttribute('aria-pressed', active ? 'true' : 'false');
          });
        }
        function applyAllGuards() {
          syncPastSalesEditToggleUi();
          applyPastSalesGuards();
          applySalesDataGuards();
          applyAnnualEditGuards();
          document.dispatchEvent(new CustomEvent('kpi:editGuardsApplied'));
        }
        function bindPastSalesEditToggle() {
          var wrap = document.getElementById('past-sales-edit-mode');
          if (!wrap || wrap.getAttribute('data-kpi-bound') === '1') return;
          wrap.setAttribute('data-kpi-bound', '1');
          wrap.addEventListener('click', function (ev) {
            var btn = ev.target.closest('[data-ps-edit-mode]');
            if (!btn || !storeReady()) return;
            var mode = btn.getAttribute('data-ps-edit-mode');
            if (mode === 'edit' && !KpiYearStore.getPastSalesEditEnabled()) {
              var ok = window.confirm(
                isJa()
                  ? '過去売上データの編集モードに切り替えます。確定済みの年は編集できません。'
                  : 'Switch to edit mode for past sales. Locked years remain read-only.'
              );
              if (!ok) return;
            }
            KpiYearStore.setPastSalesEditEnabled(mode === 'edit');
            applyAllGuards();
          });
        }
        bindPastSalesEditToggle();
        document.addEventListener('kpi:dailySalesInputPathChanged', applyAllGuards);
        document.addEventListener('kpi:pastSalesEditChanged', applyAllGuards);
        document.addEventListener('kpi:editLeaseChanged', applyAllGuards);
        document.addEventListener('kpi:editGuardsRefresh', applyAllGuards);
        window.__KPI_EDIT_GUARDS = {
          applyAll: applyAllGuards,
          annualSalesPathActive: annualSalesPathActive,
          mepSalesPathActive: mepSalesPathActive,
          pastSalesEditable: pastSalesEditable,
        };
        applyAllGuards();
      })();
"""

PAST_SALES_TOGGLE_JA = """        <div
          class="past-sales-modal__edit-mode"
          id="past-sales-edit-mode"
          role="group"
          aria-label="過去データの編集モード"
        >
          <button
            type="button"
            class="past-sales-modal__edit-mode-btn is-active"
            data-ps-edit-mode="view"
            data-kpi-guard-ignore
            aria-pressed="true"
            title="閲覧のみ（過去データは編集できません）"
          >
            閲覧
          </button>
          <button
            type="button"
            class="past-sales-modal__edit-mode-btn"
            data-ps-edit-mode="edit"
            data-kpi-guard-ignore
            aria-pressed="false"
            title="編集モード（確定済みの年は編集不可）"
          >
            編集
          </button>
        </div>"""

PAST_SALES_TOGGLE_EN = PAST_SALES_TOGGLE_JA.replace(
    '過去データの編集モード', 'Past data edit mode'
).replace(
    '閲覧のみ（過去データは編集できません）', 'View only (past data is read-only)'
).replace('閲覧', 'View').replace(
    '編集モード（確定済みの年は編集不可）', 'Edit mode (locked years stay read-only)'
).replace('編集', 'Edit')

PAST_SALES_TOGGLE_CSS = """
    .past-sales-modal__edit-mode {
      position: absolute;
      top: var(--psm-tab-top);
      right: 22px;
      display: flex;
      gap: 4px;
      z-index: 6;
    }
    .past-sales-modal__edit-mode-btn {
      min-width: 52px;
      height: 27px;
      margin: 0;
      padding: 0 8px;
      border: 1px solid rgba(88, 225, 243, 0.55);
      border-radius: 2px;
      background: rgba(88, 225, 243, 0.12);
      color: #58e1f3;
      font: inherit;
      font-size: 12px;
      cursor: pointer;
    }
    .past-sales-modal__edit-mode-btn.is-active {
      background: rgba(88, 225, 243, 0.55);
      color: #000;
      font-weight: 700;
    }
    .past-sales-modal__pane--view-only .past-sales-modal__sales-input,
    .sales-data-modal__pane--path-blocked .sales-data-modal__sales-input,
    .sales-data-modal__pane--path-blocked .sales-data-modal__cb,
    .annual-edit-modal--path-blocked .annual-edit-modal__sales-input,
    .annual-edit-modal--path-blocked .annual-edit-modal__cb {
      opacity: 0.72;
    }"""

MEP_PERSIST_OLD = """      function persistAnnualDailyShared() {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!daily) return;
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(daily);
          return;
        }"""

MEP_PERSIST_NEW = """      function persistAnnualDailyShared() {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!daily) return;
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(daily, { source: 'monthly-edit-float' });
          return;
        }"""

MEP_BIZDAY_OLD = """      function persistBusinessDayToAnnualStore(iso, isBusinessDay) {
        var daily = ensureAnnualDailyStore();
        daily.businessDayByDate[iso] = !!isBusinessDay;
        var cur = Number(daily.targetSalesByDate[iso]);
        if (!isBusinessDay) {
          daily.targetSalesByDate[iso] = 0;
        } else if (!Number.isFinite(cur) || cur <= 0) {
          daily.targetSalesByDate[iso] = 1234;
        }
        persistAnnualDailyShared();
      }"""

MEP_BIZDAY_NEW = """      function persistBusinessDayToAnnualStore(iso, isBusinessDay) {
        if (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso)) return;
        var daily = ensureAnnualDailyStore();
        daily.businessDayByDate[iso] = !!isBusinessDay;
        var cur = Number(daily.targetSalesByDate[iso]);
        if (!isBusinessDay) {
          daily.targetSalesByDate[iso] = 0;
        } else if (!Number.isFinite(cur) || cur <= 0) {
          delete daily.targetSalesByDate[iso];
        }
        persistAnnualDailyShared();
      }"""

MEP_MONEY_HANDLER_OLD = """        } else if (action === 'money-input') {
          var rowId = target.getAttribute('data-row-id');
          var iso2 = target.getAttribute('data-iso');
          pushUndo();
          writeValue(rowId, iso2, parseMoney(target.value));
          if (MEF_STATIC_INPUT_IDS.indexOf(rowId) < 0) {
            syncMonthlySalesToAnnualStoreForMonth();
            document.dispatchEvent(new CustomEvent('annual:salesMapChanged', { detail: { year: mefYear, source: 'monthly-edit-float' } }));
          }
          markDirty();
          buildGrid();
        }"""

MEP_MONEY_HANDLER_NEW = """        } else if (action === 'money-input') {
          var rowId = target.getAttribute('data-row-id');
          var iso2 = target.getAttribute('data-iso');
          if (window.KpiYearStore && !KpiYearStore.canWriteDailySalesFrom('mep', iso2)) {
            buildGrid();
            return;
          }
          pushUndo();
          writeValue(rowId, iso2, parseMoney(target.value));
          if (MEF_STATIC_INPUT_IDS.indexOf(rowId) < 0) {
            syncMonthlySalesToAnnualStoreForMonth();
            document.dispatchEvent(new CustomEvent('annual:salesMapChanged', { detail: { year: mefYear, source: 'monthly-edit-float' } }));
          }
          markDirty();
          buildGrid();
        }"""

MEP_BIZDAY_HANDLER_OLD = """        if (action === 'bizday-toggle') {
          var iso = target.getAttribute('data-iso');
          pushUndo();
          bizDayByIso[iso] = !!target.checked;
          persistBusinessDayToAnnualStore(iso, !!target.checked);"""

MEP_BIZDAY_HANDLER_NEW = """        if (action === 'bizday-toggle') {
          var iso = target.getAttribute('data-iso');
          if (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso)) {
            target.checked = bizDayByIso[iso] !== false;
            return;
          }
          pushUndo();
          bizDayByIso[iso] = !!target.checked;
          persistBusinessDayToAnnualStore(iso, !!target.checked);"""

MEP_INPUT_DISABLE_OLD = """                if (r.row.mepEditable) {
                  inp.setAttribute('title', manualInputHint());
                } else {
                  inp.disabled = true;
                  inp.readOnly = true;
                  inp.setAttribute('title', t('PL表で月次入力', 'Enter monthly on PL table'));
                }"""

MEP_INPUT_DISABLE_NEW = """                if (r.row.mepEditable) {
                  var salesBlocked =
                    window.KpiYearStore &&
                    iso &&
                    !KpiYearStore.canWriteDailySalesFrom('mep', iso);
                  if (salesBlocked) {
                    inp.disabled = true;
                    inp.readOnly = true;
                    inp.setAttribute(
                      'title',
                      t(
                        '日次売上の入力経路は Annual / Sales Data です（設定で MEP に切替可）',
                        'Daily sales input is via Annual / Sales Data (switch to MEP in settings)'
                      )
                    );
                  } else {
                    inp.setAttribute('title', manualInputHint());
                  }
                } else {
                  inp.disabled = true;
                  inp.readOnly = true;
                  inp.setAttribute('title', t('PL表で月次入力', 'Enter monthly on PL table'));
                }"""

ANNUAL_PERSIST_OLD = """      function persistAnnualDailyShared() {
        var d = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!d) return;
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(d);
          return;
        }"""

ANNUAL_PERSIST_NEW = """      function persistAnnualDailyShared() {
        var d = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!d) return;
        if (window.KpiYearStore) {
          KpiYearStore.persistFromAnnualDaily(d, { source: 'annual-daily-compat' });
          return;
        }"""

MEP_BIZDAY_CB_OLD = """              cb.setAttribute('data-action', 'bizday-toggle');
              cb.setAttribute('data-iso', iso);
              td.appendChild(cb);"""

MEP_BIZDAY_CB_NEW = """              cb.setAttribute('data-action', 'bizday-toggle');
              cb.setAttribute('data-iso', iso);
              if (window.KpiYearStore && !KpiYearStore.canWriteBusinessDayFrom('mep', iso)) {
                cb.disabled = true;
                cb.title = t(
                  '営業日の入力経路は Annual / Sales Data です',
                  'Business-day input is via Annual / Sales Data'
                );
              }
              td.appendChild(cb);"""

PAST_SALES_OPEN_PATCH_OLD = """        var resumeTab = savedUi && savedUi.activeTab === 'analyze' ? 'analyze' : 'input';
        setPastSalesTab(resumeTab);
        renderPastSalesTable();
        modal.removeAttribute('hidden');"""

PAST_SALES_OPEN_PATCH_NEW = """        var resumeTab = savedUi && savedUi.activeTab === 'analyze' ? 'analyze' : 'input';
        setPastSalesTab(resumeTab);
        renderPastSalesTable();
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }
        modal.removeAttribute('hidden');"""

SALES_DATA_OPEN_PATCH_OLD = """          setSalesDataTab(resumeTab);
          renderSalesDataTable();
          modal.removeAttribute('hidden');
          document.body.style.overflow = 'hidden';"""

SALES_DATA_OPEN_PATCH_NEW = """          setSalesDataTab(resumeTab);
          renderSalesDataTable();
          modal.removeAttribute('hidden');
          document.body.style.overflow = 'hidden';
          if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
            window.__KPI_EDIT_GUARDS.applyAll();
          }"""

ANNUAL_EDIT_OPEN_PATCH_OLD = """        renderTable();
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');"""

ANNUAL_EDIT_OPEN_PATCH_NEW = """        renderTable();
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        if (window.__KPI_EDIT_GUARDS && typeof window.__KPI_EDIT_GUARDS.applyAll === 'function') {
          window.__KPI_EDIT_GUARDS.applyAll();
        }"""


def inject_edit_guards_js(text: str) -> str:
    guards = (ROOT / "scripts" / "_kpi_edit_guards.js").read_text(encoding="utf-8")
    if KPI_EDIT_GUARDS_MARKER not in text:
        anchor = "/* KPI-YEAR-STORE */"
        pos = text.find(anchor)
        if pos < 0:
            raise SystemExit("KPI-YEAR-STORE anchor not found")
        end = text.find("})();", pos)
        if end < 0:
            raise SystemExit("KPI-YEAR-STORE block end not found")
        end = text.find("\n", end) + 1
        return text[:end] + "\n" + guards + text[end:]
    if "window.__KPI_EDIT_GUARDS" in text:
        pattern = re.compile(
            r"/\* KPI-EDIT-GUARDS \*/.*?\n      \(function \(\) \{.*?\n      \}\)\(\);\n",
            re.DOTALL,
        )
        return pattern.sub(guards.rstrip() + "\n", text, count=1)
    empty = re.compile(r"\n\s*/\* KPI-EDIT-GUARDS \*/\s*\n+(?=\s*/\* KPI-)", re.MULTILINE)
    return empty.sub("\n" + guards.rstrip() + "\n", text, count=1)


def remove_past_sales_edit_toggle(text: str) -> str:
    text = re.sub(
        r"\n        <div\n          class=\"past-sales-modal__edit-mode\"[\s\S]*?\n        </div>",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"\n    \.past-sales-modal__edit-mode \{[\s\S]*?\n    \}\n    \.past-sales-modal__edit-mode-btn\.is-active \{[\s\S]*?\n    \}",
        "",
        text,
        count=1,
    )
    return text


def patch_annual(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = remove_past_sales_edit_toggle(text)
    if ANNUAL_PERSIST_OLD in text:
        text = text.replace(ANNUAL_PERSIST_OLD, ANNUAL_PERSIST_NEW, 1)
    if PAST_SALES_OPEN_PATCH_OLD in text:
        text = text.replace(PAST_SALES_OPEN_PATCH_OLD, PAST_SALES_OPEN_PATCH_NEW, 1)
    if SALES_DATA_OPEN_PATCH_OLD in text:
        text = text.replace(SALES_DATA_OPEN_PATCH_OLD, SALES_DATA_OPEN_PATCH_NEW, 1)
    if ANNUAL_EDIT_OPEN_PATCH_OLD in text:
        text = text.replace(ANNUAL_EDIT_OPEN_PATCH_OLD, ANNUAL_EDIT_OPEN_PATCH_NEW, 1)
    text = inject_edit_guards_js(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_mep(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in (
        (MEP_PERSIST_OLD, MEP_PERSIST_NEW),
        (MEP_BIZDAY_OLD, MEP_BIZDAY_NEW),
        (MEP_MONEY_HANDLER_OLD, MEP_MONEY_HANDLER_NEW),
        (MEP_BIZDAY_HANDLER_OLD, MEP_BIZDAY_HANDLER_NEW),
        (MEP_INPUT_DISABLE_OLD, MEP_INPUT_DISABLE_NEW),
        (MEP_BIZDAY_CB_OLD, MEP_BIZDAY_CB_NEW),
    ):
        if old not in text:
            raise SystemExit(f"MEP patch block not found in {path}")
        text = text.replace(old, new, 1)
    if KPI_EDIT_GUARDS_MARKER not in text:
        anchor = "/* KPI-YEAR-STORE */"
        pos = text.find(anchor)
        if pos < 0:
            raise SystemExit(f"KPI-YEAR-STORE not found in {path}")
        end = text.find("})();", pos)
        end = text.find("\n", end) + 1
        mep_guard = """      /* KPI-EDIT-GUARDS */
      (function () {
        function refreshMepSalesGuards() {
          if (typeof buildGrid === 'function') buildGrid();
        }
        document.addEventListener('kpi:dailySalesInputPathChanged', refreshMepSalesGuards);
        document.addEventListener('kpi:editGuardsApplied', refreshMepSalesGuards);
        document.addEventListener('kpi:editGuardsRefresh', refreshMepSalesGuards);
        document.addEventListener('kpi:editLeaseChanged', refreshMepSalesGuards);
      })();
"""
        text = text[:end] + "\n" + mep_guard + text[end:]
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in ANNUAL_TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_annual(path)
    for path in MEP_TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_mep(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

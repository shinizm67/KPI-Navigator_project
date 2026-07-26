#!/usr/bin/env python3
"""Inject shared PL line catalog into Monthly Edit pages (JA/EN)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pl_line_catalog import mep_catalog_js  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

CATALOG_MARKER = "/* PL-MEP-LINE-CATALOG */"
CSS_MARKER = "/* PL-MEP-DAILY-INPUT-STYLE */"
SYNC_MARKER = "/* PL-MEP-PL-CATALOG-SYNC */"

CATALOG_BLOCK = f"""      {CATALOG_MARKER}
      var PL_LINE_CATALOG = {mep_catalog_js()};
      var PL_CATALOG_BY_ID = {{}};
      PL_LINE_CATALOG.forEach(function (entry) {{
        PL_CATALOG_BY_ID[entry.lineId] = entry;
      }});
      var PL_CATALOG_STORAGE_KEY = 'kpiNavigator.plLineCatalog';
      function loadPlCatalogLines() {{
        try {{
          var raw = localStorage.getItem(PL_CATALOG_STORAGE_KEY);
          if (!raw) return null;
          var parsed = JSON.parse(raw);
          if (!parsed || !Array.isArray(parsed.lines) || !parsed.lines.length) return null;
          return parsed.lines.filter(function (line) {{
            return line && line.active !== false;
          }});
        }} catch (_e) {{
          return null;
        }}
      }}
      function loadPlExpenseCatalogLines() {{
        var lines = loadPlCatalogLines();
        if (!lines) return null;
        return lines.filter(function (line) {{
          return !!line.bucket;
        }});
      }}
      function plLineToMepDef(line) {{
        var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
        if (style !== 'daily') style = 'monthly';
        return {{
          lineId: line.lineId,
          section: 'expense',
          bucket: line.bucket,
          labelJa: line.labelJa,
          labelEn: line.labelEn,
          editableLabel: false,
          inputStyle: line.inputStyle || style,
          resolvedInputStyle: style,
          mepEditable: style === 'daily',
          active: line.active !== false,
        }};
      }}
      function catalogExpenseDefsFromStorage(bucket) {{
        var lines = loadPlExpenseCatalogLines();
        if (!lines) return null;
        return lines
          .filter(function (line) {{ return line.bucket === bucket; }})
          .sort(function (a, b) {{
            return (a.sortOrder || 0) - (b.sortOrder || 0);
          }})
          .map(plLineToMepDef);
      }}
      function catalogExpenseDefsFromEmbedded(bucket) {{
        return PL_LINE_CATALOG.filter(function (e) {{
          return e.bucket === bucket && e.active !== false;
        }});
      }}
      function catalogIncomeDefs() {{
        var fromStorage = loadPlCatalogLines();
        if (fromStorage) {{
          var defs = fromStorage
            .filter(function (line) {{
              return line.section === 'income';
            }})
            .map(function (line) {{
              var base = PL_CATALOG_BY_ID[line.lineId] || line || {{}};
              return {{
                lineId: line.lineId,
                section: 'income',
                bucket: null,
                labelJa: line.labelJa || base.labelJa || line.lineId,
                labelEn: line.labelEn || base.labelEn || line.lineId,
                editableLabel: base.editableLabel === true,
                inputStyle: base.inputStyle || 'daily',
                resolvedInputStyle: base.resolvedInputStyle || 'daily',
                mepEditable: base.mepEditable !== false,
                mepAutoCalc: base.mepAutoCalc === true,
                active: line.active !== false,
              }};
            }});
          if (defs.length) return defs;
        }}
        return PL_LINE_CATALOG.filter(function (e) {{ return e.section === 'income'; }});
      }}
      function catalogFixedDefs() {{
        var fromStorage = catalogExpenseDefsFromStorage('fixed');
        if (fromStorage) return fromStorage;
        return catalogExpenseDefsFromEmbedded('fixed');
      }}
      function catalogVariableDefs() {{
        var fromStorage = catalogExpenseDefsFromStorage('variable');
        if (fromStorage) return fromStorage;
        return catalogExpenseDefsFromEmbedded('variable');
      }}
      function makeCatalogRow(def) {{
        return {{
          id: def.lineId,
          lineId: def.lineId,
          kind: 'money',
          labelJa: def.labelJa,
          labelEn: def.labelEn,
          editableLabel: !!def.editableLabel,
          deletable: false,
          sub: def.section === 'expense',
          mepEditable: !!def.mepEditable,
          mepAutoCalc: def.mepAutoCalc === true,
          resolvedInputStyle: def.resolvedInputStyle || 'monthly',
          bucket: def.bucket || null
        }};
      }}
      function syncSectionFromCatalog(targetArr, defs) {{
        if (!targetArr.length) {{
          defs.forEach(function (d) {{ targetArr.push(makeCatalogRow(d)); }});
          return;
        }}
        var byLine = {{}};
        targetArr.forEach(function (r) {{
          if (r.lineId) byLine[r.lineId] = r;
        }});
        targetArr.length = 0;
        defs.forEach(function (d) {{
          var prev = byLine[d.lineId];
          if (prev) {{
            prev.labelJa = d.labelJa;
            prev.labelEn = d.labelEn;
            prev.mepEditable = !!d.mepEditable;
            prev.mepAutoCalc = !!d.mepAutoCalc;
            prev.resolvedInputStyle = d.resolvedInputStyle || 'monthly';
            prev.bucket = d.bucket || null;
            prev.editableLabel = !!d.editableLabel;
            prev.deletable = false;
            targetArr.push(prev);
          }} else {{
            targetArr.push(makeCatalogRow(d));
          }}
        }});
      }}
      function upsertPlIncomeLabelsFromState() {{
        var lines = loadPlCatalogLines();
        if (!lines) {{
          lines = JSON.parse(JSON.stringify(PL_LINE_CATALOG));
        }}
        var changed = false;
        var ids = {{ sales_a: true, sales_b: true }};
        (state.incomeItems || []).forEach(function (row) {{
          if (!row || !ids[row.lineId]) return;
          var line = lines.find(function (l) {{ return l.lineId === row.lineId; }});
          if (!line) return;
          var nextJa = row.labelJa || line.labelJa;
          var nextEn = row.labelEn || line.labelEn;
          if (line.labelJa !== nextJa || line.labelEn !== nextEn) {{
            line.labelJa = nextJa;
            line.labelEn = nextEn;
            changed = true;
          }}
        }});
        if (!changed) return;
        try {{
          localStorage.setItem(
            PL_CATALOG_STORAGE_KEY,
            JSON.stringify({{ lines: lines, updatedAt: Date.now() }})
          );
          window.dispatchEvent(new Event('pl-expense-catalog-changed'));
        }} catch (_e) {{}}
      }}
"""

SYNC_BLOCK = f"""      {SYNC_MARKER}
      function refreshExpenseCatalogFromPl() {{
        createInitialRowsIfNeeded();
        syncSectionFromCatalog(state.fixedItems, catalogFixedDefs());
        syncSectionFromCatalog(state.variableItems, catalogVariableDefs());
        try {{
          buildGrid();
          syncLabelScroll();
          pinLabelsToRight();
        }} catch (_e) {{}}
      }}
      window.addEventListener('storage', function (ev) {{
        if (ev.key === PL_CATALOG_STORAGE_KEY) refreshExpenseCatalogFromPl();
      }});
      window.addEventListener('pl-expense-catalog-changed', refreshExpenseCatalogFromPl);
      window.addEventListener('pl-expense-label-changed', refreshExpenseCatalogFromPl);
"""

CSS_BLOCK = f"""    {CSS_MARKER}
    .monthly-edit-float__label-row--daily-input {{
      background: rgba(20, 72, 52, 0.72);
      color: rgba(210, 245, 225, 0.96);
    }}
    .monthly-edit-float__label-row--daily-input.monthly-edit-float__label-row--input-income {{
      background: rgba(18, 68, 96, 0.72);
      color: rgba(200, 240, 255, 0.96);
    }}
    .monthly-edit-float__label-row--pl-readonly {{
      opacity: 0.82;
    }}
    .monthly-edit-float__table tr.mef-row--daily-input td {{
      background: rgba(20, 72, 52, 0.72) !important;
    }}
    .monthly-edit-float__table tr.mef-row--daily-input.mef-row--input-income td {{
      background: rgba(18, 68, 96, 0.72) !important;
    }}
    .monthly-edit-float__table tr.mef-row--daily-input td.kpi-fill-empty {{
      background: rgba(16, 58, 42, 0.82) !important;
      box-shadow: inset 0 0 0 1px rgba(120, 200, 150, 0.22);
    }}
    .monthly-edit-float__table tr.mef-row--daily-input.mef-row--input-income td.kpi-fill-empty {{
      background: rgba(14, 52, 78, 0.82) !important;
      box-shadow: inset 0 0 0 1px rgba(120, 200, 230, 0.28);
    }}
    .monthly-edit-float__table tr.mef-row--daily-input td .monthly-edit-float__input:not(:disabled) {{
      color: rgba(210, 245, 225, 0.96);
    }}
    .monthly-edit-float__table tr.mef-row--daily-input.mef-row--input-income td .monthly-edit-float__input:not(:disabled) {{
      color: rgba(200, 240, 255, 0.96);
    }}
    .monthly-edit-float__table tr.mef-row--pl-readonly td {{
      opacity: 0.75;
    }}
    body.office-mode .monthly-edit-float__label-row--daily-input {{
      background: rgba(180, 220, 200, 0.45);
      color: #113322;
    }}
    body.office-mode .monthly-edit-float__label-row--daily-input.monthly-edit-float__label-row--input-income {{
      background: rgba(170, 210, 230, 0.48);
      color: #0a3040;
    }}
    body.office-mode .monthly-edit-float__table tr.mef-row--daily-input td {{
      background: rgba(180, 220, 200, 0.45) !important;
    }}
    body.office-mode .monthly-edit-float__table tr.mef-row--daily-input.mef-row--input-income td {{
      background: rgba(170, 210, 230, 0.48) !important;
    }}
"""

CREATE_INITIAL_OLD = re.compile(
    r"      function createInitialRowsIfNeeded\(\) \{[\s\S]*?\n      \}",
    re.MULTILINE,
)

CREATE_INITIAL_NEW = """      function createInitialRowsIfNeeded() {
        syncSectionFromCatalog(state.incomeItems, catalogIncomeDefs());
        syncSectionFromCatalog(state.fixedItems, catalogFixedDefs());
        syncSectionFromCatalog(state.variableItems, catalogVariableDefs());
        if (state.memoItems.length === 0)
          state.memoItems.push(makeRow('memo', 'メモ1', 'Memo 1', { editableLabel: true, deletable: true }));
      }"""

PRIMARY_SALES_OLD = re.compile(
    r"      function primarySalesRowId\(\) \{[\s\S]*?\n      \}",
    re.MULTILINE,
)

PRIMARY_SALES_NEW = """      function primarySalesRowId() {
        createInitialRowsIfNeeded();
        if (PL_CATALOG_BY_ID.store_sales) return 'store_sales';
        var items = state.incomeItems || [];
        if (!items.length) return null;
        return items[0].lineId || items[0].id;
      }"""

ADD_ROW_OLD = """      function addRow(section) {
        if (section === 'income') state.incomeItems.push(makeRow('money', '副収入', 'Side income', { editableLabel: true, deletable: true }));
        if (section === 'fixed') state.fixedItems.push(makeRow('money', '固定費項目', 'Fixed item', { editableLabel: true, deletable: true }));
        if (section === 'variable')
          state.variableItems.push(makeRow('money', '変動費項目', 'Variable item', { editableLabel: true, deletable: true }));
        if (section === 'memo')
          state.memoItems.push(makeRow('memo', 'メモ', 'Memo', { editableLabel: true, deletable: true }));
      }"""

ADD_ROW_NEW = """      function addRow(section) {
        if (section === 'memo')
          state.memoItems.push(makeRow('memo', 'メモ', 'Memo', { editableLabel: true, deletable: true }));
      }"""

REMOVE_ROW_OLD = """      function removeRow(section) {
        if (section === 'income' && state.incomeItems.length > 1) state.incomeItems.pop();
        if (section === 'fixed' && state.fixedItems.length > 1) state.fixedItems.pop();
        if (section === 'variable' && state.variableItems.length > 1) state.variableItems.pop();
        if (section === 'memo' && state.memoItems.length > 1) state.memoItems.pop();
      }"""

REMOVE_ROW_NEW = """      function removeRow(section) {
        if (section === 'memo' && state.memoItems.length > 1) state.memoItems.pop();
      }"""


def patch_current_rows(text: str) -> str:
    text = text.replace(
        """          section: 'income',
          plusminus: 'income',
          autoCalc: true""",
        """          section: 'income',
          autoCalc: true""",
    )
    text = text.replace(
        """          section: 'fixed',
          plusminus: 'fixed'""",
        """          section: 'fixed'""",
    )
    text = text.replace(
        """          section: 'variable',
          plusminus: 'variable'""",
        """          section: 'variable'""",
    )
    return text


def patch_create_label_row(text: str) -> str:
    old = """        if (item.rowRef && item.rowRef.editableLabel) {
          var btnEdit = document.createElement('button');
          btnEdit.type = 'button';
          btnEdit.className = 'monthly-edit-float__label-edit';
          btnEdit.textContent = '✎';
          btnEdit.setAttribute('data-action', 'edit-label');
          btnEdit.setAttribute('data-row-id', item.rowRef.id);
          btnEdit.setAttribute('aria-label', t('費目名を編集', 'Edit label'));
          main.appendChild(btnEdit);
        }
        rowEl.appendChild(main);"""
    new = """        if (item.rowRef && item.rowRef.editableLabel) {
          var btnEdit = document.createElement('button');
          btnEdit.type = 'button';
          btnEdit.className = 'monthly-edit-float__label-edit';
          btnEdit.textContent = '✎';
          btnEdit.setAttribute('data-action', 'edit-label');
          btnEdit.setAttribute('data-row-id', item.rowRef.id);
          btnEdit.setAttribute('aria-label', t('費目名を編集', 'Edit label'));
          main.appendChild(btnEdit);
        }
        if (item.dailyInput) rowEl.classList.add('monthly-edit-float__label-row--daily-input');
        else if (item.plReadonly) rowEl.classList.add('monthly-edit-float__label-row--pl-readonly');
        rowEl.appendChild(main);"""
    if old not in text:
        # Already patched variant (without edit button) -> upgrade to with-button variant.
        old2 = """        if (item.dailyInput) rowEl.classList.add('monthly-edit-float__label-row--daily-input');
        else if (item.plReadonly) rowEl.classList.add('monthly-edit-float__label-row--pl-readonly');
        rowEl.appendChild(main);"""
        if old2 not in text:
            raise ValueError("createLabelRow patch miss")
        return text.replace(old2, new, 1)
    return text.replace(old, new, 1)


def patch_build_grid(text: str) -> str:
    old_agg = """            if (r.id === 'totalSales') labelInfo.controls = { section: 'income', plusminus: 'income' };
            if (r.id === 'fixed') labelInfo.controls = { section: 'fixed', plusminus: 'fixed' };
            if (r.id === 'expected') labelInfo.controls = { section: 'variable', plusminus: 'variable' };
            if (r.id === 'memoHead') labelInfo.controls = { section: 'memo', plusminus: 'memo' };"""
    new_agg = """            if (r.id === 'totalSales') labelInfo.controls = { section: 'income' };
            if (r.id === 'fixed') labelInfo.controls = { section: 'fixed' };
            if (r.id === 'expected') labelInfo.controls = { section: 'variable' };
            if (r.id === 'memoHead') labelInfo.controls = { section: 'memo', plusminus: 'memo' };"""
    if old_agg not in text:
        raise ValueError("aggregate controls patch miss")
    text = text.replace(old_agg, new_agg, 1)
    old = """          } else if (r.type === 'moneyRow' || r.type === 'moneyStatic' || r.type === 'percent') {
            if (r.type === 'moneyRow') {
              labelInfo.label = rowLabel(r.row);
              labelInfo.rowRef = r.row;
              labelInfo.sub = r.section !== 'income';
              labelInfo.manualInput = true;
            } else {"""
    new = """          } else if (r.type === 'moneyRow' || r.type === 'moneyStatic' || r.type === 'percent') {
            if (r.type === 'moneyRow') {
              labelInfo.label = rowLabel(r.row);
              labelInfo.rowRef = r.row;
              labelInfo.sub = r.section !== 'income';
              labelInfo.dailyInput = !!r.row.mepEditable;
              labelInfo.plReadonly = !r.row.mepEditable;
              labelInfo.manualInput = !!r.row.mepEditable;
              if (r.row.mepEditable) tr.classList.add('mef-row--daily-input');
              else tr.classList.add('mef-row--pl-readonly');
            } else {"""
    if old not in text:
        raise ValueError("buildGrid label patch miss")
    text = text.replace(old, new, 1)

    old2 = """              } else if (r.type === 'moneyRow') {
                inp.value = fmtMoney(readValue(r.row.id, iso));
                inp.setAttribute('data-action', 'money-input');
                inp.setAttribute('data-row-id', r.row.id);
                inp.setAttribute('data-iso', iso);
                inp.setAttribute('title', manualInputHint());
              } else if (r.autoCalc) {"""
    new2 = """              } else if (r.type === 'moneyRow') {
                inp.value = fmtMoney(readValue(r.row.id, iso));
                inp.setAttribute('data-action', 'money-input');
                inp.setAttribute('data-row-id', r.row.id);
                inp.setAttribute('data-iso', iso);
                if (r.row.mepEditable) {
                  inp.setAttribute('title', manualInputHint());
                } else {
                  inp.disabled = true;
                  inp.readOnly = true;
                  inp.setAttribute('title', t('PL表で月次入力', 'Enter monthly on PL table'));
                }
              } else if (r.autoCalc) {"""
    if old2 not in text:
        raise ValueError("buildGrid input patch miss")
    return text.replace(old2, new2, 1)


def patch_total_sales_exclude_food_drink(text: str) -> str:
    """Food/Drink は Store 内訳のため Total Sales 合算から除外。冪等。"""
    if "function isTotalSalesIncomeRow(" in text:
        return text
    old = """      function aggregateValue(id, iso) {
        if (id === 'totalSales') return sumRows(state.incomeItems, iso);
        if (id === 'fixed') return sumRows(state.fixedItems, iso);
        if (id === 'expected') return sumRows(state.variableItems, iso);
        if (id === 'totalExpenses') return aggregateValue('fixed', iso) + aggregateValue('expected', iso);
        if (id === 'profit') return aggregateValue('totalSales', iso) - aggregateValue('totalExpenses', iso);
        return 0;
      }"""
    new = """      function isTotalSalesIncomeRow(row) {
        if (!row) return false;
        var lid = row.lineId || row.id;
        return lid === 'store_sales' || lid === 'sales_a' || lid === 'sales_b';
      }
      function sumTotalSalesIncome(iso) {
        var total = 0;
        (state.incomeItems || []).forEach(function (r) {
          if (!isTotalSalesIncomeRow(r)) return;
          total += readValue(r.id, iso);
        });
        return total;
      }
      function aggregateValue(id, iso) {
        /* Food/Drink は Store の内訳。総売上(Store+A+B)には含めない */
        if (id === 'totalSales') return sumTotalSalesIncome(iso);
        if (id === 'fixed') return sumRows(state.fixedItems, iso);
        if (id === 'expected') return sumRows(state.variableItems, iso);
        if (id === 'totalExpenses') return aggregateValue('fixed', iso) + aggregateValue('expected', iso);
        if (id === 'profit') return aggregateValue('totalSales', iso) - aggregateValue('totalExpenses', iso);
        return 0;
      }"""
    if old not in text:
        raise ValueError("totalSales exclude food/drink patch miss")
    return text.replace(old, new, 1)


def patch_build_grid_food_drink_auto(text: str) -> str:
    """Phase 2: drink_sales (mepAutoCalc) を AUTO CALC 表示にする。冪等。"""
    if "r.row.mepAutoCalc" in text and "computeDrinkSalesValue" in text:
        return text
    old_label = """            if (r.type === 'moneyRow') {
              labelInfo.label = rowLabel(r.row);
              labelInfo.rowRef = r.row;
              labelInfo.sub = r.section !== 'income';
              labelInfo.dailyInput = !!r.row.mepEditable;
              labelInfo.plReadonly = !r.row.mepEditable;
              labelInfo.manualInput = !!r.row.mepEditable;
              if (r.row.mepEditable) tr.classList.add('mef-row--daily-input');
              else tr.classList.add('mef-row--pl-readonly');
            } else {"""
    new_label = """            if (r.type === 'moneyRow') {
              labelInfo.label = rowLabel(r.row);
              labelInfo.rowRef = r.row;
              labelInfo.sub = r.section !== 'income';
              if (r.row.mepAutoCalc) {
                labelInfo.autoCalc = true;
                labelInfo.autoCalcTitle = typeof drinkSalesAutoCalcHint === 'function'
                  ? drinkSalesAutoCalcHint()
                  : t('店舗売上 − フード売上（自動）', 'Store − Food (auto)');
                labelInfo.dailyInput = false;
                labelInfo.plReadonly = false;
                labelInfo.manualInput = false;
              } else {
                labelInfo.dailyInput = !!r.row.mepEditable;
                labelInfo.plReadonly = !r.row.mepEditable;
                labelInfo.manualInput = !!r.row.mepEditable;
                if (r.row.mepEditable) tr.classList.add('mef-row--daily-input');
                else tr.classList.add('mef-row--pl-readonly');
              }
            } else {"""
    if old_label not in text:
        raise ValueError("food/drink auto label patch miss")
    text = text.replace(old_label, new_label, 1)

    # Current HTML may already have the mepEditable title branch from Phase1 catalog apply.
    old_input_a = """              } else if (r.type === 'moneyRow') {
                inp.value = fmtMoney(readValue(r.row.id, iso));
                inp.setAttribute('data-action', 'money-input');
                inp.setAttribute('data-row-id', r.row.id);
                inp.setAttribute('data-iso', iso);
                if (r.row.mepEditable) {
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
                }
              } else if (r.autoCalc) {"""
    old_input_b = """              } else if (r.type === 'moneyRow') {
                inp.value = fmtMoney(readValue(r.row.id, iso));
                inp.setAttribute('data-action', 'money-input');
                inp.setAttribute('data-row-id', r.row.id);
                inp.setAttribute('data-iso', iso);
                if (r.row.mepEditable) {
                  inp.setAttribute('title', manualInputHint());
                } else {
                  inp.disabled = true;
                  inp.readOnly = true;
                  inp.setAttribute('title', t('PL表で月次入力', 'Enter monthly on PL table'));
                }
              } else if (r.autoCalc) {"""
    new_input = """              } else if (r.type === 'moneyRow') {
                if (r.row.mepAutoCalc) {
                  var drinkVal = typeof computeDrinkSalesValue === 'function'
                    ? computeDrinkSalesValue(iso)
                    : Math.max(
                        0,
                        Math.round(Number(readValue(primarySalesRowId() || 'store_sales', iso)) || 0) -
                          Math.round(Number(readValue('food_sales', iso)) || 0)
                      );
                  inp.value = fmtMoney(drinkVal);
                  inp.disabled = true;
                  inp.readOnly = true;
                  inp.setAttribute(
                    'title',
                    typeof drinkSalesAutoCalcHint === 'function'
                      ? drinkSalesAutoCalcHint()
                      : t('店舗売上 − フード売上（自動）', 'Store − Food (auto)')
                  );
                } else {
                  inp.value = fmtMoney(readValue(r.row.id, iso));
                  inp.setAttribute('data-action', 'money-input');
                  inp.setAttribute('data-row-id', r.row.id);
                  inp.setAttribute('data-iso', iso);
                  if (r.row.mepEditable) {
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
                  }
                }
              } else if (r.autoCalc) {"""
    if old_input_a in text:
        text = text.replace(old_input_a, new_input, 1)
    elif old_input_b in text:
        text = text.replace(old_input_b, new_input, 1)
    else:
        raise ValueError("food/drink auto input patch miss")
    return text


def patch_hydrate_income_on_year_context(text: str) -> str:
    """Year 切替時に dailyIncome (food 等) を rowValueById へ復帰。"""
    needle = """      function onMepYearContextChanged(year) {
        createInitialRowsIfNeeded();
        loadMepFromYearStore(year);
        if (typeof syncMonthlySalesFromAnnualStoreForMonth === 'function') {
          syncMonthlySalesFromAnnualStoreForMonth();
        }
        if (typeof syncBizDayFromAnnualStoreForMonth === 'function') {
          syncBizDayFromAnnualStoreForMonth();
        }
      }"""
    repl = """      function onMepYearContextChanged(year) {
        createInitialRowsIfNeeded();
        loadMepFromYearStore(year);
        if (typeof hydrateMepIncomeStreamsFromStore === 'function') {
          hydrateMepIncomeStreamsFromStore(year);
        }
        if (typeof syncMonthlySalesFromAnnualStoreForMonth === 'function') {
          syncMonthlySalesFromAnnualStoreForMonth();
        }
        if (typeof syncBizDayFromAnnualStoreForMonth === 'function') {
          syncBizDayFromAnnualStoreForMonth();
        }
      }"""
    if "hydrateMepIncomeStreamsFromStore(year)" in text:
        return text
    if needle not in text:
        # Dual-injected blocks: replace all occurrences
        if "function onMepYearContextChanged(year)" not in text:
            raise ValueError("onMepYearContextChanged missing")
        text2 = text.replace(
            """        loadMepFromYearStore(year);
        if (typeof syncMonthlySalesFromAnnualStoreForMonth === 'function') {
          syncMonthlySalesFromAnnualStoreForMonth();
        }""",
            """        loadMepFromYearStore(year);
        if (typeof hydrateMepIncomeStreamsFromStore === 'function') {
          hydrateMepIncomeStreamsFromStore(year);
        }
        if (typeof syncMonthlySalesFromAnnualStoreForMonth === 'function') {
          syncMonthlySalesFromAnnualStoreForMonth();
        }""",
        )
        if text2 == text:
            raise ValueError("hydrate year-context patch miss")
        return text2
    return text.replace(needle, repl)


def inject_sync(text: str) -> str:
    if SYNC_MARKER in text:
        text = re.sub(
            re.escape(SYNC_MARKER) + r"[\s\S]*?window\.addEventListener\('pl-expense-label-changed', refreshExpenseCatalogFromPl\);\n",
            SYNC_BLOCK.rstrip() + "\n",
            text,
            count=1,
        )
    else:
        anchor = "      loadSummaryCollapsed();\n      initEditPage();"
        if anchor not in text:
            raise ValueError("initEditPage anchor missing")
        text = text.replace(anchor, SYNC_BLOCK.rstrip() + "\n\n" + anchor, 1)
    return text


def inject_catalog(text: str) -> str:
    if CATALOG_MARKER in text:
        # Include trailing duplicate upsert helpers left by older inject runs.
        text = re.sub(
            re.escape(CATALOG_MARKER)
            + r"[\s\S]*?function syncSectionFromCatalog[\s\S]*?\n      \}\n"
            + r"(?:      function upsertPlIncomeLabelsFromState\(\) \{[\s\S]*?\n      \}\n)*",
            CATALOG_BLOCK.rstrip() + "\n",
            text,
            count=1,
        )
    else:
        anchor = "      var state = {"
        if anchor not in text:
            raise ValueError("state anchor missing")
        pos = text.find("      };\n", text.find(anchor))
        if pos < 0:
            raise ValueError("state block end missing")
        pos += len("      };\n")
        text = text[:pos] + "\n" + CATALOG_BLOCK + text[pos:]
    return text


def inject_css(text: str) -> str:
    if CSS_MARKER in text:
        text = re.sub(
            re.escape(CSS_MARKER) + r"[\s\S]*?body\.office-mode \.monthly-edit-float__table tr\.mef-row--daily-input td \{[\s\S]*?\n    \}\n",
            CSS_BLOCK.rstrip() + "\n",
            text,
            count=1,
        )
    else:
        anchor = "    .monthly-edit-float__label-row {"
        if anchor not in text:
            raise ValueError("CSS anchor missing")
        text = text.replace(anchor, CSS_BLOCK + anchor, 1)
    return text


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_catalog(text)
    text = inject_css(text)
    text = inject_sync(text)
    text, n1 = CREATE_INITIAL_OLD.subn(CREATE_INITIAL_NEW, text, count=1)
    if n1 != 1 and "syncSectionFromCatalog" not in text:
        raise ValueError(f"createInitialRowsIfNeeded patch miss in {path}")
    text, n2 = PRIMARY_SALES_OLD.subn(PRIMARY_SALES_NEW, text, count=1)
    if n2 != 1 and "PL_CATALOG_BY_ID.store_sales" not in text:
        raise ValueError(f"primarySalesRowId patch miss in {path}")
    if ADD_ROW_OLD in text:
        text = text.replace(ADD_ROW_OLD, ADD_ROW_NEW, 1)
    if REMOVE_ROW_OLD in text:
        text = text.replace(REMOVE_ROW_OLD, REMOVE_ROW_NEW, 1)
    if "labelInfo.dailyInput" not in text:
        text = patch_current_rows(text)
        text = patch_build_grid(text)
    text = patch_build_grid_food_drink_auto(text)
    text = patch_hydrate_income_on_year_context(text)
    text = patch_total_sales_exclude_food_drink(text)
    text = patch_create_label_row(text)
    commit_with_upsert = (
        "              markDirty();\n"
        "              if (typeof upsertPlIncomeLabelsFromState === 'function') {\n"
        "                upsertPlIncomeLabelsFromState();\n"
        "              }\n"
        "            }\n            buildGrid();"
    )
    commit_bare = "              markDirty();\n            }\n            buildGrid();"
    if commit_with_upsert not in text and commit_bare in text:
        text = text.replace(commit_bare, commit_with_upsert, 1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    for target in TARGETS:
        patch_file(target)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""MEP: 収入=シアン / 支出=緑の手入力トーン + 静的入力行を緑化相当、トグル名明確化。
PL: 収入・総支出の縦ラベルセルのみ同色。
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]
PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
]

CSS_MARKER = "/* PL-MEP-DAILY-INPUT-STYLE */"
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

PL_CSS_MARKER = "/* PL-INCOME-EXPENSE-MAJOR-TONE */"
PL_CSS_BLOCK = f"""    {PL_CSS_MARKER}
    body:not(.office-mode) .pl-table--labels .pl-v-major[data-pl-section="income"],
    body:not(.office-mode) .pl-table--labels .pl-data-row--income > .pl-h-label {{
      background: rgba(18, 68, 96, 0.72);
    }}
    body:not(.office-mode) .pl-table--labels .pl-v-major[data-pl-section="expenses"],
    body:not(.office-mode) .pl-table--labels .pl-data-row--expenses > .pl-h-label {{
      background: rgba(20, 72, 52, 0.72);
    }}
    body.office-mode .pl-table--labels .pl-v-major[data-pl-section="income"],
    body.office-mode .pl-table--labels .pl-data-row--income > .pl-h-label {{
      background: rgba(170, 210, 230, 0.55);
    }}
    body.office-mode .pl-table--labels .pl-v-major[data-pl-section="expenses"],
    body.office-mode .pl-table--labels .pl-data-row--expenses > .pl-h-label {{
      background: rgba(180, 220, 200, 0.55);
    }}
"""


def replace_css_block(text: str) -> str:
    pat = re.compile(
        re.escape(CSS_MARKER)
        + r"[\s\S]*?body\.office-mode \.monthly-edit-float__table tr\.mef-row--daily-input td \{[\s\S]*?\n    \}\n"
        + r"(?:    body\.office-mode \.monthly-edit-float__table tr\.mef-row--daily-input\.mef-row--input-income td \{[\s\S]*?\n    \}\n)?"
    )
    if not pat.search(text):
        raise SystemExit("MEP daily-input CSS block not found")
    return pat.sub(CSS_BLOCK, text, count=1)


def patch_blocked_selector(text: str) -> str:
    old = (
        ".monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table tr.mef-row--daily-input td .monthly-edit-float__input,\n"
        "    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table .monthly-edit-float__cb[data-action='bizday-toggle'] {"
    )
    new = (
        ".monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table tr.mef-row--sales-path td .monthly-edit-float__input,\n"
        "    .monthly-edit-float--daily-sales-path-blocked .monthly-edit-float__table .monthly-edit-float__cb[data-action='bizday-toggle'] {"
    )
    if old not in text:
        if "mef-row--sales-path td .monthly-edit-float__input" in text:
            return text
        raise SystemExit("blocked selector not found")
    return text.replace(old, new, 1)


def patch_label_row_classes(text: str) -> str:
    old = (
        "        if (item.dailyInput) rowEl.classList.add('monthly-edit-float__label-row--daily-input');\n"
        "        else if (item.plReadonly) rowEl.classList.add('monthly-edit-float__label-row--pl-readonly');"
    )
    new = (
        "        if (item.dailyInput) {\n"
        "          rowEl.classList.add('monthly-edit-float__label-row--daily-input');\n"
        "          if (item.inputTone === 'income') {\n"
        "            rowEl.classList.add('monthly-edit-float__label-row--input-income');\n"
        "          }\n"
        "        } else if (item.plReadonly) {\n"
        "          rowEl.classList.add('monthly-edit-float__label-row--pl-readonly');\n"
        "        }"
    )
    if new.strip() in text:
        return text
    if old not in text:
        raise SystemExit("label row class assign not found")
    return text.replace(old, new, 1)


def patch_money_row_build(text: str) -> str:
    """Attach income/expense tone + sales-path; mark static manual rows as income input."""
    old = """            if (r.type === 'moneyRow') {
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
            } else {
              labelInfo.label = useJa ? r.labelJa : r.labelEn;
              labelInfo.sub = !!r.sub;
              labelInfo.autoCalc = !!r.autoCalc;
              if (r.autoCalcTitle) labelInfo.autoCalcTitle = r.autoCalcTitle;
              if (!r.autoCalc) labelInfo.manualInput = true;
            }"""
    new = """            if (r.type === 'moneyRow') {
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
                if (r.row.mepEditable) {
                  var incomeTone = r.section === 'income';
                  labelInfo.inputTone = incomeTone ? 'income' : 'expense';
                  tr.classList.add('mef-row--daily-input');
                  if (incomeTone) {
                    tr.classList.add('mef-row--input-income');
                    tr.classList.add('mef-row--sales-path');
                  }
                } else {
                  tr.classList.add('mef-row--pl-readonly');
                }
              }
            } else {
              labelInfo.label = useJa ? r.labelJa : r.labelEn;
              labelInfo.sub = !!r.sub;
              labelInfo.autoCalc = !!r.autoCalc;
              if (r.autoCalcTitle) labelInfo.autoCalcTitle = r.autoCalcTitle;
              if (!r.autoCalc) {
                labelInfo.manualInput = true;
                labelInfo.dailyInput = true;
                labelInfo.inputTone = 'income';
                labelInfo.plReadonly = false;
                tr.classList.add('mef-row--daily-input');
                tr.classList.add('mef-row--input-income');
              }
            }"""
    if "mef-row--input-income" in text and "labelInfo.inputTone = incomeTone" in text:
        return text
    if old not in text:
        raise SystemExit("moneyRow/moneyStatic build block not found")
    return text.replace(old, new, 1)


def patch_sales_blocked_on_build(text: str) -> str:
    """Only gate sales-path income catalog rows; static inputs stay enabled."""
    old = """                  if (r.row.mepEditable) {
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
                  } else {"""
    new = """                  if (r.row.mepEditable) {
                    if (r.section === 'income') {
                      inp.setAttribute('data-mep-sales-path', '1');
                    }
                    var salesBlocked =
                      r.section === 'income' &&
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
                  } else {"""
    if "data-mep-sales-path" in text and "r.section === 'income' &&" in text:
        return text
    if old not in text:
        raise SystemExit("salesBlocked build block not found")
    return text.replace(old, new, 1)


def patch_money_input_handler(text: str) -> str:
    old = """        } else if (action === 'money-input') {
          var rowId = target.getAttribute('data-row-id');
          var iso2 = target.getAttribute('data-iso');
          if (window.KpiYearStore && !KpiYearStore.canWriteDailySalesFrom('mep', iso2)) {
            buildGrid();
            return;
          }"""
    new = """        } else if (action === 'money-input') {
          var rowId = target.getAttribute('data-row-id');
          var iso2 = target.getAttribute('data-iso');
          var salesPathOnly =
            target.getAttribute('data-mep-sales-path') === '1' ||
            (MEF_STATIC_INPUT_IDS.indexOf(rowId) < 0 &&
              state.incomeItems.some(function (it) {
                return it && (it.id === rowId || it.lineId === rowId) && !!it.mepEditable && !it.mepAutoCalc;
              }));
          if (
            salesPathOnly &&
            window.KpiYearStore &&
            !KpiYearStore.canWriteDailySalesFrom('mep', iso2)
          ) {
            buildGrid();
            return;
          }"""
    if "salesPathOnly" in text:
        return text
    if old not in text:
        raise SystemExit("money-input handler not found")
    return text.replace(old, new, 1)


def patch_toggle_labels(text: str, *, is_ja: bool) -> str:
    if is_ja:
        reps = [
            (
                'aria-label="日次売上の入力経路"',
                'aria-label="売上入力の経路（Annual / Monthly）"',
            ),
            (
                '<p class="kpi-daily-input-path__title">編集</p>',
                '<p class="kpi-daily-input-path__title">売上入力</p>',
            ),
            (
                'aria-label="日次売上を Annual と Monthly で切り替え"',
                'aria-label="売上入力を Annual と Monthly で切り替え"',
            ),
        ]
    else:
        reps = [
            (
                'aria-label="Daily sales input path"',
                'aria-label="Sales input path (Annual / Monthly)"',
            ),
            (
                '<p class="kpi-daily-input-path__title">Edit</p>',
                '<p class="kpi-daily-input-path__title">Sales Input</p>',
            ),
            (
                'aria-label="Switch daily sales between Annual and Monthly"',
                'aria-label="Switch sales input between Annual and Monthly"',
            ),
        ]
    for a, b in reps:
        if b in text:
            continue
        if a not in text:
            # EN page may already use different strings; soft-skip
            continue
        text = text.replace(a, b, 1)
    return text


def patch_mep(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_ja = "/en/" not in str(path).replace("\\", "/")
    text = replace_css_block(text)
    text = patch_blocked_selector(text)
    text = patch_label_row_classes(text)
    text = patch_money_row_build(text)
    text = patch_sales_blocked_on_build(text)
    text = patch_money_input_handler(text)
    text = patch_toggle_labels(text, is_ja=is_ja)
    path.write_text(text, encoding="utf-8")
    print(f"patched MEP: {path}")


def patch_pl(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if PL_CSS_MARKER in text:
        text = re.sub(
            re.escape(PL_CSS_MARKER)
            + r"[\s\S]*?body\.office-mode \.pl-table--labels \.pl-v-major--expenses(?:,\n    body\.office-mode \.pl-table--labels \.pl-data-row--expenses > \.pl-h-label)? \{[\s\S]*?\n    \}\n",
            PL_CSS_BLOCK,
            text,
            count=1,
        )
    else:
        anchor = "    .pl-table--v1 .pl-v-major--expenses {"
        if anchor not in text:
            raise SystemExit(f"PL anchor not found: {path}")
        text = text.replace(anchor, PL_CSS_BLOCK + "\n" + anchor, 1)
    path.write_text(text, encoding="utf-8")
    print(f"patched PL: {path}")


def sync_apply_mep_pl_catalog_css() -> None:
    path = ROOT / "scripts" / "apply_mep_pl_catalog.py"
    text = path.read_text(encoding="utf-8")
    if "label-row--input-income" in text:
        print(f"catalog script already has income tone: {path}")
        return
    # Best-effort: replace CSS_BLOCK assignment if present
    m = re.search(
        r'CSS_BLOCK = f"""    \{CSS_MARKER\}[\s\S]*?body\.office-mode \.monthly-edit-float__table tr\.mef-row--daily-input td \{\{[\s\S]*?\n    \}\}\n"""',
        text,
    )
    if not m:
        print(f"skip catalog CSS sync (pattern miss): {path}")
        return
    # Escape for Python f-string source: {{ -> need in file as {{
    src_block = CSS_BLOCK.replace("{", "{{").replace("}", "}}")
    # But CSS_MARKER line used {CSS_MARKER} in f-string originally
    src_block = src_block.replace("{{/* PL-MEP-DAILY-INPUT-STYLE */}}", "{CSS_MARKER}")
    # Our CSS_BLOCK already has the marker expanded; rebuild properly
    src_block = (
        'CSS_BLOCK = f"""    {CSS_MARKER}\n'
        + "\n".join(CSS_BLOCK.splitlines()[1:]).replace("{", "{{").replace("}", "}}")
        + '\n"""'
    )
    text = text[: m.start()] + src_block + text[m.end() :]
    path.write_text(text, encoding="utf-8")
    print(f"synced catalog CSS: {path}")


def main() -> None:
    for p in MEP_PAGES:
        if not p.is_file():
            raise SystemExit(f"missing {p}")
        patch_mep(p)
    for p in PL_PAGES:
        if not p.is_file():
            raise SystemExit(f"missing {p}")
        patch_pl(p)
    sync_apply_mep_pl_catalog_css()


if __name__ == "__main__":
    main()

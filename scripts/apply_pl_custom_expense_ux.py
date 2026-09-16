#!/usr/bin/env python3
"""Unit 5B-2: patch PL custom UX + MEP non-restaurant embed only."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PL_PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]
MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

WARN = {
    "app/profit/pl/index.html": (
        "分析カテゴリが未設定です",
        "この費目は分析カテゴリが未設定です。支出合計・利益計算にはすでに反映されていますが、カテゴリ別分析の精度を高めるため、属性を設定してください。",
    ),
    "en/app/profit/pl/index.html": (
        "Analysis category is not set",
        "This line has no analysis category yet. It is already included in expense totals and profit, but setting an attribute will improve category analysis.",
    ),
    "zh-tw/app/profit/pl/index.html": (
        "尚未設定分析類別",
        "此科目尚未設定分析類別。金額已計入支出合計與利益，但設定屬性可提高類別分析的精確度。",
    ),
}

PROMPT_OLD = """      function promptAddLine(bucket) {
        if (bucket === 'fixed') {
          openExpenseAttributeModal({
            bucket: 'fixed',
            title: attributeAddTitle,
            mode: 'add',
          }).then(function (attrId) {
            if (!attrId) return;
            addLine(bucket, 'monthly', attrId);
          });
          return;
        }
        if (bucket !== 'variable') return;
        openExpenseAttributeModal({
          bucket: 'variable',
          title: attributeVariableAddTitle,
          mode: 'add',
        }).then(function (attrId) {
          if (!attrId) return;
          /* 入力元は続く統合モーダル（ラベル編集）で選ぶ */
          addLine(bucket, 'monthly', attrId);
        });
      }"""

PROMPT_NEW = """      function promptAddLine(bucket) {
        if (bucket !== 'fixed' && bucket !== 'variable') return;
        openCreateLineLabelModal(bucket);
      }"""

ADD_ATTR_OLD = """        if (bucket === 'fixed' && expenseAttribute) {
          entry.expenseAttribute = expenseAttribute;
        }
        if (bucket === 'variable' && expenseAttribute) {
          entry.expenseAttribute = expenseAttribute;
        }"""

ADD_ATTR_NEW = """        if (expenseAttribute) {
          entry.expenseAttribute = expenseAttribute;
        } else {
          entry.expenseAttribute = UNCLASSIFIED_ATTR;
        }"""

LABELCELL_OLD = """          editableLabelSpan(line.lineId, labelText(line)) +
          rowAttributeBtn(line) +"""

LABELCELL_NEW = """          editableLabelSpan(line.lineId, labelText(line)) +
          rowUnclassifiedWarn(line) +
          rowAttributeBtn(line) +"""

CLICK_OLD = """        if (action === 'edit-attribute') {
          editLineAttribute(btn.getAttribute('data-line-id'));
          return;
        }"""

CLICK_NEW = """        if (action === 'edit-attribute') {
          editLineAttribute(btn.getAttribute('data-line-id'));
          return;
        }
        if (action === 'unclassified-warn') {
          editLineAttribute(btn.getAttribute('data-line-id'));
          return;
        }"""

COMMIT_OLD = """      function commitLabelEdit() {
        if (!pendingLabelEdit || !labelEditInput) return false;
        var lineId = pendingLabelEdit.lineId;"""

COMMIT_NEW = """      function commitLabelEdit() {
        if (!pendingLabelEdit || !labelEditInput) return false;
        if (pendingLabelEdit.createBucket) {
          return commitCreateLineFromLabel();
        }
        var lineId = pendingLabelEdit.lineId;"""

IMPORT_OLD = """          isDefault: false,
          active: true,
          sortOrder: maxOrder + 1,
        });
        saveLines(lines);
        renderExpenseDetail();
        window.dispatchEvent(
          new CustomEvent('pl-expense-line-added', { detail: { lineId: lineId } })
        );
        return lineId;
      }"""

IMPORT_NEW = """          isDefault: false,
          active: true,
          sortOrder: maxOrder + 1,
          expenseAttribute: UNCLASSIFIED_ATTR,
        });
        saveLines(lines);
        renderExpenseDetail();
        window.dispatchEvent(
          new CustomEvent('pl-expense-line-added', { detail: { lineId: lineId } })
        );
        return lineId;
      }"""

SHOW_ATTR_OLD = """      function showAttributeChoicesForBucket(bucket) {
        if (!attributeModal) return;
        var target = bucket === 'variable' ? 'variable' : 'fixed';
        attributeModal.querySelectorAll('.pl-expense-attribute-choices').forEach(function (fs) {
          var show = fs.getAttribute('data-pl-expense-attribute-bucket') === target;
          fs.hidden = !show;
          fs.querySelectorAll('input[type="radio"]').forEach(function (inp) {
            inp.disabled = !show;
          });
        });
      }"""

HELPERS = r"""      function restaurantLikeNow() {
        if (window.KpiBusinessType && typeof window.KpiBusinessType.isRestaurantLike === 'function') {
          try {
            return window.KpiBusinessType.isRestaurantLike();
          } catch (_eLike) {}
        }
        return true;
      }

      function attributeLabel(attr) {
        if (!attr) return '';
        var lang = '';
        try {
          lang = String(document.documentElement.lang || '').toLowerCase();
        } catch (_eLang) {}
        if (lang.indexOf('zh') === 0) return attr.labelZh || attr.labelJa || attr.labelEn || attr.id;
        if (lang.indexOf('ja') === 0) return attr.labelJa || attr.labelEn || attr.id;
        return attr.labelEn || attr.labelJa || attr.id;
      }

      function allowAttributeId(attrId, bucket) {
        var id = String(attrId || '');
        if (!id || id === UNCLASSIFIED_ATTR) return false;
        var restaurant = restaurantLikeNow();
        var api = window.KpiPlExpensePresets || {};
        var restOnly = api.RESTAURANT_ONLY_ATTRIBUTES || ['food_cost', 'drink_cost'];
        var nonRestOnly = api.NON_RESTAURANT_ONLY_ATTRIBUTES || [];
        if (!restaurant && restOnly.indexOf(id) >= 0) return false;
        if (restaurant && nonRestOnly.indexOf(id) >= 0) return false;
        if (restaurant && bucket === 'variable' && id === 'occupancy') return false;
        return true;
      }

      function rebuildAttributeChoices(bucket) {
        if (!attributeModal) return;
        var api = window.KpiPlExpensePresets;
        var list = bucket === 'variable'
          ? (api && api.VARIABLE_ATTRIBUTES) || []
          : (api && api.FIXED_ATTRIBUTES) || [];
        if (!list.length) return;
        var fs = attributeModal.querySelector(
          '.pl-expense-attribute-choices[data-pl-expense-attribute-bucket="' + bucket + '"]'
        );
        if (!fs) return;
        var legend = fs.querySelector('legend');
        var legendHtml = legend ? legend.outerHTML : '';
        var html = legendHtml;
        list.forEach(function (attr) {
          if (!allowAttributeId(attr.id, bucket)) return;
          html +=
            '<label class="pl-input-source-modal__choice">' +
            '<input type="radio" name="pl-expense-attribute" value="' +
            escapeHtml(attr.id) +
            '"><span>' +
            escapeHtml(attributeLabel(attr)) +
            '</span></label>';
        });
        fs.innerHTML = html;
      }

      function showAttributeChoicesForBucket(bucket) {
        if (!attributeModal) return;
        var target = bucket === 'variable' ? 'variable' : 'fixed';
        rebuildAttributeChoices(target);
        attributeModal.querySelectorAll('.pl-expense-attribute-choices').forEach(function (fs) {
          var show = fs.getAttribute('data-pl-expense-attribute-bucket') === target;
          fs.hidden = !show;
          fs.querySelectorAll('input[type="radio"]').forEach(function (inp) {
            inp.disabled = !show;
          });
        });
      }

      function isUnclassifiedCustom(line) {
        if (!line || String(line.lineId || '').indexOf('exp_custom_') !== 0) return false;
        var a = line.expenseAttribute;
        return !a || a === UNCLASSIFIED_ATTR;
      }

      function rowUnclassifiedWarn(line) {
        if (!isUnclassifiedCustom(line)) return '';
        return (
          '<span class="pl-row-unclassified">' +
          '<button type="button" class="pl-row-unclassified__btn" data-action="unclassified-warn" data-line-id="' +
          line.lineId +
          '" title="' +
          escapeHtml(unclassifiedWarnTooltip) +
          '" aria-label="' +
          escapeHtml(unclassifiedWarnAria) +
          '">⚠</button></span>'
        );
      }

      function openCreateLineLabelModal(bucket) {
        if (!labelEditModal || !labelEditInput) {
          addLine(bucket, 'monthly', UNCLASSIFIED_ATTR);
          return;
        }
        pendingLabelEdit = { createBucket: bucket };
        labelEditInput.value = '';
        var showSource = bucket === 'variable';
        if (labelEditSource) {
          labelEditSource.hidden = !showSource;
          labelEditSource.querySelectorAll('input[type="radio"]').forEach(function (inp) {
            inp.disabled = !showSource;
          });
          if (showSource) setLabelEditSourceStyle('monthly');
        }
        labelEditModal.hidden = false;
        document.body.classList.add('pl-expense-label-edit-modal-open');
        labelEditInput.focus();
      }

      function commitCreateLineFromLabel() {
        if (!pendingLabelEdit || !pendingLabelEdit.createBucket || !labelEditInput) return false;
        var next = String(labelEditInput.value || '').replace(/\s+/g, ' ').trim();
        if (!next) {
          labelEditInput.focus();
          return false;
        }
        var bucket = pendingLabelEdit.createBucket;
        var style = 'monthly';
        if (bucket === 'variable') {
          var picked = getLabelEditSourceStyle();
          if (picked === 'daily' || picked === 'monthly') style = picked;
        }
        closeLabelEditModal();
        var lineId = addLine(bucket, style, UNCLASSIFIED_ATTR);
        var lines = loadLines();
        var line = lines.find(function (l) { return l.lineId === lineId; });
        if (line) {
          line.labelJa = next;
          line.labelEn = next;
          line.labelZh = next;
          saveLines(lines);
          renderExpenseDetail();
        }
        return true;
      }

"""

CSS_OLD = """    body.office-mode .pl-table--v1 .pl-row-attr__btn {
      border-color: #999;
      background: #f5f5f5;
      color: #111;
    }"""

CSS_NEW = """    body.office-mode .pl-table--v1 .pl-row-attr__btn {
      border-color: #999;
      background: #f5f5f5;
      color: #111;
    }
    .pl-table--v1 .pl-row-unclassified {
      display: inline-flex;
      flex-shrink: 0;
      margin-left: 4px;
    }
    .pl-table--v1 .pl-row-unclassified__btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 14px;
      height: 13px;
      margin: 0;
      padding: 0 2px;
      border: 0;
      border-radius: 2px;
      background: transparent;
      color: #e0b84a;
      font-size: 11px;
      line-height: 1;
      cursor: pointer;
    }
    body.office-mode .pl-table--v1 .pl-row-unclassified__btn {
      color: #b8860b;
    }"""

MEP_PLINE_OLD = """          labelJa: line.labelJa,
          labelEn: line.labelEn,
          editableLabel: false,"""

MEP_PLINE_NEW = """          labelJa: line.labelJa,
          labelEn: line.labelEn,
          labelZh: line.labelZh,
          editableLabel: false,"""

MEP_ROW_OLD = """          labelJa: def.labelJa,
          labelEn: def.labelEn,
          editableLabel: !!def.editableLabel,"""

MEP_ROW_NEW = """          labelJa: def.labelJa,
          labelEn: def.labelEn,
          labelZh: def.labelZh,
          editableLabel: !!def.editableLabel,"""

MEP_SYNC_OLD = """            prev.labelJa = d.labelJa;
            prev.labelEn = d.labelEn;
            prev.mepEditable = !!d.mepEditable;"""

MEP_SYNC_NEW = """            prev.labelJa = d.labelJa;
            prev.labelEn = d.labelEn;
            if (d.labelZh) prev.labelZh = d.labelZh;
            prev.mepEditable = !!d.mepEditable;"""

MEP_EMBED_OLD = """      function catalogExpenseDefsFromEmbedded(bucket) {
        if (window.KpiPlExpensePresets && !window.KpiPlExpensePresets.hasDefinedPreset()) {
          return [];
        }
        return PL_LINE_CATALOG.filter(function (e) {
          return e.bucket === bucket && e.active !== false;
        });
      }"""

MEP_EMBED_NEW = """      function catalogExpenseDefsFromEmbedded(bucket) {
        if (window.KpiPlExpensePresets) {
          if (!window.KpiPlExpensePresets.hasDefinedPreset()) return [];
          var bt = window.KpiPlExpensePresets.resolveBusinessType();
          if (bt) {
            return window.KpiPlExpensePresets.getDefaultExpenseLines(bt)
              .filter(function (line) {
                return line && line.bucket === bucket && line.active !== false;
              })
              .map(plLineToMepDef);
          }
        }
        return PL_LINE_CATALOG.filter(function (e) {
          return e.bucket === bucket && e.active !== false;
        });
      }"""


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    if new.strip() and new in text and old not in text:
        return text
    if old not in text:
        raise ValueError(f"{label} missing in {path}")
    return text.replace(old, new, 1)


def patch_pl(path: Path) -> None:
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    aria, tip = WARN[rel]
    if "var UNCLASSIFIED_ATTR = 'unclassified';" not in text:
        needle = "      var occupancyOwnedOption = "
        idx = text.find(needle)
        if idx < 0:
            raise ValueError(f"occupancyOwnedOption missing in {path}")
        end = text.find("\n", idx)
        insert = (
            "\n      var unclassifiedWarnAria = "
            + repr(aria)
            + ";\n      var unclassifiedWarnTooltip = "
            + repr(tip)
            + ";\n      var UNCLASSIFIED_ATTR = 'unclassified';"
        )
        text = text[:end] + insert + text[end:]
    if "function openCreateLineLabelModal" not in text:
        text = replace_once(text, SHOW_ATTR_OLD, HELPERS, "showAttributeChoices", path)
    text = replace_once(text, PROMPT_OLD, PROMPT_NEW, "promptAddLine", path) if PROMPT_OLD in text else text
    if "openCreateLineLabelModal(bucket)" not in text:
        raise ValueError(f"promptAddLine not patched in {path}")
    text = replace_once(text, ADD_ATTR_OLD, ADD_ATTR_NEW, "addLine attr", path) if ADD_ATTR_OLD in text else text
    if "rowUnclassifiedWarn(line)" not in text:
        text = replace_once(text, LABELCELL_OLD, LABELCELL_NEW, "labelCell", path)
    if "unclassified-warn" not in text.split("action === 'edit-attribute'", 1)[-1][:400]:
        text = replace_once(text, CLICK_OLD, CLICK_NEW, "click warn", path)
    if "pendingLabelEdit.createBucket" not in text:
        text = replace_once(text, COMMIT_OLD, COMMIT_NEW, "commitLabelEdit", path)
    if "expenseAttribute: UNCLASSIFIED_ATTR" not in text:
        text = replace_once(text, IMPORT_OLD, IMPORT_NEW, "import custom", path)
    if ".pl-row-unclassified__btn" not in text:
        text = replace_once(text, CSS_OLD, CSS_NEW, "unclassified css", path)
    path.write_text(text, encoding="utf-8")
    print(f"patched PL UX {rel}")


def patch_mep(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "KpiPlExpensePresets.resolveBusinessType" not in text:
        text = replace_once(text, MEP_EMBED_OLD, MEP_EMBED_NEW, "MEP embed", path)
    if "labelZh: line.labelZh" not in text:
        text = replace_once(text, MEP_PLINE_OLD, MEP_PLINE_NEW, "plLineToMepDef zh", path)
    if "labelZh: def.labelZh" not in text:
        text = replace_once(text, MEP_ROW_OLD, MEP_ROW_NEW, "makeCatalogRow zh", path)
    if "if (d.labelZh) prev.labelZh = d.labelZh;" not in text:
        text = replace_once(text, MEP_SYNC_OLD, MEP_SYNC_NEW, "sync labelZh", path)
    path.write_text(text, encoding="utf-8")
    print(f"patched MEP {path.relative_to(ROOT)}")


def main() -> None:
    for path in PL_PAGES:
        patch_pl(path)
    for path in MEP_PAGES:
        patch_mep(path)


if __name__ == "__main__":
    main()

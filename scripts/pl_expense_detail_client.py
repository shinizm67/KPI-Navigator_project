"""Client-side JS for PL expense detail lines (add / hide / restore / reorder)."""

from __future__ import annotations

import json


def expense_detail_client_js(
    *,
    catalog_json: str,
    mid_fixed: str,
    mid_var: str,
    add_aria: str,
    hide_aria: str,
    hide_confirm_title: str,
    hide_confirm_body: str,
    hide_confirm_ok: str,
    hide_confirm_cancel: str,
    delete_line_confirm_title: str,
    delete_line_confirm_body: str,
    delete_line_confirm_ok: str,
    line_manage_title: str,
    line_manage_empty: str,
    line_manage_restore: str,
    line_manage_close: str,
    move_up_aria: str,
    move_down_aria: str,
    new_row: str,
    edit_aria: str,
    expense_attribute_add_title: str,
    expense_attribute_variable_add_title: str,
    expense_attribute_edit_title: str,
    expense_attribute_btn_label: str,
    expense_attribute_btn_aria: str,
    expense_attr_edit_toggle: str,
    expense_attr_edit_toggle_aria: str,
    expense_attr_edit_on: str,
    expense_attr_edit_off: str,
    schema_version: int = 3,
) -> str:
    return f"""
    (function () {{
      var isJa = document.documentElement.lang === 'ja';
      var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
      var INPUT_PREFS_KEY = 'kpiNavigator.plInputSourcePrefs';
      var ATTR_EDIT_KEY = 'kpiNavigator.plExpenseAttrEditMode';
      var DEFAULT_LINES = {catalog_json};
      var midFixed = {json.dumps(mid_fixed, ensure_ascii=False)};
      var midVar = {json.dumps(mid_var, ensure_ascii=False)};
      var addAria = {json.dumps(add_aria, ensure_ascii=False)};
      var hideAria = {json.dumps(hide_aria, ensure_ascii=False)};
      var hideConfirmTitle = {json.dumps(hide_confirm_title, ensure_ascii=False)};
      var hideConfirmBodyTpl = {json.dumps(hide_confirm_body, ensure_ascii=False)};
      var hideConfirmOk = {json.dumps(hide_confirm_ok, ensure_ascii=False)};
      var hideConfirmCancel = {json.dumps(hide_confirm_cancel, ensure_ascii=False)};
      var deleteConfirmTitle = {json.dumps(delete_line_confirm_title, ensure_ascii=False)};
      var deleteConfirmBodyTpl = {json.dumps(delete_line_confirm_body, ensure_ascii=False)};
      var deleteConfirmOk = {json.dumps(delete_line_confirm_ok, ensure_ascii=False)};
      var lineManageTitle = {json.dumps(line_manage_title, ensure_ascii=False)};
      var lineManageEmpty = {json.dumps(line_manage_empty, ensure_ascii=False)};
      var lineManageRestore = {json.dumps(line_manage_restore, ensure_ascii=False)};
      var lineManageClose = {json.dumps(line_manage_close, ensure_ascii=False)};
      var moveUpAria = {json.dumps(move_up_aria, ensure_ascii=False)};
      var moveDownAria = {json.dumps(move_down_aria, ensure_ascii=False)};
      var newRowLabel = {json.dumps(new_row, ensure_ascii=False)};
      var labelEditAria = {json.dumps(edit_aria, ensure_ascii=False)};
      var attributeAddTitle = {json.dumps(expense_attribute_add_title, ensure_ascii=False)};
      var attributeVariableAddTitle = {json.dumps(expense_attribute_variable_add_title, ensure_ascii=False)};
      var attributeEditTitle = {json.dumps(expense_attribute_edit_title, ensure_ascii=False)};
      var attributeBtnLabel = {json.dumps(expense_attribute_btn_label, ensure_ascii=False)};
      var attributeBtnAria = {json.dumps(expense_attribute_btn_aria, ensure_ascii=False)};
      var attrEditOnLabel = {json.dumps(expense_attr_edit_on, ensure_ascii=False)};
      var attrEditOffLabel = {json.dumps(expense_attr_edit_off, ensure_ascii=False)};
      var block = document.getElementById('pl-expense-detail-block');
      var attrToggle = document.getElementById('pl-expense-attr-toggle');
      var modal = document.getElementById('pl-input-source-modal');
      var modalSkip = document.getElementById('pl-input-source-skip');
      var attributeModal = document.getElementById('pl-expense-attribute-modal');
      var attributeModalTitle = document.getElementById('pl-expense-attribute-modal-title');
      var hideModal = document.getElementById('pl-hide-line-modal');
      var hideModalBody = document.getElementById('pl-hide-line-modal-body');
      var hideModalTitle = document.getElementById('pl-hide-line-modal-title');
      var hideModalOk = hideModal
        ? hideModal.querySelector('[data-pl-hide-line-action="confirm"]')
        : null;
      var manageModal = document.getElementById('pl-line-manage-modal');
      var manageList = document.getElementById('pl-line-manage-list');
      var manageOpen = document.getElementById('pl-line-manage-open');
      var CATALOG_SCHEMA_VERSION = {schema_version};
      var pendingInputSource = null;
      var pendingHideLineId = null;
      var pendingHideMode = null;
      var pendingAttributePick = null;
      var INPUTSTYLE_MIGRATIONS = {{}};
      if (!block) return;

      function escapeHtml(text) {{
        return String(text)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;');
      }}

      function defaultById() {{
        var map = {{}};
        DEFAULT_LINES.forEach(function (line) {{
          map[line.lineId] = line;
        }});
        return map;
      }}

      function reconcileCatalogLines(oldLines) {{
        var defs = defaultById();
        var defaultLabelKeys = {{}};
        DEFAULT_LINES.forEach(function (d) {{
          defaultLabelKeys[d.bucket + '\\0' + String(d.labelEn || '').toLowerCase()] = true;
          defaultLabelKeys[d.bucket + '\\0' + String(d.labelJa || '')] = true;
        }});
        var out = [];
        var seenIds = {{}};
        DEFAULT_LINES.forEach(function (def) {{
          var prev = (oldLines || []).find(function (l) {{ return l.lineId === def.lineId; }});
          var line = JSON.parse(JSON.stringify(def));
          if (prev) {{
            if (typeof prev.active === 'boolean') line.active = prev.active;
            if (typeof prev.sortOrder === 'number') line.sortOrder = prev.sortOrder;
            if (prev.labelJa) line.labelJa = prev.labelJa;
            if (prev.labelEn) line.labelEn = prev.labelEn;
            if (prev.expenseAttribute) line.expenseAttribute = prev.expenseAttribute;
          }}
          if (line.expenseAttribute == null) {{
            delete line.expenseAttribute;
          }}
          out.push(line);
          seenIds[line.lineId] = true;
        }});
        (oldLines || []).forEach(function (line) {{
          if (String(line.lineId || '').indexOf('exp_custom_') !== 0) return;
          if (seenIds[line.lineId]) return;
          var keyEn = line.bucket + '\\0' + String(line.labelEn || '').toLowerCase();
          var keyJa = line.bucket + '\\0' + String(line.labelJa || '');
          if (defaultLabelKeys[keyEn] || defaultLabelKeys[keyJa]) return;
          line.isDefault = false;
          if (!line.resolvedInputStyle) {{
            line.resolvedInputStyle = line.inputStyle === 'daily' ? 'daily' : 'monthly';
          }}
          out.push(line);
          seenIds[line.lineId] = true;
        }});
        return out;
      }}

      function normalizeFixedBucketLines(lines) {{
        var changed = false;
        lines.forEach(function (line) {{
          if (line.bucket !== 'fixed') return;
          if (line.inputStyle !== 'monthly' || line.resolvedInputStyle !== 'monthly') {{
            line.inputStyle = 'monthly';
            line.resolvedInputStyle = 'monthly';
            changed = true;
          }}
        }});
        return changed;
      }}

      function mergeCatalogFromDefaults(oldLines) {{
        var lines = reconcileCatalogLines(oldLines);
        normalizeAllBucketSortOrders(lines);
        if (normalizeFixedBucketLines(lines)) {{}}
        saveLines(lines);
        return lines;
      }}

      function loadLines() {{
        try {{
          var raw = localStorage.getItem(CATALOG_KEY);
          if (raw) {{
            var parsed = JSON.parse(raw);
            if (parsed && Array.isArray(parsed.lines) && parsed.lines.length) {{
              if (parsed.schemaVersion !== CATALOG_SCHEMA_VERSION) {{
                return mergeCatalogFromDefaults(parsed.lines);
              }}
              return migrateLines(parsed.lines);
            }}
          }}
        }} catch (_e) {{}}
        var fresh = JSON.parse(JSON.stringify(DEFAULT_LINES));
        saveLines(fresh);
        return fresh;
      }}

      function migrateLines(lines) {{
        var reconciled = reconcileCatalogLines(lines);
        var defs = defaultById();
        var changed = reconciled.length !== lines.length;
        if (!changed) {{
          for (var i = 0; i < lines.length; i++) {{
            if (lines[i].lineId !== reconciled[i].lineId) {{
              changed = true;
              break;
            }}
          }}
        }}
        reconciled.forEach(function (line) {{
          var def = defs[line.lineId];
          if (!def) return;
          var prev = lines.find(function (l) {{ return l.lineId === line.lineId; }});
          if (!prev) {{
            changed = true;
            return;
          }}
          if (
            prev.isDefault !== line.isDefault ||
            prev.labelJa !== line.labelJa ||
            prev.labelEn !== line.labelEn ||
            prev.resolvedInputStyle !== line.resolvedInputStyle ||
            prev.inputStyle !== line.inputStyle ||
            prev.active !== line.active ||
            prev.expenseAttribute !== line.expenseAttribute
          ) {{
            changed = true;
          }}
        }});
        if (normalizeAllBucketSortOrders(reconciled)) changed = true;
        if (normalizeFixedBucketLines(reconciled)) changed = true;
        if (changed) saveLines(reconciled);
        return reconciled;
      }}

      function saveLines(lines) {{
        try {{
          localStorage.setItem(
            CATALOG_KEY,
            JSON.stringify({{
              lines: lines,
              schemaVersion: CATALOG_SCHEMA_VERSION,
              updatedAt: Date.now(),
            }})
          );
          window.dispatchEvent(new Event('pl-expense-catalog-changed'));
        }} catch (_e) {{}}
      }}

      function activeBucket(lines, bucket) {{
        return lines
          .filter(function (line) {{ return line.active && line.bucket === bucket; }})
          .sort(function (a, b) {{ return a.sortOrder - b.sortOrder; }});
      }}

      function ensureUniqueBucketSortOrders(lines, bucket) {{
        var bucketLines = activeBucket(lines, bucket);
        var seen = {{}};
        var hasDup = false;
        for (var i = 0; i < bucketLines.length; i++) {{
          var order = bucketLines[i].sortOrder;
          if (seen[order]) {{
            hasDup = true;
            break;
          }}
          seen[order] = true;
        }}
        if (!hasDup) return false;
        bucketLines.forEach(function (line, idx) {{
          var target = lines.find(function (l) {{ return l.lineId === line.lineId; }});
          if (target) target.sortOrder = idx;
        }});
        return true;
      }}

      function normalizeAllBucketSortOrders(lines) {{
        var changed = false;
        if (ensureUniqueBucketSortOrders(lines, 'fixed')) changed = true;
        if (ensureUniqueBucketSortOrders(lines, 'variable')) changed = true;
        return changed;
      }}

      function inactiveLines(lines) {{
        return lines
          .filter(function (line) {{ return !line.active; }})
          .sort(function (a, b) {{
            if (a.bucket !== b.bucket) return a.bucket === 'fixed' ? -1 : 1;
            return a.sortOrder - b.sortOrder;
          }});
      }}

      function isNonDefault(line) {{
        return line && line.isDefault === false;
      }}

      function rowClass(line) {{
        var s = line.resolvedInputStyle || line.inputStyle;
        if (s === 'daily') return ' pl-expense-detail-row--input-daily';
        if (s === 'monthly') return ' pl-expense-detail-row--input-monthly';
        return '';
      }}

      function loadInputPrefs() {{
        try {{
          var raw = localStorage.getItem(INPUT_PREFS_KEY);
          if (raw) {{
            var parsed = JSON.parse(raw);
            if (parsed && typeof parsed === 'object') return parsed;
          }}
        }} catch (_e) {{}}
        return {{ skipPrompt: false, lastChoice: 'monthly' }};
      }}

      function saveInputPrefs(prefs) {{
        try {{
          localStorage.setItem(INPUT_PREFS_KEY, JSON.stringify(prefs));
        }} catch (_e) {{}}
      }}

      function getSelectedInputStyle() {{
        if (!modal) return null;
        var picked = modal.querySelector('input[name="pl-input-source"]:checked');
        return picked ? picked.value : null;
      }}

      function setModalInputStyle(style) {{
        if (!modal) return;
        var radio = modal.querySelector('input[name="pl-input-source"][value="' + style + '"]');
        if (radio) radio.checked = true;
      }}

      function closeInputSourceModal() {{
        if (!modal) return;
        modal.hidden = true;
        document.body.classList.remove('pl-input-source-modal-open');
        pendingInputSource = null;
      }}

      function openInputSourceModal(opts) {{
        if (!modal) return Promise.resolve(null);
        var options = opts || {{}};
        var prefs = loadInputPrefs();
        if (options.skipPrefs && prefs.skipPrompt && prefs.lastChoice) {{
          return Promise.resolve(prefs.lastChoice);
        }}
        setModalInputStyle(options.initialStyle || prefs.lastChoice || 'monthly');
        if (modalSkip) modalSkip.checked = false;
        pendingInputSource = {{
          mode: options.mode || 'add',
          bucket: options.bucket || null,
          lineId: options.lineId || null,
          resolve: null,
        }};
        modal.hidden = false;
        document.body.classList.add('pl-input-source-modal-open');
        var primary = modal.querySelector('[data-pl-input-source-action="confirm"]');
        if (primary) primary.focus();
        return new Promise(function (resolve) {{
          pendingInputSource.resolve = resolve;
        }});
      }}

      function finishInputSourceModal(confirmed) {{
        if (!pendingInputSource) return;
        var resolve = pendingInputSource.resolve;
        closeInputSourceModal();
        if (!confirmed || !resolve) {{
          if (resolve) resolve(null);
          return;
        }}
        var style = getSelectedInputStyle();
        if (!style) {{
          resolve(null);
          return;
        }}
        var prefs = loadInputPrefs();
        prefs.lastChoice = style;
        if (modalSkip && modalSkip.checked) prefs.skipPrompt = true;
        saveInputPrefs(prefs);
        resolve(style);
      }}

      function showAttributeChoicesForBucket(bucket) {{
        if (!attributeModal) return;
        var target = bucket === 'variable' ? 'variable' : 'fixed';
        attributeModal.querySelectorAll('.pl-expense-attribute-choices').forEach(function (fs) {{
          var show = fs.getAttribute('data-pl-expense-attribute-bucket') === target;
          fs.hidden = !show;
          fs.querySelectorAll('input[type="radio"]').forEach(function (inp) {{
            inp.disabled = !show;
          }});
        }});
      }}

      function attributeTitleForBucket(bucket, mode) {{
        if (mode === 'edit') return attributeEditTitle;
        return bucket === 'variable' ? attributeVariableAddTitle : attributeAddTitle;
      }}

      function getSelectedExpenseAttribute() {{
        if (!attributeModal) return null;
        var visible = attributeModal.querySelector(
          '.pl-expense-attribute-choices:not([hidden])'
        );
        if (!visible) return null;
        var picked = visible.querySelector('input[name="pl-expense-attribute"]:checked');
        return picked ? picked.value : null;
      }}

      function setSelectedExpenseAttribute(attrId) {{
        if (!attributeModal || !attrId) return;
        var visible = attributeModal.querySelector(
          '.pl-expense-attribute-choices:not([hidden])'
        );
        if (!visible) return;
        var radio = visible.querySelector(
          'input[name="pl-expense-attribute"][value="' + attrId + '"]'
        );
        if (radio) radio.checked = true;
      }}

      function closeExpenseAttributeModal() {{
        if (!attributeModal) return;
        attributeModal.hidden = true;
        document.body.classList.remove('pl-expense-attribute-modal-open');
        pendingAttributePick = null;
      }}

      function openExpenseAttributeModal(opts) {{
        if (!attributeModal) return Promise.resolve(null);
        var options = opts || {{}};
        var bucket = options.bucket === 'variable' ? 'variable' : 'fixed';
        showAttributeChoicesForBucket(bucket);
        if (attributeModalTitle) {{
          attributeModalTitle.textContent =
            options.title || attributeTitleForBucket(bucket, options.mode || 'add');
        }}
        var initial = options.initialAttribute;
        if (initial) setSelectedExpenseAttribute(initial);
        else {{
          var visible = attributeModal.querySelector(
            '.pl-expense-attribute-choices:not([hidden])'
          );
          var first = visible
            ? visible.querySelector('input[name="pl-expense-attribute"]')
            : null;
          if (first) first.checked = true;
        }}
        attributeModal.hidden = false;
        document.body.classList.add('pl-expense-attribute-modal-open');
        var primary = attributeModal.querySelector('[data-pl-expense-attribute-action="confirm"]');
        if (primary) primary.focus();
        return new Promise(function (resolve) {{
          pendingAttributePick = {{
            resolve: resolve,
            mode: options.mode || 'add',
            bucket: bucket,
            lineId: options.lineId || null,
          }};
        }});
      }}

      function finishExpenseAttributeModal(confirmed) {{
        if (!pendingAttributePick) return;
        var resolve = pendingAttributePick.resolve;
        closeExpenseAttributeModal();
        if (!confirmed || !resolve) {{
          if (resolve) resolve(null);
          return;
        }}
        resolve(getSelectedExpenseAttribute());
      }}

      function setLineExpenseAttribute(lineId, attrId) {{
        if (!attrId) return;
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line) return;
        if (line.bucket !== 'fixed' && line.bucket !== 'variable') return;
        line.expenseAttribute = attrId;
        saveLines(lines);
        renderExpenseDetail();
      }}

      function editLineAttribute(lineId) {{
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line) return;
        if (line.bucket === 'fixed') {{
          openExpenseAttributeModal({{
            bucket: 'fixed',
            title: attributeEditTitle,
            initialAttribute: line.expenseAttribute,
            mode: 'edit',
            lineId: lineId,
          }}).then(function (attrId) {{
            if (!attrId) return;
            setLineExpenseAttribute(lineId, attrId);
          }});
          return;
        }}
        if (line.bucket !== 'variable') return;
        openExpenseAttributeModal({{
          bucket: 'variable',
          title: attributeEditTitle,
          initialAttribute: line.expenseAttribute,
          mode: 'edit',
          lineId: lineId,
        }}).then(function (attrId) {{
          if (!attrId) return;
          setLineExpenseAttribute(lineId, attrId);
          openInputSourceModal({{
            mode: 'edit-source',
            lineId: lineId,
            initialStyle: line.inputStyle || line.resolvedInputStyle || 'monthly',
            skipPrefs: true,
          }}).then(function (style) {{
            if (!style) return;
            setLineInputStyle(lineId, style);
          }});
        }});
      }}

      function labelText(line) {{
        return isJa ? line.labelJa : line.labelEn;
      }}

      function bucketLabel(bucket) {{
        return bucket === 'fixed' ? midFixed : midVar;
      }}

      function editableLabelSpan(lineId, text) {{
        return (
          '<span class="pl-h-label__text pl-h-label__text--editable" data-pl-label-editable="1" ' +
          'data-label-id="' +
          lineId +
          '" data-label-scope="expense-detail" tabindex="0" role="button" aria-label="' +
          escapeHtml(labelEditAria) +
          '">' +
          escapeHtml(text) +
          '</span>'
        );
      }}

      function rowHeightStyle(count) {{
        var h = 'calc(var(--pl-row-label-h) * ' + count + ')';
        return ' style="height:' + h + ';min-height:' + h + ';max-height:' + h + '"';
      }}

      function midCell(bucket, bucketLines, midLabel) {{
        return (
          '<td class="pl-v-mid pl-v-mid--expense-detail" rowspan="' +
          bucketLines.length +
          '"' +
          rowHeightStyle(bucketLines.length) +
          '><div class="pl-v-mid__inner"><span class="pl-v-mid__text">' +
          escapeHtml(midLabel) +
          '</span><div class="pl-v-mid__pm pl-v-mid__pm--add-only">' +
          '<button type="button" class="pl-v-mid__pm-btn" data-action="add" data-bucket="' +
          bucket +
          '" aria-label="' +
          escapeHtml(addAria) +
          '">+</button></div></div></td>'
        );
      }}

      function rowHideBtn(line) {{
        if (!isNonDefault(line)) return '';
        return (
          '<span class="pl-row-hide"><button type="button" class="pl-row-hide__btn pl-v-mid__pm-btn" data-action="hide-line" data-line-id="' +
          line.lineId +
          '" aria-label="' +
          escapeHtml(hideAria) +
          '">−</button></span>'
        );
      }}

      function orderBtns(line, idx, bucketLines) {{
        var upDisabled = idx === 0 ? ' disabled' : '';
        var downDisabled = idx === bucketLines.length - 1 ? ' disabled' : '';
        return (
          '<span class="pl-row-order"><button type="button" class="pl-row-order__btn" data-action="move-up" data-line-id="' +
          line.lineId +
          '"' +
          upDisabled +
          ' aria-label="' +
          escapeHtml(moveUpAria) +
          '">▲</button><button type="button" class="pl-row-order__btn" data-action="move-down" data-line-id="' +
          line.lineId +
          '"' +
          downDisabled +
          ' aria-label="' +
          escapeHtml(moveDownAria) +
          '">▼</button></span>'
        );
      }}

      function rowAttributeBtn(line) {{
        if (line.bucket !== 'fixed' && line.bucket !== 'variable') return '';
        return (
          '<span class="pl-row-attr"><button type="button" class="pl-row-attr__btn" data-action="edit-attribute" data-line-id="' +
          line.lineId +
          '" aria-label="' +
          escapeHtml(attributeBtnAria) +
          '">' +
          escapeHtml(attributeBtnLabel) +
          '</button></span>'
        );
      }}

      function labelCell(line, idx, bucketLines) {{
        return (
          '<th scope="row" class="pl-h-label pl-h-label--detail"><span class="pl-h-label__row">' +
          editableLabelSpan(line.lineId, labelText(line)) +
          rowAttributeBtn(line) +
          rowHideBtn(line) +
          orderBtns(line, idx, bucketLines) +
          '</span></th>'
        );
      }}

      function dataRow(line) {{
        var cells = '';
        for (var mi = 0; mi < 12; mi++) {{
          cells +=
            '<td class="pl-amt-cell pl-amt-cell--expense-detail" data-row="' +
            line.lineId +
            '" data-line-id="' +
            line.lineId +
            '" data-month="' +
            mi +
            '" data-field="amount"><span class="pl-amt-cell__text"></span></td>' +
            '<td class="pl-ratio-cell pl-ratio-cell--expense-detail" data-row="' +
            line.lineId +
            '" data-line-id="' +
            line.lineId +
            '" data-month="' +
            mi +
            '" data-field="ratio"><span class="pl-ratio-cell__text"></span></td>';
        }}
        return (
          '<tr class="pl-data-row pl-data-row--expense-detail' +
          rowClass(line) +
          '" data-line-id="' +
          line.lineId +
          '" data-bucket="' +
          line.bucket +
          '" data-pl-section="expense-detail">' +
          cells +
          '</tr>'
        );
      }}

      function renderExpenseDetail() {{
        var lines = loadLines();
        var labelBody = document.getElementById('pl-expense-detail-label-body');
        var dataBody = document.getElementById('pl-expense-detail-data-body');
        if (!labelBody || !dataBody) return;
        var fixed = activeBucket(lines, 'fixed');
        var variable = activeBucket(lines, 'variable');
        var total = fixed.length + variable.length;
        if (!total) return;
        var labelHtml = '';
        var dataHtml = '';

        fixed.forEach(function (line, idx) {{
          labelHtml +=
            '<tr class="pl-data-row pl-data-row--expense-detail' +
            rowClass(line) +
            '" data-line-id="' +
            line.lineId +
            '" data-bucket="' +
            line.bucket +
            '" data-pl-section="expense-detail">';
          if (idx === 0) labelHtml += midCell('fixed', fixed, midFixed);
          labelHtml += labelCell(line, idx, fixed) + '</tr>';
          dataHtml += dataRow(line);
        }});

        variable.forEach(function (line, idx) {{
          labelHtml +=
            '<tr class="pl-data-row pl-data-row--expense-detail' +
            rowClass(line) +
            '" data-line-id="' +
            line.lineId +
            '" data-bucket="' +
            line.bucket +
            '" data-pl-section="expense-detail">';
          if (idx === 0) labelHtml += midCell('variable', variable, midVar);
          labelHtml += labelCell(line, idx, variable) + '</tr>';
          dataHtml += dataRow(line);
        }});

        labelBody.innerHTML = labelHtml;
        dataBody.innerHTML = dataHtml;
        renderLineManageList();
        window.dispatchEvent(new Event('pl-expense-detail-rendered'));
      }}

      function nextLineId(bucket) {{
        return 'exp_custom_' + bucket + '_' + Date.now().toString(36);
      }}

      function addLine(bucket, inputStyle, expenseAttribute) {{
        var lines = loadLines();
        var bucketLines = activeBucket(lines, bucket);
        var maxOrder = -1;
        bucketLines.forEach(function (line) {{
          if (line.sortOrder > maxOrder) maxOrder = line.sortOrder;
        }});
        var lineId = nextLineId(bucket);
        var resolvedStyle = bucket === 'fixed' ? 'monthly' : inputStyle === 'daily' ? 'daily' : 'monthly';
        var entry = {{
          lineId: lineId,
          labelJa: newRowLabel,
          labelEn: newRowLabel,
          bucket: bucket,
          inputStyle: resolvedStyle,
          resolvedInputStyle: resolvedStyle,
          isDefault: false,
          active: true,
          sortOrder: maxOrder + 1,
        }};
        if (bucket === 'fixed' && expenseAttribute) {{
          entry.expenseAttribute = expenseAttribute;
        }}
        if (bucket === 'variable' && expenseAttribute) {{
          entry.expenseAttribute = expenseAttribute;
        }}
        lines.push(entry);
        saveLines(lines);
        renderExpenseDetail();
        window.dispatchEvent(
          new CustomEvent('pl-expense-line-added', {{ detail: {{ lineId: lineId }} }})
        );
        return lineId;
      }}

      function setLineInputStyle(lineId, inputStyle) {{
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line) return;
        line.inputStyle = inputStyle;
        line.resolvedInputStyle = inputStyle === 'daily' ? 'daily' : 'monthly';
        saveLines(lines);
        renderExpenseDetail();
      }}

      function parseCellNumber(text) {{
        var raw = String(text || '').replace(/[^\\d.-]/g, '');
        if (!raw) return 0;
        var n = parseFloat(raw);
        return Number.isFinite(n) ? n : 0;
      }}

      function cellTextHasValue(text) {{
        var s = String(text || '').replace(/\\s+/g, ' ').trim();
        if (!s || s === '—' || s === '-') return false;
        if (parseCellNumber(s) !== 0) return true;
        return /\\d/.test(s);
      }}

      function lineHasEnteredData(lineId) {{
        var dataBody = document.getElementById('pl-expense-detail-data-body');
        if (dataBody) {{
          var row = dataBody.querySelector('tr[data-line-id="' + lineId + '"]');
          if (row) {{
            var spans = row.querySelectorAll(
              '[data-field="amount"] .pl-amt-cell__text, [data-field="ratio"] .pl-ratio-cell__text'
            );
            for (var i = 0; i < spans.length; i++) {{
              if (cellTextHasValue(spans[i].textContent)) return true;
            }}
          }}
        }}
        try {{
          var prefix = lineId + ':';
          for (var si = 0; si < localStorage.length; si++) {{
            var storageKey = localStorage.key(si);
            if (!storageKey || storageKey.indexOf('kpi-pl-expenses-v1:') !== 0) continue;
            var map = JSON.parse(localStorage.getItem(storageKey) || '{{}}');
            if (!map || typeof map !== 'object') continue;
            for (var key in map) {{
              if (!Object.prototype.hasOwnProperty.call(map, key)) continue;
              if (key.indexOf(prefix) !== 0) continue;
              var n = Number(map[key]);
              if (Number.isFinite(n) && n !== 0) return true;
            }}
          }}
        }} catch (_e) {{}}
        return false;
      }}

      function clearStoredAmountsForLine(lineId) {{
        var prefix = lineId + ':';
        try {{
          for (var si = 0; si < localStorage.length; si++) {{
            var storageKey = localStorage.key(si);
            if (!storageKey || storageKey.indexOf('kpi-pl-expenses-v1:') !== 0) continue;
            var map = JSON.parse(localStorage.getItem(storageKey) || '{{}}');
            if (!map || typeof map !== 'object') continue;
            var changed = false;
            for (var key in map) {{
              if (Object.prototype.hasOwnProperty.call(map, key) && key.indexOf(prefix) === 0) {{
                delete map[key];
                changed = true;
              }}
            }}
            if (changed) localStorage.setItem(storageKey, JSON.stringify(map));
          }}
        }} catch (_e) {{}}
      }}

      function hideLine(lineId) {{
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line || !isNonDefault(line)) return;
        line.active = false;
        saveLines(lines);
        closeHideModal();
        renderExpenseDetail();
      }}

      function deleteLine(lineId) {{
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line || !isNonDefault(line)) return;
        if (lineHasEnteredData(lineId)) return;
        lines = lines.filter(function (l) {{ return l.lineId !== lineId; }});
        saveLines(lines);
        clearStoredAmountsForLine(lineId);
        closeHideModal();
        renderExpenseDetail();
      }}

      function restoreLine(lineId) {{
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId; }});
        if (!line || line.active) return;
        var bucketActive = activeBucket(lines, line.bucket);
        var maxOrder = -1;
        bucketActive.forEach(function (l) {{
          if (l.sortOrder > maxOrder) maxOrder = l.sortOrder;
        }});
        line.active = true;
        line.sortOrder = maxOrder + 1;
        saveLines(lines);
        renderExpenseDetail();
      }}

      function openHideModal(lineId) {{
        if (!hideModal) return;
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line || !isNonDefault(line)) return;
        var hasData = lineHasEnteredData(lineId);
        pendingHideLineId = lineId;
        pendingHideMode = hasData ? 'hide' : 'delete';
        if (hideModalTitle) {{
          hideModalTitle.textContent =
            pendingHideMode === 'delete' ? deleteConfirmTitle : hideConfirmTitle;
        }}
        if (hideModalBody) {{
          var bodyTpl =
            pendingHideMode === 'delete' ? deleteConfirmBodyTpl : hideConfirmBodyTpl;
          hideModalBody.textContent = bodyTpl.replace('{{label}}', labelText(line));
        }}
        if (hideModalOk) {{
          hideModalOk.textContent =
            pendingHideMode === 'delete' ? deleteConfirmOk : hideConfirmOk;
        }}
        hideModal.hidden = false;
        document.body.classList.add('pl-hide-line-modal-open');
        if (hideModalOk) hideModalOk.focus();
      }}

      function closeHideModal() {{
        if (!hideModal || hideModal.hidden) return;
        hideModal.hidden = true;
        document.body.classList.remove('pl-hide-line-modal-open');
        pendingHideLineId = null;
        pendingHideMode = null;
      }}

      function openLineManageModal() {{
        if (!manageModal) return;
        renderLineManageList();
        manageModal.hidden = false;
        document.body.classList.add('pl-line-manage-modal-open');
        var closeBtn = manageModal.querySelector('[data-pl-line-manage-action="close"]');
        if (closeBtn) closeBtn.focus();
      }}

      function closeLineManageModal() {{
        if (!manageModal || manageModal.hidden) return;
        manageModal.hidden = true;
        document.body.classList.remove('pl-line-manage-modal-open');
      }}

      function renderLineManageList() {{
        if (!manageList) return;
        var hidden = inactiveLines(loadLines());
        if (!hidden.length) {{
          manageList.innerHTML =
            '<p class="pl-line-manage__empty">' + escapeHtml(lineManageEmpty) + '</p>';
          return;
        }}
        manageList.innerHTML = hidden
          .map(function (line) {{
            return (
              '<div class="pl-line-manage__item" data-line-id="' +
              escapeHtml(line.lineId) +
              '"><span class="pl-line-manage__item-label">' +
              escapeHtml(bucketLabel(line.bucket) + ' — ' + labelText(line)) +
              '</span><button type="button" class="pl-line-manage__restore" data-action="restore-line" data-line-id="' +
              escapeHtml(line.lineId) +
              '">' +
              escapeHtml(lineManageRestore) +
              '</button></div>'
            );
          }})
          .join('');
      }}

      function promptAddLine(bucket) {{
        if (bucket === 'fixed') {{
          openExpenseAttributeModal({{
            bucket: 'fixed',
            title: attributeAddTitle,
            mode: 'add',
          }}).then(function (attrId) {{
            if (!attrId) return;
            addLine(bucket, 'monthly', attrId);
          }});
          return;
        }}
        if (bucket !== 'variable') return;
        openExpenseAttributeModal({{
          bucket: 'variable',
          title: attributeVariableAddTitle,
          mode: 'add',
        }}).then(function (attrId) {{
          if (!attrId) return;
          openInputSourceModal({{ mode: 'add', bucket: bucket, skipPrefs: true }}).then(function (
            style
          ) {{
            if (!style) return;
            addLine(bucket, style, attrId);
          }});
        }});
      }}

      function promptRelabelInputSource(lineId, currentStyle) {{
        openInputSourceModal({{
          mode: 'relabel',
          lineId: lineId,
          initialStyle: currentStyle || 'monthly',
          skipPrefs: false,
        }}).then(function (style) {{
          if (!style) return;
          setLineInputStyle(lineId, style);
        }});
      }}

      function moveLine(lineId, dir) {{
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line) return;
        var bucketLines = activeBucket(lines, line.bucket);
        var idx = bucketLines.findIndex(function (l) {{ return l.lineId === lineId; }});
        if (idx < 0) return;
        var swapIdx = dir === 'up' ? idx - 1 : idx + 1;
        if (swapIdx < 0 || swapIdx >= bucketLines.length) return;
        var moved = bucketLines.splice(idx, 1)[0];
        bucketLines.splice(swapIdx, 0, moved);
        bucketLines.forEach(function (l, i) {{
          var target = lines.find(function (x) {{ return x.lineId === l.lineId; }});
          if (target) target.sortOrder = i;
        }});
        saveLines(lines);
        renderExpenseDetail();
      }}

      block.addEventListener('click', function (e) {{
        var btn = e.target && e.target.closest ? e.target.closest('button[data-action]') : null;
        if (!btn || !block.contains(btn)) return;
        var action = btn.getAttribute('data-action');
        if (action === 'add') {{
          promptAddLine(btn.getAttribute('data-bucket'));
          return;
        }}
        if (action === 'hide-line') {{
          openHideModal(btn.getAttribute('data-line-id'));
          return;
        }}
        if (action === 'edit-attribute') {{
          editLineAttribute(btn.getAttribute('data-line-id'));
          return;
        }}
        if (action === 'move-up' || action === 'move-down') {{
          moveLine(btn.getAttribute('data-line-id'), action === 'move-up' ? 'up' : 'down');
        }}
      }});

      if (manageOpen) {{
        manageOpen.addEventListener('click', function () {{
          openLineManageModal();
        }});
      }}

      if (manageModal) {{
        manageModal.addEventListener('click', function (e) {{
          var btn =
            e.target && e.target.closest
              ? e.target.closest('[data-pl-line-manage-action],[data-action="restore-line"]')
              : null;
          if (!btn) return;
          var action = btn.getAttribute('data-pl-line-manage-action') || btn.getAttribute('data-action');
          if (action === 'close' || action === 'cancel') {{
            e.preventDefault();
            closeLineManageModal();
            return;
          }}
          if (action === 'restore-line') {{
            e.preventDefault();
            restoreLine(btn.getAttribute('data-line-id'));
          }}
        }});
      }}

      if (hideModal) {{
        hideModal.addEventListener('click', function (e) {{
          var btn =
            e.target && e.target.closest ? e.target.closest('[data-pl-hide-line-action]') : null;
          if (!btn) return;
          var action = btn.getAttribute('data-pl-hide-line-action');
          if (action === 'cancel') {{
            e.preventDefault();
            closeHideModal();
            return;
          }}
          if (action === 'confirm' && pendingHideLineId) {{
            e.preventDefault();
            if (pendingHideMode === 'delete') deleteLine(pendingHideLineId);
            else hideLine(pendingHideLineId);
          }}
        }});
      }}

      function loadAttrEditMode() {{
        try {{
          return localStorage.getItem(ATTR_EDIT_KEY) === '1';
        }} catch (_e) {{}}
        return false;
      }}

      function saveAttrEditMode(on) {{
        try {{
          localStorage.setItem(ATTR_EDIT_KEY, on ? '1' : '0');
        }} catch (_e) {{}}
      }}

      function applyAttrEditMode(on) {{
        if (!block) return;
        block.classList.toggle('pl-expense-detail-block--attr-edit', !!on);
        if (!attrToggle) return;
        attrToggle.setAttribute('aria-pressed', on ? 'true' : 'false');
        var stateEl = attrToggle.querySelector('.pl-expense-attr-toggle__state');
        if (stateEl) {{
          stateEl.textContent = on ? attrEditOnLabel : attrEditOffLabel;
          stateEl.setAttribute('data-state', on ? 'on' : 'off');
        }}
      }}

      function initAttrEditToggle() {{
        applyAttrEditMode(loadAttrEditMode());
        if (!attrToggle) return;
        attrToggle.addEventListener('click', function () {{
          var next = !block.classList.contains('pl-expense-detail-block--attr-edit');
          saveAttrEditMode(next);
          applyAttrEditMode(next);
        }});
      }}

      document.addEventListener('keydown', function (e) {{
        if (e.key === 'Escape') {{
          if (attributeModal && !attributeModal.hidden) finishExpenseAttributeModal(false);
          else if (hideModal && !hideModal.hidden) closeHideModal();
          else if (manageModal && !manageModal.hidden) closeLineManageModal();
        }}
      }});

      if (attributeModal) {{
        attributeModal.addEventListener('click', function (e) {{
          var btn =
            e.target && e.target.closest
              ? e.target.closest('[data-pl-expense-attribute-action]')
              : null;
          if (!btn) return;
          var action = btn.getAttribute('data-pl-expense-attribute-action');
          if (action === 'cancel') {{
            e.preventDefault();
            finishExpenseAttributeModal(false);
            return;
          }}
          if (action === 'confirm') {{
            e.preventDefault();
            if (!getSelectedExpenseAttribute()) return;
            finishExpenseAttributeModal(true);
          }}
        }});
        attributeModal.addEventListener('keydown', function (e) {{
          if (attributeModal.hidden) return;
          if (e.key === 'Escape') {{
            e.preventDefault();
            finishExpenseAttributeModal(false);
            return;
          }}
          if (e.key === 'Enter' && getSelectedExpenseAttribute()) {{
            e.preventDefault();
            finishExpenseAttributeModal(true);
          }}
        }});
      }}

      if (modal) {{
        modal.addEventListener('click', function (e) {{
          var btn =
            e.target && e.target.closest
              ? e.target.closest('[data-pl-input-source-action]')
              : null;
          if (!btn) return;
          var action = btn.getAttribute('data-pl-input-source-action');
          if (action === 'cancel') {{
            e.preventDefault();
            finishInputSourceModal(false);
            return;
          }}
          if (action === 'confirm') {{
            e.preventDefault();
            if (!getSelectedInputStyle()) return;
            finishInputSourceModal(true);
          }}
        }});
        modal.addEventListener('keydown', function (e) {{
          if (modal.hidden) return;
          if (e.key === 'Escape') {{
            e.preventDefault();
            finishInputSourceModal(false);
            return;
          }}
          if (e.key === 'Enter' && getSelectedInputStyle()) {{
            e.preventDefault();
            finishInputSourceModal(true);
          }}
        }});
      }}

      window.addEventListener('pl-expense-label-changed', function (e) {{
        var detail = e.detail || {{}};
        if (!detail.lineId || !detail.labelChanged) return;
        if (detail.previousLabel === newRowLabel) return;
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === detail.lineId && l.active; }});
        if (!line) return;
        if (line.bucket !== 'fixed') {{
          promptRelabelInputSource(detail.lineId, line.inputStyle);
        }}
      }});

      initAttrEditToggle();
      renderExpenseDetail();
    }})();
"""

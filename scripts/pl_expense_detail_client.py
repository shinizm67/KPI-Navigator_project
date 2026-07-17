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
    variable_mid_edit_tip: str = "",
    schema_version: int = 3,
    occupancy_aria: str = "Occupancy",
    occupancy_rent_option: str = "Rented",
    occupancy_owned_option: str = "Owned",
) -> str:
    return f"""
    (function () {{
      var isJa = document.documentElement.lang === 'ja';
      var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
      var OCCUPANCY_KEY = 'kpiNavigator.plOccupancy';
      var OCC_RENT_LINE = 'exp_rent';
      var OCC_OWNED_LINE = 'exp_depreciable_asset_tax';
      var INPUT_PREFS_KEY = 'kpiNavigator.plInputSourcePrefs';
      var ATTR_EDIT_KEY = 'kpiNavigator.plExpenseAttrEditMode';
      var DEFAULT_LINES = {catalog_json};
      var midFixed = {json.dumps(mid_fixed, ensure_ascii=False)};
      var midVar = {json.dumps(mid_var, ensure_ascii=False)};
      var variableMidEditTip = {json.dumps(variable_mid_edit_tip, ensure_ascii=False)};
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
      var occupancyAria = {json.dumps(occupancy_aria, ensure_ascii=False)};
      var occupancyRentOption = {json.dumps(occupancy_rent_option, ensure_ascii=False)};
      var occupancyOwnedOption = {json.dumps(occupancy_owned_option, ensure_ascii=False)};
      var block = document.getElementById('pl-expense-detail-block');
      var attrToggle = document.getElementById('pl-expense-attr-toggle');
      var modal = document.getElementById('pl-input-source-modal');
      var labelEditModal = document.getElementById('pl-expense-label-edit-modal');
      var labelEditInput = document.getElementById('pl-expense-label-edit-input');
      var labelEditSource = document.getElementById('pl-expense-label-edit-source');
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
      var pendingLabelEdit = null;
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
            /* ユーザーが選んだ入力元(daily/monthly)をデフォルトに戻さない */
            if (prev.inputStyle === 'daily' || prev.inputStyle === 'monthly') {{
              line.inputStyle = prev.inputStyle;
            }}
            if (prev.resolvedInputStyle === 'daily' || prev.resolvedInputStyle === 'monthly') {{
              line.resolvedInputStyle = prev.resolvedInputStyle;
            }} else if (line.inputStyle === 'daily' || line.inputStyle === 'monthly') {{
              line.resolvedInputStyle = line.inputStyle;
            }}
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

      function applyInputStyleDefaultMigrations(lines) {{
        /* schema v7: FL 方針に合わせたデフォルト移行（旧デフォルトのままの行だけ） */
        var rules = {{
          exp_supplies: {{ from: 'daily', to: 'monthly' }},
          exp_misc: {{ from: 'daily', to: 'monthly' }},
          exp_variable_labor: {{ from: 'monthly', to: 'daily' }},
        }};
        var changed = false;
        (lines || []).forEach(function (line) {{
          if (!line || !line.lineId) return;
          var rule = rules[line.lineId];
          if (!rule) return;
          var cur = line.resolvedInputStyle || line.inputStyle;
          if (cur !== rule.from) return;
          line.inputStyle = rule.to;
          line.resolvedInputStyle = rule.to;
          changed = true;
        }});
        return changed;
      }}

      function isOccupancyLineId(lineId) {{
        return lineId === OCC_RENT_LINE || lineId === OCC_OWNED_LINE;
      }}

      function loadOccupancy() {{
        try {{
          var raw = localStorage.getItem(OCCUPANCY_KEY);
          if (raw === 'owned' || raw === 'rent') return raw;
        }} catch (_e) {{}}
        return 'rent';
      }}

      function saveOccupancy(mode) {{
        var next = mode === 'owned' ? 'owned' : 'rent';
        try {{
          localStorage.setItem(OCCUPANCY_KEY, next);
        }} catch (_e) {{}}
        return next;
      }}

      function occupancyVisibleLineId(mode) {{
        return (mode || loadOccupancy()) === 'owned' ? OCC_OWNED_LINE : OCC_RENT_LINE;
      }}

      function syncOccupancyActiveFlags(lines) {{
        var mode = loadOccupancy();
        var rentLine = null;
        var ownedLine = null;
        (lines || []).forEach(function (line) {{
          if (line.lineId === OCC_RENT_LINE) rentLine = line;
          if (line.lineId === OCC_OWNED_LINE) ownedLine = line;
        }});
        var changed = false;
        if (rentLine) {{
          var wantRent = mode === 'rent';
          if (rentLine.active !== wantRent) {{
            rentLine.active = wantRent;
            changed = true;
          }}
        }}
        if (ownedLine) {{
          var wantOwned = mode === 'owned';
          if (ownedLine.active !== wantOwned) {{
            ownedLine.active = wantOwned;
            changed = true;
          }}
          if (wantOwned && rentLine && typeof rentLine.sortOrder === 'number') {{
            if (ownedLine.sortOrder !== rentLine.sortOrder) {{
              ownedLine.sortOrder = rentLine.sortOrder;
              changed = true;
            }}
          }}
        }}
        return changed;
      }}

      function setOccupancy(mode) {{
        saveOccupancy(mode);
        var lines = loadLines();
        if (syncOccupancyActiveFlags(lines)) saveLines(lines);
        renderExpenseDetail();
      }}

      function mergeCatalogFromDefaults(oldLines) {{
        var lines = reconcileCatalogLines(oldLines);
        applyInputStyleDefaultMigrations(lines);
        normalizeAllBucketSortOrders(lines);
        if (normalizeFixedBucketLines(lines)) {{}}
        syncOccupancyActiveFlags(lines);
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
        syncOccupancyActiveFlags(fresh);
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
        if (syncOccupancyActiveFlags(reconciled)) changed = true;
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
        var visibleOcc = occupancyVisibleLineId();
        return lines
          .filter(function (line) {{
            if (!(line.active && line.bucket === bucket)) return false;
            if (isOccupancyLineId(line.lineId) && line.lineId !== visibleOcc) return false;
            return true;
          }})
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
          .filter(function (line) {{
            if (line.active) return false;
            /* 物件切替で隠している行は科目管理に出さない */
            if (isOccupancyLineId(line.lineId)) return false;
            return true;
          }})
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
        saveInputPrefs(prefs);
        resolve(style);
      }}

      function getLabelEditSourceStyle() {{
        if (!labelEditSource || labelEditSource.hidden) return null;
        var picked = labelEditSource.querySelector(
          'input[name="pl-expense-label-edit-source"]:checked'
        );
        return picked ? picked.value : null;
      }}

      function setLabelEditSourceStyle(style) {{
        if (!labelEditSource) return;
        var radio = labelEditSource.querySelector(
          'input[name="pl-expense-label-edit-source"][value="' + style + '"]'
        );
        if (radio) radio.checked = true;
      }}

      function closeLabelEditModal() {{
        if (!labelEditModal) return;
        labelEditModal.hidden = true;
        document.body.classList.remove('pl-expense-label-edit-modal-open');
        pendingLabelEdit = null;
      }}

      function openLabelEditModal(lineId) {{
        if (!labelEditModal || !labelEditInput) return;
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line) return;
        pendingLabelEdit = {{ lineId: lineId }};
        labelEditInput.value = labelText(line);
        var showSource = line.bucket === 'variable';
        if (labelEditSource) {{
          labelEditSource.hidden = !showSource;
          labelEditSource.querySelectorAll('input[type="radio"]').forEach(function (inp) {{
            inp.disabled = !showSource;
          }});
          if (showSource) {{
            setLabelEditSourceStyle(line.resolvedInputStyle || line.inputStyle || 'monthly');
          }}
        }}
        labelEditModal.hidden = false;
        document.body.classList.add('pl-expense-label-edit-modal-open');
        labelEditInput.focus();
        labelEditInput.select();
      }}

      function commitLabelEdit() {{
        if (!pendingLabelEdit || !labelEditInput) return false;
        var lineId = pendingLabelEdit.lineId;
        var next = String(labelEditInput.value || '').replace(/\\s+/g, ' ').trim();
        if (!next) {{
          labelEditInput.focus();
          return false;
        }}
        var lines = loadLines();
        var line = lines.find(function (l) {{ return l.lineId === lineId && l.active; }});
        if (!line) {{
          closeLabelEditModal();
          return false;
        }}
        var prevJa = line.labelJa;
        var prevEn = line.labelEn;
        var prevStyle = line.resolvedInputStyle || line.inputStyle || 'monthly';
        if (isJa) line.labelJa = next;
        else line.labelEn = next;
        if (line.bucket === 'variable') {{
          var style = getLabelEditSourceStyle();
          if (style === 'daily' || style === 'monthly') {{
            line.inputStyle = style;
            line.resolvedInputStyle = style;
            cleanupAbandonedInputDataOnStyleChange(lineId, prevStyle, style);
          }}
        }}
        saveLines(lines);
        closeLabelEditModal();
        renderExpenseDetail();
        window.dispatchEvent(
          new CustomEvent('pl-expense-label-changed', {{
            detail: {{
              lineId: lineId,
              labelJa: line.labelJa,
              labelEn: line.labelEn,
              labelChanged: prevJa !== line.labelJa || prevEn !== line.labelEn,
              previousLabel: isJa ? prevJa : prevEn,
            }},
          }})
        );
        return true;
      }}

      function finishLabelEditModal(confirmed) {{
        if (!pendingLabelEdit) return;
        if (!confirmed) {{
          closeLabelEditModal();
          return;
        }}
        commitLabelEdit();
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
        var tipAttr =
          bucket === 'variable' && variableMidEditTip
            ? ' title="' + escapeHtml(variableMidEditTip) + '"'
            : '';
        return (
          '<td class="pl-v-mid pl-v-mid--expense-detail" rowspan="' +
          bucketLines.length +
          '"' +
          tipAttr +
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
        if (!isNonDefault(line) || isOccupancyLineId(line.lineId)) return '';
        return (
          '<span class="pl-row-hide"><button type="button" class="pl-row-hide__btn pl-v-mid__pm-btn" data-action="hide-line" data-line-id="' +
          line.lineId +
          '" aria-label="' +
          escapeHtml(hideAria) +
          '">−</button></span>'
        );
      }}

      function occupancySelectHtml() {{
        var mode = loadOccupancy();
        return (
          '<label class="pl-occupancy-select-wrap">' +
          '<select class="pl-occupancy-select" data-pl-occupancy-select="1" aria-label="' +
          escapeHtml(occupancyAria) +
          '">' +
          '<option value="rent"' +
          (mode === 'rent' ? ' selected' : '') +
          '>' +
          escapeHtml(occupancyRentOption) +
          '</option>' +
          '<option value="owned"' +
          (mode === 'owned' ? ' selected' : '') +
          '>' +
          escapeHtml(occupancyOwnedOption) +
          '</option>' +
          '</select></label>'
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
        var occSelect = isOccupancyLineId(line.lineId) ? occupancySelectHtml() : '';
        return (
          '<th scope="row" class="pl-h-label pl-h-label--detail' +
          (isOccupancyLineId(line.lineId) ? ' pl-h-label--occupancy' : '') +
          '"><span class="pl-h-label__row">' +
          occSelect +
          editableLabelSpan(line.lineId, labelText(line)) +
          rowAttributeBtn(line) +
          rowHideBtn(line) +
          orderBtns(line, idx, bucketLines) +
          '</span></th>'
        );
      }}

      function dataRow(line) {{
        var cells = '';
        var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
        var isMonthly = style !== 'daily';
        var dailyReadonlyHint = isJa
          ? 'MEP（月次編集）で日次入力。ダブルクリック / F2 で調整額'
          : 'Enter daily on Monthly Edit. Double-click / F2 for adjustment';
        for (var mi = 0; mi < 12; mi++) {{
          var amountInner = isMonthly
            ? '<span class="pl-amt-cell__text" contenteditable="true" data-pl-editable="1" data-pl-field="amount" data-row="' +
              line.lineId +
              '" data-month="' +
              mi +
              '"></span>'
            : '<span class="pl-amt-cell__text" tabindex="0" role="button">—</span>';
          cells +=
            '<td class="pl-amt-cell pl-amt-cell--expense-detail' +
            (isMonthly ? ' pl-amt-cell--pl-monthly-editable' : ' pl-amt-cell--pl-daily-readonly') +
            '"' +
            (isMonthly ? '' : ' title="' + dailyReadonlyHint + '" data-pl-adj-editable="1"') +
            ' data-row="' +
            line.lineId +
            '" data-line-id="' +
            line.lineId +
            '" data-month="' +
            mi +
            '" data-field="amount">' +
            amountInner +
            '</td>' +
            '<td class="pl-ratio-cell pl-ratio-cell--expense-detail" data-row="' +
            line.lineId +
            '" data-line-id="' +
            line.lineId +
            '" data-month="' +
            mi +
            '" data-field="ratio"><span class="pl-ratio-cell__text"></span></td>';
        }}
        cells +=
          '<td class="pl-amt-cell pl-amt-cell--expense-detail pl-amt-cell--year-total" data-row="' +
          line.lineId +
          '" data-line-id="' +
          line.lineId +
          '" data-month="year" data-field="amount">' +
          '<span class="pl-amt-cell__text">—</span></td>' +
          '<td class="pl-ratio-cell pl-ratio-cell--expense-detail pl-ratio-cell--year-total" data-row="' +
          line.lineId +
          '" data-line-id="' +
          line.lineId +
          '" data-month="year" data-field="ratio">' +
          '<span class="pl-ratio-cell__text">—</span></td>';
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
        var prevStyle = line.resolvedInputStyle || line.inputStyle || 'monthly';
        var nextStyle = inputStyle === 'daily' ? 'daily' : 'monthly';
        line.inputStyle = nextStyle;
        line.resolvedInputStyle = nextStyle;
        cleanupAbandonedInputDataOnStyleChange(lineId, prevStyle, nextStyle);
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

      function clearDailyExpensesForLine(lineId) {{
        var gw = window.__KPI_DATA_GATEWAY;
        if (!gw || typeof gw.getJson !== 'function' || typeof gw.setJson !== 'function') {{
          return false;
        }}
        var store = null;
        try {{
          store = gw.getJson('kpiNavigator.kpiYearStore');
        }} catch (_e) {{
          return false;
        }}
        if (!store || typeof store !== 'object' || !store.years) return false;
        var changed = false;
        Object.keys(store.years).forEach(function (yk) {{
          var rec = store.years[yk];
          if (!rec || typeof rec !== 'object') return;
          if (!rec.dailyExpenses || typeof rec.dailyExpenses !== 'object') return;
          if (!Object.prototype.hasOwnProperty.call(rec.dailyExpenses, lineId)) return;
          delete rec.dailyExpenses[lineId];
          rec.mepUpdatedAt = Date.now();
          changed = true;
        }});
        if (!changed) return false;
        var saved = false;
        try {{
          saved = !!gw.setJson('kpiNavigator.kpiYearStore', store);
        }} catch (_e2) {{
          return false;
        }}
        if (saved) {{
          try {{
            document.dispatchEvent(
              new CustomEvent('kpi:mepDataChanged', {{
                detail: {{ source: 'pl-input-style-cleanup', lineId: lineId }},
              }})
            );
          }} catch (_e3) {{}}
        }}
        return saved;
      }}

      function cleanupAbandonedInputDataOnStyleChange(lineId, prevStyle, nextStyle) {{
        if (!lineId || !prevStyle || !nextStyle || prevStyle === nextStyle) return;
        if (prevStyle === 'monthly' && nextStyle === 'daily') {{
          clearStoredAmountsForLine(lineId);
        }} else if (prevStyle === 'daily' && nextStyle === 'monthly') {{
          clearDailyExpensesForLine(lineId);
          if (typeof window.__plClearExpenseAdjustmentsForLine === 'function') {{
            window.__plClearExpenseAdjustmentsForLine(lineId);
          }}
        }}
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
        if (isOccupancyLineId(lineId)) {{
          setOccupancy(lineId === OCC_OWNED_LINE ? 'owned' : 'rent');
          return;
        }}
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
          /* 入力元は続く統合モーダル（ラベル編集）で選ぶ */
          addLine(bucket, 'monthly', attrId);
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

      if (labelEditModal) {{
        labelEditModal.addEventListener('click', function (e) {{
          var btn =
            e.target && e.target.closest
              ? e.target.closest('[data-pl-label-edit-action]')
              : null;
          if (!btn) return;
          var action = btn.getAttribute('data-pl-label-edit-action');
          if (action === 'cancel') {{
            e.preventDefault();
            finishLabelEditModal(false);
            return;
          }}
          if (action === 'confirm') {{
            e.preventDefault();
            finishLabelEditModal(true);
          }}
        }});
        labelEditModal.addEventListener('keydown', function (e) {{
          if (labelEditModal.hidden) return;
          if (e.key === 'Escape') {{
            e.preventDefault();
            finishLabelEditModal(false);
            return;
          }}
          if (e.key === 'Enter') {{
            e.preventDefault();
            finishLabelEditModal(true);
          }}
        }});
      }}

      window.addEventListener('pl-expense-label-edit-request', function (e) {{
        var lineId = e.detail && e.detail.lineId;
        if (!lineId) return;
        openLabelEditModal(lineId);
      }});

      // Create a catalog line with an explicit label (used by CSV/Excel import
      // "新規作成"). Unlike addLine(), the label is provided up front instead of a
      // placeholder. Returns the new lineId (or '' on invalid bucket).
      function addCatalogLineWithLabel(labelJa, labelEn, bucket, inputStyle) {{
        var b = bucket === 'fixed' ? 'fixed' : 'variable';
        var lines = loadLines();
        var bucketLines = activeBucket(lines, b);
        var maxOrder = -1;
        bucketLines.forEach(function (line) {{
          if (line.sortOrder > maxOrder) maxOrder = line.sortOrder;
        }});
        var base = 'exp_custom_' + b + '_' + Date.now().toString(36);
        var lineId = base;
        var n = 1;
        while (lines.some(function (l) {{ return String(l.lineId) === lineId; }})) {{
          lineId = base + '_' + n;
          n++;
        }}
        var resolvedStyle = b === 'fixed'
          ? 'monthly'
          : (inputStyle === 'daily' ? 'daily' : 'monthly');
        var lj = (labelJa != null && String(labelJa).trim()) ? String(labelJa).trim() : newRowLabel;
        var le = (labelEn != null && String(labelEn).trim()) ? String(labelEn).trim() : lj;
        lines.push({{
          lineId: lineId,
          labelJa: lj,
          labelEn: le,
          bucket: b,
          inputStyle: resolvedStyle,
          resolvedInputStyle: resolvedStyle,
          isDefault: false,
          active: true,
          sortOrder: maxOrder + 1,
        }});
        saveLines(lines);
        renderExpenseDetail();
        window.dispatchEvent(
          new CustomEvent('pl-expense-line-added', {{ detail: {{ lineId: lineId }} }})
        );
        return lineId;
      }}

      window.__plSetLineInputStyle = setLineInputStyle;
      window.__plSetOccupancy = setOccupancy;
      window.__plGetOccupancy = loadOccupancy;
      window.__plAddCatalogLineWithLabel = addCatalogLineWithLabel;
      window.__plRenderExpenseDetail = renderExpenseDetail;
      window.__plGetCatalogLines = function () {{
        try {{ return loadLines(); }} catch (_e) {{ return []; }}
      }};

      if (block) {{
        block.addEventListener('change', function (e) {{
          var sel = e.target && e.target.closest
            ? e.target.closest('[data-pl-occupancy-select]')
            : null;
          if (!sel || !block.contains(sel)) return;
          setOccupancy(sel.value);
        }});
        block.addEventListener('mousedown', function (e) {{
          var sel = e.target && e.target.closest
            ? e.target.closest('[data-pl-occupancy-select]')
            : null;
          if (sel) e.stopPropagation();
        }});
        block.addEventListener('click', function (e) {{
          var sel = e.target && e.target.closest
            ? e.target.closest('[data-pl-occupancy-select]')
            : null;
          if (sel) e.stopPropagation();
        }});
      }}

      initAttrEditToggle();
      renderExpenseDetail();
    }})();
"""

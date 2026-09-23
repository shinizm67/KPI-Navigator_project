/**
 * C2-L6-B — Excel Sheet Picker (Launch).
 * Multi-sheet workbooks: user picks one sheet. Single-sheet: no modal.
 * Cached cell values only. No formula evaluation. No recommended-sheet scan.
 */
(function (global) {
  'use strict';

  if (global.KpiExcelSheetPicker && global.KpiExcelSheetPicker.__ready) {
    return;
  }

  var ROOT_ID = 'kpi-excel-sheet-picker';
  var STYLE_ID = 'kpi-excel-sheet-picker-style';
  var COPY = {
    ja: {
      title: '取り込むシートを選択してください',
      cancel: 'キャンセル',
      fallback:
        'このシートの形式を自動判定できませんでした。\nKPNテンプレートを使用して取り込むことができます。',
    },
    en: {
      title: 'Select the sheet to import',
      cancel: 'Cancel',
      fallback:
        'This sheet layout could not be recognized automatically.\nYou can import using a KPN template.',
    },
    'zh-tw': {
      title: '選擇要匯入的工作表',
      cancel: '取消',
      fallback:
        '無法自動判斷此工作表的格式。\n可以使用 KPN 範本匯入。',
    },
  };

  function locale() {
    var raw = '';
    try {
      raw = String(
        (global.document &&
          global.document.documentElement &&
          global.document.documentElement.getAttribute('lang')) ||
          ''
      );
    } catch (_e) {}
    var l = raw.toLowerCase();
    if (l.indexOf('ja') === 0) return 'ja';
    if (l.indexOf('zh') === 0) return 'zh-tw';
    return 'en';
  }

  function text(key) {
    var pack = COPY[locale()] || COPY.en;
    return pack[key] || COPY.en[key] || '';
  }

  function isExcelName(name) {
    return /\.(xlsx|xls)$/i.test(String(name || ''));
  }

  function cancelledError() {
    var err = new Error('cancelled');
    err.code = 'cancelled';
    return err;
  }

  function isCancelled(err) {
    if (!err) return false;
    return err.code === 'cancelled' || err.message === 'cancelled';
  }

  function ensureStyle() {
    if (!global.document || global.document.getElementById(STYLE_ID)) return;
    var css = global.document.createElement('style');
    css.id = STYLE_ID;
    /* 20120: above Sales/Past Sales host 20055 and graph popover 20100; below leave-close 20150. */
    css.textContent =
      '#' +
      ROOT_ID +
      '{position:fixed;inset:0;z-index:20120;display:flex;align-items:center;justify-content:center;padding:24px;box-sizing:border-box;pointer-events:auto;}' +
      '#' +
      ROOT_ID +
      ' .kpi-sheet-picker__backdrop{position:absolute;inset:0;background:rgba(0,0,0,.62);}' +
      '#' +
      ROOT_ID +
      ' .kpi-sheet-picker__panel{position:relative;width:min(420px,100%);max-height:calc(100vh - 48px);overflow:auto;padding:20px 18px 16px;border:1px solid rgba(88,225,243,.55);border-radius:6px;background:#1f1e1e;color:#58e1f3;box-shadow:0 12px 40px rgba(0,0,0,.45);box-sizing:border-box;}' +
      'html[lang="ja"] #' +
      ROOT_ID +
      ' .kpi-sheet-picker__panel{font-family:"BIZ UDPGothic",sans-serif;}' +
      '#' +
      ROOT_ID +
      ' .kpi-sheet-picker__title{margin:0 0 14px;font-size:15px;font-weight:600;line-height:1.45;}' +
      '#' +
      ROOT_ID +
      ' .kpi-sheet-picker__list{display:flex;flex-direction:column;gap:8px;margin:0 0 14px;}' +
      '#' +
      ROOT_ID +
      ' .kpi-sheet-picker__sheet{display:block;width:100%;text-align:left;padding:10px 12px;border:1px solid rgba(88,225,243,.45);border-radius:4px;background:transparent;color:inherit;font:inherit;cursor:pointer;}' +
      '#' +
      ROOT_ID +
      ' .kpi-sheet-picker__sheet:hover,#' +
      ROOT_ID +
      ' .kpi-sheet-picker__sheet:focus{background:rgba(88,225,243,.12);}' +
      '#' +
      ROOT_ID +
      ' .kpi-sheet-picker__cancel{display:block;width:100%;padding:8px 12px;border:0;border-radius:4px;background:transparent;color:rgba(88,225,243,.85);font:inherit;cursor:pointer;}' +
      'body.office-mode #' +
      ROOT_ID +
      ' .kpi-sheet-picker__panel{background:#fff;color:#111;border-color:#ccc;}' +
      'body.office-mode #' +
      ROOT_ID +
      ' .kpi-sheet-picker__sheet{border-color:#ccc;}' +
      'body.office-mode #' +
      ROOT_ID +
      ' .kpi-sheet-picker__sheet:hover,body.office-mode #' +
      ROOT_ID +
      ' .kpi-sheet-picker__sheet:focus{background:#f3f3f3;}' +
      'body.office-mode #' +
      ROOT_ID +
      ' .kpi-sheet-picker__cancel{color:#444;}';
    global.document.head.appendChild(css);
  }

  function closePicker() {
    var el = global.document && global.document.getElementById(ROOT_ID);
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function pickSheetName(names) {
    var list = Array.isArray(names) ? names.slice() : [];
    if (!list.length) return Promise.reject(new Error('empty'));
    if (list.length === 1) return Promise.resolve(list[0]);
    ensureStyle();
    return new Promise(function (resolve, reject) {
      closePicker();
      var root = global.document.createElement('div');
      root.id = ROOT_ID;
      root.setAttribute('role', 'dialog');
      root.setAttribute('aria-modal', 'true');
      root.setAttribute('aria-labelledby', ROOT_ID + '-title');
      var backdrop = global.document.createElement('div');
      backdrop.className = 'kpi-sheet-picker__backdrop';
      var panel = global.document.createElement('div');
      panel.className = 'kpi-sheet-picker__panel';
      var title = global.document.createElement('p');
      title.id = ROOT_ID + '-title';
      title.className = 'kpi-sheet-picker__title';
      title.textContent = text('title');
      var ul = global.document.createElement('div');
      ul.className = 'kpi-sheet-picker__list';
      list.forEach(function (name) {
        var btn = global.document.createElement('button');
        btn.type = 'button';
        btn.className = 'kpi-sheet-picker__sheet';
        btn.setAttribute('data-kpi-sheet-name', name);
        btn.textContent = name;
        btn.addEventListener('click', function () {
          finish(name);
        });
        ul.appendChild(btn);
      });
      var cancel = global.document.createElement('button');
      cancel.type = 'button';
      cancel.id = ROOT_ID + '-cancel';
      cancel.className = 'kpi-sheet-picker__cancel';
      cancel.textContent = text('cancel');
      function finish(value) {
        global.document.removeEventListener('keydown', onKey, true);
        closePicker();
        if (value == null) reject(cancelledError());
        else resolve(value);
      }
      function onKey(ev) {
        if (ev.key === 'Escape') {
          ev.preventDefault();
          finish(null);
        }
      }
      cancel.addEventListener('click', function () {
        finish(null);
      });
      backdrop.addEventListener('click', function () {
        finish(null);
      });
      panel.appendChild(title);
      panel.appendChild(ul);
      panel.appendChild(cancel);
      root.appendChild(backdrop);
      root.appendChild(panel);
      global.document.body.appendChild(root);
      global.document.addEventListener('keydown', onKey, true);
      var first = ul.querySelector('button');
      if (first && typeof first.focus === 'function') first.focus();
    });
  }

  function sheetToRows(wb, name) {
    if (!global.XLSX || !global.XLSX.utils || !wb) return [];
    var sheet = wb.Sheets && wb.Sheets[name];
    if (!sheet) return [];
    /* raw:true → cached/displayed cell.v only. Do not evaluate formulas. */
    return global.XLSX.utils.sheet_to_json(sheet, {
      header: 1,
      raw: true,
      defval: '',
      blankrows: false,
    });
  }

  function rowsFromWorkbook(wb) {
    var names = wb && wb.SheetNames ? wb.SheetNames.slice() : [];
    if (!names.length) return Promise.reject(new Error('empty'));
    return pickSheetName(names).then(function (name) {
      return { name: name, rows: sheetToRows(wb, name) };
    });
  }

  function showTemplateFallback() {
    try {
      global.window.alert(text('fallback'));
    } catch (_eAlert) {}
    try {
      var details = global.document && global.document.getElementById('header-dl');
      if (details) details.setAttribute('open', '');
    } catch (_eDl) {}
  }

  global.KpiExcelSheetPicker = {
    __ready: true,
    COPY: COPY,
    locale: locale,
    text: text,
    isExcelName: isExcelName,
    isCancelled: isCancelled,
    pickSheetName: pickSheetName,
    sheetToRows: sheetToRows,
    rowsFromWorkbook: rowsFromWorkbook,
    showTemplateFallback: showTemplateFallback,
  };
})(typeof window !== 'undefined' ? window : this);

/**
 * Unit 6F — Excel template download. Thin SheetJS wrapper around KpiCsvTemplates.
 * Python twin: scripts/csv_excel_template_generator.py
 */
(function (global) {
  'use strict';

  if (global.KpiExcelTemplates && global.KpiExcelTemplates.__ready) {
    return;
  }

  var XLSX_CDN = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';
  var SALES_BLANK_ROWS = 8;
  var SHEET_NAMES = {
    ja: { sales: '売上', 'expense-daily': '支出_日次', 'expense-monthly': '支出_月次' },
    en: { sales: 'Sales', 'expense-daily': 'Daily Expenses', 'expense-monthly': 'Monthly Expenses' },
    'zh-tw': { sales: '銷售', 'expense-daily': '支出_每日', 'expense-monthly': '支出_月度' },
  };
  var BTN_LABEL = {
    ja: 'Excel雛形をダウンロード',
    en: 'Download Excel Template',
    'zh-tw': '下載 Excel 範本',
  };

  var _xlsxLoading = null;

  function csvApi() {
    return global.KpiCsvTemplates || null;
  }

  function detectLang() {
    var api = csvApi();
    if (!api) return 'en';
    var raw = '';
    try {
      raw = String(
        (global.document && global.document.documentElement &&
          global.document.documentElement.getAttribute('lang')) || ''
      );
    } catch (_e) {}
    var l = raw.toLowerCase();
    if (l.indexOf('ja') === 0) return 'ja';
    if (l.indexOf('zh') === 0) return 'zh-tw';
    return 'en';
  }

  function currentBusinessType() {
    if (global.KpiBusinessType && typeof global.KpiBusinessType.getBusinessType === 'function') {
      try {
        var bt = global.KpiBusinessType.getBusinessType();
        if (bt) return String(bt);
      } catch (_e) {}
    }
    return 'restaurant';
  }

  function sheetName(kind, lang) {
    var loc = lang || detectLang();
    var pack = SHEET_NAMES[loc] || SHEET_NAMES.en;
    return pack[kind] || kind;
  }

  function parseCsvText(text) {
    var api = csvApi();
    var lines = String(text || '').replace(/^\uFEFF/, '').split(/\r?\n/);
    var rows = [];
    for (var i = 0; i < lines.length; i++) {
      if (lines[i] === '') continue;
      rows.push(splitCsvLine(lines[i]));
    }
    return rows;
  }

  function splitCsvLine(line) {
    var out = [];
    var cur = '';
    var inQ = false;
    for (var i = 0; i < line.length; i++) {
      var ch = line[i];
      if (inQ) {
        if (ch === '"') {
          if (line[i + 1] === '"') {
            cur += '"';
            i++;
          } else inQ = false;
        } else cur += ch;
      } else if (ch === '"') inQ = true;
      else if (ch === ',') {
        out.push(cur);
        cur = '';
      } else cur += ch;
    }
    out.push(cur);
    return out;
  }

  function salesRows(businessType, lang) {
    var rec = csvApi().buildSalesTemplate(businessType, lang);
    var rows = parseCsvText(rec.text);
    var width = (rec.keys && rec.keys.length) || (rows[0] && rows[0].length) || 0;
    for (var i = 0; i < SALES_BLANK_ROWS; i++) {
      var blank = [];
      for (var c = 0; c < width; c++) blank.push('');
      rows.push(blank);
    }
    return { rows: rows, keys: rec.keys || (rows[0] || []) };
  }

  function expensePack(style, lang, catalog, businessType) {
    var rec = csvApi().buildExpenseTemplate(catalog, style, lang, businessType);
    return {
      rows: parseCsvText(rec.text),
      lineIds: rec.lineIds || [],
    };
  }

  function buildExcelSpec(businessType, lang, catalogLines) {
    var api = csvApi();
    if (!api) return null;
    var loc = lang || detectLang();
    var bt = businessType == null ? currentBusinessType() : businessType;
    var sales = salesRows(bt, loc);
    var daily = expensePack('daily', loc, catalogLines, bt);
    var monthly = expensePack('monthly', loc, catalogLines, bt);
    return {
      businessType: bt,
      lang: loc,
      filename: 'kpi_template_' + bt + '.xlsx',
      sheets: [
        { kind: 'sales', name: sheetName('sales', loc), rows: sales.rows, keys: sales.keys, lineIds: [] },
        {
          kind: 'expense-daily',
          name: sheetName('expense-daily', loc),
          rows: daily.rows,
          lineIds: daily.lineIds,
        },
        {
          kind: 'expense-monthly',
          name: sheetName('expense-monthly', loc),
          rows: monthly.rows,
          lineIds: monthly.lineIds,
        },
      ],
    };
  }

  function ensureXlsx() {
    if (global.XLSX && global.XLSX.utils && typeof global.XLSX.writeFile === 'function') {
      return Promise.resolve(global.XLSX);
    }
    if (_xlsxLoading) return _xlsxLoading;
    _xlsxLoading = new Promise(function (resolve, reject) {
      var s = global.document.createElement('script');
      s.src = XLSX_CDN;
      s.async = true;
      s.onload = function () {
        _xlsxLoading = null;
        global.XLSX ? resolve(global.XLSX) : reject(new Error('xlsx'));
      };
      s.onerror = function () {
        _xlsxLoading = null;
        reject(new Error('xlsx'));
      };
      global.document.head.appendChild(s);
    });
    return _xlsxLoading;
  }

  function workbookFromSpec(XLSX, spec) {
    var wb = XLSX.utils.book_new();
    (spec.sheets || []).forEach(function (sheet) {
      var ws = XLSX.utils.aoa_to_sheet(sheet.rows || []);
      XLSX.utils.book_append_sheet(wb, ws, sheet.name);
    });
    return wb;
  }

  function downloadExcelTemplate(opts) {
    opts = opts || {};
    var spec = buildExcelSpec(opts.businessType, opts.lang, opts.catalogLines);
    if (!spec) return Promise.reject(new Error('csv-templates'));
    return ensureXlsx().then(function (XLSX) {
      var wb = workbookFromSpec(XLSX, spec);
      XLSX.writeFile(wb, spec.filename);
      return spec;
    });
  }

  function ensureExcelButton(menu) {
    if (!menu || menu.querySelector('#kpi-dl-excel-template')) return;
    var btn = global.document.createElement('button');
    btn.type = 'button';
    btn.id = 'kpi-dl-excel-template';
    btn.className = 'template-dl-item';
    btn.setAttribute('role', 'menuitem');
    btn.setAttribute('data-kpi-excel-template', 'workbook');
    btn.textContent = BTN_LABEL[detectLang()] || BTN_LABEL.en;
    var monthly = menu.querySelector('[data-kpi-csv-template="expense-monthly"]');
    if (monthly && monthly.nextSibling) menu.insertBefore(btn, monthly.nextSibling);
    else if (monthly) monthly.parentNode.appendChild(btn);
    else menu.appendChild(btn);
  }

  function onMenuClick(e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var btn = t.closest('[data-kpi-excel-template]');
    if (!btn) return;
    e.preventDefault();
    downloadExcelTemplate().catch(function () {});
  }

  function bindDownloadMenu(root) {
    var doc = root || global.document;
    if (!doc || doc.__kpiExcelTemplateBound) return;
    doc.__kpiExcelTemplateBound = true;
    doc.addEventListener('click', onMenuClick, true);
    var menus = doc.querySelectorAll('.template-dl-menu');
    for (var i = 0; i < menus.length; i++) ensureExcelButton(menus[i]);
  }

  global.KpiExcelTemplates = {
    __ready: true,
    SHEET_NAMES: SHEET_NAMES,
    buildExcelSpec: buildExcelSpec,
    workbookFromSpec: workbookFromSpec,
    downloadExcelTemplate: downloadExcelTemplate,
    ensureXlsx: ensureXlsx,
    bindDownloadMenu: bindDownloadMenu,
  };

  if (global.document) {
    if (global.document.readyState === 'loading') {
      global.document.addEventListener('DOMContentLoaded', function () {
        bindDownloadMenu(global.document);
      });
    } else {
      bindDownloadMenu(global.document);
    }
  }
})(typeof window !== 'undefined' ? window : this);

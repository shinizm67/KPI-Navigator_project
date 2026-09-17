/**
 * Unit 6D — download CSV templates from Business Type + active PL catalog.
 * Python twin: scripts/csv_template_generator.py
 */
(function (global) {
  'use strict';

  if (global.KpiCsvTemplates && global.KpiCsvTemplates.__ready) {
    return;
  }

  var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
  var COMMON_KEYS = ['date', 'business_day', 'daily_sales'];
  var RESTAURANT_ONLY_KEYS = [
    'lunch_sales',
    'dinner_sales',
    'total_customers',
    'lunch_customers',
    'dinner_customers',
    'total_groups',
    'lunch_groups',
    'dinner_groups',
    'food_sales',
    'drink_sales',
  ];
  var SALES_LABELS = {
    ja: {
      date: '日付',
      business_day: '営業日',
      daily_sales: '日次売上',
      lunch_sales: 'ランチ売上',
      dinner_sales: 'ディナー売上',
      total_customers: 'トータル客数',
      lunch_customers: 'ランチ客数',
      dinner_customers: 'ディナー客数',
      total_groups: 'トータル組数',
      lunch_groups: 'ランチ組数',
      dinner_groups: 'ディナー組数',
      food_sales: 'フード売上',
      drink_sales: 'ドリンク売上',
    },
    en: {
      date: 'date',
      business_day: 'business day',
      daily_sales: 'daily sales',
      lunch_sales: 'lunch sales',
      dinner_sales: 'dinner sales',
      total_customers: 'total customers',
      lunch_customers: 'lunch customers',
      dinner_customers: 'dinner customers',
      total_groups: 'total groups',
      lunch_groups: 'lunch groups',
      dinner_groups: 'dinner groups',
      food_sales: 'food sales',
      drink_sales: 'drink sales',
    },
    'zh-tw': {
      date: '日期',
      business_day: '營業日',
      daily_sales: '日次銷售',
      lunch_sales: '午餐銷售',
      dinner_sales: '晚餐銷售',
      total_customers: '總客數',
      lunch_customers: '午餐客數',
      dinner_customers: '晚餐客數',
      total_groups: '總組數',
      lunch_groups: '午餐組數',
      dinner_groups: '晚餐組數',
      food_sales: '餐點銷售',
      drink_sales: '飲料銷售',
    },
  };
  var EXPENSE_HEADER_LABELS = {
    ja: { date: '日付', month: '年月', item: 'lineId', label: '費目', amount: '金額' },
    en: { date: 'date', month: 'month', item: 'lineId', label: 'item', amount: 'amount' },
    'zh-tw': { date: '日期', month: '年月', item: 'lineId', label: '費目', amount: '金額' },
  };
  var SALES_BTN_LABEL = {
    ja: '売上雛形をダウンロード',
    en: 'Download Sales Template',
    'zh-tw': '下載銷售範本',
  };

  function detectLang() {
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

  function csvCell(value) {
    var s = value == null ? '' : String(value);
    if (/[",\n\r]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
    return s;
  }

  function csvDumps(rows) {
    return rows
      .map(function (row) {
        return row.map(csvCell).join(',');
      })
      .join('\n') + '\n';
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

  function isRestaurantLike(businessType) {
    if (global.KpiBusinessType && typeof global.KpiBusinessType.isRestaurantLike === 'function') {
      if (businessType == null) {
        try {
          return !!global.KpiBusinessType.isRestaurantLike();
        } catch (_eLike) {}
      }
    }
    var key = String(businessType || currentBusinessType());
    if (global.KpiBusinessType && typeof global.KpiBusinessType.normalizeBusinessType === 'function') {
      try {
        key = String(global.KpiBusinessType.normalizeBusinessType(key) || key);
      } catch (_eNorm) {}
    }
    return key === 'restaurant';
  }

  function salesFieldKeys(businessType) {
    var keys = COMMON_KEYS.slice();
    if (isRestaurantLike(businessType)) keys = keys.concat(RESTAURANT_ONLY_KEYS);
    return keys;
  }

  function buildSalesTemplate(businessType, lang) {
    var loc = lang || detectLang();
    var keys = salesFieldKeys(businessType);
    var pack = SALES_LABELS[loc] || SALES_LABELS.en;
    var labels = keys.map(function (k) {
      return pack[k] || k;
    });
    return {
      kind: 'sales',
      filename: 'sales_template.csv',
      keys: keys,
      labels: labels,
      text: csvDumps([keys, labels]),
    };
  }

  function isCustomLineId(lineId) {
    return String(lineId || '').indexOf('exp_custom_') === 0;
  }

  function lineInputStyle(line) {
    var style = (line && (line.resolvedInputStyle || line.inputStyle)) || 'monthly';
    return style === 'daily' ? 'daily' : 'monthly';
  }

  function lineLabel(line, lang) {
    var loc = lang || detectLang();
    if (!line) return '';
    if (loc === 'ja') return String(line.labelJa || line.labelEn || line.lineId || '');
    if (loc === 'zh-tw') {
      return String(line.labelZh || line.labelJa || line.labelEn || line.lineId || '');
    }
    return String(line.labelEn || line.labelJa || line.lineId || '');
  }

  function unwrapCatalog(parsed) {
    if (!parsed) return [];
    if (Array.isArray(parsed)) return parsed;
    if (parsed && Array.isArray(parsed.lines)) return parsed.lines;
    return [];
  }

  function readCatalogLines() {
    try {
      var raw = global.localStorage && global.localStorage.getItem(CATALOG_KEY);
      if (!raw) return [];
      return unwrapCatalog(JSON.parse(raw));
    } catch (_e) {
      return [];
    }
  }

  function defaultCatalogLines(businessType) {
    var api = global.KpiPlExpensePresets;
    if (api && typeof api.getDefaultExpenseLines === 'function') {
      try {
        var rows = api.getDefaultExpenseLines(businessType);
        return Array.isArray(rows) ? rows : [];
      } catch (_eDef) {}
    }
    return [];
  }

  function resolveCatalogLines(catalogLines, businessType) {
    var api = global.KpiPlExpensePresets;
    var incoming = Array.isArray(catalogLines) ? catalogLines : readCatalogLines();
    if (api && typeof api.reconcileCatalogLines === 'function') {
      try {
        var reconciled = api.reconcileCatalogLines(incoming, businessType);
        if (Array.isArray(reconciled) && reconciled.length) return reconciled;
      } catch (_eRec) {}
    }
    if (incoming.length) return incoming;
    return defaultCatalogLines(businessType);
  }

  function selectActiveExpenseLines(catalogLines) {
    var seen = {};
    var out = [];
    (catalogLines || []).forEach(function (line) {
      if (!line || typeof line !== 'object') return;
      var id = String(line.lineId || '').trim();
      if (!id || seen[id]) return;
      if (line.active === false) return;
      if (line.presetOrphan) return;
      seen[id] = true;
      out.push(line);
    });
    out.sort(function (a, b) {
      var ad = lineInputStyle(a) === 'daily' ? 0 : 1;
      var bd = lineInputStyle(b) === 'daily' ? 0 : 1;
      if (ad !== bd) return ad - bd;
      var ab = String(a.bucket || '');
      var bb = String(b.bucket || '');
      if (ab !== bb) return ab < bb ? -1 : 1;
      var aso = Number(a.sortOrder) || 0;
      var bso = Number(b.sortOrder) || 0;
      if (aso !== bso) return aso - bso;
      var ai = String(a.lineId || '');
      var bi = String(b.lineId || '');
      return ai < bi ? -1 : ai > bi ? 1 : 0;
    });
    return out;
  }

  function buildExpenseTemplate(catalogLines, style, lang, businessType) {
    var want = style === 'daily' ? 'daily' : 'monthly';
    var loc = lang || detectLang();
    var bt = businessType == null ? currentBusinessType() : businessType;
    var active = selectActiveExpenseLines(resolveCatalogLines(catalogLines, bt));
    var picked = active.filter(function (line) {
      return lineInputStyle(line) === want;
    });
    var labels = EXPENSE_HEADER_LABELS[loc] || EXPENSE_HEADER_LABELS.en;
    var dateKey = want === 'daily' ? 'date' : 'month';
    var rows = [
      [dateKey, 'item', 'label', 'amount'],
      [labels[dateKey] || labels.date, labels.item, labels.label, labels.amount],
    ];
    picked.forEach(function (line) {
      rows.push(['', String(line.lineId || ''), lineLabel(line, loc), '']);
    });
    return {
      kind: 'expense-' + want,
      filename: want === 'daily' ? 'expense_daily_template.csv' : 'expense_monthly_template.csv',
      lineIds: picked.map(function (line) {
        return String(line.lineId || '');
      }),
      lines: picked,
      text: csvDumps(rows),
    };
  }

  function downloadCsv(filename, text) {
    var blob = new Blob(['\uFEFF' + text], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);
    var a = global.document.createElement('a');
    a.href = url;
    a.download = filename;
    a.rel = 'noopener';
    global.document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () {
      try {
        URL.revokeObjectURL(url);
      } catch (_eRev) {}
    }, 1000);
  }

  function templateForKind(kind) {
    var bt = currentBusinessType();
    var lang = detectLang();
    if (kind === 'sales') return buildSalesTemplate(bt, lang);
    if (kind === 'expense-daily') return buildExpenseTemplate(null, 'daily', lang, bt);
    if (kind === 'expense-monthly') return buildExpenseTemplate(null, 'monthly', lang, bt);
    return null;
  }

  function downloadKind(kind) {
    var rec = templateForKind(kind);
    if (!rec) return false;
    downloadCsv(rec.filename, rec.text);
    return true;
  }

  function kindFromExcelHref(href) {
    var s = String(href || '');
    if (/支出入力_日次|expense-import_daily/i.test(s)) return 'expense-daily';
    if (/支出入力_月次|expense-import_monthly/i.test(s)) return 'expense-monthly';
    return '';
  }

  function ensureSalesButton(menu) {
    if (!menu || menu.querySelector('#kpi-dl-csv-sales')) return;
    var heading = menu.querySelector('.template-dl-heading');
    var btn = global.document.createElement('button');
    btn.type = 'button';
    btn.id = 'kpi-dl-csv-sales';
    btn.className = 'template-dl-item';
    btn.setAttribute('role', 'menuitem');
    btn.setAttribute('data-kpi-csv-template', 'sales');
    btn.textContent = SALES_BTN_LABEL[detectLang()] || SALES_BTN_LABEL.en;
    var firstItem = menu.querySelector('.template-dl-item');
    if (firstItem) menu.insertBefore(btn, firstItem);
    else if (heading && heading.nextSibling) menu.insertBefore(btn, heading.nextSibling);
    else menu.appendChild(btn);
  }

  function onMenuClick(e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var btn = t.closest('[data-kpi-csv-template]');
    if (btn) {
      var kind = btn.getAttribute('data-kpi-csv-template');
      if (kind === 'sales' || kind === 'expense-daily' || kind === 'expense-monthly') {
        e.preventDefault();
        downloadKind(kind);
      }
      return;
    }
    var link = t.closest('a.template-dl-item[href]');
    if (!link) return;
    var fromHref = kindFromExcelHref(link.getAttribute('href'));
    if (!fromHref) return;
    e.preventDefault();
    downloadKind(fromHref);
  }

  function bindDownloadMenu(root) {
    var doc = root || global.document;
    if (!doc || doc.__kpiCsvTemplateBound) return;
    doc.__kpiCsvTemplateBound = true;
    doc.addEventListener('click', onMenuClick, true);
    var menus = doc.querySelectorAll('.template-dl-menu');
    for (var i = 0; i < menus.length; i++) ensureSalesButton(menus[i]);
  }

  global.KpiCsvTemplates = {
    __ready: true,
    CATALOG_KEY: CATALOG_KEY,
    COMMON_KEYS: COMMON_KEYS.slice(),
    RESTAURANT_ONLY_KEYS: RESTAURANT_ONLY_KEYS.slice(),
    csvDumps: csvDumps,
    salesFieldKeys: salesFieldKeys,
    buildSalesTemplate: buildSalesTemplate,
    selectActiveExpenseLines: selectActiveExpenseLines,
    resolveCatalogLines: resolveCatalogLines,
    buildExpenseTemplate: buildExpenseTemplate,
    isCustomLineId: isCustomLineId,
    downloadKind: downloadKind,
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

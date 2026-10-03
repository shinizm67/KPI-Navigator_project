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

  /* Presentation only. Does not parse files or relax the safety guard. */
  var RECOVERY_ID = 'kpi-import-recovery';
  var RECOVERY_STYLE_ID = 'kpi-import-recovery-style';
  var RECOVERY = {
    ja: {
      reasons: {
        A: '売上の列を特定できませんでした',
        B: '日付を読み取れませんでした',
        C: '売上金額を読み取れませんでした',
        D: 'この表は売上データとして判定できませんでした',
        E: 'このシートには取り込めるデータがありません',
        F: '一部のデータを安全に判定できませんでした',
      },
      expenseReason: 'この表は支出データとして判定できませんでした',
      main: 'このファイルは安全に読み取れませんでした。\nKPNの売上雛形へ、日付と売上を貼り付けて、\nもう一度アップロードしてください。',
      steps: [
        'Excel雛形をダウンロード',
        '元のファイルから「日付」と「売上」をコピー',
        '雛形の3行目から貼り付け',
        'もう一度アップロード',
      ],
      protect: '雛形の1行目と2行目はそのまま残してください。',
      date: '日付は「2026-04-01」のように、\n年も含めてください。',
      note: '合計や小計の行は貼らないでください。',
      restaurant: 'ディナー、客数、組数、フード、ドリンクも、\nあれば貼れます。\n空欄のままでも取り込めます。',
      past: '今年より前の日付を貼ってください。',
      guideFrom: '元のファイル',
      guideTo: 'KPN雛形',
      fromDate: '日付',
      fromSales: '売上',
      toDate: '日付',
      toSales: '日次売上',
      expenseDaily: '日次：日付 / 費目 / 金額',
      expenseMonthly: '月次：年月 / 費目 / 金額',
      download: 'Excel雛形をダウンロード',
      downloadCsv: 'CSV雛形',
      daily: '日次の雛形',
      monthly: '月次の雛形',
      retry: 'もう一度アップロード',
      close: '閉じる',
    },
    en: {
      reasons: {
        A: 'The sales column could not be identified',
        B: 'Dates could not be read',
        C: 'A sales amount could not be read',
        D: 'This table could not be recognized as sales',
        E: 'This sheet has no rows to import',
        F: 'Some values could not be judged safely',
      },
      expenseReason: 'This table could not be recognized as expenses',
      main: 'This file could not be read safely. Copy the date and sales into the KPN sales template, then upload it again.',
      steps: [
        'Download the Excel template',
        'Copy the date and sales from your file',
        'Paste from row 3 of the template',
        'Upload again',
      ],
      protect: 'Leave row 1 and row 2 as they are.',
      date: 'Include the year, such as 2026-04-01.',
      note: 'Do not paste total or subtotal rows.',
      restaurant: 'You can also paste dinner, customers, parties, food, and drinks. Blank cells are fine.',
      past: 'Use dates from before this year.',
      guideFrom: 'Your file',
      guideTo: 'KPN template',
      fromDate: 'Date',
      fromSales: 'Sales',
      toDate: 'Date',
      toSales: 'Daily sales',
      expenseDaily: 'Daily: date / item / amount',
      expenseMonthly: 'Monthly: month / item / amount',
      download: 'Download Excel template',
      downloadCsv: 'CSV template',
      daily: 'Daily template',
      monthly: 'Monthly template',
      retry: 'Upload again',
      close: 'Close',
    },
    'zh-tw': {
      reasons: {
        A: '無法判斷哪一欄是銷售',
        B: '無法讀取日期',
        C: '無法讀取銷售金額',
        D: '這張表無法判定為銷售資料',
        E: '這張工作表沒有可匯入的資料',
        F: '有部分資料無法安全判定',
      },
      expenseReason: '這張表無法判定為支出資料',
      main: '這個檔案無法安全讀取。請把日期和銷售金額貼到 KPN 銷售範本，再上傳一次。',
      steps: ['下載 Excel 範本', '從原本的檔案複製「日期」和「銷售」', '從範本第3列貼上', '再上傳一次'],
      protect: '範本的第1列和第2列請保持原樣。',
      date: '日期請含年份，例如 2026-04-01。',
      note: '請不要貼上合計或小計列。',
      restaurant: '也可以貼上晚餐、客數、組數、餐點、飲料。留空也可以匯入。',
      past: '請貼上今年以前的日期。',
      guideFrom: '原本的檔案',
      guideTo: 'KPN範本',
      fromDate: '日期',
      fromSales: '銷售',
      toDate: '日期',
      toSales: '日次銷售',
      expenseDaily: '每日：日期 / 項目 / 金額',
      expenseMonthly: '月度：年月 / 項目 / 金額',
      download: '下載 Excel 範本',
      downloadCsv: 'CSV 範本',
      daily: '每日範本',
      monthly: '月度範本',
      retry: '再上傳一次',
      close: '關閉',
    },
  };

  function recoveryPack() {
    return RECOVERY[locale()] || RECOVERY.en;
  }

  function ensureRecoveryStyle() {
    if (!global.document || global.document.getElementById(RECOVERY_STYLE_ID)) return;
    var css = global.document.createElement('style');
    css.id = RECOVERY_STYLE_ID;
    css.textContent =
      '#' +
      RECOVERY_ID +
      '{position:fixed;inset:0;z-index:20120;display:flex;align-items:center;justify-content:center;padding:24px;box-sizing:border-box;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__backdrop{position:absolute;inset:0;background:rgba(0,0,0,.62);}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__panel{position:relative;width:min(520px,100%);max-height:calc(100vh - 48px);overflow:auto;padding:20px 18px 16px;border:1px solid rgba(88,225,243,.55);border-radius:6px;background:#1f1e1e;color:#58e1f3;box-shadow:0 12px 40px rgba(0,0,0,.45);box-sizing:border-box;}' +
      'html[lang="ja"] #' +
      RECOVERY_ID +
      ' .kpi-import-recovery__panel{font-family:"BIZ UDPGothic",sans-serif;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__reason{margin:0 0 10px;font-size:15px;font-weight:600;line-height:1.45;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__main,#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__line{margin:0 0 10px;font-size:13px;line-height:1.5;white-space:pre-line;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__steps{margin:0 0 10px;padding-left:1.3em;font-size:13px;line-height:1.5;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__guide{width:100%;border-collapse:collapse;margin:0 0 14px;font-size:12px;line-height:1.4;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__guide th,#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__guide td{border:1px solid rgba(88,225,243,.35);padding:4px 6px;text-align:left;font-weight:400;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__actions{display:flex;flex-direction:column;gap:8px;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__btn{display:block;width:100%;padding:10px 12px;border:1px solid rgba(88,225,243,.45);border-radius:4px;background:transparent;color:inherit;font:inherit;cursor:pointer;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__btn:hover,#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__btn:focus{background:rgba(88,225,243,.12);}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__btn--quiet{width:auto;align-self:center;padding:2px 4px 6px;border:0;background:transparent;font-size:12px;line-height:1.4;text-decoration:underline;opacity:.8;}' +
      '#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__btn--quiet:hover,#' +
      RECOVERY_ID +
      ' .kpi-import-recovery__btn--quiet:focus{background:transparent;opacity:1;}' +
      'body.office-mode #' +
      RECOVERY_ID +
      ' .kpi-import-recovery__panel{background:#fff;color:#111;border-color:#ccc;}' +
      'body.office-mode #' +
      RECOVERY_ID +
      ' .kpi-import-recovery__guide th,body.office-mode #' +
      RECOVERY_ID +
      ' .kpi-import-recovery__guide td{border-color:#ccc;}' +
      'body.office-mode #' +
      RECOVERY_ID +
      ' .kpi-import-recovery__btn{border-color:#ccc;}';
    global.document.head.appendChild(css);
  }

  function closeImportRecovery() {
    var el = global.document && global.document.getElementById(RECOVERY_ID);
    if (el && el.parentNode) el.parentNode.removeChild(el);
    if (global.document) global.document.removeEventListener('keydown', onRecoveryKey, true);
  }

  function onRecoveryKey(ev) {
    if (ev.key === 'Escape') {
      ev.preventDefault();
      closeImportRecovery();
    }
  }

  function recoveryButton(id, label, onClick, extraClass) {
    var btn = global.document.createElement('button');
    btn.type = 'button';
    btn.id = id;
    btn.className = 'kpi-import-recovery__btn' + (extraClass ? ' ' + extraClass : '');
    btn.textContent = label;
    btn.addEventListener('click', onClick);
    return btn;
  }

  function downloadTemplate(kind) {
    var api = global.KpiCsvTemplates;
    if (api && typeof api.downloadKind === 'function') api.downloadKind(kind);
  }

  function xlsxUnavailableGuidance() {
    /* Same wording as the importer's existing xlsx-library alert. That alert is JA/EN only. */
    var msg =
      locale() === 'ja'
        ? 'Excel ライブラリを読み込めませんでした。CSVで保存してから再度お試しください。'
        : 'Could not load the Excel library. Save as CSV and try again.';
    try {
      global.window.alert(msg);
    } catch (_eAlert) {}
  }

  function downloadRecoveryExcel() {
    var api = global.KpiExcelTemplates;
    if (!api || typeof api.downloadRecoverySalesTemplate !== 'function') {
      xlsxUnavailableGuidance();
      return;
    }
    api.downloadRecoverySalesTemplate().catch(function () {
      xlsxUnavailableGuidance();
    });
  }

  function showImportRecovery(opts) {
    opts = opts || {};
    if (!global.document || !global.document.body) return;
    ensureRecoveryStyle();
    closeImportRecovery();
    var pack = recoveryPack();
    var kind = opts.kind === 'expense' ? 'expense' : 'sales';
    var category = String(opts.category || 'D');
    if (!pack.reasons[category]) category = 'D';
    var root = global.document.createElement('div');
    root.id = RECOVERY_ID;
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('data-recovery-kind', kind);
    root.setAttribute('data-recovery-category', category);
    root.setAttribute('data-recovery-entry', String(opts.entry || ''));
    root.setAttribute('data-recovery-restaurant', opts.restaurant ? '1' : '0');
    root.setAttribute('data-recovery-past', opts.pastSales ? '1' : '0');
    var backdrop = global.document.createElement('div');
    backdrop.className = 'kpi-import-recovery__backdrop';
    backdrop.addEventListener('click', closeImportRecovery);
    var panel = global.document.createElement('div');
    panel.className = 'kpi-import-recovery__panel';
    var reason = global.document.createElement('p');
    reason.id = 'kpi-import-recovery-reason';
    reason.className = 'kpi-import-recovery__reason';
    reason.textContent = kind === 'expense' ? pack.expenseReason : pack.reasons[category];
    panel.appendChild(reason);
    if (kind === 'sales') {
      var main = global.document.createElement('p');
      main.id = 'kpi-import-recovery-main';
      main.className = 'kpi-import-recovery__main';
      main.textContent = pack.main;
      panel.appendChild(main);
      var steps = global.document.createElement('ol');
      steps.id = 'kpi-import-recovery-steps';
      steps.className = 'kpi-import-recovery__steps';
      for (var i = 0; i < pack.steps.length; i++) {
        var li = global.document.createElement('li');
        li.textContent = pack.steps[i];
        steps.appendChild(li);
      }
      panel.appendChild(steps);
    } else {
      var dailyLine = global.document.createElement('p');
      dailyLine.id = 'kpi-import-recovery-daily';
      dailyLine.className = 'kpi-import-recovery__line';
      dailyLine.textContent = pack.expenseDaily;
      var monthlyLine = global.document.createElement('p');
      monthlyLine.id = 'kpi-import-recovery-monthly';
      monthlyLine.className = 'kpi-import-recovery__line';
      monthlyLine.textContent = pack.expenseMonthly;
      panel.appendChild(dailyLine);
      panel.appendChild(monthlyLine);
    }
    var protect = global.document.createElement('p');
    protect.id = 'kpi-import-recovery-protect';
    protect.className = 'kpi-import-recovery__line';
    protect.textContent = pack.protect;
    panel.appendChild(protect);
    if (kind === 'sales') {
      var dateLine = global.document.createElement('p');
      dateLine.id = 'kpi-import-recovery-date';
      dateLine.className = 'kpi-import-recovery__line';
      dateLine.textContent = pack.date;
      var note = global.document.createElement('p');
      note.id = 'kpi-import-recovery-note';
      note.className = 'kpi-import-recovery__line';
      note.textContent = pack.note;
      panel.appendChild(dateLine);
      panel.appendChild(note);
      if (opts.restaurant) {
        var rest = global.document.createElement('p');
        rest.id = 'kpi-import-recovery-restaurant';
        rest.className = 'kpi-import-recovery__line';
        rest.textContent = pack.restaurant;
        panel.appendChild(rest);
      }
      if (opts.pastSales) {
        var past = global.document.createElement('p');
        past.id = 'kpi-import-recovery-past';
        past.className = 'kpi-import-recovery__line';
        past.textContent = pack.past;
        panel.appendChild(past);
      }
      var table = global.document.createElement('table');
      table.id = 'kpi-import-recovery-guide';
      table.className = 'kpi-import-recovery__guide';
      table.innerHTML =
        '<thead><tr><th colspan="2"></th><th colspan="2"></th></tr></thead><tbody>' +
        '<tr><td></td><td></td><td></td><td></td></tr>' +
        '<tr><td></td><td></td><td></td><td></td></tr></tbody>';
      var heads = table.querySelectorAll('th');
      heads[0].textContent = pack.guideFrom;
      heads[1].textContent = pack.guideTo;
      var cells = table.querySelectorAll('td');
      cells[0].textContent = pack.fromDate;
      cells[1].textContent = pack.fromSales;
      cells[2].textContent = pack.toDate;
      cells[3].textContent = pack.toSales;
      cells[4].textContent = '4/1';
      cells[5].textContent = '120000';
      cells[6].textContent = '2026-04-01';
      cells[7].textContent = '120000';
      panel.appendChild(table);
    }
    var actions = global.document.createElement('div');
    actions.className = 'kpi-import-recovery__actions';
    if (kind === 'sales') {
      actions.appendChild(
        recoveryButton('kpi-import-recovery-download-sales', pack.download, function () {
          downloadRecoveryExcel();
        })
      );
      actions.appendChild(
        recoveryButton(
          'kpi-import-recovery-download-csv',
          pack.downloadCsv,
          function () {
            downloadTemplate('sales');
          },
          'kpi-import-recovery__btn--quiet'
        )
      );
    } else {
      actions.appendChild(
        recoveryButton('kpi-import-recovery-download-daily', pack.daily, function () {
          downloadTemplate('expense-daily');
        })
      );
      actions.appendChild(
        recoveryButton('kpi-import-recovery-download-monthly', pack.monthly, function () {
          downloadTemplate('expense-monthly');
        })
      );
    }
    actions.appendChild(
      recoveryButton('kpi-import-recovery-retry', pack.retry, function () {
        var retry = opts.onRetry;
        closeImportRecovery();
        if (typeof retry === 'function') retry();
      })
    );
    actions.appendChild(
      recoveryButton('kpi-import-recovery-close', pack.close, function () {
        closeImportRecovery();
      })
    );
    panel.appendChild(actions);
    root.appendChild(backdrop);
    root.appendChild(panel);
    global.document.body.appendChild(root);
    global.document.addEventListener('keydown', onRecoveryKey, true);
    var first = panel.querySelector('button');
    if (first && typeof first.focus === 'function') first.focus();
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
    showImportRecovery: showImportRecovery,
    closeImportRecovery: closeImportRecovery,
  };
})(typeof window !== 'undefined' ? window : this);

/**
 * Shared workbook layout detector + horizontal → vertical transformer.
 * CSV and XLSX both arrive as a 2D cell matrix; this module decides
 * horizontal vs vertical, then emits the existing canonical row shape
 * (date | sales | customers | parties | ...) so Vertical Importer v1
 * stays unchanged.
 *
 * BR-POST-HORIZONTAL-WORKBOOK-PARSER
 */
(function (global) {
  'use strict';

  if (global.KpiWorkbookLayout && global.KpiWorkbookLayout.__ready) {
    return;
  }

  var MIN_DATE_TOKENS = 3;

  function pad2(n) {
    return n < 10 ? '0' + n : String(n);
  }

  function isoFromYmd(y, m, d) {
    y = Number(y);
    m = Number(m);
    d = Number(d);
    if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(d)) return null;
    var dt = new Date(y, m - 1, d);
    if (dt.getFullYear() !== y || dt.getMonth() !== m - 1 || dt.getDate() !== d) return null;
    return y + '-' + pad2(m) + '-' + pad2(d);
  }

  function excelSerialToIso(n) {
    var serial = Number(n);
    if (!Number.isFinite(serial) || serial < 20000) return null;
    var base = Date.UTC(1899, 11, 30);
    var ms = base + Math.round(serial) * 86400000;
    var dt = new Date(ms);
    return isoFromYmd(dt.getUTCFullYear(), dt.getUTCMonth() + 1, dt.getUTCDate());
  }

  function parseDateCell(raw) {
    if (raw == null || raw === '') return null;
    if (typeof raw === 'number') return excelSerialToIso(raw);
    var s = String(raw).trim();
    if (!s) return null;
    if (/^\d{4,5}(\.\d+)?$/.test(s)) {
      var fromSerial = excelSerialToIso(Number(s));
      if (fromSerial) return fromSerial;
    }
    var iso = s.match(/^(\d{4})[\/\-.](\d{1,2})[\/\-.](\d{1,2})/);
    if (iso) return isoFromYmd(iso[1], iso[2], iso[3]);
    var loose = s.match(/(\d{4})\D+(\d{1,2})\D+(\d{1,2})/);
    if (loose) return isoFromYmd(loose[1], loose[2], loose[3]);
    return null;
  }

  function cellText(v) {
    if (v == null) return '';
    return String(v).replace(/^\uFEFF/, '').trim();
  }

  function norm(v) {
    return cellText(v)
      .toLowerCase()
      .replace(/[\s_]+/g, '');
  }

  function parseNumber(raw) {
    if (raw == null || raw === '') return { missing: true };
    if (typeof raw === 'number') {
      if (!Number.isFinite(raw)) return { missing: true };
      return { value: raw };
    }
    var s = cellText(raw);
    if (!s) return { missing: true };
    if (/^#(N\/A|VALUE!|REF!|DIV\/0!|NAME\?)$/i.test(s)) return { missing: true };
    var neg = /^\(.*\)$/.test(s);
    s = s.replace(/[¥￥$,\s]/g, '');
    if (neg) s = s.replace(/[()]/g, '');
    if (!s || s === '-' || s === '—' || s === '–') return { missing: true };
    if (/%$/.test(s)) return { missing: true };
    s = s.replace(/[()]/g, '');
    var n = Number(s);
    if (!Number.isFinite(n)) return { missing: true };
    if (neg) n = -Math.abs(n);
    return { value: n };
  }

  function isTotalLike(raw) {
    var n = norm(raw);
    if (!n) return false;
    if (n === '合計' || n === '計' || n === 'total' || n === 'grandtotal') return true;
    if (n === '月間合計' || n === '月間' || n === 'monthlytotal') return true;
    return false;
  }

  function classifyPeriod(raw) {
    var n = norm(raw);
    if (!n) return '';
    if (n === 'ランチ' || n === 'lunch') return 'lunch';
    if (n === 'ディナー' || n === 'dinner') return 'dinner';
    if (
      n === '全日' ||
      n === '終日' ||
      n === '通日' ||
      n === '終日計' ||
      n === 'fullday' ||
      n === 'allday' ||
      n === 'wholeday' ||
      n === '終日合計'
    ) {
      return 'full';
    }
    if (n === '件数' || n === 'count' || n === 'qty') return 'count';
    if (n === '金額' || n === 'amount') return 'amount';
    return '';
  }

  function scanDateRow(rows) {
    var best = null;
    var limit = Math.min(rows.length, 20);
    for (var r = 0; r < limit; r++) {
      var row = rows[r] || [];
      var cols = [];
      for (var c = 0; c < row.length; c++) {
        if (isTotalLike(row[c])) continue;
        var iso = parseDateCell(row[c]);
        if (iso) cols.push({ c: c, iso: iso });
      }
      if (!best || cols.length > best.cols.length) best = { row: r, cols: cols };
    }
    if (!best || best.cols.length < MIN_DATE_TOKENS) return null;
    best.cols = keepSheetMonthCols(best.cols, rows);
    if (!best.cols.length || best.cols.length < MIN_DATE_TOKENS) return null;
    return best;
  }

  function yearMonthKey(iso) {
    return String(iso || '').slice(0, 7);
  }

  function readLabeledYearMonth(rows) {
    var year = 0;
    var month = 0;
    var limit = Math.min((rows && rows.length) || 0, 12);
    for (var r = 0; r < limit; r++) {
      var row = rows[r] || [];
      for (var c = 0; c < Math.min(row.length, 4); c++) {
        var t = cellText(row[c]);
        var yHit = t.match(/^(\d{4})\s*年$/);
        if (yHit) year = Number(yHit[1]);
        var mHit = t.match(/^(\d{1,2})\s*月$/);
        if (mHit) month = Number(mHit[1]);
      }
    }
    if (year >= 1900 && month >= 1 && month <= 12) return year + '-' + pad2(month);
    return '';
  }

  function dominantYearMonth(cols) {
    var counts = {};
    var best = '';
    var bestN = 0;
    for (var i = 0; i < cols.length; i++) {
      var k = yearMonthKey(cols[i].iso);
      if (!k) continue;
      counts[k] = (counts[k] || 0) + 1;
      if (counts[k] > bestN) {
        bestN = counts[k];
        best = k;
      }
    }
    return best;
  }

  function keepSheetMonthCols(cols, rows) {
    if (!cols || !cols.length) return cols || [];
    var labeled = readLabeledYearMonth(rows);
    var ym = labeled || dominantYearMonth(cols);
    if (!ym) return cols;
    var kept = [];
    for (var i = 0; i < cols.length; i++) {
      if (yearMonthKey(cols[i].iso) === ym) kept.push(cols[i]);
    }
    if (kept.length) return kept;
    return labeled ? [] : cols;
  }

  function reconstructFromYearMonthDay(rows) {
    var year = 0;
    var month = 0;
    var dayRow = -1;
    var days = [];
    var limit = Math.min(rows.length, 12);
    for (var r = 0; r < limit; r++) {
      var row = rows[r] || [];
      for (var c = 0; c < Math.min(row.length, 4); c++) {
        var t = cellText(row[c]);
        var ym = t.match(/^(\d{4})\s*年$/);
        if (ym) year = Number(ym[1]);
        var mm = t.match(/^(\d{1,2})\s*月$/);
        if (mm) month = Number(mm[1]);
      }
      var dayCols = [];
      for (var c2 = 0; c2 < row.length; c2++) {
        var dt = cellText(row[c2]).match(/^(\d{1,2})\s*日$/);
        if (dt) dayCols.push({ c: c2, d: Number(dt[1]) });
      }
      if (dayCols.length >= MIN_DATE_TOKENS && dayCols.length > days.length) {
        days = dayCols;
        dayRow = r;
      }
    }
    if (!year || !month || days.length < MIN_DATE_TOKENS) return null;
    var cols = [];
    for (var i = 0; i < days.length; i++) {
      var iso = isoFromYmd(year, month, days[i].d);
      if (iso) cols.push({ c: days[i].c, iso: iso });
    }
    if (cols.length < MIN_DATE_TOKENS) return null;
    cols = keepSheetMonthCols(cols, rows);
    if (cols.length < MIN_DATE_TOKENS) return null;
    return { row: dayRow, cols: cols };
  }

  function detectDateAxis(rows) {
    return scanDateRow(rows) || reconstructFromYearMonthDay(rows);
  }

  function isPeriodRow(row, dateCols) {
    if (!row || !dateCols || !dateCols.length) return false;
    var hits = 0;
    for (var i = 0; i < dateCols.length; i++) {
      var c = dateCols[i].c;
      if (classifyPeriod(row[c]) || classifyPeriod(row[c + 1])) hits++;
    }
    return hits >= Math.max(3, Math.floor(dateCols.length * 0.4));
  }

  function isBlankRow(row) {
    if (!row) return true;
    for (var i = 0; i < row.length; i++) {
      if (cellText(row[i])) return false;
    }
    return true;
  }

  var WEEKDAY = {
    月: 1,
    火: 1,
    水: 1,
    木: 1,
    金: 1,
    土: 1,
    日: 1,
    mon: 1,
    tue: 1,
    wed: 1,
    thu: 1,
    fri: 1,
    sat: 1,
    sun: 1,
    monday: 1,
    tuesday: 1,
    wednesday: 1,
    thursday: 1,
    friday: 1,
    saturday: 1,
    sunday: 1,
  };

  function weekdayOnly(row) {
    var n = 0;
    var w = 0;
    if (!row) return false;
    for (var i = 0; i < row.length; i++) {
      var t = cellText(row[i]);
      if (!t) continue;
      n++;
      var k = norm(t);
      if (WEEKDAY[t] || WEEKDAY[k] || WEEKDAY[k.slice(0, 3)]) w++;
    }
    return n > 5 && w / n > 0.6;
  }

  function metricKind(label) {
    var n = norm(label);
    if (!n) return '';
    if (/^-?\d+(\.\d+)?$/.test(n)) return 'skip';
    if (/^[¥￥]/.test(cellText(label)) && !/[a-zA-Zぁ-んァ-ン一-龥]/.test(cellText(label))) {
      return 'skip';
    }
    if (
      n === '天気' ||
      n === 'weather' ||
      n === '売上明細' ||
      n === 'クレジット明細' ||
      n === '金券' ||
      n === '↑'
    ) {
      return 'skip';
    }
    if (n.indexOf('推定') >= 0 || n.indexOf('適正') >= 0 || n.indexOf('考察') >= 0) return 'skip';
    if (n.indexOf('原価率') >= 0) return 'skip';
    if (n === '割引' || n === '値引') return 'skip';
    if (n.indexOf('アルバイト人数') >= 0) return 'skip';
    if (n === '時給' || n === '時間' || n === '交通費') return 'skip';
    if (n.indexOf('固定費月額') >= 0) return 'skip';
    if (n.indexOf('節約') >= 0) return 'skip';

    if (
      n === '総売上' ||
      n === '日次売上' ||
      n === '店舗売上' ||
      n === 'dailysales' ||
      n === 'storesales' ||
      n === 'netsales' ||
      n === 'grosssales'
    ) {
      return 'sales';
    }
    if (n === '組数' || n === '総組数' || n === 'トータル組数' || n === 'totalgroups' || n === 'totalparties') {
      return 'parties';
    }
    if (n === '客数' || n === '総客数' || n === 'トータル客数' || n === 'totalcustomers') {
      return 'customers';
    }
    if (n === 'フード売上' || n === '食売上' || n === 'foodsales' || n === 'food') return 'food';
    if (n === 'ドリンク売上' || n === '飲料売上' || n === 'drinksales' || n === 'drink' || n === 'beveragesales') {
      return 'drink';
    }
    if (n === 'ランチ売上' || n === 'lunchsales') return 'lunch_sales';
    if (n === 'ディナー売上' || n === 'dinnersales') return 'dinner_sales';

    if (n.indexOf('推定') < 0 && (n.indexOf('仕入') >= 0 || n.indexOf('人件費') >= 0)) {
      return 'expense';
    }

    return 'unknown';
  }

  function labelFromRow(row, labelCol) {
    var a = cellText(row[labelCol]);
    if (a) return a;
    for (var c = 0; c <= 2; c++) {
      var t = cellText(row[c]);
      if (t && !parseDateCell(t) && classifyPeriod(t) === '') return t;
    }
    return '';
  }

  function findLabelCol(rows, dateAxis, dataStart) {
    var firstDateCol = dateAxis.cols[0] ? dateAxis.cols[0].c : 2;
    var scores = [0, 0, 0];
    var end = Math.min(rows.length, dataStart + 50);
    for (var r = dataStart; r < end; r++) {
      var row = rows[r] || [];
      for (var c = 0; c < 3; c++) {
        if (c >= firstDateCol) continue;
        var k = metricKind(cellText(row[c]));
        if (k && k !== 'skip' && k !== 'unknown') scores[c]++;
      }
    }
    var best = 0;
    for (var i = 1; i < 3; i++) {
      if (scores[i] > scores[best]) best = i;
    }
    if (scores[best] === 0) return Math.min(1, Math.max(0, firstDateCol - 1));
    return best;
  }

  function buildGroups(dateAxis) {
    var cols = dateAxis.cols.slice().sort(function (a, b) {
      return a.c - b.c;
    });
    var groups = [];
    for (var i = 0; i < cols.length; i++) {
      var cur = cols[i];
      var next = cols[i + 1];
      var width = next ? next.c - cur.c : 2;
      if (width < 1) width = 1;
      if (width > 4) width = 2;
      groups.push({ c: cur.c, iso: cur.iso, width: width });
    }
    return groups;
  }

  function periodSlotsFor(periodRow, group) {
    var slots = { lunch: -1, dinner: -1, full: -1, amount: -1, count: -1 };
    if (!periodRow) return slots;
    for (var w = 0; w < group.width; w++) {
      var p = classifyPeriod(periodRow[group.c + w]);
      if (p && slots[p] < 0) slots[p] = group.c + w;
    }
    return slots;
  }

  function pickCell(row, group, slots, kind) {
    if (kind === 'lunch' && slots.lunch >= 0) return parseNumber(row[slots.lunch]);
    if (slots.full >= 0 || slots.dinner >= 0 || slots.lunch >= 0) {
      var primary = slots.full >= 0 ? slots.full : slots.dinner >= 0 ? slots.dinner : slots.lunch;
      return parseNumber(row[primary]);
    }
    if (slots.amount >= 0 && kind !== 'count') return parseNumber(row[slots.amount]);
    if (slots.count >= 0 && kind === 'count') return parseNumber(row[slots.count]);
    return parseNumber(row[group.c]);
  }

  var DATE_HEADER_KEYS = [
    'date',
    '日付',
    '日にち',
    '年月日',
    '営業日付',
    'transactiondate',
    'salesdate',
    '費目',
    'item',
  ];

  function headerLooksVertical(header) {
    var nameHits = 0;
    var tokenHits = 0;
    for (var c = 0; c < header.length; c++) {
      var n = norm(header[c]);
      if (parseDateCell(header[c])) tokenHits++;
      for (var k = 0; k < DATE_HEADER_KEYS.length; k++) {
        var key = DATE_HEADER_KEYS[k];
        if (n === key) {
          nameHits++;
          break;
        }
      }
    }
    return nameHits > 0 && tokenHits < MIN_DATE_TOKENS;
  }

  function countMetricLabels(rows, dateAxis) {
    if (!dateAxis || !dateAxis.cols.length) return 0;
    var firstDateCol = dateAxis.cols[0].c;
    var n = 0;
    var limit = Math.min(rows.length, 50);
    for (var r = 0; r < limit; r++) {
      var row = rows[r] || [];
      for (var c = 0; c < Math.min(3, firstDateCol); c++) {
        var k = metricKind(cellText(row[c]));
        if (k === 'sales' || k === 'customers' || k === 'parties' || k === 'food' || k === 'drink' || k === 'expense') {
          n++;
        }
      }
    }
    return n;
  }

  function detectLayout(rows) {
    if (!rows || !rows.length) return 'empty';
    var header = rows[0] || [];
    if (headerLooksVertical(header)) return 'vertical';
    var axis = detectDateAxis(rows);
    if (axis && axis.cols.length >= MIN_DATE_TOKENS) {
      var labels = countMetricLabels(rows, axis);
      var headerTokens = 0;
      for (var c = 0; c < header.length; c++) {
        if (parseDateCell(header[c])) headerTokens++;
      }
      if (labels >= 2 || headerTokens >= MIN_DATE_TOKENS) return 'horizontal';
    }
    return 'vertical';
  }

  function transform(rows) {
    var axis = detectDateAxis(rows);
    if (!axis) return null;
    var groups = buildGroups(axis);
    var currentPeriod = null;
    var labelCol = findLabelCol(rows, axis, axis.row + 1);
    var byIso = {};
    var unknown = [];

    for (var r = 0; r < rows.length; r++) {
      var row = rows[r] || [];
      if (r === axis.row) continue;
      if (isBlankRow(row)) {
        currentPeriod = null;
        continue;
      }
      if (isPeriodRow(row, axis.cols)) {
        currentPeriod = row;
        continue;
      }
      if (weekdayOnly(row)) continue;
      var label = labelFromRow(row, labelCol);
      if (!label) continue;
      if (/^\d{4}\s*年$/.test(label) || /^\d{1,2}\s*月$/.test(label)) continue;
      var kind = metricKind(label);
      if (kind === 'skip') continue;

      for (var g = 0; g < groups.length; g++) {
        var group = groups[g];
        if (!byIso[group.iso]) byIso[group.iso] = { iso: group.iso };
        var rec = byIso[group.iso];
        var slots = periodSlotsFor(currentPeriod, group);
        var cell;
        if (kind === 'sales' || kind === 'customers' || kind === 'parties' || kind === 'food' || kind === 'drink') {
          cell = pickCell(row, group, slots, kind);
          if (!cell.missing && rec[kind] == null) rec[kind] = cell.value;
          if (kind === 'sales' && slots.lunch >= 0 && (slots.full >= 0 || slots.dinner >= 0)) {
            var lunchCell = parseNumber(row[slots.lunch]);
            if (!lunchCell.missing && rec.lunch_sales == null) rec.lunch_sales = lunchCell.value;
            if (slots.dinner >= 0) {
              var dCell = parseNumber(row[slots.dinner]);
              if (!dCell.missing && rec.dinner_sales == null) rec.dinner_sales = dCell.value;
            } else if (slots.full >= 0 && !lunchCell.missing && rec.sales != null && rec.dinner_sales == null) {
              var dinnerEst = rec.sales - lunchCell.value;
              if (dinnerEst >= 0) rec.dinner_sales = dinnerEst;
            }
          }
        } else if (kind === 'lunch_sales' || kind === 'dinner_sales') {
          cell = pickCell(row, group, slots, kind === 'lunch_sales' ? 'lunch' : kind);
          if (!cell.missing && rec[kind] == null) rec[kind] = cell.value;
        } else if (kind === 'expense' || kind === 'unknown') {
          var pickKind = slots.amount >= 0 ? 'amount' : kind;
          cell = pickCell(row, group, slots, pickKind);
          if (cell.missing) continue;
          unknown.push({ iso: group.iso, label: label, amount: cell.value, kind: kind });
        }
      }
    }
    return { byIso: byIso, unknown: unknown, groups: groups };
  }

  function toVerticalSalesRows(rows) {
    var t = transform(rows);
    if (!t) return { rows: rows, unknown: [], layout: 'horizontal' };
    var header = [
      '日付',
      '日次売上',
      'トータル客数',
      'トータル組数',
      'ランチ売上',
      'ディナー売上',
      'フード売上',
      'ドリンク売上',
    ];
    var out = [header];
    var isos = Object.keys(t.byIso).sort();
    for (var i = 0; i < isos.length; i++) {
      var rec = t.byIso[isos[i]];
      if (rec.sales == null && rec.customers == null && rec.parties == null) continue;
      out.push([
        rec.iso,
        rec.sales != null ? Math.round(rec.sales) : '',
        rec.customers != null ? Math.round(rec.customers) : '',
        rec.parties != null ? Math.round(rec.parties) : '',
        rec.lunch_sales != null ? Math.round(rec.lunch_sales) : '',
        rec.dinner_sales != null ? Math.round(rec.dinner_sales) : '',
        rec.food != null ? Math.round(rec.food) : '',
        rec.drink != null ? Math.round(rec.drink) : '',
      ]);
    }
    return { rows: out, unknown: t.unknown, layout: 'horizontal' };
  }

  function expenseLikeUnknown(u) {
    if (!u) return false;
    if (u.kind === 'expense') return true;
    var n = norm(u.label);
    if (n.indexOf('仕入') >= 0) return true;
    if (n.indexOf('人件費') >= 0 && n.indexOf('推定') < 0) return true;
    return false;
  }

  function toVerticalExpenseRows(rows) {
    var t = transform(rows);
    if (!t) return { rows: rows, unknown: [], layout: 'horizontal' };
    var out = [['日付', '費目', '金額']];
    for (var i = 0; i < t.unknown.length; i++) {
      var u = t.unknown[i];
      if (!expenseLikeUnknown(u)) continue;
      out.push([u.iso, u.label, u.amount]);
    }
    return { rows: out, unknown: t.unknown, layout: 'horizontal' };
  }

  function prepare(rows, kind) {
    var layout = detectLayout(rows);
    if (layout !== 'horizontal') {
      return { rows: rows, layout: layout, unknown: [] };
    }
    if (kind === 'expense') return toVerticalExpenseRows(rows);
    return toVerticalSalesRows(rows);
  }

  function hasOwn(obj, key) {
    return !!(obj && Object.prototype.hasOwnProperty.call(obj, key));
  }

  function nonzeroAmount(map, iso) {
    if (!hasOwn(map, iso)) return false;
    var n = Number(map[iso]);
    return Number.isFinite(n) && n !== 0;
  }

  function ensureMap(maps, key) {
    if (!maps[key] || typeof maps[key] !== 'object' || Array.isArray(maps[key])) {
      maps[key] = {};
    }
    return maps[key];
  }

  function resolveToday(opts) {
    if (opts && opts.today instanceof Date && !isNaN(opts.today.getTime())) {
      return opts.today;
    }
    if (opts && typeof opts.today === 'string') {
      var parsed = parseDateCell(opts.today) || String(opts.today).trim();
      var m = String(parsed).match(/^(\d{4})-(\d{2})-(\d{2})/);
      if (m) return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
    }
    return new Date();
  }

  function lastDayOfMonth(y, m) {
    var d;
    for (d = 31; d >= 28; d--) {
      if (isoFromYmd(y, m, d)) return d;
    }
    return 0;
  }

  function isoParts(iso) {
    var m = String(iso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!m) return null;
    var y = Number(m[1]);
    var mo = Number(m[2]);
    var d = Number(m[3]);
    if (!isoFromYmd(y, mo, d)) return null;
    return { y: y, m: mo, d: d };
  }

  function todayIso(opts) {
    var today = resolveToday(opts);
    return isoFromYmd(today.getFullYear(), today.getMonth() + 1, today.getDate());
  }

  function isImportableMonth(y, m, opts) {
    var today = resolveToday(opts);
    var ty = today.getFullYear();
    var tm = today.getMonth() + 1;
    if (y > ty) return false;
    if (y === ty && m > tm) return false;
    return true;
  }

  function collectMonthsFromMaps(maps) {
    var months = {};
    function addIso(iso) {
      var p = isoParts(iso);
      if (!p) return;
      months[p.y + '-' + pad2(p.m)] = { y: p.y, m: p.m };
    }
    function addFrom(map) {
      if (!map || typeof map !== 'object') return;
      Object.keys(map).forEach(addIso);
    }
    addFrom(maps.salesByDate);
    addFrom(maps.businessDayByDate);
    addFrom(maps.totalCustomersByDate);
    addFrom(maps.totalGroupsByDate);
    addFrom(maps.lunchSalesByDate);
    addFrom(maps.dinnerSalesByDate);
    addFrom(maps.foodByDate);
    addFrom(maps.drinkByDate);
    addFrom(maps.expenseByDate);
    var list = maps.unmatchedMetrics || maps.unknown || [];
    var i;
    for (i = 0; i < list.length; i++) {
      if (list[i] && list[i].iso) addIso(list[i].iso);
    }
    return months;
  }

  function inferHistoricalBusinessDay(maps, iso) {
    if (!maps || !iso) return false;
    return (
      nonzeroAmount(maps.salesByDate, iso) ||
      nonzeroAmount(maps.totalCustomersByDate, iso) ||
      nonzeroAmount(maps.lunchCustomersByDate, iso) ||
      nonzeroAmount(maps.dinnerCustomersByDate, iso) ||
      nonzeroAmount(maps.totalGroupsByDate, iso) ||
      nonzeroAmount(maps.lunchGroupsByDate, iso) ||
      nonzeroAmount(maps.dinnerGroupsByDate, iso) ||
      nonzeroAmount(maps.lunchSalesByDate, iso) ||
      nonzeroAmount(maps.dinnerSalesByDate, iso) ||
      nonzeroAmount(maps.foodByDate, iso) ||
      nonzeroAmount(maps.drinkByDate, iso)
    );
  }

  function expenseAmountOnIso(maps, iso) {
    var total = 0;
    if (nonzeroAmount(maps.expenseByDate, iso)) total += Number(maps.expenseByDate[iso]);
    if (nonzeroAmount(maps.expenseAmountByDate, iso)) total += Number(maps.expenseAmountByDate[iso]);
    var list = maps.unmatchedMetrics || maps.unknown || [];
    var i;
    for (i = 0; i < list.length; i++) {
      var u = list[i];
      if (!u || u.iso !== iso) continue;
      if (u.kind === 'expense' || expenseLikeUnknown(u)) {
        var n = Number(u.amount);
        if (Number.isFinite(n) && n !== 0) total += n;
      }
    }
    return total;
  }

  function snapshotUnresolvedDay(maps, iso, reason) {
    return {
      sales: hasOwn(maps.salesByDate, iso) ? Number(maps.salesByDate[iso]) || 0 : 0,
      customers: hasOwn(maps.totalCustomersByDate, iso) ? Number(maps.totalCustomersByDate[iso]) || 0 : 0,
      parties: hasOwn(maps.totalGroupsByDate, iso) ? Number(maps.totalGroupsByDate[iso]) || 0 : 0,
      lunch: hasOwn(maps.lunchSalesByDate, iso) ? Number(maps.lunchSalesByDate[iso]) || 0 : 0,
      dinner: hasOwn(maps.dinnerSalesByDate, iso) ? Number(maps.dinnerSalesByDate[iso]) || 0 : 0,
      food: hasOwn(maps.foodByDate, iso) ? Number(maps.foodByDate[iso]) || 0 : 0,
      drink: hasOwn(maps.drinkByDate, iso) ? Number(maps.drinkByDate[iso]) || 0 : 0,
      expense: expenseAmountOnIso(maps, iso),
      reason: reason || 'unresolved',
    };
  }

  function recountImportMeta(maps) {
    var years = {};
    var n = 0;
    Object.keys(maps.salesByDate || {}).forEach(function (iso) {
      var p = isoParts(iso);
      if (!p) return;
      years[p.y] = true;
      n++;
    });
    maps.imported = n;
    maps.years = Object.keys(years)
      .map(Number)
      .filter(Number.isFinite)
      .sort(function (a, b) {
        return a - b;
      });
  }

  /**
   * Shared post-parse calendar + business-day classification (Replace contract).
   * For dates in the imported calendar (importable months, up to today):
   * Open: operational activity non-zero.
   * Closed: all operational activity 0/blank, no expense — overwrites existing KPN state.
   * Unresolved: no operational activity but expense (or other unsafe signal).
   * Future dates: do not classify; do not modify.
   */
  function completeHistoricalImport(maps, opts) {
    if (!maps || typeof maps !== 'object') return maps;
    opts = opts || {};
    ensureMap(maps, 'salesByDate');
    ensureMap(maps, 'businessDayByDate');
    ensureMap(maps, 'unresolvedBusinessDayByDate');
    var limitIso = todayIso(opts);
    var months = collectMonthsFromMaps(maps);
    var keys = Object.keys(months);
    var i;
    for (i = 0; i < keys.length; i++) {
      var rec = months[keys[i]];
      if (!isImportableMonth(rec.y, rec.m, opts)) {
        var lastSkip = lastDayOfMonth(rec.y, rec.m);
        var ds;
        for (ds = 1; ds <= lastSkip; ds++) {
          var skipIso = isoFromYmd(rec.y, rec.m, ds);
          if (skipIso && hasOwn(maps.businessDayByDate, skipIso)) {
            delete maps.businessDayByDate[skipIso];
          }
        }
        continue;
      }
      var last = lastDayOfMonth(rec.y, rec.m);
      var d;
      for (d = 1; d <= last; d++) {
        var iso = isoFromYmd(rec.y, rec.m, d);
        if (!iso) continue;
        if (limitIso && iso > limitIso) {
          if (hasOwn(maps.businessDayByDate, iso)) delete maps.businessDayByDate[iso];
          continue;
        }
        if (!hasOwn(maps.salesByDate, iso)) {
          maps.salesByDate[iso] = 0;
        }
        if (inferHistoricalBusinessDay(maps, iso)) {
          maps.businessDayByDate[iso] = true;
          if (hasOwn(maps.unresolvedBusinessDayByDate, iso)) {
            delete maps.unresolvedBusinessDayByDate[iso];
          }
          continue;
        }
        var expenseN = expenseAmountOnIso(maps, iso);
        if (expenseN !== 0) {
          if (hasOwn(maps.businessDayByDate, iso)) delete maps.businessDayByDate[iso];
          maps.unresolvedBusinessDayByDate[iso] = snapshotUnresolvedDay(maps, iso, 'expense-only');
          continue;
        }
        maps.businessDayByDate[iso] = false;
        if (hasOwn(maps.unresolvedBusinessDayByDate, iso)) {
          delete maps.unresolvedBusinessDayByDate[iso];
        }
      }
    }
    recountImportMeta(maps);
    return maps;
  }

  function importedClassification(maps, iso) {
    if (!maps || !iso) return 'omit';
    if (maps.unresolvedBusinessDayByDate && hasOwn(maps.unresolvedBusinessDayByDate, iso)) {
      return 'unresolved';
    }
    if (maps.businessDayByDate && hasOwn(maps.businessDayByDate, iso)) {
      return maps.businessDayByDate[iso] ? 'open' : 'closed';
    }
    return 'omit';
  }

  function existingClassification(existing, iso) {
    if (!existing || !iso) return null;
    var unresolved = existing.businessDayUnresolved || existing.unresolvedBusinessDayByDate || {};
    if (hasOwn(unresolved, iso)) return 'unresolved';
    var biz = existing.businessDays || existing.businessDayByDate || {};
    if (hasOwn(biz, iso)) return biz[iso] ? 'open' : 'closed';
    return null;
  }

  function salesNumber(map, iso) {
    if (!map || !hasOwn(map, iso)) return null;
    var n = Number(map[iso]);
    return Number.isFinite(n) ? n : 0;
  }

  /**
   * Meaningful conflicts between classified import maps and current KPN state.
   * Unset existing + imported fill is not a conflict (first write).
   */
  function diffHistoricalImport(maps, existing) {
    var diffs = [];
    if (!maps || typeof maps !== 'object') return diffs;
    existing = existing || {};
    var existingSales = existing.salesByDate || existing.dailySales || {};
    var salesMap = maps.salesByDate || {};
    Object.keys(salesMap).forEach(function (iso) {
      var importedSales = salesNumber(salesMap, iso);
      if (importedSales == null) importedSales = 0;
      var existingAmt = salesNumber(existingSales, iso);
      var importedClass = importedClassification(maps, iso);
      if (importedClass === 'omit') return;
      var existingClass = existingClassification(existing, iso);
      var salesDiff = existingAmt != null && existingAmt !== importedSales;
      var classDiff = existingClass != null && existingClass !== importedClass;
      if (!salesDiff && !classDiff) return;
      diffs.push({
        iso: iso,
        existingSales: existingAmt,
        importedSales: importedSales,
        existingClass: existingClass,
        importedClass: importedClass,
      });
    });
    diffs.sort(function (a, b) {
      return String(a.iso).localeCompare(String(b.iso));
    });
    return diffs;
  }

  global.KpiWorkbookLayout = {
    __ready: true,
    detectLayout: detectLayout,
    toVerticalSalesRows: toVerticalSalesRows,
    toVerticalExpenseRows: toVerticalExpenseRows,
    prepare: prepare,
    parseDateCell: parseDateCell,
    isoFromYmd: isoFromYmd,
    lastDayOfMonth: lastDayOfMonth,
    inferHistoricalBusinessDay: inferHistoricalBusinessDay,
    completeHistoricalImport: completeHistoricalImport,
    diffHistoricalImport: diffHistoricalImport,
    importedClassification: importedClassification,
  };
})(typeof window !== 'undefined' ? window : typeof globalThis !== 'undefined' ? globalThis : this);

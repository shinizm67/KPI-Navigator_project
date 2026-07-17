"""PL expense CSV/Excel import (template long-format: date / item / amount).

Inserted as an f-string expression `{pl_expense_import_client_js()}` inside the
big PL page IIFE in ``build_pl_table_page.py``. Because it is a *substituted
value*, the returned JS uses plain single braces (it is not re-parsed for
f-string braces).

The snippet runs inside the PL toolbar IIFE, so it closes over: ``plYear``,
``isJa``, ``t``, ``formatMoney``, ``pad2`` and ``btnCsv``. Cross-client calls go
through the stable ``window.__pl*`` globals.

Role split (decided 2026-07-18): PL owns expenses, Monthly Edit / Annual Sales
Data own income. So the PL "Upload Expenses" button imports expenses directly
(no income/expense chooser). See docs/expense-csv-excel-import-memo.md #3/#4.

Slice 1 scope:
- Expense import of the fixed template long format only (date, item, amount).
- Item -> catalog line by exact (normalized) label match; unmatched are skipped
  and reported (the "篩" principle). Column-mapping UI + auto-creating new
  catalog lines are a later slice.
- Monthly rows (YYYY-MM) -> kpi-pl-expenses-v1:{year}. Daily rows (YYYY-MM-DD)
  for daily-style lines -> kpiYearStore years[y].dailyExpenses[lineId][iso].
"""

from __future__ import annotations


def pl_expense_import_client_js() -> str:
    """JS snippet (single braces; inserted verbatim via f-string expression)."""
    return """
      /* ===== PL 支出 CSV/Excel 取込（雛形: 日付 / 費目 / 金額） ===== */
      (function () {
        var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
        var YEAR_STORE_KEY = 'kpiNavigator.kpiYearStore';
        var PL_EXP_PREFIX = 'kpi-pl-expenses-v1:';
        var XLSX_URL = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';

        var fileInput = null;

        function tt(ja, en) {
          return typeof t === 'function' ? t(ja, en) : (document.documentElement.lang === 'ja' ? ja : en);
        }
        function money(n) {
          return typeof formatMoney === 'function'
            ? formatMoney(Math.round(Number(n) || 0))
            : String(Math.round(Number(n) || 0));
        }
        function pad(n) {
          return typeof pad2 === 'function' ? pad2(n) : (n < 10 ? '0' + n : String(n));
        }

        /* ---------- parsing helpers ---------- */
        function normText(v) {
          return String(v == null ? '' : v).replace(/\\s+/g, '').toLowerCase();
        }
        function parseAmount(v) {
          if (typeof v === 'number' && isFinite(v)) return Math.round(v);
          var raw = String(v == null ? '' : v).replace(/[^0-9.\\-]/g, '');
          if (!raw || raw === '-' || raw === '.') return 0;
          var n = Number(raw);
          return isFinite(n) ? Math.round(n) : 0;
        }
        /** -> 'YYYY-MM-DD' (daily) | 'YYYY-MM' (monthly) | null */
        function normDate(v) {
          if (typeof v === 'number' && isFinite(v) && v > 20000 && v < 100000) {
            var ms = Date.UTC(1899, 11, 30) + Math.round(v) * 86400000;
            var d = new Date(ms);
            return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
          }
          var s = String(v == null ? '' : v).trim();
          if (!s) return null;
          s = s.replace(/[\\/.]/g, '-');
          var md = s.match(/^(\\d{4})-(\\d{1,2})-(\\d{1,2})$/);
          if (md) {
            return md[1] + '-' + pad(Number(md[2])) + '-' + pad(Number(md[3]));
          }
          var mm = s.match(/^(\\d{4})-(\\d{1,2})$/);
          if (mm) {
            return mm[1] + '-' + pad(Number(mm[2]));
          }
          return null;
        }
        function detectDelimiter(sample) {
          var line = String(sample || '').split(/\\r\\n|\\r|\\n/)[0] || '';
          var counts = { ',': 0, '\\t': 0, ';': 0 };
          for (var i = 0; i < line.length; i++) {
            var ch = line.charAt(i);
            if (counts.hasOwnProperty(ch)) counts[ch]++;
          }
          var best = ',';
          var bestN = -1;
          Object.keys(counts).forEach(function (k) {
            if (counts[k] > bestN) { bestN = counts[k]; best = k; }
          });
          return best;
        }
        function splitLine(line, delim) {
          var out = [];
          var cur = '';
          var inQ = false;
          for (var i = 0; i < line.length; i++) {
            var ch = line.charAt(i);
            if (inQ) {
              if (ch === '"') {
                if (line.charAt(i + 1) === '"') { cur += '"'; i++; }
                else inQ = false;
              } else cur += ch;
            } else if (ch === '"') {
              inQ = true;
            } else if (ch === delim) {
              out.push(cur); cur = '';
            } else cur += ch;
          }
          out.push(cur);
          return out.map(function (c) { return c.trim(); });
        }
        function parseText(text) {
          var clean = String(text || '').replace(/^\\uFEFF/, '');
          var delim = detectDelimiter(clean);
          return clean
            .split(/\\r\\n|\\r|\\n/)
            .filter(function (l) { return l.trim() !== ''; })
            .map(function (l) { return splitLine(l, delim); });
        }
        function ensureXlsx() {
          return new Promise(function (resolve, reject) {
            if (window.XLSX) return resolve(window.XLSX);
            var s = document.createElement('script');
            s.src = XLSX_URL;
            s.onload = function () { window.XLSX ? resolve(window.XLSX) : reject(new Error('xlsx')); };
            s.onerror = function () { reject(new Error('xlsx')); };
            document.head.appendChild(s);
          });
        }
        function readText(file) {
          return new Promise(function (resolve, reject) {
            var r = new FileReader();
            r.onload = function () { resolve(String(r.result || '')); };
            r.onerror = function () { reject(new Error('read')); };
            r.readAsText(file);
          });
        }
        function readBuffer(file) {
          return new Promise(function (resolve, reject) {
            var r = new FileReader();
            r.onload = function () { resolve(r.result); };
            r.onerror = function () { reject(new Error('read')); };
            r.readAsArrayBuffer(file);
          });
        }
        function parseFile(file) {
          var name = (file && file.name ? file.name : '').toLowerCase();
          if (/\\.(xlsx|xls)$/.test(name)) {
            return ensureXlsx().then(function () {
              return readBuffer(file).then(function (buf) {
                var wb = window.XLSX.read(buf, { type: 'array' });
                var first = wb.SheetNames[0];
                var sheet = wb.Sheets[first];
                return window.XLSX.utils.sheet_to_json(sheet, { header: 1, raw: true, blankrows: false });
              });
            });
          }
          return readText(file).then(function (text) { return parseText(text); });
        }

        /* ---------- catalog ---------- */
        function loadCatalogLines() {
          try {
            var raw = localStorage.getItem(CATALOG_KEY);
            if (!raw) return [];
            var parsed = JSON.parse(raw);
            var lines = parsed && Array.isArray(parsed.lines) ? parsed.lines : [];
            return lines.filter(function (l) { return l && l.lineId && l.active !== false; });
          } catch (_e) {
            return [];
          }
        }
        function buildLabelIndex(lines) {
          var idx = {};
          lines.forEach(function (l) {
            [l.labelJa, l.labelEn, l.lineId].forEach(function (label) {
              var k = normText(label);
              if (k && !idx[k]) idx[k] = l;
            });
          });
          return idx;
        }

        /* ---------- column detection ---------- */
        var DATE_KEYS = ['日付', '年月日', '年月', 'date', 'day', 'month', 'ym', 'ymd'];
        var ITEM_KEYS = ['費目', '項目', '科目', '勘定科目', 'item', 'category', 'account', 'name'];
        var AMT_KEYS = ['金額', '額', '値', 'amount', 'value', 'price', 'cost'];
        function findCol(headerNorm, keys) {
          for (var i = 0; i < headerNorm.length; i++) {
            for (var j = 0; j < keys.length; j++) {
              if (headerNorm[i] === normText(keys[j])) return i;
            }
          }
          for (var a = 0; a < headerNorm.length; a++) {
            for (var b = 0; b < keys.length; b++) {
              if (headerNorm[a] && headerNorm[a].indexOf(normText(keys[b])) !== -1) return a;
            }
          }
          return -1;
        }

        /* ---------- build import plan ---------- */
        function buildPlan(rows) {
          if (!rows || !rows.length) throw new Error('empty');
          var header = rows[0].map(normText);
          var dateCol = findCol(header, DATE_KEYS);
          var itemCol = findCol(header, ITEM_KEYS);
          var amtCol = findCol(header, AMT_KEYS);
          var start = 1;
          if (dateCol === -1 || itemCol === -1 || amtCol === -1) {
            // No recognizable header -> assume positional date/item/amount, no header row.
            dateCol = 0; itemCol = 1; amtCol = 2; start = 0;
          }
          var lines = loadCatalogLines();
          var idx = buildLabelIndex(lines);

          var monthlyByYear = {};   // year -> { "lineId:month0": amount }
          var dailyByYear = {};     // year -> { lineId -> { iso -> amount } }
          var matchedLines = {};
          var unmatched = {};
          var mismatched = [];      // monthly data hitting a daily-style line
          var years = {};
          var parsed = 0;
          var skippedNoData = 0;

          for (var r = start; r < rows.length; r++) {
            var row = rows[r] || [];
            var date = normDate(row[dateCol]);
            var item = String(row[itemCol] == null ? '' : row[itemCol]).trim();
            var amount = parseAmount(row[amtCol]);
            if (!date || !item) { skippedNoData++; continue; }
            parsed++;
            var line = idx[normText(item)];
            if (!line) {
              unmatched[item] = (unmatched[item] || 0) + 1;
              continue;
            }
            var lineId = String(line.lineId);
            var year = Number(date.slice(0, 4));
            var month0 = Number(date.slice(5, 7)) - 1;
            var isDaily = date.length === 10;
            var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
            years[year] = true;
            matchedLines[lineId] = (line.labelJa || line.labelEn || lineId);

            if (style === 'daily') {
              if (!isDaily) {
                mismatched.push({ item: item, date: date, need: 'daily' });
                continue;
              }
              dailyByYear[year] = dailyByYear[year] || {};
              dailyByYear[year][lineId] = dailyByYear[year][lineId] || {};
              dailyByYear[year][lineId][date] = (dailyByYear[year][lineId][date] || 0) + amount;
            } else {
              monthlyByYear[year] = monthlyByYear[year] || {};
              var key = lineId + ':' + month0;
              monthlyByYear[year][key] = (monthlyByYear[year][key] || 0) + amount;
            }
          }

          return {
            monthlyByYear: monthlyByYear,
            dailyByYear: dailyByYear,
            matchedLines: matchedLines,
            unmatched: unmatched,
            mismatched: mismatched,
            years: Object.keys(years).map(Number).sort(),
            parsed: parsed,
            skippedNoData: skippedNoData
          };
        }

        /* ---------- apply ---------- */
        function applyMonthly(plan) {
          Object.keys(plan.monthlyByYear).forEach(function (yStr) {
            var year = Number(yStr);
            var key = PL_EXP_PREFIX + year;
            var map = {};
            try {
              var raw = localStorage.getItem(key);
              if (raw) { var p = JSON.parse(raw); if (p && typeof p === 'object') map = p; }
            } catch (_e) {}
            var inc = plan.monthlyByYear[yStr];
            Object.keys(inc).forEach(function (k) { map[k] = Math.round(Number(inc[k]) || 0); });
            try { localStorage.setItem(key, JSON.stringify(map)); } catch (_e2) {}
          });
        }
        function applyDaily(plan) {
          var years = Object.keys(plan.dailyByYear);
          if (!years.length) return;
          var g = window.__KPI_DATA_GATEWAY;
          if (!g || typeof g.getJson !== 'function' || typeof g.setJson !== 'function') return;
          var store = g.getJson(YEAR_STORE_KEY);
          if (!store || typeof store !== 'object') {
            store = { meta: { schemaVersion: 4, operatingYear: new Date().getFullYear() }, timeline: { dailySales: {}, businessDays: {} }, years: {} };
          }
          if (!store.years || typeof store.years !== 'object') store.years = {};
          years.forEach(function (yStr) {
            var year = Number(yStr);
            var rec = store.years[year] || store.years[String(year)];
            if (!rec || typeof rec !== 'object') { rec = { year: year, status: 'open', plan: {} }; store.years[year] = rec; }
            if (!rec.dailyExpenses || typeof rec.dailyExpenses !== 'object') rec.dailyExpenses = {};
            var byLine = plan.dailyByYear[yStr];
            Object.keys(byLine).forEach(function (lineId) {
              if (!rec.dailyExpenses[lineId] || typeof rec.dailyExpenses[lineId] !== 'object') rec.dailyExpenses[lineId] = {};
              var byIso = byLine[lineId];
              Object.keys(byIso).forEach(function (iso) {
                rec.dailyExpenses[lineId][iso] = Math.round(Number(byIso[iso]) || 0);
              });
            });
            rec.mepUpdatedAt = Date.now();
          });
          g.setJson(YEAR_STORE_KEY, store);
        }
        function applyPlan(plan) {
          applyMonthly(plan);
          applyDaily(plan);
          var affected = {};
          plan.years.forEach(function (y) { affected[y] = true; });
          Object.keys(affected).forEach(function (yStr) {
            var year = Number(yStr);
            try {
              if (typeof window.__plWriteMonthlyExpenseAllocationToMep === 'function') {
                window.__plWriteMonthlyExpenseAllocationToMep({ year: year });
              }
            } catch (_e) {}
            try {
              document.dispatchEvent(new CustomEvent('kpi:mepDataChanged', { detail: { year: year, source: 'pl-expense-import' } }));
            } catch (_e2) {}
          });
          if (affected[plYear]) {
            if (typeof window.__plRefreshExpenseAmounts === 'function') window.__plRefreshExpenseAmounts();
            if (typeof window.__plFillDailyExpenseRowsFromMep === 'function') window.__plFillDailyExpenseRowsFromMep();
          }
        }

        /* ---------- summary / confirm ---------- */
        function summarize(plan) {
          var lines = [];
          var matchedCount = Object.keys(plan.matchedLines).length;
          var unmatchedKeys = Object.keys(plan.unmatched);
          var monthlyWrites = 0;
          Object.keys(plan.monthlyByYear).forEach(function (y) { monthlyWrites += Object.keys(plan.monthlyByYear[y]).length; });
          var dailyWrites = 0;
          Object.keys(plan.dailyByYear).forEach(function (y) {
            Object.keys(plan.dailyByYear[y]).forEach(function (lid) { dailyWrites += Object.keys(plan.dailyByYear[y][lid]).length; });
          });
          lines.push(tt('支出データを取り込みます。内容を確認してください。', 'Import expense data. Please review.'));
          lines.push('');
          lines.push(tt('対象年', 'Years') + ': ' + (plan.years.length ? plan.years.join(', ') : '-'));
          lines.push(tt('読取行', 'Rows read') + ': ' + plan.parsed);
          lines.push(tt('一致した費目', 'Matched items') + ': ' + matchedCount);
          lines.push(tt('月次セル書込', 'Monthly cells') + ': ' + monthlyWrites);
          lines.push(tt('日次エントリ書込', 'Daily entries') + ': ' + dailyWrites);
          if (unmatchedKeys.length) {
            lines.push('');
            lines.push(tt('未一致（スキップ）の費目', 'Unmatched items (skipped)') + ':');
            lines.push('  ' + unmatchedKeys.slice(0, 12).join(', ') + (unmatchedKeys.length > 12 ? ' …' : ''));
            lines.push(tt('※ 費目カタログのラベルと完全一致する必要があります。', '* Must exactly match a line label in the catalog.'));
          }
          if (plan.mismatched.length) {
            lines.push('');
            lines.push(tt('粒度不一致（スキップ）', 'Granularity mismatch (skipped)') + ': ' + plan.mismatched.length);
            lines.push(tt('※ 日次入力の費目に月次データ（YYYY-MM）が来た行。', '* Daily-input items received monthly (YYYY-MM) rows.'));
          }
          var current = plan.years.indexOf(plYear) !== -1;
          if (plan.years.length && !current) {
            lines.push('');
            lines.push(tt('※ 表示中の年（' + plYear + '）以外のデータは、年セレクタで切替表示してください。',
                          '* Data for years other than the current one (' + plYear + ') — switch the year selector to view.'));
          }
          return lines.join('\\n');
        }

        function runExpenseImport(file) {
          parseFile(file).then(function (rows) {
            var plan;
            try { plan = buildPlan(rows); }
            catch (e) {
              window.alert(tt('ファイルを読み取れませんでした（空、または形式が不正です）。',
                              'Could not read the file (empty or invalid format).'));
              return;
            }
            var hasWrites = Object.keys(plan.monthlyByYear).length || Object.keys(plan.dailyByYear).length;
            if (!hasWrites) {
              window.alert(summarize(plan) + '\\n\\n' + tt('取り込める行がありませんでした。',
                                                          'No importable rows were found.'));
              return;
            }
            if (!window.confirm(summarize(plan))) return;
            applyPlan(plan);
            window.alert(tt('取り込みが完了しました。', 'Import complete.'));
          }).catch(function () {
            window.alert(tt('Excel の読み込みに失敗しました。CSV でお試しください（オフライン時は .xlsx を読めません）。',
                            'Failed to read Excel. Try CSV instead (.xlsx needs to be online).'));
          });
        }

        function pickExpenseFile() {
          if (!fileInput) {
            fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.csv,.tsv,.txt,.xlsx,.xls';
            fileInput.style.display = 'none';
            fileInput.addEventListener('change', function () {
              var f = fileInput.files && fileInput.files[0];
              fileInput.value = '';
              if (f) runExpenseImport(f);
            });
            document.body.appendChild(fileInput);
          }
          fileInput.click();
        }

        window.__plExpenseImport = {
          buildPlan: buildPlan,
          parseText: parseText,
          applyPlan: applyPlan,
          normDate: normDate,
          parseAmount: parseAmount,
          pickFile: pickExpenseFile
        };

        /* Role split: PL "Upload Expenses" imports expenses only (no chooser).
           Income (daily sales) is imported on Monthly Edit / Annual Sales Data. */
        if (typeof btnCsv !== 'undefined' && btnCsv) {
          var clone = btnCsv.cloneNode(true);
          btnCsv.parentNode.replaceChild(clone, btnCsv);
          clone.addEventListener('click', function (e) {
            e.preventDefault();
            pickExpenseFile();
          });
        }
      })();
"""

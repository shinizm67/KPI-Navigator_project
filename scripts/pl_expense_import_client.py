"""PL expense CSV/Excel import (long-format: date / item / amount).

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

Slice 2 scope (2026-07-18, ①「列マッピング＋未一致費目の割当/新規作成」):
- Free-format files: after upload we auto-detect date/item/amount columns; if the
  header is not confidently recognized OR some items don't map to a catalog line,
  a mapping modal opens so the user can re-map columns and, per unmatched item,
  choose "スキップ / 既存へ割当 / 新規作成".
- "既存へ割当" persists an alias (``kpiNavigator.plExpenseImportAliases``:
  normalizedName -> lineId) so the same wording auto-maps next time (名寄せの土台).
- "新規作成" creates a catalog line via ``window.__plAddCatalogLineWithLabel`` and
  aliases the wording to the new lineId.
- Clean template files (recognized header + all items matched) still take the fast
  path (no modal), identical to slice 1.
- Monthly rows (YYYY-MM) -> kpi-pl-expenses-v1:{year}. Daily rows (YYYY-MM-DD) for
  daily-style lines -> kpiYearStore years[y].dailyExpenses[lineId][iso].

Slice 3 scope (2026-07-18, ②「重複ポリシー＋名寄せ・月跨ぎの精緻化」):
- Duplicate policy: when an incoming cell overlaps an already-stored value the user
  chooses replace (overwrite) / add (sum) / skip (keep existing). Default replace.
  Conflicts are detected up front (``analyzeConflicts``) and, if any exist, the
  modal opens even for clean template files so overwrite is never silent.
- 名寄せ (fuzzy suggestions): unmatched items are pre-matched to the closest catalog
  line (Levenshtein/containment similarity >= 0.6) and pre-selected as a "候補" in
  the modal; the user can override. Confirmed choices persist as aliases (slice 2).
- 月跨ぎ: rows are bucketed into the correct month/day and same lineId+month rows are
  summed within a file. Prepaid/accrual spreading across months is intentionally NOT
  auto-applied (it is a product-level accounting decision that would fabricate
  numbers); it stays a manual edit for now.
"""

from __future__ import annotations


def pl_expense_import_client_js() -> str:
    """JS snippet (single braces; inserted verbatim via f-string expression)."""
    return """
      /* ===== PL 支出 CSV/Excel 取込（列マッピング＋未一致費目の割当/新規作成） ===== */
      (function () {
        var CATALOG_KEY = 'kpiNavigator.plLineCatalog';
        var YEAR_STORE_KEY = 'kpiNavigator.kpiYearStore';
        var PL_EXP_PREFIX = 'kpi-pl-expenses-v1:';
        var ALIAS_KEY = 'kpiNavigator.plExpenseImportAliases';
        var XLSX_URL = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';

        var fileInput = null;
        var modalEl = null;

        function isJaLang() {
          return document.documentElement.lang === 'ja';
        }
        function tt(ja, en) {
          return typeof t === 'function' ? t(ja, en) : (isJaLang() ? ja : en);
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

        /* ---------- catalog + aliases ---------- */
        function loadCatalogLines() {
          if (typeof window.__plGetCatalogLines === 'function') {
            try {
              var viaApi = window.__plGetCatalogLines();
              if (Array.isArray(viaApi)) {
                return viaApi.filter(function (l) { return l && l.lineId && l.active !== false; });
              }
            } catch (_e0) {}
          }
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
        function loadAliases() {
          try {
            var raw = localStorage.getItem(ALIAS_KEY);
            var m = raw ? JSON.parse(raw) : null;
            return m && typeof m === 'object' ? m : {};
          } catch (_e) {
            return {};
          }
        }
        function saveAliases(m) {
          try { localStorage.setItem(ALIAS_KEY, JSON.stringify(m || {})); } catch (_e) {}
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
        /** resolver(displayName) -> line | null (catalog label first, then alias). */
        function makeResolver(lines, aliases) {
          var idx = buildLabelIndex(lines);
          var byId = {};
          lines.forEach(function (l) { byId[String(l.lineId)] = l; });
          return function (display) {
            var k = normText(display);
            if (idx[k]) return idx[k];
            var aid = aliases && aliases[k];
            if (aid && byId[String(aid)]) return byId[String(aid)];
            return null;
          };
        }
        function lineLabel(line) {
          if (!line) return '';
          return isJaLang()
            ? (line.labelJa || line.labelEn || line.lineId)
            : (line.labelEn || line.labelJa || line.lineId);
        }

        /* ---------- fuzzy name reconciliation (名寄せ候補) ---------- */
        function levenshtein(a, b) {
          a = String(a || ''); b = String(b || '');
          var m = a.length, n = b.length;
          if (!m) return n;
          if (!n) return m;
          var prev = [], cur = [], i, j;
          for (j = 0; j <= n; j++) prev[j] = j;
          for (i = 1; i <= m; i++) {
            cur[0] = i;
            for (j = 1; j <= n; j++) {
              var cost = a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1;
              cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost);
            }
            for (j = 0; j <= n; j++) prev[j] = cur[j];
          }
          return prev[n];
        }
        function similarity(a, b) {
          a = normText(a); b = normText(b);
          if (!a || !b) return 0;
          if (a === b) return 1;
          if (a.indexOf(b) !== -1 || b.indexOf(a) !== -1) {
            return 0.5 + 0.5 * (Math.min(a.length, b.length) / Math.max(a.length, b.length));
          }
          var d = levenshtein(a, b);
          return 1 - d / Math.max(a.length, b.length);
        }
        function bestCatalogMatch(display, lines) {
          var best = null, bestScore = 0;
          lines.forEach(function (l) {
            [l.labelJa, l.labelEn].forEach(function (lab) {
              if (!lab) return;
              var s = similarity(display, lab);
              if (s > bestScore) { bestScore = s; best = l; }
            });
          });
          return (best && bestScore >= 0.6) ? { line: best, score: bestScore } : null;
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
        function detectColumns(rows) {
          var header = (rows[0] || []).map(normText);
          var dateCol = findCol(header, DATE_KEYS);
          var itemCol = findCol(header, ITEM_KEYS);
          var amtCol = findCol(header, AMT_KEYS);
          var confident = dateCol !== -1 && itemCol !== -1 && amtCol !== -1;
          if (confident) {
            return { dateCol: dateCol, itemCol: itemCol, amtCol: amtCol, start: 1, hasHeader: true, confident: true };
          }
          // Positional fallback. Treat row 0 as a header unless its first cell is a date.
          var hasHeader = !normDate((rows[0] || [])[0]);
          return {
            dateCol: dateCol === -1 ? 0 : dateCol,
            itemCol: itemCol === -1 ? 1 : itemCol,
            amtCol: amtCol === -1 ? 2 : amtCol,
            start: hasHeader ? 1 : 0,
            hasHeader: hasHeader,
            confident: false
          };
        }
        function maxColCount(rows) {
          var m = 0;
          for (var i = 0; i < rows.length; i++) {
            if (rows[i] && rows[i].length > m) m = rows[i].length;
          }
          return m;
        }
        function columnLabels(rows, cols) {
          var n = maxColCount(rows);
          var headerRow = cols.hasHeader ? (rows[0] || []) : null;
          var sampleRow = rows[cols.start] || rows[cols.start + 1] || [];
          var out = [];
          for (var c = 0; c < n; c++) {
            var name = (headerRow && headerRow[c] != null && String(headerRow[c]).trim() !== '')
              ? String(headerRow[c]).trim()
              : (isJaLang() ? ('列' + (c + 1)) : ('Col ' + (c + 1)));
            var sample = sampleRow[c] != null ? String(sampleRow[c]).trim() : '';
            if (sample.length > 18) sample = sample.slice(0, 18) + '…';
            out.push(sample ? (name + '  ›  ' + sample) : name);
          }
          return out;
        }

        /* ---------- build import plan ---------- */
        function buildPlan(rows, cols, resolver) {
          if (!rows || !rows.length) throw new Error('empty');
          var dateCol = cols.dateCol, itemCol = cols.itemCol, amtCol = cols.amtCol;
          var start = cols.start || 0;

          var monthlyByYear = {};   // year -> { "lineId:month0": amount }
          var dailyByYear = {};     // year -> { lineId -> { iso -> amount } }
          var matchedLines = {};
          var unmatched = {};       // normName -> { display, count, hasDaily, hasMonthly }
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
            var isDaily = date.length === 10;
            var line = resolver(item);
            if (!line) {
              var uk = normText(item);
              if (!unmatched[uk]) unmatched[uk] = { display: item, count: 0, hasDaily: false, hasMonthly: false };
              unmatched[uk].count++;
              if (isDaily) unmatched[uk].hasDaily = true; else unmatched[uk].hasMonthly = true;
              continue;
            }
            var lineId = String(line.lineId);
            var year = Number(date.slice(0, 4));
            var month0 = Number(date.slice(5, 7)) - 1;
            var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
            years[year] = true;
            matchedLines[lineId] = lineLabel(line) || lineId;

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
            years: Object.keys(years).map(Number).sort(function (a, b) { return a - b; }),
            parsed: parsed,
            skippedNoData: skippedNoData,
            cols: cols
          };
        }
        function buildPlanAuto(rows) {
          var cols = detectColumns(rows);
          return buildPlan(rows, cols, makeResolver(loadCatalogLines(), loadAliases()));
        }

        /* ---------- conflict analysis (重複ポリシー) ---------- */
        function readMonthlyMap(year) {
          try {
            var raw = localStorage.getItem(PL_EXP_PREFIX + year);
            if (raw) { var p = JSON.parse(raw); if (p && typeof p === 'object') return p; }
          } catch (_e) {}
          return {};
        }
        function readDailyStore() {
          var g = window.__KPI_DATA_GATEWAY;
          if (!g || typeof g.getJson !== 'function') return null;
          var store = g.getJson(YEAR_STORE_KEY);
          return (store && typeof store === 'object') ? store : null;
        }
        /** Count incoming cells that already have a stored value (overlap). */
        function analyzeConflicts(plan) {
          var monthly = 0, daily = 0;
          Object.keys(plan.monthlyByYear).forEach(function (yStr) {
            var map = readMonthlyMap(Number(yStr));
            var inc = plan.monthlyByYear[yStr];
            Object.keys(inc).forEach(function (k) {
              if (Object.prototype.hasOwnProperty.call(map, k)) monthly++;
            });
          });
          var store = readDailyStore();
          if (store && store.years) {
            Object.keys(plan.dailyByYear).forEach(function (yStr) {
              var rec = store.years[yStr] || store.years[Number(yStr)];
              var de = rec && rec.dailyExpenses;
              if (!de) return;
              var byLine = plan.dailyByYear[yStr];
              Object.keys(byLine).forEach(function (lineId) {
                var existing = de[lineId];
                if (!existing) return;
                Object.keys(byLine[lineId]).forEach(function (iso) {
                  if (Object.prototype.hasOwnProperty.call(existing, iso)) daily++;
                });
              });
            });
          }
          return { monthly: monthly, daily: daily, total: monthly + daily };
        }

        /* ---------- apply (policy: 'replace' | 'add' | 'skip') ---------- */
        function mergeValue(existingHas, existing, incoming, policy) {
          if (policy === 'add') return Math.round((Number(existing) || 0) + (Number(incoming) || 0));
          if (policy === 'skip') return existingHas ? existing : Math.round(Number(incoming) || 0);
          return Math.round(Number(incoming) || 0); // replace (default)
        }
        function applyMonthly(plan, policy) {
          Object.keys(plan.monthlyByYear).forEach(function (yStr) {
            var year = Number(yStr);
            var key = PL_EXP_PREFIX + year;
            var map = readMonthlyMap(year);
            var inc = plan.monthlyByYear[yStr];
            Object.keys(inc).forEach(function (k) {
              var has = Object.prototype.hasOwnProperty.call(map, k);
              map[k] = mergeValue(has, map[k], inc[k], policy);
            });
            try { localStorage.setItem(key, JSON.stringify(map)); } catch (_e2) {}
          });
        }
        function applyDaily(plan, policy) {
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
              var target = rec.dailyExpenses[lineId];
              var byIso = byLine[lineId];
              Object.keys(byIso).forEach(function (iso) {
                var has = Object.prototype.hasOwnProperty.call(target, iso);
                target[iso] = mergeValue(has, target[iso], byIso[iso], policy);
              });
            });
            rec.mepUpdatedAt = Date.now();
          });
          g.setJson(YEAR_STORE_KEY, store);
        }
        function applyPlan(plan, policy) {
          policy = (policy === 'add' || policy === 'skip') ? policy : 'replace';
          applyMonthly(plan, policy);
          applyDaily(plan, policy);
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
        function policyLabel(policy) {
          if (policy === 'add') return tt('追記（加算）', 'Add (sum)');
          if (policy === 'skip') return tt('スキップ（既存を残す）', 'Skip (keep existing)');
          return tt('置換（上書き）', 'Replace (overwrite)');
        }
        function summarize(plan, policy, conflicts) {
          policy = policy || 'replace';
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
          lines.push(tt('重複時の扱い', 'On conflict') + ': ' + policyLabel(policy));
          if (conflicts && conflicts.total) {
            lines.push(tt('既存と重複するセル', 'Cells overlapping existing') + ': ' + conflicts.total);
          }
          if (unmatchedKeys.length) {
            var disp = unmatchedKeys.map(function (k) { return plan.unmatched[k].display; });
            lines.push('');
            lines.push(tt('未一致（スキップ）の費目', 'Unmatched items (skipped)') + ':');
            lines.push('  ' + disp.slice(0, 12).join(', ') + (disp.length > 12 ? ' …' : ''));
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

        function finalizeImport(plan, useConfirm, policy) {
          policy = (policy === 'add' || policy === 'skip') ? policy : 'replace';
          var hasWrites = Object.keys(plan.monthlyByYear).length || Object.keys(plan.dailyByYear).length;
          if (!hasWrites) {
            window.alert(summarize(plan, policy, null) + '\\n\\n' + tt('取り込める行がありませんでした。',
                                                        'No importable rows were found.'));
            return false;
          }
          var conflicts = analyzeConflicts(plan);
          if (useConfirm && !window.confirm(summarize(plan, policy, conflicts))) return false;
          applyPlan(plan, policy);
          window.alert(tt('取り込みが完了しました。', 'Import complete.'));
          return true;
        }

        /* ---------- mapping modal ---------- */
        function el(tag, cls, text) {
          var e = document.createElement(tag);
          if (cls) e.className = cls;
          if (text != null) e.textContent = text;
          return e;
        }
        function makeColSelect(colLabels, selectedIdx) {
          var sel = el('select', 'pl-import-map__select');
          colLabels.forEach(function (lab, i) {
            var o = el('option', null, lab);
            o.value = String(i);
            if (i === selectedIdx) o.selected = true;
            sel.appendChild(o);
          });
          return sel;
        }
        function catalogOptions(lines) {
          return lines.map(function (l) {
            var bkt = l.bucket === 'fixed' ? tt('固定費', 'Fixed') : tt('変動費', 'Variable');
            var sty = (l.resolvedInputStyle || l.inputStyle) === 'daily' ? tt('日次', 'Daily') : tt('月次', 'Monthly');
            return { lineId: String(l.lineId), text: lineLabel(l) + '（' + bkt + '・' + sty + '）' };
          });
        }
        function closeMappingModal() {
          if (modalEl && modalEl.parentNode) modalEl.parentNode.removeChild(modalEl);
          modalEl = null;
          document.body.classList.remove('pl-import-map-open');
          document.removeEventListener('keydown', onModalKeydown);
        }
        function onModalKeydown(e) {
          if (e.key === 'Escape' || e.keyCode === 27) closeMappingModal();
        }

        function openMappingModal(rows, cols) {
          closeMappingModal();
          var lines = loadCatalogLines();
          var colLabels = columnLabels(rows, cols);
          var optData = catalogOptions(lines);

          var overlay = el('div', 'pl-import-map');
          overlay.setAttribute('role', 'dialog');
          overlay.setAttribute('aria-modal', 'true');
          var backdrop = el('div', 'pl-import-map__backdrop');
          backdrop.addEventListener('click', closeMappingModal);
          overlay.appendChild(backdrop);

          var panel = el('div', 'pl-import-map__panel');
          overlay.appendChild(panel);

          panel.appendChild(el('h2', 'pl-import-map__title',
            tt('支出CSV/Excel の取込設定', 'Configure expense import')));
          panel.appendChild(el('p', 'pl-import-map__desc',
            tt('列の対応づけを確認し、未一致の費目は「既存へ割当」か「新規作成」を選んでください。',
               'Confirm the column mapping and, for each unmatched item, choose "assign to existing" or "create new".')));

          /* --- column mapping section --- */
          var colSec = el('div', 'pl-import-map__section');
          colSec.appendChild(el('h3', 'pl-import-map__section-title', tt('列の対応', 'Column mapping')));
          var grid = el('div', 'pl-import-map__cols');
          function colRow(labelText, selectedIdx) {
            var wrap = el('label', 'pl-import-map__col-row');
            wrap.appendChild(el('span', 'pl-import-map__col-label', labelText));
            var sel = makeColSelect(colLabels, selectedIdx);
            wrap.appendChild(sel);
            grid.appendChild(wrap);
            return sel;
          }
          var dateSel = colRow(tt('日付', 'Date'), cols.dateCol);
          var itemSel = colRow(tt('費目', 'Item'), cols.itemCol);
          var amtSel = colRow(tt('金額', 'Amount'), cols.amtCol);
          colSec.appendChild(grid);
          panel.appendChild(colSec);

          /* --- unmatched section --- */
          var unSec = el('div', 'pl-import-map__section');
          unSec.appendChild(el('h3', 'pl-import-map__section-title', tt('未一致の費目', 'Unmatched items')));
          var unBody = el('div', 'pl-import-map__ubody');
          unSec.appendChild(unBody);
          panel.appendChild(unSec);

          /* --- duplicate policy section --- */
          var polSec = el('div', 'pl-import-map__section');
          polSec.appendChild(el('h3', 'pl-import-map__section-title', tt('重複時の扱い', 'On conflict')));
          var polNote = el('p', 'pl-import-map__conflict', '');
          polSec.appendChild(polNote);
          var polWrap = el('div', 'pl-import-map__policy');
          function polRadio(val, labelText, hintText) {
            var lab = el('label', 'pl-import-map__pol');
            var input = document.createElement('input');
            input.type = 'radio';
            input.name = 'pl-import-policy';
            input.value = val;
            if (val === 'replace') input.checked = true;
            lab.appendChild(input);
            lab.appendChild(el('span', 'pl-import-map__pol-label', labelText));
            if (hintText) lab.appendChild(el('span', 'pl-import-map__pol-hint', hintText));
            polWrap.appendChild(lab);
          }
          polRadio('replace', tt('置換（上書き）', 'Replace'), tt('取込値で上書き', 'overwrite with imported'));
          polRadio('add', tt('追記（加算）', 'Add'), tt('既存＋取込値', 'existing + imported'));
          polRadio('skip', tt('スキップ（既存を残す）', 'Skip'), tt('既存があれば据置', 'keep existing if present'));
          polSec.appendChild(polWrap);
          panel.appendChild(polSec);
          function currentPolicy() {
            var c = polWrap.querySelector('input[name="pl-import-policy"]:checked');
            return c ? c.value : 'replace';
          }

          function currentCols() {
            return {
              dateCol: Number(dateSel.value),
              itemCol: Number(itemSel.value),
              amtCol: Number(amtSel.value),
              start: cols.start,
              hasHeader: cols.hasHeader,
              confident: cols.confident
            };
          }

          function buildUnmatchedRow(normKey, info) {
            var row = el('div', 'pl-import-map__urow');
            row.setAttribute('data-norm', normKey);
            row.setAttribute('data-display', info.display);

            var name = el('div', 'pl-import-map__uname');
            name.appendChild(el('span', 'pl-import-map__uname-text', info.display));
            name.appendChild(el('span', 'pl-import-map__ucount', '×' + info.count));
            row.appendChild(name);

            var action = el('select', 'pl-import-map__select pl-import-map__uaction');
            var optSkip = el('option', null, tt('スキップ', 'Skip'));
            optSkip.value = 'skip';
            action.appendChild(optSkip);
            if (optData.length) {
              var grp = document.createElement('optgroup');
              grp.label = tt('既存へ割当', 'Assign to existing');
              optData.forEach(function (o) {
                var op = el('option', null, o.text);
                op.value = 'assign:' + o.lineId;
                grp.appendChild(op);
              });
              action.appendChild(grp);
            }
            var optCreate = el('option', null, tt('＋ 新規作成', '+ Create new'));
            optCreate.value = '__create';
            action.appendChild(optCreate);
            row.appendChild(action);

            var createBox = el('span', 'pl-import-map__ucreate');
            createBox.hidden = true;
            var bucketSel = el('select', 'pl-import-map__select pl-import-map__ubucket');
            var ob1 = el('option', null, tt('変動費', 'Variable')); ob1.value = 'variable';
            var ob2 = el('option', null, tt('固定費', 'Fixed')); ob2.value = 'fixed';
            bucketSel.appendChild(ob1); bucketSel.appendChild(ob2);
            var styleSel = el('select', 'pl-import-map__select pl-import-map__ustyle');
            var os1 = el('option', null, tt('月次', 'Monthly')); os1.value = 'monthly';
            var os2 = el('option', null, tt('日次', 'Daily')); os2.value = 'daily';
            styleSel.appendChild(os1); styleSel.appendChild(os2);
            styleSel.value = (info.hasDaily && !info.hasMonthly) ? 'daily' : 'monthly';
            createBox.appendChild(bucketSel);
            createBox.appendChild(styleSel);
            row.appendChild(createBox);

            action.addEventListener('change', function () {
              createBox.hidden = action.value !== '__create';
            });
            bucketSel.addEventListener('change', function () {
              // Fixed bucket lines are always monthly.
              if (bucketSel.value === 'fixed') { styleSel.value = 'monthly'; styleSel.disabled = true; }
              else { styleSel.disabled = false; }
            });

            // 名寄せ候補: pre-select the closest catalog line (user can override).
            var suggest = bestCatalogMatch(info.display, lines);
            if (suggest) {
              action.value = 'assign:' + String(suggest.line.lineId);
              var badge = el('span', 'pl-import-map__suggest', tt('候補', 'suggested'));
              badge.title = tt('近い費目を自動提案：' + lineLabel(suggest.line) + '（変更できます）',
                               'Suggested closest item: ' + lineLabel(suggest.line) + ' (you can change it)');
              name.appendChild(badge);
            }
            return row;
          }

          function refreshConflictNote(plan) {
            var conflicts = analyzeConflicts(plan);
            polNote.textContent = conflicts.total
              ? tt('既存の値と重複するセル: ' + conflicts.total + ' 件。扱いを選んでください。',
                   'Cells overlapping existing values: ' + conflicts.total + '. Choose how to handle.')
              : tt('既存データとの重複はありません。', 'No overlap with existing data.');
          }
          function renderUnmatched() {
            var plan = buildPlan(rows, currentCols(), makeResolver(loadCatalogLines(), loadAliases()));
            refreshConflictNote(plan);
            var keys = Object.keys(plan.unmatched);
            unBody.innerHTML = '';
            if (!keys.length) {
              unBody.appendChild(el('p', 'pl-import-map__ok',
                tt('未一致の費目はありません。そのまま取り込めます。', 'No unmatched items. Ready to import.')));
              return;
            }
            keys.forEach(function (k) {
              unBody.appendChild(buildUnmatchedRow(k, plan.unmatched[k]));
            });
          }
          // Item column drives the unmatched list; recompute when it changes.
          itemSel.addEventListener('change', renderUnmatched);
          renderUnmatched();

          /* --- actions --- */
          var actions = el('div', 'pl-import-map__actions');
          var cancel = el('button', 'pl-import-map__btn pl-import-map__btn--ghost',
            tt('キャンセル', 'Cancel'));
          cancel.type = 'button';
          cancel.addEventListener('click', closeMappingModal);
          var doImport = el('button', 'pl-import-map__btn pl-import-map__btn--primary',
            tt('取込を実行', 'Run import'));
          doImport.type = 'button';
          doImport.addEventListener('click', function () {
            var aliases = loadAliases();
            var next = {};
            Object.keys(aliases).forEach(function (k) { next[k] = aliases[k]; });
            var urows = unBody.querySelectorAll('.pl-import-map__urow');
            for (var i = 0; i < urows.length; i++) {
              var uEl = urows[i];
              var k = uEl.getAttribute('data-norm');
              var display = uEl.getAttribute('data-display');
              var val = uEl.querySelector('.pl-import-map__uaction').value;
              if (val === 'skip') continue;
              if (val.indexOf('assign:') === 0) {
                next[k] = val.slice('assign:'.length);
              } else if (val === '__create') {
                var bucket = uEl.querySelector('.pl-import-map__ubucket').value;
                var style = uEl.querySelector('.pl-import-map__ustyle').value;
                var newId = (typeof window.__plAddCatalogLineWithLabel === 'function')
                  ? window.__plAddCatalogLineWithLabel(display, display, bucket, style)
                  : '';
                if (newId) next[k] = newId;
              }
            }
            saveAliases(next);
            var cols2 = currentCols();
            var policy = currentPolicy();
            var plan2 = buildPlan(rows, cols2, makeResolver(loadCatalogLines(), next));
            closeMappingModal();
            // The modal itself was the confirmation step, so import without a second confirm.
            finalizeImport(plan2, false, policy);
          });
          actions.appendChild(cancel);
          actions.appendChild(doImport);
          panel.appendChild(actions);

          document.body.appendChild(overlay);
          document.body.classList.add('pl-import-map-open');
          document.addEventListener('keydown', onModalKeydown);
          modalEl = overlay;
        }

        function runExpenseImport(file) {
          parseFile(file).then(function (rows) {
            if (!rows || !rows.length) {
              window.alert(tt('ファイルを読み取れませんでした（空、または形式が不正です）。',
                              'Could not read the file (empty or invalid format).'));
              return;
            }
            var cols = detectColumns(rows);
            var plan;
            try { plan = buildPlan(rows, cols, makeResolver(loadCatalogLines(), loadAliases())); }
            catch (e) {
              window.alert(tt('ファイルを読み取れませんでした（空、または形式が不正です）。',
                              'Could not read the file (empty or invalid format).'));
              return;
            }
            var unmatchedCount = Object.keys(plan.unmatched).length;
            var conflicts = analyzeConflicts(plan);
            // Fast path: recognized header, everything maps, AND no overlap with
            // existing data (nothing to decide). Otherwise open the modal so the
            // user consciously handles mapping and/or the duplicate policy.
            if (cols.confident && unmatchedCount === 0 && conflicts.total === 0) {
              finalizeImport(plan, true, 'replace');
              return;
            }
            openMappingModal(rows, cols);
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
          buildPlan: buildPlanAuto,
          buildPlanWith: buildPlan,
          detectColumns: detectColumns,
          columnLabels: columnLabels,
          makeResolver: makeResolver,
          parseText: parseText,
          applyPlan: applyPlan,
          analyzeConflicts: analyzeConflicts,
          bestCatalogMatch: bestCatalogMatch,
          similarity: similarity,
          normDate: normDate,
          parseAmount: parseAmount,
          loadAliases: loadAliases,
          saveAliases: saveAliases,
          openModal: openMappingModal,
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

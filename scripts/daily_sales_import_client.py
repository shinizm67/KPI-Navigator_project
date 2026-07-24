"""Browser-side CSV / Excel daily-sales import (header detection + modal wiring)."""

from __future__ import annotations

DAILY_SALES_IMPORT_MARKER = "/* KPI-DAILY-SALES-IMPORT */"


def daily_sales_import_js() -> str:
    return f"""      {DAILY_SALES_IMPORT_MARKER}
      (function () {{
        var XLSX_CDN = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';

        function isJa() {{
          return (
            String(document.documentElement.getAttribute('lang') || '')
              .toLowerCase()
              .indexOf('ja') === 0
          );
        }}

        function t(ja, en) {{
          return isJa() ? ja : en;
        }}

        function pad2(n) {{
          return n < 10 ? '0' + n : String(n);
        }}

        function isoFromYmd(y, m, d) {{
          y = Number(y);
          m = Number(m);
          d = Number(d);
          if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(d)) return null;
          var dt = new Date(y, m - 1, d);
          if (dt.getFullYear() !== y || dt.getMonth() !== m - 1 || dt.getDate() !== d) return null;
          return y + '-' + pad2(m) + '-' + pad2(d);
        }}

        function isoYear(iso) {{
          return Number(String(iso || '').slice(0, 4));
        }}

        function normalizeHeader(raw) {{
          return String(raw || '')
            .replace(/\\uFEFF/g, '')
            .trim()
            .toLowerCase()
            .replace(/[\\s_]+/g, '');
        }}

        var DATE_KEYS = [
          'date',
          '日付',
          '日にち',
          '年月日',
          '営業日付',
          'transactiondate',
          'salesdate',
        ];
        /** Optional business-day column. Values: 1/営業/open = 営業日, 0/店休/off = 店休日.
         *  If no column is detected, 売上>0 を営業日とみなす（一般的な CSV 向け）。 */
        var BIZ_KEYS = [
          '営業日',
          '営業日フラグ',
          '営業フラグ',
          'businessday',
          'businessdayflag',
          'bizday',
          'bday',
          'open',
          'isopen',
          'openflag',
          'closed',
          'closeday',
          'dayoff',
          'off',
          '店休',
          '店休日',
          '休業',
          '休業日',
          '営業',
        ];
        var SALES_KEYS = [
          '店舗売上',
          'storesales',
          '売上',
          '売上高',
          '売上金額',
          'sales',
          'amount',
          'netsales',
          'dailysales',
          'grosssales',
        ];
        var FOOD_KEYS = [
          'フード売上',
          '食売上',
          'foodsales',
          'food_sales',
          'foodsale',
          'food',
        ];
        var DRINK_KEYS = [
          'ドリンク売上',
          '飲料売上',
          'drinksales',
          'drink_sales',
          'drinksale',
          'beveragesales',
          'beverage',
          'drink',
        ];

        function matchKey(norm, keys) {{
          for (var i = 0; i < keys.length; i++) {{
            var k = normalizeHeader(keys[i]);
            if (!k) continue;
            /* 完全一致、またはヘッダがキーを含む（キーがヘッダを含む逆方向は短い語の誤爆になるので不可） */
            if (norm === k || norm.indexOf(k) >= 0) return true;
          }}
          return false;
        }}

        function isFoodHeader(norm) {{
          return matchKey(norm, FOOD_KEYS);
        }}
        function isDrinkHeader(norm) {{
          return matchKey(norm, DRINK_KEYS);
        }}

        function detectColumns(headerRow) {{
          var dateIdx = -1;
          var bizIdx = -1;
          var salesIdx = -1;
          var foodIdx = -1;
          var drinkIdx = -1;
          for (var c = 0; c < headerRow.length; c++) {{
            var norm = normalizeHeader(headerRow[c]);
            if (!norm) continue;
            /* Food/Drink を先に拾い、汎用「売上」に食わないようにする */
            if (foodIdx < 0 && isFoodHeader(norm)) foodIdx = c;
            else if (drinkIdx < 0 && isDrinkHeader(norm)) drinkIdx = c;
            else if (dateIdx < 0 && matchKey(norm, DATE_KEYS)) dateIdx = c;
            else if (bizIdx < 0 && matchKey(norm, BIZ_KEYS)) bizIdx = c;
            else if (
              salesIdx < 0 &&
              matchKey(norm, SALES_KEYS) &&
              !isFoodHeader(norm) &&
              !isDrinkHeader(norm)
            ) {{
              salesIdx = c;
            }}
          }}
          if (dateIdx < 0 && headerRow.length >= 1) dateIdx = 0;
          if (salesIdx < 0 && headerRow.length >= 2) {{
            salesIdx = headerRow.length - 1;
            while (
              salesIdx >= 0 &&
              (salesIdx === dateIdx ||
                salesIdx === foodIdx ||
                salesIdx === drinkIdx ||
                salesIdx === bizIdx)
            ) {{
              salesIdx--;
            }}
          }}
          return {{
            dateIdx: dateIdx,
            bizIdx: bizIdx,
            salesIdx: salesIdx,
            foodIdx: foodIdx,
            drinkIdx: drinkIdx,
          }};
        }}

        function excelSerialToIso(n) {{
          var serial = Number(n);
          if (!Number.isFinite(serial) || serial < 20000) return null;
          var base = Date.UTC(1899, 11, 30);
          var ms = base + Math.round(serial) * 86400000;
          var dt = new Date(ms);
          return isoFromYmd(dt.getUTCFullYear(), dt.getUTCMonth() + 1, dt.getUTCDate());
        }}

        function parseDateCell(raw) {{
          if (raw == null || raw === '') return null;
          if (typeof raw === 'number') return excelSerialToIso(raw);
          var s = String(raw).trim();
          if (!s) return null;
          if (/^\\d{{4,5}}(\\.\\d+)?$/.test(s)) {{
            var fromSerial = excelSerialToIso(Number(s));
            if (fromSerial) return fromSerial;
          }}
          var iso = s.match(/^(\\d{{4}})[\\/\\-.](\\d{{1,2}})[\\/\\-.](\\d{{1,2}})/);
          if (iso) return isoFromYmd(iso[1], iso[2], iso[3]);
          var dt = new Date(s);
          if (!isNaN(dt.getTime())) return isoFromYmd(dt.getFullYear(), dt.getMonth() + 1, dt.getDate());
          return null;
        }}

        function parseSalesCell(raw) {{
          if (raw == null || raw === '') return 0;
          if (typeof raw === 'number' && Number.isFinite(raw)) return raw;
          var s = String(raw).replace(/[¥$,\\s]/g, '');
          if (s === '' || s === '-') return 0;
          var n = Number(s);
          return Number.isFinite(n) ? n : 0;
        }}

        function parseBizCell(raw, salesAmount) {{
          if (raw == null || raw === '') {{
            return Number(salesAmount) > 0;
          }}
          if (typeof raw === 'number') return raw !== 0;
          var s = String(raw).trim().toLowerCase();
          if (!s) return Number(salesAmount) > 0;
          if (s === '0' || s === 'false' || s === 'no' || s === 'off' || s === '休' || s === '店休' || s === '×' || s === 'x') {{
            return false;
          }}
          if (s === '1' || s === 'true' || s === 'yes' || s === 'on' || s === '営業' || s === '○' || s === '◯') {{
            return true;
          }}
          var n = Number(s);
          if (Number.isFinite(n)) return n !== 0;
          return Number(salesAmount) > 0;
        }}

        function splitCsvLine(line, delim) {{
          var out = [];
          var cur = '';
          var inQ = false;
          for (var i = 0; i < line.length; i++) {{
            var ch = line[i];
            if (ch === '"') {{
              if (inQ && line[i + 1] === '"') {{
                cur += '"';
                i++;
              }} else inQ = !inQ;
            }} else if (!inQ && ch === delim) {{
              out.push(cur);
              cur = '';
            }} else cur += ch;
          }}
          out.push(cur);
          return out;
        }}

        function detectDelimiter(sample) {{
          var lines = sample.split(/\\r?\\n/).filter(function (l) {{ return l.trim(); }});
          if (!lines.length) return ',';
          var c = (lines[0].match(/,/g) || []).length;
          var t = (lines[0].match(/\\t/g) || []).length;
          var s = (lines[0].match(/;/g) || []).length;
          if (t >= c && t >= s) return '\\t';
          if (s > c) return ';';
          return ',';
        }}

        function parseDelimitedText(text) {{
          var body = String(text || '').replace(/^\\uFEFF/, '');
          if (!body.trim()) return [];
          var delim = detectDelimiter(body.slice(0, 2048));
          var lines = body.split(/\\r?\\n/).filter(function (l) {{ return l.trim() !== ''; }});
          return lines.map(function (line) {{ return splitCsvLine(line, delim); }});
        }}

        function ensureXlsx() {{
          if (window.XLSX) return Promise.resolve(window.XLSX);
          return new Promise(function (resolve, reject) {{
            var s = document.createElement('script');
            s.src = XLSX_CDN;
            s.async = true;
            s.onload = function () {{
              if (window.XLSX) resolve(window.XLSX);
              else reject(new Error('xlsx'));
            }};
            s.onerror = function () {{ reject(new Error('xlsx')); }};
            document.head.appendChild(s);
          }});
        }}

        function sheetToRows(wb) {{
          var name = wb.SheetNames && wb.SheetNames[0];
          if (!name) return [];
          var sheet = wb.Sheets[name];
          return window.XLSX.utils.sheet_to_json(sheet, {{ header: 1, raw: true, defval: '' }});
        }}

        function parseWorkbookBuffer(buf) {{
          return ensureXlsx().then(function () {{
            var wb = window.XLSX.read(buf, {{ type: 'array' }});
            return sheetToRows(wb);
          }});
        }}

        function cellHasValue(row, idx) {{
          if (idx < 0 || !row) return false;
          var raw = row[idx];
          if (raw == null) return false;
          if (typeof raw === 'number') return Number.isFinite(raw);
          return String(raw).trim() !== '';
        }}

        function rowsToMaps(rows) {{
          if (!rows || !rows.length) throw new Error('empty');
          var header = rows[0].map(function (c) {{ return String(c == null ? '' : c); }});
          var cols = detectColumns(header);
          if (cols.dateIdx < 0 || cols.salesIdx < 0) throw new Error('columns');
          var salesByDate = {{}};
          var businessDayByDate = {{}};
          var foodByDate = {{}};
          var drinkByDate = {{}};
          var years = {{}};
          var imported = 0;
          var foodCount = 0;
          var drinkCount = 0;
          var mismatchCount = 0;
          for (var r = 1; r < rows.length; r++) {{
            var row = rows[r];
            if (!row || !row.length) continue;
            var iso = parseDateCell(row[cols.dateIdx]);
            if (!iso) continue;
            var sales = parseSalesCell(row[cols.salesIdx]);
            var biz =
              cols.bizIdx >= 0
                ? parseBizCell(row[cols.bizIdx], sales)
                : sales > 0;
            if (!biz) sales = 0;
            sales = Math.round(sales);
            salesByDate[iso] = sales;
            businessDayByDate[iso] = !!biz;
            years[isoYear(iso)] = true;
            imported++;

            var hasFood = cellHasValue(row, cols.foodIdx);
            var hasDrink = cellHasValue(row, cols.drinkIdx);
            if (!biz) {{
              if (hasFood || hasDrink || cols.foodIdx >= 0 || cols.drinkIdx >= 0) {{
                foodByDate[iso] = 0;
                drinkByDate[iso] = 0;
              }}
              continue;
            }}
            if (!hasFood && !hasDrink) continue;

            var food = hasFood ? Math.round(parseSalesCell(row[cols.foodIdx])) : null;
            var drink = hasDrink ? Math.round(parseSalesCell(row[cols.drinkIdx])) : null;
            if (hasFood && hasDrink) {{
              if (Math.abs(sales - (food + drink)) > 1) mismatchCount++;
            }} else if (hasFood) {{
              drink = Math.max(0, sales - food);
            }} else {{
              food = Math.max(0, sales - drink);
            }}
            foodByDate[iso] = food;
            drinkByDate[iso] = drink;
            if (hasFood) foodCount++;
            if (hasDrink) drinkCount++;
          }}
          if (!imported) throw new Error('rows');
          return {{
            salesByDate: salesByDate,
            businessDayByDate: businessDayByDate,
            foodByDate: foodByDate,
            drinkByDate: drinkByDate,
            years: Object.keys(years).map(Number).filter(Number.isFinite).sort(),
            imported: imported,
            foodCount: foodCount,
            drinkCount: drinkCount,
            mismatchCount: mismatchCount,
            hasFoodCol: cols.foodIdx >= 0,
            hasDrinkCol: cols.drinkIdx >= 0,
          }};
        }}

        function formatMoney(n) {{
          var v = Math.round(Number(n) || 0);
          if (window.KpiCurrency) return KpiCurrency.format(v, {{ round: true }});
          if (isJa()) return '¥' + v.toLocaleString('en-US');
          return '$' + v.toLocaleString('en-US');
        }}

        function sumSales(map) {{
          var total = 0;
          Object.keys(map || {{}}).forEach(function (k) {{
            total += Number(map[k]) || 0;
          }});
          return total;
        }}

        function decodeSpreadsheetText(buf) {{
          var bytes = new Uint8Array(buf);
          if (bytes.length >= 2 && bytes[0] === 0xff && bytes[1] === 0xfe) {{
            return new TextDecoder('utf-16le').decode(bytes);
          }}
          if (bytes.length >= 2 && bytes[0] === 0xfe && bytes[1] === 0xff) {{
            return new TextDecoder('utf-16be').decode(bytes);
          }}
          var utf8 = new TextDecoder('utf-8').decode(bytes);
          /* Excel が Shift_JIS で保存した CSV を救済（日本語ヘッダが文字化けしているとき） */
          if (/\\uFFFD/.test(utf8) || /[\u00C0-\u00FF]{{3,}}/.test(utf8.slice(0, 80))) {{
            try {{
              var sjis = new TextDecoder('shift-jis').decode(bytes);
              if (/日付|売上|日にち|営業/.test(sjis)) return sjis;
            }} catch (e) {{}}
          }}
          return utf8;
        }}

        function readFileAsText(file) {{
          return readFileAsArrayBuffer(file).then(decodeSpreadsheetText);
        }}

        function readFileAsArrayBuffer(file) {{
          return new Promise(function (resolve, reject) {{
            var reader = new FileReader();
            reader.onload = function () {{ resolve(reader.result); }};
            reader.onerror = reject;
            reader.readAsArrayBuffer(file);
          }});
        }}

        function parseFile(file) {{
          var name = String(file && file.name ? file.name : '').toLowerCase();
          if (name.endsWith('.xlsx') || name.endsWith('.xls')) {{
            return readFileAsArrayBuffer(file).then(parseWorkbookBuffer).then(rowsToMaps);
          }}
          return readFileAsText(file).then(function (text) {{
            return rowsToMaps(parseDelimitedText(text));
          }});
        }}

        function confirmImport(maps, targetYear) {{
          var years = maps.years || [];
          var yearLine =
            years.length === 1
              ? String(years[0])
              : years.join(', ');
          var msg =
            t(
              '取り込み: ' +
                maps.imported +
                ' 日分（' +
                yearLine +
                '年）\\n売上合計: ' +
                formatMoney(sumSales(maps.salesByDate)),
              'Import ' +
                maps.imported +
                ' day(s) (' +
                yearLine +
                ')\\nTotal sales: ' +
                formatMoney(sumSales(maps.salesByDate))
            );
          if (maps.hasFoodCol || maps.hasDrinkCol) {{
            msg +=
              '\\n' +
              t(
                'フード/ドリンク: フード ' +
                  (maps.foodCount || 0) +
                  ' 日 / ドリンク ' +
                  (maps.drinkCount || 0) +
                  ' 日（片方のみの日は店舗売上から逆算）',
                'Food/Drink: food ' +
                  (maps.foodCount || 0) +
                  ' day(s) / drink ' +
                  (maps.drinkCount || 0) +
                  ' day(s) (missing side = Store − other)'
              );
          }}
          if (maps.mismatchCount > 0) {{
            msg +=
              '\\n' +
              t(
                '注意: 店舗売上 ≠ フード+ドリンク の日が ' +
                  maps.mismatchCount +
                  ' 日あります。MEP では Drink＝店舗−フードで再計算されます。',
                'Note: Store ≠ Food+Drink on ' +
                  maps.mismatchCount +
                  ' day(s). MEP recomputes Drink as Store − Food.'
              );
          }}
          if (targetYear != null && years.indexOf(Number(targetYear)) < 0) {{
            msg +=
              '\\n\\n' +
              t(
                '表示中の年（' + targetYear + '）はファイルに含まれていません。該当年のみ反映します。',
                'The open year (' +
                  targetYear +
                  ') is not in this file. Only matching dates will be applied.'
              );
          }} else if (targetYear != null && years.length > 1) {{
            msg +=
              '\\n\\n' +
              t(
                '表示中の年（' + targetYear + '）の日付のみ表に反映します。',
                'Only dates for the open year (' + targetYear + ') will be applied.'
              );
          }}
          msg += '\\n\\n' + t('この内容で表に反映しますか？', 'Apply to the table?');
          return window.confirm(msg);
        }}

        function applyToRowState(rowStateByIso, maps, yearFilter) {{
          if (!rowStateByIso || !maps) return;
          var yf = yearFilter != null ? Number(yearFilter) : NaN;
          Object.keys(maps.salesByDate).forEach(function (iso) {{
            if (Number.isFinite(yf) && isoYear(iso) !== yf) return;
            var biz = maps.businessDayByDate[iso] !== false;
            var sales = Number(maps.salesByDate[iso]);
            if (!biz || !Number.isFinite(sales) || sales <= 0) {{
              rowStateByIso[iso] = {{ off: true, last: '0' }};
            }} else {{
              rowStateByIso[iso] = {{ off: false, last: String(Math.round(sales)) }};
            }}
          }});
        }}

        function countForYear(maps, year) {{
          var n = 0;
          Object.keys(maps.salesByDate).forEach(function (iso) {{
            if (isoYear(iso) === year) n++;
          }});
          return n;
        }}

        var fileInput = null;
        function ensureFileInput() {{
          if (fileInput) return fileInput;
          fileInput = document.createElement('input');
          fileInput.type = 'file';
          fileInput.accept = '.csv,.txt,.tsv,.xlsx,.xls';
          fileInput.style.display = 'none';
          document.body.appendChild(fileInput);
          return fileInput;
        }}

        function bindButton(btn, options) {{
          if (!btn || btn.getAttribute('data-kpi-import-bound') === '1') return;
          btn.setAttribute('data-kpi-import-bound', '1');
          var tip = t(
            'CSVで日次売上を取り込めます。Excel（.xlsx）も可。任意でフード/ドリンク列（どちらか一方でも可）。',
            'Import daily sales from CSV or Excel (.xlsx). Optional Food/Drink columns (either side OK).'
          );
          btn.setAttribute('data-tooltip', tip);
          btn.removeAttribute('title');

          btn.addEventListener('click', function () {{
            var input = ensureFileInput();
            input.value = '';
            input.onchange = function () {{
              var file = input.files && input.files[0];
              if (!file) return;
              parseFile(file)
                .then(function (maps) {{
                  var targetYear =
                    options && typeof options.getYear === 'function'
                      ? options.getYear()
                      : null;
                  if (!confirmImport(maps, targetYear)) return;
                  if (targetYear != null && countForYear(maps, Number(targetYear)) === 0) {{
                    window.alert(
                      t(
                        'このファイルに表示中の年（' + targetYear + '）の日付がありません。',
                        'This file has no dates for the open year (' + targetYear + ').'
                      )
                    );
                    return;
                  }}
                  if (options && typeof options.applyMaps === 'function') {{
                    options.applyMaps(maps, targetYear);
                  }}
                }})
                .catch(function (err) {{
                  var code = err && err.message;
                  if (code === 'xlsx') {{
                    window.alert(
                      t(
                        'Excel ライブラリを読み込めませんでした。CSVで保存してから再度お試しください。',
                        'Could not load the Excel library. Save as CSV and try again.'
                      )
                    );
                    return;
                  }}
                  if (code === 'empty') {{
                    window.alert(
                      t('ファイルが空です。', 'The file is empty.')
                    );
                    return;
                  }}
                  if (code === 'columns') {{
                    window.alert(
                      t(
                        '列を認識できませんでした。1行目に「日付」「店舗売上」（任意で「フード売上」「ドリンク売上」）などの列名が必要です。',
                        'Could not detect columns. Row 1 needs headers such as Date, Store Sales (optional Food Sales / Drink Sales).'
                      )
                    );
                    return;
                  }}
                  if (code === 'rows') {{
                    window.alert(
                      t(
                        '有効な日付行がありません。日付列（YYYY-MM-DD など）を確認してください。',
                        'No valid date rows found. Check the date column (YYYY-MM-DD, etc.).'
                      )
                    );
                    return;
                  }}
                  window.alert(
                    t(
                      'ファイルを読み取れませんでした。1行目に列名（日付・営業日・売上など）があるか確認してください。' +
                        (code ? '\\n(' + code + ')' : ''),
                      'Could not read the file. Ensure row 1 has column headers (date, business day, sales, etc.).' +
                        (code ? '\\n(' + code + ')' : '')
                    )
                  );
                }});
            }};
            input.click();
          }});
        }}

        window.__KPI_DAILY_IMPORT = {{
          parseFile: parseFile,
          rowsToMaps: rowsToMaps,
          applyToRowState: applyToRowState,
          bindButton: bindButton,
          tooltip: function () {{
            return t(
              'CSVで日次売上を取り込めます。Excel（.xlsx）も可。任意でフード/ドリンク列（どちらか一方でも可）。',
              'Import daily sales from CSV or Excel (.xlsx). Optional Food/Drink columns (either side OK).'
            );
          }},
        }};
      }})();
"""

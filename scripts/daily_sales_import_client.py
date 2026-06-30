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
          '売上',
          '売上高',
          '売上金額',
          'sales',
          'amount',
          'netsales',
          'dailysales',
          'grosssales',
        ];

        function matchKey(norm, keys) {{
          for (var i = 0; i < keys.length; i++) {{
            var k = normalizeHeader(keys[i]);
            if (norm === k || norm.indexOf(k) >= 0 || k.indexOf(norm) >= 0) return true;
          }}
          return false;
        }}

        function detectColumns(headerRow) {{
          var dateIdx = -1;
          var bizIdx = -1;
          var salesIdx = -1;
          for (var c = 0; c < headerRow.length; c++) {{
            var norm = normalizeHeader(headerRow[c]);
            if (!norm) continue;
            if (dateIdx < 0 && matchKey(norm, DATE_KEYS)) dateIdx = c;
            else if (bizIdx < 0 && matchKey(norm, BIZ_KEYS)) bizIdx = c;
            else if (salesIdx < 0 && matchKey(norm, SALES_KEYS)) salesIdx = c;
          }}
          if (dateIdx < 0 && headerRow.length >= 1) dateIdx = 0;
          if (salesIdx < 0 && headerRow.length >= 2) {{
            salesIdx = headerRow.length - 1;
            while (salesIdx === dateIdx && salesIdx > 0) salesIdx--;
          }}
          return {{ dateIdx: dateIdx, bizIdx: bizIdx, salesIdx: salesIdx }};
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

        function rowsToMaps(rows) {{
          if (!rows || !rows.length) throw new Error('empty');
          var header = rows[0].map(function (c) {{ return String(c == null ? '' : c); }});
          var cols = detectColumns(header);
          if (cols.dateIdx < 0 || cols.salesIdx < 0) throw new Error('columns');
          var salesByDate = {{}};
          var businessDayByDate = {{}};
          var years = {{}};
          var imported = 0;
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
            salesByDate[iso] = Math.round(sales);
            businessDayByDate[iso] = !!biz;
            years[isoYear(iso)] = true;
            imported++;
          }}
          if (!imported) throw new Error('rows');
          return {{
            salesByDate: salesByDate,
            businessDayByDate: businessDayByDate,
            years: Object.keys(years).map(Number).filter(Number.isFinite).sort(),
            imported: imported,
          }};
        }}

        function formatMoney(n) {{
          var v = Math.round(Number(n) || 0);
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

        function readFileAsText(file) {{
          return new Promise(function (resolve, reject) {{
            var reader = new FileReader();
            reader.onload = function () {{ resolve(String(reader.result || '')); }};
            reader.onerror = reject;
            reader.readAsText(file, 'UTF-8');
          }});
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
            'CSVで日次売上を取り込めます。Excel（.xlsx）も利用できます。',
            'Import daily sales from CSV. You can upload Excel (.xlsx) files as well.'
          );
          btn.setAttribute('title', tip);
          btn.setAttribute('data-tooltip', tip);

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
                  window.alert(
                    t(
                      'ファイルを読み取れませんでした。1行目に列名（日付・営業日・売上など）があるか確認してください。',
                      'Could not read the file. Ensure row 1 has column headers (date, business day, sales, etc.).'
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
              'CSVで日次売上を取り込めます。Excel（.xlsx）も利用できます。',
              'Import daily sales from CSV. You can upload Excel (.xlsx) files as well.'
            );
          }},
        }};
      }})();
"""

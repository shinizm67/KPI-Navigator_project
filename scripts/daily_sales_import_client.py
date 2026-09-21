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

        function isZhTw() {{
          return (
            String(document.documentElement.getAttribute('lang') || '')
              .toLowerCase()
              .indexOf('zh') === 0
          );
        }}

        function t(ja, en, zh) {{
          if (isJa()) return ja;
          if (isZhTw() && zh) return zh;
          return en;
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
         *  Missing column / empty / unparseable → unset (no key). Never infer from sales. */
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
        var DAILY_SALES_EXACT_KEYS = [
          '日次売上',
          '店舗売上',
          'storesales',
          'dailysales',
        ];
        var LUNCH_SALES_KEYS = ['ランチ売上', 'lunchsales', 'lunchsale'];
        var DINNER_SALES_KEYS = ['ディナー売上', 'dinnersales', 'dinnersale'];
        var LUNCH_CUST_KEYS = ['ランチ客数', 'lunchcustomers', 'lunchcustomer'];
        var DINNER_CUST_KEYS = ['ディナー客数', 'dinnercustomers', 'dinnercustomer'];
        var TOTAL_CUST_KEYS = ['トータル客数', '総客数', 'totalcustomers', 'totalcustomer'];
        var LUNCH_GROUP_KEYS = ['ランチ組数', 'lunchgroups', 'lunchgroup', 'lunchparties'];
        var DINNER_GROUP_KEYS = ['ディナー組数', 'dinnergroups', 'dinnergroup', 'dinnerparties'];
        var TOTAL_GROUP_KEYS = ['トータル組数', '総組数', 'totalgroups', 'totalgroup', 'totalparties'];
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
        var MEAL_PERSIST_PAIRS = [
          ['dinnerSalesByDate', 'dinner_sales'],
          ['totalCustomersByDate', 'total_customers'],
          ['dinnerCustomersByDate', 'dinner_customers'],
          ['totalGroupsByDate', 'total_groups'],
          ['dinnerGroupsByDate', 'dinner_groups'],
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

        function matchExact(norm, keys) {{
          for (var i = 0; i < keys.length; i++) {{
            var k = normalizeHeader(keys[i]);
            if (k && norm === k) return true;
          }}
          return false;
        }}

        function isFoodHeader(norm) {{
          return matchKey(norm, FOOD_KEYS);
        }}
        function isDrinkHeader(norm) {{
          return matchKey(norm, DRINK_KEYS);
        }}
        function isMealSalesHeader(norm) {{
          return matchExact(norm, LUNCH_SALES_KEYS) || matchExact(norm, DINNER_SALES_KEYS);
        }}

        function detectColumns(headerRow) {{
          var dateIdx = -1;
          var bizIdx = -1;
          var salesIdx = -1;
          var foodIdx = -1;
          var drinkIdx = -1;
          var lunchSalesIdx = -1;
          var dinnerSalesIdx = -1;
          var lunchCustIdx = -1;
          var dinnerCustIdx = -1;
          var totalCustIdx = -1;
          var lunchGroupsIdx = -1;
          var dinnerGroupsIdx = -1;
          var totalGroupsIdx = -1;
          for (var c = 0; c < headerRow.length; c++) {{
            var norm = normalizeHeader(headerRow[c]);
            if (!norm) continue;
            if (lunchSalesIdx < 0 && matchExact(norm, LUNCH_SALES_KEYS)) lunchSalesIdx = c;
            else if (dinnerSalesIdx < 0 && matchExact(norm, DINNER_SALES_KEYS)) dinnerSalesIdx = c;
            else if (lunchCustIdx < 0 && matchExact(norm, LUNCH_CUST_KEYS)) lunchCustIdx = c;
            else if (dinnerCustIdx < 0 && matchExact(norm, DINNER_CUST_KEYS)) dinnerCustIdx = c;
            else if (totalCustIdx < 0 && matchExact(norm, TOTAL_CUST_KEYS)) totalCustIdx = c;
            else if (lunchGroupsIdx < 0 && matchExact(norm, LUNCH_GROUP_KEYS)) lunchGroupsIdx = c;
            else if (dinnerGroupsIdx < 0 && matchExact(norm, DINNER_GROUP_KEYS)) dinnerGroupsIdx = c;
            else if (totalGroupsIdx < 0 && matchExact(norm, TOTAL_GROUP_KEYS)) totalGroupsIdx = c;
            else if (foodIdx < 0 && isFoodHeader(norm)) foodIdx = c;
            else if (drinkIdx < 0 && isDrinkHeader(norm)) drinkIdx = c;
            else if (dateIdx < 0 && matchKey(norm, DATE_KEYS)) dateIdx = c;
            else if (bizIdx < 0 && matchKey(norm, BIZ_KEYS)) bizIdx = c;
            else if (salesIdx < 0 && matchExact(norm, DAILY_SALES_EXACT_KEYS)) salesIdx = c;
            else if (
              salesIdx < 0 &&
              matchKey(norm, SALES_KEYS) &&
              !isFoodHeader(norm) &&
              !isDrinkHeader(norm) &&
              !isMealSalesHeader(norm)
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
                salesIdx === bizIdx ||
                salesIdx === lunchSalesIdx ||
                salesIdx === dinnerSalesIdx ||
                salesIdx === lunchCustIdx ||
                salesIdx === dinnerCustIdx ||
                salesIdx === totalCustIdx ||
                salesIdx === lunchGroupsIdx ||
                salesIdx === dinnerGroupsIdx ||
                salesIdx === totalGroupsIdx)
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
            lunchSalesIdx: lunchSalesIdx,
            dinnerSalesIdx: dinnerSalesIdx,
            lunchCustIdx: lunchCustIdx,
            dinnerCustIdx: dinnerCustIdx,
            totalCustIdx: totalCustIdx,
            lunchGroupsIdx: lunchGroupsIdx,
            dinnerGroupsIdx: dinnerGroupsIdx,
            totalGroupsIdx: totalGroupsIdx,
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

        function parseBizCell(raw) {{
          /* Three-value: true=open, false=closed, null=unset. Never infer from sales. */
          if (raw == null || raw === '') return null;
          if (typeof raw === 'number') {{
            if (!Number.isFinite(raw)) return null;
            return raw === 0 ? false : true;
          }}
          var s = String(raw).trim().toLowerCase();
          if (!s) return null;
          if (s === '0' || s === 'false' || s === 'no' || s === 'off' || s === '休' || s === '店休' || s === '×' || s === 'x') {{
            return false;
          }}
          if (s === '1' || s === 'true' || s === 'yes' || s === 'on' || s === '営業' || s === '○' || s === '◯') {{
            return true;
          }}
          var n = Number(s);
          if (Number.isFinite(n) && s !== '') {{
            return n === 0 ? false : true;
          }}
          return null;
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

        function mealKindLabel(kind) {{
          if (kind === 'sales') return t('売上', 'Sales', '銷售');
          if (kind === 'customers') return t('客数', 'Customers', '客數');
          return t('組数', 'Parties', '組數');
        }}

        function mealError(iso, kind, reason) {{
          var detail =
            reason === 'mismatch'
              ? t(
                  '合計と内訳が一致しません。値は自動修正しません。',
                  'Total and breakdown do not match. Values are not auto-corrected.',
                  '合計與明細不一致。不會自動修正。'
                )
              : reason === 'lunch-only'
                ? t(
                    'ランチを取り込むには合計とディナーの両方が必要です。',
                    'Lunch requires both total and dinner.',
                    '匯入午餐需要合計與晚餐。'
                  )
              : reason === 'dinner-gt-total'
                ? t(
                    'ディナーが合計を超えています。値は自動修正しません。',
                    'Dinner exceeds total. Values are not auto-corrected.',
                    '晚餐超過合計。不會自動修正。'
                  )
              : reason === 'sales-total-missing'
                ? t(
                    '時間帯売上が明示されているため、日次売上セルが必要です。空欄を0としては扱いません。',
                    'A daily sales cell is required when meal sales are explicit. Blank is not treated as 0.',
                    '已填時段銷售時，日次銷售儲存格不可空白。空白不視為0。'
                  )
                : t('不正な値です。', 'Invalid value.', '值無效。');
          var err = new Error('meal-invalid');
          err.userMessage = String(iso || '') + ' — ' + mealKindLabel(kind) + ': ' + detail;
          return err;
        }}

        function readMealCell(row, idx, asCount) {{
          if (idx < 0 || !cellHasValue(row, idx)) return {{ missing: true }};
          var raw = row[idx];
          var n;
          if (typeof raw === 'number') {{
            n = raw;
          }} else {{
            var s = String(raw).replace(/[¥$,\\s]/g, '').trim();
            if (s === '' || s === '-') return {{ missing: true }};
            if (!/^-?\\d+(\\.\\d+)?$/.test(s)) return {{ error: 'invalid' }};
            n = Number(s);
          }}
          if (!Number.isFinite(n) || n < 0) return {{ error: 'invalid' }};
          if (asCount && n !== Math.floor(n)) return {{ error: 'invalid' }};
          return {{ value: Math.round(n) }};
        }}

        function putMeal(map, iso, cell) {{
          if (!cell || cell.missing) return;
          map[iso] = cell.value;
        }}

        function mealCellOn(cell) {{
          return !!(cell && !cell.missing && cell.error !== 'invalid');
        }}

        function validateMealTriple(iso, kind, totalCell, lunchCell, dinnerCell) {{
          var hasL = mealCellOn(lunchCell);
          var hasD = mealCellOn(dinnerCell);
          var hasT = mealCellOn(totalCell);
          if (hasL && !(hasT && hasD)) return mealError(iso, kind, 'lunch-only');
          if (hasT && hasD && dinnerCell.value > totalCell.value) {{
            return mealError(iso, kind, 'dinner-gt-total');
          }}
          if (hasT && hasL && hasD && lunchCell.value + dinnerCell.value !== totalCell.value) {{
            return mealError(iso, kind, 'mismatch');
          }}
          return null;
        }}

        function salesCsvAllowsRestaurantFields() {{
          /* Missing/legacy Business Type stays restaurant so existing CSVs keep Unit 4 persist. */
          if (window.KpiBusinessType && typeof window.KpiBusinessType.isRestaurantLike === 'function') {{
            try {{
              return !!window.KpiBusinessType.isRestaurantLike();
            }} catch (_eBt) {{}}
          }}
          return true;
        }}

        function rowsToMaps(rows) {{
          if (!rows || !rows.length) throw new Error('empty');
          var header = rows[0].map(function (c) {{ return String(c == null ? '' : c); }});
          var cols = detectColumns(header);
          if (cols.dateIdx < 0 || cols.salesIdx < 0) throw new Error('columns');
          var allowRestaurant = salesCsvAllowsRestaurantFields();
          var pending = [];
          var mealErrors = [];
          for (var r = 1; r < rows.length; r++) {{
            var row = rows[r];
            if (!row || !row.length) continue;
            var iso = parseDateCell(row[cols.dateIdx]);
            if (!iso) continue;
            var sales = Math.round(parseSalesCell(row[cols.salesIdx]));
            var biz = cols.bizIdx >= 0 ? parseBizCell(row[cols.bizIdx]) : null;
            var lunchSales = readMealCell(row, cols.lunchSalesIdx, false);
            var dinnerSales = readMealCell(row, cols.dinnerSalesIdx, false);
            var lunchCust = readMealCell(row, cols.lunchCustIdx, true);
            var dinnerCust = readMealCell(row, cols.dinnerCustIdx, true);
            var totalCust = readMealCell(row, cols.totalCustIdx, true);
            var lunchGroups = readMealCell(row, cols.lunchGroupsIdx, true);
            var dinnerGroups = readMealCell(row, cols.dinnerGroupsIdx, true);
            var totalGroups = readMealCell(row, cols.totalGroupsIdx, true);
            if (allowRestaurant) {{
              var mealCells = [
                [lunchSales, 'sales'],
                [dinnerSales, 'sales'],
                [lunchCust, 'customers'],
                [dinnerCust, 'customers'],
                [totalCust, 'customers'],
                [lunchGroups, 'groups'],
                [dinnerGroups, 'groups'],
                [totalGroups, 'groups'],
              ];
              for (var mi = 0; mi < mealCells.length; mi++) {{
                if (mealCells[mi][0] && mealCells[mi][0].error === 'invalid') {{
                  mealErrors.push(mealError(iso, mealCells[mi][1], 'invalid'));
                }}
              }}
              var dailySalesMissing = !cellHasValue(row, cols.salesIdx);
              if ((mealCellOn(lunchSales) || mealCellOn(dinnerSales)) && dailySalesMissing) {{
                mealErrors.push(mealError(iso, 'sales', 'sales-total-missing'));
              }}
              var salesTotalCell = dailySalesMissing
                ? {{ missing: true }}
                : {{ value: sales, missing: false }};
              var vSales = validateMealTriple(iso, 'sales', salesTotalCell, lunchSales, dinnerSales);
              if (vSales) mealErrors.push(vSales);
              var vCust = validateMealTriple(iso, 'customers', totalCust, lunchCust, dinnerCust);
              if (vCust) mealErrors.push(vCust);
              var vGroups = validateMealTriple(iso, 'groups', totalGroups, lunchGroups, dinnerGroups);
              if (vGroups) mealErrors.push(vGroups);
            }}
            pending.push({{
              iso: iso,
              sales: sales,
              biz: biz,
              row: row,
              lunchSales: lunchSales,
              dinnerSales: dinnerSales,
              lunchCust: lunchCust,
              dinnerCust: dinnerCust,
              totalCust: totalCust,
              lunchGroups: lunchGroups,
              dinnerGroups: dinnerGroups,
              totalGroups: totalGroups,
            }});
          }}
          if (mealErrors.length) throw mealErrors[0];
          var salesByDate = {{}};
          var businessDayByDate = {{}};
          var foodByDate = {{}};
          var drinkByDate = {{}};
          var dinnerSalesByDate = {{}};
          var lunchSalesByDate = {{}};
          var totalCustomersByDate = {{}};
          var lunchCustomersByDate = {{}};
          var dinnerCustomersByDate = {{}};
          var totalGroupsByDate = {{}};
          var lunchGroupsByDate = {{}};
          var dinnerGroupsByDate = {{}};
          var years = {{}};
          var imported = 0;
          var foodCount = 0;
          var drinkCount = 0;
          var mismatchCount = 0;
          for (var p = 0; p < pending.length; p++) {{
            var rec = pending[p];
            salesByDate[rec.iso] = rec.sales;
            if (rec.biz !== null) businessDayByDate[rec.iso] = !!rec.biz;
            years[isoYear(rec.iso)] = true;
            imported++;
            if (!allowRestaurant) continue;
            putMeal(lunchSalesByDate, rec.iso, rec.lunchSales);
            putMeal(dinnerSalesByDate, rec.iso, rec.dinnerSales);
            putMeal(lunchCustomersByDate, rec.iso, rec.lunchCust);
            putMeal(dinnerCustomersByDate, rec.iso, rec.dinnerCust);
            putMeal(totalCustomersByDate, rec.iso, rec.totalCust);
            putMeal(lunchGroupsByDate, rec.iso, rec.lunchGroups);
            putMeal(dinnerGroupsByDate, rec.iso, rec.dinnerGroups);
            putMeal(totalGroupsByDate, rec.iso, rec.totalGroups);
            var hasFood = cellHasValue(rec.row, cols.foodIdx);
            var hasDrink = cellHasValue(rec.row, cols.drinkIdx);
            if (!hasFood && !hasDrink) continue;
            var food = hasFood ? Math.round(parseSalesCell(rec.row[cols.foodIdx])) : null;
            var drink = hasDrink ? Math.round(parseSalesCell(rec.row[cols.drinkIdx])) : null;
            if (hasFood && hasDrink) {{
              if (Math.abs(rec.sales - (food + drink)) > 1) mismatchCount++;
            }} else if (hasFood) {{
              drink = Math.max(0, rec.sales - food);
            }} else {{
              food = Math.max(0, rec.sales - drink);
            }}
            foodByDate[rec.iso] = food;
            drinkByDate[rec.iso] = drink;
            if (hasFood) foodCount++;
            if (hasDrink) drinkCount++;
          }}
          if (!imported) throw new Error('rows');
          return {{
            salesByDate: salesByDate,
            businessDayByDate: businessDayByDate,
            foodByDate: foodByDate,
            drinkByDate: drinkByDate,
            dinnerSalesByDate: dinnerSalesByDate,
            lunchSalesByDate: lunchSalesByDate,
            totalCustomersByDate: totalCustomersByDate,
            lunchCustomersByDate: lunchCustomersByDate,
            dinnerCustomersByDate: dinnerCustomersByDate,
            totalGroupsByDate: totalGroupsByDate,
            lunchGroupsByDate: lunchGroupsByDate,
            dinnerGroupsByDate: dinnerGroupsByDate,
            years: Object.keys(years).map(Number).filter(Number.isFinite).sort(),
            imported: imported,
            foodCount: foodCount,
            drinkCount: drinkCount,
            mismatchCount: mismatchCount,
            hasFoodCol: allowRestaurant && cols.foodIdx >= 0,
            hasDrinkCol: allowRestaurant && cols.drinkIdx >= 0,
          }};
        }}

        function writeDailyMealViaGetStore(field, iso, value) {{
          if (!window.KpiYearStore || typeof KpiYearStore.getStore !== 'function') return false;
          var store = KpiYearStore.getStore();
          if (!store || typeof store !== 'object') return false;
          var y = isoYear(iso);
          if (!Number.isFinite(y)) return false;
          var rec = null;
          if (typeof KpiYearStore.ensureYearMepData === 'function') {{
            rec = KpiYearStore.ensureYearMepData(y);
          }} else {{
            if (!store.years || typeof store.years !== 'object') store.years = {{}};
            rec = store.years[y] || store.years[String(y)];
            if (!rec || typeof rec !== 'object') {{
              rec = {{ year: y, plan: {{}} }};
              store.years[y] = rec;
            }}
          }}
          if (!rec || typeof rec !== 'object') return false;
          if (!rec.dailyMeal || typeof rec.dailyMeal !== 'object' || Array.isArray(rec.dailyMeal)) {{
            rec.dailyMeal = {{}};
          }}
          if (!rec.dailyMeal[field] || typeof rec.dailyMeal[field] !== 'object' || Array.isArray(rec.dailyMeal[field])) {{
            rec.dailyMeal[field] = {{}};
          }}
          if (value === undefined || value === null) {{
            if (Object.prototype.hasOwnProperty.call(rec.dailyMeal[field], iso)) delete rec.dailyMeal[field][iso];
            return true;
          }}
          if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) return false;
          rec.dailyMeal[field][iso] = Math.round(value);
          return true;
        }}

        function persistDailyMealFromMaps(maps) {{
          if (!maps) return 0;
          if (!salesCsvAllowsRestaurantFields()) return 0;
          var ops = [];
          for (var pi = 0; pi < MEAL_PERSIST_PAIRS.length; pi++) {{
            var pair = MEAL_PERSIST_PAIRS[pi];
            var src = maps[pair[0]];
            if (!src || typeof src !== 'object') continue;
            var keys = Object.keys(src);
            for (var ki = 0; ki < keys.length; ki++) {{
              var iso = keys[ki];
              if (!Object.prototype.hasOwnProperty.call(src, iso)) continue;
              var val = src[iso];
              if (!Number.isFinite(isoYear(iso))) {{
                throw mealError(iso, 'sales', 'invalid');
              }}
              if (typeof val !== 'number' || !Number.isFinite(val) || val < 0) {{
                throw mealError(iso, 'sales', 'invalid');
              }}
              ops.push({{ field: pair[1], iso: String(iso), value: Math.round(val) }});
            }}
          }}
          if (!ops.length) return 0;
          var hasWrite = !!(window.KpiYearStore && typeof KpiYearStore.writeDailyMeal === 'function');
          var hasStore = !!(window.KpiYearStore && typeof KpiYearStore.getStore === 'function');
          if (!hasWrite && !hasStore) {{
            var missing = new Error('meal-persist');
            missing.userMessage = t(
              '取り込みを中止しました。保存APIがありません。',
              'Import stopped. Persist API is unavailable.',
              '已停止匯入。沒有可用的儲存API。'
            );
            throw missing;
          }}
          var wrote = 0;
          try {{
            for (var oi = 0; oi < ops.length; oi++) {{
              var op = ops[oi];
              var ok = hasWrite
                ? KpiYearStore.writeDailyMeal(op.field, op.iso, op.value)
                : writeDailyMealViaGetStore(op.field, op.iso, op.value);
              if (!ok) {{
                var fail = new Error('meal-persist');
                fail.userMessage = t(
                  '取り込みを中止しました。',
                  'Import stopped.',
                  '已停止匯入。'
                );
                throw fail;
              }}
              wrote++;
            }}
          }} catch (eWrite) {{
            if (eWrite && (eWrite.message === 'meal-persist' || eWrite.message === 'meal-invalid')) throw eWrite;
            var wrap = new Error('meal-persist');
            wrap.userMessage = t(
              '取り込みを中止しました。',
              'Import stopped.',
              '已停止匯入。'
            );
            throw wrap;
          }}
          return wrote;
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

        function confirmImport(maps, targetYear, opts) {{
          opts = opts || {{}};
          var persistByCsvYear = !!opts.persistByCsvYear;
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
          if (persistByCsvYear) {{
            msg +=
              '\\n\\n' +
              t(
                'CSVの日付年ごとに保存します（' +
                  yearLine +
                  '）。表示年へ移動する必要はありません。',
                'Each CSV date year will be saved (' +
                  yearLine +
                  '). You do not need to change the displayed year.'
              );
          }} else if (targetYear != null && years.indexOf(Number(targetYear)) < 0) {{
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
          /* KPI-CSV-IMPORT-SAFETY-6H */
          msg +=
            '\\n\\n' +
            t(
              '同じ日付のデータは取込値で上書きされます。\\n売上が空欄の場合は 0 として保存されます。',
              'Existing data for the same date will be overwritten with imported values.\\nBlank sales are saved as 0.',
              '相同日期的既有資料會被匯入值覆寫。\\n銷售額空白時會以 0 儲存。'
            );
          msg +=
            '\\n\\n' +
            t('この内容で表に反映しますか？', 'Apply to the table?', '要套用到表格嗎？');
          return window.confirm(msg);
        }}

        function applyToRowState(rowStateByIso, maps, yearFilter) {{
          if (!rowStateByIso || !maps) return;
          var yf = yearFilter != null ? Number(yearFilter) : NaN;
          Object.keys(maps.salesByDate).forEach(function (iso) {{
            if (Number.isFinite(yf) && isoYear(iso) !== yf) return;
            /* KPI-BIZDAY-IMPORT-DD: never treat missing/0 as open via !== false */
            var bizMap0 = maps.businessDayByDate || {{}};
            var biz = Object.prototype.hasOwnProperty.call(bizMap0, iso)
              ? !!bizMap0[iso]
              : Number(maps.salesByDate[iso]) > 0;
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

        function getDailyImportApi() {{
          var api = window.__KPI_DAILY_IMPORT;
          if (
            !api ||
            typeof api.parseFile !== 'function' ||
            typeof api.rowsToMaps !== 'function' ||
            typeof api.applyToRowState !== 'function'
          ) {{
            return null;
          }}
          return api;
        }}

        function alertEngineMissing() {{
          window.alert(
            t(
              'CSV取込エンジンの読み込みに失敗しました。ページを再読み込みしてください。',
              'CSV import engine failed to load. Please reload the page.',
              'CSV 匯入引擎載入失敗，請重新整理頁面。'
            )
          );
        }}

        function beginImport(options) {{
          var api = getDailyImportApi();
          if (!api) {{
            alertEngineMissing();
            return;
          }}
          var btApi = window.KpiBusinessType;
          if (!btApi || typeof btApi.isBusinessTypeSet !== 'function' || !btApi.isBusinessTypeSet()) {{
            window.alert(t(
              'データを取り込む前に業種を選択してください。',
              'Please select your business type before importing data.',
              '請先選擇業種類型，再匯入資料。'
            ));
            return;
          }}
          if (window.__KPI_BUSY && window.__KPI_BUSY.isBusy()) return;
          var input = ensureFileInput();
          input.value = '';
          input.onchange = function () {{
            var file = input.files && input.files[0];
            if (!file) return;
            var live = getDailyImportApi();
            if (!live) {{
              alertEngineMissing();
              return;
            }}
            var busy = window.__KPI_BUSY;
            if (busy && typeof busy.show === 'function') busy.show('parse');
            live.parseFile(file)
                .then(function (maps) {{
                  if (busy && typeof busy.hide === 'function') busy.hide();
                  var targetYear =
                    options && typeof options.getYear === 'function'
                      ? options.getYear()
                      : null;
                  var persistByCsvYear = !!(options && options.persistByCsvYear);
                  if (!confirmImport(maps, targetYear, {{ persistByCsvYear: persistByCsvYear }})) return;
                  if (
                    !persistByCsvYear &&
                    targetYear != null &&
                    countForYear(maps, Number(targetYear)) === 0
                  ) {{
                    window.alert(
                      t(
                        'このファイルに表示中の年（' + targetYear + '）の日付がありません。',
                        'This file has no dates for the open year (' + targetYear + ').'
                      )
                    );
                    return;
                  }}
                  if (options && typeof options.applyMaps !== 'function') return;
                  var apply = function () {{
                    return Promise.resolve(options.applyMaps(maps, targetYear));
                  }};
                  if (busy && typeof busy.run === 'function') {{
                    return busy.run('import', apply, {{ count: maps.imported }});
                  }}
                  return apply();
                }})
                .catch(function (err) {{
                  if (window.__KPI_BUSY && typeof window.__KPI_BUSY.hide === 'function') {{
                    window.__KPI_BUSY.hide();
                  }}
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
                  if (code === 'meal-invalid' || code === 'meal-persist' || code === 'persist-unavailable') {{
                    window.alert(
                      (err && err.userMessage) ||
                        t('取り込みを中止しました。', 'Import stopped.', '已停止匯入。')
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
            beginImport(options);
          }});
        }}

        window.__KPI_DAILY_IMPORT = {{
          parseFile: parseFile,
          parseDelimitedText: parseDelimitedText,
          rowsToMaps: rowsToMaps,
          detectColumns: detectColumns,
          parseBizCell: parseBizCell,
          salesCsvAllowsRestaurantFields: salesCsvAllowsRestaurantFields,
          persistDailyMealFromMaps: persistDailyMealFromMaps,
          applyToRowState: applyToRowState,
          getDailyImportApi: getDailyImportApi,
          beginImport: beginImport,
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

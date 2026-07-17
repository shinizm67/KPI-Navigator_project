"""PL reference budget — L1 variable frame + L2 per-line guideline.

L1 (row var_ref_budget):
  amount = sales × max(0, targetTotalCostRate − fixedCostRate)

L2 (per-line expense detail cells, independent of L1 — method A):
  amount = sales × median(same-month lineExpense/sales over past years)
  Fallback chain per lineId/month (PRIOR YEARS ONLY, for consistency &
  defensibility — current-year other months are NOT used because they do
  not reflect seasonality/busy-slow patterns):
    1. past years, same month
    2. past years, any month
    3. no data → hide guideline (row height not expanded; a brief notice
       is shown instead — see build_pl_table_page toggle wiring)
  Applies to both fixed and variable expense lines. Gated by the corner
  +/- toggle (body.pl-guide-on); off → all L2 hints cleared.
"""

from __future__ import annotations


def pl_reference_budget_client_js() -> str:
    return r"""
      var PL_REF_BUDGET_RATE_KEY = 'kpiNavigator.plTargetCostRate';
      var PL_REF_BUDGET_DEFAULT_RATE = 0.65;
      var PL_REF_BUDGET_ROW = 'var_ref_budget';
      var PL_REF_PLACEHOLDER = 1234;
      var PL_REF_L2_LOOKBACK = 3;

      /* 1 リフレッシュ内メモ化: localStorage / 年ストアの全体 JSON.parse を
         セル×年×月ごとに繰り返さず、パス内で使い回して軽量化する。
         同期処理の間だけ有効で、終了時に必ず破棄するため陳腐化しない。 */
      var _plRefCache = null;
      var _plRefCacheDepth = 0;
      function plRefCacheEnter() {
        if (_plRefCacheDepth === 0) {
          _plRefCache = {
            store: undefined,
            sales: {},
            expMap: {},
            forecast: undefined,
          };
        }
        _plRefCacheDepth++;
      }
      function plRefCacheExit() {
        _plRefCacheDepth--;
        if (_plRefCacheDepth <= 0) {
          _plRefCacheDepth = 0;
          _plRefCache = null;
        }
      }
      var PL_REF_L2_OVER_RATIO = 1.05;
      var PL_REF_ANNUAL_DAILY_KEY = 'kpiNavigator.annualDailyShared';

      function plRefBudgetLoadTargetRate() {
        try {
          var raw = localStorage.getItem(PL_REF_BUDGET_RATE_KEY);
          if (raw == null || raw === '') return PL_REF_BUDGET_DEFAULT_RATE;
          var n = Number(raw);
          if (!Number.isFinite(n)) return PL_REF_BUDGET_DEFAULT_RATE;
          if (n > 1) n = n / 100;
          if (n < 0) n = 0;
          if (n > 1) n = 1;
          return n;
        } catch (_e) {
          return PL_REF_BUDGET_DEFAULT_RATE;
        }
      }

      function plRefBudgetReadYearStore() {
        if (_plRefCache && _plRefCache.store !== undefined) {
          return _plRefCache.store;
        }
        var gw = window.__KPI_DATA_GATEWAY;
        var result = null;
        if (gw && typeof gw.getJson === 'function') {
          try {
            result = gw.getJson('kpiNavigator.kpiYearStore');
          } catch (_e) {
            result = null;
          }
        }
        if (_plRefCache) _plRefCache.store = result;
        return result;
      }

      function plRefBudgetMedian(values) {
        var nums = (values || []).filter(function (n) {
          return Number.isFinite(n);
        });
        if (!nums.length) return null;
        nums.sort(function (a, b) {
          return a - b;
        });
        var mid = Math.floor(nums.length / 2);
        if (nums.length % 2) return nums[mid];
        return (nums[mid - 1] + nums[mid]) / 2;
      }

      function plRefBudgetSalesMapFromObject(map, year) {
        var out = [];
        var has = [];
        for (var i = 0; i < 12; i++) {
          out[i] = 0;
          has[i] = false;
        }
        if (!map || typeof map !== 'object') return { totals: out, has: has };
        var yStr = String(year);
        Object.keys(map).forEach(function (iso) {
          if (!iso || iso.length < 7) return;
          if (iso.slice(0, 4) !== yStr) return;
          var mo = parseInt(iso.slice(5, 7), 10);
          if (!(mo >= 1 && mo <= 12)) return;
          var v = Number(map[iso]);
          if (!Number.isFinite(v) || v === PL_REF_PLACEHOLDER) return;
          out[mo - 1] += v;
          has[mo - 1] = true;
        });
        return { totals: out, has: has };
      }

      function plRefBudgetSalesByMonth(year) {
        if (_plRefCache && _plRefCache.sales[year] !== undefined) {
          return _plRefCache.sales[year];
        }
        var store = plRefBudgetReadYearStore();
        var ds = store && store.timeline && store.timeline.dailySales;
        var result = plRefBudgetSalesMapFromObject(ds, year);
        if (_plRefCache) _plRefCache.sales[year] = result;
        return result;
      }

      function plRefBudgetForecastSalesByMonth(year) {
        if (_plRefCache && _plRefCache.forecast !== undefined && _plRefCache.forecast.year === year) {
          return _plRefCache.forecast.value;
        }
        var _forecastResult = plRefBudgetForecastSalesByMonthCompute(year);
        if (_plRefCache) _plRefCache.forecast = { year: year, value: _forecastResult };
        return _forecastResult;
      }

      function plRefBudgetForecastSalesByMonthCompute(year) {
        var gw = window.__KPI_DATA_GATEWAY;
        var map = null;
        if (gw && typeof gw.getJson === 'function') {
          try {
            var annual = gw.getJson(PL_REF_ANNUAL_DAILY_KEY);
            map = annual && annual.targetSalesByDate;
          } catch (_e) {}
        }
        var forecast = plRefBudgetSalesMapFromObject(map, year);
        var actual = plRefBudgetSalesByMonth(year);
        var out = [];
        var has = [];
        for (var mi = 0; mi < 12; mi++) {
          if (forecast.has[mi] && forecast.totals[mi] > 0) {
            out[mi] = forecast.totals[mi];
            has[mi] = true;
          } else {
            out[mi] = actual.totals[mi];
            has[mi] = actual.has[mi];
          }
        }
        return { totals: out, has: has };
      }

      function plRefBudgetFixedLineIds() {
        var ids = [];
        var seen = {};
        try {
          var raw = localStorage.getItem('kpiNavigator.plLineCatalog');
          if (raw) {
            var parsed = JSON.parse(raw);
            (parsed && parsed.lines ? parsed.lines : []).forEach(function (line) {
              if (!line || !line.lineId || line.active === false) return;
              if (line.bucket !== 'fixed') return;
              if (seen[line.lineId]) return;
              seen[line.lineId] = true;
              ids.push(String(line.lineId));
            });
          }
        } catch (_e) {}
        if (ids.length) return ids;
        document
          .querySelectorAll(
            '#pl-expense-detail-data-body tr[data-bucket="fixed"][data-line-id]'
          )
          .forEach(function (tr) {
            var id = tr.getAttribute('data-line-id');
            if (!id || seen[id]) return;
            seen[id] = true;
            ids.push(id);
          });
        return ids;
      }

      function plRefBudgetVariableLineIds() {
        var ids = [];
        var seen = {};
        try {
          var raw = localStorage.getItem('kpiNavigator.plLineCatalog');
          if (raw) {
            var parsed = JSON.parse(raw);
            (parsed && parsed.lines ? parsed.lines : []).forEach(function (line) {
              if (!line || !line.lineId || line.active === false) return;
              if (line.bucket !== 'variable') return;
              if (seen[line.lineId]) return;
              seen[line.lineId] = true;
              ids.push(String(line.lineId));
            });
          }
        } catch (_e) {}
        if (ids.length) return ids;
        document
          .querySelectorAll(
            '#pl-expense-detail-data-body tr[data-bucket="variable"][data-line-id]'
          )
          .forEach(function (tr) {
            var id = tr.getAttribute('data-line-id');
            if (!id || seen[id]) return;
            seen[id] = true;
            ids.push(id);
          });
        return ids;
      }

      function plRefBudgetReadExpenseMap(year) {
        if (_plRefCache && _plRefCache.expMap[year] !== undefined) {
          return _plRefCache.expMap[year];
        }
        var map = {};
        try {
          var raw = localStorage.getItem('kpi-pl-expenses-v1:' + year);
          var parsed = raw ? JSON.parse(raw) : {};
          if (parsed && typeof parsed === 'object') map = parsed;
        } catch (_e) {
          map = {};
        }
        if (_plRefCache) _plRefCache.expMap[year] = map;
        return map;
      }

      function plRefBudgetDailyExpenseMonth(year, lineId, mi) {
        var store = plRefBudgetReadYearStore();
        var rec = store && store.years && store.years[String(year)];
        var byLine = rec && rec.dailyExpenses && rec.dailyExpenses[lineId];
        if (!byLine || typeof byLine !== 'object') return { value: 0, has: false };
        var yStr = String(year);
        var moStr = String(mi + 1);
        if (moStr.length < 2) moStr = '0' + moStr;
        var sum = 0;
        var has = false;
        Object.keys(byLine).forEach(function (iso) {
          if (!iso || iso.length < 7) return;
          if (iso.slice(0, 4) !== yStr) return;
          if (iso.slice(5, 7) !== moStr) return;
          var n = Number(byLine[iso]);
          if (!Number.isFinite(n)) return;
          sum += n;
          has = true;
        });
        return { value: Math.round(sum), has: has };
      }

      function plRefBudgetLineExpenseMonth(year, lineId, mi) {
        var map = plRefBudgetReadExpenseMap(year);
        var key = lineId + ':' + mi;
        if (Object.prototype.hasOwnProperty.call(map, key)) {
          var n = Number(map[key]);
          if (Number.isFinite(n)) return { value: n, has: true };
        }
        return plRefBudgetDailyExpenseMonth(year, lineId, mi);
      }

      function plRefBudgetFixedByMonth(year) {
        var out = [];
        var has = [];
        for (var i = 0; i < 12; i++) {
          out[i] = 0;
          has[i] = false;
        }
        var ids = plRefBudgetFixedLineIds();
        if (!ids.length) return { totals: out, has: has };
        ids.forEach(function (lineId) {
          for (var mi = 0; mi < 12; mi++) {
            var got = plRefBudgetLineExpenseMonth(year, lineId, mi);
            if (!got.has) continue;
            out[mi] += got.value;
            has[mi] = true;
          }
        });
        return { totals: out, has: has };
      }

      function plRefL2RateForLineMonth(lineId, mi) {
        var sameMonth = [];
        var anyMonth = [];
        for (var back = 1; back <= PL_REF_L2_LOOKBACK; back++) {
          var y = plYear - back;
          if (!(y >= 2000)) continue;
          var sales = plRefBudgetSalesByMonth(y);
          for (var m = 0; m < 12; m++) {
            if (!sales.has[m] || !(sales.totals[m] > 0)) continue;
            var exp = plRefBudgetLineExpenseMonth(y, lineId, m);
            if (!exp.has) continue;
            var rate = exp.value / sales.totals[m];
            if (!Number.isFinite(rate) || rate < 0) continue;
            anyMonth.push(rate);
            if (m === mi) sameMonth.push(rate);
          }
        }
        // 前年以前のデータのみを根拠にする（一貫性・説明可能性を優先）。
        // 今年の他月は繁閑（季節性）を反映しないため目安の根拠にしない。
        var med = plRefBudgetMedian(sameMonth);
        if (med != null) return { rate: med, sample: sameMonth.length, basis: 'same-month' };
        med = plRefBudgetMedian(anyMonth);
        if (med != null) return { rate: med, sample: anyMonth.length, basis: 'any-month' };
        return null;
      }

      function plRefL2FormatHint(amount) {
        if (!Number.isFinite(amount)) return '';
        var money =
          typeof formatMoney === 'function' ? formatMoney(Math.round(amount)) : String(Math.round(amount));
        return isJa ? '目安 ' + money : '~' + money;
      }

      function plRefL2ClearCell(amtTd) {
        if (!amtTd) return;
        amtTd.removeAttribute('data-pl-l2-amount');
        amtTd.removeAttribute('data-pl-l2-rate');
        amtTd.removeAttribute('data-pl-l2-basis');
        amtTd.classList.remove('pl-amt-cell--has-l2', 'pl-amt-cell--over-l2');
        var tipBase = amtTd.getAttribute('data-pl-l2-base-title');
        if (tipBase != null) {
          if (tipBase) amtTd.title = tipBase;
          else amtTd.removeAttribute('title');
          amtTd.removeAttribute('data-pl-l2-base-title');
        }
        var hint = amtTd.querySelector('.pl-amt-cell__l2');
        if (hint) hint.remove();
      }

      function plRefL2ApplyCell(amtTd, info) {
        if (!amtTd || !info) {
          plRefL2ClearCell(amtTd);
          return;
        }
        if (!amtTd.hasAttribute('data-pl-l2-base-title')) {
          amtTd.setAttribute('data-pl-l2-base-title', amtTd.getAttribute('title') || '');
        }
        amtTd.setAttribute('data-pl-l2-amount', String(info.amount));
        amtTd.setAttribute('data-pl-l2-rate', String(Math.round(info.rate * 10000) / 100));
        amtTd.setAttribute('data-pl-l2-basis', info.basis);
        amtTd.classList.add('pl-amt-cell--has-l2');
        var actualParsed =
          typeof plRatioParseCellAmount === 'function'
            ? plRatioParseCellAmount(amtTd)
            : { value: 0, has: false };
        var over =
          actualParsed.has &&
          info.amount > 0 &&
          actualParsed.value > info.amount * PL_REF_L2_OVER_RATIO;
        amtTd.classList.toggle('pl-amt-cell--over-l2', !!over);
        var basisJa = info.basis === 'same-month' ? '過去同月' : '過去実績';
        var basisEn = info.basis === 'same-month' ? 'past same-month' : 'past sample';
        var tip = isJa
          ? '費目の参考予算（' +
            basisJa +
            '中央値 ' +
            (info.rate * 100).toFixed(1) +
            '% × 売上）。断定の適正値ではありません'
          : 'Line guideline (median ' +
            basisEn +
            ' ' +
            (info.rate * 100).toFixed(1) +
            '% × sales). Not a prescribed ideal';
        amtTd.title = tip;
        var hint = amtTd.querySelector('.pl-amt-cell__l2');
        if (!hint) {
          hint = document.createElement('span');
          hint.className = 'pl-amt-cell__l2';
          hint.setAttribute('aria-hidden', 'true');
          amtTd.appendChild(hint);
        }
        hint.textContent = plRefL2FormatHint(info.amount);
      }

      function plRefBudgetGuideOn() {
        try {
          return document.body.classList.contains('pl-guide-on');
        } catch (_e) {
          return false;
        }
      }

      function plRefBudgetAllLineIds() {
        var ids = [];
        var seen = {};
        plRefBudgetVariableLineIds().forEach(function (id) {
          if (id && !seen[id]) { seen[id] = true; ids.push(id); }
        });
        plRefBudgetFixedLineIds().forEach(function (id) {
          if (id && !seen[id]) { seen[id] = true; ids.push(id); }
        });
        return ids;
      }

      function plRefBudgetSetHasData(hasData) {
        try {
          document.body.classList.toggle('pl-guide-has-data', !!hasData);
        } catch (_e) {}
      }

      function refreshPlReferenceBudgetL2() {
        if (!plRefBudgetGuideOn()) {
          plRefBudgetSetHasData(false);
          document
            .querySelectorAll(
              '#pl-expense-detail-data-body .pl-amt-cell[data-field="amount"]'
            )
            .forEach(function (amtTd) {
              plRefL2ClearCell(amtTd);
            });
          return;
        }
        plRefCacheEnter();
        try {
          var sales = plRefBudgetForecastSalesByMonth(plYear);
          var lineIds = plRefBudgetAllLineIds();
          var rateCache = {};
          document
            .querySelectorAll(
              '#pl-expense-detail-data-body .pl-amt-cell[data-field="amount"][data-month]'
            )
            .forEach(function (amtTd) {
              var lineId = amtTd.getAttribute('data-row') || amtTd.getAttribute('data-line-id');
              var miRaw = amtTd.getAttribute('data-month');
              if (!lineId || miRaw === 'year') {
                plRefL2ClearCell(amtTd);
                return;
              }
              var mi = Number(miRaw);
              if (!Number.isFinite(mi) || mi < 0 || mi > 11) {
                plRefL2ClearCell(amtTd);
                return;
              }
              if (lineIds.indexOf(lineId) < 0) {
                plRefL2ClearCell(amtTd);
                return;
              }
              if (!sales.has[mi] || !(sales.totals[mi] > 0)) {
                plRefL2ClearCell(amtTd);
                return;
              }
              var cacheKey = lineId + ':' + mi;
              if (!Object.prototype.hasOwnProperty.call(rateCache, cacheKey)) {
                rateCache[cacheKey] = plRefL2RateForLineMonth(lineId, mi);
              }
              var stat = rateCache[cacheKey];
              if (!stat || !(stat.rate > 0)) {
                plRefL2ClearCell(amtTd);
                return;
              }
              var amount = Math.round(sales.totals[mi] * stat.rate);
              plRefL2ApplyCell(amtTd, {
                amount: amount,
                rate: stat.rate,
                basis: stat.basis,
                sample: stat.sample,
              });
            });
          // 目安が1つでも出せた時だけ行高を拡張（データ皆無なら行高そのまま）
          var hasAnyL2 =
            document.querySelectorAll(
              '#pl-expense-detail-data-body .pl-amt-cell--has-l2'
            ).length > 0;
          plRefBudgetSetHasData(hasAnyL2);
        } finally {
          plRefCacheExit();
        }
      }

      function refreshPlReferenceBudget() {
        plRefCacheEnter();
        try {
          refreshPlReferenceBudgetInner();
        } finally {
          plRefCacheExit();
        }
      }

      function refreshPlReferenceBudgetInner() {
        var targetRate = plRefBudgetLoadTargetRate();
        var sales = plRefBudgetForecastSalesByMonth(plYear);
        var fixed = plRefBudgetFixedByMonth(plYear);
        for (var mi = 0; mi < 12; mi++) {
          var amtTd = document.querySelector(
            '[data-field="amount"][data-row="' +
              PL_REF_BUDGET_ROW +
              '"][data-month="' +
              mi +
              '"]'
          );
          var ratioTd = document.querySelector(
            '[data-field="ratio"][data-row="' +
              PL_REF_BUDGET_ROW +
              '"][data-month="' +
              mi +
              '"]'
          );
          if (!amtTd || !ratioTd) continue;
          var amtSpan = amtTd.querySelector('.pl-amt-cell__text');
          var ratioSpan = ratioTd.querySelector('.pl-ratio-cell__text');
          if (!amtSpan || !ratioSpan) continue;
          if (!sales.has[mi] || !(sales.totals[mi] > 0)) {
            amtSpan.textContent = '\u2014';
            ratioSpan.textContent = '\u2014';
            amtTd.removeAttribute('title');
            continue;
          }
          var s = sales.totals[mi];
          var f = fixed.has[mi] ? fixed.totals[mi] : 0;
          var fixedRate = f / s;
          var varRate = targetRate - fixedRate;
          if (varRate < 0) varRate = 0;
          if (varRate > 1) varRate = 1;
          var amount = Math.round(s * varRate);
          amtSpan.textContent = formatMoney(amount);
          ratioSpan.textContent =
            typeof formatPlRatioPct === 'function'
              ? formatPlRatioPct(varRate * 100)
              : (Math.round(varRate * 10000) / 100).toFixed(2) + '%';
          var tip = isJa
            ? '変動費の参考枠 = 目標総費率 ' +
              (targetRate * 100).toFixed(0) +
              '% − 固定費率 ' +
              (fixedRate * 100).toFixed(1) +
              '%'
            : 'Variable guideline = target cost ' +
              (targetRate * 100).toFixed(0) +
              '% − fixed rate ' +
              (fixedRate * 100).toFixed(1) +
              '%';
          amtTd.title = tip;
          ratioTd.title = tip;
        }
        refreshPlReferenceBudgetL2();
      }

      window.__plRefreshReferenceBudget = refreshPlReferenceBudget;
      window.__plRefreshReferenceBudgetL2 = refreshPlReferenceBudgetL2;
"""

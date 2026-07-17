"""PL income block — read-only aggregates of MEP daily income.

Inserted INSIDE the main PL IIFE, so it shares `plYear`, `formatMoney`,
`isJa` from that scope. Fully read-only; income is entered daily on MEP and
the monthly cumulative is shown here (never editable in PL):

- Total Sales   = monthly sum of `kpiNavigator.kpiYearStore` timeline.dailySales
                  for `plYear` (legacy placeholder 1234 excluded). This is the
                  canonical grand total (= store + A + B) that MEP writes and
                  Annual/Insight consume.
- Sales A / B   = monthly sum of `years.{Y}.dailyIncome[streamId]` (ISO-keyed),
                  written daily on MEP. Shows "—" until data exists.
- Store Sales   = Total Sales − (Sales A + Sales B). Derived so `timeline.dailySales`
                  stays untouched (no double counting). Clamped at 0.
"""

from __future__ import annotations


def pl_income_client_js() -> str:
    """JS snippet inserted via f-string expression (single braces; already resolved)."""
    return """
      var PL_INCOME_STORE_KEY = 'kpiNavigator.kpiYearStore';
      var PL_INCOME_PLACEHOLDER = 1234;
      var PL_INCOME_STREAM_ROWS = ['sales_a', 'sales_b'];
      var plIncomeStoreTotals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
      var plIncomeStoreHas = [
        false, false, false, false, false, false, false, false, false, false, false, false
      ];
      var plIncomeStreamTotals = {};
      var plIncomeStreamHas = {};
      var plIncomeTotalTotals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
      var plIncomeTotalHas = [
        false, false, false, false, false, false, false, false, false, false, false, false
      ];

      function plIncomeReadStore() {
        var gw = window.__KPI_DATA_GATEWAY;
        if (!gw || typeof gw.getJson !== 'function') return null;
        try {
          return gw.getJson(PL_INCOME_STORE_KEY);
        } catch (_e) {
          return null;
        }
      }

      function plIncomeEmptyMonthAgg() {
        return {
          totals: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          has: [
            false, false, false, false, false, false, false, false, false, false, false, false
          ]
        };
      }

      function plIncomeSumIsoMap(map, year, excludePlaceholder) {
        var agg = plIncomeEmptyMonthAgg();
        if (!map || typeof map !== 'object') return agg;
        var yStr = String(year);
        Object.keys(map).forEach(function (iso) {
          if (!iso || iso.length < 7) return;
          if (iso.slice(0, 4) !== yStr) return;
          var mo = parseInt(iso.slice(5, 7), 10);
          if (!(mo >= 1 && mo <= 12)) return;
          var v = Number(map[iso]);
          if (!Number.isFinite(v)) return;
          if (excludePlaceholder && v === PL_INCOME_PLACEHOLDER) return;
          agg.totals[mo - 1] += v;
          agg.has[mo - 1] = true;
        });
        return agg;
      }

      function plIncomeLoadStore(year) {
        var store = plIncomeReadStore();
        var ds = store && store.timeline && store.timeline.dailySales;
        return plIncomeSumIsoMap(ds, year, true);
      }

      function plIncomeLoadStream(year, streamId) {
        var store = plIncomeReadStore();
        var rec = store && store.years && (store.years[year] || store.years[String(year)]);
        var di = rec && rec.dailyIncome && rec.dailyIncome[streamId];
        return plIncomeSumIsoMap(di, year, false);
      }

      function plIncomeSetCell(rid, mi, sum, has) {
        var cell =
          document.querySelector(
            '[data-field="amount"][data-row="' + rid + '"][data-month="' + mi + '"] .pl-amt-cell__text'
          ) ||
          document.querySelector(
            '.pl-month-cell[data-row="' + rid + '"][data-month="' + mi + '"] .pl-month-cell__text'
          );
        if (!cell) return;
        cell.textContent = has ? formatMoney(sum) : '\\u2014';
      }

      function plIncomeLoadTotals() {
        // timeline.dailySales = 総売上(store + A + B)。placeholder(1234) 除外。
        var res = plIncomeLoadStore(plYear);
        plIncomeTotalTotals = res.totals;
        plIncomeTotalHas = res.has;
      }

      function plIncomeFillStreams() {
        PL_INCOME_STREAM_ROWS.forEach(function (rid) {
          var res = plIncomeLoadStream(plYear, rid);
          plIncomeStreamTotals[rid] = res.totals;
          plIncomeStreamHas[rid] = res.has;
          for (var mi = 0; mi < 12; mi++) {
            plIncomeSetCell(rid, mi, res.totals[mi], res.has[mi]);
          }
        });
      }

      function plIncomeStreamsSum(mi) {
        var s = 0;
        PL_INCOME_STREAM_ROWS.forEach(function (rid) {
          var totals = plIncomeStreamTotals[rid];
          if (totals) s += Number(totals[mi]) || 0;
        });
        return s;
      }

      function plIncomeAnyStreamHas(mi) {
        var any = false;
        PL_INCOME_STREAM_ROWS.forEach(function (rid) {
          var has = plIncomeStreamHas[rid];
          if (has && has[mi]) any = true;
        });
        return any;
      }

      function plIncomeFillStore() {
        // 店舗売上 = 総売上 − (A + B)。総売上に内訳が含まれるため差し引く(0でクランプ)。
        for (var mi = 0; mi < 12; mi++) {
          var storeVal = (Number(plIncomeTotalTotals[mi]) || 0) - plIncomeStreamsSum(mi);
          if (storeVal < 0) storeVal = 0;
          plIncomeStoreTotals[mi] = storeVal;
          plIncomeStoreHas[mi] = !!plIncomeTotalHas[mi];
          plIncomeSetCell('store_sales', mi, storeVal, plIncomeTotalHas[mi]);
        }
      }

      function plIncomeFillTotal() {
        // 合計 = 総売上(dailySales) が正。dailySales 無・stream 有の縁のみ stream 和。
        for (var mi = 0; mi < 12; mi++) {
          var hasDs = !!plIncomeTotalHas[mi];
          var total = hasDs ? (Number(plIncomeTotalTotals[mi]) || 0) : plIncomeStreamsSum(mi);
          var anyData = hasDs || plIncomeAnyStreamHas(mi);
          plIncomeSetCell('sales_total', mi, total, anyData);
        }
      }

      function refreshIncomeBlock() {
        plIncomeLoadTotals();
        plIncomeFillStreams();
        plIncomeFillStore();
        plIncomeFillTotal();
      }

      window.__plRefreshIncomeBlock = refreshIncomeBlock;
"""

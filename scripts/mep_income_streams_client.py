"""MEP → dailyIncome: 追加収入ストリームを dailyIncome へ保存する独立フック.

二重注入されている MEP-STORE ブロック(buildMepPersistPayload 等)には一切触れず、
全保存経路が発火する `kpi:mepDataChanged`(source='monthly-edit-float') を1か所で拾い、
Phase 1 で追加した公開API `KpiYearStore.bulkPersistMepYear` を使って
`years.{Y}.dailyIncome[streamId]` にマージ保存する。

- sales_a / sales_b: 手入力（総売上とは別枠。店舗 = 総売上 − (A+B)）
- food_sales: 手入力（Store の内訳。総売上には加算しない）
- drink_sales: AUTO CALC = Store − Food（負は 0）。表示・保存とも派生値
- store_sales は timeline.dailySales 側で扱うため対象外
- 再帰(bulkPersist が再度 mepDataChanged を同期発火)は排他フラグで防止
- rowValueById は lineId をキーに日次値を保持しているためそのまま読める
"""

from __future__ import annotations

MEP_INCOME_STREAMS_BEGIN = "/* KPI-MEP-INCOME-STREAMS */"
MEP_INCOME_STREAMS_END = "/* KPI-MEP-INCOME-STREAMS-END */"


def mep_income_streams_client_js() -> str:
    return f"""      {MEP_INCOME_STREAMS_BEGIN}
      var MEP_INCOME_STREAM_IDS = ['sales_a', 'sales_b', 'food_sales', 'drink_sales'];
      var MEP_INCOME_INPUT_STREAM_IDS = ['sales_a', 'sales_b', 'food_sales'];
      var __mepIncomeStreamsBusy = false;
      function mepIncomeStreamIsoYear(iso) {{
        if (!iso || iso.length < 4) return NaN;
        var y = Number(iso.slice(0, 4));
        return Number.isFinite(y) ? y : NaN;
      }}
      function computeDrinkSalesValue(iso) {{
        /* Drink = Store − Food。Store は store_sales 行（総売上 − A − B） */
        var storeId = 'store_sales';
        if (typeof primarySalesRowId === 'function') {{
          storeId = primarySalesRowId() || 'store_sales';
        }}
        var store = 0;
        var food = 0;
        if (typeof readValue === 'function') {{
          store = Math.round(Number(readValue(storeId, iso)) || 0);
          food = Math.round(Number(readValue('food_sales', iso)) || 0);
        }}
        var drink = store - food;
        return drink < 0 ? 0 : drink;
      }}
      function drinkSalesAutoCalcHint() {{
        return typeof t === 'function'
          ? t('店舗売上 − フード売上（自動）', 'Store − Food (auto)')
          : 'Store − Food (auto)';
      }}
      function collectMepIncomeStreamsPayload(year) {{
        var y = Number(year);
        var out = {{}};
        if (typeof rowValueById === 'undefined' || !rowValueById) return out;
        MEP_INCOME_INPUT_STREAM_IDS.forEach(function (id) {{
          var byIso = rowValueById[id];
          if (!byIso || typeof byIso !== 'object') return;
          var filtered = {{}};
          Object.keys(byIso).forEach(function (iso) {{
            if (mepIncomeStreamIsoYear(iso) !== y) return;
            filtered[iso] = byIso[iso];
          }});
          out[id] = filtered;
        }});
        /* drink_sales = Store − Food（iso は store / food の和集合） */
        var drinkByIso = {{}};
        var isoSet = {{}};
        var storeId = typeof primarySalesRowId === 'function' ? primarySalesRowId() : 'store_sales';
        [storeId || 'store_sales', 'food_sales'].forEach(function (id) {{
          var byIso = rowValueById[id];
          if (!byIso || typeof byIso !== 'object') return;
          Object.keys(byIso).forEach(function (iso) {{
            if (mepIncomeStreamIsoYear(iso) === y) isoSet[iso] = true;
          }});
        }});
        Object.keys(isoSet).forEach(function (iso) {{
          drinkByIso[iso] = computeDrinkSalesValue(iso);
        }});
        out.drink_sales = drinkByIso;
        return out;
      }}
      function hydrateMepIncomeStreamsFromStore(year) {{
        var y = Number(year);
        if (!Number.isFinite(y)) return;
        if (!window.KpiYearStore || typeof KpiYearStore.loadMepYearPayload !== 'function') return;
        if (typeof rowValueById === 'undefined' || !rowValueById) return;
        var payload = KpiYearStore.loadMepYearPayload(y);
        var di = payload && payload.dailyIncome;
        if (!di || typeof di !== 'object') return;
        MEP_INCOME_INPUT_STREAM_IDS.forEach(function (id) {{
          var byIso = di[id];
          if (!byIso || typeof byIso !== 'object') return;
          if (!rowValueById[id]) rowValueById[id] = {{}};
          Object.keys(byIso).forEach(function (iso) {{
            if (mepIncomeStreamIsoYear(iso) !== y) return;
            var n = Number(byIso[iso]);
            if (!Number.isFinite(n) || n === 0) {{
              delete rowValueById[id][iso];
            }} else {{
              rowValueById[id][iso] = Math.round(n);
            }}
          }});
        }});
      }}
      document.addEventListener('kpi:mepDataChanged', function (ev) {{
        var d = ev && ev.detail;
        if (!d) return;
        var year = Number(d.year);
        if (!Number.isFinite(year)) return;
        if (d.source === 'monthly-edit-float') {{
          if (__mepIncomeStreamsBusy) return;
          if (!window.KpiYearStore || typeof KpiYearStore.bulkPersistMepYear !== 'function') return;
          var streams = collectMepIncomeStreamsPayload(year);
          __mepIncomeStreamsBusy = true;
          try {{
            KpiYearStore.bulkPersistMepYear(
              year,
              {{ dailyIncome: streams }},
              {{ source: 'monthly-edit-float' }}
            );
          }} finally {{
            __mepIncomeStreamsBusy = false;
          }}
          return;
        }}
        /* 外部更新時は dailyIncome → グリッドへ復帰 */
        hydrateMepIncomeStreamsFromStore(year);
      }});
      {MEP_INCOME_STREAMS_END}
"""

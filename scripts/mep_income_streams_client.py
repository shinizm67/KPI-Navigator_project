"""MEP → dailyIncome: 追加収入ストリーム(Sales A/B)を dailyIncome へ保存する独立フック.

二重注入されている MEP-STORE ブロック(buildMepPersistPayload 等)には一切触れず、
全保存経路が発火する `kpi:mepDataChanged`(source='monthly-edit-float') を1か所で拾い、
Phase 1 で追加した公開API `KpiYearStore.bulkPersistMepYear` を使って
`years.{Y}.dailyIncome[streamId]` にマージ保存する。

- 対象は追加ストリームのみ ['sales_a','sales_b']。store_sales は timeline.dailySales
  (=総売上) 側で扱うため対象外(PL 側で 店舗売上 = dailySales − (A+B) を算出)。
- 再帰(bulkPersist が再度 mepDataChanged を同期発火)は排他フラグで防止。
- rowValueById は lineId(sales_a/sales_b) をキーに日次値を保持しているためそのまま読める。
"""

from __future__ import annotations

MEP_INCOME_STREAMS_BEGIN = "/* KPI-MEP-INCOME-STREAMS */"
MEP_INCOME_STREAMS_END = "/* KPI-MEP-INCOME-STREAMS-END */"


def mep_income_streams_client_js() -> str:
    return f"""      {MEP_INCOME_STREAMS_BEGIN}
      var MEP_INCOME_STREAM_IDS = ['sales_a', 'sales_b'];
      var __mepIncomeStreamsBusy = false;
      function mepIncomeStreamIsoYear(iso) {{
        if (!iso || iso.length < 4) return NaN;
        var y = Number(iso.slice(0, 4));
        return Number.isFinite(y) ? y : NaN;
      }}
      function collectMepIncomeStreamsPayload(year) {{
        var y = Number(year);
        var out = {{}};
        if (typeof rowValueById === 'undefined' || !rowValueById) return out;
        MEP_INCOME_STREAM_IDS.forEach(function (id) {{
          var byIso = rowValueById[id];
          if (!byIso || typeof byIso !== 'object') return;
          var filtered = {{}};
          Object.keys(byIso).forEach(function (iso) {{
            if (mepIncomeStreamIsoYear(iso) !== y) return;
            filtered[iso] = byIso[iso];
          }});
          out[id] = filtered;
        }});
        return out;
      }}
      document.addEventListener('kpi:mepDataChanged', function (ev) {{
        var d = ev && ev.detail;
        if (!d || d.source !== 'monthly-edit-float') return;
        if (__mepIncomeStreamsBusy) return;
        var year = Number(d.year);
        if (!Number.isFinite(year)) return;
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
      }});
      {MEP_INCOME_STREAMS_END}
"""

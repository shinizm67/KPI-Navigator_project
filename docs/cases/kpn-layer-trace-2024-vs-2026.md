# 層別トレース（2024 vs 2026）— 修正なし・調査用

## 目的

2026 の 1/6/7/12 がどこで最初に 0 になるかを特定する。  
修正は原因確定後。

## DevTools 貼り付け用（ログイン済み・任意の KPI 画面）

Console にそのまま貼る。結果 JSON をコピーして共有。

```javascript
(async function () {
  function pad(n) { return n < 10 ? '0' + n : String(n); }
  function monthAgg(map, year, m1, getVal) {
    var dim = new Date(year, m1, 0).getDate();
    var positive = 0, sum = 0, explicitZero = 0, missing = 0;
    for (var d = 1; d <= dim; d++) {
      var iso = year + '-' + pad(m1) + '-' + pad(d);
      if (!map || !Object.prototype.hasOwnProperty.call(map, iso)) { missing++; continue; }
      var n = Number(getVal ? getVal(map[iso]) : map[iso]);
      if (!Number.isFinite(n)) n = 0;
      if (n > 0) { positive++; sum += n; } else explicitZero++;
    }
    return {
      positive: positive,
      explicitZero: explicitZero,
      missing: missing,
      sum: Math.round(sum),
      firstZeroLayerHint: positive === 0 ? (explicitZero > 0 ? 'explicit_zero' : 'missing') : 'has_sales'
    };
  }
  function yearBlock(getMaps) {
    var months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    var focus = [1, 6, 7, 12];
    var out = { all: {}, focus: {} };
    months.forEach(function (m) {
      var row = {};
      Object.keys(getMaps).forEach(function (layer) {
        var spec = getMaps[layer];
        row[layer] = monthAgg(spec.map, spec.year, m, spec.getVal);
      });
      out.all[m] = row;
      if (focus.indexOf(m) >= 0) out.focus[m] = row;
    });
    return out;
  }
  function rowsToMap(rows, salesKey) {
    var m = {};
    (rows || []).forEach(function (r) {
      var iso = r.iso || r.date;
      if (!iso) return;
      m[iso] = Number(r[salesKey] != null ? r[salesKey] : r.sales) || 0;
    });
    return m;
  }
  var root = (location.pathname.match(/^(.*?\/kpi-navigator)/) || [])[1] || '';
  var headers = { 'Content-Type': 'application/json' };
  try {
    var o = JSON.parse(localStorage.getItem('kpiNavigator.storeSync') || 'null');
    if (o && o.token) headers['X-KPI-Store-Token'] = String(o.token);
  } catch (e) {}
  async function api(path) {
    var r = await fetch(root + path, { credentials: 'include', headers: headers });
    var j = null; try { j = await r.json(); } catch (e) {}
    return { status: r.status, ok: !!(j && j.ok), body: j };
  }
  var store = window.KpiYearStore && KpiYearStore.getStore && KpiYearStore.getStore();
  var tl = (store && store.timeline && store.timeline.dailySales) || {};
  var meta = {
    href: location.href,
    operatingYear: KpiYearStore.getOperatingYear && KpiYearStore.getOperatingYear(),
    calendarYear: window.__ANNUAL_DATA && __ANNUAL_DATA.calendarYear,
    displaySelected: KpiYearStore.getSelectedDate && KpiYearStore.getSelectedDate(),
    salesPath: KpiYearStore.getDailySalesInputPath && KpiYearStore.getDailySalesInputPath(),
    year2024status: store && store.years && store.years[2024] && store.years[2024].status,
    year2026status: store && store.years && store.years[2026] && store.years[2026].status
  };
  var result = { meta: meta, years: {} };
  for (var yi = 0; yi < 2; yi++) {
    var year = yi === 0 ? 2024 : 2026;
    var from = year + '-01-01', to = year + '-12-31';
    var inputs = await api('/api/v1/daily-inputs.php?from=' + from + '&to=' + to);
    var facts = await api('/api/v1/daily-facts.php?from=' + from + '&to=' + to);
    var storeApi = await api('/api/v1/store.php');
    var inputsMap = inputs.ok ? rowsToMap(inputs.body.rows, 'sales') : {};
    var factsMap = facts.ok ? rowsToMap(facts.body.rows, 'sales') : {};
    var storeTl = {};
    if (storeApi.ok && storeApi.body.store && storeApi.body.store.timeline) {
      storeTl = storeApi.body.store.timeline.dailySales || {};
    }
    var factsMem = (store && store.years && store.years[year] && store.years[year].dailyFacts) || {};
    var getMaps = {
      dailyInputs: { map: inputsMap, year: year },
      dailyFactsApi: { map: factsMap, year: year },
      storeTimelineApi: { map: storeTl, year: year },
      memTimeline: { map: tl, year: year },
      memDailyFacts: { map: factsMem, year: year, getVal: function (f) { return f && f.sales; } }
    };
    result.years[year] = {
      api: {
        inputs: { status: inputs.status, ok: inputs.ok, rows: inputs.body && inputs.body.rows ? inputs.body.rows.length : 0 },
        facts: { status: facts.status, ok: facts.ok, rows: facts.body && facts.body.rows ? facts.body.rows.length : 0 },
        store: { status: storeApi.status, ok: storeApi.ok, error: storeApi.body && storeApi.body.error }
      },
      months: yearBlock(getMaps)
    };
  }
  console.log('[KPI layer trace 2024 vs 2026]', result);
  copy(JSON.stringify(result, null, 2));
  return 'copied JSON to clipboard — paste here';
})();
```

## 読み方

各月・各層の `firstZeroLayerHint`:

- `has_sales` … 正の売上あり
- `explicit_zero` … キーはあるが値が 0（潰しの痕跡）
- `missing` … キー自体なし

**最初に 0 になる層** = 上流は `has_sales`、その次の層から `explicit_zero` / 全滅、の境界。

## コード上の仮説（実測前）

- `operatingYear=2026` のとき、MEP sync のゼロ書きは **2026 にだけ効く**（2024 は `canEditIso` / year-lock で書き込み拒否されやすい）
- 経路の分岐というより **「運用年だけ潰せた」** 可能性が高い
- PL は `timeline > 0` 優先。timeline が 0／欠落なら `—`
- MEP hydrate も timeline/annual の **正の値だけ**埋める（0 は埋めない）

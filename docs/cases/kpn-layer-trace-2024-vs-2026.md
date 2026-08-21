# 層別トレース（2024 vs 2026）— 修正なし・調査用

## 判定ルール（合意）

| 観測 | 原因側 |
|------|--------|
| timeline で既に 0 | 保存／同期側 |
| timeline 正・daily-inputs 0 | Dual Write 側 |
| daily-inputs 正・daily-facts 0 | rebuild 側 |
| facts まで正・PL だけ 0 | 表示／集計側 |

## エージェントブラウザの結果（2026-08-21）

Cursor 内蔵ブラウザは `store.php` / `daily-inputs` / `daily-facts` が **全て 401**、メモリ timeline キー数 **0**。  
→ **本番データに届いていない**（ログイン済み Chrome での実行が必要）。

## DevTools 貼り付け用（ログイン済み KPI 画面）

CSV Network が 200 だったのと同じログイン済みタブで Console に貼る → JSON が clipboard に入る → チャットへ貼る。

```javascript
(async function () {
  function pad(n) { return n < 10 ? '0' + n : String(n); }
  function monthAgg(map, year, m1) {
    var dim = new Date(year, m1, 0).getDate();
    var positive = 0, sum = 0, explicitZero = 0, missing = 0;
    for (var d = 1; d <= dim; d++) {
      var iso = year + '-' + pad(m1) + '-' + pad(d);
      if (!map || !Object.prototype.hasOwnProperty.call(map, iso)) { missing++; continue; }
      var n = Number(map[iso]); if (!Number.isFinite(n)) n = 0;
      if (n > 0) { positive++; sum += n; } else explicitZero++;
    }
    return {
      positive: positive, explicitZero: explicitZero, missing: missing, sum: Math.round(sum),
      hint: positive === 0 ? (explicitZero > 0 ? 'explicit_zero' : 'missing') : 'has_sales'
    };
  }
  function rowsToMap(rows) {
    var m = {};
    (rows || []).forEach(function (r) {
      var iso = r.iso || r.date; if (!iso) return;
      m[iso] = Number(r.sales != null ? r.sales : r.store_sales) || 0;
    });
    return m;
  }
  function firstZero(tl, inp, fac) {
    if (tl.hint !== 'has_sales') return { at: 'timeline', cause: 'save_or_sync' };
    if (inp.hint !== 'has_sales') return { at: 'daily-inputs', cause: 'dual_write' };
    if (fac.hint !== 'has_sales') return { at: 'daily-facts', cause: 'rebuild' };
    return { at: null, cause: 'ok_check_PL_display' };
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
  var store = KpiYearStore.getStore();
  var memTl = (store.timeline && store.timeline.dailySales) || {};
  var storeApi = await api('/api/v1/store.php');
  if (!storeApi.ok) {
    return 'API unauthorized (' + storeApi.status + '). Use the logged-in Chrome tab where CSV Network showed 200.';
  }
  var serverTl = (storeApi.body.store.timeline && storeApi.body.store.timeline.dailySales) || {};
  var out = {
    meta: {
      oy: KpiYearStore.getOperatingYear && KpiYearStore.getOperatingYear(),
      cy: window.__ANNUAL_DATA && __ANNUAL_DATA.calendarYear,
      path: KpiYearStore.getDailySalesInputPath && KpiYearStore.getDailySalesInputPath(),
      y2024: store.years[2024] && store.years[2024].status,
      y2026: store.years[2026] && store.years[2026].status
    },
    years: {}
  };
  for (var yi = 0; yi < 2; yi++) {
    var year = yi === 0 ? 2024 : 2026;
    var inp = await api('/api/v1/daily-inputs.php?from=' + year + '-01-01&to=' + year + '-12-31');
    var fac = await api('/api/v1/daily-facts.php?from=' + year + '-01-01&to=' + year + '-12-31');
    var imap = inp.ok ? rowsToMap(inp.body.rows) : {};
    var fmap = fac.ok ? rowsToMap(fac.body.rows) : {};
    var months = {};
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].forEach(function (m) {
      var tl = monthAgg(serverTl, year, m);
      var i = monthAgg(imap, year, m);
      var f = monthAgg(fmap, year, m);
      var z = firstZero(tl, i, f);
      months[m] = {
        timeline: tl, inputs: i, facts: f,
        firstZeroAt: z.at, cause: z.cause,
        memTimelineSum: monthAgg(memTl, year, m).sum
      };
    });
    out.years[year] = {
      api: { inputs: inp.status, facts: fac.status, store: storeApi.status },
      months: months,
      focus: {}
    };
    [1, 6, 7, 12].forEach(function (m) { out.years[year].focus[m] = months[m]; });
  }
  console.log('[KPI layer trace]', out);
  copy(JSON.stringify(out, null, 2));
  return 'OK — JSON copied. Paste into chat.';
})();
```

## コード仮説（実測前・変更なし）

- `operatingYear=2026` だけ MEP sync の 0 書きが通る → **timeline で既に 0** になりやすい
- 2024 は year-lock / `canEditIso` で書き込み拒否され、売上残存と整合
- Dual Write / rebuild / PL 表示は、上記の下流結果の可能性が高い

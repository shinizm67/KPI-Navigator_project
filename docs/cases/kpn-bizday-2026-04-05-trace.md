# Business Day 層別トレース — 2026-04-05

## CSV 取込値（ローカル検証用ファイル）

`excel/検証用_2026売上_日次_フード.csv`:

```
日付,営業日,店舗売上,フード売上
...
2026-04-05,0,0,0
```

→ **CSV 取込時点の営業日 = 0（店休）**。ここは 1 にならない。

## DevTools（ログイン済み MEP）

```javascript
(async function () {
  var ISO = '2026-04-05';
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
  function openish(v) {
    if (v === true || v === 1 || v === '1') return 1;
    if (v === false || v === 0 || v === '0') return 0;
    return null;
  }
  var storeApi = await api('/api/v1/store.php');
  var sb = storeApi.ok && storeApi.body.store && storeApi.body.store.timeline
    ? storeApi.body.store.timeline.businessDays || {} : {};
  var ss = storeApi.ok && storeApi.body.store && storeApi.body.store.timeline
    ? storeApi.body.store.timeline.dailySales || {} : {};
  var inp = await api('/api/v1/daily-inputs.php?from=' + ISO + '&to=' + ISO);
  var ir = inp.ok && inp.body.rows ? inp.body.rows.find(function (r) { return (r.iso || r.date) === ISO; }) : null;
  var fac = await api('/api/v1/daily-facts.php?from=' + ISO + '&to=' + ISO);
  var fr = fac.ok && fac.body.rows ? fac.body.rows.find(function (r) { return r.iso === ISO; }) : null;
  var mem = KpiYearStore.getStore();
  var mb = mem && mem.timeline && mem.timeline.businessDays;
  /* MEP 表示: Business Day 行の checkbox（data-iso） */
  var mepCb = null;
  try {
    var el =
      document.querySelector('input[type="checkbox"][data-iso="' + ISO + '"]') ||
      document.querySelector('[data-iso="' + ISO + '"] input[type="checkbox"]');
    if (el) mepCb = el.checked ? 1 : 0;
  } catch (e) {}
  var layers = {
    csv_expected: 0,
    store_timeline: Object.prototype.hasOwnProperty.call(sb, ISO) ? openish(sb[ISO]) : null,
    store_timeline_sales: Object.prototype.hasOwnProperty.call(ss, ISO) ? Number(ss[ISO]) : null,
    daily_inputs: ir ? openish(ir.businessDay != null ? ir.businessDay : ir.business_day) : null,
    daily_facts: fr ? openish(fr.businessDay != null ? fr.businessDay : fr.business_day) : null,
    mem_timeline: mb && Object.prototype.hasOwnProperty.call(mb, ISO) ? openish(mb[ISO]) : null,
    mep_display: mepCb
  };
  var order = ['store_timeline', 'daily_inputs', 'daily_facts', 'mep_display'];
  var first1 = null;
  order.forEach(function (k) {
    if (layers[k] === 1 && !first1) first1 = k;
  });
  var out = {
    iso: ISO,
    layers: layers,
    first_becomes_1: first1 || 'none_still_0_or_missing'
  };
  console.log(out);
  try { copy(JSON.stringify(out, null, 2)); } catch (e) {}
  return out;
})();
```

実行後、コンソールの JSON（または `copy` した内容）をチャットに貼ってください。
`first_becomes_1` で原因層を確定します。

---

## 原因確定（Trace）

- CSV = 0 / `first_becomes_1` = **store_timeline**
- 経路: `applyDailyImportMaps`（false）→ **`buildGrid` → `syncBizDayFromAnnualStore`** が旧 store の true で上書き → `syncMonthlySales` が true を書き戻し

## 修正（案A / Step DC）

マーカー: `KPI-BIZDAY-CSV-ORDER-A`  
CSV `applyMaps` のみ: persist → その後 `buildGrid()`。

## 追加検証・修正（Step DD / 2026-12 再発）

元データ `excel/2026年売上入力用のコピー.xlsx`（列: 日にち, 曜日, 営業日, 売上）は日曜 `営業日=0` で正しい。  
パーサも false。残っていた穴:

1. `syncBizDayFromAnnualStore` が import の false を旧 store true で上書き  
2. `ensureDefaults` の `null → true`（キー無し日曜が営業扱い）  
3. `syncMonthlySales` の `hasBiz` 欠落時 `isBusiness = true`

マーカー: `KPI-BIZDAY-IMPORT-DD` — 再取込で timeline に 0 を書き直すこと。

# CSV / 複数年取込後の再描画嵐を抑える（段階1）

更新日: 2026-08-14  
関連: [`monthly-page-load-performance.md`](./monthly-page-load-performance.md) · [`annual-page-load-performance.md`](./annual-page-load-performance.md)

## 狙い

正本はブラウザの巨大 JSON のまま。DB 化前でも効く **重複イベント削減 + debounce**。

## 変更

| 箇所 | 内容 |
|------|------|
| `KpiYearStore.mergeDailyMaps` / `mergePastSalesMaps` | 年ごと `dailySalesChanged` → **1回（bulk）** |
| `scheduleRenderAnnualDailyTimeline` | 32ms → **120ms** |
| `onArea1CockpitRefresh` | 0ms → **100ms** |
| `monthlyTwRebuildKeepFocus` | **120ms** debounce（点滅抑制） |

適用: `python3 scripts/apply_bulk_store_refresh_perf.py`  
ソース: `scripts/kpi_year_store_client.py` · `scripts/focus_tw_metrics_client.py`

## ローカル確認

1. Annual / Monthly に 2〜3 年分 CSV（または Past Sales Save）  
2. 取込直後の TW 点滅が減るか  
3. Cockpit 日付移動と TW フォーカスがずれないか  

段階2以降（解の DB 保存・窓読み・仮想化）は [`snapshot-store-phased-plan.md`](./snapshot-store-phased-plan.md)。debounce は応急として残してよい。

## 実装済み（2026-07-20）／ライブ追従（2026-07-21）

PL 表最下段の月次バーグラフ（`#pl-graph-data-body`）と Total Expenses サマリーを実データ化し、明細編集に追従。

### 方針

| 項目 | 内容 |
|---|---|
| 書込 | サマリー／グラフクライアント自体は**読取のみ**。月次セル blur 時の persist は PL 本体 |
| 描画 | 既存 `window.plGraphRender(months)` のみ呼び出し |
| Fixed / Expected 正本（画面追従） | `#pl-expense-detail-data-body` を `data-bucket` で合算 |
| Insight フォールバック | `window.__plInsight.monthMetrics`（persist + `resetCache` 後と一致） |
| 初期表示 | ¥0/$0（ダミー `$123,456` なし）→ ブート完了後に実データで上書き |

### ライブ追従

| 操作 | 挙動 |
|---|---|
| 明細セル `input` | 約 120ms debounce で Fixed/Expected/Total + 下グラフを再計算（DOM 合算） |
| 明細セル `blur` | 月次マップへ merge 保存 → `__plInsight.resetCache()` → 再描画 |
| Save | 同上 + MEP 配賦（既存）+ サマリー／グラフ refresh |

### ファイル

- `scripts/pl_bottom_graph_data_client.py`
- `scripts/build_pl_table_page.py`（`persistExpenseMapFromDom` / live refresh）

### 系列マッピング

| グラフ | ソース |
|---|---|
| Income（緑） | `sales_total`（なければ Insight `income`） |
| Total expenses（赤） | Fixed + Expected |
| Fixed（黄） | 明細 `bucket=fixed` 合計 |
| Expected / Variable（橙） | 明細 `bucket=variable` 合計 |
| 棒の高さスケール | **その年 12 ヶ月の最大値**（売上・支出・固定・変動のピーク）を 100%。月同士の差が比較できる。年計列のみ自己スケール |

### 確認

1. 変動費（緑）月次セルに大きな金額を入力 → Expected / Total Expenses が即追従
2. 固定費セル入力 → Fixed / Total が追従
3. 最下段グラフの支出バーが同じ月で動く
4. リロード後も値が残る（blur で localStorage 保存済み）

# Food / Drink Sales — 設計メモ

## Phase 0 確定（2026-07-20）

| 項目 | 決定 |
|---|---|
| 関係式 | `Food Sales + Drink Sales = Store Sales` |
| MEP 入力 | Store 固定（既存）／**Food 手入力（緑）**／**Drink = Store − Food（AUTO CALC）** |
| Drink の見た目 | 緑行ではない（Target / Difference と同系の AUTO CALC） |
| % 分母 | 売上合計（`sales_total`、既存 ratio と同じ） |
| CSV 取込（Phase 4） | Store 必須。Food / Drink は **どちらか一方あれば可**、両方あれば整合チェック |

### 採用方針（UI）

- **MEP 画面は Food 固定・Drink AUTO のまま**（2026-07-20 再確認）。
- Drink しか分からない店向けの痒みは、当面 **CSV 取込の柔軟モード**（Drink 列だけ入れて Food を逆算）でカバーする想定。
- 画面側の「手入力側切替」は **フィードバックが来たらすぐ足せる**が、今は入れない（多機能化を避ける）。

### 後続候補（未実装・フィードバック待ち）— 手入力側の切替

**動機:** ドリンク主軸の店は「Drink は分かるが Food は Store − Drink の手計算が面倒」になりうる。Food を蔑ろにするほどではないが、Drink が主のケースはありうる。

**推奨案（やるならこれだけ）:**

| 項目 | 内容 |
|---|---|
| UX | Sales 近くに小さなトグル／設定 1 つ。`手入力 = Food`（既定）／`手入力 = Drink` |
| 挙動 | 緑行は常に **1 本だけ**。もう一方は AUTO CALC（`Store − 手入力側`） |
| 保存 | `localStorage` 例: `kpiNavigator.fdInputMode = 'food' \| 'drink'` |
| 難易度 | 小〜中（Phase 2 の AUTO CALC 配線を対称化するだけ） |
| やらない | 日ごとセル切替・両方いつも緑入力 → UI がうるさい／ズレ処理が増える |

**やらない理由（現状）:** CSV で片方入力を既に想定しているので、画面を増やす必然がまだ弱い。オナニー機能化を避ける。

### MEP Sales 並び

```
Store Sales     … 既存
Sales A         … 既存
Sales B         … 既存
Food Sales      … 新規（緑・手入力）
Drink Sales     … 新規（AUTO CALC＝Store − Food）
```

### PL 表示先

- **Analyze** ブロック（`analyze_food_sales` / `analyze_drink_sales`）に月次金額＋% を配線（Phase 3）
- PL 収入ブロック（店舗/A/B/合計）には **出さない**（`PL_INCOME_TABLE_EXCLUDE`）

---

## Phase 1 実装済み（2026-07-20）

- `scripts/pl_line_catalog.py`
  - `INCOME_ROWS_V1` に `food_sales` / `drink_sales` 追加
  - `PL_INCOME_TABLE_EXCLUDE` / `MEP_INCOME_AUTO_CALC_IDS`
  - `mep_catalog_entries()`: Food=`mepEditable:true`, Drink=`mepEditable:false` + `mepAutoCalc:true`
  - `CATALOG_SCHEMA_VERSION` → 8
- `scripts/build_pl_table_page.py`
  - Analyze EN: **Drink Purchase Amount → Drink Sales**
  - PL 収入表から Food/Drink を除外
- `scripts/apply_mep_pl_catalog.py`
  - カタログ同期で `mepEditable` / `mepAutoCalc` を尊重

## Phase 2 実装済み（2026-07-20）

- `scripts/mep_income_streams_client.py`
  - `food_sales` を手入力ストリームとして `dailyIncome` へ保存
  - `drink_sales` を Confirm 時に `Store − Food`（負は 0）で計算して保存
  - `hydrateMepIncomeStreamsFromStore` で年切替・外部更新時に Food を復帰
- `scripts/apply_mep_pl_catalog.py`
  - Drink 行は緑ではなく **AUTO CALC** 表示（`mepAutoCalc`）
  - Food 入力後に `buildGrid` で Drink が即再計算
  - **Total Sales 合算から Food/Drink を除外**（Store+A+B のみ）。Food を総売上に足していたことが「Drink に足される」見え方・Store 上書き汚染の原因だった（2026-07-20 修正）
- MEP 再適用: `apply_mep_pl_catalog.py` + `apply_mep_income_streams.py`

### 確認手順（MEP）

1. ページ再読み込み → Sales B 下に Food Sales（緑）／Drink Sales（AUTO CALC）
2. Store がある日に Food を入力 → Drink が `Store − Food` になる
3. **Total Sales は Store（+A+B）のまま**（Food を入れても増えない）
4. Confirm → `dailyIncome.food_sales` / `drink_sales` に保存

### 既に汚染された日がある場合

修正前に Confirm 済みだと `timeline.dailySales` / Store 行に Food が混ざっていることがある。その日は **Store を正しい売上に戻してから再 Confirm**（または売上CSV再取込）が必要。

## Phase 3 実装済み（2026-07-20）

- `scripts/pl_analyze_client.py`（新規）
  - `analyze_food_sales` / `analyze_drink_sales` ← `dailyIncome.food_sales` / `drink_sales` の月合計
  - Drink 欠落時は **Store − Food（月次）** で補完
  - `analyze_food_cost` / `analyze_drink_cost` ← 支出明細 `exp_food_cost` / `exp_drink_cost` の金額コピー
  - % は既存 `refreshPlRatios`（÷ 売上合計）
- `scripts/build_pl_table_page.py` に注入＋ expense/income/MEP 更新時の refresh チェーンへ接続

### 確認手順（PL）

1. MEP で Food を入れて Confirm 済みの月を開く
2. Analyze「食材原価率」ブロック:
   - Food Sales / Drink Sales に金額
   - 右側 %（売上合計比）
   - 仕入額行は支出明細と一致

## Phase 4 実装済み（2026-07-20）

- `scripts/daily_sales_import_client.py`
  - ヘッダ検出: `フード売上` / `Food Sales` / `ドリンク売上` / `Drink Sales` など（汎用「売上」より先に判定）
  - 取込ルール:
    - **Store（店舗売上）必須**
    - **Food のみ** → Drink = Store − Food
    - **Drink のみ** → Food = Store − Drink（MEP 緑行に Food を書き込み → Drink AUTO が一致）
    - **両方** → 双方採用。`|Store − (Food+Drink)| > 1` は確認ダイアログで警告
  - 確認ダイアログに Food/Drink 日数・不一致件数を表示
- `applyDailyImportMapsToOpenYear`（MEP JA/EN）
  - `foodByDate` がある日は `food_sales` 行へ書き込み（Drink は既存 AUTO CALC）
- `scripts/apply_daily_sales_import.py` で再注入＋耐久パッチ
- 雛形 CSV:
  - `excel/売上入力_日次_雛形_フード.csv`
  - `excel/売上入力_日次_雛形_ドリンク.csv`
  - `excel/売上入力_日次_雛形_フードドリンク.csv`

### 確認手順（CSV → MEP）

1. MEP で Upload CSV → 上記雛形のいずれかを選択
2. 確認ダイアログに Food/Drink 日数が出る
3. Food 行に値が入り、Drink = Store − Food
4. Confirm → PL Analyze の Food/Drink Sales に反映

## 後続

| Phase | 内容 |
|---|---|
| 5 | 検証・docs・Commit |

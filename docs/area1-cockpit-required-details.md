# Area1 Cockpit 必須詳細情報

更新日: 2026-05-09

## 対象

- `app/annual/index.html`
- `app/monthly/index.html`
- `en/app/annual/index.html`
- `en/app/monthly/index.html`

Area1 Cockpit は Annual / Monthly 共通で、売上の「当日・月次・年次」を 1 画面で把握し、Focus Bar へ接続する最上位の要約領域。

## 実装必須要素（トグル以外）

- 配分クラスタ（`annual-kpi-allocation-cluster`）
  - 繁閑期比率（H/L Sea%）の月別表示と平均（Total）表示
  - `initAllocationWidget` による達成率グラフ
- Group5 KPI 行（Daily / Monthly / Annual）
  - Daily: `annual-group5-sales-value`（`daily.sales` 連携）
  - Monthly 累積: 売上 / 目標 / 差額 / 達成率グラフ
  - Annual 累積: 売上 / 目標 / 差額 / 達成率グラフ
- `▼ Focus Bar` ジャンプボタン
  - クリック時に Table Window 内 `annual-daily-focus-global-menu` へスクロール
  - sticky な `.site-header` がある場合はヘッダー高さ分を差し引く

## 実装しない要素（今回スコープ外）

- Annual Table Window の Open / Close トグル
  - Monthly には実装しない

## Office mode 要件

- `.office-mode` 時の枠線、文字色、グラフ色を Annual 側仕様と一致させる
- Focus Bar 画像切り替え
  - close: `focus_bar_office_mode.svg`
  - open: `focus_bar_office_mode_open.svg`

## データ同期要件

- Area1 の売上表示は `window.__ANNUAL_DATA` を参照
- `annual-current-sales-value` と `annual-difference-value` を更新
- `annual-group5-sales-value` は `data.daily.sales` を優先し、未設定時は `currentSales` へフォールバック

## 受け入れ確認チェック

- Annual / Monthly の両方で、Area1 の Group5 と配分クラスタが表示される
- Office mode ON/OFF で色・枠線・Focus Bar 画像が破綻しない
- `▼ Focus Bar` クリックで、Table Window の Global Menu が画面上端（sticky header 直下）に来る
- Monthly 側に Open/Close トグルが存在しない

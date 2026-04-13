# Monthly Vertical Focus Bar メモ

更新日: 2026-04-10

## 実装済み（現状）

- **列幅**: Focus Bar 内スタックの幅は **`110px`**（`--monthly-vfocus-col-w`）。
- **行高（縦セル）**: 横方向の **1px 線と線のあいだ**を **45px** とし、`border-box` でその内側に下線 1px を含む行トラックは **`46px`**（`--monthly-vfocus-cell-inner-h` / `--monthly-vfocus-cell-row-h`）。Income は 9 行＝`repeat(8, 46px) 45px`（最終行はグリッド下辺の 1px が外枠）、Expenses は 6 行＝`repeat(5, 46px) 45px`。**Date はセル枠なし**（15px 太字のテキストのみ）。Profit は上下に 1px 枠で内側 **45px**（合計 **47px**）。
- **タイポグラフィ**: Date は **15px・太字**（枠・背景なし）。Income / Expenses / Profit のセル内文字は **15px・通常字重**（Annual の `.annual-daily-focus-bar-lower__cell` の 15px に揃える意図）。
- **レイアウト**: `vertical_focus_bar.svg` の内側ダーク矩形（おおよそ上端 39px・下端 17px の余白）に合わせた `.monthly-vfocus-fill` の中で、スタック全体を **縦方向センター**（`align-items: center`）に置く。Income–Expenses 間・Profit 前のスペーサーは TW と同じ **39px / 27px**。
- **表示内容**: 横スクロール領域の **ビューポート中央**に来る列インデックスを `scrollLeft` と `clientWidth` から算出し、その列の日付ヘッダー・Income / Expenses の各セル・Profit セルのテキストを反映。セルが空のときはデモ用に `¥123,456` / `$123,456` を表示（本番データ接続時は差し替え可）。
- **Office モード**: 枠・文字色をグレー系に合わせたオーバーライドあり。

## 将来検討（未実装・仕様メモ）

### 行の追加（目標売上・達成率など）

- TW に行が増えた場合は **Vertical Focus Bar 内のスタックを再設計**し、行数に応じて **45px（線間）＋ 1px 罫線**のルールを維持しつつグリッドを組み直す想定。
- 今回の実装では **対象外**（高さ・グリッド行数は現行 TW にのみ一致）。

### Focus Bar 内の縦スクロールと幅

- 行数増加で **Focus Bar 内を縦スクロール**させる案あり。その場合、**スクロールバーが右端**に乗るため、**表示幅を広げる**か **右パディングでバーと数字の重なりを防ぐ**必要がある。
- **左位置（`left: 504px` など）は据え置き**で、幅だけ調整する方針が候補。

### 横スクロールとスナップ

- Annual の Focus Bar 展開時と同様、**日次列の横スクロールは列単位でスナップ**して止まる挙動にしたい、という要望をメモ。
- Monthly の `#monthly-scroll-data` には現状 `scroll-snap` は未適用。実装時は `scroll-snap-type` / `scroll-snap-align` または JS での整列を Annual 側と UX を揃えて検討する。

## 関連ファイル

- `app/monthly/index.html` / `en/app/monthly/index.html`（スタイル・マークアップ・月次ピッカー IIFE 内の `updateVerticalFocus`）
- `images/vertical_focus_bar.svg` / `images/vertical_focus_bar_office.svg`

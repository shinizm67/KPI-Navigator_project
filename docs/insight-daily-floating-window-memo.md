# Insight / Daily Floating Window メモ

## 日本語ページ（jp）と表示モード

- **日本語の月次・年次ページ**（`app/monthly/index.html`, `app/annual/index.html`）の Insight は、現状 **背景が黒系・フォントが Orbitron** のため、**Sci-Fi（通常）モードの見た目に寄っている**理解でよい。
- **Daily** は日本語版に **専用の日本語 UI**（例: `daily-overlay` の「本日」など）が用意されている。Insight 内の **Sales Status / Reference などのラベル文言**は、日本語ページでは **日本語表記に揃える**のが望ましい（未対応なら要実装）。
- **Office モード**はページ全体で切り替わるが、Insight / Daily フローティングの **Office 用の色・コントラストを十分に当てる作業は別途**（下記）。

## Daily と Insight の Office モード（色味・仕様メモ）

実装は後続タスク。方針のみ記録。

### 共通

- **背景**: 白に近い **薄いグレー**
- **枠線**: **濃いグレー**、太さは **Sci-Fi 時と同じ**（既存の枠の太さに合わせる）
- **文字**: **黒**で統一

### ボックス

- **既存の Office モード仕様**を流用（背景色・枠線の色など。Cockpit の Office 系と整合）

### グラフ（Insight Daily の配分バー等）

- **Office モードの Cockpit** で使っている **Monthly Allocation Graph**（年次エリアの配分グラフ）と **同じ色味**を採用する

## Insight Daily: ラベル＋ボックス行の縦方向スペース（以降の描画ルール）

Insight の Daily エリアで **ラベル列＋値ボックス列**を積み上げるときの **行間（＝前行のボックス下端〜次行のボックス上端のあいだ）** を次で統一する。

### 標準行間（既定）

- **15px**  
- Reference ブロックや、Target Sales / Difference / Profit Margin のように **主役ではない行同士**のあいだはこの値を使う。  
- **今後**同様の「ラベル＋ボックス」ブロックを追加する場合も、特段の指定がなければ **15px** を既定とする。  
- 2行ラベルが続くと視覚的にはまだやや詰まり感は残り得るが、**1行ラベル**とのバランスではこの値でよい、という判断。

### メイン行の直後（主張したいブロックの下）

- **31px**（Sales 行の高さ 60px のボックスの直下 → Target Sales 行のあいだで採用している値）  
- **セクションの顔となる1行目**（大きいボックス・強調したい指標）の **すぐ下**だけ、この広めのギャップを使う。  
- それ以外の行間は上記 **15px**。

### 実装メモ（CSS）

- `.insight-daily-kpi__row + .insight-daily-kpi__row { margin-top: 15px; }` と、`.insight-daily-kpi__row:first-child + .insight-daily-kpi__row { margin-top: 31px; }` で上記を表現。  
- `.insight-daily-reference__row + .insight-daily-reference__row { margin-top: 15px; }`（Reference は主行の区切りが無い限り 15px のみ）。

## Insight: Daily / Monthly / Annual のバンド高（CSS 変数）

`.insight-overlay__content` に次を定義し、**横線の位置・各 `section` の `min-height`・スクロール領域の `min-height`・縦線の高さ**を一括で整合させる。**いじれる**（変更は主にこの3変数と派生の `--insight-content-scroll-min` のみ）。

| 変数 | 意味 | 既定値（例） |
|------|------|----------------|
| `--insight-band-daily` | Daily バンドの高さ ＝ **Daily 下端の 0.5px 横線**（`.insight-overlay__hline--monthly` の `top`） | `1380px`（旧 1217px から延長。Expenses / Profit 縦ラベル用の余白確保） |
| `--insight-band-monthly` | Monthly バンドの高さ（月次横線〜年次横線の間） | `1617px` |
| `--insight-band-annual` | Annual バンドの高さ | `2670px` |
| `--insight-content-scroll-min` | 上3つの合算（`min-height` 用） | `calc(...)` |

- `.insight-overlay__hline--annual` の `top` は `calc(var(--insight-band-daily) + var(--insight-band-monthly))`。  
- `.insight-overlay__vline` の `height` は `calc(var(--insight-content-scroll-min) + 4px)`（従来の +4px 踏襲）。  
- Daily 内の **Expenses / Profit** など `top` 固定の縦ラベルは、**Daily バンドを延ばしたあと**に重ならないよう個別に調整する（例: `translateY(-50%)` と `top` の組み合わせ）。

## Insight Monthly: Sales Status（先頭ブロック）

- **レイアウト・行間・グリッド・グラフ**は **Insight Daily の Sales Status 部と同一**（`200px | 113px | 500px`、1 行目下 **31px**、以降 **15px**、グラフ上余白 **43px**、配分バー **654×25** 等）。
- **ラベル文言のみ差し替え**（例・英語 UI）: **Cumulative Sales**（大箱 60px 高）→ **Expenses** → **Profit** → **Profit Margin**；グラフは **Today (Sales)** / **Today's Target Sales**。
- 日本語 UI では例: **累計売上** → **経費** → **利益** → **利益率**；グラフは Daily 冒頭に合わせ **本日の売上** / **本日の目標売上**。
- 縦書きサブラベル **Sales Status** は `.insight-overlay__sub-label--monthly-sales-status`（Daily の `--sales-status` と同じ `top: 269px` 幾何＝セクション先頭基準）。
- 配分グラフ DOM の **`id` は `insight-monthly-alloc-graph`**（`initAllocationWidget` を別インスタンスでバインド）。グラフ用ラッパーに **`.insight-kpi-graph-wrap`** を付与し、`closest` はこの共通クラスで CSS 変数のルートを解決する。

### Cost Structure（Sales Status の直下）

- **ブロック**: `.insight-monthly-cost`（Sales のグラフ直下に **48px** 空け＝ Daily の Reference 前空けと同じ）。
- **行**: ラベル列＋値エリアは **200px | 113px | 500px**、行間 **15px**（Reference と同様）。
- **ラベル**: 画像どおり右寄せ（`justify-self: end`）。
- **全幅ボックス**: **500×40**（枠・文字は Sales Status と同系）。
- **分割行**（Food / Drink / Misc）: 数値 **335×40** ＋ **3px** gap ＋ パーセント **162×40**（合計 **500px**）。
- 縦書きサブラベル: `.insight-overlay__sub-label--monthly-cost-structure`（**Cost Structure**／日本語ページは **コスト構造**）。`top` は `calc` で当該 9 行ブロックの Y 中央。

## 関連ファイル（参考）

- Insight: `app/monthly/index.html`, `app/annual/index.html` および `en/` 対応
- Daily overlay: 同上
- Cockpit Office の配分グラフ: `.office-mode .annual-allocation-graph` 等（`app/monthly/index.html` 内）

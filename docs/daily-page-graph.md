# Daily page graph

更新日: 2026-04-26（Annual KPI・KPI 行の縦中央揃え追記）

Global Menu の **Daily** から開く UI は、独立した Daily URL ではなく **読み取り専用のフローティングオーバーレイ**（以下「Daily Floating Window」）として実装している。  
この文書では、そのうち **グラフ見出し＋横棒グラフ（達成率）** のレイアウトを **Daily / Monthly セクションで同一ルール**として定義する。実装の単一の参照先とする。

## 実装の置き場所

次の **4 ファイル**に、同一のマークアップ・CSS・日付制御 JS を載せている（JP / EN × Annual / Monthly）。

| ファイル |
|----------|
| `app/annual/index.html` |
| `app/monthly/index.html` |
| `en/app/annual/index.html` |
| `en/app/monthly/index.html` |

ルート要素: `#daily-overlay`（バックドロップ・パネル・閉じるボタンを含む）。

---

## Daily page graph（統一仕様）

「Daily page graph」とは、Daily Floating Window 内の **日次ブロック**および**月次ブロック**それぞれに置く、**2 行のグラフ見出し＋横棒トラック＋達成率表示**の組みを指す。**両セクションで同じ幾何ルール**を使う。

### 水平方向

- パネル幅 **1100px** を基準とする。
- **値ボックス列**は `left: 500px`、`width: 480px` のため、**値ボックスの右端は 980px**（パネル左端からの距離）。
- **トラック（緑の横棒）の右端**は **常に 980px**（値ボックス右端と一致）。トラック幅はこの制約から導出する。
- **達成率テキスト**（例: `120%`）は、トラックの**右端から 24px**あとに配置する。ボックス列の右端より**右にはみ出してよい**（Figma 上のパーセントがボックスより外側に出る表現と同じ）。
- **グラフ見出しブロック**
  - **左端**は外枠（パネル）左端から **183px**（グラフ行コンテナの `padding-left: 183px`）。
  - **見出し列幅**は Daily / Monthly **共通で 250px**（月次の長い 2 行英語を幅の基準とする）。`text-align: center`。改行は `white-space: pre-line`。
  - 日次の短い見出しも**同じ 250px 列**に載せることで、**両セクションの見出しブロックの水平方向の中心**が **同一の縦線**（`183 + 125 = 308px`）上に揃う。
- **トラック左端〜見出し右端の間**は **24px**（`margin-right` / 相当）。
- **トラック幅（導出）**  
  `980 − 183 − 250 − 24 = 523px`（固定。右端維持のための計算値）。

### 垂直方向

- **トラック上端**は、**最下段の値ボックス下端から 42px**下（Daily・Monthly とも同じルール）。
- グラフ行全体は `display: flex; flex-direction: row; align-items: center` とし、**見出しブロックとトラックの縦方向センター**を一致させる。
- トラックの高さは **14px**（現状）。行コンテナの `top` は、上記 42px 制約とトラック高を踏まえたオフセットで置く（例: 日次ブロック約 `314.5px`、月次ブロック約 `718.5px` ※実装値に従う）。

### 月次のみの補助ルール（Figma）

- **月次 KPI 見出し**（左列 6 行）の**最下段テキスト下端**から**グラフ見出し上端**まで **46px** といった縦の関係は、Figma 上の指定として実装時に参照する。トラック〜ボックス 42px と組み合わせて微調整する場合がある。

---

## Daily Floating Window — パネル・罫線・セクション

グラフ以外の**オーバーレイ全体**のメモ。

### パネル

- **幅 1100px × 高さ 1350px**（固定）。`padding: 0`（子の絶対座標は外枠基準で統一）。
- パネルは `overflow: hidden`。ビューポートに収まらない場合は**外側**のオーバーレイでスクロール。

### ヘッダー（日付）

- 前日 ◀ / 日付ボタン（クリックでネイティブ `input[type=date]`）/ 翌日 ▶ / **本日**（既に今日なら非表示）。
- 初回表示は **Today** 寄り。Annual / Monthly のフォーカス日付と同期する処理は各ページの JS（`resolveIso` 等）に従う。

### 装飾線

- **縦線（0.5px）**: 左 **134px**、上 **104px** から、下はパネル下端から **34px** の位置まで（`bottom: 34px` で可変高に追従）。
- **横線（0.5px）×2**: 上端から **383px** / **792px**、左 **79px**、幅 **955px**。

### 左ラベル（縦書き）

- **Daily / Monthly / Annual** を各区間の中央付近に配置。`writing-mode: vertical-rl` と回転で「左が下・上へ向かって読む」向きに揃えている。

---

## KPI 行レイアウト（Daily / Monthly / Annual 共通）

- 各 KPI は **1 行 = タイトル列（250px・センター）＋ 62px 相当のすきま + 値ボックス（480×40）** の **flex 行**（`align-items: center`）。**タイトル文字の縦センターとボックスの縦センター**を一致させる。
- ブロック全体は `left: 188px` 起点。ボックス左端は `500px`（Daily / Monthly / Annual 揃い）。

## Daily セクション（KPI ブロック）

- **4 行**。タイトル（16px）例: Sales / Target Sales / Variance / Achievement Rate（JP は日本語ラベル）。
- ブロック先頭行の上端は概ね **`top: 106px`**。
- その下に **Daily page graph**（プレースホルダー）。

## Monthly セクション（KPI ブロック）

- **6 行**。タイトル例: 月次累積売上 / 月次累積目標売上 / 差額 / 達成率 / 目標達成までの 1 日の売上 / 月次残営業日数（EN は Cumulative Sales, Cumulative Monthly Target Sales, Variance, Achievement Rate, Daily Sales Needed to Hit Target, Remaining Business Days）。
- ブロック先頭行の上端は概ね **`top: 422px`**。
- その下に **Daily page graph**（グラフ見出し 2 行: EN は `Cumulative Monthly Sales` / `Cumulative Monthly Target Sales`）。

## Annual セクション（KPI ブロック）

- ブロック起点 **`top: 848px`**（外枠上端から）。**Group 1**（4 行）と **Group 2**（4 行）の **値ボックス列同士の間**に **20px** の縦すきま。行内の行間（ボックス同士）は他セクションと同様 **4px**（= 行の `gap: 4px`、グループ間のみ `gap: 20px`）。
- **Group 1** ラベル例（JP）: 年次累積売上 / 年次累積目標売上 / 差額 / 達成率。（EN）: Cumulative Sales / Cumulative Annual Target Sales / Variance / Achievement Rate。
- **Group 2** ラベル例（JP）: 年次目標売上 / 目標達成までの残額 / 残総営業日 / 目標達成までの 1 日の売上。（EN）: Annual Target Sales / Remaining Amount to Target / Remaining Business Days / Required Daily Sales。
- **グラフ**は **Daily page graph** と同一水平ルール。グラフ見出し 2 行例: EN は `Cumulative Annual Sales` / `Cumulative Target Annual Sales`、JP は `年次累積売上` / `年次累積目標売上`。
- トラック上端は **最下段ボックス下端 + 42px**（他セクションと同じ導出）。実装ではグラフ行 `top` 約 **1248.5px**。

---

## データ・今後

### Phase 10 — KPI 配線（2026-07-08）

`#daily-overlay` の数値・達成率バーは **`window.__computeTwMetricsForIso(iso)`**（Focus TW と同算出）から描画する。

| API / フック | 役割 |
|--------------|------|
| `window.renderDailyOverlayKpis(iso)` | Daily / Monthly / Annual 各 KPI ボックス + 横棒グラフ更新 |
| `fill(iso)` | 日付表示後に `renderDailyOverlayKpis` を呼ぶ |
| Store イベント | `kpi:dailySalesChanged` / `kpi:businessDayChanged` / `kpi:annualPlanChanged` / `annual:salesMapChanged` / Save 系 / `kpi:readSurfacesRefresh` / `kpi:dailyTargetModeChanged` / `kpi:weekdayBaselineChanged` で、開いているときだけ再描画 |

**再適用:** `python3 scripts/apply_daily_overlay_kpi.py`（idempotent）

**OFF 日:** Daily 行は売上・目標・差額・達成率が `—`。Monthly / Annual 累計は当日までの MTD/YTD を表示（Focus Bar Graph と同方針）。

**未着手（別サブフェーズ）:** メモ日付マーカーの Focus Bar / Daily 窓反映（`docs/phase-10-memo-flags-memo.md` の **10-c**）。

- 通貨・桁区切りはアプリ全体のルール（`docs/currency-and-markets-memo.md` 等）に合わせる。

---

## 関連ドキュメント

- Global Menu 全般: `docs/global-menu.md`
- Target Sales の日/月/年の概念: `docs/target-sales-daily-monthly-annual.md`
- Phase 10 メモ印（TW 点）: `docs/phase-10-memo-flags-memo.md`

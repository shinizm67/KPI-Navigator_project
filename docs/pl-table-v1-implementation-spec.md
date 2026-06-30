# PL 表 v1 — 実装仕様（現行）

更新日: 2026-06-10  
ステータス: **実装中**（段階的ゼロから再描画）

関連:

- 生成スクリプト: `scripts/build_pl_table_page.py`（`python3 scripts/build_pl_table_page.py` で JA/EN 再生成）
- 本番ページ: `app/profit/pl/index.html` / `en/app/profit/pl/index.html`
- 行ラベル・科目カタログ設計: [pl-table-label-layout-memo.md](./pl-table-label-layout-memo.md)
- 入力元設計（提案）: [pl-expense-input-source-design.md](./pl-expense-input-source-design.md)
- **PL Insight フローティング**（描画シェル・最終調整）: [pl-insight-final-adjustments-memo.md](./pl-insight-final-adjustments-memo.md)
- デザイン参照: `excel/PL表例4.pdf`、Figma

---

## 概要

Monthly Edit → **View Profit & Loss** から開く本番 PL ページを Figma に沿って再構築している。  
旧 1 枚テーブル + `position: sticky` は横スクロールで枠線が消える問題があったため、**ラベル用テーブル + データ用テーブルの 2 分割** に変更。

### デザイン進行方針（2026-06-10）

- Figma に **取り急ぎ足せる項目だけ** を並べた版で描画を進める（Analyze 帯、Profit 行、Expenses 明細、▲▼ 等）。
- **2024 年実 PL との全項目・全数値一致** はデバッグには望ましいが、**一旦は後回し**（描画完了後に段階的に寄せる）。
- 支出明細は **ラベル編集可・行の追加可・削除はソフト（非表示）** — [pl-table-label-layout-memo.md](./pl-table-label-layout-memo.md) § 行の非表示

---

## Window Box

| 項目 | 値 |
|------|-----|
| 幅 | **画面全幅**（`profile-wrap` max-width 解除。Monthly Edit と同様に左右余白なし） |
| 高さ | **`calc(100vh - 132px)`** — ツールバー下から下端まで表領域 |
| 縦スクロール | Business Days より下（`pl-table-scroll-y`） |
| 横スクロール | ラベル帯 **350px 固定**、月次列は **残り viewport 全幅＋横スクロール**（12 ヶ月） |
| 背景 | `#1f1e1e` |
| 角丸 | なし |
| テーマ | Sci-Fi / Office 両対応 |

---

## ラベル帯（合計 350px）

| 部分 | 幅 |
|------|-----|
| Profit & Loss 角セル / Business Days 行 | **350px** 全幅（`colspan="2"`） |
| 縦ラベル（Income / Total Expenses 等） | **50px** |
| 横ラベル | **300px**（350 − 50。右端は P&L 角セルと揃う） |

横ラベルが長い場合はセル内 **横スクロール**（`overflow-x: auto`）。

---

## テーブル構造（2 分割 + 固定ペイン）

```
pl-table-window
├── pl-split-seam          … 300px 位置の固定縦線（z-index: 25）
├── pl-table-frozen        … 縦スクロールしない上部
│   └── pl-table-split
│       ├── pl-label-pane  … 300px 固定
│       └── pl-data-pane--frozen  … 横スクロール（ヘッダー同期用）
└── pl-table-scroll-y      … Income 以降（縦スクロール、max-height: calc(100vh - 300px)）
    └── pl-table-split
        ├── pl-label-pane
        └── pl-data-pane     … 横スクロール
```

### 固定ペイン（Excel のウィンドウ枠固定）

**固定（上）**: Profit & Loss ヘッダー ＋ 月名 / Amount・Ratio ＋ **Business Days** まで  
**スクロール（下）**: Income 以降

- Business Days 行の下線: **`3px double`**（`--pl-freeze-border`）— 固定エリアとスクロールエリアの境界
- 横スクロール: 固定ブロックとスクロールブロックの `scrollLeft` を JS で同期
- 行高: ラベル表・データ表を `syncPlSplitRowHeights` でペア同期

### 既知の課題（WIP）

- 縦スクロール固定の体感確認には **スクロール領域を超える行数** が必要（現状 7 行程度ではバーが出ないことが多い）
- ラベル帯とデータ帯の **横線ズレ** は行高同期 JS で緩和中。完全解消は未確認
- 境界縦線は `pl-split-seam` オーバーレイで固定（セル border に依存しない）

---

## ヘッダー行

| 要素 | サイズ | 備考 |
|------|--------|------|
| Profit & Loss（角セル） | 350×60 | `colspan="2"` `rowspan="2"`、**21px 中央寄せ** |
| 月名（1〜12月） | 260×30 | `colspan="2"`（Amount+Ratio 束ね）、13px 中央 |
| Amount | 160×30 | 13px 中央 |
| Ratio | 100×30 | 13px 中央 |

---

## データ行 — 共通

| 項目 | 値 |
|------|-----|
| 行高（固定ペイン〜Business Days） | **30px** |
| 行高（Business Days より下・スクロール領域） | **40px**（縦ラベル用） |
| 枠線 | 1px `#58e1f3`（Office: `#999`） |
| フォント | EN: Orbitron / JA 本文: BIZ UDPGothic |
| 横文字の寄せ | **Profit & Loss のみ中央**、他は右寄せ（ラベル）／中央（数値） |

---

## 実装済みブロック

### 1. Business Days

| 側 | 内容 |
|----|------|
| ラベル | 「Business Days」/「営業日」— 300px 全幅（`colspan="2"`） |
| データ | 月ごと `colspan="2"`、営業日数 |

**データ同期**: `kpiNavigator.annualDailyShared` から `syncPlBusinessDays()`。`storage` イベント + `annual:businessDayMapChanged` を監視。

---

### 2. Income（収入）— 4 行

| # | EN | JA | スタイル |
|---|----|----|---------|
| 縦ラベル | Income | 収入 | 13px、`rotate(-90deg)`（文字頭が下） |
| 1 | Store Sales | 店舗売上 | 13px 右寄せ |
| 2 | Sales A | 売上A | 13px + ✎ 編集ボタン |
| 3 | Sales B | 売上B | 13px + ✎ 編集ボタン |
| 4 | Total Sales | 売上合計 | **15px bold** |

**月次データ（Income のみ特殊）**

- **260px × 1 セル / 月**（`pl-month-cell`、`colspan="2"`）
- Amount / Ratio の **2 分割なし**（パーセンテージ不要）
- ダミー: `$123,456` / `¥123,456`

---

### 3. Total Expenses（総支出）— 3 行

| # | EN | JA | スタイル |
|---|----|----|---------|
| 縦ラベル | Total / Expenses（改行） | 総 / 支出 | 13px、90px（3×30）高、`rotate(-90deg)` + 改行中心をセル縦中央に配置 |
| 1 | Fixed | 固定費 | 13px |
| 2 | Expected | 変動費 | 13px |
| 3 | Total Expenses | 総支出 | **15px bold** |

**月次データ**

- 月ごと **Amount 160px + Ratio 100px**（合計 260px）
- ダミー金額 + 空 Ratio セル

---

### 4. Analysis（分析）帯 — Total Expenses の直下

| 項目 | 仕様 |
|------|------|
| 帯タイトル | EN: **Analysis** / JA: **分析**（Figma の "Analyze" を名詞形に調整） |
| 帯の高さ | **40px**（スクロール領域の他行と同じ） |
| 折りたたみ | 左端 **▼ / ▶** で開閉（`#pl-analyze-body`） |
| 背景 | シアン **30%**（`rgba(88, 225, 243, 0.3)`）— 帯＋ブロック内セル全体 |
| 月次セル | **260×30** 単一セル（Income と同様、`colspan="2"`） |

**3 グループ（縦ラベル 50px + 横ラベル 250px）**

1. Food cost Ratio / 食材原価率 — 4 行（Food Sales … Drink Procurement Costs）
2. Labor share / 労働分配率 — 3 行（社員人件費 … 合計）
3. Food & Labor Ratio / FL率 — 3 行（月次食材費 … 合計）

データセルは現状 **空**（描画のみ）。横スクロールはメイン表と同期。

---

### 5. Profit（利益）— Analysis の直下

| 項目 | 仕様 |
|------|------|
| ラベル | ラベル帯 **全幅 350px**（`colspan="2"`） |
| 文言 | EN: **Profit** / JA: **利益** — **15px bold・右寄せ** |
| 行高 | **40px** |
| 月次セル | **260px × 1** / 月（`colspan="2"`）。現状空 |

---

## 生成関数（`build_pl_table_page.py`）

| 関数 | 用途 |
|------|------|
| `pl_label_colgroup()` / `pl_data_colgroup()` | 列幅定義 |
| `month_head_row_v1()` / `month_subhead_row_v1()` | 月ヘッダー |
| `bizdays_label_row_v1()` / `bizdays_data_row_v1()` | Business Days |
| `income_label_rows_v1()` / `income_data_rows_v1()` | Income |
| `expenses_label_rows_v1()` / `expenses_data_rows_v1()` | Total Expenses サマリー |
| `_section_data_rows_v1()` | Amount+Ratio 2 セル行の共通化 |

定数:

- `INCOME_ROWS_V1` — 4 行
- `EXPENSES_ROWS_V1` — 3 行（Fixed / Expected / Total Expenses）

---

## 実装フェーズの区切り

| フェーズ | 状態 | 内容 |
|----------|------|------|
| **A — 描画** | **進行中** | 枠線・ラベル・ブロック構成・ダミー数値。入力色分けはまだ不要 |
| **B — データ組み込み** | 未着手 | 科目マスタ、Daily/Monthly 入力元、[pl-expense-input-source-design.md](./pl-expense-input-source-design.md) に従う。**Tars が理解・実装をリード** |
| **B の必須 UX** | 未着手 | **入力可能セルだけ色付き** — 「ここにしか入力できない」を PL / Monthly 両方で明示 |

ChatGPT メモ（入力元設計）は **フェーズ B の正本**。どの科目が Daily / Monthly かは描画完了後に確定してよい。

---

### 6. Expense detail（支出明細）— Profit の直下

| 項目 | 仕様 |
|------|------|
| ラベル列 | 大 50 + 中 50 + 小 **300** = ラベル帯 **400px** |
| 行追加 / 非表示 | 中費目セル内 **＋／−**（`active: false` ソフト削除） |
| 並べ替え | 小費目右端 **▲▼** |
| ラベル編集 | **ダブルクリック / F2**（鉛筆なし） |

---

### 7. Graph（収支縦棒）— 支出明細の直下

| 項目 | 仕様 |
|------|------|
| 月次セル | **260 × 700px**（`colspan="2"`） |
| 棒エリア高さ | **533px** 固定 |
| 棒幅 | **30px 一本**（左半 15px + 右半 15px の2分割） |
| 黒字月 | 100% = 売上。上: **緑 30px幅**（利益）／ 下: **赤15px \| 黄+橙15px**（支出合計と内訳） |
| 赤字月 | 100% = 支出。**左15px 赤**（全高）の中に下端揃えで **緑15px**（収入）／ **右15px 黄+橙**（内訳・全高） |
| % 表示 | 分母 = **売上**（表 Ratio 列と整合） |
| データ | フェーズ A: ダミー（3月目 = 赤字サンプル）。`window.plGraphRender(data)` で差し替え可 |

---

### ラベル編集（実装済み・フェーズ A）

| 対象 | 編集可 | 保存先 |
|------|--------|--------|
| Income 行（Total 除く） | ✓ | `kpiNavigator.plLabelOverrides` |
| Total Expenses サマリー（Fixed / Expected） | ✓ | 同上 |
| Analysis 明細（Total 除く） | ✓ | 同上 |
| 支出明細 小費目 | ✓ | `kpiNavigator.plLineCatalog` |
| 縦大費目・Total 行・Profit・Analysis 帯 | ✗ | — |

操作: **ダブルクリック** または フォーカス + **F2** → 編集 → **Enter** 確定 / **Esc** 取消。

---

## PL Insight フローティング（2026-06）

PL 表ツールバー **PL Insight** から開く読み取り専用オーバーティング（Monthly Insight Floating Window 同系）。旧称 **Expenses Bridge** / **Compare（比較）** は廃止。

| 項目 | 状態 |
|------|------|
| 固定ヘッダー・日付ナビ・× 閉じる・Area 1/2/3 | 実装済 |
| Area 1〜3（FL 横棒・累積折れ線・縦棒・凡例） | **モック描画完了** |
| ラベル確定・実データ・No Data | 未着手 |

詳細・作業順・名称統合: **[pl-insight-final-adjustments-memo.md](./pl-insight-final-adjustments-memo.md)**  
プレス向け v2 構想: [press-release-backlog.md](./press-release-backlog.md) § PL Insight

---

## 未実装（Figma / PDF 順の次ステップ）

### フェーズ A（描画）

- [x] 固定費・変動費の **明細行**（デフォルト科目 + ＋追加 + ▲▼）
- [x] Analysis 帯
- [x] Profit 行
- [x] **ラベル編集（ダブルクリック / F2）**
- [x] **月次 Graph 帯**（ダミー数値・黒字/赤字切替）
- [ ] 年計列
- [ ] 家賃・物件選択（固定費行ラベル内ドロップダウン）
- [ ] 行の並べ替え（▲▼ ボタン案を優先検討）
- [ ] 縦スクロール固定の仕上げ・行追加後の QA

### フェーズ B（データ・入力 UX）

- [x] **ユーザー追加科目の入力元確認**（＋押下 → モーダル → `inputStyle` 保存。PL選択=緑行 `--input-pl`）
- [x] ラベル名変更時の入力元再確認（プレースホルダ「新規科目」からの初回編集は除く）
- [ ] 科目ごと `Input Method`（Daily Aggregate / Monthly Manual / + Adjustment）— テンプレ `default` の確定
- [ ] 入力元バッジ（`DAILY` / `MONTHLY`）
- [ ] Monthly Edit 側の緑行表示・カタログ同期
- [ ] Monthly ↔ PL の二重入力ガード（編集不可セル）
- [ ] 日次合算の自動反映 + 調整額
- [ ] 参考予算（定規）— `pl-table-label-layout-memo.md` § 参考予算

---

## JS（インライン）

| 処理 | 説明 |
|------|------|
| `syncPlBusinessDays()` | 営業日数セル更新 |
| `syncPlSubheadTop()` | 月ヘッダー高さ → CSS 変数 |
| `syncPlSplitLayout()` | 固定/スクロール各ペアの行高同期、seam 高さ、横スクロール同期 |
| `plYear` | URL `?year=` |
| PL 編集・保存 | `kpi-pl-expenses-v1:` 系（旧ロジック、v1 グリッド再描画と段階統合中） |
| ラベル上書き | `kpiNavigator.plLabelOverrides`（Income / Analyze / Expenses サマリー） |
| 支出カタログ | `kpiNavigator.plLineCatalog`（明細行・ラベル・順序・`active`） |
| 月次グラフ | `window.plGraphRender(months)` — 12 件 `{ sales, expenseRatio, fixedRatio, expectedRatio }` または `{ sales, expenses, fixed, expected }` |

---

## 確認方法

1. Monthly Edit → **View Profit & Loss**
2. **Cmd+Shift+R** ハードリロード（生成 HTML の反映）
3. 横スクロール後: 境界縦線・横線の連続性
4. Business Days 下の二重線、Income 260px 単一セル、Total Expenses 縦ラベルの改行位置

---

## 行並べ替え（検討メモ）

Expenses 明細行の順序変更について:

- **ドラッグ**: ラベル表 + データ表の 2 同期、ブロック内制限があり中〜高コスト
- **▲▼ ボタン**: 低〜中コスト。誤操作少・Undo と相性良。**第一候補**
- 実装時は DOM 直操作より **行配列モデル → 両表再描画** を推奨

詳細はチャット上の合意待ち。明細行実装時に合わせて設計する。

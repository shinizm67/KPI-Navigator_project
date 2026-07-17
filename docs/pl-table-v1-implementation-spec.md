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

- ~~縦スクロール固定の体感確認にはスクロール領域を超える行数が必要~~ → 明細＋Graph で十分に溢れる。検証 `verify_pl_scroll_freeze.py`
- ラベル帯とデータ帯の **横線ズレ** は行高同期 JS で緩和（明細再描画・ResizeObserver）。残差は 2px 超で検証失敗
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

**データ同期**: `kpiNavigator.kpiYearStore.timeline`（真実源）から `syncPlBusinessDays()`。判定は Annual/MEP/Insight と同一（`businessDays[iso]` 明示 → `dailySales[iso]===0` は休 → 土日既定休）。`storage`（`kpiYearStore`/`annualDailyShared`）+ `annual:businessDayMapChanged` / `kpi:businessDayChanged` / `kpi:dailySalesChanged` / `kpi:readSurfacesRefresh` を監視。

---

### 2. Income（収入）— 4 行

| # | EN | JA | スタイル |
|---|----|----|---------|
| 縦ラベル | Income | 収入 | 13px、`rotate(-90deg)`（文字頭が下） |
| 1 | Store Sales | 店舗売上 | 13px 右寄せ |
| 2 | Sales A | 売上A | 13px + ✎ 編集ボタン |
| 3 | Sales B | 売上B | 13px + ✎ 編集ボタン |
| 4 | Total Sales | 売上合計 | **15px bold** |

**月次データ（Income）**

- 月ごと **Amount 160px + Ratio 100px**（合計 260px）— 支出明細と同レイアウト
- Ratio(%) = 金額 ÷ 売上合計（`sales_total`）。合計行はデータ有時 **100.00%**
- 金額は MEP 日次の月累積（読取専用）。ダミー初期表示は `—`

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
- [x] **年計列（2026-07-17）** — 12ヶ月の右に Amount160+Ratio100（`data-month="year"`）。JA「年計」/ EN「Annual」。金額＝12ヶ月合計、Ratio＝年計額÷年計売上合計。営業日も年計合算。読取専用。実装 `pl_year_total_client.py` + `build_pl_table_page.py` / `pl_expense_detail_client.py`、検証 `verify_pl_year_totals.py`。
- [x] **家賃・物件選択（2026-07-17）** — 固定費の物件行ラベル内ドロップダウン（JA: 賃貸/自持、EN: Rented/Owned）。`kpiNavigator.plOccupancy`=`rent|owned`。賃貸=`exp_rent`／自持=`exp_depreciable_asset_tax` を排他表示（金額は保持）。実装 `pl_expense_detail_client.py`、検証 `verify_pl_occupancy.py`。
- [x] **行の並べ替え（▲▼・実装済確認 2026-07-17）** — 同バケット内で `sortOrder` 入替 → 両表再描画。検証 `verify_pl_row_reorder.py`。
- [x] **縦スクロール固定の仕上げ（2026-07-17）** — Business Days まで固定 / Income 以降 `pl-table-scroll-y`。縦バー幅を固定ヘッダ側 `padding-right` で相殺、横 `scrollLeft` を全データペイン同期、明細再描画後に行高同期。検証 `verify_pl_scroll_freeze.py`。

### フェーズ B（データ・入力 UX）

- [x] **ユーザー追加科目の入力元確認**（＋押下 → モーダル → `inputStyle` 保存。PL選択=緑行 `--input-pl`）
- [x] ラベル名変更時の入力元再確認（プレースホルダ「新規科目」からの初回編集は除く）
- [x] **収入ブロック 読取化（2026-07-15 / 2026-07-16 改訂）** — 収入は **すべて PL では読取専用**（日次で MEP 入力 → 月次累積を PL 表示）。**合計＝`kpiNavigator.kpiYearStore.timeline.dailySales` の月合計（＝総売上・実績・プレースホルダ`1234`除外）が正**。売上A/B＝`years.{Y}.dailyIncome[streamId]` の月合計。**店舗売上＝合計−(A+B)**（`dailySales` に内訳が含まれるため差し引き・0でクランプ／`timeline.dailySales` は不変＝二重計上回避）。`kpi:dailySalesChanged`/`kpi:mepDataChanged` で自動更新。支出系（`data-pl-editable`/`kpi-pl-expenses-v1`）とは完全分離。実装 `scripts/pl_income_client.py`、検証 `scripts/verify_pl_income_store_sales.py`。
- **MEP 複数収入ストリーム（Sales A/B）** — 3分割完了（波及ゼロ設計）。
  - [x] **Phase 1（2026-07-16 完了・完全無害）** — `kpiYearStore` に `dailyIncome` の read/write を純追加。`ensureYearMepData` で `dailyIncome:{}` 初期化 / `loadMepYearPayload` が `dailyIncome` を返す / `bulkPersistMepYear` が `payload.dailyIncome[streamId][iso]` を保存（0/空は削除）＋`kpi:mepDataChanged` / `writeDailyIncome`・`readDailyIncome` を export。**書き込む側がまだ無いので既存挙動は不変**（`timeline.dailySales`＝総売上・`dailyExpenses`・summary/insight 全て回帰 OK）。実装 `scripts/kpi_year_store_client.py`、検証 `scripts/verify_kpi_daily_income_store.py`。
  - [x] **Phase 2（2026-07-16 完了・波及ゼロ）** — 危険な二重注入掃除を**回避する安全設計にピボット**。MEP-STORE ブロック（`buildMepPersistPayload` 等）には一切触れず、**独立フック**を新設: 全保存経路が発火する `kpi:mepDataChanged`(source=`monthly-edit-float`) を1か所で拾い、Phase 1 の `KpiYearStore.bulkPersistMepYear(year,{dailyIncome},…)` で A/B(`sales_a`/`sales_b`)を `years.{Y}.dailyIncome[streamId]` へマージ保存（再帰は排他フラグで防止／`rowValueById` は lineId キー）。PL は `店舗売上＝dailySales−(A+B)`／`合計＝dailySales` に修正済み。実装 `scripts/mep_income_streams_client.py`＋`scripts/apply_mep_income_streams.py`（BEGIN/END マーカーで冪等）／`scripts/pl_income_client.py`、検証 `scripts/verify_mep_income_streams.py`。**フック有効/無効で `timeline.dailySales` は完全同一＝副作用ゼロを実証**（PL/store/summary/insight 全回帰 OK）。
    - 注1（既知の別課題・要別タスク）: MEP-STORE ブロックの**二重注入は未掃除**。実際に動くのは後発コピー（`refreshMepSalesFromStore` 等あり・メモ安全マージ無）、マーカー付き先発コピーは影に隠れて未実行。生成元 `mep_store_client.py` と実行コードが不一致で、`build_monthly_edit_pages.py` は必要パッチ（`apply_read_surface_sync`/`apply_mep_strategy_user_note`）を呼ばないため**単純再ビルドは機能欠落**。Phase 2 では触らず温存。
    - 注2（~~既知不具合~~ **2026-07-17 修正**）: 入力パス=`mep` で Confirm のたびに `timeline.dailySales` が増える問題。原因は自己発火の `kpi:dailySalesChanged` → `refreshMepSalesFromStore` が総売上を `store_sales` に戻し A/B と再合算していたこと。修正: 自己 source（`monthly-edit-float`/`mep`）は再 hydrate スキップ + `syncMonthlySalesFromAnnualStoreForMonth` を `店舗=総額−(A+B)` に変更。検証 `verify_mep_income_streams.py`（2回 Confirm で額不変）。
  - [x] **Phase 3（2026-07-16 完了）** — MEP で Sales A/B の ✎ を再有効化し、編集ラベルを `kpiNavigator.plLineCatalog`（収入行）へ保存。空カタログ時は埋め込み `PL_LINE_CATALOG` からシードして書き込む（`upsertPlIncomeLabelsFromState`）。PL は `applyLabelOverrides` で income スコープをカタログ優先表示。注入の冪等修正（古い `upsert` 重複残骸を除去）込み。実装 `scripts/apply_mep_pl_catalog.py` / `scripts/build_pl_table_page.py`、検証 `scripts/verify_mep_income_label_sync.py`。
- [x] **営業日数の実データ化（2026-07-16）** — PL 営業日数を `kpiYearStore.timeline`（真実源）から算出。判定は Annual/MEP/Insight と同一（`businessDays[iso]` 明示 → `dailySales[iso]===0` は休 → 土日は既定休）。従来は休業日マップが空だと**全暦日**を数えていたが、土日既定休を適用して整合。`kpi:businessDayChanged`/`kpi:dailySalesChanged`/`kpi:readSurfacesRefresh` で自動更新。支出配賦用の `isBizDayIso`/`countBizDaysInMonth`（`annualDailyShared`）は温存（表示専用の変更）。実装 `scripts/build_pl_table_page.py`、検証 `scripts/verify_pl_business_days.py`。
- [x] **Ratio(%) セル（2026-07-16・支出明細＋収入）** — 各行の右セルに `金額 ÷ 売上合計` を表示（`xx.xx%` / データ無は —）。売上合計は収入ブロックの Total Sales。収入行も Amount/Ratio 分割済み（店舗/A/B/合計）。実装 `scripts/pl_ratio_client.py` + `income_data_rows_v1`、検証 `scripts/verify_pl_ratios.py`。
- [x] **科目ごと Input Method（2026-07-17・テンプレ確定）** — デフォルト方針: **FL 近傍（食材・ドリンク・アルバイト）= daily**（月次切替可）／**固定費＋それ以外の変動費（光熱・通信・備品・雑費など）= monthly**。カタログ schema v7。旧デフォルトのままの行は schema 移行で更新（ユーザーが明示切替した値は保持）。実装 `pl_line_catalog.py` / `pl_expense_detail_client.py`、検証 `verify_pl_catalog_input_defaults.py`。
- [x] **入力元 UX（2026-07-16）** — 各行トグル不採用。ラベル **ダブルクリック / F2** で **統合モーダル**（科目名＋入力元、Don't ask again なし）。固定費は科目名のみ。実装 `pl-expense-label-edit-modal` / `pl_expense_detail_client.py`、検証 `verify_pl_input_source_label_ux.py`。→ [pl-expense-input-source-design.md § 入力元の選び方](./pl-expense-input-source-design.md#入力元の選び方採用-ux--統合モーダル)
- [x] **入力元バッジ（廃止・2026-07-17）** — 行ラベル横の `DAILY` / `MONTHLY` 常時表示は外した。入力可否の主信号は **緑（編集可）／黒（閲覧）**。入力先の明示は科目編集モーダル内のみ。
- [x] **Monthly Edit 側の緑行表示・カタログ同期（実装済み）** — daily 行は MEP で入力可（緑）、monthly 行は MEP 非活性（`mef-row--pl-readonly`）＋ PL カタログ同期。実装 `scripts/apply_mep_pl_catalog.py`。
- [x] **Monthly ↔ PL の二重入力ガード（実装済み）** — monthly は PL のみ編集可、daily は PL 読取専用（MEP 合計表示）。実装 `pl_expense_detail_client.py` / `pl_monthly_allocate_client.py`。
- [x] **日次合算 + 調整額（2026-07-16・最小版）** — daily 行の PL 表示 = MEP 月次合計 + 調整額。調整はダブルクリック / F2 のモーダルで編集（日次は消さない）。ストア `kpi-pl-expense-adjustments-v1:{year}`。実装 `scripts/pl_monthly_allocate_client.py`、検証 `scripts/verify_pl_expense_adjustment.py`。3 行分割 UI は将来。
- [x] **入力元切替時の旧データ整理（2026-07-16）** — daily↔monthly 切替で使わなくなる側を掃除（daily→monthly: `dailyExpenses[lineId]` 削除 / monthly→daily: `kpi-pl-expenses-v1` の当該キー削除）。同スタイル再設定は保持。実装 `scripts/pl_expense_detail_client.py`、検証 `scripts/verify_pl_input_style_cleanup.py`。
- [x] **参考予算 L1（2026-07-17・最小版）** — 総支出サマリー直下に「変動費の参考枠」行。`売上 × max(0, 目標総費率65% − 固定費率)`。固定費は `kpi-pl-expenses-v1` の fixed 行合計。目標総費率は `kpiNavigator.plTargetCostRate`（未設定時 0.65）。実装 `scripts/pl_reference_budget_client.py`、検証 `scripts/verify_pl_reference_budget.py`。
- [x] **参考予算 L2（2026-07-17・最小版）** — 明細セルに過去同月中央値比率×売上の「目安」。方式 A（L1 と独立）。実績 > 目安×1.05 で強調。検証 `verify_pl_reference_budget_l2.py`。同曜日・枠内按分は未着手。
- [x] **参考予算 L2 トグル化（2026-07-17）** — コーナー（損益表/Profit & Loss）セルに +/- ボタン。既定 OFF で目安は非表示、ON で全 Amount セルに目安を出し明細行高を +12px 拡張（`body.pl-guide-on`）。**変動費だけでなく固定費行も対象**。over 強調はトグル ON 時のみ。状態は `kpiNavigator.plGuideOn` に保存。実装 `scripts/pl_reference_budget_client.py`＋`scripts/build_pl_table_page.py`、検証 `scripts/verify_pl_l2_toggle.py`。

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

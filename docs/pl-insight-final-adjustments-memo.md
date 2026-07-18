# PL Insight — 最終調整メモ

更新日: 2026-07-18  
ステータス: **実データ接続 完了（スライス1）**（Area1/2/3 の折れ線・縦棒・FL スナップショットを実ストアへ接続）→ 残は §4 のドリルダウン（`press-release-backlog` v2）・本番店休カレンダー（§4 の Y 軸/No Data/Office 色/アクセシビリティは完了）

---

## 名称の変遷（ドキュメント統合用）

| 時期・文脈 | 名称 | 備考 |
|-----------|------|------|
| 初期実装 | **比較** / **Compare** | オーバーレイ内部タイトル（`graph_overlay_title` ラベルキー）。UI 表示からは外れ、キー名のみ残存 |
| 中間（2026-06 頃） | **Expenses Bridge** | PL 表ツールバー・フローティングヘッダーの表示名。**廃止** |
| **現行（正）** | **PL Insight** | PL 表中央上ボタン・フローティングウィンドウヘッダー・aria ラベル |

**読み替えルール**

- 旧チャット・メモの「Expenses Bridge」「Compare オーバーレイ」「比較フローティング」→ すべて **PL Insight**（本 doc）。
- コード上の CSS / DOM 接頭辞（`pl-graph-overlay-*`・`pl-compare-*`）は **内部実装名**。リファクタ前はそのまま。ユーザー向け文言は `toolbar_graph` = `"PL Insight"`。
- プレス向け Pro 機能の構想・Analyze/Graph タブ案 → **`docs/press-release-backlog.md` § PL Insight**（将来 v2）。本ページのフローティングはその **シェル＋Area 1〜3 プロトタイプ**。

---

## 概要

PL 表（`app/profit/pl/`）から開く **読み取り専用フローティングウィンドウ**。Monthly **Insight Floating Window** と同系統の UX（固定ヘッダー・日付ナビ・× 閉じる・Area ジャンプ）。

| 項目 | 内容 |
|------|------|
| 入口 | PL 表ツールバー **PL Insight**（`#pl-graph-open`） |
| 本体 | `#pl-graph-overlay` |
| 再生成 | `python3 scripts/build_pl_table_page.py` → JA/EN `app/profit/pl/index.html` |
| 確認 | ブラウザ **Cmd+Shift+R** |

---

## 現状（描画完了スコープ）

### 共通 UI

- 固定ヘッダー **170px**（タイトル・日付 ◀︎ ▶︎ 本日・Area 1/2/3 ジャンプ・0.5px 下線）
- 右上 **× 閉じる**（Insight と同仕様: 22×22px、`z-index: 10`）
- スクロール本体 `#pl-compare-scroll`、Area ジャンプは各 Area 先頭の **0.5px 横線** に合わせてスクロール

### Area 1 — 当日ベース（選択月・選択日まで）

| ブロック | 内容 |
|----------|------|
| FL スナップショット | 選択日 / 前年同曜日（2 ブロック横棒） |
| 累積折れ線 | Income / Expenses / Fixed / Expected / Profit タブ。This Year / Last Year / Best Year |
| 縦棒 Daily Performance | 同上 5 指標。折れ線とチェックボックス **独立** |
| X 軸 | 当月日次。1 日・月末は Y 軸 +15px / 右端 −15px を棒中心。日付ラベル 1,5,10…,月末 |

### Area 2 — 前年同月（フル月）

| ブロック | 内容 |
|----------|------|
| FL スナップショット | 前年同月同日 / 2 年前同月同日 |
| 折れ線・縦棒 | Area 1 と同 UI。**表示は当月全日**（`dim = periodCount`） |
| 店休（テスト用モック） | 1月=最初の日曜まで休み / 以降毎週日曜休み（1月最初の日曜のみ営業）/ 12月=最終日曜〜年末（該当なければ 30 日〜） |
| 累積折れ線 | 店休日は **横ばい**（前日累積を継承、0 に落とさない） |
| 縦棒 | 店休日は日次 0 → 棒なし |

### Area 3 — 年次 YTD

| ブロック | 内容 |
|----------|------|
| FL スナップショット | YTD（選択日）/ 前年 YTD |
| 折れ線・縦棒 | **月次 1〜12**。1 月・12 月も両端 15px インセット。ラベル 1〜12 |
| 縦棒タイトル | Monthly Performance |

### データ

- **すべてモック**（`buildArea1ChartData` / `buildArea2ChartData` / `buildArea3ChartData`）
- **No Data 制御**・実 PL / Monthly ストア連携は **未着手**

### 主要実装ファイル

| パス | 役割 |
|------|------|
| `scripts/build_pl_table_page.py` | 正本: `pl_graph_overlay_html`・`pl_compare_client_js`・Compare 系 CSS・`compare_labels` |
| `app/profit/pl/index.html` | 生成物（編集はスクリプト経由） |

---

## 最終調整 — 作業順（予定）

頭から順に進める想定。**Monthly Edit ↔ PL 表連携**（科目カタログ・日次合算）が実データの前提。

### 1. ラベル・文言

- [ ] Area タイトル・FL キャプション・折れ線/縦棒タイトル（JA/EN）の確定  
  → `compare_labels` / `build_pl_table_page.py` 内 `L[...]`
- [ ] Insight 既存用語との統一（Food & Labor / Income / Expected 等）
- [ ] `graph_overlay_title`（比較/Compare）キーの整理 or 削除検討

### 2. 実数値の取り込み

- [x] Monthly Edit 日次 → PL 月次集計パイプライン（`docs/pl-expense-input-source-design.md`）— **PL 表と同一ストアから読む**（後述 §実装状況）
- [x] PL 表・FL スナップショット用 KPI ストア（Income / Food / Labor / 支出内訳）
- [x] Area 1/2/3 各系列の **年・月・日** マッピングを実データ定義に合わせる
- [x] データなし日・店休日 → **No Data**（何も返さない）。FL スナップショットは全 0 の期間で `null`（No Data カード）。※モック店休ルールは撤去済（実データが 0 の日は棒なし・累積横ばい）。**本番店休カレンダー連携は営業日判定を kpiYearStore.timeline に統一済**

### 3. グラフの実データ化

- [x] 横棒 FL（`renderHsnapBlock`）をストア値に差し替え
- [x] 累積折れ線・縦棒の `buildArea*ChartData` を実集計に接続
- [x] Best Year 表示条件を実データで再確認 — **過去年（<選択年）で年間売上が最大の年**。データ年が 3 年未満なら非表示（`plInsight.bestYear`）
- [~] Area 2 店休日の累積横ばい — 実データでは「その日の値が 0 → 棒なし・累積は前日据置」で自動達成（明示的店休マップは不要）

### 4. UX 微調整（必要に応じて）

- [x] ホバー・ツールチップ・Y 軸スケール — ツールチップは実装済（This/Last/Best 値表示）。**Y 軸を「きれいな目盛」に刷新（2026-07-18）**：`compareNiceAxis` で 1/2/2.5/5 ×10^n の丸め目盛にし、`formatScale` を 1 桁小数対応（`7.5k` 等）。旧実装の 8k/23k のような半端目盛・小さい値でも 10k 刻みになる問題を解消。折れ線・縦棒の両方に適用。
- [x] Office モード色（2026-07-18）— グラフ系列色（折れ線 stroke・縦棒 fill・軸線・ガイド線・ホバー点・凡例スウォッチ）を**CSS クラス化**し、Office モード（白背景）で濃色に上書き。This=`#0a63c2`／Last=`#b8860b`／Best=`#0f9403`、軸線/ガイド=`#888`、ツールチップ metric=`#555`。淡いシアン・黄が白地で見えづらい問題を解消。
- [x] Area ジャンプ・アクセシビリティ（2026-07-18）— Area ナビの `role="tablist"`（tab 不在で意味破綻）を `role="group"` に修正。メトリクスタブに `aria-pressed` を付与（折れ線・縦棒とも）。オーバーレイは既に `role="dialog" aria-modal="true" aria-labelledby` 済を確認。
- [ ] Monthly Edit / PL 表からのドリルダウン（`press-release-backlog` v2 構想）

---

## 実装状況（2026-07-18 スライス1：実データ接続）

新モジュール **`scripts/pl_insight_data_client.py`**（`window.__plInsight`）を追加。PL 表と**同一ストア**を読むため、Insight の数値は PL 表の表示と一致する（source of truth 一致）。compare オーバーレイ（`pl_compare_client_js`）側はモック `buildArea1/2/3ChartData`・`area1CanShowBestYear/area1BestYearNumber`・`renderCompareFl` の FL 取得を **`window.__plInsight` への薄い委譲**に置き換え（モック関数は残置・未使用）。

### 指標の定義（根拠を説明できる形）

| 指標 | 定義 | 出典ストア |
|------|------|-----------|
| Income | 日次売上（プレースホルダ `1234` 除外） | `kpiYearStore.timeline.dailySales` |
| Expenses | Fixed + Variable | 下記 |
| Fixed | `bucket==='fixed'` 費目の合計 | 月次: `kpi-pl-expenses-v1:{year}[lineId:month0]` |
| Variable(=Expected) | `bucket==='variable'` 費目の合計 | 日次: `years.{Y}.dailyExpenses[lineId][iso]`（+ 調整 `kpi-pl-expense-adjustments-v1`） |
| Profit | Income − Expenses | 導出 |

- **月次セル一致**：日次入力費目の月額は「MEP 日次合計 + 調整額」で PL 表の表示と一致させる。
- **日次配賦**：月次入力費目を日別に落とす際は共通エンジン `window.__plPreviewMonthlyExpenseAllocation` の `byDate` を使用（**日別合計＝月額**を保証。ヘッドレスで検証済）。
- **営業日/店休**：`kpiYearStore.timeline.businessDays` 明示 → `dailySales===0` は休 → 土日既定休（PL 営業日数行と同じ system B）。
- **FL スナップショット**：Food = `expenseAttribute` が `food_cost`/`drink_cost`（既定 `exp_food_cost`/`exp_drink_cost` にフォールバック）、Labor = `salaries_wages`/`variable_labor`/`labor_related`（既定 `exp_fixed_labor`/`exp_variable_labor`）。`renderHsnapBlock` の `variable`=Food・`fixed`=Labor に対応。全 0 期間は `null`（No Data）。
- **Best Year**：過去年（<選択年）で年間 Income 最大の年。全データ年が 3 年未満なら非表示。
- **前払い/按分の月跨ぎ自動化はしない**（会計方針依存・手動運用）。

### ライブ更新
オーバーレイが開いている間に PL/MEP データが変わったら再描画：`kpi:mepDataChanged` / `kpi:dailySalesChanged` / `kpi:readSurfacesRefresh` と `storage`（`kpiYearStore`・`plLineCatalog`・`kpi-pl-expenses-v1:*`・`kpi-pl-expense-adjustments-v1:*`）を購読。描画毎に `plInsight.resetCache()`。

### 検証
JavaScriptCore ハーネス（`/tmp/pl_insight_harness.js`）で 32 アサーション全 PASS：月次/日次メトリクス、日次配賦の月末一致（Area1 累積 fixed 終端＝月額）、Area3 月次 YTD、Best Year（過去年で年間売上最大＝該当年）、FL（Food/Labor 分解・No Data→null・YTD 合算）。生成 PL 日英ページのインライン JS 構文チェックも OK。

### 実装ファイル
| パス | 役割 |
|------|------|
| `scripts/pl_insight_data_client.py` | **正本**: `window.__plInsight`（実データ集計・Area builder・FL・Best Year） |
| `scripts/build_pl_table_page.py` | 注入（`insight_data_js`）＋ compare 側の委譲・ライブ更新配線 |

## No Data 表現の統一方針（2026-07-18 確定・全 UI 共通ルール）

> **データのない日/期間を表現するときは、要素を消してレイアウトを詰めない。骨格（ラベル・行・軸）を残し、値だけを「—」にする。**

背景: データのない日に横棒ブロックごと消していたため、下のコンテンツが上へ「ドカン」と跳ね上がり、視線の基準が失われて非常にストレスだった（ユーザー指摘）。

統一ルール（No Data 時）:

1. **枠・ラベルは残す** — 見出し（日付キャプション）と各行ラベル（例: Income / Food & Labor / Food / Labor）は常時表示。
2. **高さを一定に保つ** — ブロックを削除・折り畳みしない。データ有無で行数・高さが変わらないようにする（必要なら `min-height` で担保）。
3. **値は「—」** — 数値/比率は `—`（em dash）で表示。ゼロ実績（`$0`）と「未入力・データ無し」を混同させない。
4. **無データの淡色ヒント** — 「—」は淡色（例: `rgba(88,225,243,0.45)`）にして無データと分かるようにするが、ラベルは通常色のまま。
5. **バーやプロットは描かない** — 横棒は幅 0（＝非表示）、折れ線/縦棒は 0 で横ばい（前値据置）にして「爆発的な再レイアウト」を起こさない。

実装リファレンス: PL Insight の横棒 = `renderHsnapBlock`（`scripts/build_pl_table_page.py`、`allowNoData` 時も 3 行骨格＋「—」を描画・`.pl-compare-hsnap--empty` で meta を淡色・`.pl-compare-hsnap { min-height }`）。**今後、他画面で No Data を表現する場合もこの方法に統一すること。**

## 関連ドキュメント

| Doc | 関係 |
|-----|------|
| [press-release-backlog.md](./press-release-backlog.md) § PL Insight | Pro プレス向け **将来 v2**（Analyze タブ・固定/変動比較・ドリルダウン） |
| [pl-table-v1-implementation-spec.md](./pl-table-v1-implementation-spec.md) | PL 表本体・フェーズ B（Monthly 連携） |
| [pl-table-label-layout-memo.md](./pl-table-label-layout-memo.md) | 科目マスタ・参考予算（定規）・Insight 3 本比較 |
| [pl-expense-input-source-design.md](./pl-expense-input-source-design.md) | 日次/月次入力元・二重入力防止 |
| [insight-graph-cumulative-trend-line-chart.md](./insight-graph-cumulative-trend-line-chart.md) | 累積折れ線 UX 参照（Monthly Insight） |
| [insight-monthly-analyze-grid-rules.md](./insight-monthly-analyze-grid-rules.md) | Insight フローティングレイアウト参照 |
| [index-profit-hub.md](./index-profit-hub.md) | Pro 利益ハブの位置づけ |

---

## メンテナンス

- PL Insight の仕様変更・完了タスクは **本ファイルを更新**する。
- 旧名称（Expenses Bridge 等）で書かれたメモを見つけたら、上表に従い **PL Insight** に読み替え、必要なら本 doc へリンクを追加する。

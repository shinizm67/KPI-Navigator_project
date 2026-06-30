# PL Insight — 最終調整メモ

更新日: 2026-06-19  
ステータス: **大まかな描画完了**（モックデータ）→ 以降は本メモの順で微修正・実データ化

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

- [ ] Monthly Edit 日次 → PL 月次集計パイプライン（`docs/pl-expense-input-source-design.md`）
- [ ] PL 表・FL スナップショット用 KPI ストア（Income / Food / Labor / 支出内訳）
- [ ] Area 1/2/3 各系列の **年・月・日** マッピングを実データ定義に合わせる
- [ ] データなし日・店休日 → **No Data**（何も返さない）。モック店休ルールは本番店休カレンダーに置換

### 3. グラフの実データ化

- [ ] 横棒 FL（`renderHsnapBlock`）をストア値に差し替え
- [ ] 累積折れ線・縦棒の `buildArea*ChartData` を実集計に接続
- [ ] Best Year 表示条件（サービス開始年・3 年分以上）を実データで再確認
- [ ] Area 2 店休日の累積横ばいロジックを本番データでも維持

### 4. UX 微調整（必要に応じて）

- [ ] ホバー・ツールチップ・Y 軸スケール
- [ ] Office モード色
- [ ] Area ジャンプ・アクセシビリティ
- [ ] Monthly Edit / PL 表からのドリルダウン（`press-release-backlog` v2 構想）

---

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

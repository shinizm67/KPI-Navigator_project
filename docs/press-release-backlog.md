# プレスリリース／後回し機能ネタ — 索引

更新日: 2026-08-21

## このファイルの役割

ローンチ v1 では入れず、**後続アップデート・プレスリリース・告知**で出す想定の機能を一覧化する。詳細仕様は各専用 doc に分散しているため、本ファイルは **索引＋新規たたき台** を担う。

### 探していた doc はどれか

**プレス向けネタを明示している中心は `docs/memo-read-surfaces.md` の「追加予定機能（Strategy Note / AI）」**（System Comment / Alert Message）。  
「プレスリリース専用の単一 doc」は以前からなく、Annual / Past Sales / Monthly など各メモの **未実装・別フェーズ** にも同種の項目が散らばっている。本索引で横断参照できるようにした。

---

## 一覧（優先度・告知イメージ）

| # | ネタ（短名） | 主な対象プラン | 告知の強さ | 詳細 doc |
|---|-------------|----------------|------------|----------|
| 1 | **Insight AI — System Comment** | Basic / Pro | 大（AI 導入） | `docs/memo-read-surfaces.md` § System Comment |
| 2 | **Insight AI — Alert Message**（Annual Target Revision） | Basic / Pro | 大（AI 導入） | 同上 § Alert Message |
| 3 | **PL Insight**（支出グラフ・比較・ドリルダウン） | **Pro** | 大（Pro 差別化） | **本ファイル § PL Insight** · 実装シェル: **`docs/pl-insight-final-adjustments-memo.md`** |
| 3b | **PL表レイアウト・科目／数値の修正**（縦書き大見出し＋中見出し2列） | **Pro** | 大（実装必須） | `docs/pl-table-label-layout-memo.md` |
| 3c | **PL 参考予算（定規）** — KPI 予想売上 × 過去費目比率・変動費参考枠 | **Pro** | 中〜大（Pro 差別化） | `docs/pl-table-label-layout-memo.md` § 参考予算（定規） |
| 4 | **支出 CSV アップロード** | Pro | 中 | `docs/monthly-page-memo.md` § 支出CSV |
| 5 | **変動人件費・法域テンプレ・CSV** | Pro | 中 | `docs/part-time-labor-cost.md` |
| 6 | **POS 連携・Register/Settings** | 全般 | 中 | `docs/csv-upload-pos-import-memo.md` |
| 7 | **Past Sales — CSV 取込** | Basic / Pro | 中 | `docs/past-sales-floating-window-memo.md` §13 |
| 8 | **売上データ／過去売上 — Sales 列ソート** | Basic / Pro | 小 | 同上 §13 |
| 9 | **過去売上 → Focus Bar / Monthly 反映** | Basic / Pro | 中 | 同上 §13 |
| 10 | **Focus Bar Edit 廃止**（今年窓へ集約） | Basic / Pro | 小（内部整理） | `docs/annual-edit-modal-memo.md` |
| 11 | **Annual KPI ストリップ 4 エリア本実装** | Basic / Pro | 中 | `docs/annual-kpi-strip-memo.md` |
| 12 | **Daily Graph ポップアップ** | Basic / Pro | 中 | `docs/annual-surface-integration-memo.md` |
| 13 | **日次目標の AI 日別提案** | Basic / Pro | 大 | `docs/target-sales-daily-monthly-annual.md` §7 |
| 14 | **Monthly Vertical Focus Bar 拡張**（行追加・スナップ） | Pro 寄り | 小〜中 | `docs/monthly-vertical-focus-bar-memo.md` |
| 15 | **利益ハブ各セクション本実装**（日次／月次／年次利益） | Pro | 中 | `docs/index-profit-hub.md` |
| 16 | **ツールチップ → YouTube チュートリアル** | 全般 | 小 | `docs/csv-upload-pos-import-memo.md` §ホバー |
| 17 | ~~**Strategy Note：Monthly Edit 導線**~~ | Basic / Pro | 小 | **実装済み（2026-07-22）** — Monthly User Note クリック → Monthly Edit + Strategy Note。Annual 帯の重複 UI は削除。`docs/memo-read-surfaces.md` |
| 18 | **Sales Data — 繁閑期%アシスト**（過去平均参照・100%正規化） | Basic / Pro | 中〜大 | **本ファイル § Sales Data 繁閑期%アシスト** · `docs/year-rollover-data-architecture.md` |
| 19 | ~~**歯車フィードバック／リクエスト窓口**~~（Survey 本製品ではない） | 全般 | 小 | **実装・本番済み（2026-08-11）** — 再スモーク 2026-08-21 OK。`docs/ops-support-email-and-mobile-view-memo.md` §2 |
| 20 | **スマホ縦持ち「数値を見る」専用面**（閲覧優先・情報量削減） | Basic / Pro | 大 | `docs/ops-support-email-and-mobile-view-memo.md` §3 |
| 21 | **ブランド改称 → Key Performance Navigator**（JA/zh-TW サブ付き・確定） | 全般 | 大（必須） | `docs/brand-key-performance-navigator.md`（旧 Pilot 案は同メモ §2） |
| 22 | **予約台帳（Restaurant / Salon Edition）** — 仮売上ナビ・CSV・カレンダー/Row切替 | Basic / Pro | 大（ローンチ直後〜配布相手次第で前倒し） | `docs/reservation-ledger-edition-memo.md` |

### ローンチ済み・索引から外すもの（参考）

| 項目 | 備考 |
|------|------|
| 今年の日次売上窓（Sales Data） | `docs/annual-current-year-sales-floating-window-plan.md` は当初「未実装」だったが **2026-06 接続済み**（`past-sales-floating-window-memo.md` §13） |
| 歯車フィードバック／リクエスト窓口（#19） | 実装 2026-08-09・本番通し 2026-08-11・再スモーク 2026-08-21。`ops-support-email-and-mobile-view-memo.md` §1–§2 |

---

## 製品方針メモ（2026-06-04 合意たたき台）

**PL Insight フル版は後回し → プレス第2弾**でよい。理由: 実用性は高いが v1 必須ではない／実装が Insight 姉妹＋支出ドメインで重い。

**ただし Pro 初版だけは「表だけ」だと Basic の Insight との対比で弱い**ため、可能なら v1 は次のどちらか。

- **A（推奨）**: PL 表＋**軽いグラフ 1〜2 枚**（月次支出トレンド、売上 vs 支出の概要など）のみ今
- **B**: 表のみのまま、文言で「分析拡張予定」を明示し、空白の期待値を抑える

フル Insight 級（下記 § PL Insight）は **データが溜まったタイミングのプレス**向け。

---

## PL Insight（Pro・プレス向けたたき台）

### 目的

- Pro の **PL 表**（`app/profit/pl/`）に、Monthly **Insight** と同系統の **読み取り専用・分析ペイン**を追加する。
- **売上側（Basic でも Insight あり）と対になる「支出・利益の物語」**を Pro で提供し、「Basic にあるのに Pro の支出は表だけ」という期待値ギャップを埋める。

**2026-06 時点**: PL 表から開く **PL Insight フローティング**（旧称 Expenses Bridge / Compare オーバーレイ）の **Area 1〜3 描画シェル＋モックグラフ**は完了。ラベル確定・実データ・No Data は **`docs/pl-insight-final-adjustments-memo.md`** を正とする。本 § の v2 Analyze/Graph タブ構想はその先。

### 参照 UX

- レイアウト・タブ（Input / Analyze / Graph 等）の考え方: Monthly Insight オーバーレイ（`docs/insight-monthly-analyze-grid-rules.md`、`docs/insight-graph-cumulative-trend-line-chart.md`）。
- データ入力は **Monthly 支出・PL 表**が正。Insight は **編集不可・ドリルダウンで入力画面／月次へ**。

### v1（ローンチ〜プレス前の最小、任意）

| 要素 | 内容 |
|------|------|
| グラフ 1 | 月次 **支出合計トレンド**（当年、折れ線 or 棒） |
| グラフ 2（任意） | **売上 vs 支出** 同一期間の概要（既存 KPI ストアから集計） |
| 非スコープ | 固定費／変動費分解、ベスト／ワースト月比較、年跨ぎ複数系列 |

### v2（プレスリリース本命）

#### Analyze 想定ブロック（案）

1. **支出トレンド（当年 vs 過去）**  
   - 過去年（確定月）と当年を同一グラフまたは並列。  
   - 固定費／変動費（または FL / Food / Labor）の **積み上げ or 2 系列**。

2. **固定費 vs 変動費 — 過去 vs 今年**  
   - 月次または四半期で比較。  
   - 定義は `docs/part-time-labor-cost.md` および PL 科目マスタと一致させる。

3. **ベンチマーク月**  
   - **過去最優秀月・最下位月**（利益率 or 支出率など指標は要選定）を並べ表示。  
   - 各カードから **その月の Monthly / PL 詳細**へ遷移（クエリ: `year` + `month`）。

4. **ドリルダウン**  
   - グラフ上の月クリック → Monthly ページ該当月 or PL 表の該当ブロックへ。  
   - Global Menu の現在コンテキストを壊さないよう、離脱確認は PL / Monthly 既存ルールに合わせる。

#### Graph 想定（案）

- 累計 **支出 vs 予算（あれば）** の折れ線（売上 Insight の累計トレンドと同型: `docs/insight-graph-cumulative-trend-line-chart.md`）。
- 季節性バー（Past Sales Analyze の繁閑グラフと同思想を支出側に）。

#### プラン・ゲーティング

| プラン | PL 表入力 | PL Insight |
|--------|-----------|------------|
| Basic | 不可（Change Plan 誘導） | 不可 |
| Pro | 可 | **v2 で Pro 専用**（v1 ミニグラフを入れる場合も Pro のみ） |

#### データ・実装メモ（未着手）

- 集計レイヤ: `localStorage` / 将来 API — Annual・Monthly・PL で **同一 KPI 定義**（`docs/monthly-page-memo.md` § PL 連携の到達目標）。
- **参考予算（定規）**: KPI 月次予想売上 × 過去費目比率、変動費参考枠 — `docs/pl-table-label-layout-memo.md` § 参考予算（定規）（**#3c**）。
- 過去年支出は **Monthly 確定月＋CSV（将来）** に依存。v2 告知前に「何ヶ月分あればグラフが意味を持つか」を決める。
- 新規 doc 候補（実装着手時）: ~~`docs/pl-insight-spec.md`（本 § から分割）~~ → **`docs/pl-insight-final-adjustments-memo.md`**（描画シェル完了・最終調整タスク）

#### プレス見出し案（英日）

- JA: 「Pro に PL Insight — 支出の季節性・固定費比較・過去最良月との差をワンクリックで」
- EN: "PL Insight for Pro — Compare fixed vs variable costs, spot your best and worst months, and jump to details."

---

## Sales Data — 繁閑期%アシスト（プレス向けたたき台）

更新日: 2026-06-24

### 現状（v1 実装済み）

- **Sales Data → Analyze** タブ右端に **計画繁閑期%（H/L Season% Setting）** 列と **Monthly Allocated Total** 行。
- 明るいシアン背景で **「ここが繁閑期%を作るエリア」** と視覚グループ化（見出し列＋12ヶ月＋合計行）。
- 手動編集（5%刻み）→ `KpiYearStore.plan.monthlyHlWeights` 永続化 → Annual / Monthly Cockpit 繁閑期%列へ同期。

### 将来（v2 — プレス告知候補）

**目的:** 左隣列の **観測繁閑期%**（過去実績・`observed.monthlyPct` または Analyze 上の Seasonality %）を参照し、ユーザーが **Monthly Allocated Total ≈ 100%** に収まる範囲で計画繁閑期%を設定しやすくする。

| 要素 | 内容 |
|------|------|
| **参照元** | 過去年の観測%（実績から算出した月次平均%）。複数年ある場合は Phase 3 の複数年平均。 |
| **左列** | Analyze 5列目 — 観測・参考（read-only） |
| **右列** | 計画繁閑期% — 編集可（現行） |
| **ガイド** | Monthly Allocated Total が 100% から乖離しているとき、調整方向のヒント（例: 「3月を -5%」） |
| **アシスト（案）** | 「過去平均を初期値にコピー」→ ユーザーが微調整／「100%に正規化」ボタン（保存値はユーザー入力のまま保持する方針は `year-rollover-data-architecture.md` §7 と整合） |
| **データ** | `years.{Y}.observed.monthlyPct` + `years.{operatingYear}.plan.monthlyHlWeights` |

### プレス見出し案

- JA: 「過去の繁忙期を学習 — ワンクリックで今年の月次配分を最適化」
- EN: "Learn from past seasonality — one-click monthly weight suggestions that sum to 100%"

### 関連

- `docs/year-rollover-data-architecture.md` §4.3（観測%算出）· §7（plan 保存）
- `docs/target-sales-daily-monthly-annual.md` §3（繁閑期フロー）
- Phase 3 実装: 複数年 `observed` 平均による plan 初期値

---

## メンテナンス

- 新しい「後回し／プレス」項目を決めたら **本表に 1 行追加**し、詳細は専用 doc へ。
- AI 系の文言・Figma 参照は **`docs/memo-read-surfaces.md` を正**とし、本ファイルでは要約のみに留める。
- 実装完了したら一覧から **「ローンチ済み」節へ移動**または行を削除。

## 関連ドキュメント

- `docs/pl-insight-final-adjustments-memo.md` — **PL Insight フローティング**（描画完了・最終調整・旧称 Expenses Bridge 統合）
- `docs/memo-read-surfaces.md` — **プレス向け AI ネタ（System Comment / Alert Message）**
- `docs/index-profit-hub.md` — Pro 利益ハブの位置づけ
- `docs/monthly-page-memo.md` — 支出入力・CSV・PL 到達目標
- `docs/pl-table-label-layout-memo.md` — PL 行ラベル（大縦／中横）レイアウト正
- `docs/part-time-labor-cost.md` — 変動人件費・将来 CSV
- `docs/past-sales-floating-window-memo.md` — Past Sales 未実装一覧

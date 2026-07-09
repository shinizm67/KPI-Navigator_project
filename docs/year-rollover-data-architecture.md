# 年跨ぎデータ引き継ぎ — 設計メモ（ドラフト）

更新日: 2026-07-08  
ステータス: **実装中** — P0 / 1 / 3 / 4 / 5 / 5b / 5c / 6 / **8** / **9** / **10**（KPI + **10-c**）完了。**2** / **6b** / **11** 残。

**優先度:** 繁閑期%・Cockpit・PL/MEP 同期・Insight グラフより**先**。  
三本柱の**単一時系列ストア**が無い限り、入力はすべて無意味になる。

**このファイルを読むタイミング**

1. 年次目標・繁閑期%・日次売上の永続化を実装する**前**
2. Sales Data / Past Sales / MEP / Annual Edit のどれかに手を入れる**前**
3. 「今年」と「過去」の UI 分離・プラン別入力制限を設計するとき

**関連ドキュメント**

| ドキュメント | 役割 |
|--------------|------|
| `docs/target-sales-daily-monthly-annual.md` | 目標売上・繁閑期の算出フロー（高レベル） |
| `docs/past-sales-floating-window-memo.md` | Past Sales 窓の現行実装・`pastSalesShared` |
| `docs/annual-current-year-sales-floating-window-plan.md` | Sales Data 窓・`annualDailyShared` |
| `docs/annual-kpi-strip-memo.md` | Cockpit 繁閑ウェイト・Monthly Table |
| `docs/edit-floating-window.md` | Monthly Edit Page（MEP）全体仕様 |
| `docs/annual-surface-integration-memo.md` | コックピット・Focus Bar・イベント連携 |

---

## 1. 背景と問題意識

### 1.1 なぜ今やるか

KPI Navigator のコアは「ユーザーと一緒に作る年間月次 KPI」である。  
その前提データ（日次売上・営業日・年次目標・繁閑期%）は**年を跨いでも残り、振り返れ、翌年の計画に使われなければならない**。

現状は以下が未整備であり、年跨ぎで破綻する。

| 課題 | 現状 |
|------|------|
| Sales Data → Past Sales の自動引き継ぎ | ✅ 実装 + 受け入れ完了（§11.1 · 2026-07-02） |
| 年次目標売上の年別永続化 | **なし**（メモリ + 未接続フック） |
| 繁閑期%の永続化 | **なし**（Cockpit DOM 編集のみ） |
| 入力面の正本統一 | `annualDailyShared` と `pastSalesShared` が**別箱・移行ルールなし** |
| MEP の支出・メモ | セッション内メモリのみ（リロードで消失） |

### 1.2 プロダクト上の合意（基本方針）

> **営業日・日次売上・年次目標は、Annual / Sales Data / MEP のどこから入力しても 1 次情報として扱う。年を跨いだら、どの画面から見ても過去データとして参照できる。**

- 「入力面」と「保存面」を分離する（UI は複数、正本は一つ）。
- 「今年」と「過去」は**ビューの切り替え**であり、別ストアへの手動コピーではない。
- 年跨ぎ時は**移動ではなく確定（ロック）+ 当年バケットの初期化**とする。

### 1.6 年跨ぎ時の Sales Data → Past Sales 引き継ぎ（合意・2026-07）

**プロダクト期待（ユーザー合意）:**

- 例: **2027 年運用開始**時、**2026 年に Sales Data（当年窓）で入力・Save 済みの日次売上・営業日・年次目標**は、**再入力なし**で **Past Sales Data の 2026 年**として参照・編集できること。
- 窓は **Sales Data（当年）** と **Past Sales（過去年）** の 2 つだが、正本は **単一 `timeline` / `KpiYearStore`**。年跨ぎは**別ストアへの手動コピーではない**。
- 当年データは `years.{operatingYear}` に確定し、翌年の `operatingYear` 切替後は **過去年ビュー（Past Sales・MEP・Focus Bar）** から同じ ISO の事実が読めること。

**実装タイミング:** **Sales Data 窓 Phase**（`docs/annual-current-year-sales-floating-window-plan.md` §11）+ **Phase 1b**（本表）。Past Sales Input 単体では行わない。

**受け入れ（Phase 1b 完了時）** — 手順: `docs/annual-current-year-sales-floating-window-plan.md` **§11.1**

- [x] 12/31 まで Sales Data で Save した年が、翌年 1/1 以降 Past Sales の当該年セレクタで開ける
- [x] 日次売上・営業日チェック・年間目標が Sales Data 保存時点と一致（`timeline` 正本）
- [x] ユーザーによる再 CSV / 再手入力は不要（補正は Past Sales から可能）

**合格判定:** Tars = SD-R1 コンソール smoke · ユーザー = Past Sales 目視確認（最終合格）— **2026-07-02 ユーザー合格**

**本基盤が無い限り、Annual / Monthly でいくら数値を入力しても意味がなく、アプリは完成しない。**  
KPI の提案・過去との比較グラフという強みは、すべてこのデータの一貫性に依存する。

### 1.3 三本柱（必須 1 次情報）

以下 3 つは **同年・同月・同日（同 ISO）で常に同一の値** でなければならない。  
Annual / Monthly（Daily・Insight 含む）の**どの画面を開いても同じ正本を閲覧**している状態が必須である。

| # | 1 次情報 | 内容 | 集計への影響 |
|---|----------|------|-------------|
| 1 | **日次売上** | 営業日ごとの実績金額 | 月次・年次実績、KGI、Insight |
| 2 | **営業日** | 日別 ON/OFF（チェック）→ 月次・年次の営業日数 | 定規・日次平均・繁閑%算出 |
| 3 | **年次目標売上** | その年の KPI 年間目標 | 月次目標・日次目標・達成率 |

**禁止:** 4/5 の売上を Annual と Monthly で別々に入力・保持すること（UX 上の最悪ケース）。  
**必須:** 1 か所の更新が全画面に即反映されること（同一タブはイベント、別タブは `storage`）。

年を跨いだ後は、上記 3 つすべてが**前年（過去年）の 1 次情報**として残り、  
Annual / Monthly の **Focus Bar・Table Window（Cockpit Open 含む）** から参照できること。

### 1.4 アプリの強み（データが繋がったとき）

1. 三本柱が揃う → 月次繁閑%・目標配分を含む **KPI を提案できる**
2. 過去年が蓄積される → **すぐに過去と比較するグラフ**で可視化できる
3. Annual と Monthly の両方で **編集・閲覧・管理**できる（正本は一つ、ビューが複数）→ このアプリならではの UX

### 1.5 単一時系列（Unified Timeline）— 1 次情報の持ち方（再認識）

**今年・去年・一昨年…の違いは「同じ時系列上のどの位置か」だけである。**

日次売上と営業日（店休/営業日チェック）は、**暦年で箱を分けた別データではない**。  
すべて **`YYYY-MM-DD`（ISO 日付）をキーとする 1 本の時系列**上の事実として保持する。

```
時系列（正本・日次実績）
──────────────────────────────────────────────────────────────►
  …  2024-12-31   2025-01-01   …   2025-12-31   2026-01-01   …
      sales: N      sales: N         sales: N      sales: N
      biz: T/F      biz: T/F         biz: T/F      biz: T/F
```

**入力面（いずれも同じ時系列へ書き込む）:**

| 入力面 | 備考 |
|--------|------|
| Annual — **Sales Data** Floating Window | 当年向け UI。中身は時系列の一部ビュー |
| Annual — **Past Sales Data** Floating Window | 過去年向け UI。同じ時系列の別ビュー |
| **Monthly Edit Page（MEP）** | **1 ページ**。月ピッカーで任意年・月へ移動し同じ時系列を編集 |

→ Sales Data と Past Sales は**窓が2つ**だが、**データは 1 本の時系列**。  
→ MEP も**Annual 専用ではなく**、過去年の日次を開いて編集できる必要がある（権限・ロックは別レイヤー）。

**年次目標売上**は日次ではないため **年単位メタ**（`years.{YYYY}.plan`）として時系列と並存するが、  
閲覧・編集の一貫性要件は三本柱と同じ（全サーフェスで同じ値）。

### 1.6 ナビゲーション要件（時系列がある以上の必須 UX）

データが時系列上に存在する以上、**Annual / Monthly とも**次を満たすこと。

| 手段 | 要件 |
|------|------|
| **スクロール（縦・横）** | Focus Bar・Table Window で、**データが存在する範囲**を縦横スクロールして**年を跨いで**連続移動できる（2024 → 2025 → 2026 …） |
| **カレンダー / 日付ジャンプ** | 年・月・日を指定して任意の ISO に飛べる（2024-04-05 など） |
| **年セレクタ** | Cockpit・Past Sales・MEP 月ピッカー等で表示年を切り替え、時系列の該当区間を表示 |
| **一貫した選択日** | `selectedDate`（または同等）がサーフェス間で共有され、Annual ↔ Monthly 遷移しても同じ日を指す |

**禁止:** 当年しか Focus Bar に行けない・Past Sales 窓を開かないと去年が見えない、など**データはあるのに UI から到達できない**状態。

**意図（ユーザー合意 2026-06-17）:** 単一時系列にデータがある限り、Annual / Monthly の **Table Window** と **Focus Bar** は、スクロール（縦・横）だけで年を跨いで辿れる UX とする。カレンダージャンプは補助手段。

### 1.7 日次 1 次情報の入力面（2 箇所）

**当年・過去年を問わず**、日次売上と営業日（店休チェック）を入力できる面は次の **2 つ**（+ 過去年は Past Sales 窓が第 3 ビュー）。

| 入力面 | 画面 | 備考 |
|--------|------|------|
| **A** | Annual — **Sales Data** Floating Window | 当年向け UI が主。実体は時系列への書き込み |
| **B** | **Monthly Edit Page（MEP）** | 1 ページ。月ピッカーで年月移動 |
| （参考） | Annual — **Past Sales Data** Floating Window | 過去年向け UI。P0 後は同じ `timeline` へ統合 |

→ **A と B から同じ ISO に入力可能**（プランにより排他トグルで一方のみ編集可にする設計は §2.4）。  
→ 正本は 1 つ。二重に別値が残る状態は禁止。

年次目標売上の入力面は別（Cockpit Edit 等）だが、閲覧は全サーフェスで一致（§1.3）。

---

## 2. 設計原則

### 2.1 単一正本（Single Source of Truth）

```
入力面（複数）                         正本                           表示面（複数）
──────────────────────────────────────────────────────────────────────────────────
Annual — Sales Data Floating Window  ─┐
Annual — Past Sales Floating Window  ─┼→  単一時系列（日次）     →  Focus Bar
Monthly Edit Page（1 ページ）         ─┘   + 年次メタ（目標等）       Table Window
                                         KpiYearStore                 Cockpit / Daily / Insight
```

- **日次売上・営業日:** `timeline.dailySales[iso]` / `timeline.businessDays[iso]` — **年を問わない 1 マップ**
- **年次目標・繁閑%等:** `years.{YYYY}.plan` — 年メタ（時系列と直交）
- 同一 ISO の値は**常に 1 つ**。最後の書き込みが勝つ（`last-write-wins`）。
- 書き込み元は監査用メタデータとして記録（`source`, `updatedAt`, `updatedBy`）。

### 2.2 年スコープ（ロック・計画用。日次実績の格納とは別概念）

日次実績は **§1.5 の単一時系列**に載る。  
「年」は次の用途で使う（**同じデータを別箱にコピーしない**）。

- `operatingYear` = アプリが「今年」として扱う年。
- `years.{YYYY}.status` = `"open"` | `"locked"` — 過去年の**編集可否**・年確定スナップショット（`observed`）用。
- `year < operatingYear` の日次データも **timeline 上に残る**。locked は**書き込み制御**であり別ストアではない。

### 2.3 実績と計画の分離

| 種別 | 例 | 性質 |
|------|-----|------|
| **実績（actual）** | 日次売上、営業日（確定後） | 入力された事実。年確定後は原則追記修正のみ |
| **計画（plan）** | 年次目標売上、月次繁閑%（設定値） | ユーザーが決めた配分。年ごとにスナップショット |
| **観測（observed）** | 繁閑期%（実績から算出） | 派生だが履歴として保存。「あの年はこうだった」 |

Cockpit Open テーブルの列対応（参考）:

| 列 | 種別 |
|----|------|
| 繁閑期%（4列目・ハイライト） | **計画** `annualPlan.monthlyHlWeights` |
| 月次平均%（9列目） | **観測** `seasonalityObserved.monthlyPct` |
| 月次実質%（10列目） | **評価**（計画目標 vs 実績・都度算出） |

### 2.4 入力経路の排他（プラン・設定）

日次売上・営業日の入力経路は **排他** とする（前回合意・Phase 5b で確定）。

| 項目 | ルール |
|------|--------|
| **排他対象** | `timeline.dailySales` + `timeline.businessDays` **のみ** |
| **Monthly（MEP）選択** | MEP で売上・営業日・支出・Daily Notes を編集可。Annual 側の日次は **Read-Only** |
| **Annual 選択** | Sales Data / Table 等で日次編集。MEP の日次売上・営業日は **Read-Only** |
| **未保存でトグル** | 確認ダイアログ → 未保存時は **3 択**（保存して切替 / 保存せず切替 / キャンセル） |
| **プラン** | **Pro** のみトグル表示。**Standard** は非表示・既定 `annual` |
| **設定の正本** | `KpiYearStore.getDailySalesInputPath()` — ページごとの独立トグルは持たない |

**MEP CSV 取込（Phase 5b）:** 表示月のみでなく **表示年の全日付**を `timeline` に反映する（月を跨いで取り込み）。確認ダイアログに日数と「月を跨いで取り込み」を明示。

**実装:** `scripts/_kpi_sales_input_path_ui.js` + `apply_kpi_sales_input_path_ui.py`（Annual / MEP 各 ja/en）。  
各ページは `window.__KPI_PATH_CHANGE_HOOKS__` で未保存検知・保存・破棄を登録（MEP: グリッド + Daily Notes Float、Annual: Sales Data モーダル）。

- 複数アカウント同時ログイン時は編集ロック（上位優先・同率は一方のみ編集可）は**別レイヤー**（Phase 5）。

---

## 3. データモデル（案）

### 3.1 ストレージキー（localStorage / 将来 DB）

| キー | 内容 |
|------|------|
| `kpiNavigator.kpiYearStore` | ルートオブジェクト（下記を内包） |
| `kpiNavigator.kpiYearStore.meta` | `schemaVersion`, `operatingYear`, `lastRolloverAt` |
| `kpiNavigator.kpiYearStore.timeline` | **単一時系列（日次実績の正本）** |
| `kpiNavigator.kpiYearStore.years.{YYYY}` | 年メタ（計画・観測・ロック・支出・メモ） |

**`timeline`（日次 1 次情報 — 年を横断する 1 マップ）:**

```javascript
timeline: {
  dailySales: {
    "2024-04-05": 120000,
    "2025-04-05": 135000,
    "2026-04-05": 140000
    // ISO キーは全世界で一意。年はキーに含まれる
  },
  businessDays: {
    "2024-04-05": true,
    "2025-04-05": false,
    "2026-04-05": true
  }
}
```

**年レコード `years.{YYYY}`（年単位メタ + 日次以外）:**

```javascript
{
  year: 2025,
  status: "locked",           // "open" | "locked" — 編集制御・確定用（日次データの格納場所ではない）
  lockedAt: "2026-01-03T...", // 年確定日時（null = 未確定）

  // --- 計画（1次情報・年単位）---
  plan: {
    targetSales: 652528.55,
    monthlyHlWeights: [85, 85, 100, ...],
    updatedAt: "...",
    source: "annual-edit"
  },

  // --- 観測（年確定時スナップショット。timeline から集計）---
  observed: {
    annualSales: 640000.00,
    totalBusinessDays: 290,
    monthlyPct: [101.35, 99.37, ...],
    computedAt: "..."
  },

  // --- MEP 固有（日次・時系列に近いが行次元あり）---
  dailyExpenses: { /* lineId → { iso → amount } */ },
  dailyMeta: { /* memos, flags, weather — §8.1 */ }
}
```

※ `dailySales` / `businessDays` は **`timeline` にのみ**持つ。年レコード内に重複コピーしない。

**旧ドラフトからの変更点:** 日次実績を `years.{YYYY}.dailySales` に年別分割する案はやめ、**単一 `timeline` マップ**を正とする。年跨ぎは「別箱へ移動」ではなく **timeline はそのまま + `years.{Y}.status/observed` の更新**。

### 3.2 書き込み API（ランタイム・全画面共通）

```javascript
KpiYearStore.writeDailySales(iso, amount, meta)      // → timeline.dailySales
KpiYearStore.writeBusinessDay(iso, isOpen, meta)    // → timeline.businessDays
KpiYearStore.readDaily(iso)                         // 任意年の1日
KpiYearStore.readRange(startIso, endIso)            // スクロール・集計用
KpiYearStore.writeAnnualPlan(year, partialPlan, meta)
KpiYearStore.getYearMeta(year)
KpiYearStore.getOperatingYear()
KpiYearStore.listYearsWithData()                    // timeline + years から存在年一覧
```

**ルール:**

- `iso` から `year` を抽出し `years.{year}` に書き込む。
- `year < operatingYear` かつ `status === "locked"` の場合は**編集拒否**（管理者モード・監査付き修正は別途）。
- 同一 `iso` は last-write-wins。`meta.source` は `annual-edit` | `sales-data` | `mep` | `csv` | `rollover` 等。

### 3.3 現行ストアからのマイグレーション

| 現行キー | 移行先 |
|----------|--------|
| `annualDailyShared.targetSalesByDate` | `timeline.dailySales`（ISO キーそのままマージ） |
| `annualDailyShared.businessDayByDate` | `timeline.businessDays` |
| `pastSalesShared.salesByDate` | `timeline.dailySales`（マージ・重複は last-write-wins） |
| `pastSalesShared.businessDayByDate` | `timeline.businessDays` |
| `pastSalesShared.referenceAnnualSalesByYear` | `years.{YYYY}.plan.targetSales` または `observed` |
| `window.__ANNUAL_DATA.targetSales` | `years.{operatingYear}.plan.targetSales` |

初回起動時に `migrateLegacyKpiStores()` を 1 回実行。`schemaVersion` で再実行を防ぐ。

---

## 4. 年跨ぎパイプライン（Year Rollover）

### 4.1 トリガー

次のいずれかで `maybeRolloverYear()` を実行する。

1. アプリ起動時（Annual / Monthly ページ hydrate 後）
2. `operatingYear` がシステム年とずれた初回検知時
3. 管理者が「年度確定」を明示したとき（将来）

### 4.2 処理フロー

```
operatingYear = 2026, 未確定の 2025 がある場合:

  Step A — 2025 を確定（lock）
    1. timeline から 2025 年の ISO を集計し observed を算出・ years.2025 に保存
    2. plan が未保存なら当年運用中の値をスナップショット
    3. years.2025.status = "locked", lockedAt = now
    ※ timeline の 2025-* エントリは削除しない

  Step B — 2026 を初期化（open）
    1. years.2026 が無ければ作成（plan 初期値など）
    2. timeline に 2026 の日次はユーザー入力まで空でよい

  Step C — メタ更新
    - operatingYear = 2026
    - lastRolloverAt = now
    - カスタムイベント kpi:yearRolloverCompleted
```

**注意:** `annualDailyShared` から旧年キーを「削除」するのではなく、**年別バケットへ振り分け済みであること**を正とする。レガシーキーはマイグレーション後に読み取り専用フォールバックとし、最終的に廃止。

### 4.3 観測繁閑%の算出（年確定時）

`docs/target-sales-daily-monthly-annual.md` §3 に準拠。

```
年間売上     = Σ dailySales（営業日のみ）
総営業日数   = count(businessDays === true)
日次平均     = 年間売上 ÷ 総営業日数

各月 m:
  月次実績   = Σ dailySales（月 m の営業日）
  月次定規   = 日次平均 × 月 m の営業日数
  観測%      = 月次実績 ÷ 月次定規 × 100
```

結果を `years.{YYYY}.observed` に保存。再計算可能だが、**locked 後の observed は履歴として保持**（上書きは監査付き）。

---

## 5. 複数年平均 — 翌年 KPI の初期値

### 5.1 ユースケース

ユーザーが 2024 から入力（または CSV で 2024 まで投入）し、2026 年を「今年」とする場合:

- **2024, 2025** は locked な過去データ
- **2026** の計画繁閑%・目標の**提案**に 2024+2025 を使う

### 5.2 ルール（案）

```javascript
function computeBaselineWeights(completedYears, operatingYear) {
  // completedYears: locked かつ observed.monthlyPct が揃っている年（昇順）
  // デフォルト: 直近 2 年の単純平均。1 年しかなければその年のみ。

  var eligible = completedYears
    .filter(function (y) { return y.year < operatingYear && y.observed; })
    .sort(function (a, b) { return b.year - a.year; })
    .slice(0, 2);  // 直近2年（設定で 1〜5 に変更可）

  if (!eligible.length) return repeat(12, 100);

  var months = [];
  for (var m = 0; m < 12; m++) {
    var sum = 0, n = 0;
    eligible.forEach(function (yr) {
      var v = yr.observed.monthlyPct[m];
      if (v != null && isFinite(v)) { sum += v; n++; }
    });
    months.push(n ? Math.round(sum / n) : 100);
  }
  return months;
}
```

| 条件 | フォールバック |
|------|----------------|
| 完了年 0 | 全月 100% |
| 完了年 1 | その年の observed のみ |
| 完了年 2+ | 直近 N 年の月次単純平均（**デフォルト N=2**） |
| 特定月のみ欠損 | その月は 100%、または除外して平均 |

ユーザーは初期値を Edit 画面で調整し、**調整後の値を plan として保存**（観測値は上書きしない）。

### 5.3 年次目標売上の提案（任意・Phase 2）

- 過去 2 年の年間実績の平均 × 成長率（ユーザー入力）
- または前年 plan.targetSales を踏襲  
※ 自動設定するかはプロダクト判断。最低限は**手入力 + 年別保存**が必須。

---

## 6. UI とデータの対応

### 6.1 当年（operatingYear）

| UI | 編集可 | 読むデータ |
|----|--------|-----------|
| Sales Data Modal | ✅ 日次売上・営業日 | `years.{operatingYear}` |
| MEP | ✅ 日次売上・営業日・支出（プランによる） | 同上 + `dailyExpenses` |
| Annual Edit Modal | ✅（プラン・入力経路による） | 同上 |
| Cockpit Open Table | ❌ 閲覧のみ | `plan` + 算出列 |
| 年次目標 Edit | ✅ | `plan.targetSales` |

### 6.2 過去年（year < operatingYear）

| UI | 編集 | 読むデータ |
|----|------|-----------|
| Past Sales Modal | 閲覧中心。補正は監査付き修正モード | `years.{selectedYear}` |
| Cockpit（年切替時） | 閲覧 | `plan` + `observed` のスナップショット |
| MEP | 原則非対象（当年月のみ） | — |
| Analyze タブ | 閲覧 | `observed` |

### 6.3 全サーフェスでの閲覧一貫性（必須）

三本柱は次の **すべて** で同じ `KpiYearStore` を参照する。ハードコード・モック・画面ローカル変数での表示は禁止（移行期のフォールバックを除く）。

| サーフェス | 日次売上 | 営業日 | 年次目標 |
|-----------|---------|--------|---------|
| Annual — Cockpit / Area2 | ✅ | ✅ | ✅ |
| Annual — Focus Bar | ✅ | ✅ | — |
| Annual — Table Window（Open テーブル） | ✅（実績列） | ✅ | ✅（計画） |
| Annual — Sales Data / Past Sales | ✅ 編集 | ✅ 編集 | 参照 |
| Monthly — Cockpit / Area2 | ✅ | ✅ | ✅ |
| Monthly — Focus Bar | ✅ | ✅ | — |
| Monthly — Table Window | ✅ | ✅ | ✅ |
| Monthly — Daily タブ | ✅ | ✅ | ✅ |
| Monthly — Insight | ✅（集計元） | ✅ | ✅ |
| MEP | ✅ 編集 | ✅ 編集 | 参照 |

過去年を選択したときも、上記サーフェスは **その年の locked レコード** を読む（当年用の固定表示にしない）。

### 6.4 画面間同期

- 書き込み後: `kpi:dailySalesChanged` / `kpi:businessDayChanged` / `kpi:annualPlanChanged` を発火。
- 既存 `annual:salesMapChanged` 等は**互換ラッパー**として当面維持し、内部で新 API を呼ぶ。
- 別タブ: `storage` イベントで `kpiNavigator.kpiYearStore` を監視。

---

## 7. 繁閑期%と年次目標の保存（Cockpit 連携）

### 7.1 保存場所

- **計画繁閑%** → `years.{operatingYear}.plan.monthlyHlWeights`
- **年次目標** → `years.{operatingYear}.plan.targetSales`
- Cockpit 4 列目は **read-only** で `plan.monthlyHlWeights` を表示
- 編集は **Annual Edit**（Basic）または将来の専用 Plan タブ

### 7.2 月次目標の算出（表示列）

```
予定日次平均     = plan.targetSales ÷ 予定総営業日数
月次平均目標定規 = 予定日次平均 × 月 m の営業日数
月次目標売上     = 月次平均目標定規 × plan.monthlyHlWeights[m] ÷ 100
```

正規化（12 ヶ月合計＝年次目標を強制）するかは**算出レイヤーのオプション**。  
**保存値はユーザー入力のまま**保持する（前回合意）。

---

## 8. MEP（Monthly Edit Page）の位置づけ

- 日次売上・営業日は Annual と**同一正本**（`KpiYearStore`）。
- 支出（Daily 行）は `dailyExpenses` に年別保存。PL 表カタログ（`plLineCatalog`）と行 ID で対応。
- メモ・天気は `dailyMeta`（§8.1 参照）。
- 年跨ぎ時: 当年の `dailyExpenses` / `dailyMeta` は新バケットへ。旧年は lock され蓄積。

### 8.1 メモ（dailyMeta）— データと UI（別途仕上げ必須）

現状: MEP 最下行の**細いセル**に無理やり入力。リロードで消失。視認性・読み返しに不向き。

**データ（正本）:**

```javascript
dailyMeta: {
  memos: {
  // rowId（または "default"）→ { iso → string }
    "memo1": { "2026-04-05": "雨天。ランチ客減。" }
  },
  flags: {
  // メモが存在する日にフラグ（書き込み時に自動 true）
    "2026-04-05": true
  },
  weather: { "2026-04-05": "rain" }  // 既存相当
}
```

- メモも **年スコープ**で `years.{YYYY}.dailyMeta` に保存（三本柱と同じ Store）。
- 年跨ぎ後も過去年のメモを読み返せること。

**UI/UX 要件（Phase 10 以降・プロダクト必須）:**

| 要件 | 内容 |
|------|------|
| **日付フラグ** | メモがある日はカレンダー・日次レール・Focus Bar 上に視認可能なマーカー |
| **入力** | 狭いグリッドセル依存をやめる。日付タップ → メモパネル / モーダルで十分な幅 |
| **一覧** | 月単位・年単位のメモ一覧（日付・冒頭・全文へドリルダウン） |
| **読み返し** | Insight・戦略メモ連携を見据えた検索・フィルタ（将来） |
| **他画面** | Annual Focus Bar 等からも「その日のメモあり」を参照可能（読み取り） |

MEP グリッド内のメモ行は、移行期は残しつつ **正本は Store** に寄せる。表示は Store から同期。

---

## 9. CSV Upload（将来）

- バルク書き込み: `KpiYearStore.bulkWriteDailySales(year, rows, { source: 'csv' })`
- 2024 年まで一括投入 → `years.2024` locked 扱いは**別途ユーザー確認**（誤 lock 防止）
- 取込後 `observed` は手動または一括再計算ボタンで生成

---

## 10. 実装フェーズ（推奨順）

| Phase | 内容 | 依存 | 状態 |
|-------|------|------|------|
| **P0** | **`KpiYearStore` + `timeline` + マイグレーション + 全入力面を API 経由に** | — | ✅ |
| **P0** | **時系列ナビ（スクロール・カレンダージャンプ・selectedDate 共有）** Annual + Monthly | P0 Store | ✅ |
| **1** | `maybeRolloverYear()` + `observed` 算出 | P0 | ✅ |
| **1b** | **年跨ぎ — Sales Data → Past Sales 自動引き継ぎ**（詳細 §1.6） | 1 + Sales Data 窓 Save 経路 | ✅ 2026-07-02 受け入れ完了 |
| **2** | `annualPlan` 保存 + Cockpit 繁閑% read-only | P0 | 🟡 |
| **3** | **複数年 `observed` → Seasonality % 算出** + Sales Data Analyze 表示 + plan 繁閑% ▲▼ 5% 初期値（詳細 §15-C） | 1 | ✅ |
| **4** | MEP `dailyExpenses` / `dailyMeta` 永続化 | P0 | ✅ |
| **5** | 編集ロック・入力経路排他（基本・`canWrite*` ガード） | P0 | ✅ |
| **5b** | **トグル最終ルール・未保存 3 択 chooser・MEP 年間 CSV** | 5 | ✅ |
| **5c** | **MEP 営業日/売上セルの path・lease 連動**（`editGuardsRefresh`） | 5b | ✅ |
| **5d** | **MEP Save スコープ** — 未ロード月を timeline に 0 上書きしない | 5b | ✅ |
| **6** | **Daily Notes UI**（旧 Memo Float・UNDO/Save・日付ピル） | 4 | ✅ |
| **6b** | **Weekly Insight 連携** + DN 固定 6 行 / 自由 Memo 二層 + **Strategy User Note**（Insight 読取のみ・MEP UI は撤回） | 6 | 🟡 |
| **8** | **読取面同期** — Table Window（Annual / Monthly）・MEP 過去年が `timeline` を表示（詳細 §15-A/B/D） | P0 | ✅ |
| **10** | **Daily Floating Window KPI 配線** + **10-c メモ印**（Focus Bar / Daily 窓 / 日付ボタン） | 8 | ✅（2026-07-09） |
| **9** | **Focus Bar Graph ポップオーバー** — フォーカス日の Daily / Monthly / Annual KPI + 達成率バー（Annual / Monthly 共通・詳細 §15.5） | 8 | ✅（OFF は Daily のみ neutral・MTD/YTD は累計表示） |
| **11** | **曜日別日次目標 KPI** — ベースライン年選択・構成比平均 → 月×曜日 1 日 KPI → TW / Focus Bar（`docs/weekday-target-sales-kpi-memo.md` §6） | 3 + 8 + §15.0 | ⬜ |
| **7** | CSV 監査ログ・POS 連携・DB 移行（本格） | P0+ | ⬜ |

**他機能との関係:**

- PL 表 → MEP 支出ラベル同期（実装済）: `plLineCatalog` は行定義。金額は `dailyExpenses` と別。
- `build_monthly_edit_pages.py` / `apply_mep_pl_catalog.py` 実行後も Store API は維持されるよう **注入スクリプトを Store 対応に更新**すること。

---

## 11. 受け入れ確認（チェックリスト）

- [ ] **timeline 上の 2025-04-05 が Sales Data・Past Sales・MEP のいずれから編集しても同一値**
- [ ] **Focus Bar / Table Window からスクロールまたはカレンダーで 2024 年の日付に到達できる**
- [ ] **Annual ↔ Monthly 遷移後も selectedDate が同じ ISO を指す**
- [ ] 2025 年に入力した日次売上が、2026 年開始後も timeline から参照できる（Past Sales 窓・MEP 2025 月）
- [ ] MEP で入力した売上が Sales Data と同一値（同一タブ・別タブ）
- [ ] 2025 の plan（目標・繁閑%）が 2026 から振り返り可能
- [ ] 2026 初回に plan.monthlyHlWeights が 2024+2025 平均（またはフォールバック）で初期化される
- [ ] Cockpit 繁閑%列は編集不可・plan から表示
- [ ] レガシー `annualDailyShared` / `pastSalesShared` からのマイグレーションが 1 回だけ成功する
- [ ] locked 年の誤編集がブロックされる
- [ ] **4/5 の日次売上が Annual Focus Bar と Monthly Daily で常に同一値**
- [ ] **年次目標が Annual Cockpit と Monthly Area2 で同一値**
- [ ] **過去年選択時、Focus Bar / Table Window がその年の実績・目標を表示**
- [x] メモ入力日にフラグが立ち、月次一覧から読み返せる（Phase 10 / 10-c）

---

## 12. 未確定事項（実装前に決める）

| 項目 | 選択肢 |
|------|--------|
| 年確定のタイミング | 自動（初回起動）のみ / ユーザー確認ダイアログ付き |
| 過去年の修正 | 常に禁止 / 管理者のみ / 監査付きで誰でも可 |
| 平均に使う年数 N | 固定 2 / 設定可能 1〜5 |
| plan 繁閑%の正規化 | 保存は生値のみ / 表示時のみ正規化 / 保存時に正規化オプション |
| `annual-edit-modal` の将来 | Sales Data に統合 / 計画専用に縮小 / 維持 |
| operatingYear | システム年固定 / ユーザーが閲覧年を変更可能 |

---

## 14. 実装直前メモ（2026-06-17・次プロンプト用）

### 14.1 Sales Data と MEP の重複入力 — 現状の再確認

**質問:** 重複入力は既に解決しているか？このまま P0 実装に進んでよいか？

**回答（コード確認済み）:**

| 項目 | 状態 |
|------|------|
| 共通ストア | **あり** — 両方とも `kpiNavigator.annualDailyShared`（`targetSalesByDate` / `businessDayByDate`）を参照 |
| MEP → Sales Data | **あり** — 売上セル `change` 時に `syncMonthlySalesToAnnualStoreForMonth()` → `annual:salesMapChanged` |
| Sales Data → MEP | **あり（同一タブ）** — Save / 変更後に `annual:salesMapChanged` → MEP が `syncMonthlySalesFromAnnualStoreForMonth()` |
| Past Sales との統合 | **なし** — 依然 `pastSalesShared` は別箱 |
| 単一 `timeline` | **なし** — P0 で新設 |
| 別タブ同期 | **弱い** — MEP は `storage` で `annualDailyShared` を未監視 |
| 副収入行 | **非対称** — Annual→MEP は主収入行のみ。MEP→Annual は合計 |
| 年跨ぎ・過去年 | **未整備** — 当年中心の同期のみ |

**結論:**

- **「Sales Data と MEP が別々の値を持ち続ける」という最悪ケースは、当年・主収入・同一タブに限れば概ね回避できている**（骨格あり）。
- **「1 次情報として完成」とは言えない。** Past Sales 分離・年跨ぎ・`timeline` 統一・別タブ・年次目標未永続化は未解決。
- **次プロンプトで P0（`KpiYearStore` + `timeline`）を実装して進めてよい。** 既存 `annualDailyShared` 同期はマイグレーション元として吸収し、最終的に Store API 1 本に置き換える。

### 14.2 Table Window / Focus Bar — 年跨ぎスクロール UX（実装要件）

- データが `timeline` 上に存在する限り、**Annual / Monthly 両方**の Table Window と Focus Bar で:
  - **縦スクロール**で日次行を連続移動（月を跨ぎ年を跨ぐ）
  - **横スクロール**で日付列を連続移動（表形式の場合）
  - 端まで達したら次の年のデータへシームレスに続く（または年境界で軽い区切り表示）
- カレンダーボタン・日付ピッカーは**ジャンプ補助**（§1.6）。
- 実装時は `KpiYearStore.readRange()` と `selectedDate` の共有が前提。

### 14.3 次プロンプトでの実装スコープ（想定）

1. `scripts/kpi_year_store.js`（または同等）— `timeline` + `years` + マイグレーション
2. Sales Data / MEP を Store API 経由に差し替え（`annualDailyShared` 互換レイヤー可）
3. `annual:salesMapChanged` 等のイベントを Store 変更にフック
4. （可能なら）Focus Bar / Table Window の `selectedDate` と Store 読み取りの接続
5. Past Sales → `timeline` マイグレーション

繁閑期%・Cockpit read-only・メモ UI は P0 の後続でも可。

---

## 15. 実装メモ（2026-06-17 — MEP 修復後・次 Phase 用）

### 15.0 データ正本の最優先（Phase より先 — 2026-06-17）

**合意:** Daily FW / Insight / Graph 等の挙動検証には **2024・2025・当年（〜今日付近）の入力済みデータ** が前提。ここが壊れると毎回復旧依頼が発生するため、**Phase 表の順序より先に** 次を満たす。

| ルール | 内容 |
|--------|------|
| **正本** | `KpiYearStore.timeline`（`dailySales` / `businessDays`） |
| **保持** | CSV / Past Sales / Sales Data / MEP Save 後は **消えない**（`persistStore` + legacy キー同期） |
| **未入力年** | 2023 以前など **timeline に ISO が無い日** → 読取面は **¥0 / $0**（`readTwSalesAmt` 等） |
| **入力済み年** | 2024 / 2025 / 2026（例: 6/30 まで）— リセット時は CSV 再アップロードで復旧 |

**2026-06-17 修復（Phase 8 の一部・先行実装）:**

- Past Sales Save が path/lease で `timeline` に書けない regression を修正（`past-sales-*` ソースは path 独立）
- `persistFromPastSales` / `persistFromAnnualDaily` 後に `syncToAnnualDaily()`
- 起動時 `reconcileTimelineFromLegacy()` — legacy キーから timeline の欠損 ISO を補完
- TW: `annual:pastSalesSaved` 等で `renderAnnualDailyTimeline` 再描画
- MEP: 年切替時 `syncMonthlySalesFromAnnualStoreForMonth()` で過去年グリッド hydrate
- **Monthly Table Window** — 客数・客単価（P/C）・組数・Expenses は **MEP Save 済みのみ反映**、未入力は `0` / `$0` / `¥0`（`scripts/monthly_tw_mep_metrics_client.py`）

### 15.1 このセッションで完了した修復

| 項目 | 内容 |
|------|------|
| MEP レイアウト | Strategy Note UI 撤回・無限ループ修正 |
| Phase 5c | トグル Monthly 時 Annual Sales Data Read-Only（`__cb` セレクタ修正） |
| MEP persist | `persistAnnualDailyShared` が `syncToAnnualDaily` で上書きする regression 修正 |
| MEP Save | 未ロード月を timeline に 0 書き込まない（**Phase 5d**） |
| CSV 辞書 | 営業日列ヘッダー拡張・`1`/`0` セル値（列がある場合のみ） |

### 15.2 報告された未修復バグ（Phase に組込済み）

#### A. Table Window — 2024 / 2025 が空（Phase 8）

**症状:** Past Sales / Sales Data へ CSV 再取込後、モーダル Input タブには反映されるが、**Annual Table Window**（Focus Bar 日次一覧）の 2024・2025 行に売上が出ない。

**想定原因（コード確認済み）:**

- Table Window（`KPI-FOCUS-TW-METRICS`）は `__ANNUAL_DATA.daily.targetSalesByDate` を全 ISO で参照。
- `syncToAnnualDaily()` は `timeline` 全体をコピーするが、**Past Sales Save 後に TW 再描画 / sync が走らない**、または **過去年 ISO が `daily` に載らない経路**が残っている可能性。
- `readTwSalesAmt(iso, smap)` が operating year 以外の `timeline` キーを拾えていないケースを要検証。

**受け入れ:**

- [ ] Past Sales Save → Annual TW で 2024/2025 日次売上が表示
- [ ] Sales Data Save → 当年 TW と一致
- [ ] `annual:pastSalesSaved` / `kpi:dailySalesChanged` 後に `renderAnnualDailyTimeline` が再実行される

#### B. Monthly Table Window — 同型（Phase 8）

**症状:** Annual と同様、過去年スクロール時に売上が空の可能性。

**検証 TODO:**

- [ ] Monthly `KPI-FOCUS-TW-METRICS` が `KpiYearStore.syncToAnnualDaily()` 後の smap を過去年含め参照しているか
- [ ] Annual TW 修正と **同一パッチ**（`scripts/focus_tw_metrics_client.py`）で直るか確認

#### C. Sales Data Analyze — Seasonality % が空（Phase 3）

**症状:** 2026 年 Sales Data › Analyze の **Seasonality %** 列・グラフが `—` のまま。

**本来の仕様（再確認）:**

1. 過去年（2024+2025）の日次が `timeline` に揃っている
2. `KpiYearStore.computeAverageSeasonalityPct(operatingYear, 2)` が各年の `observed.monthlySales` / `monthlyBizDays` から月次ベースライン vs 実績を平均
3. 算出された **平均繁閑期%** を Analyze の Seasonality % 列に表示
4. ユーザーは **繁閑期%設定** 列の ▲▼ で 5% 刻み調整し、合計 100% を目指す（`getSdmHlWeightsForYear` / `bindSdmHlCell`）

**想定原因:**

- CSV 取込後 **`years.{YYYY}.observed` が未生成**（`computeObserved` 未実行）
- `listEligiblePastYearsForBaseline` が `yearHasTimelineData` を見るが `monthlyPct` 欠落で除外
- Past Sales Save が `timeline` には書くが **Analyze 再計算イベント未発火**

**受け入れ:**

- [ ] 2024+2025 CSV 取込・Save 後、2026 Analyze の Seasonality % に 12 か月分の数値
- [ ] ▲▼ 調整・合計 100% アラートが従来どおり動作
- [ ] Past Sales Analyze タブとも数値整合

#### D. MEP — 2024 / 2025 年が空（Phase 8）

**症状:** MEP で年を 2024/2025 に切替えてもグリッドが空。

**想定原因:**

- `loadMepFromYearStore` / `syncMonthlySalesFromAnnualStoreForMonth` が **operating year 以外**の timeline を `rowValueById` に載せていない
- または `canWriteMepYear` / path ガードで past year 表示のみの経路が未実装

**受け入れ:**

- [ ] MEP で 2024/2025 を開くと Sales Data / Past Sales と同じ日次売上・営業日（**Read-Only** when path=annual / Basic）
- [ ] 当年 path=mep でも **過去年は Read-Only 表示**

### 15.3 CSV 再取込について（運用上の回答）

- **復旧用途:** 2026 年分は MEP / Sales Data から CSV 再取込 + Save で復旧可能（**5d 適用後**は未表示月の消去なし）。
- **2024/2025:** Past Sales Data から取込 + Save で `timeline` には入る想定だが、**TW / Analyze / MEP 表示は Phase 8・3 完了まで不完全**。
- 営業日列なし CSV は **売上>0=営業日** ルール（§9 / `daily_sales_import_client.py`）。

### 15.4 推奨実装順（次プロンプト）

0. **§15.0 データ正本** — timeline 保持・過去年 TW / MEP 表示（Phase 8 先行）✅
1. **Phase 3** — Seasonality% / Analyze ✅
2. **Phase 10** — Daily Floating Window KPI 配線 + **10-c** メモ印 ✅
3. **Phase 9** — Focus Bar Graph ✅
4. **Phase 11** — **曜日別日次目標 KPI**（ベースライン年選択 UI 含む）→ TW / Focus Bar（`docs/weekday-target-sales-kpi-memo.md`）
5. **Phase 2** — Cockpit 繁閑% read-only（plan 連動）

### 15.5 Focus Bar Graph ポップオーバー（Phase 9 — 2026-06-17 追記）

**方針:** 見つかった UI バグ・未配線は Phase 表に随時追加してよい（本セッション合意）。一覧を一度に書き出せなくても、気づいたタイミングで §15 に追記する。

**対象:** Annual / Monthly 両方の Focus Bar 右端 **Graph** ボタン（Monthly は `#monthly-vfocus-graph-btn`、Annual は `#annual-daily-focus-bar-graph-btn`）。ポップオーバー DOM は Monthly が Annual と **共有**（`#annual-graph-popover`）。

**データ源（正本）:** Focus Bar に **ハマっている（フォーカス中の）日付行** — Table Window / 時系列行の KPI セル。手入力上書き（現行プロトタイプ）は **本番では廃止 or デバッグ限定** とし、Store + plan 由来の実績・目標を表示する。

**モード別 KPI ラベル（ユーザー確定仕様）:**

| モード | 実績 | 目標 | 派生 |
|--------|------|------|------|
| **Daily** | Today's Sales | Today's Target Sales | Difference, Achievement |
| **Monthly** | Cumulative Actual Sales | Cumulative Target Sales | Difference, Achievement |
| **Annual** | Cumulative Actual Sales | Cumulative Target Sales | Difference, Achievement |

ドロップダウンで Daily / Monthly / Annual を切替。表示値・達成率横棒（Area1 Achievement  graph と同色ルール）は **同一フォーカス日** の TW 行から取得。

**現状（コード）:**

- Annual: ポップオーバー JS **あり**（`parseRowGroup` で TW 行 DOM を scrape）。TW が空なら Graph も空。
- Monthly: 同一ポップオーバー HTML/CSS。**JS 配線要確認**（Graph ボタン `aria-controls` は共有 panel を指す）。
- 旧仕様メモ `docs/annual-focus-bar-graph-window-spec.md` に「Target/Actual 手入力」記載 — Phase 9 で **Store 連動に更新**。

**依存・競合:**

| 関係 | 内容 |
|------|------|
| **Phase 8 後** | Graph は TW 行を読むため、過去年・当年の TW 表示修正が **先** |
| **P0 selectedDate** | フォーカス日 ↔ Graph 同期 |
| **KPI-FOCUS-TW-METRICS** | 日次/月次/年次 cumulative の算出元（`scripts/focus_tw_metrics_client.py`） |
| **Phase 3 と競合なし** | Seasonality Analyze は別サーフェス |
| **Phase 2 と競合なし** | Cockpit 繁閑% は plan 表示のみ |

**受け入れ:**

- [ ] Annual Graph: フォーカス日を変えると Daily / Monthly / Annual 各 KPI が TW と一致
- [ ] Monthly Graph: 同上（縦 Focus Bar の選択列 / 日付と TW 同期）
- [ ] 店休日（OFF）行は実績 `—`・グラフ neutral
- [ ] 2024/2025 年フォーカス時も Phase 8 完了後は Graph に実績反映
- [ ] JA / EN ラベル（Today's Sales / Cumulative Actual Sales 等）

**実装メモ:**

- 可能なら DOM scrape から **`KpiYearStore` + plan 直接計算**へ移行（TW 未描画でも Graph 更新可）。
- 共通 JS 抽出: Annual / Monthly / EN の 4 ページ重複を `scripts/focus_bar_graph_client.py` 等に寄せる。

**関連 doc:** `docs/annual-focus-bar-graph-window-spec.md` · `docs/press-release-backlog.md` §12 Daily Graph ポップアップ

### 15.7 曜日別日次目標 KPI（Phase 11 — 2026-06-27 追記）

**背景:** 旧 Excel 版は各月・各曜日で 1 日あたり目標売上を統一表示（出現回数付き）。月次 Seasonality% だけでは **月内全日同額** になり KPI/UX が弱い。

**方針:**

- **新規ページ・表 UI は作らない** — 算出結果を **Table Window / Focus Bar / Target Sales** にのみ反映。
- **ベースライン年はユーザー選択**（デフォルト直近2年）。異常年（コロナ等）はチェック外しで除外（§6 `weekday-target-sales-kpi-memo.md`）。
- 選択年の **曜日構成比平均** × **当年カレンダー出現回数** で月次 target を曜日配分。
- 正本: `timeline`（実績）+ `plan`（年次・月次 H/L%・`weekdayBaselineYears`）。日次 target は **都度再計算**（DB 前後同じ）。

**詳細:** `docs/weekday-target-sales-kpi-memo.md`（§6 ベースライン年 UI、§7 丸め、§5 Excel 簡易式）

**依存:** Phase 3・8 完了・§15.0（過去日次 Save 済み）

**将来（対象外）:** Phase 11b（月内第N週曜日）・AI — メモ §9。

### 15.6 バックログ運用（メモ）

- Phase 修正タスクを一区切りしたい心理 → **未実装・バグは Phase 表 / §15 に都度追記で OK**
- 理想は全件リスト化だが、**追いつく前提で気づき次第伝える**運用でよい
- 新規項目は Phase 番号を付与し、依存（特に Phase 8 の読取面）を §15 に 1 行書く

---

## 13. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-06-17 | 初版ドラフト（会話ベース: 年跨ぎ・正本統一・複数年平均・MEP 含む） |
| 2026-06-17 | §1.3 三本柱・全サーフェス閲覧一貫性・§8.1 メモ UX 要件を追記 |
| 2026-06-17 | §1.5–1.6 単一時系列・ナビゲーション要件。`timeline` モデルに改訂。**P0 最優先**を明記 |
| 2026-06-17 | §1.7 入力面2箇所・§14 実装直前メモ（Sales Data↔MEP 再確認・年跨ぎスクロール UX） |
| 2026-06-17 | §15 追加 — TW / Seasonality / MEP 過去年バックログ。Phase 5d / 8 / 3 表更新 |
| 2026-06-17 | **Phase 9** Focus Bar Graph ポップオーバー（§15.5）。バックログ運用 §15.6 |
| 2026-06-28 | Phase 11 §6 ベースライン年選択 UI・§7 丸め・推奨順更新（10→9→11）。Phase 3・8 ✅ |
| 2026-07-08 | Phase 9 着手・確定。Focus Bar Graph（Annual/Monthly・JA/EN）は Store KPI 連動済み。**OFF は Daily のみ** `—`/neutral。**Monthly/Annual は当日まで累計（MTD/YTD）を表示**。Graph 内 ◀▶ 日付送りはプレス/マイナー枠に退避。 |
| 2026-07-08 | Phase 10 KPI 配線を確認・docs 更新。`#daily-overlay` は `renderDailyOverlayKpis` + `__computeTwMetricsForIso` で実データ表示済み（JA/EN × Annual/Monthly）。リスナーに weekday/targetMode 同期を含む。受け入れ待ち。10-c（メモ印）は未着手。 |
| 2026-07-09 | Phase 10 受け入れ + **10-c** 完了。Focus Bar / Daily 窓 / Cockpit 日付 / Monthly 縦 Focus・日付ヘッダーにメモ点。次は Phase 11。 |

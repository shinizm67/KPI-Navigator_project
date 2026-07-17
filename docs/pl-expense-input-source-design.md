# PL / Monthly — 支出項目の入力元設計

更新日: 2026-06-10  
ステータス: **重要設計（データ組み込みフェーズの正）** — ChatGPT との作戦検討より。**描画完了後の数値入れ込み時に本ドキュメントを前提に実装する。**

> **運用メモ（合意）**  
> - どの科目を Daily 入力・どの科目を Monthly（PL）入力にするかは、**現時点では未確定**。  
> - 科目マッピングの確定と実装は、**PL 表の描画が一通り終わり数値組み込みに入る段階**で Cursor（Tars）が本ドキュメントを読み、理解・実装をリードする。  
> - 旧メモの「PL で定義 → Monthly に全部流す」単純モデルより、**本ドキュメントの入力元分離を優先**する。

関連:

- [pl-table-label-layout-memo.md](./pl-table-label-layout-memo.md) — 行ラベル・科目カタログ
- [pl-table-v1-implementation-spec.md](./pl-table-v1-implementation-spec.md) — 現行 PL 表 UI の実装状況
- [monthly-page-memo.md](./monthly-page-memo.md) — Monthly Edit
- [expense-csv-excel-import-memo.md](./expense-csv-excel-import-memo.md) — 支出（費目）CSV/Excel 取り込み設計（費目名を Excel 由来の正にする構想・列マッピング）

---

## 実装状況（2026-07 時点）— Phase A〜D 実装済み

本ドキュメントの「入力元分離」は **実装済み**（PL 表 `app/profit/pl/`）。要点:

| フェーズ | 内容 | 実装場所 |
|----------|------|----------|
| **A** | PL 表で **monthly 行のセルを編集可**（`contenteditable` + `data-pl-editable`）。daily 行は読み取り専用（`—`）。固定費は 1 月入力で **全月一括反映**（他月が空なら無確認、差異があれば確認ダイアログ、Undo 対応） | `pl_expense_detail_client.py` / `build_pl_table_page.py` |
| **B** | monthly の月次額を **営業日数で日割り**プレビュー（MEP 非書込。端数は当月最終営業日に寄せる） | `pl_monthly_allocate_client.py`（`previewMonthlyExpenseAllocation`） |
| **C** | monthly 行の日割り額を **MEP `dailyExpenses` に書込**（`kpiNavigator.kpiYearStore`）。当月・当行の既存分をクリアしてから再配分。daily 行は不変。`kpi:mepDataChanged` 発火 | `pl_monthly_allocate_client.py`（`writeMonthlyExpenseAllocationToMep`） |
| **D** | daily 行に **MEP 日次入力の月次合計を読取表示**（編集不可・`title` ツールチップで入力先を明示）。初回描画・`pl-expense-detail-rendered`・`kpi:mepDataChanged` で更新 | `pl_monthly_allocate_client.py`（`fillDailyExpenseRowsFromMep`） |

### 入力元の選択（実装の要点）

- **変動費（Expected）**: 行ごとに **日次（Monthly Edit）/ 月次（PL）を選択可**。追加時およびラベル **ダブルクリック / F2** で **統合モーダル**（科目名＋入力元）を開く。`inputStyle` / `resolvedInputStyle` を更新。
  - **デフォルト方針（2026-07-17）**: **FL 近傍のみ daily**（食材仕入れ費 / ドリンク仕入れ費 / アルバイト人件費）。光熱・通信・備品・雑費などは **monthly**。いずれもユーザーが切替可能。
- **固定費（Fixed）**: **月次固定**。統合モーダルでは科目名のみ（入力元ラジオ非表示）。
- **UX 方針（2026-07-16）**: 各行トグル不採用。ラベル編集と入力元選択を1ポップアップに統合。Don't ask again なし（毎回表示）。
- データフローは選択された入力元で一方向:
  - **monthly 行** → PL 入力 → 営業日割り → MEP `dailyExpenses`（C）
  - **daily 行** → MEP 日次入力 → PL 月次合計を読取表示（D）
- **二重入力ガード**: monthly 行は PL のセルのみ編集可、daily 行は PL 側読み取り専用（ツールチップ「MEP（月次編集）で日次入力」/ "Enter daily on Monthly Edit"）。

### ストレージキー

| キー | 用途 |
|------|------|
| `kpiNavigator.plLineCatalog` | 科目カタログ（`lineId`・ラベル・bucket・`inputStyle`/`resolvedInputStyle`・`active`） |
| `kpi-pl-expenses-v1:{year}` | PL 月次入力額（monthly 行）。キーは `lineId:month0` |
| `kpiNavigator.kpiYearStore` | MEP 日次データ。`years.{Y}.dailyExpenses[lineId][ISO]` |

### 検証スクリプト

- `verify_pl_monthly_expense_edit.py`（A） / `verify_pl_fixed_fill_all_months.py`（固定費一括）
- `verify_pl_monthly_expense_allocate.py`（B） / `verify_pl_monthly_expense_to_mep.py`（C）
- `verify_pl_daily_expense_from_mep.py`（D）

> 未実装/将来: 入力可能セル色の Daily/Monthly 意匠差別化、Adjustment の 3 行分割 UI。以下の設計節は引き続き将来指針として保持する。

> **修正（2026-07-16）**: カタログ照合（`reconcileCatalogLines`）がデフォルト行の `inputStyle` を捨ててテンプレ値に戻していた不具合を修正。ラベル操作で選んだ記述先が保存・再描画後も維持される。

> **追加（2026-07-16）**: 入力元切替時の旧データ整理を実装。`daily → monthly` で `dailyExpenses[lineId]` を削除、`monthly → daily` で `kpi-pl-expenses-v1` の当該行キーを削除（同スタイル再設定では保持）。検証 `verify_pl_input_style_cleanup.py`。

> **追加（2026-07-17）**: 行ラベル横の `DAILY` / `MONTHLY` バッジを廃止。入力可否はセル色（緑／黒）のみで示す。入力先の切替 UI は統合モーダルに残す。

> **追加（2026-07-17）**: 入力元デフォルトを FL 方針で確定（schema v7）。食材・ドリンク・アルバイト = daily／その他変動費・固定費 = monthly。旧デフォルトのままの行は schema 移行で更新。検証 `verify_pl_catalog_input_defaults.py`。

---

## 入力元の選び方（採用 UX — 統合モーダル）

**2026-07-16 再合意:** 各行トグルは不採用。  
**2026-07-16 さらに:** インラインラベル編集→別モーダルの2段は発見性が弱いため、**ラベル編集＋入力元を1枚のポップアップに統合**。Don't ask again は**この操作では不要**（毎回出す）。

> 「売上入力パス」（Annual ↔ Monthly）とは別物。あちらは日次**売上**の入力経路。本節は支出科目ごとの **Daily(MEP) ↔ Monthly(PL)**。

### 操作（正）

| タイミング | 操作 | 内容 |
|------------|------|------|
| **変動費の行追加（＋）** | 属性モーダル → **統合モーダル** | 科目名＋入力元（Daily / Monthly）を同じ画面で設定 |
| **既存行の編集・再選択** | ラベルを **ダブルクリック / F2** | 同上の統合モーダル（名前だけ／入力元だけの変更も可） |
| **固定費** | 同上 | 科目名のみ（入力元ラジオは非表示・月次固定） |

- モーダル ID: `pl-expense-label-edit-modal`（Don't ask again なし）
- 切替は `inputStyle` / `resolvedInputStyle` 更新 → 再描画で緑/黒が入替
- 旧データは切替時に**消さず保持**（掃除は別タスク）

### 不採用（記録）

- ~~変動費の該当行にインライン・ピル型トグル~~
- ~~インライン contentEditable ラベル編集のあと、別モーダルで入力元だけ聞く2段UX~~
- ~~統合モーダル内の Don't ask again~~（毎回出す前提）

---

## 要旨

**支出項目ごとに「入力元」を固定する。**  
同じ費目を日次（Monthly Edit）と月次（PL）の両方で入力可能にすると、**二重計上が必ず起きる**。

したがって:

1. 項目ごとに **日次集計型** か **月次直接入力型** のどちらかを選ぶ
2. 日次集計と請求書のズレは **上書きではなく調整額** で吸収する
3. UI 上で **入力元を明示** する（**緑＝編集可／黒＝閲覧** が主。行バッジは廃止。詳細は科目編集モーダル）

---

## 問題：二重入力の例（食材費）

| 経路 | 内容 |
|------|------|
| 日次入力を合算して PL へ反映 | Monthly で日々入力 → 月次合計 |
| 月次請求書の金額を PL へ直接入力 | PL で請求書ベースの金額を入力 |

**両方を同時に有効にすると危険。** どちらか一方に決める必要がある。

---

## 入力方式 1 — 日次集計型（Daily Aggregate）

### 向いている項目

- 食材仕入れ
- ドリンク仕入れ
- 消耗品
- 日払い人件費
- 配送料
- 小口現金支出

### 挙動

- Monthly Edit で日々入力した金額を **合算** し、PL の該当行へ **自動反映**
- PL 側は **基本的に編集不可**（元データは日次）

### 表示例

```
食材仕入れ
Input Source: Daily Entries
May Total: ¥428,000
```

### Pro プランの価値

日次で次まで見られる:

- Daily Sales
- Daily Food Cost
- Daily Drink Cost
- Daily FL Cost

月末に自動集計:

- Monthly Food Cost / Monthly Drink Cost
- Food Cost Ratio / Drink Cost Ratio

---

## 入力方式 2 — 月次直接入力型（Monthly Manual）

### 向いている項目

- 電気代・ガス代・水道代
- 家賃
- 保険料・社会保険料・雇用保険
- 税理士報酬
- システム利用料
- **月末に届く請求書** で確定する費目全般

### 挙動

- PL へ **月次単位で直接入力**
- Monthly Edit からは **流入しない**

### 表示例

```
Electricity
Input Source: Monthly Entry
May: ¥86,400
```

---

## 日次合計と請求書のズレ — 調整額

食材費・ドリンク費は日次合算が自然だが、実際の請求書金額と日次合計はズレることがある。

| 要因の例 |
|----------|
| 返品・値引き |
| 掛仕入れ・月跨ぎ |
| 送料・消費税 |
| 締め日の違い |

### 推奨：上書きではなく調整額

```
Daily Entries Total       ¥428,000
Monthly Adjustment         -¥8,000
PL Amount                 ¥420,000
```

日次入力を捨てず、請求書と整合できる。

---

## 推奨データモデル（項目マスタ）

PL 項目ごとに以下を持つ。

| フィールド | 説明 |
|------------|------|
| `Item Name` | 表示名 |
| `Category` | 固定費 / 変動費 等 |
| `Input Method` | 下記 3 種のいずれか |
| `Adjustment Allowed` | 調整額を許すか |

### Input Method（3 種で十分）

| 値 | 意味 |
|----|------|
| `Daily Aggregate` | 日次合算のみ。PL は読み取り専用 |
| `Monthly Manual` | PL で月次直接入力 |
| `Daily Aggregate + Adjustment` | 日次合算 ＋ PL で調整額 |

### 設定例

| 項目 | Input Method |
|------|----------------|
| Food Cost | Daily Aggregate + Adjustment |
| Drink Cost | Daily Aggregate + Adjustment |
| Variable Labor | Daily Aggregate + Adjustment |
| Electricity | Monthly Manual |
| Supplies / Misc | Monthly Manual |
| Rent | Monthly Manual |
| Employment Insurance | Monthly Manual |

---

## UI — 入力元の可視化

**採用（2026-07-17）**: 行ごとの `DAILY` / `MONTHLY` バッジは **出さない**。

| 信号 | 意味 |
|------|------|
| **緑行** | この画面（PL）で編集可 = Monthly 入力 |
| **黒行** | 閲覧のみ（日次は MEP。調整額はダブルクリック / F2） |
| **科目編集モーダル** | 変動費の入力先（Daily / Monthly）を選ぶ場所 |

旧案の常時バッジ／アイコンは情報過多になりやすいため不採用（緑／黒で足りる）。

---

## UI — 入力可能セルの色分け（必須 UX）

**「ここにしか入力できない」** を色で示す。行バッジは使わず、**セル／行自体の見た目**で区別する。

### 原則

| ルール | 内容 |
|--------|------|
| 入力元は 1 箇所 | 日次集計型 → **Monthly Edit のセルだけ**編集可。PL は読み取り専用（調整額セルを除く） |
| 月次直接入力型 → **PL のセルだけ**編集可。Monthly Edit には出さない or 非活性 |
| 集計・合計行 | どちらの画面も **編集不可**（色なし / ロック表示） |
| 誤タップ防止 | 編集不可セルは `contenteditable` もフォーカスリングも付けない |

### セル種別と色（案 — 実装時に Sci-Fi / Office 両テーマで調整）

| 種別 | 画面 | 意味 | 見た目（案） |
|------|------|------|--------------|
| `input-daily` | Monthly Edit | 日次で入力するセル | 編集可背景（例: シアン系の薄いハイライト） |
| `input-monthly` | PL 表 | 月次請求書・領収書を入力するセル | 編集可背景（例: 別系統のハイライト — Daily と混同しない） |
| `input-adjustment` | PL 表 | 日次合計に対する月次調整額 | 調整用の第三色（小さめ列 or サブ行でも可） |
| `computed` | 両方 | 自動集計・参照のみ | デフォルト背景、カーソル `default` |
| `locked` | 両方 | 合計行・KPI 行など | やや暗い固定背景 |

### データ属性（実装メモ）

セル生成時に科目マスタから付与する想定:

```html
<td class="pl-amt-cell pl-cell--monthly" data-input-method="monthly-manual" …>
<td class="pl-amt-cell pl-cell--computed" data-input-method="daily-aggregate" …>
```

Monthly Edit 側も同様に `data-input-method` を揃え、**ストア書き込みは許可された種別のセルだけ**にする。

### フェーズ

| フェーズ | 内容 |
|----------|------|
| **現在** | PL 表の **レイアウト描画**（枠・ラベル・ダミー数値）。全セル同色でよい |
| **次** | 科目マスタ + Input Method 確定 → **色付き入力セル** + ストア連携 + 二重入力ガード |

---

## PL は「領収書・請求書の入力場所」でもある

PL を単なる集計画面にせず、**月次請求書・領収書の入力場所** として使う。

### 将来持たせたい情報

- 金額
- 支払日
- 対象月
- 取引先
- メモ
- 添付ファイル
- 支払済 / 未払い
- 日次集計由来か月次入力由来か

### MVP で十分な項目

- Amount
- Payment Date
- Memo

---

## 月跨ぎ — Target Month と Payment Date

光熱費・保険料は **請求月 ≠ 使用月** になりやすい。

| フィールド | 例 |
|------------|-----|
| `Target Month` | May（PL に載せる月） |
| `Payment Date` | June 20（実際の支払日） |

例: 6 月に支払った 5 月分電気代 → **5 月 PL** に反映。

---

## 画面の役割分担（現実的な分割）

### Monthly Edit — 日次で把握する価値がある項目

- 売上
- 食材仕入れ
- ドリンク仕入れ
- 日次人件費
- 消耗品
- 小口経費

### PL 表 — 月次でしか確定しない項目

- 家賃
- 光熱費
- 保険料・社会保険・雇用保険
- システム料
- 税理士費用
- **月次調整額**（日次集計型のズレ吸収）

### 自動反映

Monthly の日次合算 → PL の該当項目（`Daily Aggregate` 系）へ流入。

---

## 設計原則（まとめ）

1. **同じ支出を二度入力させない**
2. **入力元を 1 つに決める**（項目マスタで固定）
3. **ズレは調整額で吸収する**（日次を捨てない）

支出管理は一律に扱わず:

- **日次管理向きの費用** → Monthly Edit
- **月次確定向きの費用** → PL 直接入力

に分ける。ここが整理できれば Monthly と PL の役割が明確になる。

---

## 行の追加・削除（カタログ UX）

ChatGPT メモ・ユーザー合意:

| 操作 | 挙動 |
|------|------|
| **＋ 行追加** | 新 `lineId` を発行しカタログに追加。表示順は `sortOrder` |
| **− 行削除** | **物理削除しない**。`active: false` で **非表示** — UI からは見えないがストレージ・過去月の数値は残る |
| **ラベル編集** | **ダブルクリック / F2**（鉛筆アイコンは使わない — 幅を取らない）。`lineId` は不変 |

理由: 過去データとの整合・デバッグ・将来の再表示のため。**目にうるさい行を消す＝見えなくするだけ**。

詳細フィールド: [pl-table-label-layout-memo.md](./pl-table-label-layout-memo.md) § 行の非表示（ソフト削除）

---

## ユーザー追加科目と入力元の確認 UI（実装済み — § 実装状況 参照）

**背景**: テンプレにない費目をユーザーが PL 表で追加するケースを想定する。追加した行は **Monthly Edit にも自動反映**し、**表示順（`sortOrder`）も PL と一致**させる。

**現時点の想定（要精査・未確定）**

| 領域 | PL ↔ Monthly の関係 |
|------|---------------------|
| **支出明細** | PL で行追加 → Monthly Edit（Fixed / Expected）へ同期。**どちらで数値入力するか**をユーザーに選ばせる |
| **収入** | 日次入力が前提。どこから入力しても PL に反映するだけ（詳細は別途精査） |

### 新規行・ラベル編集の統合ポップアップ（正）

PL 表で **＋** により行を追加したあと、または既存ラベルを **ダブルクリック / F2** したとき、**1枚のモーダル**（`pl-expense-label-edit-modal`）を表示する。

| 要素 | 変動費 | 固定費 |
|------|--------|--------|
| 科目名 | ○ | ○ |
| 入力元（Daily / Monthly） | ○ | 非表示（月次固定） |
| Don't ask again | **なし**（毎回表示） | **なし** |

| ルール | 内容 |
|--------|------|
| **名前だけ変更** | 入力元ラジオはそのままで決定すればよい |
| **入力元だけ変更** | 科目名はそのままでラジオだけ変えて決定 |
| **ストア** | `lineId` ごとに `inputStyle` / `resolvedInputStyle` を保持 |

### 同期の原則

1. PL 表が **科目マスタの正**（`lineId`・ラベル・Fixed/Expected・順序）
2. Monthly Edit は PL カタログから **支出明細のみ**読み込み（収入は別ルール）
3. 入力元が Daily の行 → Monthly で日次入力、PL は集計表示（編集不可）
4. 入力元が Monthly の行 → PL で月次直接入力、Monthly Edit には数値行を出さない（またはグレーアウト）

> **ステータス**: 統合モーダルによる支出明細の入力元選択は **実装済み**（§ 入力元の選び方）。収入側の細部は引き続き精査。

---

## 未決事項・実装時の検討

**データ組み込みフェーズ開始時に Tars が本節を起点に確定・実装する。**

- [x] **科目ごとの Input Method 一覧**（Daily / Monthly）— `fnb` デフォルトは `pl_line_catalog.py`（schema v7）。**FL 近傍のみ daily**、他は monthly。固定費は monthly 固定、変動費は行ごとに選択可
- [x] 科目マスタ UI（**ダブルクリック / F2** → 統合モーダル）と入力元選択
- [x] Monthly Edit の行表示 — PL で monthly の項目は MEP 側非活性（daily 行のみ MEP 入力）
- [x] **ユーザー追加科目の入力元確認** — 統合モーダルに統合
- [ ] **入力可能セルの色** — Sci-Fi / Office パレット、Daily vs Monthly の判別（monthly 編集可セルは色分け済、Daily/Monthly の意匠差別化は残）
- [x] **`Daily Aggregate + Adjustment`（最小版・2026-07-16）** — モーダルで調整額。3 行構成 UI は将来
- [x] **入力元切替時の旧データ整理** — monthly↔daily 切替で使わなくなる側を掃除（調整額も daily→monthly 時に削除）
- [ ] 既存 `kpi-pl-expenses-v1` ストアとのマイグレーション
- [ ] Basic / Pro で日次 FL 系 KPI の出し分け

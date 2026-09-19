# Planning Readiness / KPI Setup Status

ステータス: **正式仕様 / runtime 実装済み（2026-09-19）**  
記録日: 2026-09-19  
実装: `js/kpi-planning-readiness.js` · `scripts/planning_readiness_lib.py` · Annual/Monthly hosts  
関連: [`target-sales-daily-monthly-annual.md`](./target-sales-daily-monthly-annual.md) · [`display-vs-operating-year.md`](./display-vs-operating-year.md) · [`weekday-target-sales-kpi-memo.md`](./weekday-target-sales-kpi-memo.md)

---

## 1. 名称

| 層 | 名称 |
|----|------|
| Internal concept | **Planning Readiness** |
| User-facing (EN) | **KPI Setup Status** |
| User-facing (JP) | **KPI設定状況** |

---

## 2. 目的

「計算可能な目標値」と「ユーザーが確認済みで信頼できる目標値」を分離する。

**重要原則:**

> 数字が表示される ≠ ユーザーが確認済みで信用できる数字

KPN のデータ層は次のように分離する。

```
Plan
  Annual Target
  + Business Days（確認済み）
  + Seasonality（確認済み）
  ↓
  Daily Target

Actual
  Daily Sales
  ↓
  Difference / Achievement
```

Actual Sales は Planning Readiness の Ready 条件に **含めない**。  
Actual は Difference / Achievement 等の実績比較にのみ使用する。

---

## 3. Plan layer（Readiness 対象）

Planning Readiness の対象は次の 3 つだけである。

1. **Annual Target**（年次目標売上）
2. **Business Days confirmation**（営業日設定の確定）
3. **Monthly seasonality confirmation**（月次繁閑／月次配分の確定）

Actual layer（Daily Sales）は Ready 判定に使わない。

---

## 4. State model

| State | 意味 |
|-------|------|
| **NOT_READY** | 年次目標売上そのものがない等。有効な日次目標を構成できない |
| **PROVISIONAL** | 日次目標は計算可能。ただし必須設定のユーザー確認が未完了 |
| **READY** | 必須 Planning 設定がすべて確認済み（`confirmed`） |

---

## 5. Annual Target

- 年次目標売上が存在すること。
- **売上実績入力は条件にしない。**

年次目標が無い場合は `NOT_READY`（日次目標を構成できない）。

---

## 6. Business Days（営業日設定）

### 6.1 正式操作

「**営業日設定を確定**」操作を正式採用する。

### 6.2 禁止する判定

営業日数を値から推測して Ready 判定してはならない。

理由: 全日営業が本当に正しい店舗と、まだ休日設定をしていない店舗を、データだけでは区別できない。

### 6.3 状態例

| 操作 | 状態 |
|------|------|
| 未訪問 | unconfirmed |
| ページ訪問のみ | unconfirmed |
| 編集したが確定していない | unconfirmed |
| 「営業日設定を確定」 | **confirmed** |
| confirmed 後に営業日を変更 | **confirmed 解除**（再度確定が必要） |

### 6.4 365 日営業の確認導線

全日営業の場合も、推測で Ready にせず確認を取る。

例文:

> 年間365日すべて営業日として設定されています。  
> この設定でよろしいですか？

操作:

- [このまま確定]
- [営業日を編集]

---

## 7. Monthly Seasonality（月次繁閑／月次配分）

### 7.1 デフォルト想定（runtime 正本）

実装開始時にコードから固定した正式 contract:

| 項目 | 正本 |
|------|------|
| 保存キー | `years[YYYY].plan.monthlyHlWeights`（長さ 12） |
| デフォルト seed | `[85, 85, 100, 110, 120, 85, 100, 100, 100, 110, 110, 115]`（**全月 100% ではない**） |
| 構造 valid | 各値整数・60–200・5% 刻み（`normalizeHlWeights`） |
| 配分 UI OK | 12 か月の **平均 ≈ 100%**（`|(sum/12)−100| < 0.01`） |
| Auto-adjust | **なし**（平均≠100 でも保存は可能。確定時は下記） |

確定ルール:

- デフォルト seed（または全月 100%）のまま「このまま確定」→ 構造 valid なら可
- ユーザーが調整した場合 → **平均 ≈ 100%** を満たさない限り確定不可

形式的に有効でも、ユーザー未確認なら **confirmed にしない**。

### 7.2 提示例

> 月次配分は現在デフォルト設定です。  
> この設定を使用しますか？

操作:

- [このまま確定]
- [調整する]

### 7.3 調整時

ユーザーが調整した場合は、現在の正式な繁閑係数 contract に従う。

**Product decision:** 月次繁閑係数をユーザーが調整した場合、最終的な配分条件が正しく成立していることを confirmed 条件にする。

調整後の最終係数が正式な必要条件を満たしていない場合は **確定不可**。

### 7.4 実装時の固定結果

§7.1 に runtime 正本を記録済み。Login Reminder は初回実装では **DEFERRED**（page-entry alert まで）。

---

## 8. visited / edited / confirmed

各設定について、必要に応じて内部的に次を管理してよい。

| フラグ | 意味 |
|--------|------|
| `visited` | ページに行った |
| `edited` | 一度触った／編集した |
| `confirmed` | ユーザーが確定操作をした |

**Ready 判定の最終条件は `confirmed` のみ。**

「ページに行っただけ」「一度触っただけ」では Ready にしない。

---

## 9. Provisional Target UI

Planning 未確定（`PROVISIONAL`）でも、日次目標値は消さない。  
計算可能なら表示する。

ただし「信頼済みの正式値」と誤認させない。

### 9.1 Warning 表現

- 赤〜赤橙系
- 真っ赤な error 色は避ける
- 背景または border 中心
- error ではなく **warning / provisional**
- Ready になったら通常色へ戻す

### 9.2 Tooltip 方針

セル内に「暫定値」という **常時テキストを入れない。**

理由: UI 密度を壊す。Annual / Monthly で大量反復すると UX が悪化する。

| 面 | 方針 |
|----|------|
| **Annual** | 日次目標列は warning 色。Tooltip は原則 Focus Bar の目標売上セルを主対象。ページ進入時に未確定 Alert Floating |
| **Monthly** | 目標売上行は warning 色。Tooltip は原則 Focus Bar の目標売上セルを主対象。ページ進入時に未確定 Alert Floating |
| **Floating Windows** | 目標売上の font / border 等を warning 色。hover 時 Tooltip 可。FW は情報密度が低いため対象を広げてもよい |

Tooltip 例:

```
暫定目標値
KPI設定が完了していないため、
この目標値は暫定計算です。

未確定:
営業日設定
月次配分
```

---

## 10. Page Entry Alert / Confirm Action FW

Planning 未確定状態で Annual / Monthly 等の対象ページへ入った場合、Floating Alert を出す。

例:

> KPI設定に未確定項目があります。  
> 現在表示している目標値は暫定値です。

**確定操作は Alert FW 内にのみ置く（Sales Data 常設ボタンは置かない）。**

- 未確定項目だけセクション表示（営業日設定 / 月次配分）
- 各セクション: `[確定]` + `[編集する|調整する]`
- 確定後は Alert FW を再描画。未確定が 0 なら完了メッセージ後に閉じる
- signature mismatch で confirmed が解除された項目だけ、次回表示時に再出現
- 同一 page/session で連発しない（閉じたあとはページ離脱後に再表示可）
- READY なら表示しない

---

## 11. Login Reminder

ログイン時に時々表示する。

例:

> 〇〇様、おかえりなさい。  
> 今年のKPI設定をご確認ください。
>
> ・年次目標売上  
> ・営業日設定  
> ・月次配分  

各設定ページへのリンクを付ける。

checkbox: **「次回から表示しない」**

ただし **永久 disable ではない。**

内部仕様: 現在の状態について reminder を抑制するだけ。  
設定が変更され Planning Readiness が再び未確定になった場合は reminder 再表示可能。

---

## 12. 実装メモ

- Ready 状態は **`operatingYear`** 基準（displayYear と混同しない。[`display-vs-operating-year.md`](./display-vs-operating-year.md)）
- 永続化: `years[YYYY].planningReadiness`（signature 方式）
- Login Reminder: 初回は page-entry alert のみ（壊さない範囲で DEFERRED）

---

## 13. 決定サマリ（クイック参照）

| 決定 | 内容 |
|------|------|
| Actual Sales | Ready 条件に含めない |
| Plan 3 条件 | Annual Target / Business Days 確定 / Seasonality 確定 |
| Ready の最終条件 | `confirmed` のみ（visited / edited では不足） |
| 営業日 | 値推測禁止。「確定」操作必須。365 日も確認ダイアログ |
| 繁閑デフォルト | 全月 100% 想定。未確認なら confirmed にしない |
| 暫定目標 | 消さない。warning 色（暖色背景+濃オレンジ文字）+ Focus Bar Tooltip / Alert。セル内常時「暫定値」テキスト禁止 |
| 確定 UI | Alert FW のみ。Sales Data 常設確定ボタンなし |
| Reminder | 「次回から表示しない」は状態紐付け抑制。永久 disable ではない（Login Reminder は DEFERRED） |

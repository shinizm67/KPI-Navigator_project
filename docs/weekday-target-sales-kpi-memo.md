# 曜日別日次目標 KPI — 設計メモ（2026-06-27、§6・§13 追記 2026-06-28）

## 1. 位置づけ（なぜ大事か）

KPI Navigator のコアは **「目標売上（Target Sales）」を日次・月次・年次で一貫させ、TW / Focus Bar / Graph で実績と比較すること** である（`docs/target-sales-daily-monthly-annual.md`）。

**月次繁閑期%（Seasonality / H/L Season%）だけでは不十分** な理由:

- 月次目標が決まっても、**月内の全日に同じ日次目標** を配ると、月曜・金曜・土曜が同額になり KPI / UX として弱い。
- 旧 Excel 版では **各月 × 各曜日** で 1 日あたりの目標売上を揃え、営業日数（出現回数）とセットで見せていた。
- 根拠のある計算式から配分するため、ユーザーは「なぜこの曜日はこの目標か」を信頼できる。

**本機能は KPI 品質の要**。Phase 3（月次 Seasonality%）・過去データ正本（timeline）の上に載る **日次目標の最終配分レイヤ** として扱う。

---

## 2. 旧 Excel での見え方（参考・数値は例）

各月について、曜日ごとに **同じ 1 日目標** と **その月の出現回数** を表示していた（例: 1 月・適当な数値）:

| 曜日 | 1 日あたり目標 | 出現回数 |
|------|----------------|----------|
| 月曜 | $1,234 | 4 回 |
| 火曜 | $1,343 | 4 回 |
| 水曜 | $2,351 | 4 回 |
| 木曜 | $2,545 | 4 回 |
| 金曜 | $3,134 | 5 回 |
| 土曜 | $789 | 5 回 |
| 日曜 | $0 | 5 回 |

- **同一月内の同じ曜日はすべて同じ目標売上**（カレンダー上の 1/6 月曜も 1/13 月曜も同額）。
- 月次売上目標を 100% とし、**曜日構成比 × 出現回数** で再配分し、**月次合計を超えない** ようにする。

---

## 3. 実装方針（今回スコープ / 非スコープ）

### やること

| 項目 | 内容 |
|------|------|
| **計算のみ** | 過去実績（timeline）と当年 plan（年次・月次繁閑%）から **日次目標売上を算出** |
| **反映先** | **Table Window**・**Focus Bar**・各 **Target Sales** 表示（Daily / Monthly / Annual の読取面） |
| **データ源** | `KpiYearStore.timeline` の過去年日次 + `years.{YYYY}.plan`（月次 H/L %・年次 target） |
| **過去年本数** | **ユーザーが選んだベースライン年** の平均（デフォルトは直近 2 年。§6 参照） |

### やらないこと

| 項目 | 理由 |
|------|------|
| **新規ページ・専用表 UI** | ユーザーは TW / Focus Bar で十分。計算結果の「見せ場」は既存読取面 |
| **日別バラつき（同一曜日内で日ごとに異なる目標）** | Phase 11 では対象外。§13（Phase 11b）・§8（AI）で将来検討 |
| **AI・外部イベント・自動メモ** | 将来構想。本リリース対象外 |
| **実績の再入力** | 目標算出のみ。実績は既存 timeline / MEP 経路のまま |

### DB との関係

- **DB 移行（Phase 7）前でも可** — 正本は `timeline` + `plan`（localStorage 上の `KpiYearStore`）。
- DB 後は **同じ算出関数** を Store API 越しに呼び、永続するのは入力データのみ。**日次目標は都度再計算**（キャッシュは任意）。

---

## 4. 算出フロー（高レベル）

```
過去年日次実績（timeline）
    ↓ 月×曜日集計
前年月別・曜日別構成比
    ↓ × 当年該当月の曜日出現回数（営業日ベース）
当年月別・曜日別配分率
    ↓ × 当年月次目標売上（Seasonality% 適用後）
当年月別・曜日別売上目標
    ↓ ÷ 出現回数
当年月別・曜日別 1 日 KPI  ← TW / Focus Bar の各日 Target Sales に展開
```

**制約:** 各月について、全曜日の `(1日 KPI × 営業日数)` の合計 ＝ **その月の月次目標売上**（年次目標超過なし）。

---

## 5. 計算式（詳細）

対象: **当年（operating year）の各月 `m`**、各曜日 `dow`（0=日 … 6=土。実装は ISO / locale 規約に合わせる）。

### 記号

| 記号 | 意味 |
|------|------|
| `Y` | 当年（例: 2026） |
| `PastYears` | 過去ベースライン年（例: `{2024, 2025}`。最大 2 年・平均） |
| `Sales(y, m, dow)` | 年 `y`・月 `m`・曜日 `dow` の **営業日のみ** の売上合計 |
| `MonthSales(y, m)` | 年 `y`・月 `m` の **営業日のみ** の売上合計 |
| `Count(Y, m, dow)` | 年 `Y`・月 `m` に存在する曜日 `dow` の **営業日数** |
| `MonthlyTarget(Y, m)` | 当年月次目標売上（年次 target × 月次繁閑% 等。Phase 3 / plan 由来） |

### ステップ（過去 1 年分。複数年は §6）

1. **前年月間売上**  
   `MonthSales(y, m)` ＝ 前年該当月の売上合計（営業日のみ）

2. **前年月別曜日売上**  
   `Sales(y, m, dow)` ＝ 前年該当月・該当曜日の売上合計

3. **前年月別曜日構成比**  
   `Share(y, m, dow)` ＝ `Sales(y, m, dow) ÷ MonthSales(y, m)`  
   （`MonthSales` が 0 の月は除外 or 均等フォールバック — 実装時に §7 参照）

4. **今年月別曜日出現回数**  
   `Count(Y, m, dow)` ＝ 当年該当月の **営業日** として数えた該当曜日数

5. **今年月別曜日配分ウェイト**  
   `Weight(Y, m, dow)` ＝ `Share(y, m, dow) × Count(Y, m, dow)`

6. **今年月別曜日配分率**  
   `Rate(Y, m, dow)` ＝ `Weight(Y, m, dow) ÷ Σ_dow Weight(Y, m, dow)`

7. **今年月別曜日売上目標**  
   `DowMonthTarget(Y, m, dow)` ＝ `MonthlyTarget(Y, m) × Rate(Y, m, dow)`

8. **今年月別曜日 1 日あたり KPI**  
   `DailyKpi(Y, m, dow)` ＝ `DowMonthTarget(Y, m, dow) ÷ Count(Y, m, dow)`  
   （`Count` が 0 の曜日は 0 または非営業扱い）

### Excel 版同等の簡易式（実装の正 — 2026-06-28 合意）

旧 Excel・ユーザー手計算と同じ形。`ShareAvg` は §6 のベースライン年平均。

```text
MonthlyTarget(Y, m) ＝ 当年月次目標（年次 target → 日次平均 → × 当月営業日数 → × 月次繁閑%）
加重比率 ShareAvg(m, dow) ＝ 過去ベースライン年の「その月・その曜日売上合計 ÷ その月売上合計」の平均（%）
DailyKpi(Y, m, dow) ＝ MonthlyTarget(Y, m) × ShareAvg(m, dow) ÷ Count(Y, m, dow)
```

**月次一致の証明:** `ShareAvg` を月内で合計 100% に正規化していれば  
`Σ_dow DailyKpi × Count(Y,m,dow) ＝ MonthlyTarget(Y,m)`。

§5 ステップ 5〜6 の `Weight / Rate` 再正規化は、当年の曜日出現回数が過去と大きくずれた年向けの代替式。**Phase 11 の第一実装は上記簡易式を正とする。**

### 日次への展開

カレンダー日 `iso` の曜日が `dow` かつ **営業日** なら:

```text
targetSales(iso) = DailyKpi(Y, month(iso), dow)
```

**非営業日** は `0`（TW / Focus Bar の off 行と一致）。

---

## 6. ベースライン年の選択（UI・永続化）

### 6.1 方針（なぜ前年1本足ではないか）

- **前年だけ**だと、コロナ・改装・災害など **異常年** が加重比率を歪める。
- 本質は **「通常営業が続いた年」の実績を血と肉にして** 当年目標に載せること。
- Phase 3（月次 Seasonality%）と同型だが、曜日配分は **年の集合をユーザーが選べる** ことを必須とする。

### 6.2 デフォルト動作

| 項目 | ルール |
|------|--------|
| **初期選択** | `operatingYear` の直前から最大 **2 年**（Phase 3 と同じ。例: 2026 向け → 2024, 2025） |
| **対象年の条件** | `timeline` に当該年の日次売上が **1件以上** Save 済み |
| **平均の取り方** | 選択年ごとに `Share(y,m,dow)` を算出し、**算術平均** → `ShareAvg(m,dow)` |
| **データなし月** | その年・その月は平均から **除外**（0 で足さない）。全選択年で欠損なら §7 フォールバック |

自動で「異常年を検出して除外」は **しない**（店舗ごとに定義が違うため）。ユーザーが外す。

### 6.3 UI 置き場（案）

**第一候補: Sales Data › Analyze**（Seasonality %・H/L と並ぶ「目標算出の設定」帯）

| UI 要素 | 内容 |
|---------|------|
| **見出し** | 「曜日配分のベースライン年」/ EN: *Weekday baseline years* |
| **年チェックリスト** | `operatingYear - 1` から遡り **最大 5 年** 程度を列挙（データがある年のみ活性） |
| **各年の行** | チェックボックス ＋ 年ラベル ＋ 補足（例: 「日次 312 日入力済み」/ 「データなし」で disabled） |
| **デフォルト** | 直近 2 年にチェック |
| **リセット** | 「直近2年に戻す」リンク |
| **注意文** | 「異常な売上の年（休業・改装等）はチェックを外してください」 |

**第二候補（将来）:** Annual コックピット › 目標売上エリアの歯車メニュー — Analyze と **同一 Store キー**を編集。

**新規フルページは作らない。** チェックリスト 1 ブロック ＋ 既存 Analyze 再描画で足りる。

### 6.4 永続化（Store）

```javascript
// years.{operatingYear}.plan.weekdayBaselineYears: number[]
// 例: [2024, 2025]
// 未設定時 → getDefaultWeekdayBaselineYears(operatingYear) === [Y-1, Y-2]（存在する年のみ）
```

| API（案） | 役割 |
|-----------|------|
| `readWeekdayBaselineYears(Y)` | 保存済み or デフォルトを返す |
| `writeWeekdayBaselineYears(Y, years[], meta)` | チェック変更時 Save。`meta.source: 'sales-data-analyze'` |
| `computeWeekdayShareAvg(Y, m, dow)` | 選択年から `ShareAvg` を算出（内部キャッシュ可） |

`kpi:annualPlanChanged` または専用 `kpi:weekdayBaselineChanged` で TW / Focus Bar を再描画。

### 6.5 バリデーション

| ケース | UI / 算出 |
|--------|-----------|
| 0 年選択 | Save 不可。トースト「1年以上選んでください」 |
| 1 年のみ | 平均 ＝ その年1本（許可） |
| 選択年に当該月の実績なし | その年はその月の平均から除外 |
| 全年・全月欠損 | §7「均等配分」フォールバック ＋ Analyze に警告バッジ |

### 6.6 Phase 3 との関係

| 項目 | 月次 Seasonality%（Phase 3） | 曜日加重比率（Phase 11） |
|------|------------------------------|---------------------------|
| デフォルト年 | 直近 2 年 | **同じデフォルト** |
| 年の選択 UI | 現状は固定2年（将来共通化可） | **Phase 11 で選択 UI を導入** |
| 共通化案 | `plan.baselineYears` を両方で参照し、Analyze で一括編集（Phase 11b 以降でも可） |

第一実装では `weekdayBaselineYears` を独立キーにし、後から Seasonality とマージしてもよい。

---

## 7. 丸め・月次一致（表示ルール）

### 7.1 計算中

- **内部は倍精度の小数のまま**最後まで計算する（加重比率・日次目標とも）。
- 過去の「曜日発生回数の平均」を小数にする必要は **ない**。回数は **当年カレンダーの整数** のみ使用。平均するのは **構成比（%）** だけ。

### 7.2 画面表示（TW / Focus Bar / Daily FW）

- 通貨表示はアプリ共通（`fmtMoney`）。**円・ドルとも整数表示**（既存ルールに従う）。
- 各日の Target Sales は表示用に丸める（四捨五入をデフォルト案とする）。

### 7.3 月次合計のずれ（端数調整）

表示丸め後、  
`Σ（営業日の表示目標）≠ MonthlyTarget` となりうる。

**方針（推奨）:**

1. 営業日ごとに `DailyKpi` を小数で保持  
2. 表示用に丸めた値をセルに出す  
3. **その月の最後の営業日**（または ISO 最大の営業日）に  
   `MonthlyTarget − Σ(それ以前の表示目標)` の **差分を加算**して月次を一致させる  
4. 差分が 0 の月は調整なし

Analyze / デバッグ用に「調整日」を `data-adjusted="1"` 等でマークしてもよい（UI 非表示で可）。

---

## 8. エッジケース（実装時メモ）

| ケース | 方針案 |
|--------|--------|
| 過去月に実績なし | その月は **均等配分**（7 曜日同 Rate）または Seasonality のみで月次 target を均等日割 — 要 UX 確認 |
| 某曜日のみ Count=0 | `DailyKpi` 未定義。他曜日の Rate 再正規化 |
| 年次 target 未設定 | 日次 target は `—` / 0。Cockpit 誘導 |
| 月次 H/L % 未調整（≠100% 平均） | Phase 3 の Allocated Total 警告と同様。算出は plan 保存値を正とする |
| 営業日定義 | Store の `businessDays` / `isCalendarBusinessDay` と **同一**（Sales Data・MEP と一致） |
| 休日・店休 | 営業日でなければ target=0。曜日 KPI は営業日 Count のみ |

---

## 9. 将来（本リリース対象外 — Phase 11 以降）

### 9.1 AI・外部データ

- **AI 解析:** 同一曜日内の日別差（イベント・天候・近隣動向）を反映した target 提案。
- **自動メモ:** 可能性・根拠のテキストを Insight / Daily Notes に書き込む。
- **ネットイベント取得:** 外部 API 連携。

### 9.2 Phase 11b — 月内「第 N 週の曜日」配分（任意・難易度高）

**動機:** 同一月内の「1 回目の月曜」と「4 回目の月曜」で実績が違う。Phase 11 では同じ月曜は同額だが、より現実的にする拡張。

**案:**

1. Phase 11 で求めた **その月・その曜日の月間目標合計** `DowMonthTarget(Y,m,dow)` を確定  
2. 過去ベースライン年から **「その月の第 k 回目のその曜日」** ごとに売上を集計（k = 1, 2, 3, 4 …）  
3. 第 k 回目の構成比を平均し、当年その月の第 k 回目の営業日に配分  
4. データが薄い k は **均等割り** にフォールバック  

AI なしでも「過去の順位パターンに基づく配分」として説明可能。実装は Phase 11 完了後に判断。

現行 Phase 11 は **統計的な曜日構成比 + 当年カレンダー補正** まで。Excel 版と同等の信頼性を Web 上で再現するのがゴール。

---

## 10. 読取面への配線（実装イメージ・未着手）

| 読取面 | 反映内容 |
|--------|----------|
| **Annual / Monthly Table Window** | 各行の Target Sales 列（日次） |
| **Focus Bar** | Daily Target Sales・Achievement 算出の目標側 |
| **Focus Bar Graph（Phase 9）** | フォーカス日の Today's Target |
| **Daily Floating Window（Phase 10）** | 同上 |
| **Area2 Cockpit** | 月次・年次 target は既存 plan。日次は TW 経由 |

**新規 UI なし。** `KpiYearStore` に `computeDailyTargetByIso(Y, iso)` または月×曜日テーブル API を追加し、既存 TW メトリクス（`KPI-FOCUS-TW-METRICS`）が **実績（timeline）と目標（算出）** を分けて読む。

---

## 11. Phase 表での位置（`year-rollover-data-architecture.md` 参照）

| Phase | 内容 | 依存 |
|-------|------|------|
| **11** | **曜日別日次目標 KPI** — ベースライン年平均構成比 → 当年日次 target → TW / Focus Bar | Phase 3・8 完了・§15.0 timeline |
| **11b** | 月内第 N 週曜日配分（任意） | Phase 11 |

**推奨順（2026-06-28）:** Phase 3・8 ✅ → **Phase 10**（Daily FW）→ **Phase 9**（Graph）→ **Phase 11** →（任意）11b。

---

## 12. 関連ドキュメント

- 目標売上の全体フロー: `docs/target-sales-daily-monthly-annual.md`（§3 ステップ 7）
- 月次 Seasonality%: `docs/year-rollover-data-architecture.md` §15-C（Phase 3）
- TW / Focus Bar: `docs/annual-daily-focus-table-window-notes.md`
- データ正本: `docs/year-rollover-data-architecture.md` §15.0
- Analyze H/L ステッパー: Sales Data Analyze（Phase 3 UI）

---

## 13. 合意メモ

### 2026-06-27

- 本機能は **忘れがちだが KPI として必須**。Excel 時代の曜日別 KPI を Web で再現したい。
- **計算結果だけ** を既存 TW / Target Sales に載せる。**新表・新ページは作らない**。
- コード作業は別プロンプト。本ドキュメントは **仕様の正本メモ**。

### 2026-06-28

- **前年1本足ではなく**、選択した複数年の **加重比率（構成比）の平均** を使う。
- **ベースライン年はユーザーが任意選択**（異常年を外せる）。デフォルトは直近 2 年。
- **丸め:** 計算は小数のまま、表示だけ整数。月次一致は **月末営業日で端数調整**（§7）。**Export（CSV/Excel）は精密値** → `docs/data-export-precision-memo.md`
- **Excel 簡易式**（§5）を Phase 11 実装の正とする。
- **同一曜日内の週次差**（第1〜4月曜など）は Phase 11b / AI で将来検討。Phase 11 では同月同曜日は同額でよい。

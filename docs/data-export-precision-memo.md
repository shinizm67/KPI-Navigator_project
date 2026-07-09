# データ Export（CSV / Excel）— 精密値出力メモ

更新日: 2026-07-05  
ステータス: **設計メモ（未実装）** — Web UI 表示方針とは別レイヤ

関連:

- `docs/weekday-target-sales-kpi-memo.md` §7（丸め・月次一致）
- `docs/weekday-target-phase-plan.md`（Phase 11-6 完了）
- `docs/target-sales-daily-monthly-annual.md`
- `docs/csv-upload-pos-import-memo.md`（取込は既存・出力は本メモ）

---

## 1. 位置づけ

| レイヤー | 方針 |
|----------|------|
| **Web UI（TW / Cockpit / Focus Bar / Daily FW）** | **整数表示**（現場向け）。月次は日次表示値の合計と一致（11-6 最終営業日調整） |
| **CSV / Excel Export** | **小数フル精度**（精密バージョン）。経理・オーナーへの橋渡し用 |

KPI Navigator は **店舗の Excel 日次表・目標表の代替** が主目的であり、**各国の税計算・会計ソフト連携はスコープ外**（`docs/currency-and-markets-memo.md` 参照）。

Export は「アプリを経理ツールにしない」前提の **任意機能**。必要とするユーザーがいれば、小さな需要 × 多国展開でも価値になる。

---

## 2. 出力する値の正本

| 項目 | Export 値 | 備考 |
|------|-----------|------|
| 日次 Target Sales | `resolveDailyTargetByIso(...).rawValue` | 調整前の小数。表示用 `value`（整数）は Export に使わない |
| 月次 Target Sales | `computePlanMonthlyTargets(Y).monthlyTargets[m0]` | 設計上の月次（小数） |
| 日次 Actual Sales | `timeline.dailySales[iso]` | 入力正本 |
| 営業日 | `businessDays` / `isCalendarBusinessDay` と同一 | Sales Data・MEP と一致 |
| 繁閑期 % | `plan.monthlyHlWeights` | そのまま |

**原則:** Export は **Store の算出結果（小数）** をそのまま出す。Web 上の丸め・最終営業日調整は **表示専用** とし、Export 列には載せない（または別列 `target_display` として任意追加可）。

---

## 3. Excel の「見た目 vs 中身」

Excel（および `.xlsx` 生成）では次を分離できる。

| レイヤー | 例 |
|----------|-----|
| **セル値（stored value）** | `386363.63636363635` |
| **表示形式（number format）** | `#,##0` → 画面上は `386,364` |
| **数式バー** | セル選択時に **実値** が見える |

実装候補: SheetJS（`xlsx`）— 取込で既に MEP 等で CDN 利用実績あり。

```javascript
// 例: 値は小数、表示は整数書式
ws['B2'] = { t: 'n', v: 386363.63636363635, z: '#,##0' };
```

CSV には **常にフル精度の数値文字列**（不要ならそのまま、区切りは locale 設定で）。

---

## 4. 想定 Export シート構成（たたき台）

### シート A — 日次（当年 or 選択年）

| 列 | 内容 |
|----|------|
| ISO 日付 | `2026-01-15` |
| 曜日 | locale 依存 |
| 営業日 | Y/N |
| Target Sales（精密） | `rawValue` |
| Actual Sales | timeline |
| Diff | Actual − Target（精密で計算） |

### シート B — 月次サマリー

| 列 | 内容 |
|----|------|
| 月 | 1–12 |
| 月次 Target（精密） | plan.monthlyTargets |
| 日次 Target 合計（精密） | 営業日の rawValue 合計 |
| 月次 Actual 合計 | timeline 集計 |

注釈行（1 行）:

> Daily targets in the app UI are rounded integers; exported values retain full precision for reconciliation.

（JA / EN は Export 時の locale に合わせる）

---

## 5. Web 表示との関係（11-6）

| 項目 | Web | Export |
|------|-----|--------|
| 日次 Target | 整数（最終営業日のみ調整あり） | `rawValue` 小数 |
| 月次 Target | 整数（Cockpit 等は今後揃える） | plan 小数 |
| 手計算との一致 | Web 上は **表示値同士** で一致 | Export 上は **小数同士** で一致 |

ユーザーが Excel で足し算する用途では **Export 精密版** を使う。Web は現場 KPI 用。

---

## 6. スコープ外（明示）

- 各国の税・インボイス・会計ソフト API
- 通貨換算（Export は選択通貨のまま）
- Web UI の小数表示切替（dropdown 等）— **当面不要**。Export で足りる

---

## 7. 実装フェーズ案

| 順 | 内容 | 依存 |
|----|------|------|
| 1 | 日次 Target + Actual の CSV（当年） | Phase 11 Store API ✅ |
| 2 | 同上 Excel（`raw` + `#,##0` 書式） | SheetJS |
| 3 | 月次サマリー・複数年 | timeline 正本 |
| 4 | Sales Data / Past Sales 窓からの Export ボタン | UI 配置要検討 |

`docs/press-release-backlog.md` の告知ネタとしても可（「Excel 互換エクスポート」）。

---

## 8. 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-07-05 | 初版。Web=整数・Export=精密の二層方針 |

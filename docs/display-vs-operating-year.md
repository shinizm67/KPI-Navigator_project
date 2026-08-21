# displayYear と operatingYear / planningYear（必須ルール）

更新日: 2026-08-17  
ステータス: **必須・恒久**  
きっかけ: Step AI（Past Sales が 2025 に行けない / Sales Data の H/L ▲▼ がロック）  
Cursor ルール: [`.cursor/rules/display-vs-operating-year.mdc`](../.cursor/rules/display-vs-operating-year.mdc)  
関連: [`year-rollover-data-architecture.md`](./year-rollover-data-architecture.md) · [`snapshot-store-phased-plan.md`](./snapshot-store-phased-plan.md)

---

## 1. なぜ必須か

画面で見ている年と、いま計画している年は別物である。  
`calendarYear`（表示）を計画年として使うと、次のような壊れ方が起きる。

| 表示年 | 計画年（正しい） | 誤用したとき |
|--------|------------------|--------------|
| 2025 | 2026 | Past Sales の上限が 2024 → **2025 に ◀︎▶︎ できない** |
| 2025 | 2026 | Sales Data / H/L が 2025（locked）扱い → **▲▼ が押せない** |

Step AI の修正方針は「計画・編集は常にストアの運用年」である。以降も同じ。

---

## 2. 用語（正本）

| 用語 | 別名・実装 | 意味 |
|------|------------|------|
| **displayYear** | `calendarYear`、`__ANNUAL_DATA.calendarYear`、年ナビの現在値 | ユーザーがタイムライン／カレンダーで **見ている** 年 |
| **operatingYear** | `store.meta.operatingYear`、`KpiYearStore.getOperatingYear()` | いまの **運用・計画年**（例: 2026）。ロールオーバーで進む |
| **planningYear** | operatingYear と同義（ドキュメント・設計メモ向け） | 「いま計画している年」。コードでは `operatingYear` を優先 |

**別名の扱い**

- コードの正本キーは **`operatingYear`**
- 設計メモで「計画年」と書くときは **planningYear = operatingYear**
- UI の年ラベルが「Sales Data の年」ならそれは **operatingYear**。displayYear ではない

---

## 3. どちらを使うか（判定表）

| 用途 | 使う年 |
|------|--------|
| Cockpit / Focus / 日次行のスクロール・選択日 | displayYear |
| Past Sales の年セレクト上限（`max = ? - 1`） | **operatingYear** |
| Sales Data の年表示・Analyze・H/L 書き込み | **operatingYear** |
| 繁閑%初期値・参考繁閑期%の平均対象年キャップ | **operatingYear** |
| 年次目標・計画デフォルト・`ensureOperatingYearPlanDefaults` | **operatingYear** |
| `isYearLocked` / 編集可否（計画面） | 対象年そのもの。計画面の「今年」は **operatingYear** |
| 過去実績の参照（Past Sales で選んだ年） | ユーザーが選んだ **past year**（≤ operatingYear − 1） |

---

## 4. 実装ルール

1. モーダルや計画ロジックの `getOperatingYear()` は、**必ず**先に `KpiYearStore.getOperatingYear()` を見る。`calendarYear` はストア未初期化時のフォールバックのみ（マーカー例: `KPI-MODAL-OY-STORE-AI`）。
2. `clampPastSalesYear` / Past Sales の `ensureYearOptions` の上限は `operatingYear - 1`。displayYear から引かない。
3. Sales Data Analyze の `state.year` / `planYear` は **operatingYear に同期**する。displayYear を入れない。
4. 変数名: 表示なら `displayYear` / `calendarYear`、計画なら `operatingYear` / `oy`。曖昧な `cy` だけで両方を表さない。
5. 新規コード・パッチスクリプトでも、この表に無い用法を増やさない。

---

## 5. 回帰チェック（年まわりを触ったら必須）

前提: `operatingYear === 2026`、画面の displayYear を **2025** にする。

1. Past Sales: ◀︎▶︎ / 年セレクトで **2025** に行ける。**2026 には行けない**
2. Sales Data: 年表示が **2026**。Target Sales の H/L ▲▼ が有効
3. 2023 以前への ◀︎ は従来どおり

---

## 6. やってはいけない例

```javascript
// NG: 表示年を計画年として使う
function getOperatingYear() {
  return Number(window.__ANNUAL_DATA.calendarYear);
}

// OK: ストアの運用年を優先
function getOperatingYear() {
  if (window.KpiYearStore && typeof KpiYearStore.getOperatingYear === 'function') {
    var oy = Number(KpiYearStore.getOperatingYear());
    if (Number.isFinite(oy)) return oy;
  }
  // calendarYear はフォールバックのみ
  ...
}
```

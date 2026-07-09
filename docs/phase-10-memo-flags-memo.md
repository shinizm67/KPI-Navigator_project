# Phase 10 — Daily Floating Window / メモ日付マーカー

> **関連:** `docs/year-rollover-data-architecture.md` §10, `docs/daily-page-graph.md`  
> **更新日:** 2026-07-06

---

## 目的

MEP（月次編集）で保存した **日次メモ** がある日を、年次・月次の **日次表（TW）** でひと目でわかるようにする。

---

## サブフェーズ

| Phase | 内容 | 状態 |
|-------|------|------|
| **10-a** | Store に「この日メモあり」を読む API | ✅ |
| **10-b** | 日次表の日付列に水色の点 | ✅ |
| **10-c** | フォーカスバー・Daily 窓・カレンダーにも印 | ✅ 2026-07-09 |

---

## 10-a — Store API

| API | 説明 |
|-----|------|
| `KpiYearStore.readDailyMemoFlagMapForYear(year)` | その年の `{ '2026-03-15': true, ... }` |
| `KpiYearStore.hasDailyMemoForIso(year, iso)` | 1 日だけ調べる |

**判定:** `dailyMeta.flags[iso]` または `dailyMeta.memos[*][iso]` に文字が入っていれば true。

**触る場所:** `scripts/kpi_year_store_client.py` → 6 ページ Store ブロック再注入

---

## 10-b — TW 日付マーカー

- 日次表を描くとき、メモがある日の日付セルに `annual-daily-row__cell--has-memo` クラス
- 右端に **6px の水色の点**（Office モードは青）
- MEP で Save 後 → `kpi:mepDataChanged` → TW 再描画で印が付く

**触る場所:** `scripts/focus_tw_metrics_client.py` + CSS（年次・月次 4 ページ）

**触らない:** Past Sales、Sales Data モーダル、MEP 編集ロジック本体

---

## 10-c — Focus Bar / Daily 窓 / 日付ボタン

10-b と同じ **6px 水色ドット**（Office は青）を、次の面にも出す。

| 面 | 対象 |
|----|------|
| Focus Bar（横） | `.annual-daily-focus-bar-lower__cell--date` — TW 行の `has-memo` をコピー |
| Cockpit 日付ボタン | `#annual-daily-date-btn` — `hasDailyMemoForIso` |
| Daily Floating Window | `#daily-overlay-date-btn` — `fill(iso)` 時 |
| Monthly 縦 Focus / 日付ヘッダー | `.monthly-vfocus-date` / `.monthly-date-header-cell` |

**触る場所:** `scripts/apply_phase_10c_memo_flags.py` → JA/EN × Annual/Monthly 4 ページ

**触らない:** Past Sales、Sales Data モーダル、MEP 編集ロジック本体、数値 KPI

---

## 再適用

```bash
python3 scripts/apply_phase_10_memo_flags.py
python3 scripts/apply_phase_10c_memo_flags.py
```

（10-a/b は内部で `apply_kpi_year_store_block_only.py` と `apply_focus_tw_metrics.py` を実行）

---

## 確認チェックリスト

### 10-a / 10-b

1. MEP を開き、営業日のセルでメモを書いて **Save**
2. 年次ページの日次表で、その日の **日付の右に水色の点** が付く
3. 月次ページでも同じ日に点が付く（縦 TW を表示したあと）
4. メモを空にして Save → 点が **消える**
5. 売上数字・目標数字は **変わっていない**（印だけの変更）

### 10-c

1. メモがある日を Focus Bar に合わせると、**横 Focus の日付セル右に点**
2. Cockpit の日付ボタンにも同じ点が付く
3. Daily 窓を開くと、日付ボタンに点が付く（ナビしてもその日があれば付く）
4. Monthly: 縦 Focus 日付・日付ヘッダーにも点
5. メモを空にして Save → 上記の点がすべて消える
6. 売上・目標・達成率の数字は変わらない

### 触っていないので壊れていないはず

- Annual / Monthly の表示速度（perf パッチ）
- Graph ポップオーバー
- 曜日別目標の計算
- Past Sales

---

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-07-06 | 10-a + 10-b 初回適用 |
| 2026-07-09 | 10-c Focus Bar / Daily 窓 / 日付ボタン・Monthly ヘッダー |
| 2026-07-09 | **Daily Notes Save 修復** — 入力中メモが Store 空文字マージで消える・日付切替で DOM 未 flush、Save 失敗を成功扱いしていたのを修正（`mep_store_client` / `_mep_memo_float`） |
| 2026-07-09 | **MEP → Daily Notes ジャンプ** — 全メモ行（Store Event〜Reservation + 自由 Memo）セルクリックで該当日・該当行へ。プレビュー表示。`apply_mep_memo_drilldown.py` |

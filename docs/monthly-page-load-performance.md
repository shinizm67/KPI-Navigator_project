# Monthly ページ — 読み込み・操作パフォーマンス改善メモ

> **共有先:** Codex / Tars など後続エージェント向け  
> **更新日:** 2026-07-06  
> **関連:** `docs/monthly-page-memo.md`, `docs/monthly-vertical-focus-bar-memo.md`, `docs/weekday-target-phase-plan.md`

---

## 1. 背景と課題

Monthly ページ（`app/monthly/index.html`, `en/app/monthly/index.html`）で、次の UX 問題があった。

| 症状 | 体感 |
|------|------|
| ページリロード | 完了まで **約 30 秒** |
| 日付移動（Cockpit 矢印・Today） | 1 クリックごとに重い（改善前） |
| 年移動 | 特に重い（改善前） |
| リロード直後の TW（Focus Bar 下段） | しばらく `—` のまま（空っぽ） |

**制約（最重要）:** 改善は **Monthly ページのみ**。Annual コックピット・Past Sales・Store ブロック全体の再注入には **極力触れない**。回帰リスクが高い。

---

## 2. 根本原因（DB ではない）

遅さの主因は **localStorage / DB の有無ではなく、クライアント側 JS の重複処理と DOM 全再構築**。

### 2.1 リロード時の重い処理

1. **`renderAnnualDailyTimeline()`** — 複数年 × 約 365 日 × 多数セルの DOM 構築（数千行）
2. **`rebuildColumns()`** — 横スクロール列（約 90 列）の同期再構築
3. **`syncCockpitForCalendarYear()`** — 12 ヶ月分の営業日カウント・売上集計が **複数箇所から重複呼び出し**
4. **`onArea1CockpitRefresh()`** — Cockpit KPI 帯の重複更新
5. **イベント連鎖** — `renderAnnualDailyTimeline` 完了 → `annual:timelineRowsRendered` → Cockpit 再描画

### 2.2 日付・年移動時の重い処理

- 同じ月内の日付変更でも `rebuildColumns()` が走っていた
- `persistStore()` がナビ操作のたびに同期実行
- `kpi:selectedDateChanged` 経由で Cockpit が二重更新
- 年変更のたびに `buildDailyTargetMapForYear` が日ごとに再計算

### 2.3 DB 化だけでは速くならない理由

- 同じロジックをブラウザで回せば **計算量は変わらない**
- 速くするには **サーバー側で集計済みスナップショットを返す** など設計変更が別途必要（工数大）
- 現フェーズでは **重複のバイパス・遅延・段階描画** で対処

---

## 3. 実施した改善（フェーズ一覧）

すべて **Monthly HTML（JA/EN）のみ** をパッチ。適用は Python スクリプト経由（HTML 直編集より再現性が高い）。

### Phase A — TW リスナー debounce

| 項目 | 内容 |
|------|------|
| スクリプト | `scripts/apply_tw_listener_schedule.py` |
| 問題 | Store イベント二重発火で `renderAnnualDailyTimeline` が連続フル再構築 |
| 対策 | 10 リスナーを `scheduleRenderAnnualDailyTimeline(cy, { preserveScroll: true })` に変更（32ms debounce） |
| 初回描画 | `renderAnnualDailyTimeline(calendarYear)` の同期 1 回は維持（のち Phase D で変更） |

### Phase B — 日付ナビ高速化

| 項目 | 内容 |
|------|------|
| スクリプト | `scripts/apply_monthly_nav_perf.py` |
| 対策 | 同月内の日付移動では `rebuildColumns` をスキップ（`scheduleScroll` のみ） |
| 対策 | Cockpit 更新を `setTimeout(0)` でまとめる |
| 対策 | `readGroup1TwSnapshot` を `resolveDailyTargetByIso` の軽量パス＋キャッシュ参照に |

### Phase C — 年ナビ高速化

| 項目 | 内容 |
|------|------|
| スクリプト | `scripts/apply_monthly_year_nav_perf.py` |
| 対策 | `window.__buildDailyTargetMapForYear` を export、年 1 回の target map キャッシュ |
| 対策 | `scheduleRebuildColumns`（32ms debounce）導入 |
| 対策 | `syncCockpitForCalendarYear` を `requestAnimationFrame` で遅延 |
| 対策 | `calendarYearChanged` の営業日数カウント重複リスナー削除 |
| 対策 | 日付ナビ時の `kpi:selectedDateChanged` による Cockpit 二重更新をスキップ |
| 対策 | `setSelectedDate` の `persistStore` をナビ操作時 500ms 遅延（Monthly 内 Store ブロックのみ） |

### Phase D — リロード高速化（第 1 弾）

| 項目 | 内容 |
|------|------|
| スクリプト | `scripts/apply_monthly_load_perf.py` |
| マーカー | `/* KPI-MONTHLY-LOAD-PERF */` |
| 対策 | 縦 TW 初回描画を遅延（`__ensureMonthlyVerticalTwRendered`） |
| 対策 | 初期 `rebuildColumns` → `scheduleRebuildColumns` + `monthly:pageReady` 後に発火 |
| 対策 | `syncCockpitForCalendarYearCore` + debounce ラッパーで Cockpit 同期を 1 回に集約 |
| 対策 | 初回 `onArea1CockpitRefresh()` 直叩きを削除（`scheduleInitialCockpitSync` に任せる） |
| 対策 | 日付スクロール時に TW 未描画なら `__ensureMonthlyVerticalTwRendered` を起動 |

### Phase E — リロード高速化（第 2 弾・TW 空表示の短縮）

| 項目 | 内容 |
|------|------|
| スクリプト | 同上 `apply_monthly_load_perf.py` |
| マーカー | `/* KPI-MONTHLY-LOAD-PERF-2 */` |
| 対策 | TW 開始タイミングを `requestIdleCallback(4000)` から **`monthly:pageReady` 直後** に変更 |
| 対策 | **2 段階描画:** 先に `boundsHint: 'anchor-year-only'`（表示年 ±14 日）→ 暇なときに全年度 |
| 対策 | `computeAnchorYearTimelineBounds()` を Monthly TW ブロック内に追加 |
| 対策 | Focus Bar **展開状態**で開いた場合は最初から全年度描画（`forceFull`） |

---

## 4. 主要なランタイム API（Monthly 内）

エージェントが HTML を読むときの目印。

```text
window.__ensureMonthlyVerticalTwRendered(forceFull?)
  → 縦 TW の遅延／段階描画エントリポイント

window.__monthlyVerticalTwPartialRendered  // 表示年のみ描画済み
window.__monthlyVerticalTwFullRendered     // 全年度描画済み

scheduleRebuildColumns(scrollIso, scrollOpts, onComplete?)
  → rebuildColumns の 32ms debounce 版

scheduleRenderAnnualDailyTimeline(anchorYear, opts)
  → 縦 TW の 32ms debounce 版（イベントリスナー用）

syncCockpitForCalendarYear(explicitYear?)
  → debounce ラッパー（実体は syncCockpitForCalendarYearCore）

monthly:pageReady  // 横列の初期 rebuild 完了後に dispatch
data-monthly-page-ready="1"  // 同上の DOM 属性
```

### Focus Bar 下段が空に見える理由

下段セルは `#annual-daily-rows` の行からテキストをコピーする。縦 TW 未描画の間は **意図的に `—` 表示**。Phase E で空の時間を短縮。

---

## 5. パッチの再適用手順

```bash
# Monthly のみ。順不同だが、以下の順が安全。
python3 scripts/apply_tw_listener_schedule.py
python3 scripts/apply_monthly_nav_perf.py
python3 scripts/apply_monthly_year_nav_perf.py
python3 scripts/apply_monthly_load_perf.py   # Phase D + E（idempotent）
```

各スクリプトは **idempotent**（既適用ならスキップまたは no-op）。  
`apply_monthly_load_perf.py` は Phase 1 未適用の HTML に対しては Phase D から適用し、Phase E は V1 ブロックを V2 に置換。

**対象ファイル（この改善セット）:**

- `app/monthly/index.html`
- `en/app/monthly/index.html`

**触ってはいけない（原則）:**

- `app/annual/index.html` / `en/app/annual/index.html` — 本改善の対象外
- `scripts/apply_kpi_year_store.py` による Store 全体再注入
- `scripts/apply_kpi_year_store_block_only.py` 系の無闇な再実行

---

## 6. 改善結果（ユーザー確認済み）

| 操作 | 改善前 | 改善後（体感） |
|------|--------|----------------|
| 年移動 | 非常に重い | **格段に速い** |
| 日付移動 | UX が悪い | **俄然速い・普通の UX** |
| リロード | 約 30 秒 | **かなり改善**（TW 一瞬空は Phase E で短縮） |

---

## 7. 今後の改善候補（未実装）

優先度順のメモ。いずれも **Monthly 限定・Annual 非影響** を維持すること。

| 候補 | 効果 | 難易度 |
|------|------|--------|
| DOM チャンク追加（requestAnimationFrame で N 行ずつ） | 初回ペイントさらに前倒し | 中 |
| `computeTwMetricsForIso` の年間ループ結果キャッシュ | 再計算削減 | 中 |
| Focus Bar 下段を Store 直読み（縦 TW 非依存） | 空表示の根絶 | 中〜高 |
| サーバー集計 API + DB | 根本解決に近い | **高** |

---

## 8. デバッグのヒント

1. **リロードがまだ遅い** — Performance タブで `renderAnnualDailyTimeline` / `rebuildColumns` / `syncCockpitForCalendarYearCore` の合計時間を確認
2. **TW が長く空** — `monthly:pageReady` から `__ensureMonthlyVerticalTwRendered` までの遅延、`boundsHint` の partial が効いているか
3. **年移動だけ遅い** — `scheduleRebuildColumns` と `__monthlyTwTargetCache` の有無
4. **Annual が壊れた** — 本改善のコミット範囲外。Monthly 専用マーカーが Annual HTML に入っていないか grep 確認

```bash
rg "KPI-MONTHLY-LOAD-PERF|__ensureMonthlyVerticalTwRendered" app/annual en/app/annual
# → ヒット 0 件であること
```

---

## 9. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-07-06 | 初版。Phase A〜E、DB 非依存の説明、再適用手順、今後の候補 |

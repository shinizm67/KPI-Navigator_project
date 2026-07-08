# Annual Repair Project（ARP）— Phase 一覧

**目的:** Annual Table Window / Focus Bar で **スクロールによる年跨ぎ** を Monthly の月跨ぎと同型の UX で実現する（Must）。  
**正本・前提:** `docs/year-rollover-data-architecture.md` §14.2 · `KpiYearStore.timeline` · `selectedDate` 共有  
**Monthly 参照実装:** `crossMonthByEdge` · `anchor-year-only` · MRP 2.x〜3.x（スケルトン / チャンク hydrate）

---

## 描画コントロールの原則（合意）

> **TW に載せる行数（＝日数）で描画をコントロールする**

| 用語 | 意味 |
|------|------|
| **アンカー年** | Cockpit `calendarYear` / `data-year`。TW の「主役」の1年 |
| **描画窓（DOM 行数）** | 常に **アンカー年 ± 端バッファ** の日数だけ `annual-daily-row` を生成する |
| **端バッファ** | 年境界の手前で次の年へ続くための余白（目安: ±14日。Monthly 前後月と同発想） |
| **年跨ぎ** | 縦スクロールが端に達したら `anchorYear ± 1` に切替 → 窓をリビルド（`preserveScroll`） |

**注意（よくある誤解）:**

- ❌ 画面上に見えている行だけ（純粋な virtual scroll）— ARP 初期スコープ外（Phase 5 候補）
- ❌ 常に3年分（現 `computeFocusTimelineBounds` の max）— やめる方向
- ✅ **DOM 上の行数 ≒ 365 + バッファ（約 30〜90 日）** を上限にスライディング
- ✅ Open / Close とも **同じ窓原則**（Open は1行のセル数が多いだけ）

---

## Phase 一覧

| Phase | 名称 | スコープ | 受け入れ（要約） | 状態 |
|-------|------|----------|------------------|------|
| **ARP-0** | 現状整理・計測 | Annual / Monthly の bounds・行数・scroll 端処理を文書化。DevTools で Close/Open の初期 render 時間・DOM 行数を記録 | ベースライン数値あり | ✅ |
| **ARP-1** | `anchor-year-only` 統一 | Annual を Monthly 同様 `computeAnchorYearTimelineBounds` をデフォルトに。`outside-year` はバッファ行のみ。3年一括描画を廃止 | DOM 行数 ≦ 400。当年データは従来どおり表示 | ✅ |
| **ARP-2** | 縦スクロール年跨ぎ（Close） | `crossYearByEdge`（縦・Close モード）。12/31 ↔ 1/1 で `calendarYear` 切替 + 窓リビルド + `selectedDate` / 年バッジ同期 | Cockpit 戻らず TW だけで 2025↔2026 を往復 | ✅ |
| **ARP-3** | Focus Bar 同期 | 年跨ぎ時 Focus Bar 行・横同期・`annual:dailyDateChanged` 整合。年バッジ（TW 左上）追従 | フォーカス日と TW 行・年表示が一致 | ✅ |
| **ARP-4** | Open モード対応 | `annual-focus-bar-expanded` 時の3グループ横スクロール + 年跨ぎ。端で同 `crossYearByEdge` | Open でも年境界をスクロールで跨げる | ✅ |
| **ARP-5** | 性能（Annual MRP 移植） | ジオメトリキャッシュ・DocumentFragment・focus-sync debounce・着地短縮・Open OFF Date 色修正（5a〜5d） | 年跨ぎ・スクロールの体感ストレスなし | ✅ |
| **ARP-6** | Monthly 横 TW 年跨ぎ | Monthly 90日窓の **年境界**（12月→1月）で `state.year` 切替。既存 `crossMonthByEdge` を表示同期のみに安定化 | Monthly でも年をスクロールのみで跨げる | ✅ |
| **ARP-7** | 受け入れ・回帰 | §14.2 チェックリスト・Past Sales 過去年・Annual↔Monthly `selectedDate`・Office/Sci-Fi | 本筋 Phase 9 再開前のゲート | ✅ |

---

## 技術メモ（実装の当たり所）

### 現状（Annual）— ARP-1 後

- `renderAnnualDailyTimeline(anchorYear)` — アンカー年 ±14 日のみ DOM 生成（デフォルト `anchor-year-only`）
- `computeAnchorYearTimelineBounds` — デフォルト bounds（≈393 行）
- `computeFocusTimelineBounds` — 残置（明示的に `boundsHint` 未指定かつ full が必要な場合のみ将来利用）
- 年変更 — `annual:calendarYearChanged` → Cockpit 経由 / TW スクロール端（ARP-2）
- **ARP-2 実装** — `crossYearByEdge(dir)`（Close のみ）。縦スクロール端で発火。
  - `annual:calendarYearChanged` は**飛ばさない**（副作用の多いリスナー群を回避）
  - 窓リビルド `renderAnnualDailyTimeline(nextYear, { boundsHint:'anchor-year-only' })`
  - 年バッジ DOM 直接更新 + `setDailyDateByISO(境界日, 'focus-sync')`
  - データ範囲: `annualRenderableYearBounds()`（`listYearsWithData` / `operatingYear` / `systemYear+1`）
- **ARP-2b** — Cockpit 年ナビ表示の追従（表示のみ）＋ 着地の慣性打ち消し
  - `window.__ANNUAL_UI.setCalendarYearDisplayOnly(y)`: `currentYear` / `yearBtn` / `calendarYear` / メニューのみ更新。`annual:calendarYearChanged` は**飛ばさない**（二重描画・`selectedDate` 上書きを回避）
  - 営業日数表示 `syncBusinessDayDisplayFromDailyMap()` も追従（純粋な表示更新）
  - 境界日着地: `requestAnimationFrame` で `scrollTop` を再セットし慣性を打ち消し、`snapping` 保持を 160ms に延長

### 目標パターン（Monthly から移植）

```
crossYearByEdge(dir):
  nextYear = anchorYear + dir
  if データ範囲外: return
  anchorYear = nextYear
  calendarYear / selectedDate / 年バッジ 同期
  renderAnnualDailyTimeline(nextYear, { preserveScroll, boundsHint: 'anchor-year-only' })
  scrollToIso(境界日の ISO)
```

### ファイル（想定）

| 種別 | パス |
|------|------|
| Annual 本体 | `app/annual/index.html`, `en/app/annual/index.html` |
| Monthly（ARP-6） | `app/monthly/index.html`, `en/app/monthly/index.html` |
| パッチ | `scripts/apply_annual_arp_phase*.py`（MRP と同型） |
| 設計正本 | `docs/year-rollover-data-architecture.md` |

---

## 本筋 Phase との関係

| 本筋 | ARP との関係 |
|------|----------------|
| Phase 8 読取面 | ARP の前提（過去年 timeline 表示） |
| Phase 9 Graph | ARP-7 完了済み。フォーカス日は `selectedDate` 共有 |
| Phase 10+ | ARP-7 完了後に再開可 |

---

## ARP-7 受け入れ結果（2026-07-08）

ユーザー検証により以下を確認。いずれも問題なし。

| # | 項目 | 結果 |
|---|------|------|
| 1 | Annual Close: 縦スクロールで 12/31 ↔ 1/1 年跨ぎ | ✅ |
| 2 | Annual Open: 同上（横リセット含む） | ✅ |
| 3 | 2段階停止（境界で一旦止まる → 再スクロールで跨ぐ） | ✅ |
| 4 | Focus Bar スナップ・縦方向・セル値整合 | ✅ |
| 5 | 年跨ぎの体感（应力なし / トン→ん→パッ） | ✅ |
| 6 | Open/Close の OFF 日 Date 列が非アクティブ表記 | ✅（差分があれば追報） |
| 7 | Monthly 横TW: 12月↔1月スクロール年跨ぎ | ✅ |
| 8 | Annual↔Monthly `selectedDate` / 年表示追従・回帰目視 | ✅ |

**結論:** ARP-0〜7 は完了。Must であった「Annual 年跨ぎスクロール」は達成。本筋 Phase 9 以降に復帰してよい。

---

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-07-07 | 初版（ARP-0〜7。年跨ぎスクロール Must 対応） |
| 2026-07-08 | ARP-1 適用（`scripts/apply_annual_arp_phase1.py`） |
| 2026-07-08 | ARP-2 適用（`scripts/apply_annual_arp_phase2.py`。Close 縦スクロール年跨ぎ・検証待ち） |
| 2026-07-08 | ARP-2b 適用（`scripts/apply_annual_arp_phase2b.py`。Cockpit 年ナビ表示追従＝表示のみ軽量同期・着地の慣性打ち消し） |
| 2026-07-08 | ARP-3 適用（`scripts/apply_annual_arp_phase3.py`。Focus Bar 行の明示同期・dailyDateChanged 連動） |
| 2026-07-08 | ARP-4 適用（`scripts/apply_annual_arp_phase4.py`。Open モード縦スクロール年跨ぎ・横スクロールリセット） |
| 2026-07-08 | ARP-2c 適用（`scripts/apply_annual_arp_phase2c.py`。2段階年跨ぎ＝年始/年末で一旦停止→再スクロールで跨ぐ。行き過ぎ現象を解消） |
| 2026-07-08 | ARP-2d 適用（`scripts/apply_annual_arp_phase2d.py`。scroll 即時バッファクランプ・DOM 実測スナップ・Close でも snapToNearestRow） |
| 2026-07-08 | Focus Bar 縦方向の符号反転バグ修正（`refreshLower` の `oy` 符号を ARP-2d の offset 定義に合わせる） |
| 2026-07-08 | ARP-2e 適用（`scripts/apply_annual_arp_phase2e.py`。hot path 軽量化＝毎スクロール393行計測を O(1) 算術に・range キャッシュ・enforce rAF 間引き。カクつき低減） |
| 2026-07-08 | ARP-5a 適用（`scripts/apply_annual_arp_phase5a.py`。性能第1弾）。(1) ジオメトリを描画後1回だけ実測しキャッシュ（`getAnnualGeom`）→ スクロール hot path（enforce/snap/nearest/`getFocusedRowState`）から `getBoundingClientRect` 由来の強制 reflow を排除＝カクつき低減。(2) 年跨ぎ描画を DocumentFragment 一括挿入。(3) `crossYearByEdge` の Cockpit 表示・営業日数同期を着地後 setTimeout に遅延＝停止→跨ぎのタイムラグ低減。キャッシュ無効化は `annual:timelineRowsRendered` / `annual:focusBarStateChanged` / `resize`。 |
| 2026-07-08 | ARP-5b 適用（`scripts/apply_annual_arp_phase5b.py`。性能第2弾・DevTools 計測に基づく副作用削減）。(1) `focus-sync` 時の `onArea1CockpitRefresh`（`computeTwMetricsForIso` 年365日ループ）を 320ms debounce。(2) `focus-sync` 時の `persistStore` / `syncAnnualNavToStorage` を 500ms debounce。(3) `refreshLower` は行 index 変化時のみセル textContent 更新（transform は毎フレーム）。 |
| 2026-07-08 | ARP-5c 適用（`scripts/apply_annual_arp_phase5c.py`。UX 微調整）。`crossYearByEdge` の年跨ぎ着地解除を固定 160ms から「`waitForVerticalScrollSettle` による着地検知 + 48ms」へ変更。境界で止まった後の「んん〜」を短縮し、`トン→ん→パッ` に寄せる。 |
| 2026-07-08 | ARP-6 適用（Monthly 横TW年跨ぎの安定化）。`app/monthly/index.html` / `en/app/monthly/index.html` で `crossMonthByEdge` のスクロール境界跨ぎ時の年同期を `syncYearUiDisplayOnly`（表示のみ）へ切替。`setCalendarYearDisplayOnly` / `setCalendarYearSilent` を追加し、年跨ぎ時の不要な `annual:calendarYearChanged` 連鎖を避けつつ、年表示・`calendarYear` は追従。 |
| 2026-07-08 | ARP-5d: Open 時 Focus Bar 下段 OFF Date を非アクティブ色へ修正（`#263638`）。 |
| 2026-07-08 | **ARP-7 受け入れ完了。** ユーザー回帰確認済み（Annual Close/Open 年跨ぎ・性能体感・Monthly 年跨ぎ・selectedDate 整合）。ARP-0〜7 すべて ✅。本筋 Phase 9 再開可。 |

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
| **ARP-2** | 縦スクロール年跨ぎ（Close） | `crossYearByEdge`（縦・Close モード）。12/31 ↔ 1/1 で `calendarYear` 切替 + 窓リビルド + `selectedDate` / 年バッジ同期 | Cockpit 戻らず TW だけで 2025↔2026 を往復 | ⬜ |
| **ARP-3** | Focus Bar 同期 | 年跨ぎ時 Focus Bar 行・横同期・`annual:dailyDateChanged` 整合。年バッジ（TW 左上）追従 | フォーカス日と TW 行・年表示が一致 | ⬜ |
| **ARP-4** | Open モード対応 | `annual-focus-bar-expanded` 時の3グループ横スクロール + 年跨ぎ。端で同 `crossYearByEdge` | Open でも年境界をスクロールで跨げる | ⬜ |
| **ARP-5** | 性能（Annual MRP 移植） | スケルトン先行・メトリクス遅延 hydrate・Cockpit 同期チャンク化（Monthly MRP 2.6〜3.2 の Annual 版） | 低スペックでも年跨ぎ INP / 体感許容 | ⬜ |
| **ARP-6** | Monthly 横 TW 年跨ぎ | Monthly 90日窓の **年境界**（12月→1月）で `state.year` 切替。既存 `crossMonthByEdge` 拡張 | Monthly でも年をスクロールのみで跨げる | ⬜ |
| **ARP-7** | 受け入れ・回帰 | §14.2 チェックリスト・Past Sales 過去年・Annual↔Monthly `selectedDate`・Office/Sci-Fi | 本筋 Phase 9 再開前のゲート | ⬜ |

---

## 技術メモ（実装の当たり所）

### 現状（Annual）— ARP-1 後

- `renderAnnualDailyTimeline(anchorYear)` — アンカー年 ±14 日のみ DOM 生成（デフォルト `anchor-year-only`）
- `computeAnchorYearTimelineBounds` — デフォルト bounds（≈393 行）
- `computeFocusTimelineBounds` — 残置（明示的に `boundsHint` 未指定かつ full が必要な場合のみ将来利用）
- 年変更 — `annual:calendarYearChanged` → Cockpit 経由のみ
- **未実装** — scroll 端での `crossYearByEdge`

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
| Phase 9 Graph | ARP-3 後でも可。フォーカス日は `selectedDate` 共有 |
| Phase 10+ | ARP-7 完了後に再開推奨 |

---

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-07-07 | 初版（ARP-0〜7。年跨ぎスクロール Must 対応） |
| 2026-07-08 | ARP-1 適用（`scripts/apply_annual_arp_phase1.py`） |

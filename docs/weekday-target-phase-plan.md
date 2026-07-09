# Phase 11 — 曜日別日次目標（加重比率）実装計画

> 関連: `docs/weekday-target-sales-kpi-memo.md`, `docs/year-rollover-data-architecture.md` §15.7  
> **ステータス: ✅ 受け入れ完了（2026-07-09）**

## 目的

ユーザーが日々見る **日次 Target Sales** を、月内フラットより **曜日傾向（月×曜日構成比）を反映した現実的な数値** にする。  
設定は **Sales Data ヘッダー 1 か所**、表示は **TW / Focus Bar / Daily FW 全体で統一**。

## 配分モード（ユーザー向け 2 択）

| Store 値 | 表示名（JA） | 説明 |
|----------|-------------|------|
| `monthly-flat` | 月内均等（フラット） | 月次目標 ÷ 当月営業日数。全日同額。 |
| `weekday-weighted` | 曜日加重（標準） | 過去複数年の構成比平均 × 月次目標 ÷ 当年曜日出現数。 |

- デフォルト: `weekday-weighted`
- 過去データ不足時: `resolveDailyTargetByIso` が内部でフラットにフォールバック（`fallback: true`）

---

## サブフェーズ一覧

| Phase | 名称 | 内容 | 状態 |
|-------|------|------|------|
| **11-0** | Store 算出 API | ShareAvg / DailyKpi / computeDailyTargetByIso | ✅ |
| **11-1** | モード永続化 | `dailyTargetMode` read/write, `resolveDailyTargetByIso` | ✅ |
| **11-2** | Sales Data dropdown | Import CSV 右・チュートリアル付き custom dropdown | ✅ |
| **11-3** | ベースライン年 UI | Target Sales タブ内チェックリスト | ✅ |
| **11-4** | TW 配線 | `buildDailyTargetMapForYear` → `resolveDailyTargetByIso` | ✅ |
| **11-5** | Focus Bar / Daily FW | 同一 resolver 経由 | ✅ |
| **11-6** | 端数・月次一致 | 最終営業日差分吸収 | ✅ |
| **11-7** | データ品質 UX | フォールバック警告・Past Sales 再計算促し | ✅ |

---

## Cockpit Open テーブル（意図的に対象外）

**Cockpit Open（年次月次サマリ表）の「日次目標売上」列は、加重比率を使わず月内平均（フラット）のまま。**

| 画面 | 日次目標の算出 |
|------|----------------|
| TW / Focus Bar / Daily FW | `resolveDailyTargetByIso`（曜日加重 or 月内均等） |
| **Cockpit Open テーブル** | `月次目標売上 ÷ 当月営業日数`（常にフラット） |

理由: Open 表は月次サマリの俯瞰用。曜日別のばらつきを載せると読みにくくなる。  
クレームが出た場合のみ、列ヘッダーに tooltip で説明を追加する（現時点では未実装）。

実装箇所: `syncCockpitForCalendarYearCore` 内の `dailyTarget = monthlyTarget / bdCount`。

---

## 完了条件（フェーズごと）

### 11-0 ✅
- [x] `computeWeekdayShareAvg` / `computeDailyTargetByIso` / `buildDailyTargetDisplayMapForYear`
- [x] `scripts/weekday_target_kpi_client.py` + `apply_weekday_target_kpi_store.py`

### 11-1 ✅
- [x] `KpiYearStore.readDailyTargetMode(Y)` / `writeDailyTargetMode(Y, mode)`
- [x] `resolveDailyTargetByIso(Y, iso)` → `{ value, mode, effectiveMode, fallback, rawValue }`
- [x] 6 ページ Store 注入済み

### 11-2 ✅
- [x] Sales Data ヘッダー（Import CSV 右）に dropdown
- [x] 各 option に長文チュートリアル（trigger tooltip + パネル説明）
- [x] 変更時 `writeDailyTargetMode` + `kpi:dailyTargetModeChanged`
- [x] Input / Target Sales 両タブで同じヘッダー表示

### 11-3 ✅
- [x] Target Sales タブ: ベースライン年チェック（最大 5 年遡り）
- [x] `writeWeekdayBaselineYears`
- [x] 0 年選択不可（曜日加重モード時のみブロック表示）

### 11-4 ✅
- [x] TW 日次 Target 列が `resolveDailyTargetByIso` 由来
- [x] モード切替で TW 再描画
- [x] 月内均等モード時、従来と **同値**（回帰）

### 11-5 ✅
- [x] Focus Bar 下段 Target = TW → `resolveDailyTargetByIso`
- [x] Daily FW KPI = `__computeTwMetricsForIso` → resolver
- [x] Graph popover / Cockpit KPI 帯もモード・ベースライン変更で再描画
- 適用: `python3 scripts/apply_phase_11_5_read_surfaces.py`

### 11-6 ✅
- [x] 営業日ごとに小数で算出 → 表示は整数（`Math.round`）
- [x] 月の最終営業日に `MonthlyTarget − Σ(表示目標)` を加算して月次一致
- [x] `resolveDailyTargetByIso` が `value`（表示）と `rawValue`（小数）を返却

### 11-7 ✅
- [x] 品質バナーは **注意が必要なときだけ** 表示（Flat 時・正常時は非表示）
- [x] Past Sales 保存後のみ一時的に「再計算しました」を表示

---

## パフォーマンス受け入れ（2026-07-09）

Phase 11 配線後の重さを解消済み。

| ページ | CLS | INP | LCP |
|--------|-----|-----|-----|
| Monthly | 0.00 | 56ms | 0.52s |
| Annual | 0.00 | 32ms | 0.28s |

関連スクリプト:
- `apply_phase_11_perf_fix.py`
- `apply_cockpit_business_days_perf.py`（Monthly）
- `apply_monthly_cls_fix.py`（Monthly）
- `apply_annual_cls_place_perf.py`（Annual）

---

## 再適用コマンド

```bash
python3 scripts/apply_weekday_target_kpi_store.py
python3 scripts/apply_sdm_daily_target_mode.py
python3 scripts/apply_sdm_weekday_baseline.py
python3 scripts/apply_sdm_weekday_quality.py
python3 scripts/apply_weekday_target_section.py
python3 scripts/apply_phase_11_5_read_surfaces.py
python3 scripts/apply_phase_11_6_display_rounding.py
python3 scripts/apply_phase_11_perf_fix.py
```

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-07-09 | **Phase 11 受け入れ完了**。チェックリスト更新、Open 表フラット方針明記、perf 受け入れ |
| 2026-07-05 | 11-7 完了（データ品質バナー・Past Sales 再計算お知らせ） |
| 2026-07-05 | Export 精密値方針メモ `docs/data-export-precision-memo.md` |
| 2026-07-05 | 11-6 完了（端数・月次一致 — 最終営業日差分吸収） |
| 2026-07-05 | 11-5 完了（Focus Bar / Daily FW / Graph 読取面） |
| 2026-07-04 | 初版。11-0 完了、11-1 Store モード API 追加 |

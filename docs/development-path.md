# KPN Development Path（Task Tree）

**役割:** 本線 / 岐路 / 派生枝 / 復帰先の正本。古いチャットを掘らなくても現在地を復元する。  
**対象読者:** Case / Cursor / Codex / Shin  
**作成日:** 2026-09-20  
**更新ルール:** 新しい岐路を発見したらコードより先に本ファイルへ記録する。CLOSED node は削除しない。

---

## CURRENT PATH

```
CURRENT PATH:
TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-B

PRIOR TRUNK (CLOSED):
Unit 5B -> Unit 5C -> Floating Window Functional Audit
-> Planning Readiness -> Automatic Seasonality / Baseline
-> UI/UX branches closeout

ACTIVE BRANCHES:
- BR-LAUNCH-01 (Demo / New User State) P0
- BR-LAUNCH-01-B (New User Smoke Reset / Account Reuse) P0

PAUSED (under TRUNK-06):
- BR-LAUNCH-01-A (New User Empty-State Contract) P0
  reason: BT unset fix production反映済。New User Human Smoke再実施前に Smoke アカウント完全初期化手段が必要
- BR-LAUNCH-02 Production Smoke / Operational Runbook P1
- BR-LAUNCH-03 UI Consistency Audit P1
- BR-LAUNCH-04 PL Editable Cell Visual Finish P1

DEFERRED:
- BR-LAUNCH-05 Registration / Billing Readiness Assessment P1
  note: Stripe / billing は外部条件を含むため実装本線にせず assessment に留める
- BR-UI-PL-INSIGHT-FIRSTOPEN-PERF P3
  return when: Final Performance / Speed Optimization phase

RETURN TARGET:
BR-LAUNCH-01-A (then BR-LAUNCH-01 → TRUNK-06)

NEXT ACTION:
BR-LAUNCH-01-B Phase 1 local完了確認 →（合意後）commit/push/deploy → browser clear + Human Smoke
```

### Git snapshot（経路記録時点）

| 項目 | 値 |
|------|-----|
| git branch | `wip/unit5b-pl-mep-preset-engine-20260916` |
| HEAD | `6ee7d3b` — Fix unset business type profile hydration |
| origin sync | ahead 0 / behind 0 |
| uncommitted mainline | empty-state app/** 等（BT-scope は commit済） |
| excel/ | user-owned dirty / **do not touch** |

---

## 1. Task Tree 概念（正本）

| 用語 | 意味 |
|------|------|
| **TRUNK** | 本線。製品の主経路。 |
| **BRANCH** | 本線または別 branch から派生した岐路。 |
| **PARENT** | どこから派生したか（node id）。 |
| **RETURN TARGET** | branch 終了後に戻る場所（通常は TRUNK 上の node / NEXT TRUNK）。 |

### STATUS

| 値 | 意味 |
|----|------|
| `ACTIVE` | いま着手中 |
| `PAUSED` | 意図的に中断（再開条件あり） |
| `DEFERRED` | 後回し（復帰条件を必ず書く） |
| `CLOSED` | 完了。削除しない |
| `UNKNOWN` | 確証なし。推測で埋めない |

### PRIORITY

| 値 | 意味 |
|----|------|
| `P0` | 本線 blocking |
| `P1` | 本線復帰前に閉じる |
| `P2` | 関連しているので今やる価値あり |
| `P3` | polish / optimization / later |

---

## 2. Node 必須フィールド

各 node に最低限:

| フィールド | 説明 |
|------------|------|
| `id` | 安定 ID（例: `TR-UNIT-5C`, `BR-UI-OSB`） |
| `name` | 人間可読名 |
| `parent` | 派生元 node id（TRUNK 直下は `TRUNK` 可） |
| `status` | ACTIVE / PAUSED / DEFERRED / CLOSED / UNKNOWN |
| `priority` | P0–P3 |
| `started_at` | 開始日（YYYY-MM-DD）。不明なら UNKNOWN |
| `return_to` | 終了後の復帰先 |
| `reason` | なぜこの岐路/本線か |
| `evidence` | commit / docs / tests / deploy の根拠 |
| `next_action` | 次にやること（CLOSED なら `—`） |

必要に応じて:

- `closed_at`
- `commit`
- `docs`
- `tests`
- `deploy`
- `reusable_pattern`

---

## 3. Operating Rule

### 岐路を発見したとき

すぐコードを書かない。先に本ファイルへ:

- `parent`
- `reason`
- `priority`
- `return_to`
- `status: ACTIVE`

を記録してから着手する。

### branch を閉じるとき

- `status` → `CLOSED`
- `closed_at`
- `commit`
- `tests`（あれば）
- `deploy` evidence（あれば）
- `return_to` を明示

CLOSED node は **削除しない**（履歴・再利用のため残す）。

### Source of Truth

本ファイルは **開発経路の正本**。

ただし code / commit / test / deploy evidence と矛盾した場合は、どちらかを勝手に採用しない。

1. 矛盾を報告する  
2. reconcile してから進む  

履歴に確証がないものは **UNKNOWN**。推測で埋めない。

---

## 4. New Chat Handoff Rule

新しい Cursor / Case / Codex chat は **最初に本ファイルを読む**。

実装前に最低限確認:

1. Current trunk  
2. Current active path  
3. Active branches  
4. Deferred branches  
5. Return target  
6. Next confirmed task  
7. branch / HEAD / origin sync  
8. uncommitted mainline work  

---

## 5. TRUNK nodes（本線履歴）

確証のある順序のみ。subunit の欠番（例: 5C-3 / 5C-4）は UNKNOWN。

### TR-UNIT-5B

| フィールド | 値 |
|------------|-----|
| id | `TR-UNIT-5B` |
| name | Unit 5B — PL/MEP Business Type preset engine |
| parent | `TRUNK`（Unit 5） |
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN（branch 名 `unit5b-...-20260916`） |
| closed_at | UNKNOWN（5C へ移行。厳密な閉じ日は未記録） |
| return_to | `TR-UNIT-5C` |
| reason | Business Type 向け expense preset / catalog エンジン |
| evidence | commits `f41e1f9` Add PL MEP business preset engine; `6fe3275` deferred classification; `7ba334d` PL Analyze BT; `cf7b67a` MEP preset sync; tests `_test_pl_mep_preset_engine.py`, `_test_business_expense_presets.py`, `_test_pl_analysis_business_type.py` |
| next_action | — |
| note | git branch 名はいまも unit5b。経路上は 5C へ進んだ（命名ラグ。矛盾ではなく記録上の遅れ）。 |

### TR-UNIT-5C

| フィールド | 値 |
|------------|-----|
| id | `TR-UNIT-5C` |
| name | Unit 5C — Business Type surface adaptation |
| parent | `TR-UNIT-5B` |
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN |
| closed_at | 2026-09（close tests: `3f35989`, `f609d32`） |
| return_to | `TR-FW-AUDIT` |
| reason | PL Insight / Insight Summary / Monthly TW / MEP meal を BT に合わせる |
| evidence | markers `UNIT-5C-1`…`5C-2`…`5C-5`…`5C-6`; commits `9ca3ab0`, `f179989`, `ab4fa9f`, `0249724`, `3f35989`, `f609d32`; tests `_test_pl_insight_finalization.py`, `_test_monthly_tw_business_type.py`, `_test_mep_meal_business_type.py` |
| next_action | — |
| unknown | `5C-3` / `5C-4` の marker・doc は repo に無し → **UNKNOWN（欠番か未作成か未確定）** |

### TR-FW-AUDIT

| フィールド | 値 |
|------------|-----|
| id | `TR-FW-AUDIT` |
| name | Floating Window Functional Audit |
| parent | `TR-UNIT-5C` |
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN |
| closed_at | 2026-09-19 前後（wiring tests） |
| return_to | `TR-PLANNING-READINESS` |
| reason | FW のデータ配線を contract test で固定し、本線を閉じる |
| evidence | `e2fc0ac` Daily FW wiring; `10f5495` Top Insight wiring; `f609d32` PL Insight wiring close prep; `3f35989` Unit 5C close tests |
| next_action | — |
| note | 「一通り完了」は `docs/planning-readiness.md` 初版（`138edd1`）の実装タイミング記述と整合。全 FW の COMPLETE 一覧 doc は無し → 個別 FW の完全網羅は UNKNOWN。 |

### TR-PLANNING-READINESS

| フィールド | 値 |
|------------|-----|
| id | `TR-PLANNING-READINESS` |
| name | Planning Readiness / KPI Setup Status |
| parent | `TR-FW-AUDIT` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-19 |
| closed_at | 2026-09-19〜20（本体 + Amber/Gold visual） |
| return_to | `TRUNK-06`（後続本線・2026-09-20 決定） |
| reason | 暫定目標と確定目標を分離。FW Audit 後の独立本線タスク |
| evidence | `138edd1` doc; `a260227` implementation; `docs/planning-readiness.md`; `js/kpi-planning-readiness.js`; `_test_planning_readiness.py` |
| next_action | — |
| docs | [`planning-readiness.md`](./planning-readiness.md) |

### TR-SEASONALITY-BASELINE

| フィールド | 値 |
|------------|-----|
| id | `TR-SEASONALITY-BASELINE` |
| name | Automatic Seasonality / Baseline-Year Contract |
| parent | `TR-PLANNING-READINESS` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-19 |
| closed_at | 2026-09-19 |
| return_to | UI/UX polish branches → その後 TRUNK |
| reason | Recommended seasonality / baseline years / anomaly flag |
| evidence | `474ec5f`, `4733b57`, `fbe7a48`, `43fbfe2`; `js/kpi-seasonality-allocator.js`; `docs/planning-readiness.md` ステータス行 |
| next_action | — |

### TR-UIUX-CLOSEOUT

| フィールド | 値 |
|------------|-----|
| id | `TR-UIUX-CLOSEOUT` |
| name | UI/UX branches close（Sales Data / Past Sales / Overlay / Amber） |
| parent | `TR-SEASONALITY-BASELINE` |
| status | CLOSED |
| priority | P1〜P3（各子 node 参照） |
| started_at | 2026-09-19〜20 |
| closed_at | 2026-09-20（`dffeb8e`） |
| return_to | `TRUNK-06` |
| reason | 視認性・scrollbar・PROVISIONAL warning の岐路を閉じ本線へ戻す |
| evidence | 下記 CLOSED BRANCHES |
| next_action | — |

---

## 6. CLOSED BRANCHES（UI/UX 岐路）

### BR-UI-SALES-DATA-HIERARCHY

| フィールド | 値 |
|------------|-----|
| id | `BR-UI-SALES-DATA-HIERARCHY` |
| name | Sales Data UI hierarchy |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P2 |
| started_at | UNKNOWN |
| closed_at | 2026-09-20 前後 |
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | readonly / active / closed-day 可読性 |
| evidence | commits `b613297`, `a22a5cf`, `a8762ed`, `5987de7` |
| next_action | — |

### BR-UI-PAST-SALES-HIERARCHY

| フィールド | 値 |
|------------|-----|
| id | `BR-UI-PAST-SALES-HIERARCHY` |
| name | Past Sales UI hierarchy |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P2 |
| started_at | UNKNOWN |
| closed_at | 2026-09-20 前後 |
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | Past Sales を Sales Data 視認性と揃える |
| evidence | commits `a937550`, `ce9ae34`, `a443802` |
| next_action | — |

### BR-UI-OVERLAY-SCROLLBAR

| フィールド | 値 |
|------------|-----|
| id | `BR-UI-OVERLAY-SCROLLBAR` |
| name | Overlay Scrollbar UX |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 前後 |
| closed_at | 2026-09-20 |
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | 共通 overlay scrollbar 標準化 |
| evidence | `b18c7a3`; `docs/kpn-scrollbar-ux-contract.md`; `js/kpi-overlay-scrollbar.js` |
| deploy | production 反映済み（後続 hotfix 含む） |
| reusable_pattern | shared OSB host wrap + Mac native opt-out |
| next_action | — |

### BR-UI-ANNUAL-TW-OSB

| フィールド | 値 |
|------------|-----|
| id | `BR-UI-ANNUAL-TW-OSB` |
| name | Annual TW dedicated overlay adapter |
| parent | `BR-UI-OVERLAY-SCROLLBAR` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-UI-OVERLAY-SCROLLBAR` |
| reason | Annual TW は wrap しない専用 overlay |
| evidence | `bfad0bf`; `js/kpi-annual-tw-overlay-scrollbar.js` |
| next_action | — |

### BR-UI-INSIGHT-PL-OSB-REGRESSION

| フィールド | 値 |
|------------|-----|
| id | `BR-UI-INSIGHT-PL-OSB-REGRESSION` |
| name | Insight / PL Insight scrollbar regression |
| parent | `BR-UI-OVERLAY-SCROLLBAR` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-UI-OVERLAY-SCROLLBAR` |
| reason | Insight absolute inset / PL first-open scroll |
| evidence | `0d95910`, `058b9cd` |
| next_action | — |
| note | first-open **scroll** 修正は CLOSED。first-open **performance** は別 DEFERRED node。 |

### BR-UI-MONTHLY-TW-HSCROLL

| フィールド | 値 |
|------------|-----|
| id | `BR-UI-MONTHLY-TW-HSCROLL` |
| name | Monthly TW horizontal overflow |
| parent | `BR-UI-OVERLAY-SCROLLBAR` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| commit | `2abc23c` |
| return_to | `BR-UI-OVERLAY-SCROLLBAR` |
| reason | box-style absolute に residual inset を誤コピーしていた |
| evidence | `2abc23c`; `js/kpi-overlay-scrollbar.js`（insetPort vs box-style） |
| deploy | production PASS（RETR/SHA） |
| next_action | — |

### BR-UI-PR-AMBER-GOLD

| フィールド | 値 |
|------------|-----|
| id | `BR-UI-PR-AMBER-GOLD` |
| name | Amber/Gold Planning Readiness warning |
| parent | `TR-PLANNING-READINESS` |
| status | CLOSED |
| priority | P2 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| commit | `dffeb8e` |
| return_to | `TRUNK-06`（UI/UX closeout 後の本線） |
| reason | PROVISIONAL 目標売上を bright orange から dark amber/gold へ |
| evidence | `dffeb8e`; `js/kpi-planning-readiness.js`; `_test_planning_readiness.py` 117 passed; deploy 7/7 |
| docs | [`planning-readiness.md`](./planning-readiness.md) §9.1 |
| next_action | — |

---

## 7. ACTIVE TRUNK — TRUNK-06 Launch / Demo / New-user Readiness

### TRUNK-06

| フィールド | 値 |
|------------|-----|
| id | `TRUNK-06` |
| name | Launch / Demo / New-user Readiness |
| parent | KPN Development |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | N/A |
| reason | Unit 5C / Floating Window Functional Audit / Planning Readiness / Automatic Seasonality / 主要 UI/UX closeout が完了し、KPN を「開発中」から「安全に人へ見せ、使わせられる状態」へ移行するため。 |
| evidence | `docs/development-path.md` Next Trunk Selection Audit（2026-09-20）; HEAD `dffeb8e` UI/UX closeout; Shin/Case 決定で本線開始 |
| next_action | `BR-LAUNCH-01-A` Empty-State Contract 実装 |
| docs | [`free-trial-account-ops.md`](./free-trial-account-ops.md)（配布運用・関連） |

### BR-LAUNCH-01

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01` |
| name | Demo / New User State |
| parent | `TRUNK-06` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | 新規・デモ利用者が壊れない初期状態・導線を確定する |
| evidence | TRUNK-06 開始決定（2026-09-20） |
| next_action | `BR-LAUNCH-01-A` 完了後に Demo Seed / Reset 等の残スコープへ |

### BR-LAUNCH-01-A

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-A` |
| name | New User Empty-State Contract |
| parent | `BR-LAUNCH-01` |
| status | PAUSED |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01` |
| reason | BT unset fix production反映済。New User Human Smoke再実施前に Smoke アカウント完全初期化手段が必要 |
| evidence | emptyStore / demoMoney / BT unset audit; Option B; commit `6ee7d3b` BT unset Settings hydrate（prod deploy済） |
| next_action | `BR-LAUNCH-01-B` 完了後に Human Smoke 再実施 → 01-A へ復帰 |
| contract | 空≠デモ; `—`=未定義; `0`=定義済みゼロ; PR empty=NOT_READY; BT Option B; 数値契約は言語/plan/theme共通 |
| note | CLOSED にしない。Smoke は 01-B reset 確立後 |

### BR-LAUNCH-01-B

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-B` |
| name | New User Smoke Reset / Account Reuse |
| parent | `BR-LAUNCH-01` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-A` |
| reason | 同一 Smoke 専用アカウントを毎回 emptyStore / BT 未設定の新規同等状態へ戻して再利用する |
| evidence | Human Smoke で BT unset 再確認前に初期化手段が必要; 対象 `kpn_empty_state_smoke01@trial.forge-laboratory.com` |
| next_action | Phase 1 完了後: local verify → commit/push/deploy（未実施）→ browser clear + Human Smoke |
| target_account | `kpn_empty_state_smoke01@trial.forge-laboratory.com` |
| phase1 | Admin Reset API `api/v1/admin/reset-user-kpi.php` + tests + ops docs（Founder UI なし） |
| phase2_candidate | Founder Console Reset UI |

### BR-LAUNCH-02

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-02` |
| name | Production Smoke / Operational Runbook |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | 本番スモークと運用手順の固定 |
| evidence | TRUNK-06 child（PAUSED until BR-LAUNCH-01） |
| next_action | BR-LAUNCH-01 完了後に ACTIVE 化を検討 |

### BR-LAUNCH-03

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-03` |
| name | UI Consistency Audit |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | Annual / Monthly / FW 横断の見た目・挙動一貫性 |
| evidence | TRUNK-06 child（PAUSED） |
| next_action | スコープ確定後に ACTIVE |

### BR-LAUNCH-04

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-04` |
| name | PL Editable Cell Visual Finish |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | 入力可能セルの視覚明示（緑/黒等）仕上げ |
| evidence | `pl-table-v1-implementation-spec.md`「Bの必須UX 未着手」; TRUNK-06 child（PAUSED） |
| next_action | BR-LAUNCH-01 後に ACTIVE 化を検討 |

### BR-LAUNCH-05

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-05` |
| name | Registration / Billing Readiness Assessment |
| parent | `TRUNK-06` |
| status | DEFERRED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | 公開登録再開と課金の readiness 評価。Stripe / billing は外部条件を含むため、現時点では実装本線にせず assessment に留める。 |
| evidence | commit `af07bf7` Disable public registration until billing is ready; `free-trial-account-ops.md`（billingType 未実装） |
| next_action | 外部条件（Stripe / サポート体制）が揃ったら assessment → 実装可否を再判定 |
| note | **実装本線にしない**（readiness assessment only）。 |

---

## 8. DEFERRED BRANCHES（既存）

### BR-UI-PL-INSIGHT-FIRSTOPEN-PERF

| フィールド | 値 |
|------------|-----|
| id | `BR-UI-PL-INSIGHT-FIRSTOPEN-PERF` |
| name | PL Insight first-open performance |
| parent | `BR-UI-INSIGHT-PL-OSB-REGRESSION`（関連） / 製品上は PL Insight |
| status | DEFERRED |
| priority | P3 |
| started_at | UNKNOWN（課題認識のみ） |
| return_to | Final Performance / Speed Optimization phase |
| reason | first-open の体感速度。scroll 不能回帰（`058b9cd`）とは別課題 |
| evidence | Case 確定状態（2026-09-20 Current Position）：P3 deferred |
| next_action | Performance phase 開始時に ACTIVE へ昇格するか再評価 |

---

## 9. ACTIVE BRANCHES（一覧）

| id | name | status | priority | parent |
|----|------|--------|----------|--------|
| `BR-LAUNCH-01` | Demo / New User State | ACTIVE | P0 | `TRUNK-06` |
| `BR-LAUNCH-01-B` | New User Smoke Reset / Account Reuse | ACTIVE | P0 | `BR-LAUNCH-01` |

PAUSED under `TRUNK-06`: `BR-LAUNCH-01-A`, `BR-LAUNCH-02`, `BR-LAUNCH-03`, `BR-LAUNCH-04`  
DEFERRED under `TRUNK-06`: `BR-LAUNCH-05`

---

## 10. UNKNOWN / OPEN QUESTIONS

| 項目 | 状態 |
|------|------|
| Unit 5C-3 / 5C-4 | marker・doc なし → **UNKNOWN** |
| Unit 5D 以降 | **UNKNOWN**（現本線は TRUNK-06） |
| FW Audit が全 Floating Window を網羅したか | 配線 tests は Daily / Top Insight / PL Insight のみ確認。それ以外の COMPLETE 宣言 doc なし → **UNKNOWN** |
| `TR-UNIT-5B` / `TR-UNIT-5C` の厳密な started_at | **UNKNOWN** |
| BR-LAUNCH-01 の詳細スコープ（画面・ストア・デモデータ） | Empty-State は `BR-LAUNCH-01-A` で契約確定。Demo Seed/Reset 等は親ブランチ残件 |
| BT Option C 全面ゲート | **DEFERRED**（01-A は Option B） |

---

## 11. Contradictions / Notes（reconcile ログ）

| 観察 | 扱い |
|------|------|
| git branch 名が `unit5b` のままだが経路は 5C・その後・TRUNK-06 へ進んでいる | **命名ラグ**。内容矛盾ではない。本ファイルに明記。 |
| `pl-insight-final-adjustments-memo.md` 旧節に「モック」記述が残る一方、冒頭ステータスは「実データ接続 完了（スライス1）」 | **doc 内部の新旧併記**。経路判断は冒頭ステータス + wiring tests を優先。全面 rewrite は本タスク外。 |
| first-open scroll fix（CLOSED）vs first-open performance（DEFERRED） | **別 node**。混同しない。 |
| NEXT TRUNK は TRUNK-06 で決定済み | 2026-09-20 以前の「UNKNOWN / TO DECIDE」は解消。 |

記録時点で、経路決定を止める未 reconcile の blocker は **なし**。

---

## 12. 変更履歴（本ファイル）

| 日付 | 内容 |
|------|------|
| 2026-09-20 | 初版。Task Tree ルール + CURRENT PATH（HEAD `dffeb8e`）を記録。 |
| 2026-09-20 | **TRUNK-06** Launch / Demo / New-user Readiness を ACTIVE 本線に設定。CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01`。 |
| 2026-09-20 | **BR-LAUNCH-01-A** New User Empty-State Contract ACTIVE。CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-A`。契約: 空≠デモ / Option B。 |
| 2026-09-20 | BT unset Settings hydrate fix commit `6ee7d3b` + prod deploy。01-A は **ACTIVE / Human Smoke pending**（CLOSED にしない）。 |
| 2026-09-20 | **BR-LAUNCH-01-B** New User Smoke Reset / Account Reuse ACTIVE。01-A → PAUSED。CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-B`。 |
| 2026-09-20 | **BR-LAUNCH-01-B Phase 1** Admin Reset API + tests + Smoke Reset ops（Founder UI 未着手・未 commit）。 |

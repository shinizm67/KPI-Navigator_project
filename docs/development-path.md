# KPN Development Path（Task Tree）

**役割:** 本線 / 岐路 / 派生枝 / 復帰先の正本。古いチャットを掘らなくても現在地を復元する。  
**対象読者:** Case / Cursor / Codex / Shin  
**作成日:** 2026-09-20  
**更新ルール:** 新しい岐路を発見したらコードより先に本ファイルへ記録する。CLOSED node は削除しない。

---

## CURRENT PATH

```
CURRENT PATH:
TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-C -> BR-LAUNCH-01-C2

PRIOR TRUNK (CLOSED):
Unit 5B -> Unit 5C -> Floating Window Functional Audit
-> Planning Readiness -> Automatic Seasonality / Baseline
-> UI/UX branches closeout

ACTIVE BRANCHES:
- BR-LAUNCH-01 (Demo / New User State) P0
- BR-LAUNCH-01-C (Demo Seed / Demo Reset) P0
- BR-LAUNCH-01-C1 (Demo Dataset Contract & Existing Fixture Audit) P0
- BR-LAUNCH-01-C2 (Demo Operation Pack) P0
- BR-LAUNCH-01-C2-C (Cross-Tab Account Session Collision) P0

CLOSED (under BR-LAUNCH-01):
- BR-LAUNCH-01-A (New User Empty-State Contract) P0 — closed 2026-09-20
- BR-LAUNCH-01-B (New User Smoke Reset / Account Reuse) P0 — closed 2026-09-20

CLOSED (under BR-LAUNCH-01-C):
- BR-LAUNCH-01-C0 (Founder Pro + Demo Account Setup) P0 — closed 2026-09-20
- BR-LAUNCH-01-C2-A (Annual TW Content Missing) P0 — closed 2026-09-20
- BR-LAUNCH-01-C2-B (Sales Data Target Tab Layout Gap) P0 — closed 2026-09-20
- BR-LAUNCH-01-C2-D (Sales Data Annual Target Edit-State UX) P1 — closed 2026-09-20
- BR-LAUNCH-01-C2-E (Sales Data Unsaved Alert + Enter Commit UX) P1 — closed 2026-09-21
- BR-LAUNCH-01-C2-F (Global Editable Grid Keyboard Navigation — Wraparound) P1 — closed 2026-09-21

PAUSED (under TRUNK-06):
- BR-LAUNCH-02 Production Smoke / Operational Runbook P1
- BR-LAUNCH-03 UI Consistency Audit P1
- BR-LAUNCH-04 PL Editable Cell Visual Finish P1

DEFERRED:
- BR-LAUNCH-05 Registration / Billing Readiness Assessment P1
  note: Stripe / billing は外部条件を含むため実装本線にせず assessment に留める
- BR-UI-PL-INSIGHT-FIRSTOPEN-PERF P3
  return when: Final Performance / Speed Optimization phase

RETURN TARGET:
BR-LAUNCH-01-C2 → BR-LAUNCH-01-C → BR-LAUNCH-01 → TRUNK-06

NEXT ACTION:
BR-LAUNCH-01-C2 — Demo Import Smoke（C2-F Wraparound CLOSED → return）
```

### Git snapshot（経路記録時点）

| 項目 | 値 |
|------|-----|
| git branch | `wip/unit5b-pl-mep-preset-engine-20260916` |
| HEAD | （wrap commit SHA） |
| origin sync | （都度確認） |
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
| next_action | `BR-LAUNCH-01-C` Demo Seed / Demo Reset（監査・設計） |
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
| next_action | `BR-LAUNCH-01-C` ACTIVE。Demo Seed / Reset 監査→実装 |

### BR-LAUNCH-01-A

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-A` |
| name | New User Empty-State Contract |
| parent | `BR-LAUNCH-01` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01` |
| reason | 新規ユーザー empty ≠ デモ。Option B BT unset。PR empty = NOT_READY |
| evidence | automated tests; production Human Smoke ALL PASS（BT unset / Annual·Monthly·PL empty / PR NOT_READY / no target amber / Pro·MEP·PL / no fake money）; BT Settings hydrate `6ee7d3b` |
| next_action | N/A（CLOSED） |
| contract | 空≠デモ; `—`=未定義; `0`=定義済みゼロ; PR empty=NOT_READY; BT Option B; 数値契約は言語/plan/theme共通 |

### BR-LAUNCH-01-B

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-B` |
| name | New User Smoke Reset / Account Reuse |
| parent | `BR-LAUNCH-01` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-A` |
| reason | 同一 Smoke 専用アカウントを毎回 emptyStore / BT 未設定の新規同等状態へ戻して再利用する |
| evidence | production Reset API `d2a9f39`; target-only wipe; session revoke; `__KPI_AUTH.clearUserScopedLocalData` → logout → same-account re-login Human Smoke PASS; Pro 維持 |
| next_action | N/A（CLOSED） |
| target_account | `kpn_empty_state_smoke01@trial.forge-laboratory.com` |
| phase1 | Admin Reset API `api/v1/admin/reset-user-kpi.php` + tests + ops docs（Founder UI なし） |
| phase2_candidate | Founder Console Reset UI |
| browser_cleanup | `window.__KPI_AUTH.clearUserScopedLocalData()` → logout → login（UI logout のみでは LS 残存。`KpiAuthClient` は誤り） |

### BR-LAUNCH-01-C

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C` |
| name | Demo Seed / Demo Reset |
| parent | `BR-LAUNCH-01` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01` |
| reason | New User Empty-State / Smoke Reset が CLOSED。再現可能なデモ状態を正式に定義・実装する |
| evidence | 01-A/01-B CLOSED; New User Reset ≠ Demo Reset; 監査: wipe API のみ（他user store inject API なし）; meal/customers は `years[].dailyMeal`（daily-inputs は sales/BD のみ）; 素材 `excel/*_official*` + `tests/generated-fixtures/`; Founder User Detail が将来 UI 候補 |
| next_action | C2 Demo Operation Pack 設計・監査（Reset + Sales/Expenses CSV） |
| constraint | 一般ユーザー UI に出さない（Founder/Admin 第一候補）。random 禁止。01-B empty reset と分離 |
| audit_note | Demo Reset = wipe（reuse `reset-user-kpi`）→ apply seed → `__KPI_AUTH.clear` → re-login |
| confirmed_v1 | loader+dataset; restaurant; Pro; JPY; 2 past + operating; deterministic; Founder/Admin only |
| accounts | Founder Pro + Demo Basic/Pro（同一 dataset・plan差のみ）。C0 で準備 |

### BR-LAUNCH-01-C2-F

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-F` |
| name | Global Editable Grid Keyboard Navigation |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-21 |
| reopened_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | Human Smokeで端停止を確認。Enter/Tab/Shift+Enter/Shift+Tab の wraparound 契約を追加 |
| evidence | helper=`bindGridKeys` + matrix wrap。Sales/Past/Annual/MEP/PL logical adapters。smoke Enter/Shift+Enter/Tab/Shift+Tab 完全循環 PASS |
| next_action | N/A（CLOSED）→ return BR-LAUNCH-01-C2 → Demo Import Smoke |
| constraint | Enter≠Save / Space native / OCC·lease·calc·excel 禁止 |

### BR-LAUNCH-01-C2-E

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-E` |
| name | Sales Data Unsaved Alert + Enter Commit UX |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | 閲覧切替後の未保存closeで lease-lost 文言が出る。年間目標/売上セルで Enter 確定できない |
| evidence | fix=`rejectSalesDataSaveNotLive` で foreign lease vs 自タブ閲覧を分離。Enter=`bindSalesAmountZeroClearUx` に keydown→blur。lease/OCC/Save意味非変更。JP/EN/ZH-TW |
| next_action | N/A（CLOSED）→ return BR-LAUNCH-01-C2 |
| constraint | save/OCC/lease logic / 計算 / import / excel 禁止 |

### BR-LAUNCH-01-C2-D

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-D` |
| name | Sales Data Annual Target Edit-State UX |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | 閲覧モードでも年間目標が入力可能に見え、編集切替でも見た目が変わらない |
| evidence | fix=`applySalesDataGuards` が summary panel + `#sales-data-summary-reference` を Past Sales 同型で guard。dim=`summary--path-blocked` opacity、active=`--sdm-bg-active-55/70`、dirty listener は readOnly/disabled で early return。local smoke JP/EN/ZH-TW × Sci-Fi/Office PASS |
| next_action | N/A（CLOSED）→ return BR-LAUNCH-01-C2 |
| constraint | save logic / 計算 / import / excel 禁止 |

### BR-LAUNCH-01-C2-C

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-C` |
| name | Cross-Tab Account Session Collision |
| parent | `BR-LAUNCH-01-C2` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | 同一 Chrome profile で複数 account tab を開くと、後からの login が他 tab の identity を上書き。Sales Data で編集権移動アラート |
| evidence | Cookie `KPISESSID` path=/ が profile 共有（login が session user を上書き）。LS `lastKpiUserId` + store も profile 共有。編集権は LS `kpiEditLeases`（ブラウザ全体1 lease）。年次目標 save 失敗は lease lost の SECONDARY。concurrent multi-account は未サポート契約 |
| next_action | Case判断: Bug扱いせず運用制約（別 profile / Incognito）とするか、将来 session redesign を DEFER するか |
| constraint | auth architecture / session redesign / Sales save / OCC / runtime 変更禁止（本ノードは audit） |

### BR-LAUNCH-01-C2-B

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-B` |
| name | Sales Data Target Tab Layout Gap |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | Demo Pro Human Smoke で Sales Data FW 目標売上 tab に巨大な不要空白を発見 |
| evidence | OSB host 残留が原因。fix=tab 時 inactive `.kpn-osb-host:has(#sales-data-pane-*)` を display:none（JP/EN/ZH-TW）。local smoke gap=0 × Sci-Fi/Office roundtrip PASS。OSB JS 非変更 |
| next_action | N/A（CLOSED）→ return BR-LAUNCH-01-C2 |
| constraint | OSB JS / calc / TW / excel 非変更 |

### BR-LAUNCH-01-C2-A

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-A` |
| name | Annual TW Content Missing |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | Demo Pro Human Smoke で Annual TW body missing を発見 |
| evidence | root=`153484e` Graph1 `buildDemoPayload`→未定義 `buildEmptyTrendPayload`。fix=Graph1 scope に同関数追加（JP/EN/ZH-TW）。local smoke: pageerror0 / renderFn / 57rows / wrapなし |
| next_action | N/A（CLOSED）→ return BR-LAUNCH-01-C2 |
| constraint | Monthly / OSB / TW sizing / excel 非変更 |

### BR-LAUNCH-01-C2

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2` |
| name | Demo Operation Pack |
| parent | `BR-LAUNCH-01-C` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | 営業が短時間で再現できる 3 点セット（Demo Reset / Sales CSV / Expenses CSV） |
| evidence | fixtures/demo/restaurant-v1 固定 CSV 作成済（integrity OK）。docs/demo-operation-pack.md。Reset=reuse reset-user-kpi。runtime 生成ロジックなし |
| next_action | C2-A 解消後 → Human Import Smoke（Demo Basic Sales / Demo Pro Sales+Expenses）→ C2 CLOSE 判断 |
| pack | Reset + sales_2024|2025|2026 + expenses daily/monthly |
| demo_basic | `kpn_demo_restaurant_basic01@…` / `u_7aac8cb5cbb0f607` |
| demo_pro | `kpn_demo_restaurant_pro01@…` / `u_a57d33d6ae864d99` |

### BR-LAUNCH-01-C0

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C0` |
| name | Founder Pro + Demo Account Setup |
| parent | `BR-LAUNCH-01-C` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | Demo 運用前に Founder=PRO と Demo Basic/Pro 専用アカウントを確定・準備する |
| evidence | Founder `u_43e738560b91617f` plan=pro role=founder_superadmin; Demo Basic `u_7aac8cb5cbb0f607` plan=basic; Demo Pro `u_a57d33d6ae864d99` plan=pro。共用 dataset・plan差のみ。BT は seed 時 |
| next_action | N/A（CLOSED） |
| founder | `s.matsushita@forge-laboratory.com` |
| demo_basic | `kpn_demo_restaurant_basic01@trial.forge-laboratory.com` |
| demo_pro | `kpn_demo_restaurant_pro01@trial.forge-laboratory.com` |

### BR-LAUNCH-01-C1

| フィールド | 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C1` |
| name | Demo Dataset Contract & Existing Fixture Audit |
| parent | `BR-LAUNCH-01-C` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | Demo Seed API 前に generated-fixtures を監査し restaurant Demo v1 の deterministic dataset 正本を確定する |
| evidence | `tests/generated-fixtures/` = CSV smoke（`csv_smoke_fixture_generator.py`）。L/D 整合ありだが線形合成・休業日にも expense。plan/PR なし。昇格は PARTIAL |
| next_action | Case合意後 → C2 dataset 正本作成 or HOLD |
| constraint | runtime変更禁止; dataset生成禁止（本ノード）; excel untouched |

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
| `BR-LAUNCH-01-C` | Demo Seed / Demo Reset | ACTIVE | P0 | `BR-LAUNCH-01` |
| `BR-LAUNCH-01-C1` | Demo Dataset Contract & Existing Fixture Audit | ACTIVE | P0 | `BR-LAUNCH-01-C` |
| `BR-LAUNCH-01-C2` | Demo Operation Pack | ACTIVE | P0 | `BR-LAUNCH-01-C` |

CLOSED under `BR-LAUNCH-01`: `BR-LAUNCH-01-A`, `BR-LAUNCH-01-B`  
CLOSED under `BR-LAUNCH-01-C`: `BR-LAUNCH-01-C0`  
PAUSED under `TRUNK-06`: `BR-LAUNCH-02`, `BR-LAUNCH-03`, `BR-LAUNCH-04`  
DEFERRED under `TRUNK-06`: `BR-LAUNCH-05`
CLOSED under `BR-LAUNCH-01`: `BR-LAUNCH-01-A`, `BR-LAUNCH-01-B`  
PAUSED under `TRUNK-06`: `BR-LAUNCH-02`, `BR-LAUNCH-03`, `BR-LAUNCH-04`  
DEFERRED under `TRUNK-06`: `BR-LAUNCH-05`

---

## 10. UNKNOWN / OPEN QUESTIONS

| 項目 | 状態 |
|------|------|
| Unit 5C-3 / 5C-4 | marker・doc なし → **UNKNOWN** |
| Unit 5D 以降 | **UNKNOWN**（現本線は TRUNK-06） |
| FW Audit が全 Floating Window を網羅したか | 配線 tests は Daily / Top Insight / PL Insight のみ確認。それ以外の COMPLETE 宣言 doc なし → **UNKNOWN** |
| `TR-UNIT-5B` / `TR-UNIT-5C` の厳密な started_at | **UNKNOWN** |
| BR-LAUNCH-01 の詳細スコープ（画面・ストア・デモデータ） | Empty-State / Smoke Reset CLOSED。残件は `BR-LAUNCH-01-C` Demo Seed/Reset |
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
| 2026-09-20 | **BR-LAUNCH-01-B** Server Reset API commit/push/deploy `d2a9f39` PASS。Real Smoke で browser cleanup namespace mismatch 発見（`KpiAuthClient` 誤 → 正 `__KPI_AUTH`）。runtime 変更なし・docs のみ修正。 |
| 2026-09-20 | **BR-LAUNCH-01-B CLOSED**（Reset API + `__KPI_AUTH` cleanup + same-account Human Smoke PASS）。**BR-LAUNCH-01-A CLOSED**（empty-state Human Smoke ALL PASS）。CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01`。 |
| 2026-09-20 | **BR-LAUNCH-01-C** Demo Seed / Demo Reset ACTIVE。CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-C`。監査・設計のみ（runtime 未着手）。 |
| 2026-09-20 | **BR-LAUNCH-01-C1** Demo Dataset Contract & Fixture Audit ACTIVE。CURRENT PATH = `… -> BR-LAUNCH-01-C1`。generated-fixtures は smoke 用・Demo 正本へは PARTIAL。 |
| 2026-09-20 | **BR-LAUNCH-01-C0** Founder Pro + Demo Account Setup ACTIVE。CURRENT PATH = `… -> BR-LAUNCH-01-C0`。 |
| 2026-09-20 | **BR-LAUNCH-01-C0 CLOSED**。Founder plan=pro; Demo Basic/Pro 作成済。CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-C`。 |
| 2026-09-20 | **BR-LAUNCH-01-C2** Demo Operation Pack ACTIVE。CURRENT PATH = `… -> BR-LAUNCH-01-C2`。Reset+Sales/Expenses CSV 設計・監査のみ。 |
| 2026-09-20 | **BR-LAUNCH-01-C2** `fixtures/demo/restaurant-v1` 固定 CSV + `docs/demo-operation-pack.md` 作成。Human Import Smoke 待ち（未 commit）。 |

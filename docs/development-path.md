# KPN Development Path�E�Eask Tree�E�E

**役割:** 本緁E/ 岐路 / 派生枝 / 復帰先�E正本。古ぁE��ャチE��を掘らなくても現在地を復允E��る、E 
**対象読老E** Case / Cursor / Codex / Shin  
**作�E日:** 2026-09-20  
**更新ルール:** 新しい岐路を発見したらコードより�Eに本ファイルへ記録する、ELOSED node は削除しなぁE��E

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
- BR-LAUNCH-01-A (New User Empty-State Contract) P0  Eclosed 2026-09-20
- BR-LAUNCH-01-B (New User Smoke Reset / Account Reuse) P0  Eclosed 2026-09-20

CLOSED (under BR-LAUNCH-01-C):
- BR-LAUNCH-01-C0 (Founder Pro + Demo Account Setup) P0  Eclosed 2026-09-20
- BR-LAUNCH-01-C2-A (Annual TW Content Missing) P0  Eclosed 2026-09-20
- BR-LAUNCH-01-C2-B (Sales Data Target Tab Layout Gap) P0  Eclosed 2026-09-20
- BR-LAUNCH-01-C2-D (Sales Data Annual Target Edit-State UX) P1  Eclosed 2026-09-20
- BR-LAUNCH-01-C2-E (Sales Data Unsaved Alert + Enter Commit UX) P1  Eclosed 2026-09-21
- BR-LAUNCH-01-C2-F (Global Editable Grid Keyboard Navigation  EWraparound) P1  Eclosed 2026-09-21

PAUSED (under TRUNK-06):
- BR-LAUNCH-02 Production Smoke / Operational Runbook P1
- BR-LAUNCH-03 UI Consistency Audit P1
- BR-LAUNCH-04 PL Editable Cell Visual Finish P1

DEFERRED:
- BR-LAUNCH-05 Registration / Billing Readiness Assessment P1
  note: Stripe / billing は外部条件を含むため実裁E��線にせず assessment に留めめE
- BR-UI-PL-INSIGHT-FIRSTOPEN-PERF P3
  return when: Final Performance / Speed Optimization phase

RETURN TARGET:
BR-LAUNCH-01-C2 ↁEBR-LAUNCH-01-C ↁEBR-LAUNCH-01 ↁETRUNK-06

NEXT ACTION:
BR-LAUNCH-01-C2  EDemo Import Smoke�E�E2-F Wraparound CLOSED ↁEreturn�E�E
```

### Git snapshot�E�経路記録時点�E�E

| 頁E�� | 値 |
|------|-----|
| git branch | `wip/unit5b-pl-mep-preset-engine-20260916` |
| HEAD | �E�Erap commit SHA�E�E|
| origin sync | �E��E度確認！E|
| excel/ | user-owned dirty / **do not touch** |

---

## 1. Task Tree 概念�E�正本�E�E

| 用誁E| 意味 |
|------|------|
| **TRUNK** | 本線。製品�E主経路、E|
| **BRANCH** | 本線また�E別 branch から派生した岐路、E|
| **PARENT** | どこから派生したか�E�Eode id�E�、E|
| **RETURN TARGET** | branch 終亁E��に戻る場所�E�通常は TRUNK 上�E node / NEXT TRUNK�E�、E|

### STATUS

| 値 | 意味 |
|----|------|
| `ACTIVE` | ぁE��着手中 |
| `PAUSED` | 意図皁E��中断�E��E開条件あり�E�E|
| `DEFERRED` | 後回し（復帰条件を忁E��書く！E|
| `CLOSED` | 完亁E��削除しなぁE|
| `UNKNOWN` | 確証なし。推測で埋めなぁE|

### PRIORITY

| 値 | 意味 |
|----|------|
| `P0` | 本緁Eblocking |
| `P1` | 本線復帰前に閉じめE|
| `P2` | 関連してぁE��ので今やる価値あり |
| `P3` | polish / optimization / later |

---

## 2. Node 忁E��フィールチE

吁Enode に最低限:

| フィールチE| 説昁E|
|------------|------|
| `id` | 安宁EID�E�侁E `TR-UNIT-5C`, `BR-UI-OSB`�E�E|
| `name` | 人間可読吁E|
| `parent` | 派生�E node id�E�ERUNK 直下�E `TRUNK` 可�E�E|
| `status` | ACTIVE / PAUSED / DEFERRED / CLOSED / UNKNOWN |
| `priority` | P0–P3 |
| `started_at` | 開始日�E�EYYY-MM-DD�E�。不�EなめEUNKNOWN |
| `return_to` | 終亁E���E復帰允E|
| `reason` | なぜこの岐路/本線か |
| `evidence` | commit / docs / tests / deploy の根拠 |
| `next_action` | 次にめE��こと�E�ELOSED なめE`—`�E�E|

忁E��に応じて:

- `closed_at`
- `commit`
- `docs`
- `tests`
- `deploy`
- `reusable_pattern`

---

## 3. Operating Rule

### 岐路を発見したとぁE

すぐコードを書かなぁE���Eに本ファイルへ:

- `parent`
- `reason`
- `priority`
- `return_to`
- `status: ACTIVE`

を記録してから着手する、E

### branch を閉じるとぁE

- `status` ↁE`CLOSED`
- `closed_at`
- `commit`
- `tests`�E�あれ�E�E�E
- `deploy` evidence�E�あれ�E�E�E
- `return_to` を�E示

CLOSED node は **削除しなぁE*�E�履歴・再利用のため残す�E�、E

### Source of Truth

本ファイルは **開発経路の正本**、E

ただぁEcode / commit / test / deploy evidence と矛盾した場合�E、どちらかを勝手に採用しなぁE��E

1. 矛盾を報告すめE 
2. reconcile してから進む  

履歴に確証がなぁE��のは **UNKNOWN**。推測で埋めなぁE��E

---

## 4. New Chat Handoff Rule

新しい Cursor / Case / Codex chat は **最初に本ファイルを読む**、E

実裁E��に最低限確誁E

1. Current trunk  
2. Current active path  
3. Active branches  
4. Deferred branches  
5. Return target  
6. Next confirmed task  
7. branch / HEAD / origin sync  
8. uncommitted mainline work  

---

## 5. TRUNK nodes�E�本線履歴�E�E

確証のある頁E���Eみ。subunit の欠番�E�侁E 5C-3 / 5C-4�E��E UNKNOWN、E

### TR-UNIT-5B

| フィールチE| 値 |
|------------|-----|
| id | `TR-UNIT-5B` |
| name | Unit 5B  EPL/MEP Business Type preset engine |
| parent | `TRUNK`�E�Enit 5�E�E|
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN�E�Eranch 吁E`unit5b-...-20260916`�E�E|
| closed_at | UNKNOWN�E�EC へ移行。厳寁E��閉じ日は未記録�E�E|
| return_to | `TR-UNIT-5C` |
| reason | Business Type 向け expense preset / catalog エンジン |
| evidence | commits `f41e1f9` Add PL MEP business preset engine; `6fe3275` deferred classification; `7ba334d` PL Analyze BT; `cf7b67a` MEP preset sync; tests `_test_pl_mep_preset_engine.py`, `_test_business_expense_presets.py`, `_test_pl_analysis_business_type.py` |
| next_action |  E|
| note | git branch 名�EぁE��めEunit5b。経路上�E 5C へ進んだ�E�命名ラグ。矛盾ではなく記録上�E遁E���E�、E|

### TR-UNIT-5C

| フィールチE| 値 |
|------------|-----|
| id | `TR-UNIT-5C` |
| name | Unit 5C  EBusiness Type surface adaptation |
| parent | `TR-UNIT-5B` |
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN |
| closed_at | 2026-09�E�Elose tests: `3f35989`, `f609d32`�E�E|
| return_to | `TR-FW-AUDIT` |
| reason | PL Insight / Insight Summary / Monthly TW / MEP meal めEBT に合わせる |
| evidence | markers `UNIT-5C-1`…`5C-2`…`5C-5`…`5C-6`; commits `9ca3ab0`, `f179989`, `ab4fa9f`, `0249724`, `3f35989`, `f609d32`; tests `_test_pl_insight_finalization.py`, `_test_monthly_tw_business_type.py`, `_test_mep_meal_business_type.py` |
| next_action |  E|
| unknown | `5C-3` / `5C-4` の marker・doc は repo に無ぁEↁE**UNKNOWN�E�欠番か未作�Eか未確定！E* |

### TR-FW-AUDIT

| フィールチE| 値 |
|------------|-----|
| id | `TR-FW-AUDIT` |
| name | Floating Window Functional Audit |
| parent | `TR-UNIT-5C` |
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN |
| closed_at | 2026-09-19 前後！Eiring tests�E�E|
| return_to | `TR-PLANNING-READINESS` |
| reason | FW のチE�Eタ配線を contract test で固定し、本線を閉じめE|
| evidence | `e2fc0ac` Daily FW wiring; `10f5495` Top Insight wiring; `f609d32` PL Insight wiring close prep; `3f35989` Unit 5C close tests |
| next_action |  E|
| note | 「一通り完亁E���E `docs/planning-readiness.md` 初版�E�E138edd1`�E��E実裁E��イミング記述と整合。�E FW の COMPLETE 一覧 doc は無ぁEↁE個別 FW の完�E網羁E�E UNKNOWN、E|

### TR-PLANNING-READINESS

| フィールチE| 値 |
|------------|-----|
| id | `TR-PLANNING-READINESS` |
| name | Planning Readiness / KPI Setup Status |
| parent | `TR-FW-AUDIT` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-19 |
| closed_at | 2026-09-19、E0�E�本佁E+ Amber/Gold visual�E�E|
| return_to | `TRUNK-06`�E�後続本線�E2026-09-20 決定！E|
| reason | 暫定目標と確定目標を刁E��、EW Audit 後�E独立本線タスク |
| evidence | `138edd1` doc; `a260227` implementation; `docs/planning-readiness.md`; `js/kpi-planning-readiness.js`; `_test_planning_readiness.py` |
| next_action |  E|
| docs | [`planning-readiness.md`](./planning-readiness.md) |

### TR-SEASONALITY-BASELINE

| フィールチE| 値 |
|------------|-----|
| id | `TR-SEASONALITY-BASELINE` |
| name | Automatic Seasonality / Baseline-Year Contract |
| parent | `TR-PLANNING-READINESS` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-19 |
| closed_at | 2026-09-19 |
| return_to | UI/UX polish branches ↁEそ�E征ETRUNK |
| reason | Recommended seasonality / baseline years / anomaly flag |
| evidence | `474ec5f`, `4733b57`, `fbe7a48`, `43fbfe2`; `js/kpi-seasonality-allocator.js`; `docs/planning-readiness.md` スチE�Eタス衁E|
| next_action |  E|

### TR-UIUX-CLOSEOUT

| フィールチE| 値 |
|------------|-----|
| id | `TR-UIUX-CLOSEOUT` |
| name | UI/UX branches close�E�Eales Data / Past Sales / Overlay / Amber�E�E|
| parent | `TR-SEASONALITY-BASELINE` |
| status | CLOSED |
| priority | P1〜P3�E�各孁Enode 参�E�E�E|
| started_at | 2026-09-19、E0 |
| closed_at | 2026-09-20�E�Edffeb8e`�E�E|
| return_to | `TRUNK-06` |
| reason | 視認性・scrollbar・PROVISIONAL warning の岐路を閉じ本線へ戻ぁE|
| evidence | 下訁ECLOSED BRANCHES |
| next_action |  E|

---

## 6. CLOSED BRANCHES�E�EI/UX 岐路�E�E

### BR-UI-SALES-DATA-HIERARCHY

| フィールチE| 値 |
|------------|-----|
| id | `BR-UI-SALES-DATA-HIERARCHY` |
| name | Sales Data UI hierarchy |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P2 |
| started_at | UNKNOWN |
| closed_at | 2026-09-20 前征E|
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | readonly / active / closed-day 可読性 |
| evidence | commits `b613297`, `a22a5cf`, `a8762ed`, `5987de7` |
| next_action |  E|

### BR-UI-PAST-SALES-HIERARCHY

| フィールチE| 値 |
|------------|-----|
| id | `BR-UI-PAST-SALES-HIERARCHY` |
| name | Past Sales UI hierarchy |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P2 |
| started_at | UNKNOWN |
| closed_at | 2026-09-20 前征E|
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | Past Sales めESales Data 視認性と揁E��めE|
| evidence | commits `a937550`, `ce9ae34`, `a443802` |
| next_action |  E|

### BR-UI-OVERLAY-SCROLLBAR

| フィールチE| 値 |
|------------|-----|
| id | `BR-UI-OVERLAY-SCROLLBAR` |
| name | Overlay Scrollbar UX |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 前征E|
| closed_at | 2026-09-20 |
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | 共送Eoverlay scrollbar 標準化 |
| evidence | `b18c7a3`; `docs/kpn-scrollbar-ux-contract.md`; `js/kpi-overlay-scrollbar.js` |
| deploy | production 反映済み�E�後綁Ehotfix 含む�E�E|
| reusable_pattern | shared OSB host wrap + Mac native opt-out |
| next_action |  E|

### BR-UI-ANNUAL-TW-OSB

| フィールチE| 値 |
|------------|-----|
| id | `BR-UI-ANNUAL-TW-OSB` |
| name | Annual TW dedicated overlay adapter |
| parent | `BR-UI-OVERLAY-SCROLLBAR` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-UI-OVERLAY-SCROLLBAR` |
| reason | Annual TW は wrap しなぁE��用 overlay |
| evidence | `bfad0bf`; `js/kpi-annual-tw-overlay-scrollbar.js` |
| next_action |  E|

### BR-UI-INSIGHT-PL-OSB-REGRESSION

| フィールチE| 値 |
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
| next_action |  E|
| note | first-open **scroll** 修正は CLOSED。first-open **performance** は別 DEFERRED node、E|

### BR-UI-MONTHLY-TW-HSCROLL

| フィールチE| 値 |
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
| reason | box-style absolute に residual inset を誤コピ�EしてぁE�� |
| evidence | `2abc23c`; `js/kpi-overlay-scrollbar.js`�E�EnsetPort vs box-style�E�E|
| deploy | production PASS�E�EETR/SHA�E�E|
| next_action |  E|

### BR-UI-PR-AMBER-GOLD

| フィールチE| 値 |
|------------|-----|
| id | `BR-UI-PR-AMBER-GOLD` |
| name | Amber/Gold Planning Readiness warning |
| parent | `TR-PLANNING-READINESS` |
| status | CLOSED |
| priority | P2 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| commit | `dffeb8e` |
| return_to | `TRUNK-06`�E�EI/UX closeout 後�E本線！E|
| reason | PROVISIONAL 目標売上を bright orange から dark amber/gold へ |
| evidence | `dffeb8e`; `js/kpi-planning-readiness.js`; `_test_planning_readiness.py` 117 passed; deploy 7/7 |
| docs | [`planning-readiness.md`](./planning-readiness.md) §9.1 |
| next_action |  E|

---

## 7. ACTIVE TRUNK  ETRUNK-06 Launch / Demo / New-user Readiness

### TRUNK-06

| フィールチE| 値 |
|------------|-----|
| id | `TRUNK-06` |
| name | Launch / Demo / New-user Readiness |
| parent | KPN Development |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | N/A |
| reason | Unit 5C / Floating Window Functional Audit / Planning Readiness / Automatic Seasonality / 主要EUI/UX closeout が完亁E��、KPN を「開発中」から「安�Eに人へ見せ、使わせられる状態」へ移行するため、E|
| evidence | `docs/development-path.md` Next Trunk Selection Audit�E�E026-09-20�E�E HEAD `dffeb8e` UI/UX closeout; Shin/Case 決定で本線開姁E|
| next_action | `BR-LAUNCH-01-C` Demo Seed / Demo Reset�E�監査・設計！E|
| docs | [`free-trial-account-ops.md`](./free-trial-account-ops.md)�E��E币E��用・関連�E�E|

### BR-LAUNCH-01

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01` |
| name | Demo / New User State |
| parent | `TRUNK-06` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | 新規�EチE��利用老E��壊れなぁE�E期状態�E導線を確定すめE|
| evidence | TRUNK-06 開始決定！E026-09-20�E�E|
| next_action | `BR-LAUNCH-01-C` ACTIVE、Eemo Seed / Reset 監査→実裁E|

### BR-LAUNCH-01-A

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-A` |
| name | New User Empty-State Contract |
| parent | `BR-LAUNCH-01` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01` |
| reason | 新規ユーザー empty ≠ チE��。Option B BT unset。PR empty = NOT_READY |
| evidence | automated tests; production Human Smoke ALL PASS�E�ET unset / Annual·Monthly·PL empty / PR NOT_READY / no target amber / Pro·MEP·PL / no fake money�E�E BT Settings hydrate `6ee7d3b` |
| next_action | N/A�E�ELOSED�E�E|
| contract | 空≠チE��; `—`=未定義; `0`=定義済みゼロ; PR empty=NOT_READY; BT Option B; 数値契紁E�E言誁Eplan/theme共送E|

### BR-LAUNCH-01-B

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-B` |
| name | New User Smoke Reset / Account Reuse |
| parent | `BR-LAUNCH-01` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-A` |
| reason | 同一 Smoke 専用アカウントを毎回 emptyStore / BT 未設定�E新規同等状態へ戻して再利用する |
| evidence | production Reset API `d2a9f39`; target-only wipe; session revoke; `__KPI_AUTH.clearUserScopedLocalData` ↁElogout ↁEsame-account re-login Human Smoke PASS; Pro 維持E|
| next_action | N/A�E�ELOSED�E�E|
| target_account | `kpn_empty_state_smoke01@trial.forge-laboratory.com` |
| phase1 | Admin Reset API `api/v1/admin/reset-user-kpi.php` + tests + ops docs�E�Eounder UI なし！E|
| phase2_candidate | Founder Console Reset UI |
| browser_cleanup | `window.__KPI_AUTH.clearUserScopedLocalData()` ↁElogout ↁElogin�E�EI logout のみでは LS 残存。`KpiAuthClient` は誤り！E|

### BR-LAUNCH-01-C

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C` |
| name | Demo Seed / Demo Reset |
| parent | `BR-LAUNCH-01` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01` |
| reason | New User Empty-State / Smoke Reset ぁECLOSED。�E現可能なチE��状態を正式に定義・実裁E��めE|
| evidence | 01-A/01-B CLOSED; New User Reset ≠ Demo Reset; 監査: wipe API のみ�E�他user store inject API なし！E meal/customers は `years[].dailyMeal`�E�Eaily-inputs は sales/BD のみ�E�E 素杁E`excel/*_official*` + `tests/generated-fixtures/`; Founder User Detail が封E�� UI 候裁E|
| next_action | C2 Demo Operation Pack 設計�E監査�E�Eeset + Sales/Expenses CSV�E�E|
| constraint | 一般ユーザー UI に出さなぁE��Eounder/Admin 第一候補）。random 禁止、E1-B empty reset と刁E�� |
| audit_note | Demo Reset = wipe�E�Eeuse `reset-user-kpi`�E��E apply seed ↁE`__KPI_AUTH.clear` ↁEre-login |
| confirmed_v1 | loader+dataset; restaurant; Pro; JPY; 2 past + operating; deterministic; Founder/Admin only |
| accounts | Founder Pro + Demo Basic/Pro�E�同一 dataset・plan差のみ�E�、E0 で準備 |

### BR-LAUNCH-01-C2-F

| フィールチE| 値 |
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
| reason | Human Smokeで端停止を確認、Enter/Tab/Shift+Enter/Shift+Tab の wraparound 契紁E��追加 |
| evidence | helper=`bindGridKeys` + matrix wrap。Sales/Past/Annual/MEP/PL logical adapters。smoke Enter/Shift+Enter/Tab/Shift+Tab 完�E循環 PASS |
| next_action | N/A�E�ELOSED�E��E return BR-LAUNCH-01-C2 ↁEDemo Import Smoke |
| constraint | Enter≠Save / Space native / OCC·lease·calc·excel 禁止 |

### BR-LAUNCH-01-C2-E

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-E` |
| name | Sales Data Unsaved Alert + Enter Commit UX |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | 閲覧刁E��後�E未保存closeで lease-lost 斁E��が�Eる。年間目樁E売上セルで Enter 確定できなぁE|
| evidence | fix=`rejectSalesDataSaveNotLive` で foreign lease vs 自タブ閲覧を�E離、Enter=`bindSalesAmountZeroClearUx` に keydown→blur。lease/OCC/Save意味非変更、EP/EN/ZH-TW |
| next_action | N/A�E�ELOSED�E��E return BR-LAUNCH-01-C2 |
| constraint | save/OCC/lease logic / 計箁E/ import / excel 禁止 |

### BR-LAUNCH-01-C2-D

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-D` |
| name | Sales Data Annual Target Edit-State UX |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | 閲覧モードでも年間目標が入力可能に見え、編雁E�E替でも見た目が変わらなぁE|
| evidence | fix=`applySalesDataGuards` ぁEsummary panel + `#sales-data-summary-reference` めEPast Sales 同型で guard。dim=`summary--path-blocked` opacity、active=`--sdm-bg-active-55/70`、dirty listener は readOnly/disabled で early return。local smoke JP/EN/ZH-TW ÁESci-Fi/Office PASS |
| next_action | N/A�E�ELOSED�E��E return BR-LAUNCH-01-C2 |
| constraint | save logic / 計箁E/ import / excel 禁止 |

### BR-LAUNCH-01-C2-C

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-C` |
| name | Cross-Tab Account Session Collision |
| parent | `BR-LAUNCH-01-C2` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | 同一 Chrome profile で褁E�� account tab を開くと、後から�E login が仁Etab の identity を上書き。Sales Data で編雁E��移動アラーチE|
| evidence | Cookie `KPISESSID` path=/ ぁEprofile 共有！Eogin ぁEsession user を上書き）、ES `lastKpiUserId` + store めEprofile 共有。編雁E��は LS `kpiEditLeases`�E�ブラウザ全佁E lease�E�。年次目樁Esave 失敗�E lease lost の SECONDARY。concurrent multi-account は未サポ�Eト契紁E|
| next_action | Case判断: Bug扱ぁE��ず運用制紁E��別 profile / Incognito�E�とするか、封E�� session redesign めEDEFER するぁE|
| constraint | auth architecture / session redesign / Sales save / OCC / runtime 変更禁止�E�本ノ�Eド�E audit�E�E|

### BR-LAUNCH-01-C2-B

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-B` |
| name | Sales Data Target Tab Layout Gap |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | Demo Pro Human Smoke で Sales Data FW 目標売丁Etab に巨大な不要空白を発要E|
| evidence | OSB host 残留が原因。fix=tab 晁Einactive `.kpn-osb-host:has(#sales-data-pane-*)` めEdisplay:none�E�EP/EN/ZH-TW�E�。local smoke gap=0 ÁESci-Fi/Office roundtrip PASS。OSB JS 非変更 |
| next_action | N/A�E�ELOSED�E��E return BR-LAUNCH-01-C2 |
| constraint | OSB JS / calc / TW / excel 非変更 |

### BR-LAUNCH-01-C2-A

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2-A` |
| name | Annual TW Content Missing |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | Demo Pro Human Smoke で Annual TW body missing を発要E|
| evidence | root=`153484e` Graph1 `buildDemoPayload`→未定義 `buildEmptyTrendPayload`。fix=Graph1 scope に同関数追加�E�EP/EN/ZH-TW�E�。local smoke: pageerror0 / renderFn / 57rows / wrapなぁE|
| next_action | N/A�E�ELOSED�E��E return BR-LAUNCH-01-C2 |
| constraint | Monthly / OSB / TW sizing / excel 非変更 |

### BR-LAUNCH-01-C2

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C2` |
| name | Demo Operation Pack |
| parent | `BR-LAUNCH-01-C` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | 営業が短時間で再現できる 3 点セチE���E�Eemo Reset / Sales CSV / Expenses CSV�E�E|
| evidence | fixtures/demo/restaurant-v1 固宁ECSV 作�E済！Entegrity OK�E�。docs/demo-operation-pack.md。Reset=reuse reset-user-kpi。runtime 生�EロジチE��なぁE|
| next_action | C2-A 解消征EↁEHuman Import Smoke�E�Eemo Basic Sales / Demo Pro Sales+Expenses�E��E C2 CLOSE 判断 |
| pack | Reset + sales_2024|2025|2026 + expenses daily/monthly |
| demo_basic | `kpn_demo_restaurant_basic01@…` / `u_7aac8cb5cbb0f607` |
| demo_pro | `kpn_demo_restaurant_pro01@…` / `u_a57d33d6ae864d99` |

### BR-LAUNCH-01-C0

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C0` |
| name | Founder Pro + Demo Account Setup |
| parent | `BR-LAUNCH-01-C` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | Demo 運用前に Founder=PRO と Demo Basic/Pro 専用アカウントを確定�E準備する |
| evidence | Founder `u_43e738560b91617f` plan=pro role=founder_superadmin; Demo Basic `u_7aac8cb5cbb0f607` plan=basic; Demo Pro `u_a57d33d6ae864d99` plan=pro。�E用 dataset・plan差のみ、ET は seed 晁E|
| next_action | N/A�E�ELOSED�E�E|
| founder | `s.matsushita@forge-laboratory.com` |
| demo_basic | `kpn_demo_restaurant_basic01@trial.forge-laboratory.com` |
| demo_pro | `kpn_demo_restaurant_pro01@trial.forge-laboratory.com` |

### BR-LAUNCH-01-C1

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-01-C1` |
| name | Demo Dataset Contract & Existing Fixture Audit |
| parent | `BR-LAUNCH-01-C` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | Demo Seed API 前に generated-fixtures を監査ぁErestaurant Demo v1 の deterministic dataset 正本を確定すめE|
| evidence | `tests/generated-fixtures/` = CSV smoke�E�Ecsv_smoke_fixture_generator.py`�E�、E/D 整合ありだが線形合�E・休業日にめEexpense。plan/PR なし。�E格は PARTIAL |
| next_action | Case合意征EↁEC2 dataset 正本作�E or HOLD |
| constraint | runtime変更禁止; dataset生�E禁止�E�本ノ�Eド！E excel untouched |

### BR-LAUNCH-02

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-02` |
| name | Production Smoke / Operational Runbook |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | 本番スモークと運用手頁E�E固宁E|
| evidence | TRUNK-06 child�E�EAUSED until BR-LAUNCH-01�E�E|
| next_action | BR-LAUNCH-01 完亁E��に ACTIVE 化を検訁E|

### BR-LAUNCH-03

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-03` |
| name | UI Consistency Audit |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | Annual / Monthly / FW 横断の見た目・挙動一貫性 |
| evidence | TRUNK-06 child�E�EAUSED�E�E|
| next_action | スコープ確定後に ACTIVE |

### BR-LAUNCH-04

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-04` |
| name | PL Editable Cell Visual Finish |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | 入力可能セルの視覚�E示�E�緁E黒等）仕上げ |
| evidence | `pl-table-v1-implementation-spec.md`「Bの忁E��EX 未着手、E TRUNK-06 child�E�EAUSED�E�E|
| next_action | BR-LAUNCH-01 後に ACTIVE 化を検訁E|

### BR-LAUNCH-05

| フィールチE| 値 |
|------------|-----|
| id | `BR-LAUNCH-05` |
| name | Registration / Billing Readiness Assessment |
| parent | `TRUNK-06` |
| status | DEFERRED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | 公開登録再開と課金�E readiness 評価。Stripe / billing は外部条件を含むため、現時点では実裁E��線にせず assessment に留める、E|
| evidence | commit `af07bf7` Disable public registration until billing is ready; `free-trial-account-ops.md`�E�EillingType 未実裁E��E|
| next_action | 外部条件�E�Etripe / サポ�Eト体制�E�が揁E��たら assessment ↁE実裁E��否を�E判宁E|
| note | **実裁E��線にしなぁE*�E�Eeadiness assessment only�E�、E|

---

## 8. DEFERRED BRANCHES�E�既存！E

### BR-UI-PL-INSIGHT-FIRSTOPEN-PERF

| フィールチE| 値 |
|------------|-----|
| id | `BR-UI-PL-INSIGHT-FIRSTOPEN-PERF` |
| name | PL Insight first-open performance |
| parent | `BR-UI-INSIGHT-PL-OSB-REGRESSION`�E�関連�E�E/ 製品上�E PL Insight |
| status | DEFERRED |
| priority | P3 |
| started_at | UNKNOWN�E�課題認識�Eみ�E�E|
| return_to | Final Performance / Speed Optimization phase |
| reason | first-open の体感速度。scroll 不�E回帰�E�E058b9cd`�E�とは別課顁E|
| evidence | Case 確定状態！E026-09-20 Current Position�E�：P3 deferred |
| next_action | Performance phase 開始時に ACTIVE へ昁E��するか�E評価 |

---

## 9. ACTIVE BRANCHES�E�一覧�E�E

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

| 頁E�� | 状慁E|
|------|------|
| Unit 5C-3 / 5C-4 | marker・doc なぁEↁE**UNKNOWN** |
| Unit 5D 以陁E| **UNKNOWN**�E�現本線�E TRUNK-06�E�E|
| FW Audit が�E Floating Window を網羁E��たか | 配緁Etests は Daily / Top Insight / PL Insight のみ確認。それ以外�E COMPLETE 宣言 doc なぁEↁE**UNKNOWN** |
| `TR-UNIT-5B` / `TR-UNIT-5C` の厳寁E�� started_at | **UNKNOWN** |
| BR-LAUNCH-01 の詳細スコープ（画面・ストア・チE��チE�Eタ�E�E| Empty-State / Smoke Reset CLOSED。残件は `BR-LAUNCH-01-C` Demo Seed/Reset |
| BT Option C 全面ゲーチE| **DEFERRED**�E�E1-A は Option B�E�E|

---

## 11. Contradictions / Notes�E�Eeconcile ログ�E�E

| 観寁E| 扱ぁE|
|------|------|
| git branch 名が `unit5b` のままだが経路は 5C・そ�E後�ETRUNK-06 へ進んでぁE�� | **命名ラグ**。�E容矛盾ではなぁE��本ファイルに明記、E|
| `pl-insight-final-adjustments-memo.md` 旧節に「モチE��」記述が残る一方、�E頭スチE�Eタスは「実データ接綁E完亁E��スライス1�E�、E| **doc 冁E��の新旧併訁E*。経路判断は冒頭スチE�Eタス + wiring tests を優先。�E面 rewrite は本タスク外、E|
| first-open scroll fix�E�ELOSED�E�vs first-open performance�E�EEFERRED�E�E| **別 node**。混同しなぁE��E|
| NEXT TRUNK は TRUNK-06 で決定済み | 2026-09-20 以前�E「UNKNOWN / TO DECIDE」�E解消、E|

記録時点で、経路決定を止める未 reconcile の blocker は **なぁE*、E

---

## 12. 変更履歴�E�本ファイル�E�E

| 日仁E| 冁E�� |
|------|------|
| 2026-09-20 | 初版。Task Tree ルール + CURRENT PATH�E�EEAD `dffeb8e`�E�を記録、E|
| 2026-09-20 | **TRUNK-06** Launch / Demo / New-user Readiness めEACTIVE 本線に設定、EURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01`、E|
| 2026-09-20 | **BR-LAUNCH-01-A** New User Empty-State Contract ACTIVE、EURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-A`。契紁E 空≠チE�� / Option B、E|
| 2026-09-20 | BT unset Settings hydrate fix commit `6ee7d3b` + prod deploy、E1-A は **ACTIVE / Human Smoke pending**�E�ELOSED にしなぁE��、E|
| 2026-09-20 | **BR-LAUNCH-01-B** New User Smoke Reset / Account Reuse ACTIVE、E1-A ↁEPAUSED、EURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-B`、E|
| 2026-09-20 | **BR-LAUNCH-01-B Phase 1** Admin Reset API + tests + Smoke Reset ops�E�Eounder UI 未着手�E未 commit�E�、E|
| 2026-09-20 | **BR-LAUNCH-01-B** Server Reset API commit/push/deploy `d2a9f39` PASS。Real Smoke で browser cleanup namespace mismatch 発見！EKpiAuthClient` 誤 ↁE正 `__KPI_AUTH`�E�。runtime 変更なし�Edocs のみ修正、E|
| 2026-09-20 | **BR-LAUNCH-01-B CLOSED**�E�Eeset API + `__KPI_AUTH` cleanup + same-account Human Smoke PASS�E�、E*BR-LAUNCH-01-A CLOSED**�E�Empty-state Human Smoke ALL PASS�E�、EURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01`、E|
| 2026-09-20 | **BR-LAUNCH-01-C** Demo Seed / Demo Reset ACTIVE、EURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-C`。監査・設計�Eみ�E�Euntime 未着手）、E|
| 2026-09-20 | **BR-LAUNCH-01-C1** Demo Dataset Contract & Fixture Audit ACTIVE、EURRENT PATH = `… -> BR-LAUNCH-01-C1`。generated-fixtures は smoke 用・Demo 正本へは PARTIAL、E|
| 2026-09-20 | **BR-LAUNCH-01-C0** Founder Pro + Demo Account Setup ACTIVE、EURRENT PATH = `… -> BR-LAUNCH-01-C0`、E|
| 2026-09-20 | **BR-LAUNCH-01-C0 CLOSED**、Eounder plan=pro; Demo Basic/Pro 作�E済、EURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-C`、E|
| 2026-09-20 | **BR-LAUNCH-01-C2** Demo Operation Pack ACTIVE、EURRENT PATH = `… -> BR-LAUNCH-01-C2`。Reset+Sales/Expenses CSV 設計�E監査のみ、E|
| 2026-09-20 | **BR-LAUNCH-01-C2** `fixtures/demo/restaurant-v1` 固宁ECSV + `docs/demo-operation-pack.md` 作�E、Euman Import Smoke 征E���E�未 commit�E�、E|

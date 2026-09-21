# KPN Development Path?Task Tree?

**??:** ?? / ?? / ??? / ?????????????????????????????  
**????:** Case / Cursor / Codex / Shin  
**???:** 2026-09-20  
**?????:** ?????????????????????????????CLOSED node ???????

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
- BR-LAUNCH-01-A (New User Empty-State Contract) P0 ? closed 2026-09-20
- BR-LAUNCH-01-B (New User Smoke Reset / Account Reuse) P0 ? closed 2026-09-20

CLOSED (under BR-LAUNCH-01-C):
- BR-LAUNCH-01-C0 (Founder Pro + Demo Account Setup) P0 ? closed 2026-09-20
- BR-LAUNCH-01-C2-A (Annual TW Content Missing) P0 ? closed 2026-09-20
- BR-LAUNCH-01-C2-B (Sales Data Target Tab Layout Gap) P0 ? closed 2026-09-20
- BR-LAUNCH-01-C2-D (Sales Data Annual Target Edit-State UX) P1 ? closed 2026-09-20
- BR-LAUNCH-01-C2-E (Sales Data Unsaved Alert + Enter Commit UX) P1 ? closed 2026-09-21
- BR-LAUNCH-01-C2-F (Global Editable Grid Keyboard Navigation ? Wraparound) P1 ? closed 2026-09-21
- BR-LAUNCH-01-C2-G / C2-H / C2-I / C2-J (CLOSED 2026-09-21)
- BR-LAUNCH-01-C2-K (PL Expense Rows Missing After BT Set) P0 closed 2026-09-21

PAUSED (under TRUNK-06):
- BR-LAUNCH-02 Production Smoke / Operational Runbook P1
- BR-LAUNCH-03 UI Consistency Audit P1
- BR-LAUNCH-04 PL Editable Cell Visual Finish P1

DEFERRED:
- BR-LAUNCH-05 Registration / Billing Readiness Assessment P1
  note: Stripe / billing ????????????????? assessment ????
- BR-UI-PL-INSIGHT-FIRSTOPEN-PERF P3
  return when: Final Performance / Speed Optimization phase

RETURN TARGET:
BR-LAUNCH-01-C2 ? BR-LAUNCH-01-C ? BR-LAUNCH-01 ? TRUNK-06

NEXT ACTION:
BR-LAUNCH-01-C2 ? Demo Import Smoke?C2-F Wraparound CLOSED ? return?
```

### Git snapshot????????

| ?? | ? |
|------|-----|
| git branch | `wip/unit5b-pl-mep-preset-engine-20260916` |
| HEAD | ?wrap commit SHA? |
| origin sync | ?????? |
| excel/ | user-owned dirty / **do not touch** |

---

## 1. Task Tree ??????

| ?? | ?? |
|------|------|
| **TRUNK** | ?????????? |
| **BRANCH** | ?????? branch ????????? |
| **PARENT** | ??????????node id?? |
| **RETURN TARGET** | branch ???????????? TRUNK ?? node / NEXT TRUNK?? |

### STATUS

| ? | ?? |
|----|------|
| `ACTIVE` | ????? |
| `PAUSED` | ?????????????? |
| `DEFERRED` | ?????????????? |
| `CLOSED` | ???????? |
| `UNKNOWN` | ???????????? |

### PRIORITY

| ? | ?? |
|----|------|
| `P0` | ?? blocking |
| `P1` | ????????? |
| `P2` | ??????????????? |
| `P3` | polish / optimization / later |

---

## 2. Node ???????

? node ????:

| ????? | ?? |
|------------|------|
| `id` | ?? ID??: `TR-UNIT-5C`, `BR-UI-OSB`? |
| `name` | ????? |
| `parent` | ??? node id?TRUNK ??? `TRUNK` ?? |
| `status` | ACTIVE / PAUSED / DEFERRED / CLOSED / UNKNOWN |
| `priority` | P0?P3 |
| `started_at` | ????YYYY-MM-DD?????? UNKNOWN |
| `return_to` | ??????? |
| `reason` | ??????/??? |
| `evidence` | commit / docs / tests / deploy ??? |
| `next_action` | ???????CLOSED ?? `?`? |

??????:

- `closed_at`
- `commit`
- `docs`
- `tests`
- `deploy`
- `reusable_pattern`

---

## 3. Operating Rule

### ?????????

???????????????????:

- `parent`
- `reason`
- `priority`
- `return_to`
- `status: ACTIVE`

????????????

### branch ??????

- `status` ? `CLOSED`
- `closed_at`
- `commit`
- `tests`?????
- `deploy` evidence?????
- `return_to` ???

CLOSED node ? **?????**??????????????

### Source of Truth

?????? **???????**?

??? code / commit / test / deploy evidence ???????????????????????

1. ???????  
2. reconcile ??????  

??????????? **UNKNOWN**?????????

---

## 4. New Chat Handoff Rule

??? Cursor / Case / Codex chat ? **???????????**?

?????????:

1. Current trunk  
2. Current active path  
3. Active branches  
4. Deferred branches  
5. Return target  
6. Next confirmed task  
7. branch / HEAD / origin sync  
8. uncommitted mainline work  

---

## 5. TRUNK nodes??????

??????????subunit ?????: 5C-3 / 5C-4?? UNKNOWN?

### TR-UNIT-5B

| ????? | ? |
|------------|-----|
| id | `TR-UNIT-5B` |
| name | Unit 5B ? PL/MEP Business Type preset engine |
| parent | `TRUNK`?Unit 5? |
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN?branch ? `unit5b-...-20260916`? |
| closed_at | UNKNOWN?5C ??????????????? |
| return_to | `TR-UNIT-5C` |
| reason | Business Type ?? expense preset / catalog ???? |
| evidence | commits `f41e1f9` Add PL MEP business preset engine; `6fe3275` deferred classification; `7ba334d` PL Analyze BT; `cf7b67a` MEP preset sync; tests `_test_pl_mep_preset_engine.py`, `_test_business_expense_presets.py`, `_test_pl_analysis_business_type.py` |
| next_action | ? |
| note | git branch ????? unit5b????? 5C ???????????????????????? |

### TR-UNIT-5C

| ????? | ? |
|------------|-----|
| id | `TR-UNIT-5C` |
| name | Unit 5C ? Business Type surface adaptation |
| parent | `TR-UNIT-5B` |
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN |
| closed_at | 2026-09?close tests: `3f35989`, `f609d32`? |
| return_to | `TR-FW-AUDIT` |
| reason | PL Insight / Insight Summary / Monthly TW / MEP meal ? BT ????? |
| evidence | markers `UNIT-5C-1`?`5C-2`?`5C-5`?`5C-6`; commits `9ca3ab0`, `f179989`, `ab4fa9f`, `0249724`, `3f35989`, `f609d32`; tests `_test_pl_insight_finalization.py`, `_test_monthly_tw_business_type.py`, `_test_mep_meal_business_type.py` |
| next_action | ? |
| unknown | `5C-3` / `5C-4` ? marker?doc ? repo ??? ? **UNKNOWN????????????** |

### TR-FW-AUDIT

| ????? | ? |
|------------|-----|
| id | `TR-FW-AUDIT` |
| name | Floating Window Functional Audit |
| parent | `TR-UNIT-5C` |
| status | CLOSED |
| priority | P0 |
| started_at | UNKNOWN |
| closed_at | 2026-09-19 ???wiring tests? |
| return_to | `TR-PLANNING-READINESS` |
| reason | FW ??????? contract test ??????????? |
| evidence | `e2fc0ac` Daily FW wiring; `10f5495` Top Insight wiring; `f609d32` PL Insight wiring close prep; `3f35989` Unit 5C close tests |
| next_action | ? |
| note | ???????? `docs/planning-readiness.md` ???`138edd1`???????????????? FW ? COMPLETE ?? doc ??? ? ?? FW ?????? UNKNOWN? |

### TR-PLANNING-READINESS

| ????? | ? |
|------------|-----|
| id | `TR-PLANNING-READINESS` |
| name | Planning Readiness / KPI Setup Status |
| parent | `TR-FW-AUDIT` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-19 |
| closed_at | 2026-09-19?20??? + Amber/Gold visual? |
| return_to | `TRUNK-06`??????2026-09-20 ??? |
| reason | ?????????????FW Audit ????????? |
| evidence | `138edd1` doc; `a260227` implementation; `docs/planning-readiness.md`; `js/kpi-planning-readiness.js`; `_test_planning_readiness.py` |
| next_action | ? |
| docs | [`planning-readiness.md`](./planning-readiness.md) |

### TR-SEASONALITY-BASELINE

| ????? | ? |
|------------|-----|
| id | `TR-SEASONALITY-BASELINE` |
| name | Automatic Seasonality / Baseline-Year Contract |
| parent | `TR-PLANNING-READINESS` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-19 |
| closed_at | 2026-09-19 |
| return_to | UI/UX polish branches ? ??? TRUNK |
| reason | Recommended seasonality / baseline years / anomaly flag |
| evidence | `474ec5f`, `4733b57`, `fbe7a48`, `43fbfe2`; `js/kpi-seasonality-allocator.js`; `docs/planning-readiness.md` ?????? |
| next_action | ? |

### TR-UIUX-CLOSEOUT

| ????? | ? |
|------------|-----|
| id | `TR-UIUX-CLOSEOUT` |
| name | UI/UX branches close?Sales Data / Past Sales / Overlay / Amber? |
| parent | `TR-SEASONALITY-BASELINE` |
| status | CLOSED |
| priority | P1?P3??? node ??? |
| started_at | 2026-09-19?20 |
| closed_at | 2026-09-20?`dffeb8e`? |
| return_to | `TRUNK-06` |
| reason | ????scrollbar?PROVISIONAL warning ??????????? |
| evidence | ?? CLOSED BRANCHES |
| next_action | ? |

---

## 6. CLOSED BRANCHES?UI/UX ???

### BR-UI-SALES-DATA-HIERARCHY

| ????? | ? |
|------------|-----|
| id | `BR-UI-SALES-DATA-HIERARCHY` |
| name | Sales Data UI hierarchy |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P2 |
| started_at | UNKNOWN |
| closed_at | 2026-09-20 ?? |
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | readonly / active / closed-day ??? |
| evidence | commits `b613297`, `a22a5cf`, `a8762ed`, `5987de7` |
| next_action | ? |

### BR-UI-PAST-SALES-HIERARCHY

| ????? | ? |
|------------|-----|
| id | `BR-UI-PAST-SALES-HIERARCHY` |
| name | Past Sales UI hierarchy |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P2 |
| started_at | UNKNOWN |
| closed_at | 2026-09-20 ?? |
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | Past Sales ? Sales Data ??????? |
| evidence | commits `a937550`, `ce9ae34`, `a443802` |
| next_action | ? |

### BR-UI-OVERLAY-SCROLLBAR

| ????? | ? |
|------------|-----|
| id | `BR-UI-OVERLAY-SCROLLBAR` |
| name | Overlay Scrollbar UX |
| parent | `TR-UIUX-CLOSEOUT` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 ?? |
| closed_at | 2026-09-20 |
| return_to | `TR-UIUX-CLOSEOUT` |
| reason | ?? overlay scrollbar ??? |
| evidence | `b18c7a3`; `docs/kpn-scrollbar-ux-contract.md`; `js/kpi-overlay-scrollbar.js` |
| deploy | production ??????? hotfix ??? |
| reusable_pattern | shared OSB host wrap + Mac native opt-out |
| next_action | ? |

### BR-UI-ANNUAL-TW-OSB

| ????? | ? |
|------------|-----|
| id | `BR-UI-ANNUAL-TW-OSB` |
| name | Annual TW dedicated overlay adapter |
| parent | `BR-UI-OVERLAY-SCROLLBAR` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-UI-OVERLAY-SCROLLBAR` |
| reason | Annual TW ? wrap ????? overlay |
| evidence | `bfad0bf`; `js/kpi-annual-tw-overlay-scrollbar.js` |
| next_action | ? |

### BR-UI-INSIGHT-PL-OSB-REGRESSION

| ????? | ? |
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
| next_action | ? |
| note | first-open **scroll** ??? CLOSED?first-open **performance** ?? DEFERRED node? |

### BR-UI-MONTHLY-TW-HSCROLL

| ????? | ? |
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
| reason | box-style absolute ? residual inset ????????? |
| evidence | `2abc23c`; `js/kpi-overlay-scrollbar.js`?insetPort vs box-style? |
| deploy | production PASS?RETR/SHA? |
| next_action | ? |

### BR-UI-PR-AMBER-GOLD

| ????? | ? |
|------------|-----|
| id | `BR-UI-PR-AMBER-GOLD` |
| name | Amber/Gold Planning Readiness warning |
| parent | `TR-PLANNING-READINESS` |
| status | CLOSED |
| priority | P2 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| commit | `dffeb8e` |
| return_to | `TRUNK-06`?UI/UX closeout ????? |
| reason | PROVISIONAL ????? bright orange ?? dark amber/gold ? |
| evidence | `dffeb8e`; `js/kpi-planning-readiness.js`; `_test_planning_readiness.py` 117 passed; deploy 7/7 |
| docs | [`planning-readiness.md`](./planning-readiness.md) ?9.1 |
| next_action | ? |

---

## 7. ACTIVE TRUNK ? TRUNK-06 Launch / Demo / New-user Readiness

### TRUNK-06

| ????? | ? |
|------------|-----|
| id | `TRUNK-06` |
| name | Launch / Demo / New-user Readiness |
| parent | KPN Development |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | N/A |
| reason | Unit 5C / Floating Window Functional Audit / Planning Readiness / Automatic Seasonality / ?? UI/UX closeout ?????KPN ?????????????????????????????????? |
| evidence | `docs/development-path.md` Next Trunk Selection Audit?2026-09-20?; HEAD `dffeb8e` UI/UX closeout; Shin/Case ??????? |
| next_action | `BR-LAUNCH-01-C` Demo Seed / Demo Reset??????? |
| docs | [`free-trial-account-ops.md`](./free-trial-account-ops.md)????????? |

### BR-LAUNCH-01

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01` |
| name | Demo / New User State |
| parent | `TRUNK-06` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | ????????????????????????? |
| evidence | TRUNK-06 ?????2026-09-20? |
| next_action | `BR-LAUNCH-01-C` ACTIVE?Demo Seed / Reset ????? |

### BR-LAUNCH-01-A

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-A` |
| name | New User Empty-State Contract |
| parent | `BR-LAUNCH-01` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01` |
| reason | ?????? empty ? ???Option B BT unset?PR empty = NOT_READY |
| evidence | automated tests; production Human Smoke ALL PASS?BT unset / Annual?Monthly?PL empty / PR NOT_READY / no target amber / Pro?MEP?PL / no fake money?; BT Settings hydrate `6ee7d3b` |
| next_action | N/A?CLOSED? |
| contract | ????; `?`=???; `0`=??????; PR empty=NOT_READY; BT Option B; ???????/plan/theme?? |

### BR-LAUNCH-01-B

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-B` |
| name | New User Smoke Reset / Account Reuse |
| parent | `BR-LAUNCH-01` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-A` |
| reason | ?? Smoke ?????????? emptyStore / BT ??????????????????? |
| evidence | production Reset API `d2a9f39`; target-only wipe; session revoke; `__KPI_AUTH.clearUserScopedLocalData` ? logout ? same-account re-login Human Smoke PASS; Pro ?? |
| next_action | N/A?CLOSED? |
| target_account | `kpn_empty_state_smoke01@trial.forge-laboratory.com` |
| phase1 | Admin Reset API `api/v1/admin/reset-user-kpi.php` + tests + ops docs?Founder UI ??? |
| phase2_candidate | Founder Console Reset UI |
| browser_cleanup | `window.__KPI_AUTH.clearUserScopedLocalData()` ? logout ? login?UI logout ???? LS ???`KpiAuthClient` ???? |

### BR-LAUNCH-01-C

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C` |
| name | Demo Seed / Demo Reset |
| parent | `BR-LAUNCH-01` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01` |
| reason | New User Empty-State / Smoke Reset ? CLOSED????????????????????? |
| evidence | 01-A/01-B CLOSED; New User Reset ? Demo Reset; ??: wipe API ????user store inject API ???; meal/customers ? `years[].dailyMeal`?daily-inputs ? sales/BD ???; ?? `excel/*_official*` + `tests/generated-fixtures/`; Founder User Detail ??? UI ?? |
| next_action | C2 Demo Operation Pack ??????Reset + Sales/Expenses CSV? |
| constraint | ?????? UI ??????Founder/Admin ??????random ???01-B empty reset ??? |
| audit_note | Demo Reset = wipe?reuse `reset-user-kpi`?? apply seed ? `__KPI_AUTH.clear` ? re-login |
| confirmed_v1 | loader+dataset; restaurant; Pro; JPY; 2 past + operating; deterministic; Founder/Admin only |
| accounts | Founder Pro + Demo Basic/Pro??? dataset?plan?????C0 ??? |


### BR-LAUNCH-01-C2-K

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-K |
| name | PL Expense Rows Missing After Business Type Set |
| parent | BR-LAUNCH-01-C2 |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | BR-LAUNCH-01-C2 |
| reason | Profile BT save did not durable-PUT store.meta.businessType; Annual hydrate wiped meta; PL seed gate stayed false |
| evidence | gateway hydrate preserve + pushToServerWhenReady; profile_edit x3 flush; verify 14 PASS; foundation 135 PASS |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2 -> Demo Import Smoke / C2-L candidate |
| constraint | no CSV inference; no restaurant fallback change; no PL seed gate change; no expense delete |


### BR-LAUNCH-01-C2-J

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-J |
| name | JP Cockpit Year Navigation Spacing Parity |
| parent | BR-LAUNCH-01-C2 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | BR-LAUNCH-01-C2 |
| reason | Human Smoke: JP year arrow/year gaps too tight vs ZH-TW |
| evidence | JP year-cluster gap 0?13px; verify L/R=13 font=18 Annual/Monthly parity; target/today?45; no overlap PASS |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2 -> Demo Import Smoke |
| constraint | no +45/target formula change; JP only; reuse existing gap token |

### BR-LAUNCH-01-C2-I

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-I |
| name | Cockpit Target Font Parity + Currency Decimal Display |
| parent | BR-LAUNCH-01-C2 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | BR-LAUNCH-01-C2 |
| reason | Human Smoke: JP Sci-Fi annual target font too small vs Office; JPY amounts show .00 |
| evidence | JP Sci-Fi target inherits 16px; KpiCurrency.fractionDigits/formatMoney; Cockpit fmtMoney JPY=0 else=2; verify PASS |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2 -> Demo Import Smoke |
| constraint | display-only; no calc/save; no layout/position change; EN/ZH font untouched |

### BR-LAUNCH-01-C2-H

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-H |
| name | Cockpit Annual Link + Target Position Parity |
| parent | BR-LAUNCH-01-C2 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | BR-LAUNCH-01-C2 |
| reason | Human Smoke: Annual Cockpit H/L % cells not clickable; Monthly target sales still right-shifted vs Annual |
| evidence | Annual same-page HL to SDM Analyze; Monthly year-nav CSS parity (JP gap0, year-value 14, ZH BIZ14); verify JP/EN/ZH-TW x Sci-Fi/Office delta0 PASS |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2 -> Demo Import Smoke |
| constraint | no Annual layout change; no calc/excel; Monthly CSS parity to Annual canonical |

### BR-LAUNCH-01-C2-G

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-G |
| name | Monthly Cockpit Annual Link + Header Alignment |
| parent | BR-LAUNCH-01-C2 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | BR-LAUNCH-01-C2 |
| reason | Human Smoke: Monthly Cockpit seasonality percent link missing + annual target box left-shift |
| evidence | sessionStorage intent sales-data-analyze; Monthly HL cell/header ? Annual SDM Analyze; prompt() removed; Monthly target place=Annual contract (left calc+opacity+RO); smoke JP/EN/ZH-TW x Sci-Fi/Office PASS |
| next_action | N/A?CLOSED?? return BR-LAUNCH-01-C2 ? Demo Import Smoke |
| constraint | no Annual layout / calc / Sales Data core / excel |

### BR-LAUNCH-01-C2-F

| ????? | ? |
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
| reason | Human Smoke????????Enter/Tab/Shift+Enter/Shift+Tab ? wraparound ????? |
| evidence | helper=`bindGridKeys` + matrix wrap?Sales/Past/Annual/MEP/PL logical adapters?smoke Enter/Shift+Enter/Tab/Shift+Tab ???? PASS |
| next_action | N/A?CLOSED?? return BR-LAUNCH-01-C2 ? Demo Import Smoke |
| constraint | Enter?Save / Space native / OCC?lease?calc?excel ?? |

### BR-LAUNCH-01-C2-E

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C2-E` |
| name | Sales Data Unsaved Alert + Enter Commit UX |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-21 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | ?????????close? lease-lost ??????????/????? Enter ?????? |
| evidence | fix=`rejectSalesDataSaveNotLive` ? foreign lease vs ?????????Enter=`bindSalesAmountZeroClearUx` ? keydown?blur?lease/OCC/Save??????JP/EN/ZH-TW |
| next_action | N/A?CLOSED?? return BR-LAUNCH-01-C2 |
| constraint | save/OCC/lease logic / ?? / import / excel ?? |

### BR-LAUNCH-01-C2-D

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C2-D` |
| name | Sales Data Annual Target Edit-State UX |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | ??????????????????????????????????? |
| evidence | fix=`applySalesDataGuards` ? summary panel + `#sales-data-summary-reference` ? Past Sales ??? guard?dim=`summary--path-blocked` opacity?active=`--sdm-bg-active-55/70`?dirty listener ? readOnly/disabled ? early return?local smoke JP/EN/ZH-TW ? Sci-Fi/Office PASS |
| next_action | N/A?CLOSED?? return BR-LAUNCH-01-C2 |
| constraint | save logic / ?? / import / excel ?? |

### BR-LAUNCH-01-C2-C

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C2-C` |
| name | Cross-Tab Account Session Collision |
| parent | `BR-LAUNCH-01-C2` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | ?? Chrome profile ??? account tab ????????? login ?? tab ? identity ?????Sales Data ?????????? |
| evidence | Cookie `KPISESSID` path=/ ? profile ???login ? session user ??????LS `lastKpiUserId` + store ? profile ??????? LS `kpiEditLeases`???????1 lease?????? save ??? lease lost ? SECONDARY?concurrent multi-account ???????? |
| next_action | Case??: Bug?????????? profile / Incognito???????? session redesign ? DEFER ??? |
| constraint | auth architecture / session redesign / Sales save / OCC / runtime ?????????? audit? |

### BR-LAUNCH-01-C2-B

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C2-B` |
| name | Sales Data Target Tab Layout Gap |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | Demo Pro Human Smoke ? Sales Data FW ???? tab ??????????? |
| evidence | OSB host ??????fix=tab ? inactive `.kpn-osb-host:has(#sales-data-pane-*)` ? display:none?JP/EN/ZH-TW??local smoke gap=0 ? Sci-Fi/Office roundtrip PASS?OSB JS ??? |
| next_action | N/A?CLOSED?? return BR-LAUNCH-01-C2 |
| constraint | OSB JS / calc / TW / excel ??? |

### BR-LAUNCH-01-C2-A

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C2-A` |
| name | Annual TW Content Missing |
| parent | `BR-LAUNCH-01-C2` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C2` |
| reason | Demo Pro Human Smoke ? Annual TW body missing ??? |
| evidence | root=`153484e` Graph1 `buildDemoPayload`???? `buildEmptyTrendPayload`?fix=Graph1 scope ???????JP/EN/ZH-TW??local smoke: pageerror0 / renderFn / 57rows / wrap?? |
| next_action | N/A?CLOSED?? return BR-LAUNCH-01-C2 |
| constraint | Monthly / OSB / TW sizing / excel ??? |

### BR-LAUNCH-01-C2

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C2` |
| name | Demo Operation Pack |
| parent | `BR-LAUNCH-01-C` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | ???????????? 3 ?????Demo Reset / Sales CSV / Expenses CSV? |
| evidence | fixtures/demo/restaurant-v1 ?? CSV ????integrity OK??docs/demo-operation-pack.md?Reset=reuse reset-user-kpi?runtime ???????? |
| next_action | C2-A ??? ? Human Import Smoke?Demo Basic Sales / Demo Pro Sales+Expenses?? C2 CLOSE ?? |
| pack | Reset + sales_2024|2025|2026 + expenses daily/monthly |
| demo_basic | `kpn_demo_restaurant_basic01@?` / `u_7aac8cb5cbb0f607` |
| demo_pro | `kpn_demo_restaurant_pro01@?` / `u_a57d33d6ae864d99` |

### BR-LAUNCH-01-C0

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C0` |
| name | Founder Pro + Demo Account Setup |
| parent | `BR-LAUNCH-01-C` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | Demo ???? Founder=PRO ? Demo Basic/Pro ??????????????? |
| evidence | Founder `u_43e738560b91617f` plan=pro role=founder_superadmin; Demo Basic `u_7aac8cb5cbb0f607` plan=basic; Demo Pro `u_a57d33d6ae864d99` plan=pro??? dataset?plan????BT ? seed ? |
| next_action | N/A?CLOSED? |
| founder | `s.matsushita@forge-laboratory.com` |
| demo_basic | `kpn_demo_restaurant_basic01@trial.forge-laboratory.com` |
| demo_pro | `kpn_demo_restaurant_pro01@trial.forge-laboratory.com` |

### BR-LAUNCH-01-C1

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01-C1` |
| name | Demo Dataset Contract & Existing Fixture Audit |
| parent | `BR-LAUNCH-01-C` |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-20 |
| return_to | `BR-LAUNCH-01-C` |
| reason | Demo Seed API ?? generated-fixtures ???? restaurant Demo v1 ? deterministic dataset ??????? |
| evidence | `tests/generated-fixtures/` = CSV smoke?`csv_smoke_fixture_generator.py`??L/D ???????????????? expense?plan/PR ?????? PARTIAL |
| next_action | Case??? ? C2 dataset ???? or HOLD |
| constraint | runtime????; dataset??????????; excel untouched |

### BR-LAUNCH-02

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-02` |
| name | Production Smoke / Operational Runbook |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | ?????????????? |
| evidence | TRUNK-06 child?PAUSED until BR-LAUNCH-01? |
| next_action | BR-LAUNCH-01 ???? ACTIVE ???? |

### BR-LAUNCH-03

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-03` |
| name | UI Consistency Audit |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | Annual / Monthly / FW ???????????? |
| evidence | TRUNK-06 child?PAUSED? |
| next_action | ???????? ACTIVE |

### BR-LAUNCH-04

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-04` |
| name | PL Editable Cell Visual Finish |
| parent | `TRUNK-06` |
| status | PAUSED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | ?????????????/?????? |
| evidence | `pl-table-v1-implementation-spec.md`?B???UX ????; TRUNK-06 child?PAUSED? |
| next_action | BR-LAUNCH-01 ?? ACTIVE ???? |

### BR-LAUNCH-05

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-05` |
| name | Registration / Billing Readiness Assessment |
| parent | `TRUNK-06` |
| status | DEFERRED |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | ?????????? readiness ???Stripe / billing ??????????????????????? assessment ????? |
| evidence | commit `af07bf7` Disable public registration until billing is ready; `free-trial-account-ops.md`?billingType ???? |
| next_action | ?????Stripe / ???????????? assessment ? ???????? |
| note | **????????**?readiness assessment only?? |

---

## 8. DEFERRED BRANCHES????

### BR-UI-PL-INSIGHT-FIRSTOPEN-PERF

| ????? | ? |
|------------|-----|
| id | `BR-UI-PL-INSIGHT-FIRSTOPEN-PERF` |
| name | PL Insight first-open performance |
| parent | `BR-UI-INSIGHT-PL-OSB-REGRESSION`???? / ???? PL Insight |
| status | DEFERRED |
| priority | P3 |
| started_at | UNKNOWN???????? |
| return_to | Final Performance / Speed Optimization phase |
| reason | first-open ??????scroll ?????`058b9cd`?????? |
| evidence | Case ?????2026-09-20 Current Position??P3 deferred |
| next_action | Performance phase ???? ACTIVE ????????? |

---

## 9. ACTIVE BRANCHES????

| id | name | status | priority | parent |
|----|------|--------|----------|--------|
| `BR-LAUNCH-01-C` | Demo Seed / Demo Reset | ACTIVE | P0 | `BR-LAUNCH-01` |
| `BR-LAUNCH-01-C1` | Demo Dataset Contract & Existing Fixture Audit | ACTIVE | P0 | `BR-LAUNCH-01-C` |
| `BR-LAUNCH-01-C2` | Demo Operation Pack | ACTIVE | P0 | `BR-LAUNCH-01-C` |
| `BR-LAUNCH-01-C2-K` | PL Expense Rows Missing After BT Set | ACTIVE | P0 | `BR-LAUNCH-01-C2` |

CLOSED under `BR-LAUNCH-01`: `BR-LAUNCH-01-A`, `BR-LAUNCH-01-B`  
CLOSED under `BR-LAUNCH-01-C`: `BR-LAUNCH-01-C0`  
PAUSED under `TRUNK-06`: `BR-LAUNCH-02`, `BR-LAUNCH-03`, `BR-LAUNCH-04`  
DEFERRED under `TRUNK-06`: `BR-LAUNCH-05`
CLOSED under `BR-LAUNCH-01`: `BR-LAUNCH-01-A`, `BR-LAUNCH-01-B`  
PAUSED under `TRUNK-06`: `BR-LAUNCH-02`, `BR-LAUNCH-03`, `BR-LAUNCH-04`  
DEFERRED under `TRUNK-06`: `BR-LAUNCH-05`

---

## 10. UNKNOWN / OPEN QUESTIONS

| ?? | ?? |
|------|------|
| Unit 5C-3 / 5C-4 | marker?doc ?? ? **UNKNOWN** |
| Unit 5D ?? | **UNKNOWN**????? TRUNK-06? |
| FW Audit ?? Floating Window ?????? | ?? tests ? Daily / Top Insight / PL Insight ?????????? COMPLETE ?? doc ?? ? **UNKNOWN** |
| `TR-UNIT-5B` / `TR-UNIT-5C` ???? started_at | **UNKNOWN** |
| BR-LAUNCH-01 ????????????????????? | Empty-State / Smoke Reset CLOSED???? `BR-LAUNCH-01-C` Demo Seed/Reset |
| BT Option C ????? | **DEFERRED**?01-A ? Option B? |

---

## 11. Contradictions / Notes?reconcile ???

| ?? | ?? |
|------|------|
| git branch ?? `unit5b` ???????? 5C?????TRUNK-06 ?????? | **????**??????????????????? |
| `pl-insight-final-adjustments-memo.md` ??????????????????????????????? ???????1?? | **doc ???????**????????????? + wiring tests ?????? rewrite ??????? |
| first-open scroll fix?CLOSED?vs first-open performance?DEFERRED? | **? node**??????? |
| NEXT TRUNK ? TRUNK-06 ????? | 2026-09-20 ????UNKNOWN / TO DECIDE????? |

??????????????? reconcile ? blocker ? **??**?

---

## 12. ???????????

| ?? | ?? |
|------|------|
| 2026-09-20 | ???Task Tree ??? + CURRENT PATH?HEAD `dffeb8e`????? |
| 2026-09-20 | **TRUNK-06** Launch / Demo / New-user Readiness ? ACTIVE ??????CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01`? |
| 2026-09-20 | **BR-LAUNCH-01-A** New User Empty-State Contract ACTIVE?CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-A`???: ???? / Option B? |
| 2026-09-20 | BT unset Settings hydrate fix commit `6ee7d3b` + prod deploy?01-A ? **ACTIVE / Human Smoke pending**?CLOSED ?????? |
| 2026-09-20 | **BR-LAUNCH-01-B** New User Smoke Reset / Account Reuse ACTIVE?01-A ? PAUSED?CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-B`? |
| 2026-09-20 | **BR-LAUNCH-01-B Phase 1** Admin Reset API + tests + Smoke Reset ops?Founder UI ????? commit?? |
| 2026-09-20 | **BR-LAUNCH-01-B** Server Reset API commit/push/deploy `d2a9f39` PASS?Real Smoke ? browser cleanup namespace mismatch ???`KpiAuthClient` ? ? ? `__KPI_AUTH`??runtime ?????docs ????? |
| 2026-09-20 | **BR-LAUNCH-01-B CLOSED**?Reset API + `__KPI_AUTH` cleanup + same-account Human Smoke PASS??**BR-LAUNCH-01-A CLOSED**?empty-state Human Smoke ALL PASS??CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01`? |
| 2026-09-20 | **BR-LAUNCH-01-C** Demo Seed / Demo Reset ACTIVE?CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-C`?????????runtime ????? |
| 2026-09-20 | **BR-LAUNCH-01-C1** Demo Dataset Contract & Fixture Audit ACTIVE?CURRENT PATH = `? -> BR-LAUNCH-01-C1`?generated-fixtures ? smoke ??Demo ???? PARTIAL? |
| 2026-09-20 | **BR-LAUNCH-01-C0** Founder Pro + Demo Account Setup ACTIVE?CURRENT PATH = `? -> BR-LAUNCH-01-C0`? |
| 2026-09-20 | **BR-LAUNCH-01-C0 CLOSED**?Founder plan=pro; Demo Basic/Pro ????CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-C`? |
| 2026-09-20 | **BR-LAUNCH-01-C2** Demo Operation Pack ACTIVE?CURRENT PATH = `? -> BR-LAUNCH-01-C2`?Reset+Sales/Expenses CSV ???????? |
| 2026-09-20 | **BR-LAUNCH-01-C2** `fixtures/demo/restaurant-v1` ?? CSV + `docs/demo-operation-pack.md` ???Human Import Smoke ???? commit?? |
| 2026-09-21 | **BR-LAUNCH-01-C2-K** PL Expense Rows Missing After BT Set ACTIVE (AUDIT FIRST) |
| 2026-09-21 | **BR-LAUNCH-01-C2-K CLOSED** Persist BT meta + restore PL expense rows; return C2 |

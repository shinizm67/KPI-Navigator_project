# KPN Development Path?Task Tree?

**??:** ?? / ?? / ??? / ?????????????????????????????  
**????:** Case / Cursor / Codex / Shin  
**???:** 2026-09-20  
**?????:** ?????????????????????????????CLOSED node ???????

---

## CURRENT PATH

```
CURRENT PATH:
(none — TRUNK-06 CLOSED)

PRIOR TRUNK (CLOSED):
Unit 5B -> Unit 5C -> Floating Window Functional Audit
-> Planning Readiness -> Automatic Seasonality / Baseline
-> UI/UX branches closeout
-> TRUNK-06 (Launch / Demo / New-user Readiness)

ACTIVE BRANCHES:
- (none — TRUNK-06 CLOSED)

REGISTERED (under TRUNK-06; do not start):
- (none — trunk CLOSED)

REGISTERED (under BR-LAUNCH-03; do not start):
- (none — parent CLOSED)

REGISTERED (POST-LAUNCH importer; do not start):
- BR-LAUNCH-01-C2-L6-A Multi-sheet Import Profile (POST-LAUNCH / DEFERRED P2)
- Horizontal parser (POST-LAUNCH; not a Launch blocker)
- Mixed income+expense parser (POST-LAUNCH; not a Launch blocker)
- Advanced date/year inference (POST-LAUNCH; not a Launch blocker)
- Import Preview expansion (POST-LAUNCH; not a Launch blocker)
- BR-POST-EXPENSE-LEDGER Purchase / Expense Ledger (DEFERRED P2)
- BR-UI-PL-EXPENSE-CLASSIFY-TOOLTIPS (DEFERRED P2)
- BR-POST-XLSX-REPORT True XLSX / PL Report Export (POST-LAUNCH HIGH)

CLOSED (under TRUNK-06):
- BR-LAUNCH-01 (Demo / New User State) P0 closed 2026-09-23
- BR-LAUNCH-02 (Production Smoke / Operational Runbook) P1 closed 2026-09-24
- BR-LAUNCH-03 (UI Consistency Audit) P1 closed 2026-09-24
- BR-LAUNCH-04 (PL Editable Cell Visual Finish) P1 closed 2026-09-24
- BR-LAUNCH-06 (PL Excel Download Repair) P1 closed 2026-09-24
- BR-LAUNCH-07 (Global Menu Spacing / Reservation Button Collision) P1 closed 2026-09-25
- BR-LAUNCH-08 (ZH-TW PL Global Menu Parity Repair) P1 closed 2026-09-25

CLOSED (under BR-LAUNCH-03):
- BR-LAUNCH-03-A Shared Header 1200 (R1) P1 closed 2026-09-24
- BR-LAUNCH-03-B Shared Chrome i18n (R2) P1 closed 2026-09-24
- BR-LAUNCH-03-C Basic Monthly layout (R3) P1 closed 2026-09-24
- BR-LAUNCH-03-D MEP Tutorial overlap (R4) P1 closed 2026-09-24
- BR-LAUNCH-03-E Responsive Eligibility Gate P1 closed 2026-09-24
- BR-LAUNCH-03-F Office Mode Focus Bar Color Consistency P1 closed 2026-09-24

CLOSED (under BR-LAUNCH-02):
- BR-LAUNCH-02-A (Launch Regression Smoke / Cross-feature Regression) P1 closed 2026-09-24
- BR-LAUNCH-02-B (Launch Operational Runbook Inventory) P1 closed 2026-09-24

CLOSED (under BR-LAUNCH-01):
- BR-LAUNCH-01-A (New User Empty-State Contract) P0 ? closed 2026-09-20
- BR-LAUNCH-01-B (New User Smoke Reset / Account Reuse) P0 ? closed 2026-09-20
- BR-LAUNCH-01-C (Demo Seed / Demo Reset) P0 closed 2026-09-23

CLOSED (under BR-LAUNCH-01-C):
- BR-LAUNCH-01-C0 (Founder Pro + Demo Account Setup) P0 ? closed 2026-09-20
- BR-LAUNCH-01-C2-A (Annual TW Content Missing) P0 ? closed 2026-09-20
- BR-LAUNCH-01-C2-B (Sales Data Target Tab Layout Gap) P0 ? closed 2026-09-20
- BR-LAUNCH-01-C2-D (Sales Data Annual Target Edit-State UX) P1 ? closed 2026-09-20
- BR-LAUNCH-01-C2-E (Sales Data Unsaved Alert + Enter Commit UX) P1 ? closed 2026-09-21
- BR-LAUNCH-01-C2-F (Global Editable Grid Keyboard Navigation ? Wraparound) P1 ? closed 2026-09-21
- BR-LAUNCH-01-C2-G / C2-H / C2-I / C2-J (CLOSED 2026-09-21)
- BR-LAUNCH-01-C2-K (PL Expense Rows Missing After BT Set) P0 closed 2026-09-21
- BR-LAUNCH-01-C2-L1-A (Profile Business Type / Genre Sync) P0 closed 2026-09-22
- BR-LAUNCH-01-C2-L1 (Business Type Import Gate) P0 closed 2026-09-22
- BR-LAUNCH-01-C2-L2 (High-confidence Expense Synonyms) P1 closed 2026-09-22
- BR-LAUNCH-01-C2-L3-A (Unknown Expense Hold Foundation) P1 closed 2026-09-22
- BR-LAUNCH-01-C2-L3-B (Persistent Mapping Record + Alias Server Persistence) P1 closed 2026-09-22
- BR-LAUNCH-01-C2-L3 (Unknown Label Preservation + Persistent Import Mapping Record) P1 closed 2026-09-22
- BR-LAUNCH-01-C2-L4 (Expense Classification Lifecycle) P1 closed 2026-09-22
- BR-LAUNCH-01-C2-L5-A (Plan-independent Expense Storage / Upgrade Safety) P1 closed 2026-09-22
- BR-LAUNCH-01-C2-L5-B (Basic / Pro Expense UI Entitlement) P1 closed 2026-09-23
- BR-LAUNCH-01-C2-L5 (Plan-independent Expense Storage + Basic / Pro Visibility) P1 closed 2026-09-23
- BR-LAUNCH-01-C2-L6-B (Excel Sheet Picker — Launch) P1 closed 2026-09-23
- BR-LAUNCH-01-C2-L6 (Flexible Translator Expansion) P1 closed 2026-09-23
- BR-LAUNCH-01-C2-C (Cross-Tab Account Session Collision) P0 closed 2026-09-23
- BR-LAUNCH-01-C2-L (Flexible CSV / Excel Import Foundation) P0 closed 2026-09-23
- BR-LAUNCH-01-C2 (Demo Operation Pack) P0 closed 2026-09-23
- BR-LAUNCH-01-C1 (Demo Dataset Contract & Existing Fixture Audit) P0 closed 2026-09-23

ACTIVE (under TRUNK-06):
- (none — trunk CLOSED)

PAUSED / REGISTER ONLY (under TRUNK-06):
- (none)

DEFERRED:
- BR-LAUNCH-05 Registration / Billing Readiness Assessment P1
  note: Stripe / billing ????????????????? assessment ????
- BR-UI-PL-EXPENSE-CLASSIFY-TOOLTIPS P2
  parent: BR-LAUNCH-01-C2
  reason: Feature works; discoverability is weak. Do not block CSV/Excel launch path.
- BR-UI-PL-INSIGHT-FIRSTOPEN-PERF P3
  return when: Final Performance / Speed Optimization phase
- BR-LAUNCH-01-C2-L6-A Multi-sheet Import Profile P2 POST-LAUNCH / DEFERRED
  parent: BR-LAUNCH-01-C2-L6. REGISTER ONLY.
- Horizontal parser P2 POST-LAUNCH
  not a Launch blocker. Template fallback covers unsupported layout.
- Mixed income+expense automatic split P2 POST-LAUNCH
  not a Launch blocker.
- Advanced date/year inference (filename / sheet-name / M/D) P2 POST-LAUNCH
  not a Launch blocker.
- Import Preview expansion P2 POST-LAUNCH
  not a Launch blocker. Persistent mapping exists; Preview UI expansion is later.
- BR-POST-EXPENSE-LEDGER Purchase / Expense Ledger P2 DEFERRED
  parent: BR-LAUNCH-01-C2. REGISTER ONLY. Not an Excel clone.
- BR-POST-XLSX-REPORT True XLSX / PL Report Export HIGH POST-LAUNCH
  parent: TRUNK-06. REGISTER ONLY. Not BR-LAUNCH-06. Accountant/archive workbook.

RETURN TARGET:
N/A (TRUNK-06 CLOSED)

NEXT ACTION:
NONE. Do not auto-start `BR-LAUNCH-05`. Do not start post-launch work.
```

### Git snapshot

| field | value |
|------|-----|
| git branch | `wip/unit5b-pl-mep-preset-engine-20260916` |
| HEAD | `56e96f0` (BR-LAUNCH-08 closeout; product `369c036`) |
| origin sync | in sync |
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

## 7. CLOSED TRUNK — TRUNK-06 Launch / Demo / New-user Readiness

### TRUNK-06

| Field | Value |
|-------|-------|
| id | `TRUNK-06` |
| name | Launch / Demo / New-user Readiness |
| parent | KPN Development |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-25 |
| return_to | N/A |
| reason | Unit 5C / Floating Window Functional Audit / Planning Readiness / Automatic Seasonality / UI/UX closeout の次。KPN Launch / Demo / New-user Readiness。 |
| evidence | Direct Launch-required children 01/02/03/04/06/07/08 CLOSED. No remaining Launch-required P0/P1. `BR-LAUNCH-05` DEFERRED (registration already disabled `af07bf7`; billing assessment not a Launch blocker). Latest production: 08 25/25 PASS. Human Smoke not required for remaining Launch contract. |
| next_action | N/A CLOSED. Do not auto-start `BR-LAUNCH-05`. Do not start post-launch work. |
| docs | [`free-trial-account-ops.md`](./free-trial-account-ops.md) |

### BR-LAUNCH-01

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-01` |
| name | Demo / New User State |
| parent | `TRUNK-06` |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-23 |
| return_to | `TRUNK-06` |
| reason | ????????????????????????? |
| evidence | Direct Launch-required children A/B/C CLOSED. C0/C1/C2 CLOSED. Remaining 01-lineage items are POST-LAUNCH / DEFERRED and not Launch blockers. |
| next_action | N/A CLOSED. Return `TRUNK-06`. Do not start `BR-LAUNCH-02-A`. |

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
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-23 |
| return_to | `BR-LAUNCH-01` |
| reason | New User Empty-State / Smoke Reset ? CLOSED????????????????????? |
| evidence | 01-A/01-B CLOSED; New User Reset ? Demo Reset; ??: wipe API ????user store inject API ???; meal/customers ? `years[].dailyMeal`?daily-inputs ? sales/BD ???; ?? `excel/*_official*` + `tests/generated-fixtures/`; Founder User Detail ??? UI ?? |
| next_action | N/A CLOSED. Return `BR-LAUNCH-01`. Do not start `BR-LAUNCH-02-A`. |
| constraint | ?????? UI ??????Founder/Admin ??????random ???01-B empty reset ??? |
| audit_note | Demo Reset = wipe?reuse `reset-user-kpi`?? apply seed ? `__KPI_AUTH.clear` ? re-login |
| confirmed_v1 | loader+dataset; restaurant; Pro; JPY; 2 past + operating; deterministic; Founder/Admin only |
| accounts | Founder Pro + Demo Basic/Pro??? dataset?plan?????C0 ??? |


### BR-LAUNCH-01-C2-L

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L |
| name | Flexible CSV / Excel Import Foundation |
| parent | BR-LAUNCH-01-C2 |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-23 |
| return_to | BR-LAUNCH-01-C2 |
| reason | User CSV/Excel should translate into KPN form; only untranslatable cases guide to KPN Template |
| principle | KPN does not require KPN-form CSV. Translate user CSV/Excel into KPN form as far as possible. Keep untranslated data for later user meaning/classification. Guide to KPN Template only when still uninterpretable. |
| children | L1 CLOSED; L1-A CLOSED; L2 CLOSED; L3 CLOSED; L4 CLOSED; L5 CLOSED; L5-A CLOSED; L5-B CLOSED; L6 CLOSED; L6-A DEFERRED; L6-B CLOSED |
| evidence | All launch-required children CLOSED. Launch importer contract LOCKED 2026-09-23. Post-launch: L6-A, Horizontal, Mixed, date inference, Preview, Ledger, tooltips. |
| next_action | CLOSED. Return to BR-LAUNCH-01-C2. Do not close C2. |
| constraint | no excel/ touch; no Demo Reset; no unilateral UX; BT unset Option B preserved; tooltips DEFERRED |

#### C2-L canonical product principle (2026-09-22)

KPN does not require KPN-form CSV.
Translate the user's CSV / Excel into KPN form as far as possible.
Do not discard data that cannot yet be translated; keep it so the user can later assign meaning / classification.
Guide to KPN Template only when the file is still uninterpretable.

#### C2-L canonical contract (2026-09-22)

1. Business Type source of truth is Profile (`store.meta.businessType`).
2. Import must not start while Business Type is unset.
3. CSV must not auto-change Business Type.
4. Known labels map to canonical lines.
5. Unknown labels are not discarded.
6. Unknown labels receive a stable internal ID.
7. Source / original label is retained.
8. Import Mapping / Preview is persisted.
9. Unknown expense initial bucket is `unclassified`.
10. User may later assign `fixed` / `variable`.
11. Reclassification `fixed` <-> `variable` is allowed.
12. Bucket change must not lose existing amount / lineId.
13. Existing row ▲▼ order remains.
14. Bucket and order are independent attributes.
15. KPN Template is the Golden Path.
16. Templates will exist for both Vertical and Horizontal (future).
17. Try user native CSV / Excel before Template.
18. Mixed income + expense input is a future target.
19. Daily / Monthly classification is interpreted by KPN when possible.
20. Import / Storage is plan-independent.
21. Visualization / Analysis is plan-dependent.
22. Basic should be able to store in-file Expense (direction).
23. Basic hides Expense UI.
24. Pro upgrade visualizes existing Expense immediately.
25. Pro -> Basic must not delete Expense.
26. Basic -> Pro restores without migration.
27. Reject only a clear Business Type mismatch.
28. An unknown label by itself is not a Business Type mismatch.

#### C2-L Launch importer contract (LOCKED 2026-09-23)

This is the Launch source of truth. Historical memos do not expand Launch promises.

KPN Launch supports:

- vertical CSV
- vertical Excel
- single-sheet Excel
- multi-sheet Excel with user Sheet Picker
- Sales import
- Daily Expense import
- Monthly Expense import
- Business Type gate
- high-confidence synonym mapping
- unknown label preservation
- persistent mapping
- user alias persistence
- unknown classification
- daily/monthly granularity preservation
- cached formula values only
- unsupported layout → KPN Template fallback
- JP / EN / ZH-TW

Launch does NOT promise:

- horizontal layouts
- mixed income + expense automatic split
- multi-sheet simultaneous import
- Import Profile reuse
- formula recalculation
- external workbook live references
- filename/sheet-name date inference
- arbitrary Excel reconstruction

Launch-required children (all CLOSED 2026-09-23): L1, L1-A, L2, L3, L3-A, L3-B, L4, L5, L5-A, L5-B, L6, L6-B.

Post-launch (not Launch blockers): L6-A, Horizontal parser, Mixed parser, advanced date inference, Preview expansion, Expense Ledger, Tooltip branch.

Canonical 28-point items 16 (Horizontal templates) and 18 (mixed income+expense) remain future / POST-LAUNCH.

#### C2-L superseded ideas (not canonical)

- A. User writes `restaurant` / `retail` into CSV A1 (or similar). Rejected. Business Type is Profile source of truth.
- B. Force-store unknown expense into `fixed` or `variable`. Rejected. Use `unclassified`, then user classification.

#### C2-L children

| id | name | status | note |
|----|------|--------|------|
| C2-L1 | Business Type Import Gate | CLOSED | Human Smoke PASS 2026-09-22 |
| C2-L1-A | Profile Business Type / Genre Sync | CLOSED | Human Smoke PASS 2026-09-22 |
| C2-L2 | High-confidence Expense Synonyms | CLOSED | Automated production smoke PASS 2026-09-22 |
| C2-L3 | Unknown Label Preservation + Persistent Import Mapping Record | CLOSED | L3-A/L3-B CLOSED 2026-09-22 |
| C2-L4 | Expense Classification Lifecycle | CLOSED | Human Smoke PASS 2026-09-22 |
| C2-L5 | Plan-independent Import / Storage + Basic/Pro Expense Visibility | CLOSED | L5-A/L5-B + first-load PASS 2026-09-23 |
| C2-L6 | Flexible Translator Expansion | CLOSED | Launch subset complete 2026-09-23. Post-launch items remain deferred. |
| C2-L6-B | Excel Sheet Picker — Launch | CLOSED | multi-sheet pick one; single-sheet no modal |
| C2-L6-A | Multi-sheet Import Profile | POST-LAUNCH / DEFERRED | reuse workbook sheet-role mapping |

### BR-LAUNCH-01-C2-L1

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L1 |
| name | Business Type Import Gate |
| parent | BR-LAUNCH-01-C2-L |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-21 |
| closed_at | 2026-09-22 |
| return_to | BR-LAUNCH-01-C2-L |
| reason | Import must start only after explicit Profile Business Type; do not use restaurant fallback as "set" |
| evidence | Human Smoke PASS: BT unset blocks Sales and Expense import; BT set opens Annual/MEP/PL picker; restaurant fallback does not bypass gate. Commit 714a62b |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2-L |
| constraint | isBusinessTypeSet only; no getBusinessType; no parser/mapping/seed/fallback change; no excel/ touch |

### BR-LAUNCH-01-C2-L1-A

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L1-A |
| name | Profile Business Type / Genre Sync |
| parent | BR-LAUNCH-01-C2-L1 |
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-22 |
| closed_at | 2026-09-22 |
| return_to | BR-LAUNCH-01-C2-L1 |
| reason | Profile confirmation/edit can show Genre as active while canonical Business Type is unset |
| evidence | Human Smoke PASS: BT unset account, Profile Edit Genre disabled+blank; first restaurant select stays blank; no stale 和食 auto-restore. Commits 115f553 / 456c683 |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2-L1 |
| constraint | Option 1 retain+inactive UI; no genre storage delete; no import gate / taxonomy / fallback change; no excel/ touch |

### BR-LAUNCH-01-C2-L2

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L2 |
| name | High-confidence Expense Synonyms |
| parent | BR-LAUNCH-01-C2-L |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-22 |
| closed_at | 2026-09-22 |
| return_to | BR-LAUNCH-01-C2-L |
| reason | Map known expense labels to canonical lines after BT gate |
| evidence | Automated production smoke PASS: prod JS LF-normalized SHA matches d320fd7; 6C C2-L2 contract 63/63; restaurant synonyms; retail isolation; alias>synonym; unmatched 人件費/手数料/その他; orphan/inactive fail-closed. Human visual smoke not required |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2-L |
| smoke_retail | `kpn_smoke_retail_pro01@trial.forge-laboratory.com` / `u_719d9f9880dc925d` / plan=pro / BT=retail / empty store |
| constraint | high-confidence exact synonyms only; restaurant-scoped food/drink; no fuzzy/AI/unknown auto-create; no excel/ touch |

### BR-LAUNCH-01-C2-L3

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L3 |
| name | Unknown Label Preservation + Persistent Import Mapping Record |
| parent | BR-LAUNCH-01-C2-L |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-22 |
| return_to | BR-LAUNCH-01-C2-L |
| reason | Keep unknown labels with stable IDs, source labels, and persisted mapping/preview |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2-L |
| constraint | unknown is not BT mismatch; do not discard |

### BR-LAUNCH-01-C2-L3-A

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L3-A |
| name | Unknown Expense Hold Foundation |
| parent | BR-LAUNCH-01-C2-L3 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-22 |
| return_to | BR-LAUNCH-01-C2-L3 |
| reason | Keep unknown expense label/amount/date in catalog-outside hold; no auto custom line |
| evidence | Automated tests scripts/_test_expense_unknown_hold_c2l3a.py; 6C/6H green; Option B-lite in pl.unknownHold |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2-L3 |
| constraint | no preview UI; no L3-B aliases; no L4 bucket; no new DB table |

### BR-LAUNCH-01-C2-L3-B

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L3-B |
| name | Persistent Mapping Record + Alias Server Persistence |
| parent | BR-LAUNCH-01-C2-L3 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-22 |
| return_to | BR-LAUNCH-01-C2-L3 |
| reason | Persist auto/user-assigned/unknown/skipped expense mappings; move aliases to user-scoped pl_json |
| evidence | scripts/_test_expense_import_mapping_c2l3b.py; 6C/6H/L3-A green; pl.expenseImportMapping |
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2-L3 |
| constraint | no Preview UI; Expense only; no catalog sibling; alias > synonym |

### BR-LAUNCH-01-C2-L4

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L4 |
| name | Expense Classification Lifecycle |
| parent | BR-LAUNCH-01-C2-L |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-22 |
| return_to | BR-LAUNCH-01-C2-L |
| reason | unclassified then user fixed/variable; allow reclass; preserve amount/lineId/order |
| next_action | CLOSED 2026-09-22 Human Smoke PASS. Do not reopen unless regression. Tooltip UX registered as BR-UI-PL-EXPENSE-CLASSIFY-TOOLTIPS (DEFERRED). |
| constraint | bucket and order independent; do not force unknown into fixed/variable |

### BR-LAUNCH-01-C2-L5

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L5 |
| name | Plan-independent Expense Storage + Basic / Pro Visibility |
| parent | BR-LAUNCH-01-C2-L |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-22 |
| closed_at | 2026-09-23 |
| return_to | BR-LAUNCH-01-C2-L |
| reason | Expense data must survive plan change on the server. Basic hides analysis UI. Pro hydrates existing expense without migration. |
| evidence | L5-A storage PASS; L5-B gates PASS; Monthly first-load fail-closed production PASS (`151d736`). Human Smoke NO. |
| next_action | CLOSED. Return to BR-LAUNCH-01-C2-L. |
| constraint | no mixed parser; no horizontal CSV; no new DB/schema; no tooltips; no Stripe; no excel/; no Demo fixture |
| phase | L5-A storage + L5-B UI entitlement + first-load fix CLOSED |

### BR-LAUNCH-01-C2-L5-A

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L5-A |
| name | Plan-independent Expense Storage / Upgrade Safety |
| parent | BR-LAUNCH-01-C2-L5 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-22 |
| closed_at | 2026-09-22 |
| return_to | BR-LAUNCH-01-C2-L5 |
| reason | Pro→Basic→Pro must not lose Expense. Option A: server retain, Basic no hydrate, Pro GET hydrate. |
| next_action | CLOSED. Return to C2-L5. UI entitlement is L5-B. |
| constraint | no PL/MEP/Monthly UI gates; no tooltips; no mixed CSV; no schema; no excel/; no Demo fixture |

### BR-LAUNCH-01-C2-L5-B

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L5-B |
| name | Basic / Pro Expense UI Entitlement |
| parent | BR-LAUNCH-01-C2-L5 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-23 |
| closed_at | 2026-09-23 |
| return_to | BR-LAUNCH-01-C2-L5 |
| reason | Storage vs UI entitlement split. Basic keeps Expense on server, hides Monthly Expense, gates MEP/PL via existing guardProPage. First-load fail-closed: Expense hidden until server-confirmed Pro (`151d736`). |
| next_action | CLOSED. Return to C2-L5 (parent then CLOSED to C2-L). |
| constraint | no L5-A storage change; no new auth framework; no Stripe; no schema; no excel/; no Demo fixture |

### BR-LAUNCH-01-C2-L6

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L6 |
| name | Flexible Translator Expansion |
| parent | BR-LAUNCH-01-C2-L |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-23 |
| closed_at | 2026-09-23 |
| return_to | BR-LAUNCH-01-C2-L |
| phase | Launch subset complete (Sheet Picker + Template fallback) |
| reason | SMALL launch subset: picker + template fallback only. |
| evidence | L6-B CLOSED (`b36bbf7`). Launch subset complete. Horizontal/Mixed/L6-A remain POST-LAUNCH. |
| next_action | CLOSED. Return to C2-L (parent then CLOSED to C2). |
| constraint | no excel/; no real-world workbook fixture; no parser redesign |

#### C2-L6 canonical principles (2026-09-23)

1. Do not reproduce every Excel/CSV feature in KPN. Prefer data that maps to Daily / Monthly / MEP / PL.
2. Do not drop a valid expense the user has, if KPN can hold that line. Unused-looking extras are not the same as discard-by-policy.
3. Granularity: keep daily when daily exists; accept monthly when only monthly exists. Do not coarsen daily just to simplify. Do not reject monthly for being coarse. Example: part-time labor monthly total -> monthly expense; daily labor cost -> daily expense.
4. Complex workbooks: do not auto-understand all sheets. Preferred direction is Workbook -> sheet list -> user picks a sheet -> existing translator.
5. Later, one workbook may name several sources (Sales, Monthly Expense, Daily Expense, Labor). Launch does not commit to a full Multi-sheet Import Profile.
6. KPN limits sheet purpose. Candidates: Sales data / Monthly Expense / Daily Expense / Ignore. Do not turn the importer into an accounting suite.

#### C2-L6 Launch Scope Audit (2026-09-23)

Product boundary: translate business data into Daily / Monthly / MEP / PL. Do not recreate Excel.

| Candidate | Class | Note |
|-----------|-------|------|
| Sheet Picker (list → user pick → existing translator) | LAUNCH-SHOULD | Separate from multi-sheet auto-analysis. SheetJS `SheetNames` already available. Current importer is first-sheet-only. |
| Sheet Purpose Mapping UI | POST-LAUNCH | Launch purpose is implicit via upload surface (Sales vs Expense). Unified mapping UI is not required yet. |
| Horizontal unpivot | POST-LAUNCH | Template fallback. Parser redesign + false-positive risk. |
| Mixed income+expense on one sheet | POST-LAUNCH | Not the same as multi-sheet merge. Split in Excel or Template. |
| Granularity preservation | LAUNCH-MUST (policy) | Daily source stays daily; monthly stays monthly. Auto source-priority engine is POST-LAUNCH; user chooses by which sheet/file they import. |
| Formula cached values | LAUNCH-MUST (contract) | Read `cell.v` only. No formula engine. Cross-sheet OK if Excel cached. External / missing cache = skip or fail that cell. |
| Advanced date/year inference (M/D, sheet name, filename) | POST-LAUNCH | Keep YYYY-MM-DD / YYYY-MM / Excel serial. Avoid false positives. |
| Multi-sheet Import Profile (L6-A) | POST-LAUNCH / DEFERRED | Depends on Picker + Purpose. Do not build before Launch. |
| Template fallback | LAUNCH-MUST (golden path) | Sufficient for unsupported layout. PARTIAL for ~20-sheet real workbooks. |
| Auto-understand all sheets / formula reimplementation / accounting suite | REJECT | Out of KPN boundary. |

Recommended Launch subset: SMALL. 2026-09-23 implement: Sheet Picker + Template fallback only.

Closeout 2026-09-23: Launch subset complete. C2-L6 CLOSED. Remaining candidates in the table above stay POST-LAUNCH / REJECT. They are not Launch blockers.

### BR-LAUNCH-01-C2-L6-B

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L6-B |
| name | Excel Sheet Picker — Launch |
| parent | BR-LAUNCH-01-C2-L6 |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-23 |
| closed_at | 2026-09-23 |
| return_to | BR-LAUNCH-01-C2-L6 |
| reason | Multi-sheet Excel: user picks one sheet. Single-sheet: no picker. Cached values only. Template fallback on unreadable. Purpose from existing import entry. |
| evidence | Local picker tests 102 PASS. Production MEP picker+cancel 3-lang PASS (`b36bbf7`). Human Smoke NO. |
| next_action | CLOSED. Return to C2-L6. Horizontal/Mixed/L6-A remain POST-LAUNCH. |
| constraint | Excel only; no first-sheet auto-import when sheet count>1; no recommended-sheet AI; no excel/ touch; no real restaurant workbook |

### BR-LAUNCH-01-C2-L6-A

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L6-A |
| name | Multi-sheet Import Profile |
| parent | BR-LAUNCH-01-C2-L6 |
| status | POST-LAUNCH / DEFERRED |
| priority | P2 |
| started_at | not started |
| return_to | BR-LAUNCH-01-C2-L6 |
| reason | Save sheet-role mapping for the same workbook layout and reuse next month. Depends on Sheet Picker + Purpose Mapping. |
| next_action | REGISTER ONLY. Do not implement. |
| constraint | no auto multi-sheet analysis; no product code now |

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
| next_action | N/A (CLOSED) -> return BR-LAUNCH-01-C2 -> C2-L ACTIVE |
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
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-23 |
| return_to | `BR-LAUNCH-01-C2` |
| phase | CLOSED 2026-09-23. Production Playwright smoke PASS. |
| reason | Same Chrome profile = one KPN session cookie. Stale tab must not PUT account A payload into account B store. |
| evidence | implement `d935bbb`; FTPS 101 files RETR+HTTP markers OK; prod smoke store/daily/profile 403 stale_account; B store/profile unchanged; missing expected 428; same-user PUT 200; logout PUT 401; Tab A stale after B login; JP alert; same-account two tabs not stale. Destination remains session. OCC 409 unchanged. |
| next_action | N/A CLOSED. Return BR-LAUNCH-01-C2. Superseded by C2 CLOSED (Human Smoke NONE). |
| constraint | no multi-account same profile; no new auth framework; no excel/; no Demo data; no password change |

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
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-23 |
| return_to | `BR-LAUNCH-01-C` |
| reason | ???????????? 3 ?????Demo Reset / Sales CSV / Expenses CSV? |
| evidence | fixtures/demo/restaurant-v1 ?? CSV ????integrity OK??docs/demo-operation-pack.md?Reset=reuse reset-user-kpi?runtime ???????? Sheet Picker z-index 20120 production pointer smoke PASS `751ce10` |
| next_action | N/A CLOSED. Return BR-LAUNCH-01-C. Human Smoke NONE. Do not start BR-LAUNCH-02-A. |
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
| status | CLOSED |
| priority | P0 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-23 |
| return_to | `BR-LAUNCH-01-C` |
| reason | Demo Seed API ?? generated-fixtures ???? restaurant Demo v1 ? deterministic dataset ??????? |
| evidence | Canonical pack tracked at `fixtures/demo/restaurant-v1`. Fixture integrity PASS. Demo Pro persistable MATCH (untouched). Demo Basic sales-only seed PASS: BT restaurant, plan basic, 2024–2026 sales/BD match fixture, expenses absent, unknownHold empty, C2L4 absent. MEP/PL `guardProPage` → change_plan. Annual/Monthly work. |
| next_action | N/A CLOSED. Return `BR-LAUNCH-01-C` (parent also CLOSED). Do not start `BR-LAUNCH-02-A`. |
| constraint | runtime????; dataset??????????; excel untouched |

### BR-LAUNCH-02

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-02` |
| name | Production Smoke / Operational Runbook |
| parent | `TRUNK-06` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-24 |
| return_to | `TRUNK-06` |
| reason | Production smoke / operational runbook after Demo / New-user (01) CLOSED. |
| evidence | Children 02-A/02-B CLOSED. Production regression PASS (Demo Pro rev 54 unchanged; Human Smoke NONE; founder/empty-state SKIP = ops password, not product FAIL). Runbook [`docs/launch-operational-runbook.md`](./launch-operational-runbook.md). Restore API not Launch-required. Launch blocker 0. |
| next_action | N/A CLOSED. Return `TRUNK-06`. Do not start `BR-LAUNCH-03`. |
| close_when | Launch ops runbook contract exists AND `BR-LAUNCH-02-A` CLOSED. Then return `TRUNK-06`. MET 2026-09-24. |

### BR-LAUNCH-02-A

| Field | Value |
|-------|-------|
| id | `BR-LAUNCH-02-A` |
| name | Launch Regression Smoke / Cross-feature Regression |
| parent | `BR-LAUNCH-02` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-24 |
| closed_at | 2026-09-24 |
| return_to | `BR-LAUNCH-02` |
| reason | After parent C remaining Launch-required children close, run cross-feature production smoke before Launch: Login, Annual, Monthly, MEP, PL, Booking, Profile, Subscription, Session, Import, 3-lang, plan entitlement, account switching. |
| evidence | Production automated regression PASS 2026-09-24. Demo Pro revision 54 unchanged. Basic sales/BT match. Entitlement / picker z=20120 / 3-lang / stale_account 403 / registration_disabled / Template fallback PASS. Founder/empty-state login SKIP (ops password absent). Human Smoke NONE. Rollback not needed. No data mutation. |
| next_action | N/A CLOSED. Parent `BR-LAUNCH-02` CLOSED. Do not start `BR-LAUNCH-03`. |
| constraint | no product feature work in this node; smoke only |

### BR-LAUNCH-02-B

| Field | Value |
|-------|-------|
| id | `BR-LAUNCH-02-B` |
| name | Launch Operational Runbook Inventory |
| parent | `BR-LAUNCH-02` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-23 |
| closed_at | 2026-09-24 |
| return_to | `BR-LAUNCH-02` |
| reason | Parent 02 contract is Production Smoke + Operational Runbook. Smoke child `02-A` is REGISTER ONLY. Launch ops knowledge is scattered; no single Launch runbook. Inventory/consolidate before regression smoke. |
| evidence | [`docs/launch-operational-runbook.md`](./launch-operational-runbook.md). Inventory: Demo/Account COMPLETE enough; Deploy/Backup/OCC/stale PARTIAL; data restore API MISSING (Launch = do not rollback data). Implementation Needed NO. |
| next_action | N/A CLOSED. Return `BR-LAUNCH-02`. Do not auto-start `BR-LAUNCH-02-A`. |
| constraint | no product feature; no excel/; no Demo Pro overwrite; no 02-A smoke |

### BR-LAUNCH-03

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-03` |
| name | UI Consistency Audit |
| parent | `TRUNK-06` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-20 |
| closed_at | 2026-09-24 |
| return_to | `TRUNK-06` |
| reason | Annual / Monthly / FW UI consistency before Launch. Inventory first. No redesign. |
| evidence | Children A–F CLOSED. R1 48/48, R2 17/17, R3 21/21, R4 18/18, R5/03-E 37/37, 03-F 16/16 production smoke PASS. Human Review NO on all children. No remaining Launch-required P1 under 03. P2 U11–U20 deferred. |
| close_when | Launch-required P1 children A–F CLOSED (R1–R5 + Office Focus Bar). Then return `TRUNK-06`. MET 2026-09-24. |
| next_action | N/A CLOSED. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-04`. |

### BR-LAUNCH-03-A

| field | value |
|-------|-------|
| id | `BR-LAUNCH-03-A` |
| name | Shared Header 1200 Repair |
| parent | `BR-LAUNCH-03` |
| status | CLOSED |
| priority | P1 |
| return_to | `BR-LAUNCH-03` |
| reason | R1. `#btn-mode-text::after` Office hang at 1200px. |
| closed_at | 2026-09-24 |
| evidence | `7d3fe9e` CSS + `989681c` cache-bust. Production smoke 48/48 PASS (1200/1201/1280/1440 × JA/EN/ZH-TW × Annual/Monthly/MEP/PL). overflowX=0. Office in-flow. |
| next_action | N/A CLOSED. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-03-B`. |

### BR-LAUNCH-03-B

| field | value |
|-------|-------|
| id | `BR-LAUNCH-03-B` |
| name | Shared Chrome i18n (JA / ZH-TW) |
| parent | `BR-LAUNCH-03` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-24 |
| closed_at | 2026-09-24 |
| return_to | `BR-LAUNCH-03` |
| reason | R2. Leftover English on JA/ZH surfaces (U02 U03 U05 U07 U08 U09 U10 + U06 copy). No new i18n framework. EN Login casing is P2 U15 — not rewritten. |
| evidence | `8f11df5` register 03-E + start; `9f12b5f` i18n. Production smoke 17/17 PASS. JA フォーカスバー/保存/ロック copy; ZH 焦點列; EN Focus Bar retained. |
| next_action | N/A CLOSED. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-03-C` / `BR-LAUNCH-03-E`. |

### BR-LAUNCH-03-C

| field | value |
|-------|-------|
| id | `BR-LAUNCH-03-C` |
| name | Basic Monthly Layout Collapse |
| parent | `BR-LAUNCH-03` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-24 |
| closed_at | 2026-09-24 |
| return_to | `BR-LAUNCH-03` |
| reason | R3. space-between hole when 編集 hidden. CSS-only collapse. Do not change entitlement. |
| evidence | `61d23a8`. Production smoke 21/21 PASS. Basic gapRight=0; Pro gapRight=908 Edit visible. 1200/1280/1440 × JA/EN/ZH-TW. MEP/PL Basic redirect + iso + mode toggle PASS. |
| next_action | N/A CLOSED. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-03-D` / `BR-LAUNCH-03-E`. |

### BR-LAUNCH-03-D

| field | value |
|-------|-------|
| id | `BR-LAUNCH-03-D` |
| name | MEP Tutorial / AUTO CALC Overlap |
| parent | `BR-LAUNCH-03` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-24 |
| closed_at | 2026-09-24 |
| return_to | `BR-LAUNCH-03` |
| reason | R4. `#tutorial-toggle-float` vs `.monthly-edit-float__label-prefix`. Left gutter = float width + left offset. Do not restyle switch. Do not start `03-E` / `03-F`. |
| evidence | `4b8097b` / `d54bbe6`. Production smoke 18/18 PASS. AABB overlapN=0. 1200/1280/1440 × JA/EN/ZH-TW × Sci-Fi/Office. Pointer + overflowX=0. Human Review NO. |
| next_action | N/A CLOSED. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-03-E` / `BR-LAUNCH-03-F`. |

### BR-LAUNCH-03-E

| field | value |
|-------|-------|
| id | `BR-LAUNCH-03-E` |
| name | Responsive Eligibility Gate / Unsupported Viewport Guidance |
| parent | `BR-LAUNCH-03` |
| status | CLOSED |
| priority | P1 / Launch required |
| started_at | 2026-09-24 |
| closed_at | 2026-09-24 |
| return_to | `BR-LAUNCH-03` |
| reason | Desktop-first. Smartphone / tablet portrait / landscape below KPN minimum width must not show broken app UI. Show dedicated guidance (JP/EN/ZH-TW). Viewport + orientation; do not use User-Agent as source of truth. Min-width not frozen at register — measure in implementation audit vs 1200px contract. Do not build a mobile KPN. |
| evidence | `ad1654d`. Measured min width = 1200 CSS px (R1 contract). CSS `@media (max-width: 1199.98px)` on login-page/profile-page. Production smoke 37/37 PASS. Phone/tablet portrait + narrow landscape → guidance; 1200/1280/1440 + iPad Pro landscape 1366 → KPN. Rotate/resize no redirect. Human Review NO. |
| next_action | N/A CLOSED. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-03-F`. |
| constraint | no mobile layout; no UA; no excel/; no 03-F |

### BR-LAUNCH-03-F

| field | value |
|-------|-------|
| id | `BR-LAUNCH-03-F` |
| name | Office Mode Focus Bar Color Consistency |
| parent | `BR-LAUNCH-03` |
| status | CLOSED |
| priority | P1 Launch polish |
| return_to | `BR-LAUNCH-03` |
| closed_at | 2026-09-24 |
| reason | Office Mode Focus Bar stays Sci-Fi black on Monthly ZH-TW (likely shared). Desired: outer medium-light gray, cells lighter gray, black text, Office borders. No cyan/white Sci-Fi text. Audit Monthly + Annual/MEP/PL shared component; JP/EN/ZH-TW; shared vs lang CSS. Do not ZH-only patch. |
| evidence | `09b8338`. Production smoke 16/16 PASS. Monthly Office fill `rgb(210,210,210)` / cells `rgb(232,232,232)` / text `rgb(17,17,17)`. Sci-Fi fill `#000` + cyan preserved. Annual Office already gray/`#111`. |
| next_action | N/A CLOSED. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-04`. |
| constraint | Sci-Fi unchanged; no Focus Bar behavior/layout/font change; excel/ untouched; do not start BR-LAUNCH-04 |

### BR-LAUNCH-04

| ????? | ? |
|------------|-----|
| id | `BR-LAUNCH-04` |
| name | PL Editable Cell Visual Finish |
| parent | `TRUNK-06` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-24 |
| return_to | `TRUNK-06` |
| reason | PL editable cells must be visually distinct from read-only / label / total; Sci-Fi/Office and JP/EN/ZH-TW consistent. Visual finish only. |
| evidence | Phase 1: [`docs/pl-editable-cell-audit-04.md`](./pl-editable-cell-audit-04.md). Phase 2 production smoke 7/7 PASS. CSS rest/hover/focus + Office daily dim. |
| next_action | N/A CLOSED. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |

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

### BR-LAUNCH-06

| Field | Value |
|-------|-------|
| id | `BR-LAUNCH-06` |
| name | PL Excel Download Repair |
| parent | `TRUNK-06` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-24 |
| return_to | `TRUNK-06` |
| reason | Visible PL 「Excelダウンロード」 navigates to blob: URL then Chrome ERR_FILE_NOT_FOUND. Restore current intended download. Not a new workbook. |
| evidence | Phase 1: [`docs/pl-excel-download-audit-06.md`](./pl-excel-download-audit-06.md). Phase 2: delay `revokeObjectURL` 1000ms + button CSV labels. Production smoke 10/10 PASS. SHA `0b8a323`. |
| next_action | N/A CLOSED. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-07`. True XLSX is `BR-POST-XLSX-REPORT` (REGISTER ONLY). |
| constraint | Launch repair of current button only; excel/ untouched; BR-LAUNCH-05 stays DEFERRED |

### BR-LAUNCH-07

| Field | Value |
|-------|-------|
| id | `BR-LAUNCH-07` |
| name | Global Menu Spacing / Reservation Button Collision |
| parent | `TRUNK-06` |
| status | CLOSED |
| priority | P1 |
| started_at | 2026-09-25 |
| return_to | `TRUNK-06` |
| reason | Launch-required chrome spacing / reservation button collision. |
| evidence | Phase 1: [`docs/global-menu-spacing-audit-07.md`](./global-menu-spacing-audit-07.md). Phase 2: shared `--kpi-header-actions-reserve: 368px` + `--kpi-header-nav-gap: 20px`. Production smoke 113/114 PASS (ZH-TW PL has no `#header-booking-btn` pre-existing). SHA `bbe3907`. |
| next_action | N/A CLOSED. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |

### BR-LAUNCH-08

| Field | Value |
|-------|-------|
| id | `BR-LAUNCH-08` |
| name | ZH-TW PL Global Menu Parity Repair |
| parent | `TRUNK-06` |
| status | CLOSED |
| priority | P1 Launch-required |
| started_at | 2026-09-25 |
| return_to | `TRUNK-06` |
| reason | Accidental locale/page omission. Shared Global Menu contract includes `#header-booking-btn` for JP / EN / ZH-TW. `zh-tw/app/profit/pl/index.html` is a forked unmarked header (Mode then DL; no booking). JP PL and EN PL include booking via `build_pl_table_page.py` → `site_chrome.build_header`. Other ZH-TW site_chrome pages (Annual / Monthly / MEP / profit landing / booking / settings) include booking. Not contractual exclusion. |
| evidence | Header via `scripts/pl_chrome.py` `pl_header()` → `site_chrome.build_header` (`--sync-zh-tw-header`). Full ZH-TW PL body not regenerated. Office gap uses `--kpi-header-nav-gap`. Production smoke 25/25 PASS (JA/EN/ZH-TW × Sci-Fi/Office × 1200–1440 + Basic redirect). SHA `90468d9` / `06ca877` / `369c036`. |
| next_action | N/A CLOSED. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |
| constraint | excel/ untouched; no booking feature change; no 07 geometry reopen unless regression; 3-lang chrome parity only |

### BR-POST-XLSX-REPORT

| Field | Value |
|-------|-------|
| id | `BR-POST-XLSX-REPORT` |
| name | True XLSX / PL Report Export |
| parent | `TRUNK-06` |
| status | DEFERRED |
| priority | HIGH |
| started_at | not started |
| return_to | `TRUNK-06` |
| reason | Post-launch workbook: PL / MEP report export, accountant sharing, local archive, Balca 18th-period style annual workbook, Report Sheet + machine-readable KPN Data sheet, future re-upload compatibility. |
| next_action | REGISTER ONLY. Do not implement in Launch. Do not expand `BR-LAUNCH-06`. |
| constraint | excel/ untouched; not CSV download repair |

---

## 8. DEFERRED BRANCHES????

### BR-UI-PL-EXPENSE-CLASSIFY-TOOLTIPS

| Field | Value |
|-------|-------|
| id | `BR-UI-PL-EXPENSE-CLASSIFY-TOOLTIPS` |
| name | Expense Classification Discoverability / Tooltips |
| parent | `BR-LAUNCH-01-C2` |
| status | DEFERRED |
| priority | P2 |
| started_at | not started |
| return_to | `BR-LAUNCH-01-C2` |
| reason | C2-L4 feature works; discoverability is weak. Do not block current CSV/Excel launch path. |
| scope | expense row label hover: 「クリックして科目設定を編集」; 科目管理: 「未分類の取込費目を分類できます」; fixed/variable selection preserves amount when safe; daily data prevents fixed classification — explain why blocked |
| next_action | REGISTER ONLY. Do not implement tooltips now. |


### BR-POST-EXPENSE-LEDGER

| Field | Value |
|-------|-------|
| id | `BR-POST-EXPENSE-LEDGER` |
| name | Purchase / Expense Ledger to MEP / PL |
| parent | `BR-LAUNCH-01-C2` |
| status | DEFERRED |
| priority | P2 |
| started_at | not started |
| return_to | `BR-LAUNCH-01-C2` |
| reason | Primary spend ledger (date, vendor, genre, amount, pay method, account) feeding Daily Expense -> MEP -> PL. Restaurant food/drink purchase; retail stock; beauty materials; hotel amenity. Input from receipts/invoices/delivery slips. |
| next_action | REGISTER ONLY. Do not implement. Not an Excel accounting clone. |
| constraint | no Launch parser work; no Demo fixture; no excel/ |

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
| `BR-LAUNCH-01` | Demo / New User State | CLOSED | P0 | `TRUNK-06` |
| `BR-LAUNCH-02` | Production Smoke / Operational Runbook | CLOSED | P1 | `TRUNK-06` |
| `BR-LAUNCH-02-B` | Launch Operational Runbook Inventory | CLOSED | P1 | `BR-LAUNCH-02` |
| `BR-LAUNCH-01-C` | Demo Seed / Demo Reset | CLOSED | P0 | `BR-LAUNCH-01` |
| `BR-LAUNCH-01-C1` | Demo Dataset Contract & Existing Fixture Audit | CLOSED | P0 | `BR-LAUNCH-01-C` |
| `BR-LAUNCH-01-C2` | Demo Operation Pack | CLOSED | P0 | `BR-LAUNCH-01-C` |
| `BR-LAUNCH-01-C2-C` | Cross-Tab Account Session Collision | CLOSED | P0 | `BR-LAUNCH-01-C2` |
| `BR-LAUNCH-01-C2-L` | Flexible CSV / Excel Import Foundation | CLOSED | P0 | `BR-LAUNCH-01-C2` |
| `BR-LAUNCH-01-C2-L5` | Plan-independent Expense Storage + Basic / Pro Visibility | CLOSED | P1 | `BR-LAUNCH-01-C2-L` |
| `BR-LAUNCH-01-C2-L5-A` | Plan-independent Expense Storage / Upgrade Safety | CLOSED | P1 | `BR-LAUNCH-01-C2-L5` |
| `BR-LAUNCH-01-C2-L5-B` | Basic / Pro Expense UI Entitlement | CLOSED | P1 | `BR-LAUNCH-01-C2-L5` |
| `BR-LAUNCH-01-C2-L6` | Flexible Translator Expansion | CLOSED | P1 | `BR-LAUNCH-01-C2-L` |
| `BR-LAUNCH-01-C2-L6-B` | Excel Sheet Picker — Launch | CLOSED | P1 | `BR-LAUNCH-01-C2-L6` |
| `BR-LAUNCH-01-C2-L6-A` | Multi-sheet Import Profile | POST-LAUNCH / DEFERRED | P2 | `BR-LAUNCH-01-C2-L6` |
| `BR-LAUNCH-02-A` | Launch Regression Smoke / Cross-feature Regression | CLOSED | P1 | `BR-LAUNCH-02` |
| `BR-POST-EXPENSE-LEDGER` | Purchase / Expense Ledger | DEFERRED | P2 | `BR-LAUNCH-01-C2` |
| `BR-LAUNCH-06` | PL Excel Download Repair | CLOSED | P1 | `TRUNK-06` |
| `BR-LAUNCH-07` | Global Menu Spacing / Reservation Button Collision | CLOSED | P1 | `TRUNK-06` |
| `BR-LAUNCH-08` | ZH-TW PL Global Menu Parity Repair | CLOSED | P1 | `TRUNK-06` |
| `BR-POST-XLSX-REPORT` | True XLSX / PL Report Export | POST-LAUNCH / DEFERRED | HIGH | `TRUNK-06` |

CLOSED under `TRUNK-06`: `BR-LAUNCH-01`, `BR-LAUNCH-02`, `BR-LAUNCH-03`, `BR-LAUNCH-04`, `BR-LAUNCH-06`, `BR-LAUNCH-07`, `BR-LAUNCH-08`  
CLOSED under `BR-LAUNCH-02`: `BR-LAUNCH-02-A`, `BR-LAUNCH-02-B`  
CLOSED under `BR-LAUNCH-01`: `BR-LAUNCH-01-A`, `BR-LAUNCH-01-B`, `BR-LAUNCH-01-C`  
CLOSED under `BR-LAUNCH-01-C`: `BR-LAUNCH-01-C0`, `BR-LAUNCH-01-C1`, `BR-LAUNCH-01-C2`  
CLOSED under `BR-LAUNCH-01-C2`: `BR-LAUNCH-01-C2-C` (stale-tab), `BR-LAUNCH-01-C2-L` (Launch importer)  
CLOSED under `BR-LAUNCH-01-C2-L`: `BR-LAUNCH-01-C2-L1`, `BR-LAUNCH-01-C2-L2`, `BR-LAUNCH-01-C2-L3`, `BR-LAUNCH-01-C2-L4`, `BR-LAUNCH-01-C2-L5`, `BR-LAUNCH-01-C2-L6`  
CLOSED under `BR-LAUNCH-01-C2-L6`: `BR-LAUNCH-01-C2-L6-B`  
CLOSED under `BR-LAUNCH-01-C2-L5`: `BR-LAUNCH-01-C2-L5-A`, `BR-LAUNCH-01-C2-L5-B`  
CLOSED under `BR-LAUNCH-01-C2-L3`: `BR-LAUNCH-01-C2-L3-A`, `BR-LAUNCH-01-C2-L3-B`  
CLOSED under `BR-LAUNCH-01-C2-L1`: `BR-LAUNCH-01-C2-L1-A`  
ACTIVE under `TRUNK-06`: none (trunk CLOSED)  
PAUSED / REGISTER ONLY under `TRUNK-06`: none  
CLOSED under `BR-LAUNCH-03`: `BR-LAUNCH-03-A`, `BR-LAUNCH-03-B`, `BR-LAUNCH-03-C`, `BR-LAUNCH-03-D`, `BR-LAUNCH-03-E`, `BR-LAUNCH-03-F`  
PAUSED under `TRUNK-06` (legacy): none  
ACTIVE under `BR-LAUNCH-02`: none (parent CLOSED)  
DEFERRED / ACTIVE-LATER: none under `BR-LAUNCH-02` (`BR-LAUNCH-02-A` CLOSED)  
DEFERRED under `TRUNK-06`: `BR-LAUNCH-05`, `BR-POST-XLSX-REPORT`  
DEFERRED UX: `BR-UI-PL-EXPENSE-CLASSIFY-TOOLTIPS` (parent `BR-LAUNCH-01-C2`, P2), `BR-UI-PL-INSIGHT-FIRSTOPEN-PERF`  
DEFERRED importer (not Launch blockers): `BR-LAUNCH-01-C2-L6-A`, Horizontal parser, Mixed parser, advanced date inference, Preview expansion, `BR-POST-EXPENSE-LEDGER`

---

## 10. UNKNOWN / OPEN QUESTIONS

| ?? | ?? |
|------|------|
| Unit 5C-3 / 5C-4 | marker?doc ?? ? **UNKNOWN** |
| Unit 5D ?? | **UNKNOWN**????? TRUNK-06? |
| FW Audit ?? Floating Window ?????? | ?? tests ? Daily / Top Insight / PL Insight ?????????? COMPLETE ?? doc ?? ? **UNKNOWN** |
| `TR-UNIT-5B` / `TR-UNIT-5C` ???? started_at | **UNKNOWN** |
| BR-LAUNCH-01 remaining Launch-required | **RESOLVED 2026-09-23** A/B/C CLOSED. 01 CLOSED. Remaining 01-lineage items are POST-LAUNCH / DEFERRED (not Launch blockers). |
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
| 2026-09-21 | **BR-LAUNCH-01-C2-L** Flexible CSV / Excel Import Foundation ACTIVE (handoff fixed; CURRENT PATH -> C2-L) |
| 2026-09-21 | **BR-LAUNCH-01-C2-L1** Business Type Import Gate ACTIVE ? Sales/PL/MEP import blocked until explicit BT; Human Smoke pending |
| 2026-09-22 | **BR-LAUNCH-01-C2-L1-A** Profile Business Type / Genre Sync ACTIVE (Option 1 retain+inactive UI; Human Smoke pending; do not close C2-L1 / start C2-L2) |
| 2026-09-22 | **C2-L Specification Consolidated** canonical translate-not-require + 28-point contract + superseded A/B; register L2-L5 spec-only and L6 POST-LAUNCH; CURRENT PATH unchanged (L1-A Human Smoke) |
| 2026-09-22 | **BR-LAUNCH-01-C2-L1-A CLOSED** Human Smoke PASS (unset Genre blank; first restaurant no stale 和食). CURRENT PATH -> C2-L1. Gate already in 714a62b; C2-L1 remains ACTIVE pending import Human Smoke |
| 2026-09-22 | **BR-LAUNCH-01-C2-L1 CLOSED** Human Smoke PASS (unset blocks Sales/Expense; BT set opens picker; no restaurant-fallback bypass). CURRENT PATH -> C2-L2. Phase 1 audit only |
| 2026-09-22 | **BR-LAUNCH-01-C2-L2** high-confidence expense synonyms in shared resolver (alias-first; restaurant-only food/drink; Human Smoke pending) |
| 2026-09-22 | Retail smoke Pro account created: `kpn_smoke_retail_pro01@trial.forge-laboratory.com` / `u_719d9f9880dc925d` / BT=retail / empty. Demo restaurant accounts untouched |
| 2026-09-22 | **BR-LAUNCH-01-C2-L2 CLOSED** automated production smoke PASS (prod JS matches d320fd7; 6C contract). CURRENT PATH -> C2-L3. Human visual smoke not required |
| 2026-09-22 | **C2-L3 Phase 1 AUDIT** unknown raw is PARTIAL; recommend Option B-lite in existing pl_json (no new table, no auto-create). Wait for implement. Do not start C2-L4 |
| 2026-09-22 | **BR-LAUNCH-01-C2-L3-A CLOSED** unknown expense hold (catalog-outside, unk_ + fnv1a). CURRENT PATH stays C2-L3. Do not start L3-B / L4 / L5 |
| 2026-09-22 | **BR-LAUNCH-01-C2-L3-B CLOSED** persistent mapping record + user-scoped alias persistence (pl.expenseImportMapping). Preview UI not started. Do not start L4 / L5 |
| 2026-09-22 | **BR-LAUNCH-01-C2-L3 CLOSED**. **C2-L4 ACTIVE** Phase 1 AUDIT only (no classification UI / no amount move) |
| 2026-09-22 | **C2-L4 launch-safe implement** custom-only setLineBucket; daily-data BLOCK; unknown hold → classified custom (hold resolved, not deleted). Human Smoke 1 UX block. Do not start L5 / L6 |
| 2026-09-22 | **BR-LAUNCH-01-C2-L4 CLOSED** Human Smoke PASS (custom 販促費 → 固定費 amount kept; unknown 予約媒体利用料 → 変動費 6789). Tooltip discoverability follow-up not started. CURRENT PATH -> C2-L |
| 2026-09-23 | **BR-LAUNCH-01-C2-L5 CLOSED** L5-A storage + L5-B entitlement + Monthly first-load fail-closed production PASS (`151d736`). Human Smoke NO. Return C2-L. |
| 2026-09-23 | **BR-LAUNCH-01-C2-L6 ACTIVE** Launch Scope Audit only. Canonical principles registered. L6-A Multi-sheet Import Profile and BR-POST-EXPENSE-LEDGER DEFERRED. CURRENT PATH -> C2-L6. Do not implement. |
| 2026-09-23 | **BR-LAUNCH-01-C2-L6-B ACTIVE** Excel Sheet Picker + Template fallback. CURRENT PATH -> L6-B. Horizontal/Mixed/L6-A remain POST-LAUNCH. |
| 2026-09-23 | **BR-LAUNCH-01-C2-L6-B CLOSED** picker + template fallback `b36bbf7`. Local 102 PASS. Production MEP picker+cancel 3-lang PASS. Human Smoke NO. Return C2-L6. |
| 2026-09-23 | **C2-L6 CLOSED** Launch subset complete (picker + template fallback). Horizontal/Mixed/L6-A/date inference/Preview remain POST-LAUNCH. Not Launch blockers. |
| 2026-09-23 | **C2-L CLOSED** All launch-required children CLOSED. Launch importer contract LOCKED. CURRENT PATH -> BR-LAUNCH-01-C2. Do not close C2 (C2-C + Human Import Smoke remain). |
| 2026-09-23 | **C2-C Launch blocker fix implementing** pageUserId snapshot + lastKpiUserId storage stale + server expectedUserId (403 stale_account). Destination remains session. OCC unchanged. |
| 2026-09-23 | **C2-C CLOSED** `d935bbb` deploy + production Playwright smoke PASS (wrong-account store/daily/profile BLOCKED; same-user multi-tab OK; logout 401). Launch blocker RESOLVED. CURRENT PATH -> C2. Human Import Smoke still pending. Do not close C2. |
| 2026-09-23 | **C2 pre-Human automated import smoke** local 6 PASS; production MEP/PL picker+mapping+cancel PASS; 3-lang picker/fallback PASS; Basic entitlement PASS; stale 403 PASS. FAIL: Annual client BT gap (server restaurant/retail, Annual isBusinessTypeSet=false). Human visual 1 BLOCK (4 screens). Registered `BR-LAUNCH-02-A`. Do not close C2. |
| 2026-09-23 | **Annual client BT hydration gap fix** `045c648`. Cause: Annual never called `enableSessionStoreSyncIfAuthed` so cookie-auth Playwright skipped store GET. Fix: Annual-only (JP/EN/ZH-TW) same MEP helper; explicit server BT hydrates before import gate; restaurant fallback does not satisfy `isBusinessTypeSet()`. Production A-E PASS (restaurant/retail/unset/reload/3-lang). MEP/PL still PASS. Do not close C2 (Human visual 1 BLOCK remains). |
| 2026-09-23 | **C2 final production Demo Import smoke** BT hydrate + MEP/PL picker/mapping/confirm/cancel + 3-lang + stale 403 + Demo Pro/Retail data unchanged PASS. Remaining 1 BLOCK: Annual/Past Sales Sheet Picker z-index 13000 under host modal 20055 (`elementFromPoint` hits sales grid). Human visual not required. Do not close C2. `BR-LAUNCH-02-A` not started. |
| 2026-09-23 | **C2 CLOSED** Sheet Picker layering `751ce10`: shared picker z-index 13000→20120 (above host 20055, below leave-close 20150). Production pointer smoke PASS (Annual/Past Sales `elementFromPoint` hits picker; MEP/PL/3-lang/fallback/BT gate; Demo data unchanged). Human Smoke NONE. Return BR-LAUNCH-01-C. Do not start `BR-LAUNCH-02-A`. |
| 2026-09-23 | **Post-C2 parent path audit** C remains ACTIVE. Remaining Launch-required child = `BR-LAUNCH-01-C1` (P0, dataset contract PARTIAL). C0/C2 CLOSED. `BR-LAUNCH-02-A` still REGISTER ONLY. Do not close C. |
| 2026-09-23 | **BR-LAUNCH-01-C1 audit** restaurant-v1 fixture PASS (integrity+seasonality+YoY). generated-fixtures classified as test/smoke, distinct SHA. Production Demo Pro GET MATCH persistable totals; lunch validation-only; no C2L4 contamination (those labels live on Retail Smoke). Demo Basic empty BT-unset. C1 remains ACTIVE. No reset/reseed/import. `BR-LAUNCH-02-A` not started. |
| 2026-09-23 | **C1 CLOSED** Track `fixtures/demo/restaurant-v1` in git. Demo Basic sales-only seed via production Annual import persist path (BT restaurant, plan basic, 2024–2026 sales/BD match, expenses absent). Demo Pro revision 54 unchanged. MEP/PL → change_plan. **C CLOSED** (C0/C1/C2). Return `BR-LAUNCH-01`. Do not start `BR-LAUNCH-02-A`. |
| 2026-09-23 | **BR-LAUNCH-01 CLOSED** Post-C parent audit: direct children A/B/C all CLOSED; remaining 01-lineage = POST-LAUNCH/DEFERRED only (L6-A, Horizontal/Mixed/date/Preview, Expense Ledger, tooltips). No Launch blocker. Return `TRUNK-06`. Do not start `BR-LAUNCH-02-A`. |
| 2026-09-23 | **TRUNK-06 next-child audit** 01 CLOSED. Direct remaining: 02/03/04 PAUSED P1, 05 DEFERRED. Next Launch phase = `BR-LAUNCH-02` (numeric order; gate until 01 now clear). `BR-LAUNCH-03` / `BR-LAUNCH-04` stay PAUSED. `BR-LAUNCH-02-A` REGISTER ONLY, not started. POST-LAUNCH items not blockers. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-02`. |
| 2026-09-23 | **BR-LAUNCH-02 parent audit** Purpose = Production Smoke + Operational Runbook. Direct child only `02-A` (REGISTER ONLY). Production evidence PARTIAL (01/C2 feature smokes, not Launch-wide). Runbook PARTIAL (FileZilla/deploy, Demo pack, free-trial ops, blob backup, C2-C stale_account; no single Launch ops contract for rollback/error/OCC restore). Registered `BR-LAUNCH-02-B` ACTIVE. Do not start `02-A`. Do not close 02. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-02 -> BR-LAUNCH-02-B`. |
| 2026-09-24 | **BR-LAUNCH-02-B CLOSED** Launch ops inventory + contract [`docs/launch-operational-runbook.md`](./launch-operational-runbook.md). Demo/Account COMPLETE enough. Deploy/Backup/OCC/stale PARTIAL. Data restore API MISSING (Launch = no data rollback). Implementation Needed NO. Return `BR-LAUNCH-02`. `02-A` REGISTER ONLY (gate clear; do not auto-start). Do not close 02. |
| 2026-09-24 | **BR-LAUNCH-02-A CLOSED** Production Launch regression automated PASS. Demo Pro revision 54 unchanged; Basic sales/BT match; no C2L4 on Demo. Entitlement / picker `elementFromPoint` z=20120 / 3-lang / stale_account 403 / registration_disabled / Template fallback PASS. Founder/empty-state login SKIP (ops password absent). Human Smoke NONE. Rollback not needed. Return `BR-LAUNCH-02` READY FOR AUDIT. Do not start `BR-LAUNCH-03`. |
| 2026-09-24 | **BR-LAUNCH-02 CLOSED** Parent closeout: 02-A/02-B CLOSED; `close_when` met. Production smoke COMPLETE. Runbook Launch-complete (restore API not required). Founder/empty-state SKIP is not a Launch blocker. Return `TRUNK-06`. Do not start `BR-LAUNCH-03`. |
| 2026-09-24 | **TRUNK-06 next Launch branch audit** 01/02 CLOSED. Remaining Launch-required = `BR-LAUNCH-03`, `BR-LAUNCH-04` (both PAUSED P1). `BR-LAUNCH-05` DEFERRED. Next phase = `BR-LAUNCH-03` by numeric order. Not started. CURRENT PATH stays `TRUNK-06`. Do not start 03/04/05. |
| 2026-09-24 | **BR-LAUNCH-03 START / Phase 1 inventory COMPLETE** Production Playwright 56 probes + screenshots. P0=0. P1=10 (1200 header clip, JA/ZH mixed EN chrome, MEP overlap, Basic Monthly LOCKED). P2=10. Human visual review YES. Fix size MEDIUM. [`docs/ui-consistency-audit-03.md`](./ui-consistency-audit-03.md). No CSS/code/copy. excel untouched. Do not start `BR-LAUNCH-04`. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-03`. |
| 2026-09-24 | **BR-LAUNCH-03 Phase 2 repair plan COMPLETE** 10 P1 → 4 roots R1 header / R2 i18n (JA+ZH-TW combined) / R3 Basic layout / R4 MEP overlap. Button tokens + KPI Pilot stay P2 (titles may piggyback R2). Order R1→R2→R3→R4. Human blocks 4. First repair `BR-LAUNCH-03-A` REGISTER ONLY. [`docs/ui-consistency-repair-plan-03.md`](./ui-consistency-repair-plan-03.md). No CSS/code/copy. Do not start 03-A/04. |
| 2026-09-24 | **BR-LAUNCH-03-A START** R1 header 1200. `Office` moved from `#btn-mode-text::after` hang to in-flow `.btn-mode::after`. Inject smoke 48/48 PASS. Do not start R2 / `BR-LAUNCH-04`. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-03 -> BR-LAUNCH-03-A`. |
| 2026-09-24 | **BR-LAUNCH-03-A CLOSED** R1 production smoke 48/48 PASS. 1200/1201/1280/1440 × JA/EN/ZH-TW × Annual/Monthly/MEP/PL. overflowX=0. Mode Office in-flow. SHA `7d3fe9e` / `989681c`. Human Review NO. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-03-B`. Do not start `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-E REGISTER ONLY** Responsive Eligibility Gate / Unsupported Viewport Guidance. P1 Launch-required. Parent `BR-LAUNCH-03`. Status PAUSED. Desktop-first: smartphone / tablet portrait / too-narrow landscape → guidance page, not broken KPN. Viewport+orientation (not UA). Min-width deferred to implementation audit vs 1200px contract. Do not implement now. Do not start `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-B START** R2 chrome i18n. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-03 -> BR-LAUNCH-03-B`. Do not start `BR-LAUNCH-03-E` / R3 / R4 / `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-B CLOSED** R2 production smoke 17/17 PASS. JA chrome leftovers localized; ZH-TW Focus Bar + weekdays; EN retained. SHA `8f11df5` / `9f12b5f`. Human Review NO. Return `BR-LAUNCH-03`. Next `BR-LAUNCH-03-C` REGISTER ONLY. Do not start `BR-LAUNCH-03-E` / `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-C START** R3 Basic Monthly layout collapse. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-03 -> BR-LAUNCH-03-C`. Do not start `BR-LAUNCH-03-D` / `BR-LAUNCH-03-E` / `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-C CLOSED** R3 production smoke 21/21 PASS. Basic Edit hidden gapRight=0; Pro Edit visible gapRight=908. 1200/1280/1440 × JA/EN/ZH-TW. SHA `61d23a8`. Human Review NO. Return `BR-LAUNCH-03`. Next `BR-LAUNCH-03-D` REGISTER ONLY. Do not start `BR-LAUNCH-03-E` / `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-F REGISTER ONLY** Office Mode Focus Bar Color Consistency. P1 Launch polish. Parent `BR-LAUNCH-03`. Status PAUSED. Observed Monthly ZH-TW Office Focus Bar still black. Desired medium-light gray outer / lighter cells / black text / Office borders. Shared-root audit when started; do not ZH-only patch. Do not implement now. |
| 2026-09-24 | **BR-LAUNCH-03-D START** R4 MEP Tutorial / AUTO CALC overlap. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-03 -> BR-LAUNCH-03-D`. Left gutter `--mef-tutorial-slot: 124px` on MEP label column. Do not start `BR-LAUNCH-03-E` / `BR-LAUNCH-03-F` / `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-D CLOSED** R4 production smoke 18/18 PASS. AABB overlapN=0. 1200/1280/1440 × JA/EN/ZH-TW × Sci-Fi/Office. SHA `d54bbe6`. Human Review NO. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-03-E` / `BR-LAUNCH-03-F` / `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-E START** Responsive Eligibility Gate. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-03 -> BR-LAUNCH-03-E`. Audit: KPN lower bound = 1200 CSS px (R1 header contract). CSS `@media (max-width: 1199.98px)` on login-page/profile-page. No UA. Do not start `BR-LAUNCH-03-F` / `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-E CLOSED** Production smoke 37/37 PASS. Min width 1200 CSS px. Phone/tablet portrait + landscape <1200 → guidance; 1200+ and iPad Pro landscape → KPN. SHA `ad1654d`. Human Review NO. Return `BR-LAUNCH-03`. Do not auto-start `BR-LAUNCH-03-F` / `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-F START** Office Mode Focus Bar Color Consistency. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-03 -> BR-LAUNCH-03-F`. Audit: Monthly vfocus is page-local × 3 langs (not ZH-only). Office fill was `#2a2a2a` + chrome `#ffffff`. Annual already gray/`#111`. MEP/PL have no this bar. Do not start `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03-F CLOSED** Production smoke 16/16 PASS. Monthly Office fill `#d2d2d2` / cells `#e8e8e8` / text `#111`. Sci-Fi unchanged. SHA `09b8338`. Human Review NO. Return `BR-LAUNCH-03` READY FOR AUDIT. Do not auto-start `BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-03 CLOSED** Parent closeout: children A–F CLOSED; `close_when` met. R1–R5 + Office Focus Bar production smoke PASS. Remaining P2 U11–U20 deferred. Human Smoke NO. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-04`. |
| 2026-09-24 | **TRUNK-06 next Launch branch audit** 01/02/03 CLOSED. Remaining Launch-required = `BR-LAUNCH-04` (PAUSED P1). `BR-LAUNCH-05` DEFERRED (billing assessment; registration already disabled; not a Launch blocker). Next phase = `BR-LAUNCH-04` by numeric order. Not started. CURRENT PATH stays `TRUNK-06`. Do not start 04/05. Do not reopen 01/02/03. |
| 2026-09-24 | **BR-LAUNCH-04 START / Phase 1 audit COMPLETE** Production Playwright + computedStyle + screenshots. Contract PARTIAL. P0=0. P1=5 (rest fill missing, unused monthly-editable class, no amount hover, Office focus Sci-Fi `#152a32`, Office daily dim lost). P2=3. Human visual YES. Fix size SMALL. [`docs/pl-editable-cell-audit-04.md`](./pl-editable-cell-audit-04.md). No CSS/code. excel untouched. Do not start `BR-LAUNCH-05`. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-04`. |
| 2026-09-24 | **BR-LAUNCH-04 CLOSED** Phase 2 CSS visual contract. Production smoke 7/7 PASS (JA/EN/ZH-TW × Sci-Fi/Office + Basic redirect). Rest/hover/focus distinct; Office focus `#c8c8c8` (no `#152a32`); daily dim restored. nEditable=132 unchanged. P1=0 remaining. P2=3 deferred (empty `—`, label vs amount hover, first-load hydrate). Human Review NO. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |
| 2026-09-24 | **BR-LAUNCH-06 REGISTER + START / Phase 1 audit COMPLETE**. **BR-LAUNCH-07 REGISTER ONLY** (PAUSED). `BR-LAUNCH-05` stays DEFERRED. PL `#pl-excel-download` builds UTF-8 CSV then immediate `revokeObjectURL`; Chrome navigates to blob: → ERR_FILE_NOT_FOUND. CSV bytes PASS (JA 8612). XLSX PK FAIL. Fix SMALL. [`docs/pl-excel-download-audit-06.md`](./pl-excel-download-audit-06.md). No code. excel untouched. Do not start 07 / 05. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-06`. |
| 2026-09-24 | **BR-LAUNCH-06 CLOSED** Phase 2 CSV download repair. Delay `revokeObjectURL` 1000ms; button JP `CSVダウンロード` / EN `Download CSV` / ZH-TW `下載 CSV`. Production smoke 10/10 PASS (3 langs × Sci-Fi/Office + Basic redirect). Filename `PL_2026.csv`. BOM retained. nEditable=132. SHA `0b8a323`. Human Review NO. `BR-POST-XLSX-REPORT` REGISTER ONLY. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-07`. |
| 2026-09-25 | **BR-LAUNCH-07 START / Phase 1 audit COMPLETE**. Production Playwright AABB. Insight overlaps `#header-booking-btn` on JP/EN/ZH-TW × Sci-Fi/Office × Annual/Monthly/MEP/PL/profile × 1200–1440 (geometry locked to inner 1200). Live gap 24/28px not dead 80/50. Actions 295/337 vs pad-right 260. P0=0 P1=1 P2=2. Fix SMALL. [`docs/global-menu-spacing-audit-07.md`](./global-menu-spacing-audit-07.md). No CSS/code. excel untouched. Do not start `BR-LAUNCH-05`. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-07`. |
| 2026-09-25 | **BR-LAUNCH-07 CLOSED** Phase 2 shared header reserve. `--kpi-header-actions-reserve: 368px` (was 260). `--kpi-header-nav-gap: 20px` (was 28; required to fit 1200). Insight–booking gap Sci-Fi 49–56 / Office 12. Production 113/114 PASS; ZH-TW PL missing booking is pre-existing not 07. SHA `bbe3907`. Human Review NO. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |
| 2026-09-25 | **TRUNK-06 closeout audit** 01/02/03/04/06/07 CLOSED. `BR-LAUNCH-05` remains DEFERRED (billing assessment; not a Launch blocker). Post-launch items do not block. 1200 contract still valid. **Cannot close TRUNK-06:** ZH-TW PL `#header-booking-btn` is **ACCIDENTAL** (forked unmarked header; `build_pl_table_page.py` JA+EN only). Registered `BR-LAUNCH-08` REGISTER ONLY. Do not implement. Do not start 05. CURRENT PATH stays `TRUNK-06`. |
| 2026-09-25 | **BR-LAUNCH-08 START** ZH-TW PL Global Menu parity. Shared `pl_header()` in `scripts/pl_chrome.py` → `site_chrome.build_header`. Full ZH-TW PL body not regenerated. Do not start `BR-LAUNCH-05`. CURRENT PATH = `TRUNK-06 -> BR-LAUNCH-08`. |
| 2026-09-25 | **BR-LAUNCH-08 CLOSED** ZH-TW PL `#header-booking-btn` via shared `pl_header()`. Office nav gap `--kpi-header-nav-gap` (page-local 28px removed). Production smoke 25/25 PASS. SHA `369c036`. Human Review NO. Return `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |
| 2026-09-25 | **TRUNK-06 CLOSED** Final Launch closeout. 01/02/03/04/06/07/08 CLOSED. Launch-required P0=0 P1=0. `BR-LAUNCH-05` DEFERRED (registration disabled; billing assessment not blocking). Post-launch / 03 P2 U11–U20 / Simple Mode remain outside Launch. Human Smoke NO. Do not auto-start 05 or post-launch. CURRENT PATH = (none). |

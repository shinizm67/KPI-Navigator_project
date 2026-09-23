# KPN Development Path?Task Tree?

**??:** ?? / ?? / ??? / ?????????????????????????????  
**????:** Case / Cursor / Codex / Shin  
**???:** 2026-09-20  
**?????:** ?????????????????????????????CLOSED node ???????

---

## CURRENT PATH

```
CURRENT PATH:
TRUNK-06 -> BR-LAUNCH-01 -> BR-LAUNCH-01-C -> BR-LAUNCH-01-C2 -> BR-LAUNCH-01-C2-L -> BR-LAUNCH-01-C2-L6 -> BR-LAUNCH-01-C2-L6-B

PRIOR TRUNK (CLOSED):
Unit 5B -> Unit 5C -> Floating Window Functional Audit
-> Planning Readiness -> Automatic Seasonality / Baseline
-> UI/UX branches closeout

ACTIVE BRANCHES:
- BR-LAUNCH-01 (Demo / New User State) P0
- BR-LAUNCH-01-C (Demo Seed / Demo Reset) P0
- BR-LAUNCH-01-C1 (Demo Dataset Contract & Existing Fixture Audit) P0
- BR-LAUNCH-01-C2 (Demo Operation Pack) P0
- BR-LAUNCH-01-C2-L (Flexible CSV / Excel Import Foundation) P0
- BR-LAUNCH-01-C2-L6 (Flexible Translator Expansion) P1
- BR-LAUNCH-01-C2-L6-B (Excel Sheet Picker — Launch) P1
- BR-LAUNCH-01-C2-C (Cross-Tab Account Session Collision) P0

REGISTERED (C2-L children; spec only; do not start):
- BR-LAUNCH-01-C2-L6-A Multi-sheet Import Profile (POST-LAUNCH / DEFERRED P2)
- BR-POST-EXPENSE-LEDGER Purchase / Expense Ledger (DEFERRED P2)

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

PAUSED (under TRUNK-06):
- BR-LAUNCH-02 Production Smoke / Operational Runbook P1
- BR-LAUNCH-03 UI Consistency Audit P1
- BR-LAUNCH-04 PL Editable Cell Visual Finish P1

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
- BR-POST-EXPENSE-LEDGER Purchase / Expense Ledger P2 DEFERRED
  parent: BR-LAUNCH-01-C2. REGISTER ONLY. Not an Excel clone.

RETURN TARGET:
BR-LAUNCH-01-C2 ? BR-LAUNCH-01-C ? BR-LAUNCH-01 ? TRUNK-06

NEXT ACTION:
C2-L6-B Excel Sheet Picker + Template fallback ACTIVE. Do not start Horizontal/Mixed/L6-A.
```

### Git snapshot????????

| ?? | ? |
|------|-----|
| git branch | `wip/unit5b-pl-mep-preset-engine-20260916` |
| HEAD | `80ae48c` (C2-L5-B first-load fail-closed docs) |
| origin sync | in sync with origin before this checkpoint |
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


### BR-LAUNCH-01-C2-L

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L |
| name | Flexible CSV / Excel Import Foundation |
| parent | BR-LAUNCH-01-C2 |
| status | ACTIVE |
| priority | P0 |
| started_at | 2026-09-21 |
| return_to | BR-LAUNCH-01-C2 |
| reason | User CSV/Excel should translate into KPN form; only untranslatable cases guide to KPN Template |
| principle | KPN does not require KPN-form CSV. Translate user CSV/Excel into KPN form as far as possible. Keep untranslated data for later user meaning/classification. Guide to KPN Template only when still uninterpretable. |
| children | L1 CLOSED; L1-A CLOSED; L2 CLOSED; L3 CLOSED; L4 CLOSED; L5 CLOSED; L5-A CLOSED; L5-B CLOSED; L6 ACTIVE; L6-A DEFERRED; L6-B ACTIVE |
| next_action | C2-L6-B Sheet Picker ACTIVE. Horizontal/Mixed/L6-A remain POST-LAUNCH |
| constraint | no excel/ touch; no Demo Reset; no unilateral UX; BT unset Option B preserved; L6 spec only; tooltips DEFERRED |

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
| C2-L6 | Flexible Translator Expansion | ACTIVE | Launch subset: Sheet Picker + Template fallback |
| C2-L6-B | Excel Sheet Picker — Launch | ACTIVE | multi-sheet pick one; single-sheet no modal |
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
| status | ACTIVE |
| priority | P1 |
| started_at | 2026-09-23 |
| return_to | BR-LAUNCH-01-C2-L |
| phase | Launch subset implement (Sheet Picker + Template fallback) |
| reason | SMALL launch subset: picker + template fallback only. |
| next_action | C2-L6-B ACTIVE. Do not start Horizontal/Mixed/Purpose Mapping/L6-A. |
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

### BR-LAUNCH-01-C2-L6-B

| Field | Value |
|-------|-------|
| id | BR-LAUNCH-01-C2-L6-B |
| name | Excel Sheet Picker — Launch |
| parent | BR-LAUNCH-01-C2-L6 |
| status | ACTIVE |
| priority | P1 |
| started_at | 2026-09-23 |
| return_to | BR-LAUNCH-01-C2-L6 |
| reason | Multi-sheet Excel: user picks one sheet. Single-sheet: no picker. Cached values only. Template fallback on unreadable. Purpose from existing import entry. |
| next_action | Implement + automated smoke. Do not add Horizontal/Mixed/Import Profile. |
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
| `BR-LAUNCH-01-C` | Demo Seed / Demo Reset | ACTIVE | P0 | `BR-LAUNCH-01` |
| `BR-LAUNCH-01-C1` | Demo Dataset Contract & Existing Fixture Audit | ACTIVE | P0 | `BR-LAUNCH-01-C` |
| `BR-LAUNCH-01-C2` | Demo Operation Pack | ACTIVE | P0 | `BR-LAUNCH-01-C` |
| `BR-LAUNCH-01-C2-L` | Flexible CSV / Excel Import Foundation | ACTIVE | P0 | `BR-LAUNCH-01-C2` |
| `BR-LAUNCH-01-C2-L5` | Plan-independent Expense Storage + Basic / Pro Visibility | CLOSED | P1 | `BR-LAUNCH-01-C2-L` |
| `BR-LAUNCH-01-C2-L5-A` | Plan-independent Expense Storage / Upgrade Safety | CLOSED | P1 | `BR-LAUNCH-01-C2-L5` |
| `BR-LAUNCH-01-C2-L5-B` | Basic / Pro Expense UI Entitlement | CLOSED | P1 | `BR-LAUNCH-01-C2-L5` |
| `BR-LAUNCH-01-C2-L6` | Flexible Translator Expansion | ACTIVE | P1 | `BR-LAUNCH-01-C2-L` |
| `BR-LAUNCH-01-C2-L6-B` | Excel Sheet Picker — Launch | ACTIVE | P1 | `BR-LAUNCH-01-C2-L6` |
| `BR-LAUNCH-01-C2-L6-A` | Multi-sheet Import Profile | POST-LAUNCH / DEFERRED | P2 | `BR-LAUNCH-01-C2-L6` |
| `BR-POST-EXPENSE-LEDGER` | Purchase / Expense Ledger | DEFERRED | P2 | `BR-LAUNCH-01-C2` |

CLOSED under `BR-LAUNCH-01`: `BR-LAUNCH-01-A`, `BR-LAUNCH-01-B`  
CLOSED under `BR-LAUNCH-01-C`: `BR-LAUNCH-01-C0`, `BR-LAUNCH-01-C2-K`  
CLOSED under `BR-LAUNCH-01-C2-L`: `BR-LAUNCH-01-C2-L1`, `BR-LAUNCH-01-C2-L2`, `BR-LAUNCH-01-C2-L3`, `BR-LAUNCH-01-C2-L4`, `BR-LAUNCH-01-C2-L5`  
CLOSED under `BR-LAUNCH-01-C2-L5`: `BR-LAUNCH-01-C2-L5-A`, `BR-LAUNCH-01-C2-L5-B`  
CLOSED under `BR-LAUNCH-01-C2-L3`: `BR-LAUNCH-01-C2-L3-A`, `BR-LAUNCH-01-C2-L3-B`  
CLOSED under `BR-LAUNCH-01-C2-L1`: `BR-LAUNCH-01-C2-L1-A`  
PAUSED under `TRUNK-06`: `BR-LAUNCH-02`, `BR-LAUNCH-03`, `BR-LAUNCH-04`  
DEFERRED under `TRUNK-06`: `BR-LAUNCH-05`  
DEFERRED UX: `BR-UI-PL-EXPENSE-CLASSIFY-TOOLTIPS` (parent `BR-LAUNCH-01-C2`, P2), `BR-UI-PL-INSIGHT-FIRSTOPEN-PERF`  
DEFERRED importer: `BR-LAUNCH-01-C2-L6-A` (parent L6), `BR-POST-EXPENSE-LEDGER` (parent C2)

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

# KPN Development Path?Task Tree?

**??:** ?? / ?? / ??? / ?????????????????????????????  
**????:** Case / Cursor / Codex / Shin  
**???:** 2026-09-20  
**?????:** ?????????????????????????????CLOSED node ???????

---

## CURRENT PATH

```
CURRENT PATH:
BR-LAUNCH-05 (Registration -> Initial Setup Integration) P1
Phase 0 audit + Freeze 2026-09-28
Phase 1 CLOSED 2026-09-28 — Registration UI simplification (`6994e30` deployed; Shin approved)
Phase 2 CLOSED 2026-09-28 — consent record / registration-status GET / abuse protection / cache-bust (`5a3267e` + `e9e8cc2` deployed; Shin approved)
Phase 3 ACTIVE 2026-09-28 — production readiness; ConoHa: trusted real IP not obtainable → IP-independent abuse protection deployed + production verified 2026-09-29 (`09f4711`); consent table applied + verified; Controlled Registration Smoke PASS 2026-09-29 → READY approved → **PUBLIC REGISTRATION ENABLED / PRODUCTION VERIFIED 2026-09-29** (Shin GO; registrationEnabled true)

BR-LAUNCH-09 (Account Security & Destructive Actions) P0
Phase 0 CLOSED 2026-09-28 — audit (fake Delete / Password / Email flows; allowSelfPlanChange false in production)
Phase 1 CLOSED 2026-09-28 — Password Change server-side (`067c51e` deployed + verified; Shin approved; Launch blocker resolved)
Phase 2 CLOSED 2026-09-28 — Email Change server-side (`54c37d5` deployed; production Human Smoke PASS)
Phase 3 ACTIVE 2026-09-28 — Delete Account; consent retention decided (delete with account, existing CASCADE); implemented, waiting for Delete Account Human Smoke

PREVIOUS PATH (IMPLEMENTED / PRODUCTION VERIFIED):
BR-ONBOARDING-01 (KPN Initial Setup & Readiness) P0
Phase 0 CLOSED 2026-09-27
Phase 1 CLOSED 2026-09-27 — Navigation Readiness + Safe Guard (Human Smoke PASS)
Phase 2 CLOSED 2026-09-27 — Business Profile / Step 01 (production verified on account 00; Launch UI approved)
Phase 3 CLOSED 2026-09-27 — STEP 02 Historical Data (production verified on account 00; Shin approved)
Phase 4 CLOSED 2026-09-27 — STEP 03 Current Year (production verified on account 00; Shin approved)
Phase 5 CLOSED 2026-09-27 — STEP 04 Annual Target (production verified on account 00; Shin approved)
Phase 6 CLOSED 2026-09-27 — STEP 05 Review / Setup Complete (production verified on account 00; close conditions met)
Initial Setup: IMPLEMENTED / PRODUCTION VERIFIED

PRIOR TRUNK (CLOSED):
Unit 5B -> Unit 5C -> Floating Window Functional Audit
-> Planning Readiness -> Automatic Seasonality / Baseline
-> UI/UX branches closeout
-> TRUNK-06 (Launch / Demo / New-user Readiness)

CLOSED (post-launch polish; do not reopen TRUNK-06):
- BR-POST-BOOKING-ICON-COLOR (Office booking icon #fff) P2 closed 2026-09-25
- BR-POST-FOOTER-VERSION (footer Version 1.0.0 / © 2025) P2 closed 2026-09-26
- BR-POST-COCKPIT-GAP (Annual Target / Business Day gap parity) P2 closed 2026-09-26

POST-LAUNCH (not the active path):
- BR-POST-HOME-01 (KPN Home / Simple Mode) P1
  PRODUCTION VERIFIED / CLOSED (2026-10-01)
  revision 3c8ec2598843bd07d524ac1642094007893ba2a3
  CURRENT PATH above is unchanged. Home is not the active path.
- BR-POST-HOME-02 (Home / Simple Mode Redesign) P1
  PRODUCTION VERIFIED / CLOSED (2026-10-03)
  revision 305924ee4afdcf6f62d52669a654f86bdd567ad3
  CURRENT PATH above is unchanged. Home is not the active path.

REGISTERED (infrastructure; CURRENT PATH unchanged):
- BR-LOCAL-VERIFY-01 (Full Local Verification Environment) CRITICAL / HIGH
  Pre-launch foundation and post-launch continuous infrastructure. Not a one-shot ticket.
  Phase 0 audit recorded 2026-10-03. Phase 1 LOCAL VERIFIED / CLOSED 2026-10-04.
  Phase 2 Canonical Fixtures v1 is IMPLEMENTED / LOCAL VERIFIED / CLOSED (2026-10-04).
  Phase 3 Local MySQL Parity is REAL MYSQL VERIFIED / CLOSED (2026-10-04). Phase 4 Full Page Smoke is LOCAL MYSQL VERIFIED / CLOSED (2026-10-04): user-facing 122 / 122 (executed 123, supplemental 1) and Admin 5 / 5. Parent CLOSED (2026-10-04).
- BR-I18N-ARCH-01 (Localization Architecture v2) HIGH
  Depends on a BR-LOCAL-VERIFY-01 baseline. Do not add Spanish as a fourth HTML tree.
  Stripe may proceed in parallel. Implementation NOT STARTED.

ACTIVE BRANCHES:
- BR-LAUNCH-09 Account Security & Destructive Actions P0 (Phase 0 / 1 / 2 CLOSED; Phase 3A Basic Account Delete IMPLEMENTED — READY FOR HUMAN SMOKE; Phase 3B Paid / Stripe Account Delete BLOCKED — Stripe / Billing contract required)
- BR-LAUNCH-05 Registration -> Initial Setup Integration P1 (Phase 1 / 2 CLOSED 2026-09-28; PUBLIC REGISTRATION ENABLED / PRODUCTION VERIFIED 2026-09-29)
- BR-ONBOARDING-01 (outside TRUNK-06; do not reopen TRUNK-06)
- (BR-ONBOARDING-01-R2 CLOSED 2026-09-27 — fixed, deployed, production verified)

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
- BR-POST-SETUP-RULER-ANIM Initial Setup Step Ruler Progress Animation P3 POST-LAUNCH / MINOR UX POLISH
  parent: BR-ONBOARDING-01. REGISTER ONLY. Not a Launch blocker; unannounced post-launch polish.
- BR-POST-D6-MINOR d6dced6 minor leftovers outside the R2 audit P3 POST-LAUNCH / SEPARATE TASK
  parent: BR-ONBOARDING-01-R2. REGISTER ONLY. No data loss. See R2 node `residual_notes`.
- BR-POST-SETUP-EXTRA-PUT One extra store PUT during Initial Setup P2 INVESTIGATE / NOT A LAUNCH BLOCKER
  parent: BR-ONBOARDING-01. REGISTER ONLY. Do not fix inside onboarding phases.
- BR-LAUNCH-05-EMAIL-VERIFY Registration email verification POST-LAUNCH / REGISTER ONLY
  parent: BR-LAUNCH-05. Not in Launch-required scope (public registration went live 2026-09-29 without it). Reconsider before paid Pro / billing.
- BR-LAUNCH-05-REG-SESSION register.php sets a session but the UI sends the user to Login P2 REGISTER ONLY
  parent: BR-LAUNCH-05. Behavior unchanged. Cleanup options (stop session on register, or go straight in) decided later.
- BR-POST-PROGRESS-SCALE-01 Dynamic Progress Bar Scale POST-LAUNCH / REDESIGN
  parent: post-launch. REGISTER ONLY. Do not change the current Sales Progress contract. See [`docs/br-post-progress-scale-01.md`](./br-post-progress-scale-01.md).
- BR-POST-PACE-ALERT-01 Business-day vs Sales Pace Alert Visual Contract POST-LAUNCH / REDESIGN
  parent: post-launch. REGISTER ONLY. Do not change the current Home pace warning. See [`docs/br-post-pace-alert-01.md`](./br-post-pace-alert-01.md).
- BR-POST-HOME-02 Home / Simple Mode Redesign P1 PRODUCTION VERIFIED / CLOSED
  parent: post-launch. Do not reopen `BR-POST-HOME-01`. Production commit `305924ee4afdcf6f62d52669a654f86bdd567ad3`. See [`docs/br-post-home-02.md`](./br-post-home-02.md).

RETURN TARGET:
N/A (TRUNK-06 CLOSED)

NEXT ACTION:
BR-LAUNCH-09: Phase 3A (Basic Account Delete) READY FOR HUMAN SMOKE (`funkizm@mac.com` only, Shin GO required before any production deletion). Phase 3B (Paid / Stripe Account Delete) BLOCKED — Stripe / Billing contract required. Phase 3 Final Close only after 3A + 3B both pass. Phase 4 only after Shin GO.
BR-LAUNCH-05 **PUBLIC REGISTRATION ENABLED / PRODUCTION VERIFIED 2026-09-29** (Shin GO). IP-independent abuse protection (`09f4711`: forwarded-header reject, global limiter, email limiter, IP auxiliary), consent record, Basic fixed, Pro Coming Soon. Controlled smoke test account `shinizm+kpnreg@gmail.com` kept and excluded from Founder metrics (Shin decides later). `registrationEnabled` is changed only on Shin's explicit instruction. Post-launch: `BR-LAUNCH-05-EMAIL-VERIFY` (reconsider before paid Pro), `BR-LAUNCH-05-REG-SESSION` (P2). Initial Setup (BR-ONBOARDING-01) stays IMPLEMENTED / PRODUCTION VERIFIED. Do not reopen `TRUNK-06`.
`BR-LOCAL-VERIFY-01` is CLOSED (2026-10-04). Phase 1 and Phase 2 are LOCAL VERIFIED / CLOSED. Phase 3 is REAL MYSQL VERIFIED / CLOSED. Phase 4 is LOCAL MYSQL VERIFIED / CLOSED: user-facing 122 / 122 (executed 123, supplemental 1) and Admin 5 / 5. `BR-I18N-ARCH-01` is not started. Stripe stays a separate track. CURRENT PATH unchanged.

COORDINATION SNAPSHOT 2026-10-08 (does not close older nodes):
Standing rule: BR-AUDIT-FIRST — Audit Before Implementation. See Operating Rule. This is not a product task and does not start implementation.
Stripe track: STRIPE-LIVE-07 RUNBOOK READY. Live work blocked by Stripe approval / Live access.
Profile track: PROFILE-PERSISTENCE-01 AUDIT COMPLETE. PROFILE-PERSISTENCE-02 COMMITTED AND PUSHED (`5b265a0`). PROFILE-PERSISTENCE-03 production smoke failed on fresh-browser direct Profile save and is superseded. PROFILE-PERSISTENCE-04 VERIFIED IN PRODUCTION / COMPLETE (`0edce9ea51ce90616f00748995f007679154ff10`).
Tutorial track: TUTORIAL-FA-01 IN PREPARATION. Profile / Initial Setup recording is UNBLOCKED. Other tutorial production may continue.
Next Windows mainline: continue from the current canonical development path. Do not start a new product implementation in this docs registration.
Windows remains the canonical development workstation. Mac is Tutorial Production / Read-Only Inspection only.

BASELINE UX CONVENTION (not a work branch):
- Unfinished / coming-soon full pages → Construction State
  (`docs/kpn-construction-state.md`)
```

### Git snapshot

| field | value |
|------|-----|
| git branch | `wip/unit5b-pl-mep-preset-engine-20260916` |
| HEAD | `0edce9ea51ce90616f00748995f007679154ff10` (2026-10-08 profile store sync on direct entry) |
| origin sync | even with `origin/wip/unit5b-pl-mep-preset-engine-20260916` (0/0). Do not force push. |
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

### Workstation policy (2026-10-07)

Windows is the canonical development workstation: implementation, Cursor code changes, Codex work, tests, commit, push, deploy, and Stripe production work. Case coordinates task order and GO / NO-GO. Shin performs final approvals, Stripe Dashboard operations, tutorial recording, and controlled production actions.

Mac is a Tutorial Production / Read-Only Inspection workstation. It uses the same GitHub repository at a known canonical commit, preferably detached HEAD or another protected read-only state, and it does not keep an independent development branch. Mac Cursor may inspect code, explain behavior, search source, compare Cloud behavior against that commit, and prepare scripts, captions, shot lists, demo data, and tutorial production. Mac Cursor must not edit KPN production source, commit, push, create feature branches, merge, rebase, deploy, or modify production configuration. If Mac finds a KPN code issue, stop and report it to Case and the Windows canonical workflow.

### BR-AUDIT-FIRST — Audit Before Implementation (2026-10-08)

Standing development rule. Not a product feature and not an implementation task.

Any task that touches an existing feature, existing data, existing API, persistence path, account state, billing state, or cross-device behavior must begin with a short current-state audit before implementation. The audit is proportional to the task. Do not turn every task into a large forensic investigation.

Before modifying an existing system, inspect only the items that are relevant:

1. Current canonical source of truth
2. Current read path
3. Current write / persistence path
4. Existing duplicate or derived state
5. Dependencies and downstream consumers
6. Failure-path behavior
7. Cross-device / cross-browser behavior where relevant
8. Existing automated tests / regression coverage
9. JP / EN / ZH-TW parity where UI is involved
10. Current Git baseline and unrelated dirty files

If the audit discovers another problem outside the current task, do not automatically expand scope. Document the finding, classify severity and relevance, register it as a Task Tree branch or follow-up candidate, preserve the evidence and the exact code path, and return to the current task unless the discovered issue blocks safe progress. If it is a true blocker, stop and elevate it before implementation.

Before adding new storage or state, search for existing canonical storage. Avoid a duplicate source of truth. Distinguish canonical state from cache, derived state, and UI state. Do not create a new database table or field merely because the UI lacks a value.

Implementation reviews must verify the relevant failure paths as well as the success path. Examples: server write failure, partial multi-API write, stale browser cache, session or auth failure, webhook failure, invalid imported data, missing configuration, and test / live environment mismatch.

After implementation, run focused automated tests and the relevant regression tests. Define a minimal human smoke only where automation cannot prove the behavior. Do not require Shin to repeat broad manual testing when automated evidence is sufficient.

Preferred flow: task, focused audit, implementation, automated verification, smoke if required, commit / push, then continue the main Task Tree. A side issue is registered as a branch and deferred unless it blocks safe progress.

### UX / UI convention: unfinished pages (baseline)

Default for a **new full page** whose feature or content is not ready: Forge Lab / KPN **Construction State** (scramble / rotating placeholder).

- Do **not** ship a plain empty page or raw static placeholder text unless there is a **documented exception**.
- Main rotating phrases stay English on all locales: `COMING SOON` / `UNDER CONSTRUCTION` / `WORK IN PROGRESS`.
- Localized subtitle is **required** (JP / EN / ZH-TW).
- Sci-Fi: branded scramble. Office: calm freeze on `COMING SOON`.
- Future unfinished pages: use this pattern unless an exception is written down.
- Durable spec: [`docs/kpn-construction-state.md`](./kpn-construction-state.md)
- Reuse: `js/kpi-construction-state.js` + `.kpn-construction-state`

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
| audit_2026-09-28 | Phase 0 Contract Audit (Registration -> Initial Setup integration; audit only, status unchanged, nothing implemented). HEAD confirms: `registrationEnabled` false (config.example / bootstrap default); `register.php` takes email + password only, 409 `email_taken`, 8-char server minimum, plan = `defaultPlan`, creates the account and a session; never writes profile / store. Registration pages JP / EN / ZH-TW (production GET): static disabled notice, form hidden, Plan pages point to Early Access mailto only (no link to Registration). Form still asks name, company, Business Type (duplicates STEP 01; name / company never sent; Business Type goes only to browser localStorage store meta after success). Plan from `?plan=` is display-only and never sent. Terms / Privacy checkbox is client-only; no consent record in API or `kpi_users`. Success -> alert -> Login -> Annual -> existing Readiness -> Step 01. Proposed: light Registration (email, password, confirm, consent), Initial Setup STEP 01 owns Business Profile, reuse Login -> Annual -> Readiness (no new setup route), consent record needs a schema decision. Waiting for Shin decision before Phase 1. |
| phase0_freeze_2026-09-28 | Shin froze: (1) legal consent is Launch-required; the server must record Terms version, Privacy version, accepted_at (storage option A columns on `kpi_users` / B dedicated table decided in Phase 2; no schema change in Phase 1). (2) Public registration is `basic` fixed until Billing; no plan is sent from Registration; `?plan=pro` never grants anything; Pro stays Coming Soon; admin-create plan contract unchanged. (3) Abuse protection is Launch-required: server rate limit, keep duplicate-email 409, basic bot mitigation, generic safe errors; no CAPTCHA / heavy UX; email verification is a separate task (re-evaluate before paid Pro / billing). (4) Server `registrationEnabled` is the single source; the UI must read it (false: notice + hidden form, true: form) so reopening needs no HTML redeploy. (5) Registration = Email / Password / Confirmation / Terms + Privacy consent; STEP 01 = the 7 fields (City, Genre optional); Name, Company, Business Type and the local Business Type write are removed from Registration. |
| phase1_2026-09-28 | Registration UI simplification, JP / EN / ZH-TW, Sci-Fi / Office. Removed Name, Company / Business Name, Business Type (and `kpi-business-type.js`) from the 3 pages; removed the `setBusinessType` localStorage write after success; plan block fixed to Basic (`?plan=` ignored, not stored, not sent); button needs email + password rule + match + consent; payload stays `{email, password}`. Success -> alert -> same-language Login -> Annual -> existing Readiness -> STEP 01 (no auto-login). Static disabled notice / hidden form / emergency gate unchanged. Not touched: `register.php`, DB, Login, Readiness, Initial Setup, profile / store APIs, admin-create, Billing. Commit `6994e30` pushed; deployed 6 files (production matched base `5072b38` before upload; HTTP SHA match after). Smoke 83/83 local and 83/83 on production assets; emergency gate 40/40; business type foundation 140/140; Step 0 329/329; Phase 6 225/225. P0 = 0, P1 = 0. Note: register `script.js` is served with `max-age=604800` and no version query; reopening registration (Phase 2) must make sure browsers get the new script. |
| parent | `TRUNK-06` |
| phase2_2026-09-28 | Server launch requirements. (A) Consent: dedicated append-only table `kpi_user_consents` (id, user_id, terms_version, privacy_version, accepted_at, source; no IP / UA) in `schema.sql` + `schema_kpi_user_consents.add.sql`; canonical `KPI_TERMS_VERSION` / `KPI_PRIVACY_VERSION` = `2026-02-16` in `api/v1/_registration.php` (all 6 legal pages dated 2026-02-16; test enforces equality); MySQL: user INSERT + consent INSERT in one transaction, rollback on failure; file mode: `register.lock` + compensating unlink; payload `{email, password, consentAccepted, termsVersion, privacyVersion, formToken, extraNote}`, server validates all (`consent_required` / `consent_outdated`). (B) `api/v1/auth/registration-status.php` public GET, no session, `no-store`, `{registrationEnabled, termsVersion, privacyVersion}` + `formToken` only when enabled; UI hidden by default, form shown only on 200 + `registrationEnabled === true` + token; any failure stays closed; `register.php` 403 kept. (C) Rate limit IP 10 / 10 min, email 5 / h (file sliding window, no new infra; storage unavailable -> 503), honeypot `extra_note` (off-screen, `aria-hidden`, `tabindex=-1`, `autocomplete=off`), signed form token with min 2 s / max 24 h, generic `registration_rejected`, 409 `email_taken` kept, no CAPTCHA. Password rule (8+, letter, digit, symbol) applied on public registration only; Login / admin unchanged. Plan hard-coded `basic` (`defaultPlan` no longer used by register). (D) `?v=<sha256[:12]>` on `kpi-auth-client.js` and register `script.js` for JP / EN / ZH-TW via `scripts/stamp_registration_assets.py` (`--check`). ZH-TW register is generated by `build_zh_tw_public_pages.py` `build_register` (now strict, zh strings for notice, `errorMessage('zh')`, site chrome + stamp); full regeneration leaves register pages unchanged. Tests: launch contract 60/60, emergency gate 40/40, server smoke (PHP + MariaDB) 73/73, UI smoke 128/128; regressions Step 0 329/329, Phase 6 225/225, business type 140/140, password reset 106/106. Deployed 10 files (production matched `5a3267e~1` before upload; FTP + HTTP SHA match after); production GET probe 30/30 (status false, no token, no-store, fresh `?v=` assets, legal pages match repo, Login 200). No production DB change; `kpi_user_consents` not yet applied (registration fails closed with rollback if missing). |
| phase3_2026-09-28 | Production readiness (registration stays off). Consent SQL re-audited: one `CREATE TABLE IF NOT EXISTS kpi_user_consents`, no DROP / ALTER / DELETE / UPDATE / INSERT, only an FK reference to `kpi_users` (contract test enforces). Production (read-only temp diagnostic, removed after use): MySQL 8.4.8, `kpi_users` InnoDB utf8mb4_unicode_ci (FK compatible), `kpi_user_consents` absent (not applied yet), `api/v1/data` writable with `.htaccess` deny, flock exclusive works. Client IP audit: front proxy (internal 172.19.48.x) overwrites client `X-Forwarded-For`, LiteSpeed derives REMOTE_ADDR from it (= real IP), but a client-sent `CF-Connecting-IP` or `X-Real-IP` replaces REMOTE_ADDR (spoofable); ConoHa WING / LiteSpeed publish no trusted-header contract for this -> BLOCKED until Shin decides a fix. zh-tw registration success message translated and duplicate `urlZhTw` removed via `build_zh_tw_public_pages.py` (only 2 zh-tw register files regenerated); `4bca49d` deployed. Production: status false, no token, direct POST 403, `?v=` assets fresh (JP / EN / ZH-TW), Plan pages unchanged. Server smoke 86/86 (adds spoofed-header, concurrent counter, expiry, storage-failure, `?plan=pro` URL checks), UI 128/128 (production status), contract 69/69; regressions green. Shin decision on client IP: ask ConoHa support first, no code change. Plan CTA (Shin approved): `js/kpi-plan-cta.js` switches the Basic button to the same-language Registration only on the same open condition as the Registration page (true + versions + formToken); default / failure keeps Early Access mailto; Pro Coming Soon unchanged; `?v=` stamped; zh-tw via `build_plan` reps; `0e6ee18` deployed (4 files), Plan smoke 103/103 local, 102/102 on production (Early Access shown). |
| conoha_answer_2026-09-29 | **ConoHa WING official answer (fact): trusted real client IP is not obtainable.** No official spec for trusting `CF-Connecting-IP` / `X-Real-IP` or similar headers; client-sent headers can hold any value and should not be treated as the real IP; trusted proxy ranges / LiteSpeed internal settings are not disclosed; no official way to get an unspoofable source IP. Consequence: the design that uses `REMOTE_ADDR` as the only security boundary (the IP limiter is currently the only per-client volume control; the email limiter is per address) is retired. Registration is not blocked permanently: Shin ordered a multi-layer, IP-independent redesign. Kept: normalized email limiter, signed form token, honeypot, minimum submit time, duplicate-email 409, generic errors, `registrationEnabled` fail closed. Candidates: server-global limiter on attempts and account creations (existing protected file storage + flock, storage failure → fail closed); reject requests that carry `CF-Connecting-IP` / `X-Real-IP` (earlier production probe: absent on normal requests, visible in `$_SERVER` when sent); `REMOTE_ADDR` limiter only as an auxiliary signal. Not allowed: adopting any header as trusted, switching to `X-Forwarded-For`, CAPTCHA. Audit done; implementation waits for Shin decisions (limit values, header set, IP limiter kept or not). |
| redesign_2026-09-29 | Shin decided: global limits as proposed, reject only `CF-Connecting-IP` / `X-Real-IP`, keep the IP limiter as auxiliary, production read-only probe allowed. Implemented (local, not deployed): `register.php` order = `registrationEnabled` → forwarded-header reject (400 `registration_rejected`, before any counter) → global attempts 30 / 10 min → IP 10 / 10 min (auxiliary) → honeypot / token → email 5 / h → password → consent → duplicate 409 → global creations 40 / 24 h and 10 / h (only requests that reach creation) → create. Same file counters + flock under `data/registration` (timestamps only); storage failure → 503; full → 429 `rate_limited` (existing UI message). Config overrides `registrationGlobalAttemptMax` / `registrationGlobalAttemptWindowSeconds` / `registrationGlobalCreateHourMax` / `registrationGlobalCreateDayMax` (optional). No UI / schema change. Tests: registration contract 73/73; server smoke 94/98 (all new R1–R6 checks green: header reject in any case, no counter touched, XFF not rejected, global attempt bound with rotating IP buckets, creation slots only on reaching creation, day limit, 12-process concurrency, defaults; the 4 reds are the known harness artifacts from L4); lifecycle 29/29, privacy 46/46, delete 49/49; emergency gate 37/40 (Plan CTA 3 pre-existing). Production probe (key-guarded temp file, removed; names / booleans only): scripted plain GET / POST and real Chrome GET + registration-style POST carry neither header; sent `CF-Connecting-IP` / `X-Real-IP` are detected; `X-Forwarded-For` is not. Residual risk (Shin acceptance needed before enable): no trusted client IP, no email verification (`BR-LAUNCH-05-EMAIL-VERIFY`), form token re-obtainable anonymously, 409 reveals registered emails, a flood can fill the global limit and pause signups (login unaffected). |
| redesign_deploy_2026-09-29 | Shin GO (deploy only; not an enable GO). Deployed `09f4711` `api/v1/_registration.php` + `api/v1/auth/register.php` (production matched `09f4711~1` before upload; FTP SHA match). Production verify 16/16: status false / no token / versions; register POST plain, with `CF-Connecting-IP`, `X-Real-IP`, `X-Forwarded-For`, `?plan=pro` and 12 repeats all 403 `registration_disabled` (gate before every limiter, no 429 / 503), GET 405; key-guarded read-only diag (removed, 0 left): new functions live, header detection on production PHP (plain no / CF yes / X-Real-IP yes / XFF no), limits 30/600, 10/3600, 40/86400, IP 10/600, email 5/3600 with no config overrides, counter dir writable + flock ok, production `register.php` order as designed. Real counters untouched. `registrationEnabled` false. |
| controlled_smoke_2026-09-29 | **Controlled Registration Smoke PASS (Shin GO; not a permanent enable).** Production `registrationEnabled` flipped true for ~18 s (one config value, php -l + byte verify) and back to false. Before: config false, status false / no token, form hidden, POST 403, test email absent (14 users, 0 consents). Real Chrome (JP Sci-Fi): Plan Basic CTA → JP Registration → email / password / confirm / consent → 201 → 「登録が完了しました。ログイン画面へ進みます。」 → Login → Annual → KPN SETUP REQUIRED guard → 初期設定を始める → STEP 01 Business Profile 0 / 7 (not saved). One request each: `CF-Connecting-IP` → 400 `registration_rejected`, `X-Real-IP` → 400 `registration_rejected` (weak password, nothing could be created); duplicate email → 409 `email_taken`. After: status false / no token, form hidden, direct POST 403. Read-only DB: test account `shinizm+kpnreg@gmail.com` exactly 1 (basic / user / enabled / no parent / no children, last_login set), consent exactly 1 (terms 2026-02-16, privacy 2026-09-29, accepted_at, `public_registration`), origin `new`, no store / profile / daily rows / plan history; users 14 → 15, other 14 users unchanged (digest incl. plan / role / disabled / password / parent and updated_at), no new non-basic account, deletion history +0. Smoke 29/30: the one red is a harness artifact (register response body unreadable after the page navigated; status 201 captured, DB basic / user). Password generated into a local owner-only file outside the repo (not printed; 0 repo hits). Test account kept (Shin decides). P2: the config flip to false took a few seconds to show in `registration-status` (likely PHP opcache revalidation); the enable / disable procedure must re-check status and retry. |
| status | PUBLIC REGISTRATION ENABLED / PRODUCTION VERIFIED 2026-09-29 (Phase 1 / 2 CLOSED; Phase 3 controlled smoke PASS; registrationEnabled true) |
| priority | P1 |
| started_at | 2026-09-20 |
| return_to | `TRUNK-06` |
| reason | ?????????? readiness ???Stripe / billing ??????????????????????? assessment ????? |
| evidence | commit `af07bf7` Disable public registration until billing is ready; `free-trial-account-ops.md`?billingType ???? |
| enable_2026-09-29 | **PUBLIC REGISTRATION ENABLED / PRODUCTION VERIFIED** (Shin approved the smoke + READY verdict and gave the enable GO). Before: test account `shinizm+kpnreg@gmail.com` set `exclude_from_metrics = true` (same helper as `admin/set-metrics-exclusion.php`, one-shot key-guarded PHP, removed; only its origin row changed; metrics 2026-09 Active 14 → 13, New 6 → 5, excluded accounts 1). Production `registrationEnabled` written true once; `registration-status` true after 3 s (opcache delay polled). Verify 19/19 (no account created): status true + token + Terms 2026-02-16 / Privacy 2026-09-29 (3 reads); Registration form shown JP / EN / ZH-TW; Plan Basic CTA → same-language Registration with the register label, Pro stays Coming Soon / 即將推出 (mailto); register POST `{}` / filled honeypot / forged token / `CF-Connecting-IP` / Pro + role escalation → 400 `registration_rejected`, GET 405; production `register.php` == repo (plan `basic`, role `user` fixed); test account still excluded; other users unchanged. Limits unchanged (global 30 / 10 min, creations 10 / h + 40 / 24 h, email 5 / h, IP 10 / 10 min auxiliary). |
| next_action | Live. Watch for abuse / support contacts. Test account `shinizm+kpnreg@gmail.com` kept (excluded from metrics) until Shin decides. Post-launch: `BR-LAUNCH-05-EMAIL-VERIFY` (reconsider before paid Pro), `BR-LAUNCH-05-REG-SESSION` (P2). Consent table done. Then controlled smoke (after Shin GO), then `READY TO ENABLE PUBLIC REGISTRATION`. `registrationEnabled` is flipped only by Shin with explicit GO. |
| note | Separate tasks: `BR-LAUNCH-05-EMAIL-VERIFY`, `BR-LAUNCH-05-REG-SESSION` (P2). Billing / Stripe stay out of scope. |

### BR-LAUNCH-09

| Field | Value |
|-------|-------|
| id | `BR-LAUNCH-09` |
| name | Account Security & Destructive Actions |
| parent | Launch readiness (outside `TRUNK-06`; do not reopen `TRUNK-06`) |
| audit_2026-09-28 | Phase 0 audit (audit only). Delete Account 5 steps are UI only (no API; password / OTP not checked; shows deleted but deletes nothing). Change Password stored the new password in plaintext `localStorage['kpi-auth-password']` and faked success (no current password, no API). Change Email only rewrote local profile cache (login ID unchanged). Session Management = Coming soon; no Basic 1 / Pro 3 limit. Change Plan buttons `href="#"`. All mock pages confirmed live in production (GET). Numbered 09 because `BR-LAUNCH-06` is the CLOSED PL Excel task. |
| gate0_2026-09-28 | Production `allowSelfPlanChange` = false (read-only probe: no-session POST to `set-plan.php` -> 403 `forbidden`, exits before any write). Not a Launch blocker; no config change. |
| phase1_2026-09-28 | Real server-side Password Change. New `api/v1/auth/change-password.php` (POST, session user only, `X-KPI-Expected-User` guard, disabled -> 403, rule = public registration `kpi_v1_registration_password_ok` (8+, letter, digit, symbol), current password `password_verify`, same password -> `password_unchanged`, `PASSWORD_DEFAULT` hash; MySQL transaction `UPDATE ... WHERE user_id = ? AND password_hash = ?` (409 `password_conflict` if it changed meanwhile), revoke epoch bump inside the transaction (failure -> rollback, 500 `change_failed`); then `session_regenerate_id(true)` + epoch re-stamp). Shin decisions: other sessions revoked (same epoch as password reset), this session stays signed in on a new session ID (A); same password rejected; legacy `kpi-auth-password` removed on every page load (`kpi-auth-client.js`) and on the Change Password page. UI JP / EN / ZH-TW x Sci-Fi / Office: current password field, inline errors, `js/kpi-change-password-page.js` (only pre-existing `__KPI_AUTH` members, so a cached client still works), success screen only after server 200 (flag read once; direct open shows nothing), password values never stored. `stamp_registration_assets.py` now also covers the 6 Change Password pages; registration pages got only a new `?v=` for `kpi-auth-client.js` (Shin approved; registration unchanged, still off). Not changed: Login, Logout, Password Reset (8-char rule, clears current session), Admin Set Password (8-char rule), Registration, Initial Setup, Profile, force logout, DB schema. Commit `067c51e` pushed; deployed 13 files (production matched `067c51e~1` before upload; FTP + HTTP SHA match). Tests: contract 50/50; local server + UI smoke (PHP 8.3 + MariaDB + Chrome) 161/161; registration server smoke 86/86; password reset 106/106; admin actions 54/54; admin console 43/43; planning readiness 148/148; registration contract 69/69; production verify 36/36 (GET + no-session POST 401; no production password changed) + registration probe 33/33. Pre-existing failures unchanged at HEAD (stale-account annual cache-bust 1, emergency gate Plan CTA 3, profile_edit 3). |
| phase1_close_2026-09-28 | Shin approved the Phase 1 final report. Phase 1 CLOSED; Password Change Launch blocker resolved. |
| phase2_2026-09-28 | Real server-side Email Change with ownership proof. Audit: reuse `kpi_v1_mail_send` (PHP `mail()`), Password Reset TTL (30 min) and cooldown (120 s); `kpi_password_reset_tokens` not reused (no new-email column; `invalidate_user_tokens` would cross-cancel reset tokens). Shin decisions: file-backed pending store `api/v1/data/email_change/` (no DB schema), 6-digit code entered in Settings, old-address notice, explicit duplicate error after the password check, JA labels in Japanese. `request-email-change.php`: session user, expected-user guard, disabled 403, normalize (trim + lowercase + format, 254 max), confirmation match, current password, same email -> `email_unchanged`, duplicate -> 409 `email_unavailable` (only after password), per-user cooldown + 5 sends / hour -> 429 `too_many_requests` + `retryAfterSeconds`, code `random_int` stored only as `password_hash`, pending bound to old email + password fingerprint + revoke epoch, mail failure -> 503 `mail_failed` and pending removed; canonical email untouched. `confirm-email-change.php` (under the registration lock): disabled voids the request, expiry, 5 attempts -> `code_locked`, code verify, state re-check (email / password / revoke epoch changed -> 409 `email_change_stale`), duplicate re-check, MySQL transaction `UPDATE ... WHERE user_id AND email AND password_hash` (UNIQUE 23000 -> `email_unavailable`) + revoke bump, file mode user + index swap with rollback; then `session_regenerate_id(true)` + re-stamp, old address notice (masked new email, best effort). UI JP / EN / ZH-TW x Sci-Fi / Office: step A current password + new email, step B code + back link; `js/kpi-change-email-page.js` (only pre-existing `__KPI_AUTH` members); success banner only after server 200; local profile cache never rewritten; removed the hardcoded password `value` that was live in all 3 pages and the local-only fake update. Commit `54c37d5` pushed; deployed 8 files (production matched `54c37d5~1`; FTP + HTTP SHA match). Tests: contract 59/59; local server + UI smoke with SMTP sink (file + MySQL, 3 languages x 2 modes) 238/238; Phase 1 smoke 161/161; registration smoke 86/86; password change contract 50/50; registration contract 69/69; password reset 106/106; admin actions 54/54; planning readiness 148/148; production verify 35/35 (GET + no-session POST 401; no production email changed, no mail sent). Pre-existing failures unchanged (emergency gate Plan CTA 3, stale-account annual cache-bust 1, profile_edit 3; old Step 0 smoke fails the same at HEAD). Production mail delivery (`mail()` on ConoHa) is not yet verified end to end. |
| phase2_close_2026-09-28 | Production Human Smoke PASS (Shin, dedicated test account created via `admin-create-user.php`, basic / user): code mailed to the new address and confirmed; old email login fails; new email login succeeds; KPN Annual works. P1 observation: old-address notice ("メールアドレスが変更されました") not reported as confirmed in the Human Smoke. Phase 2 CLOSED. |
| phase3_audit_2026-09-28 | Current delete flow (7 pages × JA/EN/ZH-TW) is fake end-to-end: no API call; hardcoded Pro / next billing / Stripe buttons; fictional retention claims; password not verified; OTP never sent and any 6 digits pass; `confirm()` then "削除完了"; reason form sends nothing. All `kpi_users` FKs are ON DELETE CASCADE (store, daily facts / inputs, plan history, profiles, reset tokens, consents); `parent_user_id` has no FK. File data under `api/v1/data/`: users + email index, store blobs + backups, profiles, plan_history, email_change, password_reset, session_revoke, consents, feedback (userId / session email / contact email / UA / message; also mailed to support), registration rate-limit. No audit log exists. Store / profile / daily endpoints re-read the user (401 once deleted); MySQL FK blocks orphan inserts. |
| phase3_freeze_2026-09-28 | Shin frozen: (1) only role `user` may self-delete; `founder_superadmin` / `admin_staff` / `support_readonly` rejected server-side; (2) user with child accounts rejected (「関連アカウントを先に整理してください」), no cascade / no parent_user_id rewrite; a child (leaf) account may delete itself; (3) feedback of the deleted user anonymized (keep message + time, strip userId / emails / UA; mailbox copies out of system scope); (4) 5 real steps: what is deleted → kept / deleted data → current password (server-verified, 10-min delete intent in server session) → 「この操作は取り消せません」 final confirm → server delete → completion; OTP page and Stripe steps removed (old URLs redirect to step 1); (5) completion page: ACCOUNT DELETED / 「アカウントを削除しました。」 + KPN top CTA, reason form removed; (6) session_revoke file bumped and kept as tombstone (deleting it would reset epoch to 0 and revive stale sessions); theme / language keys kept, user-scoped client keys cleared; Stripe wording removed. |
| phase3_blocked_2026-09-28 | **BLOCKED — consent retention policy decision required.** Privacy §6 (「必要な期間…法的義務の履行・紛争解決」) and Terms do not state whether consent evidence survives deletion; Shin chose not to decide yet. Options on the table: cascade delete (as-is) / minimized file record (userId hash + terms / privacy versions + accepted / deleted time, no email; no schema change) / keep DB rows (FK schema change). Production likely has 0 consent rows (registration never opened; admin-created users write none) — not verified. No implementation until decided. |
| phase3_consent_2026-09-28 | Shin decided **Delete everything**: `kpi_user_consents` rows are deleted with the account through the existing `kpi_users -> kpi_user_consents ON DELETE CASCADE` (no schema change, no separate retention file). Reasons: current Terms / Privacy define no post-deletion consent retention; no concrete legal requirement identified; no unnecessary personal data kept. A future retention requirement (legal review) is a separate task that must first define Privacy Policy wording, purpose and period. BLOCK lifted. |
| phase3_impl_2026-09-28 | `api/v1/auth/delete-account.php` (POST; `verify` = current password → 10-min delete intent in server session, 5 failures → 15-min lock; `delete` = `acknowledge: true` + valid intent) and `api/v1/_account_delete.php` (role `user` only; children reject, fail closed; register.lock; preflight writable dirs; MySQL `SELECT … FOR UPDATE` + child re-check + `DELETE FROM kpi_users` in one transaction, dependents via existing CASCADE; file mode removes user + index; then revoke bump (tombstone kept) and best-effort cleanup of email change / reset tokens / store blob / backups / profile / consent / plan history, feedback anonymized; residual logged). `js/kpi-delete-account-page.js`; 7 pages × JA / EN / ZH-TW rewritten (steps 1 / 2 / 3 / 4 + completion; `delete_account2` / `4-2` redirect to step 1; completion page drops the session guard and shows only after a 200 in this tab); client account keys cleared, theme / UI prefs kept. Local smoke 254/254 (file + MySQL + Chrome, 3 languages × Sci-Fi / Office), contract test `scripts/_test_delete_account_contract.py` 49/49; regressions: Phase 2 238/238, Phase 1 161/161, registration 86/86, contract suites green. |
| phase3_split_2026-09-28 | Shin split Phase 3. **Phase 3A — Basic Account Delete: IMPLEMENTED / READY FOR HUMAN SMOKE** (no Stripe subscription; server-side delete; password re-check; protected role / child account guard; consent cascade delete; session revoke; feedback anonymization; client storage cleanup) = `phase3_impl_2026-09-28`. **Phase 3B — Paid / Stripe Account Delete: BLOCKED — Stripe / Billing contract required.** Required before close: Stripe Customer / Subscription ownership contract; active subscription detection; cancellation timing contract; immediate cancel vs `cancel_at_period_end`; proration / refund policy; cancellation failure behavior; Stripe webhook reconciliation; account delete vs billing cancel order; retry / partial failure handling; prevention of deleted KPN account + surviving Stripe subscription; paid-user delete UI copy; JP / EN / ZH-TW; Basic / Pro branching; production-safe smoke. As of 2026-09-28 the repo has no Stripe integration (`api/` has no Stripe code; plan changes are admin-only), so no KPN account can hold a Stripe subscription yet. **Phase 3 Final Close only after 3A + 3B both pass.** |
| phase3a_lifecycle_2026-09-29 | **Phase 3A Extension — Account Lifecycle / Deleted Accounts History** (Shin). Delete Account Human Smoke **paused**; `funkizm@mac.com` not deleted and reserved for the first Human Smoke after Lifecycle is implemented. Direction frozen: minimal Founder-only deletion history, separate from personal / business data deletion (no raw email, password hash, profile, store, daily data, consent contents, IP, UA); return detection by HMAC(normalized email, server-side secret not in repo; plain SHA-256 rejected); returned users start from an empty new account; Founder `Deleted Accounts` page separate from active Users; churn metrics (Active / New / Deleted / Monthly Churn / Returned). Unchanged: consent rows deleted with the account, feedback anonymization, Phase 3B BLOCKED, no Stripe IDs stored. Audit done 2026-09-29 (proposed schema `kpi_account_deletions` + `kpi_account_origins`, history row inserted in the same MySQL transaction as `DELETE FROM kpi_users`). Decisions pending before implementation: Privacy Policy revision, retention period, HMAC key provisioning, fail-closed rule, churn denominator, test-account exclusion, Delete UI copy. |
| phase3a_lifecycle_decisions_2026-09-29 | Shin: **fail closed** (missing HMAC key / history table → delete nothing, 500, retry allowed); **test accounts** excluded via a Founder-toggled "exclude from metrics" flag (per account and per history row); **Privacy order** = Cursor drafts Privacy Policy (JP / EN / ZH-TW + version bump) and STEP 2 copy in L1 → Shin approves (legal review if needed) → L2 implementation. **Retention period: decide after legal review — implementation on hold.** **Churn definition: needs discussion** (not frozen). |
| phase3a_churn_freeze_2026-09-29 | **Monthly Churn contract FROZEN (Shin).** Core metric = **Standalone Customer Account Churn**: role `user` only; child accounts excluded from main churn and counted separately; denominator = eligible accounts existing at start of month; numerator = eligible accounts deleted during the month that existed at its start; same-month create / delete excluded from main churn and shown separately as **Early Churn**; disabled accounts included in the denominator for now (no disable / enable history, past months cannot be excluded exactly); month boundary = **JST**; accounts / history rows with `exclude_from_metrics = true` excluded; plan-specific churn = reference value based on `plan_at_deletion` for now; exact plan timeline = separate task. Formula: Monthly Churn Rate = eligible accounts deleted during month / eligible accounts existing at start of month × 100. |
| phase3a_retention_2026-09-29 | **Retention decided (Shin): 3 years after account deletion**, same contract JP / EN / ZH-TW. Not a statutory period — the period needed for churn, account lifetime, return / re-registration and cohort analysis. Rows older than `deleted_at + 3 years` are deleted automatically. Kept: no raw email (HMAC matching value only), no business data, no consent history, no IP / UA, Founder-side erasure procedure on request. Churn contract `phase3a_churn_freeze_2026-09-29` unchanged. L1 final draft updated; waiting for Shin final approval before final Privacy version / date and L2. |
| phase3a_l1_closed_2026-09-29 | **L1 CLOSED (Shin approved).** Privacy §6 also states: anonymized feedback keeps only message text, sent date / time and category (user ID, login email, contact email, UA, plan, page removed; used for service improvement / quality analysis, not to identify individuals); emails already sent to support before deletion are not deleted automatically by KPN account deletion (support record policy applies). STEP 2 aligned. **Final Privacy version / Last updated = the JST date of the actual L4 production deploy** (not the approval date). Approved contract: retention 3 years after deletion with automatic purge; churn per `phase3a_churn_freeze_2026-09-29`; HMAC only (no raw email); consents deleted with the account; erasure via Founder email lookup; fail closed on missing HMAC key / history table; `exclude_from_metrics`. **L2 implementation ACTIVE.** Delete Account Human Smoke (`funkizm@mac.com`) only after L2 / L3 / L4 are complete and READY. |
| phase3a_l2_2026-09-29 | **L2 implemented, local green (not deployed).** `api/v1/_lifecycle.php` (HMAC-SHA256 over the normalized email with `lifecycleHmacKey` / `lifecycleHmacKeyId` from `config.local.php`, retired keys in `lifecycleHmacPreviousKeys`; readiness = key ≥ 32 chars + both tables / readable files; record build / insert; cleanup status; 3-year purge; NEW / RETURNED / unknown on account creation, never blocking it). `_account_delete.php`: preflight fails closed without lifecycle readiness; MySQL history INSERT inside the delete transaction (after the locked-row + child re-check, before `DELETE FROM kpi_users`); file mode inserts first and removes the row if the user cannot be deleted; after cleanup → `cleanup_status` complete / residual → purge; feedback also blanks `plan` / `pageUrl`. `register.php` + `admin-create-user.php` record the origin. Schema: `kpi_account_deletions` (no FK) + `kpi_account_origins` (FK CASCADE) in `schema.sql` + `schema_kpi_account_lifecycle.add.sql`. STEP 2 copy (JP / EN / ZH-TW) updated in repo. Tests: lifecycle contract 29/29; local smoke 341/341 (Phase 3 file + MySQL + Chrome 3 languages × Sci-Fi / Office, lifecycle 88 incl. fail-closed, INSERT / DELETE failure rollback, residual, purge, rotation, repeat churn); regressions Phase 1 161/161, Phase 2 238/238, registration 85/86 (the one red is the expected lifecycle log line from the legacy-schema test DB without the migration; registration itself 201), delete contract 49/49; other contract suites unchanged vs `dc17991` (same pre-existing reds). Privacy Policy pages / `KPI_PRIVACY_VERSION` untouched until L4. |
| phase3a_l4_2026-09-29 | **L4 ACTIVE (Shin GO 2026-09-29).** Scope: production migration (`schema_kpi_account_lifecycle.add.sql`), HMAC key in production `config.local.php` (never in repo / docs / logs / chat), Privacy Policy JP / EN / ZH-TW with the L1 text + `KPI_PRIVACY_VERSION` = Last updated = actual JST deploy date (prepared as `2026-09-29`; re-stamped if the deploy date differs), STEP 2 + Lifecycle server + Founder UI in the same rollout, read-only production verification → stop at READY FOR LIFECYCLE DELETE HUMAN SMOKE. `funkizm@mac.com` is not deleted without Shin GO. Pre-check (read-only diag): MySQL 8.4.8, lifecycle tables absent, 7 CASCADE FKs, `kpi_users.user_id` varchar(64) utf8mb4_unicode_ci InnoDB (FK compatible), no lifecycle key, registrationEnabled false, target account role user / enabled / basic / no parent / no children. |
| phase3a_l4_result_2026-09-29 | **L4 production rollout done → READY FOR LIFECYCLE DELETE HUMAN SMOKE.** DB backup = ConoHa WING automatic backup (Shin). Migration: CREATE TABLE × 2 only (one-shot key-guarded runner that rejects any other statement; removed after use, 404); schema verified (columns / indexes as defined, InnoDB utf8mb4_unicode_ci, `fk_kpi_account_origins_user` CASCADE → 8 CASCADE FKs, none on `kpi_account_deletions`, 0 rows, existing tables unchanged). HMAC: key id `k1`, 64-char random key (48 random bytes), no previous keys, appended additively to production `config.local.php` between `BEGIN / END lifecycle HMAC (BR-LAUNCH-09 L4)` markers (php -l ok, byte verify); key copy kept only outside the repo in the local ops backup folder (owner-only ACL); the temporary server config backup was deleted after verification. Rotation = move the old key to `lifecycleHmacPreviousKeys`, set a new id / key. Secret check: key value found in 0 repo files (incl. untracked temp outputs) and 0 commits; never printed. Deploy `f191ea3` (24 files: Lifecycle server + admin APIs + Founder UI + Privacy JP / EN / ZH-TW + STEP 2 JP / EN / ZH-TW; production matched the base before upload; FTP + HTTP SHA match). `KPI_PRIVACY_VERSION` = Last updated = 2026-09-29 (JST deploy date); Terms unchanged 2026-02-16. Production verify: read-only diag (lifecycleReady true; fail-closed without key / bad key id / short key; history 0; public rows have no email / HMAC; metrics 2026-09 Active 13 / New 5 / Deleted 0 / Churn 0 of 8 / Early 0; registrationEnabled false; `funkizm@mac.com` role user, enabled, basic, no parent / children, profile 1, store present, origin none → legacy / NEW (pre-tracking), no history row, not excluded) + static / anonymous verify 32/32 (admin APIs 401 / 405, admin pages redirect to login, delete-account 405 / 401, Privacy + STEP 2 live = repo). Founder login UI + general-user 403 verified locally only (no production credentials used). Expectation: `funkizm@mac.com` was created 2026-09-28 (JST month 2026-09), so deleting it in September counts as Deleted +1 and **Early Churn +1**; core Monthly Churn stays 0 / 8 (deleted from 2026-10-01 JST on, it counts in core churn). P2: deleted temp PHP answered 500 once right after removal (file confirmed absent; fresh names return 404). Human Smoke is run by Shin only. |
| ext_marketing_m1_2026-09-29 | **Extension: Lifecycle Segmentation + Marketing Opt-in (Shin GO).** M1 audit / contract / Privacy draft in `docs/br-launch-09-marketing-m1-draft.md`. Legal: 特定商取引法 (consent record 3 years from the last e-mail ad, also after refusal) + 特定電子メール法 (1 month; sender name, refusal notice + address, postal address, contact in every ad mail) → evidence 3 years after the last send. Lifecycle History and Marketing Subscribers are separate (HMAC only vs raw email on opt-in only, no link). Terms need no change. No marketing send in this Phase. Phases M2–M7 proposed. **Shin decided D1–D6 = all recommended (2026-09-29): D1 evidence-only row 3 years after the last send (delete at once if never sent), D2 required choice with no preselection, D3 no new opt-in at delete, D4 the subscription follows the account on email change, D5 ALTER ADD 3 nullable columns, D6 sender address decided in the sender Phase.** Next: M2 (local). Nothing implemented / deployed. |
| ext_marketing_m2_2026-09-29 | **M2 GO (Shin approved D1–D6 + one contract correction).** Lookup correction: Deleted Accounts Email Lookup sends the Founder's email in the POST body (never URL / query); the server normalizes + HMACs it in memory only; raw email never saved to DB / files / logs nor returned; input cleared after lookup; a temporary `Matched lookup: <email>` line only in browser memory, gone on reload / navigation (M1 draft section 10; the L3 server already works this way). **M2 implemented locally (server only; no UI, no production migration / deploy, no marketing send):** `schema_kpi_marketing.add.sql` (`kpi_marketing_subscribers` + `kpi_marketing_consent_events`, no FK, + `seg_country` / `seg_business_type` / `seg_currency` on `kpi_account_deletions`), `_marketing.php` (wording version `mkt-2026-09-29`, HMAC-derived unsubscribe token — only nonce + sha256 stored, stop rule never-mailed → delete / mailed → evidence 3 years after the last send, purge, file + MySQL), registration opt-in inside the account + consent transaction (fail closed; no opt-in = untouched), delete keep / stop required for subscribers (400 `marketing_choice_required`), email change follows the account in the same transaction, neutral POST unsubscribe endpoint with its own rate limits, Settings preference API, Founder list / action APIs (legal hold), lifecycle segment snapshot (catalog codes / `other` / NULL). Details: M1 draft section 16. Local: M2 smoke 124/124, Delete + Lifecycle regression 341/341, Lifecycle phase-2 236/238 + Registration 94/98 (pre-existing harness expectations only), static contracts green incl. new `_test_marketing_m2_contract.py` 45/45. **Deploy order constraint: migration before the M2 server (lifecycle readiness requires the segment columns).** Next: M3 (Registration checkbox + Settings + unsubscribe page). |
| ext_marketing_m3_2026-09-29 | **M2 review OK, `f2fa402` pushed (HEAD == origin). M3 GO (Shin, 2026-09-29).** Decisions: Registration JP meaning frozen (「Forge Laboratoryから、KPNの新機能・新サービス・キャンペーン等のお知らせをメールで受け取る」; separate from Terms / Privacy, optional, default OFF, registration works when OFF, no auto opt-in of existing users; final copy checked by Shin before production deploy). Settings = one row on the existing Preferences page (current state, ON = explicit subscribe + consent event, OFF = unsubscribe, OFF→ON = new consent, no hidden / default opt-in). Production Gate: unsubscribe secret outside the web document root / in the production secret area where possible (`.htaccess` not the primary defense; audit before M7); the server validates the client `marketingConsentVersion` against its current version and fails closed. **M3 implemented locally (UI; no production deploy / migration, no Delete UI (M4), no Founder UI (M6), no marketing send):** Registration optional checkbox (JP / EN / ZH-TW, Sci-Fi / Office; shown only if the server wording version matches the page), Preferences newsletter row (`js/kpi-marketing-preference.js`, immediate apply), unsubscribe confirm page `unsubscribe/` × 3 (`js/kpi-unsubscribe-page.js`, public, POST only by button, neutral result), server consent text = sentence without the optional marker, reason note max 200. Cache-bust via `stamp_registration_assets.py` (now also Preferences / Unsubscribe). Verification: M3 UI smoke 226/226 (file + MySQL), `_test_marketing_m3_ui_contract.py` 43/43, M2 smoke 124/124, Registration e2e 94/98 (pre-existing), other static FAILs identical on `f2fa402`. Details: M1 draft section 17. Next: Shin review of M3 copy + push GO, then M4 (Delete UI). |
| ext_marketing_m4_2026-09-29 | **M3 review PASS, `c4e7e8d` pushed (HEAD == origin). M4 GO (Shin): Delete UI on the frozen D1 / D2 / D3 contract.** M3 copy note for M7: EN "Newsletter emails" → "Email updates" candidate, "You will now receive our newsletter emails." → "You will now receive email updates from Forge Laboratory." candidate (not an M4 blocker). **M4 implemented locally (UI only; no production deploy / migration, no marketing send, no Founder UI):** STEP 4 newsletter block (`js/kpi-delete-account-page.js` + `delete_account5.html` × 3, JP / EN / ZH-TW, Sci-Fi / Office): subscribed → 「退会後もお知らせメールを受け取る」 / 「お知らせメールの配信を停止する」 with no preselection, Delete disabled until chosen, sent as `marketingAfterDelete`; not subscribed → notice only (「現在、お知らせメールは配信されていません。退会後にメールアドレスを配信用として保持することはありません。」), no new opt-in; state unknown → Delete blocked; server `marketing_choice_required` → message + choice shown, nothing deleted. STEP 2: two short lines (newsletter recipient only on keep, separate from the deletion record; consent record only if already mailed, 3 years). Server unchanged (M2 required validation, same transaction / compensation). Verification: M4 UI smoke 140/140 (file + MySQL, incl. marketing store failure inside delete → nothing deleted), `_test_marketing_m4_delete_ui_contract.py` 35/35, Delete + Lifecycle regression 341/341, M2 124/124, M3 226/226, other static FAILs identical to `f2fa402`. Details: M1 draft section 18. Next: Shin review + push GO, then M5 / M6. |
| ext_marketing_m5_2026-09-29 | **M4 review → `ef6643f` pushed (HEAD == origin). M5 GO (Shin): lifecycle segment aggregation, then M6.** **M5 implemented locally (server only; no UI, no production deploy / migration, no marketing send):** `kpi_v1_lifecycle_segments_compute` in `_lifecycle_admin.php` + `lifecycleSegments` on `admin/dashboard.php` (Founder only), separate from the unchanged `lifecycle` metrics. Deletions by country / business type / currency from history rows only (no email / HMAC / ids); same population as `lifecycle.deleted` (standalone, not excluded; month total reconciles with deleted / churn numerator / early churn); scopes = selected JST month + 3-year retention window; NULL → `unknown` (no inference), unlisted → `other`. Verification: M5 smoke 30/30 (file + MySQL), `_test_lifecycle_segments_m5_contract.py` 11/11, L3 dashboard 105/105, lifecycle 201/201, M2 124/124, static FAILs identical to `f2fa402`. Details: M1 draft section 19. Next: M6 Founder UI. |
| ext_marketing_m6_2026-09-30 | **M5 review PASS, `6299a0f` pushed (HEAD == origin). M6 GO (Shin): Founder UI.** **M6 implemented locally (UI; no production deploy / migration, no bulk marketing send):** Founder Email Updates page (`admin/marketing/`: raw email here only; locale / consent / last sent / status; manual unsubscribe + erase with confirm; token material never shown); Deleted Accounts display labels for `seg_country` / `seg_business_type` / `seg_currency` (Unknown vs Other, no backfill, stored codes unchanged); Dashboard "Deletions by Segment" separate from lifecycle metrics ("This month" vs "Retained history"); lookup Option B (`Matched lookup:` in page memory, input cleared); EN "Newsletter emails" → "Email updates", subscribed "You will now receive email updates from Forge Laboratory." (JP / ZH-TW headings unchanged). Verification: M6 smoke 44/44, `_test_marketing_m6_founder_ui_contract.py` 18/18, Founder lifecycle UI 83/83, M5 30/30, M2 124/124, M3 226/226, M4 140/140, L3 121/121, Delete + Lifecycle 341/341. Details: M1 draft section 20. Next: Shin review + push GO, then M7 production readiness (secret placement audit; no deploy until GO). |
| ext_marketing_m7a1_2026-09-30 | **M7-A.1 Consent Evidence Data Minimization (local, no production).** After STOP / unsubscribe of a mailed address: raw email cleared from the evidence-only row. Kept: wording version, source, consent / unsubscribe timestamps and method, last send, retain_until, and a marketing-only match key — not the lifecycle HMAC. Subscribed and keep-after-delete still keep raw email. Founder list shows email only while subscribed. Privacy §1/§6 JP/EN/ZH-TW + Delete STEP 2 aligned. Terms still NO CHANGE. Superseded on the secret used for match_key by M7-A.2. |
| ext_marketing_m7a2_2026-09-30 | **M7-A.2 Marketing Evidence Secret Separation (local, no production).** `marketingTokenSecret` = unsubscribe token only. `marketingEvidenceSecret` = evidence `match_key` only (prefix `kpn-marketing-evidence|`). First `match_key_id` = `k1`. Previous evidence secrets stay usable for the 3-year window. Token-secret rotation must not break evidence lookup. Lifecycle HMAC remains a third key. Privacy user text unchanged (no secret / key-id names). Verification: M2 contract 50/50, M2 131/131 (incl. 23b/23c/23d), M3 226/226, M4 140/140, M5 30/30, M6 44/44. Next: Shin + Case review, then M7-B GO. |
| phase3a_l3_2026-09-29 | **L3 CLOSED (Shin approved 2026-09-29, incl. the 6 implementation choices: existing dashboard cards kept, pre-tracking = NEW (pre-tracking), Founders excluded from metrics, Active / Disabled = current counts, Kind column, admin.js / admin.css cache bust).** L3 (Founder UI) implemented, local green. English-only Founder console. `api/v1/_lifecycle_admin.php` (list without HMAC, email lookup via HMAC under every configured key — input neither stored nor logged, history row delete that only clears returned-account links, `exclude_from_metrics` for live accounts (origin row upsert, `legacy` when absent) and history rows, JST monthly metrics per `phase3a_churn_freeze_2026-09-29`; accounts that are Founders via `founderSuperAdminEmails` are also excluded). Endpoints (Founder Super Admin only): `admin/deleted-accounts.php` (GET, runs the 3-year purge), `admin/lifecycle-lookup.php`, `admin/lifecycle-erase.php`, `admin/set-metrics-exclusion.php` (POST); `admin/dashboard.php` adds `lifecycle` (`?month=YYYY-MM`, last 36 JST months, default current month-to-date) + `lifecycleMonths`; `admin/users.php` adds `signupOrigin` / `excludeFromMetrics`. UI: new `admin/deleted-accounts/` page (Previous User ID / Created / Deleted (JST) / Lifetime / Plan at Deletion / Kind / Origin / Cleanup Status / Returned / Return Count / Exclude / Delete Row with confirm; email lookup form); Dashboard "Account Lifecycle" section (Active / New / Deleted / Monthly Churn / Returned + Early Churn / Child Deletions / Disabled, month selector) above the existing cards (kept as "Accounts (all roles)"); Users adds Origin (NEW / RETURNED / UNKNOWN, pre-tracking accounts shown as NEW (pre-tracking)) + Exclude toggle; nav link on every admin page; `admin.js` / `admin.css` get `?v=20260929-l3`. Tests: Founder lifecycle UI contract 71/71; local smoke 121/121 (file + MySQL: access control, metrics fixture incl. JST boundary seconds, lookup incl. rotation / no key, list + purge, row delete, exclusion, Chrome screenshots); L2 regression 341/341; lifecycle contract 29/29; delete contract 49/49; admin console suites green (profile sync 3 pre-existing reds unchanged). Privacy / Lifecycle contracts unchanged. Production unchanged (new URLs 404). |
| phase3a_l1_draft_2026-09-29 | L1 draft only: `docs/br-launch-09-lifecycle-l1-draft.md` (Privacy Policy JP / EN / ZH-TW change draft + Delete Account STEP 2 draft copy; retention period `TBD — legal review pending`; legal review points). Production Privacy Policy, `KPI_PRIVACY_VERSION` (`2026-02-16`) and STEP 2 unchanged. Next: retention period decided → Shin approval → final Privacy version / date → L2. Lifecycle implementation HOLD. |
| status | ACTIVE (Phase 0 / 1 / 2 CLOSED; Phase 3A IMPLEMENTED + Lifecycle L1–L4 in production — READY FOR LIFECYCLE DELETE HUMAN SMOKE; Phase 3B BLOCKED — Stripe / Billing contract required) |
| priority | P0 |
| started_at | 2026-09-28 |
| phases | 1 Password Change / 2 Email Change / 3 Delete Account / 4 Plan / Subscription placeholder cleanup / 5 Account launch-wide smoke. One phase at a time. |
| next_action | L1 / L3 CLOSED. L4 production rollout done (`phase3a_l4_result_2026-09-29`) → **READY FOR LIFECYCLE DELETE HUMAN SMOKE**; waiting for Shin GO, then the Delete Account Human Smoke with `funkizm@mac.com` only (Cursor never deletes a production account on its own). Phase 3B waits for the Stripe / Billing contract. Phase 4 only after Shin GO. |
| note | Registered follow-ups (not in Phase 1): no attempt limit on wrong current password (same as login; P1); password rule differs between registration / self change (8+ letter digit symbol) and reset / admin set (8+ only), not unified (P2); no `session_regenerate_id` on login (P2, unchanged). |

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

### BR-POST-BOOKING-ICON-COLOR

| Field | Value |
|-------|-------|
| id | `BR-POST-BOOKING-ICON-COLOR` |
| name | Booking Icon Office Mode Color |
| parent | KPN Development (post-launch polish; do not reopen `TRUNK-06`) |
| status | CLOSED |
| priority | P2 Post-launch polish |
| started_at | 2026-09-25 |
| return_to | NONE |
| reason | Office `#header-booking-btn` calendar icon is black because `images/booking_office.svg` hardcodes `fill="#000000"`. Rendered via `<img>`, so CSS `currentColor` cannot recolor it. Desired Office fill `#fff`. Sci-Fi `booking_sci-fi.svg` (`#59e1f3`) unchanged. |
| evidence | Shared SVG fill `#000000` → `#ffffff`. Production Playwright 30/30 PASS (Annual/Monthly/MEP/PL/profile × JA/EN/ZH-TW × Sci-Fi/Office @1200). Office fill `#ffffff`. Sci-Fi fill `#59e1f3`. Booking 30×30. pad-right 368px. overflowX=0. overlapArea=0. Hits booking/DL/settings/mode/Insight all ok. SHA `414b164`. |
| next_action | N/A CLOSED. Do not reopen `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |
| constraint | color-only; no header geometry / booking routing / 07 spacing |

### BR-POST-FOOTER-VERSION

| Field | Value |
|-------|-------|
| id | `BR-POST-FOOTER-VERSION` |
| name | Footer Version Display |
| parent | KPN Development (post-launch polish; do not reopen `TRUNK-06`) |
| status | CLOSED |
| priority | P2 Post-launch polish |
| started_at | 2026-09-26 |
| return_to | NONE |
| reason | Shared footer showed only `© 2025 Forge-Laboratory. All rights reserved.` Source: `scripts/site_chrome.py` `build_footer` / `build_public_footer`. Tutorial and language selector are `position: fixed`, outside the footer. |
| evidence | Static 3-line brand: Key Performance Navigator / Version 1.0.0 / © 2025 Forge Laboratory. Logo kept. Production footer smoke 24/24 PASS. SHA `900bfc3`. |
| next_action | N/A CLOSED. Do not reopen `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |
| constraint | no SHA; no dynamic year; 2025 is Forge Laboratory start year |

### BR-POST-COCKPIT-GAP

| Field | Value |
|-------|-------|
| id | `BR-POST-COCKPIT-GAP` |
| name | Cockpit Annual Target / Business Day layout parity |
| parent | KPN Development (post-launch polish; do not reopen `TRUNK-06`) |
| status | CLOSED |
| priority | P2 Post-launch polish |
| started_at | 2026-09-26 |
| return_to | NONE |
| reason | EN BD label `Total Business Day` widened `.annual-total-bd-group`, centering the 79px box ~19px right. JP/ZH-TW short labels left the box at group left, so Office boxes overlapped. JS `today.right+45` also shifted Sci-Fi target left by locale. Not a viewport-size limit (parent 1020px at 1200–1440). No `@media`. |
| evidence | Shared CSS tokens: BD box `left: calc(100% - 228px)`, gap Sci-Fi 30px / Office 17px (EN reference). JS no longer sets inline left. Production 24/24 cockpit PASS. SHA `deabb85`. |
| next_action | N/A CLOSED. Do not reopen `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |
| constraint | visual/layout only; no KPI math / Today / History behavior |

### BR-ONBOARDING-01

| Field | Value |
|-------|-------|
| id | `BR-ONBOARDING-01` |
| name | KPN Initial Setup & Readiness |
| parent | none (new parent; do not reopen `TRUNK-06`) |
| status | IMPLEMENTED / PRODUCTION VERIFIED 2026-09-27 (Initial Setup; Phase 0-6 CLOSED). Separate follow-up tasks listed in `next_action`. |
| priority | P0 |
| started_at | 2026-09-27 |
| return_to | NONE |
| reason | First-run navigation readiness for existing full_authorized stores. Flow B only. Registration stays on deferred `BR-LAUNCH-05`. |
| phase_0 | CLOSED 2026-09-27. Grandfather, Opening Date, Flow B, Importer reuse, Navigation Readiness, and Setup Completion are frozen. `explicitKnownSeedState` has no store predicate. |
| phase_1 | CLOSED 2026-09-27. Safe guard only: `!grandfathered && !businessTypeComplete` after hydrate. A successful GET with `store:null` is an empty business state (`kpi:storeHydrateSettled`); fetch / profile / Business Type hydrate failure stays PENDING. Commits `bdbc8aa`, `a35a0c7`, `d799395` deployed. Human Smoke PASS on `kpn_full_authorized00` Annual. |
| phase_2 | CLOSED 2026-09-27. Business Profile / Hard Required Step 01 (input + save only). `js/kpi-setup-step0.js`, opened from the Phase 1 guard button on Annual / Monthly JP / EN / ZH-TW. Deployed after `BR-ONBOARDING-01-R1`; UI `39ba2dc`, Step Ruler `76eae50`, ruler visual `d5d1418` (all deployed, production SHA match). Production verification on `kpn_full_authorized00` (real UI, no Human Smoke): Guard -> 初期設定を始める -> Step 01 -> 7 fields -> REQUIRED FIELDS 7 / 7 -> Save -> BUSINESS PROFILE SAVED -> KPNに進む -> Reload. Server after save: profile businessName / companyName / businessType `restaurant` / country `JP` / stateRegion `Kanagawa` / currency `JPY`; store.meta businessType `restaurant`, openingDate `2026-01-01`; dailySales / targets / setup unchanged; daily inputs / facts 0. Reload keeps values on Annual JP / EN (memory + Step 01 prefill); Monthly -> Annual -> Monthly in one browser keeps openingDate. Contract smoke on production assets 329 / 329 (JP / EN / ZH-TW, Sci-Fi / Office, grandfather). Account 00 reset afterwards (`reset-user-kpi.php`): store null, profile empty, daily 0, Guard shows again. Note (pre-existing design, not a regression): Monthly opened alone in a fresh browser does not GET the server store (no session store sync on Monthly since before `d6dced6`), so its memory lacks openingDate until Annual has run. |
| step01_ui | Launch approved 2026-09-27. Kicker `KPN INITIAL SETUP`; 5-step ruler Business Profile / History / Current / Target / Review, Step 01 active; active / completed node + rail `#0F9403`, rail 4px, node 16px, future muted, skipped dashed; `REQUIRED FIELDS n / 7` is a separate in-step count. No further pre-launch visual refinement. |
| blocker_r1 | `BR-ONBOARDING-01-R1` P0 (found 2026-09-27; FIXED and deployed 2026-09-27, `a3b9803`). `d6dced6` removed `readStorePayloadFromLocal` and the user-scope init (`startInitAfterUserScopeBound` / `__userScopeReady`) from Annual / Monthly / Monthly Edit in 3 languages. `KpiYearStore.loadStore()` now reads the in-memory store via `__KPI_DATA_GATEWAY.getJson`, so localStorage and server store never reach memory; store hydrate also waits 8 s. Production Annual HTML matches. Effects: Navigation Readiness can guard grandfathered users with Business Type unset; `store.meta.openingDate` looks empty after reload; any store PUT from these pages sends the in-memory store. FIX 2026-09-27 (Shin GO, not a revert of `d6dced6`): restored per page `readStorePayloadFromLocal`, `resetForUserScope` + init user-scope consume (Annual / Monthly), deferred init `startInitAfterUserScopeBound` / `markUserScopeReady` / `__userScopeReady` (+ `enableSessionStoreSyncIfAuthed` on Annual), MEP preserve + hollow-PUT guard (`persistStoreIfYearMepSafe`) on load / legacy merge / rollover. Kept `d6dced6` past-business-day review (`businessDayUnresolved`, review APIs). Other `d6dced6` losses (dailySalesInputPath light key, MEP lease steal, annual target source heal, business-day three-layer helpers, A/B stream sync, Sales Data lease checks, Busy background rule) were audited 2026-09-27 as `BR-ONBOARDING-01-R2` (see below). Smoke: R1 store 171/171, Step 0 regression 215/215 (no neutralize). DEPLOY 2026-09-27: R1 stage = 9 pages (Annual / Monthly built as `3cc23c8^` + R1, no Step 0 tags), production SHA match, production-asset smoke 171/171. Then Phase 2 stage = `js/kpi-navigation-readiness.js`, `js/kpi-setup-step0.js`, HEAD Annual / Monthly x3; production-asset smoke Step 0 215/215, R1 171/171. |
| hard_required | Business Profile Hard Complete = all 7: businessName (屋号 / サービス名 / 店名), companyName, businessType (canonical, never the restaurant fallback), openingDate (`store.meta.openingDate`, `YYYY-MM-DD`, year+month required, missing day = `01`), country, stateRegion (non-empty text; catalog match not required), currency (country may suggest, never lock). Business Name and Company Name are both required. |
| optional | city, genre, KPI focus, other profile helpers. Never part of Hard Complete. |
| profile_save_p0 | `profile.php` PUT overwrites every column. Step 0 must GET the current profile, keep existing values, merge only Step 0 changes, then PUT the full payload. Never partial-PUT. |
| setup_progress | Unchanged: `complete`, `currentYearAcknowledged`, `targetAcknowledged`, `historicalSkipped`. No `currentStep` / `lastCompletedStep`. Phase 2 never writes `store.meta.setup`. Phase 3: guard-entry Step 01 save creates an empty `store.meta.setup` (activeSetup marker, no flags); STEP 02 Skip sets `historicalSkipped` only. Phase 4: STEP 03 acknowledge sets `currentYearAcknowledged` only (explicit click; refused while the summary is invalid; never inferred from sales). Phase 5: STEP 04 acknowledge / continue-without-target sets `targetAcknowledged` only (explicit click; never inferred from a target value). Phase 6: `complete = true` is written only by the STEP 05 Complete button after the completion contract passes on the latest state; the other flags are kept. Resume is derived from Readiness. |
| grandfather | Unchanged. Grandfathered users are never sent to Step 0 for missing company / country / region / currency / opening date. |
| evidence | Phase 0 freeze 2026-09-27. Module `js/kpi-navigation-readiness.js`. Wired on Annual and Monthly, JP / EN / ZH-TW. MEP / PL and Monthly Edit direct URLs are not wired. |
| blocker_r2 | `BR-ONBOARDING-01-R2` CLOSED 2026-09-27 (see node below). Phase 3 block lifted: `PHASE 3 SAFE TO PROCEED`. |
| phase_3 | CLOSED 2026-09-27 (Shin approved; ACTIVE 2026-09-27 on Shin GO). The STEP 02 done card below was replaced in Phase 4: Next / Skip now continue into STEP 03. STEP 02 Historical Data, `7937a9e`. Pure `KpiNavigationReadiness.historicalSummary(store)`: opening month, range opening..(operatingYear-1)-12, state from frozen `initialDataState`, detected years, level (same year `not_applicable`, previous year `recommended`, 2+ years back `strong`). Detection = canonical `timeline.dailySales` (0 counts, key without finite value does not, before opening date / operatingYear+ ignored, 1234 sentinel only on operatingYear+ per Phase 0 freeze). UI in the Step 01 dialog (`KpiSetupStep0.openHistory`): 5-step ruler 01 completed / 02 active, summary, recommendation note, CTAs Close / Skip / Add Past Data (present: Add More / Next; not_applicable: Next only). Import = existing Annual Past Sales dialog (`#annual-past-sales-btn`, CSV / Excel importer unchanged); STEP 02 returns when it closes. Monthly: Add Past Data opens Annual `?kpnSetup=1`. Skip: light inline confirm, writes `store.meta.setup.historicalSkipped = true` only. Done card after STEP 02 (02 completed / skipped, "next: Current Year (coming soon)", Continue to KPN); no STEP 03 screen. Resume derived from Readiness (no stored step): Annual `初期設定を続ける` button (non-grandfathered, setup pending) and `?kpnSetup=1`; absent -> STEP 02, otherwise the done card. activeSetup: guard-entry Step 01 save creates `store.meta.setup = {}` in the same store push (existing object kept), so imported history does not grandfather mid-setup. `setup.complete` never written. Smoke local 235/235, production assets 235/235; Step 0 regression 329/329 (3 checks re-pointed to the new contract), R2 165/165 + busy 9/9, R1 171/171, importer tests 73/73 + 97/97, planning readiness 148/148. Production real API on 00: 15/15, then reset (store null, profile empty, daily 0). Human Smoke not required. Note: `_test_business_day_review.py` 3 FAIL are pre-existing (expects old `kpi-workbook-layout.js?v=20260926-bdr2`; pages carry `20260927-bdfalse` since before Phase 3). |
| phase_4 | CLOSED 2026-09-27 (Shin approved; ACTIVE 2026-09-27 on Shin GO). Approved decisions: STEP 02 goes straight to STEP 03; Current Year registration reuses Sales Data; a future opening date cannot be confirmed (back to Step 01); operatingYear ahead of today cannot be confirmed. The STEP 03 done card below was replaced in Phase 5: acknowledge / Next now continue into STEP 04. STEP 03 Current Year, `4a3dbc5`. Pure `KpiNavigationReadiness.currentYearSummary(store, today?)`: range max(openingDate, operatingYear-01-01) .. min(local today, operatingYear-12-31); detectedDays / positiveDays from canonical `timeline.dailySales` in range (0 counts as data, non-finite / malformed keys do not, 1234 sentinel excluded on operatingYear per Phase 0 freeze, future dates never counted); status `present` / `none` / `new_business` (opened this year, no data) / `invalid` (`opening_future`: opening date after today; `no_period`: operatingYear ahead of today). Counts never decide completion. UI in the same dialog (`KpiSetupStep0.openCurrentYear`): ruler 01 completed / 02 completed or skipped / 03 active; summary Operating Year / Business Start / Data Period / Days Recorded / Days with Sales (only when recorded > 0) / Status; CTAs Close / Add This Year's Data (Add More when present) / primary `今年度データを確認しました` (present) or `現在の状態で続ける` (none / new business); invalid shows no acknowledge (opening_future offers Edit Business Information -> Step 01 -> STEP 02 -> STEP 03). Acknowledge writes `store.meta.setup.currentYearAcknowledged = true` only, then store push; done card 01 / 02 / 03 completed, "next: Annual Target (coming soon)", `KPN に進む`; no STEP 04 screen. Import = existing Annual Sales Data dialog (`#annual-current-sales-btn`, operatingYear, CSV / Excel importer unchanged); STEP 03 returns and re-evaluates when it closes. Monthly: Add opens Annual `?kpnSetup=1`. STEP 02 Next / Skip now open STEP 03 directly (STEP 02 done card retired; skip push warning shown on STEP 03). Resume (no stored step): history absent -> STEP 02; else not acknowledged -> STEP 03; else STEP 03 done card. activeSetup unchanged (current-year data does not grandfather mid-setup). `setup.complete` never written. Decisions taken on the recommended options (question form returned no answer): STEP 02 -> STEP 03 direct; Sales Data reuse; future opening blocks with Edit Business Information; operatingYear ahead of today blocks. Smoke local 225/225, production assets 225/225; Step 02 regression 235/235 (4 done-card checks re-pointed to STEP 03), Step 0 329/329, R2 165/165 + busy 9/9, R1 171/171, importer 73/73 + 97/97, planning readiness 148/148 (local; Step 0 / Step 02 also on production assets). Deploy 8 files, production matched `7937a9e` before upload, SHA match after. Production real API on 00: 17/17, then reset (store null, profile empty, daily 0). Human Smoke not required. `_test_business_day_review.py` 3 FAIL still pre-existing (bdr2 cache tag). |
| phase_5 | CLOSED 2026-09-27 (Shin approved; ACTIVE 2026-09-27 on Shin GO). The STEP 04 done card below was replaced in Phase 6: acknowledge / Next / resume now continue into STEP 05. STEP 04 Annual Target, `6696849`. Pure `KpiNavigationReadiness.annualTargetSummary(store)`: operatingYear, targetSales, status `set` (operatingYear `years[oy].plan`, source `sales-data-save`, targetSales > 0 — same rule as R2 `isUserSavedAnnualPlanSource`) / `not_set` (none, `rollover-snapshot`, `memory-reference-heal`, default `kpi-year-store`, 0, another year), `acknowledged` (`targetAcknowledged === true`). The frozen grandfather predicate `hasUserAnnualTarget` is unchanged. UI in the same dialog (`KpiSetupStep0.openAnnualTarget`): ruler 01 completed / 02 completed or skipped / 03 completed / 04 active / 05 future; summary Operating Year / Annual Target (currency or 未設定) / Status. CTAs: set -> Close / 年間目標を変更する / primary 年間目標を確認しました; not set -> Close / 今は設定せず続ける (light inline confirm: can set later, KPN usable, existing annual target reminder shows while unset) / primary 年間目標を設定する; already acknowledged -> Close / set or change / primary 次へ (no write). Target input = existing Annual Sales Data dialog (Edit, 年間目標売上, Save; R2 `sales-data-save`, OCC unchanged); STEP 04 re-reads the store when it closes; Monthly goes to Annual `?kpnSetup=1`. Only write: `targetAcknowledged = true`. No separate Setup target. STEP 03 acknowledge / Next go straight to STEP 04; resume: STEP 03 acknowledged -> STEP 04, target acknowledged -> STEP 04 done card (01-04 completed, 05 future, 次は最終確認です（準備中）, KPN に進む). Planning Readiness unchanged: after passing STEP 04 without a target the Annual alert still shows the annual target section, is closable, and Setup does not reopen. Saving a target mid-setup does not grandfather. No `setup.complete`, no STEP 05 screen. Assets `?v=20260927-s4a`. Smoke 276/276 local + prod assets; Phase 4 smoke re-pointed 225/225, Phase 3 235/235, Step 0 329/329 (local + prod); R2 165/165 + busy 9/9, R1 171/171, importer 73 + 97, planning readiness 148, business day review 59 (3 pre-existing bdr2). Production 00: 18/19 + read-only recheck PASS (the one fail was a probe bug), then reset. |
| phase_6 | CLOSED 2026-09-27 (Shin GO; close conditions met: implemented, production verified, P0 / P1 = 0, regression clean, 00 reset). STEP 05 Review / Setup Complete, `e11a327`. Pure `KpiNavigationReadiness.completionCheck({store, profile, businessTypeSet, today})`: Hard 7 (Business Name, Company Name, Business Type, opening year-month, Country, State / Region, Currency) -> historical present / skipped / not_applicable -> `currentYearAcknowledged === true` (summary not invalid) -> `targetAcknowledged === true`; returns `ready` and the first unresolved `step` (profile / history / current / target), never a stored step. `loadCompletion()` re-reads the profile, Business Type and the server store (read-only GET) and checks the in-memory store that will be sent. UI in the same dialog (`KpiSetupStep0.openReview`): re-checks before showing; an unresolved step opens that step instead (profile -> Step 01, history -> STEP 02, current -> STEP 03, target -> STEP 04). Review: ruler 01 completed / 02 completed or skipped / 03 / 04 completed / 05 active; 4 sections (Business Profile 7 rows; Historical state + detected years; Current Year confirmed + detected / positive days; Annual Target amount or 未設定のまま続行 + confirmed); non-blocking warnings (historical skipped, target not set, no positive sales day this year, Pro with no expense data). CTAs Close / primary 初期設定を完了する (Complete Initial Setup / 完成初始設定). Complete re-checks the latest state (unresolved -> that step, nothing written), then sets only `setup.complete = true` on the existing setup object (historicalSkipped / currentYearAcknowledged / targetAcknowledged kept) and saves through the gateway (expectedRevision; 409 -> gateway conflict pull, Review re-checked with a notice, nothing completed; other failure -> memory flag reverted, error, retry possible). CTA disabled while saving (one complete PUT on triple click). Already complete -> completion card, no write. Completion card: ruler 01-05 completed (02 stays skipped when skipped), KPN INITIAL SETUP COMPLETE / 初期設定が完了しました。 / KPN に進む; Readiness settles so 初期設定を続ける disappears. After complete: NORMAL because `setupComplete` (activeSetup false), no guard, no resume, `?kpnSetup=1` ignored; Planning Readiness target alert may still show and does not reopen Setup. Before complete: Close keeps setup pending, resume goes to STEP 05; no auto complete on STEP 04 ack, reload, return to Annual, or Review display. STEP 04 acknowledge / Next go straight to STEP 05. Assets `?v=20260927-s5a`. Smoke 225/225 local + prod assets; Phase 5 smoke re-pointed 276/276, Phase 4 225/225, Phase 3 235/235, Step 0 329/329 (local + prod); R2 165/165 (single run; one tab-sync timing flake only under 11 parallel jobs) + busy 9/9, R1 171/171, importer 73 + 97, planning readiness 148, business day review 59 (3 pre-existing bdr2). Production 00: 16/16 (Step 01 -> 02 skip -> 03 -> 04 without target -> Review -> close -> reload -> resume -> Complete -> NORMAL -> reload Annual / Monthly / `?kpnSetup=1` NORMAL), then reset (store null, profile empty). Human Smoke NOT REQUIRED. |
| next_action | Initial Setup IMPLEMENTED / PRODUCTION VERIFIED. Nothing new starts without Shin GO. Separate tasks: post-launch ruler animation, `BR-POST-SETUP-EXTRA-PUT` investigation, reminder polish, Registration integration (`BR-LAUNCH-05`, do not auto-start), launch-wide destructive action smoke. The 7-field Hard Gate on the Phase 1 guard stays off in production (separate GO); the 7 fields are enforced for completion at STEP 05. |
| constraint | no DB migration; no Registration change; no Importer change; no Business Type contract change; no Planning Readiness reuse; no Annual / Monthly / MEP / PL math change; excel/ untouched |

### BR-ONBOARDING-01-R2

| Field | Value |
|-------|-------|
| id | `BR-ONBOARDING-01-R2` |
| name | `d6dced6` Residual Regressions (non-R1) |
| parent | `BR-ONBOARDING-01` |
| status | CLOSED 2026-09-27 (ACTIVE 2026-09-27 on Shin GO; fixed, deployed, production verified) |
| priority | P0 |
| started_at | 2026-09-27 |
| closed_at | 2026-09-27 |
| return_to | `BR-ONBOARDING-01` Phase 3 (block lifted) |
| reason | `d6dced6` replaced the inline `KpiYearStore` of Annual / Monthly / Monthly Edit (JP / EN / ZH-TW) with an older copy. R1 restored store init only. Callers still use `typeof KpiYearStore.X === 'function'` guards, so the missing APIs fail silently. Production runtime (account 00, read-only probe): `canEditSalesDataLive`, `readSavedAnnualPlanTarget`, `hasSavedAnnualPlanTarget`, `isUiBusinessDay`, `isBaselineActualDay`, `isPlanningBusinessDay` are undefined on all 9 pages. |
| audit | Method: `d6dced6~1` vs `d6dced6` vs HEAD, production runtime probe, mocked before/HEAD render. (1) dailySalesInputPath light key: C P2. Path still persists via `store.meta` + full `persistStore()`; cross-tab storage sync and toggle-without-store-PUT are lost. (2) MEP lease steal: D. `acquireEditLease` no longer honours `meta.steal`, but no caller passes `steal: true` before or after `d6dced6`. (3) Annual target source / memory heal: C P0. `syncAnnualTargetDisplay` and `hasPlan` read the missing APIs, so Annual Cockpit shows `—` for annual target, Total Business Day, monthly business days / average target and cumulative targets for every saved target (mock: before `¥36,000,000` / `364`, HEAD `—` / `—`). Stored target is intact. `memory-reference-heal` also gone. (4) Business-day three layers: C P1. Planning layer masked by (3). Baseline layer: `computeObserved` counts no-data weekdays as business days; partial-year history skews `rec.observed` (persisted) and the operating-year H/L baseline (mock Apr-Dec data: before 266 BD / ~100 %, HEAD 330 BD / Jan-Mar 0 % / ~123 %). Full-year data identical. (5) A/B stream sync: C P1. `syncDailyIncomeStreamsFromTimelineTotals` removed from Sales Data Save; masked by (6), but restoring (6) alone would let MEP `sales_a` / `sales_b` / `store_sales` diverge from daily totals. (6) Sales Data lease check: C P0. `canEditSalesDataLiveNow()` is always false, so Sales Data Save is rejected even in Edit with the lease held (production UI on account 00: dialog `未保存の変更があります。編集モードに切り替えて保存してください。`, 0 writes). `persistSalesDataModalSave` also lost its own path / lease check. (7) Busy background rule: C P2. `runServerYearRebuild` wraps background year rebuild in `__KPI_BUSY.run('save')` again (`KPI-BUSY-NAV-OFF-CX` lost). No data loss or OCC break found: stored sales / targets / business days stay intact; Monthly PUTs carry the full store. |
| root_cause | `d6dced6` swapped in an older `KpiYearStore` copy and HEAD kept it (R1 restored init only). The six APIs were dropped, and callers guard them with `typeof ... === 'function'`, so they failed silently: no saved target (`—`), `canEditSalesDataLiveNow()` always false, readiness / cockpit fell back to weekday or raw-target paths. |
| fix | `fabd406` (R2-1..R2-5) + `335d6af` (R2-6), 9 pages (Annual / Monthly / Monthly Edit x JP / EN / ZH-TW). Per page, only functions that page had at `d6dced6~1` were ported (Monthly never had `canEditSalesDataLive`, A/B sync or the light key; they were not added). R2-1: `isUserSavedAnnualPlanSource` (`sales-data-save` only; `rollover-snapshot` / `memory-reference-heal` are not user targets), `hasSavedAnnualPlanTarget`, `readSavedAnnualPlanTarget`, `annualFacts.annualTarget` from the saved target, memory-only heal in `syncToAnnualDaily` (only when no plan target > 0; never persists), `writeAnnualTarget` persists on `sales-data-save` (target was memory-only after Save). R2-2: `canEditSalesDataLive` (annual path + daily-sales lease); `persistSalesDataModalSave` returns `{ok:false}` for no_daily / path_blocked / edit_lease_lost; `persistFromAnnualDaily` skips sync on failure. R2-3: `readBusinessDayFlag`, `isUiBusinessDay` (false off, true/unset open), `isBaselineActualDay` (false off, true on, unset only if sales > 0), `isPlanningBusinessDay` (saved-target year only, false off); `computeObserved` uses baseline, `snapshotIsBusinessDay` uses planning / baseline. Unresolved review days are unset flags (baseline excluded; resolve writes the flag). R2-4: `syncDailyIncomeStreamsFromTimelineTotals` in Sales Data Save (store_sales = total - A - B; A+B > total clears A/B); dailySales stays canonical, dailyMeal untouched. R2-5: per-device `kpiNavigator.dailySalesInputPath` light key (write on toggle, apply on init / `reload()` after server hydrate / storage event); Edit toggle and tier enforcement no longer full-PUT the store. R2-6: background year rebuild without Busy (`KPI-BUSY-NAV-OFF-CX`). Not restored: MEP lease steal (dead). Kept: past-business-day review, dailyMeal, R1 init, Step 0, OCC. |
| smoke | R2 contract smoke 165/165 (JP / EN / ZH-TW; Annual / Monthly / Monthly Edit; target, Sales Data View/Edit/Save/reload/OCC 409, full-store PUT, null store + Edit, 3 business-day layers on full / partial year, zero-sales / closed / unresolved / resolved days, series daily / lunch / dinner / customers / groups / A-B / reload, tab sync). Same smoke on `31824c3` pages: 30/111. R2-6 busy 9/9 (fails before). Regression: R1 store 171/171, Step 0 329/329 (Sci-Fi / Office, grandfather). Inline script syntax check OK on all 9 pages. |
| deploy | 2026-09-27 stage r2: 9 pages from `335d6af`, production matched `31824c3` before upload, backup taken, production SHA match + markers OK. Production-asset smoke 165/165 + busy 9/9. |
| production | Account 00 only, real API: View Save refused (read-only, disabled, handler refuses, 0 PUT); Edit toggle 0 store PUT (empty store not pushed); Edit Save accepted, server dailySales + plan.targetSales `12345678` source `sales-data-save`, revision advanced; close without prompt; reload Annual / Monthly both use the saved target (Annual `¥12,345,678`, BD 365, MTD / YTD targets). 7/7. Reset afterwards: store null, profile empty, daily 0. No other account touched. Human Smoke not required. |
| residual_notes | Not in the R2 audit, not fixed (registered as `BR-POST-D6-MINOR`, P3): Monthly Edit `writeDailyIncome` ignores `meta.deferPersist` (extra local persist per MEP cell; server PUT is debounced, no partial PUT); `setSelectedDate` no longer writes `operatingSelectedIso` (Annual Focus reads it as optional fallback); `setPastSalesEditEnabled` full-persists the store on toggle. |
| next_action | none (CLOSED). Phase 3 SAFE TO PROCEED; needs Shin GO. |
| constraint | not a revert of `d6dced6`; keep past-business-day review (`businessDayUnresolved`) and R1 init; excel/ untouched |

### BR-POST-SETUP-RULER-ANIM

| Field | Value |
|-------|-------|
| id | `BR-POST-SETUP-RULER-ANIM` |
| name | Initial Setup Step Ruler Progress Animation |
| parent | `BR-ONBOARDING-01` |
| status | DEFERRED — POST-LAUNCH / MINOR UX POLISH |
| priority | P3 |
| started_at | not started |
| return_to | none |
| reason | Users likely see Initial Setup once. Show setup progression as the start of navigation. Idea: at step start the rail stops at the active node; on Save / Step Complete the green rail extends smoothly to the next node, then that node turns into a green dot. Sci-Fi is the main effect; Office keeps the same meaning with a quieter animation. |
| next_action | REGISTER ONLY. Not a Launch blocker; unannounced post-launch polish. Do not implement now. |
| constraint | keep 5 steps, state logic, `#0F9403`, rail 4px, node 16px, separate REQUIRED FIELDS count |

### BR-POST-SETUP-EXTRA-PUT

| Field | Value |
|-------|-------|
| id | `BR-POST-SETUP-EXTRA-PUT` |
| name | One extra store PUT during Initial Setup |
| parent | `BR-ONBOARDING-01` |
| status | REGISTERED — INVESTIGATE (not a Launch blocker) |
| priority | P2 |
| started_at | not started (registered 2026-09-27, Shin) |
| return_to | none |
| reason | Phase 3 production run on account 00: one more store PUT than expected between Step 01 save and STEP 02 skip. Phase 4 production run showed the same pattern (one store PUT between STEP 02 skip and the Sales Data import; none after STEP 03 close). Phase 5 production run: plain reloads of Annual and Monthly with a saved target sent 2 store PUTs (no setup / target change). Phase 6 production run: 6 store PUTs for 5 expected writes (Step 01, STEP 02 skip, STEP 03 ack, STEP 04 ack, Complete); setup unchanged after reloads. STEP 02 / STEP 03 / STEP 04 view, close, next and resume write nothing in the mocked smoke. Suspected init / reload / sync path; not investigated. |
| goal | Identify which init / reload / sync path sends it; check whether it is a redundant PUT of the same store; confirm no revision / OCC / data-loss impact. |
| next_action | REGISTER ONLY. Do not fix inside onboarding phases. |
| constraint | no Busy / persist / rebuild changes as a side effect |

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

### BR-POST-HOME-01

| Field | Value |
|-------|-------|
| id | `BR-POST-HOME-01` |
| name | KPN Home / Simple Mode |
| parent | post-launch (do not reopen `TRUNK-06`) |
| status | PRODUCTION VERIFIED / CLOSED |
| priority | P1 |
| started_at | registered 2026-09-30 (Shin); production close 2026-10-01 |
| return_to | none |
| purpose | Daily-use entry page so Daily / Monthly / Annual current state can be read on one screen. Initial Setup = do not get lost the first time; Home = do not get lost in daily operation; Full KPN = detail analysis. |
| concept | Do not redesign. Recompose. Three independent windows (Daily, Monthly, Annual), 32px gap, default collapsed, multiple expansion allowed. One Shared Reference Date. Home is in the Global Menu before Annual. Logo stays 217×32. |
| design_note | [`docs/br-post-home-01.md`](./br-post-home-01.md) |
| head | `3c8ec2598843bd07d524ac1642094007893ba2a3` |
| h1 | **DONE** |
| h2 | **DONE** |
| h3 | **DONE** |
| h4a | **DONE / VERIFIED** — Shared Reference Date Foundation |
| h4b | **DONE / VERIFIED** — Home Shell / 3 Window Layout |
| h4c | **DONE / VERIFIED** — Primary KPI / Data Binding |
| h4d | **DONE / VERIFIED** — Expanded KPI / Progress |
| h4e | **DONE / VERIFIED** — Global Menu / Site Chrome Integration |
| h4f1 | **DONE / VERIFIED** — Daily CTA |
| h4f2 | **DONE / VERIFIED** — Sales Progress Warning |
| h4g | **DONE / VERIFIED** — Opening Date Preference UI |
| h4h | **DONE / VERIFIED** — Pre-Deploy Validation. Technical blockers = 0. |
| next_action | None. PRODUCTION VERIFIED / CLOSED. CURRENT PATH unchanged. Home is not the active path. |
| constraint | 78 runtime files deployed. Docs and generator scripts were not in the runtime deploy. Deferred, not blocking this close: Annual rebuild stays outside the Home `businessDays` guard; Opening Date Preference server sync; Settings pages without a CSS cache query; disabled smoke users with KPI data reset; Home replacing some Daily-page usage is not v1. |

### BR-POST-HOME-02

| Field | Value |
|-------|-------|
| id | `BR-POST-HOME-02` |
| name | Home / Simple Mode Redesign |
| parent | post-launch (do not reopen `TRUNK-06`) |
| status | PRODUCTION VERIFIED / CLOSED |
| priority | P1 |
| started_at | registered 2026-10-02 |
| return_to | none |
| purpose | Daily-use entry so Daily / Monthly / Annual current state can be read on one screen. Home v2 is not an edit screen. Initial Setup = do not get lost the first time; Home = do not get lost in daily operation; Full KPN = detail analysis. |
| design_source | Shin’s latest PNG. Red dimension lines, red px numbers, and red guides are annotation, not UI. |
| dimensions | Width 900px. Daily Close 360px / Open 650px. Monthly Close 360px / Open 985px. Annual uses the Monthly structure. |
| sales_progress | Existing KPN contract. Values only: Daily Actual/Target, Monthly cumulative, Annual cumulative. No dynamic scale. That stays `BR-POST-PROGRESS-SCALE-01`. |
| business_day_progress | Working proposal: bright green = elapsed, dark track = remaining, triangle = current/selected business day, yellow marker on this bar = remove candidate. Sales yellow marker stays. |
| pace_alert | No large visual redesign here. That stays `BR-POST-PACE-ALERT-01`. |
| color | Sci-Fi primary: Cyan `#58E1F3`, Green `#0F9403`. Yellow target marker remains the existing Progress contract. Office keeps the existing Office contract. |
| menu | JP ホーム / EN Home / ZH-TW 首頁. JP does not use "Home". 1200px must not overflow or overlap. Adjust left padding, margin, and logo-menu gap before shrinking the logo. |
| detail_nav | Lower-right link to that window’s detail page. Home v2 keeps the existing v1 label and destination. |
| design_note | [`docs/br-post-home-02.md`](./br-post-home-02.md) |
| h2_1 | **SUPERSEDED** — separate pre-implementation audit was not recorded |
| next_action | None. PRODUCTION VERIFIED / CLOSED. CURRENT PATH unchanged. Home is not the active path. |
| constraint | Do not build a Home-only KPI engine. Reuse existing Daily / Monthly / Annual calculations. Home is presentation only. Annual Target Revision / Reforecast is a separate task. Production commit `305924ee4afdcf6f62d52669a654f86bdd567ad3` (2026-10-03). JP / EN / ZH-TW × Sci-Fi / Office smoke PASS. `kpi-navigator/favicon.ico` 404 did not surface as a pageerror. |

### BR-POST-PROGRESS-SCALE-01

| Field | Value |
|-------|-------|
| id | `BR-POST-PROGRESS-SCALE-01` |
| name | Dynamic Progress Bar Scale |
| parent | post-launch (do not reopen `TRUNK-06`) |
| status | DEFERRED / POST-LAUNCH / REDESIGN |
| priority | not raised |
| started_at | registered 2026-10-02 |
| return_to | none |
| purpose | Later redesign so an achievement above the current visual ceiling can still move the target marker left and keep 150 / 200 / 300% visually distinct, on one contract for Daily, Monthly, Annual, Insight, and Home. |
| current_contract | Target 100% = 66.67% of the track. Actual = that position times the achievement ratio. Visual max = 90% of the track. 135% and above share one visual position. The printed percent is not clamped. |
| historical_audit | Sales Progress dynamic scale: evidence not found. First shipped formula is `e69ada5` (2026-03-27). `docs/annual-kpi-strip-memo.md` records the fixed 2/3 line. |
| reference | Past Sales seasonality only: `getSeasonalityChartScale`, `scaleMax = max(peak, 100)`, 100% marker = `(100 / scaleMax) × 100%`. `9ef8dba` (2026-07-02). `docs/past-sales-floating-window-memo.md` §12.5. Not the Sales Progress bar. |
| design_note | [`docs/br-post-progress-scale-01.md`](./br-post-progress-scale-01.md) |
| next_action | REGISTER ONLY. Do not implement. Do not change the current Sales Progress contract. |

### BR-POST-PACE-ALERT-01

| Field | Value |
|-------|-------|
| id | `BR-POST-PACE-ALERT-01` |
| name | Business-day vs Sales Pace Alert Visual Contract |
| parent | post-launch (do not reopen `TRUNK-06`) |
| status | DEFERRED / POST-LAUNCH / REDESIGN |
| priority | not raised |
| started_at | registered 2026-10-02 |
| return_to | none |
| purpose | Later redesign of the Home pace warning visual contract. |
| current_contract | gap = raw Business-day Progress − raw Sales Progress. gap < 10 normal; 10 <= gap < 20 orange; gap >= 20 red. Home overwrites the Sales Progress triangle and percentage color. Introduced `5e7dd63` (2026-10-01). Bar paint `a6503ed` (2026-10-01). |
| historical_audit | Pre-Home Business-day vs Sales pace warning: evidence not found. Not a restore. Achievement-severity triangle color since `e69ada5` (2026-03-27) is a different rule and remains on Daily FW / Insight. |
| design_note | [`docs/br-post-pace-alert-01.md`](./br-post-pace-alert-01.md) |
| next_action | REGISTER ONLY. Do not change the current Home pace warning. |

### BR-LOCAL-VERIFY-01

| Field | Value |
|-------|-------|
| id | `BR-LOCAL-VERIFY-01` |
| name | Full Local Verification Environment |
| parent | none (infrastructure parent; do not reopen `TRUNK-06`; does not replace CURRENT PATH) |
| status | CLOSED (2026-10-04). Phase 0 audit CLOSED. Phase 1 LOCAL VERIFIED / CLOSED. Phase 2 LOCAL VERIFIED / CLOSED. Phase 3 REAL MYSQL VERIFIED / CLOSED (3A CLOSED, 3B CLOSED). Phase 4 LOCAL MYSQL VERIFIED / CLOSED. Phase 4A user-facing contract 122 / 122, executed 123, supplemental 1, CLOSED. Phase 4B Admin 5 / 5, normal-user denial verified, CLOSED. |
| priority | CRITICAL / HIGH (tree band P0 for release safety). Continuous, not a one-shot Launch ticket. |
| type | Development Infrastructure / Release Safety / Continuous Quality |
| timing | Pre-launch foundation and post-launch continuous. New features extend fixture and smoke coverage. |
| started_at | registered 2026-10-03 |
| return_to | none |
| purpose | Confirm major KPN behavior locally without touching the production DB or production users. Sequence to prefer: local, automated smoke, representative human visual smoke, API / DB contract verification, production deploy, minimal production read-only verification. |
| principle | Production-like frontend: real JS, navigation, rendering, importer, and feature gating. Replace dangerous external dependencies with a local fixture, a test DB, or a controlled local API. Do not weaken production code to make tests easier. Not a fake screenshot site. |
| phase_0 | Audit only (2026-10-03). No local-auth mock, no new fixture framework, no page migration, no Stripe mock. Canonical local API doc is `php -S 127.0.0.1:8080 -t .` plus gitignored `api/v1/config.local.php`. Example `storageDriver` is `file`, so local MySQL is optional. `python -m http.server` serves HTML and does not execute PHP, so authenticated product behavior is incomplete on that server. Playwright is a host Python package launching system Chrome (`channel="chrome"`). There is no npm Playwright project. Committed browser harness to reuse, not replace: `scripts/_test_multi_business_upload_smoke.py` (local API stub, six business types). Logic harnesses: import safety guard, import recovery, multi-business acceptance. Auth contract tests exist for registration, password, email, delete, and session enforcement. They are not one command. |
| pages | Derived 2026-10-03, excluding `scripts/`, `old_projecto/`, `back_up/`. 128 HTML/PHP files. Product surface 116 = app 22 (JA 8, EN 7, ZH-TW 7) + settings 57 (19 x 3) + public 32 (JA 11, EN 11, ZH-TW 10; no `zh-tw/index.html`) + admin PHP 5. Excluded from that 116: `PHP/` 4, `tools/` 4, PL `shell.html` / `layout-prototype.html` 3. Daily has no page (floating window). Initial Setup has no page (dialog on Annual / Monthly). Subscription UI is `setting/change_plan.html` plus static `plan_details.html`. |
| local_run | This audit did not boot a server. Static HTML can open on the documented Python server. Product pages that call `/api/v1` do not complete there. Admin pages are PHP. `plan_details.html` and session management open, and they are dummy / construction state, not billing or session-limit behavior. |
| auth_recommendation | One architecture: local PHP with `storageDriver=file` and versioned fixture users (logged out, Basic, Pro, setup required, setup complete, grandfather, demo/test, founder only where the page needs it). Playwright drives the real pages on `127.0.0.1`. Keep the existing Python API stub for importer-only browser tests. Do not make interception the second auth model. |
| store_recommendation | Hybrid, with local PHP file storage as the primary. Fixture JSON seeds that file store. Playwright interception stays inside the existing importer harness. Local MySQL is optional later, not the first step. No production DB. |
| visual | Functional smoke and visual smoke are both required. Playwright screenshots can cover geometry, overflow, clipped labels, locale layout, the responsive lower bound, modal placement, and pageerror. Human visual smoke stays representative. |
| language_matrix | Same page, same state, same fixture, JP / EN / ZH-TW. Prerequisite for `BR-I18N-ARCH-01`. Trees already diverge (ZH-TW PL generator is JA/EN only). |
| business_matrix | Do not run the full Cartesian product. Restaurant = full feature. Hotel = non-restaurant complex. Retail = non-restaurant simple. Hair / Fitness / Other = targeted parity. |
| fixtures | Possible canonical set: empty, basic, pro, restaurant, hotel, retail, setup-required, full-year, imported, pl. Must be deterministic, versionable, free of personal data and production IDs, resettable. `fixtures/demo/restaurant-v1/` is restaurant CSV only. It is not this set. |
| write_safety | Required later, not built: LOCAL TEST MODE refuses known production hosts, production DB credentials, FTP, live Stripe keys, outbound email, account deletion, registration, and password reset against production. Today, safety is per-script (`127.0.0.1` in some harnesses). Deploy scripts can still reach production. There is no shared hard fail. |
| release_gate | Future gate before deploy: relevant contract tests, page functional smoke, locale smoke, visual smoke, pageerror 0, targeted human smoke, git diff audit, deploy, production static/read-only check. A single `python scripts/kpn_release_smoke.py` is not justified yet. Existing pieces are many scripts, not one command. Do not create it in Phase 0. |
| stripe | Do not mock Stripe in this task yet. The local user/plan response must be able to grow later: unpaid Basic, active Pro, inactive, cancellation pending, checkout return, webhook-derived state. UI locale and billing region stay separate (`BR-I18N-ARCH-01`). |
| phases | 0 audit CLOSED. 1 Safe Local Runtime Foundation LOCAL VERIFIED / CLOSED (2026-10-04). 2 Canonical Fixtures v1 IMPLEMENTED / LOCAL VERIFIED / CLOSED (2026-10-04). 3A Local MySQL runtime foundation IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED (2026-10-04). 3B Canonical Fixture MySQL Parity IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED (2026-10-04). Phase 3 Local MySQL Parity REAL MYSQL VERIFIED / CLOSED. 4 Full Page Smoke LOCAL MYSQL VERIFIED / CLOSED (2026-10-04). 4A user-facing CLOSED. 4B Admin CLOSED. Importer harness reuse stays with the existing upload smoke. |
| phase_mysql | **Phase 3A — IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED (2026-10-04). Phase 3B — IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED (2026-10-04). Phase 3 Local MySQL Parity — REAL MYSQL VERIFIED / CLOSED. Phase 4 Full Page Smoke — LOCAL MYSQL VERIFIED / CLOSED (2026-10-04).** Contract: [`local-mysql-runtime.md`](./local-mysql-runtime.md) and [`local-canonical-fixtures.md`](./local-canonical-fixtures.md). `localTestMode` allows `storageDriver=mysql` only for `127.0.0.1` / `localhost` / `::1` and the exact database name `kpn_local_test`. The guard runs before PDO. Local test connections set `time_zone='+00:00'`. Production connections do not. Bootstrap uses a machine-local admin identity. Normal SQL, including canonical seed and reseed, uses `kpn_local_runtime` with DML only on `kpn_local_test`. `scripts/kpn_local_mysql_bootstrap.php` applies `api/v1/schema.sql`. `scripts/kpn_local_mysql_seed.php` maps five canonical accounts from the manifest into `kpi_users`, `kpi_user_profiles`, `kpi_store`, and `kpi_daily_inputs`. Reseed deletes only those five user ids. `fx-legacy-pro` stays file-only. `founder-seed` / `founder-delete` touch only the local smoke user `localfounder1` and do not change the five customer accounts. |
| size | First usable baseline is a small slice. Full page x locale x state coverage is continuous and larger than one implementation turn. |
| p0 | Phase 1 local guard is LOCAL VERIFIED / CLOSED. Unresolved client plan does not grant Pro. Explicit server `pro`, including `legacyPlan`, is still honored. A static-server "open" is not a behavioral pass. |
| p1 | Canonical fixture v1 is LOCAL VERIFIED / CLOSED. No one-command gate. Subscription and session pages are not locally meaningful yet. Daily and Setup are not URLs. Page smoke still has to inject `fixtureClock` before application JavaScript. |
| p2 | Full screenshot archive, admin visual matrix, responsive sweep beyond the representative set. |
| phase_2 | IMPLEMENTED / LOCAL VERIFIED / CLOSED (2026-10-04). Contract: [`local-canonical-fixtures.md`](./local-canonical-fixtures.md). Manifest `fixtures/local/canonical/manifest.json`. Six accounts, four lightweight business-type cases, fixed clock `2026-10-03T12:00:00+09:00` / `Asia/Tokyo`. Reset requires `localTestMode`, a non-production root, and `.kpn-local-fixture-root` bound to that path. `fx-legacy-pro` is file-storage only. Phase 1 ids `LOCAL_BASIC` / `LOCAL_PRO` alias the basic restaurant and pro hotel accounts. `fixtures/local/phase1-baseline.json` is retained and is not the seed source. |
| phase_4 | LOCAL MYSQL VERIFIED / CLOSED (2026-10-04). Stack: local KPN, local PHP, local MySQL, production-equivalent schema, canonical fixtures, automated browser smoke. User-facing contract 122 / 122, executed 123, supplemental 1 (`core-profile-jp`). Admin routes 5 / 5. A normal Basic user is denied with HTTP 403. `localfounder1` is local-smoke only and is removed when `scripts/_test_local_admin_smoke.py` finishes. Production DB, production KPN requests, FTP, and real mail stay prohibited. `kpn_local_runtime` is DML-only on `kpn_local_test`. The bootstrap identity stays separate. Browser contexts are isolated. Fixture mutations are detected and restored. |
| next_action | CLOSED (2026-10-04). Do not reopen. `BR-I18N-ARCH-01` is not started. Stripe stays a separate track. CURRENT PATH unchanged. |
| constraint | Phase 2 changes the canonical manifest, the local seeder, the Phase 1 runner fixture source, and this task record. No MySQL, no importer change, no product clock, no Stripe, excel/ untouched. |

### BR-I18N-ARCH-01

| Field | Value |
|-------|-------|
| id | `BR-I18N-ARCH-01` |
| name | Localization Architecture v2 |
| parent | none (architecture parent). Prerequisite: `BR-LOCAL-VERIFY-01` baseline. |
| status | REGISTERED — direction recorded 2026-10-03. Implementation NOT STARTED. Phase 0 parity map not started. |
| priority | HIGH (tree band P1). Post-launch scalability. Not a current Launch blocker. |
| type | Architecture Debt Paydown / Internationalization / Post-launch Scalability |
| started_at | registered 2026-10-03 |
| return_to | `BR-LOCAL-VERIFY-01` until its baseline exists |
| purpose | Stop copying a full HTML tree per language. Target: one shared page structure, locale dictionaries (`ja`, `en`, `zh-tw`, later `es` / `fr` / `it` / `th` / `id` and others), shared CSS for the majority, and a locale CSS override only where a language needs it. |
| principle_locale_billing | UI locale and billing region are different. EN may serve US, GB, AU, SG, IN, and others. ES may serve Spain, Mexico, and Latin America. Stripe regional pricing must not be derived only from UI language. |
| pilot | Home is the first product pilot after the local-verification baseline. It is smaller than generated Annual / Monthly / MEP, it has a fresh JP / EN / ZH-TW visual contract, and it has less editing logic. It still hydrates the store, so it is not a safe pilot before `BR-LOCAL-VERIFY-01`. A public legal page would be easier and would not prove app chrome. |
| migration_order | 0 parity map. 1 i18n foundation. 2 Home. 3 Annual. 4 Monthly. 5 Daily floating window (there is no Daily HTML page). 6 Insight. 7 PL / MEP. 8 Profile / Settings / Subscription (skip dummy plan details and construction session management until those pages are real). 9 Setup dialog / Registration / Login. 10 Legal and remaining public pages. 11 Retire legacy locale HTML. Order stands. Do not start at Annual. |
| no_big_bang | Never convert all pages at once. Each migrated group must reach local verified, 3-language parity, automated smoke, human visual approval where judgment is required, production deploy, and a stable period before the next group. |
| spanish_gate | Do not add Spanish as a fourth duplicated HTML tree. Spanish is the first new language added through this architecture, and only after the v2 baseline exists. |
| future_languages | Candidates only, not prioritized: Spanish, French, Italian, Thai, Indonesian, Malay, additional Chinese markets where appropriate. Adding a language must mean adding locale resources, not copying the application. |
| relation | `BR-LOCAL-VERIFY-01` is the prerequisite. Then this task. Then ES and later locales. Stripe may proceed in parallel; local verification also protects that release. |
| next_action | REGISTER ONLY. Do not start the parity map or any HTML consolidation until `BR-LOCAL-VERIFY-01` has a reviewed baseline and Case + Shin approve this task. |
| constraint | no HTML merge; no locale dictionary; no Spanish; no Stripe; no runtime change in this registration |

### PROFILE-PERSISTENCE-01

| Field | Value |
|-------|-------|
| id | `PROFILE-PERSISTENCE-01` |
| name | Profile Source of Truth Audit |
| parent | none (coordination track; does not reopen `TRUNK-06`) |
| status | AUDIT COMPLETE (2026-10-07) |
| priority | P1 SETUP READINESS ISSUE |
| started_at | 2026-10-07 |
| return_to | `PROFILE-PERSISTENCE-02` (COMMITTED AND PUSHED; deploy and smoke remain) |
| finding | “Profile is entirely localStorage-only” is false. `kpi_user_profiles` / `profile.php` already stores the main profile fields. No new profile table is required. Opening Date is server-canonical at `store.meta.openingDate`. Business Type exists in both profile storage and `store.meta.businessType`; `store.meta.businessType` is the current canonical path. Profile display pages still read browser-local data and do not hydrate from `profile.php`. Profile edit writes the local cache before server persistence is confirmed, so a server save failure can still look like success. Timezone and KPI Focus remain local-only. Required Initial Setup fields are substantially server-backed, so multi-device Initial Setup readiness is not fundamentally broken. Multi-device Profile display and edit consistency still needs improvement. |
| next_action | None on this node. The audit stays complete. Implementation lives on `PROFILE-PERSISTENCE-02`. |
| constraint | audit only; no code; no new table; no commit of product code in the audit session |

### PROFILE-PERSISTENCE-02

| Field | Value |
|-------|-------|
| id | `PROFILE-PERSISTENCE-02` |
| name | Server-First Profile Hydration & Save Integrity |
| parent | `PROFILE-PERSISTENCE-01` |
| status | COMMITTED AND PUSHED (2026-10-07) |
| priority | P1 |
| started_at | 2026-10-07 |
| commit | `5b265a0a998345ef9ce541824ac414921b4a39bf` |
| return_to | `PROFILE-PERSISTENCE-01` |
| depends_on | `PROFILE-PERSISTENCE-01` AUDIT COMPLETE |
| scope | Profile display pages hydrate from the authenticated server profile. Save order: validate, server write, server success, local cache update, then navigate or update the UI. A server save failure is not success. Keep `store.meta.businessType` canonical and `profile.business_type` a synchronized copy. Do not create a second source of truth. Preserve existing account data. Multi-device and fresh-browser smoke is required. |
| next_action | In production. The fresh-browser direct-entry gap found by `PROFILE-PERSISTENCE-03` is fixed and verified by `PROFILE-PERSISTENCE-04`. |
| constraint | implementation is already committed; this registration does not change product code or deploy |

### PROFILE-PERSISTENCE-03

| Field | Value |
|-------|-------|
| id | `PROFILE-PERSISTENCE-03` |
| name | Production Profile Smoke |
| parent | `PROFILE-PERSISTENCE-02` |
| status | PARTIAL / FAIL — superseded by `PROFILE-PERSISTENCE-04` |
| priority | P0 at the time of the smoke |
| started_at | 2026-10-08 |
| finding | Production deploy of `5b265a0` succeeded. A fresh browser that opened Profile Edit directly could not save. Store sync was enabled only after Annual or MEP. `profile.php` was not called. The form stayed on screen and the server profile stayed empty. |
| next_action | None. The blocker is fixed and verified by `PROFILE-PERSISTENCE-04`. |

### PROFILE-PERSISTENCE-04

| Field | Value |
|-------|-------|
| id | `PROFILE-PERSISTENCE-04` |
| name | Fresh-Browser Profile Store Bootstrap |
| parent | `PROFILE-PERSISTENCE-03` |
| status | VERIFIED IN PRODUCTION / COMPLETE (2026-10-08) |
| priority | BLOCKER, resolved |
| started_at | 2026-10-08 |
| commit | `0edce9ea51ce90616f00748995f007679154ff10` |
| scope | Profile display and edit initialize the existing authenticated session store sync. No Annual or MEP visit is required first. Canonical Business Type is written before the profile copy. Cache and navigation happen only after server success. |
| verification | Fresh browser on `kpn_full_authorized00`: direct Profile Edit save, store PUT, profile POST, display, reopen, second fresh browser restore, and profile-cache clear all passed. Opening Date stayed empty and readiness stayed incomplete, matching `store.meta.openingDate`. Mac cross-device check was not run. |
| next_action | None on this node. |
| constraint | registration lock and Stripe configuration were not changed |

### TUTORIAL-FA-01

| Field | Value |
|-------|-------|
| id | `TUTORIAL-FA-01` |
| name | Full Authorized Tutorial Production |
| parent | none (production support; does not reopen `TRUNK-06`) |
| status | IN PREPARATION |
| priority | not a code task |
| started_at | registered 2026-10-07 |
| return_to | none |
| purpose | About five short setup and tutorial videos for Full Authorized evaluator accounts. Target narrative: Forge Bistro Demo. |
| sequence | #01 Profile / Initial Setup. #02 Past Sales import. #03 Current-year data and setup. #04 Annual Target. #05 Reading and using KPN. The exact sequence may be refined later. |
| dependency | Profile / Initial Setup recording is UNBLOCKED. `PROFILE-PERSISTENCE-04` is verified in production. Mac cross-device recording remains optional follow-up. Work that may continue: tutorial account preparation, narration and script, shot list, demo CSV and data, titles and captions, DaVinci template, intro and outro. |
| workstation | Mac, under the 2026-10-07 read-only inspection policy. |
| next_action | IN PREPARATION. Do not edit KPN source from Mac. |
| constraint | no product-code change; no Mac commit, push, branch, merge, rebase, or deploy |

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
| `BR-LAUNCH-09` | Account Security & Destructive Actions | ACTIVE | P0 | Launch readiness |
| `BR-POST-XLSX-REPORT` | True XLSX / PL Report Export | POST-LAUNCH / DEFERRED | HIGH | `TRUNK-06` |
| `BR-POST-BOOKING-ICON-COLOR` | Booking Icon Office Mode Color | CLOSED | P2 | post-launch (do not reopen `TRUNK-06`) |
| `BR-POST-FOOTER-VERSION` | Footer Version Display | CLOSED | P2 | post-launch (do not reopen `TRUNK-06`) |
| `BR-POST-COCKPIT-GAP` | Cockpit Annual Target / Business Day gap | CLOSED | P2 | post-launch (do not reopen `TRUNK-06`) |
| `BR-POST-HOME-01` | KPN Home / Simple Mode | PRODUCTION VERIFIED / CLOSED | P1 | post-launch (do not reopen `TRUNK-06`) |
| `BR-POST-HOME-02` | Home / Simple Mode Redesign | PRODUCTION VERIFIED / CLOSED | P1 | post-launch (do not reopen `TRUNK-06`) |
| `BR-POST-PROGRESS-SCALE-01` | Dynamic Progress Bar Scale | DEFERRED / POST-LAUNCH / REDESIGN | not raised | post-launch (do not reopen `TRUNK-06`) |
| `BR-POST-PACE-ALERT-01` | Business-day vs Sales Pace Alert Visual Contract | DEFERRED / POST-LAUNCH / REDESIGN | not raised | post-launch (do not reopen `TRUNK-06`) |
| `BR-LOCAL-VERIFY-01` | Full Local Verification Environment | CLOSED (2026-10-04). Phase 4 LOCAL MYSQL VERIFIED / CLOSED | CRITICAL / HIGH | none (infrastructure; CURRENT PATH unchanged) |
| `BR-I18N-ARCH-01` | Localization Architecture v2 | REGISTERED — implementation not started | HIGH | prerequisite `BR-LOCAL-VERIFY-01` |
| `PROFILE-PERSISTENCE-01` | Profile Source of Truth Audit | AUDIT COMPLETE (2026-10-07) | P1 SETUP READINESS ISSUE | none (coordination track) |
| `PROFILE-PERSISTENCE-02` | Server-First Profile Hydration & Save Integrity | COMMITTED AND PUSHED (`5b265a0`); fresh-browser gap closed by `PROFILE-PERSISTENCE-04` | P1 | `PROFILE-PERSISTENCE-01` |
| `PROFILE-PERSISTENCE-03` | Production Profile Smoke | PARTIAL / FAIL — superseded | P0 at smoke time | `PROFILE-PERSISTENCE-02` |
| `PROFILE-PERSISTENCE-04` | Fresh-Browser Profile Store Bootstrap | VERIFIED IN PRODUCTION / COMPLETE (`0edce9e`) | BLOCKER, resolved | `PROFILE-PERSISTENCE-03` |
| `TUTORIAL-FA-01` | Full Authorized Tutorial Production | IN PREPARATION; Profile / Initial Setup recording UNBLOCKED | not a code task | `PROFILE-PERSISTENCE-04` |

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
ACTIVE (outside `TRUNK-06` closeout): `BR-LAUNCH-05` (Phase 2 CLOSED; Phase 3 ACTIVE — BLOCKED on client IP), `BR-LAUNCH-09` (Phase 0 / 1 / 2 CLOSED; Phase 3A READY FOR HUMAN SMOKE; Phase 3B BLOCKED — Stripe / Billing contract required)  
DEFERRED under `TRUNK-06`: `BR-POST-XLSX-REPORT`  
CLOSED post-launch (do not reopen `TRUNK-06`): `BR-POST-BOOKING-ICON-COLOR`, `BR-POST-FOOTER-VERSION`, `BR-POST-COCKPIT-GAP`, `BR-POST-HOME-01`, `BR-POST-HOME-02`  
DEFERRED UX: `BR-UI-PL-EXPENSE-CLASSIFY-TOOLTIPS` (parent `BR-LAUNCH-01-C2`, P2), `BR-UI-PL-INSIGHT-FIRSTOPEN-PERF`  
PRODUCTION VERIFIED / CLOSED (not the active path): `BR-POST-HOME-01` (KPN Home / Simple Mode, P1. Revision `3c8ec2598843bd07d524ac1642094007893ba2a3`. 78 runtime files. CURRENT PATH unchanged.) `BR-POST-HOME-02` (Home / Simple Mode Redesign, P1. Production commit `305924ee4afdcf6f62d52669a654f86bdd567ad3`. 2026-10-03. CURRENT PATH unchanged.)  
DEFERRED importer (not Launch blockers): `BR-LAUNCH-01-C2-L6-A`, Horizontal parser, Mixed parser, advanced date inference, Preview expansion, `BR-POST-EXPENSE-LEDGER`  
DEFERRED post-launch REDESIGN (do not start): `BR-POST-PROGRESS-SCALE-01`, `BR-POST-PACE-ALERT-01`  
`BR-LOCAL-VERIFY-01` is CLOSED (2026-10-04). Phase 1 and Phase 2 are LOCAL VERIFIED / CLOSED. Phase 3 is REAL MYSQL VERIFIED / CLOSED. Phase 4 is LOCAL MYSQL VERIFIED / CLOSED: user-facing 122 / 122 (executed 123, supplemental 1) and Admin 5 / 5. `BR-I18N-ARCH-01` is not started. Spanish is not a fourth HTML tree. Stripe may proceed in parallel. CURRENT PATH unchanged.

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
| 2026-09-25 | **BR-POST-BOOKING-ICON-COLOR START** Office booking icon `#fff`. Root: `<img>` → `images/booking_office.svg` `fill="#000000"`. `currentColor` not applicable. Do not reopen `TRUNK-06`. |
| 2026-09-25 | **BR-POST-BOOKING-ICON-COLOR CLOSED** Office SVG fill `#ffffff`. Sci-Fi `#59e1f3` unchanged. Production smoke 30/30 PASS. SHA `414b164`. Human Review NO. Do not reopen `TRUNK-06`. Do not auto-start `BR-LAUNCH-05`. |
| 2026-09-26 | **BR-POST-FOOTER-VERSION CLOSED** Shared footer brand: Key Performance Navigator / Version 1.0.0 / © 2025 Forge Laboratory. SHA `900bfc3`. |
| 2026-09-26 | **BR-POST-COCKPIT-GAP CLOSED** Shared Cockpit box gap Sci-Fi 30px / Office 17px (EN reference). JP/ZH-TW match EN. Production 48/48 PASS. SHA `deabb85`. Human Review NO. Do not reopen `TRUNK-06`. |
| 2026-09-27 | **BR-ONBOARDING-01 Phase 3 ACTIVE** STEP 02 Historical Data: summary + recommendation from canonical dailySales, existing Past Sales importer bridge, light skip (historicalSkipped only), done card before unbuilt STEP 03, Annual resume button / `?kpnSetup=1`, Step 01 starts `store.meta.setup`. `7937a9e` deployed (8 files, SHA match). Smoke 235/235 local + prod assets; regressions green; production 00 15/15 then reset. Verdict `PHASE 3 READY TO CLOSE`. Phase 4 not started. |
| 2026-09-27 | **BR-ONBOARDING-01 Phase 3 CLOSED** Shin approved production verification, smoke, regressions, activeSetup / Historical / Importer reuse / Skip contracts. |
| 2026-09-27 | **BR-POST-SETUP-EXTRA-PUT registered** P2. One extra store PUT seen during Initial Setup in production (Phase 3, again in Phase 4). Investigate source / redundancy / OCC impact later; not a Launch blocker; not fixed in Phase 4. |
| 2026-09-27 | **BR-ONBOARDING-01 Phase 4 ACTIVE** STEP 03 Current Year: current-year summary from canonical dailySales (range max(opening, Jan 1)..today, detected / positive days, present / none / new business / invalid), explicit acknowledge (currentYearAcknowledged only), existing Sales Data importer bridge, STEP 02 continues into STEP 03, resume to STEP 03, done card before unbuilt STEP 04. `4a3dbc5` deployed (8 files, SHA match). Smoke 225/225 local + prod assets; regressions green; production 00 17/17 then reset. Verdict `PHASE 4 READY TO CLOSE`. Phase 5 not started. |
| 2026-09-27 | **BR-ONBOARDING-01 Phase 4 CLOSED** Shin approved STEP 03 and its 4 decisions (STEP 02 -> STEP 03 direct, Sales Data reuse, future opening date blocked, operatingYear ahead blocked). |
| 2026-09-27 | **BR-ONBOARDING-01 Phase 5 ACTIVE** STEP 04 Annual Target: summary (sales-data-save target for operatingYear, rollover / heal = not set), targetAcknowledged-only acknowledge incl. continue-without-target with light confirm, existing Sales Data target input, STEP 03 continues into STEP 04, resume to STEP 04 / done card before unbuilt STEP 05, Planning Readiness unchanged and coexisting. `6696849` deployed (8 files, SHA match). Smoke 276/276 local + prod assets; regressions green; production 00 verified then reset. Verdict `PHASE 5 READY TO CLOSE`. Phase 6 not started. |
| 2026-09-27 | **BR-ONBOARDING-01 Phase 5 CLOSED** Shin approved STEP 04 Annual Target. |
| 2026-09-27 | **BR-ONBOARDING-01 Phase 6 CLOSED** STEP 05 Review / Setup Complete: completion contract (Hard 7 + historical resolved + current year / target acknowledged) re-checked before Review and on Complete, routing to the first unresolved step; Review summary + non-blocking warnings; explicit-only `setup.complete = true` keeping other setup fields, OCC-safe (409 re-check, failure revert, double-click safe); completion card; NORMAL by setupComplete after reload; Planning Readiness coexists. `e11a327` deployed (8 files, SHA match). Smoke 225/225 local + prod assets; regressions green; production 00 16/16 then reset. Human Smoke NOT REQUIRED. **Initial Setup IMPLEMENTED / PRODUCTION VERIFIED.** |
| 2026-09-27 | **BR-ONBOARDING-01-R2 CLOSED** d6dced6 residual store contracts ported (no revert): saved target source + memory heal, Sales Data edit right, 3 business-day layers, A/B sync, light key, background Busy off. `fabd406` / `335d6af` deployed (9 pages, SHA match). Smoke 165/165, R1 171/171, Step 0 329/329; production 00 7/7 then reset. `PHASE 3 SAFE TO PROCEED` (not started). |
| 2026-09-27 | **Construction State baseline recorded.** Future unfinished full pages default to scramble placeholder unless a documented exception. Spec: `docs/kpn-construction-state.md`. Task Tree §3 Operating Rule. No product-code change. |
| 2026-09-28 | **BR-LAUNCH-05 Phase 0 audit** Registration -> Initial Setup contract audit (audit only). Commit `5072b38`. |
| 2026-09-28 | **BR-LAUNCH-05 Phase 0 Freeze / Phase 1 done** Freeze: consent server record required, Basic fixed, abuse protection required, server `registrationEnabled` single source, Registration vs STEP 01 split. Phase 1 Registration UI simplification JP / EN / ZH-TW x Sci-Fi / Office. `6994e30` deployed (6 files, SHA match). Smoke 83/83 local + production assets; regressions green. P0 = 0, P1 = 0. Registered `BR-LAUNCH-05-EMAIL-VERIFY` (separate) and `BR-LAUNCH-05-REG-SESSION` (P2). Phase 2 not started. |
| 2026-09-28 | **BR-LAUNCH-05 Phase 1 CLOSED / Phase 2 deployed** Consent table `kpi_user_consents` (append-only, transaction with user), `registration-status.php` + fail-closed UI, IP / email rate limit, honeypot, min submit time, `?v=` cache-bust JP / EN / ZH-TW, ZH generator strict. `5a3267e` + `e9e8cc2` deployed (10 files, SHA match). Production GET 30/30; smokes green. `registrationEnabled` stays false. Consent table not applied to production DB (Phase 3 prerequisite). P0 = 0, P1 = 0. Phase 3 not started. |
| 2026-09-28 | **BR-LAUNCH-05 Phase 2 CLOSED / Phase 3 ACTIVE (BLOCKED)** Consent SQL safe (CREATE TABLE only); production MySQL 8.4.8 FK-compatible; table not applied yet. Client IP audit: REMOTE_ADDR spoofable via client `CF-Connecting-IP` / `X-Real-IP` (P1, IP rate limit bypass); no hosting contract. zh-tw register success message + duplicate var fixed via generator (`4bca49d`, 2 files deployed). `registrationEnabled` stays false. |
| 2026-09-28 | **BR-LAUNCH-05 Phase 3 Plan CTA** Basic CTA follows registration-status (Early Access by default / on failure; Pro unchanged). `0e6ee18` deployed (4 files). Client IP: Shin asks ConoHa support; no code change; still BLOCKED. `registrationEnabled` stays false. |
| 2026-09-28 | **BR-LAUNCH-05 Phase 3 Gate A done** Shin applied `schema_kpi_user_consents.add.sql`. Read-only verification: table InnoDB utf8mb4_unicode_ci; id BIGINT UNSIGNED AI, user_id VARCHAR(64), terms_version / privacy_version / source VARCHAR(32), accepted_at DATETIME, all NOT NULL; PRIMARY + `idx_kpi_user_consents_user_accepted`; `fk_kpi_user_consents_user` -> `kpi_users.user_id` CASCADE; 0 rows; `kpi_users` columns / row count unchanged. Still BLOCKED on client IP. `registrationEnabled` false. |
| 2026-09-28 | **BR-LAUNCH-09 REGISTER / Phase 0 CLOSED** Account Security & Destructive Actions (09 because 06 is the CLOSED PL Excel task). Audit: Delete / Password / Email flows are UI mocks live in production. Gate 0: production `allowSelfPlanChange` false (no-session POST `set-plan.php` 403). Shin: real server-side processing, one phase at a time. |
| 2026-09-28 | **BR-LAUNCH-09 Phase 1 deployed** Password Change: `change-password.php` (current password, registration rule, same password rejected, transaction + revoke epoch, new session ID), UI JP / EN / ZH-TW x Sci-Fi / Office, plaintext `kpi-auth-password` removed. `067c51e` deployed (13 files, SHA match). Smokes: contract 50/50, local 161/161, registration 86/86, production 36/36 + 33/33. No production password changed. `registrationEnabled` false. Phase 2 not started. |
| 2026-09-28 | **BR-LAUNCH-09 Phase 1 CLOSED / Phase 2 GO** Shin approved Password Change (Launch blocker resolved). Phase 2 Email Change started. Phase 3 not started. |
| 2026-09-28 | **BR-LAUNCH-09 Phase 2 deployed** Email Change: `request-email-change.php` + `confirm-email-change.php` (current password, normalize, duplicate, 6-digit code to the new address, 30 min, 5 attempts, cooldown + hourly cap, re-check at confirm, other sessions revoked, new session ID, old-address notice), file-backed pending (no schema), UI JP / EN / ZH-TW x Sci-Fi / Office, hardcoded password value removed. `54c37d5` deployed (8 files, SHA match). Smokes: contract 59/59, local 238/238, Phase 1 161/161, registration 86/86, production 35/35. No production email changed. Phase 3 not started. |
| 2026-09-28 | **BR-LAUNCH-09 Phase 2 CLOSED / Phase 3 GO** Email Change production Human Smoke PASS (code to new address, old email login fails, new email login OK, Annual OK). P1 observation: old-address notice not confirmed. Phase 3 Delete Account started (contract audit first). |
| 2026-09-28 | **BR-LAUNCH-09 Phase 3 BLOCKED** Delete Account contract audit done (existing flow fake end-to-end). Frozen: user-role only, reject if children, feedback anonymized, 5 real steps with server-verified password + delete intent, completion page without reason form, revoke tombstone kept. BLOCKED — consent retention policy decision required. No code changes. |
| 2026-09-28 | **BR-LAUNCH-09 Phase 3 consent decided / implemented** Shin: Delete everything (consents cascade with the account; no schema change). Delete Account implemented per freeze; local smoke 254/254 + regressions green. Waiting for Delete Account Human Smoke (`funkizm@mac.com` only). |
| 2026-09-28 | **BR-LAUNCH-09 Phase 3 split** 3A Basic Account Delete = IMPLEMENTED / READY FOR HUMAN SMOKE. 3B Paid / Stripe Account Delete = BLOCKED — Stripe / Billing contract required (14 close requirements in `phase3_split_2026-09-28`). Phase 3 Final Close only after both. No code changes. |
| 2026-09-29 | **BR-LAUNCH-09 Phase 3A Extension audit** Account Lifecycle / Deleted Accounts History direction frozen by Shin; Delete Account Human Smoke paused (`funkizm@mac.com` kept). Audit: Founder console, schema, HMAC key storage, Privacy Policy, delete transaction, churn denominator. Decisions pending. No code changes. |
| 2026-09-29 | **BR-LAUNCH-09 Lifecycle L1 draft / churn freeze** Privacy Policy JP / EN / ZH-TW draft + STEP 2 draft copy (`docs/br-launch-09-lifecycle-l1-draft.md`, retention `TBD — legal review pending`). Monthly Churn = Standalone Customer Account Churn (JST, Early Churn separate, child separate, disabled in denominator). Production unchanged; Lifecycle HOLD. |
| 2026-09-29 | **BR-LAUNCH-09 Lifecycle retention decided** 3 years after account deletion (automatic purge), same in JP / EN / ZH-TW; L1 final draft updated. Waiting for Shin final approval; L2 not started. Production unchanged. |
| 2026-09-29 | **BR-LAUNCH-09 Lifecycle L1 CLOSED / L2 GO** Privacy §6 feedback (text / date / category only) + support mailbox wording added (JP / EN / ZH-TW), STEP 2 aligned; version / last updated = L4 production deploy date. L2 implementation started. |
| 2026-09-29 | **BR-LAUNCH-09 Lifecycle L2 implemented (local)** `_lifecycle.php`, same-transaction history row, fail closed, 3-year purge, NEW / RETURNED, feedback plan / page blanked, schema + migration, STEP 2 copy. Local smoke 341/341, lifecycle contract 29/29, regressions green. Not deployed. |
| 2026-09-29 | **BR-LAUNCH-09 Lifecycle L3 implemented (local)** Founder Deleted Accounts page (email lookup, history row delete, exclude), Dashboard lifecycle metrics (frozen JST churn), Users Origin / Exclude. UI contract 71/71, local smoke 121/121, L2 regression 341/341. Not deployed; L4 waits for GO. |
| 2026-09-29 | **BR-LAUNCH-09 Lifecycle L3 CLOSED / L4 GO** Privacy Policy lifecycle text (JP / EN / ZH-TW) + `KPI_PRIVACY_VERSION` prepared for the deploy date; production pre-check read-only. |
| 2026-09-29 | **BR-LAUNCH-09 Lifecycle L4 production** Migration (2 tables), HMAC key `k1` in production config, deploy `f191ea3` (24 files), Privacy 2026-09-29; read-only diag + static verify 32/32. READY FOR LIFECYCLE DELETE HUMAN SMOKE (Shin GO pending). `registrationEnabled` false. |
| 2026-09-29 | **BR-LAUNCH-05 ConoHa answer** Trusted real client IP not obtainable (no trusted header contract, no unspoofable source IP). `REMOTE_ADDR` retired as the security boundary; IP-independent abuse protection redesign audited, waiting for Shin decisions. `registrationEnabled` false. |
| 2026-09-29 | **BR-LAUNCH-05 redesign implemented (local)** Forwarded-header reject (`CF-Connecting-IP` / `X-Real-IP`), global limiter (attempts 30 / 10 min, creations 10 / h + 40 / 24 h), IP limiter auxiliary. Contract 73/73, server smoke new checks green, production header probe OK (real Chrome sends neither header). Not deployed. |
| 2026-09-29 | **BR-LAUNCH-05 redesign deployed** `09f4711` (2 api files). Production verify 16/16; emergency gate 403 kept; `registrationEnabled` false. |
| 2026-09-29 | **BR-LAUNCH-05 Controlled Registration Smoke PASS** Registration open ~18 s, one test account (basic / user, 1 consent), header rejects + duplicate 409 on production, Login → Annual → Setup STEP 01. Back to false. READY TO ENABLE PUBLIC REGISTRATION (permanent enable waits for Shin GO). |
| 2026-09-29 | **BR-LAUNCH-05 PUBLIC REGISTRATION ENABLED / PRODUCTION VERIFIED** Test account excluded from metrics; `registrationEnabled` true (status true after 3 s); verify 19/19, no account created. `BR-LAUNCH-05-EMAIL-VERIFY` stays post-launch. |
| 2026-09-30 | **BR-POST-HOME-01 registered** KPN Home / Simple Mode. DEFERRED / POST-LAUNCH P1. First Action H1 Global Menu / Home Entry Pre-Implementation Audit. No implementation. |
| 2026-09-30 | **BR-POST-HOME-01 H1 DONE / REVIEWED; H2 DESIGN APPROVED / NOT IMPLEMENTED.** Design note [`docs/br-post-home-01.md`](./br-post-home-01.md). Next: H3 Shared Reference Date Architecture Audit (NOT STARTED). H4 NOT STARTED. REGISTER ONLY. CURRENT PATH unchanged. No implementation. |
| 2026-09-30 | **BR-POST-HOME-01 H3 DONE / REVIEWED.** Canonical date stays `kpiNavigator.annualNav.selectedIso`. Opening preference v1 default Yesterday (user may choose Today). Explicit `?iso=` wins. New login does not restore a distant previous `selectedIso`. PL comparison Deferred. Next: H4 NOT STARTED, blocked on Shin GO. REGISTER ONLY. CURRENT PATH unchanged. No implementation. |
| 2026-10-01 | **BR-POST-HOME-01 IMPLEMENTATION COMPLETE / VALIDATION COMPLETE / PRODUCTION DEPLOY PENDING.** H1–H3 DONE. H4-A through H4-H DONE / VERIFIED. H4-H technical blockers = 0. HEAD `37702722b1b88bbd4b51d5e85cb44ff3ec739e82`. Not deployed. Not PRODUCTION VERIFIED. CURRENT PATH unchanged. |
| 2026-10-01 | **BR-POST-HOME-01 PRODUCTION VERIFIED / CLOSED.** Deployed revision `3c8ec2598843bd07d524ac1642094007893ba2a3`. 78 runtime files. JP / EN / ZH-TW, Sci-Fi / Office, Global Menu, Shared Reference Date, Daily CTA, Opening Date Preference, auth login / logout / re-login, rebuild POST = 0, 1200px. No Infinity / NaN. Production errors none. CURRENT PATH unchanged. Home is not the active path. |
| 2026-10-02 | **BR-POST-PROGRESS-SCALE-01** and **BR-POST-PACE-ALERT-01** registered. Both DEFERRED / POST-LAUNCH / REDESIGN. Priority not raised. CURRENT PATH unchanged. Home status not changed. Sales Progress dynamic scale: evidence not found (`e69ada5`). Seasonality dynamic scale remains `getSeasonalityChartScale` (`9ef8dba`). Home pace warning remains `5e7dd63`. No implementation. |
| 2026-10-02 | **BR-POST-HOME-02 registered** Home / Simple Mode Redesign. DEFERRED / POST-LAUNCH / P1 / REGISTER ONLY. Design note [`docs/br-post-home-02.md`](./br-post-home-02.md). H2-1 not started. `BR-POST-HOME-01` stays PRODUCTION VERIFIED / CLOSED. CURRENT PATH unchanged. No implementation. |
| 2026-10-03 | **BR-POST-HOME-02 PRODUCTION VERIFIED / CLOSED.** Production commit `305924ee4afdcf6f62d52669a654f86bdd567ad3`. Runtime files: `app/home/home-shell.css`, `app/home/index.html`, `en/app/home/index.html`, `zh-tw/app/home/index.html`. JP / EN / ZH-TW × Sci-Fi / Office at 1200px PASS. `kpi-navigator/favicon.ico` 404 was not a pageerror. CURRENT PATH unchanged. Home is not the active path. |
| 2026-10-03 | **BR-LOCAL-VERIFY-01 and BR-I18N-ARCH-01 REGISTERED.** Phase 0 local-verification audit recorded in the `BR-LOCAL-VERIFY-01` node. Implementation not started. Home remains the intended first i18n pilot after that baseline. Spanish is not a fourth HTML tree. UI locale and billing region stay separate. CURRENT PATH unchanged. Docs only. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 3 named, not started.** Local MySQL Parity. localTestMode may later use MySQL only for localhost / 127.0.0.1 / an approved local container and a dedicated DB name such as `kpn_local_test`. Production host, name, and detectable credentials are rejected. Phase 1 remains PARTIAL, not closed. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 1 LOCAL VERIFIED.** Basic Home no longer uses `guardProPage`. Unresolved client plan does not grant Pro. Server `legacyPlan` resolution is unchanged. Parent task stays open. Phase 3 Local MySQL is not started. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 1 LOCAL VERIFIED / CLOSED.** Parent stays ACTIVE / MAINTAINED. Phase 2 Canonical Fixtures, Phase 3 Local MySQL, localization v2, and Stripe are not started. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 2 Canonical Fixtures v1 IMPLEMENTED / AWAITING CASE REVIEW.** Manifest `fixtures/local/canonical/manifest.json`. Six accounts, four business-type cases, fixed clock, sentinel reset. Parent stays ACTIVE / MAINTAINED. Phase 3 Local MySQL is not started. Not closed. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 2 Canonical Fixtures v1 IMPLEMENTED / LOCAL VERIFIED / CLOSED.** Case approved. Parent stays ACTIVE / MAINTAINED. Phase 3 Local MySQL stays UNSTARTED. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 3A Local MySQL runtime foundation implemented in the working tree.** Guard allows MySQL only for loopback plus exact `kpn_local_test`. Not committed. Phase 3B not started. Parent stays ACTIVE / MAINTAINED. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 3A IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED.** Case approved. Runtime identity is `kpn_local_runtime` with DML only on `kpn_local_test`. Parent stays ACTIVE / MAINTAINED. Phase 3 overall stays open. Phase 3B is NEXT / UNSTARTED. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 3B IMPLEMENTED / REAL MYSQL VERIFIED in the working tree.** Five canonical accounts seeded into `kpn_local_test` from the manifest. `fx-legacy-pro` stays file-only. Not CLOSED. Not committed. Full page smoke is not started. Parent stays ACTIVE / MAINTAINED. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 Phase 3B IMPLEMENTED / REAL MYSQL VERIFIED / CLOSED.** Case approved. Phase 3 Local MySQL Parity is CLOSED. Parent stays ACTIVE / MAINTAINED. Phase 4 Full Page Smoke is NEXT / UNSTARTED. CURRENT PATH unchanged. |
| 2026-10-04 | **BR-LOCAL-VERIFY-01 CLOSED.** Phase 4 Full Page Smoke is LOCAL MYSQL VERIFIED / CLOSED. User-facing contract 122 / 122 (executed 123, supplemental 1). Admin 5 / 5, with normal-user HTTP 403. Local Founder `localfounder1` is smoke-only. CURRENT PATH unchanged. |
| 2026-10-07 | **TASK-TREE-PROFILE-TUTORIAL-01.** Registered `PROFILE-PERSISTENCE-01` AUDIT COMPLETE (P1; profile is not local-only), `PROFILE-PERSISTENCE-02` PENDING, and `TUTORIAL-FA-01` IN PREPARATION. Stripe track noted as `STRIPE-LIVE-07` RUNBOOK READY, blocked on Live access. Mac is tutorial production / read-only. Windows remains canonical development. Docs only. No product implementation. |
| 2026-10-08 | **TASK-TREE-AUDIT-FIRST-01.** Registered standing rule `BR-AUDIT-FIRST` under Operating Rule. Updated `PROFILE-PERSISTENCE-02` to COMMITTED AND PUSHED `5b265a0`, with production deploy and multi-device smoke still required before Tutorial Profile recording. `PROFILE-PERSISTENCE-01` stays AUDIT COMPLETE. `TUTORIAL-FA-01` stays IN PREPARATION. `STRIPE-LIVE-07` stays RUNBOOK READY, blocked on Live access. Docs only. No product implementation. |
| 2026-10-08 | **PROFILE-PERSISTENCE-04.** Fresh-browser direct Profile save is verified in production at `0edce9e`. `PROFILE-PERSISTENCE-03` stays the recorded smoke failure and is superseded. Profile / Initial Setup recording on `TUTORIAL-FA-01` is UNBLOCKED. This task-tree note is not part of the product commit. |

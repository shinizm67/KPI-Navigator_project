# BR-POST-HOME-01 — KPN Home / Simple Mode

Status: **IMPLEMENTATION COMPLETE / VALIDATION COMPLETE / PRODUCTION DEPLOY PENDING**  
Parent: post-launch (do not reopen `TRUNK-06`)  
Registered: 2026-09-30 (Shin)  
Validation close: 2026-10-01  
HEAD: `37702722b1b88bbd4b51d5e85cb44ff3ec739e82`

Home v1 is implemented and validated. It is not deployed, and it is not PRODUCTION VERIFIED. CURRENT PATH is unchanged.

Home v1 principle: **Do not redesign. Recompose.**

Upper half = Current Position.  
Lower half = What is required to reach the goal.  
Progress comparison = Is sales keeping pace with operating time?

---

## Task tree

| id | name | status |
|----|------|--------|
| H1 | Global Menu / Home Entry Audit | **DONE** |
| H2 | Home Information Architecture / Window Contract | **DONE** |
| H3 | Shared Reference Date Architecture Audit | **DONE** |
| H4-A | Shared Reference Date Foundation | **DONE / VERIFIED** |
| H4-B | Home Shell / 3 Window Layout | **DONE / VERIFIED** |
| H4-C | Primary KPI / Data Binding | **DONE / VERIFIED** |
| H4-D | Expanded KPI / Progress | **DONE / VERIFIED** |
| H4-E | Global Menu / Site Chrome Integration | **DONE / VERIFIED** |
| H4-F1 | Daily CTA | **DONE / VERIFIED** |
| H4-F2 | Sales Progress Warning | **DONE / VERIFIED** |
| H4-G | Opening Date Preference UI | **DONE / VERIFIED** |
| H4-H | Pre-Deploy Validation | **DONE / VERIFIED** |

Technical blockers at close: 0. Production deploy is still pending.

---

## Close record (2026-10-01)

### Home structure

- Daily / Monthly / Annual.
- Three independent windows.
- 32px gap.
- Default collapsed.
- Multiple windows may stay expanded at the same time.

### Shared Reference Date

- Reuses `annualNav.selectedIso`.
- New login default is Yesterday.
- User preference is Today or Yesterday.
- The same authenticated login keeps the current reference date.
- Explicit `iso` or year-month takes precedence.

### Daily CTA

Home Daily CTA → locale-preserving Monthly → Daily FW → `?open=daily&iso=`.

### Warning

- gap = raw Business-day Progress − raw Sales Progress.
- Normal: gap < 10pt.
- Orange: gap >= 10pt and < 20pt.
- Red: gap >= 20pt.
- Sales Progress >= Business-day Progress is Normal.
- A negative Sales Progress is clamped to 0 for the warning calculation only.

### Rebuild safety

- Home automatic rebuild requires a complete boolean `businessDays` map for every day of the target year.
- Incomplete map → no POST.
- Existing facts → no POST.
- Leap years use 366 days.

### Opening Date Preference

- Key: `kpiNavigator.openingDatePreference`.
- Default: `yesterday`.
- v1 is localStorage.
- Server sync is deferred.

### Site chrome

- Home is formally integrated, before Annual.
- Logo stays 217×32.
- 1200px is supported.
- The site chrome generator preserves page-specific header scripts.
- Regeneration idempotence was verified.

### Validation evidence

PHP:

- Production PHP is 8.2.34.
- Portable PHP 8.2.34 was used for lint.
- `api/v1/_auth.php` PASS.
- `api/v1/auth/login.php` PASS.
- `api/v1/auth/register.php` PASS.

Real rebuild smoke, dedicated test account only:

- Baseline facts = 0.
- Rebuild POST once.
- Written = 365.
- Re-GET = 365.
- Home displayed those facts.
- A second rebuild POST did not happen.
- Cleanup / reset completed.

Integration:

- JP / EN / ZH-TW.
- Sci-Fi / Office.
- 1200px PASS.
- Home full integration smoke PASS.

### Remaining non-blockers / deferred

- Annual's existing rebuild logic is outside this Home guard.
- Opening Date Preference server sync is deferred.
- Settings pages without a CSS cache query remain non-blocking.
- Disabled smoke users remain, with KPI data reset.
- Future reconsideration: Home may eventually replace some Daily-page usage. That is not part of v1.

---

## H1 — Global Menu / Home Entry Pre-Implementation Audit

Status: **DONE / REVIEWED** (2026-09-30). Audit only. No code change.

Question: can Home be added to the left of Annual at the 1200px floor, in JP / EN / ZH-TW and Sci-Fi / Office, without shrinking the Forge Laboratory logo first.

Measured on local Annual at viewport 1200px (`header-inner` is `max-width: 1200px`, so a wider window does not add room inside the bar).

| Piece | Sci-Fi | Office |
|-------|--------|--------|
| header / inner | 1200 / 1200 | 1200 / 1200 |
| left padding | 24 | 24 |
| logo | 217×32, x=24 | same |
| logo-to-menu gap | JA 40; EN / ZH-TW 45.5 | 45.5 |
| menu gap | JA 24; EN / ZH-TW 20 | 20 (all langs) |
| each menu slot | JA 119.8; others 120 | 120 |
| actions reserve | padding-right 368 | 368 |
| actions width | 294.6–294.7 | 337–337.4 |
| last item to booking | 49.4–54.9 | **12.1–12.5** |
| wrap / page overflow | none | none |

Right-side visual order: booking 30, DL 46–48, gear 24, Mode (Sci-Fi ~141–143, Office 185), gaps 16px. Office Mode is wider, so the booking button sits closer to Insight. That 12px is the BR-LAUNCH-07 floor.

A fifth 120px slot plus one gap needs about **140px** (JA Sci-Fi gap 24px: 144px). Label width is not the constraint (Home / ホーム / 首頁 are about 23–41px). The widest existing label is EN Office Annual at 59.3px.

Inserting Home at the current 120px slot:

| Mode | Result |
|------|--------|
| Office, all languages | No wrap, no page overflow. Home overlaps the logo by **24.5px**. Insight overlaps booking by **57.5px**. |
| Sci-Fi | No overlap. Frames shrink to **91px (JA)** / **94px (EN / ZH-TW)** because Sci-Fi has `max-width: 120px` and no min-width. The 120px slot contract does not hold. |

Safe left budget (padding down by about 12px, logo-menu gap down by about 16px, existing center slack about 11px) is about 40px. That does not cover 140px. The Office 12px booking gap is not available.

Reviewed candidate, **not implemented**. Logo stays 217px. Actions and the 368px reserve stay.

| Knob | Now | Candidate |
|------|-----|-----------|
| left padding | 24 | **12** (logo x=24 → x=12) |
| header gap (logo to menu) | 40 | **24** |
| menu gap | 20 (JA Sci-Fi 24) | **12** |
| slot | 120 | **104**, with Sci-Fi min-width locked |

Measured with a DOM-only Home item: logo still 217×32 at x=12; logo-to-Home gap 29.5px; booking gap Sci-Fi ~55px and Office **12.1–12.5px** (same as today); overlap 0; no wrap. EN Office Annual 59.3px still fits in 104px. A 108px slot drops the Office booking gap to about 10px and breaks the 12px floor.

Keeping 120px slots and only tightening left spacing still misses the Office booking gap by about 30–50px. Logo shrink is not required for this candidate.

Language difference is the JA Sci-Fi page-local gap of 24px, plus EN text width. Office is the overlap gate.

Candidate files when implementation is allowed later (not edited in H1):

- `en/setting/style.css` (app header only; do not change `register/style.css` base padding, or login chrome moves)
- `scripts/site_chrome.py` (`build_header()`, Home left of Annual)
- `scripts/build_site_chrome.py`, `scripts/pl_chrome.py`
- Page-local Office `width: 120px !important` that can beat a shared slot change: `app/annual/index.html`, `app/monthly/index.html`, `app/profit/index.html`, `app/profit/pl/index.html`, `en/app/profit/pl/index.html`, `zh-tw/app/profit/pl/index.html`
- JA Sci-Fi `gap: 24px` in `app/annual/index.html` and `app/monthly/index.html` (a shared `!important` gap token beats it)

---

## H2 — Home Information Architecture / Window Contract

Status: **DONE** (design approved 2026-09-30, Shin; implemented and verified in H4).  
Purpose: Home v1 information architecture and interaction contract. The selected gap is 32px.

### Core principle

Home does not introduce a new visual language. Reuse existing KPN / Daily FW typography, colors, KPI presentation, date controls, progress bars, interactions and calculation logic wherever possible.

### Home structure

- Three independent Window Boxes arranged vertically:
  1. Daily
  2. Monthly
  3. Annual
- Windows are not one connected container.
- Each Window Box has visible black-background spacing between it and the next.
- Initial gap candidate: approximately 24–40px.
- Final gap must be selected by visual smoke at a 1200px viewport.
- Start around 32px; compare 24 / 32 / 40px if useful.
- Each Window expands downward independently.
- Expanding one Window pushes following Windows downward.
- Multiple Windows may remain expanded simultaneously.
- Default state: all collapsed.

### Window identity / header

- Each Window permanently displays its identity at upper left: Daily / Monthly / Annual.
- Identity remains visible in both collapsed and expanded states.
- Shared Reference Date is displayed as full YYYY/MM/DD + weekday in all three Windows.
- Monthly and Annual must not display only YYYY/MM or YYYY. Their KPI values are calculated as of the same exact reference date.

### Shared date behavior

- Daily / Monthly / Annual visually have their own date controls, but they operate on one KPN Shared Reference Date.
- Existing previous / next controls and long-press continuous navigation are reused.
- A reference-date change updates KPI values, progress bars, warnings and graphs together.
- The same reference date must ultimately synchronize with Home v1 date-aware areas: Home, Annual, Monthly, Daily / Daily FW, MEP, and Insight.
- During an active session, the selected reference date remains shared across KPN.
- New-session opening date preference: Today / Yesterday. v1 default is **Yesterday**. The user can switch to Today. Decided in H3.
- Explicit URL `?iso=` is an intentional cross-screen handoff and wins over the opening preference.
- Do not automatically restore a distant previously viewed `annualNav.selectedIso` as the initial date of a new login.

Architecture of that shared date is recorded in **H3**. It was implemented in H4-A and H4-G.

### Collapsed contract — common

Upper section represents: **CURRENT POSITION**.

Common primary KPI structure:

- Actual
- Target / Cumulative Target
- Difference
- Achievement %

Daily:

- Actual = selected day's sales
- Target = selected day's target

Monthly:

- Actual = month-to-reference-date cumulative sales
- Cumulative Target = month-to-reference-date cumulative target

Annual:

- Actual = year-to-reference-date cumulative sales
- Cumulative Target = year-to-reference-date cumulative target

### Expanded contract

Lower section represents: **WHAT IS REQUIRED TO REACH THE GOAL**.

Daily:

- Keep lighter than Monthly / Annual.
- Reuse only meaningful daily supplemental information from existing Daily FW.
- Avoid duplicate KPIs already visible in the collapsed area.
- Reuse the existing Daily progress bar where appropriate.

Monthly:

- Final Monthly Target
- Remaining Amount
- Business Days Left
- Required Sales / Remaining Business Day
- Business-day Progress
- Sales Progress
- Existing Monthly progress bar / graph
- Warning / tooltip area as needed

Annual:

- Final Annual Target
- Remaining Amount
- Business Days Left
- Required Sales / Remaining Business Day
- Business-day Progress
- Sales Progress
- Existing Annual progress bar / graph
- Warning / tooltip area as needed

### Progress comparison contract

For Monthly and Annual, progress order is fixed:

1. Business-day Progress
2. Sales Progress

Reason: Business-day Progress is the temporal baseline. Sales Progress follows beneath it so the user can immediately compare business performance against elapsed operating time.

This comparison is a Home-specific decision-support value: how much operating time has elapsed, and has sales performance kept pace?

### Window controls

- Bottom-left: Expand / Collapse
- Bottom-right: Detail CTA
- CTA remains at the Window's lower-right edge after expansion.

Detail destinations:

- Daily → View Daily Details → Annual / Daily context
- Monthly → View Monthly Details → Monthly
- Annual → View Annual Details → Annual

Navigation must preserve Shared Reference Date.

### Home does not provide

- Data editing
- PL editing
- MEP editing
- Detailed analysis
- Advanced drilldown
- Recent Date
- Pinned Date
- Planning Bookmark

Recent Date / Pinned Date / Planning Bookmark stay deferred. Do not add them to Home v1.

### Chrome

Existing Global Menu and Footer remain normal page chrome. Do not add a Home-specific Back-to-Top control. Use the existing Footer top-return control.

Global Menu geometry (Home to the left of Annual) was applied in H4-E. Logo stays 217×32.

---

## H3 — Shared Reference Date Architecture Audit

Status: **DONE** (audit reviewed 2026-09-30; foundation implemented in H4-A). The notes below are the audit record.

Screens are not fully independent. A shared cursor already exists. Daily FW, Insight, and PL comparison keep a local date that does not write that cursor back.

### Canonical date

- Keep `kpiNavigator.annualNav.selectedIso` as the Shared Reference Date.
- Do not create a new date store.
- `operatingYear` stays a separate concept. Do not change it. displayYear / `calendarYear` stay separate from operatingYear (`docs/display-vs-operating-year.md`).
- In-session writers that already use this cursor: Annual cockpit, Monthly cockpit, MEP open/push, graph date step, and Monthly vertical focus, via `KpiYearStore.setSelectedDate` / `window.__ANNUAL_UI.setDailyDateByISO`.
- `KpiYearStore` is copied inside Annual, Monthly, and MEP HTML (JA / EN / ZH-TW). The shared axis is the storage key and the server `annualNav` field, not one JS module.
- The server stores client `annualNav` JSON on the user blob (`api/v1/store.php`). A date move uses a nav-only PUT. PHP does not compute the reference date.

### Opening Date Preference

- Two choices: Today / Yesterday.
- v1 default is **Yesterday**.
- The user can change it to Today.

### Date precedence

1. Explicit URL `?iso=` is an intentional cross-screen date handoff and has highest priority.
2. During the same session, keep the Shared Reference Date.
3. On a new session with no explicit `iso`, apply the Opening Date Preference.
4. Do not automatically restore a distant `annualNav.selectedIso` from the previous session as the initial date of a new login.

### Home v1 integration targets

- Home
- Annual
- Monthly
- Daily / Daily FW
- MEP
- Insight

### Daily FW / Insight

Today they read the shared date only as the opening value. Previous / next, Today, the date picker, and long-press update a local `selectedIso` and do not write the canonical date. Closing the overlay drops that local date.

At implementation time, wire previous / next, Today, picker, and long-press onto the Shared Reference Date write path (`setDailyDateByISO` / `setSelectedDate`).

### PL comparison

PL comparison keeps its own date context (`selectedIso`, hash `#insight=areaN&date=`, `localStorage` `kpiNavigator.plInsightLast`). It does not read `annualNav`.

Out of Home v1 Shared Reference Date integration. **Deferred.**

### Long-press timing

Graph long-press starts at 350ms. Cockpit long-press starts at 400ms, then repeats every 75ms. Do not fix that difference in this task.

Home v1 reuses the existing Cockpit date controls. Do not add a new date engine.

---

## H4 — Home Implementation

Status: **DONE / VERIFIED** (2026-10-01). Production deploy is pending.

| id | name | status |
|----|------|--------|
| H4-A | Shared Reference Date Foundation | **DONE / VERIFIED** |
| H4-B | Home Shell / 3 Window Layout | **DONE / VERIFIED** |
| H4-C | Primary KPI / Data Binding | **DONE / VERIFIED** |
| H4-D | Expanded KPI / Progress | **DONE / VERIFIED** |
| H4-E | Global Menu / Site Chrome Integration | **DONE / VERIFIED** |
| H4-F1 | Daily CTA | **DONE / VERIFIED** |
| H4-F2 | Sales Progress Warning | **DONE / VERIFIED** |
| H4-G | Opening Date Preference UI | **DONE / VERIFIED** |
| H4-H | Pre-Deploy Validation | **DONE / VERIFIED** |

H4-H technical blockers = 0. HEAD `37702722b1b88bbd4b51d5e85cb44ff3ec739e82`. Not deployed. Not PRODUCTION VERIFIED.

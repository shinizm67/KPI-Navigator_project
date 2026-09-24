# BR-LAUNCH-07 Global Menu Spacing / Reservation Button Collision — Phase 1 Audit

Date: 2026-09-25  
Status: CLOSED (Phase 2 production smoke 113/114)  
Production: `https://forge-laboratory.com/kpi-navigator`  
excel/: untouched

Playwright: `scripts/_tmp_c7_header_audit.json` (112 overlapping probes / 113). Screenshots: `scripts/_tmp_c7_header_shots/`.

Daily has no separate URL; it uses the same shared header as Annual / Monthly (`#global-nav-daily-btn`). Language selector is not in this header (`langSel: null`).

---

## Root cause

Shared header geometry, not a one-language / one-mode / one-page bug.

1. `.header-actions` is `position: absolute; right: 24px` (`register/style.css`).
2. `.si-fi.profile-page .header-inner` only reserves `padding-right: 260px` (`en/setting/style.css`).
3. Measured actions width is **294.6px Sci-Fi** and **337px Office** (Mode control grew after BR-LAUNCH-03-A in-flow `Office`). 260px is **35–77px short**.
4. `.global-nav` is `flex: 1` with `.global-nav-list { justify-content: center }`. The four 120px tabs are laid out in that under-reserved row, so **Insight/考察/洞察 AABB overlaps `#header-booking-btn`**.

Page-local `gap: 80px` (JA Office) / `50px` (EN Office) on Annual/Monthly/MEP is **dead**. Shared CSS wins:

`html[lang="ja|en"] .si-fi.office-mode.profile-page .global-nav-list { gap: 28px !important; }`

Live computed gap is **24px (JA Sci-Fi Annual/Monthly/MEP only)** or **28px (everything else)**. Reducing gap is not the only fix, but a smaller centered list does move Insight left slightly (JA Sci-Fi −5.1 vs EN Sci-Fi −11.2).

Office vs Sci-Fi share the same 120px tab slots. Office is worse because the Mode control is wider (185 vs 143), which shifts the absolute actions left over Insight.

---

## Shared component

**YES.** HTML from `scripts/site_chrome.py` (`KPI-SITE-HEADER`). Layout CSS: `register/style.css` + `en/setting/style.css`. Page-local header gap overrides exist but do not win.

---

## Measured (1200 CSS px; identical at 1280 / 1366 / 1440 because `header-inner` `max-width: 1200px`)

| Piece | Sci-Fi JA Annual | Office JA Annual |
|-------|------------------|------------------|
| Annual/Monthly/Daily/Insight width | 120 / 120 / 120 / 120 | 120 / 120 / 120 / 120 |
| Primary nav item gaps | 24 / 24 / 24 | 28 / 28 / 28 |
| list `gap` | 24px | 28px |
| Booking | 30 × 30 | 30 × 30 |
| DL | 46 | 46 |
| Settings gear | 24 | 24 |
| Mode | 142.6 | 185 |
| Actions total | 294.6 | 337 |
| Actions `position` | absolute | absolute |
| Header inner | 1200, pad-right 260, gap 40 | same |
| Logo | 217 | 217 |
| Nav flex width | 659 | 659 |
| Insight–booking gap | **−5.1** (overlap 152) | **−53.5** (overlap **900** = full 30×30) |
| overflowX | 0 | 0 |

EN Sci-Fi Insight–booking gap **−11.2** (overlap 336). ZH-TW Sci-Fi **−11.1** Annual / **−9.7** MEP+profile. Office all langs **−53.5 to −53.9**, overlap 900.

Labels: JA `年次 月次 日次 考察` · EN `Annual Monthly Daily Insight` · ZH-TW `年度 月度 每日 洞察`. Slots stay 120px; English words fill the frame, CJK looks sparse, but collision is the 120px box vs absolute booking, not glyph overflow.

---

## Viewport contract

| Width | Result |
|-------|--------|
| 1200 | FAIL (overlap). Header still 1200; 03-E gate remains valid. |
| 1280 | FAIL (same boxes) |
| 1366 | FAIL (same boxes) |
| 1440 | FAIL (same boxes) |

Widening the viewport does not move booking; it stays inside the 1200 inner.

---

## Affected

**Pages:** Annual, Monthly, MEP (`monthly/edit`), PL, settings/profile. Same chrome on booking and other `site_chrome` pages. ZH-TW PL probe timed out waiting for `#header-booking-btn`; other ZH-TW surfaces match the same geometry.

**Languages:** JP, EN, ZH-TW  

**Modes:** Sci-Fi and Office (Office fully covers the calendar icon)

---

## Findings

| ID | Sev | Finding |
|----|-----|---------|
| H01 | **P1** | Insight tab AABB overlaps `#header-booking-btn` on all measured langs × modes × pages × 1200–1440. Shared absolute actions + 260px pad. |
| H02 | P2 | Dead page-local Office gaps 80px/50px (Annual/Monthly/MEP). Misleading; do not use as the repair. |
| H03 | P2 | JA Sci-Fi page-local `gap: 24px` vs shared 28px. Tiny difference only. |
| H04 | Intentional | 120px Sci-Fi frame slot; Office copies that width. Keep unless Phase 2 also hugs text after booking has reserved space. |

P0: **0** (overflowX=0; booking still hit-testable in Sci-Fi sample; 1200 header contract itself holds)  
P1: **1**  
P2: **2**

---

## Recommended repair (do not implement now)

Shared CSS only. Do **not** absolute-offset the calendar. Do **not** fix one language/mode/page.

1. Reserve real actions width: raise `.si-fi.profile-page .header-inner` `padding-right` from 260px to **≥ Office actions (~337) + ≥8px gap** (about **360–380px**), **or** stop absolutely positioning `.header-actions` and put it in the flex row.
2. After booking has clear space, optionally tighten primary nav (smaller `gap` than 28 and/or shrink 120px slots toward label width) so Annual–Insight sit closer. Tightening gap **without** reserved actions is not enough for Office (−53px).
3. Leave DL / Mode / gear behavior. Do not re-break 03-A in-flow `Office`.
4. Optionally delete dead 80/50 page-local rules (P2).

Estimated fix: **SMALL**.

---

## Verdict

| Field | Value |
|-------|--------|
| Shared Component | YES |
| 1200 / 1280 / 1366 / 1440 | FAIL / FAIL / FAIL / FAIL |
| P0 | 0 |
| P1 | 1 |
| P2 | 2 |
| Estimated Fix Size | **SMALL** |
| Human Review Required | **YES** (padding vs hug-text tightness after geometry fix) |
| BR-LAUNCH-07 | **ACTIVE** |
| Next Task | **BR-LAUNCH-07 Phase 2 Repair** |
| excel untouched | **YES** |

---

## Phase 2 Repair — CLOSED 2026-09-25

Shared `en/setting/style.css` tokens:

- `--kpi-header-actions-reserve: 368px` (was `padding-right: 260px`)
- `--kpi-header-nav-gap: 20px` (was 28px; required so 4×120px tabs fit remaining 1200 after reserve)

No calendar absolute offset. No per-language/mode/page header hacks. `site_chrome.py` markup unchanged.

SHA: `bbe3907`  
FileZilla: C71–C83  
Production: `scripts/_tmp_c7_phase2_smoke.json` **113/114 PASS**. ZH-TW PL has no `#header-booking-btn` (pre-existing markup; pad 368px confirmed). Basic redirect PASS.

Insight–booking gap after: Sci-Fi **49–56px**, Office **12.1–12.5px**. Overlap 0. overflowX 0. 1200 Mode `Office` still in-flow (03-A).

---

## Trunk closeout note (2026-09-25) — ZH-TW PL booking

The 113/114 miss is **not** a 07 geometry miss. It is an **accidental language/page parity omission**.

| Surface | `#header-booking-btn` | Header source |
|---------|------------------------|---------------|
| JP PL `app/profit/pl/index.html` | present | `build_pl_table_page.py` → `site_chrome.build_header` (no KPI-SITE-HEADER markers) |
| EN PL `en/app/profit/pl/index.html` | present | same generator |
| ZH-TW PL `zh-tw/app/profit/pl/index.html` | **absent** | forked unmarked `<header>` (Mode then DL) |
| ZH-TW Annual / Monthly / MEP / profit landing / booking / settings | present | `build_site_chrome.py` + `site_chrome.py` |

`scripts/build_site_chrome.py` explicitly excludes PL (`owned by build_pl_table_page.py`). That generator `main()` writes JA + EN only. ZH-TW PL never received the shared booking control.

Registered **BR-LAUNCH-08** (REGISTER ONLY). Do not repair in 07.
